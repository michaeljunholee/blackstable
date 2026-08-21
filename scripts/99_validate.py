#!/usr/bin/env python3
"""CircleUSDC dataset validation.

Run before every commit touching `data/`. Exits non-zero on any error.

Checks:
    1. Every CSV exists and has the canonical header.
    2. Every data row has exactly len(header) comma-separated fields.
    3. Every primary key is non-empty and unique within its table.
    4. Every enum value is in its canonical enum list.
    5. Every foreign key resolves to an existing primary key.
    6. Required date orderings hold (reversal_date >= action_date, etc.).
    7. No date field is in the future (likely typo).
    8. Every YES / NO entity classification has at least one source_id.
    9. Every cited source in `sources.csv` with a `local_path` and `content_sha256`
       matches the file on disk (tamper detection).
"""
from __future__ import annotations

import csv
import hashlib
import io
import sys
from datetime import date
from pathlib import Path

import pandas as pd

# Add project root to path so we can import scripts.utils
_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

from scripts.utils import schema  # noqa: E402
from scripts.utils.schema import ISSUER_VALUES  # noqa: E402


def _read_table(data_dir: Path, name: str) -> pd.DataFrame:
    path = data_dir / f"{name}.csv"
    # Our seed-CSV convention writes a trailing comma after the final field
    # (e.g. `...,HIGH,\n` — leaving `notes_path` empty). That produces data
    # rows with one more comma-separated field than the header. With pandas'
    # default `index_col=None`, that asymmetry causes `read_csv` to promote
    # the first data column (action_id / entity_id / ...) to the row index,
    # which breaks `row {idx}` error messages downstream (idx would be the
    # PK value rather than 0, 1, 2, ...). Passing `index_col=False` forces
    # positional integer indexing and keeps the PK as a regular column.
    # Row-width validation (malformed rows) is handled separately in
    # `check_row_widths` on the raw file.
    return pd.read_csv(path, dtype=str, keep_default_na=False, index_col=False)


def check_headers(data_dir: Path) -> list[str]:
    errors: list[str] = []
    for name, expected in schema.TABLE_HEADERS.items():
        path = data_dir / f"{name}.csv"
        if not path.exists():
            errors.append(f"{name}.csv: missing file")
            continue
        with open(path) as f:
            header = f.readline().strip().split(",")
        if header != expected:
            errors.append(
                f"{name}.csv: header mismatch. "
                f"Expected {expected}, got {header}"
            )
    return errors


def check_row_widths(data_dir: Path) -> list[str]:
    """Verify every data row has exactly len(header) comma-separated fields.

    Runs on raw text via the stdlib csv module so we catch malformed rows
    before pandas silently truncates or shifts them. A row with the wrong
    field count is almost always a hand-edit mistake (missing comma,
    accidental newline, stray quote).
    """
    errors: list[str] = []
    for name, expected_cols in schema.TABLE_HEADERS.items():
        path = data_dir / f"{name}.csv"
        if not path.exists():
            continue
        expected_n = len(expected_cols)
        with open(path) as f:
            lines = f.readlines()
        # Skip header (line 0); check data rows.
        for i, line in enumerate(lines[1:], start=1):
            # Strip trailing newline only, not trailing commas.
            stripped = line.rstrip("\n").rstrip("\r")
            if stripped == "":
                continue  # Allow trailing blank lines.
            # Note: by project convention, seed rows end with a trailing
            # comma that leaves the final (optional) field empty — e.g.
            # `...,HIGH,` for actions.notes_path. The csv module parses
            # that correctly as N fields where the last is "". A row that
            # yields != len(header) fields is genuinely malformed.
            row = next(csv.reader(io.StringIO(stripped)))
            if len(row) != expected_n:
                errors.append(
                    f"{name}.csv line {i+1}: {len(row)} fields, "
                    f"expected {expected_n}"
                )
    return errors


