from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class TransformApplication:
    transform_id: str
    description: str
    confidence: float
    occurrences: int


@dataclass(frozen=True)
class ManualReviewFinding:
    code: str
    message: str
    line: int | None = None
    confidence: float = 1.0


@dataclass(frozen=True)
class ValidationCommandResult:
    phase: str
    command: list[str]
    returncode: int
    stdout: str = ""
    stderr: str = ""
    skipped: bool = False
    note: str | None = None

    @property
    def success(self) -> bool:
        return self.skipped or self.returncode == 0


@dataclass(frozen=True)
class FileMigrationResult:
    path: str
    changed: bool
    transforms: list[TransformApplication] = field(default_factory=list)
    findings: list[ManualReviewFinding] = field(default_factory=list)
    diff: str | None = None
    parse_error: str | None = None

    @property
    def confidence(self) -> float:
        weighted_occurrences = sum(item.occurrences for item in self.transforms)
        if weighted_occurrences == 0:
            return 0.0

        total = sum(item.confidence * item.occurrences for item in self.transforms)
        return round(total / weighted_occurrences, 3)


@dataclass(frozen=True)
class MigrationReport:
    root_path: str
    mode: str
    created_at: str
    files_scanned: int
    file_results: list[FileMigrationResult]
    validation_results: list[ValidationCommandResult]

    @property
    def files_changed(self) -> list[str]:
        return [item.path for item in self.file_results if item.changed]

    @property
    def transform_count(self) -> int:
        return sum(
            transform.occurrences
            for file_result in self.file_results
            for transform in file_result.transforms
        )

    @property
    def unsupported_count(self) -> int:
        return sum(len(item.findings) for item in self.file_results)

    @property
    def validation_passed(self) -> bool:
        executed = [item for item in self.validation_results if not item.skipped]
        return bool(executed) and all(item.success for item in executed)

    @property
    def parse_error_count(self) -> int:
        return sum(1 for item in self.file_results if item.parse_error is not None)

    @property
    def overall_confidence(self) -> float:
        scored_files = [
            item.confidence for item in self.file_results if item.confidence > 0
        ]
        if not scored_files:
            return 0.0
        return round(sum(scored_files) / len(scored_files), 3)

    @property
    def manual_todos(self) -> list[str]:
        todos: list[str] = []
        for file_result in self.file_results:
            for finding in file_result.findings:
                prefix = f"{file_result.path}"
                if finding.line is not None:
                    prefix = f"{prefix}:{finding.line}"
                todos.append(f"{prefix} - {finding.message}")
        return todos

    @property
    def status(self) -> str:
        if self.parse_error_count > 0:
            return "parse_error"
        if self.mode == "apply" and not any(
            not item.skipped for item in self.validation_results
        ):
            return "validation_not_run"
        if self.mode == "apply" and not self.validation_passed:
            return "validation_failed"
        if self.unsupported_count > 0:
            return "manual_review_required"
        if self.mode == "dry-run":
            return "preview_only"
        return "validated"
