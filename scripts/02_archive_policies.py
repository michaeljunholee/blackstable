#!/usr/bin/env python3
"""Archive Circle policy documents from the Wayback Machine.

For each URL in `scripts/config/policy_urls.yaml`:
    1. List Wayback snapshots via CDX API.
    2. For each unique capture (by digest), fetch the snapshot.
    3. Convert HTML to Markdown, save to `policies/<slug>_<date>.md`.
    4. Record a `policies.csv` row and a `sources.csv` row.
    5. Optionally compute diff between consecutive captures (deferred to notebook 02).
"""
from __future__ import annotations

import hashlib
import os
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd
import yaml
from bs4 import BeautifulSoup
from dotenv import load_dotenv

_HERE = Path(__file__).parent
sys.path.insert(0, str(_HERE.parent))

from scripts.utils import schema
from scripts.utils.id_minter import mint_id
from scripts.utils.wayback_client import WaybackClient
from scripts.utils.source_archive import ArchiveManifest


def cdx_timestamp_to_iso(timestamp: str) -> str:
    """Convert CDX timestamp (YYYYMMDDHHMMSS) to ISO date (YYYY-MM-DD)."""
    dt = datetime.strptime(timestamp[:8], "%Y%m%d")
    return dt.strftime("%Y-%m-%d")


def html_to_markdown(html: bytes) -> str:
    """Best-effort HTML -> Markdown. We preserve structure; fidelity is not critical
    since the original HTML is archived with a hash in `sources/`."""
    soup = BeautifulSoup(html, "lxml")
    for script in soup(["script", "style"]):
        script.decompose()
    lines: list[str] = []
    for elem in soup.find_all(["h1", "h2", "h3", "h4", "p", "li"]):
        text = elem.get_text(strip=True)
        if not text:
            continue
        if elem.name == "h1":
            lines.append(f"# {text}")
        elif elem.name == "h2":
            lines.append(f"## {text}")
        elif elem.name == "h3":
            lines.append(f"### {text}")
        elif elem.name == "h4":
            lines.append(f"#### {text}")
        elif elem.name == "li":
            lines.append(f"- {text}")
        else:
            lines.append(text)
        lines.append("")
    return "\n".join(lines)


def _slug_for_url(url: str) -> str:
    """Short slug derived from URL path, e.g. 'tos' for /legal/terms."""
    if "/terms" in url:
        return "tos"
    if "/user-agreement" in url:
        return "user_agreement"
    if "/privacy" in url:
        return "privacy"
    if "/transparency" in url:
        return "transparency"
    if "/blog" in url:
        return "blog_index"
    return hashlib.md5(url.encode()).hexdigest()[:8]


def build_policy_row(
    policy_id: str,
    policy_name: str,
    policy_type: str,
    effective_date: str,
    document_path: str,
    source_id: str,
) -> dict:
    row = {field: "" for field in schema.TABLE_HEADERS["policies"]}
    row["policy_id"] = policy_id
    row["policy_name"] = policy_name
    row["policy_type"] = policy_type
    row["effective_date"] = effective_date
    row["document_path"] = document_path
    row["source_id"] = source_id
    return row


def build_source_row(
    source_id: str,
    url: str,
    archived_url: str,
    local_path: str,
    content_sha256: str,
    publication_date: str,
    policy_name: str,
) -> dict:
    row = {field: "" for field in schema.TABLE_HEADERS["sources"]}
    row["source_id"] = source_id
    row["source_tier"] = "PRIMARY"
    row["source_type"] = "CIRCLE_LEGAL_DOC"
    row["title"] = policy_name
    row["publisher"] = "Circle Internet Financial"
    row["publication_date"] = publication_date
    row["url"] = url
    row["archived_url"] = archived_url
    row["local_path"] = local_path
    row["content_sha256"] = content_sha256
    row["accessed_date"] = datetime.utcnow().strftime("%Y-%m-%d")
    return row


def _supersede_prior_versions(policies_path: Path, policy_type: str, policy_name: str) -> None:
    """Set `superseded_date` on older versions of this policy so the
    timeline is consistent. The latest version stays un-superseded; each
    older version is superseded by the immediately-following version's
    effective_date."""
    df = pd.read_csv(policies_path, dtype=str, keep_default_na=False)
    matches = df[
        (df["policy_type"] == policy_type)
        & (df["policy_name"] == policy_name)
    ].sort_values("effective_date")
    if len(matches) <= 1:
        return
    indices = list(matches.index)
    for prev_idx, next_idx in zip(indices[:-1], indices[1:]):
        df.loc[prev_idx, "superseded_date"] = df.loc[next_idx, "effective_date"]
    # Ensure the latest has no superseded_date.
    df.loc[indices[-1], "superseded_date"] = ""
    df.to_csv(policies_path, index=False)


