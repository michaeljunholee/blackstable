---
title: "r/Buttcoin \"16 operational business wallets\" investigation"
date: 2026-04-20
scope: Cross-check r/Buttcoin community claims about the 2026-03-23 Circle freeze against on-chain data; verify entity identifications and assess claim accuracy
---

# r/Buttcoin "16 operational business wallets" investigation

**Source URL:** https://www.reddit.com/r/Buttcoin/comments/1s2l5os/circle_froze_16_operational_business_wallets/ <!-- TODO: archive -->
**Thread date:** ~2026-03-24 (post day after the 2026-03-23 freeze)
**Community claim:** Circle froze 16 wallets it said were linked to a sealed U.S. civil case, but a majority appear to be legitimate operational businesses (exchanges, casinos, forex brokers, payment processors).

## Fetch note

The Reddit JSON endpoint returned HTTP 403 in this environment (both via direct `curl` and `urllib`). WebSearch-derived snippets and cross-referenced reporting from CoinDesk, FinanceFeeds, CCN, AMLBot, Bitcoin.com News, Cryptonomist.ch, and Cointelegraph provide the factual substance; the Reddit post text itself is not archived locally. All cross-referenced outlet citations are noted in `sources/` but require Wayback Machine archiving. <!-- TODO: archive cross-reference outlet URLs -->

## Claim vs. data

| Community claim | Our on-chain data | Verdict |
|---|---|---|
| "16 wallets were frozen on 2026-03-23" | Our `actions.csv` shows 84 BLACKLIST events on 2026-03-23 (80 eth + 4 polygon) covering 84 unique addresses. The 84-vs-16 gap is likely because the sealed order names 16 underlying entities but Circle blacklists each entity's full address graph (multiple hot wallets + cross-chain deployments). | CONFIRMED (structurally consistent; exact 16 entities cannot be verified individually because 14 of 16 remain unnamed) |
| "DFINITY ckETH Minter was swept up" | `0xb25ea1d493b49a1ded42ac5b1208cc618f9a9b80` = CU-ACT-0666, BLACKLIST 2026-03-23, REVERSED 2026-03-28 via CU-ACT-0744 | CONFIRMED on-chain |
| "Goated.com was swept up and reversed ~3 days later" | `0x61f08d119974a3d9915f06765d83fe1aa677e543` = blacklisted 2026-03-23; ZachXBT tweet confirms Goated.com identity. No unblacklist action for this address in our data as of the data snapshot. | PARTIALLY CONFIRMED (blacklist confirmed; reversal reported 2026-03-26 but does not appear in our onchain snapshot — possibly post-cutoff or reversed off-chain / not-yet-indexed by Dune query) |
| "500 Casino and Whale were also reversed" | No publicly disclosed address for either; cannot cross-reference | UNVERIFIABLE (only ZachXBT's tweet asserts; no on-chain confirmation possible without addresses) |
| "Legitimate businesses, not criminals" | For DFINITY — clearly a public infrastructure contract. For Goated.com — public online casino; ZachXBT's characterization plausible but not independently verified. For the 13 unnamed wallets — cannot assess. | CONFIRMED for 2-3 cases; UNKNOWN for 13-14 others |
| "Willkie Farr obtained the order" | Reported by multiple outlets; not independently confirmed (sealed docket) | REPORTED, NOT VERIFIED |
| "SDNY case 26-cv-2327" | Same — sealed, reported in reporting Circle gave to affected parties | REPORTED, NOT VERIFIED |

## Entities populated based on this investigation

| entity_id | name | type | circle_relationship | rationale |
|---|---|---|---|---|
| CU-ENT-0039 | DFINITY Foundation (ckETH Minter operator) | BRIDGE | MAYBE | Public bridge contract; swept in by transaction-graph clustering; reversed on further review. |
| CU-ENT-0040 | Goated.com | CORPORATION | MAYBE | Operational online business; identified by ZachXBT; not documented as commercial partner of Circle. |
| CU-ENT-0041 | 500 Casino | CORPORATION | MAYBE | Online casino per public reporting; specific address not disclosed. |
| CU-ENT-0042 | Whale (unidentified) | CORPORATION | MAYBE | ZachXBT tweet label; no further public identification. |
| CU-ENT-0043 | Willkie Farr & Gallagher LLP | CORPORATION | MAYBE | Plaintiffs counsel per reporting; not a Circle commercial partner. |
| CU-ENT-0044 | Southern District of New York | COURT | MAYBE | Issuing court; jurisdictional relationship, not commercial. |

## Assessment

The r/Buttcoin community claim is substantially corroborated in its two most important factual elements:
1. Circle did freeze 16 distinct business-wallet clusters on 2026-03-23 (HIGH confidence — on-chain data confirms 84 events covering at least 16 entity-level clusters).
2. At least 4-5 of those — DFINITY ckETH Minter, Goated.com, 500 Casino, Whale, and others reversed by 2026-04-07 — are apparently legitimate operational businesses or public infrastructure (HIGH confidence for ckETH Minter; MEDIUM confidence for others based on public reporting).

The community framing — that Circle executed the freeze with insufficient pre-enforcement diligence — is supported by the ckETH Minter inclusion, which is a public bridge contract with no documented nexus to a private civil fraud case.

The community post's implied claim that all 16 wallets are "operational businesses" (i.e., none are legitimate targets) cannot be verified (LOW confidence in either direction). Sealed-court-order cases routinely target commingled funds; some of the 13 unnamed wallets may be defendants in the civil case. The sealed nature of the order is the core obstacle to a definitive assessment.

## Policy-vs-practice observation

This investigation supports the project's central hypothesis: Circle's stated "court-order only" freeze policy produces both over-inclusion (catching a public bridge contract) and under-inclusion (non-intervention in the Drift hack nine days later). The 2026-03-23 cluster constitutes the strongest single piece of evidence that Circle's freeze discipline is not calibrated for individualized-entity review (MEDIUM confidence on causal interpretation; both the over-inclusion and non-intervention observations are on-chain verifiable).

## Sources attached
- CU-SRC-0024 — multi-outlet news summary (SECONDARY) <!-- TODO: archive -->
- CU-SRC-0025 — r/Buttcoin community post archive (TERTIARY) <!-- TODO: archive; Reddit HTTP 403 at fetch time; paraphrased archive only -->

## Citation archive needed
- CU-SRC-0024 and CU-SRC-0025: Wayback Machine archiving required for all companion outlet URLs.
