from pathlib import Path
import pytest

import importlib.util
_APATH = Path(__file__).parent.parent / "scripts" / "02_archive_policies.py"
_spec = importlib.util.spec_from_file_location("archive_policies", _APATH)
archive_policies = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(archive_policies)


def test_cdx_timestamp_to_iso_date():
    assert archive_policies.cdx_timestamp_to_iso("20190115120000") == "2019-01-15"


def test_html_to_markdown_strips_tags(tmp_path):
    html = b"<html><body><h1>Title</h1><p>Paragraph with <b>bold</b>.</p></body></html>"
    md = archive_policies.html_to_markdown(html)
    assert "# Title" in md or "Title" in md
    assert "<h1>" not in md
    assert "bold" in md


def test_build_policy_row_produces_canonical_fields(tmp_path):
    row = archive_policies.build_policy_row(
        policy_id="CU-POL-0001",
        policy_name="Circle Terms of Service",
        policy_type="TERMS_OF_SERVICE",
        effective_date="2019-01-15",
        document_path="policies/tos_2019-01-15.md",
        source_id="CU-SRC-0001",
    )
    from scripts.utils.schema import TABLE_HEADERS
    assert set(row.keys()) == set(TABLE_HEADERS["policies"])
    assert row["policy_type"] == "TERMS_OF_SERVICE"
    assert row["effective_date"] == "2019-01-15"
