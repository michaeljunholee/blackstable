"""Emit pre-rendered JSON files for client-side dashboard consumption.

The output is a small set of curated fields per row — not a full CSV dump.
Browser-loadable size budget: ~1MB total across all JSON files.
"""
import json
from pathlib import Path
import pandas as pd

# Fields exported per record. Add fields here intentionally; do not
# blanket-export the full row.
EVENT_FIELDS = [
    "action_id", "action_date", "mechanism_type", "target_identifier",
    "target_category", "chain", "trigger_id", "status", "confidence",
    "notes_path", "issuer",
]
TRIGGER_FIELDS = [
    "trigger_id", "trigger_date", "trigger_type", "description",
]
ENTITY_FIELDS = [
    "entity_id", "entity_name", "entity_type", "circle_relationship",
]


def _records(df: pd.DataFrame, fields: list[str]) -> list[dict]:
    """Return DataFrame as list-of-dict, restricted to `fields`. NaN → None."""
    available = [c for c in fields if c in df.columns]
    sub = df[available].copy()
    return sub.where(sub.notna(), None).to_dict(orient="records")


def emit_events_json(actions: pd.DataFrame, impls: pd.DataFrame, out_path: Path) -> None:
    merged = actions.merge(impls[["implementation_id", "chain"]], on="implementation_id")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(_records(merged, EVENT_FIELDS), default=str), encoding="utf-8")


def emit_triggers_json(triggers: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(_records(triggers, TRIGGER_FIELDS), default=str), encoding="utf-8")


def emit_entities_json(entities: pd.DataFrame, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(_records(entities, ENTITY_FIELDS), default=str), encoding="utf-8")
