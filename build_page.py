#!/usr/bin/env python3
"""
Generate the browsable/searchable single-file page for the sales tips library.

    python3 build_library.py && python3 build_page.py

Writes sales-tips-library.html: one self-contained file, no network calls, so it
works opened from disk, served from GitHub Pages, or published as an Artifact.
"""

import json
import os
import sys
import re as _re
import html
from collections import defaultdict

from taxonomy import classify, TOPIC_META, SHELVES

HERE = os.path.dirname(os.path.abspath(__file__))
# --public builds the shareable version: opening excerpt plus a link out, never
# the full text of someone else's post. Search still works, because each post
# ships a sorted set of its unique words, which matches queries but cannot be
# reassembled back into the post.
PUBLIC = "--public" in sys.argv
OUT = os.path.join(HERE, "docs", "library.html") if PUBLIC \
    else os.path.join(HERE, "sales-tips-library.html")

EXCERPT_CHARS = 240
STOP = set("the a an and or but if of to in on for with is are was were be been "
           "you your i my we our they their this that it its as at by from not "
           "so do does did have has had will would can could should".split())


def excerpt(text):
    t = _re.sub(r"\s+", " ", text).strip()
    if len(t) <= EXCERPT_CHARS:
        return t, False
    cut = t[:EXCERPT_CHARS]
    cut = cut[:cut.rfind(" ")] if " " in cut else cut
    return cut.rstrip(" .,;:") + "...", True


def keywords(*texts):
    """Sorted unique words: enough to search, not enough to rebuild the post."""
    words = set()
    for t in texts:
        if t:
            words.update(w for w in _re.findall(r"[a-z0-9']{3,}", t.lower())
                         if w not in STOP)
    return " ".join(sorted(words))

SHELF_HUE = {
    "prospecting": "#B4553A",
    "deal": "#14584C",
    "pipeline": "#4A6FA5",
    "career": "#8A5CA8",
    "tools": "#3E7C8C",
    "leadership": "#7A6A3A",
    "other": "#8A8F88",
}

# One line per shelf, so the rail explains itself instead of just listing nouns.
SHELF_NOTE = {
    "prospecting": "Getting the first conversation.",
    "deal": "Everything between the first meeting and signature.",
    "pipeline": "Running your patch as a book of business.",
    "career": "Getting hired, paid, and promoted.",
    "tools": "What to point at the work.",
    "leadership": "Managing reps, and reading the org you're joining.",
    "other": "Saves that aren't about selling. Parked here so they stay out of the way.",
}


def load():
    posts = json.load(open(os.path.join(HERE, "data", "posts.json")))
    for p in posts:
        extra = (p.get("media_transcript", "") or "") + " " + (p.get("video_transcript", "") or "")
        p["primary"], p["secondary"] = classify(p["title"], p["body"], extra, p["n"])
    return posts


