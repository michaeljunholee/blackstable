---
title: "CU-ACT-0001 — First USDC Blacklist Action (2020-06-16)"
date: 2020-07-08
scope: "Precedent case: Circle's first on-chain USDC blacklist, attributed to a law-enforcement request with no publicly verifiable court order."
---

# CU-ACT-0001 — First USDC blacklist

- **Action date:** 2020-06-16 (block 10,274,701)
- **Mechanism:** BLACKLIST on Ethereum mainnet
- **Target:** `0xaa05f7c7eb9af63d6cc03c36c4f4ef6c37431ee0`
- **Amount:** 100,000 USDC
- **Tx hash:** `0x15cbde1b9bf285db50e22eeff1a7d04ea267dd94726df8ecabdb4cb6c2b590cb`

## Significance

This is the **first-ever** USDC blacklist action. It established precedent for Circle's discretionary freeze behavior and the public framing Circle would use in subsequent cases.

## Circle's framing (verbatim, per Centre/Circle statement via CoinDesk, 2020-07-08)

> Centre can confirm it blacklisted an address in response to a request from law enforcement. While we cannot comment on the specifics of law enforcement requests, Centre complies with binding court orders that have appropriate jurisdiction over the organization.

<!-- TODO: archive — CoinDesk 2020-07-08 URL not confirmed archived locally beyond CU-SRC-0022 summary -->

## What's documented vs. unknown

| Fact | Known |
|---|---|
| Target address | Yes |
| Amount | Yes (~100,000 USDC) |
| Approximate date | Yes (June 16, 2020) |
| Requesting agency | **No** — not disclosed |
| Court order docket # | **No** — not disclosed |
| Underlying crime | Alleged theft (Etherscan commenter claimed "stole tokens from him" — unverified, LOW confidence) |
| Victim identity | **No** |
| Disclosure date | July 8, 2020 (≈22 days after action; disclosed via press response, not proactive) |

## Policy-vs-practice observation

Circle's public rationale ("complies with binding court orders") is **consistent** with a law-enforcement-driven action as stated. However, several aspects are not externally verifiable:

- No court order was ever published or identified publicly.
- The "binding court order" framing is Circle's self-characterization; Centre's spokesperson explicitly declined to comment on specifics.
- The 22-day disclosure gap is notable: Circle did not proactively disclose the action, instead responding to press inquiry after Etherscan observers noticed the `blacklist(address)` transaction.

This case illustrates (HIGH confidence from data): even where Circle claims a clean legal basis, that basis is not externally verifiable from on-chain data or public records alone.

## Sources

- Yahoo Finance / CoinDesk, 2020-07-08: `CU-SRC-0022` (local archive at `sources/2020/CU-SRC-0022.md`)
