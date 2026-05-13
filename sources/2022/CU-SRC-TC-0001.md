# Source — CryptoSlate: Circle blacklists Tornado Cash ETH addresses

**URL:** https://cryptoslate.com/circle-blacklists-all-tornado-cash-eth-addresses-effectively-freezing-usdc/
**Publication date:** 2022-08-08
**Publisher:** CryptoSlate

## Cross-verifying source: LRQA Cyber Labs

**URL:** https://www.lrqa.com/en/cyber-labs/how-circle-banned-tornado-cash-users/

## Key facts attested by both sources

- OFAC designated Tornado Cash on 2022-08-08 (citing $7 billion laundering, including $455M linked to Lazarus Group).
- Circle blacklisted 38 wallet addresses on 2022-08-08 alone.
- Balances on blacklisted addresses ranged from 0 to 71,000 USDC.
- Total USDC frozen: approximately $81,000.
- Mechanism: addresses added to USDC's FiatTokenV2 blacklist via the `Blacklisted` event.

## Critical industry context (from web search)

- **Tether** publicly criticized Circle's move as "premature" — arguing that proactive blacklisting without explicit US authority instructions sets a concerning precedent. Tether itself declined to blacklist Tornado Cash addresses without a formal request.
- Circle did NOT publish a contemporaneous statement justifying the specific addresses chosen; the action was detected by on-chain observers.

## Implication for research

Whether the 38 addresses blacklisted on 2022-08-08 match OFAC's explicit SDN list (and whether additional events on 2022-08-09 extend beyond OFAC) is a key data point for the policy-vs-practice gap analysis.
