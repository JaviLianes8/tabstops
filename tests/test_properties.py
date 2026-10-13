"""Seeded random checks of the promises that hold for every input."""

from __future__ import annotations

import random

import pytest

from tabstops import Expander, Unexpander, expand, expand_stream, unexpand, unexpand_stream

ALPHABET = "ab  \t\t\n\r\b\x0b\u4e2d\u0301\u00b1\u200b"
SPECS: list[object] = [1, 2, 3, 4, 8, "4,8,12", "2,4,/8", "1,+8", "3,7,20", [5, 6]]


def _texts(seed: int, count: int = 400) -> list[str]:
    rng = random.Random(seed)
    return ["".join(rng.choices(ALPHABET, k=rng.randrange(40))) for _ in range(count)]


def _options(rng: random.Random) -> dict[str, object]:
    width = rng.choice(["chars", "display"])
    return {
        "tabs": rng.choice(SPECS),
        "width": width,
        "ambiguous_wide": width == "display" and rng.random() < 0.5,
        "posix": rng.random() < 0.5,
    }


@pytest.mark.parametrize("tabsize", range(18))
def test_expand_equals_str_expandtabs(tabsize: int) -> None:
    for text in _texts(tabsize):
        assert expand(text, tabsize) == text.expandtabs(tabsize)
        # The engine itself, not only the shortcut expand() takes for this case.
        assert Expander(tabsize).feed(text) == text.expandtabs(tabsize)


def test_unexpand_then_expand_gives_the_expanded_text() -> None:
    rng = random.Random(7)
    for text in _texts(7, 3000):
        options = _options(rng)
        tabs = options.pop("tabs")
        convert_all = rng.random() < 0.5
        packed = unexpand(text, tabs, all=convert_all, **options)  # type: ignore[arg-type]
        assert expand(packed, tabs, **options) == expand(text, tabs, **options)  # type: ignore[arg-type]


def test_unexpand_only_changes_blanks() -> None:
    rng = random.Random(11)
    for text in _texts(11, 1000):
        options = _options(rng)
        tabs = options.pop("tabs")
        packed = unexpand(text, tabs, all=True, **options)  # type: ignore[arg-type]
        assert packed.replace(" ", "").replace("\t", "") == text.replace(" ", "").replace("\t", "")


def _split(text: str, rng: random.Random) -> list[str]:
    cuts = sorted(rng.sample(range(len(text) + 1), k=min(len(text) + 1, rng.randrange(1, 6))))
    return [text[a:b] for a, b in zip([0, *cuts], [*cuts, len(text)], strict=True)]


def test_streaming_any_split_gives_the_whole_text_result() -> None:
    rng = random.Random(3)
    for text in _texts(3, 2000):
        options = _options(rng)
        tabs = options.pop("tabs")
        pieces = _split(text, rng)
        initial = rng.random() < 0.3
        whole = expand(text, tabs, initial=initial, **options)  # type: ignore[arg-type]
        streamed = expand_stream(pieces, tabs, initial=initial, **options)  # type: ignore[arg-type]
        assert "".join(streamed) == whole
        convert_all = rng.random() < 0.5
        whole = unexpand(text, tabs, all=convert_all, **options)  # type: ignore[arg-type]
        streamed = unexpand_stream(pieces, tabs, all=convert_all, **options)  # type: ignore[arg-type]
        assert "".join(streamed) == whole


def test_engines_start_over_after_flush() -> None:
    expander = Expander("3,5")
    unexpander = Unexpander(4, all=True)
    for text in _texts(5, 200):
        assert expander.feed(text) + expander.flush() == expand(text, "3,5")
        assert unexpander.feed(text) + unexpander.flush() == unexpand(text, 4, all=True)


def test_stream_outputs_one_piece_per_input_piece_plus_the_tail() -> None:
    assert list(expand_stream(["a\t", "b"], 4)) == ["a   ", "b"]
    assert list(unexpand_stream(["  ", "  "], 4)) == ["", "\t"]
    assert list(unexpand_stream(["  ", " "], 4)) == ["", "", "   "]
    assert list(unexpand_stream(["  x"], 4)) == ["  x"]
