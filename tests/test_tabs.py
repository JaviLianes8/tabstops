from __future__ import annotations

import pytest

from tabstops import expand, unexpand


def test_expand_aligns_to_the_next_tab_stop() -> None:
    assert expand("a\tb") == "a       b"


def test_expand_honours_a_smaller_tabsize() -> None:
    assert expand("a\tb", 4) == "a   b"


def test_expand_handles_multiple_tabs() -> None:
    assert expand("\t\t", 4) == " " * 8


def test_expand_resets_the_column_on_each_line() -> None:
    assert expand("a\tb\nc\td", 4) == "a   b\nc   d"


def test_expand_resets_the_column_on_a_carriage_return() -> None:
    assert expand("ab\r\tc", 4) == "ab\r    c"


def test_expand_with_zero_tabsize_drops_tabs() -> None:
    assert expand("a\tb", 0) == "ab"


def test_expand_rejects_a_negative_tabsize() -> None:
    with pytest.raises(ValueError):
        expand("a\tb", -1)


def test_expand_of_empty_text_is_empty() -> None:
    assert expand("", 8) == ""


def test_unexpand_converts_leading_spaces_to_a_tab() -> None:
    assert unexpand(" " * 8 + "x") == "\tx"


def test_unexpand_leaves_a_lone_space_at_a_stop_alone() -> None:
    assert unexpand(" x", 1) == " x"


def test_unexpand_only_touches_leading_space_by_default() -> None:
    assert unexpand("a" + " " * 8 + "b") == "a" + " " * 8 + "b"


def test_unexpand_all_converts_interior_runs() -> None:
    assert unexpand("a" + " " * 7 + "b", all=True) == "a\tb"


def test_unexpand_keeps_remainder_spaces_after_a_tab() -> None:
    assert unexpand(" " * 9 + "x") == "\t x"


def test_unexpand_honours_a_smaller_tabsize() -> None:
    assert unexpand(" " * 4 + "x", 4) == "\tx"


def test_unexpand_rejects_a_non_positive_tabsize() -> None:
    with pytest.raises(ValueError):
        unexpand("    x", 0)


def test_unexpand_of_empty_text_is_empty() -> None:
    assert unexpand("", 8) == ""


@pytest.mark.parametrize("tabsize", [1, 2, 4, 8, 3])
def test_round_trip_is_lossless_for_expanded_text(tabsize: int) -> None:
    lines = ["a\tb\tc", "\t\tindented", "no tabs here", "x\ty\n\tz"]
    for line in lines:
        expanded = expand(line, tabsize)
        assert expand(unexpand(expanded, tabsize, all=True), tabsize) == expanded
