# Schema — Data Dictionary

Canonical enum values live in `scripts/utils/schema.py` and are enforced by `scripts/99_validate.py`. When updating this file, update `schema.py` in the same commit.

## Multi-issuer design

Every fact table carries an `issuer` column identifying which stablecoin issuer the row belongs to. Allowed values: `Circle`, `Tether`, or `Circle,Tether`.

The `Circle,Tether` form is reserved for rows that a single real-world event caused **both** issuers to act on — for example, an OFAC designation that produced both a USDC blacklist and a USDT freeze. All existing rows carry `issuer='Circle'`. Tether rows are introduced by the USDT expansion (Project A).

## Table overview

| Table | Role |
|---|---|
| `actions.csv` | Spine — one row per freeze, restrict, or non-action event |
| `triggers.csv` | External catalysts (OFAC designations, court orders, statutes) |
| `incidents.csv` | Real-world events that may precipitate requests |
| `requests.csv` | Explicit or plausible requests for Circle action (nullable `resulting_action_id` captures refusals) |
| `policies.csv` | Circle policies, versioned by effective date |
| `implementations.csv` | Mechanical execution records (on-chain tx or off-chain operational step) |
| `entities.csv` | Every relevant party, with YES/MAYBE/NO Circle relationship classification |
| `sources.csv` | Every citation, audit-trailed with SHA256 |
| `action_sources.csv` | Many-to-many join between actions and sources |

## `actions.csv` — spine

One row per discrete freeze / restrict / non-action event.

