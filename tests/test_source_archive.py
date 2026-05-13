import hashlib
import json
from pathlib import Path
import pytest
import responses
from scripts.utils.source_archive import (
    compute_sha256,
    store_local,
    archive_to_wayback,
    fetch_and_store,
    ArchiveManifest,
)


FIXTURE = Path(__file__).parent / "fixtures" / "example.html"


def test_compute_sha256_matches_hashlib():
    content = FIXTURE.read_bytes()
    assert compute_sha256(content) == hashlib.sha256(content).hexdigest()


def test_store_local_writes_file_and_returns_path(tmp_path):
    content = b"<html>hello</html>"
    path = store_local(content, source_id="CU-SRC-0001", root=tmp_path, extension="html")
    assert path.exists()
    assert path.read_bytes() == content
    # Year-partitioned by convention.
    assert "CU-SRC-0001.html" in str(path)


@responses.activate
def test_archive_to_wayback_returns_snapshot_url():
    target_url = "https://example.com/page"
    responses.add(
        responses.GET,
        "https://web.archive.org/save/https://example.com/page",
        headers={"Content-Location": "/web/20260417120000/https://example.com/page"},
        status=200,
    )
    snapshot = archive_to_wayback(target_url)
    assert snapshot == "https://web.archive.org/web/20260417120000/https://example.com/page"


@responses.activate
def test_fetch_and_store_roundtrip(tmp_path):
    target_url = "https://example.com/doc"
    body = b"<html>doc</html>"
    responses.add(responses.GET, target_url, body=body, status=200)
    responses.add(
        responses.GET,
        "https://web.archive.org/save/https://example.com/doc",
        headers={"Content-Location": "/web/20260417120000/https://example.com/doc"},
        status=200,
    )
    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps({"schema_version": 1, "sources": {}}))
    manifest = ArchiveManifest(manifest_path)

    record = fetch_and_store(
        url=target_url,
        source_id="CU-SRC-0042",
        root=tmp_path,
        manifest=manifest,
    )

    assert record["local_path"].endswith("CU-SRC-0042.html")
    assert record["content_sha256"] == hashlib.sha256(body).hexdigest()
    assert record["archived_url"].startswith("https://web.archive.org/")
    # Manifest is persisted on disk.
    assert "CU-SRC-0042" in json.loads(manifest_path.read_text())["sources"]


def test_manifest_roundtrip(tmp_path):
    mf = tmp_path / "manifest.json"
    mf.write_text(json.dumps({"schema_version": 1, "sources": {}}))
    m = ArchiveManifest(mf)
    m.add("CU-SRC-0001", {"local_path": "foo", "content_sha256": "abc"})
    m.save()
    loaded = json.loads(mf.read_text())
    assert loaded["sources"]["CU-SRC-0001"]["content_sha256"] == "abc"


def test_archive_manifest_initializes_empty_when_file_missing(tmp_path):
    """I1: ArchiveManifest handles missing file gracefully."""
    missing = tmp_path / "new_manifest.json"
    assert not missing.exists()
    manifest = ArchiveManifest(missing)
    assert manifest.get("anything") is None
    manifest.save()
    assert missing.exists()
    import json
    assert json.loads(missing.read_text()) == {"schema_version": 1, "sources": {}}


def test_archive_manifest_save_is_atomic(tmp_path):
    """I2: save() does not leave a .tmp file on success."""
    mf = tmp_path / "manifest.json"
    mf.write_text('{"schema_version": 1, "sources": {}}')
    manifest = ArchiveManifest(mf)
    manifest.add("CU-SRC-0001", {"local_path": "foo", "content_sha256": "abc"})
    manifest.save()
    # Temp file must not linger after successful save.
    tmp = mf.with_suffix(".json.tmp")
    assert not tmp.exists()
    # Final file has the entry.
    import json
    assert "CU-SRC-0001" in json.loads(mf.read_text())["sources"]


def test_store_local_refuses_overwrite_with_different_bytes(tmp_path):
    """I5: store_local raises on content collision."""
    store_local(b"<html>v1</html>", source_id="CU-SRC-0001", root=tmp_path, extension="html")
    with pytest.raises(FileExistsError, match="different content"):
        store_local(b"<html>v2</html>", source_id="CU-SRC-0001", root=tmp_path, extension="html")


def test_store_local_allows_idempotent_rewrite(tmp_path):
    """I5 follow-up: same bytes is fine (retry case)."""
    path1 = store_local(b"<html>v1</html>", source_id="CU-SRC-0001", root=tmp_path, extension="html")
    path2 = store_local(b"<html>v1</html>", source_id="CU-SRC-0001", root=tmp_path, extension="html")
    assert path1 == path2


@responses.activate
def test_archive_to_wayback_returns_none_on_http_failure():
    """I4 follow-up: archive_to_wayback swallows failures."""
    responses.add(
        responses.GET,
        "https://web.archive.org/save/https://example.com/down",
        status=503,
    )
    assert archive_to_wayback("https://example.com/down") is None


@responses.activate
def test_archive_to_wayback_returns_none_on_missing_content_location():
    """I4 follow-up: no Content-Location header → None."""
    responses.add(
        responses.GET,
        "https://web.archive.org/save/https://example.com/page",
        status=200,
    )
    assert archive_to_wayback("https://example.com/page") is None
