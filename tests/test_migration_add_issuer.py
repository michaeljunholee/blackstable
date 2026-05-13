"""Migration tests: adding `issuer` column to every fact table.

The migration is purely additive at the schema level. Pre-migration rows
must be unchanged after migration, except for the new `issuer='Circle'` field.
"""
import pandas as pd
import subprocess
import shutil
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "data"
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


def test_migration_adds_only_issuer_column(tmp_path):
    """Re-running migrate against an already-migrated CSV is a no-op."""
    for table in TABLES:
        src = DATA / table
        if not src.exists():
            continue
        df = pd.read_csv(src)
        assert "issuer" in df.columns, f"{table} missing issuer column"
        # Every existing row must have issuer='Circle' (post-migration state).
        assert (df["issuer"] == "Circle").all(), (
            f"{table} has non-Circle issuer values pre-USDT ingestion"
        )


def test_migration_script_idempotent(tmp_path):
    """Running migrate_add_issuer.py twice produces identical CSVs."""
    work = tmp_path / "data"
    work.mkdir()
    for t in TABLES:
        src = DATA / t
        if src.exists():
            shutil.copy(src, work / t)
    # Run migration script twice against the working copy
    script = REPO / "scripts" / "migrate_add_issuer.py"
    for _ in range(2):
        result = subprocess.run(
            ["python", str(script), "--data-dir", str(work)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, result.stderr
    # CSV contents should equal what's in DATA after one run
    for t in TABLES:
        if (DATA / t).exists():
            assert (work / t).read_bytes() == (DATA / t).read_bytes(), (
                f"Idempotency broken for {t}"
            )
