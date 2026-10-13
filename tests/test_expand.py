from __future__ import annotations

import pytest

from tabstops import Expander, expand


# Python documentation, str.expandtabs (fetched 2026-10-13):
# https://docs.python.org/3/library/stdtypes.html#str.expandtabs
@pytest.mark.parametrize(
    ("text", "tabsize", "expected"),
    [
        ("01\t012\t0123\t01234", 8, "01      012     0123    01234"),
        ("01\t012\t0123\t01234", 4, "01  012 0123    01234"),
        ("01\t012\n0123\t01234", 4, "01  012\n0123    01234"),
    ],
)
def test_the_examples_of_the_python_documentation(text: str, tabsize: int, expected: str) -> None:
    assert expand(text, tabsize) == expected
    assert Expander(tabsize).feed(text) == expected


def test_expand_defaults_to_eight_columns() -> None:
    assert expand("a\tb") == "a       b"


def test_both_line_ends_restart_the_column_by_default() -> None:
    assert Expander(4).feed("ab\r\tc\nab\tc") == "ab\r    c\nab  c"


def test_zero_tab_size_drops_tabs() -> None:
    assert expand("a\tb", 0) == "ab"
    assert Expander(0, posix=True).feed("a\t\tb") == "ab"


@pytest.mark.parametrize("engine", [False, True])
def test_negative_tab_size_is_rejected(engine: bool) -> None:
    with pytest.raises(ValueError):
        Expander(-1) if engine else expand("a\tb", -1)


def test_a_float_zero_is_not_a_tab_size() -> None:
    with pytest.raises(TypeError):
        expand("a\tb", 0.0)  # type: ignore[arg-type]


@pytest.mark.parametrize("value", [b"a\tb", None, 3])
def test_expand_rejects_non_text(value: object) -> None:
    with pytest.raises(TypeError):
        expand(value)  # type: ignore[arg-type]
    with pytest.raises(TypeError):
        expand(value, "4,8")  # type: ignore[arg-type]


def test_a_list_places_tabs_on_the_listed_columns() -> None:
    assert expand("a\tb\tc", [3, 10]) == "a  b      c"


def test_a_tab_past_the_last_listed_stop_becomes_one_space() -> None:
    assert expand("a\tb\tc\td\te", "4,8") == "a   b   c d e"


def test_tails_keep_placing_stops() -> None:
    assert expand("\t\t\t\tx", "2,4,/8") == " " * 16 + "x"
    assert expand("\t\t\tx", "1,+8") == " " * 17 + "x"


def test_posix_treats_carriage_return_as_a_character() -> None:
    assert expand("ab\r\tc", posix=True) == "ab\r     c"


def test_posix_backspace_moves_the_column_back() -> None:
    assert expand("abc\b\tx", posix=True) == "abc\b      x"


def test_posix_backspace_stops_at_the_line_start() -> None:
    assert expand("\b\b\tx", 4, posix=True) == "\b\b    x"


def test_without_posix_backspace_is_a_column_like_any_character() -> None:
    assert expand("abc\b\tx") == "abc\b    x"


def test_initial_expands_only_leading_tabs() -> None:
    assert expand("\ta\tb\n \tc\td", initial=True) == "        a\tb\n        c\td"


def test_initial_restarts_after_each_line_end() -> None:
    assert expand("x\t\r\ty", 4, initial=True) == "x\t\r    y"
    assert expand("x\t\r\ty", 4, initial=True, posix=True) == "x\t\r\ty"


def test_initial_stops_at_a_posix_backspace() -> None:
    assert expand("\b\tx", 4, initial=True, posix=True) == "\b\tx"


def test_display_width_counts_wide_characters_twice() -> None:
    assert expand("\u4e2d\tx", 4, width="display") == "\u4e2d  x"
    assert expand("\u4e2d\tx", 4) == "\u4e2d   x"


def test_display_width_skips_combining_marks() -> None:
    assert expand("e\u0301\tx", 4, width="display") == "e\u0301   x"


def test_ambiguous_characters_are_narrow_unless_asked() -> None:
    assert expand("\u00b1\tx", 4, width="display") == "\u00b1   x"
    assert expand("\u00b1\tx", 4, width="display", ambiguous_wide=True) == "\u00b1  x"


@pytest.mark.parametrize("kwargs", [{"ambiguous_wide": True}, {"width": "cells"}])
def test_bad_width_options_are_rejected(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        expand("a\tb", **kwargs)  # type: ignore[arg-type]


def test_the_expander_keeps_the_column_across_pieces() -> None:
    engine = Expander(4)
    assert engine.feed("ab") == "ab"
    assert engine.feed("\tc") == "  c"
    assert engine.flush() == ""
    assert engine.feed("\tc") == "    c"


def test_the_expander_rejects_non_text() -> None:
    with pytest.raises(TypeError):
        Expander().feed(b"\t")  # type: ignore[arg-type]


def test_a_negative_tab_size_names_the_problem() -> None:
    with pytest.raises(ValueError, match="negative"):
        expand("a\tb", -1)
