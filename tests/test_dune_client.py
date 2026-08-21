import json
from pathlib import Path
import pytest
import responses
from scripts.utils.dune_client import DuneClient, DuneQueryError


FIXTURES = Path(__file__).parent / "fixtures"


@responses.activate
def test_execute_and_poll_returns_rows():
    execute_resp = json.loads((FIXTURES / "dune_execution_response.json").read_text())
    results_resp = json.loads((FIXTURES / "dune_results_response.json").read_text())

    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/1234/execute",
        json=execute_resp, status=200,
    )
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/execution/01HAY2ZXABC123/results",
        json=results_resp, status=200,
    )

    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    rows = client.execute_query(1234)

    assert len(rows) == 2
    assert rows[0]["tx_hash"] == "0xdead"
    assert rows[1]["event"] == "UnBlacklisted"


@responses.activate
def test_execute_raises_on_failed_state():
    execute_resp = {"execution_id": "fail1", "state": "QUERY_STATE_FAILED"}
    failed_results = {"execution_id": "fail1", "state": "QUERY_STATE_FAILED", "error": "syntax error"}

    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/9999/execute",
        json=execute_resp, status=200,
    )
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/execution/fail1/results",
        json=failed_results, status=200,
    )

    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="syntax error"):
        client.execute_query(9999)


@responses.activate
def test_execute_query_with_parameters_sends_params_in_body():
    execute_resp = {"execution_id": "p1", "state": "QUERY_STATE_COMPLETED"}
    results_resp = {
        "execution_id": "p1",
        "state": "QUERY_STATE_COMPLETED",
        "result": {"rows": [], "metadata": {"column_names": []}},
    }
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/555/execute",
        json=execute_resp, status=200,
    )
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/execution/p1/results",
        json=results_resp, status=200,
    )

    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    client.execute_query(555, params={"chain": "ethereum"})

    # Verify params were sent
    exec_call = responses.calls[0]
    body = json.loads(exec_call.request.body)
    assert body["query_parameters"]["chain"] == "ethereum"


def test_client_requires_api_key():
    with pytest.raises(ValueError, match="api_key"):
        DuneClient(api_key="")


@responses.activate
def test_http_error_on_submit_wraps_as_dune_query_error():
    """I-1: 401 bad API key surfaces as DuneQueryError, not requests.HTTPError."""
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/1234/execute",
        json={"error": "unauthorized"}, status=401,
    )
    client = DuneClient(api_key="bad-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="Dune submit failed"):
        client.execute_query(1234)


@responses.activate
def test_http_error_on_poll_wraps_as_dune_query_error():
    """I-1: 5xx during poll surfaces as DuneQueryError."""
    execute_resp = {"execution_id": "e1", "state": "QUERY_STATE_PENDING"}
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/1234/execute",
        json=execute_resp, status=200,
    )
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/execution/e1/results",
        json={"error": "internal server error"}, status=502,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="Dune poll failed"):
        client.execute_query(1234)


@responses.activate
def test_execute_raises_on_row_cap_exceeded():
    """I-3: silent truncation risk — raise explicitly if results hit the cap."""
    # Build a response with exactly 100000 rows (the cap). Since responses lib
    # matches request-by-request, stub a completed response with cap-sized rows.
    big_rows = [{"tx_hash": f"0x{i:064x}"} for i in range(100000)]
    execute_resp = {"execution_id": "big1", "state": "QUERY_STATE_COMPLETED"}
    results_resp = {
        "execution_id": "big1",
        "state": "QUERY_STATE_COMPLETED",
        "result": {"rows": big_rows, "metadata": {"column_names": ["tx_hash"]}},
    }
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/555/execute",
        json=execute_resp, status=200,
    )
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/execution/big1/results",
        json=results_resp, status=200,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="at or above cap"):
        client.execute_query(555)


@responses.activate
def test_unexpected_schema_on_submit_raises_dune_query_error():
    """I-1/I-4: missing execution_id in submit response → DuneQueryError."""
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/1234/execute",
        json={"state": "QUERY_STATE_PENDING"}, status=200,  # no execution_id
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="unexpected schema"):
        client.execute_query(1234)


@responses.activate
def test_fetch_latest_results_returns_rows_when_completed():
    results_resp = {
        "execution_id": "e1",
        "state": "QUERY_STATE_COMPLETED",
        "query_parameters": [
            {"key": "blockchain", "value": "ethereum", "type": "text"},
            {"key": "contract_address", "value": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "type": "text"},
        ],
        "result": {
            "rows": [{"tx_hash": "0xdead"}, {"tx_hash": "0xbeef"}],
            "metadata": {"column_names": ["tx_hash"]},
        },
    }
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/query/7338524/results",
        json=results_resp, status=200,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    rows = client.fetch_latest_results(
        query_id=7338524,
        expected_params={
            "blockchain": "ethereum",
            "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48",
        },
    )
    assert len(rows) == 2
    assert rows[0]["tx_hash"] == "0xdead"


@responses.activate
def test_fetch_latest_results_raises_when_params_mismatch():
    results_resp = {
        "execution_id": "e1",
        "state": "QUERY_STATE_COMPLETED",
        "query_parameters": [
            {"key": "blockchain", "value": "base", "type": "text"},  # wrong chain
            {"key": "contract_address", "value": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48", "type": "text"},
        ],
        "result": {"rows": [], "metadata": {"column_names": []}},
    }
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/query/7338524/results",
        json=results_resp, status=200,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="mismatched parameters"):
        client.fetch_latest_results(
            query_id=7338524,
            expected_params={"blockchain": "ethereum", "contract_address": "0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48"},
        )


