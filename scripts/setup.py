#!/usr/bin/env python3
"""Setup and health check for deep-paper.

usage: setup.py status                       # JSON: config, dependencies, backend readiness
       setup.py init --answers FILE [--force] # write ~/.config/deep-paper/config.yaml
       setup.py notion-schema                 # CREATE TABLE statement for the Notion database
       setup.py notion-set --data-source ID --database-url URL [--parent-page URL]
                                              # remember the database so every paper goes there

Answers JSON for init (all optional except backend):
{"backend": "html" | "notion" | "both", "language": "en" | "ko", "data_dir": "~/deep-papers",
 "site_title": "Deep Papers", "notion_data_source_id": "...", "categories": ["...", ...]}
"""
from __future__ import annotations

import argparse
import importlib
import json
import shutil
import sys

import yaml

from common import DEFAULTS, SKILL_DIR, config_path, load_config, out

NOTION_COLUMNS = [
    ("Title", "title", "paper title"),
    ("Abbr", "rich_text", "the paper's own short name (method, system, benchmark); may be empty"),
    ("Link", "url", "arXiv PDF URL (or the paper's page)"),
    ("Venue", "rich_text", "e.g. 'ICLR 2026 (Oral)', 'CVPR 2026', or 'arXiv 2026.05'"),
    ("Submitted", "date", "first arXiv submission date (sort Newest first on this column)"),
    ("Category", "multi_select", "broad area; options from taxonomy.categories"),
    ("Tags", "multi_select", "method/topic keywords"),
    ("Added", "created_time", "when the row was created"),
]


def status():
    deps = {}
    for mod in ("requests", "yaml", "bs4", "markdown", "pymupdf"):
        try:
            importlib.import_module(mod)
            deps[mod] = True
        except ImportError:
            deps[mod] = False
    if not deps["pymupdf"]:
        try:
            importlib.import_module("fitz")
            deps["pymupdf"] = True
        except ImportError:
            pass
    cfg_ok = config_path().exists()
    cfg = load_config(required=False)
    problems, next_steps = [], []
    for m in ("requests", "yaml", "bs4", "markdown"):
        if not deps[m]:
            problems.append(f"missing Python package for {m}: pip install -r {SKILL_DIR}/requirements.txt")
    if not deps["pymupdf"]:
        next_steps.append("optional: pip install pymupdf (PDF page numbers, figures of PDF-only papers)")
    if not cfg_ok:
        next_steps.append("run onboarding: choose backend and language, then setup.py init --answers FILE")
    backend = cfg.get("backend")
    if cfg_ok and backend in ("notion", "both") and not (cfg.get("notion") or {}).get("data_source_id"):
        next_steps.append("Notion: create the database (setup.py notion-schema) and set notion.data_source_id")
    out({"configured": cfg_ok, "config": str(config_path()), "skill_dir": str(SKILL_DIR),
         "python": sys.executable, "backend": backend, "language": cfg.get("language"),
         "data_dir": str(cfg["data_dir"]), "deps": deps,
         "tools": {"rsvg-convert": bool(shutil.which("rsvg-convert"))},
         "problems": problems, "next_steps": next_steps})


def init(answers_path: str, force: bool):
    p = config_path()
    if p.exists() and not force:
        raise SystemExit(f"{p} exists; use --force to replace it (the old file is kept as .bak)")
    a = json.loads(open(answers_path, encoding="utf-8").read())
    backend = a.get("backend", "html")
    if backend not in ("html", "notion", "both"):
        raise SystemExit("backend must be html, notion or both")
    cfg = {
        "language": a.get("language", "en"),
        "backend": backend,
        "data_dir": a.get("data_dir", DEFAULTS["data_dir"]),
        "html": {"title": a.get("site_title", DEFAULTS["html"]["title"])},
        "notion": {"data_source_id": a.get("notion_data_source_id"),
                   "token_file": a.get("notion_token_file")},
        "taxonomy": {"categories": a.get("categories") or DEFAULTS["taxonomy"]["categories"],
                     "allow_new_options": a.get("allow_new_options", True)},
        "figures": DEFAULTS["figures"],
        "venues": a.get("venues", "auto"),
        "check": DEFAULTS["check"],
    }
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.with_suffix(".yaml.bak").write_text(p.read_text(encoding="utf-8"), encoding="utf-8")
    p.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
    out({"config": str(p), **cfg})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("action", choices=["status", "init", "notion-schema", "notion-set"])
    ap.add_argument("--answers")
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--data-source")
    ap.add_argument("--database-url")
    ap.add_argument("--parent-page")
    args = ap.parse_args()
    if args.action == "notion-set":
        p = config_path()
        if not p.exists():
            raise SystemExit("run setup.py init first")
        cfg = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
        ds = (args.data_source or "").replace("collection://", "")
        if not ds:
            raise SystemExit("--data-source is required")
        cfg.setdefault("notion", {}).update({"data_source_id": ds, "database_url": args.database_url,
                                             "parent_page": args.parent_page})
        p.write_text(yaml.safe_dump(cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
        out({"notion": cfg["notion"]})
        return
    if args.action == "status":
        status()
    elif args.action == "init":
        if not args.answers:
            raise SystemExit("init needs --answers FILE")
        init(args.answers, args.force)
    else:
        cfg = load_config(required=False)
        colors = ["blue", "purple", "orange", "green", "yellow", "pink", "red", "brown", "gray", "default"]
        cats = ", ".join(f"'{c}':{colors[i % len(colors)]}" for i, c in enumerate(cfg["taxonomy"]["categories"]))
        ddl = ('CREATE TABLE ("Title" TITLE, "Abbr" RICH_TEXT, "Link" URL, "Venue" RICH_TEXT, '
               f'"Submitted" DATE, "Category" MULTI_SELECT({cats}), "Tags" MULTI_SELECT(), "Added" CREATED_TIME)')
        out({"title": "Papers", "schema": ddl,
             "columns": [{"name": n, "type": t, "meaning": m} for n, t, m in NOTION_COLUMNS],
             "next": "notion-create-database with parent = the user's page and this schema; then "
                     "setup.py notion-set --data-source <collection id> --database-url <url> --parent-page <page url>"})


if __name__ == "__main__":
    main()
