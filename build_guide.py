#!/usr/bin/env python3
"""
Generate the Field Guide: the consolidation layer over the library.

    python3 build_library.py && python3 build_guide.py

Self-contained. Every [n] pointer embeds its source post, so the guide never
depends on the library page being open, or on any URL staying alive.
"""

import json
import os
import re
import sys
from collections import OrderedDict

from taxonomy import classify, TOPIC_META
from guide_content import SECTIONS

HERE = os.path.dirname(os.path.abspath(__file__))
# --public: the synthesis is mine and ships whole, but the source drawer shows an
# excerpt and links out rather than reprinting someone else's post.
PUBLIC = "--public" in sys.argv
OUT = os.path.join(HERE, "docs", "index.html") if PUBLIC \
    else os.path.join(HERE, "field-guide.html")

EXCERPT_CHARS = 320


def excerpt(text):
    t = re.sub(r"\s+", " ", text).strip()
    if len(t) <= EXCERPT_CHARS:
        return t, False
    cut = t[:EXCERPT_CHARS]
    cut = cut[:cut.rfind(" ")] if " " in cut else cut
    return cut.rstrip(" .,;:") + "...", True


def load_posts():
    posts = json.load(open(os.path.join(HERE, "data", "posts.json")))
    for p in posts:
        extra = (p.get("media_transcript", "") or "") + " " + (p.get("video_transcript", "") or "")
        p["primary"], p["secondary"] = classify(p["title"], p["body"], extra, p["n"])
    return {p["n"]: p for p in posts}


def collect_cites(node, out):
    """Walk the content tree and gather every post number referenced."""
    if isinstance(node, dict):
        for v in node.values():
            collect_cites(v, out)
    elif isinstance(node, (list, tuple)):
        if node and all(isinstance(x, int) for x in node):
            out.update(node)
        else:
            for v in node:
                collect_cites(v, out)


