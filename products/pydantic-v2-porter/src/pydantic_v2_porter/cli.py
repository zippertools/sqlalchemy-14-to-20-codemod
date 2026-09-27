from __future__ import annotations

import argparse
import sys
from pathlib import Path

from pydantic_v2_porter.models import MigrationReport
from pydantic_v2_porter.reporting import report_to_json
from pydantic_v2_porter.runner import DEFAULT_REPORT, run_migration


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pydantic-v2-porter",
        description=(
            "Scan a repo for Pydantic v1 -> v2 migration fit in the public "
            "community edition."
        ),
    )
    parser.add_argument("path", help="Repository path to scan.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Reserved for the commercial pack. The public repo is scan-only.",
    )
    parser.add_argument(
        "--diff",
        action="store_true",
        help="Accepted for compatibility. Community scans do not emit file diffs.",
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_REPORT,
        help="Where to write the machine-generated JSON report.",
    )
    return parser


def _print_summary(report: MigrationReport) -> None:
    _write_console(f"Status: {report.status}")
    _write_console(f"Files changed: {len(report.files_changed)}")
    _write_console(f"Unsupported findings: {len(report.findings)}")
    _write_console(f"Confidence: {report.confidence:.3f}")
    if not report.transforms_applied and not report.findings:
        _write_console("No supported findings detected.")
    if report.transforms_applied:
        _write_console("Commercial pack coverage candidates:")
        for transform in report.transforms_applied:
            _write_console(f"- {transform}")
    if report.notes:
        _write_console("Notes:")
        for note in report.notes:
            _write_console(f"- {note}")


def _write_console(text: str) -> None:
    stream = sys.stdout
    encoding = stream.encoding or "utf-8"
    data = (text + "\n").encode(encoding, errors="backslashreplace")
    stream.buffer.write(data)
    stream.flush()


def _write_report(report: MigrationReport, report_path: Path) -> None:
    report_path.write_text(report_to_json(report), encoding="utf-8")


def _exit_code(report: MigrationReport, apply_requested: bool) -> int:
    if apply_requested:
        return 1
    if report.status in {"preview_only", "applied"}:
        return 0
    if report.status == "manual_review_required":
        return 2
    return 1


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)

    root = Path(args.path).resolve()
    report = run_migration(root=root, apply=args.apply, show_diff=args.diff)
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