@responses.activate
def test_fetch_latest_results_raises_when_not_completed():
    results_resp = {
        "execution_id": "e1",
        "state": "QUERY_STATE_PENDING",
        "result": {"rows": [], "metadata": {"column_names": []}},
    }
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/query/7338524/results",
        json=results_resp, status=200,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="is in state 'QUERY_STATE_PENDING'"):
        client.fetch_latest_results(query_id=7338524)


@responses.activate
def test_dune_error_includes_response_body():
    """Response body is surfaced in DuneQueryError (was previously swallowed)."""
    responses.add(
        responses.POST,
        "https://api.dune.com/api/v1/query/1234/execute",
        json={"error": "Invalid performance tier"}, status=400,
    )
    client = DuneClient(api_key="test-key", poll_interval_sec=0)
    with pytest.raises(DuneQueryError, match="Invalid performance tier"):
        client.execute_query(1234)


# ---------------------------------------------------------------------------
# Saved-query SQL read/update (used to switch the `<chain>.logs` table between
# per-chain executions of the single shared saved query).
# ---------------------------------------------------------------------------

@responses.activate
def test_get_query_sql_returns_sql_text():
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/query/555",
        json={"query_id": 555, "name": "blacklist", "query_sql": "SELECT 1 FROM ethereum.logs"},
        status=200,
    )
    client = DuneClient(api_key="test-key")
    assert client.get_query_sql(555) == "SELECT 1 FROM ethereum.logs"


@responses.activate
def test_update_query_sql_patches_query_and_returns_none():
    responses.add(
        responses.PATCH,
        "https://api.dune.com/api/v1/query/555",
        json={"query_id": 555},
        status=200,
    )
    client = DuneClient(api_key="test-key")
    assert client.update_query_sql(555, "SELECT 1 FROM base.logs") is None
    body = json.loads(responses.calls[0].request.body)
    assert body == {"query_sql": "SELECT 1 FROM base.logs"}


@responses.activate
def test_update_query_sql_http_error_wraps_as_dune_query_error():
    responses.add(
        responses.PATCH,
        "https://api.dune.com/api/v1/query/555",
        json={"error": "forbidden"},
        status=403,
    )
    client = DuneClient(api_key="test-key")
    with pytest.raises(DuneQueryError, match="update"):
        client.update_query_sql(555, "SELECT 1")


@responses.activate
def test_get_query_sql_missing_field_raises():
    responses.add(
        responses.GET,
        "https://api.dune.com/api/v1/query/555",
        json={"query_id": 555},
        status=200,
    )
    client = DuneClient(api_key="test-key")
    with pytest.raises(DuneQueryError, match="query_sql"):
        client.get_query_sql(555)


# ---------------------------------------------------------------------------
# Rate limiting: a 429 during polling or fetching must back off and retry,
# not abort the run (Dune's free tier rate-limits API calls per minute).
# ---------------------------------------------------------------------------

@responses.activate
def test_poll_backs_off_on_429_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr("scripts.utils.dune_client.time.sleep", lambda s: sleeps.append(s))
    responses.add(responses.POST, "https://api.dune.com/api/v1/query/1/execute",
                  json={"execution_id": "e1", "state": "QUERY_STATE_PENDING"}, status=200)
    responses.add(responses.GET, "https://api.dune.com/api/v1/execution/e1/results",
                  json={"error": "Too many requests"}, status=429)
    responses.add(responses.GET, "https://api.dune.com/api/v1/execution/e1/results",
                  json={"state": "QUERY_STATE_COMPLETED", "result": {"rows": [{"a": 1}]}}, status=200)

    client = DuneClient(api_key="k", poll_interval_sec=0, rate_limit_backoff_sec=7)
    assert client.execute_query(1) == [{"a": 1}]
    assert 7 in sleeps  # backed off once on the 429


@responses.activate
def test_fetch_latest_results_backs_off_on_429_then_succeeds(monkeypatch):
    sleeps = []
    monkeypatch.setattr("scripts.utils.dune_client.time.sleep", lambda s: sleeps.append(s))
    responses.add(responses.GET, "https://api.dune.com/api/v1/query/1/results",
                  json={"error": "Too many requests"}, status=429)
    responses.add(responses.GET, "https://api.dune.com/api/v1/query/1/results",
                  json={"state": "QUERY_STATE_COMPLETED", "result": {"rows": [{"a": 2}]}}, status=200)

    client = DuneClient(api_key="k", rate_limit_backoff_sec=3)
    assert client.fetch_latest_results(1) == [{"a": 2}]
    assert sleeps == [3]


@responses.activate
def test_persistent_429_eventually_raises(monkeypatch):
    monkeypatch.setattr("scripts.utils.dune_client.time.sleep", lambda s: None)
    for _ in range(10):
        responses.add(responses.GET, "https://api.dune.com/api/v1/query/1/results",
                      json={"error": "Too many requests"}, status=429)
    client = DuneClient(api_key="k", rate_limit_backoff_sec=1, max_rate_limit_retries=3)
    with pytest.raises(DuneQueryError, match="429"):
        client.fetch_latest_results(1)
