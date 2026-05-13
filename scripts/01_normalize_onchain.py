#!/usr/bin/env python3
"""Scan blacklist / unblacklist / pause / unpause events across EVM chains.

Populates `data/actions.csv` and `data/implementations.csv` from Dune Analytics
query results. Each event becomes one action row plus one implementation row.

Use --issuer to select which token contract to scan (default: Circle).
"""
from __future__ import annotations

import argparse
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from dotenv import load_dotenv

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

from scripts.utils import schema
from scripts.utils import issuers as issuers_mod
from scripts.utils.id_minter import mint_id
from scripts.utils.dune_client import DuneClient


# Per-issuer event-name→mechanism mapping.  issuers.yaml is the source of truth
# for the actual topic0 hashes; this dict maps event names → schema mechanism types.
_EVENT_TO_MECHANISM: dict[str, dict[str, str]] = {
    "Circle": {
        "Blacklisted":    "BLACKLIST",
        "UnBlacklisted":  "UNBLACKLIST",
        "Paused":         "PAUSE",
        "Unpaused":       "UNPAUSE",
    },
    "Tether": {
        "AddedBlackList":      "BLACKLIST",
        "RemovedBlackList":    "UNBLACKLIST",
        "DestroyedBlackFunds": "BLACKLIST",  # enforce-on-BL'd address; no finer schema type
    },
}


def _build_topic_to_mechanism(issuer: str) -> dict[str, str]:
    """Return a topic0→mechanism_type dict for the given issuer.

    topic0 hashes are resolved from issuers.yaml via topic_for(), making
    issuers.yaml the single source of truth for topic0 values.
    """
    if issuer not in _EVENT_TO_MECHANISM:
        raise KeyError(
            f"No topic→mechanism mapping defined for issuer {issuer!r}. "
            f"Add a mapping in 01_normalize_onchain.py."
        )
    return {
        issuers_mod.topic_for(issuer, evt).lower(): mech
        for evt, mech in _EVENT_TO_MECHANISM[issuer].items()
    }


# Per-issuer method name lookup (used to populate method_called in implementations).
_ISSUER_MECHANISM_TO_METHOD: dict[str, dict[str, str]] = {
    "Circle": {
        "BLACKLIST":    "blacklist(address)",
        "UNBLACKLIST":  "unBlacklist(address)",
        "PAUSE":        "pause()",
        "UNPAUSE":      "unpause()",
    },
    "Tether": {
        "BLACKLIST":    "addBlackList(address)",
        "UNBLACKLIST":  "removeBlackList(address)",
    },
}


def topic_to_address(topic: str) -> str:
    """Convert a 32-byte padded topic to a 20-byte lowercase address."""
    t = topic.lower().removeprefix("0x")
    if len(t) != 64:
        raise ValueError(f"unexpected topic length: {topic}")
    return "0x" + t[-40:]


def event_to_mechanism(topic0: str, issuer: str = "Circle") -> str:
    """Return the mechanism_type for topic0.

    For backward compatibility, calling with a single argument (issuer='Circle')
    behaves identically to the pre-refactor version.
    """
    mapping = _build_topic_to_mechanism(issuer)
    t = topic0.lower()
    if t not in mapping:
        raise ValueError(f"unknown topic0 for issuer={issuer!r}: {topic0}")
    return mapping[t]


def _parse_block_date(timestamp: str) -> str:
    """Return YYYY-MM-DD from a block timestamp string.

    Accepts multiple formats observed in practice:
      - ISO 8601 with Z or offset: '2020-06-16T04:39:08Z', '2020-06-16T04:39:08+00:00'
      - Dune SQL default: '2020-06-16 04:39:08.000 UTC'
      - Plain date: '2020-06-16'

    Since we only need the date portion, extract the leading YYYY-MM-DD and
    validate the format rather than trying to parse every timestamp variant.
    """
    if len(timestamp) < 10:
        raise ValueError(f"timestamp too short to contain a date: {timestamp!r}")
    date_part = timestamp[:10]
    # Validate YYYY-MM-DD; raises ValueError if malformed.
    datetime.strptime(date_part, "%Y-%m-%d")
    return date_part


