# AGENTS.md

## Operating authority

`docs/master-operating-directive.md` is the current owner directive. It takes
precedence over older strategy and session notes below. Prioritize trust and
purchasing defects, then one verified customer journey. Keep internal Product
Well strategy out of purchasing paths. Preserve the directive's explicit owner
approval boundaries for prices, policies, licenses, and consequential external
actions. Historical commercial-ready claims below are not current launch proof.

## Mission

Build a zero-cost, repo-native autonomous product-well engine for self-serve
developer tools. Each product should turn a fresh deadline, deprecation, policy
shift, compliance requirement, or recurring operational breakage into a local
scanner/remediator that produces a useful artifact without emails, meetings,
custom setup, or manual fulfillment.

The standing product shape is:

- local-first input: repo, workflow YAML, manifest, lockfile, app bundle,
  package config, container, or source tree
- deterministic rules first: static analysis, parsing, patch synthesis,
  validation, and confidence scoring before any optional LLM help
- autonomous output: patch set, HTML/JSON report, CI gate, submission bundle,
  compliance dossier, or manager-readable risk summary
- no trust cliff: no source upload, no production credentials, no required paid
  API, no human delivery path
- fail closed: uncertain cases become explicit findings, not guessed fixes
- verification loop: never claim success until local checks for that product
  pass

## Current Decision

- Strategy source of truth: `Autonomous Product Wells for a Solo Developer.docx`.
- New operating model: Zipper Tools is a portfolio of autonomous product wells,
  not a single SQLAlchemy migration-product bet.
- Active new wells: GitHub Actions Upgrade Guard, Python 3.14 Readiness Pack,
  Apple Privacy Manifest Composer, CRA Evidence Builder, ESLint v10 Migration
  Radar, and Package Publisher Hardening Pack.
- First buyer promise: scan deadline-sensitive software repos and emit
  source-linked findings, safe patch previews, and business-readable reports
  without hosted services or source upload.
- Existing SQLAlchemy, Pydantic, and ESLint/flat-config assets stay useful as
  portfolio proof and legacy search assets, but SQLAlchemy is no longer the
  growth bottleneck or primary build target.
- Monthly front-page motion: publish a current "Product Well of the Month",
  archive past wells, and promote only wells that show real demand through
  downloads, scans, checkout intent, or direct buyer conversations.

## Evidence Status

- Official docs reviewed:
  - GitHub Actions changelog items around artifact, cache, runner image, and
    Node runtime deprecations
  - Python 3.14 porting notes and Pydantic Python 3.14 compatibility updates
  - Apple privacy manifest and required-reason API guidance
  - EU Cyber Resilience Act timeline and evidence requirements
  - SQLAlchemy 2.0 migration guide
  - SQLAlchemy declarative mapping docs
  - ESLint flat-config migration guide and migrator announcement
  - Tailwind CSS v4 upgrade guide and v4 launch post
  - Pydantic v2 migration guide and bump-pydantic repo
  - GitHub Pages limits
  - Cloudflare Pages docs and Cloudflare Web Analytics docs
  - Lemon Squeezy getting-paid, payments, fees, and supported-countries docs
  - SBA business-structure and EIN guidance
  - IRS EIN guidance
  - Oregon business registration, assumed-business-name, and license-directory pages
  - FTC advertising and endorsement guidance
  - USPTO trademark search guidance
  - FinCEN BOI toolkit
- Public issue/discussion signal reviewed:
  - SQLAlchemy migration discussion examples
  - Tailwind upgrade issues/discussions
  - Pydantic V2 issue examples
- Install-base proxies reviewed:
  - GitHub platform scale and GitHub Actions ecosystem pressure
  - `sqlalchemy` and `pydantic` PyPI download stats
  - `tailwindcss` npm package page
  - `eslint` npm dependents/package metadata

## Constraints

- Startup cost must remain exactly $0.
- No paid API, hosting, ads, datasets, or dev tools.
- Everything must live in a normal repository workflow.
- Deterministic transforms first; uncertain cases go to manual review.
- Every code/doc change is only "done" after local verification succeeds.

## Planned Repo Shape

- `docs/`
  - `autonomous-product-wells.md`
  - `product-wells-todo.md`
  - `market-selection.md`
  - `product-spec.md`
  - `pricing.md`
  - `launch-posts.md`
  - `demo.md`
- `products/actions-upgrade-guard/`
  - CLI
  - GitHub Actions workflow parser
  - rule-pack engine
  - patch synthesizer
  - report generator
  - fixture repos
