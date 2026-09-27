# Release audit — September 26, 2026

## Production result

**Deployed September 26, 2026 (America/Los_Angeles).** Production source commit:
`361bd400caed99f9085f6ba15990666195fb5b4d`. Public scanner tag `v0.1.2` points to
`00595bc3db8283f4eb519bdc773cbfea306a44a4`; the later commit updates publishing
and final site claims, not the installed scanner implementations.

Cloudflare Worker `sa20-pack` version:
`b1b8f436-e306-4fe6-8ad7-4ecee9a409c7`, serving existing `zippertools.org` and
`www.zippertools.org` targets. Wrangler uploaded 92 changed assets (195 scanned).
No DNS, account, binding, or secret changes were made.

After publishing, fresh **public GitHub archive** installs and scans passed on
Python 3.10, 3.11, 3.12, 3.13, and 3.14 for SQLAlchemy, Pydantic, and Action Guard.
The root archive URL is in the quickstart; subprojects use pip's `#subdirectory=`
fragment. Each was installed non-editably and run outside the source checkout.
No-supported-pattern fixtures produced `No supported findings detected.`
An empty Pydantic directory correctly reported `no-pydantic-targets`, so the
zero-finding check used a valid modern Pydantic source file instead.

GitHub Windows CI passed for production source; Linux release build/tests passed.
Initial release publishing collided with the pre-created release page after all
checks/builds succeeded. Publishing now uploads assets when the release exists;
workflow_dispatch rerun **36283462342 passed** and attached the public wheel,
sdist, and demo reports. Public paid source/ZIPs were not uploaded.

Post-deploy `python scripts/verify_live_funnel.py --skip-paid-routes` passed:
public page/slash/cache variants, homepage, pricing, product catalog, SQLAlchemy,
Pydantic, Action Guard product/proof, scanner guidance, policies, runtime assets,
13 tracked free routes, GitHub raw/API/rendered quickstarts, and retired paths.
`python scripts/audit_site_urls.py --live` also passed. Live browser pricing
showed $99/$299.99/$149.99/$249.99 and no expired sale. Success/cancel returned
200, delivery without session returned 400, direct paid asset access returned
404, and webhook status reports configured. Published catalog module, Action
Guard JSON, and patch-note bytes match the candidate.

The four live Stripe price objects were read again immediately before deployment:
active USD product identities and amounts match the catalog. No live checkout
session or payment was created. End-to-end fulfillment proof remains the four
real **test-mode** payments through the candidate Worker, signed forwarded
webhooks, remote KV, exact ZIP hashes, repeat download, and clean installation.
The production payment form and a live-mode paid download were deliberately not
tested. This distinction is not replaced by the public smoke checks.

Rollback remains Cloudflare version `895a399d-6943-4857-92d2-737b8182fb4f` and
Git tag `pre-release-2026-09-26`; the original artifact KV values are preserved.
The unrelated untracked DOCX remains untouched.


## Predeployment evidence (supersedes historical attempts below)

Owner approved commercial/proprietary licensing for new SQLAlchemy and Pydantic
paid packages. The inconsistency is corrected in v0.1.2; third-party texts and
prior MIT rights are preserved. See [license evidence](paid-license-decision-2026-09-26.md).

Predeployment gates passed locally: root 45 tests; eight product suites 64 tests;
paid suites 23 tests; repository Ruff; root/Action Guard/Pydantic MyPy; isolated
root and all eight product wheel builds; both private wheel metadata and license
text checks. Changed Python format checks and URL audit pass. The site builder
is byte-stable on repeat generation. Action Guard rules reviewed September 26
against primary GitHub sources, with no rules eligible for automatic edits.

Both exact replacement paid ZIPs passed fresh installs and customer sample
preview/apply/execution on Python 3.10.21, 3.11.16, 3.12.14, 3.13.15, and 3.14.7.
No development PYTHONPATH or editable installs were used. SQLAlchemy truth checks
prove skipped validation does not report success. Product tests prove narrower
supported fixtures, not all real repositories. Public archive installation will
be checked after publishing v0.1.2 and before Worker deployment.

