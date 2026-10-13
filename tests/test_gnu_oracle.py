"""Differential test against GNU coreutils expand and unexpand, run live when installed."""

from __future__ import annotations

import random

import pytest

from tabstops import expand, unexpand

from .conftest import gnu, run_gnu
from .test_cli import run_cli

SPECS = ["8", "1", "3", "4,8,12", "2,4,/8", "1,+8", "3,7,20", "5 6"]
EXPAND_FLAGS: list[list[str]] = [[], ["-i"]]
UNEXPAND_FLAGS: list[list[str]] = [[], ["-a"], ["--first-only"]]


def _input(seed: int) -> str:
    rng = random.Random(seed)
    lines = ["".join(rng.choices("ab   \t\t\b\r", k=rng.randrange(30))) for _ in range(400)]
    return "\n".join(lines) + "\n"


@pytest.mark.skipif(gnu("expand") is None, reason="GNU expand not installed")
@pytest.mark.parametrize("spec", SPECS)
@pytest.mark.parametrize("flags", EXPAND_FLAGS)
def test_expand_matches_gnu(spec: str, flags: list[str]) -> None:
    text = _input(len(spec) + len(flags))
    wanted = run_gnu("expand", [*flags, "-t", spec], text.encode()).decode()
    assert expand(text, spec, initial="-i" in flags, posix=True) == wanted
    assert run_cli(["expand", *flags, "-t", spec], text.encode()) == (0, wanted.encode())


@pytest.mark.skipif(gnu("unexpand") is None, reason="GNU unexpand not installed")
@pytest.mark.parametrize("spec", [None, *SPECS])
@pytest.mark.parametrize("flags", UNEXPAND_FLAGS)
def test_unexpand_matches_gnu(spec: str | None, flags: list[str]) -> None:
    text = _input(len(spec or "") * 3 + len(flags))
    args = [*flags, *(["-t", spec] if spec else [])]
    wanted = run_gnu("unexpand", args, text.encode()).decode()
    convert_all = ("-a" in flags or spec is not None) and "--first-only" not in flags
    assert unexpand(text, spec or 8, all=convert_all, posix=True) == wanted
    assert run_cli(["unexpand", *args], text.encode()) == (0, wanted.encode())


@pytest.mark.skipif(gnu("unexpand") is None, reason="GNU unexpand not installed")
def test_text_without_a_final_newline_matches_gnu() -> None:
    for text in ["        ", "a       ", "abcdefg ", "  \t", "x\b        "]:
        wanted = run_gnu("unexpand", ["-a"], text.encode()).decode()
        assert unexpand(text, all=True, posix=True) == wanted, repr(text)