def check_primary_keys(data_dir: Path) -> list[str]:
    """Verify every PK is non-empty and unique within its table."""
    errors: list[str] = []
    for table, pk in schema.PRIMARY_KEYS.items():
        df = _read_table(data_dir, table)
        if pk not in df.columns:
            continue
        seen: dict[str, int] = {}
        for idx, val in df[pk].items():
            if val == "":
                errors.append(f"{table}.csv row {idx}: empty {pk}")
                continue
            if val in seen:
                errors.append(
                    f"{table}.csv row {idx}: duplicate {pk}={val!r} "
                    f"(also row {seen[val]})"
                )
            else:
                seen[val] = idx
    return errors


def check_enums(data_dir: Path) -> list[str]:
    errors: list[str] = []
    enum_checks = [
        ("actions", "mechanism_type", schema.MECHANISM_TYPES),
        ("actions", "target_type", schema.TARGET_TYPES),
        ("actions", "status", schema.STATUS),
        ("actions", "discovery_source", schema.DISCOVERY_SOURCE),
        ("actions", "confidence", schema.CONFIDENCE),
        ("triggers", "trigger_type", schema.TRIGGER_TYPES),
        ("incidents", "incident_type", schema.INCIDENT_TYPES),
        ("requests", "request_channel", schema.REQUEST_CHANNEL),
        ("requests", "legal_weight", schema.LEGAL_WEIGHT),
        ("policies", "policy_type", schema.POLICY_TYPES),
        ("implementations", "implementation_type", schema.IMPLEMENTATION_TYPES),
        ("implementations", "caller_role", schema.CALLER_ROLE),
        ("entities", "entity_type", schema.ENTITY_TYPES),
        ("entities", "circle_relationship", schema.CIRCLE_RELATIONSHIP),
        ("sources", "source_tier", schema.SOURCE_TIER),
        ("sources", "source_type", schema.SOURCE_TYPE),
        ("action_sources", "relation", schema.ACTION_SOURCE_RELATION),
    ]
    for table, column, allowed in enum_checks:
        df = _read_table(data_dir, table)
        if column not in df.columns:
            continue
        pk_col = schema.PRIMARY_KEYS.get(table)
        for idx, val in df[column].items():
            if val == "":  # NULL permitted for nullable enums
                continue
            if val not in allowed:
                pk_val = (
                    df.at[idx, pk_col]
                    if pk_col and pk_col in df.columns
                    else ""
                )
                id_str = f" ({pk_val})" if pk_val else ""
                errors.append(
                    f"{table}.csv row {idx}{id_str}: column {column} value "
                    f"{val!r} not in allowed list"
                )
    return errors


def check_foreign_keys(data_dir: Path) -> list[str]:
    errors: list[str] = []
    tables = {name: _read_table(data_dir, name) for name in schema.TABLE_HEADERS}
    for src_table, src_col, tgt_table, tgt_col in schema.FOREIGN_KEYS:
        src_df = tables[src_table]
        tgt_df = tables[tgt_table]
        if src_col not in src_df.columns or tgt_col not in tgt_df.columns:
            continue
        valid_ids = set(tgt_df[tgt_col].tolist())
        src_pk_col = schema.PRIMARY_KEYS.get(src_table)
        for idx, val in src_df[src_col].items():
            if val == "":
                continue
            if val not in valid_ids:
                pk_val = (
                    src_df.at[idx, src_pk_col]
                    if src_pk_col and src_pk_col in src_df.columns
                    else ""
                )
                id_str = f" ({pk_val})" if pk_val else ""
                errors.append(
                    f"{src_table}.csv row {idx}{id_str}: {src_col}={val!r} "
                    f"does not resolve to {tgt_table}.{tgt_col}"
                )
    return errors


