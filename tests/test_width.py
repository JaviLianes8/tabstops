from __future__ import annotations

import re
import subprocess
import sys

import pytest

from tabstops import char_width, display_width

from .conftest import ROOT, UCD, needs_ucd

# Hand-picked characters; the expected widths follow the rules in char_width's docstring.
VECTORS = [
    ("a", 1),
    (" ", 1),
    ("~", 1),
    ("\t", 0),
    ("\x00", 0),
    ("\x7f", 0),
    ("\x85", 0),
    ("\u00a0", 1),
    ("\u00ad", 0),
    ("\u0301", 0),
    ("\u20dd", 0),
    ("\u200b", 0),
    ("\u2060", 0),
    ("\ufe0f", 0),
    ("\u0600", 1),
    ("\u0903", 1),
    ("\u1100", 2),
    ("\u1160", 0),
    ("\u11a8", 0),
    ("\u3099", 0),
    ("\u4e2d", 2),
    ("\uac00", 2),
    ("\uff21", 2),
    ("\uff61", 1),
    ("\U0001f600", 2),
    ("\U00020000", 2),
    ("\U0003fffd", 2),
    ("\U000e0001", 0),
    ("\U000e0fff", 0),
    ("\U0010ffff", 1),
]


@pytest.mark.parametrize(("char", "width"), VECTORS)
def test_char_width(char: str, width: int) -> None:
    assert char_width(char) == width


@pytest.mark.parametrize("char", ["\u00b1", "\u2460", "\u03b1", "\ue000"])
def test_ambiguous_characters_widen_on_request(char: str) -> None:
    assert char_width(char) == 1
    assert char_width(char, ambiguous_wide=True) == 2


def test_ambiguous_wide_leaves_other_characters_alone() -> None:
    assert [char_width(c, ambiguous_wide=True) for c in "a\u4e2d\u0301"] == [1, 2, 0]


@pytest.mark.parametrize(
    ("value", "error"), [("", ValueError), ("ab", ValueError), (65, TypeError)]
)
def test_char_width_wants_one_character(value: object, error: type[Exception]) -> None:
    with pytest.raises(error):
        char_width(value)  # type: ignore[arg-type]


def test_display_width_sums_the_characters() -> None:
    assert display_width("e\u0301\u4e2d!") == 4
    assert display_width("\u00b1\u00b1", ambiguous_wide=True) == 4
    assert display_width("") == 0


def test_display_width_rejects_bytes() -> None:
    with pytest.raises(TypeError):
        display_width(b"abc")  # type: ignore[arg-type]


def _ranges(name: str, wanted: set[str]) -> set[int]:
    found: set[int] = set()
    pattern = re.compile(r"^([0-9A-F]+)(?:\.\.([0-9A-F]+))?\s*;\s*(\w+)")
    for line in (UCD / name).read_text(encoding="utf-8").splitlines():
        match = pattern.match(line)
        if match and match.group(3) in wanted:
            last = match.group(2) or match.group(1)
            found.update(range(int(match.group(1), 16), int(last, 16) + 1))
    return found


@needs_ucd
def test_every_code_point_has_the_width_the_data_gives() -> None:
    zero = (
        _ranges("DerivedGeneralCategory.txt", {"Mn", "Me", "Cc"})
        | _ranges("DerivedCoreProperties.txt", {"Default_Ignorable_Code_Point"})
        | _ranges("HangulSyllableType.txt", {"V", "T"})
    )
    wide = _ranges("DerivedEastAsianWidth.txt", {"W", "F"})
    ambiguous = _ranges("DerivedEastAsianWidth.txt", {"A"})
    # Unlisted code points in these blocks default to Wide (the @missing lines of the file).
    for first, last in [(0x3400, 0x4DBF), (0x4E00, 0x9FFF), (0xF900, 0xFAFF)]:
        wide.update(range(first, last + 1))
    for first, last in [(0x20000, 0x2FFFD), (0x30000, 0x3FFFD)]:
        wide.update(range(first, last + 1))
    wide -= ambiguous
    wrong = []
    for cp in range(0x110000):
        expected = 0 if cp in zero else 2 if cp in wide else 1
        narrow = char_width(chr(cp))
        broad = char_width(chr(cp), ambiguous_wide=True)
        if (narrow, broad) != (expected, 2 if cp in ambiguous and cp not in zero else expected):
            wrong.append(f"U+{cp:04X}")
    assert wrong == []


@needs_ucd
def test_the_generated_table_is_current() -> None:
    script = ROOT / "scripts" / "gen_width_table.py"
    done = subprocess.run([sys.executable, str(script), "--check"], capture_output=True)
    assert done.returncode == 0, done.stdout.decode()
