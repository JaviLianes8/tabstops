"""Cached tab boundaries with local column offsets for unexpansion."""

from __future__ import annotations

from ._stops import TabStops


class StopCursor:
    def __init__(self, stops: TabStops) -> None:
        self._stops = stops
        self._base = 0
        self.offset = 0
        self._stop: int | None = None
        self._known = False

    def boundary(self) -> int | None:
        if not self._known or (self._stop is not None and self.offset >= self._stop):
            stop = self._stops.next_stop(self._base + self.offset)
            self._stop = None if stop is None else stop - self._base
            self._known = True
        return self._stop

    def reach(self, stop: int) -> None:
        # Rebase once per crossed stop, keeping per-character arithmetic small even
        # after a tab has jumped to an arbitrary-precision column.
        self._base += stop
        self.offset = 0
        self._known = False

    def backspace(self) -> None:
        self.offset -= 1
        if self.offset < 0 and -self.offset > self._base:
            self.offset = -self._base
        self._known = False
