# Onboarding

Talk in the user's language. Ask once for the choices below, use defaults for anything not given,
then write the config. Never ask for a token in chat.

1. **Backend**: `html` (a static site in a local folder; open it, serve it, or host it), `notion`
   (one database row per paper), or `both`.
2. **Write-up language**: `en`, or `ko` (Korean sentences with English technical terms).
   Other languages work the same way: Korean-style rules apply to any non-English choice.
3. **Data folder** (default `~/deep-papers`): working files for every paper and, for HTML, the site.
4. **Categories** (optional): the broad areas used for the `category` field. Default list:
   LLM, Reasoning, Agents, Vision-Language, Computer Vision, Generative Models, Video, 3D, Robotics,
   Reinforcement Learning, Efficient ML, Theory, Benchmark, Survey.
5. **Notion only**: an existing database to use, or create a new one (below).

Write the answers to a temporary JSON file outside the skill folder and run:

```bash
python3 <skill_dir>/scripts/setup.py init --answers /tmp/deep-paper-answers.json
python3 <skill_dir>/scripts/setup.py status
```

Answers format: `{"backend": "html", "language": "ko", "data_dir": "~/deep-papers",
"site_title": "Deep Papers", "categories": [...], "notion_data_source_id": "..."}`.

## Notion database

1. The Notion MCP server must be connected (`claude mcp add --transport http notion
   https://mcp.notion.com/mcp`, then authenticate with `/mcp`).
2. `setup.py notion-schema` lists the columns. Create the database with the Notion MCP
   create-database tool under a page the user names (or have the user create it), with
   `Category` options from the config.
3. Put the database's **data source id** in `notion.data_source_id` (fetch the database with the
   Notion tools to read it).
4. Optional, only for figures of papers without arXiv HTML: an internal integration token
   (notion.so/my-integrations, connected to the database). Store it in a file with mode 600 and
   set `notion.token_file`, or export `NOTION_TOKEN`. Without it those figures are skipped and
   reported.

## Python dependencies

```bash
python3 -m venv ~/.local/share/deep-paper/venv
~/.local/share/deep-paper/venv/bin/pip install -r <skill_dir>/requirements.txt
```

Use that Python for all scripts. PyMuPDF is optional but gives PDF page numbers (page buttons in
the HTML view) and figures for PDF-only papers.
