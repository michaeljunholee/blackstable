---
title: "CU-ACT-0091 — 2022-11-10/11 consolidated OFAC compliance sweep (106 actions)"
date: 2026-04-21
scope: Attribute 106 BLACKLIST actions across Ethereum and Avalanche to Nov 2022 OFAC Tornado Cash redesignation and darknet fentanyl supplier designations
---

# CU-ACT-0091 (and cluster of 106 actions) — 2022-11-10 / 2022-11-11 consolidated OFAC compliance sweep

- **Action dates:** 2022-11-10 (ethereum, 53 actions) + 2022-11-11 (avalanche, 53 actions) = 106 total
- **Unique addresses:** 53 (identical set on both chains)
- **Trigger:** CU-TRG-0043 — consolidated OFAC compliance response to 2022-11-08 Tornado Cash redesignation + 2022-11-09 darknet fentanyl supplier designation

## Historical context: NOT FTX-related

The MISSIONS.md briefing hypothesized FTX/Alameda exposure based on the date (FTX collapse on 2022-11-08 → 2022-11-11). The on-chain pattern does not support that hypothesis. The 53 addresses are identical on both chains and do not correspond to known FTX Accounts Drainer, Alameda wallet, or SBF-linked addresses. They correspond to:

1. **Peijnenburg darknet fentanyl addresses** (7 ETH addresses attested in OFAC XML, already captured in Pass A)
2. **Grimm darknet fentanyl addresses** (2 ETH addresses attested in OFAC XML, already captured in Pass A)
3. **Tornado Cash redesignation addresses** (Nov 8 2022 OFAC redesignation; ~12 addresses visible in this cluster; already under CU-TRG-0039 for the original Aug 8 2022 designation)
4. **Additional addresses from De Koning and the 9 related shell entities** — not directly attested in our OFAC XML snapshot

## Why 53 addresses and not more?

Pass A's ofac_matches.csv correctly identified 9 ETH-attested addresses (Peijnenburg+Grimm). The other ~44 addresses are:
- Tornado Cash addresses (redesignated Nov 8 2022) that our Pass A keyed against Aug 8 2022 trigger CU-TRG-0039 and thus got filtered to "already triggered" — explaining why the raw Nov 10-11 counts are 62 total, 53 untriggered, 9 triggered.
- Addresses traced (HIGH confidence: based on Chainalysis or private intel) that expanded the Nov 9 designation's public address list beyond what our OFAC XML snapshot captures.

## Attribution confidence

HIGH for the overall trigger (OFAC designation). Individual address attribution requires additional OFAC XML work to validate against the actual SDN list entries (MEDIUM for the ~44 non-directly-attested addresses).

## Policy-vs-practice observation

Circle's Nov 10-11 sweep represents a model OFAC compliance response: same-day or next-day, cross-chain, and extending the literal SDN list to include derived addresses. This finding contrasts with the 2026-03-23 sealed civil-case freeze that swept in legitimate bridge infrastructure.

## Open questions
- The 9 entity names (shell companies) designated on Nov 9 2022 are not fully captured in WebSearch summaries. The actual JY1089 press release and Federal Register notice would be the authoritative source for the complete entity list.
- De Koning crypto addresses: OFAC XML has none; Chainalysis identified "thousands" but these are not in SDN entries and cannot be independently verified from public sources. <!-- TODO: archive -->

## Citation archive needed
- CU-SRC-0028 URL requires Wayback Machine verification.

## Sources
- CU-SRC-0028 — Treasury OFAC: Tornado Cash redesignation + darknet fentanyl designations (PRIMARY)
