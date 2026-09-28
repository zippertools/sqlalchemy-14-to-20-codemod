# Sales journey release — 2026-09-27

Deployed Cloudflare Worker version: `9c5c40b8-27af-488e-824a-c2ca7242e1c3`.

The homepage, free scanner instructions, Pydantic offer and proof now form one
focused customer journey for existing FastAPI applications migrating to native
Pydantic v2. Existing prices, policies and customer access remain unchanged.

## Evidence

- 46 repository tests pass; Ruff, mypy, package build and site URL checks pass.
- Live URL audit passes. All four paid GET routes return purchase review forms,
  without creating Stripe sessions. Session creation requires a same-origin POST.
- All four products passed Stripe test-mode checkout, signed completion webhook,
  automatic download, recovery download and success-page checks. Unpaid delivery
  was denied. This is sandbox evidence, not live revenue.
- The delivered Pydantic ZIP matches the package used for the public proof.
- The synthetic FastAPI example passes six tests before migration and after each
  of the paid and free migrations. Unsupported behavior and exact versions are
  disclosed. No customer outcome or time savings are claimed.
- Desktop and mobile pages were visually inspected; mobile proof and product
  pages had no horizontal overflow.
- Public comparison patches retain the whitespace required by unified-diff
  context lines; those artifact lines are excluded from whitespace lint.

## Remaining commercial evidence

The release improves the buying path but does not establish willingness to pay.
Use `first-sales-experiment.md` and `scripts/sales_snapshot.mjs` to evaluate it.
Checkout form submissions are not verified unique humans. No repository
telemetry was added.

Cloudflare traffic analytics require authenticated access or a suitably scoped
read token; the available token could not supply the requested traffic history.
The prepared FastAPI showcase post remains unpublished pending explicit owner
approval under section 15 of the master operating directive.
