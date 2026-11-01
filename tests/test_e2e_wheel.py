"""Build the real wheel, install it into a throwaway venv and drive the installed script.

Nothing is mocked: this needs network access for pip to fetch the build backend.
"""

from __future__ import annotations

import os
import subprocess
import sys
import tarfile
import venv
import zipfile
from pathlib import Path

import pytest

import tabstops

from .conftest import ROOT


def _run(
    cmd: list[str], stdin: bytes = b"", *, cwd: Path | None = None
) -> subprocess.CompletedProcess[bytes]:
    env = {k: v for k, v in os.environ.items() if k != "PYTHONPATH"}
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(cmd, input=stdin, capture_output=True, env=env, cwd=cwd, timeout=120)


@pytest.mark.e2e
def test_wheel_installs_and_the_script_works(tmp_path: Path) -> None:
    dist = tmp_path / "dist"
    built = _run([sys.executable, "-m", "build", "--outdir", str(dist), str(ROOT)])
    assert built.returncode == 0, built.stderr.decode(errors="replace")
    wheels = list(dist.glob("tabstops-*.whl"))
    assert [w.name for w in wheels] == [f"tabstops-{tabstops.__version__}-py3-none-any.whl"]
    names = zipfile.ZipFile(wheels[0]).namelist()
    assert "tabstops/py.typed" in names and "tabstops/_width_data.py" in names
    assert any(n.endswith("licenses/LICENSE-UNICODE") for n in names)
    assert not [n for n in names if n.startswith(("data/", "tests/", "scripts/"))]
    assert not [n for n in names if n.endswith(".txt") and ".dist-info/" not in n]
    with tarfile.open(next(dist.glob("*.tar.gz"))) as archive:
        members = [name.split("/", 1)[-1] for name in archive.getnames()]
    assert {"LICENSE", "LICENSE-UNICODE", "GUIDE.md", "data/ucd/MANIFEST.json"} <= set(members)
    assert not any("__pycache__" in name or "CERT-" in name for name in members)
    assert not any(name.startswith("data/ucd/") and name.endswith(".txt") for name in members)

    env_dir = tmp_path / "venv"
    venv.EnvBuilder(with_pip=True, clear=True).create(env_dir)
    bindir = env_dir / ("Scripts" if os.name == "nt" else "bin")
    python = bindir / ("python.exe" if os.name == "nt" else "python")
    script = bindir / ("tabstops.exe" if os.name == "nt" else "tabstops")
    released = _run([str(python), "-m", "pip", "install", "-q", "tabstops==0.2.0"])
    assert released.returncode == 0, released.stderr.decode(errors="replace")
    probe_file = tmp_path / "consumer.py"
    probe_file.write_text(CONSUMER, encoding="utf-8")
    before = _run([str(python), "-I", str(probe_file)], cwd=tmp_path)
    assert before.returncode == 0, before.stderr
    old = _run([str(python), "-I", "-c", "import tabstops; print(tabstops.__version__)"])
    assert old.stdout.strip() == b"0.2.0"
    installed = _run([str(python), "-m", "pip", "install", "-q", "--no-index", str(wheels[0])])
    assert installed.returncode == 0, installed.stderr.decode(errors="replace")
    assert script.is_file()
    after = _run([str(python), "-I", str(probe_file)], cwd=tmp_path)
    assert (after.returncode, after.stdout) == (0, before.stdout), after.stderr
    differences = _run([str(python), "-I", "-c", CHANGES], cwd=tmp_path)
    assert differences.returncode == 0, differences.stderr

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
    shown = _run([str(python), "-I", "-c", probe], cwd=tmp_path).stdout.decode()
    assert shown.startswith("a  b ") and str(env_dir) in shown
    for args in (["expand"], ["--help"], ["--version"]):
        process = subprocess.Popen(
            [str(python), "-I", "-m", "tabstops", *args],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=tmp_path,
        )
        assert process.stdout is not None
        process.stdout.close()
        process.stdout = None
        _, errors = process.communicate(
            b"\tx\n" * 100_000 if args == ["expand"] else b"", timeout=30
        )
        assert process.returncode == 1
        assert b"Traceback" not in errors and b"Exception ignored" not in errors


CONSUMER = """import inspect, json, random
import tabstops as t
rng = random.Random(1000)
results = []
for _ in range(2000):
    text = "".join(rng.choices("ab  \\t\\n\\r\\b中\\u0301", k=rng.randrange(80)))
    tabs = rng.choice([1, 4, 8, "2,4,/8", "1,+8", "4,8"])
    for mode in ("chars", "display"):
        for posix in (False, True):
            results.append(t.expand(text, tabs, width=mode, posix=posix))
            results.append(t.unexpand(text, tabs, all=True, width=mode, posix=posix))
    results.append(t.display_width(text))
print(json.dumps(results, ensure_ascii=True))
print([(n, str(inspect.signature(getattr(t, n)))) for n in t.__all__ if callable(getattr(t, n))])
"""

CHANGES = """import tabstops as t
assert t.__version__ == "1.0.0"
assert not hasattr(t, "annotations")
for value, kind in [(-1, ValueError), (True, TypeError), (1.5, TypeError)]:
    try:
        t.TabStops().next_stop(value)
    except kind:
        pass
    else:
        raise AssertionError(value)
try:
    t.TabStops.parse("private-token" * 1000)
except ValueError as error:
    assert "private-token" not in str(error) and len(str(error)) < 100
"""
