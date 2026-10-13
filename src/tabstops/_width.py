"""Column widths of characters: one per code point, or as a terminal displays them."""

from __future__ import annotations

from bisect import bisect_right
from collections.abc import Callable
from typing import Literal

from ._width_data import RUNS, UNICODE_VERSION

__all__ = ["UNICODE_VERSION", "Width", "char_width", "display_width", "width_function"]

Width = Literal["chars", "display"]


def _decode() -> tuple[list[int], bytes]:
    starts: list[int] = []
    classes = bytearray()
    start = 0
    for token in "".join(RUNS).split():
        starts.append(start)
        classes.append(int(token[0]))
        start += int(token[1:], 36)
    if start != 0x110000:
        raise RuntimeError("the width table does not cover the code space")
    return starts, bytes(classes)


_STARTS, _CLASSES = _decode()


def char_width(char: str, *, ambiguous_wide: bool = False) -> int:
    """Return how many terminal columns ``char`` advances the cursor: 0, 1 or 2.

    East Asian Wide and Fullwidth characters take two columns; combining and enclosing
    marks, default ignorable characters, control characters and conjoining Hangul vowels
    and trailing consonants take none. East Asian Ambiguous characters take one column, or
    two with ``ambiguous_wide``. Everything else takes one.
    """
    if not isinstance(char, str):
        raise TypeError(f"expected a str, got {type(char).__name__}")
    if len(char) != 1:
        raise ValueError(f"expected a single character, got {len(char)}")
    if " " <= char < "\x7f":
        return 1
    found = _CLASSES[bisect_right(_STARTS, ord(char)) - 1]
    if found == 3:
        return 2 if ambiguous_wide else 1
    return found


def display_width(text: str, *, ambiguous_wide: bool = False) -> int:
    """Return the sum of :func:`char_width` over ``text``.

    Tabs are control characters here and count as zero: expand them first with
    ``expand(text, width="display")`` to measure a line that holds tabs.
    """
    if not isinstance(text, str):
        raise TypeError(f"expected a str, got {type(text).__name__}")
    return sum(char_width(char, ambiguous_wide=ambiguous_wide) for char in text)


def _one(char: str) -> int:
    return 1


def width_function(width: Width, ambiguous_wide: bool) -> Callable[[str], int]:
    """Resolve the ``width`` and ``ambiguous_wide`` arguments to a per-character width."""
    if width == "chars":
        if ambiguous_wide:
            raise ValueError("ambiguous_wide needs width='display'")
        return _one
    if width == "display":
        return lambda char: char_width(char, ambiguous_wide=ambiguous_wide)
    raise ValueError(f"width must be 'chars' or 'display', got {width!r}")