def build_action_row(
    event: dict,
    action_id: str,
    implementation_id: str,
    chain: str,
    issuer: str = "Circle",
) -> dict:
    mechanism = event_to_mechanism(event["topic0"], issuer=issuer)
    row = {field: "" for field in schema.TABLE_HEADERS["actions"]}
    row["action_id"] = action_id
    row["action_date"] = _parse_block_date(event["block_timestamp"])
    row["mechanism_type"] = mechanism
    if mechanism in ("BLACKLIST", "UNBLACKLIST"):
        row["target_identifier"] = topic_to_address(event["topic1"])
        row["target_type"] = "ADDRESS"
    else:
        # Pause/Unpause are system-wide, no target address.
        row["target_identifier"] = f"{chain}:{event['contract_address']}"
        row["target_type"] = "NA"
    row["status"] = "ACTIVE"
    row["implementation_id"] = implementation_id
    row["discovery_source"] = "ONCHAIN_SCAN"
    row["confidence"] = "HIGH"
    row["issuer"] = issuer
    return row


def build_implementation_row(
    event: dict,
    implementation_id: str,
    chain: str,
    issuer: str = "Circle",
) -> dict:
    mechanism = event_to_mechanism(event["topic0"], issuer=issuer)
    method_map = _ISSUER_MECHANISM_TO_METHOD.get(issuer, _ISSUER_MECHANISM_TO_METHOD["Circle"])
    row = {field: "" for field in schema.TABLE_HEADERS["implementations"]}
    row["implementation_id"] = implementation_id
    row["implementation_type"] = "ONCHAIN_TX"
    row["tx_hash"] = event["tx_hash"]
    row["block_number"] = str(event["block_number"])
    row["block_timestamp"] = event["block_timestamp"]
    row["chain"] = chain
    row["contract_address"] = event["contract_address"]
    row["method_called"] = method_map.get(mechanism, mechanism.lower() + "(address)")
    row["caller_role"] = {
        "BLACKLIST": "BLACKLISTER",
        "UNBLACKLIST": "BLACKLISTER",
        "PAUSE": "PAUSER",
        "UNPAUSE": "PAUSER",
    }.get(mechanism, "UNKNOWN")
    row["issuer"] = issuer
    return row


def load_config() -> dict:
    path = _HERE / "config" / "chains.yaml"
    with open(path) as f:
        return yaml.safe_load(f)


def load_existing_ids(data_dir: Path, table: str, key: str) -> list[str]:
    df = pd.read_csv(data_dir / f"{table}.csv", dtype=str, keep_default_na=False)
    return df[key].tolist()


def append_rows(data_dir: Path, table: str, rows: list[dict]) -> None:
    path = data_dir / f"{table}.csv"
    df = pd.DataFrame(rows, columns=schema.TABLE_HEADERS[table])
    df.to_csv(path, mode="a", header=False, index=False)


