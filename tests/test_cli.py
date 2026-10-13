from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

import tabstops
from tabstops._cli import main


def run_cli(argv: list[str], data: bytes = b"") -> tuple[int, bytes]:
    """Run the tool in process with ``data`` on stdin; return the exit code and stdout."""
    stdin = io.TextIOWrapper(io.BytesIO(data))
    stdout = io.TextIOWrapper(io.BytesIO())
    saved = sys.stdin, sys.stdout
    sys.stdin, sys.stdout = stdin, stdout
    try:
        code = main(argv)
    finally:
        sys.stdin, sys.stdout = saved
    stdout.flush()
    return code, stdout.buffer.getvalue()


def test_expand_reads_stdin() -> None:
    assert run_cli(["expand", "-t", "4"], b"a\tb\n") == (0, b"a   b\n")


def test_unexpand_converts_leading_blanks_only() -> None:
    assert run_cli(["unexpand"], b"        a        b\n") == (0, b"\ta        b\n")


def test_unexpand_tab_list_implies_all() -> None:
    assert run_cli(["unexpand", "-t", "4"], b"    x    y\n") == (0, b"\tx\t y\n")
    assert run_cli(["unexpand", "--first-only", "-t", "4"], b"    x    y\n") == (
        0,
        b"\tx    y\n",
    )


def test_the_tool_follows_posix_unless_asked_for_python() -> None:
    assert run_cli(["expand"], b"ab\r\tc") == (0, b"ab\r     c")
    assert run_cli(["expand", "--python"], b"ab\r\tc") == (0, b"ab\r        c")


def test_display_columns() -> None:
    text = "\u4e2d\tx\n".encode()
    assert run_cli(["expand", "-t", "4", "--display"], text) == (0, "\u4e2d  x\n".encode())
    assert run_cli(["expand", "-t", "4"], text) == (0, "\u4e2d   x\n".encode())
    wide = "\u00b1\tx".encode()
    assert run_cli(["expand", "-t", "4", "--display", "--ambiguous-wide"], wide) == (
        0,
        "\u00b1  x".encode(),
    )


def test_undecodable_bytes_pass_through() -> None:
    assert run_cli(["expand", "-t", "4"], b"\xff\t\xe4\xb8\n") == (0, b"\xff   \xe4\xb8\n")


def test_a_character_split_across_blocks_is_kept(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr("tabstops._cli._BLOCK", 1)
    text = "\u4e2d\tx".encode()
    assert run_cli(["expand", "-t", "4", "--display"], text) == (0, "\u4e2d  x".encode())


def test_files_are_one_stream(tmp_path: Path) -> None:
    first, second = tmp_path / "a.txt", tmp_path / "b.txt"
    first.write_bytes(b"ab")
    second.write_bytes(b"\tc\n")
    assert run_cli(["expand", "-t", "4", str(first), str(second)]) == (0, b"ab  c\n")
    assert run_cli(["expand", "-t", "4", str(first), "-"], b"\tc") == (0, b"ab  c")


def test_a_missing_file_is_reported_and_the_rest_still_runs(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    good = tmp_path / "good.txt"
    good.write_bytes(b"\tx\n")
    code, out = run_cli(["expand", "-t", "2", str(tmp_path / "nope.txt"), str(good)])
    assert (code, out) == (1, b"  x\n")
    assert "nope.txt" in capsys.readouterr().err


def test_held_blanks_are_written_at_the_end() -> None:
    assert run_cli(["unexpand", "-a"], b"abcdefg   ") == (0, b"abcdefg\t  ")


@pytest.mark.parametrize(
    "argv",
    [[], ["expand", "-t", "0"], ["expand", "-t", "8,4"], ["unexpand", "-t", ""],
     ["expand", "--ambiguous-wide"], ["expand", "-a"], ["unexpand", "-i"]],
)  # fmt: skip
def test_bad_usage_exits_2(argv: list[str], capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        run_cli(argv)
    assert raised.value.code == 2
    assert capsys.readouterr().err


def test_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        main(["--version"])
    out = capsys.readouterr().out
    assert out.strip() == f"tabstops {tabstops.__version__} (Unicode {tabstops.UNICODE_VERSION})"


def test_an_incomplete_character_at_the_end_is_kept() -> None:
    assert run_cli(["expand"], b"a\t\xe4\xb8") == (0, b"a       \xe4\xb8")


def test_ambiguous_wide_without_display_is_explained(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        run_cli(["expand", "--ambiguous-wide"])
    assert "--ambiguous-wide needs --display" in capsys.readouterr().err
