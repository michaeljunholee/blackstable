"""Typed loader for scripts/config/issuers.yaml.

Provides ergonomic accessors for per-issuer contract addresses, supported
chains, and event topics. The YAML is the source of truth; this module is a
thin wrapper to keep callers from re-parsing it.
"""
from functools import lru_cache
from pathlib import Path
import yaml

CONFIG_PATH = Path(__file__).resolve().parents[1] / "config" / "issuers.yaml"


@lru_cache(maxsize=1)
def load_issuers_config() -> dict:
    """Return the parsed issuers.yaml config."""
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def list_issuers() -> list[str]:
    """Names of all issuers in the config."""
    return list(load_issuers_config().keys())


def contract_for(issuer: str, chain: str) -> str:
    """Contract address for an issuer on a chain. Raises KeyError on unknown."""
    cfg = load_issuers_config()
    if issuer not in cfg:
        raise KeyError(f"Unknown issuer {issuer!r}; known: {sorted(cfg)}")
    chains = cfg[issuer]["chains"]
    if chain not in chains:
        raise KeyError(
            f"Issuer {issuer!r} has no entry for chain {chain!r}; "
            f"supported: {sorted(chains)}"
        )
    return chains[chain]


def chains_supported_by(issuer: str) -> list[str]:
    """Chains where this issuer has a contract entry."""
    cfg = load_issuers_config()
    if issuer not in cfg:
        raise KeyError(f"Unknown issuer {issuer!r}; known: {sorted(cfg)}")
    return list(cfg[issuer]["chains"].keys())


def topic_for(issuer: str, event_name: str) -> str:
    """topic0 for a named event of this issuer's contract."""
    cfg = load_issuers_config()
    if issuer not in cfg:
        raise KeyError(f"Unknown issuer {issuer!r}; known: {sorted(cfg)}")
    topics = cfg[issuer]["event_topics"]
    if event_name not in topics:
        raise KeyError(
            f"Issuer {issuer!r} has no event {event_name!r}; "
            f"available: {sorted(topics)}"
        )
    return topics[event_name]


def function_selector_for(issuer: str, function_name: str) -> str:
    """4-byte function selector for a named function of this issuer's contract."""
    cfg = load_issuers_config()
    if issuer not in cfg:
        raise KeyError(f"Unknown issuer {issuer!r}; known: {sorted(cfg)}")
    selectors = cfg[issuer]["function_selectors"]
    if function_name not in selectors:
        raise KeyError(
            f"Issuer {issuer!r} has no function {function_name!r}; "
            f"available: {sorted(selectors)}"
        )
    return selectors[function_name]
