from __future__ import annotations

import os
import subprocess
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib
from importlib.util import find_spec
from pathlib import Path

from sa20_pack.models import ValidationCommandResult

PHASES = ("format", "typecheck", "build", "test")


def _replace_python_token(command: list[str]) -> list[str]:
    if not command:
        return command
    if command[0] == "python":
        return [sys.executable, *command[1:]]
    return command


def _is_python_module_command(
    command: list[str],
    module: str,
    *subcommands: str,
) -> bool:
    return (
        len(command) >= 3 + len(subcommands)
        and command[1] == "-m"
        and command[2] == module
        and command[3 : 3 + len(subcommands)] == list(subcommands)
    )


def _is_mutating_validation_command(command: list[str]) -> bool:
    ruff_format = _is_python_module_command(
        command,
        "ruff",
        "format",
    ) or command[:2] == ["ruff", "format"]
    black_format = _is_python_module_command(command, "black") or command[:1] == [
        "black"
    ]

    if ruff_format and "--check" not in command:
        return True
    if black_format and "--check" not in command:
        return True
    return False


def _load_validation_config(root: Path) -> dict[str, list[str]]:
    pyproject_path = root / "pyproject.toml"
    if not pyproject_path.exists():
        return {}

    data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
    tool_section = data.get("tool", {})
    sa20_section = tool_section.get("sa20_pack", {})
    validation_section = sa20_section.get("validation", {})
    commands: dict[str, list[str]] = {}

    for phase in PHASES:
        raw_value = validation_section.get(phase)
        if isinstance(raw_value, list) and all(
            isinstance(item, str) for item in raw_value
        ):
            commands[phase] = list(raw_value)

    return commands


def detect_validation_commands(root: Path) -> dict[str, list[str]]:
    configured = _load_validation_config(root)
    if configured:
        return configured

    commands: dict[str, list[str]] = {}

    if find_spec("ruff") is not None and (root / "pyproject.toml").exists():
        commands["format"] = ["python", "-m", "ruff", "format", "--check", "."]
    if find_spec("mypy") is not None and (
        (root / "pyproject.toml").exists() or (root / "mypy.ini").exists()
    ):
        commands["typecheck"] = ["python", "-m", "mypy", "."]
    if find_spec("build") is not None and (root / "pyproject.toml").exists():
        commands["build"] = ["python", "-m", "build", "--no-isolation"]
    if find_spec("pytest") is not None and (root / "tests").exists():
        commands["test"] = ["python", "-m", "pytest"]

    return commands


def run_validation(root: Path) -> list[ValidationCommandResult]:
    commands = detect_validation_commands(root)
    results: list[ValidationCommandResult] = []
    temp_root = root / "sa20_tmp"
    temp_root.mkdir(exist_ok=True)
    env = os.environ.copy()
    env["TMP"] = str(temp_root)
    env["TEMP"] = str(temp_root)
    env["TMPDIR"] = str(temp_root)
    env["RUFF_CACHE_DIR"] = str(root / "ruff_cache")
    env["MYPY_CACHE_DIR"] = str(root / "mypy_cache")
    env["PYTHONPYCACHEPREFIX"] = str(root / "pycache")

    for phase in PHASES:
        command = commands.get(phase)
        if command is None:
            results.append(
                ValidationCommandResult(
                    phase=phase,
                    command=[],
                    returncode=0,
                    skipped=True,
                    note="No validation command detected",
                )
            )
            continue

        normalized = _replace_python_token(command)
        if phase == "format" and _is_mutating_validation_command(normalized):
            results.append(
                ValidationCommandResult(
                    phase=phase,
                    command=normalized,
                    returncode=1,
                    note=(
                        "Mutating format validation commands are not allowed. "
                        "Use a check-only formatter command."
                    ),
                )
            )
            continue
        completed = subprocess.run(
            normalized,
            cwd=root,
            check=False,
            capture_output=True,
            env=env,
            text=True,
        )
        results.append(
            ValidationCommandResult(
                phase=phase,
                command=normalized,
                returncode=completed.returncode,
                stdout=completed.stdout,
                stderr=completed.stderr,
            )
        )

    return results
