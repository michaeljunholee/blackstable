"""Tests for the issuers.yaml config loader."""
from pathlib import Path
import pytest

from scripts.utils.issuers import (
    load_issuers_config,
    list_issuers,
    contract_for,
    chains_supported_by,
    topic_for,
    function_selector_for,
)


def test_load_returns_dict_with_known_issuers():
    cfg = load_issuers_config()
    assert "Circle" in cfg
    assert "Tether" in cfg


def test_list_issuers_returns_known_pair():
    issuers = list_issuers()
    assert set(issuers) == {"Circle", "Tether"}


def test_contract_for_circle_ethereum_matches_canonical():
    addr = contract_for("Circle", "ethereum")
    assert addr.lower() == "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


def test_contract_for_tether_tron_matches_canonical():
    addr = contract_for("Tether", "tron")
    assert addr == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


def test_chains_supported_by_circle_is_six_evm():
    chains = chains_supported_by("Circle")
    assert set(chains) == {"ethereum", "base", "polygon", "avalanche", "arbitrum", "optimism"}


def test_chains_supported_by_tether_includes_tron_plus_six_evm():
    chains = chains_supported_by("Tether")
    assert "tron" in chains
    assert {"ethereum", "base", "polygon", "avalanche", "arbitrum", "optimism"}.issubset(set(chains))


def test_topic_for_circle_blacklisted_event():
    topic = topic_for("Circle", "Blacklisted")
    assert topic.startswith("0x")
    assert len(topic) == 66  # 0x + 64 hex chars


def test_topic_for_tether_added_blacklist_event():
    topic = topic_for("Tether", "AddedBlackList")
    assert topic.startswith("0x")


def test_unknown_issuer_raises():
    with pytest.raises(KeyError):
        contract_for("Paxos", "ethereum")


def test_unknown_chain_raises():
    with pytest.raises(KeyError):
        contract_for("Circle", "solana")


def test_function_selector_for_circle_blacklist():
    sel = function_selector_for("Circle", "blacklist")
    assert sel == "0xf9f92be4"
    assert len(sel) == 10  # 0x + 8 hex chars


def test_function_selector_for_tether_addBlackList():
    sel = function_selector_for("Tether", "addBlackList")
    assert sel.startswith("0x")
    assert len(sel) == 10
