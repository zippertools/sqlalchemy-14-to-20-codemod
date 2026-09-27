from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sa20_pack.models import MigrationReport
from sa20_pack.reporting import report_to_json
from sa20_pack.runner import run_migration


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sa20-pack",
        description=(
            "Scan a repo for SQLAlchemy 1.4 -> 2.0 migration fit in the public "
            "community edition."
        ),
    )
    parser.add_argument("path", help="Repository or package path to migrate.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reserved for the commercial pack. The public repo is scan-only.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Print unified diffs for changed files.",
    )
    parser.add_argument(
        "--report",
        default="migration-report.json",
        help="Where to write the machine-generated JSON report.",
    )
    return parser


def _print_summary(report: MigrationReport) -> None:
    _write_console(f"Status: {report.status}")
    if (
        not report.transform_count
        and not report.unsupported_count
        and not report.parse_error_count
    ):
        _write_console("No supported findings detected.")
    _write_console(f"Files scanned: {report.files_scanned}")
    _write_console(f"Files changed: {len(report.files_changed)}")
    _write_console(f"Transforms applied: {report.transform_count}")
    _write_console(f"Unsupported findings: {report.unsupported_count}")
    _write_console(f"Overall confidence: {report.overall_confidence:.3f}")

    if report.validation_results:
        for result in report.validation_results:
            if result.skipped:
                _write_console(f"[{result.phase}] skipped: {result.note}")
            else:
                outcome = "passed" if result.returncode == 0 else "failed"
                command_text = " ".join(result.command)
                _write_console(f"[{result.phase}] {outcome}: {command_text}")
    else:
        _write_console("Validation: skipped in community scan mode")


def _write_console(text: str) -> None:
    stream = sys.stdout
    encoding = stream.encoding or "utf-8"
    data = (text + "\n").encode(encoding, errors="backslashreplace")
    stream.buffer.write(data)
    stream.flush()


def _print_diffs(report: MigrationReport) -> None:
    for file_result in report.file_results:
        if file_result.diff:
            _write_console(file_result.diff.rstrip("\n"))


def _write_report(report: MigrationReport, report_path: Path) -> None:
    report_path.write_text(report_to_json(report), encoding="utf-8")


def _exit_code(report: MigrationReport, apply_requested: bool) -> int:
    if apply_requested:
        return 1
    if report.status in {"validated", "preview_only"}:
        return 0
    if report.status == "manual_review_required":
        return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    report = run_migration(root=root, apply=False, show_diff=args.diff)

    if args.diff:
        _print_diffs(report)
    _write_report(report, Path(args.report).resolve())
    if args.apply:
        _write_console(
            "Community edition is scan-only. "
            "Apply mode is only available in the commercial pack."
        )
    _print_summary(report)

    return _exit_code(report, args.apply)


if __name__ == "__main__":
    raise SystemExit(main())
