"""Tab stop model: a fixed interval, or listed stops with an optional repeating tail."""

from __future__ import annotations

import re
from bisect import bisect_right
from collections.abc import Sequence
from dataclasses import dataclass
from typing import TypeAlias, cast

__all__ = ["TabStops", "Tabs", "as_tab_stops"]

_SEPARATORS = re.compile(r"[, \t]+")
_ITEM = re.compile(r"([/+]?)([0-9]+)")


@dataclass(frozen=True)
class TabStops:
    """Where the tab stops of a line sit, with columns counted from zero.

    ``TabStops(8)`` puts a stop at every multiple of 8. ``TabStops(0, (4, 10))`` puts stops
    at columns 4 and 10 and nowhere after (a list needs two or more stops, as in POSIX).
    With listed stops, a positive ``every`` keeps going after the last one: at every
    multiple of ``every``, or with ``relative`` at the last listed stop plus every multiple
    of ``every`` (the GNU ``/N`` and ``+N`` forms).
    """

    every: int = 8
    stops: tuple[int, ...] = ()
    relative: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(self, "stops", tuple(self.stops))
        for value in (self.every, *self.stops):
            if not isinstance(value, int) or isinstance(value, bool):
                raise TypeError(f"tab stops must be ints, got {value!r}")
        if not isinstance(self.relative, bool):
            raise TypeError("relative must be a bool")
        if self.every < 0 or any(stop <= 0 for stop in self.stops):
            raise ValueError("tab stops must be positive")
        if any(a >= b for a, b in zip(self.stops, self.stops[1:], strict=False)):
            raise ValueError("tab stops must be strictly ascending")
        if not self.stops and (self.every == 0 or self.relative):
            raise ValueError("an interval needs a positive size and no relative tail")
        if self.relative and not self.every:
            raise ValueError("a relative tail needs a positive every")
        if len(self.stops) == 1 and not self.every:
            raise ValueError("list two or more stops, or one stop with a tail")

    @classmethod
    def parse(cls, spec: str) -> TabStops:
        """Read a ``-t`` argument: ``"4"``, ``"4,8,12"``, ``"2,4,/8"`` or ``"1,+8"``.

        Items are separated by commas or blanks. A single number is an interval. Only the
        last item may carry ``/`` or ``+``. Zero, an empty list and descending stops are
        rejected with ``ValueError``.
        """
        if not isinstance(spec, str):
            raise TypeError(f"expected a str, got {type(spec).__name__}")
        items = [item for item in _SEPARATORS.split(spec) if item]
        if not items:
            raise ValueError("empty tab stop list")
        values: list[int] = []
        tail = ""
        for index, item in enumerate(items):
            match = _ITEM.fullmatch(item)
            if match is None:
                raise ValueError(f"invalid tab stop {item!r}")
            if match.group(1) and index != len(items) - 1:
                raise ValueError(f"{match.group(1)!r} is only allowed on the last tab stop")
            tail = match.group(1)
            values.append(int(match.group(2)))
        if 0 in values:
            raise ValueError("tab stops must be positive")
        if len(values) == 1:
            return cls(values[0])
        if tail:
            return cls(values[-1], tuple(values[:-1]), tail == "+")
        return cls(0, tuple(values))

    def next_stop(self, column: int) -> int | None:
        """Return the first stop after ``column``, or ``None`` past the last listed stop."""
        index = bisect_right(self.stops, column)
        if index < len(self.stops):
            return self.stops[index]
        if not self.every:
            return None
        base = self.stops[-1] if self.relative else 0
        return column + self.every - (column - base) % self.every

    def __str__(self) -> str:
        if not self.stops:
            return str(self.every)
        listed = ",".join(map(str, self.stops))
        if not self.every:
            return listed
        return f"{listed},{'+' if self.relative else '/'}{self.every}"


Tabs: TypeAlias = int | str | Sequence[int] | TabStops


def as_tab_stops(tabs: Tabs) -> TabStops:
    """Turn any accepted ``tabs`` argument into a :class:`TabStops`.

    An int is an interval, a str is parsed like ``-t``, and a sequence of ints lists the
    stops exactly (with nothing after the last one).
    """
    if isinstance(tabs, TabStops):
        return tabs
    if isinstance(tabs, bool):
        raise TypeError("tabs must be an int, a str, a sequence of ints or TabStops")
    if isinstance(tabs, int):
        if tabs <= 0:
            raise ValueError("tab size must be positive")
        return TabStops(tabs)
    if isinstance(tabs, str):
        return TabStops.parse(tabs)
    if isinstance(tabs, Sequence) and not isinstance(tabs, (bytes, bytearray)):
        if not tabs:
            raise ValueError("empty tab stop list")
        return TabStops(0, tuple(cast(Sequence[int], tabs)))
    raise TypeError("tabs must be an int, a str, a sequence of ints or TabStops")
