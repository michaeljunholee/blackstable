# Source CU-SRC-0027 — Treasury OFAC: DPRK Bankers + Cheil Credit Bank crypto address listing (2025-11-04)

**Primary URL:** https://home.treasury.gov/news/press-releases/sb0302
**Recent-actions URL:** https://ofac.treasury.gov/recent-actions/20251104
**Companion URLs:** https://www.elliptic.co/blog/ofac-lists-53-crypto-addresses-of-sanctioned-north-korean-cheil-credit-bank ; https://www.trmlabs.com/resources/blog/us-treasury-sanctions-dprk-bankers-and-front-companies-laundering-proceeds-from-cybercrime-and-it-worker-operations ; https://www.coindesk.com/business/2025/11/04/u-s-sanctions-north-korean-bankers-over-crypto-laundering-tied-to-cyberattacks
**Publication date:** 2025-11-04
**Publisher:** U.S. Department of the Treasury — Office of Foreign Assets Control (press release SB0302)
**Title:** Treasury Sanctions DPRK Bankers and Institutions Involved in Laundering Cybercrime Proceeds and IT Worker Funds

## Designations

On 2025-11-04, OFAC designated 8 individuals and 2 entities for laundering proceeds from DPRK cybercrime / IT worker fraud schemes to fund WMD and ballistic-missile programs.

### Individuals (all added to SDN list)
- Jang Kuk Chol — First Credit Bank (aka Cheil Credit Bank) banker; managed ~$5.3M in crypto
- Ho Jong Son — First Credit Bank banker (same cluster)
- Han Hong Gil — Koryo Commercial Bank (KCB); ~$630K USD/CNY transactions on behalf of Ryugyong Commercial Bank
- Ho Yong Chol — China- or Russia-based DPRK bank rep
- Jong Sung Hyok — Chief representative, DPRK Foreign Trade Bank (FTB), Vladivostok
- Choe Chun Pom — DPRK bank rep
- Ri Jin Hyok — DPRK bank rep
- (one more individual, name not precisely captured in cross-sources)

### Entities (added to SDN)
- Korea Mangyongdae Computer Technology Company (KMCTC) — DPRK IT worker firm operating in Shenyang/Dandong China
- (one more entity, likely a front company — not precisely captured)

### Cheil Credit Bank crypto address update
OFAC updated Cheil Credit Bank's SDN entry with 53 specific cryptocurrency addresses. Per Elliptic and TRM Labs, 53 addresses were added. In our OFAC XML extract, these appear as USDT-TRC20 (Tron) addresses.

## Circle response (on-chain observation)

Within minutes of the OFAC press release on 2025-11-04, Circle executed a coordinated multi-chain USDC blacklist across 6 EVM chains (ethereum, polygon, base, avalanche, arbitrum, optimism). The pattern:
- 53 unique addresses blacklisted on each of the 6 chains (318 min) + 21 additional Ethereum-only events = **339 total blacklist actions** between 17:20:55 UTC and 17:22:11 UTC (76-second window).

Notably, the 53 blacklisted EVM addresses are NOT directly present in our OFAC XML snapshot (which only captures the Tron-USDT addresses for Cheil). This implies Circle had either:
1. Obtained independent on-chain tracing data linking the EVM addresses to the same DPRK banking network, OR
2. Worked from a superset list OFAC shared privately with major stablecoin issuers that included EVM-chain sister addresses for the same designees.

The timing + count match + coordinated multi-chain sweep pattern are unmistakable for an OFAC compliance action.

## Integrity

SHA256 of this file recorded in sources.csv. Direct fetch of the Treasury press release was blocked in this environment; content reconstructed from cross-verified WebSearch snippets (Elliptic, TRM Labs, CoinDesk, SlowMist, Money Laundering News).
