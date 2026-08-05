#!/usr/bin/env python3
"""
Build the sales tips library from the raw LinkedIn saved-posts capture.

Input:  data/linkedin_saved_posts_raw.json   (captured from linkedin.com/my-items/saved-posts)
Output: posts/*.md                          (one markdown file per saved post)
        INDEX.md                            (master index, newest first)
        by-topic/*.md                       (topic indexes)
        data/posts.json                      (cleaned, tagged records)

Re-run any time the raw capture is refreshed:  python3 build_library.py
"""

import json
import re
import os
import datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "data", "linkedin_saved_posts_raw.json")
POSTS_DIR = os.path.join(HERE, "posts")
TOPIC_DIR = os.path.join(HERE, "by-topic")
SUBS_DIR = os.path.join(HERE, "data", "video_subs")

# Capture date -- relative ages ("4d", "1yr") are resolved against this.
CAPTURE_DATE = datetime.date(2026, 8, 4)

# ---------------------------------------------------------------- topic rules
# Keyword-based tagging. Each entry is matched as a whole word/phrase (\b...\b),
# so "power" no longer fires on "powerful" and "demo" no longer fires on
# "demographic". A post can carry several tags. Trailing * = allow any suffix.
TOPICS = {
    "job-search-interviewing": [
        "interview*", "resume", "hiring manager*", "recruiter*", "job search",
        "candidate*", "job hunt", "applicant*", "offer letter", "laid off",
        "layoff*", "get hired", "land a job", "job market", "job description",
        "hiring for", "screening call", "president's club", "job posting",
    ],
    "outbound-prospecting": [
        "cold call*", "cold email*", "coldcall*", "prospect*", "outbound",
        "sequence*", "cadence*", "sdr", "sdrs", "bdr", "bdrs", "dials",
        "gatekeeper*", "voicemail*", "cold outreach", "first touch",
    ],
    "discovery": [
        "discovery", "disco call", "qualif*", "meddic", "meddpicc", "spiced",
        "pain point*", "first call", "root cause", "discovery call",
    ],
    "objection-handling": [
        "objection*", "not interested", "push back", "pushback", "ghost*",
        "no budget", "send me an email", "we're all set", "brush off",
        "stall*", "too expensive", "bad timing", "no thanks",
    ],
    "deal-management-closing": [
        "close the deal", "closing", "negotiat*", "procurement", "champion*",
        "mutual action plan", "forecast*", "next step*", "deal review",
        "late stage", "legal review", "renewal*", "close plan", "close date",
    ],
    "messaging-copywriting": [
        "subject line*", "email copy", "personaliz*", "copywriting", "messaging",
        "call to action", "talk track*", "value prop*", "one-liner",
        "cold email template", "email template*",
    ],
    "pipeline-territory": [
        "pipeline generation", "pipe gen", "pg plan", "territory", "account plan*",
        "book of business", "quota", "target account*", "pipeline",
    ],
    "exec-selling": [
        "cfo", "cfos", "ceo", "ceos", "coo", "cio", "cios", "ciso", "cro",
        "c-level", "c level", "c-suite", "executive*", "above the line",
        "vp of", "economic buyer", "the board", "board meeting", "boardroom",
    ],
    "mindset-career": [
        "mindset", "habits", "burnout", "burn out", "promotion", "career",
        "discipline", "confidence", "imposter", "motivation", "morning routine",
        "personal brand", "work life balance", "work-life balance",
    ],
    "sales-leadership": [
        "sales leader*", "sales manager*", "coaching", "my team", "my org",
        "onboarding", "ramp time", "leadership", "hiring reps", "1:1s", "1:1",
        "manage up", "sales team*",
    ],
    "ai-tools": [
        "chatgpt", "gpt-4*", "gpt-5*", "ai", "artificial intelligence", "claude",
        "llm*", "automation", "prompt*", "clay", "outreach.io", "apollo",
    ],
    "demos-presenting": [
        "demo", "demos", "demoing", "presentation*", "storytell*", "slide*",
        "deck", "whiteboard*", "poc", "pilot", "proof of concept",
    ],
}

# Precompile: each keyword becomes a word-boundary regex.
TOPIC_RE = {
    topic: [
        re.compile(r"\b" + re.escape(k[:-1]).replace(r"\ ", r"\s+") + r"\w*", re.I)
        if k.endswith("*")
        else re.compile(r"\b" + re.escape(k).replace(r"\ ", r"\s+") + r"\b", re.I)
        for k in kws
    ]
    for topic, kws in TOPICS.items()
}

AGE_UNITS = {
    "s": 1 / 86400, "m": 1 / 1440, "h": 1 / 24,
    "d": 1, "w": 7, "mo": 30.44, "yr": 365.25,
}


def slugify(text, maxlen=48):
    s = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return s[:maxlen].strip("-") or "post"


