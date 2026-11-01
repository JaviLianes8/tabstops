# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-11-01

### Stable

- The ten public names, signatures and defaults from 0.2.0: tab stop models, expansion,
  compression, streaming engines and iterators, and Unicode 18.0.0 widths.
- Runnable public docstrings, a complete GUIDE, strict typing, installed-wheel and
  PyPI upgrade checks, live GNU and Unicode comparisons, and mutation contracts.

### Changed

- `TabStops.next_stop` requires a nonnegative integer column: boolean/non-integer
  arguments raise `TypeError`, negative arguments raise `ValueError`.
- Validation errors no longer echo invalid values or dynamic type names. Overlong
  decimal stops have a short `ValueError` message instead of the interpreter's wording.
- CLI unknown-argument errors use a generic message. File errors identify a bounded,
  escaped basename and errno instead of the full path and operating-system message.
  Read/write errors exit 1 with a short diagnostic instead of a traceback.
- Remove the accidental top-level `annotations` attribute (never in `__all__`).
- Pending spaces in `Unexpander` are counted rather than repeatedly concatenated,
  avoiding quadratic work for distant stops. Valid conversion outputs are unchanged.
- Closed output pipes are handled without opening a device file. Help/version output
  now flushes before exiting, returning 1 on output failure instead of exit 120.


## [0.2.0]

### Added

- `TabStops`: intervals, lists of stops and the `/N` and `+N` tails, parsed from the
  `-t` syntax of the `expand` and `unexpand` tools. `tabs` accepts an int, a list string,
  a sequence of ints or a `TabStops` everywhere.
- `posix=True` on `expand` and `unexpand`: only a newline restarts the column and a
  backspace moves it back, as the tools do.
- `initial=True` on `expand`, like `expand -i`.
- Display columns: `width="display"` and `ambiguous_wide`, plus `char_width` and
  `display_width`, from tables generated out of Unicode 18.0.0 (`UNICODE_VERSION`).
- Streaming: `Expander`, `Unexpander`, `expand_stream` and `unexpand_stream`.
- The `tabstops expand|unexpand` command, also as `python -m tabstops`. Repeated `-t`
  lists are joined; a closed output pipe ends the command quietly.

### Changed

- `expand(text, n)` is now exactly `text.expandtabs(n)`; the tab parameter is named
  `tabs` instead of `tabsize`.
- `unexpand` groups blanks by tab stop as the `unexpand` tool does: a space in front of a
  tab is absorbed into it (`" \tx"` gives `"\tx"`), and a lone leading space that reaches
  a stop becomes a tab (with a tab size of 1, `" x"` gives `"\tx"`).
- Invalid tab arguments raise `TypeError` (wrong type) or `ValueError` (zero or negative
  where not allowed, empty or descending lists).

## [0.1.0]

- First release.
- `expand`: tabs to spaces, aligned to the next tab stop, column reset per line.
- `unexpand`: spaces back to tabs at tab stops, leading-only or everywhere, filling
  the gap the standard library leaves (it expands tabs but has no `unexpand`).
