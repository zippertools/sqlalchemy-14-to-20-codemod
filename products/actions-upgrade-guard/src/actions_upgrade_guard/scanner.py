from __future__ import annotations

from collections.abc import Iterable
from datetime import timezone
from pathlib import Path
from typing import Any, cast

import yaml

from actions_upgrade_guard.discovery import (
    discover_local_action_files,
    discover_workflow_files,
)
from actions_upgrade_guard.models import Finding, ScanReport, WorkflowSummary
from actions_upgrade_guard.patching import (
    Replacement,
    apply_patches,
    build_patches,
    replace_action_version,
)
from actions_upgrade_guard.rules import RULE_PACK_VERSION, rule

PRODUCT = "actions-upgrade-guard"
VERSION = "0.1.0"
DEFAULT_JSON_REPORT = "actions-upgrade-report.json"
DEFAULT_HTML_REPORT = "actions-upgrade-report.html"


def _line_number(lines: list[str], needle: str) -> int | None:
    for index, line in enumerate(lines, start=1):
        if needle in line:
            return index
    return None


def _utc_now() -> str:
    from datetime import datetime

    return datetime.now(timezone.utc).isoformat()


def _relative(root: Path, path: Path) -> str:
    return str(path.relative_to(root)).replace("\\", "/")


def _finding(
    rule_id: str,
    path: str,
    message: str,
    line: int | None = None,
    current: str | None = None,
    recommended: str | None = None,
    confidence: float = 1.0,
    blocking: bool | None = None,
) -> Finding:
    metadata = rule(rule_id)
    is_blocking = (
        metadata.classification in {"autofix", "manual_review", "blocked"}
        if blocking is None
        else blocking
    )
    return Finding(
        rule_id=metadata.id,
        title=metadata.title,
        severity=metadata.severity,
        classification=metadata.classification,
        message=message,
        path=path,
        line=line,
        source_url=metadata.source_url,
        source_label=metadata.source_label,
        deadline=metadata.deadline,
        current=current,
        recommended=recommended or metadata.recommendation,
        confidence=confidence,
        blocking=is_blocking,
    )


