# antonidemoragas.eu

Personal academic website of Antoni-Italo de Moragas — Associate Professor of Economics, CUNEF Universidad.

## Stack

Single-page static HTML, no build pipeline. Hosted on GitHub Pages with a custom domain.

The page is regenerated from two sources of truth:

- `_bibliography/papers.bib` — every publication, working paper, and work-in-progress entry, in BibTeX, with a `category` field.
- `_news/*.md` — short news entries with date frontmatter (Jekyll-style for compatibility).

`build.py` (Python 3, stdlib only) reads both and rewrites the regions of `index.html` between `<!-- BUILD:START name -->` … `<!-- BUILD:END name -->` markers. Everything else in `index.html` is hand-written: bio, hero, "Currently" strip, teaching table, press list, footer.

## Updating

1. Edit `_bibliography/papers.bib` (add a paper, fix a coauthor) or drop a markdown file into `_news/`.
2. `python build.py`
3. `git add -A && git commit -m "…" && git push`

Live in ~30 seconds. No CI, no Jekyll, no Ruby.

For routine updates you can also just ask Claude in this folder ("new paper out: …", "add a news item") and it will do steps 1–3 for you.

## Layout

```
index.html                       single-file site (CSS inline)
build.py                         regenerates news + publications blocks
CNAME                            www.antonidemoragas.eu
.nojekyll                        tells GitHub Pages to skip Jekyll
_bibliography/papers.bib         publications (single source of truth)
_news/*.md                       news entries (frontmatter + body)
assets/img/prof_pic.jpg          profile photo
assets/pdf/cv.pdf                CV (replace this file when updated)
```

## BibTeX conventions

Each entry needs a `category` field:

- `category={publications}` — peer-reviewed articles and book chapters; rendered under "Published". The first one (most recent) is auto-promoted to "featured" on the homepage.
- `category={working_papers}` — rendered under "Working papers".
- `category={work_in_progress}` — rendered under "Work in progress".

Author names follow al-folio convention: brace `{De Moragas}` to keep it as a single capitalised family name for the BibTeX. The build script lowercases it to `de Moragas` for display and wraps it in `<span class="me">` so the user's name is highlighted.

Recognised link fields: `html` (rendered as "Journal"), `pdf`, `supp` ("Online appendix"), `blog` ("Discussion"), `slides`, `code`, `poster`, `website`.