- `products/python-314-readiness/`
  - CLI
  - Python metadata/source/workflow scanner
  - Python 3.14 readiness rule pack
  - CI matrix patch synthesizer
  - JSON/HTML report generator
  - proof fixtures
- `products/apple-privacy-manifest-composer/`
  - CLI
  - required-reason API scanner
  - third-party SDK detector
  - PrivacyInfo.xcprivacy parser and candidate generator
  - JSON/HTML report generator
  - proof fixtures
- `products/cra-evidence-builder/`
  - CLI
  - CRA evidence-readiness scanner
  - safe template generator
  - JSON/HTML dossier generator
  - proof fixtures
- `products/eslint-v10-radar/`
  - CLI
  - ESLint v10 blocker scanner
  - simple script-flag patch synthesizer
  - JSON/HTML report generator
  - proof fixtures
- `products/package-publisher-hardening/`
  - CLI
  - npm/PyPI publisher workflow scanner
  - OIDC permission patch synthesizer
  - JSON/HTML report generator
  - proof fixtures
- `src/sa20_pack/`
  - CLI
  - codemods
  - validation runner
  - report generator
  - fixture support
- `tests/`
- `fixtures/`
- `.github/actions/sa20-pack/`
- `.github/workflows/`

## Verification Standard

The repo should support:

- format/lint
- typecheck
- tests
- package build

And the migration runner itself should produce a structured report showing:

- files changed
- transforms applied
- unsupported/manual-review findings
- validation command results
- overall confidence

New autonomous products should also produce:

- input files scanned
- rule-pack version
- deadline/policy source for each finding
- fixability classification: autofix, manual review, blocked, or informational
- generated patches or explicit "no safe patch" notes
- HTML summary for humans and JSON output for CI
- exit-code behavior documented and tested

## Session Notes

- Workspace started empty and not yet initialized as a git repository.
- Python 3.12.10 is available.
- Node 22.11.0 is available.
- `uv` is not installed.
- `npm` works through `npm.cmd`.
- `mypy 1.20.0` crashed the interpreter on this machine; pinning to
  `mypy 1.11.2` fixed that.
- Windows filesystem permissions in this workspace caused repeated temp/cache
  failures. The validation runner now redirects temp, bytecode, and cache paths
  into repo-local scratch directories.

## Current State

- `Autonomous Product Wells for a Solo Developer.docx` is now the strategic
  source of truth for product direction.
- `docs/autonomous-product-wells.md` summarizes the new doctrine, scoring model,
  portfolio map, and monthly well cycle.
- `docs/product-wells-todo.md` is the active execution checklist for pivoting
  the repo, site, and first new product toward the autonomous product-well
  framework.
- SQLAlchemy showed traffic but almost no paid intent; keep it live as proof,
  not as the flagship growth bet.
- GitHub Actions Upgrade Guard is now the first new well implementation.
- Python 3.14 Readiness Pack is now the second new well implementation.
- `docs/market-selection.md` completed with rubric, scorecard, and decision.
- `docs/product-spec.md` completed.
- `docs/max-revenue-todo.md` completed as the working revenue roadmap.
- `docs/product-ideas.txt` is the rolling tracker for future product candidates,
  filtered against the strict downloadable/autonomous/no-human-in-the-loop
  constraint.
- `docs/commercial-benchmark.md` is the product go / no-go bar. A product is
  not commercially ready until it is strong enough for a buyer to justify real
  budget to a manager.
- `docs/paid-product-checklist.md` is the release gate for every paid pack:
  boss-approval, scope, leak-prevention, commerce, verification, and
  compliance all have to pass.
- Commercial delivery artifacts are now kept outside the tracked public tree so
  the repo can stay scanner-first.
- `docs/public-proof.md` and `docs/commercial-case.md` now exist for the root
  SQLAlchemy product.
- `products/flatconfig-lift/` now exists as the second product subproject, with
  its own CLI, fixtures, tests, and product spec.
- `products/flatconfig-lift/docs/public-proof.md` and
  `products/flatconfig-lift/docs/commercial-case.md` now document public-proof
  evidence and the buyer case for the static-config subset.
- `products/pydantic-v2-porter/` now exists as the third product subproject,
  with deterministic validator/config/settings rewrites, fail-closed findings,
  and a 12-test fixture suite.
- `products/pydantic-v2-porter/docs/commercial-case.md` now exists beside the
  existing public-proof doc, so the first three products all have a
  boss-readable budget case and explicit "do not buy this if" boundaries.
