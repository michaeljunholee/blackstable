# Known Gaps

Documented unknowns and their causes. New gaps discovered during Pass B / Pass C are added here.

## Counterfactual observability

Requests Circle received but did not disclose, which produced no action, are partially unobservable. Only these subsets are visible:

- Compulsory requests surfaced in court dockets (CourtListener, PACER).
- Public appeals (victim Twitter threads, published counsel statements).
- Aggregate counts from Circle's Transparency Reports, when published.

The `requests.csv` table with nullable `resulting_action_id` captures what is observable. Missing from this table is any non-public informal request.

## Attribution decay

Older blacklist events (2018–2021) are less likely to carry public attribution. Pass B will record an attribution-rate statistic per era.

## Non-EVM chains

USDC circulating on Solana, NEAR, Stellar, Algorand, and Hedera uses different freeze mechanisms. Pass A does not cover these. Estimated share of outstanding USDC affected: 20–30% (will be quantified during Pass A).

## Policy-archaeology gaps

archive.org captures Circle's published documents but misses:
- Internal Circle policies that were never published.
- Policies published only in PDFs that archive.org did not crawl.
- Documents behind authentication (e.g., institutional-customer agreements).

**Pass A status (2026-04-17):** First crawl captured 20 Privacy Policy versions
(2024-11 through 2026-02). Other URLs (Terms of Service, User Agreement,
Transparency Reports landing page, Blog index) returned no captures during
the initial run due to archive.org rate-limiting and intermittent CDX API
failures. The script (`scripts/02_archive_policies.py`) is idempotent — rerunning
after a cool-off period should pick up the missing URLs and earlier Privacy
Policy history (archive.org has snapshots back to ~2018 that the first crawl
did not reach before being rate-limited).
