from __future__ import annotations

import json
import shutil
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from uuid import uuid4

from actions_upgrade_guard.cli import main
from actions_upgrade_guard.reporting import report_to_html, report_to_json
from actions_upgrade_guard.scanner import scan_repo

FIXTURES = Path(__file__).resolve().parents[1] / "fixtures"
TEST_RUNS = Path(__file__).resolve().parents[1] / "test_runs"


@contextmanager
def _copied_fixture(name: str) -> Iterator[Path]:
    TEST_RUNS.mkdir(exist_ok=True)
    source = FIXTURES / name
    target = TEST_RUNS / f"{name}-{uuid4().hex}"
    shutil.copytree(source, target)
    try:
        yield target
    finally:
        shutil.rmtree(target, ignore_errors=True)


def test_patchable_actions_emit_report_and_patch_preview() -> None:
    with _copied_fixture("deprecated_repo") as root:
        workflow = root / ".github" / "workflows" / "build.yml"
        before = workflow.read_text(encoding="utf-8")

        report = scan_repo(root=root, apply=False)

        assert report.status == "manual_review_required"
        assert {finding.rule_id for finding in report.findings} >= {"AUG001", "AUG002"}
        assert report.patches == []
        assert all(f.classification != "autofix" for f in report.findings)
        assert workflow.read_text(encoding="utf-8") == before

        json_report = json.loads(report_to_json(report))
        assert json_report["rule_pack_version"] == "2026.09.26"
        assert json_report["status"] == "manual_review_required"

        html_report = report_to_html(report)
        assert "Actions Upgrade Guard Report" in html_report
        assert "Artifact action v3 is retired" in html_report


def test_apply_preserves_unverified_action_upgrade_cases() -> None:
    with _copied_fixture("deprecated_repo") as root:
        workflow = root / ".github" / "workflows" / "build.yml"

        report = scan_repo(root=root, apply=True)
        updated = workflow.read_text(encoding="utf-8")

        assert report.files_changed == []
        assert "actions/upload-artifact@v3" in updated
        assert "actions/download-artifact@v3" in updated
        assert "actions/cache@v2" in updated
        assert "ubuntu-latest" in updated


def test_manual_review_repo_reports_runner_node_and_permission_risks() -> None:
    with _copied_fixture("manual_review_repo") as root:
        report = scan_repo(root=root, apply=False)

        rule_ids = {finding.rule_id for finding in report.findings}
        assert {"AUG003", "AUG004", "AUG005", "AUG007"} <= rule_ids
        assert not report.patches
        assert report.status == "manual_review_required"
        assert any(summary.local_actions == 1 for summary in report.workflow_summaries)


def test_clean_repo_is_clean_with_explicit_permissions() -> None:
    with _copied_fixture("clean_repo") as root:
        report = scan_repo(root=root, apply=False)

        assert report.status == "clean"
        assert report.findings == []
        assert report.patches == []
        assert report.workflow_summaries[0].jobs == 1


def test_invalid_yaml_fails_closed_without_crashing() -> None:
    with _copied_fixture("invalid_yaml_repo") as root:
        report = scan_repo(root=root, apply=False)

        assert report.status == "manual_review_required"
        assert report.blocking_findings[0].rule_id == "AUG000"
        assert report.patches == []


def test_cli_writes_json_and_html_reports() -> None:
    with _copied_fixture("deprecated_repo") as root:
        json_path = root / "actions-report.json"
        html_path = root / "actions-report.html"

        exit_code = main(
            [
                str(root),
                "--report",
                str(json_path),
                "--html-report",
                str(html_path),
            ]
        )

        assert exit_code == 1
        assert json_path.exists()
        assert html_path.exists()
        data = json.loads(json_path.read_text(encoding="utf-8"))
        assert data["product"] == "actions-upgrade-guard"
        assert "Legacy cache action" in html_path.read_text(encoding="utf-8")


def test_cli_missing_path_returns_scanner_error() -> None:
    exit_code = main([str(FIXTURES / "does-not-exist")])

    assert exit_code == 2


def test_no_rule_is_eligible_for_unverified_automatic_application() -> None:
    from actions_upgrade_guard.rules import RULES

    assert all(not rule.autofix for rule in RULES.values())
    assert all(rule.classification != "autofix" for rule in RULES.values())


def test_zero_findings_html_explains_supported_scope() -> None:
    with _copied_fixture("clean_repo") as root:
        rendered = report_to_html(scan_repo(root))
        assert "No supported findings detected." in rendered
        assert "not exhaustive" in rendered


def test_self_hosted_ubuntu_label_is_not_hosted_retirement() -> None:
    with _copied_fixture("clean_repo") as root:
        path = root / ".github/workflows/build.yml"
        path.write_text(
            (
                "jobs:\n  build:\n    runs-on: [self-hosted, ubuntu-20.04]"
                "\n    steps: []\n"
            ),
            encoding="utf-8",
        )
        report = scan_repo(root, apply=True)
        assert "AUG003" not in {item.rule_id for item in report.findings}
        assert not report.files_changed


def test_uncertain_artifacts_and_cache_preserve_every_byte() -> None:
    with _copied_fixture("clean_repo") as root:
        path = root / ".github/workflows/build.yml"
        original = (
            b"jobs:\r\n  build:\r\n    runs-on: self-hosted\r\n    steps:\r\n"
            b"      # uses: actions/cache@v1\r\n      - uses: actions/u"
            b"pload-artifact@v3\r\n        with: {name: shared, path: ."
            b"hidden}\r\n      - uses: actions/upload-artifact@v3\r\n    "
            b"    with: {name: shared, path: other}\r\n      - uses: ac"
            b"tions/cache@v1\r\n"
        )
        path.write_bytes(original)
        report = scan_repo(root, apply=True)
        assert path.read_bytes() == original
        assert not report.patches
        assert not report.files_changed
        assert {f.rule_id for f in report.findings} >= {"AUG001", "AUG002"}


def test_public_proof_matches_current_scanner() -> None:
    root = FIXTURES / "deprecated_repo"
    actual = json.loads(report_to_json(scan_repo(root.resolve())))
    expected = json.loads((FIXTURES.parent / "proof-report.json").read_text())
    for key in ("root_path", "created_at"):
        actual.pop(key)
        expected.pop(key)
    assert actual == expected
