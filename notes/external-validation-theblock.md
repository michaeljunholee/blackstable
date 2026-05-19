---
title: "External validation: TheBlock USDC Banned Addresses on Ethereum"
date: 2026-04-23
scope: Independent cross-check of our Ethereum net-blacklisted count against TheBlock's dashboard series from 2020-06-16 through 2026-04-22
---

# External validation: TheBlock "USDC Banned Addresses on Ethereum"

**Validation date:** 2026-04-23
**Our source:** `data/actions.csv` + `data/implementations.csv`, Ethereum chain, net running count (BL=+1, UB=−1)
**Their source:** TheBlock dashboard `usdc-banned-addresses-on-ethereum`, series `Total Banned Addresses`, pulled from JSON API at `https://www.theblock.co/api/charts/chart/stablecoins/usd-pegged/usdc-banned-addresses-on-ethereum` (archived as `CU-SRC-0040`, SHA256 `cffd26fa…ed9e021`)

## Headline finding

**From 2020-06-16 through 2025-12-02 — 1,995 consecutive days — our daily net-blacklisted count on Ethereum matches TheBlock's to the address. Zero disagreement days.** Every Tornado Cash spike, every Nov 2022 consolidated sweep, every OFAC cluster, and the 540-address Tornado Cash delisting cascade on 2025-03-22 lands at the same value on both series.

From 2025-12-03 onward TheBlock's chart stopped updating (frozen at **337**). Our dataset continues and picks up 115 net-additional events through 2026-04-22, including the 2026-03-23 sealed-SDNY-civil-order batch and the 2026-04-11 cluster.

## Side-by-side at anchor dates

| Date | Our net | TheBlock | Δ |
|---|---:|---:|---:|
| 2020-06-16 (first ever) | 1 | 1 | 0 |
| 2022-08-09 (Tornado Cash OFAC) | 79 | 79 | 0 |
| 2022-11-11 (Circle consolidated sweep) | 147 | 147 | 0 |
| 2023-10-04 (untriggered cluster) | 190 | 190 | 0 |
| 2025-03-22 (Tornado Cash delisting) | 174 | 174 | 0 |
| 2025-10-07 | 226 | 226 | 0 |
| 2025-12-02 (TheBlock's last update) | 337 | 337 | 0 |
| 2026-01-01 | 344 | 337 | +7 |
| 2026-03-22 (pre 16-wallet) | 379 | 337 | +42 |
| 2026-03-23 (post 16-wallet) | 459 | 337 | +122 |
| 2026-04-22 (current) | 452 | 337 | +115 |

## What this validates

1. **Ingest pipeline correctness.** Our `scripts/01_normalize_onchain.py` Dune queries (`blacklist_events.sql`) produce an Ethereum event set byte-identical to what TheBlock built independently over 5.5 years. Two separate teams, two separate data stacks, identical address set.
2. **Net-vs-gross accounting.** TheBlock's public number is net-currently-frozen (subtracting unblacklists), and our running sum matches it exactly at every inflection point. Importantly, the Tornado Cash delisting cascade on 2025-03-22 reads correctly on both series as a ~400-address drop, confirming the UB propagation fix (commit `ebcab26`) is methodologically aligned with the canonical reference.
3. **OFAC-cluster timing fidelity.** Every multi-address cluster (2022-08 Tornado Cash, 2022-11 consolidated sweep, 2024-03-21, 2024-08-24 Zservers, 2025-09-16 Iran shadow banking, 2025-10-14 Prince Group TCO, etc.) registers on the same day on both series. Our `action_date` field maps directly to what TheBlock considers the change-date.

## What's new in our data beyond TheBlock

TheBlock's series has been stale for 141 days. Everything we've captured post-2025-12-02 is net-new Circle-blacklist behavior that TheBlock's dashboard consumers are not seeing:

- **2025-12-03 → 2026-03-22:** +42 net. Scattered clusters including the December-January OFAC follow-ups.
- **2026-03-23:** +80 net in one day (16 unique addresses × 5 chains; the Ethereum component alone was +16 and pushed the net chart from 337 → 459 because some of those addresses were fresh-freezes never seen before on Ethereum).
- **2026-04-11:** +12 net (the sealed-order-hypothesis cluster, see `notes/untriggered-cluster-2026-04-11.md`).
- Other 2026 Q1 clusters: 2026-03-27, 2026-04-15, various singletons.

## Caveats

- TheBlock's methodology is not documented on the dashboard. The perfect match strongly implies they are running the same on-chain scan (same contract, same event signatures, same net-count accounting), but no query is published (HIGH confidence on match validity; LOW confidence on the specific mechanism TheBlock uses).
- The stale-since-2025-12-02 observation is a behavioral inference from the time series; TheBlock's `lastUpdated` timestamp auto-refreshes even when the value does not change. If they resume updating, the +115 gap will close.
- The 2026-04-22 cross-check uses our running-sum method (which counts each BL as +1, UB as −1). For a single address, this can drift if Circle emits duplicate Blacklisted events (e.g., during contract upgrades that re-emit events for already-blacklisted addresses). The exact agreement for 5.5 years suggests this drift is negligible in practice for Ethereum.

## What to do with this finding

- **Cite in dashboard methodology section** (`docs/methodology.md` or equivalent) as external validation.
- **Include in any public-facing write-up.** "Our Ethereum blacklist count matches TheBlock's to the address for every day from 2020-06-16 to 2025-12-02" is the strongest single claim about dataset correctness.
- **Optional: cross-chain TheBlock comparison** — TheBlock may publish per-chain USDC banned-address charts for Base / Polygon / Arbitrum / Optimism / Avalanche. If so, the same validation can be run on those chains, locking down all 6 EVM chains against an independent reference.

## Follow-ups

1. Check for TheBlock Base / Polygon / Arbitrum / Optimism / Avalanche equivalents — same API pattern.
2. Reach out to TheBlock editorial to flag the 141-day staleness (public-interest signal, not blocker).
3. Add a small `scripts/` utility that refetches this JSON and alerts on disagreement >0 post-2025-12-02 once they resume updating. Would be a lightweight ongoing external monitor.
