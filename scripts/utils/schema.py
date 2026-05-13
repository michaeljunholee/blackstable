"""Canonical enum values and table headers.

Authoritative source for `docs/schema.md`. If you change this, update the
Markdown in the same commit.
"""

ISSUERS = ("Circle", "Tether")

# A row's `issuer` field stores either a single issuer name or a comma-joined
# pair ('Circle,Tether') indicating the row applies to both. This shared form
# is reserved for triggers/entities/sources/incidents that one real-world event
# (e.g., an OFAC designation) caused both issuers to act on.
ISSUER_VALUES = (*ISSUERS, "Circle,Tether")

MECHANISM_TYPES = (
    "BLACKLIST", "UNBLACKLIST", "PAUSE", "UNPAUSE",
    "REDEMPTION_REFUSAL", "ACCOUNT_CLOSURE",
    "JURISDICTIONAL", "LAW_ENFORCEMENT_RESPONSE",
    "NON_ACTION", "POLICY_COMMITMENT",
)

TARGET_TYPES = ("ADDRESS", "ACCOUNT", "JURISDICTION", "COUNTERPARTY", "CATEGORY", "NA")

STATUS = ("ACTIVE", "REVERSED", "UNCLEAR")

DISCOVERY_SOURCE = (
    "ONCHAIN_SCAN", "COURT_RECORD", "SEC_FILING",
    "CIRCLE_DISCLOSURE", "NEWS", "FORENSICS_REPORT", "OTHER",
)

CONFIDENCE = ("HIGH", "MEDIUM", "LOW")

TRIGGER_TYPES = (
    "OFAC_DESIGNATION", "COURT_ORDER", "SUBPOENA", "STATUTE",
    "FOREIGN_REGULATOR", "INTERNAL_POLICY", "EXCHANGE_HACK_RESPONSE",
    "INFORMAL_REQUEST", "INDUSTRY_COORDINATION", "OTHER", "UNKNOWN",
)

INCIDENT_TYPES = (
    "HACK_DEFI", "HACK_CEX", "HACK_BRIDGE", "PHISHING", "RANSOMWARE",
    "SANCTIONS_DESIGNATION", "CIVIL_FORFEITURE", "FRAUD_ENFORCEMENT",
    "REGULATORY_COMPLIANCE", "OTHER",
)

REQUEST_CHANNEL = (
    "COURT_ORDER", "SUBPOENA", "LAW_ENFORCEMENT_LETTER",
    "OFAC_AUTO", "INFORMAL_EMAIL", "PUBLIC_APPEAL",
    "SOCIAL_MEDIA", "NONE_INFERRED", "UNKNOWN",
)

LEGAL_WEIGHT = (
    "BINDING_COURT_ORDER", "VOLUNTARY_COMPLIANCE",
    "STATUTORY_OBLIGATION", "INFORMAL", "NA",
)

POLICY_TYPES = (
    "TERMS_OF_SERVICE", "USER_AGREEMENT", "COMPLIANCE_POLICY",
    "TRANSPARENCY_REPORT", "BLOG_POST", "TESTIMONY",
    "SEC_FILING", "PRIVACY_POLICY",
)

IMPLEMENTATION_TYPES = (
    "ONCHAIN_TX", "ACCOUNT_ACTION", "OFFCHAIN_REFUSAL",
    "POLICY_STATEMENT", "NO_IMPLEMENTATION",
)

CALLER_ROLE = ("BLACKLISTER", "PAUSER", "OWNER", "MASTER_MINTER", "UNKNOWN")

ENTITY_TYPES = (
    "EXCHANGE", "DEFI_PROTOCOL", "BRIDGE", "WALLET_PROVIDER", "BANK",
    "GOV_AGENCY", "COURT", "INDIVIDUAL", "CORPORATION",
    "SANCTIONED_ENTITY", "UNKNOWN",
)

CIRCLE_RELATIONSHIP = ("YES", "MAYBE", "NO")

SOURCE_TIER = ("PRIMARY", "SECONDARY", "TERTIARY")

