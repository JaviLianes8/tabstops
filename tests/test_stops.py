from __future__ import annotations

import pytest

from tabstops import TabStops, expand


def _stops(tabs: TabStops, upto: int) -> list[int]:
    found: list[int] = []
    column = 0
    while (stop := tabs.next_stop(column)) is not None and stop <= upto:
        found.append(stop)
        column = stop
    return found


def test_an_interval_puts_a_stop_at_every_multiple() -> None:
    assert _stops(TabStops(8), 32) == [8, 16, 24, 32]


def test_the_default_interval_is_eight() -> None:
    assert TabStops() == TabStops(8)


def test_next_stop_is_strictly_after_the_column() -> None:
    assert TabStops(4).next_stop(4) == 8
    assert TabStops(4).next_stop(3) == 4


# GNU coreutils manual, expand invocation (fetched 2026-10-13):
# https://www.gnu.org/software/coreutils/manual/html_node/expand-invocation.html
# "--tabs=2,4,/8 will set tab stops at position 2 and 4, and every multiple of 8 after that"
def test_slash_tail_from_the_gnu_manual() -> None:
    assert _stops(TabStops.parse("2,4,/8"), 32) == [2, 4, 8, 16, 24, 32]


# Same page: "--tabs=1,+8 ... will set tab stops at positions 1,9,17,..."
def test_plus_tail_from_the_gnu_manual() -> None:
    assert _stops(TabStops.parse("1,+8"), 17) == [1, 9, 17]


def test_a_list_has_no_stop_after_the_last() -> None:
    tabs = TabStops.parse("4,10")
    assert _stops(tabs, 100) == [4, 10]
    assert tabs.next_stop(10) is None


@pytest.mark.parametrize(
    ("spec", "expected"),
    [
        ("4", TabStops(4)),
        ("4,8,12", TabStops(0, (4, 8, 12))),
        ("4 8\t12", TabStops(0, (4, 8, 12))),
        ("4,,8", TabStops(0, (4, 8))),
        (" 4,", TabStops(4)),
        ("04", TabStops(4)),
        ("/8", TabStops(8)),
        ("+8", TabStops(8)),
        ("4,/8", TabStops(8, (4,))),
        ("4,+3", TabStops(3, (4,), relative=True)),
    ],
)
def test_parse_accepts_the_list_syntax(spec: str, expected: TabStops) -> None:
    assert TabStops.parse(spec) == expected


@pytest.mark.parametrize(
    "spec",
    ["", " , ", "0", "0,4", "4,0", "8,4", "4,4", "4,/0", "+0", "/8,12", "4,/8,12", "x", "4.",
     "4,-8", "4,/8/", "\u0664", "1e3"],
)  # fmt: skip
def test_parse_rejects_bad_lists(spec: str) -> None:
    with pytest.raises(ValueError):
        TabStops.parse(spec)


def test_parse_rejects_a_non_string() -> None:
    with pytest.raises(TypeError):
        TabStops.parse(8)  # type: ignore[arg-type]


@pytest.mark.parametrize("spec", ["8", "4,8,12", "2,4,/8", "1,+8", "3,9"])
def test_str_round_trips_through_parse(spec: str) -> None:
    assert str(TabStops.parse(spec)) == spec
    assert TabStops.parse(str(TabStops.parse(spec))) == TabStops.parse(spec)


def test_stops_are_kept_as_a_tuple() -> None:
    assert TabStops(0, [3, 6]).stops == (3, 6)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "kwargs",
    [
        {"every": 0},
        {"every": -4},
        {"every": 4, "relative": True},
        {"every": 0, "stops": (4,)},
        {"every": 0, "stops": (4, 4)},
        {"every": 0, "stops": (6, 4)},
        {"every": 0, "stops": (0, 4)},
        {"every": 0, "stops": (4, 8), "relative": True},
    ],
)
def test_construction_rejects_meaningless_stops(kwargs: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        TabStops(**kwargs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    "kwargs",
    [{"every": 2.0}, {"every": True}, {"every": 0, "stops": (4, "8")}, {"relative": 1}],
)
def test_construction_rejects_wrong_types(kwargs: dict[str, object]) -> None:
    with pytest.raises(TypeError):
        TabStops(**kwargs)  # type: ignore[arg-type]


def test_tab_stops_are_immutable_and_hashable() -> None:
    tabs = TabStops.parse("2,4,/8")
    with pytest.raises(AttributeError):
        tabs.every = 4  # type: ignore[misc]
    assert {tabs: 1}[TabStops(8, (2, 4))] == 1


@pytest.mark.parametrize(
    "tabs", ["4,8", [4, 8], (4, 8), TabStops(0, (4, 8)), range(4, 9, 4)]
)  # fmt: skip
def test_every_form_of_a_list_means_the_same(tabs: object) -> None:
    assert expand("a\tb\tc\td", tabs) == "a   b   c d"  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("tabs", "error"),
    [([], ValueError), ([4], ValueError), (True, TypeError), (4.0, TypeError), (None, TypeError)],
)
def test_bad_tabs_arguments_are_rejected(tabs: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        expand("a\tb", tabs)  # type: ignore[arg-type]


@pytest.mark.parametrize(
    ("spec", "message"),
    [("", "empty"), (" , ", "empty"), ("0", "positive"), ("4,/0", "positive"), ("+0", "positive")],
)
def test_parse_errors_say_what_is_wrong(spec: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        TabStops.parse(spec)
