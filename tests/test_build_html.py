"""Smoke tests for scripts/03_build_html.py — the build orchestrator."""
import importlib.util
import json
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "03_build_html.py"


def _run_build(out_dir: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["python", str(SCRIPT), "--output-dir", str(out_dir)],
        capture_output=True,
        text=True,
        cwd=REPO,
    )


def test_build_runs_without_error(tmp_path):
    out = tmp_path / "dashboard"
    result = _run_build(out)
    assert result.returncode == 0, f"Build failed:\nstdout: {result.stdout}\nstderr: {result.stderr}"


def test_build_produces_index_html(tmp_path):
    out = tmp_path / "dashboard"
    _run_build(out)
    assert (out / "index.html").exists(), "index.html not produced"


def test_build_produces_data_json(tmp_path):
    out = tmp_path / "dashboard"
    _run_build(out)
    events_json = out / "data" / "events.json"
    assert events_json.exists()
    data = json.loads(events_json.read_text())
    assert isinstance(data, list)
    assert len(data) > 100


def test_build_filters_to_circle_only(tmp_path):
    out = tmp_path / "dashboard"
    _run_build(out)
    events = json.loads((out / "data" / "events.json").read_text())
    issuers = {e.get("issuer") for e in events}
    assert issuers == {"Circle"}, f"events.json contains non-Circle issuers: {issuers}"


def test_build_renders_all_expected_pages(tmp_path):
    out = tmp_path / "dashboard"
    _run_build(out)
    expected = [
        "index.html",
        "timeline.html",
        "explore.html",
        "clusters.html",
        "entities.html",
        "triggers.html",
        "sources.html",
        "notes.html",
        "methodology.html",
    ]
    for name in expected:
        assert (out / name).exists(), f"missing page: {name}"


def test_entities_json_includes_name_and_type(tmp_path):
    """Regression test for entities.json schema — must include entity_name and entity_type."""
    out = tmp_path / "dashboard"
    _run_build(out)
    entities = json.loads((out / "data" / "entities.json").read_text())
    if entities:
        sample = entities[0]
        assert "entity_name" in sample, f"entity_name missing from entities.json: {list(sample.keys())}"
        assert "entity_type" in sample, f"entity_type missing from entities.json: {list(sample.keys())}"


def _load_build_module():
    """Load scripts/03_build_html.py as a module via spec_from_file_location.

    importlib.import_module('scripts.03_build_html') fails because the leading
    digit makes it an invalid Python identifier.
    """
    spec = importlib.util.spec_from_file_location("build_html", REPO / "scripts" / "03_build_html.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_multi_issuer_row_included_for_either_issuer_filter(tmp_path):
    """A row with issuer='Circle,Tether' must match both --issuers Circle and --issuers Tether."""
    work = tmp_path / "data"
    work.mkdir()
    for f in (REPO / "data").glob("*.csv"):
        shutil.copy(f, work / f.name)

    # Append a Circle,Tether trigger row
    triggers = pd.read_csv(work / "triggers.csv")
    new_row = triggers.iloc[0].copy()
    new_row["trigger_id"] = "CU-TRG-TEST"
    new_row["issuer"] = "Circle,Tether"
    triggers = pd.concat([triggers, new_row.to_frame().T], ignore_index=True)
    triggers.to_csv(work / "triggers.csv", index=False)

    build_mod = _load_build_module()
    original_data_dir = build_mod.DATA_DIR
    try:
        build_mod.DATA_DIR = work
        circle_data = build_mod.load_data(["Circle"])
        assert any(circle_data["triggers"]["trigger_id"] == "CU-TRG-TEST"), \
            "Circle,Tether trigger not included when filtering by Circle"
        tether_data = build_mod.load_data(["Tether"])
        assert any(tether_data["triggers"]["trigger_id"] == "CU-TRG-TEST"), \
            "Circle,Tether trigger not included when filtering by Tether"
    finally:
        build_mod.DATA_DIR = original_data_dir
