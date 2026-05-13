"""Thin wrapper around the Dune Analytics v1 API.

Supports: executing a saved query, polling for completion, retrieving results.
Does NOT support uploading new queries programmatically — Dune's free tier requires
queries to be created via the web UI. Query IDs are stored in
`scripts/config/dune_queries/*.sql` for version control, but executed by ID.
"""
from __future__ import annotations

import time
from typing import Any

import requests

_BASE_URL = "https://api.dune.com/api/v1"
_TERMINAL_STATES = {"QUERY_STATE_COMPLETED", "QUERY_STATE_FAILED", "QUERY_STATE_CANCELLED"}
_HTTP_TIMEOUT_SEC = 60.0   # Per-request HTTP timeout. Intentionally > default 30s for large results.
_MAX_RESULT_LIMIT = 100000 # Cap on rows fetched in a single results call. See _poll_results.


class DuneQueryError(RuntimeError):
    """Raised when a Dune query execution fails or is cancelled."""


def _format_request_error(e: requests.RequestException) -> str:
    """Format a RequestException for DuneQueryError, including response body when available."""
    body = ""
    if isinstance(e, requests.HTTPError) and e.response is not None:
        try:
            body = f" body={e.response.text[:500]!r}"
        except Exception:
            body = ""
    return f"{e}{body}"


class DuneClient:
    def __init__(self, api_key: str, poll_interval_sec: float = 2.0, timeout_sec: float = 300.0):
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._poll = poll_interval_sec
        self._timeout = timeout_sec
        self._session = requests.Session()
        self._session.headers.update({"X-Dune-API-Key": api_key})

    def execute_query(
        self,
        query_id: int,
        params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Run a saved Dune query, poll to completion, return result rows.

        Caps result size at 100,000 rows. Raises DuneQueryError if the query would
        return more — signaling the caller to implement pagination (not currently
        needed for USDC on-chain scans).

        Raises:
            DuneQueryError: on HTTP failure, query failure, cancellation, timeout,
                unexpected response schema, or row-count cap exceeded.
        """
        execution_id = self._submit(query_id, params)
        result = self._poll_results(execution_id)
        state = result["state"]
        if state != "QUERY_STATE_COMPLETED":
            error_msg = result.get("error", f"state={state}")
            raise DuneQueryError(error_msg)
        rows = result.get("result", {}).get("rows", [])
        if len(rows) >= _MAX_RESULT_LIMIT:
            raise DuneQueryError(
                f"result row count ({len(rows)}) at or above cap ({_MAX_RESULT_LIMIT}); "
                f"pagination not implemented — consider chunking the query or adding "
                f"offset/limit support"
            )
        return rows

    def fetch_latest_results(
        self,
        query_id: int,
        expected_params: dict[str, Any] | None = None,
    ) -> list[dict[str, Any]]:
        """Fetch cached results of the most recent execution of a saved query.

        Does NOT trigger execution. Use on Dune's free tier where programmatic
        execution is not available — the user manually runs the query in Dune's
        web UI, then this method retrieves those cached results.

        If `expected_params` is provided, verifies the cached execution was run
        with matching parameter values and raises DuneQueryError on mismatch.

        Raises:
            DuneQueryError: on HTTP failure, missing/pending execution, unexpected
                schema, row-cap exceeded, or parameter mismatch.
        """
        url = f"{_BASE_URL}/query/{query_id}/results"
        try:
            r = self._session.get(
                url, timeout=_HTTP_TIMEOUT_SEC, params={"limit": _MAX_RESULT_LIMIT}
            )
            r.raise_for_status()
        except requests.RequestException as e:
            raise DuneQueryError(
                f"Dune fetch results failed for query_id={query_id}: {_format_request_error(e)}"
            ) from e
        try:
            data = r.json()
        except ValueError as e:
            raise DuneQueryError(
                f"Dune returned invalid JSON for query_id={query_id}: {e}"
            ) from e

        state = data.get("state")
        if state != "QUERY_STATE_COMPLETED":
            raise DuneQueryError(
                f"latest execution for query_id={query_id} is in state {state!r} "
                f"— run the query manually in Dune's web UI first"
            )

        # Verify execution params match expected, when Dune returns them.
        if expected_params:
            # Dune returns execution parameters in data['query_parameters'] as a list
            # of {'key', 'value', 'type'} dicts, or may omit this field entirely for
            # parameterless queries / older API versions.
            exec_params_raw = data.get("query_parameters") or []
            actual = {}
            for p in exec_params_raw:
                if isinstance(p, dict) and "key" in p:
                    actual[p["key"]] = p.get("value", "")
            if actual:
                mismatches = []
                for key, expected_val in expected_params.items():
                    actual_val = actual.get(key)
                    if str(actual_val) != str(expected_val):
                        mismatches.append(
                            f"{key}: expected {expected_val!r}, got {actual_val!r}"
                        )
                if mismatches:
                    raise DuneQueryError(
                        f"cached execution for query_id={query_id} has mismatched "
                        f"parameters: {'; '.join(mismatches)} — re-run the query in "
                        f"Dune's UI with the correct parameters"
                    )
            else:
                # No parameter info returned — log to stderr as a warning.
                import sys as _sys
                print(
                    f"WARNING: Dune did not return execution parameters for query_id="
                    f"{query_id}; cannot verify the cached run used "
                    f"{expected_params!r}. Trusting the user's manual execution.",
                    file=_sys.stderr,
                )

        rows = data.get("result", {}).get("rows", [])
        if len(rows) >= _MAX_RESULT_LIMIT:
            raise DuneQueryError(
                f"result row count ({len(rows)}) at or above cap ({_MAX_RESULT_LIMIT}); "
                f"pagination not implemented"
            )
        return rows

    def _submit(self, query_id: int, params: dict[str, Any] | None) -> str:
        url = f"{_BASE_URL}/query/{query_id}/execute"
        body: dict[str, Any] = {}
        if params:
            body["query_parameters"] = params
        try:
            r = self._session.post(url, json=body, timeout=_HTTP_TIMEOUT_SEC)
            r.raise_for_status()
        except requests.RequestException as e:
            raise DuneQueryError(f"Dune submit failed for query_id={query_id}: {_format_request_error(e)}") from e
        data = r.json()
        if "execution_id" not in data:
            raise DuneQueryError(f"Dune submit returned unexpected schema: {data}")
        return data["execution_id"]

    def _poll_results(self, execution_id: str) -> dict[str, Any]:
        url = f"{_BASE_URL}/execution/{execution_id}/results"
        deadline = time.time() + self._timeout
        while True:
            try:
                r = self._session.get(url, timeout=_HTTP_TIMEOUT_SEC, params={"limit": _MAX_RESULT_LIMIT})
                r.raise_for_status()
            except requests.RequestException as e:
                raise DuneQueryError(f"Dune poll failed for execution_id={execution_id}: {_format_request_error(e)}") from e
            data = r.json()
            if "state" not in data:
                raise DuneQueryError(f"Dune poll returned unexpected schema: missing 'state'")
            if data["state"] in _TERMINAL_STATES:
                return data
            if time.time() > deadline:
                raise DuneQueryError(f"poll timeout after {self._timeout}s for execution_id={execution_id}")
            time.sleep(self._poll)
