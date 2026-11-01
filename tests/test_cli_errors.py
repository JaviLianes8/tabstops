"""Bounded diagnostics and real input/output failure contracts."""

from __future__ import annotations

import io
import sys
from pathlib import Path

import pytest

from tabstops._cli import main

from .test_cli import run_cli


def test_unknown_arguments_do_not_echo_values(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        run_cli(["expand", "--private-token-" + "x" * 100_000])
    assert raised.value.code == 2
    error = capsys.readouterr().err
    assert "private-token" not in error and len(error) < 500


def test_bad_tab_lists_do_not_echo_values(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as raised:
        run_cli(["expand", "-t", "private-token-" + "x" * 100_000])
    assert raised.value.code == 2
    error = capsys.readouterr().err
    assert "private-token" not in error and len(error) < 100


def test_missing_path_reports_only_bounded_basename(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "private-token" / ("x" * 200)
    assert run_cli(["expand", str(path)]) == (1, b"")
    error = capsys.readouterr().err
    assert "private-token" not in error and len(error) < 100


class _Unreadable(io.BytesIO):
    def read(self, size: int | None = -1) -> bytes:
        raise OSError("private-token")


def test_read_failure_has_status_one_and_safe_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(_Unreadable()))
    assert main(["expand"]) == 1
    assert capsys.readouterr().err == "tabstops: input/output operation failed\n"


class _Unwritable(io.BytesIO):
    def write(self, data: object) -> int:
        raise OSError("private-token")


def test_write_failure_has_status_one_and_safe_message(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(sys, "stdin", io.TextIOWrapper(io.BytesIO(b"x")))
    monkeypatch.setattr(sys, "stdout", io.TextIOWrapper(_Unwritable()))
    assert main(["expand"]) == 1
    assert capsys.readouterr().err == "tabstops: input/output operation failed\n"
