# GitHub Actions Upgrade Guard

GitHub Actions Upgrade Guard is a local-first scanner for workflow deprecations,
runner drift, permissions risk, and supported maintenance findings.

The current tool is free and runs locally without uploading source code.
No paid Action Guard package is currently offered.

## Installation

Requires Python 3.10 or newer. From a checkout of the Zipper Tools repository,
install the product and its PyYAML dependency:

```bash
python -m pip install ./products/actions-upgrade-guard
python -m actions_upgrade_guard.cli --help
```

Use the same Python interpreter for installation and scanning. If Python cannot
find `actions_upgrade_guard`, check that installation succeeded in that interpreter
or activate the virtual environment where you installed it.

## Who This Is For

- Platform engineers responsible for many repositories.
- DevOps leads cleaning up brittle Actions workflows before deadlines.
- Repo owners who need a reviewer-friendly maintenance report.
- Maintainers who want a CI gate for upcoming Actions breakage.

## Do Not Use This If

- You need a hosted monitoring service.
- You want the tool to log in to GitHub and mutate repos for you.
- Your workflows are generated dynamically and the generated files are not
  checked into the repo.
- You expect security hardening beyond the documented workflow-upgrade rules.

## Current Supported Rules

- `actions/upload-artifact@v3` and `actions/download-artifact@v3` detection
  with source-linked manual migration guidance.
- `actions/cache@v1` and `actions/cache@v2` detection with manual runner compatibility review.
- `ubuntu-20.04` hosted runner retirement detection.
- `macos-latest` migration-risk detection.
- Local JavaScript actions using `node20` runtime detection.
- Temporary Node 20 opt-out environment variable detection.
- Missing or broad `GITHUB_TOKEN` permissions detection.
- Composite and local action inventory.
- Fail-closed reporting for invalid workflow YAML.

## Example

```bash
python -m actions_upgrade_guard.cli path/to/repo \
  --report actions-upgrade-report.json \
  --html-report actions-upgrade-report.html
```

The September 26 rule pack has no rules eligible for automatic application.
Artifact platform/behavior and runner prerequisites cannot be inferred from tags.
`--apply` is retained for compatibility and leaves workflow files unchanged:

```bash
python -m actions_upgrade_guard.cli path/to/repo --apply
```

## Outputs

- `actions-upgrade-report.json`: machine-readable report for CI and dashboards.
- `actions-upgrade-report.html`: reviewer and manager-readable summary.
- explicit no-safe-patch notes and manual alternatives.
- exit code `0` when there are no blocking findings.
- exit code `1` when blocking findings require action.
- exit code `2` when the scanner cannot run.

## Trust Boundary

- Runs locally.
- No GitHub token required.
- No source upload.
- No workflow mutation: all current upgrades require manual review.
- Every finding names the source-backed rule and whether the fix is automatic,
  manual review, blocked, or informational.
- No supported findings detected does not mean a repository is safe or compatible.
  The scanner only checks its documented rules, and does not execute workflows.
- Review the source guidance in each finding for manual remediation. Inspect
  manual changes on a branch and run your own CI checks before merging.
- Local action metadata scope is `.github/actions/**/action.yml` or `action.yaml`.
- Exact major action tags only: pinned SHAs, reusable workflows, generated YAML,
  remote actions, and arbitrary local-action directories are not analyzed.
- The numeric confidence field is a heuristic, not a safety probability.
- See [rule review](docs/rule-review-2026-09-26.md) for sources and limitations.
