# Public Proof

Proof pass date: 2026-04-07

This pass checked `sa20-pack` on real public SQLAlchemy migration patterns,
not only on local fixtures. The goal was to prove two things:

- the public scanner classifies supported legacy patterns cleanly on copied
  public input
- unsupported patterns are surfaced as explicit manual-review findings

## Trust Boundary

Do not trust this blindly with your project. Visible GitHub social proof is
still weak, the public repo is scanner-first and does not expose the full paid
apply engine, and this proof is narrow: a few supported examples plus
fail-closed examples. Treat it as a fit signal, then run the scanner or paid
workflow on a branch and rely on your own typecheck, build, and tests before
merge.

## Supported Path Proof

- [`Bogdanp/flask_dramatiq_example`](https://github.com/Bogdanp/flask_dramatiq_example/blob/a2f2c2baf7bdd7e1044ec6d241556f6333a6e397/app.py)
  - Public file: `app.py`
  - Result: supported
  - Scanner status: `preview_only`
  - Commercial-pack apply result on the copied file: `validated`
  - Verified transforms:
    - `from sqlalchemy.ext.declarative import declarative_base`
      -> `from sqlalchemy.orm import declarative_base`
    - `session.query(Job).get(job_id)` -> `session.get(Job, job_id)`

- [`dunossauro/live-de-python`](https://github.com/dunossauro/live-de-python/blob/c0c83d3cb1271b0e55de2f83ad3a2aa4a57b53a8/codigo/Live011/core_select.py)
  - Public file: `codigo/Live011/core_select.py`
  - Result: supported
  - Scanner status: `preview_only`
  - Commercial-pack apply result on the copied file: `validated`
  - Verified transform:
    - `select([user_table])` -> `select(user_table)`

- [`nylas/sync-engine`](https://github.com/nylas/sync-engine/blob/b91b94b9a0033be4199006eb234d270779a04443/inbox/transactions/search.py)
  - Public file: `inbox/transactions/search.py`
  - Result: supported
  - Scanner status: `preview_only`
  - Commercial-pack apply result on the copied file: `validated`
  - Verified transforms:
    - `db_session.query(Transaction).get(max_id)`
      -> `db_session.get(Transaction, max_id)`
    - `joinedload("phone_numbers")` -> `joinedload(Contact.phone_numbers)`

## Fail-Closed Proof

- [`nylas/sync-engine`](https://github.com/nylas/sync-engine/blob/b91b94b9a0033be4199006eb234d270779a04443/inbox/ignition.py)
  - Public file: `inbox/ignition.py`
  - Result: blocked correctly
  - Status: `manual_review_required`
  - Findings:
    - `engine_execute_removed`
    - `engine_execute_removed`

- [`teamclairvoyant/airflow-maintenance-dags`](https://github.com/teamclairvoyant/airflow-maintenance-dags/blob/fe592a5cb90508804b589652ef7fedc624bff595/db-cleanup/airflow-db-cleanup.py)
  - Public file: `db-cleanup/airflow-db-cleanup.py`
  - Result: blocked correctly
  - Status: `manual_review_required`
  - Findings:
    - `query_from_self_removed`
    - `query_from_self_removed`

## Public-Proof Commands

These were the public scanner CLI paths exercised during the pass:

```bash
python -m sa20_pack.cli public_repo_trials/sa20-pack/bogdanp-flask-dramatiq --report public_repo_trials/sa20-pack/bogdanp-flask-dramatiq-report.json
python -m sa20_pack.cli public_repo_trials/sa20-pack/dunossauro-core-select --report public_repo_trials/sa20-pack/dunossauro-core-select-report.json
python -m sa20_pack.cli public_repo_trials/sa20-pack/nylas-search --report public_repo_trials/sa20-pack/nylas-search-report.json
python -m sa20_pack.cli public_repo_trials/sa20-pack/nylas-ignition --report public_repo_trials/sa20-pack/nylas-ignition-report.json
python -m sa20_pack.cli public_repo_trials/sa20-pack/airflow-db-cleanup --report public_repo_trials/sa20-pack/airflow-db-cleanup-report.json
```

## Fixes Uncovered By This Pass

- added the missing `python -m sa20_pack.cli` module entrypoint
- made diff output safe on Windows consoles that cannot emit every Unicode
  character directly
- moved the public proof docs back into scanner-only language after the repo was
  split into community and commercial editions

## What This Proves

- three real public files land inside the supported automation surface
- two known SQLAlchemy 2.0 removals are blocked explicitly instead of guessed
- the root CLI now works through the actual module invocation path buyers will
  use

## What This Does Not Prove

- full `engine.execute(...)` automation
- full `Query` API migration to `select()`
- package, test, or database integration success for every public repo that
  contains one supported snippet

## September 26, 2026 validation correction

Historical `validated` statuses below do not establish that application checks ran: the old runner accepted an all-skipped validation set. Version 0.1.2 reports `validation_not_run` in that case. Historical rewrite examples remain static rewrite evidence, not verified application compatibility. Run your own configured checks on a copy before adopting changes.