def resolve_date(age):
    """'4d' -> approximate absolute date. Returns (iso_date, is_approx)."""
    m = re.match(r"^(\d+)\s*(s|m|h|d|w|mo|yr)$", (age or "").strip())
    if not m:
        return "", True
    n, unit = int(m.group(1)), m.group(2)
    days = n * AGE_UNITS[unit]
    d = CAPTURE_DATE - datetime.timedelta(days=days)
    # day/hour/minute ages are near-exact; week+ are rounded by LinkedIn
    approx = unit in ("w", "mo", "yr")
    return d.isoformat(), approx


def fix_repost(rec):
    """LinkedIn repost cards put the age inside a 'Reposted from X - 1yr -' line.

    The first pass left author/headline/age unparsed for those. Recover them.
    """
    body = rec["body"]
    m = re.search(r"Reposted from (.+?)\s*•\s*(\d+\s*(?:s|m|h|d|w|mo|yr))\s*•", body)
    if not m:
        return rec
    rec["reposted_by"] = rec["author"]
    rec["author"] = m.group(1).strip()
    rec["age"] = m.group(2).replace(" ", "")
    # headline of the reposter sits before the 'Reposted from' marker
    head = body[: m.start()]
    head = re.sub(r"^\s*•\s*(1st|2nd|3rd\+?)\s*", "", head).strip()
    rec["headline"] = head.strip("| \n")
    rec["body"] = body[m.end():].strip()
    return rec


def vtt_to_text(path):
    """Flatten a WebVTT caption file into readable prose."""
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.strip()
        if (not line or line == "WEBVTT" or "-->" in line
                or re.match(r"^\d+$", line) or line.startswith(("NOTE", "Kind:", "Language:"))):
            continue
        if out and out[-1] == line:      # captions often repeat a line
            continue
        out.append(line)
    text = " ".join(out)
    return re.sub(r"\s+", " ", text).strip()


def tag(rec):
    # Recovered media/video content counts: for teaser posts it IS the post.
    hay = " ".join([
        rec["body"], rec.get("headline", ""),
        rec.get("media_transcript", ""), rec.get("video_transcript", ""),
    ])
    tags = [t for t, rxs in TOPIC_RE.items() if any(rx.search(hay) for rx in rxs)]
    return tags or ["general"]