def process_url(entry: dict, wayback: WaybackClient, data_dir: Path, sources_dir: Path, policies_dir: Path, manifest: ArchiveManifest) -> int:
    url = entry["url"]
    slug = _slug_for_url(url)
    policy_type = entry["policy_type"]
    policy_name = entry["policy_name"]

    try:
        snapshots = wayback.list_snapshots(url)
    except Exception as e:
        # CDX itself can fail (504s, connection timeouts). Don't crash the
        # whole run; log and move to the next URL.
        print(f"[archive_policies] CDX list failed for {url}: {e}")
        return 0
    if not snapshots:
        print(f"[archive_policies] no snapshots for {url}")
        return 0

    existing_policy_ids = pd.read_csv(data_dir / "policies.csv", dtype=str, keep_default_na=False)["policy_id"].tolist()
    existing_source_ids = pd.read_csv(data_dir / "sources.csv", dtype=str, keep_default_na=False)["source_id"].tolist()

    new_policies: list[dict] = []
    new_sources: list[dict] = []

    for snap in snapshots:
        timestamp = snap["timestamp"]
        effective_date = cdx_timestamp_to_iso(timestamp)
        md_path_rel = f"policies/{slug}_{effective_date}.md"
        md_path_abs = data_dir.parent / md_path_rel
        if md_path_abs.exists():
            continue  # Already captured.

        try:
            content = wayback.fetch_snapshot(url, timestamp)
        except Exception as e:
            print(f"[archive_policies] fetch failed {url}@{timestamp}: {e}")
            continue

        md = html_to_markdown(content)
        md_path_abs.parent.mkdir(parents=True, exist_ok=True)
        md_path_abs.write_text(md)

        # Archive raw HTML under sources/
        source_id = mint_id("SRC", existing_source_ids + [r["source_id"] for r in new_sources])
        year_dir = sources_dir / effective_date.split("-")[0]
        year_dir.mkdir(parents=True, exist_ok=True)
        raw_path = year_dir / f"{source_id}.html"
        raw_path.write_bytes(content)
        sha = hashlib.sha256(content).hexdigest()

        archived_url = f"https://web.archive.org/web/{timestamp}/{url}"
        new_sources.append(build_source_row(
            source_id=source_id,
            url=url,
            archived_url=archived_url,
            local_path=str(raw_path.relative_to(data_dir.parent)),
            content_sha256=sha,
            publication_date=effective_date,
            policy_name=policy_name,
        ))
        manifest.add(source_id, {
            "local_path": str(raw_path.relative_to(data_dir.parent)),
            "content_sha256": sha,
            "archived_url": archived_url,
        })

        policy_id = mint_id("POL", existing_policy_ids + [r["policy_id"] for r in new_policies])
        new_policies.append(build_policy_row(
            policy_id=policy_id,
            policy_name=policy_name,
            policy_type=policy_type,
            effective_date=effective_date,
            document_path=md_path_rel,
            source_id=source_id,
        ))

    # Append new rows
    if new_sources:
        pd.DataFrame(new_sources, columns=schema.TABLE_HEADERS["sources"]).to_csv(
            data_dir / "sources.csv", mode="a", header=False, index=False,
        )
    if new_policies:
        pd.DataFrame(new_policies, columns=schema.TABLE_HEADERS["policies"]).to_csv(
            data_dir / "policies.csv", mode="a", header=False, index=False,
        )
    manifest.save()

    _supersede_prior_versions(data_dir / "policies.csv", policy_type, policy_name)
    return len(new_policies)


def main() -> int:
    load_dotenv()
    data_dir = _HERE.parent / "data"
    sources_dir = _HERE.parent / "sources"
    policies_dir = _HERE.parent / "policies"
    policies_dir.mkdir(exist_ok=True)

    manifest = ArchiveManifest(sources_dir / "manifest.json")
    wayback = WaybackClient()

    config_path = _HERE / "config" / "policy_urls.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)

    total = 0
    for entry in config["urls"]:
        n = process_url(entry, wayback, data_dir, sources_dir, policies_dir, manifest)
        print(f"[archive_policies] url={entry['url']} new_versions={n}")
        total += n
    print(f"[main] total new policy versions: {total}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
