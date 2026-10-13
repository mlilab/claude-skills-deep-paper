# HTML backend

`render.py` turns every `summary.md` into a static site under `data_dir`:

```
<data_dir>/
├── index.html            all papers: sortable table, category filter, search
├── index.json            the same data as JSON (title, abbr, venue, submitted, category, tags, tldr)
├── assets/               style.css, app.js
└── papers/<id>/
    ├── index.html        split view: write-up | original PDF
    ├── figures/          figure images
    └── summary.md, content.md, meta.json, ...
```

## Split view

- Left: the write-up (title, authors, venue, links, chips, 3-line TL;DR, then the body).
- Right: the original PDF rendered with PDF.js (loaded from cdnjs). arXiv PDFs are fetched
  straight from arxiv.org, which allows it; non-arXiv papers use the local `paper.pdf`.
- Each section heading and figure has a `p.N` button that scrolls the PDF to that page.
- Modes: split, write-up only, PDF only; drag the divider to resize. On narrow screens the two
  panes become tabs. The choice is remembered in the browser.

## Viewing and hosting

- `serve.py` serves the folder at http://127.0.0.1:8010/ (forward the port for a remote machine).
- Opening `index.html` from disk also works in most browsers.
- To host it, publish the folder as static files (GitHub Pages, any web server). The PDFs are not
  copied into the site for arXiv papers; local `paper.pdf` files are, so do not publish
  non-arXiv PDFs you may not redistribute. Write-ups contain figures from the papers: keep the
  site private or check the papers' licenses before making it public.

## Re-rendering

`render.py --all` rebuilds every page (after a template update or a config change);
`render.py --index` rebuilds only the index.
