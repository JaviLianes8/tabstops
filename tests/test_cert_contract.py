"""Stable surface, bounded failures and streaming edge contracts."""

from __future__ import annotations

import doctest
import importlib
import inspect
import pickle
import random
from dataclasses import replace
from typing import get_type_hints

import pytest

import tabstops
from tabstops import Expander, TabStops, Unexpander, expand, unexpand


def test_public_callable_examples_run() -> None:
    attempted = 0
    for name in ("", "._stops", "._expand", "._unexpand", "._width"):
        result = doctest.testmod(importlib.import_module("tabstops" + name))
        assert result.failed == 0
        attempted += result.attempted
    assert attempted == 19
    for name in tabstops.__all__:
        value = getattr(tabstops, name)
        if callable(value):
            assert ">>>" in (inspect.getdoc(value) or "")
            target = value.__init__ if inspect.isclass(value) else value
            assert get_type_hints(target)


def test_no_accidental_top_level_exports() -> None:
    assert {name for name in vars(tabstops) if not name.startswith("_")} == set(tabstops.__all__)


def test_tab_stops_copy_pickle_and_replace() -> None:
    stops = TabStops.parse("1,+8")
    assert replace(stops, every=3).next_stop(1) == 4
    for protocol in range(pickle.HIGHEST_PROTOCOL + 1):
        restored = pickle.loads(pickle.dumps(stops, protocol))
        assert restored == stops and restored.next_stop(9) == 17


@pytest.mark.parametrize("column", [True, 2.0, "2", None])
def test_next_stop_refuses_non_integer_columns(column: object) -> None:
    with pytest.raises(TypeError, match="column must be an int"):
        TabStops().next_stop(column)  # type: ignore[arg-type]


def test_next_stop_refuses_negative_columns() -> None:
    with pytest.raises(ValueError, match="column must not be negative"):
        TabStops().next_stop(-1)


def test_next_stop_accepts_arbitrary_precision_columns() -> None:
    column = 10**5000
    assert TabStops(7).next_stop(column) == column + 7 - column % 7


def test_invalid_values_are_not_echoed() -> None:
    secret = "private-token-" + "x" * 100_000
    for call in (
        lambda: TabStops.parse(secret),
        lambda: TabStops(secret),  # type: ignore[arg-type]
        lambda: expand("", width=secret),  # type: ignore[arg-type]
    ):
        with pytest.raises((TypeError, ValueError)) as raised:
            call()
        assert len(str(raised.value)) < 100
        assert "private-token" not in str(raised.value)


def test_type_names_cannot_enlarge_error_messages() -> None:
    value = type("private-token-" + "x" * 10000, (), {})()
    for call in (expand, unexpand, tabstops.char_width, tabstops.display_width, TabStops.parse):
        with pytest.raises(TypeError) as raised:
            call(value)
        assert str(raised.value) == "expected a str"


def test_large_pending_blank_run_is_retained_across_chunks() -> None:
    engine = Unexpander(2_000_001)
    for _ in range(20):
        assert engine.feed(" " * 50_000) == ""
    assert engine.flush() == " " * 1_000_000
    assert engine.feed("x") == "x"


def test_very_long_stop_list_and_hostile_parser_inputs() -> None:
    spec = ",".join(map(str, range(1, 50_001)))
    stops = TabStops.parse(spec)
    assert stops.next_stop(49_999) == 50_000
    assert stops.next_stop(50_000) is None
    rng = random.Random(1001)
    for _ in range(5000):
        text = "".join(rng.choices("0148,+/ \t\n\x00x\ud800", k=rng.randrange(70)))
        try:
            result = TabStops.parse(text)
        except ValueError as error:
            assert len(str(error)) < 100
        else:
            assert TabStops.parse(str(result)) == result


def test_bad_piece_does_not_change_engine_state() -> None:
    for engine in (Expander(4), Unexpander(4)):
        engine.feed("a")
        with pytest.raises(TypeError):
            engine.feed(None)  # type: ignore[arg-type]
        assert engine.feed("\t") == ("   " if isinstance(engine, Expander) else "\t")
