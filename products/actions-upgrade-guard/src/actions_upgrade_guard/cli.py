from __future__ import annotations

import argparse
import sys
from pathlib import Path

from actions_upgrade_guard.models import ScanReport
from actions_upgrade_guard.reporting import report_to_html, report_to_json
from actions_upgrade_guard.scanner import (
    DEFAULT_HTML_REPORT,
    DEFAULT_JSON_REPORT,
    scan_repo,
)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="actions-upgrade-guard",
        description=(
            "Scan GitHub Actions workflows for deadline-sensitive breakage, "
            "runner drift, permissions risk, and deterministic patch previews."
        ),
    )
    parser.add_argument("path", help="Repository path to scan.")
    parser.add_argument(
        "--apply",
        action="store_true",
        help=(
            "Request eligible fixes; this rule pack has none and lea"
            "ves files unchanged."
        ),
    )
    parser.add_argument(
        "--report",
        default=DEFAULT_JSON_REPORT,
        help="Where to write the machine-readable JSON report.",
    )
    parser.add_argument(
        "--html-report",
        default=DEFAULT_HTML_REPORT,
        help="Where to write the human-readable HTML report.",
    )
    parser.add_argument(
        "--no-html",
        action="store_true",
        help="Do not write the HTML report.",
    )
    return parser


def _write_console(text: str) -> None:
    stream = sys.stdout
    encoding = stream.encoding or "utf-8"
    data = (text + "\n").encode(encoding, errors="backslashreplace")
    stream.buffer.write(data)
    stream.flush()


def _write_reports(report: ScanReport, json_path: Path, html_path: Path | None) -> None:
    json_path.write_text(report_to_json(report), encoding="utf-8")
    if html_path is not None:
        html_path.write_text(report_to_html(report), encoding="utf-8")


def _print_summary(report: ScanReport) -> None:
    _write_console(f"Status: {report.status}")
    if not report.findings:
        _write_console("No supported findings detected.")
    _write_console(f"Scanned files: {len(report.scanned_files)}")
    _write_console(f"Findings: {len(report.findings)}")
    _write_console(f"Blocking findings: {len(report.blocking_findings)}")
    _write_console(f"Patch previews: {len(report.patches)}")
    _write_console(f"Files changed: {len(report.files_changed)}")
    _write_console(f"Confidence: {report.confidence:.3f}")
    if report.blocking_findings:
        _write_console("Blocking findings:")
        for finding in report.blocking_findings:
            location = (
                f"{finding.path}:{finding.line}" if finding.line else finding.path
            )
            _write_console(f"- {finding.rule_id} {location} {finding.message}")


def _exit_code(report: ScanReport) -> int:
    return 1 if report.blocking_findings else 0


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    root = Path(args.path).resolve()
    if not root.exists() or not root.is_dir():
        _write_console(f"Scanner error: repository path does not exist: {root}")
        return 2

    try:
        report = scan_repo(root=root, apply=args.apply)
        html_path = None if args.no_html else Path(args.html_report).resolve()
        _write_reports(report, Path(args.report).resolve(), html_path)
        _print_summary(report)
        return _exit_code(report)
    except OSError as exc:
        _write_console(f"Scanner error: {exc}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
