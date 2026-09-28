"""Reproduce a bounded commercial/free comparison without publishing engines."""

from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", type=Path, required=True)
    args = parser.parse_args()
    work = ROOT / "test_runs" / ("pydantic-case-" + uuid.uuid4().hex[:8])
    work.mkdir(parents=True)
    output = ROOT / "site" / "proof" / "pydantic-v2-porter" / "case-study"
    output.mkdir(parents=True, exist_ok=True)
    records: list[dict] = []
    env = dict(os.environ)
    env.pop("PYTHONPATH", None)
    env["PYTHONIOENCODING"] = "utf-8"

    def run(
        command: list[str], cwd: Path, label: str, expected: tuple = (0,)
    ) -> subprocess.CompletedProcess:
        result = subprocess.run(
            command, cwd=cwd, env=env, capture_output=True, text=True
        )
        (work / (label + ".txt")).write_text(
            result.stdout + result.stderr, encoding="utf-8"
        )
        records.append({"step": label, "exit_code": result.returncode})
        if result.returncode not in expected:
            raise RuntimeError(f"{label} failed; see {work / (label + '.txt')}")
        return result

    def environment(name: str, deps: list[str]) -> str:
        target = work / name
        run([sys.executable, "-m", "venv", str(target)], work, name + "-venv")
        exe = str(target / ("Scripts/python.exe" if os.name == "nt" else "bin/python"))
        run([exe, "-m", "pip", "install", *deps], work, name + "-install")
        return exe

    fixture = ROOT / "proof" / "fastapi-orders"
    for name in ("baseline", "paid", "free"):
        shutil.copytree(fixture, work / name)
    shared = ["httpx==0.28.1", "pytest==8.4.2"]
    old = environment("v1", ["fastapi==0.119.0", "pydantic==1.10.24", *shared])
    new = environment(
        "v2",
        ["fastapi==0.119.0", "pydantic==2.12.0", "pydantic-settings==2.11.0", *shared],
    )
    tool = environment("paid-tool", [str(args.pack.resolve())])
    free = environment(
        "free-tool", ["bump-pydantic==0.8.0", "typer==0.12.5", "click==8.1.8"]
    )
    scanner = environment(
        "scanner",
        [
            "https://github.com/zippertools/sqlalchemy-14-to-20-codemod/archive/refs/tags/v0.1.2.zip#subdirectory=products/pydantic-v2-porter"
        ],
    )
    baseline = run(
        [old, "-m", "pytest", "-q", "test_app.py"], work / "baseline", "baseline-tests"
    )
    (output / "baseline-tests.txt").write_text(
        (baseline.stdout + baseline.stderr).replace(str(work), "<proof-workspace>"),
        encoding="utf-8",
    )
    run(
        [scanner, "-m", "pydantic_v2_porter.cli", ".", "--report", "scan.json"],
        work / "paid",
        "public-scan",
        (0, 2),
    )
    run(
        [
            tool,
            "-m",
            "pydantic_v2_porter.cli",
            ".",
            "--diff",
            "--report",
            "preview.json",
        ],
        work / "paid",
        "paid-preview",
        (0, 2),
    )
    for path in fixture.rglob("*.py"):
        assert (
            path.read_bytes()
            == (work / "paid" / path.relative_to(fixture)).read_bytes()
        )
    run(
        [
            tool,
            "-m",
            "pydantic_v2_porter.cli",
            ".",
            "--apply",
            "--diff",
            "--report",
            "paid.json",
        ],
        work / "paid",
        "paid-apply",
        (0, 2),
    )
    # The free tool expects paths relative to its working directory.
    run([free, "-m", "bump_pydantic", "."], work / "free", "free-apply")
    outcomes = {}
    for name in ("paid", "free"):
        result = run(
            [new, "-m", "pytest", "-q", "test_app.py"],
            work / name,
            name + "-tests",
            (0, 1, 2),
        )
        diff = ""
        changed = []
        for path in sorted(fixture.rglob("*.py")):
            rel = path.relative_to(fixture)
            before = path.read_text(encoding="utf-8")
            after = (work / name / rel).read_text(encoding="utf-8")
            if before != after:
                changed.append(rel.as_posix())
                diff += "".join(
                    difflib.unified_diff(
                        before.splitlines(True),
                        after.splitlines(True),
                        fromfile="before/" + rel.as_posix(),
                        tofile=name + "/" + rel.as_posix(),
                    )
                )
        (output / (name + ".diff")).write_text(diff, encoding="utf-8")
        # Test output contains no customer input; replace machine-specific paths.
        (output / (name + "-tests.txt")).write_text(
            (result.stdout + result.stderr).replace(str(work), "<proof-workspace>"),
            encoding="utf-8",
        )
        outcomes[name] = {
            "tests_passed": result.returncode == 0,
            "files_changed": changed,
            "unsupported_file_unchanged": (
                work / name / "manual_review.py"
            ).read_bytes()
            == (fixture / "manual_review.py").read_bytes(),
        }
    for name in ("scan", "preview", "paid"):
        report = json.loads(
            (work / "paid" / (name + ".json")).read_text(encoding="utf-8")
        )
        report["root_path"] = "fastapi-orders"
        (output / (name + ".json")).write_text(
            json.dumps(report, indent=2), encoding="utf-8"
        )
    with zipfile.ZipFile(
        output / "example-source.zip", "w", zipfile.ZIP_DEFLATED
    ) as archive:
        for path in sorted(fixture.rglob("*")):
            if path.is_file() and (
                path.suffix in {".py", ".md"} or path.name == "LICENSE"
            ):
                archive.write(
                    path, "fastapi-orders/" + path.relative_to(fixture).as_posix()
                )
    locks = {}
    for name, exe in (
        ("v1", old),
        ("v2", new),
        ("paid-tool", tool),
        ("free-tool", free),
        ("scanner", scanner),
    ):
        freeze = run(
            [exe, "-m", "pip", "list", "--format=json"], work, name + "-versions"
        )
        locks[name] = json.loads(freeze.stdout)
    summary = {
        "recorded_at": datetime.now(timezone.utc).isoformat(),
        "fixture": "Original synthetic FastAPI application, not customer evidence",
        "fixture_hashes": {
            p.relative_to(fixture).as_posix(): hashlib.sha256(
                p.read_bytes()
            ).hexdigest()
            for p in sorted(fixture.rglob("*.py"))
        },
        "python": sys.version.split()[0],
        "dependencies": locks,
        "outcomes": outcomes,
        "steps": records,
        "limitations": [
            "One small app; no time savings or full migration claim.",
            "Dependency upgrades performed by harness.",
            "Unsupported module scanned but not imported by app tests.",
            "Paid engine requires purchased ZIP to reproduce; "
            "free comparison is public.",
        ],
    }
    (output / "results.json").write_text(
        json.dumps(summary, indent=2), encoding="utf-8"
    )
    print(json.dumps({"work": str(work), "outcomes": outcomes}))
    if (
        not outcomes["paid"]["tests_passed"]
        or not outcomes["paid"]["unsupported_file_unchanged"]
    ):
        raise RuntimeError("Paid proof gate failed")


if __name__ == "__main__":
    main()
