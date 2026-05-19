---
title: "CU-ACT-0633 — 2026-03-12 OFAC DPRK IT Worker Fraud Network designation (60 actions)"
date: 2026-04-21
scope: Attribute 60 BLACKLIST actions across 6 EVM chains to OFAC SB0416 DPRK IT Worker Fraud Network designation
---

# CU-ACT-0633 (and cluster of 60 actions) — 2026-03-12 OFAC DPRK IT Worker Fraud Network designation

- **Action date:** 2026-03-12
- **Mechanism:** BLACKLIST across ethereum (10), polygon (10), base (10), avalanche (10), arbitrum (10), optimism (10) — 60 events, 10 unique addresses
- **Trigger:** CU-TRG-0041 — OFAC SDN designation of 2026-03-12 DPRK IT Worker Fraud Network
- **Incident:** CU-INC-0002

## Attribution confidence

MEDIUM. These 10 addresses are not in our current OFAC XML snapshot (`data/raw/ofac_sdn/sdn_advanced.xml`), but they were blacklisted by Circle on the exact same day and in the same multi-chain (all 6 EVM chains simultaneously) coordinated pattern as 11 addresses that are attested in OFAC to the 2026-03-12 designation (Sim Hyon Sop, Yun Song-guk, Amnokgang Technology Development Company). This timing and operational signature is consistent with an OFAC compliance response.

Working hypothesis (MEDIUM confidence): these 10 addresses were part of the 21 crypto addresses designated by OFAC on 2026-03-12 but are recorded in the OFAC XML under party-refs not included in our current extract (which filters only certain symbols). The 10 untriggered addresses on 6 chains = 60 actions, plus 11 attested OFAC addresses accounting for 66 pre-triggered actions = 126 total Mar-12 BLACKLIST events.

## Related 2026-03-12 sanctioned parties

- Individuals: Yun Song-guk (DPRK), York Louis Celestino Herrera (DR), Nguyen Quang Viet (VN), Do Phi Khanh (VN), Hoang Van Nguyen (VN), Hoang Minh Quang (VN)
- Entities: Amnokgang Technology Development Company (DPRK), Quangvietdnbg International Services Company (VN)
- Volume: ~$800M defrauded in 2024 from U.S. businesses via DPRK IT worker remote contracts
- Purpose: Funds DPRK weapons-of-mass-destruction and ballistic-missile programs

## Policy-vs-practice observation

This cluster presents as a clean compliance case. Circle blacklisted all directly attested OFAC addresses within hours and also blacklisted 10 additional addresses on the same day that cannot be directly attested in the current snapshot but are consistent with the same designation. Circle's behavior is consistent with its stated OFAC sanctions-compliance posture. The methodological observation is that Circle's blacklist sweep covered addresses OFAC announced but that the downstream OFAC-XML extract misses; this implies Circle has tighter OFAC intake than public-snapshot extraction can capture.

Policy-vs-practice verdict: Circle's response to this designation is consistent with its compliance promise (MEDIUM confidence given the 10 non-directly-attested addresses).

## Sources
- CU-SRC-0026 — Treasury OFAC press release SB0416 + Chainalysis blog + Federal Register summary (PRIMARY)

## Citation archive needed
- CU-SRC-0026: Chainalysis blog URL requires Wayback Machine archiving.