Four real test-mode Stripe Checkout payments passed through the local candidate
Worker: unpaid delivery 402, paid ZIP 200, repeated recovery 200, success page
200, and four signed completion webhooks 200. Original 3-second webhook wait
was too short for the fourth event; a bounded 45-second wait passed. This is real
Stripe test API/CLI transport with the candidate Worker and remote KV, not the
hosted browser payment form or a live-mode payment. Stripe account
`acct_1TKBtaATQfsHIwbt`, profile `zippertools-sandbox`, livemode false throughout.
The final downloaded ZIP hashes match the license evidence exactly. Other two
artifacts remain byte-identical. Private packages are not included in Git.

Existing live Stripe product/price reads agree with unchanged catalog amounts:
$99 fit report, $299.99 SQLAlchemy, $149.99 presets, $249.99 Pydantic. No live
Checkout Session or customer transaction was created. Signed event receipt
itself does not grant access: delivery retrieves the paid session from Stripe.

Customer review: local browser rendered homepage, pricing, and SQLAlchemy page;
checked local scope, manual alternatives, prices, install commands, reports,
unsupported cases, delivery, and policy links. Removed remaining stale Action
Guard patch claims and free-transform claims. Sample numeric report/validation
blocks are explicitly illustrative. Historical SQLAlchemy proof no longer claims
application validation from the old all-skipped runner result. Public Pydantic
install and free-scan links now target the repaired subproject in this release.

Wrangler 4.141.0 dry-run passed with 195 assets, existing `sa20-pack` Worker and
PAID_ARTIFACTS binding. New v0.1.2 keys were staged without overwriting old KV
values. Existing Worker remains unchanged until the release below is deployed.

Rollback: current production Worker version re-read before release is
`895a399d-6943-4857-92d2-737b8182fb4f` (100%). Existing Git base is
`89861967378265fab5121b1ff245e2df0084d904`. A Git tag
`pre-release-2026-09-26` preserves that checkout; Cloudflare version is the
actual production rollback reference. Rollback command:
`npx.cmd --yes wrangler@4.141.0 rollback 895a399d-6943-4857-92d2-737b8182fb4f`.
Old artifact keys remain intact for that version. No DNS or bindings changed.

No real charges, refunds, subscriptions, customer messages, expenses, customer
data deletion, DNS changes, or unapproved price/policy changes were performed.
Hosted payment-form UI and a real production purchase are deliberately untested.

## Historical attempts (superseded)

# Operating directive: initial trust and purchasing repair

Status: release held for an owner decision on contradictory paid-package license
declarations; not deployed. Filesystem and Stripe sandbox access are now working.
The complete business operating test has not passed. The release-owner attempt
below supersedes the earlier local verification summary.

## Release-owner attempt â€” September 26, 2026

### Current result: sandbox verified, license decision pending

This section supersedes every earlier blocker statement below. See
[the concrete license decision](paid-license-decision-2026-09-26.md). An owner
question is pending; no license declaration was changed by assumption. Production
KV, Worker deployment, live Stripe configuration, prices, and policies were not
modified. No release commit/push or Git rollback tag was created.

#### Proven in this attempt

- Stripe profile `zippertools-sandbox` successfully selected test mode for
  `acct_1TKBtaATQfsHIwbt`. The account identity was retrieved and checked before
  testing. Existing live credentials were not used for payments.
- Four real Stripe test Checkout Sessions were created using the local Worker's
  normal catalog/body. Stripe's payment-page fixture mechanism completed test
  payments for 9900, 29999, 14999, and 24999 USD cents. All sessions had
  `livemode: false` and `payment_status: paid`.
- All four unpaid sessions initially returned delivery HTTP 402. Four signed
  `checkout.session.completed` events were forwarded by Stripe CLI to the local
  Worker and accepted. Paid delivery then returned HTTP 200 with the real ZIP
  contents read from existing production KV, without manual file fulfillment.
  ZIP integrity checks passed. Sizes: fit report 2459 bytes, SQLAlchemy 29141,
  presets 3735, Pydantic 23938. Byte sizes are evidence, not marketing claims.
- `scripts/audit_stripe_sandbox.mjs` preserves the repeatable test. It requires
  explicit test-mode selection, checks account identity and session livemode,
  and never writes production KV. Stripe API transport is adapted through the
  authenticated CLI; this is real Stripe test data, not a mocked Stripe response.
  Signed webhook handling runs in a local HTTP server. The deployed Worker and
  browser-hosted payment form were not exercised by this harness.
- Pristine copies of the delivered SQLAlchemy and Pydantic packages installed
  in fresh Python 3.12 environments. Preview left sample source unchanged;
  apply changed a supported sample, and the resulting code executed successfully.
  This is narrow fixture proof, not complete real-customer repository validation.
