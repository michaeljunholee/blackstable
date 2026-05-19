# OFAC SDN raw data

Raw OFAC sanctions data used to reconcile blacklisted on-chain addresses
against US Treasury designations.

## sdn_advanced.xml — fetched on demand, not committed

The `sdn_advanced.xml` file (the OFAC SDN Advanced list) is published by
the US Treasury at:

> https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML

It is **not** committed to this repository (file is ~118 MB and updates
frequently — see `.gitignore`). To reproduce the OFAC reconciliation
locally, download it once:

```bash
curl -L -o data/raw/ofac_sdn/sdn_advanced.xml \
  https://sanctionslistservice.ofac.treas.gov/api/PublicationPreview/exports/SDN_ADVANCED.XML
```

## Derived files (committed)

- `ofac_crypto_addresses.csv` — every digital-currency address extracted
  from the SDN list (regardless of chain/asset).
- `ofac_matches.csv` — intersection of `ofac_crypto_addresses.csv` with
  the blacklisted addresses observed on Circle's USDC contract. Each row
  is one match between an on-chain freeze target and an SDN entry.

Both derived files are produced by the OFAC reconciliation step of the
pipeline; see `scripts/utils/` for the parsing logic.