def scan_chain(
    chain_name: str,
    config: dict,
    dune: DuneClient,
    data_dir: Path,
    issuer: str = "Circle",
    fetch_only: bool = False,
) -> int:
    """Scan a single chain for a given issuer. Returns number of events ingested.

    Contract address is resolved from issuers.yaml via issuers.contract_for().
    Chain-level metadata (dune_blockchain, from_block) still comes from chains.yaml.

    If fetch_only=True, retrieves the latest cached execution from Dune
    (user must have run the query in the Dune UI first). Otherwise uses
    programmatic execute+poll (requires paid tier).
    """
    chain_config = config["chains"][chain_name]
    contract_address = issuers_mod.contract_for(issuer, chain_name)
    query_id = int(os.environ["DUNE_QUERY_BLACKLIST_EVENTS"])

    expected_params = {
        "blockchain": chain_config["dune_blockchain"],
        "contract_address": contract_address,
    }

    if fetch_only:
        print(
            f"[scan_chain] issuer={issuer} chain={chain_name} fetching latest cached results "
            f"(expects params={expected_params})..."
        )
        rows = dune.fetch_latest_results(
            query_id=query_id, expected_params=expected_params
        )
    else:
        print(f"[scan_chain] issuer={issuer} chain={chain_name} querying Dune...")
        rows = dune.execute_query(query_id=query_id, params=expected_params)

    # Write raw dump for audit.
    raw_path = data_dir / "raw" / "dune" / f"{issuer.lower()}_{chain_name}_blacklist_events.csv"
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(raw_path, index=False)
    print(f"[scan_chain] issuer={issuer} chain={chain_name} events={len(rows)} raw_path={raw_path}")

    if len(rows) == 0:
        print(
            f"WARNING: issuer={issuer} chain={chain_name} returned 0 events — verify contract "
            f"({contract_address}) and dune_blockchain param ({chain_config['dune_blockchain']})",
            file=sys.stderr,
        )
        return 0

    # Normalize into actions + implementations.
    existing_action_ids = load_existing_ids(data_dir, "actions", "action_id")
    existing_impl_ids = load_existing_ids(data_dir, "implementations", "implementation_id")

    new_actions: list[dict] = []
    new_impls: list[dict] = []
    try:
        for event in rows:
            impl_id = mint_id("IMP", existing_impl_ids + [r["implementation_id"] for r in new_impls])
            action_id = mint_id("ACT", existing_action_ids + [r["action_id"] for r in new_actions])
            new_impls.append(build_implementation_row(event, impl_id, chain_name, issuer=issuer))
            new_actions.append(build_action_row(event, action_id, impl_id, chain_name, issuer=issuer))
    except ValueError as e:
        print(
            f"ERROR: issuer={issuer} chain={chain_name} unexpected event schema — {e}. "
            f"Raw dump preserved at {raw_path}. No rows appended.",
            file=sys.stderr,
        )
        raise

    append_rows(data_dir, "implementations", new_impls)
    append_rows(data_dir, "actions", new_actions)
    return len(rows)


def _build_arg_parser() -> argparse.ArgumentParser:
    known_issuers = issuers_mod.list_issuers()
    parser = argparse.ArgumentParser(
        description="Scan blacklist events for a token issuer across EVM chains.",
    )
    parser.add_argument(
        "--issuer",
        choices=known_issuers,
        default="Circle",
        help=(
            "Token issuer whose contract to scan.  "
            f"One of: {', '.join(known_issuers)}.  Default: Circle."
        ),
    )
    parser.add_argument(
        "--fetch-only",
        action="store_true",
        default=False,
        help=(
            "Retrieve the latest cached Dune execution rather than triggering a "
            "fresh run (requires the query to have been run in the Dune UI first)."
        ),
    )
    parser.add_argument(
        "chains",
        nargs="*",
        metavar="CHAIN",
        help=(
            "Chain(s) to scan.  If omitted, all chains supported by the selected "
            "issuer are scanned."
        ),
    )
    return parser


def main() -> int:
    load_dotenv()
    api_key = os.environ.get("DUNE_API_KEY")
    if not api_key:
        print("ERROR: DUNE_API_KEY not set in environment.", file=sys.stderr)
        return 2

    config = load_config()
    data_dir = _HERE.parent / "data"
    dune = DuneClient(api_key=api_key)

    parser = _build_arg_parser()
    args = parser.parse_args()

    # Determine which chains to scan.
    if args.chains:
        chains = args.chains
    else:
        # Default: all chains that this issuer supports AND that appear in chains.yaml.
        issuer_chains = set(issuers_mod.chains_supported_by(args.issuer))
        chains = [c for c in config["chains"] if c in issuer_chains]

    for chain in chains:
        if chain not in config["chains"]:
            print(f"ERROR: unknown chain {chain!r} in chains.yaml", file=sys.stderr)
            return 2
        try:
            issuers_mod.contract_for(args.issuer, chain)
        except KeyError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2

    total = 0
    for chain in chains:
        total += scan_chain(
            chain, config, dune, data_dir,
            issuer=args.issuer,
            fetch_only=args.fetch_only,
        )

    print(f"[main] issuer={args.issuer} total events ingested: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
