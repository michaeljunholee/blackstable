# Completeness Map

For every cell below, one of: `EXHAUSTIVE` (provably complete), `BEST_EFFORT` (good-faith search, gaps possible), `OUT_OF_SCOPE` (Phase 1 exclusion).

Updated at the end of each Pass and each on-chain refresh (last: 2026-09-14).

## Summary

- Total on-chain events (Circle USDC): 4493 (3796 BLACKLIST + 697 UNBLACKLIST) — as of the 2026-09-14 re-scan
- Chains covered: 6 EVM (Ethereum, Base, Polygon, Avalanche, Arbitrum, Optimism)
- Date range: 2020-06-16 to 2026-09-10
- Pause/Unpause events observed: 0 across all chains
- Policy documents captured: 20 versions of Circle Privacy Policy (2024-11-03 to 2026-02-17)
- Policy URLs not yet captured: Terms of Service, User Agreement, Transparency Reports landing, Blog index — retry pending (see known-gaps.md)

## By mechanism × era

| Mechanism | 2018-09 to 2022-07 | 2022-08 to present |
|---|---|---|
| `BLACKLIST` (on-chain) | EXHAUSTIVE (2020-06+ Ethereum, 2022-03+ Avalanche); OUT_OF_SCOPE 2018-09 to 2020-06 (pre-USDC-blacklist-activity) | EXHAUSTIVE (all 6 EVM chains) |
| `UNBLACKLIST` (on-chain) | EXHAUSTIVE (2020-06+ Ethereum, 2022-03+ Avalanche); OUT_OF_SCOPE 2018-09 to 2020-06 | EXHAUSTIVE (all 6 EVM chains) |
| `PAUSE` / `UNPAUSE` | EXHAUSTIVE (zero events observed on any chain) | EXHAUSTIVE (zero events observed on any chain) |
| `REDEMPTION_REFUSAL` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |
| `ACCOUNT_CLOSURE` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |
| `JURISDICTIONAL` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |
| `LAW_ENFORCEMENT_RESPONSE` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |
| `NON_ACTION` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |
| `POLICY_COMMITMENT` | BEST_EFFORT (Pass B) | BEST_EFFORT (Pass B) |

## By chain

| Chain | Coverage | Notes |
|---|---|---|
| Ethereum mainnet | EXHAUSTIVE (2020-06-16 to present) | Primary EVM target; 1110 events |
| Base | EXHAUSTIVE (2023-08-18 to present) | 682 events |
| Polygon | EXHAUSTIVE (2023-07-21 to present) | 707 events |
| Avalanche | EXHAUSTIVE (2022-03-30 to present) | 667 events |
| Arbitrum | EXHAUSTIVE (2023-06-08 to present) | 669 events; per-chain query (see decisions.md D-003) |
| Optimism | EXHAUSTIVE (2023-07-28 to present) | 658 events; per-chain query (see decisions.md D-003) |
| Solana | OUT_OF_SCOPE (Pass A) | Different `FreezeAuthority` mechanism; Pass C may promote |
| NEAR | OUT_OF_SCOPE (Pass A) | |
| Stellar | OUT_OF_SCOPE (Pass A) | |
| Algorand | OUT_OF_SCOPE (Pass A) | |
| Hedera | OUT_OF_SCOPE (Pass A) | |
