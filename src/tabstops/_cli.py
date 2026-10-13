"""Command line tool: ``tabstops expand`` and ``tabstops unexpand``."""

from __future__ import annotations

import argparse
import codecs
import sys
from collections.abc import Sequence
from typing import BinaryIO, TypeAlias

from ._expand import Expander
from ._stops import TabStops
from ._unexpand import Unexpander
from ._width import Width
from ._width_data import UNICODE_VERSION

__all__ = ["main"]

_BLOCK = 1 << 16
Engine: TypeAlias = Expander | Unexpander
Flags = list[tuple[tuple[str, ...], str]]

_FLAGS: dict[str, Flags] = {
    "expand": [
        (("-i", "--initial"), "only expand tabs before the first non-blank of a line"),
    ],
    "unexpand": [
        (("-a", "--all"), "convert blanks anywhere, not only at the start of a line"),
        (("--first-only",), "convert only leading blanks, even with -t"),
    ],
}
_COMMON: Flags = [
    (("--display",), "count columns as a terminal shows them (wide and combining)"),
    (("--ambiguous-wide",), "with --display, count East Asian Ambiguous as two columns"),
    (("--python",), "count like str.expandtabs: a carriage return restarts the line"),
]


def _tab_stops(spec: str) -> TabStops:
    try:
        return TabStops.parse(spec)
    except ValueError as error:
        raise argparse.ArgumentTypeError(str(error)) from None


def _parser() -> argparse.ArgumentParser:
    from . import __version__

    parser = argparse.ArgumentParser(
        prog="tabstops", description="Convert tabs to spaces and back, like expand and unexpand."
    )
    version = f"tabstops {__version__} (Unicode {UNICODE_VERSION})"
    parser.add_argument("--version", action="version", version=version)
    commands = parser.add_subparsers(dest="command", required=True)
    for name, summary in (("expand", "tabs to spaces"), ("unexpand", "spaces to tabs")):
        sub = commands.add_parser(name, help=summary, description=f"Convert {summary}.")
        sub.add_argument(
            "-t",
            "--tabs",
            type=_tab_stops,
            metavar="LIST",
            help="tab size, or stops like 4,8,12 with an optional /N or +N tail (default 8)",
        )
        for flags, text in _FLAGS[name] + _COMMON:
            sub.add_argument(*flags, action="store_true", help=text)
        sub.add_argument("files", nargs="*", metavar="FILE", help="files to read; - is stdin")
    return parser


def _engine(args: argparse.Namespace) -> Engine:
    if args.ambiguous_wide and not args.display:
        raise ValueError("--ambiguous-wide needs --display")
    width: Width = "display" if args.display else "chars"
    tabs = args.tabs or TabStops(8)
    posix = not args.python
    if args.command == "expand":
        return Expander(
            tabs, initial=args.initial, width=width, ambiguous_wide=args.ambiguous_wide, posix=posix
        )
    # As in the utility, -t implies -a unless --first-only is given.
    convert_all = (args.all or args.tabs is not None) and not args.first_only
    return Unexpander(
        tabs, all=convert_all, width=width, ambiguous_wide=args.ambiguous_wide, posix=posix
    )


def _pump(source: BinaryIO, engine: Engine, out: BinaryIO) -> None:
    # Undecodable bytes travel as lone surrogates and are written back unchanged.
    decoder = codecs.getincrementaldecoder("utf-8")("surrogateescape")
    while block := source.read(_BLOCK):
        out.write(engine.feed(decoder.decode(block)).encode("utf-8", "surrogateescape"))
    out.write(engine.feed(decoder.decode(b"", final=True)).encode("utf-8", "surrogateescape"))


def main(argv: Sequence[str] | None = None) -> int:
    """Run the tool; return 0 on success, 1 if a file could not be read, 2 on bad usage."""
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        engine = _engine(args)
    except ValueError as error:
        parser.error(str(error))
    out = sys.stdout.buffer
    status = 0
    # Files are one stream, as with the utilities: a line may run on into the next file.
    for name in args.files or ["-"]:
        if name == "-":
            _pump(sys.stdin.buffer, engine, out)
            continue
        try:
            with open(name, "rb") as source:
                _pump(source, engine, out)
        except OSError as error:
            out.flush()
            print(f"tabstops: {name}: {error.strerror or error}", file=sys.stderr)
            status = 1
    out.write(engine.flush().encode("utf-8", "surrogateescape"))
    out.flush()
    return status
