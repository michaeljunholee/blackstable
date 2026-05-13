import json
from pathlib import Path
import pytest
import responses
from scripts.utils.wayback_client import WaybackClient


FIXTURES = Path(__file__).parent / "fixtures"


@responses.activate
def test_list_snapshots_returns_parsed_rows():
    rows = json.loads((FIXTURES / "wayback_cdx_response.json").read_text())
    responses.add(
        responses.GET,
        "https://web.archive.org/cdx/search/cdx",
        json=rows, status=200,
    )
    client = WaybackClient()
    snapshots = client.list_snapshots("https://www.circle.com/legal/terms")
    assert len(snapshots) == 2
    assert snapshots[0]["timestamp"] == "20190115120000"
    assert snapshots[0]["original"] == "https://www.circle.com/legal/terms"
    assert snapshots[1]["digest"] == "DEF456"


@responses.activate
def test_fetch_snapshot_returns_content():
    responses.add(
        responses.GET,
        "https://web.archive.org/web/20190115120000/https://www.circle.com/legal/terms",
        body=b"<html>terms v1</html>",
        status=200,
    )
    client = WaybackClient()
    content = client.fetch_snapshot(
        url="https://www.circle.com/legal/terms",
        timestamp="20190115120000",
    )
    assert content == b"<html>terms v1</html>"


from scripts.utils.wayback_client import WaybackError


@responses.activate
def test_wayback_list_snapshots_http_error_wraps_as_wayback_error():
    """I-2: 504 from CDX surfaces as WaybackError."""
    responses.add(
        responses.GET,
        "https://web.archive.org/cdx/search/cdx",
        status=504,
    )
    client = WaybackClient()
    with pytest.raises(WaybackError, match="CDX request failed"):
        client.list_snapshots("https://www.circle.com/legal/terms")


@responses.activate
def test_wayback_fetch_snapshot_http_error_wraps_as_wayback_error():
    """I-2: replay-endpoint failure surfaces as WaybackError."""
    responses.add(
        responses.GET,
        "https://web.archive.org/web/20190115120000/https://www.circle.com/legal/terms",
        status=503,
    )
    client = WaybackClient()
    with pytest.raises(WaybackError, match="Wayback fetch failed"):
        client.fetch_snapshot(
            url="https://www.circle.com/legal/terms",
            timestamp="20190115120000",
        )


def test_wayback_list_snapshots_empty_cdx_returns_empty_list():
    """Sanity: empty CDX response returns []."""
    import responses as responses_mod
    @responses_mod.activate
    def _run():
        responses_mod.add(
            responses_mod.GET,
            "https://web.archive.org/cdx/search/cdx",
            json=[], status=200,
        )
        client = WaybackClient()
        assert client.list_snapshots("https://www.circle.com/never-crawled") == []
    _run()


def test_wayback_error_subclasses_runtime_error():
    """I-2: WaybackError is a RuntimeError subclass for generic exception-catchers."""
    assert issubclass(WaybackError, RuntimeError)