def main():
    with open(RAW) as f:
        raw = json.load(f)

    os.makedirs(POSTS_DIR, exist_ok=True)
    os.makedirs(TOPIC_DIR, exist_ok=True)
    for d in (POSTS_DIR, TOPIC_DIR):
        for fn in os.listdir(d):
            if fn.endswith(".md"):
                os.remove(os.path.join(d, fn))

    overrides = {}
    ov_path = os.path.join(HERE, "data", "overrides.json")
    if os.path.exists(ov_path):
        overrides = {k: v for k, v in json.load(open(ov_path)).items()
                     if not k.startswith("_")}

    flags = {}
    fl_path = os.path.join(HERE, "data", "media_flags.json")
    if os.path.exists(fl_path):
        flags = json.load(open(fl_path))

    transcripts = {}
    tr_path = os.path.join(HERE, "data", "media_transcripts.json")
    if os.path.exists(tr_path):
        transcripts = {k: v for k, v in json.load(open(tr_path)).items()
                       if not k.startswith("_")}

    posts = []
    for rec in raw:
        rec = dict(rec)
        if not rec.get("age"):
            rec = fix_repost(rec)

        # Repost cards carry only the reposter's commentary in the list DOM.
        # overrides.json supplies the original post, fetched from its own page.
        ov = overrides.get(str(rec["i"]))
        if ov:
            rec.update({k: v for k, v in ov.items() if k != "commentary"})
            rec["commentary"] = ov.get("commentary", "")

        f = flags.get(str(rec["i"]), {})
        rec["media"] = f.get("media", "")

        tr = transcripts.get(str(rec["i"]))
        if tr:
            rec["media_transcript"] = tr["transcript"]
            rec["media_kind"] = tr.get("kind", rec["media"])
            rec["media_no_loss"] = tr.get("no_loss", False)
            rec["media_off_topic"] = tr.get("off_topic", False)

        vtt = os.path.join(SUBS_DIR, f"post-{rec['i']}.en.vtt")
        if os.path.exists(vtt):
            rec["video_transcript"] = vtt_to_text(vtt)

        rec["body"] = rec["body"].strip()
        # Strip the stray see-more marker LinkedIn injects mid-body on polls
        rec["body"] = re.sub(r"\n…see more\n", "\n", rec["body"]).strip()
        rec["tags"] = tag(rec)
        rec["date"], rec["date_approx"] = resolve_date(rec["age"])
        rec["words"] = len(rec["body"].split())
        posts.append(rec)

    # A short body plus an attached image/video/article means the text is just a
    # caption and the real content is in the media. Flag it rather than let the
    # teaser pass for the whole post.
    # Only still incomplete if nothing recovered the media's content.
    for p in posts:
        short_with_media = bool(p.get("media")) and len(p["body"]) < 250
        recovered = bool(p.get("media_transcript")) or p.get("media_no_loss")
        p["text_is_teaser"] = short_with_media and not recovered

    # newest first (the capture is already in that order)
    for n, p in enumerate(posts, 1):
        p["n"] = n
        first_line = p["body"].split("\n")[0]
        p["title"] = (first_line[:80] + "…") if len(first_line) > 80 else first_line
        p["file"] = f"{n:03d}-{slugify(p['author'])}-{slugify(first_line, 40)}.md"

    # ------------------------------------------------------------ post files
    for p in posts:
        fm = [
            "---",
            f"author: {p['author']}",
            f"headline: {p.get('headline','')}",
        ]
        if p.get("reposted_by"):
            fm.append(f"reposted_by: {p['reposted_by']}")
        fm += [
            f"posted: {p['date']}{' (approx)' if p['date_approx'] else ''}  # LinkedIn showed \"{p['age']}\" at capture",
            f"url: {p['url']}",
            f"tags: {', '.join(p['tags'])}",
            f"words: {p['words']}",
        ]
        if p.get("media"):
            fm.append(f"media: {p['media']}")
        if p.get("text_is_teaser"):
            fm.append("text_is_teaser: true  # the substance is in the attached media, open the url")
        fm += [
            "---",
            "",
            f"# {p['author']}: {p['title']}",
            "",
        ]
        if p.get("text_is_teaser"):
            fm += [
                f"> Incomplete: this post's content lives in an attached {p['media']}, "
                f"which is not capturable as text. The body below is only the caption. "
                f"Open the url to see the rest.",
                "",
            ]
        if p.get("commentary"):
            fm += [f"*Reposted by {p['reposted_by']}, who added:* {p['commentary']}", "", "---", ""]
        fm += [p["body"], ""]

        if p.get("media_transcript"):
            fm += ["", "---", ""]
            if p.get("media_no_loss"):
                fm += [f"## Attached {p['media']}", "", p["media_transcript"], ""]
            else:
                note = ""
                if p.get("media_off_topic"):
                    note = " Not a sales tip; see the note at the end."
                fm += [
                    f"## Transcribed from the attached {p.get('media_kind', p['media'])}",
                    "",
                    f"*Read from the rendered post on {CAPTURE_DATE.isoformat()}. "
                    f"Not present in the original text capture.{note}*",
                    "",
                    p["media_transcript"],
                    "",
                ]

        if p.get("video_transcript"):
            fm += [
                "", "---", "",
                "## Video captions",
                "",
                "*Pulled with yt-dlp from the attached LinkedIn video. "
                "Auto-generated, so expect transcription errors and no speaker labels.*",
                "",
                p["video_transcript"],
                "",
            ]
        with open(os.path.join(POSTS_DIR, p["file"]), "w") as f:
            f.write("\n".join(fm))

    # ---------------------------------------------------------- topic indexes
    by_topic = defaultdict(list)
    for p in posts:
        for t in p["tags"]:
            by_topic[t].append(p)

    for topic, plist in sorted(by_topic.items()):
        lines = [
            f"# {topic.replace('-', ' ').title()} ({len(plist)} posts)",
            "",
            "| # | Author | Opening line | Date |",
            "|---|--------|--------------|------|",
        ]
        for p in plist:
            t = p["title"].replace("|", "\\|")
            lines.append(
                f"| [{p['n']}](../posts/{p['file']}) | {p['author']} | {t} | {p['date']} |"
            )
        with open(os.path.join(TOPIC_DIR, f"{topic}.md"), "w") as f:
            f.write("\n".join(lines) + "\n")

    # ------------------------------------------------------------ master index
    authors = defaultdict(int)
    for p in posts:
        authors[p["author"]] += 1

    lines = [
        "# Sales Tips Library",
        "",
        f"{len(posts)} posts saved from LinkedIn, captured {CAPTURE_DATE.isoformat()}.",
        f"{len(authors)} distinct authors.",
        "",
        "## Topics",
        "",
    ]
    for topic, plist in sorted(by_topic.items(), key=lambda x: -len(x[1])):
        lines.append(f"- [{topic}](by-topic/{topic}.md) ({len(plist)} posts)")

    lines += ["", "## Most-saved authors", ""]
    for a, n in sorted(authors.items(), key=lambda x: (-x[1], x[0]))[:20]:
        lines.append(f"- {a} ({n})")

    lines += ["", "## All posts (newest first)", "",
              "| # | Author | Opening line | Date | Topics |",
              "|---|--------|--------------|------|--------|"]
    for p in posts:
        t = p["title"].replace("|", "\\|")
        lines.append(
            f"| [{p['n']}](posts/{p['file']}) | {p['author']} | {t} | {p['date']} | {' '.join(p['tags'])} |"
        )

    with open(os.path.join(HERE, "INDEX.md"), "w") as f:
        f.write("\n".join(lines) + "\n")

    with open(os.path.join(HERE, "data", "posts.json"), "w") as f:
        json.dump(posts, f, indent=1)

    print(f"wrote {len(posts)} posts")
    print(f"topics: {len(by_topic)}")
    for t, pl in sorted(by_topic.items(), key=lambda x: -len(x[1])):
        print(f"  {len(pl):4d}  {t}")


if __name__ == "__main__":
    main()
