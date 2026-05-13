"""Render Markdown notes to HTML for the dashboard.

Uses Python-Markdown with extensions for tables and code highlighting.
Rewrites internal links from .md → .html (since notes are rendered side-by-side).
"""
import re
from pathlib import Path
import markdown


_MD_EXTENSIONS = ["tables", "fenced_code", "toc"]


def markdown_to_html(md_text: str) -> str:
    """Convert raw Markdown text to HTML, rewriting internal .md links."""
    # Rewrite internal links to other notes:
    # [text](notes/foo.md) → [text](foo.html)
    md_text = re.sub(r"\]\(notes/([^)]+)\.md\)", r"](\1.html)", md_text)
    # Rewrite ../notes/foo.md → foo.html
    md_text = re.sub(r"\]\(\.\./notes/([^)]+)\.md\)", r"](\1.html)", md_text)
    return markdown.markdown(md_text, extensions=_MD_EXTENSIONS)


def render_note_to_html(md_file: Path, env, data: dict, site_config: dict | None = None) -> str:
    """Render a Markdown note file into a complete HTML page using
    notes_detail.html.j2 as the wrapper.
    """
    md_text = md_file.read_text(encoding="utf-8")
    body_html = markdown_to_html(md_text)
    template = env.get_template("notes_detail.html.j2")
    return template.render(
        title=md_file.stem,
        body=body_html,
        page="notes",
        site_config=site_config or {},
    )
