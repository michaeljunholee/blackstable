"""Tests for scripts/build/notes_render.py — Markdown to HTML."""
from pathlib import Path
import pytest

from scripts.build.notes_render import markdown_to_html


def test_markdown_to_html_basic_paragraph():
    md = "# Title\n\nA paragraph.\n"
    html = markdown_to_html(md)
    assert "<h1" in html  # toc extension adds id attr: <h1 id="...">
    assert "<p>" in html
    assert "Title" in html
    assert "A paragraph." in html


def test_markdown_to_html_internal_link_rewrites():
    """A markdown link to notes/foo.md should rewrite to foo.html in
    the rendered output (notes are rendered as siblings under docs/dashboard/notes/)."""
    md = "See [the case](notes/CU-ACT-0001.md)."
    html = markdown_to_html(md)
    assert "CU-ACT-0001.html" in html
    assert "CU-ACT-0001.md" not in html


def test_markdown_to_html_address_block_preserved():
    md = "Address: `0xaa05f7c7eb9af63d6cc03c36c4f4ef6c37431ee0`"
    html = markdown_to_html(md)
    assert "0xaa05f7c7eb9af63d6cc03c36c4f4ef6c37431ee0" in html
    assert "<code>" in html
