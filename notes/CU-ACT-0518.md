---
title: "CU-ACT-0518 — 2025-11-04 OFAC DPRK Bankers + Cheil Credit Bank designation (339 actions)"
date: 2026-04-21
scope: Attribute 339 BLACKLIST actions across 6 EVM chains to OFAC SB0302 designating DPRK bankers and Cheil Credit Bank front companies
---

# CU-ACT-0518 (and cluster of 339 actions) — 2025-11-04 OFAC DPRK Bankers + Cheil Credit Bank designation

- **Action date:** 2025-11-04
- **Mechanism:** BLACKLIST on 6 EVM chains (ethereum 74, avalanche 53, base 53, polygon 53, arbitrum 53, optimism 53) = 339 total actions
- **Unique addresses:** 53 (each blacklisted on all 6 chains; Ethereum has 21 additional repeat actions)
- **Trigger:** CU-TRG-0042 — OFAC SB0302 (2025-11-04)
- **Incident:** CU-INC-0003 — DPRK bankers and front-company network laundering cybercrime and IT-worker fraud proceeds

## Attribution confidence

HIGH. The cluster has an unmistakable compliance signature:
- Executed within a 76-second window (17:20:55 to 17:22:11 UTC) across 6 chains — impossible without a pre-planned coordinated sweep
- Count exactly matches OFAC's 53-address designation published same day
- Targets are all novel multi-chain deployments (coordinated across avax/op/arb/polygon/base/eth)
- All actions fired by the Circle BLACKLISTER EOA

The primary caveat: the 53 EVM addresses are not directly present in our OFAC XML snapshot (which captures only the USDT-TRC20 addresses OFAC attached to Cheil's SDN listing). Circle appears to have operated from a richer intelligence base — either private OFAC coordination or independent tracing to identify EVM sister addresses (LOW confidence on the exact mechanism). The overall match is circumstantial but overwhelming given the timing and count.

## OFAC action details (2025-11-04, Press Release SB0302)

**8 individuals sanctioned** for DPRK cybercrime and IT-worker fraud laundering:
- Jang Kuk Chol (Cheil Credit Bank banker, managed ~$5.3M in crypto)
- Ho Jong Son (Cheil Credit Bank)
- Han Hong Gil (Koryo Commercial Bank, ~$630K on behalf of Ryugyong)
- Ho Yong Chol, Jong Sung Hyok (DPRK Foreign Trade Bank rep in Vladivostok), Choe Chun Pom, Ri Jin Hyok + 1

**2 entities sanctioned:**
- Korea Mangyongdae Computer Technology Company (KMCTC)
- Plus a front company

**Crypto address update:** 53 addresses appended to Cheil Credit Bank's SDN entry.

**Scale:** Cheil-controlled wallets received $12.7M June 2023–May 2025 per TRM Labs; total ecosystem ~$2B+ stolen by DPRK actors in 2025.

## Policy-vs-practice observation

This is a textbook OFAC compliance response. Circle's compliance infrastructure demonstrates precision at sub-minute timing across 6 chains. Compared to the over-inclusive behavior on the 2026-03-23 sealed civil case (76 seconds for a clean OFAC action vs. sweeping up public bridges under sealed orders), the contrast sharpens the central research question: Circle's enforcement quality is not uniform across trigger types — it appears conditioned on the clarity and source of authority behind each request (MEDIUM confidence on this characterization, pending broader sampling).

## Sources
- CU-SRC-0027 — Treasury OFAC Press Release SB0302 + Elliptic + TRM Labs blog analysis (PRIMARY)

## Citation archive needed
- CU-SRC-0027: Elliptic and TRM Labs blog URLs require Wayback Machine archiving.
