import importlib.util
from pathlib import Path

import pandas as pd

_PATH = Path(__file__).parent.parent / "scripts" / "05_link_reversals.py"
_spec = importlib.util.spec_from_file_location("link_reversals", _PATH)
lr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lr)


def _actions(rows):
    base = {"target_identifier": "0xabc", "status": "ACTIVE", "reversal_action_id": "", "issuer": "Circle"}
    return pd.DataFrame([{**base, **r} for r in rows])


def _impls(rows):
    return pd.DataFrame(rows)


def test_links_unblacklist_to_latest_prior_blacklist_same_chain():
    a = _actions([
        {"action_id": "CU-ACT-0001", "action_date": "2026-01-01", "mechanism_type": "BLACKLIST", "implementation_id": "I1"},
        {"action_id": "CU-ACT-0002", "action_date": "2026-01-01", "mechanism_type": "BLACKLIST", "implementation_id": "I2"},  # other chain
        {"action_id": "CU-ACT-0003", "action_date": "2026-02-01", "mechanism_type": "UNBLACKLIST", "implementation_id": "I3"},
    ])
    i = _impls([
        {"implementation_id": "I1", "chain": "ethereum", "block_timestamp": "2026-01-01 10:00:00"},
        {"implementation_id": "I2", "chain": "polygon", "block_timestamp": "2026-01-01 10:00:00"},
        {"implementation_id": "I3", "chain": "ethereum", "block_timestamp": "2026-02-01 10:00:00"},
    ])
    out, links = lr.link_reversals(a, i)
    assert links == [("CU-ACT-0001", "CU-ACT-0003")]
    assert out.loc[out.action_id == "CU-ACT-0001", "status"].item() == "REVERSED"
    assert out.loc[out.action_id == "CU-ACT-0001", "reversal_action_id"].item() == "CU-ACT-0003"
    assert out.loc[out.action_id == "CU-ACT-0002", "status"].item() == "ACTIVE"  # polygon untouched
    assert out.loc[out.action_id == "CU-ACT-0003", "status"].item() == "ACTIVE"  # UB row itself untouched


def test_idempotent_and_respects_existing_links():
    a = _actions([
        {"action_id": "CU-ACT-0001", "action_date": "2026-01-01", "mechanism_type": "BLACKLIST", "implementation_id": "I1",
         "status": "REVERSED", "reversal_action_id": "CU-ACT-0002"},
        {"action_id": "CU-ACT-0002", "action_date": "2026-01-05", "mechanism_type": "UNBLACKLIST", "implementation_id": "I2"},
        {"action_id": "CU-ACT-0003", "action_date": "2026-02-01", "mechanism_type": "BLACKLIST", "implementation_id": "I3"},  # re-blacklisted
        {"action_id": "CU-ACT-0004", "action_date": "2026-03-01", "mechanism_type": "UNBLACKLIST", "implementation_id": "I4"},
    ])
    i = _impls([{"implementation_id": f"I{n}", "chain": "ethereum", "block_timestamp": f"2026-0{n}-01 00:00:00"} for n in range(1, 5)])
    out, links = lr.link_reversals(a, i)
    assert links == [("CU-ACT-0003", "CU-ACT-0004")]  # second cycle links to the re-blacklist, not the old one
    out2, links2 = lr.link_reversals(out, i)
    assert links2 == [] and out2.equals(out)


def test_unblacklist_without_prior_blacklist_is_left_alone():
    a = _actions([{"action_id": "CU-ACT-0001", "action_date": "2026-02-01", "mechanism_type": "UNBLACKLIST", "implementation_id": "I1"}])
    i = _impls([{"implementation_id": "I1", "chain": "ethereum", "block_timestamp": "2026-02-01 00:00:00"}])
    out, links = lr.link_reversals(a, i)
    assert links == [] and out.equals(a)