def check_date_orderings(data_dir: Path) -> list[str]:
    errors: list[str] = []
    actions = _read_table(data_dir, "actions")
    # Map action_id -> action_date
    date_map = dict(zip(actions["action_id"], actions["action_date"]))
    for idx, row in actions.iterrows():
        rev_id = row["reversal_action_id"]
        if rev_id and rev_id in date_map:
            original = row["action_date"]
            reversal = date_map[rev_id]
            if reversal and original and reversal < original:
                errors.append(
                    f"actions.csv row {idx}: reversal_action_id {rev_id} "
                    f"dated {reversal} is before original action_date {original}"
                )
    return errors


def check_future_dates(data_dir: Path) -> list[str]:
    """Flag dates in the future as likely typos."""
    errors: list[str] = []
    today = date.today().isoformat()
    date_fields = [
        ("actions", "action_date"),
        ("actions", "disclosure_date"),
        ("triggers", "trigger_date"),
        ("incidents", "incident_date"),
        ("incidents", "public_disclosure_date"),
        ("requests", "request_date"),
        ("policies", "effective_date"),
        ("policies", "superseded_date"),
        ("implementations", "block_timestamp"),
        ("entities", "relationship_last_reviewed"),
        ("sources", "publication_date"),
        ("sources", "accessed_date"),
    ]
    for table, col in date_fields:
        df = _read_table(data_dir, table)
        if col not in df.columns:
            continue
        pk_col = schema.PRIMARY_KEYS.get(table)
        for idx, val in df[col].items():
            if val == "":
                continue
            # Compare lexicographically — ISO 8601 dates sort correctly as
            # strings. Only compare date portion (first 10 chars) for
            # timestamps like "2024-01-01T12:34:56Z".
            date_part = val[:10]
            if date_part > today:
                pk_val = (
                    df.at[idx, pk_col]
                    if pk_col and pk_col in df.columns
                    else ""
                )
                id_str = f" ({pk_val})" if pk_val else ""
                errors.append(
                    f"{table}.csv row {idx}{id_str}: {col}={val!r} is in the "
                    f"future (today={today})"
                )
    return errors


def check_entity_sources_for_yes_no(data_dir: Path) -> list[str]:
    errors: list[str] = []
    entities = _read_table(data_dir, "entities")
    for idx, row in entities.iterrows():
        rel = row["circle_relationship"]
        src_ids = row["relationship_source_ids"]
        if rel in ("YES", "NO") and not src_ids.strip():
            errors.append(
                f"entities.csv row {idx} ({row['entity_id']}): "
                f"circle_relationship={rel} requires at least one "
                f"source_id in relationship_source_ids"
            )
    return errors


def check_source_hashes(data_dir: Path, allow_missing: bool = False) -> list[str]:
    """Verify archived source copies against their recorded SHA256.

    Local copies under `sources/` and `data/raw/` are gitignored (size), so a
    fresh clone has only `sources/manifest.json`. With `allow_missing=True` a
    missing copy is skipped (reported to stderr) while a present copy whose
    hash differs is still an error.
    """
    errors: list[str] = []
    sources = _read_table(data_dir, "sources")
    missing = 0
    for idx, row in sources.iterrows():
        local_path = row["local_path"]
        expected_hash = row["content_sha256"]
        if not local_path or not expected_hash:
            continue
        p = Path(local_path)
        if not p.exists():
            if allow_missing:
                missing += 1
                continue
            errors.append(
                f"sources.csv row {idx} ({row['source_id']}): "
                f"local_path {local_path} does not exist"
            )
            continue
        actual = hashlib.sha256(p.read_bytes()).hexdigest()
        if actual != expected_hash:
            errors.append(
                f"sources.csv row {idx} ({row['source_id']}): "
                f"hash mismatch. Expected {expected_hash}, got {actual}"
            )
    if missing:
        print(f"note: {missing} archived source copies not present locally (gitignored); hashes not checked for those",
              file=sys.stderr)
    return errors


