#!/usr/bin/env python
"""One-time migration: add `issuer` column to every fact table, backfill 'Circle'.

Idempotent: running twice produces identical output.
"""
import argparse
import sys
from pathlib import Path
import pandas as pd

TABLES = [
    "actions.csv",
    "implementations.csv",
    "triggers.csv",
    "entities.csv",
    "incidents.csv",
    "policies.csv",
    "sources.csv",
    "action_sources.csv",
]


def migrate(data_dir: Path) -> int:
    n_modified = 0
    for table in TABLES:
        path = data_dir / table
        if not path.exists():
            print(f"skip {table} (not present)")
            continue
        df = pd.read_csv(path, dtype=str, keep_default_na=False, index_col=False)
        if "issuer" in df.columns:
            print(f"skip {table} (already has issuer column)")
            continue
        df["issuer"] = "Circle"
        df.to_csv(path, index=False)
        print(f"migrated {table}: added issuer='Circle' to {len(df)} rows")
        n_modified += 1
    return n_modified


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--data-dir", default="data", type=Path)
    args = p.parse_args()
    n = migrate(args.data_dir)
    print(f"\nmigration complete: {n} tables modified")
    return 0


if __name__ == "__main__":
    sys.exit(main())
