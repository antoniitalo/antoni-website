#!/usr/bin/env python3
"""Regenerate the news + publications blocks of index.html from
_news/*.md and _bibliography/papers.bib.

Single source of truth: the BibTeX file. Add a paper there, run
`python build.py`, push. No Jekyll, no dependencies — just stdlib.
"""

from __future__ import annotations
import html
import re
from pathlib import Path

ROOT = Path(__file__).parent
INDEX = ROOT / "index.html"
BIB = ROOT / "_bibliography" / "papers.bib"
NEWS_DIR = ROOT / "_news"

def _esc(s: str) -> str:
    """HTML-escape body text without touching apostrophes/quotes (which
    don't need escaping outside attribute values and look ugly in source)."""
    return html.escape(s, quote=False)

# ─── BibTeX parsing ──────────────────────────────────────────────────────

def parse_bibtex(text: str) -> list[dict]:
    """Tiny BibTeX parser. Handles {nested {braces}} and quoted values.
    Skips @string{} preludes. Field names are lowercased."""
    entries = []
    i = 0
    n = len(text)
    while i < n:
        m = re.search(r"@(\w+)\s*\{", text[i:])
        if not m:
            break
        etype = m.group(1).lower()
        i += m.end()
        if etype == "string":
            depth = 1
            while i < n and depth:
                depth += (text[i] == "{") - (text[i] == "}")
                i += 1
            continue
        # entry key
        key_end = text.find(",", i)
        key = text[i:key_end].strip()
        i = key_end + 1
        fields = {}
        while i < n:
            while i < n and text[i] in " \t\r\n":
                i += 1
            if i >= n or text[i] == "}":
                i += 1
                break
            eq = text.find("=", i)
            if eq < 0:
                break
            fname = text[i:eq].strip().lower()
            i = eq + 1
            while i < n and text[i] in " \t\r\n":
                i += 1
            if i < n and text[i] == "{":
                depth = 1
                i += 1
                start = i
                while i < n and depth:
                    depth += (text[i] == "{") - (text[i] == "}")
                    if depth: i += 1
                fields[fname] = text[start:i]
                i += 1
            elif i < n and text[i] == '"':
                i += 1
                start = i
                while i < n and text[i] != '"':
                    i += 1
                fields[fname] = text[start:i]
                i += 1
            else:
                start = i
                while i < n and text[i] not in ",}\n":
                    i += 1
                fields[fname] = text[start:i].strip()
            while i < n and text[i] in " \t\r\n":
                i += 1
            if i < n and text[i] == ",":
                i += 1
        entries.append({"type": etype, "key": key, "fields": fields})
    return entries

# ─── Author / journal / year helpers ─────────────────────────────────────

ME_LAST = "de Moragas"  # display form (lowercase nobiliary 'de')
ME_FULL = "Antoni-Italo de Moragas"

def fmt_author(name: str) -> str:
    """'{De Moragas}, Antoni-Italo' → 'Antoni-Italo de Moragas' (lowercased)."""
    name = name.replace("{De Moragas}", "<<ME>>")
    name = name.replace("{", "").replace("}", "").strip()
    if "," in name:
        last, first = [p.strip() for p in name.split(",", 1)]
        out = f"{first} {last}"
    else:
        out = name
    return out.replace("<<ME>>", ME_LAST)

def fmt_authors(field: str) -> str:
    """Format a BibTeX 'author' field into a comma-separated HTML string,
    wrapping the user's name in <span class='me'>."""
    parts = re.split(r"\s+and\s+", field.strip())
    formatted = []
    for p in parts:
        a = fmt_author(p)
        if ME_LAST in a:
            a = f'<span class="me">{_esc(a)}</span>'
        else:
            a = _esc(a)
        formatted.append(a)
    return ", ".join(formatted)

def fmt_year(f: dict) -> str:
    return str(f.get("year", "")).strip()

# ─── Paper rendering ─────────────────────────────────────────────────────

LINK_KEYS = [
    ("html",  "Journal"),
    ("pdf",   "PDF"),
    ("supp",  "Online appendix"),
    ("blog",  "Discussion"),
    ("slides","Slides"),
    ("code",  "Code"),
    ("poster","Poster"),
    ("website","Website"),
]

def fmt_links(f: dict) -> str:
    bits = []
    for key, label in LINK_KEYS:
        url = f.get(key)
        if url:
            bits.append(f'<a href="{_esc(url.strip())}">{label}</a>')
    if not bits:
        return ""
    return '\n    <div class="links">\n      ' + "\n      ".join(bits) + "\n    </div>"

def render_published(e: dict, featured: bool=False) -> str:
    f = e["fields"]
    title = _esc(f.get("title", "").strip())
    authors = fmt_authors(f.get("author", ""))
    year = fmt_year(f)
    if e["type"] == "incollection":
        venue = _esc(f.get("booktitle", "").strip())
        publisher = f.get("publisher", "").strip()
        venue_html = f'<span class="venue">{venue}</span>' + (
            f' &middot; {_esc(publisher)}' if publisher else "")
    else:
        journal = _esc(f.get("journal", "").strip())
        venue_html = journal
    cls = "paper published" + (" featured" if featured else "")
    return (
        f'  <li class="{cls}">\n'
        f'    <div class="t">{title}</div>\n'
        f'    <div class="a">{authors}</div>\n'
        f'    <div class="j">{venue_html}<span class="yr">, {year}</span></div>'
        f'{fmt_links(f)}\n'
        f'  </li>'
    )

