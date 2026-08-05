# Sales Tips Library

Two static pages built from 292 sales posts I had saved on LinkedIn over about
five years, and never once gone back to read.

**[Field Guide](https://eric-hastie.github.io/sales-tips-library/)** - what the
292 posts actually say, consolidated by argument rather than by subject: the
places dozens of practitioners independently agree, the six places they flatly
contradict each other, and an index of the templates worth stealing.

**[Library](https://eric-hastie.github.io/sales-tips-library/library.html)** -
all 292 posts sorted into 30 topics across seven shelves, with full-text search
and combinable topic filters.

## What is published here

The published pages **index and link to** these posts. They show each post's
opening lines, its author, date and topics, and a link to the original on
LinkedIn. They do not reproduce anyone's post in full: the writing belongs to
the people who wrote it.

Search still works across the whole corpus. Each post ships a sorted set of its
unique words, which is enough to match a query and not enough to reassemble the
post from. The trade-off is that phrase search does not work in the published
version, only word matching.

The corpus itself is not in this repo, by design. See `.gitignore`.

## How it was built

A capture step, a classifier, and two generators.

```
taxonomy.py        the two-level topic scheme and the classifier
build_library.py   raw capture  ->  per-post markdown + indexes
build_page.py      ->  the browsable, searchable library page
guide_content.py   the consolidation: claims, conflicts, pointers
build_guide.py     ->  the field guide page
```

Rebuild the published pair with:

```bash
python3 build_library.py
python3 build_page.py  --public     # docs/library.html
python3 build_guide.py --public     # docs/index.html
```

Both pages are single self-contained files. No build step, no dependencies, no
network calls, no analytics. They work opened from disk.

### Capture

The saved-posts list renders every post's full text in the DOM. The visible
"...see more" is CSS line-clamping, not truncation, so the whole corpus came out
of one page rather than 292 page loads.

Two things that read as complete but were not, and were only caught by checking
rather than assuming:

- **Reposts.** The list carries only the reposter's one-line commentary, so four
  posts arrived with bodies as short as 12 characters. Each original had to be
  fetched from its own page.
- **Media-only posts.** Eleven posts were a short caption over an image, carousel
  or linked article, where the substance was in the media. LinkedIn's alt text is
  a useless "Image preview". Where the platform had OCR'd a document into the page
  images' alt attributes, that recovered the text; where it had not, the slides had
  to be read. Nine of fifteen videos had English captions that `yt-dlp` pulls
  without auth.

### Classification

Weighted keyword matching over a hand-built taxonomy, with title matches counted
double. It is a heuristic, not judgement, and it was tuned against real errors:
a cold-call post exiled to "off topic" by the word "podcast" deep in its body, a
post about a VP *hiring* AEs filed under executive access because of "VP of", a
deal-rescue post filed under cold calling because it said "pick up the phone".
Expect a handful still sitting one topic away from ideal.

Each post gets one primary topic, so it appears exactly once in the navigation,
plus secondary topics so search and the AND filters can still find it.

### Dates

Derived from LinkedIn's relative timestamps. Day-level ages are near exact;
anything shown as weeks, months or years is marked approximate and can be off by
up to that unit. LinkedIn is inconsistent with itself here: one post showed "4yr"
in the list and "3yr" on its own page.

## Credit

The thinking belongs to the people who wrote these posts. The most-cited here are
Kyle Asay, Josh Braun, Ian Koniak, Chris Orlob, Justin Michael, Brian LaManna,
Isaiah Crossman and Kyle Coleman, among 140 authors in total. Every claim in the
Field Guide carries a pointer to the post it came from, and every post links back
to its author.
