from sa20_pack.models import MigrationReport, ValidationCommandResult


def report(results: list[ValidationCommandResult]) -> MigrationReport:
    return MigrationReport("fixture", "apply", "2026-09-26", 0, [], results)


def test_empty_validation_does_not_claim_success() -> None:
    result = report([])
    assert not result.validation_passed
    assert result.status == "validation_not_run"


def test_skipped_validation_does_not_claim_success() -> None:
    result = report([ValidationCommandResult("test", [], 0, skipped=True)])
    assert not result.validation_passed
    assert result.status == "validation_not_run"


def test_executed_validation_preserves_pass_and_failure() -> None:
    assert report([ValidationCommandResult("test", ["pytest"], 0)]).status == (
        "validated"
    )
    assert report([ValidationCommandResult("test", ["pytest"], 1)]).status == (
        "validation_failed"
    )