- `docs/max-revenue-todo.md` now also contains the detailed go-live checklist
  for website hosting, payments, payout access, analytics, and legal readiness.
- Static storefront pages now exist under `site/` with config-based checkout
  links, success/cancel pages, policy page, and Cloudflare analytics hook.
- The storefront now also has issue-shaped landing pages and product-detail
  pages, plus a sitemap and canonical tags, so organic discovery can target
  exact supported upgrade problems instead of relying only on the homepage.
- The public storefront has been polished and pushed live on GitHub Pages.
- GitHub Pages should now redirect to the canonical Cloudflare storefront so
  public traffic does not split across two different site experiences.
- `wrangler.jsonc` now exists so the same storefront can be deployed through
  Cloudflare without re-entering static asset settings by hand.
- `site/config.js` is now populated with the current seller name, contact email,
  and public GitHub repo URL.
- Stripe Checkout is now the active checkout direction for new orders, driven
  by the Cloudflare Worker instead of external product pages.
- Store-product copy, fulfillment docs, release checklist, repo-fit checklist,
  preset-bundle checklist, legal checklist, lead tracker, and launch log now
  exist.
- Claims-and-safeguards docs now exist, and the public/legal copy has been
  tightened to avoid broad guarantees.
- `site/config.js` now points the storefront at tracked `/go/...` routes for
  Stripe-controlled checkout:
  - `/go/sa20-pack`
  - `/go/sa20-preset`
  - `/go/pydantic-v2-porter`
  - `/go/fit-report`
- Repo launch/legal docs now exist for deployment, company setup, policies, KPI
  tracking, and launch readiness.
- `sa20_pack.launch_readiness` now checks for missing launch assets and
  placeholder values in `site/config.js`.
- Core CLI, transforms, validation runner, reporting, and fixtures are working.
- Demo fixture migrates from failing pre-state to passing post-state.
- Generated demo artifacts live under `artifacts/`.
- GitHub Action wrapper and CI workflow are scaffolded.
- `flatconfig-lift` is now scaffolded under `products/flatconfig-lift` with:
  - deterministic static-config discovery
  - `eslint.config.cjs` generation through `FlatCompat`
  - ignore-pattern migration for simple cases
  - fail-closed findings for JS configs, multiple sources, and negated ignores
  - its own README, AGENTS file, fixtures, tests, and compile-based build check
- `pydantic-v2-porter` is now scaffolded under `products/pydantic-v2-porter`
  with:
  - deterministic rewrites for direct `pydantic` / `pydantic.v1` imports
  - `BaseSettings` move to `pydantic_settings`
  - safe `Config` -> `model_config` conversion with key renames
  - strict `validator` / `root_validator(pre=True)` / `validate_arguments`
    decorator rewrites
  - fail-closed findings for alias imports, removed config keys, post root
    validators, and signature-heavy validators
  - its own README, AGENTS file, fixtures, tests, and compile-based build check
  - a public proof pass documented in
    `products/pydantic-v2-porter/docs/public-proof.md`
- The first three products now meet the commercial benchmark for their
  documented supported subsets:
  - `sa20-pack` for the SQLAlchemy patterns in `docs/product-spec.md`
  - `flatconfig-lift` for static JSON/YAML ESLint configs
  - `pydantic-v2-porter` for the documented validator/settings/config subset
- The tracked public repo is now being split into community scanners only so
  public GitHub establishes trust without exposing the full commercial apply
  engines.
- Discovery is the active bottleneck. The daily control room now lives in
  `docs/traffic-war-room.md`, with priority URLs, Search Console fields,
  decision rules, and the current 1000 qualified visits/day gap.
- `https://zippertools.org/proof/sqlalchemy-public-proof/` is now live as the
  SQLAlchemy trust asset, linked from the homepage, README, SQLAlchemy product
  page, and SQLAlchemy exact-problem pages.
- `scripts/audit_site_urls.py` and `tests/test_site_url_audit.py` now guard
  sitemap URLs, clean canonicals, and internal links so redirect-related Search
  Console rejection issues are caught before resubmission.
- As of 2026-04-16, the updated site has been deployed through Cloudflare
  Worker version `3a69b325-0b4d-40e9-b9b0-e081dc9227bd`, IndexNow submission
  has run, and the local site URL audit, live URL audit, and full pytest suite
  pass.
- `scripts/cloudflare_traffic_snapshot.mjs` now reads Cloudflare GraphQL
  analytics from environment variables and reports total page views, qualified
  guide/product/proof visits, and `/go/...` checkout requests.