- The delivered fit-report script successfully read real scanner output and
  produced a `not_enough_signal` summary with a manual-work recommendation.
  The preset ZIP contains readable guidance/templates and no new apply engine.
- Action Guard installed non-editably and executed outside the checkout on
  Python 3.10.21, 3.11.16, 3.12.14, 3.13.15, and 3.14.7, each in a separate seeded
  environment without PYTHONPATH/development leftovers. The tested customer
  command is `python -m pip install ./products/actions-upgrade-guard`.
- Local root scanner installation and CLI loading passed on 3.10 and 3.12 after
  compatibility repair. Repaired private candidates also installed and loaded
  on 3.10 and 3.12. These repairs have NOT replaced the production ZIPs.

#### Repairs and rule evidence

- Rule pack `2026.09.26` is documented in
  [the rule review](../products/actions-upgrade-guard/docs/rule-review-2026-09-26.md).
  Primary GitHub sources were checked September 26. Node20 removal is September
  23, 2026; the obsolete June date was corrected. Floating-label findings no
  longer carry one misleading shared migration deadline.
- Artifact/cache tags alone do not establish GitHub.com versus GHES, runner
  requirements, shared artifact names, hidden-file behavior, or download
  compatibility. Their automatic edits were disabled; diagnostics and manual
  source guidance remain free. No current rule is eligible for auto-application.
  Tests verify unchanged bytes, including uncertain artifact/cache cases.
- HTML and CLI zero-findings output now says `No supported findings detected.`
  The readme states exact detection limits. Source-linked reports do not prove
  runtime compatibility; numeric confidence is not a safety probability.
- Action Guard proof now comes from actual scanner JSON. A test compares the
  published data with a fresh scan, normalizing only path/time. The site explains
  why no safe automatic patch is generated instead of advertising blanket fixes.
- Fixed Python 3.10 imports: datetime.timezone.utc instead of datetime.UTC;
  root/private SQLAlchemy use the conditional tomli backport for tomllib.
- Found a truth defect in delivered SQLAlchemy: all validation commands skipped
  still yielded `validated`. Root model and private candidate now report
  `validation_not_run`; tests cover empty/skipped/executed/failed checks. A
  private candidate run on 3.10 reported validation_not_run without commands and
  validated only after an actual configured command executed successfully.
- Fixed stale pricing documentation and dangerous deployment instructions that
  confused a `/test` tracking suffix with test-mode checkout. Production secrets
  must not be replaced to test. Success copy now says payment must be verified.
- Builder skips rewriting byte-equivalent text; this addressed repeated Windows
  failures while rebuilding unchanged sitemap/proof files. Second build was
  byte-identical across all site files. Existing source/generated ownership is
  preserved; the unrelated DOCX is untouched.

#### Latest validation

- Root pytest: **45 passed**.
- Eight product suites: **64 passed** total (Action Guard 12; Apple 7; CRA 6;
  ESLint radar 6; flatconfig 8; publisher 6; Pydantic 12; Python readiness 7).
- Whole-repository Ruff lint passed. Format checks passed for root src/tests/
  scripts and changed Action Guard src/tests. Root MyPy passed (25 source files);
  Action Guard MyPy passed (11 source files).
- Root and Action Guard isolated wheel builds passed. The other products were
  tested but their distribution builds were not rerun in this attempt.
- Local URL audit passed; generated-site repeat build byte comparison passed;
  Git diff whitespace check passed. Environment credential literal scan of the
  diff/new release docs/harness passed; it is not an exhaustive secret detector.
- Wrangler 4.141.0 dry-run passed against the existing configuration and KV
  binding, reading 195 assets. No new production target or DNS change occurred.
- Public baseline GETs returned 200 for homepage, pricing, catalog, Action Guard
  product/proof, scan, policies, success, and cancel. Delivery without a session
  returned 400; direct paid-asset access returned 404. These are checks of OLD
  production, not post-deployment proof of this candidate. No live checkout
  session/payment was created by these smoke checks.

Current production rollback candidate remains the observed Cloudflare version
`895a399d-6943-4857-92d2-737b8182fb4f`. No rollback was invoked.

#### Remaining and deliberately not performed