def _check_issuer_column(df: pd.DataFrame, table_name: str) -> list[str]:
    errors = []
    if "issuer" not in df.columns:
        errors.append(f"{table_name}: missing required 'issuer' column")
        return errors
    bad = df[~df["issuer"].isin(ISSUER_VALUES)]
    if len(bad):
        errors.append(
            f"{table_name}: {len(bad)} rows have issuer not in "
            f"{ISSUER_VALUES} (sample: {bad['issuer'].head(3).tolist()})"
        )
    return errors


def _check_action_trigger_issuer_fk(actions: pd.DataFrame, triggers: pd.DataFrame) -> list[str]:
    errors = []
    # Build trigger_id → issuer map
    tmap = dict(zip(triggers["trigger_id"], triggers["issuer"]))
    for _, row in actions.iterrows():
        tid = row["trigger_id"]
        if tid == "":
            continue
        if tid not in tmap:
            errors.append(f"action {row['action_id']} references unknown trigger {tid}")
            continue
        trigger_issuers = set(s.strip() for s in str(tmap[tid]).split(","))
        if row["issuer"] not in trigger_issuers:
            errors.append(
                f"action {row['action_id']} (issuer={row['issuer']}) "
                f"references trigger {tid} (issuer={tmap[tid]}) — "
                f"allowed={trigger_issuers}, actual={row['issuer']!r} — FK respect violation"
            )
    return errors


def run_all_checks(data_dir: Path, allow_missing_local: bool = False) -> list[str]:
    """Run every validation check. Return flat list of error strings."""
    errors: list[str] = []
    errors.extend(check_headers(data_dir))
    # If headers are wrong, skip downstream checks.
    if errors:
        return errors
    # Row-width check runs on raw text; must happen before anything that
    # reads via pandas, since malformed rows can silently shift columns.
    errors.extend(check_row_widths(data_dir))
    errors.extend(check_primary_keys(data_dir))
    errors.extend(check_enums(data_dir))
    errors.extend(check_foreign_keys(data_dir))
    errors.extend(check_date_orderings(data_dir))
    errors.extend(check_future_dates(data_dir))
    errors.extend(check_entity_sources_for_yes_no(data_dir))
    errors.extend(check_source_hashes(data_dir, allow_missing=allow_missing_local))
    # Issuer column presence and value checks for every fact table.
    issuer_tables = [
        "actions", "implementations", "triggers", "entities",
        "incidents", "policies", "sources", "action_sources",
    ]
    for tname in issuer_tables:
        path = data_dir / f"{tname}.csv"
        if not path.exists():
            errors.append(f"{tname}.csv: missing file required for issuer column check")
            continue
        df = _read_table(data_dir, tname)
        errors.extend(_check_issuer_column(df, tname))
    # FK respect: action.issuer must be a member of its trigger's issuer set.
    actions_path = data_dir / "actions.csv"
    triggers_path = data_dir / "triggers.csv"
    if not actions_path.exists():
        errors.append("actions.csv: missing file required for issuer column check")
    elif not triggers_path.exists():
        errors.append("triggers.csv: missing file required for issuer column check")
    else:
        actions_df = _read_table(data_dir, "actions")
        triggers_df = _read_table(data_dir, "triggers")
        if "trigger_id" in actions_df.columns and "issuer" in actions_df.columns and "issuer" in triggers_df.columns:
            errors.extend(_check_action_trigger_issuer_fk(actions_df, triggers_df))
    return errors


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Validate the CircleUSDC fact tables.")
    parser.add_argument("--allow-missing-local", action="store_true",
                        help="tolerate archived source copies that are not present locally (they are gitignored); hash mismatches remain errors")
    args = parser.parse_args()
    data_dir = _HERE.parent / "data"
    errors = run_all_checks(data_dir, allow_missing_local=args.allow_missing_local)
    if errors:
        print(f"VALIDATION FAILED — {len(errors)} issue(s):")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
