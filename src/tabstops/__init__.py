"""Expand and unexpand tabs with tab stop lists, display columns and streaming.

UNICODE_VERSION names the pinned Unicode Character Database used for widths.

>>> UNICODE_VERSION
'18.0.0'
"""

from __future__ import annotations

from ._expand import Expander, expand, expand_stream
from ._stops import TabStops
from ._unexpand import Unexpander, unexpand, unexpand_stream
from ._width import UNICODE_VERSION, char_width, display_width

__version__ = "1.0.0"

del annotations

__all__ = [
    "UNICODE_VERSION",
    "Expander",
    "TabStops",
    "Unexpander",
    "char_width",
    "display_width",
    "expand",
    "expand_stream",
    "unexpand",
    "unexpand_stream",
]
