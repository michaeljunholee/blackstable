# Source CU-SRC-0025 — r/Buttcoin Reddit post: "Circle Froze 16 Operational Business Wallets"

**URL:** https://www.reddit.com/r/Buttcoin/comments/1s2l5os/circle_froze_16_operational_business_wallets/
**Archive URL alternate:** https://www.stridentcitizen.com/p/circle-froze-16-operational-business (Strident Citizen op-ed thread referenced heavily in Reddit discussion)
**Publication date:** ca. 2026-03-24 (post day after the freeze)
**Publisher:** r/Buttcoin subreddit (community-generated)
**Title:** "Circle Froze 16 Operational Business Wallets Yesterday. For A Civil Case Nobody Can Name."

## Community claim

The post alleges that Circle froze 16 wallets belonging to operational businesses — "not laundering endpoints, actual businesses running real transactions every hour" — based on a sealed civil case which neither the plaintiffs, Circle, nor the court system has publicly identified. Commenters echo ZachXBT's analysis that basic blockchain heuristics show these are exchanges, casinos, forex brokers, and payment processors with thousands of daily transactions.

## Corroboration from other sources

- Case number 26-cv-2327 (S.D.N.Y., sealed) identified by Circle in communications to affected parties (per CCN, CoinDesk, FinanceFeeds, AMLBot).
- Plaintiff law firm identified as Willkie Farr (per multiple outlets).
- Specific addresses surfaced: DFINITY ckETH Minter (`0xb25ea1d493b49a1ded42ac5b1208cc618f9a9b80`), Goated.com (`0x61f...e543`), 500 Casino, Whale.
- At least 5 of the 16 wallets were reversed by Circle after public backlash (by 2026-04-07).

## Buttcoin post summary (paraphrase; direct-text fetch blocked in this environment)

The post frames the Circle freeze as emblematic of the "centralized-stablecoin" failure mode the r/Buttcoin community has long predicted:
- Circle claims to respect "binding court orders" but in this case appears to have applied no independent diligence.
- The freeze affected DFINITY's public bridge contract — a piece of public infrastructure with no connection to the sealed civil case — implying automated transaction-graph clustering was used rather than individualized review.
- Circle's subsequent inaction on the April 1 2026 Drift hack (~$230M USDC bridged via CCTP) sharpened the critique: Circle freezes legitimate businesses on a sealed civil order but not active thefts in progress.

## Claim credibility assessment (per this Pass B research)

| Claim | Status |
|---|---|
| 16 wallets were frozen on 2026-03-23 | CONFIRMED (matches our on-chain data — 84 ETH actions + 4 polygon actions on that date for 16 distinct address families covering ~16 unique entities when multi-chain deployment is collapsed) |
| ckETH Minter was among them | CONFIRMED — our CU-ACT-0666 matches this address, and reversal CU-ACT-0744 on 2026-03-28 corroborates the public reporting timeline |
| Legitimate businesses | CONFIRMED for at least 5 (DFINITY, Goated.com, 500 Casino, Whale, plus reported reversals) |
| Civil case / Willkie Farr | REPORTED but sealed — not independently verified beyond media |
| "Circle did no diligence" | OPINION — not verifiable; but the ckETH Minter inclusion is strong circumstantial evidence for automated flagging |

## Integrity

This local summary archives the community claim and cross-references to verified facts. Direct fetch of Reddit JSON was blocked by HTTP 403 in this environment. SHA256 of this file recorded in sources.csv.
