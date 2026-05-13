---
title: "2026-04-11 cluster — 12 Ethereum-only addresses, untriggered"
date: 2026-04-21
scope: Attribution attempt for 12 BLACKLIST events on 2026-04-11, Ethereum only; working hypothesis of sealed civil court order; no public attribution found
---

# 2026-04-11 cluster (12 Ethereum-only addresses) — research note

**Status:** Untriggered. No public attribution found after targeted web search.
**Research date:** 2026-04-21
**Actions:** `CU-ACT-0764` through `CU-ACT-0775` (12 BLACKLIST events, Ethereum only)
**Blocks:** 24857573 → 24857593 (sequential, ~4 minutes)
**Timestamps:** 2026-04-11 16:04:11 UTC → 16:08:11 UTC
**Caller:** `0x0A06BE16275B95a7d2567fBdAE118b36C7DA78F9` (pulled from Etherscan tx `0x5814c2…`; not recorded in `implementations.csv` — `caller_address` is NaN in our ingest)

## The 12 blacklisted addresses

| action_id | address | Etherscan notes |
|---|---|---|
| CU-ACT-0764 | `0xe38c9bfc757d6c1607126a63e7e98a21032c47a6` | 3y9d old; last active 2025-10-28; dust balance; small USDC outflows |
| CU-ACT-0765 | `0x0a232683648f83e48af7c5b91ca6c580cd060c79` | — |
| CU-ACT-0766 | `0x10e9f6063cecd1d1d475e943e1952abedd58f275` | Holds ~1.59M USDC; **received transfers tagged `Fake_Phishing1740987`**; Kraken-funded |
| CU-ACT-0767 | `0x2ec48bde7ab622863824b1408d6bb68e188f9db2` | Holds ~1.24M USDC; Kraken-funded |
| CU-ACT-0768 | `0x073fb97a1b7da715a5ccd00a257c7e1cbae6e309` | Inactive 258d; $172 portfolio |
| CU-ACT-0769 | `0x1f954c350eed5c27569cde6dee83aebb007b346e` | — |
| CU-ACT-0770 | `0xc8bdd5c269e8c105ad29d78894875068c60269f6` | — |
| CU-ACT-0771 | `0xeecfb175eec3172aad557332aaaa3fb9b06da48f` | — |
| CU-ACT-0772 | `0x0b844cb8f826a9fb44918be44b1abe01c3ddc16b` | — |
| CU-ACT-0773 | `0x618ddf95d334685aea70608fa0888b0bc2d3809f` | Revolut-funded; 6 tx total; inactive since 2025-07 |
| CU-ACT-0774 | `0xcc9468dc0070ada8e12feeffaf2a1edab5aff12c` | — |
| CU-ACT-0775 | `0xf76788730307c465012bda3fa2280dde823054b4` | — |

## What the cluster looks like

- **Ethereum-only**, no cross-chain propagation. This rules out the canonical OFAC cross-chain sweep signature (which the dataset shows as 4–8 addresses × 6 chains).
- **Tight batch**: 12 successive `blacklist(address)` calls within 20 blocks (~4 minutes) from a single caller. Consistent with one legal request processed in one compliance session.
- **Heterogeneous wallet profiles**: mix of large ($1M+) USDC holders and dormant / dust wallets; funding sources include Kraken and Revolut (retail on-ramps). No single hack-source pattern is apparent.
- **No common on-chain ancestor** identified from spot checks. No obvious bridge, mixer, or hack-drain pattern.

## Attribution attempts — all negative

1. **OFAC designation on or near 2026-04-11** — none matching. No Treasury press release names these addresses.
2. **Drift Protocol hack (2026-04-01)** — wrong chain + wrong pattern. Drift attacker moved funds Solana → Ethereum via CCTP and is called out by ZachXBT as *not* blacklisted.
3. **Multichain extension order** — April 2026 NY court ruling covers 3 pre-existing Multichain hack addresses (freeze extension, not new blacklist). Prefixes don't match.
4. **Direct address search** — `WebSearch` for specific addresses returned no public attribution (no sanctions lists, no hack databases, no thread mentions).
5. **Phishing hypothesis** — one address carries Etherscan's `Fake_Phishing1740987` tag, but the other 11 have no phishing tags and have profiles inconsistent with a single phishing operator. The phishing tag is more likely an artifact of one victim-interaction than a cluster-wide attribution.

## Working hypothesis (LOW confidence)

A private U.S. civil court order, analogous to the 2026-03-23 sealed SDNY case 26-cv-2327 (documented in `notes/reddit-buttcoin-16-wallets.md`), is assessed as the most plausible explanation. Supporting signals:
- Same operational pattern: heterogeneous wallets, no public justification, single-chain batch, executed by Circle without public comment.
- The ~3-week interval (March 23 → April 11) is consistent with a second batch from the same case or a separate sealed order (LOW confidence on which).
- Neither OFAC publication timelines nor incident-response patterns explain the cluster.

This hypothesis cannot be confirmed without: docket access (PACER) for SDNY sealed cases filed March–April 2026, direct Circle transparency disclosure, or public disclosure from an affected wallet operator.

## Why attribution is not assigned

Per project operating rule: "Never fabricate attributions. If a blacklist address is not publicly attributed by Chainalysis / TRM / Elliptic / government, leave it as UNKNOWN." The sealed-civil-order hypothesis is plausible but not publicly documented. Assigning a trigger without a citable source would violate the conservative-defaults rule.

## Follow-up options

1. **Monitor forward**: If a wallet operator publicly complains about being frozen on 2026-04-11 (the Goated.com pattern from the March 23 case), that disclosure would attribute the cluster.
2. **Check Circle's transparency reports** when Q2 2026 data lands — Circle publishes periodic aggregates that may disclose batched civil-order freezes without naming cases.
3. **Watch for unfreeze activity**: if any of these 12 addresses is unfrozen within weeks (like Goated.com was), that strengthens the "bad civil order → reversal" hypothesis and links the clusters.