- The 2026-04-16 21:24 PDT Cloudflare snapshot showed `1173` page views and
  `942` qualified visits in the prior 24 hours; checkout intent was still thin
  at `5` `/go/...` requests.
- The 2026-04-16 22:22 PDT Cloudflare snapshot showed `1446` page views and
  `1311` qualified visits in the prior 24 hours; the raw traffic goal is now
  crossed in Cloudflare, but checkout/free-scan intent remains the active
  bottleneck at `4` `/go/...` requests.
- Product-to-intent tracking has been repaired: static homepage/pricing CTAs
  now route through `/go/free-scan`, `/go/sa20-pack`, `/go/sa20-preset`, and
  `/go/pydantic-v2-porter`; SQLAlchemy pages use the tracked free-scan route;
  product pages now lead with a narrow decision block and tracked buy/proof
  links.
- The Cloudflare storefront now uses a Worker wrapper instead of static assets
  only, so Stripe Checkout Sessions and signed webhook handling can run from
  runtime secrets. Stripe webhook setup notes live in `docs/stripe-checkout.md`.
- GitHub repo About is now updated with the `https://zippertools.org/` website,
  narrow scanner-first SQLAlchemy migration description, and exact-intent
  migration topics.
- GitHub release `v0.1.0` now exists for the public scanner/discovery baseline:
  `https://github.com/zippertools/sqlalchemy-14-to-20-codemod/releases/tag/v0.1.0`.
- `products/actions-upgrade-guard/` now exists with a local CLI, deterministic
  GitHub Actions workflow scanner, JSON/HTML reports, safe patch previews, an
  apply mode for narrow fixes, fixtures, tests, lint/type/build verification,
  and a product README.
- `products/python-314-readiness/` now exists with a local CLI, Python
  metadata/source/workflow scanner, Python 3.14 rule pack, JSON/HTML reports,
  safe CI matrix patch preview/apply mode, proof fixtures, tests, product spec,
  public proof doc, commercial case, lint/type/build verification, and a wheel
  build through Hatchling.
- `docs/ranks-3-6-product-task-list.md` now tracks the completed build ledger
  for ranks 3 through 6 from the product-wells paper.
- `products/apple-privacy-manifest-composer/` now exists with a local CLI,
  required-reason API scanning, listed-SDK detection, PrivacyInfo.xcprivacy
  parsing, candidate manifest generation, JSON/HTML reports, proof fixtures,
  tests, product spec, public proof doc, commercial case, lint/type/build
  verification, and a wheel build through Hatchling.
- `products/cra-evidence-builder/` now exists with a local CLI, CRA
  evidence-readiness scanner, missing-template generation, JSON/HTML dossier,
  proof fixtures, tests, product spec, public proof doc, commercial case,
  lint/type/build verification, and a wheel build through Hatchling.
- `products/eslint-v10-radar/` now exists with a local CLI, ESLint v10 blocker
  scanner, simple package-script patch preview/apply mode, JSON/HTML reports,
  proof fixtures, tests, product spec, public proof doc, commercial case,
  lint/type/build verification, and a wheel build through Hatchling.
- `products/package-publisher-hardening/` now exists with a local CLI, npm/PyPI
  publishing workflow scanner, OIDC permission patch preview/apply mode,
  JSON/HTML reports, proof fixtures, tests, product spec, public proof doc,
  commercial case, lint/type/build verification, and a wheel build through
  Hatchling.

## Next Steps

1. Build the Product Wells site frame: homepage "Well of the Month", `/wells/`
   archive, active product page, proof page, and legacy SQLAlchemy archive path.
2. Add product/proof pages for the six new Product Wells:
   GitHub Actions Upgrade Guard, Python 3.14 Readiness Pack, Apple Privacy
   Manifest Composer, CRA Evidence Builder, ESLint v10 Migration Radar, and
   Package Publisher Hardening Pack.
3. Produce public proof pages showing before files, command, generated report,
   generated patch, and fail-closed findings for both new wells.
4. Add route/click analytics that can distinguish well-page visits, free-scan
   clicks, product-page clicks, and paid checkout intent.
5. Run exact-fit demand tests for the six new wells before adding paid checkout
   scope.
6. Keep SQLAlchemy/Pydantic/flatconfig pages available as proof/archive assets,
   but stop adding product scope unless real demand appears.
7. Review the product-well board monthly and promote, pause, or kill wells by
   evidence, not by how interesting they are to build.
