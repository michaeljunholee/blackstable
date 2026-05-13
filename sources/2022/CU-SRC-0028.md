# Source CU-SRC-0028 — Treasury OFAC: Darknet Fentanyl Suppliers + Tornado Cash Redesignation (2022-11-08 / 2022-11-09)

**Primary URLs:**
- https://home.treasury.gov/news/press-releases/jy1089 — Treasury press release on darknet fentanyl suppliers (Nov 9, 2022)
- https://ofac.treasury.gov/recent-actions/20221108 — Tornado Cash redesignation (Nov 8, 2022)
**Companion URLs:**
- https://www.chainalysis.com/blog/ofac-sanctions-suppliers-of-illicit-fentanyl/
- https://www.elliptic.co/blog/ofac-sanctions-11-members-of-the-trickbot-cybercrime-gang
- https://www.chainalysis.com/blog/trickbot-ransomware-sanctions/
**Publication dates:** 2022-11-08 (Tornado redesignation); 2022-11-09 (darknet fentanyl suppliers)
**Publisher:** U.S. Department of the Treasury — OFAC

## November 8, 2022 — Tornado Cash Redesignation

OFAC delisted and relisted Tornado Cash, replacing the Aug 8, 2022 designation. The redesignation cited additional Executive Order 13722 authority regarding DPRK WMD proliferation finance in addition to the original E.O. 13694 cyber-enabled activity authority. This re-established the full SDN coverage of Tornado Cash smart-contract addresses.

## November 9, 2022 — Darknet Fentanyl Suppliers

OFAC designated three individuals and nine entities pursuant to Executive Order 14059 (December 2021) for supplying illicit fentanyl, synthetic stimulants, cannabinoids, and opioids to U.S. markets through internet sales and shell companies:

### Individuals
- Alex Adrianus Martinus Peijnenburg (Dutch) — 7 ETH, 18 BTC, 1 BCH addresses added to SDN
- Martinus Pterus Henri De Koning (Dutch) — co-operator of darknet fentanyl businesses with Peijnenburg
- Matthew Simon Grimm — registered owner of Smokeyschemsite.com; 2 ETH, 26 BTC, 2 BCH addresses added to SDN

### Entities (9)
Various shell companies registered in the Netherlands and UK used to facilitate drug traffic and money movement. Individual company names not captured in cross-cite.

### Context
First use of E.O. 14059 to target online/darknet drug suppliers. Chainalysis identified "thousands of additional addresses" associated with these actors beyond the SDN list entries.

## Circle response (2022-11-10 / 2022-11-11)

On 2022-11-10 (ethereum) and 2022-11-11 (avalanche), Circle blacklisted 53 addresses — the same 53 on both chains. These 53 include a mixture of:
1. Peijnenburg's 7 ETH addresses (already OFAC-attested)
2. Grimm's 2 ETH addresses (already OFAC-attested)
3. Addresses from Tornado Cash redesignation on 2022-11-08
4. Additional Peijnenburg/Grimm/De Koning addresses that Circle independently traced but that our current OFAC XML snapshot only partially captures (likely due to our snapshot containing only a subset of the full list)

## Integrity

SHA256 of this file recorded in sources.csv. Direct fetch of the Treasury press releases was blocked in this environment; content reconstructed from cross-verified WebSearch snippets (Chainalysis, Treasury, Elliptic, Global Sanctions, Mr. Watchlist).
