"""Refactored pipeline must accept --issuer flag and preserve Circle behavior.

Tests verify:
1. --issuer flag is present in the CLI (help output).
2. Default issuer is Circle.
3. All existing rows in actions.csv have issuer=Circle (pre-USDT ingestion
   invariant).

A full bit-identical end-to-end test is not included here because the pipeline
requires a live or cached Dune API response; the unit-level build_action_row /
build_implementation_row tests in test_normalize_onchain.py cover row content.
"""
import subprocess
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "01_normalize_onchain.py"


# ---------------------------------------------------------------------------
# CLI shape tests
# ---------------------------------------------------------------------------


def test_refactored_pipeline_accepts_issuer_flag():
    """Verify the script accepts --issuer flag without error (smoke test)."""
    result = subprocess.run(
        ["python", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"--help failed:\n{result.stderr}"
    assert "--issuer" in result.stdout, "--issuer flag not in help output"


def test_refactored_pipeline_default_issuer_is_circle():
    """Help output should mention Circle as the default issuer."""
    result = subprocess.run(
        ["python", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"--help failed:\n{result.stderr}"
    assert "Circle" in result.stdout, "'Circle' not mentioned in help output"


def test_refactored_pipeline_tether_in_choices():
    """Help output should mention Tether as a valid issuer choice."""
    result = subprocess.run(
        ["python", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"--help failed:\n{result.stderr}"
    assert "Tether" in result.stdout, "'Tether' not mentioned in help output"


def test_refactored_pipeline_fetch_only_flag_present():
    """--fetch-only flag should still be present after refactor."""
    result = subprocess.run(
        ["python", str(SCRIPT), "--help"],
        capture_output=True,
        text=True,
        cwd=REPO,
    )
    assert result.returncode == 0, f"--help failed:\n{result.stderr}"
    assert "--fetch-only" in result.stdout, "--fetch-only flag not in help output"


# ---------------------------------------------------------------------------
# Data invariant tests
# ---------------------------------------------------------------------------


def test_existing_circle_data_is_unchanged_after_refactor():
    """The existing actions.csv must have issuer=Circle on all rows.

    Pre-USDT-ingestion all rows are Circle.  This test catches any accidental
    modification to actions.csv by the refactor.
    """
    actions = pd.read_csv(REPO / "data" / "actions.csv", dtype=str, keep_default_na=False)
    assert "issuer" in actions.columns, "actions.csv missing 'issuer' column"
    circle_count = (actions["issuer"] == "Circle").sum()
    assert circle_count == len(actions), (
        f"Expected all {len(actions)} rows to have issuer=Circle, "
        f"but only {circle_count} do.  "
        "Either USDT ingestion has already run (update this test) or the "
        "refactor accidentally modified actions.csv."
    )


def test_existing_implementations_all_circle():
    """Pre-USDT-ingestion all implementations.csv rows must have issuer=Circle."""
    impls = pd.read_csv(REPO / "data" / "implementations.csv", dtype=str, keep_default_na=False)
    assert "issuer" in impls.columns, "implementations.csv missing 'issuer' column"
    circle_count = (impls["issuer"] == "Circle").sum()
    assert circle_count == len(impls), (
        f"Expected all {len(impls)} rows to have issuer=Circle, "
        f"but only {circle_count} do."
    )


# ---------------------------------------------------------------------------
# Unit tests for issuer-aware row builders
# ---------------------------------------------------------------------------


def _load_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("normalize_onchain", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.fixture(scope="module")
def norm():
    return _load_module()


def test_build_action_row_circle_writes_issuer(norm):
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855",
        "topic1": "0x000000000000000000000000" + "a" * 40,
    }
    row = norm.build_action_row(event, action_id="CU-ACT-X", implementation_id="CU-IMP-X", chain="ethereum", issuer="Circle")
    assert row["issuer"] == "Circle"
    assert row["mechanism_type"] == "BLACKLIST"


def test_build_action_row_tether_writes_issuer(norm):
    """Tether AddedBlackList event → issuer=Tether, mechanism_type=BLACKLIST."""
    # topic0 for Tether's AddedBlackList (from issuers.yaml)
    tether_topic = "0x42e160154868087d6bfdc0ca23d96a1c1cfa32f1b72ba9ba27b69b98a0d819dc"
    event = {
        "tx_hash": "0xbeef",
        "block_number": 19000000,
        "block_timestamp": "2024-06-01T00:00:00Z",
        "contract_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "topic0": tether_topic,
        "topic1": "0x000000000000000000000000" + "b" * 40,
    }
    row = norm.build_action_row(event, action_id="CU-ACT-Y", implementation_id="CU-IMP-Y", chain="ethereum", issuer="Tether")
    assert row["issuer"] == "Tether"
    assert row["mechanism_type"] == "BLACKLIST"


def test_build_implementation_row_circle_writes_issuer(norm):
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855",
    }
    impl = norm.build_implementation_row(event, implementation_id="CU-IMP-X", chain="ethereum", issuer="Circle")
    assert impl["issuer"] == "Circle"
    assert impl["method_called"] == "blacklist(address)"


def test_build_implementation_row_tether_writes_issuer(norm):
    """Tether AddedBlackList → method_called=addBlackList(address), issuer=Tether."""
    tether_topic = "0x42e160154868087d6bfdc0ca23d96a1c1cfa32f1b72ba9ba27b69b98a0d819dc"
    event = {
        "tx_hash": "0xbeef",
        "block_number": 19000000,
        "block_timestamp": "2024-06-01T00:00:00Z",
        "contract_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
        "topic0": tether_topic,
    }
    impl = norm.build_implementation_row(event, implementation_id="CU-IMP-Y", chain="ethereum", issuer="Tether")
    assert impl["issuer"] == "Tether"
    assert impl["method_called"] == "addBlackList(address)"


def test_event_to_mechanism_backward_compat_no_issuer_arg(norm):
    """Calling event_to_mechanism without issuer= still works (Circle default)."""
    blacklisted_topic = "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855"
    assert norm.event_to_mechanism(blacklisted_topic) == "BLACKLIST"


def test_event_to_mechanism_unknown_topic_raises(norm):
    with pytest.raises(ValueError):
        norm.event_to_mechanism("0x" + "ff" * 32)


def test_event_to_mechanism_tether_added_blacklist(norm):
    tether_topic = "0x42e160154868087d6bfdc0ca23d96a1c1cfa32f1b72ba9ba27b69b98a0d819dc"
    assert norm.event_to_mechanism(tether_topic, issuer="Tether") == "BLACKLIST"


def test_event_to_mechanism_tether_removed_blacklist(norm):
    tether_topic = "0xd7c0101d4cf124eb000ddafabb6db7c93c20b6e1eba51d3c80a1b2cd6d6e3a8b"
    assert norm.event_to_mechanism(tether_topic, issuer="Tether") == "UNBLACKLIST"
