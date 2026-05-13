---
title: "CU-ACT-0666 — 2026-03-23 sealed SDNY civil case freeze (84 actions, \"16 wallets\")"
date: 2026-04-21
scope: Attribute 84 BLACKLIST actions on 2026-03-23 to SDNY sealed civil case 26-cv-2327; document over-inclusion of public bridge infrastructure
---

# CU-ACT-0666 (and cluster of 84 actions) — 2026-03-23 "16 wallets" civil case freeze

- **Action date:** 2026-03-23
- **Mechanism:** BLACKLIST on ethereum (80 actions) + polygon (4 actions)
- **Cluster size:** 84 distinct address/chain events; reporting refers to "16 business hot wallets" — the 84-count is consistent with 16 entities each represented across multiple chain deployments or multiple hot wallets per entity.
- **Marquee targets:** DFINITY ckETH Minter (`0xb25ea1d493b49a1ded42ac5b1208cc618f9a9b80`, REVERSED 2026-03-28 via CU-ACT-0744); Goated.com (`0x61f08d119974a3d9915f06765d83fe1aa677e543`); 500 Casino, Whale (specific addresses undisclosed).
- **Trigger:** CU-TRG-0040 — sealed SDNY civil-case court order (26-cv-2327), plaintiff counsel Willkie Farr.

## Significance

This cluster is the **main community trigger** for the 2026 controversy over Circle's freeze discipline. Three distinctive features:

1. **Sealed legal basis.** Circle executed the freeze under a sealed court order it cannot disclose. No public docket entry, no visible statute, no named plaintiffs. Affected parties learned only by receiving Circle's private notice.

2. **Indiscriminate inclusion of public infrastructure.** The freeze swept in the ckETH Minter — a public bridge contract operated by DFINITY Foundation — with no apparent connection to the underlying civil case. This is the strongest on-chain evidence that Circle applied transaction-graph clustering without individualized review (HIGH confidence for ckETH inclusion; LOW confidence on the specific clustering method used). ZachXBT characterized the pattern as: "any analyst with basic tools could have identified within minutes that these were operational business wallets." <!-- TODO: archive ZachXBT tweet citation -->

3. **Timing juxtaposition against the 2026-04-01 Drift hack.** Nine days later, Circle did not freeze approximately $230M in actively-laundered USDC flowing through CCTP from Solana to Ethereum over 100+ transactions across six hours. CEO Allaire stated publicly (2026-04-13): "We don't freeze without a court order." The 2026-03-23 cluster demonstrates that the court-order requirement was applied broadly enough to catch public bridge contracts — but the same mechanism did not produce real-time intervention in response to active theft intelligence (this juxtaposition is factual on-chain; the policy interpretation is MEDIUM confidence pending broader data).

## Policy-vs-practice implication

The data shows that a sealed civil order was sufficient basis for Circle to freeze 16 business wallet clusters — including a public cross-chain bridge with no apparent nexus to the underlying civil case. This finding sits in tension with CEO Allaire's stated "rule of law" framing (CU-SRC-0024) as it applies to the refusal to act on public on-chain evidence of the Drift Protocol theft. The Drift Protocol class action (Gibbs Mura law firm, filed 2026-04-15) is testing this same tension. <!-- editorial: claim needs author verification — Drift class action filing date and law firm not independently confirmed in this note; see CU-SRC-0024 -->

## Sources
- CU-SRC-0024 (CoinDesk / multi-outlet summary, 2026-04-13) — EVIDENCE_OF_TRIGGER for all 84 actions <!-- TODO: archive -->
- CU-SRC-0025 (r/Buttcoin community post, 2026-03-24) — CONTEXT for marquee addresses <!-- TODO: archive -->

## Citation archive needed
- CU-SRC-0024: CoinDesk URL and companion outlet URLs require Wayback Machine archiving.
- CU-SRC-0025: Reddit post is not archived locally (HTTP 403 at fetch time; see fetch note in `notes/reddit-buttcoin-16-wallets.md`).

## Open research questions
- Addresses for 500 Casino and Whale are not publicly disclosed — confirmation would require direct reporting or affected-entity disclosure.
- 12 of the 16 underlying entities remain unnamed.
- Underlying sealed case plaintiffs and specific theft allegation are unknown to the public.
