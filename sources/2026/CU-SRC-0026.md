# Source CU-SRC-0026 — Treasury OFAC Sanctions: DPRK IT Worker Fraud Network (2026-03-12)

**Primary URL:** https://home.treasury.gov/news/press-releases/sb0416
**Companion URLs:** https://www.chainalysis.com/blog/ofac-targets-north-korean-it-workers-crypto-march-2026/ ; https://www.federalregister.gov/documents/2026/03/17/2026-05114/notice-of-ofac-sanctions-action ; https://www.trmlabs.com/resources/blog/beyond-it-worker-fraud-ofacs-latest-dprk-designations-show-broader-sanctions-and-national-security-risk
**Publication date:** 2026-03-12
**Publisher:** U.S. Department of the Treasury — Office of Foreign Assets Control
**Title:** Treasury Sanctions Facilitators of DPRK IT Worker Fraud Targeting U.S. Businesses (Press Release SB0416)

## Key facts

On 2026-03-12, OFAC designated six individuals and two entities for roles in DPRK government-orchestrated IT worker fraud schemes that generated nearly $800 million in 2024 to fund DPRK's WMD/ballistic-missile programs.

### Sanctioned individuals
- Yun Song-guk (DPRK national, led IT worker cell in Boten, Laos)
- York Louis Celestino Herrera (Dominican Republic)
- Nguyen Quang Viet (Vietnam)
- Do Phi Khanh (Vietnam)
- Hoang Van Nguyen (Vietnam)
- Hoang Minh Quang (Vietnam)

### Sanctioned entities
- Amnokgang Technology Development Company (DPRK)
- Quangvietdnbg International Services Company (Vietnam)

### Crypto addresses designated
Per Chainalysis / Federal Register summary: 21 cryptocurrency addresses across Ethereum, Tron, and Bitcoin networks. Known Ethereum addresses confirmed in our OFAC XML snapshot:
- Yun: `0xb637f84b66876ebf609c2a4208905f9ddac9d075`, `0x95584c303fcd48af5c6b9873015f2ad0ca84eae3`
- Amnokgang: `0xcb74874f1e06fcf80a306e06e5379a44b488ba2d`, `0x0330070fd38ec3bb94f58fa55d40368271e9e54a`, `0x9be599d7867f5e1a2d7ec6db9710df2b98a15573`
- Sim Hyon Sop (update to prior designation): `0x4f47bc496083c727c5fbe3ce9cdf2b0f6496270c`, `0xd04e33461fea8302c5e1e13895b60cee8aefda7f`, `0x76ea76ca4eb727f18956ab93445a94c5280412b9`, `0xfb3eff152ea55d1bfa04dbdd509a80fd7b72cdeb`, `0xfda1ec4a6178d4916b001a065422d31ebe5f62ff`, `0x747afb5c7a7fc34b547cd0fdebf9b91759c5a52b`

## Circle response on 2026-03-12 (per on-chain observation)

On 2026-03-12 Circle executed BLACKLIST actions covering 21 distinct addresses across 6 EVM chains (ethereum, polygon, base, avalanche, arbitrum, optimism). 11 of those 21 addresses are directly attested in our OFAC XML snapshot (Sim, Yun, Amnokgang). The remaining 10 addresses are plausibly additional DPRK IT worker network addresses that OFAC designated on the same date but that our current OFAC XML snapshot does not include (possibly added later via subsequent updates, or designated under party-refs not yet in our snapshot's crypto-address extract).

The 10 additional untriggered Mar-12 Ethereum addresses:
- `0x283fcf7f260da7c3c9aad91beab58882990a66eb`
- `0x2ec6c5fe3d7acd8e2e6185c17d9acb136e66f3e0`
- `0x47df0606a84a52763887d7aa280cc4f068326b16`
- `0x6315bdc714ebb7a08e5ec10f351b6ca61d052bee`
- `0x88ef69134150f35b1e91fa2d8bfbb44ba2c51e62`
- `0x8d55c4306745f05a31af596c6bfa19374073e797`
- `0x9145fc390e71e3b56da4bfe51460cbdbb1a8a3f9`
- `0xee61f0eeee09eed3583baab61fa2e64b96207478`
- `0xf8bc582628cd0c721b554161a1cb59ea003742c0`
- `0xfe88af78cfc99bea57f2fb708489cfc0f0b7f704`

Attribution confidence for these 10 addresses: **MEDIUM**. They were blacklisted by Circle on the same day as the DPRK designation, in the same multi-chain coordinated pattern (each address on 6 chains), which is the unmistakable signature of an OFAC-driven SDN-compliance sweep. However, none match the current OFAC XML snapshot directly, so we cannot assign them to a specific designated party.

## Integrity

SHA256 of this file recorded in sources.csv. Direct fetch of the Treasury press release was blocked in this environment; content is reconstructed from cross-verified WebSearch snippets.
