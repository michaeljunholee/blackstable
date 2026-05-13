#!/usr/bin/env python
"""Build the public-facing dashboard from CSVs + Markdown notes.

This is the single entry point. Reads canonical data from data/, renders
HTML pages from Jinja2 templates in scripts/build/templates/, and emits
JSON data files for client-side consumption.

Usage:
    python scripts/03_build_html.py [--output-dir docs/dashboard] [--issuers Circle]
"""
import argparse
import shutil
import sys
from pathlib import Path

# Ensure repo root is on sys.path so that `scripts.build.*` imports work
# whether the script is run as `python scripts/03_build_html.py` or via pytest.
_HERE = Path(__file__).resolve()
_REPO_ROOT = _HERE.parents[1]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import pandas as pd
import yaml
from jinja2 import Environment, FileSystemLoader, select_autoescape

from scripts.build.data_export import emit_events_json, emit_triggers_json, emit_entities_json

REPO = _REPO_ROOT
DATA_DIR = REPO / "data"
TEMPLATE_DIR = REPO / "scripts" / "build" / "templates"
STATIC_DIR = REPO / "scripts" / "build" / "static"
NOTES_DIR = REPO / "notes"
SOURCES_DIR = REPO / "sources"
DEFAULT_OUTPUT = REPO / "docs" / "dashboard"
SITE_CONFIG = REPO / "scripts" / "build" / "site_config.yaml"


def df_to_records(df: pd.DataFrame) -> list[dict]:
    """Convert DataFrame to list[dict] with NaN→None.

    Required because Jinja's selectattr / boolean-context use raises on
    DataFrames. Use this anywhere a DataFrame needs to enter Jinja or JSON.
    """
    return df.where(df.notna(), None).to_dict(orient="records")


PAGES = [
    "index",
    "timeline",
    "explore",
    "clusters",
    "entities",
    "triggers",
    "sources",
    "notes",
    "methodology",
]


def load_site_config() -> dict:
    if SITE_CONFIG.exists():
        with open(SITE_CONFIG) as f:
            return yaml.safe_load(f) or {}
    return {}


def load_data(issuers: list[str]) -> dict:
    """Load and filter all CSVs to the requested issuers."""
    actions = pd.read_csv(DATA_DIR / "actions.csv")
    impl = pd.read_csv(DATA_DIR / "implementations.csv")
    triggers = pd.read_csv(DATA_DIR / "triggers.csv")
    entities = pd.read_csv(DATA_DIR / "entities.csv")
    sources = pd.read_csv(DATA_DIR / "sources.csv")

    def _filter_by_issuer(df: pd.DataFrame) -> pd.DataFrame:
        if "issuer" not in df.columns:
            return df
        # Allow 'Circle,Tether' rows for any selected issuer
        mask = df["issuer"].isin(issuers) | df["issuer"].apply(
            lambda v: any(i in str(v).split(",") for i in issuers)
        )
        return df[mask].copy()

    return {
        "actions": _filter_by_issuer(actions),
        "implementations": _filter_by_issuer(impl),
        "triggers": _filter_by_issuer(triggers),
        "entities": _filter_by_issuer(entities),
        "sources": _filter_by_issuer(sources),
    }


def render_pages(env: Environment, data: dict, output_dir: Path, site_config: dict) -> None:
    # Convert DataFrames to lists of dicts for Jinja2 template consumption.
    # DataFrames don't support truthiness tests used in selectattr / boolean checks.
    template_data = {
        k: df_to_records(v) if hasattr(v, "to_dict") else v
        for k, v in data.items()
    }
    for page in PAGES:
        template = env.get_template(f"{page}.html.j2")
        html = template.render(**template_data, page=page, site_config=site_config)
        (output_dir / f"{page}.html").write_text(html, encoding="utf-8")


def emit_json_data(data: dict, output_dir: Path) -> None:
    """Pre-render JSON data files for client-side JS consumption."""
    out = output_dir / "data"
    emit_events_json(data["actions"], data["implementations"], out / "events.json")
    emit_triggers_json(data["triggers"], out / "triggers.json")
    emit_entities_json(data["entities"], out / "entities.json")


def copy_static(output_dir: Path) -> None:
    """Copy static assets (CSS, JS) from scripts/build/static/ to dashboard."""
    target = output_dir / "assets"
    target.mkdir(parents=True, exist_ok=True)
    if STATIC_DIR.exists():
        for f in STATIC_DIR.iterdir():
            if f.is_file():
                shutil.copy(f, target / f.name)


def render_notes(env: Environment, data: dict, output_dir: Path, site_config: dict) -> None:
    """Render each Markdown note as an HTML page under docs/dashboard/notes/."""
    from scripts.build.notes_render import render_note_to_html
    notes_out = output_dir / "notes"
    notes_out.mkdir(parents=True, exist_ok=True)
    for md_file in sorted(NOTES_DIR.glob("*.md")):
        if md_file.name.startswith("_"):
            continue
        html = render_note_to_html(md_file, env, data, site_config)
        (notes_out / f"{md_file.stem}.html").write_text(html, encoding="utf-8")


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--output-dir", default=str(DEFAULT_OUTPUT), type=Path)
    p.add_argument("--issuers", default="Circle",
                   help="Comma-separated list of issuers to include (default: Circle)")
    args = p.parse_args()

    issuers = [i.strip() for i in args.issuers.split(",") if i.strip()]
    if not issuers:
        print("ERROR: --issuers must contain at least one issuer", file=sys.stderr)
        return 1

    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        autoescape=select_autoescape(["html", "j2", "html.j2"]),
    )

    site_config = load_site_config()
    data = load_data(issuers)

    render_pages(env, data, out, site_config)
    emit_json_data(data, out)
    copy_static(out)
    render_notes(env, data, out, site_config)

    print(f"build complete: {len(data['actions'])} actions for issuers={issuers}")
    print(f"output: {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
