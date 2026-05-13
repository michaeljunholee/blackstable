"""Thin wrapper around the Etherscan v1 API with built-in rate limiting.

Used as a verification layer for Dune scan results. Free tier: 5 calls/second.

Rate limiting is per-instance. Reuse a single `EtherscanClient` across calls;
do not construct multiple instances in parallel — the rate limiter does not
coordinate across instances.
"""
from __future__ import annotations

import time
from typing import Any

import requests

_BASE_URL = "https://api.etherscan.io/api"
_RATE_LIMIT_SEC = 0.25  # 4 req/sec under the 5/sec limit
_HTTP_TIMEOUT_SEC = 30.0


class EtherscanError(RuntimeError):
    """Raised when Etherscan returns an API-level error, HTTP error, or the response
    hits the pagination cap (silent-truncation guard)."""


class EtherscanClient:
    def __init__(
        self,
        api_key: str,
        rate_limit_sec: float = _RATE_LIMIT_SEC,
        timeout_sec: float = _HTTP_TIMEOUT_SEC,
    ) -> None:
        if not api_key:
            raise ValueError("api_key is required")
        self._api_key = api_key
        self._rate = rate_limit_sec
        self._timeout = timeout_sec
        self._last_call = 0.0

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_call
        if elapsed < self._rate:
            time.sleep(self._rate - elapsed)
        self._last_call = time.time()

    def get_logs(
        self,
        address: str,
        topic0: str,
        from_block: int,
        to_block: int,
        page: int = 1,
        offset: int = 1000,
    ) -> list[dict[str, Any]]:
        """Return event logs matching `topic0` emitted by `address` between blocks.

        Raises:
            EtherscanError: on HTTP failure, Etherscan API-level error, or if the
                result size equals `offset` (signaling silent truncation — caller
                should narrow the block window or implement pagination).
        """
        self._respect_rate_limit()
        params = {
            "module": "logs",
            "action": "getLogs",
            "address": address,
            "topic0": topic0,
            "fromBlock": from_block,
            "toBlock": to_block,
            "page": page,
            "offset": offset,
            "apikey": self._api_key,
        }
        try:
            r = requests.get(_BASE_URL, params=params, timeout=self._timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise EtherscanError(f"Etherscan request failed: {e}") from e
        try:
            data = r.json()
        except ValueError as e:
            raise EtherscanError(f"Etherscan returned invalid JSON: {e}") from e
        if data.get("status") != "1" and data.get("message") != "No records found":
            raise EtherscanError(data.get("result") or data.get("message", "etherscan error"))
        result = data.get("result", [])
        if isinstance(result, str):
            raise EtherscanError(result)
        if len(result) >= offset:
            raise EtherscanError(
                f"result count ({len(result)}) at or above offset cap ({offset}); "
                f"pagination not implemented — narrow the block window or extend get_logs"
            )
        return result
