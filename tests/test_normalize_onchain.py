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


# ---------------------------------------------------------------------------
# Incremental refresh: scan_chain must not re-append events already present
# in actions.csv / implementations.csv (the Dune query returns full history).
# ---------------------------------------------------------------------------

_BL_TOPIC = "0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855"
_UB_TOPIC = "0x117e3210bb9aa7d9baff172026820255c6f6c30ba8999d1c2fd88e2848137c4e"
_USDC = "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"


def _evt(tx, block, topic0=_BL_TOPIC, addr="a" * 40, ts="2026-05-01T00:00:00Z"):
    return {
        "tx_hash": tx,
        "block_number": block,
        "block_timestamp": ts,
        "contract_address": _USDC,
        "topic0": topic0,
        "topic1": "0x000000000000000000000000" + addr,
        "topic2": None,
        "data": "0x",
    }


class _FakeDune:
    def __init__(self, rows):
        self.rows = rows
        self.calls = []

    def fetch_latest_results(self, query_id, expected_params=None):
        self.calls.append(("fetch", query_id, expected_params))
        return list(self.rows)

    def execute_query(self, query_id, params=None):
        self.calls.append(("execute", query_id, params))
        return list(self.rows)


def _seed_data_dir(tmp_path, seed_events, chain="ethereum"):
    """Create a data dir holding actions/implementations built from seed_events."""
    data_dir = tmp_path / "data"
    (data_dir / "raw" / "dune").mkdir(parents=True)
    actions, impls = [], []
    for n, ev in enumerate(seed_events, start=1):
        impl_id, act_id = f"CU-IMP-{n:04d}", f"CU-ACT-{n:04d}"
        impls.append(normalize_onchain.build_implementation_row(ev, impl_id, chain))
        actions.append(normalize_onchain.build_action_row(ev, act_id, impl_id, chain))
    pd.DataFrame(actions, columns=TABLE_HEADERS["actions"]).to_csv(data_dir / "actions.csv", index=False)
    pd.DataFrame(impls, columns=TABLE_HEADERS["implementations"]).to_csv(data_dir / "implementations.csv", index=False)
    return data_dir


def _read(data_dir, table):
    return pd.read_csv(data_dir / f"{table}.csv", dtype=str, keep_default_na=False)


def _config():
    return {"chains": {"ethereum": {"dune_blockchain": "ethereum", "from_block": 0}}}


