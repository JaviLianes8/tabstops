# tabstops

Expand and unexpand tabs like `str.expandtabs` and the POSIX `expand` and `unexpand`
tools, with tab stop lists, terminal display columns and streaming.

## Install

```
pip install tabstops
```

## Usage

```python
from tabstops import expand, unexpand

# Tabs to spaces. With an int this is exactly str.expandtabs.
expand("name\tvalue")  # -> 'name    value'
expand("a\tb", 4)  # -> 'a   b'
expand("01\t012\n0123\t01234", 4)  # -> '01  012\n0123    01234'

# Spaces back to tabs. Leading blanks only, unless all=True.
unexpand("        x")  # -> '\tx'
unexpand("a       b")  # -> 'a       b'
unexpand("a       b", all=True)  # -> 'a\tb'
unexpand(" \tx")  # -> '\tx'
```

A lone space after text that happens to reach a stop stays a space, as with the
`unexpand` tool, and `expand(unexpand(text)) == expand(text)` holds for any text.

### Tab stop lists

`tabs` takes an interval, a list of columns (counted from zero), or the `-t` syntax of
the tools, including the `/N` (every multiple of N after the list) and `+N` (every N
columns after the last stop) tails.

```python
from tabstops import TabStops, expand, unexpand

expand("a\tb\tc", [3, 10])  # -> 'a  b      c'
expand("a\tb\tc\td", "4,8")  # -> 'a   b   c d'
expand("\t\t\tx", "1,+8")  # -> '                 x'
unexpand("ab    cd", "2,4", all=True)  # -> 'ab\t  cd'

stops = TabStops.parse("2,4,/8")
stops.next_stop(4)  # -> 8
str(stops)  # -> '2,4,/8'
```

A tab past the last listed stop becomes a single space; blanks past it are left alone.

### Display columns

Columns count code points by default. `width="display"` counts them as a terminal draws
them: East Asian Wide and Fullwidth characters take two columns, combining marks and
invisible characters take none. The data comes from Unicode 18.0.0 and does not depend
on the Python version.

```python
from tabstops import char_width, display_width, expand

expand("\u4e2d\tx", 4)  # -> '\u4e2d   x'
expand("\u4e2d\tx", 4, width="display")  # -> '\u4e2d  x'
expand("e\u0301\tx", 4, width="display")  # -> 'e\u0301   x'
char_width("\u4e2d")  # -> 2
char_width("\u00b1", ambiguous_wide=True)  # -> 2
display_width("e\u0301\u4e2d!")  # -> 4
```

### Same rules as the tools

By default a carriage return restarts the column, as in `str.expandtabs`. With
`posix=True` only a newline does, and a backspace moves the column back one place, which
is what `expand` and `unexpand` do. `initial=True` expands only the tabs that start a
line, like `expand -i`.

```python
from tabstops import expand

expand("ab\r\tc")  # -> 'ab\r        c'
expand("ab\r\tc", posix=True)  # -> 'ab\r     c'
expand("abc\b\tx", posix=True)  # -> 'abc\b      x'
expand("\ta\tb", 4, initial=True)  # -> '    a\tb'
```

### Streaming

`Expander` and `Unexpander` take text in pieces and keep the column across them;
`expand_stream` and `unexpand_stream` wrap any iterable of strings, such as an open file.

```python
from tabstops import Unexpander, expand_stream

"".join(expand_stream(["a", "\tb\n"], 4))  # -> 'a   b\n'

engine = Unexpander(4)
engine.feed("  ")  # -> ''
engine.feed("  x")  # -> '\tx'
```

## Command line

```
tabstops expand [-t LIST] [-i] [--display] [--python] [FILE ...]
tabstops unexpand [-t LIST] [-a] [--first-only] [--display] [--python] [FILE ...]
```

The options follow GNU `expand` and `unexpand` (`-t` implies `-a` for `unexpand`), and
so do the defaults. `--display` counts display columns and `--python` applies the
`str.expandtabs` rules. Input is read as UTF-8; bytes that do not decode are passed
through unchanged. `python -m tabstops` works too.

## Why

The standard library expands tabs but never compresses them back, has no tab stop lists,
and counts a wide CJK character or a combining accent as one column. `tabstops` gives
both directions with one stop model, checked against `str.expandtabs` and against GNU
coreutils, and measures columns with current Unicode data.

## License

MIT. See [LICENSE](LICENSE). The width table derives from the Unicode Character
Database; see [LICENSE-UNICODE](LICENSE-UNICODE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