The immediate owner boundary is the MIT metadata versus commercial license
declarations in the actual paid ZIPs. After that decision, finish versioning and
packaging private repairs, verify exact replacement ZIPs through sandbox delivery,
and preserve original KV values for rollback. Publish the repaired public scanner
installation path and verify the resulting public artifact; local-source installs
do not establish that the old v0.1.1 download includes these fixes. Finish the
candidate audit, intended-diff/secret review, commit/push, deployment, and actual
post-deployment smoke tests only when those gates pass.

No real charge, refund, subscription, customer email, price/policy/license change,
customer-data deletion, DNS change, or production deployment was performed.
Original/private-candidate files are under ignored `test_runs/release-evidence/`;
they must not enter the public Git repository.

### Latest retry with unrestricted execution

This section supersedes the environment-blocker conclusions below. Filesystem
permissions and disk space now permit installation and authenticated Cloudflare
inspection. Production remains unchanged; no release commit or push was made.

**Current hard blocker:** Stripe CLI is authorized to `Piano man`
(`acct_1O4E2vC9QV0dn5V1`), not the documented Zipper Tools account
`acct_1TKBtaATQfsHIwbt`. Attempting
`stripe.exe switch acct_1TKBtaATQfsHIwbt --format json` returned
`Account acct_1TKBtaATQfsHIwbt not found in your authorized accounts`.
Both available Stripe environment credentials are live-mode. No correct-account
test credential was available in the environment or configured CLI profiles.
Testing an unrelated account would not prove Zipper Tools fulfillment. A live
charge is prohibited. Resume after authorizing the CLI for the Zipper Tools
sandbox or securely providing its test credential; do not paste keys into Git
or the audit. No credentials were displayed or rotated.

New proven evidence:

- Created a new, separate `test_runs/release-full-clean` virtual environment
  with Python 3.12.14. The documented
  `python -m pip install ./products/actions-upgrade-guard` path completed with
  build isolation and installed PyYAML. Its installed CLI scanned the clean
  fixture, emitted JSON/HTML, returned zero findings, and `pip check` passed.
  This proves Python 3.12 installation only, not the full declared >=3.10 range.
- Installed the development dependencies into `.venv` successfully.
- Root pytest: first run had the previously observed transient sitemap write
  error (41 passed, 1 failed); an unchanged rerun passed all 42 tests. The
  intermittent write failure remains a reliability observation, not erased proof.
- Action Guard tests: 7 passed using the development interpreter and product src.
- Ruff lint on `src tests scripts`: passed. MyPy: passed, 24 source files.
- Isolated wheel builds for root and Action Guard: both passed with
  `python -m build --wheel` (and the product directory argument).
- Local mocked Stripe checkout/delivery audit: passed for all four products.
  No actual sandbox checkout/payment/webhook/delivery was exercised.
- Read-only Stripe REST queries using the existing live environment credential
  returned the four documented Price IDs. Amounts are USD 9900, 29999, 14999,
  and 24999 cents for fit report, SQLAlchemy, presets, and Pydantic respectively,
  matching the repository's regular prices. This verifies catalog amounts,
  not production checkout or customer fulfillment.
- Wrangler 4.141.0 deployment listing succeeded. Latest existing production
  version is `895a399d-6943-4857-92d2-737b8182fb4f`, deployed May 15, 2026 UTC
  at 100%. This is an observed pre-release rollback candidate; no rollback was
  invoked, and no Git rollback tag was created.

The full Python support matrix, complete Action Guard rule review/safety repairs,
formatting gate, full portfolio validation, generated-site consistency, real
Stripe sandbox flow, delivered paid-artifact usability, production smoke tests,
and release-candidate audit remain incomplete. No all-gates-passed claim is made.
No real payment/refund/subscription, production mutation, customer communication,
price/terms change, or DNS change was performed. The untracked DOCX is untouched.

### Retry at 12:49 PDT

The owner repeated the release request. Disk space is now sufficient:
324,808,339,456 bytes free. The earlier low-space condition is resolved.
The current hard blocker is execution permissions, not disk capacity.

A new, separate `test_runs/release-retry-clean` environment was attempted with
Python 3.12.14 and new repository-local TEMP/TMP at
`test_runs/release-retry-temp`. Creation again failed during ensurepip. Running
ensurepip directly confirmed permission denied writing its bundled pip wheel in
the newly created temporary subdirectory, followed by access denied during
cleanup. Stripe CLI again failed to chmod its existing config with access denied.
The active session still disallows approval escalation and makes `.git` read-only.
No permissions, credentials, or sandbox controls were altered to bypass this.

