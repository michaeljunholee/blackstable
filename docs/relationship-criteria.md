# Entity → Circle Relationship Classification

Every `entities.csv` row carries `circle_relationship ∈ {YES, MAYBE, NO}`. This file defines when each applies.

## `YES` (value 2)

Requires at least one documented source showing any of the following ties:

1. **Equity investment.** Circle holds or held equity in the entity, or the entity holds or held equity in Circle. Source: SEC filings (S-1, 10-K, 10-Q), Crunchbase + confirming press release, Circle press release naming the investment.
2. **Centre Consortium founding / membership.** The entity was a Centre Consortium member (2018-09 through 2023-08). Source: Circle or Coinbase announcements, Centre Consortium archived site.
3. **Revenue-share agreement.** The entity has a disclosed revenue-share arrangement with Circle on USDC reserves. Source: SEC filings (notably Coinbase's quarterly disclosures), Circle disclosures.
4. **Board / advisor interlock.** A director or named advisor of Circle sits on the entity's board or vice-versa. Source: proxy statements, SEC filings.
5. **Banking counterparty named in Transparency Reports.** Circle's published Transparency Reports (monthly attestations) name the entity as a banking or custodial counterparty.
6. **Disclosed commercial partnership.** Circle press release, official blog post, or the entity's SEC filing names a formal commercial partnership (distribution, custody, integration).

All `YES` classifications require at least one `source_id` in `relationship_source_ids`.

## `NO` (value 0)

Requires affirmative evidence of absence or adversarial distance. Examples:

- Entity is on a sanctions list Circle has formally complied with (the entity is a freeze target, not a counterparty).
- Circle has publicly severed ties with the entity (documented in Circle press release or news coverage of a breakup).
- Entity is in active litigation against Circle.

`NO` is rare. Requires at least one `source_id`.

## `MAYBE` (value 1)

Default residual. Used whenever we lack documented evidence in either direction. Empty `relationship_source_ids` is permitted.

Expected to be the largest bucket. Examples that default to `MAYBE` absent documented evidence: Binance, Bybit, OKX, most DeFi protocols, most individual addresses.

## Robustness

Phase 3 analyses re-run under two alternative codings:
- **Conservative:** treat `MAYBE` as `NO`.
- **Liberal:** treat `MAYBE` as `YES`.

Conclusions that hold under both are reported as robust.
