import pandas as pd
import pytest

from scripts.utils.schema import TABLE_HEADERS
import importlib.util
from pathlib import Path
_NORM_PATH = Path(__file__).parent.parent / "scripts" / "01_normalize_onchain.py"
_spec = importlib.util.spec_from_file_location("normalize_onchain", _NORM_PATH)
normalize_onchain = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(normalize_onchain)


def test_topic_to_address_decodes_padded_address():
    padded = "0x000000000000000000000000" + "a" * 40
    assert normalize_onchain.topic_to_address(padded) == "0x" + "a" * 40


def test_event_to_mechanism_maps_correctly():
    blacklisted_topic = "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855"
    assert normalize_onchain.event_to_mechanism(blacklisted_topic) == "BLACKLIST"


def test_event_to_mechanism_unknown_topic_raises():
    with pytest.raises(ValueError):
        normalize_onchain.event_to_mechanism("0x" + "ff" * 32)


def test_build_action_row_produces_canonical_fields():
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855",
        "topic1": "0x000000000000000000000000" + "a" * 40,
    }
    action_id = "CU-ACT-0001"
    impl_id = "CU-IMP-0001"
    action = normalize_onchain.build_action_row(event, action_id=action_id, implementation_id=impl_id, chain="ethereum")

    assert set(action.keys()) == set(TABLE_HEADERS["actions"])
    assert action["action_id"] == action_id
    assert action["mechanism_type"] == "BLACKLIST"
    assert action["target_identifier"] == "0x" + "a" * 40
    assert action["target_type"] == "ADDRESS"
    assert action["implementation_id"] == impl_id
    assert action["discovery_source"] == "ONCHAIN_SCAN"
    assert action["confidence"] == "HIGH"
    assert action["status"] == "ACTIVE"
    assert action["action_date"] == "2024-01-01"  # Date-only, not datetime


def test_build_implementation_row_populates_chain_and_contract():
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855",
    }
    impl = normalize_onchain.build_implementation_row(event, implementation_id="CU-IMP-0001", chain="ethereum")

    assert set(impl.keys()) == set(TABLE_HEADERS["implementations"])
    assert impl["implementation_id"] == "CU-IMP-0001"
    assert impl["implementation_type"] == "ONCHAIN_TX"
    assert impl["tx_hash"] == "0xdead"
    assert impl["chain"] == "ethereum"
    assert impl["contract_address"] == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"
    assert impl["method_called"] == "blacklist(address)"


def test_build_action_row_pause_uses_contract_identifier():
    """PAUSE events have no target address; use <chain>:<contract> convention."""
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0x62e78cea01bee320cd4e420270b5ea74000d11b0c9f74754ebdbfc544b05a258",
    }
    action = normalize_onchain.build_action_row(
        event, action_id="CU-ACT-0001", implementation_id="CU-IMP-0001", chain="ethereum"
    )
    assert action["mechanism_type"] == "PAUSE"
    assert action["target_type"] == "NA"
    assert action["target_identifier"] == "ethereum:0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


def test_build_implementation_row_pause_uses_pauser_role():
    """PAUSE events record caller_role=PAUSER."""
    event = {
        "tx_hash": "0xdead",
        "block_number": 18000000,
        "block_timestamp": "2024-01-01T00:00:00Z",
        "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        "topic0": "0x62e78cea01bee320cd4e420270b5ea74000d11b0c9f74754ebdbfc544b05a258",
    }
    impl = normalize_onchain.build_implementation_row(
        event, implementation_id="CU-IMP-0001", chain="ethereum"
    )
    assert impl["method_called"] == "pause()"
    assert impl["caller_role"] == "PAUSER"


def test_parse_block_date_handles_iso_8601():
    assert normalize_onchain._parse_block_date("2024-01-01T00:00:00Z") == "2024-01-01"


def test_parse_block_date_handles_dune_utc_format():
    """Dune returns timestamps like '2020-06-16 04:39:08.000 UTC'."""
    assert normalize_onchain._parse_block_date("2020-06-16 04:39:08.000 UTC") == "2020-06-16"


def test_parse_block_date_handles_plain_date():
    assert normalize_onchain._parse_block_date("2020-06-16") == "2020-06-16"


def test_parse_block_date_rejects_malformed():
    with pytest.raises(ValueError):
        normalize_onchain._parse_block_date("not-a-date")
    with pytest.raises(ValueError):
        normalize_onchain._parse_block_date("short")
