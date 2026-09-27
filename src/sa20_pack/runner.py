from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from sa20_pack.discovery import iter_python_files
from sa20_pack.models import FileMigrationResult, MigrationReport
from sa20_pack.transforms import scan_sqlalchemy20_patterns


def run_migration(root: Path, apply: bool, show_diff: bool) -> MigrationReport:
    del apply, show_diff
    file_results: list[FileMigrationResult] = []

    for file_path in iter_python_files(root):
        relative_path = file_path.relative_to(root).as_posix()
        original_source = file_path.read_text(encoding="utf-8")
        _, transforms, findings, parse_error = scan_sqlalchemy20_patterns(
            original_source
        )

        file_results.append(
            FileMigrationResult(
                path=relative_path,
                changed=False,
                transforms=transforms,
                findings=findings,
                diff=None,
                parse_error=parse_error,
            )
        )

    return MigrationReport(
        root_path=str(root),
        mode="dry-run",
        created_at=datetime.now(timezone.utc).isoformat(),
        files_scanned=len(file_results),
        file_results=file_results,
        validation_results=[],
    )
