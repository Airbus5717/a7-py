"""End-to-end verification for all example programs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERIFY_SCRIPT = PROJECT_ROOT / "scripts" / "verify_examples_e2e.py"


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


@pytest.mark.skipif(not has_zig(), reason="zig not installed")
def test_examples_end_to_end_outputs_match_goldens() -> None:
    result = subprocess.run(
        [sys.executable, str(VERIFY_SCRIPT)],
        cwd=PROJECT_ROOT,
        capture_output=True,
        text=True,
        timeout=180,
    )
    combined = (result.stdout or "") + (result.stderr or "")
    assert result.returncode == 0, combined
