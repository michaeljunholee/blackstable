# Sourcing Standards

## Source tiers

Every `source_id` carries a `source_tier`:

- **`PRIMARY`** — Circle itself or US / foreign government primary documents. Examples: Circle blog posts, Circle SEC filings, Circle Terms of Service, OFAC press releases, federal court dockets, subpoenas, Congressional testimony transcripts.
- **`SECONDARY`** — Reputable news organizations and court-filed third-party documents. Examples: Reuters, Bloomberg, FT, NYT, CoinDesk, The Block, Protos, Unchained, court complaints filed by third parties.
- **`TERTIARY`** — Forensics-firm reports, industry publications, research notes, social media. Examples: Chainalysis blog posts, TRM reports, Elliptic, ZachXBT Twitter threads, Rekt News, SlowMist.

## Confidence mapping

The `confidence` field on `actions.csv` reflects evidence strength, not source tier alone. Mapping guidance:

| Evidence available | `confidence` |
|---|---|
| On-chain event recovered via Dune / Etherscan | `HIGH` |
| PRIMARY source explicitly describing the action | `HIGH` |
| ≥2 SECONDARY sources corroborating | `HIGH` or `MEDIUM` |
| 1 SECONDARY source, no corroboration | `MEDIUM` |
| TERTIARY sources only | `LOW` |
| Inferred from context, no direct statement | `LOW` |

## Archival requirement

Every `source_id` with a URL must have a local copy in `sources/` and a SHA256 hash recorded in `content_sha256`. Exception: on-chain sources (`source_type = CHAIN_DATA`) record the block number and tx hash instead.
