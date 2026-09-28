# First-sales experiment — 2026-09-27

## Offer and audience

Existing FastAPI/Python application teams already planning native Pydantic v2
migration, with repeated supported edits and an application test suite.
Hypothesis only: they may pay $249.99 for the packaged deterministic workflow.
Do not infer demand from the historical 15,598 Stripe sessions: none paid, and
automated bursts contaminated that denominator. The separate $1 charge is not
a verified product sale.

Keep current prices, licenses and policies. No mandatory fit-report purchase.
Do not expand the product portfolio during this experiment.

## Evidence and competition

The original MIT-licensed order API is synthetic, not a customer endorsement.
Both Zipper Tools 0.1.2 and bump-pydantic 0.8.0 passed the same six app assertions.
Zipper Tools left an unsupported file unchanged and recorded a JSON finding;
bump-pydantic inserted a TODO without rewriting the unsupported validator.
Do not call that difference a free-tool failure. Neither resolves that work.

Important correction: Pydantic 2.13 includes an updated v1 namespace with Python
3.14 support. Avoid the old blanket claim that all Pydantic v1 usage fails on
Python 3.14. Use a team's actual native-v2 migration requirement as the trigger.
Source: https://pydantic.dev/docs/validation/latest/get-started/changelog/#v2130-2026-04-13

## Zero-cost distribution, prepared but not sent

Publish the owned-site proof and direct technical guides. For external posts,
obtain owner approval for the exact destination and draft. No bulk outreach,
unsolicited DMs, scraping contacts, or pitching on unrelated bug reports.

Candidate channels to review before posting:

- FastAPI GitHub discussions: https://github.com/fastapi/fastapi/discussions
  Use only a current question whose supplied code matches the supported subset.
- Python community: https://www.reddit.com/r/Python/
  Check current self-promotion rules and appropriate showcase thread first.
- FastAPI community: https://www.reddit.com/r/FastAPI/
  Answer a concrete migration question before mentioning the optional tool.

Research exclusions, checked 2026-09-27:

- https://github.com/pydantic/pydantic/issues/12618 is closed; it is evidence of
  changing compatibility, not an outreach target.
- https://github.com/cognizant-ai-lab/neuro-san/issues/1207 concerns a compatibility
  warning and newer shim behavior. Do not pitch a paid migration based on a warning.
- https://github.com/reflex-dev/reflex/issues/5964 is closed and framework-level;
  do not claim the narrow pack resolves it.

No qualified current buyer lead has been established by this research. Community
membership or a public issue does not imply purchasing interest.

### Ready-to-review standalone showcase draft

Title: A reproducible Pydantic migration comparison on a small FastAPI app

I build Zipper Tools. I tested our paid local migration pack and the free
bump-pydantic tool against the same small MIT-licensed FastAPI order API.
Both passed the same six application tests after the supported rewrites.
An unsupported validator remained manual work: our tool recorded it in JSON;
bump-pydantic added a TODO. The input, diffs, versions and test output are here:
https://zippertools.org/proof/pydantic-v2-porter/

The free scanner and interpretation steps are here:
https://zippertools.org/scan#pydantic

This is a small synthetic example, not evidence of a complete migration or
measured time savings. If the free alternative meets your needs, use it.
If you try the scanner, optional feedback on installation trouble or unsupported
patterns is useful. Please do not share private source, credentials or raw reports.

### Reply template — requires a verified matching question

Explain the specific manual fix and upstream source first. Then, only if useful:
"Disclosure: I build Zipper Tools. If this exact supported pattern repeats across
your app, our local scanner can help inventory it. The free report is enough to
evaluate fit; there is also a paid apply workflow. Here is a small comparison
against bump-pydantic, which also passed: [proof link]."

Never paste this template without tailoring it to the supplied code and rules.

## Measurement and decisions

Run `node scripts/sales_snapshot.mjs 14` for a read-only, paginated live Stripe
snapshot. Save it under ignored test_runs, not the public repository.

- GET/HEAD paid routes now render a review page without creating a session.
- Successful same-origin POST creates a session marked purchase_form_v1.
- These are explicit submissions, not verified humans or unique buyers.
- Internal source labels are separated; unmarked legacy sessions stay unverified.
- Existing Worker logs distinguish checkout_review, checkout_created,
  checkout_failed, stripe_checkout_paid and stripe_delivery_artifact.
- Free-scan route requests indicate documentation interest, not scanner execution.
- No new cookies, tracking pixels, source uploads or repository telemetry.
- Cloudflare current traffic remains unavailable to the existing API token.
  Owner sign-in or a separately approved analytics-read permission is needed;
  do not report missing traffic as zero.

Use `docs/first-sales-metrics.csv` for voluntary aggregate observations. Leave
unknowns blank. Do not store names, emails, raw reports or private paths there.
Reconcile paid sessions with signed payment and delivery logs before claiming
fulfillment. Gross paid cents are not net revenue.

Initial learning targets, not forecasts: 20 relevant people reaching the offer,
10 voluntary scanner trials and at least 3 scans with meaningful supported work.
Only record self-reported trials, never infer them from GET requests.

At 14 days (or after these targets):

- No relevant visitors: improve distribution; do not infer product failure.
- Relevant visitors but no trials: investigate trust and installation.
- Trials mostly unsupported: correct audience or scope before selling harder.
- Supported work but no purchases: ask optional value/price feedback; do not
  automatically cut prices or broaden guarantees.
- Paid but delivery/use fails: stop promotion and repair the customer journey.

This is a manual review checkpoint, not a scheduled automation.