def test_existing_event_keys_covers_chain_tx_mechanism_target(tmp_path):
    seed = [_evt("0x01", 100, addr="a" * 40), _evt("0x02", 101, topic0=_UB_TOPIC, addr="b" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    keys = normalize_onchain.existing_event_keys(data_dir, issuer="Circle")
    assert keys == {
        ("ethereum", "0x01", "BLACKLIST", "0x" + "a" * 40),
        ("ethereum", "0x02", "UNBLACKLIST", "0x" + "b" * 40),
    }


def test_scan_chain_appends_only_new_events(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    seed = [_evt("0x01", 100, addr="a" * 40), _evt("0x02", 101, addr="b" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    # Dune returns full history: the two seeded events plus two genuinely new ones.
    fetched = seed + [_evt("0x03", 200, addr="c" * 40), _evt("0x03", 200, addr="d" * 40)]
    dune = _FakeDune(fetched)

    n = normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True)

    assert n == 2
    actions, impls = _read(data_dir, "actions"), _read(data_dir, "implementations")
    assert len(actions) == 4 and len(impls) == 4
    assert actions["action_id"].tolist() == ["CU-ACT-0001", "CU-ACT-0002", "CU-ACT-0003", "CU-ACT-0004"]
    assert sorted(actions["target_identifier"].tail(2)) == ["0x" + "c" * 40, "0x" + "d" * 40]
    # Same tx, two addresses → two distinct events, both kept.
    assert (impls["tx_hash"] == "0x03").sum() == 2


def test_scan_chain_rerun_is_idempotent(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    seed = [_evt("0x01", 100, addr="a" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    dune = _FakeDune(seed)

    assert normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True) == 0
    assert len(_read(data_dir, "actions")) == 1
    assert len(_read(data_dir, "implementations")) == 1


def test_scan_chain_dedupe_is_case_insensitive_on_hashes(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    seed = [_evt("0xABCD", 100, addr="A" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    dune = _FakeDune([_evt("0xabcd", 100, addr="a" * 40)])

    assert normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True) == 0
    assert len(_read(data_dir, "actions")) == 1


def test_scan_chain_dry_run_writes_nothing_but_reports_new(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    seed = [_evt("0x01", 100, addr="a" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    dune = _FakeDune(seed + [_evt("0x09", 900, addr="e" * 40)])

    n = normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True, dry_run=True)

    assert n == 1
    assert len(_read(data_dir, "actions")) == 1
    assert len(_read(data_dir, "implementations")) == 1
    assert not (data_dir / "raw" / "dune" / "circle_ethereum_blacklist_events.csv").exists()
    assert "new=1" in capsys.readouterr().out


def test_scan_chain_warns_when_fetched_results_do_not_extend_existing(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    seed = [_evt("0x01", 100, addr="a" * 40), _evt("0x02", 500, addr="b" * 40)]
    data_dir = _seed_data_dir(tmp_path, seed)
    # A stale cached execution: max block 100 < existing max block 500.
    dune = _FakeDune([_evt("0x01", 100, addr="a" * 40)])

    normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True)

    assert "stale" in capsys.readouterr().err.lower()


def test_dry_run_flag_present():
    parser = normalize_onchain._build_arg_parser()
    args = parser.parse_args(["--dry-run", "--fetch-only", "ethereum"])
    assert args.dry_run is True and args.fetch_only is True and args.chains == ["ethereum"]


# ---------------------------------------------------------------------------
# Per-chain execution through the single shared saved query: the active
# `FROM <chain>.logs` table is rewritten before each execute.
# ---------------------------------------------------------------------------

_SQL = """-- header comment mentioning FROM arbitrum.logs in prose
SELECT tx_hash FROM optimism.logs WHERE contract_address = {{contract_address}}
-- SELECT tx_hash FROM arbitrum.logs  (old variant, commented out)
"""


def test_set_logs_table_rewrites_only_active_statement():
    out = normalize_onchain.set_logs_table(_SQL, "avalanche_c")
    assert "SELECT tx_hash FROM avalanche_c.logs WHERE" in out
    # Comment lines untouched.
    assert "-- header comment mentioning FROM arbitrum.logs in prose" in out
    assert "-- SELECT tx_hash FROM arbitrum.logs  (old variant, commented out)" in out


def test_set_logs_table_is_idempotent():
    once = normalize_onchain.set_logs_table(_SQL, "base")
    assert normalize_onchain.set_logs_table(once, "base") == once


def test_set_logs_table_raises_when_no_active_table():
    with pytest.raises(ValueError, match="logs"):
        normalize_onchain.set_logs_table("-- SELECT 1 FROM ethereum.logs\n", "base")


class _FakeDuneWithSql(_FakeDune):
    def __init__(self, rows, sql):
        super().__init__(rows)
        self.sql = sql

    def get_query_sql(self, query_id):
        self.calls.append(("get_sql", query_id))
        return self.sql

    def update_query_sql(self, query_id, sql):
        self.calls.append(("update_sql", query_id, sql))
        self.sql = sql


def test_scan_chain_execute_path_switches_table_then_executes(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    data_dir = _seed_data_dir(tmp_path, [_evt("0x01", 100, addr="a" * 40)])
    dune = _FakeDuneWithSql([_evt("0x02", 200, addr="b" * 40)], _SQL)
    config = {"chains": {"avalanche": {"dune_blockchain": "avalanche_c", "from_block": 0}}}

    n = normalize_onchain.scan_chain("avalanche", config, dune, data_dir, fetch_only=False)

    assert n == 1
    kinds = [c[0] for c in dune.calls]
    assert kinds == ["get_sql", "update_sql", "execute"]
    assert "FROM avalanche_c.logs" in dune.calls[1][2]
    assert dune.calls[2][2]["contract_address"] == normalize_onchain.issuers_mod.contract_for("Circle", "avalanche")


def test_scan_chain_execute_path_skips_update_when_table_already_set(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    data_dir = _seed_data_dir(tmp_path, [_evt("0x01", 100, addr="a" * 40)])
    dune = _FakeDuneWithSql([], _SQL)  # _SQL already targets optimism.logs

    normalize_onchain.scan_chain("optimism", {"chains": {"optimism": {"dune_blockchain": "optimism", "from_block": 0}}}, dune, data_dir, fetch_only=False)

    assert [c[0] for c in dune.calls] == ["get_sql", "execute"]


def test_scan_chain_fetch_only_never_touches_query_sql(tmp_path, monkeypatch):
    monkeypatch.setenv("DUNE_QUERY_BLACKLIST_EVENTS", "1")
    data_dir = _seed_data_dir(tmp_path, [_evt("0x01", 100, addr="a" * 40)])
    dune = _FakeDuneWithSql([], _SQL)

    normalize_onchain.scan_chain("ethereum", _config(), dune, data_dir, fetch_only=True)

    assert [c[0] for c in dune.calls] == ["fetch"]
