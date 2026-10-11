"""Tab-stop-aware conversion between tabs and spaces."""

from __future__ import annotations

__all__ = ["expand", "unexpand"]

_LINE_RESETS = ("\n", "\r")


def expand(text: str, tabsize: int = 8) -> str:
    """Replace tabs with spaces, advancing to the next tab stop on each line.

    The column resets at every newline or carriage return, so each line is aligned
    independently. A ``tabsize`` of zero drops tabs entirely.
    """
    if tabsize < 0:
        raise ValueError("tabsize must not be negative")
    out: list[str] = []
    column = 0
    for char in text:
        if char == "\t":
            if tabsize == 0:
                continue
            width = tabsize - (column % tabsize)
            out.append(" " * width)
            column += width
        elif char in _LINE_RESETS:
            out.append(char)
            column = 0
        else:
            out.append(char)
            column += 1
    return "".join(out)


def unexpand(text: str, tabsize: int = 8, *, all: bool = False) -> str:
    """Replace runs of spaces with tabs at tab stops.

    By default only the leading whitespace of each line is converted; set ``all``
    to convert every run of spaces on the line. A single space that merely reaches
    a tab stop is left alone, matching the usual ``unexpand`` behaviour.
    """
    if tabsize <= 0:
        raise ValueError("tabsize must be positive")
    out: list[str] = []
    column = 0
    run = 0
    run_start = 0
    leading = True
    for char in text:
        if char == " " and (all or leading):
            if run == 0:
                run_start = column
            run += 1
            column += 1
            continue
        if run:
            out.append(_squeeze(run, run_start, tabsize))
            run = 0
        if char == "\t":
            out.append("\t")
            column += tabsize - (column % tabsize)
        elif char in _LINE_RESETS:
            out.append(char)
            column = 0
            leading = True
        else:
            out.append(char)
            column += 1
            leading = False
    if run:
        out.append(_squeeze(run, run_start, tabsize))
    return "".join(out)


def _squeeze(count: int, start: int, tabsize: int) -> str:
    """Render ``count`` spaces starting at ``start`` using tabs where they fit."""
    out: list[str] = []
    column = start
    remaining = count
    while remaining:
        gap = tabsize - (column % tabsize)
        if 2 <= gap <= remaining:
            out.append("\t")
            column += gap
            remaining -= gap
        else:
            out.append(" ")
            column += 1
            remaining -= 1
    return "".join(out)