def main():
    posts = load_posts()

    cited = set()
    collect_cites(SECTIONS, cited)
    cited = sorted(n for n in cited if n in posts)

    # only the cited posts travel with the guide, keeping it light
    payload = OrderedDict()
    for n in cited:
        p = posts[n]
        body, clipped = (excerpt(p["body"]) if PUBLIC else (p["body"], False))
        payload[str(n)] = {
            "a": p["author"], "t": p["title"], "d": p["date"], "ap": p["date_approx"],
            "u": p["url"], "b": body,
            "mt": "" if PUBLIC else p.get("media_transcript", ""),
            "mk": p.get("media_kind", ""),
            "vt": "" if PUBLIC else p.get("video_transcript", ""),
            "tp": TOPIC_META[p["primary"]]["label"],
            "clip": clipped,
        }

    nav = [{"id": s["id"], "title": s["title"], "kicker": s["kicker"]} for s in SECTIONS]

    html_body = "".join(render_section(s) for s in SECTIONS)

    page = (TEMPLATE
            .replace("__NAV__", json.dumps(nav, ensure_ascii=True))
            .replace("__POSTS__", json.dumps(payload, ensure_ascii=True, separators=(",", ":")))
            .replace("__BODY__", html_body)
            .replace("__NCITED__", str(len(cited)))
            .replace("__PUBLIC__", "true" if PUBLIC else "false"))

    os.makedirs(os.path.join(HERE, "docs"), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write(page)
    print(f"wrote {OUT}  ({os.path.getsize(OUT)/1024:.0f} KB)")
    print(f"  sections: {len(SECTIONS)}   posts cited: {len(cited)}")


# ------------------------------------------------------------------ rendering
def cites(nums):
    if not nums:
        return ""
    return ('<span class="cites">'
            + "".join(f'<button class="cite" data-n="{n}">{n}</button>' for n in nums)
            + "</span>")


def esc(s):
    return (s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


CITE_RX = re.compile(r"\[(\d+(?:\s*,\s*\d+)*)\]")


def linkify(text):
    """Turn inline [39] / [85, 152] markers into clickable pointers in place.

    Keeps the mapping between a specific claim and its source when a paragraph
    makes several claims, instead of dumping every number at the end.
    """
    def sub(m):
        nums = [x.strip() for x in m.group(1).split(",")]
        return ('<span class="cites">'
                + "".join(f'<button class="cite" data-n="{n}">{n}</button>' for n in nums)
                + "</span>")
    return CITE_RX.sub(sub, esc(text))


def has_inline(text):
    return bool(CITE_RX.search(text))


def render_section(s):
    h = [f'<section class="sec" id="{s["id"]}">',
         f'<div class="kicker">{esc(s["kicker"])}</div>',
         f'<h2>{esc(s["title"])}</h2>',
         f'<p class="lede">{esc(s["lede"])}</p>']

    for b in s["blocks"]:
        t = b["type"]

        if t == "h":
            h.append(f'<h3>{esc(b["h"])}</h3>')

        elif t == "p":
            h.append(f'<p>{linkify(b["p"])}</p>')

        elif t == "finding":
            tail = "" if has_inline(b["p"]) else cites(b.get("cite", []))
            h.append(f'<div class="finding"><h4>{esc(b["h"])}</h4>'
                     f'<p>{linkify(b["p"])}{tail}</p></div>')

        elif t == "bullets":
            h.append('<ul class="pts">')
            for text, c in b["items"]:
                h.append(f'<li>{linkify(text)}{cites(c)}</li>')
            h.append("</ul>")

        elif t == "numbered":
            h.append('<ol class="steps">')
            for title, text, c in b["items"]:
                h.append(f'<li><strong>{esc(title)}</strong>'
                         f'<span>{linkify(text)}{cites(c)}</span></li>')
            h.append("</ol>")

        elif t == "conflict":
            (la, ta, ca), (lb, tb, cb) = b["a"], b["b"]
            h.append(f'<div class="conflict"><h4>{esc(b["h"])}</h4><div class="sides">'
                     f'<div class="side"><span class="slab">{esc(la)}</span>'
                     f'<p>{esc(ta)}{cites(ca)}</p></div>'
                     f'<div class="side"><span class="slab">{esc(lb)}</span>'
                     f'<p>{esc(tb)}{cites(cb)}</p></div></div></div>')

        elif t == "data":
            h.append('<table class="data"><tbody>')
            for label, val in b["rows"]:
                cls = "up" if val.startswith("+") else "down"
                h.append(f'<tr><td>{esc(label)}</td>'
                         f'<td class="num {cls}">{esc(val)}</td></tr>')
            h.append(f'</tbody></table><p class="src">{cites(b.get("cite", []))}</p>')

        elif t == "assets":
            h.append('<table class="assets"><tbody>')
            for name, note, c in b["rows"]:
                n = f'<span class="anote">{esc(note)}</span>' if note else ""
                h.append(f'<tr><td>{esc(name)}{n}</td><td class="ac">{cites(c)}</td></tr>')
            h.append("</tbody></table>")

        elif t == "voices":
            h.append('<table class="voices"><tbody>')
            for name, n, note in b["rows"]:
                h.append(f'<tr><td class="vn">{esc(name)}</td><td class="vc">{n}</td>'
                         f'<td>{esc(note)}</td></tr>')
            h.append("</tbody></table>")

    h.append("</section>")
    return "".join(h)


TEMPLATE = r"""<title>Sales Field Guide</title>
<style>
  :root{
    --bg:#E6E7E2; --surface:#FBFBF9; --surface-2:#F1F2ED;
    --ink:#16191C; --ink-2:#5A6169; --ink-3:#868D94;
    --rule:#CFD2CB; --rule-2:#DEE0DA;
    --accent:#14584C; --accent-soft:#14584C1A;
    --warn:#B4553A; --warn-soft:#B4553A14;
    --up:#14584C; --down:#B4553A;
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
      --warn:#D98A6B; --warn-soft:#D98A6B14;
      --up:#68C4AC; --down:#D98A6B;
    }
  }
  :root[data-theme="dark"]{
    --bg:#121513; --surface:#191D1B; --surface-2:#20241F;
    --ink:#E7E9E4; --ink-2:#9AA29B; --ink-3:#77807A;
    --rule:#2C312E; --rule-2:#242926;
    --accent:#68C4AC; --accent-soft:#68C4AC1F;
    --warn:#D98A6B; --warn-soft:#D98A6B14;
    --up:#68C4AC; --down:#D98A6B;
  }
  :root[data-theme="light"]{
    --bg:#E6E7E2; --surface:#FBFBF9; --surface-2:#F1F2ED;
    --ink:#16191C; --ink-2:#5A6169; --ink-3:#868D94;
    --rule:#CFD2CB; --rule-2:#DEE0DA;
    --accent:#14584C; --accent-soft:#14584C1A;
    --warn:#B4553A; --warn-soft:#B4553A14;
    --up:#14584C; --down:#B4553A;
  }

  *{box-sizing:border-box}
  body{margin:0;background:var(--bg);color:var(--ink);
    font-family:var(--sans);font-size:12px;line-height:1.32;
    -webkit-font-smoothing:antialiased}
  a{color:var(--accent)}

  .wrap{display:grid;grid-template-columns:214px minmax(0,1fr);min-height:100vh}

  .rail{background:var(--surface-2);border-right:1px solid var(--rule);
    padding:18px 0 50px;position:sticky;top:0;height:100vh;overflow-y:auto}
  .brand{padding:0 16px 12px;border-bottom:1px solid var(--rule)}
  .brand h1{margin:0;font-size:11.5px;font-weight:650;letter-spacing:-.005em}
  .brand .sub{margin-top:4px;font-family:var(--mono);font-size:8.8px;
    text-transform:uppercase;letter-spacing:.09em;color:var(--ink-3);line-height:1.4}
  .toc{padding:10px 8px 0;display:flex;flex-direction:column;gap:1px}
  .toc a{display:block;padding:5px 9px;border-radius:4px;text-decoration:none;
    color:var(--ink-2);font-size:11px;line-height:1.32}
  .toc a:hover{background:var(--surface);color:var(--ink)}
  .toc a.on{background:var(--accent-soft);color:var(--accent);font-weight:640}
  .toc .tk{display:block;font-family:var(--mono);font-size:8.2px;
    text-transform:uppercase;letter-spacing:.08em;color:var(--ink-3);margin-bottom:1px}
  .railfoot{padding:12px 16px 0;margin-top:10px;border-top:1px solid var(--rule);
    font-size:10px;color:var(--ink-3);line-height:1.45}

  .main{min-width:0;padding:0 0 90px}
  .topbar{position:sticky;top:0;z-index:20;
    background:color-mix(in srgb,var(--bg) 88%,transparent);backdrop-filter:blur(10px);
    border-bottom:1px solid var(--rule);padding:9px 40px;
    display:flex;justify-content:flex-end;gap:10px}
  .tbtn{border:1px solid var(--rule);background:var(--surface);color:var(--ink-2);
    border-radius:6px;padding:6px 9px;cursor:pointer;font-family:var(--sans);
    font-size:10.5px;display:flex;align-items:center;gap:5px}
  .tbtn:hover{color:var(--ink);border-color:var(--ink-3)}

  .hero{padding:34px 40px 0;max-width:760px}
  .hero h1{font-size:26px;margin:0;letter-spacing:-.022em;font-weight:650;text-wrap:balance}
  .hero .stand{font-family:var(--serif);font-size:15px;line-height:1.45;
    color:var(--ink-2);margin:10px 0 0;max-width:62ch}
  .hero .how{margin:18px 0 0;padding:12px 14px;border:1px solid var(--rule);
    border-radius:6px;background:var(--surface);font-size:11.3px;color:var(--ink-2);
    line-height:1.5;max-width:68ch}
  .hero .how b{color:var(--ink)}

  .sec{padding:34px 40px 0;max-width:760px;scroll-margin-top:56px}
  .kicker{font-family:var(--mono);font-size:9px;text-transform:uppercase;
    letter-spacing:.1em;color:var(--ink-3)}
  .sec h2{font-size:19px;margin:6px 0 0;letter-spacing:-.017em;font-weight:640;text-wrap:balance}
  .sec .lede{font-family:var(--serif);font-size:13.7px;line-height:1.46;color:var(--ink-2);
    margin:8px 0 0;max-width:64ch}
  .sec h3{font-size:11.5px;margin:24px 0 0;font-weight:680;letter-spacing:.005em;
    padding-bottom:5px;border-bottom:1px solid var(--rule)}
  .sec > p{font-size:12px;line-height:1.46;color:var(--ink-2);margin:10px 0 0;max-width:66ch}

  .pts{margin:10px 0 0;padding:0;list-style:none;display:flex;flex-direction:column;gap:8px}
  .pts li{font-size:12px;line-height:1.46;color:var(--ink-2);max-width:70ch;
    padding-left:13px;position:relative}
  .pts li::before{content:"";position:absolute;left:0;top:.52em;width:4px;height:4px;
    border-radius:50%;background:var(--rule);}

  .steps{margin:12px 0 0;padding:0;list-style:none;counter-reset:s;
    display:flex;flex-direction:column;gap:9px}
  .steps li{counter-increment:s;display:grid;grid-template-columns:20px 1fr;gap:9px;
    max-width:70ch}
  .steps li::before{content:counter(s);font-family:var(--mono);font-size:10px;
    color:var(--accent);border:1px solid var(--accent-soft);border-radius:3px;
    height:17px;display:flex;align-items:center;justify-content:center;
    background:var(--accent-soft)}
  .steps strong{display:block;font-size:12px;font-weight:640;color:var(--ink)}
  .steps span{display:block;font-size:12px;line-height:1.46;color:var(--ink-2);margin-top:2px}

  .finding{margin:14px 0 0;padding:13px 15px;border-radius:6px;background:var(--surface);
    border:1px solid var(--rule);border-left:2px solid var(--accent);max-width:70ch}
  .finding h4{margin:0;font-size:12px;font-weight:660;line-height:1.35;text-wrap:balance}
  .finding p{margin:6px 0 0;font-size:12px;line-height:1.46;color:var(--ink-2)}

  .conflict{margin:14px 0 0;padding:13px 15px;border-radius:6px;
    background:var(--warn-soft);border:1px solid var(--rule);max-width:74ch}
  .conflict h4{margin:0 0 9px;font-size:12px;font-weight:660}
  .sides{display:grid;grid-template-columns:1fr 1fr;gap:14px}
  .side .slab{font-family:var(--mono);font-size:8.6px;text-transform:uppercase;
    letter-spacing:.09em;color:var(--warn);font-weight:700}
  .side p{margin:4px 0 0;font-size:11.5px;line-height:1.46;color:var(--ink-2)}

  table{border-collapse:collapse;width:100%;max-width:64ch;margin:12px 0 0}
  td{padding:5px 0;border-bottom:1px solid var(--rule-2);font-size:11.7px;
    color:var(--ink-2);vertical-align:top;line-height:1.4}
  .data .num{text-align:right;font-family:var(--mono);font-variant-numeric:tabular-nums;
    white-space:nowrap;width:1%;padding-left:14px;font-size:11px}
  .data .up{color:var(--up)} .data .down{color:var(--down)}
  .src{margin:7px 0 0}
  .assets{max-width:72ch}
  .assets td:first-child{color:var(--ink)}
  .anote{display:block;font-family:var(--mono);font-size:9px;color:var(--ink-3);
    margin-top:2px;text-transform:uppercase;letter-spacing:.05em}
  .assets .ac{text-align:right;white-space:nowrap;width:1%;padding-left:12px}
  .voices{max-width:74ch}
  .voices .vn{color:var(--ink);font-weight:640;white-space:nowrap;padding-right:10px}
  .voices .vc{font-family:var(--mono);font-size:10px;color:var(--ink-3);
    font-variant-numeric:tabular-nums;text-align:right;width:1%;padding-right:12px}

  .cites{display:inline-flex;gap:3px;margin-left:5px;vertical-align:baseline}
  .cite{font-family:var(--mono);font-size:9px;font-variant-numeric:tabular-nums;
    border:1px solid var(--rule);background:var(--surface);color:var(--ink-3);
    border-radius:3px;padding:1px 4px;cursor:pointer;line-height:1.4}
  .cite:hover{border-color:var(--accent);color:var(--accent);background:var(--accent-soft)}

  /* source drawer */
  .scrim{position:fixed;inset:0;background:#0006;z-index:40;display:none}
  .scrim.on{display:block}
  .drawer{position:fixed;top:0;right:0;height:100vh;width:min(480px,92vw);z-index:41;
    background:var(--surface);border-left:1px solid var(--rule);
    transform:translateX(100%);transition:transform .18s ease;
    display:flex;flex-direction:column}
  .drawer.on{transform:none}
  .dhead{padding:14px 18px;border-bottom:1px solid var(--rule);display:flex;
    justify-content:space-between;align-items:flex-start;gap:12px}
  .dhead h3{margin:0;font-size:12px;font-weight:650;line-height:1.35}
  .dmeta{margin-top:4px;font-size:10px;color:var(--ink-3);display:flex;gap:8px;flex-wrap:wrap}
  .dmeta .pdate{font-family:var(--mono);font-variant-numeric:tabular-nums}
  .dclose{border:0;background:none;color:var(--ink-3);cursor:pointer;font-size:19px;
    line-height:1;padding:0 2px}
  .dclose:hover{color:var(--ink)}
  .dbody{padding:14px 18px 40px;overflow-y:auto}
  .dbody .text{font-family:var(--serif);font-size:13.1px;line-height:1.4;color:var(--ink)}
  .dbody .text p{margin:0 0 .42em}
  .dsect{margin-top:15px;padding-top:11px;border-top:1px solid var(--rule)}
  .dsect h4{margin:0 0 3px;font-family:var(--mono);font-size:9.5px;text-transform:uppercase;
    letter-spacing:.08em;color:var(--ink-2)}
  .dsect .note{font-size:10px;color:var(--ink-3);margin:0 0 8px;line-height:1.4}
  .dfoot{margin-top:16px;font-size:10.5px}
  .clipnote{margin:10px 0 0;font-size:9.8px;color:var(--ink-3);line-height:1.45;
    font-style:italic}
  .xlink{display:block;font-size:10.6px;font-weight:640;color:var(--accent);
    text-decoration:none;margin-bottom:5px}
  .xlink:hover{text-decoration:underline}
  .railfoot p{margin:5px 0 0}

  @media (max-width:980px){
    .wrap{grid-template-columns:1fr}
    .rail{position:static;height:auto;border-right:0;border-bottom:1px solid var(--rule)}
    .topbar,.hero,.sec{padding-left:18px;padding-right:18px}
    .sides{grid-template-columns:1fr;gap:11px}
  }
  @media (prefers-reduced-motion:reduce){*{transition:none!important}}
  :focus-visible{outline:2px solid var(--accent);outline-offset:2px;border-radius:3px}
</style>

<div class="wrap">
  <nav class="rail">
    <div class="brand">
      <h1>Sales Field Guide</h1>
      <div class="sub">Consolidated from<br>292 saved posts</div>
    </div>
    <div class="toc" id="toc"></div>
    <div class="railfoot">
      <a class="xlink" href="library.html">Browse the full library &rarr;</a>
      <p>All 292 posts, 30 topics, search and combinable filters.</p>
      <p style="margin-top:10px;padding-top:9px;border-top:1px solid var(--rule)">
      Every <b>[n]</b> opens the post it came from. __NCITED__ posts are cited here;
      the rest of the library is supporting material.</p>
    </div>
  </nav>

  <main class="main">
    <div class="topbar">
      <button class="tbtn" id="themebtn" title="Toggle light and dark">
        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="4.5"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/>
        </svg>
        <span id="themelabel">Dark</span>
      </button>
    </div>

    <header class="hero">
      <h1>What 292 saved posts actually say</h1>
      <p class="stand">The library sorts your saves by subject. This sorts them by
        argument: what the corpus agrees on once you collapse the repetition, where it
        contradicts itself, and which posts hold the templates worth stealing.</p>
      <div class="how">
        <b>How to read it.</b> Every claim carries the posts it came from. Click any
        numbered pointer to read that post in full, without leaving the page. Nothing
        here asks to be taken on trust.<br>
        <b>Contested</b> marks the places where credible people in this library disagree.
        Those are left unresolved on purpose.
      </div>
    </header>

    __BODY__
  </main>
</div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" aria-hidden="true">
  <div class="dhead">
    <div>
      <h3 id="dtitle"></h3>
      <div class="dmeta" id="dmeta"></div>
    </div>
    <button class="dclose" id="dclose" title="Close">&times;</button>
  </div>
  <div class="dbody" id="dbody"></div>
</aside>

<script>
const NAV = __NAV__, SRC = __POSTS__;
const PUBLIC = __PUBLIC__;

const toc = document.getElementById('toc');
NAV.forEach(s => {
  const a = document.createElement('a');
  a.href = '#' + s.id;
  a.innerHTML = `<span class="tk">${s.kicker}</span>${s.title}`;
  toc.appendChild(a);
});

// highlight the section you are actually reading
const obs = new IntersectionObserver(es => {
  es.forEach(e => {
    if (!e.isIntersecting) return;
    toc.querySelectorAll('a').forEach(a =>
      a.classList.toggle('on', a.getAttribute('href') === '#' + e.target.id));
  });
}, {rootMargin: '-56px 0px -70% 0px'});
document.querySelectorAll('.sec').forEach(s => obs.observe(s));

/* ------------------------------------------------------------ source drawer */
const drawer = document.getElementById('drawer'), scrim = document.getElementById('scrim');
function escape_(s){ return s.replace(/[&<>]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;'}[c])); }
function para(s){
  return escape_(s).split(/\n{2,}/).map(b => b.trim()).filter(Boolean)
    .map(b => `<p>${b.replace(/\n/g,'<br>')}</p>`).join('');
}
function openSrc(n){
  const p = SRC[n];
  if (!p) return;
  document.getElementById('dtitle').textContent = p.t;
  document.getElementById('dmeta').innerHTML =
    `<span><strong>${escape_(p.a)}</strong></span>
     <span class="pdate">${p.d}${p.ap ? '~' : ''}</span>
     <span>${escape_(p.tp)}</span><span class="pdate">post ${n}</span>`;
  let h = `<div class="text">${para(p.b)}</div>`;
  if (PUBLIC) h += `<p class="clipnote">${p.clip ? 'Opening lines only. ' : ''}This
      guide cites and links to posts; it does not republish them.</p>`;
  if (p.mt) h += `<div class="dsect"><h4>Transcribed from the attached ${escape_(p.mk)}</h4>
    <p class="note">Read from the rendered post; not present in the text capture.</p>
    <div class="text">${para(p.mt)}</div></div>`;
  if (p.vt) h += `<div class="dsect"><h4>Video captions</h4>
    <p class="note">Auto-generated, so expect transcription errors.</p>
    <div class="text">${para(p.vt)}</div></div>`;
  h += `<div class="dfoot"><a href="${p.u}" target="_blank" rel="noopener">Open on LinkedIn</a></div>`;
  document.getElementById('dbody').innerHTML = h;
  document.getElementById('dbody').scrollTop = 0;
  drawer.classList.add('on'); scrim.classList.add('on');
  drawer.setAttribute('aria-hidden', 'false');
  document.getElementById('dclose').focus();
}
function closeSrc(){
  drawer.classList.remove('on'); scrim.classList.remove('on');
  drawer.setAttribute('aria-hidden', 'true');
}
document.addEventListener('click', e => {
  const c = e.target.closest('.cite');
  if (c) { openSrc(c.dataset.n); }
});
document.getElementById('dclose').onclick = closeSrc;
scrim.onclick = closeSrc;
document.addEventListener('keydown', e => { if (e.key === 'Escape') closeSrc(); });

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
</script>
"""

if __name__ == "__main__":
    main()
