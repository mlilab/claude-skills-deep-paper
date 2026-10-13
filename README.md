# Deep Paper

Deep Paper is a Claude Code skill for reading one research paper in depth. It writes a
section-by-section study of the paper that you can use for related work, reproduction, or a
reading group, and saves it to a **Notion database** or a **static HTML site** where the
write-up and the original PDF sit side by side.

It is the opposite of a digest: one paper at a time, nothing dropped.

## What it does

| Feature | What you get |
| --- | --- |
| Follows the paper | One heading per section and subsection, in the paper's order, with the original titles. Every paragraph is represented; enumerations, numbers and comparisons become lists and tables (prose ≤ 30%). |
| Figures in place | 6-8 main-body figures, each matched to its number through its caption (not the file order), placed where the text first mentions it. Appendix figures are left out. |
| Linked citations | Every cited model, method or dataset is a link to its source. Links come from the paper's bibliography or an arXiv title search, never from the model's memory. |
| Venue check | Title match against official accepted-paper lists (ICLR, ICML, NeurIPS, CVPR, ICCV, ECCV, WACV). arXiv comments alone are not trusted. |
| Quality check | `check.py` flags missing sections, over-compressed sections, too much prose, misplaced or unknown figures, and links that are not in the bibliography. |
| Notion backend | One database row per paper (Title, Abbr, Link, Venue, Submitted, Category, Tags) with the write-up as the page: callouts, toggles, tables and figures. |
| HTML backend | A static site: an index of all papers (sort, filter, search) and a split view per paper. The PDF renders next to the write-up; a click on a section's `p.N` jumps the PDF to that page. |
| Languages | English, or Korean sentences with English technical terms (other languages work the same way). |

## Requirements

- Claude Code (or another agent that reads `SKILL.md` skills).
- Python 3.9+ with `requirements.txt` (`requests`, `pyyaml`, `beautifulsoup4`, `markdown`; `pymupdf`
  is optional and gives PDF page numbers and figures for papers without arXiv HTML).
- Notion backend: the Notion MCP server (`claude mcp add --transport http notion
  https://mcp.notion.com/mcp`). An integration token is needed only to upload figures of
  papers that have no arXiv HTML.

## Install

```bash
git clone <this repository> ~/.claude/skills/deep-paper
python3 -m venv ~/.local/share/deep-paper/venv
~/.local/share/deep-paper/venv/bin/pip install -r ~/.claude/skills/deep-paper/requirements.txt
~/.local/share/deep-paper/venv/bin/python ~/.claude/skills/deep-paper/scripts/setup.py status
```

Check that `SKILL.md` is directly inside the installed folder.

## First run

Ask Claude: **"Set up Deep Paper."** It asks for:

1. the backend: `html`, `notion`, or `both`;
2. the write-up language;
3. the data folder (default `~/deep-papers`) and, optionally, your category list;
4. for Notion, an existing database or a page under which to create one.

Settings live in `~/.config/deep-paper/config.yaml`; see [config.example.yaml](config.example.yaml).

## Use

| Ask | Result |
| --- | --- |
| "Read this paper in depth: https://arxiv.org/abs/2610.07018" | A full write-up in the configured backend |
| "Add *Attention Is All You Need* to my paper DB" | Title search on arXiv, then the same |
| "Deep-read these 6 papers for my related work: …" | One subagent per paper, five at a time |
| "Open the paper site" | `scripts/serve.py`, then http://127.0.0.1:8010/ |

## How it works

```
resolve.py  title / id / URL → one verified arXiv record, duplicate check
fetch.py    arXiv HTML (title-checked) or PDF → content.md, outline, figures (number ↔ caption ↔ image), refs, PDF pages
refs.py     arXiv links for cited works that the bibliography does not link
venue.py    official accepted lists → venue + evidence
(Claude)    reads everything, writes summary.md by references/writing_guide.md
check.py    structure, coverage, prose share, figures, links
render.py   HTML split view + index        notion_md.py  Notion page + row properties
```

## Notes

- arXiv PDFs are rendered from arxiv.org in the browser and are not copied into the site.
  Write-ups include figures from the papers: keep a public site in line with the papers' licenses.
- The venue lists are cached in `~/.cache/deep-paper/` for 14 days.
