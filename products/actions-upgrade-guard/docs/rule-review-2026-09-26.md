# Rule review: September 26, 2026

Rule pack: `2026.09.26`. This is a diagnostic review, not proof that any
repository's workflows execute successfully. No current rule is eligible for
automatic application. `--apply` produces findings but leaves workflows unchanged.
This protects existing users without withholding diagnostic information.

| Rules | Primary evidence inspected | Scope and safe behavior |
| --- | --- | --- |
| AUG001 | [Artifact retirement](https://github.blog/changelog/2024-04-16-deprecation-notice-v3-of-the-artifact-actions/), [v4 migration behavior](https://github.com/actions/upload-artifact/blob/v4/README.md) | Exact upload/download v3 tags. GitHub.com retirement is January 30, 2025; GHES is excluded. Server edition, shared names, hidden files, and download compatibility are not established by a tag. Report for review; no patch. |
| AUG002 | [Cache service retirement](https://github.blog/changelog/2025-01-15-github-actions-ubuntu-20-runner-image-brownout-dates-and-other-breaking-changes/), [cache v4 requirements](https://github.com/actions/cache/blob/v4/README.md) | Exact cache v1/v2 tags. March 1, 2025 cutoff concerns GitHub.com; GHES differs. Runner version >=2.231.0 is a service prerequisite. A version-only patch cannot prove compatibility; no patch. |
| AUG003 | [Hosted Ubuntu retirement](https://github.blog/changelog/2025-01-15-github-actions-ubuntu-20-runner-image-brownout-dates-and-other-breaking-changes/) | Literal ubuntu-20.04, excluding explicit self-hosted label lists. Hosted image retired April 15, 2025. Custom labels and tooling require review. Never change runner labels automatically. |
| AUG004–005 | [Node 20 removal](https://github.blog/changelog/2026-09-23-node-20-is-no-longer-available-in-github-actions/), [updated migration announcement](https://github.blog/changelog/2025-09-19-deprecation-of-node-20-on-github-actions-runners/) | Local action metadata node20 and job-level opt-out declarations. Updated removal date September 23, 2026. Does not inspect remote action internals or runner installations. Review runtime, architecture, dependencies, and platform; no patch. |
| AUG006–007 | [GITHUB_TOKEN guidance](https://docs.github.com/en/actions/tutorials/authenticate-with-github_token) | Missing declarations and declared write scopes. Defaults and actual permission needs are unknown. These are review signals, not proof of a vulnerability; nonblocking. |
| AUG008 | [Image migrations](https://github.blog/changelog/2026-05-14-github-actions-upcoming-image-migrations/) | Literal ubuntu/windows/macos-latest labels. Informational only. Removed the misleading shared June deadline; this is floating-label detection, not a current-image inventory. |

Tests in `tests/test_scanner.py` cover legacy references, unchanged bytes under
apply (including repeated artifact names, hidden paths, and comments), explicit
self-hosted labels, invalid YAML, zero-findings wording, and no auto-eligible
rules. Existing fixture tests cover runtime, permissions, and clean workflows.
These tests verify static behavior, not hosted CI execution.

Manual alternative: follow each source, choose a platform-compatible maintained
action version, review upstream migration changes, edit a branch, inspect the
diff, and run your CI. Roll back a manual change with your normal version-control
review process. There is no automatic change to roll back in this pack.

Coverage remains deliberately bounded: workflow YAML directly under
`.github/workflows`, metadata under `.github/actions`, and exact recognized tags.
Reusable workflow resolution, pinned SHA interpretation, remote actions, dynamic
expressions, and complete permissions/runtime analysis are not implemented.
Zero findings means **No supported findings detected.**

Reproduce `proof-report.json` by scanning `fixtures/deprecated_repo` and serializing
with `report_to_json`; normalize only root_path to `fixture/deprecated_repo` and
created_at to `2026-09-26T00:00:00+00:00`. The site reads this actual report instead
of maintaining a separate hand-written findings list.
