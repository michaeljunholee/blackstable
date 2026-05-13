# Source CU-SRC-0024 — CoinDesk / multi-outlet coverage: Circle 16-wallet USDC freeze (2026-03-23 civil case)

**URL (primary):** https://www.coindesk.com/business/2026/04/13/circle-ceo-says-he-won-t-freeze-usdc-without-a-court-order-even-as-hackers-walk-away-with-millions
**Companion URLs:** https://financefeeds.com/circle-freezes-usdc-in-16-business-hot-wallets-amid-undisclosed-u-s-civil-case/ ; https://www.ccn.com/news/crypto/circle-first-froze-16-usdc-wallets-and-now-unfreezing-them-heres-why/ ; https://blog.amlbot.com/circle-froze-16-business-hot-wallets-including-a-blockchain-bridge-smart-contract/
**Publication date:** 2026-04-13 (Allaire statement); initial reporting starting 2026-03-25
**Publisher:** CoinDesk (with cross-verification by FinanceFeeds, CCN.com, AMLBot, Bitcoin.com News, Cryptonomist.ch)
**Title:** "Circle's Allaire says USDC freezes require legal orders amid rising criticism" (and related reports)

## Key attribution

On 2026-03-23, Circle executed a bulk USDC blacklist covering 16 distinct business hot wallet addresses across multiple chains. Per multiple secondary-source reports cross-referenced with Circle's own statements to affected parties, the freeze was triggered by a sealed U.S. civil case in the Southern District of New York, case number **26-cv-2327**. The plaintiffs' law firm has been identified in reporting as **Willkie Farr & Gallagher LLP**. Court order particulars remain sealed; the on-chain effect was publicly observable via `blacklist(address)` calls on the USDC contracts across ethereum, polygon, arbitrum, avalanche, base, and optimism.

## Known entities inside the 16-wallet batch (per onchain sleuth ZachXBT and third-party reporting)

| Entity | Status | Known address prefix |
|---|---|---|
| DFINITY Foundation — ckETH Minter Contract | REVERSED ~2026-03-28 | `0xb25ea1d493b49a1ded42ac5b1208cc618f9a9b80` |
| Goated.com | REVERSED 2026-03-26 (~$131K) | `0x61f...e543` → `0x61f08d119974a3d9915f06765d83fe1aa677e543` |
| 500 Casino | REVERSED (by ZachXBT tweet dated ~2026-03-26) | not disclosed |
| Whale | REVERSED (same tweet) | not disclosed |
| Crypto exchanges, online casinos, forex brokers, payment processors (unnamed) | Various | — |

## Analysis (ZachXBT, per X post / Cointelegraph / CCN syndication)

ZachXBT (onchain investigator) publicly reviewed the 16 addresses within 24 hours and concluded that basic heuristics would have shown they were operational business infrastructure with no apparent connections to each other. He characterized the action as "potentially the single most incompetent freeze" he had seen in 5+ years. Circle responded by partially reversing the freeze: at least 5 of the 16 had been unfrozen by 2026-04-07, including the ckETH Minter and Goated.com wallet.

## Circle's official position

Per CEO Jeremy Allaire's 2026-04-13 statement: Circle will not freeze USDC without a court order, even when hackers are clearly stealing funds. This directly contradicts the rapid self-initiated freeze of 76 Tornado Cash addresses in 2022 and is cited by Drift-hack class-action plaintiffs as evidence of inconsistent policy.

## Contradiction / Policy-vs-practice observation

Circle's 2026 position — "binding court orders only" — cannot be reconciled with:
- 2022-08-08 mass-blacklist of Tornado Cash–associated addresses (pre-sanction, no court order)
- 2026-04-01 Drift hack: Circle had ~6 hours of warning per ZachXBT and took no action
- 2026-03-23 freeze: Circle executed a bulk freeze that swept in legitimate infrastructure (DFINITY bridge) with clear signs of minimal pre-enforcement diligence.

## Integrity

This local summary archives the factual content extracted from multiple cross-verified secondary sources. WebFetch of underlying URLs was blocked in this environment; search-engine snippets and cross-referenced reporting constitute the citation basis. SHA256 of this file recorded in sources.csv.
