"""Regression tests for the findings of the independent review of the 0.2.0 round."""

from __future__ import annotations

import io
import subprocess
import sys
from pathlib import Path

import pytest

from tabstops import expand, expand_stream, unexpand, unexpand_stream
from tabstops._cli import main

from .conftest import ROOT, gnu, run_gnu
from .test_cli import run_cli


def test_columns_are_characters_not_bytes() -> None:
    # GNU expand 9.7 counts the two UTF-8 bytes of the accent as two columns; this
    # library counts characters, as documented in the README.
    assert expand("é\tx", posix=True) == "é" + " " * 7 + "x"
    assert run_cli(["expand"], "é\tx".encode()) == (0, ("é" + " " * 7 + "x").encode())


@pytest.mark.skipif(gnu("expand") is None, reason="GNU expand not installed")
def test_the_byte_counting_of_gnu_is_the_documented_difference() -> None:
    assert run_gnu("expand", [], "é\tx".encode()) == ("é" + " " * 6 + "x").encode()


def test_repeated_tab_lists_are_joined() -> None:
    assert run_cli(["expand", "-t", "4", "-t", "10"], b"\ta\tb\tc\n") == (
        0,
        b"    a     b c\n",
    )
    assert run_cli(["unexpand", "-t", "2", "--tabs", "4"], b"    x\n") == (0, b"\t\tx\n")


@pytest.mark.skipif(gnu("expand") is None, reason="GNU expand not installed")
def test_repeated_tab_lists_match_gnu() -> None:
    data = b"\ta\tb\tc\n"
    assert run_cli(["expand", "-t", "4", "-t", "10"], data)[1] == run_gnu(
        "expand", ["-t", "4", "-t", "10"], data
    )


def test_a_bad_list_among_repeated_ones_is_a_usage_error() -> None:
    with pytest.raises(SystemExit) as raised:
        run_cli(["expand", "-t", "8", "-t", "4"])
    assert raised.value.code == 2


@pytest.mark.parametrize("tabs", [b"\x03\x06", bytearray(b"\x03\x06")])
def test_bytes_are_not_a_tab_stop_list(tabs: bytes) -> None:
    with pytest.raises(TypeError):
        expand("a\tb\tc", tabs)
    with pytest.raises(TypeError):
        unexpand("    x", tabs)


@pytest.mark.parametrize("stream", [expand_stream, unexpand_stream])
def test_streams_check_their_arguments_at_the_call(stream: object) -> None:
    with pytest.raises(ValueError):
        stream(["a\tb"], "8,4")  # type: ignore[operator]
    with pytest.raises(TypeError):
        stream(["a\tb"], None)  # type: ignore[operator]


@pytest.mark.parametrize("stream", [expand_stream, unexpand_stream])
def test_streams_reject_a_piece_that_is_not_text(stream: object) -> None:
    pieces = stream(["a", b"\t"], 4)  # type: ignore[operator]
    assert next(pieces) == "a"
    with pytest.raises(TypeError):
        next(pieces)


class _ClosedPipe(io.RawIOBase):
    """An output whose reader has gone away, until ``mend`` lets the test clean up."""

    broken = True

    def writable(self) -> bool:
        return True

    def write(self, data: object) -> int:
        if self.broken:
            raise BrokenPipeError(32, "Broken pipe")
        return len(data)  # type: ignore[arg-type]

    @classmethod
    def stdout(cls, monkeypatch: pytest.MonkeyPatch) -> _ClosedPipe:
        pipe = cls()
        monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(io.BufferedWriter(pipe)))
        return pipe


def test_a_closed_output_ends_quietly(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"\tx\n")))
    pipe = _ClosedPipe.stdout(monkeypatch)
    assert main(["expand"]) == 1
    pipe.broken = False
    assert capsys.readouterr().err == ""


def test_a_closed_output_is_not_blamed_on_the_input_file(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    source = tmp_path / "in.txt"
    source.write_bytes(b"\tx\n" * 50000)
    pipe = _ClosedPipe.stdout(monkeypatch)
    assert main(["expand", str(source)]) == 1
    pipe.broken = False
    assert "in.txt" not in capsys.readouterr().err


def test_the_table_check_rejects_a_changed_data_file(tmp_path: Path) -> None:
    script = (ROOT / "scripts" / "gen_width_table.py").read_text(encoding="utf-8")
    copy = tmp_path / "scripts" / "gen_width_table.py"
    copy.parent.mkdir()
    copy.write_text(script, encoding="utf-8")
    data = tmp_path / "data" / "ucd"
    data.mkdir(parents=True)
    manifest = (ROOT / "data" / "ucd" / "MANIFEST.json").read_text(encoding="utf-8")
    (data / "MANIFEST.json").write_text(manifest, encoding="utf-8")
    run = [sys.executable, "-B", str(copy), "--check"]
    skipped = subprocess.run(run, capture_output=True, text=True)
    assert (skipped.returncode, skipped.stdout.split(":")[0]) == (0, "SKIPPED")
    for name in ("DerivedEastAsianWidth.txt", "DerivedGeneralCategory.txt"):
        (data / name).write_text("# not the pinned file\n", encoding="utf-8")
    changed = subprocess.run(run, capture_output=True, text=True)
    assert changed.returncode == 1
    assert "differs from the sha256" in changed.stdout
