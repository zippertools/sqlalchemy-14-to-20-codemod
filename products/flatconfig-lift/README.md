# flatconfig-lift

`flatconfig-lift` is the public trust layer for a narrow ESLint migration:
a free repo-fit scanner for static legacy configs plus buyer proof for the
commercial flat-config pack.

It is intentionally narrow:

- supports static `.eslintrc` JSON/YAML-style configs
- supports `package.json` `eslintConfig`
- fails closed on JS configs with logic
- writes a machine-generated report

## What the public repo does

- discovers one supported legacy ESLint config source
- reads the legacy config as structured data
- emits a report with findings and manual TODOs

The commercial pack generates `eslint.config.cjs`, carries over supported
ignore patterns, and includes the packaged rollout materials.

## What it does not do

- evaluate `.eslintrc.js` logic
- guarantee a fully working ESLint v9 setup for every plugin ecosystem
- silently guess through ambiguous configs

## Who This Is For

- teams migrating from static `.eslintrc*` files or `package.json`
  `eslintConfig`
- repos that want a fast fit check before buying a generated
  `eslint.config.cjs` bridge
- engineers who want a clear stop signal on JS configs or already-existing flat
  configs

Run the free scan first. This product is strongest when the source config is
plain JSON or YAML data and the report shows the repo is inside supported
scope.

## Do Not Buy This If

- the repo uses `.eslintrc.js`, `.cjs`, or `.mjs`
- the repo already has `eslint.config.*`
- you want a tool that executes config logic or guesses through plugin-specific
  edge cases

## Quickstart

Install from the public GitHub repo subproject:

```bash
python -m pip install "https://github.com/zippertools/sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip#subdirectory=products/flatconfig-lift"
```

Then scan a local checkout:

```bash
python -m flatconfig_lift.cli path/to/repo --report migration-report.json
```

The public repo always runs in scan mode. `--apply` is reserved for the
commercial pack.

## Verification

```bash
python -m ruff check .
$env:PYTHONPATH='src'; python -m mypy src tests
$env:PYTHONPATH='src'; python -m pytest
$env:PYTHONPATH='src'; python -m flatconfig_lift.build_runner
```

## Exit codes

- `0`: preview completed without unsupported findings
- `1`: blocked
- `2`: unsupported findings require follow-up

## Proof And Buyer Docs

- [Public proof](docs/public-proof.md)
- [Commercial case](docs/commercial-case.md)
- [Demo summary artifact](demo-report.json)