def render_unpublished(e: dict, label: str) -> str:
    f = e["fields"]
    title = _esc(f.get("title", "").strip())
    authors = fmt_authors(f.get("author", ""))
    year = fmt_year(f)
    month = f.get("month", "").strip()
    line = label
    if month and year:
        line = f"{label} &middot; {month} {year}"
    elif year:
        line = f"{label} &middot; {year}"
    return (
        f'  <li class="paper wp">\n'
        f'    <div class="t">{title}</div>\n'
        f'    <div class="a">{authors}</div>\n'
        f'    <div class="j">{line}</div>'
        f'{fmt_links(f)}\n'
        f'  </li>'
    )

# ─── News rendering ──────────────────────────────────────────────────────

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]

def md_to_html(text: str) -> str:
    """Minimal markdown → HTML for our news bodies. Order matters: links
    first (so ** inside link text is preserved), then bold, then italic."""
    text = text.strip()
    # Links: [text](url)
    text = re.sub(r"\[([^\]]+)\]\(([^)]+)\)",
                  lambda m: f'<a href="{m.group(2).strip()}">{m.group(1)}</a>',
                  text)
    # Bold: **text**
    text = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", text)
    # Italic: *text* (but not ** which is already gone) and _text_
    text = re.sub(r"(?<![*\w])\*([^*\n]+)\*(?![*\w])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![_\w])_([^_\n]+)_(?![_\w])", r"<em>\1</em>", text)
    # Collapse whitespace runs to single space
    text = re.sub(r"\s+", " ", text)
    return text

def parse_news_file(path: Path) -> tuple[str, str, str]:
    """Returns (date_label, sort_key, body_html). date_label like 'Jan 2026'."""
    raw = path.read_text(encoding="utf-8")
    fm_match = re.match(r"---\s*\n(.*?)\n---\s*\n(.*)", raw, re.DOTALL)
    if not fm_match:
        raise ValueError(f"No frontmatter in {path}")
    fm, body = fm_match.group(1), fm_match.group(2)
    date_match = re.search(r"^date:\s*(\d{4}-\d{2}-\d{2})", fm, re.MULTILINE)
    if not date_match:
        # fall back to filename: 2026-01-10-...
        fn_match = re.match(r"(\d{4})-(\d{2})-(\d{2})", path.name)
        if not fn_match:
            raise ValueError(f"No date in {path}")
        y, mo, d = fn_match.groups()
    else:
        y, mo, d = date_match.group(1).split("-")
    label = f"{MONTHS[int(mo)-1]} {y}"
    sort_key = f"{y}{mo}{d}"
    return label, sort_key, md_to_html(body)

# ─── Marker injection ────────────────────────────────────────────────────

def inject(text: str, name: str, content: str) -> str:
    pat = re.compile(
        rf"(<!-- BUILD:START {name} -->)(.*?)(<!-- BUILD:END {name} -->)",
        re.DOTALL,
    )
    if not pat.search(text):
        raise RuntimeError(f"Markers not found for '{name}' in index.html")
    block = "\n" + content.rstrip() + "\n"
    return pat.sub(lambda m: m.group(1) + block + m.group(3), text)

# ─── Main ────────────────────────────────────────────────────────────────

def main() -> None:
    bib = parse_bibtex(BIB.read_text(encoding="utf-8"))

    # Group by `category` field. Fall back to type-based heuristics.
    pubs, working, wip = [], [], []
    for e in bib:
        cat = e["fields"].get("category", "").strip().lower()
        if cat == "publications":
            pubs.append(e)
        elif cat == "working_papers":
            working.append(e)
        elif cat == "work_in_progress":
            wip.append(e)
        elif e["type"] == "article" or e["type"] == "incollection":
            pubs.append(e)
        elif e["type"] == "unpublished":
            working.append(e)

    # Sort each group by year descending. Ties → keep BibTeX order
    # (first one in the file ranks first within a year, which lets
    # the user prioritise the featured paper by ordering the .bib).
    yr = lambda e: int(e["fields"].get("year", "0") or 0)
    pubs.sort(key=yr, reverse=True)
    working.sort(key=yr, reverse=True)
    wip.sort(key=yr, reverse=True)

    # Render published, with the first one (most recent) featured.
    pub_html = "\n\n".join(
        render_published(e, featured=(idx == 0))
        for idx, e in enumerate(pubs)
    )
    wp_html = "\n\n".join(render_unpublished(e, "Working paper") for e in working)
    wip_html = "\n\n".join(render_unpublished(e, "Work in progress") for e in wip)

    # News
    news = sorted(
        (parse_news_file(p) for p in NEWS_DIR.glob("*.md")),
        key=lambda t: t[1],
        reverse=True,
    )
    news_html = "\n".join(
        f'  <li><span class="date">{label}</span>'
        f'<span class="body">{body}</span></li>'
        for label, _, body in news
    )

    # Inject
    text = INDEX.read_text(encoding="utf-8")
    text = inject(text, "news", news_html)
    text = inject(text, "published", pub_html)
    text = inject(text, "working", wp_html)
    text = inject(text, "wip", wip_html)
    INDEX.write_text(text, encoding="utf-8")

    print(f"✓ regenerated index.html")
    print(f"  news:       {len(news)} entries")
    print(f"  published:  {len(pubs)}")
    print(f"  working:    {len(working)}")
    print(f"  in progress:{len(wip)}")

if __name__ == "__main__":
    main()
