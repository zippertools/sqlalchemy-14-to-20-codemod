# Pricing

## Product ladder

| Buyer Question | Recommended Option | Price |
| --- | --- | --- |
| "Does my repo have supported patterns?" | Free scan | Free |
| "Is automation worth it for SQLAlchemy or Pydantic?" | SQLAlchemy/Pydantic fit report | $99 |
| "I want the SQLAlchemy cleanup workflow." | SQLAlchemy pack | $299.99 |
| "I want SQLAlchemy rollout docs and presets." | Preset bundle | $149.99 |
| "I need the Pydantic v1 to v2 cleanup subset." | Pydantic cleanup pack | $249.99 |

## Current pricing

The May 2026 promotion has ended. Regular checkout prices above apply.

## Checkout and delivery terms

Paid products use Stripe Checkout. After payment, `/stripe/delivery` verifies
the paid Stripe Checkout Session and streams the matching ZIP from private
Cloudflare storage. Normal use does not require source-code upload or manual
email delivery.

Refunds receive a 14-day review for published-scope or delivery mismatches.
Support email: `support@zippertools.org`.

## Free vs paid at a glance

| Capability | Free scan | $99 SQLAlchemy/Pydantic fit report | Cleanup pack | Preset bundle |
| --- | --- | --- | --- | --- |
| Public/local CLI | Yes | Reads scanner output locally | Yes | Uses scanner output locally |
| Supported-candidate detection | Yes | No code changes | Yes | Uses scanner output |
| Diff preview | No | Summarizes candidates | Yes | Uses scanner output |
| JSON migration report | Yes | Adds buyer-fit summary | Yes, plus buyer docs | Uses public CLI outputs plus richer templates |
| Manual-review findings | Yes | Summarizes risk buckets | Yes | Uses public CLI outputs plus rollout guidance |
| Preset/rollout guidance | Basic public docs | Automated recommendation | Yes | Yes |
| Human service dependency | No | No | No | No |
| Full custom migration service | No | No | No | No |

### Free scan

Price: **$0**

Use the public repo, CLI, and GitHub Action for:

- supported-candidate detection
- manual-review findings
- JSON migration report
- source locations and manual-review findings
- demo fixture and public docs

The point of the free tier is qualification and trust. A buyer should know
whether the repo is a fit before paying.

Best for:

- finding whether a repo has repeated supported SQLAlchemy patterns
- creating a local report without checkout, repo upload, or source sharing

Not for:

- custom migration decisions
- private source review
- guaranteed app-level success

### SQLAlchemy/Pydantic fit report

Product name: **`SQLAlchemy/Pydantic Fit Report Add-on`**

Normal checkout price: **$99 per team**.

What it adds:

- a local report summarizer for SQLAlchemy or Pydantic free scanner JSON
- supported-pattern summary
- manual-review risk summary
- autonomous recommendation to use the cleanup pack, use the preset bundle, or do not buy

What it does not include:

- human review
- custom coding
- guaranteed migration success

Best for: promising SQLAlchemy or Pydantic scan output where the business case
is still unclear.

Not for: ESLint proof-only pages, applying rewrites, custom consulting, or
human review.

### SQLAlchemy cleanup pack

Product name: **`SQLAlchemy 1.4 to 2.0 Migration Cleanup Pack`**

Normal checkout price: **$299.99 per team**.

What it adds:

- deterministic local rewrites for the documented SQLAlchemy subset
- before/after diff preview and apply workflow
- JSON reports, rollback notes, and rollout checklists
- manager-facing migration summary
- supported rewrite table and manual-review flags

What the buyer is really paying for:

- fewer repetitive manual fixes
- clearer unsupported buckets
- tighter rollout confidence

Best for: repeated supported SQLAlchemy findings that are still expensive to
fix by hand.

Not for: unsupported transaction semantics, broad `Query` to `select()`
rewrites, or app-specific debugging.

### Migration Preset Bundle

Product name: **`Migration Preset Bundle`**

Normal checkout price: **$149.99 per team**.

What it includes:

- repo-type preset files
- richer report templates
- rollout notes and manager summary templates
- downloadable add-on with no service dependency

What it does not include:

- custom repo debugging
- custom coding by a person
- guaranteed full migration ownership

Best for: teams that already know the repo fit and want reusable rollout
structure.

Not for: code rewrites, private repo debugging, or a migration service.

### Pydantic cleanup pack

Product name: **`Pydantic v1 to v2 Migration Cleanup Pack`**

Normal checkout price: **$249.99 per team**.

What it includes:

- safe validator rewrites
- `BaseSettings` migration support
- supported `root_validator(pre=True)` rewrites
- safe config conversion for the documented subset
- fail-closed unsupported findings

Free qualification: run the separate Pydantic scanner from the Pydantic README.
It is not the SQLAlchemy free scan.

Best for: repos with direct `pydantic` imports, `BaseSettings`, safe `Config`
blocks, or simple validators.

Not for: custom semantic rewrites, post root validators, or unsupported
validator signatures.

## Why the split works

Free spreads because it is genuinely useful and easy to prove.

Paid differentiates on:

- wider coverage
- better presets
- better reporting
- better docs/templates
- more repeatable rollout structure

That keeps the repo public and useful without giving away the entire revenue
engine.

## Who should not buy this

Do not buy if:

- you have not run the free scan yet
- your repo needs human consulting or a custom migration service
- your repo depends on unsupported patterns being auto-rewritten today
- you expect the paid pack to guarantee a passing application without manual
  review

## What happens if validation fails

If a migration run fails validation, the result is a failed migration run. The
tool should report that clearly instead of pretending the migration succeeded.

That means the buyer still gets useful information:

- what changed
- what was unsupported
- which validation phase failed

But it does not count as a quiet success.

## What the paid pack does not cover

The paid pack still does not promise:

- full `Query` to `select()` migration coverage
- transaction-semantics decisions for legacy execution paths
- every repo-specific rollout decision
- custom framework wrappers that hide SQLAlchemy internals
- human debugging of application-specific failures
