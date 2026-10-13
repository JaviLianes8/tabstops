# Contributing

Thanks for taking the time. This project keeps a small, predictable shape.

## Setup

```
pip install -r requirements-dev.txt
```

## Before you open a pull request

- Keep public API in `src/tabstops/__init__.py`; internals live in `_`-prefixed modules.
- Add a test for the behaviour you change. Tests inject time, disk and network; they
  never touch the real thing.
- Run `scripts/check.ps1` (format, lint, types, tests) and make sure it passes.
- `pytest -m e2e` builds the wheel, installs it into a fresh virtual environment and
  drives the command; it needs network for the build backend and runs before a release.
- `tests/test_gnu_oracle.py` compares the results with GNU `expand` and `unexpand` when
  they are installed (`gnuexpand` on Ubuntu with the Rust coreutils, or through WSL on
  Windows) and skips otherwise.
- One logical change per commit, imperative subject line.

## Unicode data

The width table in `src/tabstops/_width_data.py` is generated; never edit it by hand.

```
python scripts/fetch_upstream.py        # fetch the pinned UCD files into data/ucd/
python scripts/gen_width_table.py       # regenerate the table
python scripts/gen_width_table.py --check
```

Open an issue first if the change is large or shifts the public API.
