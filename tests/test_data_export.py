"""Tests for scripts/build/data_export.py — JSON export for client JS."""
import json
from pathlib import Path
import pandas as pd
import pytest

from scripts.build.data_export import (
    emit_events_json,
    emit_triggers_json,
    emit_entities_json,
)


def _sample_actions():
    return pd.DataFrame([
        {
            "action_id": "CU-ACT-0001",
            "action_date": "2020-06-16",
            "mechanism_type": "BLACKLIST",
            "target_identifier": "0xaa05",
            "target_category": "stolen_funds",
            "trigger_id": "CU-TRG-0001",
            "status": "ACTIVE",
            "confidence": "HIGH",
            "implementation_id": "CU-IMP-0001",
            "issuer": "Circle",
            "notes_path": "notes/CU-ACT-0001.md",
        }
    ])


def _sample_impls():
    return pd.DataFrame([
        {
            "implementation_id": "CU-IMP-0001",
            "tx_hash": "0xdeadbeef",
            "chain": "ethereum",
            "block_number": 123456,
            "issuer": "Circle",
        }
    ])


def test_emit_events_json_roundtrips(tmp_path):
    out = tmp_path / "events.json"
    emit_events_json(_sample_actions(), _sample_impls(), out)
    data = json.loads(out.read_text())
    assert isinstance(data, list)
    assert len(data) == 1
    rec = data[0]
    assert rec["action_id"] == "CU-ACT-0001"
    assert rec["chain"] == "ethereum"
    assert rec["issuer"] == "Circle"


def test_emit_events_json_only_includes_export_fields(tmp_path):
    actions = _sample_actions()
    actions["secret_field"] = "not-for-export"
    out = tmp_path / "events.json"
    emit_events_json(actions, _sample_impls(), out)
    data = json.loads(out.read_text())
    assert "secret_field" not in data[0]


def test_emit_entities_json_uses_correct_field_names(tmp_path):
    """Regression: entities.json must use entity_name and entity_type (not name/type)."""
    entities = pd.DataFrame([{
        "entity_id": "CU-ENT-0001",
        "entity_name": "TestEntity",
        "entity_type": "EXCHANGE",
        "circle_relationship": "NO",
        "issuer": "Circle",
    }])
    out = tmp_path / "entities.json"
    emit_entities_json(entities, out)
    data = json.loads(out.read_text())
    assert data[0]["entity_name"] == "TestEntity"
    assert data[0]["entity_type"] == "EXCHANGE"


def test_emit_triggers_json_includes_required_fields(tmp_path):
    triggers = pd.DataFrame([{
        "trigger_id": "CU-TRG-0001",
        "trigger_date": "2020-06-16",
        "trigger_type": "OFAC_DESIGNATION",
        "description": "Test",
        "issuer": "Circle",
    }])
    out = tmp_path / "triggers.json"
    emit_triggers_json(triggers, out)
    data = json.loads(out.read_text())
    assert data[0]["trigger_id"] == "CU-TRG-0001"
    assert data[0]["description"] == "Test"
