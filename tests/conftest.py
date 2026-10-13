"""Shared test helpers: the fetched Unicode data and the GNU coreutils oracle."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from functools import cache
from pathlib import Path
from typing import Any

import pytest

ROOT = Path(__file__).resolve().parent.parent
UCD = ROOT / "data" / "ucd"
MANIFEST: dict[str, dict[str, Any]] = json.loads(
    (UCD / "MANIFEST.json").read_text(encoding="utf-8")
)

needs_ucd = pytest.mark.skipif(
    not all((UCD / name).is_file() for name in MANIFEST),
    reason="Unicode data not fetched; run python scripts/fetch_upstream.py",
)


@cache
def gnu(tool: str) -> tuple[str, ...] | None:
    """Return the command that runs GNU ``expand`` or ``unexpand``, or None if absent.

    Debian and Ubuntu with the Rust coreutils keep GNU as ``gnuexpand``; on Windows the
    same programs are reached through WSL.
    """
    prefixes: list[tuple[str, ...]] = []
    if os.name == "nt":
        if shutil.which("wsl"):
            prefixes += [("wsl", "-e", f"gnu{tool}"), ("wsl", "-e", tool)]
    else:
        prefixes += [(name,) for name in (f"gnu{tool}", tool) if shutil.which(name)]
    for prefix in prefixes:
        try:
            done = subprocess.run(
                [*prefix, "--version"], capture_output=True, timeout=60, check=False
            )
        except (OSError, subprocess.TimeoutExpired):
            continue
        if done.returncode == 0 and b"GNU coreutils" in done.stdout:
            return prefix
    return None


def run_gnu(tool: str, args: list[str], data: bytes) -> bytes:
    """Run the GNU tool on ``data`` and return its output; fail on a non-zero exit."""
    prefix = gnu(tool)
    assert prefix is not None
    done = subprocess.run([*prefix, *args], input=data, capture_output=True, timeout=120)
    assert done.returncode == 0, done.stderr.decode(errors="replace")
    return done.stdout
