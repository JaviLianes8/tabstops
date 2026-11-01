# tabstops 1.0.0 certification report

Preparation for 1.0.0, dated 2026-11-01. Base: `0b4ad09` (0.2.0).
PyPI's JSON endpoint and an actual installation confirm that 0.2.0 is published.

Progress:
- [x] Resume existing `release/1.0.0` branch; no earlier certification commits or report
- [x] API stability, explicit exports, runnable docstrings, errors and strict typing
- [x] Live Unicode sources, Python documentation and GNU program comparisons
- [x] Contract tests, seeded properties and adversarial inputs
- [x] README badge, GUIDE, dated CHANGELOG, 1.0.0 metadata
- [x] Built wheel and sdist; real CLI and in-place upgrade from PyPI 0.2.0
- [ ] Available Python matrix
- [ ] Mutation round and final four gates
- [ ] Independent reviewer (item 16, separate stage)
- [ ] Five independent QA lenses (item 19, separate stage)
- [ ] PR and guard; merge and publishing remain separate stages

## API and compatibility

The ten names in `__all__`, constructor/function signatures, parameter names and
defaults are retained. A seeded consumer compares 18,000 results and all public
callable signatures before and after upgrading from the installed PyPI 0.2.0 wheel.
All agree. The changes are documented in CHANGELOG and GUIDE:

- `next_stop` validates nonnegative integer columns (excluding booleans).
- Validation errors avoid echoing input values or type names; overlong decimal stops
  use a short conversion-limit error.
- CLI usage messages omit unknown arguments; file failures show a bounded escaped
  basename and errno; ordinary read/write failures exit 1 without a traceback.
- The accidental `annotations` attribute is removed.
- Pending spaces use a counter to avoid repeated copying; closed pipes no longer
  require opening a device file.

The public docs contain 19 passing doctest examples. README and GUIDE expression
results execute as tests. `mypy --strict src tests` passes; `py.typed` ships.
Built-in `TypeError` and `ValueError` remain the documented validation families.
User-defined iterator/subclass exceptions propagate. Output size is intentionally
uncapped; memory use is bounded by caller input and requested expansion output, as
documented in GUIDE. Widths are per code point, not a grapheme or terminal emulator.

## Real ground truth

Retrieved and exercised on 2026-11-01:

- Unicode 18.0.0: the four URLs and exact sizes/SHA-256 in
  `data/ucd/MANIFEST.json`. `scripts/fetch_upstream.py` fetched each into external
  scratch storage selected with `TABSTOPS_UCD`. All hashes match. Tests independently
  derive expected widths and compare both ambiguity modes for all 1,114,112 code
  points. The generated table matches byte for byte. Missing downloads skip the two
  source tests; altered downloads fail before testing. Only derived width facts and
  the Unicode license ship, not the downloaded files.
- Python documentation:
  https://docs.python.org/3/library/stdtypes.html#str.expandtabs . The three example
  outputs were verified against the live HTML. CPython itself is the independent
  reference for 7,200 seeded inputs, including the streaming engine path.
- GNU manual:
  https://www.gnu.org/software/coreutils/manual/html_node/expand-invocation.html .
  The live page confirms the `/N` and `+N` examples. GNU coreutils 8.32 `expand.exe`
  and `unexpand.exe` from Git for Windows are run live: list/tail/flag combinations,
  400 generated lines per case, no-final-newline cases, repeated options, the ASCII
  versus UTF-8 byte-counting distinction, and the recorded short vectors.
  The unexpand manual fetch was unavailable; real program output supplies its oracle.
- PyPI metadata: https://pypi.org/pypi/tabstops/json . The release installed during
  end-to-end testing is 0.2.0. No new release was published.

Source copies and local logs are outside the repository. Hand-picked Unicode vectors
and constructed boundary cases are explicitly test data, not claimed source vectors.

## Tests and packaging

The suite covers every public function and engine method, invalid inputs, parser
grammar, every streaming split in seeded samples, reset behavior, immutable values,
pickle/replace, safe diagnostics, real CLI files/stdin, and failure exit codes.
Seeded parser fuzz: 5,000 malformed strings. Property tests: 3,000 compression round
trips, 2,000 streaming comparisons, 1,000 non-blank preservation cases, 200 reset cases.
Adversarial cases include 100,000-character errors, 50,000 stops and one million pending
spaces split across calls.

`tests/test_e2e_wheel.py` builds both artifacts, checks their contents, installs PyPI
0.2.0 in a fresh venv, records consumer results, upgrades to the wheel, and compares
results and signatures. It runs from an external directory with isolated Python,
then drives the installed console script and `python -m tabstops`. Both licenses,
`py.typed` and the width data are in the wheel; tests, source-regeneration scripts,
docs and the manifest are in the sdist, with no downloaded data or certification notes.

## Pending verification

The available-interpreter matrix, mutation table, final gate results and PR details
will be recorded here before preparation is complete. Independent review and five QA
lenses have not run for 1.0.0. No verdict from the earlier 0.2.0 review is carried over.
