#!/usr/bin/env python3
"""Link UNBLACKLIST actions to the BLACKLIST actions they reverse.

For every UNBLACKLIST action, find the most recent earlier BLACKLIST of the
same (issuer, chain, address) that has not yet been reversed, then mark that
BLACKLIST `status=REVERSED` and point its `reversal_action_id` at the
UNBLACKLIST. Idempotent: already-linked pairs are left untouched, so the
script can run after every on-chain refresh.

Usage:
  python scripts/05_link_reversals.py            # apply
  python scripts/05_link_reversals.py --dry-run  # report only
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

_HERE = Path(__file__).parent


def link_reversals(actions: pd.DataFrame, impls: pd.DataFrame) -> tuple[pd.DataFrame, list[tuple[str, str]]]:
    """Return (updated actions, [(blacklist_id, unblacklist_id), ...]) for new links."""
    a = actions.copy()
    chain = impls.set_index("implementation_id")["chain"]
    a["_chain"] = a["implementation_id"].map(chain).fillna("")
    a["_addr"] = a["target_identifier"].str.lower()
    a["_ts"] = a["implementation_id"].map(impls.set_index("implementation_id")["block_timestamp"]).fillna("")
    a["_ord"] = a["action_date"] + " " + a["_ts"]  # date first, then block timestamp as tiebreak
    already_used = set(a.loc[a["reversal_action_id"] != "", "reversal_action_id"])

    links: list[tuple[str, str]] = []
    ubs = a[(a["mechanism_type"] == "UNBLACKLIST") & (~a["action_id"].isin(already_used))]
    for ub in ubs.sort_values("_ord").to_dict("records"):
        cands = a[
            (a["mechanism_type"] == "BLACKLIST")
            & (a["issuer"] == ub["issuer"])
            & (a["_chain"] == ub["_chain"])
            & (a["_addr"] == ub["_addr"])
            & (a["_ord"] < ub["_ord"])
            & (a["reversal_action_id"] == "")
        ]
        if cands.empty:
            continue
        bl_idx = cands.sort_values("_ord").index[-1]
        a.loc[bl_idx, "status"] = "REVERSED"
        a.loc[bl_idx, "reversal_action_id"] = ub["action_id"]
        links.append((a.loc[bl_idx, "action_id"], ub["action_id"]))
    return a.drop(columns=["_chain", "_addr", "_ts", "_ord"]), links


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    data_dir = _HERE.parent / "data"
    actions = pd.read_csv(data_dir / "actions.csv", dtype=str, keep_default_na=False)
    impls = pd.read_csv(data_dir / "implementations.csv", dtype=str, keep_default_na=False)

    updated, links = link_reversals(actions, impls)
    unlinked = updated[(updated["mechanism_type"] == "UNBLACKLIST") & (~updated["action_id"].isin(set(updated["reversal_action_id"])))]
    print(f"[reversals] new links: {len(links)}; UNBLACKLIST actions still without a prior BLACKLIST: {len(unlinked)}")
    for bl, ub in links[:10]:
        print(f"  {bl} -> reversed by {ub}")
    if len(links) > 10:
        print(f"  ... and {len(links) - 10} more")
    if args.dry_run:
        return 0
    if links:
        updated.to_csv(data_dir / "actions.csv", index=False)
        print(f"[reversals] wrote {data_dir / 'actions.csv'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
