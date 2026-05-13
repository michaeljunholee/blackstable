---
title: "2023-10-04 cluster — 4 addresses × 6 chains (24 events), untriggered"
date: 2026-04-21
scope: Attribution attempt for 24 BLACKLIST events on 2023-10-04 across 6 EVM chains; no public attribution found
---

# 2023-10-04 cluster (4 addresses × 6 chains = 24 events) — research note

**Status:** Untriggered. No public attribution found after targeted web search.
**Research date:** 2026-04-21
**Actions:** 24 BLACKLIST events across Ethereum, Base, Polygon, Avalanche, Arbitrum, Optimism (4 addresses each)
**Ethereum timestamps:** 2023-10-04 01:44:11 UTC → 01:45:35 UTC (~90 seconds)

## The 4 blacklisted addresses

| Address | Public attribution |
|---|---|
| `0x2e13ea767da12f504ceaaaebe5950488498dc2d2` | None found. Etherscan: no tag, no activity visible (likely fully drained post-freeze). |
| `0x7de5ab1914e241177344936dc33b4a8157c98248` | None found. |
| `0xbe5e683633ddd17d8a89b4e10860a0e426c5ed24` | None found. |
| `0xa6cc8ab881debc3c9e8adb32549d0cbe614168c5` | None found. |

## What the cluster looks like

- **Cross-chain propagation**: same 4 addresses blacklisted across all 6 EVM chains Circle operates USDC on. This operational pattern is consistent with Circle's canonical OFAC-response signature (one designation becomes 4-address × 6-chain = 24 events).
- **Tight Ethereum batch**: the 4 Ethereum blacklist calls completed within 84 seconds. Consistent with a scripted compliance response.
- **Date**: 2023-10-04 (Wednesday). OFAC actions that produce next-day Circle responses typically publish on the preceding business day (here: 2023-10-03, Tuesday).

## Attribution attempts — all negative

1. **OFAC press release JY1779 (2023-10-03 China fentanyl designation, Chainalysis-documented)** — named 4 Ethereum addresses: Shen Xianbiao `0x530a64c0…`, Zhang Wei `0x961c5be5…`, Wang Mingming `0xfac583c0…`, Valerian Labs `0x983a81ca…`. **None match our cluster's 4 addresses.** JY1779 is ruled out as a direct match.
2. **Multichain hack (July 2023)** — Circle blacklisted 3 addresses (`0x027F1…`, `0xefEeF…`, `0x48BeA…`) in October 2023 per public reporting. Prefixes do not match any of our 4 addresses.
3. **Direct address search** — all 4 addresses return zero indexed public results via WebSearch. Not in OFAC SDN XML, not in hack write-ups, not in publicly available sanctions trackers.
4. **Hamas / Israel-Gaza context** — the October 7 2023 attacks were 3 days later; no OFAC crypto designations on 2023-10-03/04 specifically referenced that context.

## Working hypothesis (LOW confidence)

**Either**:
- **(A) Derivative addresses from a compliance-vendor clustering applied multi-chain by Circle.** Chainalysis / TRM / Elliptic regularly publish address-attribution updates that Circle can ingest and apply without OFAC directly naming the specific address. The cross-chain propagation signature fits, but the decoupling from OFAC publication explains why no public search result surfaces.
- **(B) Private multi-chain court order.** A U.S. civil order granted with multi-chain reach would produce the same pattern. Less common than OFAC for a small 4-address set but cannot be ruled out.

Hypothesis (A) is assessed as more likely (LOW confidence): Circle's stated operational model explicitly includes vendor-attribution-driven action beyond direct OFAC listings, and the cross-chain propagation is more consistent with a compliance rule than a specific court order (court orders typically enumerate specific chains).

## Why attribution is not assigned

Per project operating rule: "Never fabricate attributions." Without a publicly citable attribution — from OFAC, a court docket, a vendor publication, or direct Circle disclosure — no `trigger_id` is assigned. A speculative "derivative-of-OFAC" link without the specific OFAC action does not meet the `EVIDENCE_OF_TRIGGER` evidentiary bar.

## Follow-up options

1. **Check Circle's own blog / transparency page for October 2023** — Circle occasionally posts blog items about compliance actions. A direct disclosure would attribute the cluster.
2. **Tether comparator scan on the same 4 addresses** — if Tether also blacklisted them around 2023-10-03/04, that's a strong signal they're on a shared attribution list (Chainalysis Public Sanctions Dataset or similar).
3. **Chainalysis/TRM historical blog archive for 2023-10** — vendor attribution publications from that week may name these addresses.
4. **OFAC SDN ZIP history on 2023-10-03 vs 2023-10-04** — diff of the SDN XML across those days may reveal addresses added that aren't in press releases.
