# tabstops improvement round

Progress:
- [x] Brainstorm ranked improvements (this file)
- [ ] Ground truth pinned: Unicode width data in a local folder with a tracked manifest
- [ ] Tab stop lists (`TabStops`, POSIX lists, `/N` and `+N` extensions)
- [ ] `expand`: Python semantics exact, POSIX mode (backspace, carriage return), `initial`
- [ ] `unexpand`: blank groups per tab stop, lists, POSIX mode
- [ ] Display columns: East Asian Width, combining and ignorable characters
- [ ] Streaming: `Expander`, `Unexpander`, chunked results equal whole-text results
- [ ] Command line tool
- [ ] Contracts: `str.expandtabs` sweep, GNU coreutils oracle, Unicode sweep, README examples
- [ ] Docs and packaging: README, CHANGELOG, metadata, installed-wheel e2e test
- [ ] Gates: ruff format, ruff check, mypy --strict, pytest
- [ ] Mutation run: removing guarded logic makes the suite fail
- [ ] Independent review findings fixed with regression tests
- [ ] Pull request opened, guard clean

## Starting point

`0.1.0` has `expand(text, tabsize)` and `unexpand(text, tabsize, all=False)` with a fixed
tab interval, one column per code point, and the column reset at both newline and
carriage return. Compared with the sources below:

- Only a fixed interval is accepted. The POSIX `-t` list form (explicit stops, a tab past
  the last stop becomes one space in `expand`, blanks past it are left alone in
  `unexpand`) and the GNU `/N` and `+N` tail forms are missing.
- `unexpand` leaves a space in front of an existing tab (`" \tx"` stays as is, the
  utilities give `"\tx"`), and never turns a group that is a single leading space into a
  tab even where the utilities do (tab size 1, or stops one column apart).
- There is no way to get the behaviour of the utilities for control characters: a
  backspace moves the column back one place there, and a carriage return is an ordinary
  character for them, while `str.expandtabs` resets at a carriage return.
- No `--initial` mode for `expand`.
- Columns are code points, so a line holding CJK text, emoji or combining accents lines
  up wrongly on a terminal.
- No streaming: large files must be read whole.
- No command line tool, the README examples are not executed, there is no
  installed-wheel test, and `scripts/check.ps1` lints `src tests` only.

## Sources (fetched 2026-10-13)

- Python `str.expandtabs`, https://docs.python.org/3/library/stdtypes.html#str.expandtabs:
  column starts at zero, a tab pads to the next multiple of the tab size, newline and
  carriage return reset the column, every other character advances one column whatever its
  printed form. The three examples of that page are cited in the tests. The interpreter
  itself is the oracle for the sweep test.
- POSIX.1-2024 `expand`,
  https://pubs.opengroup.org/onlinepubs/9799919799/utilities/expand.html, and `unexpand`,
  https://pubs.opengroup.org/onlinepubs/9799919799/utilities/unexpand.html: stop N means
  the next character lands in column N + 1 (counting from one), lists are positive and
  strictly ascending, separated by commas or blanks, backspace moves the column back but
  not below the start, `unexpand -a` also converts runs of two or more blanks before a stop,
  and a list implies `-a`.
- GNU coreutils 9.7 manual, `expand` and `unexpand` invocation,
  https://www.gnu.org/software/coreutils/manual/html_node/expand-invocation.html and
  https://www.gnu.org/software/coreutils/manual/html_node/unexpand-invocation.html:
  `--initial`, `--first-only`, the `/N` (multiples of N after the last stop) and `+N`
  (every N after the last stop) extensions. The GNU programs (`gnuexpand`, `gnuunexpand`
  9.7 in WSL Ubuntu 26.04) are used as a black-box oracle by a test that skips where they
  are not installed.
- UAX #11 East Asian Width, https://www.unicode.org/reports/tr11/: Wide and Fullwidth take
  two columns, Ambiguous depends on context (narrow by default here, wide on request).
- Unicode Character Database 18.0.0, https://www.unicode.org/Public/18.0.0/ucd/:
  extracted/DerivedEastAsianWidth.txt (every code point, defaults applied),
  extracted/DerivedGeneralCategory.txt (Mn, Me, Cc), DerivedCoreProperties.txt
  (Default_Ignorable_Code_Point) and HangulSyllableType.txt (conjoining vowels and trailing
  consonants, which join the preceding syllable). Sizes and sha256 go in
  `data/ucd/MANIFEST.json`; the files themselves stay in the ignored `data/ucd/` folder.

## Ranked brainstorm

1. `TabStops`: a frozen value for the stop model. `TabStops(8)` is an interval;
   `TabStops.parse("2,4,/8")` reads the POSIX and GNU list syntax; `next_stop(column)`
   returns the next stop or `None` past the last one. Every function accepts an `int`, a
   list string, a sequence of ints or a `TabStops`. Contract: the examples of the GNU
   manual and the oracle for every list form.
2. `expand` exact against `str.expandtabs` for any integer tab size of zero or more (a
   sweep test over random text with tabs, newlines, carriage returns and other controls).
   `posix=True` switches to the utilities' rules (only newline resets, backspace moves back
   one column). `initial=True` leaves tabs after the first non-blank alone.
3. `unexpand` grouped by tab stops the way the utilities group them: a group of blanks
   that ends on a stop becomes a tab, a lone space after a non-blank stays a space when
   nothing blank follows it, a space before an existing tab is absorbed, blanks after the
   last listed stop are left as they are. Contract: the GNU oracle on generated text, and
   `expand(unexpand(x)) == expand(x)` for every input.
4. Display columns: `width="display"` counts East Asian Wide and Fullwidth as two columns,
   combining marks, default ignorables, controls and conjoining Hangul jamo as zero, and
   `ambiguous_wide=True` counts Ambiguous as two. `char_width` and `display_width` are
   public. Tables generated from the pinned UCD files; a sweep test checks every code point
   against the files.
5. Streaming: `Expander` and `Unexpander` take text in chunks (`feed`, `flush`) and keep
   the column across chunk borders; `expand_stream` and `unexpand_stream` wrap an iterable.
   Contract: every split of the input gives the whole-text result.
6. Command line tool `tabstops expand|unexpand` (and `python -m tabstops`) with `-t`,
   `-i`, `-a`, `--first-only`, `--display`, `--python`, files or standard input, bytes kept
   (undecodable bytes pass through), utilities' rules by default.
7. Runnable docs: every `# ->` line in the README is executed by a test.
8. Packaging: console script, `LICENSE-UNICODE` in the wheel (the tables derive from the
   data), sdist carries the manifest and scripts but no Unicode data, installed-wheel test,
   `check.ps1` covers the whole tree and the generator check.

Considered and left out:

- Grapheme clusters, emoji ZWJ sequences and the width change of a presentation selector:
  terminals disagree on them, and a per-character model matches what `wcwidth` and most
  terminals do.
- Locale specific blanks (non-breaking spaces as blanks): only space and tab are blanks,
  as in the POSIX locale.
- Negative tab sizes: `str.expandtabs` silently drops tabs for them; here they raise
  `ValueError` because they are almost always a bug.
- Empty and zero tail specs (`""`, `"+0"`, `"4,/0"`), which GNU quietly maps to a
  default, raise `ValueError` here.
