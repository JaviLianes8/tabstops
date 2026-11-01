# tabstops guide

## Stable API

Import from `tabstops`. The ten names in `__all__` are the supported surface;
`__version__` is the package version and `UNICODE_VERSION` identifies the pinned width
data. Internal modules and engine attributes are not API. The names, parameter names,
defaults and return types below are stable for 1.x.

| Name | Contract |
| --- | --- |
| `TabStops(every=8, stops=(), relative=False)` | Frozen, hashable value with integer fields; copies the stops into a tuple. |
| `TabStops.parse(spec)` | Read comma/space/tab-separated ASCII decimal stops; a single value is an interval. |
| `TabStops.next_stop(column)` | First stop strictly greater than a nonnegative integer column, or `None`. |
| `str(stops)` | Canonical syntax that `TabStops.parse` reads back to the same value. |
| `expand(text, tabs=8, *, initial=False, width="chars", ambiguous_wide=False, posix=False)` | Replace tabs with spaces. |
| `unexpand(text, tabs=8, *, all=False, width="chars", ambiguous_wide=False, posix=False)` | Compress blank groups to tabs. |
| `Expander(...)`, `Unexpander(...)` | Same options as the corresponding function, without `text`. |
| `engine.feed(text)` | Process a chunk, keeping column and line state; return a string. |
| `engine.flush()` | Return pending output and reset all line state; repeated flush returns `""`. |
| `expand_stream(chunks, ...)`, `unexpand_stream(chunks, ...)` | Lazy iterators, with the corresponding function's options. |
| `char_width(char, *, ambiguous_wide=False)` | Width 0, 1 or 2 of exactly one code point. |
| `display_width(text, *, ambiguous_wide=False)` | Sum of code point widths; tabs count as zero. |

`tabs` accepts an integer interval, a list string, a sequence of integers (except bytes
and bytearray), or a `TabStops`. A one-element sequence is rejected; use an integer
for an interval. Listed stops must be positive and strictly increasing. `/N` repeats
at multiples of N after the list; `+N` repeats relative to its last stop. Repeated or
edge separators are ignored; `/8` and `+8` alone mean interval 8. A list without a
tail has at least two stops. An integer zero is accepted only by expansion and drops
tabs. Negative sizes are rejected, unlike `str.expandtabs`.

```python
from tabstops import TabStops, expand, unexpand

str(TabStops.parse(" 2,,4,/8 "))  # -> '2,4,/8'
TabStops.parse("1,+8").next_stop(9)  # -> 17
TabStops.parse("2,4").next_stop(4)  # -> None
expand("a\tb", 0)  # -> 'ab'
unexpand("abcdefg  x", all=True)  # -> 'abcdefg\t x'
```

## Columns and blank groups

Defaults count every code point as one column except tab, newline and carriage return.
Newline and carriage return reset the column and leading-blank state. `posix=True`
resets only on newline; backspace moves back one column without going below zero.
GNU tools count bytes, so the comparison applies to ASCII input. The CLI defaults to
POSIX rules; `--python` selects the library defaults.

`initial=True` expands only leading blanks (space and tab). Unexpansion converts leading
blanks unless `all=True`. A lone space after text stays a space even if it reaches a
stop; a following blank can make it a tab. A space before a tab is absorbed. Past the
last finite stop, expansion uses one space and unexpansion leaves the rest of that
line alone, including after backspaces. Expanding the compressed output gives the
same result as expanding the original with the same options.

`width="display"` uses the pinned Unicode 18.0.0 properties: Wide/Fullwidth are two,
Mn/Me/Cc, default ignorables and Hangul V/T are zero, Ambiguous is one (two with
`ambiguous_wide=True`), and everything else is one. Surrogates are supported as code
points. This is a per-code-point model, not terminal emulation: grapheme clusters,
emoji ZWJ sequences, escape sequences, and terminal-specific rendering are not modeled.
`display_width` sums widths rather than tracking a cursor or resetting on newlines.

## Streaming and resources

Options are checked at iterator creation; chunks are consumed and checked lazily.
Expansion emits one result per chunk. Unexpansion can emit empty pieces and one extra
tail after the last chunk. A rejected non-string feed does not change engine state.
Call `flush` when finished; engines are mutable and are not shared between threads.

```python
from tabstops import Expander, Unexpander, expand_stream, unexpand_stream

list(expand_stream(["a", "\tb"], 4))  # -> ['a', '   b']
list(unexpand_stream([" ", " "], 4))  # -> ['', '', '  ']
engine = Unexpander(4)
engine.feed("  ")  # -> ''
engine.flush()  # -> '  '
engine.flush()  # -> ''
```

Processing is linear in input plus output size, with logarithmic stop lookup for lists.
Pending spaces are counted, not repeatedly copied. Tab sizes and output lengths have
no library-imposed cap: a huge tab size can request huge output and cause MemoryError
or OverflowError from Python. Bound tab sizes and input at your application's boundary
when processing untrusted requests. Decimal string parsing follows Python's configured
integer conversion limit; direct integers use arbitrary precision.

## Errors and command line

Wrong text/tab/column types raise `TypeError`; malformed lists, invalid sizes, negative
columns, invalid width modes, or `ambiguous_wide` without display mode raise `ValueError`.
Boolean tab sizes and columns are rejected. Option flags use Python truth testing;
pass booleans as annotated. `char_width` rejects lengths other than one with `ValueError`.
Library validation errors do not quote input values. Exceptions from user-defined
objects, iterators or overridden methods propagate; those objects are caller code.

The CLI accepts UTF-8 and preserves undecodable bytes. Multiple files form one text
stream; a UTF-8 character must not be split between files. `-` means stdin. Repeated
`-t` options are joined; `-t` implies `-a` for unexpansion unless `--first-only` is set.
The obsolete GNU `-8` form is unsupported. Exit codes: 0 success/help/version, 1 input
or output failure (including a closed pipe), 2 bad usage. Missing files are reported
with a bounded escaped basename and processing continues. Usage errors do not quote
unknown arguments. Ordinary read/write errors produce a short diagnostic.

## Upgrading from 0.2.0

Valid conversion results and defaults are unchanged. `next_stop` now rejects negative,
boolean and non-integer columns. Error wording is shorter and does not echo invalid
values or dynamic type names. CLI file errors show a bounded basename and errno;
unknown-argument errors use generic wording, and read/write failures exit 1. The
accidental top-level `annotations` name is removed. Long pending blank runs use a
counter, avoiding repeated string copies. See the
[CHANGELOG](https://github.com/JaviLianes8/tabstops/blob/main/CHANGELOG.md).

## Verification

`pip install -e '.[dev]'` installs the development tools. Run `scripts/check.ps1` or
the individual format, lint, strict typing and pytest gates. Tests enforce a 300-second
per-test timeout. Set `TABSTOPS_UCD` to an external data directory, then run
`python scripts/fetch_upstream.py` to fetch the pinned sources there. Without those
files the two Unicode-source tests skip; tampered files fail verification. GNU oracle
tests run when GNU expand/unexpand are available (including Git for Windows).
Run `pytest -m e2e --basetemp PATH` for the installed-wheel and PyPI upgrade check.
