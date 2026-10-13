"""Build the real wheel, install it into a throwaway venv and drive the installed script.

Nothing is mocked: this needs network access for pip to fetch the build backend.
"""

from __future__ import annotations

import os
import subprocess
import sys
import venv
import zipfile
from pathlib import Path

import pytest

import tabstops

from .conftest import ROOT


def _run(cmd: list[str], stdin: bytes = b"") -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, input=stdin, capture_output=True, env=env, timeout=600, check=False)


@pytest.mark.e2e
def test_wheel_installs_and_the_script_works(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run(
        [sys.executable, "-m", "pip", "wheel", "--no-deps", "-q", "-w", str(dist), str(ROOT)]
    )
    assert built.returncode == 0, built.stderr.decode(errors="replace")
    wheels = list(dist.glob("tabstops-*.whl"))
    assert [w.name for w in wheels] == [f"tabstops-{tabstops.__version__}-py3-none-any.whl"]
    names = zipfile.ZipFile(wheels[0]).namelist()
    assert "tabstops/py.typed" in names and "tabstops/_width_data.py" in names
    assert any(n.endswith("licenses/LICENSE-UNICODE") for n in names)
    assert not [n for n in names if n.startswith(("data/", "tests/", "scripts/"))]
    assert not [n for n in names if n.endswith(".txt") and ".dist-info/" not in n]

    env_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    bindir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bindir / ("python.exe" if os.name == "nt" else "python")
    script = bindir / ("tabstops.exe" if os.name == "nt" else "tabstops")
    installed = _run([str(python), "-m", "pip", "install", "-q", "--no-index", str(wheels[0])])
    assert installed.returncode == 0, installed.stderr.decode(errors="replace")
    assert script.is_file()

    done = _run([str(script), "expand", "-t", "2,4,/8"], b"\t\t\tx\r\n")
    assert (done.returncode, done.stdout) == (0, b"        x\r\n")
    done = _run([str(script), "unexpand", "-t", "4"], b"    x    y\n")
    assert (done.returncode, done.stdout) == (0, b"\tx\t y\n")
    done = _run([str(script), "expand", "--display", "-t", "4"], "\u4e2d\tx\n".encode())
    assert done.stdout == "\u4e2d  x\n".encode()
    done = _run([str(python), "-m", "tabstops", "expand", "--python"], b"ab\r\t\xffc")
    assert done.stdout == b"ab\r        \xffc"
    failed = _run([str(script), "expand", "-t", "8,4"])
    assert failed.returncode == 2 and b"ascending" in failed.stderr and failed.stdout == b""
    missing = _run([str(script), "unexpand", str(tmp_path / "missing.txt")])
    assert missing.returncode == 1 and b"missing.txt" in missing.stderr
    version = _run([str(script), "--version"])
    assert version.stdout.strip() == (
        f"tabstops {tabstops.__version__} (Unicode {tabstops.UNICODE_VERSION})".encode()
    )

    probe = "import tabstops; print(tabstops.expand('a\tb', '3,5'), tabstops.__file__)"
    shown = _run([str(python), "-c", probe]).stdout.decode()
    assert shown.startswith("a  b ") and str(env_dir) in shown