SOURCE_TYPE = (
    "GOV_FILING", "COURT_DOCKET", "CIRCLE_BLOG", "CIRCLE_LEGAL_DOC",
    "SEC_FILING", "NEWS_ARTICLE", "RESEARCH_REPORT", "FORUM_POST",
    "SOCIAL_MEDIA", "CHAIN_DATA", "FOIA_RESPONSE",
)

ACTION_SOURCE_RELATION = (
    "EVIDENCE_OF_ACTION", "EVIDENCE_OF_TRIGGER",
    "EVIDENCE_OF_IMPL", "EVIDENCE_OF_IMPACT", "CONTEXT",
)

# Canonical table headers for seed CSVs and validation.
TABLE_HEADERS = {
    "actions": [
        "action_id", "action_date", "mechanism_type", "target_identifier",
        "target_type", "target_category", "target_entity_id", "beneficiary_entity_id",
        "status", "reversal_action_id", "amount_affected_usd", "incident_id",
        "request_id", "trigger_id", "policy_id", "implementation_id",
        "disclosure_date", "discovery_source", "confidence", "notes_path",
        "issuer",
    ],
    "triggers": [
        "trigger_id", "trigger_date", "trigger_type", "authority",
        "legal_basis", "description", "primary_source_id",
        "issuer",
    ],
    "incidents": [
        "incident_id", "incident_date", "public_disclosure_date", "incident_type",
        "victim_entity_id", "perpetrator_description", "estimated_loss_usd",
        "affected_addresses", "jurisdiction", "summary",
        "issuer",
    ],
    "requests": [
        "request_id", "request_date", "requester_entity_id", "request_channel",
        "legal_weight", "incident_id", "resulting_action_id", "public",
    ],
    "policies": [
        "policy_id", "policy_name", "policy_type", "effective_date",
        "superseded_date", "document_path", "source_id", "key_clauses",
        "issuer",
    ],
    "implementations": [
        "implementation_id", "implementation_type", "tx_hash", "block_number",
        "block_timestamp", "chain", "contract_address", "method_called",
        "caller_address", "caller_role", "gas_used", "description",
        "issuer",
    ],
    "entities": [
        "entity_id", "entity_name", "entity_type", "aliases",
        "associated_addresses", "circle_relationship", "circle_relationship_rationale",
        "relationship_source_ids", "relationship_last_reviewed",
        "issuer",
    ],
    "sources": [
        "source_id", "source_tier", "source_type", "title", "publisher",
        "author", "publication_date", "url", "archived_url",
        "local_path", "content_sha256", "accessed_date",
        "issuer",
    ],
    "action_sources": ["action_id", "source_id", "relation", "issuer"],
}

# Primary key per table, for FK validation.
PRIMARY_KEYS = {
    "actions": "action_id",
    "triggers": "trigger_id",
    "incidents": "incident_id",
    "requests": "request_id",
    "policies": "policy_id",
    "implementations": "implementation_id",
    "entities": "entity_id",
    "sources": "source_id",
}

# Foreign key wiring: (source_table, source_column) -> (target_table, target_column)
FOREIGN_KEYS = [
    ("actions", "target_entity_id", "entities", "entity_id"),
    ("actions", "beneficiary_entity_id", "entities", "entity_id"),
    ("actions", "reversal_action_id", "actions", "action_id"),
    ("actions", "incident_id", "incidents", "incident_id"),
    ("actions", "request_id", "requests", "request_id"),
    ("actions", "trigger_id", "triggers", "trigger_id"),
    ("actions", "policy_id", "policies", "policy_id"),
    ("actions", "implementation_id", "implementations", "implementation_id"),
    ("triggers", "primary_source_id", "sources", "source_id"),
    ("incidents", "victim_entity_id", "entities", "entity_id"),
    ("requests", "requester_entity_id", "entities", "entity_id"),
    ("requests", "incident_id", "incidents", "incident_id"),
    ("requests", "resulting_action_id", "actions", "action_id"),
    ("policies", "source_id", "sources", "source_id"),
    ("action_sources", "action_id", "actions", "action_id"),
    ("action_sources", "source_id", "sources", "source_id"),
]
