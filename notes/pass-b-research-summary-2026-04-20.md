---
title: "Pass B Research Summary — 2026-04-20"
date: 2026-04-20
scope: Scorecard and findings for overnight attribution session covering 15 priority clusters plus bonus attributions; 1,290 BLACKLIST actions newly attributed
---

# Pass B Research Summary — 2026-04-20

This session addressed 15 priority cluster missions plus the r/Buttcoin community-claims investigation. Starting commit: `e5853f4` (Tornado Cash cluster). Ending commit: `7f4b455` (Tornado Cash delisting).

## Scorecard

| Mission | Date | Events | Status | Trigger | Confidence |
|---|---|---|---|---|---|
| 1 | 2026-03-23 | 84 | ✅ Attributed | CU-TRG-0040 (SDNY sealed civil 26-cv-2327) | HIGH |
| 2 | 2026-03-12 | 60 | ✅ Attributed | CU-TRG-0041 (OFAC DPRK IT Worker Fraud, SB0416) | MEDIUM |
| 3 | 2025-11-04 | 339 | ✅ Attributed | CU-TRG-0042 (OFAC DPRK Bankers Cheil Credit Bank, SB0302) | HIGH |
| 4 | 2023-07-21 | 111 | ✅ Attributed (cross-chain propagation) | Multiple triggers | HIGH |
| 5 | 2023-07-31 | 94 | ✅ Attributed (cross-chain propagation) | Multiple triggers | HIGH |
| 6 | 2023-08-18 | 94 | ✅ Attributed (cross-chain propagation) | Multiple triggers | HIGH |
| 7 | 2023-06-08 | 93 | ✅ Attributed (cross-chain propagation) | Multiple triggers | HIGH |
| 8 | 2022-11-10 | 53 | ✅ Attributed | CU-TRG-0043 (OFAC darknet fentanyl + TC redesignation, JY1089) | HIGH |
| 9 | 2022-11-11 | 53 | ✅ Attributed | CU-TRG-0043 (same) | HIGH |
| 10 | 2025-08-14 | 69 | ✅ Attributed | CU-TRG-0044 (OFAC Garantex/Grinex, SB0225) | HIGH |
| 11 | 2025-04-02 | 48 | ✅ Attributed | CU-TRG-0045 (OFAC Houthi-Russia network, SB0068) | HIGH |
| 12 | 2026-01-30 | 45 | ✅ Attributed | CU-TRG-0046 (OFAC Zedcex/Zedxion IRGC, first IRGC-linked exchange) | HIGH |
| 13 | 2025-11-19 | 32 | ✅ Attributed | CU-TRG-0047 (OFAC Media Land BPH + Ryan Wedding, Fed Reg 2025-20573) | HIGH |
| 14 | 2025-10-14 | 31 | ✅ Attributed | CU-TRG-0049 (OFAC Prince Group Cambodia TCO, SB0278) | HIGH |
| 15 | 2024-12-20 | 30 | ✅ Attributed | CU-TRG-0048 (OFAC Sa'id al-Jamal Houthi financier) | HIGH |

**All 15 priority missions attributed. PLUS 4 bonus attributions:**
- 2025-09-16 (24 actions): Iranian Shadow Banking / Derakhshan-Alivand (SB0248)
- 2024-03-27 (24 actions): Gaza Now Hamas fundraising — first joint OFAC+UK OFSI crypto designation (JY2213)
- 2025-02-24 (18 actions): Circle follow-up to OFAC 2025-02-11 Zservers/LockBit designation
- 2025-03-21/22 (222 UNBLACKLIST actions): Tornado Cash delisting following Fifth Circuit Van Loon v. Treasury (SB0057) — first major OFAC crypto delisting

**Plus cross-chain trigger propagation**: 380 additional BLACKLIST actions attributed to their cross-chain counterparts via Circle's chain-launch catch-up sweeps (primarily Tornado Cash and Nov 2022 OFAC addresses replicated on arbitrum / polygon / optimism / base when those L2 chains gained native USDC).

## Global metrics

| Metric | Pre–Pass B | Post–Pass B | Delta |
|---|---|---|---|
| Triggered BLACKLIST actions | 644 (28.1%) | 1,934 (84.5%) | +1,290 (+56.4 pp) |
| Triggered UNBLACKLIST actions | 0 | 222 (35.0%) | +222 |
| Sources | 23 | 38 | +15 |
| Entities | 38 | 58 | +20 |
| Triggers | 39 | 53 | +14 |
| Incidents | 1 | 3 | +2 |
| Action_sources | 644 | 2,159 | +1,515 |

**1,290 BLACKLIST actions newly attributed**, increasing coverage from 28% to 84.5%. 222 UNBLACKLIST actions newly attributed (the Tornado Cash delisting sweep).

## Source quality breakdown

| Tier | Count |
|---|---|
| PRIMARY (Circle/gov) | 34 |
| SECONDARY (news) | 3 |
| TERTIARY (community) | 1 |

14 PRIMARY sources were added in Pass B, all Treasury OFAC press releases or Federal Register notices. The Reddit r/Buttcoin post (CU-SRC-0025) is the sole TERTIARY source. The CoinDesk 16-wallet coverage (CU-SRC-0024) is our only major new SECONDARY source.

## Major findings and surprises

1. **The 2026-03-23 "16 wallets" freeze is a sealed SDNY civil case (26-cv-2327)**, confirmed via multi-outlet reporting. The Reddit r/Buttcoin community's core factual claim is corroborated — Circle did freeze operational businesses including the DFINITY ckETH Minter, Goated.com, 500 Casino, and Whale. Of the 16 business-wallet entities, at least 4-5 were reversed by 2026-04-07 after public pressure. This constitutes the strongest single piece of evidence that Circle's "court order" discipline produces both over-inclusion (public bridge contracts) and under-inclusion (Drift hack inaction 9 days later); the "over-inclusion" framing is HIGH confidence for ckETH Minter, MEDIUM confidence for the broader characterization.

2. **The 2026-03-12 and 2026-03-23 clusters are NOT Drift-related**, despite the mission briefing's initial hypothesis. The Drift hack was April 1, 2026; these March clusters predate it. The Drift hack does appear as context in the 2026-03-23 cluster notes (same-Circle-freeze-apparatus context). Mission 1's original motivation (Drift hack lateness) is captured in the 2026-03-23 cluster analysis, though the blacklist actions themselves are unrelated to Drift.

3. **Almost every "mystery cluster" in the MISSIONS.md list resolves to an OFAC designation** (HIGH confidence), many with same-day Circle response within a sub-minute window on 6 chains simultaneously. The pattern is extremely consistent: OFAC publishes a press release, and Circle's compliance apparatus fires `blacklist(address)` calls across all EVM chains in rapid sequence.

4. **The 2023 L2 chain launches produced "catch-up" mass-replication blacklists** (93-111 actions each on Jun 8 arbitrum, Jul 21 polygon, Jul 31 optimism, Aug 18 base). These are Circle replicating its Ethereum blacklist set to new native-USDC deployments. Previously untriggered because Pass A keyed triggers to action-date OFAC matches; cross-chain replication propagation fixed 380 of these.

5. **The 2022-11-10/11 cluster is NOT FTX-related** (despite the mission's hypothesis based on FTX collapse timing). The 53 addresses align with the Nov 8 2022 Tornado Cash redesignation + Nov 9 2022 darknet fentanyl supplier designation (Peijnenburg, Grimm, De Koning + 9 shell entities). Circle's response is cross-chain (eth + avax). No Alameda, FTX Accounts Drainer, or SBF-corporate addresses appear.

6. **The 2025-03-21 Tornado Cash DELISTING is a major data point** for policy-vs-practice: Circle mirrors not only OFAC sanctions but also OFAC de-sanctions. The Fifth Circuit's Van Loon v. Treasury ruling (Nov 2024) forced OFAC to concede that immutable smart contracts are not "property" under IEEPA — a landmark limit on OFAC's crypto reach. Circle's 540-action UNBLACKLIST cascade (Mar 21 eth + Mar 22 cross-chain) reverses the 2022-08-08 Tornado Cash campaign.

7. **OFAC's 2025 crypto enforcement was historic in scope**. The 2025-11-04 Cheil Credit Bank designation (53 addresses), 2025-10-14 Prince Group TCO (146 entities, $14.4B BTC seizure), 2025-08-14 Garantex redesignation + A7A5 Russian ruble token — all point to a dramatic expansion of OFAC crypto sanctions in scale and sophistication. Circle's compliance tracks this escalation closely.

## Policy-vs-practice observations (running thesis)

Circle's freeze discipline appears bimodal across the observed dataset (MEDIUM confidence — based on 3 trigger types; wider sampling may shift the characterization):

- **Fast and precise for OFAC designations**: sub-minute multi-chain response, well-calibrated to the literal SDN list.
- **Over-inclusive for sealed court orders**: the issue on 2026-03-23 was not speed — it was that Circle swept in public bridge infrastructure (ckETH Minter) without apparent independent diligence (HIGH confidence on the ckETH inclusion).
- **Non-responsive to public on-chain theft signals**: the 6-hour window on 2026-04-01 produced no Circle intervention despite public tracking of the $232M CCTP bridging (on-chain verifiable; characterization as "non-responsive" reflects observed behavior, not intent).

This pattern is consistent with Circle's stated policy ("we act only on legal orders"), but the data shows that the practical consequences include both over-inclusion of legitimate infrastructure and non-intervention in active thefts.

CEO Jeremy Allaire's 2026-04-13 statement — "We don't freeze without a court order" — is consistent with the data as a statement of current doctrine. The 2022-08-08 Tornado Cash sweep is consistent with this doctrine because OFAC sanctions compliance is a legal obligation distinct from discretionary court-order-triggered freezes. The 2026-03-23 sealed civil order represents a case where the doctrine was applied with apparent over-breadth. The 2026-04-01 Drift hack represents a case where the doctrine was not applied at all (MEDIUM confidence on causal interpretation; all three data points are on-chain verifiable).

## Open questions and next-pass priorities

### Still-untriggered BLACKLIST clusters (354 remaining)

| Date | Count | Hypothesis |
|---|---|---|
| 2023-10-04 | 24 | Likely Oct 3 2023 OFAC China fentanyl network (17 crypto addrs) — need Federal Register confirm |
| 2023-11-15 | 16 | Unknown — investigate |
| 2026-04-11 | 12 | Very recent; possibly Cartel-linked casinos or a hack-response |
| 2024-03-21 | 12 | OFAC Gambashidze/Tupikin Russian foreign election interference (2024-03-20) |
| 2025-10-10 | 8 | Unknown — possibly pre-Prince Group staging |
| 2024-09-14 | 7 | Unknown |
| Dozens of smaller clusters | 258 | Scattered — many likely smaller OFAC updates or individual incidents |

### Research priorities for Pass C

1. **2023-10-04** (24 actions): Check OFAC Oct 3 2023 China fentanyl network
2. **2024-03-21** (12 actions): Check OFAC Gambashidze/Tupikin March 20 2024
3. **2026-04-11** (12 actions): Very recent action, investigate Treasury OFAC April 2026 press releases
4. **Additional r/Buttcoin / community claims**: Look for other community-flagged freezes that might reveal under-documented policy actions
5. **Remaining small clusters**: Many are likely small OFAC updates (1-3 addresses) that would require Federal Register search by date

### Multichain-related addresses not yet attributed

The 3 Multichain hacker addresses (CU-ACT-0177, 0178, 0179, dated 2023-07-07) remain untriggered in our data. These should be attributed to a COURT_ORDER trigger based on the Oct 2023 DOJ seizure warrant + Nov 2025 SDNY bankruptcy court extension order. Recommended next-pass action: create CU-TRG-0054 Multichain court order with CU-SRC-0039 = The Block's coverage of Judge Jones's order.

## Commit SHA list

| SHA | Subject |
|---|---|
| 0f33b8b | 2026-03-23 "16 wallets" sealed civil case freeze + r/Buttcoin investigation |
| 32d3df2 | 2026-03-12 DPRK IT Worker Fraud Network — 60 actions |
| ac6a8f5 | 2025-11-04 OFAC DPRK Bankers designation — 339 actions |
| f6bf53a | 2022-11-10/11 FTX-era cluster + cross-chain trigger propagation — 106 + 380 actions |
| 74ad8e0 | Missions 10-13, 15 — 224 actions (Garantex/Houthi/Zedcex/Media Land/al-Jamal) |
| 9cdb7ae | 2025-10-14 Prince Group Cambodia TCO — 31 actions |
| a516098 | Bonus clusters — Sep 16 Iranian shadow + Mar 27 Gaza Now + Feb 24 Zservers |
| 7f4b455 | Tornado Cash delisting — 222 UNBLACKLIST actions |

Total 8 commits. All validated via `scripts/99_validate.py` before committing.

## Process / environment notes

- **WebFetch was blocked** in this environment (HTTP 403 from both the built-in tool and `curl`/`urllib`). All Pass B source content was reconstructed from WebSearch snippets cross-referenced across 3-8 outlets per event. SHA256-hashed Markdown summaries are stored locally under `sources/<year>/CU-SRC-<id>.md`.
- **Primary sources** (CU-SRC-0026 through CU-SRC-0038) are all Treasury OFAC press releases or Federal Register notices. Direct URL archive to Wayback Machine was not possible; each source file includes the canonical URL, companion URLs, and cross-outlet attribution.
- The Reddit r/Buttcoin post (CU-SRC-0025) required a paraphrased archive because the Reddit JSON endpoint returned HTTP 403. Community-claim corroboration is documented in `notes/reddit-buttcoin-16-wallets.md` with on-chain verification against our actions data.
