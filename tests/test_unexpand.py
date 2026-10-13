from __future__ import annotations

import pytest

from tabstops import Unexpander, unexpand

# Outputs observed from GNU coreutils 9.7 gnuunexpand (WSL Ubuntu 26.04) on 2026-10-13,
# with the arguments shown; tests/test_gnu_oracle.py rechecks such cases live.
OBSERVED = [
    ([], " \tx", "\tx"),
    ([], "        x", "\tx"),
    ([], "       x", "       x"),
    ([], "         x", "\t x"),
    ([], "a       b", "a       b"),
    (["-a"], "a       b", "a\tb"),
    (["-a"], "abcdefg b", "abcdefg b"),
    (["-a"], "abcdef  b", "abcdef\tb"),
    (["-a"], "a  \tb", "a\tb"),
    (["-a"], "a   \n", "a   \n"),
    (["-a"], "a          \n", "a\t   \n"),
    ([], "  \t  x", "\t  x"),
    ([], "\t \tx", "\t\tx"),
    (["-t", "4,8"], "a       b          c", "a\t\tb          c"),
    (["-t", "4"], "    x    y", "\tx\t y"),
    (["--first-only", "-t", "4"], "    x    y", "\tx    y"),
    (["-a"], "x\b        y", "x\b\ty"),
    ([], "        ", "\t"),
    (["-a"], "a       ", "a\t"),
    (["-t", "2,4,/8"], " " * 18 + "x", "\t\t\t\t  x"),
    (["-t", "1,+8"], " " * 18 + "x", "\t\t\t x"),
    (["-a"], "a \t b", "a\t b"),
    (["-t", "1"], " x", "\tx"),
    (["-t", "1"], "  x", "\t\tx"),
]


def _call(args: list[str], text: str) -> str:
    tabs = args[args.index("-t") + 1] if "-t" in args else "8"
    convert_all = ("-a" in args or "-t" in args) and "--first-only" not in args
    return unexpand(text, tabs, all=convert_all, posix=True)


@pytest.mark.parametrize(("args", "text", "expected"), OBSERVED)
def test_matches_what_gnu_unexpand_printed(args: list[str], text: str, expected: str) -> None:
    assert _call(args, text) == expected


def test_only_leading_blanks_by_default() -> None:
    assert unexpand("        a        b") == "\ta        b"


def test_all_converts_interior_runs() -> None:
    assert unexpand("        a       b", all=True) == "\ta\tb"


def test_a_lone_space_after_text_stays_a_space() -> None:
    assert unexpand("abcdefg x", all=True) == "abcdefg x"


def test_a_lone_space_followed_by_more_blanks_becomes_a_tab() -> None:
    assert unexpand("abcdefg  x", all=True) == "abcdefg\t x"
    assert unexpand("abcdefg \tx", all=True) == "abcdefg\t\tx"
    assert unexpand("abcdefg " + " " * 8 + "x", all=True) == "abcdefg\t\tx"


def test_a_lone_space_at_the_end_of_text_stays() -> None:
    assert unexpand("abcdefg ", all=True) == "abcdefg "


def test_blanks_short_of_a_stop_stay_spaces() -> None:
    assert unexpand("   x") == "   x"


def test_blanks_past_the_last_listed_stop_are_left_alone() -> None:
    assert unexpand("ab    cd      e", "2,4", all=True) == "ab\t  cd      e"
    assert unexpand("    \t x", [2, 3]) == "\t\t \t x"


def test_carriage_return_restarts_the_line_by_default() -> None:
    assert unexpand("ab\r        x") == "ab\r\tx"
    assert unexpand("ab\r        x", posix=True) == "ab\r        x"


def test_posix_backspace_moves_the_column_back() -> None:
    assert unexpand("x\b       y", all=True, posix=True) == "x\b       y"
    assert unexpand("x\b      y", all=True) == "x\b\ty"


def test_display_width_moves_the_stops() -> None:
    assert unexpand("\u4e2d      x", all=True, width="display") == "\u4e2d\tx"
    assert unexpand("\u4e2d      x", all=True) == "\u4e2d      x"


def test_ambiguous_wide_counts_two_columns() -> None:
    text = "\u00b1      x"
    assert unexpand(text, all=True, width="display", ambiguous_wide=True) == "\u00b1\tx"
    assert unexpand(text, all=True, width="display") == text


@pytest.mark.parametrize("tabs", [0, -1, "0", ""])
def test_tab_size_must_be_positive(tabs: object) -> None:
    with pytest.raises(ValueError):
        unexpand("    x", tabs)  # type: ignore[arg-type]


def test_unexpand_rejects_non_text() -> None:
    with pytest.raises(TypeError):
        unexpand(b"        x")  # type: ignore[arg-type]


def test_unexpand_of_empty_text_is_empty() -> None:
    assert unexpand("") == ""


def test_the_unexpander_holds_blanks_until_they_are_decided() -> None:
    engine = Unexpander(4)
    assert engine.feed("  ") == ""
    assert engine.feed("  x") == "\tx"
    assert engine.feed("  \n  ") == "  \n"
    assert engine.flush() == "  "


def test_flush_releases_the_held_blanks_and_starts_a_new_line() -> None:
    engine = Unexpander(8, all=True)
    assert engine.feed("abcdefg   ") == "abcdefg"
    assert engine.flush() == "\t  "
    assert engine.feed("        x") == "\tx"


# Observed from GNU coreutils 9.7: printf 'abcd \b\b\b   x' | gnuunexpand -t 2,4
def test_nothing_converts_after_passing_the_last_stop_even_after_backspaces() -> None:
    text = "abcd \b\b\b   x"
    assert unexpand(text, "2,4", posix=True) == text


@pytest.mark.parametrize("tabs", [True, False])
def test_a_bool_is_not_a_tab_size(tabs: bool) -> None:
    with pytest.raises(TypeError):
        unexpand("    x", tabs)


@pytest.mark.parametrize("tabs", [0, -1])
def test_a_non_positive_tab_size_names_the_problem(tabs: int) -> None:
    with pytest.raises(ValueError, match=r"^tab size must be positive$"):
        unexpand("    x", tabs)