| Field | Type | Notes |
|---|---|---|
| `action_id` | string, PK | Stable ID, e.g. `CU-ACT-0001` |
| `action_date` | ISO 8601 UTC | Date of the action itself, not the date of disclosure |
| `mechanism_type` | enum | `BLACKLIST`, `UNBLACKLIST`, `PAUSE`, `UNPAUSE`, `REDEMPTION_REFUSAL`, `ACCOUNT_CLOSURE`, `JURISDICTIONAL`, `LAW_ENFORCEMENT_RESPONSE`, `NON_ACTION`, `POLICY_COMMITMENT` |
| `target_identifier` | string | Address, account ID, jurisdiction code, or counterparty name; semantics vary by `target_type`. For system-wide actions (`target_type=NA`), use the form `<chain>:<contract_address>` to uniquely identify the affected contract across chains. |
| `target_type` | enum | `ADDRESS`, `ACCOUNT`, `JURISDICTION`, `COUNTERPARTY`, `CATEGORY`, `NA` |
| `target_category` | string, nullable | Free-tag, e.g. `sanctioned_entity`, `stolen_funds`, `ransomware`, `darknet_market` |
| `target_entity_id` | FK → entities, nullable | When the target address resolves to a known entity |
| `beneficiary_entity_id` | FK → entities, nullable | Who benefits from the action (victim of a hack, sanctioning agency, etc.) |
| `status` | enum | `ACTIVE`, `REVERSED`, `UNCLEAR` |
| `reversal_action_id` | FK → actions, nullable | Later action that reversed this one, if any |
| `amount_affected_usd` | decimal, nullable | Balance at time of action, when known |
| `incident_id` | FK → incidents, nullable | Underlying real-world event |
| `request_id` | FK → requests, nullable | Request that produced this action |
| `trigger_id` | FK → triggers, nullable | Legal / regulatory trigger |
| `policy_id` | FK → policies, nullable | Circle policy in effect at action time authorizing this action |
| `implementation_id` | FK → implementations, nullable | Mechanical execution record |
| `disclosure_date` | ISO 8601, nullable | When Circle publicly disclosed the action, if at all |
| `discovery_source` | enum | `ONCHAIN_SCAN`, `COURT_RECORD`, `SEC_FILING`, `CIRCLE_DISCLOSURE`, `NEWS`, `FORENSICS_REPORT`, `OTHER` |
| `confidence` | enum | `HIGH`, `MEDIUM`, `LOW` |
| `notes_path` | string, nullable | Path to `notes/{action_id}.md` for long-form commentary |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` — see [Multi-issuer design](#multi-issuer-design) |

Null `trigger_id`, `policy_id`, or `implementation_id` values are themselves findings — they signal a policy-versus-practice gap or opaque implementation and should be coded deliberately, not treated as missing data.

## `incidents.csv`

Real-world events that may precipitate requests for Circle action.

| Field | Type | Notes |
|---|---|---|
| `incident_id` | string, PK | `CU-INC-0001` |
| `incident_date` | ISO 8601 | When the incident occurred |
| `public_disclosure_date` | ISO 8601, nullable | First public reporting |
| `incident_type` | enum | `HACK_DEFI`, `HACK_CEX`, `HACK_BRIDGE`, `PHISHING`, `RANSOMWARE`, `SANCTIONS_DESIGNATION`, `CIVIL_FORFEITURE`, `FRAUD_ENFORCEMENT`, `REGULATORY_COMPLIANCE`, `OTHER` |
| `victim_entity_id` | FK → entities, nullable | |
| `perpetrator_description` | string | Where known |
| `estimated_loss_usd` | decimal, nullable | |
| `affected_addresses` | string | Comma-separated known on-chain addresses |
| `jurisdiction` | string | Where the incident occurred legally |
| `summary` | string | One-line description |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## `requests.csv`

Explicit or plausible requests to Circle for action. Nullable `resulting_action_id` is critical: it captures refusals and delays.

| Field | Type | Notes |
|---|---|---|
| `request_id` | string, PK | `CU-REQ-0001` |
| `request_date` | ISO 8601 | When Circle received the request |
| `requester_entity_id` | FK → entities | |
| `request_channel` | enum | `COURT_ORDER`, `SUBPOENA`, `LAW_ENFORCEMENT_LETTER`, `OFAC_AUTO`, `INFORMAL_EMAIL`, `PUBLIC_APPEAL`, `SOCIAL_MEDIA`, `NONE_INFERRED`, `UNKNOWN` |
| `legal_weight` | enum | `BINDING_COURT_ORDER`, `VOLUNTARY_COMPLIANCE`, `STATUTORY_OBLIGATION`, `INFORMAL`, `NA` |
| `incident_id` | FK → incidents, nullable | |
| `resulting_action_id` | FK → actions, nullable | NULL captures refusals and unacted-upon requests |
| `public` | bool | Whether the request itself was public |

## `triggers.csv`

The external catalyst for a request or action.

| Field | Type | Notes |
|---|---|---|
| `trigger_id` | string, PK | `CU-TRG-0001` |
| `trigger_date` | ISO 8601 | |
| `trigger_type` | enum | `OFAC_DESIGNATION`, `COURT_ORDER`, `SUBPOENA`, `STATUTE`, `FOREIGN_REGULATOR`, `INTERNAL_POLICY`, `EXCHANGE_HACK_RESPONSE`, `INFORMAL_REQUEST`, `INDUSTRY_COORDINATION`, `OTHER`, `UNKNOWN` |
| `authority` | string | Issuing entity, e.g. `OFAC`, `DOJ-SDNY`, `NYDFS`, `SEC`, `CIRCLE_INTERNAL` |
| `legal_basis` | string | Citation or description, e.g. `31 CFR §501.806`, `E.O. 13694` |
| `description` | string | One-line summary |
| `primary_source_id` | FK → sources | Authoritative source document |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## `policies.csv`

Circle's stated policies, versioned by effective date.

| Field | Type | Notes |
|---|---|---|
| `policy_id` | string, PK | `CU-POL-0001` |
| `policy_name` | string | |
| `policy_type` | enum | `TERMS_OF_SERVICE`, `USER_AGREEMENT`, `COMPLIANCE_POLICY`, `TRANSPARENCY_REPORT`, `BLOG_POST`, `TESTIMONY`, `SEC_FILING`, `PRIVACY_POLICY` |
| `effective_date` | ISO 8601 | |
| `superseded_date` | ISO 8601, nullable | |
| `document_path` | string | Markdown snapshot under `policies/` |
| `source_id` | FK → sources | |
| `key_clauses` | string | Semicolon-separated references to clauses relevant to freeze / restrict authority |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## `implementations.csv`

Mechanical execution record — on-chain transaction or off-chain operational step.

| Field | Type | Notes |
|---|---|---|
| `implementation_id` | string, PK | `CU-IMP-0001` |
| `implementation_type` | enum | `ONCHAIN_TX`, `ACCOUNT_ACTION`, `OFFCHAIN_REFUSAL`, `POLICY_STATEMENT`, `NO_IMPLEMENTATION` |
| `tx_hash` | string, nullable | |
| `block_number` | int, nullable | |
| `block_timestamp` | ISO 8601, nullable | |
| `chain` | string, nullable | e.g. `ethereum`, `base`, `polygon` |
| `contract_address` | string, nullable | Which USDC implementation (v1, v2, v2.1, v2.2, proxy) |
| `method_called` | string, nullable | e.g. `blacklist(address)`, `pause()`, `destroyBlackFunds(address)` |
| `caller_address` | string, nullable | EOA or contract that invoked the method |
| `caller_role` | enum, nullable | `BLACKLISTER`, `PAUSER`, `OWNER`, `MASTER_MINTER`, `UNKNOWN` |
| `gas_used` | int, nullable | |
| `description` | string | Free text for off-chain implementations |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## `entities.csv`

Every relevant party, with a simple ordinal classification of relationship to Circle.

| Field | Type | Notes |
|---|---|---|
| `entity_id` | string, PK | `CU-ENT-0001` |
| `entity_name` | string | |
| `entity_type` | enum | `EXCHANGE`, `DEFI_PROTOCOL`, `BRIDGE`, `WALLET_PROVIDER`, `BANK`, `GOV_AGENCY`, `COURT`, `INDIVIDUAL`, `CORPORATION`, `SANCTIONED_ENTITY`, `UNKNOWN` |
| `aliases` | string | Comma-separated |
| `associated_addresses` | string | Comma-separated on-chain addresses known to belong to this entity |
| `circle_relationship` | enum | `YES` (2), `MAYBE` (1), `NO` (0) |
| `circle_relationship_rationale` | string | One to three sentences explaining the classification |
| `relationship_source_ids` | string | Comma-separated `source_id` list. Empty for `MAYBE` when no evidence in either direction. |
| `relationship_last_reviewed` | ISO 8601 | When last assessed |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

**Classification criteria (documented in `docs/relationship-criteria.md`)**:

- **`YES`** requires at least one documented source showing any of: equity tie, Centre Consortium membership, revenue-share agreement, disclosed commercial partnership (named by Circle or counterparty in SEC filings, press releases, or Circle blog), board / advisor interlock, or custodial or banking relationship named in Circle's Transparency Reports.
- **`NO`** requires affirmative evidence of absence or adversarial distance (rare).
- **`MAYBE`** is the default residual whenever we lack documented evidence in either direction. Expected to be the largest bucket.

## `sources.csv`

Every citation, audit-trailed.

| Field | Type | Notes |
|---|---|---|
| `source_id` | string, PK | `CU-SRC-0001` |
| `source_tier` | enum | `PRIMARY` (Circle / government), `SECONDARY` (reputable news, court filings), `TERTIARY` (forensics firms, Twitter, blog posts) |
| `source_type` | enum | `GOV_FILING`, `COURT_DOCKET`, `CIRCLE_BLOG`, `CIRCLE_LEGAL_DOC`, `SEC_FILING`, `NEWS_ARTICLE`, `RESEARCH_REPORT`, `FORUM_POST`, `SOCIAL_MEDIA`, `CHAIN_DATA`, `FOIA_RESPONSE` |
| `title` | string | |
| `publisher` | string | |
| `author` | string, nullable | |
| `publication_date` | ISO 8601, nullable | |
| `url` | string | Original URL |
| `archived_url` | string, nullable | archive.org or archive.today snapshot |
| `local_path` | string, nullable | Path to stored copy in `sources/` |
| `content_sha256` | string, nullable | Hash of stored copy — tamper evidence |
| `accessed_date` | ISO 8601 | |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## `action_sources.csv`

Many-to-many join: actions often have multiple corroborating citations.

| Field | Type |
|---|---|
| `action_id` | FK → actions |
| `source_id` | FK → sources |
| `relation` | enum: `EVIDENCE_OF_ACTION`, `EVIDENCE_OF_TRIGGER`, `EVIDENCE_OF_IMPL`, `EVIDENCE_OF_IMPACT`, `CONTEXT` |
| `issuer` | enum | `Circle`, `Tether`, or `Circle,Tether` |

## Derived analytical fields

Computed in notebooks (not stored in CSV), via joins:

- `latency_incident_to_action = action_date − incidents.incident_date`
- `latency_request_to_action = action_date − requests.request_date`
- `latency_disclosure_to_action = action_date − incidents.public_disclosure_date`

## Principles encoded in the schema

- Every action can be joined to the three analytical axes — policy, trigger, implementation. Missing joins are data, not gaps.
- Confidence and sourcing are first-class fields at both the action level (`confidence`) and the source level (`source_tier`).
- Reversibility is modeled explicitly; `UNBLACKLIST` events are themselves observations.
- On-chain and off-chain actions share the same spine, distinguished by `implementation_type`.
- Non-actions and policy commitments are first-class action rows — they reveal the boundaries of Circle's discretion.