No deployment, commit, push, or rollback reference was created. No new full-suite,
upstream-rule, Stripe transaction, or production verification is claimed by this
retry. Earlier narrow test evidence remains historical to the preceding attempt.
Existing work and the unrelated DOCX remain intact. Resume with an execution
profile that permits the required temporary-file operations, authenticated tools,
and Git writes; then rerun the gates rather than treating this retry as a pass.

Production was not deployed. No commit, push, or production rollback reference
was created because prerequisite gates failed. Starting repository HEAD was
`89861967378265fab5121b1ff245e2df0084d904`; this is a repository baseline, not a
verified production rollback version. Existing modified files and the untracked
strategy DOCX were preserved. No product implementation was changed in this
attempt.

### Blocking environment gate

The current restricted execution environment cannot complete ordinary dependency
installation and required authenticated tooling. Approval escalation is disabled.
The prepared host credentials do not establish that this session can use them.

- `.venv/Scripts/python.exe --version`: Python 3.12.14.
- `.venv/Scripts/python.exe -m venv test_runs/release-clean-312`: fresh environment
  creation reached ensurepip, which failed; its Python has no pip.
- Retried ensurepip with TEMP and TMP under `test_runs/release-temp`: permission
  denied writing the bundled pip wheel inside its newly created temporary folder.
- Development dependency installation with the same local temporary paths and
  `--no-cache-dir` failed with permission denied in pip's build-tracker directory.
  The development interpreter currently has no pytest.
- Wrangler 4.141.0 initially failed writing the default npm cache. Retrying with
  repository-local `.npm-cache-codex` failed with ENOSPC and spawn EPERM.
  The C: drive then reported 189,919,232 bytes free. No unrelated files were
  removed to reclaim space.
- The installed Stripe CLI was located by absolute path. Both its version command
  and a read-only live price query failed trying to chmod its existing config:
  access denied. Direct read-only REST price queries also failed before obtaining
  an HTTP response. No credential values were printed or changed.

The immediate hard blocker is a usable release execution environment with writable
temporary/cache directories, sufficient disk space, and working authenticated
tool access. Repeating the failed bootstrap or using development leftovers would
not prove the clean-install gate. Resume the remaining gates after that blocker
is resolved; this record does not assert that no product defects remain.

### Narrow fallback evidence

The separately available system Python has development dependencies. These checks
are development evidence only, not clean installation evidence:

- `python -m pytest`: 41 passed, 1 failed. The failing URL-audit test attempted to
  regenerate `site/sitemap-pages.xml` and received OS error 22. It was not skipped
  or weakened. The builder can write generated pages before this failure.
- `python -m pytest products/actions-upgrade-guard/tests`, with that product's src
  on PYTHONPATH: 7 passed.
- `python -m ruff check src tests scripts --no-cache`: passed.
- `python -m mypy src tests`: passed, 24 source files.
- `python -m ruff format src tests scripts --check --no-cache`: three pre-existing
  formatting differences in `scripts/audit_site_urls.py`,
  `scripts/verify_live_funnel.py`, and `tests/test_worker_routes.py`; not a pass.
- `python -m sa20_pack.build_runner`: compile-based build check passed. A complete
  distribution build and supported-Python installation matrix were not verified.
- `python scripts/audit_site_urls.py`: local URL audit passed. All sitemap XML
  files also parsed after the failed generation attempt.
- `node scripts/audit_stripe_checkout.mjs`: mocked checkout and delivery passed
  for four products. This is not a Stripe sandbox payment or real artifact test.
- Node syntax checks passed for Worker, browser app, and product catalog.

Root and Action Guard metadata both declare Python >=3.10; CI only explicitly
selects 3.12. The documented Action Guard customer path is
`python -m pip install ./products/actions-upgrade-guard`. Its clean installation
has not passed on any interpreter in this attempt.

Site generation ownership was inspected: `scripts/build_site.py` and
`scripts/site_catalog.py` produce discovery/product/proof pages and sitemaps;
selected static pages and browser modules under `site/` are also maintained
directly. Existing output must not be committed without a successful consistency
check.

### Gates still unverified

Current upstream review began with the official upload-artifact and cache
repositories and GitHub's Node 20 deprecation announcement. It did not complete
the rule-by-rule gate. In particular, upload-artifact documents GHES exclusion
and v4 behavior changes; the scanner currently proposes unconditional v3-to-v4
changes. Existing passing fixtures do not prove those changes safe across GHES,
shared artifact names, or changed hidden-file behavior. No September 26 rule-pack
verification or auto-apply safety approval is claimed.

