from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

from pydantic_v2_porter.discovery import discover_python_targets
from pydantic_v2_porter.models import FileResult, Finding, MigrationReport
from pydantic_v2_porter.transformer import transform_source

DEFAULT_REPORT = "pydantic-v2-porter-report.json"


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def run_migration(root: Path, apply: bool, show_diff: bool) -> MigrationReport:
    del show_diff
    file_results: list[FileResult] = []
    findings: list[Finding] = []
    notes: list[str] = []
    transform_counts: Counter[str] = Counter()

    if apply:
        notes.append(
            "Community edition is scan-only. Apply mode is only available in "
            "the commercial migration pack."
        )

    targets = discover_python_targets(root)
    if not targets:
        findings.append(
            Finding(
                code="no-pydantic-targets",
                message="No candidate Pydantic source files were found.",
                path=str(root),
            )
        )
        return MigrationReport(
            root_path=str(root),
            mode="dry-run",
            created_at=_utc_now(),
            findings=findings,
            confidence=0.0,
            notes=notes,
        )

    for path in targets:
        relative = str(path.relative_to(root))
        before = path.read_text(encoding="utf-8")
        result = transform_source(before, relative)

        file_results.append(
            FileResult(
                path=relative,
                changed=False,
                findings=list(result.findings),
                transforms_applied=result.transforms_applied,
                notes=result.notes,
            )
        )
        findings.extend(result.findings)
        notes.extend(result.notes)
        transform_counts.update(result.transforms_applied)

    if findings:
        notes.append(
            "Unsupported files were left untouched. The public repo only "
            "reports fit and manual-review blockers."
        )
    if transform_counts:
        notes.append(
            "Detected supported candidates that the commercial pack can "
            "rewrite automatically."
        )

    confidence = 0.94
    confidence -= min(len(findings) * 0.08, 0.64)
    if not transform_counts:
        confidence -= 0.08

    return MigrationReport(
        root_path=str(root),
        mode="dry-run",
        created_at=_utc_now(),
        file_results=file_results,
        artifact_changes=[],
        findings=findings,
        transforms_applied=sorted(transform_counts.keys()),
        confidence=round(max(confidence, 0.0), 3),
        notes=sorted(set(notes)),
    )
