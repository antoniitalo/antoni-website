# antonidemoragas.eu

Personal academic website of Antoni-Italo de Moragas — Associate Professor of Economics, CUNEF Universidad.

## Stack

Single-page static HTML, no build pipeline, no CI, no Jekyll, no Ruby. Hosted on GitHub Pages with a custom domain.

`index.html` is the site: one hand-written file with the CSS inline — bio, hero, news, publications, teaching, CV summary, press and footer all live in it.

## Updating

1. Edit `index.html` directly.
2. `git add -A && git commit -m "…" && git push`

Live in ~30 seconds.

For routine updates you can also just ask Claude in this folder ("new paper out: …", "add a news item") and it will do both steps for you.

### Why there is no build script

The site originally shipped with `build.py`, which regenerated the news and publications blocks from `_bibliography/papers.bib` and `_news/*.md`. It was written in May 2026 and never updated, while `index.html` was hand-edited some thirty times after that — abstracts, coauthor homepage links, the 🎵 song links, analytics, new news entries.

By September 2026 running it would have silently deleted all of that, so the script was removed. `_bibliography/papers.bib` and `_news/*.md` are kept only as an archive of the original content; **nothing reads them** and they no longer match what the page shows.

The `<!-- BUILD:START … -->` / `<!-- BUILD:END … -->` comments left in `index.html` are inert section markers. Edit inside them freely.

## Layout

```
index.html                       single-file site (CSS inline)
home/index.html                  redirect stub: /home → / (legacy link)
404.html                         catch-all: any unknown path → /
CNAME                            www.antonidemoragas.eu
.nojekyll                        tells GitHub Pages to skip Jekyll
_bibliography/papers.bib         archive only — not read by anything
_news/*.md                       archive only — not read by anything
assets/img/prof_pic.jpg          profile photo
assets/pdf/cv.pdf                CV — copied from the `cv` repo after rebuilding it there
```
