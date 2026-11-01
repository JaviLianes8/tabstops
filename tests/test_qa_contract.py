"""Hand-written contracts for integer boundaries, diagnostics and streaming state."""

from __future__ import annotations

import os
import subprocess
import sys
from collections.abc import Iterator

import pytest

from tabstops import Expander, TabStops, Unexpander, expand, expand_stream, unexpand

from .conftest import ROOT


@pytest.mark.parametrize("tabs", [2**31 - 1, 2**31, 2**63, 10**100])
@pytest.mark.parametrize("text", ["", "x", "x\r\ny\b"])
def test_large_integer_expansion_without_tabs(tabs: int, text: str) -> None:
    assert expand(text, tabs) == text
    assert expand(text, TabStops(tabs)) == text
    assert Expander(tabs).feed(text) == text
    assert list(expand_stream([text], tabs)) == [text]


def test_large_integer_expansion_rejects_impossible_output_size() -> None:
    # Exceed Py_ssize_t so expansion fails before attempting a huge allocation.
    with pytest.raises((OverflowError, MemoryError)):
        expand("\t", 2**100)


def test_large_integer_expansion_rejects_non_text() -> None:
    with pytest.raises(TypeError):
        expand(None, 2**100)  # type: ignore[arg-type]


@pytest.mark.parametrize("prefix", ["", "\t", "\tx", "\t\b"])
def test_large_interval_blank_work_is_bounded(monkeypatch: pytest.MonkeyPatch, prefix: str) -> None:
    calls = 0
    original = TabStops.next_stop

    def counted(stops: TabStops, column: int) -> int | None:
        nonlocal calls
        calls += 1
        return original(stops, column)

    monkeypatch.setattr(TabStops, "next_stop", counted)
    engine = Unexpander(10**16000, all=True, posix=True)
    pieces = [prefix, " " * 8000, " " * 8000]
    result = "".join(engine.feed(piece) for piece in pieces) + engine.flush()
    expected = "\t\b\t" + " " * 15999 if prefix == "\t\b" else "".join(pieces)
    assert result == expected
    # Advancing within one interval must not repeat arbitrary-precision stop arithmetic.
    assert calls <= 4


def test_constructor_does_not_echo_unsupported_container_type() -> None:
    value = type("private-token-" + "x" * 10000, (), {})()
    with pytest.raises(TypeError) as raised:
        TabStops(stops=value)
    assert str(raised.value) == "stops must be an iterable of ints"


def test_constructor_preserves_iterator_exceptions() -> None:
    error = TypeError("custom iterator failure")

    def values() -> Iterator[int]:
        raise error
        yield 4

    with pytest.raises(TypeError) as raised:
        TabStops(stops=values())  # type: ignore[arg-type]
    assert raised.value is error


def test_constructor_keeps_legacy_sequence_protocol() -> None:
    class Stops:
        def __getitem__(self, index: int) -> int:
            return (4, 8)[index]

    assert TabStops(stops=Stops()).stops == (4, 8)  # type: ignore[arg-type]


@pytest.mark.parametrize("relative", [False, True])
def test_large_listed_stops_keep_local_offsets_and_resets(relative: bool) -> None:
    big = 10**100
    stops = TabStops(8, (big, big + 4), relative)
    text = "\t    x\b     \n\t    "
    tail = "     " if relative else "\t "
    assert unexpand(text, stops, all=True, posix=True) == "\t\tx\b" + tail + "\n\t\t"


def test_initial_expander_starts_over_after_flush() -> None:
    engine = Expander(4, initial=True)
    assert engine.feed("x") == "x"
    assert engine.flush() == ""
    assert engine.feed("\t") == "    "


@pytest.mark.parametrize(
    ("chunks", "tabs", "expected"),
    [([""], 4, [""]), (["\t"], 0, [""]), (["", "x", "\t", ""], 0, ["", "x", "", ""])],
)
def test_expand_stream_preserves_empty_results(
    chunks: list[str], tabs: int, expected: list[str]
) -> None:
    assert list(expand_stream(chunks, tabs)) == expected


@pytest.mark.parametrize("wide", [False, True])
def test_cli_unexpand_ambiguous_width(wide: bool) -> None:
    args = [sys.executable, "-B", "-m", "tabstops", "unexpand", "-t", "4", "--display"]
    if wide:
        args.append("--ambiguous-wide")
    env = {**os.environ, "PYTHONPATH": str(ROOT / "src")}
    done = subprocess.run(
        args, input="\u00b1  x".encode(), capture_output=True, env=env, timeout=30
    )
    assert done.returncode == 0, done.stderr
    assert done.stdout == ("\u00b1\tx" if wide else "\u00b1  x").encode()
