# Paid-package license decision approved — September 26, 2026

The owner explicitly approved the existing Zipper Tools commercial/proprietary
terms for newly released SQLAlchemy and Pydantic paid packages. No prices,
refunds, privacy terms, or public scanner licenses are changed.

Version 0.1.2 uses `LicenseRef-ZipperTools-Commercial` and includes the existing
`legal/license-terms.md` in each wheel. The package-wide MIT declaration has been
removed from these new paid distributions only. The terms expressly preserve
rights already granted in previously distributed MIT copies.

## Scope and notices

The inspected paid source inventories contain Zipper Tools engines, fixtures,
and documentation, with no vendored dependency implementation identified. Git
history for these engines lists only the owner's three existing identities
(Derek Martin's GitHub identity, thurs, and Zipper Tools). No contributor-owned
material with unclear relicensing rights was identified in that inspection.
This is repository provenance evidence, not an independent legal ownership audit.

LibCST 1.9.0 and tomli 2.4.1 license texts are preserved byte-for-byte from their
installed distributions under `legal/third-party/`. Their copyright and license
terms remain in force; those dependencies are installed separately, not
relicensed or bundled as Zipper Tools implementations. Wheel metadata and all
three license files were checked against the source bytes for both packages.

## Artifact evidence

Original ZIPs and pristine extractions remain locally under ignored
`test_runs/release-evidence/delivered-original/`; original KV keys are untouched.

| Artifact | SHA-256 |
| --- | --- |
| Original SQLAlchemy | `1cc26e33b0b0cf759d3e4bff8575bf526dbfa9211d4a76c947c1dc30e9aed059` |
| Original Pydantic | `075315372912a1d890418b1c1a377062e6bc3d62cfb991301888f52d90d49bfc` |
| SQLAlchemy v0.1.2 | `1df2ff9e11bae92406e9d3ffea8322f4a96208f0cdc4edf9c1f149abcca6a959` |
| Pydantic v0.1.2 | `81fe8b2978caafab07db1e8d13dfaeabfb1a863d57cbb1b4c594cfc160ef3ea9` |

New private source candidates are under ignored
`private_products/release-2026-09-26/`. New immutable KV artifact keys are
`sa20-pack-edge-case-pack-v0.1.2.zip` and `pydantic-v2-porter-v0.1.2.zip`.
Only the new Worker selects these keys. Rolling back the Worker restores the
old mappings without overwriting or deleting any original ZIP.

Both built wheels passed metadata/license validation. Private suites: SQLAlchemy
11 passed, Pydantic 12 passed. The exact delivered ZIPs installed cleanly on
Python 3.10, 3.11, 3.12, 3.13, and 3.14, with unchanged previews, supported sample
rewrites, and executable resulting samples. SQLAlchemy distinguishes skipped
checks (`validation_not_run`) from a successfully executed validation command.

Do not use the historical v0.1.0 defaults in `scripts/release_bundles.py` to
recreate this release. Its source paths remain historical. The versioned sources,
ZIP hashes, and wheel license files above identify this release unambiguously.
