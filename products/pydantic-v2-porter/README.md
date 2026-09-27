# pydantic-v2-porter

`pydantic-v2-porter` is the public trust layer for a narrow, high-frequency
subset of the Pydantic v1 to v2 upgrade path: a free repo-fit scanner plus
buyer proof for the commercial migration pack.

It is intentionally narrow:

- supports direct `from pydantic import ...` imports
- supports direct `from pydantic.v1 import ...` imports
- detects only safe validator, settings, and config patterns
- leaves unsupported files untouched and reports why

## What the public repo does

- detects `pydantic.v1` imports, `BaseSettings`, safe nested `Config` classes,
  supported validators, root validators, and bare `@validate_arguments`
- emits a machine-generated report with findings and notes

The commercial pack performs the supported rewrites and ships as the paid ZIP.

## What it does not do

- promise a full automatic Pydantic v2 migration
- evaluate ambiguous decorator signatures
- rewrite alias-heavy or attribute-based import styles
- silently guess through removed config keys

## Who This Is For

- teams upgrading a Pydantic v1 codebase to v2
- repos whose free scan shows direct imports plus the supported validator,
  settings, and config subset
- engineers who want deterministic fit assessment first and explicit follow-up
  for the risky files

Run the free scan first. This product is strongest when most findings fall
inside the supported validator and settings patterns.

## Do Not Buy This If

- the repo leans heavily on alias-heavy imports or `import pydantic` attribute
  access
- validator signatures depend on `values`, `field`, `config`, `each_item`, or
  `always`
- you need a promise that every Pydantic v1 file will auto-migrate

## Quickstart

Install from the public GitHub repo subproject and scan a local checkout:

```bash
python -m pip install "https://github.com/zippertools/sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip#subdirectory=products/pydantic-v2-porter"
python -m pydantic_v2_porter.cli path/to/repo --report migration-report.json
```

If installation fails, retry from the GitHub quickstart or contact support at
support@zippertools.org.

The public repo always runs in scan mode. `--apply` is reserved for the
commercial pack.

## Verification

```bash
python -m ruff check .
$env:PYTHONPATH='src'; python -m mypy src tests
$env:PYTHONPATH='src'; python -m pytest
$env:PYTHONPATH='src'; python -m pydantic_v2_porter.build_runner
```

## Exit codes

- `0`: preview completed without unsupported findings
- `1`: blocked
- `2`: unsupported findings require follow-up

## Proof And Buyer Docs

- [Public proof](docs/public-proof.md)
- [Commercial case](docs/commercial-case.md)
- [Demo summary artifact](demo-report.json)
