# tabstops

Expand and unexpand tabs with a tab-stop-aware column model

## Install

```
pip install tabstops
```

## Usage

```python
from tabstops import expand, unexpand

# Tabs to spaces, aligned to the next tab stop on each line.
expand("name\tvalue")          # 'name    value'
expand("a\tb", tabsize=4)      # 'a   b'

# Spaces back to tabs at the tab stops. Leading runs only by default.
unexpand("        x")          # '\tx'
unexpand("a       b", all=True)  # 'a\tb'
```

The column resets at each newline, so every line aligns on its own. A single space
that merely lands on a tab stop is left as a space, matching the usual `unexpand`.

## Why

The standard library expands tabs but never compresses them back. `str.expandtabs`
covers one direction only, and there is no built-in `unexpand`: turning runs of
spaces back into tabs at the correct tab stops has no maintained, typed, zero-dep
option on PyPI (Perl's `Text::Tabs` has no Python peer). `tabstops` provides both
directions with the same tab-stop model, so a round trip over already-expanded text
is lossless.

## License

MIT. See [LICENSE](LICENSE).

## Links

- Website: https://lianes8studio.com
- GitHub: https://github.com/JaviLianes8
- LinkedIn: https://www.linkedin.com/in/jlianes/
