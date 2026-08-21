# OFAC SDN raw data

Raw OFAC sanctions data used to reconcile blacklisted on-chain addresses
against US Treasury designations.

## sdn_advanced_<date>.xml — fetched on demand, not committed

The SDN Advanced list (`SDN_ADVANCED.XML`) is published by
the US Treasury at:

> https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML

It is **not** committed to this repository (file is ~118 MB and updates
frequently — see `.gitignore`). To reproduce the OFAC reconciliation
locally, download it once:

```bash
curl -L -A "Mozilla/5.0" -o data/raw/ofac_sdn/sdn_advanced_2026-08-20.xml \
  https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML
```

## Derived files (committed)

Snapshots are dated by the list's `DateOfIssue` so successive runs never
overwrite each other (`2026-04-19`, `2026-08-20`, …):

- `ofac_crypto_addresses_<date>.csv` — every digital-currency address on
  the SDN list (any chain/asset) with its owning party, programs and
  listing date, plus `evm_key`: the 20-byte key for 0x-hex identifiers and
  for TRON base58 identifiers (a TRON address is `base58check(0x41 ‖ key)`;
  the key is the account's address on every EVM chain).
- `ofac_matches_<date>.csv` — one row per blacklist/unblacklist action
  whose target key matches an SDN identifier; `match_basis` records
  whether the SDN carried the key as `HEX_IDENTIFIER` or via
  `TRON_KEY_EQUIVALENCE`, and `ofac_listed_address` the printed form.

Both are produced by `scripts/04_ofac_sdn.py --xml <snapshot> --extract --match`.
