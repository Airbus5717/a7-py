"""Regression tests for C backend code generation."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

from src.backends import get_backend, list_backends
from src.compile import ExitCode


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MAIN_PY = PROJECT_ROOT / "main.py"


def run_cli(args: list[str]) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    existing_pythonpath = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = (
        f"{PROJECT_ROOT}:{existing_pythonpath}" if existing_pythonpath else str(PROJECT_ROOT)
    )
    return subprocess.run(
        [sys.executable, str(MAIN_PY), *args],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        env=env,
    )


def has_zig() -> bool:
    try:
        result = subprocess.run(
            ["zig", "version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def test_backend_registry_exposes_c_backend() -> None:
    backend = get_backend("c")
    assert backend.file_extension == ".c"
    assert backend.language_name == "C"
    assert "c" in list_backends()


def test_cli_backend_c_default_output_extension(tmp_path: Path) -> None:
    src = tmp_path / "hello.a7"
    src.write_text(
        """
io :: import "std/io"

main :: fn() {
    io.println("hello")
}
""".strip(),
        encoding="utf-8",
    )

    result = run_cli(["--backend", "c", str(src)])
    assert result.returncode == ExitCode.SUCCESS, result.stdout + result.stderr
    assert src.with_suffix(".c").exists()


@pytest.mark.skipif(not has_zig(), reason="zig not installed")
def test_generated_c_passes_zig_cc_syntax_check(tmp_path: Path) -> None:
    src = tmp_path / "math_io.a7"
    out = tmp_path / "math_io.c"
    src.write_text(
        """
io :: import "std/io"
math :: import "std/math"

main :: fn() {
    x := 9.0
    io.println("sqrt({}) = {}", x, math.sqrt(x))
}
""".strip(),
        encoding="utf-8",
    )

    result = run_cli(["--backend", "c", "--output", str(out), str(src)])
    assert result.returncode == ExitCode.SUCCESS, result.stdout + result.stderr
    assert out.exists()

    syntax = subprocess.run(
        ["zig", "cc", "-std=c11", "-c", str(out), "-o", str(tmp_path / "math_io.o")],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
    )
    assert syntax.returncode == 0, syntax.stderr
