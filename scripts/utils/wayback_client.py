"""Thin wrapper around archive.org's CDX and Wayback APIs.

Used to enumerate historical Circle policy snapshots and fetch specific captures.

Rate limiting is per-instance. Reuse a single `WaybackClient`; do not construct
multiple in parallel — the rate limiter does not coordinate across instances.
"""
from __future__ import annotations

import time
from typing import Any

import requests

_CDX_URL = "https://web.archive.org/cdx/search/cdx"
_WAYBACK_FETCH = "https://web.archive.org/web/{timestamp}/{url}"


class WaybackError(RuntimeError):
    """Raised when archive.org returns an HTTP error or malformed response."""


class WaybackClient:
    def __init__(self, rate_limit_sec: float = 1.5, timeout_sec: float = 30.0) -> None:
        self._rate = rate_limit_sec
        self._timeout = timeout_sec
        self._last_call = 0.0

    def _respect_rate_limit(self) -> None:
        elapsed = time.time() - self._last_call
        if elapsed < self._rate:
            time.sleep(self._rate - elapsed)
        self._last_call = time.time()

    def list_snapshots(
        self,
        url: str,
        from_timestamp: str | None = None,
        to_timestamp: str | None = None,
    ) -> list[dict[str, Any]]:
        """Return list of CDX capture records for `url` with changed-digest collapse.

        Raises:
            WaybackError: on HTTP failure or malformed CDX JSON.
        """
        self._respect_rate_limit()
        params: dict[str, Any] = {
            "url": url,
            "output": "json",
            "collapse": "digest",
        }
        if from_timestamp:
            params["from"] = from_timestamp
        if to_timestamp:
            params["to"] = to_timestamp

        try:
            r = requests.get(_CDX_URL, params=params, timeout=self._timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise WaybackError(f"CDX request failed for {url}: {e}") from e
        try:
            rows = r.json()
        except ValueError as e:
            raise WaybackError(f"CDX returned invalid JSON for {url}: {e}") from e
        if not rows:
            return []
        header = rows[0]
        return [dict(zip(header, row)) for row in rows[1:]]

    def fetch_snapshot(self, url: str, timestamp: str) -> bytes:
        """Fetch the raw bytes of a specific Wayback capture.

        Raises:
            WaybackError: on HTTP failure.
        """
        self._respect_rate_limit()
        target = _WAYBACK_FETCH.format(timestamp=timestamp, url=url)
        try:
            r = requests.get(target, timeout=self._timeout)
            r.raise_for_status()
        except requests.RequestException as e:
            raise WaybackError(f"Wayback fetch failed for {url}@{timestamp}: {e}") from e
        return r.content