def _safe_load(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        return None, str(exc)
    except UnicodeDecodeError as exc:
        return None, str(exc)
    if payload is None:
        return {}, None
    if not isinstance(payload, dict):
        return None, "Top-level YAML value is not a mapping."
    return cast(dict[str, Any], payload), None


def _iter_jobs(workflow: dict[str, Any]) -> Iterable[tuple[str, dict[str, Any]]]:
    jobs = workflow.get("jobs")
    if not isinstance(jobs, dict):
        return []
    result: list[tuple[str, dict[str, Any]]] = []
    for name, value in jobs.items():
        if isinstance(value, dict):
            result.append((str(name), cast(dict[str, Any], value)))
    return result


def _iter_steps(job: dict[str, Any]) -> Iterable[dict[str, Any]]:
    steps = job.get("steps")
    if not isinstance(steps, list):
        return []
    return [cast(dict[str, Any], item) for item in steps if isinstance(item, dict)]


def _string_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        return [item for item in value if isinstance(item, str)]
    return []


def _permissions_are_broad(value: Any) -> bool:
    if value == "write-all":
        return True
    if isinstance(value, dict):
        return any(str(item).lower() == "write" for item in value.values())
    return False


def _scan_workflow(
    root: Path,
    path: Path,
) -> tuple[list[Finding], list[Replacement], WorkflowSummary]:
    findings: list[Finding] = []
    replacements: list[Replacement] = []
    relative = _relative(root, path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    workflow, error = _safe_load(path)
    if error:
        findings.append(
            Finding(
                rule_id="AUG000",
                title="Workflow YAML could not be parsed",
                severity="high",
                classification="blocked",
                message=f"Workflow could not be parsed: {error}",
                path=relative,
                blocking=True,
                confidence=1.0,
            )
        )
        return findings, replacements, WorkflowSummary(relative, 0, 0, 0, 0)
    assert workflow is not None

    jobs = list(_iter_jobs(workflow))
    total_steps = 0
    action_steps = 0
    local_actions = 0

    top_permissions = workflow.get("permissions")
    has_any_permissions = "permissions" in workflow
    if _permissions_are_broad(top_permissions):
        findings.append(
            _finding(
                "AUG007",
                relative,
                "Top-level workflow permissions include write scope.",
                line=_line_number(lines, "permissions:"),
                current=str(top_permissions),
                blocking=False,
            )
        )

    for _job_name, job in jobs:
        runs_on_values = _string_values(job.get("runs-on"))
        for value in runs_on_values:
            if value == "ubuntu-20.04" and "self-hosted" not in runs_on_values:
                findings.append(
                    _finding(
                        "AUG003",
                        relative,
                        (
                            "Job references ubuntu-20.04. This image is retired on G"
                            "itHub-hosted runners; custom self-hosted labels require"
                            " separate review."
                        ),
                        line=_line_number(lines, "ubuntu-20.04"),
                        current=value,
                        recommended="Test and move to ubuntu-22.04 or ubuntu-24.04.",
                    )
                )
            if value in {"macos-latest", "windows-latest", "ubuntu-latest"}:
                findings.append(
                    _finding(
                        "AUG008",
                        relative,
                        f"Job uses floating runner label {value}.",
                        line=_line_number(lines, value),
                        current=value,
                        blocking=False,
                    )
                )

        if "permissions" in job:
            has_any_permissions = True
        if _permissions_are_broad(job.get("permissions")):
            findings.append(
                _finding(
                    "AUG007",
                    relative,
                    "Job permissions include write scope.",
                    line=_line_number(lines, "permissions:"),
                    current=str(job.get("permissions")),
                    blocking=False,
                )
            )

        env = job.get("env")
        if isinstance(env, dict) and env.get("ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION"):
            findings.append(
                _finding(
                    "AUG005",
                    relative,
                    (
                        "Job declares the Node 20 opt-out; GitHub announced its "
                        "removal on September 23, 2026. Review runner compatibil"
                        "ity."
                    ),
                    line=_line_number(lines, "ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION"),
                    current="ACTIONS_ALLOW_USE_UNSECURE_NODE_VERSION",
                )
            )

        for step in _iter_steps(job):
            total_steps += 1
            uses = step.get("uses")
            if not isinstance(uses, str):
                continue
            action_steps += 1
            if uses.startswith("./"):
                local_actions += 1
            replacement = replace_action_version(uses)
            if replacement:
                before, after = replacement
                rule_id = "AUG002" if before.startswith("actions/cache@") else "AUG001"
                metadata = rule(rule_id)
                findings.append(
                    _finding(
                        rule_id,
                        relative,
                        f"Review {before}: compatibility is unverified.",
                        line=_line_number(lines, before),
                        current=before,
                        recommended=metadata.recommendation,
                    )
                )

    if jobs and not has_any_permissions:
        findings.append(
            _finding(
                "AUG006",
                relative,
                "Workflow has jobs but no explicit top-level or job-level permissions.",
                line=None,
                blocking=False,
            )
        )

    return (
        findings,
        replacements,
        WorkflowSummary(
            path=relative,
            jobs=len(jobs),
            steps=total_steps,
            actions=action_steps,
            local_actions=local_actions,
        ),
    )


def _scan_local_action(root: Path, path: Path) -> list[Finding]:
    relative = _relative(root, path)
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    payload, error = _safe_load(path)
    if error:
        return [
            Finding(
                rule_id="AUG000",
                title="Local action metadata could not be parsed",
                severity="high",
                classification="blocked",
                message=f"Local action metadata could not be parsed: {error}",
                path=relative,
                blocking=True,
            )
        ]
    assert payload is not None
    runs = payload.get("runs")
    if isinstance(runs, dict) and runs.get("using") == "node20":
        return [
            _finding(
                "AUG004",
                relative,
                "Local JavaScript action metadata still uses node20.",
                line=_line_number(lines, "node20"),
                current="node20",
                recommended="Test on node24, then update runs.using to node24.",
            )
        ]
    return []


def _confidence(findings: list[Finding], patches_count: int) -> float:
    if not findings:
        return 0.98
    score = 0.92
    score -= min(0.35, len([item for item in findings if item.blocking]) * 0.06)
    score -= min(0.15, len([item for item in findings if not item.blocking]) * 0.02)
    if patches_count:
        score += 0.04
    return round(max(0.1, min(score, 0.99)), 3)


def scan_repo(root: Path, apply: bool = False) -> ScanReport:
    workflow_files = discover_workflow_files(root)
    local_action_files = discover_local_action_files(root)
    findings: list[Finding] = []
    replacements: list[Replacement] = []
    summaries: list[WorkflowSummary] = []

    for path in workflow_files:
        file_findings, file_replacements, summary = _scan_workflow(root, path)
        findings.extend(file_findings)
        replacements.extend(file_replacements)
        summaries.append(summary)

    for path in local_action_files:
        findings.extend(_scan_local_action(root, path))

    patches = build_patches(root, replacements)
    changed_files: list[str] = []
    if apply and patches:
        changed_files = apply_patches(root, replacements)
        patches = [
            type(patch)(
                path=patch.path,
                rule_id=patch.rule_id,
                title=patch.title,
                description=patch.description,
                replacements=patch.replacements,
                diff=patch.diff,
                applied=patch.path in changed_files,
            )
            for patch in patches
        ]

    scanned_files = [
        _relative(root, path) for path in [*workflow_files, *local_action_files]
    ]
    notes = [
        (
            "Runs locally; no GitHub token, source upload, or repository "
            "mutation required."
        ),
        (
            "No safe patch: platform, runner, and artifact behavior "
            "cannot be established from action tags alone. All curre"
            "nt upgrade rules require manual review."
        ),
        "Rules reviewed 2026-09-26; no rules eligible for automatic application.",
        (
            "No supported findings detected does not establish repos"
            "itory safety or exhaustive compatibility."
        ),
    ]
    if not workflow_files:
        notes.append("No .github/workflows/*.yml or *.yaml files were found.")

    return ScanReport(
        product=PRODUCT,
        version=VERSION,
        rule_pack_version=RULE_PACK_VERSION,
        root_path=str(root),
        mode="apply" if apply else "dry-run",
        created_at=_utc_now(),
        scanned_files=scanned_files,
        workflow_summaries=summaries,
        findings=findings,
        patches=patches,
        files_changed=changed_files,
        confidence=_confidence(findings, len(patches)),
        notes=notes,
    )
