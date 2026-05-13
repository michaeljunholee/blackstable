"""Fetch, hash, and archive URLs for the CircleUSDC sources audit trail."""
from __future__ import annotations

import hashlib
import json
import mimetypes
import time
from pathlib import Path
from typing import Any

import requests

_WAYBACK_SAVE = "https://web.archive.org/save/{url}"
_DEFAULT_TIMEOUT_SEC = 30.0


def compute_sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _year_partition(source_id: str) -> str:
    # Default partition by current year. When integrating, caller can override path.
    from datetime import datetime, timezone
    return str(datetime.now(timezone.utc).year)


def store_local(
    content: bytes,
    source_id: str,
    root: Path,
    extension: str = "bin",
) -> Path:
    """Write content to `root/<year>/<source_id>.<extension>` and return the path.

    Raises `FileExistsError` if the target file exists with different bytes — this
    prevents silent loss of an earlier snapshot when the same source_id is reused
    for drifted content. Identical-bytes overwrites are silent (idempotent retry).
    """
    year_dir = root / _year_partition(source_id)
    year_dir.mkdir(parents=True, exist_ok=True)
    path = year_dir / f"{source_id}.{extension}"
    if path.exists() and path.read_bytes() != content:
        raise FileExistsError(
            f"{path} exists with different content; refusing to overwrite"
        )
    path.write_bytes(content)
    return path


def archive_to_wayback(url: str, timeout: float = _DEFAULT_TIMEOUT_SEC) -> str | None:
    """Request a Wayback snapshot of `url`. Return the snapshot URL or None on failure.

    Non-blocking on failure: archive.org's Save Page Now is rate-limited and sometimes
    returns 5xx; we never block the caller on archive failure.
    """
    endpoint = _WAYBACK_SAVE.format(url=url)
    try:
        resp = requests.get(endpoint, timeout=timeout, allow_redirects=False)
    except requests.RequestException:
        return None

    content_location = resp.headers.get("Content-Location")
    if content_location:
        return f"https://web.archive.org{content_location}"
    return None


def _guess_extension(url: str, content_type: str | None, body: bytes | None = None) -> str:
    # URL-based hints first: authoritative when the server echoes a generic
    # Content-Type (e.g. `text/plain`) that would otherwise mis-classify.
    url_lower = url.lower()
    if url_lower.endswith(".pdf"):
        return "pdf"
    if url_lower.endswith((".html", ".htm")):
        return "html"

    if content_type:
        mt = content_type.split(";")[0].strip().lower()
        if mt in {"text/html", "application/xhtml+xml"}:
            return "html"
        if mt == "application/pdf":
            return "pdf"
        ext = mimetypes.guess_extension(mt)
        if ext and ext != ".txt":
            return ext.lstrip(".")

    # Content sniffing as a last resort: detect HTML/PDF magic bytes.
    if body:
        head = body[:512].lstrip().lower()
        if head.startswith(b"<!doctype html") or head.startswith(b"<html"):
            return "html"
        if body[:4] == b"%PDF":
            return "pdf"

    if content_type and content_type.split(";")[0].strip().lower() == "text/plain":
        return "txt"
    return "bin"


def fetch_and_store(
    url: str,
    source_id: str,
    root: Path,
    manifest: "ArchiveManifest",
    rate_limit_sec: float = 1.0,
) -> dict[str, Any]:
    """Fetch a URL, hash it, store locally, request Wayback archival, update manifest.

    Returns a dict with `local_path`, `content_sha256`, and `archived_url` (which
    is `None` if Wayback archival failed).

    Raises:
        requests.HTTPError: on a non-2xx response from the source URL.
        OSError / PermissionError: if the local file cannot be written.
        FileExistsError: if `source_id` was previously stored with different bytes.

    Wayback archival failures are swallowed and reported as `archived_url=None`.
    On any raised exception, the manifest is NOT updated; callers should treat
    this function as all-or-nothing from the manifest's perspective and retry.
    """
    response = requests.get(url, timeout=_DEFAULT_TIMEOUT_SEC)
    response.raise_for_status()
    content = response.content
    extension = _guess_extension(url, response.headers.get("Content-Type"), content)
    path = store_local(content, source_id, root, extension)
    sha = compute_sha256(content)

    time.sleep(rate_limit_sec)
    archived = archive_to_wayback(url)

    record = {
        "local_path": str(path),
        "content_sha256": sha,
        "archived_url": archived,
    }
    manifest.add(source_id, record)
    manifest.save()
    return record


class ArchiveManifest:
    """Thin read/write wrapper over `sources/manifest.json`.

    NOT safe for concurrent writers: the class reads the file on init, keeps
    state in memory, and overwrites on save. If Pass A is ever parallelized,
    switch to file locking (`fcntl.flock`), per-source sidecar files, or
    append-only JSONL.
    """

    def __init__(self, path: Path) -> None:
        """Read manifest at `path`, or initialize an empty one if the file is missing.

        Consumers should call `.save()` to persist the initialized skeleton, or let
        `fetch_and_store` do so implicitly when it records its first entry.
        """
        self.path = Path(path)
        if self.path.exists():
            with open(self.path) as f:
                self._data = json.load(f)
        else:
            self._data = {"schema_version": 1, "sources": {}}

    def add(self, source_id: str, record: dict[str, Any]) -> None:
        self._data.setdefault("sources", {})[source_id] = record

    def save(self) -> None:
        """Atomically persist the manifest via write-then-rename."""
        tmp = self.path.with_suffix(self.path.suffix + ".tmp")
        with open(tmp, "w") as f:
            json.dump(self._data, f, indent=2, sort_keys=True)
        tmp.replace(self.path)

    def get(self, source_id: str) -> dict[str, Any] | None:
        return self._data.get("sources", {}).get(source_id)

    def verify_hash(self, source_id: str) -> bool:
        """Re-hash the local file and compare against the manifest. Returns True on match."""
        record = self.get(source_id)
        if not record or "local_path" not in record:
            return False
        try:
            content = Path(record["local_path"]).read_bytes()
        except FileNotFoundError:
            return False
        return compute_sha256(content) == record.get("content_sha256")
