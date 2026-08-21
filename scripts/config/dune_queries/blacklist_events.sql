-- CircleUSDC blacklist/unblacklist/pause/unpause event scan.
-- Parameters (set in Dune UI): contract_address (text)
--
-- Dune SQL parameter substitution only works for values, not identifiers
-- (table names), so the chain table is hardcoded. A single saved query is
-- shared across chains: before each per-chain execution,
-- `scripts/01_normalize_onchain.py` rewrites the active `FROM <chain>.logs`
-- clause via the Dune API (PATCH /query/{id}) to `ethereum`, `base`,
-- `polygon`, `avalanche_c`, `arbitrum` or `optimism`, then executes it.
-- (Free-tier accounts cap private saved queries, so one-query-per-chain is
-- not an option there.)
--
-- Low-volume chains (ethereum, base, polygon, avalanche_c) also work against
-- the cross-chain `evms.logs` view; high-volume chains (arbitrum, optimism)
-- require the per-chain `<chain>.logs` table to finish inside Dune's
-- free-tier 2-minute execution budget.
--
-- Parameter notes:
--   - `contract_address` is varbinary → SQL leaves {{contract_address}}
--     unquoted so it substitutes as a hex literal. Set the parameter value
--     WITH the `0x` prefix, e.g. `0xa0b86991c6218b36c1d19d4a2e9eb0ce3606eb48`.
--
-- Saved as a Dune query; invoked by `scripts/01_normalize_onchain.py` via
-- its query_id. Author: create this query in Dune, note the ID, set
-- DUNE_QUERY_BLACKLIST_EVENTS=<id> in .env.

SELECT
    tx_hash,
    block_number,
    block_time AS block_timestamp,
    contract_address,
    topic0,
    topic1,
    topic2,
    data
FROM <chain>.logs   -- REPLACE <chain> with ethereum | base | polygon | avalanche_c | arbitrum | optimism
WHERE contract_address = {{contract_address}}
  AND topic0 IN (
    0xffa4e6181777692565cf28528fc88fd1516ea86b56da075235fa575af6a4b855,  -- Blacklisted
    0x117e3210bb9aa7d9baff172026820255c6f6c30ba8999d1c2fd88e2848137c4e,  -- UnBlacklisted
    0x62e78cea01bee320cd4e420270b5ea74000d11b0c9f74754ebdbfc544b05a258,  -- Paused
    0x5db9ee0a495bf2e6ff9c91a7834c1ba4fdd244a5e8aa4e537bd38aeae4b073aa   -- Unpaused
  )
ORDER BY block_number ASC, tx_hash ASC;
