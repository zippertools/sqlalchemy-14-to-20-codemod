# Proposed FastAPI Show and Tell post

Destination: https://github.com/fastapi/fastapi/discussions/categories/show-and-tell

The category was checked on 2026-09-27 and invites sharing projects. This is a
single disclosed showcase, not a reply on somebody else's bug report. It has
not been posted. Owner approval is required by master-operating-directive.md.

## Title

A reproducible Pydantic migration comparison on a small FastAPI app

## Body

I build Zipper Tools. I tested our paid local Pydantic migration pack and the
free bump-pydantic tool against the same small MIT-licensed FastAPI order API.

Both passed the same six application tests after the supported rewrites:
request normalization, invalid-input rejection, extra-field rejection,
response serialization, and environment settings. An unsupported validator
remained manual work: our tool recorded a JSON finding and left the file
unchanged; bump-pydantic added a TODO without rewriting that validator.

[Input, versions, diffs and test results](https://zippertools.org/proof/pydantic-v2-porter/)

The example deliberately keeps FastAPI at 0.119.0 while changing Pydantic
1.10.24 to 2.12.0. It is a small synthetic app, not a customer migration,
latest-FastAPI compatibility test, or measured time-savings benchmark.

[Free local scanner and report interpretation](https://zippertools.org/scan#pydantic)

The free report is sufficient to evaluate fit; no paid assessment is required.
The optional commercial pack costs $249.99 per team and applies only its
documented subset. If bump-pydantic meets your needs, use it.

If you try the scanner, optional feedback about installation problems or
unsupported pattern categories would help. Please do not share private source,
credentials or raw reports. The tools run locally without repository uploads.