def main():
    posts = load()

    by_topic = defaultdict(list)
    for p in posts:
        by_topic[p["primary"]].append(p)

    # payload the page searches over
    records = []
    for p in posts:
        body, clipped = (excerpt(p["body"]) if PUBLIC else (p["body"], False))
        rec = {
            "n": p["n"],
            "a": p["author"],
            "hl": p.get("headline", "")[:150],
            "t": p["title"],
            "b": body,
            "d": p["date"],
            "ap": p["date_approx"],
            "u": p["url"],
            "pt": p["primary"],
            "st": p["secondary"],
            "md": p.get("media", ""),
            "mt": p.get("media_transcript", ""),
            "mk": p.get("media_kind", ""),
            "vt": p.get("video_transcript", ""),
            "rb": p.get("reposted_by", ""),
            "cm": p.get("commentary", ""),
            "w": p["words"],
        }
        if PUBLIC:
            # media transcripts and captions are their content too: describe, don't reprint
            rec["mt"] = ""
            rec["vt"] = ""
            rec["clip"] = clipped
            rec["k"] = keywords(p["body"], p.get("media_transcript", ""),
                                p.get("video_transcript", ""))
        records.append(rec)

    topics_meta = {
        k: {"label": v["label"], "shelf": v["shelf"], "shelfLabel": v["shelf_label"]}
        for k, v in TOPIC_META.items()
    }
    shelves = [
        {"key": k, "label": l, "topics": ts, "hue": SHELF_HUE[k], "note": SHELF_NOTE[k]}
        for k, l, ts in SHELVES
    ]

    data = json.dumps({
        "posts": records,
        "topics": topics_meta,
        "shelves": shelves,
    }, ensure_ascii=True, separators=(",", ":"))   # ASCII-only: immune to charset issues

    authors = defaultdict(int)
    for p in posts:
        authors[p["author"]] += 1
    top_authors = sorted(authors.items(), key=lambda kv: (-kv[1], kv[0]))[:8]

    os.makedirs(os.path.join(HERE, "docs"), exist_ok=True)
    page = TEMPLATE.replace("__DATA__", data)
    page = page.replace("__PUBLIC__", "true" if PUBLIC else "false")
    page = page.replace("__NPOSTS__", str(len(posts)))
    page = page.replace("__NAUTHORS__", str(len(authors)))
    page = page.replace("__NTOPICS__", str(len(TOPIC_META)))
    page = page.replace("__TOPAUTHORS__", html.escape(
        ", ".join(f"{a} ({n})" for a, n in top_authors)))

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)

    print(f"wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
    for k, l, ts in SHELVES:
        print(f"  {l}: {sum(len(by_topic[t]) for t in ts)}")



TEMPLATE = r"""<title>Sales Tips Library</title>
<style>
  :root{
    --bg:#E6E7E2; --surface:#FBFBF9; --surface-2:#F1F2ED;
    --ink:#16191C; --ink-2:#5A6169; --ink-3:#868D94;
    --rule:#CFD2CB; --rule-2:#DEE0DA;
    --accent:#14584C; --accent-soft:#14584C1A;
    --mark:#F2C14E; --mark-ink:#3A2E08;
    --sans:-apple-system,BlinkMacSystemFont,"Segoe UI",system-ui,sans-serif;
    --serif:"Iowan Old Style",Charter,"Bitstream Charter","Sitka Text",Georgia,serif;
    --mono:ui-monospace,"SF Mono",SFMono-Regular,Menlo,Consolas,monospace;
  }
  @media (prefers-color-scheme:dark){
    :root{
      --bg:#121513; --surface:#191D1B; --surface-2:#20241F;
      --ink:#E7E9E4; --ink-2:#9AA29B; --ink-3:#77807A;
      --rule:#2C312E; --rule-2:#242926;
      --accent:#68C4AC; --accent-soft:#68C4AC1F;
      --mark:#7A5F16; --mark-ink:#FFE8AE;
    }
  }
  :root[data-theme="dark"]{
    --bg:#121513; --surface:#191D1B; --surface-2:#20241F;
    --ink:#E7E9E4; --ink-2:#9AA29B; --ink-3:#77807A;
    --rule:#2C312E; --rule-2:#242926;
    --accent:#68C4AC; --accent-soft:#68C4AC1F;
    --mark:#7A5F16; --mark-ink:#FFE8AE;
  }
  :root[data-theme="light"]{
    --bg:#E6E7E2; --surface:#FBFBF9; --surface-2:#F1F2ED;
    --ink:#16191C; --ink-2:#5A6169; --ink-3:#868D94;
    --rule:#CFD2CB; --rule-2:#DEE0DA;
    --accent:#14584C; --accent-soft:#14584C1A;
    --mark:#F2C14E; --mark-ink:#3A2E08;
  }

  *{box-sizing:border-box}
  body{
    margin:0;background:var(--bg);color:var(--ink);
    font-family:var(--sans);font-size:12px;line-height:1.32;
    -webkit-font-smoothing:antialiased;
  }
  a{color:var(--accent)}
  mark{background:var(--mark);color:var(--mark-ink);border-radius:2px;padding:0 .1em}

  .wrap{display:grid;grid-template-columns:246px minmax(0,1fr);min-height:100vh}

  /* ---------------------------------------------------------------- rail */
  .rail{
    background:var(--surface-2);border-right:1px solid var(--rule);
    padding:18px 0 60px;position:sticky;top:0;height:100vh;overflow-y:auto;
  }
  .brand{padding:0 18px 13px;border-bottom:1px solid var(--rule)}
  .brand h1{margin:0;font-size:11.5px;letter-spacing:-.005em;font-weight:650}
  .brand .sub{
    margin-top:4px;font-family:var(--mono);font-size:8.8px;
    text-transform:uppercase;letter-spacing:.09em;color:var(--ink-3);
  }
  .navsec{padding:11px 10px 0}
  .shelf{margin-bottom:1px}
  .shelf > .shelfhead{
    display:flex;align-items:center;gap:7px;width:100%;
    padding:6px 7px;border:0;background:none;cursor:pointer;
    font-family:var(--sans);font-size:9px;font-weight:700;
    text-transform:uppercase;letter-spacing:.07em;color:var(--ink-2);
    text-align:left;border-radius:4px;
  }
  .shelf > .shelfhead:hover{background:var(--surface);color:var(--ink)}
  .dot{width:6px;height:6px;border-radius:50%;flex:none}
  .cnt{margin-left:auto;font-family:var(--mono);font-size:9.5px;color:var(--ink-3);
    font-variant-numeric:tabular-nums;flex:none}
  .chev{transition:transform .16s ease;flex:none;opacity:.45}
  .shelf[data-open="0"] .chev{transform:rotate(-90deg)}
  .shelf[data-open="0"] .topics{display:none}
  .topics{padding:1px 0 6px 3px;display:flex;flex-direction:column;gap:1px}
  .topic{
    display:flex;align-items:baseline;gap:7px;width:100%;text-align:left;
    padding:4px 9px 4px 17px;border:0;background:none;cursor:pointer;border-radius:4px;
    font-family:var(--sans);font-size:10.8px;color:var(--ink-2);line-height:1.28;
  }
  .topic:hover{background:var(--surface);color:var(--ink)}
  .topic[aria-pressed="true"]{background:var(--accent-soft);color:var(--accent);font-weight:640}
  .topic[data-dead="1"]{opacity:.34}
  .railfoot{padding:13px 18px 0;margin-top:9px;border-top:1px solid var(--rule);
    font-size:10.5px;color:var(--ink-3);line-height:1.45}
  .railfoot kbd{font-family:var(--mono);font-size:9.5px;border:1px solid var(--rule);
    border-radius:3px;padding:1px 4px;color:var(--ink-2)}
  .railfoot p{margin:5px 0 0}
  .railfoot .hintline{margin-top:11px;padding-top:9px;border-top:1px solid var(--rule)}
  .xlink{display:block;font-size:10.6px;font-weight:640;color:var(--accent);
    text-decoration:none}
  .xlink:hover{text-decoration:underline}
  .clipnote{margin:9px 0 0;font-size:9.6px;color:var(--ink-3);line-height:1.45;
    max-width:60ch;font-style:italic}

  /* ---------------------------------------------------------------- main */
  .main{min-width:0;padding:0 0 90px}
  .topbar{
    position:sticky;top:0;z-index:20;background:color-mix(in srgb,var(--bg) 88%,transparent);
    backdrop-filter:blur(10px);border-bottom:1px solid var(--rule);
    padding:11px 34px;display:flex;gap:11px;align-items:center;
  }
  .searchwrap{position:relative;flex:1;max-width:560px}
  .searchwrap svg{position:absolute;left:11px;top:50%;transform:translateY(-50%);opacity:.4;pointer-events:none}
  #q{
    width:100%;padding:8px 68px 8px 32px;border:1px solid var(--rule);
    border-radius:6px;background:var(--surface);color:var(--ink);
    font-family:var(--sans);font-size:11.5px;
  }
  #q:focus{outline:2px solid var(--accent);outline-offset:-1px;border-color:transparent}
  #q::placeholder{color:var(--ink-3)}
  .kbd{
    position:absolute;right:9px;top:50%;transform:translateY(-50%);
    font-family:var(--mono);font-size:9px;color:var(--ink-3);
    border:1px solid var(--rule);border-radius:3px;padding:1px 4px;pointer-events:none;
  }
  #q:not(:placeholder-shown) ~ .kbd{display:none}
  .tbtn{
    border:1px solid var(--rule);background:var(--surface);color:var(--ink-2);
    border-radius:6px;padding:6px 9px;cursor:pointer;font-family:var(--sans);font-size:10.5px;
    display:flex;align-items:center;gap:5px;white-space:nowrap;
  }
  .tbtn:hover{color:var(--ink);border-color:var(--ink-3)}

  .head{padding:26px 34px 0;max-width:860px}
  .eyebrow{font-family:var(--mono);font-size:9.5px;text-transform:uppercase;
    letter-spacing:.1em;color:var(--ink-3)}
  .head h2{font-size:18px;margin:7px 0 0;letter-spacing:-.015em;text-wrap:balance;font-weight:640}
  .head p{color:var(--ink-2);margin:6px 0 0;max-width:70ch;font-size:12px;line-height:1.42}
  .statrow{display:flex;gap:22px;margin:17px 0 0;padding:11px 0;
    border-top:1px solid var(--rule);border-bottom:1px solid var(--rule)}
  .stat b{display:block;font-family:var(--mono);font-size:13px;
    font-variant-numeric:tabular-nums;letter-spacing:-.02em}
  .stat span{font-size:9.5px;color:var(--ink-3);text-transform:uppercase;letter-spacing:.06em}

  /* --------------------------------------------------- active filter bar */
  .filterbar{display:flex;flex-wrap:wrap;align-items:center;gap:6px;
    padding:14px 34px 0;max-width:860px}
  .flabel{font-family:var(--mono);font-size:9.5px;text-transform:uppercase;
    letter-spacing:.08em;color:var(--ink-3);margin-right:2px}
  .fpill{display:flex;align-items:center;gap:6px;border:0;cursor:pointer;
    border-radius:4px;padding:3px 6px;font-family:var(--sans);font-size:10.5px;
    color:#fff;font-weight:560}
  .fpill:hover{filter:brightness(1.12)}
  .fpill .x{opacity:.7;font-size:13px;line-height:1}
  .fand{font-family:var(--mono);font-size:9.5px;color:var(--ink-3);letter-spacing:.06em}
  .fclear{border:0;background:none;cursor:pointer;color:var(--ink-3);
    font-family:var(--sans);font-size:10.5px;text-decoration:underline;padding:4px}
  .fclear:hover{color:var(--ink)}
  .fhint{font-size:10px;color:var(--ink-3);width:100%;margin-top:2px}

  .results{padding:4px 34px 0;max-width:860px}
  .rescount{font-family:var(--mono);font-size:10px;color:var(--ink-3);
    text-transform:uppercase;letter-spacing:.07em;padding:16px 0 6px}
  .topichits{display:flex;flex-wrap:wrap;gap:5px;padding:0 0 12px}
  .topichit{border:1px dashed var(--rule);background:none;color:var(--ink-2);cursor:pointer;
    border-radius:20px;padding:3px 9px;font-family:var(--sans);font-size:10px}
  .topichit:hover{border-color:var(--accent);color:var(--accent);border-style:solid}

  .post{border-bottom:1px solid var(--rule-2);padding:8px 0 9px}
  .ptitlebtn{
    display:grid;grid-template-columns:1fr auto;gap:12px;align-items:start;
    width:100%;text-align:left;border:0;background:none;cursor:pointer;
    padding:2px 4px;font-family:var(--sans);color:inherit;
  }
  .ptitlebtn:hover .ptitle{color:var(--accent)}
  .ptitle{font-size:12.5px;line-height:1.32;font-weight:560;margin:0;text-wrap:pretty}
  .pnum{font-family:var(--mono);font-size:9.5px;color:var(--ink-3);
    font-variant-numeric:tabular-nums;padding-top:2px}
  .pmeta{display:flex;flex-wrap:wrap;align-items:center;gap:5px;margin:4px 0 0;padding:0 4px;
    font-size:10px;color:var(--ink-2)}
  .pauthor{font-weight:640;color:var(--ink)}
  .pdate{font-family:var(--mono);font-size:10px;color:var(--ink-3);font-variant-numeric:tabular-nums}
  .chip{font-size:9.2px;padding:2px 6px;border-radius:3px;background:var(--surface-2);
    border:1px solid var(--rule);color:var(--ink-2);white-space:nowrap;
    cursor:pointer;font-family:var(--sans)}
  .chip:hover{border-color:var(--accent);color:var(--accent)}
  .chip.pri{border-color:transparent;color:#fff}
  .chip.pri:hover{filter:brightness(1.15);color:#fff}
  .chip.on{outline:2px solid var(--accent);outline-offset:1px}
  .badge{font-family:var(--mono);font-size:8.8px;text-transform:uppercase;letter-spacing:.06em;
    padding:2px 5px;border-radius:3px;border:1px solid var(--rule);color:var(--ink-3)}

  .body{display:none;padding:5px 4px 14px}
  .post[data-open="1"] .body{display:block}
  .body .text{font-family:var(--serif);font-size:13.1px;line-height:1.4;
    max-width:72ch;color:var(--ink)}
  /* Paragraphs are real elements, not blank lines in a pre-wrap block, so the
     gap between them is a margin we control rather than a full blank line. */
  .body .text p{margin:0 0 .42em}
  .body .text p:last-child{margin-bottom:0}
  .sect{margin-top:15px;padding-top:11px;border-top:1px solid var(--rule)}
  .sect h4{margin:0 0 3px;font-family:var(--mono);font-size:9.5px;text-transform:uppercase;
    letter-spacing:.08em;color:var(--ink-2);font-weight:600}
  .sect .note{font-size:10px;color:var(--ink-3);margin:0 0 8px;max-width:66ch;line-height:1.4}
  .repost{border-left:2px solid var(--rule);padding:1px 0 1px 11px;margin-bottom:11px;
    color:var(--ink-2);font-size:11.5px;line-height:1.42;max-width:66ch}
  .actions{display:flex;gap:13px;align-items:center;margin-top:13px;font-size:10.5px}
  .actions a{text-decoration:none;border-bottom:1px solid var(--accent-soft);padding-bottom:1px}
  .actions a:hover{border-bottom-color:var(--accent)}

  .empty{padding:48px 4px;color:var(--ink-2);max-width:60ch}
  .empty h3{margin:0 0 7px;font-size:13px;font-weight:640;color:var(--ink)}
  .empty p{font-size:12px;line-height:1.45}
  .emptyacts{display:flex;gap:9px;margin-top:15px;flex-wrap:wrap}

  @media (max-width:900px){
    .wrap{grid-template-columns:1fr}
    .rail{position:static;height:auto;border-right:0;border-bottom:1px solid var(--rule)}
    .topbar,.head,.results,.filterbar{padding-left:16px;padding-right:16px}
  }
  @media (prefers-reduced-motion:reduce){*{transition:none!important;animation:none!important}}
  :focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
</style>

<div class="wrap">
  <nav class="rail">
    <div class="brand">
      <h1>Sales Tips Library</h1>
      <div class="sub">__NPOSTS__ saved posts &middot; __NTOPICS__ topics</div>
    </div>
    <div class="navsec">
      <button class="topic" id="allbtn"><span>All posts</span><span class="cnt">__NPOSTS__</span></button>
      <div id="nav"></div>
    </div>
    <div class="railfoot">
      <a class="xlink" href="index.html">Read the Field Guide &rarr;</a>
      <p>What these 292 posts actually say, consolidated by argument, with the
      contradictions called out.</p>
      <p class="hintline"><kbd>&#8984;</kbd> or <kbd>shift</kbd> click a topic to
      combine it with the current one. Counts show what is left after the filters
      you already have.</p>
    </div>
  </nav>

  <main class="main">
    <div class="topbar">
      <div class="searchwrap">
        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.4">
          <circle cx="11" cy="11" r="7"/><path d="M20 20l-4-4"/>
        </svg>
        <input id="q" type="search" placeholder="Search everything: ghosting, CFO, quota, discovery&hellip;" autocomplete="off">
        <span class="kbd">/</span>
      </div>
      <button class="tbtn" id="themebtn" title="Toggle light and dark">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>
        </svg>
        <span id="themelabel">Dark</span>
      </button>
    </div>

    <header class="head">
      <div class="eyebrow" id="crumb">All posts</div>
      <h2 id="htitle">Everything, newest first</h2>
      <p id="hnote"></p>
      <div class="statrow">
        <div class="stat"><b>__NPOSTS__</b><span>Posts</span></div>
        <div class="stat"><b>__NAUTHORS__</b><span>Authors</span></div>
        <div class="stat"><b>__NTOPICS__</b><span>Topics</span></div>
        <div class="stat"><b>2020/26</b><span>Span</span></div>
      </div>
    </header>

    <div class="filterbar" id="filterbar"></div>

    <section class="results">
      <div class="rescount" id="rescount"></div>
      <div class="topichits" id="topichits"></div>
      <div id="list"></div>
    </section>
  </main>
</div>

<script>
const DATA = __DATA__;
const PUBLIC = __PUBLIC__;
const POSTS = DATA.posts, TOPICS = DATA.topics, SHELVES = DATA.shelves;
const HUE = {}, SHELF_OF = {};
SHELVES.forEach(s => s.topics.forEach(t => { HUE[t] = s.hue; SHELF_OF[t] = s; }));

// a post's full tag set: its primary topic plus every secondary
POSTS.forEach(p => {
  p._tags = [p.pt].concat(p.st);
  p._hay = [p.t, p.a, p.hl, p.b, p.mt || '', p.vt || '', p.cm, p.rb, p.k || '',
            ...p._tags.map(t => TOPICS[t].label)].join(' ').toLowerCase();
});

// state.topics is an AND set: a post must carry every selected topic
let state = { topics: [], terms: [] };

const hasTerms = p => state.terms.every(t => p._hay.includes(t));
const hasTopics = p => state.topics.every(t => p._tags.includes(t));
const matches = p => hasTerms(p) && hasTopics(p);

/* ------------------------------------------------------------------ rail */
const nav = document.getElementById('nav');
SHELVES.forEach(s => {
  const el = document.createElement('div');
  el.className = 'shelf'; el.dataset.open = '1'; el.dataset.shelf = s.key;
  el.innerHTML = `
    <button class="shelfhead">
      <span class="dot" style="background:${s.hue}"></span>
      <span>${s.label}</span>
      <svg class="chev" width="10" height="10" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="3"><path d="M6 9l6 6 6-6"/></svg>
      <span class="cnt" data-shelfcnt="${s.key}"></span>
    </button>
    <div class="topics">${s.topics.map(t => `
      <button class="topic" data-topic="${t}" aria-pressed="false"
              title="Click to show ${TOPICS[t].label}. Cmd or shift click to add it to the current filters.">
        <span>${TOPICS[t].label}</span><span class="cnt" data-cnt="${t}"></span>
      </button>`).join('')}</div>`;
  el.querySelector('.shelfhead').onclick = () =>
    el.dataset.open = el.dataset.open === '1' ? '0' : '1';
  nav.appendChild(el);
});

function pickTopic(t, additive){
  if (additive) {
    state.topics = state.topics.includes(t)
      ? state.topics.filter(x => x !== t)
      : state.topics.concat(t);
  } else {
    state.topics = (state.topics.length === 1 && state.topics[0] === t) ? [] : [t];
  }
  render();
}
const additive = e => e.metaKey || e.ctrlKey || e.shiftKey;

document.getElementById('allbtn').onclick = () => { state.topics = []; render(); };
nav.querySelectorAll('.topic').forEach(b => {
  b.onclick = e => pickTopic(b.dataset.topic, additive(e));
});

/* ---------------------------------------------------------------- search */
const q = document.getElementById('q');
let timer;
q.addEventListener('input', () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    state.terms = q.value.toLowerCase().split(/\s+/).filter(t => t.length > 1);
    render();
  }, 110);
});
document.addEventListener('keydown', e => {
  if (e.key === '/' && document.activeElement !== q) { e.preventDefault(); q.focus(); }
  if (e.key === 'Escape' && document.activeElement === q) {
    q.value = ''; state.terms = []; render(); q.blur();
  }
});

function esc(s){ return s.replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c])); }
// Blank-line-separated blocks become paragraphs; single newlines become breaks.
// Keeps list-style posts intact while letting CSS own the paragraph rhythm.
function para(marked){
  return marked.split(/\n{2,}/).map(b => b.trim()).filter(Boolean)
    .map(b => `<p>${b.replace(/\n/g, '<br>')}</p>`).join('');
}
function mark(s){
  let out = esc(s);
  if (!state.terms.length) return out;
  state.terms.forEach(t => {
    const rx = new RegExp('(' + t.replace(/[.*+?^${}()|[\]\\]/g, '\\$&') + ')', 'gi');
    out = out.replace(rx, '<mark>$1</mark>');
  });
  return out;
}

/* ---------------------------------------------------------------- render */
const list = document.getElementById('list');
const rescount = document.getElementById('rescount');
const topichits = document.getElementById('topichits');
const filterbar = document.getElementById('filterbar');

// How many posts would remain if this topic were added to the current filters?
// Showing that live is what stops a dead combination from being a surprise.
function liveCounts(hits){
  const c = {};
  hits.forEach(p => p._tags.forEach(t => c[t] = (c[t] || 0) + 1));
  return c;
}

function render(){
  const hits = POSTS.filter(matches);
  const counts = liveCounts(hits);

  // rail: counts reflect the current filters, dead ends are dimmed
  document.querySelectorAll('.topic[data-topic]').forEach(b => {
    const t = b.dataset.topic, on = state.topics.includes(t);
    b.setAttribute('aria-pressed', String(on));
    const n = on ? hits.length : (counts[t] || 0);
    b.querySelector('[data-cnt]').textContent = n;
    b.dataset.dead = (!on && n === 0) ? '1' : '0';
  });
  SHELVES.forEach(s => {
    const n = hits.filter(p => p._tags.some(t => SHELF_OF[t].key === s.key)).length;
    document.querySelector(`[data-shelfcnt="${s.key}"]`).textContent = n;
  });
  document.getElementById('allbtn').setAttribute('aria-pressed', String(!state.topics.length));

  // active filter pills
  filterbar.innerHTML = '';
  if (state.topics.length) {
    filterbar.insertAdjacentHTML('beforeend', '<span class="flabel">Filtered by</span>');
    state.topics.forEach((t, i) => {
      if (i) filterbar.insertAdjacentHTML('beforeend', '<span class="fand">AND</span>');
      const b = document.createElement('button');
      b.className = 'fpill'; b.style.background = HUE[t];
      b.innerHTML = `${TOPICS[t].label}<span class="x">&times;</span>`;
      b.title = 'Remove this filter';
      b.onclick = () => pickTopic(t, true);
      filterbar.appendChild(b);
    });
    const c = document.createElement('button');
    c.className = 'fclear'; c.textContent = 'Clear';
    c.onclick = () => { state.topics = []; render(); };
    filterbar.appendChild(c);
    if (state.topics.length === 1)
      filterbar.insertAdjacentHTML('beforeend',
        '<div class="fhint">Cmd or shift click another topic, in the sidebar or on any post, to narrow this further.</div>');
  }

  // header
  const names = state.topics.map(t => TOPICS[t].label);
  document.getElementById('crumb').textContent = state.topics.length === 1
    ? `${SHELF_OF[state.topics[0]].label} / ${names[0]}`
    : (state.topics.length ? `${state.topics.length} topics combined` : 'All posts');
  document.getElementById('htitle').textContent =
    names.length ? names.join(' + ') : 'Everything, newest first';
  document.getElementById('hnote').textContent =
    state.topics.length === 1
      ? SHELF_OF[state.topics[0]].note + ' Posts whose main subject is this topic, plus any that touch it.'
      : state.topics.length
        ? 'Posts carrying every one of these topics.'
        : PUBLIC
          ? `${POSTS.length} sales posts sorted into ${Object.keys(TOPICS).length} topics across seven shelves. Each entry shows its opening lines and links to the original; search matches every word in the full post, including transcribed images and video captions.`
          : `A working reference of ${POSTS.length} sales posts, sorted into ${Object.keys(TOPICS).length} topics across seven shelves. Search runs over the full text of every post, including transcribed images and video captions.`;

  // topic shortcuts when the query names a subject rather than a phrase
  topichits.innerHTML = '';
  if (state.terms.length) {
    Object.entries(TOPICS)
      .filter(([k, v]) => state.terms.some(term => v.label.toLowerCase().includes(term))
                          && !state.topics.includes(k))
      .slice(0, 6)
      .forEach(([k, v]) => {
        const b = document.createElement('button');
        b.className = 'topichit';
        b.textContent = `Jump to ${v.label} (${counts[k] || 0})`;
        b.onclick = e => { pickTopic(k, additive(e)); window.scrollTo({top:0}); };
        topichits.appendChild(b);
      });
  }

  const scope = names.length ? ` in ${names.join(' + ')}` : '';
  rescount.textContent = state.terms.length
    ? `${hits.length} post${hits.length === 1 ? '' : 's'}${scope} match "${q.value.trim()}"`
    : `${hits.length} post${hits.length === 1 ? '' : 's'}${scope}`;

  if (!hits.length) {
    const bits = [];
    if (names.length > 1) bits.push(`no post carries all of ${names.join(' + ')}`);
    else if (names.length) bits.push(`nothing in ${names[0]}`);
    if (state.terms.length) bits.push(`nothing contains "${esc(q.value.trim())}"`);
    list.innerHTML = `<div class="empty"><h3>No matches</h3>
      <p>Here, ${bits.join(', and ')}. Search covers post text, authors, headlines,
      transcribed images and video captions.</p>
      <div class="emptyacts">
        ${state.topics.length > 1 ? '<button class="tbtn" id="dropLast">Drop the last topic filter</button>' : ''}
        ${state.topics.length ? '<button class="tbtn" id="clearTopic">Clear topic filters</button>' : ''}
        ${state.terms.length ? '<button class="tbtn" id="clearQ">Clear the search</button>' : ''}
      </div></div>`;
    const dl = document.getElementById('dropLast');
    if (dl) dl.onclick = () => { state.topics = state.topics.slice(0, -1); render(); };
    const ct = document.getElementById('clearTopic');
    if (ct) ct.onclick = () => { state.topics = []; render(); };
    const cq = document.getElementById('clearQ');
    if (cq) cq.onclick = () => { q.value = ''; state.terms = []; render(); };
    return;
  }

  list.innerHTML = hits.map(p => {
    const chips = p._tags.map((t, i) =>
      `<button class="chip ${i === 0 ? 'pri' : ''} ${state.topics.includes(t) ? 'on' : ''}"
               data-topic="${t}" ${i === 0 ? `style="background:${HUE[t]}"` : ''}
               title="Show ${TOPICS[t].label}. Cmd or shift click to add it to the current filters."
      >${TOPICS[t].label}</button>`).join('');
    const badges = [
      p.md ? `<span class="badge">${p.md}</span>` : '',
      p.vt ? '<span class="badge">captions</span>' : '',
      p.rb ? '<span class="badge">repost</span>' : '',
    ].join('');
    return `<article class="post" data-open="0" data-n="${p.n}">
      <button class="ptitlebtn">
        <p class="ptitle">${mark(p.t)}</p><span class="pnum">${p.n}</span>
      </button>
      <div class="pmeta">
        <span class="pauthor">${mark(p.a)}</span>
        <span class="pdate">${p.d}${p.ap ? '~' : ''}</span>
        ${chips}${badges}
      </div>
      <div class="body"></div>
    </article>`;
  }).join('');

  list.querySelectorAll('.post').forEach(art => {
    art.querySelector('.ptitlebtn').onclick = () => toggle(art);
    art.querySelectorAll('.chip[data-topic]').forEach(c => {
      c.onclick = e => { e.stopPropagation();
        pickTopic(c.dataset.topic, additive(e)); window.scrollTo({top:0}); };
    });
  });

  if (hits.length === 1) toggle(list.querySelector('.post'));
}

function toggle(art){
  const open = art.dataset.open === '1';
  art.dataset.open = open ? '0' : '1';
  if (open) return;
  const p = POSTS.find(x => x.n === +art.dataset.n);
  const box = art.querySelector('.body');
  let h = '';
  if (p.rb) h += `<div class="repost"><strong>${esc(p.rb)}</strong> reposted this, adding:
                  ${mark(p.cm || '')}</div>`;
  h += `<div class="text">${para(mark(p.b))}</div>`;
  if (PUBLIC) h += `<p class="clipnote">${p.clip
      ? 'Opening lines only. ' : ''}This library indexes and links to posts; it does
      not republish them.</p>`;
  if (p.mt) h += `<div class="sect"><h4>Transcribed from the attached ${esc(p.mk || p.md)}</h4>
    <p class="note">Read from the rendered post; this was not in the text capture.</p>
    <div class="text">${para(mark(p.mt))}</div></div>`;
  if (p.vt) h += `<div class="sect"><h4>Video captions</h4>
    <p class="note">Auto-generated by LinkedIn, so expect transcription errors and no speaker labels.</p>
    <div class="text">${para(mark(p.vt))}</div></div>`;
  h += `<div class="actions">
    <a href="${p.u}" target="_blank" rel="noopener">Open on LinkedIn</a>
    <span class="pdate">${p.w} words</span></div>`;
  box.innerHTML = h;
}

/* ----------------------------------------------------------------- theme */
const root = document.documentElement, tl = document.getElementById('themelabel');
const isDark = () => root.dataset.theme
  ? root.dataset.theme === 'dark'
  : matchMedia('(prefers-color-scheme:dark)').matches;
const syncLabel = () => tl.textContent = isDark() ? 'Light' : 'Dark';
document.getElementById('themebtn').onclick = () => {
  root.dataset.theme = isDark() ? 'light' : 'dark'; syncLabel();
};
syncLabel();
matchMedia('(prefers-color-scheme:dark)').addEventListener('change', syncLabel);

render();
</script>
"""

if __name__ == "__main__":
    main()
