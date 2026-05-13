import pytest
from scripts.utils.id_minter import mint_id, parse_id, next_available


def test_mint_id_first_with_empty_existing():
    assert mint_id("ACT", existing=[]) == "CU-ACT-0001"


def test_mint_id_continues_from_highest():
    existing = ["CU-ACT-0001", "CU-ACT-0002"]
    assert mint_id("ACT", existing=existing) == "CU-ACT-0003"


def test_mint_id_fills_gaps_is_false_by_default():
    existing = ["CU-ACT-0001", "CU-ACT-0003"]
    # Should return 0004, not 0002 — we append, not fill.
    assert mint_id("ACT", existing=existing) == "CU-ACT-0004"


def test_mint_id_handles_different_prefix():
    assert mint_id("SRC", existing=["CU-ACT-0001"]) == "CU-SRC-0001"


def test_mint_id_pads_to_four_digits_then_expands():
    existing = [f"CU-ACT-{i:04d}" for i in range(1, 10000)]
    assert mint_id("ACT", existing=existing) == "CU-ACT-10000"


def test_mint_id_rejects_invalid_prefix():
    with pytest.raises(ValueError, match="prefix"):
        mint_id("ACTION", existing=[])


def test_parse_id_returns_prefix_and_number():
    assert parse_id("CU-ACT-0042") == ("ACT", 42)


def test_parse_id_rejects_malformed():
    with pytest.raises(ValueError):
        parse_id("ACT-0001")


def test_next_available_when_no_existing():
    assert next_available("POL", []) == 1


def test_next_available_ignores_other_prefixes():
    # Existing has SRC IDs too; should compute based on POL only.
    existing = ["CU-POL-0001", "CU-SRC-0099"]
    assert next_available("POL", existing) == 2
