"""Tabs to spaces, in one call or chunk by chunk."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from ._stops import Tabs, TabStops, as_tab_stops
from ._width import Width, width_function

__all__ = ["Expander", "expand", "expand_stream"]


class Expander:
    """Expand tabs in text that arrives in pieces, keeping the column across pieces.

    Arguments are those of :func:`expand`. ``feed`` returns the output for each piece and
    ``flush`` ends the text and starts over at column zero.
    """

    def __init__(
        self,
        tabs: Tabs = 8,
        *,
        initial: bool = False,
        width: Width = "chars",
        ambiguous_wide: bool = False,
        posix: bool = False,
    ) -> None:
        # A zero tab size drops tabs, as str.expandtabs(0) does.
        self._stops: TabStops | None = None if _is_zero(tabs) else as_tab_stops(tabs)
        self._width = width_function(width, ambiguous_wide)
        self._initial = initial
        self._posix = posix
        self._resets = "\n" if posix else "\n\r"
        self._column = 0
        self._leading = True

    def feed(self, text: str) -> str:
        """Expand the next piece of text and return the result."""
        if not isinstance(text, str):
            raise TypeError(f"expected a str, got {type(text).__name__}")
        out: list[str] = []
        column = self._column
        leading = self._leading
        for char in text:
            if char in self._resets:
                column = 0
                leading = True
                out.append(char)
            elif char == "\t" and (leading or not self._initial):
                if self._stops is None:
                    continue
                stop = self._stops.next_stop(column)
                # POSIX: a tab past the last listed stop becomes a single space.
                stop = column + 1 if stop is None else stop
                out.append(" " * (stop - column))
                column = stop
            elif char == "\b" and self._posix:
                column = max(column - 1, 0)
                leading = False
                out.append(char)
            else:
                column += self._width(char)
                leading = leading and char == " "
                out.append(char)
        self._column = column
        self._leading = leading
        return "".join(out)

    def flush(self) -> str:
        """End the text: nothing is held back, so this only resets the column."""
        self._column = 0
        self._leading = True
        return ""


def _is_zero(tabs: Tabs) -> bool:
    if isinstance(tabs, bool) or not isinstance(tabs, int):
        return False
    if tabs < 0:
        raise ValueError("tab size must not be negative")
    return tabs == 0


def expand(
    text: str,
    tabs: Tabs = 8,
    *,
    initial: bool = False,
    width: Width = "chars",
    ambiguous_wide: bool = False,
    posix: bool = False,
) -> str:
    """Replace each tab with the spaces that reach the next tab stop.

    With the defaults this is exactly ``text.expandtabs(tabs)``: the column restarts after
    a newline or a carriage return and every other character advances one column; a tab
    size of zero drops tabs. ``tabs`` also takes a list of stops (``"4,10"``,
    ``[4, 10]``, ``"2,4,/8"`` or a :class:`TabStops`); a tab past the last listed stop
    becomes one space. ``initial`` expands only the tabs before the first non-blank
    character of each line. ``width="display"`` counts columns as a terminal shows them
    (see :func:`char_width`). ``posix`` follows the ``expand`` utility instead: only a
    newline restarts the column and a backspace moves it back one place.
    """
    engine = Expander(
        tabs, initial=initial, width=width, ambiguous_wide=ambiguous_wide, posix=posix
    )
    if isinstance(tabs, int) and not (initial or posix) and width == "chars":
        if not isinstance(text, str):
            raise TypeError(f"expected a str, got {type(text).__name__}")
        # Same rules as the engine, done in C.
        return text.expandtabs(tabs)
    return engine.feed(text) + engine.flush()


def expand_stream(
    chunks: Iterable[str],
    tabs: Tabs = 8,
    *,
    initial: bool = False,
    width: Width = "chars",
    ambiguous_wide: bool = False,
    posix: bool = False,
) -> Iterator[str]:
    """Expand an iterable of text pieces (lines, file blocks) lazily, one output per piece."""
    engine = Expander(
        tabs, initial=initial, width=width, ambiguous_wide=ambiguous_wide, posix=posix
    )
    for chunk in chunks:
        yield engine.feed(chunk)
