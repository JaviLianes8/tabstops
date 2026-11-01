"""Spaces to tabs, in one call or chunk by chunk."""

from __future__ import annotations

from collections.abc import Iterable, Iterator

from ._cursor import StopCursor
from ._stops import Tabs, as_tab_stops
from ._width import Width, width_function

__all__ = ["Unexpander", "unexpand", "unexpand_stream"]


class Unexpander:
    """Turn blanks into tabs in text that arrives in pieces.

    Arguments are those of :func:`unexpand`. Blanks that may still become a tab are held
    back until the next character decides them, so ``feed`` can return less than it got;
    ``flush`` ends the text, returns what was held back and starts over at column zero.

    >>> engine = Unexpander(4)
    >>> engine.feed("  ") + engine.flush()
    '  '
    """

    def __init__(
        self,
        tabs: Tabs = 8,
        *,
        all: bool = False,
        width: Width = "chars",
        ambiguous_wide: bool = False,
        posix: bool = False,
    ) -> None:
        self._stops = as_tab_stops(tabs)
        self._width = width_function(width, ambiguous_wide)
        self._all = all
        self._posix = posix
        self._resets = "\n" if posix else "\n\r"
        self._start_line()

    def _start_line(self) -> None:
        self._cursor = StopCursor(self._stops)
        self._converting = True
        # A line start counts as a blank, so a lone leading space can become a tab.
        self._after_blank = True
        self._group = 0
        # A single space after a non-blank that ended on a stop: it becomes a tab only
        # if another blank follows, since alone it gains nothing.
        self._held = False

    def _release(self) -> str:
        """Return the blanks held back, as the text that follows them decides."""
        out = " " * self._group
        if self._held:
            out = "\t" + out if out else " "
        self._held = False
        self._group = 0
        return out

    def _blank(self, char: str, out: list[str]) -> None:
        stop = self._cursor.boundary()
        if stop is None:
            # Past the last listed stop nothing more is converted on this line.
            out.append(self._release() + char)
            self._converting = False
            return
        if char == "\t" or (self._cursor.offset + 1 == stop and self._after_blank):
            self._cursor.reach(stop)
            out.append("\t\t" if self._held else "\t")
            self._held = False
            self._group = 0
        elif self._cursor.offset + 1 == stop:
            self._cursor.reach(stop)
            self._held = True
        else:
            self._cursor.offset += 1
            self._group += 1
        self._after_blank = True

    def feed(self, text: str) -> str:
        """Convert a text piece; wrong types raise TypeError.

        >>> Unexpander(4).feed("  ")
        ''
        """
        if not isinstance(text, str):
            raise TypeError("expected a str")
        out: list[str] = []
        for char in text:
            if char in self._resets:
                out.append(self._release() + char)
                self._start_line()
            elif not self._converting:
                out.append(char)
            elif char in " \t":
                self._blank(char, out)
            else:
                out.append(self._release() + char)
                if char == "\b" and self._posix:
                    self._cursor.backspace()
                else:
                    self._cursor.offset += self._width(char)
                self._after_blank = False
                self._converting = self._all
        return "".join(out)

    def flush(self) -> str:
        """Return pending blanks and reset the column and conversion state.

        >>> engine = Unexpander(4)
        >>> engine.feed("  "), engine.flush(), engine.flush()
        ('', '  ', '')
        """
        tail = self._release()
        self._start_line()
        return tail


def unexpand(
    text: str,
    tabs: Tabs = 8,
    *,
    all: bool = False,
    width: Width = "chars",
    ambiguous_wide: bool = False,
    posix: bool = False,
) -> str:
    """Replace runs of blanks with tabs where they reach a tab stop.

    Blanks are spaces and tabs. Only the blanks that start a line are converted unless
    ``all`` is set. The blanks between two stops become one tab when they reach the second
    stop; a single space right after a non-blank stays a space unless more blanks follow;
    a space in front of a tab is absorbed into it. ``tabs`` takes the same forms as in
    :func:`expand`; blanks past the last listed stop are left alone. ``width`` and
    ``posix`` count columns as in :func:`expand`, and ``expand(unexpand(t)) == expand(t)``
    holds for the same arguments.

    Zero/negative sizes raise ValueError; wrong text or tab types raise TypeError.

    >>> unexpand("    x", 4) == chr(9) + "x"
    True
    """
    engine = Unexpander(tabs, all=all, width=width, ambiguous_wide=ambiguous_wide, posix=posix)
    return engine.feed(text) + engine.flush()


def unexpand_stream(
    chunks: Iterable[str],
    tabs: Tabs = 8,
    *,
    all: bool = False,
    width: Width = "chars",
    ambiguous_wide: bool = False,
    posix: bool = False,
) -> Iterator[str]:
    """Unexpand an iterable of text pieces lazily; the held-back tail comes last.

    The arguments are checked when this is called, not when the first piece is read.

    >>> list(unexpand_stream([" ", " "], 4))
    ['', '', '  ']
    """
    engine = Unexpander(tabs, all=all, width=width, ambiguous_wide=ambiguous_wide, posix=posix)
    return _drive(engine, chunks)


def _drive(engine: Unexpander, chunks: Iterable[str]) -> Iterator[str]:
    for chunk in chunks:
        yield engine.feed(chunk)
    tail = engine.flush()
    if tail:
        yield tail