Sources inspected:

- https://github.com/actions/upload-artifact
- https://github.com/actions/cache
- https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/

Live Stripe prices/product identities, real sandbox checkout, signed Stripe test
events, private KV artifact contents, customer download/installation, production
configuration, rollback version, and production smoke tests remain unverified.
The Worker uses inline catalog prices and paid-session retrieval for delivery;
webhook acceptance itself only logs events and does not establish entitlement.
Local tests do not establish automatic fulfillment from a customer's perspective.

No real charge/refund/subscription, external message, price or terms change,
production mutation, DNS change, or customer-data deletion was performed.

## Evidence and repairs

The [live pricing page](https://zippertools.org/pricing), inspected on September
26, still advertised May's discounted prices. The Worker already restricts that
coupon to May 6-27. Static HTML, structured offers, and browser product cards
could therefore advertise prices checkout would no longer apply.

The candidate removes expired promotion copy and expired offer dates from static
pages and generated pages. Browser price helpers now check the promotion window,
using the same helper for banner visibility. Existing regular checkout amounts
remain unchanged: fit report $99, SQLAlchemy $299.99, preset bundle $149.99,
Pydantic $249.99. No Stripe account, coupon, or payment setting was changed.

The homepage, product catalog, and Action Guard purchasing path now explain free
availability, outputs, manual alternatives, and limits instead of demand tests
and expansion gates. Research archive URLs remain available; their links are
removed from the main navigation. Legal, refund, and license terms are unchanged.

Action Guard's README no longer instructs users to buy an unavailable package. It
now includes installation steps, interpreter troubleshooting, and the meaning of
a zero-finding result. The master directive is preserved verbatim in
`docs/master-operating-directive.md`, with precedence recorded in `AGENTS.md`.

## Verification

- Root pytest suite: 42 passed, including regular-price parity between browser
  cards, structured offers, and configured Worker amounts; expired-sale absence
  across public HTML; and sale-window boundary checks.
- Action Guard tests: 7 passed.
- Ruff lint and format checks on changed Python files: passed.
- MyPy over `src tests`: passed (24 source files, including imported builder).
- Local sitemap, canonical, and internal-link audit: passed.
- Node syntax checks for the modified browser modules: passed.
- Existing local Stripe audit: checkout and ZIP delivery mocks passed for all
  four products, including direct paid-asset access blocking. This audit uses a
  historical sale clock and simulated Stripe/storage responses. Root Worker
  tests also cover checkout after promotion expiry.
- Root and Action Guard wheels built through Hatchling directly. Action Guard's
  packaged CLI help ran from its wheel with the existing system dependencies.
- Clean pip installation was attempted but failed with Windows filesystem access
  errors even with repository-local temp paths. Wheel execution is narrower proof
  than installation in a clean environment.

## Remaining release gates, in priority order

1. Verify a clean installation on an environment where pip can write temporary
   directories. Keep the current Windows failure recorded as an environment
   limitation, not a successful install.
2. Verify a real Stripe test-mode checkout through signed webhook, stored paid
   artifact, customer download, quickstart, and recovery. Local mocked results
   do not prove that production artifacts or fulfillment are currently healthy.
   Do not make irreversible Stripe changes without owner approval.
3. Review and deploy this site candidate, then recheck public prices, JSON-LD,
   navigation, and checkout. This repair is currently local only.
4. Audit Action Guard's rule assumptions against current authoritative GitHub
   sources, including eligibility for automatic application, fixtures, evidence
   dates, rollback, and stale-rule handling. Existing unit tests do not establish
   current upstream correctness. No rule refresh is claimed by this pass.
5. Reproduce public proof from the verified rule pack and exercise installation,
   diagnosis, manual remediation, preview, apply, and customer validation. Keep
   paid Action Guard unavailable until its launch bar and any price approval pass.
6. Review the paid fit-report output against the directive's objective-fit
   requirement; current marketing still describes a buy/do-not-buy recommendation.
   Do not withhold useful free diagnosis to justify the add-on.
7. Inspect available purchase/fulfillment evidence before further acquisition or
   product expansion. Historical page views are not customer-success evidence.

No external messages, purchases, deployment, DNS changes, price changes, or legal
policy changes were performed in this pass.
