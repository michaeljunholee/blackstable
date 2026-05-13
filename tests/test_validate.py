from pathlib import Path
import pandas as pd
import pytest

# Import functions from scripts/99_validate.py by loading it explicitly:
import importlib.util
_VALIDATE_PATH = Path(__file__).parent.parent / "scripts" / "99_validate.py"
_spec = importlib.util.spec_from_file_location("validate", _VALIDATE_PATH)
validate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(validate)


def _minimal_data(tmp_path: Path) -> Path:
    """Create a minimal valid dataset in tmp_path/data/ and return the data dir."""
    data = tmp_path / "data"
    data.mkdir()
    from scripts.utils.schema import TABLE_HEADERS
    (data / "actions.csv").write_text(
        ",".join(TABLE_HEADERS["actions"]) + "\n"
        "CU-ACT-0001,2024-08-08,BLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    for table in ("triggers", "incidents", "requests", "policies", "implementations",
                  "entities", "sources", "action_sources"):
        # Write minimal valid header-only CSV
        from scripts.utils.schema import TABLE_HEADERS
        (data / f"{table}.csv").write_text(",".join(TABLE_HEADERS[table]) + "\n")
    return data


def test_validate_clean_dataset_passes(tmp_path):
    data = _minimal_data(tmp_path)
    errors = validate.run_all_checks(data)
    assert errors == []


def test_validate_detects_invalid_enum(tmp_path):
    data = _minimal_data(tmp_path)
    # Overwrite actions.csv with an invalid mechanism_type
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2024-08-08,BOGUS,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("mechanism_type" in e and "BOGUS" in e for e in errors)


def test_validate_detects_orphan_fk(tmp_path):
    data = _minimal_data(tmp_path)
    # action references a non-existent entity
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2024-08-08,BLACKLIST,0xabc,ADDRESS,,CU-ENT-9999,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("target_entity_id" in e and "CU-ENT-9999" in e for e in errors)


def test_validate_detects_date_inversion_reversal_before_action(tmp_path):
    data = _minimal_data(tmp_path)
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2024-08-08,BLACKLIST,0xabc,ADDRESS,,,,REVERSED,CU-ACT-0002,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
        # Reversal action dated BEFORE the original
        "CU-ACT-0002,2024-08-07,UNBLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("reversal" in e.lower() and "before" in e.lower() for e in errors)


def test_validate_detects_yes_relationship_without_source(tmp_path):
    data = _minimal_data(tmp_path)
    header = (data / "entities.csv").read_text().splitlines()[0]
    (data / "entities.csv").write_text(
        header + "\n"
        "CU-ENT-0001,Coinbase,EXCHANGE,,,YES,\"Equity tie and consortium member\",,2026-04-17,Circle\n"
        # Missing relationship_source_ids for YES classification
    )
    errors = validate.run_all_checks(data)
    assert any("CU-ENT-0001" in e and "relationship_source_ids" in e for e in errors)


def test_validate_detects_duplicate_primary_key(tmp_path):
    """C1: duplicate PK is rejected."""
    data = _minimal_data(tmp_path)
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2024-08-08,BLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
        "CU-ACT-0001,2024-08-09,UNBLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("duplicate" in e and "CU-ACT-0001" in e for e in errors)


def test_validate_detects_empty_primary_key(tmp_path):
    """C1: empty PK is rejected."""
    data = _minimal_data(tmp_path)
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        ",2024-08-08,BLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("empty action_id" in e for e in errors)


def test_validate_detects_row_width_mismatch(tmp_path):
    """C2: malformed row with wrong field count is rejected."""
    data = _minimal_data(tmp_path)
    header = (data / "actions.csv").read_text().splitlines()[0]
    # Only 15 fields instead of 21
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2024-08-08,BLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,HIGH,\n"
    )
    errors = validate.run_all_checks(data)
    assert any("fields, expected" in e for e in errors)


def test_validate_detects_future_date(tmp_path):
    """I-5: future action_date is flagged."""
    data = _minimal_data(tmp_path)
    header = (data / "actions.csv").read_text().splitlines()[0]
    (data / "actions.csv").write_text(
        header + "\n"
        "CU-ACT-0001,2099-01-01,BLACKLIST,0xabc,ADDRESS,,,,ACTIVE,,,,,,,,,ONCHAIN_SCAN,HIGH,,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("future" in e.lower() for e in errors)


def test_validate_detects_hash_mismatch(tmp_path):
    """I-7: tamper-detection via hash."""
    data = _minimal_data(tmp_path)
    archive = tmp_path / "archive.pdf"
    archive.write_bytes(b"original content")
    header = (data / "sources.csv").read_text().splitlines()[0]
    (data / "sources.csv").write_text(
        header + "\n"
        f"CU-SRC-0001,PRIMARY,GOV_FILING,T,P,A,2024-01-01,http://e,,"
        f"{archive},0000000000000000000000000000000000000000000000000000000000000000,2024-01-01,Circle\n"
    )
    errors = validate.run_all_checks(data)
    assert any("hash mismatch" in e for e in errors)


def test_validate_detects_missing_csv_file(tmp_path):
    """I-7: absent table file is reported."""
    data = tmp_path / "data"
    data.mkdir()
    # Don't create any CSVs.
    errors = validate.run_all_checks(data)
    assert any("actions.csv" in e and "missing" in e for e in errors)
