from scripts.utils import schema


def test_mechanism_type_enum_contains_canonical_values():
    expected = {
        "BLACKLIST", "UNBLACKLIST", "PAUSE", "UNPAUSE",
        "REDEMPTION_REFUSAL", "ACCOUNT_CLOSURE",
        "JURISDICTIONAL", "LAW_ENFORCEMENT_RESPONSE",
        "NON_ACTION", "POLICY_COMMITMENT",
    }
    assert set(schema.MECHANISM_TYPES) == expected


def test_confidence_enum_is_ordered():
    assert schema.CONFIDENCE == ("HIGH", "MEDIUM", "LOW")


def test_circle_relationship_enum_has_three_values():
    assert set(schema.CIRCLE_RELATIONSHIP) == {"YES", "MAYBE", "NO"}


def test_table_headers_match_expected_field_count():
    assert len(schema.TABLE_HEADERS["actions"]) == 21
    assert len(schema.TABLE_HEADERS["triggers"]) == 8
    assert len(schema.TABLE_HEADERS["entities"]) == 10
