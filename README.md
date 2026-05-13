# Stablecoin Blacklisting — Research Dataset and Dashboard

A reproducible, cited dataset of every freeze (`BLACKLIST`) and unfreeze
(`UNBLACKLIST`) action that stablecoin issuers have executed on user
balances, traced from the on-chain transaction to the public legal or
regulatory event behind it. Initial coverage is Circle's USDC across six
EVM chains, 2020-06 to 2026-04; the schema is issuer-agnostic and is
being extended to Tether's USDT.

The animating question is whether issuers' *stated* policies — typically
"we freeze only on a binding legal request" — match their *actual*
on-chain behavior, and whether enforcement correlates with a
counterparty's commercial relationship to the issuer.

## Dashboard

The interactive dashboard is published at:

**`https://<deploy-target>/`** *(URL added once hosting is live)*

It includes a brushable bubble timeline, multi-select reason filters,
per-cluster detail cards, and right-rail breakdowns by reason mix,
largest events, and year.

## Dataset at a glance

| Table | Rows | Notes |
|---|---|---|
| `actions.csv` | 2,922 | One row per on-chain BL/UB event |
| `implementations.csv` | 2,922 | 1:1 with actions; carries tx_hash, block, chain, function called |
| `entities.csv` | 60 | Sanctioned parties, organizations, individuals |
| `triggers.csv` | 55 | Legal/regulatory causes |
| `incidents.csv` | 5 | Real-world events (hacks, sanctions waves) |
| `sources.csv` | 40 | Primary and secondary sources, archived |
| `action_sources.csv` | 2,469 | Audit trail linking actions to sources |
| `policies.csv` | 20 | Circle privacy-policy versions over time |

Date range: **2020-06-16 → 2026-04-15.** Chains: Ethereum, Base,
Polygon, Avalanche, Arbitrum, Optimism. Attribution coverage to a public
trigger is roughly 85% of BL events and 84% of UB events.

## Methodology and limitations

- [`docs/schema.md`](docs/schema.md) — field-by-field data dictionary
- [`docs/sourcing-standards.md`](docs/sourcing-standards.md) — how sources are
  selected, archived, and cited
- [`docs/relationship-criteria.md`](docs/relationship-criteria.md) — the
  rubric used to classify entity ↔ issuer relationships
- [`docs/completeness-map.md`](docs/completeness-map.md) — what is
  exhaustive, what is best-effort, what is out of scope per chain × era
- [`docs/known-gaps.md`](docs/known-gaps.md) — chains, eras, and
  mechanisms we know are under-covered, and why

The project applies conservative defaults: when evidence is insufficient
for `HIGH` confidence the row is marked `LOW`; when an entity's
relationship to the issuer is not documented it is classified `MAYBE`
rather than assumed.

## Reproducibility

```bash
# 1. Install
uv pip install -e ".[dev]"        # or: pip install -e ".[dev]"

# 2. Configure API keys
cp .env.example .env              # then set DUNE_API_KEY and ETHERSCAN_API_KEY

# 3. Run the pipeline
python scripts/01_normalize_onchain.py   # fetches on-chain BL/UB events
python scripts/02_archive_policies.py    # snapshots issuer policy pages to the Wayback Machine
python scripts/99_validate.py            # schema and referential-integrity checks

# 4. Build the dashboard
python scripts/03_build_html.py          # emits docs/dashboard/

# 5. Run the test suite
pytest tests/ -q                          # 116 tests
```

A pre-commit hook at `.git-hooks/pre-commit` runs the validator on
every commit that touches `data/*.csv`. Activate it once per clone:

```bash
git config core.hooksPath .git-hooks
```

## Citation

> Lee, M. *Stablecoin Blacklisting: A Research Dataset and Dashboard.*
> 2026. Available at: *(URL once deployed)*.

If you use the dataset in academic work, please cite the version (commit
hash) you used.

## License

Released under the MIT License — see [`LICENSE`](LICENSE).

The dataset itself is a record of *publicly observable* on-chain
transactions and *publicly cited* legal events. Where individual notes
flag claims as `LOW` confidence or `MAYBE`, treat them as such.

## Contributing

Issues and PRs are welcome — particularly:
- Cross-chain validation against the same on-chain queries
- Attribution leads for events currently in the "no public reason"
  category
- Corrections to specific cited claims (please include a primary source)

There is no formal contributor agreement; the MIT license covers
contributions.
