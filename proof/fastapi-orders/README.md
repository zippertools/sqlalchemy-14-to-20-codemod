# FastAPI order API migration example

An original, synthetic application fixture, not a customer case study. Licensed
under MIT (see LICENSE). It exercises request validation, normalization,
settings, response serialization, and a deliberately unsupported validator.
No database or external service is needed.

Reproduce with `python scripts/verify_pydantic_case_study.py --pack PATH_TO_EXTRACTED_PAID_ZIP`.
The script creates isolated environments in ignored `test_runs/`, installs the
public scanner from the published release, and compares the purchased pack with
`bump-pydantic==0.8.0`. The application and assertions are identical for both.
No commercial engine is copied into public proof files. Dependency updates are
performed by the harness, not claimed as codemod functionality.

The unsupported module is scanned but deliberately not imported by the app.
Passing app tests therefore does not resolve that module's manual-review work.
