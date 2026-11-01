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
- [x] Available Python matrix
- [x] Mutation round and final four gates
- [ ] Independent reviewer (item 16, separate stage)
- [ ] Five independent QA lenses (item 19, separate stage)
- [x] PR #3 opened; guard CLEAN; merge and publishing remain separate stages

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
  require opening a device file. Help/version flush failures now exit 1 instead of 120.

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
docs, the manifest and Hatchling's standard `.gitignore` are in the sdist, with no
downloaded data, bytecode, scratch files or certification notes.

## Supported interpreters (item 10)

`requires-python` remains >=3.10. The actual executable inventory was checked, not
only launcher registration. CPython 3.14.6 at `C:/Python314/python.exe` is the one
available installation. The suite runs from the sdist with `src` excluded against
an installed wheel in a fresh venv: 342 passed, 1 skipped, 1 e2e deselected.
The regeneration-only test skips without source;
the external Unicode sweep and GNU oracle still run. The CLI version command passes.

Unavailable: 3.10.19, 3.10.22; 3.11.5, 3.11.14, 3.11.17; 3.12.12, 3.12.15;
3.13.2, 3.13.16; 3.14.2, 3.14.8, and their free-threaded variants. These 13 launcher
entries point at deleted directories. Python 3.10 to 3.13 and free-threaded Python
could not be run in this session; their classifiers retain the existing support promise.

## Author mutation round (item 18)

At `c7e8bd1`, 25 deliberate bugs were applied individually in an isolated tree with
bytecode writing disabled. Each failed an assertion/expected-exception contract; no
collection failures or timeouts were counted as kills. After the CLI flush correction,
M23 to M25 were rechecked and M26 to M28 added on the corrected code. All 28 distinct
mutations are killed, with no survivor. The normal suite passes after restoration.

| Id | Deliberate bug | Caught by |
| --- | --- | --- |
| M01 | strict stop boundary | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M02 | relative tail base lost | `tests/test_cert_contract.py::test_tab_stops_copy_pickle_and_replace` |
| M03 | interval off by one | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M04 | Unicode digits accepted | `tests/test_stops.py::test_parse_rejects_bad_lists[\u0664]` |
| M05 | boolean column accepted | `tests/test_cert_contract.py::test_next_stop_refuses_non_integer_columns[True]` |
| M06 | negative one column accepted | `tests/test_cert_contract.py::test_next_stop_refuses_negative_columns` |
| M07 | wrong column exception | `tests/test_cert_contract.py::test_next_stop_refuses_non_integer_columns[True]` |
| M08 | unsafe parse message | `tests/test_cert_contract.py::test_invalid_values_are_not_echoed` |
| M09 | carriage return reset removed | `tests/test_cli.py::test_the_tool_follows_posix_unless_asked_for_python` |
| M10 | initial flag ignored | `tests/test_docs_examples.py::test_documented_results_are_true` |
| M11 | backspace advances | `tests/test_docs_examples.py::test_documented_results_are_true` |
| M12 | finite stop padding doubled | `tests/test_docs_examples.py::test_documented_results_are_true` |
| M13 | stream column lost | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M14 | zero interval no longer drops tabs | `tests/test_docs_examples.py::test_documented_results_are_true` |
| M15 | pending spaces doubled | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M16 | held space never compressed | `tests/test_cli.py::test_held_blanks_are_written_at_the_end` |
| M17 | all flag ignored | `tests/test_cli.py::test_unexpand_tab_list_implies_all` |
| M18 | unexpand flush loses pending spaces | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M19 | unexpand flush loses reset | `tests/test_properties.py::test_engines_start_over_after_flush` |
| M20 | ambiguous wide ignored | `tests/test_cli.py::test_display_columns` |
| M21 | width lookup boundary shifted | `tests/test_cert_contract.py::test_public_callable_examples_run` |
| M22 | unsafe width message | `tests/test_cert_contract.py::test_invalid_values_are_not_echoed` |
| M23 | CLI tabs no longer imply all | `tests/test_cli.py::test_unexpand_tab_list_implies_all` |
| M24 | CLI incomplete UTF-8 tail lost | `tests/test_cli.py::test_an_incomplete_character_at_the_end_is_kept` |
| M25 | CLI read errors report success | `tests/test_cli_errors.py::test_read_failure_has_status_one_and_safe_message` |
| M26 | help/version flush removed | `tests/test_cli_errors.py::test_help_and_version_flush_failures_exit_one[argv0]` |
| M27 | failed output wrapper retained | `tests/test_cli_errors.py::test_failed_stdout_flush_is_not_retried_at_shutdown` |
| M28 | ordinary flush failure not silenced | `tests/test_cli_errors.py::test_failed_stdout_flush_is_not_retried_at_shutdown` |

## Scaling and final gates

On this PC, 100,000 / 400,000 / 1,600,000 pending blanks took approximately
0.14 / 0.39 / 1.43 seconds. Parsing 10,000 / 40,000 / 160,000 listed stops took
0.03 / 0.07 / 0.40 seconds. These measurements support linear scaling for the
adversarial shapes; output expansion itself is necessarily proportional to output size.

Each gate was invoked separately and exited 0: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, `pytest` (343 passed, the opt-in wheel test deselected).
`mypy --strict src tests` also exits 0. Every pytest invocation uses a 300-second
per-test timeout and an explicit scratch basetemp. The installed-wheel e2e test,
including upgrade, CLI failure paths and closed help/version output, passes separately
(1 passed, 343 deselected).
`twine check --strict` passes both built artifacts.

## Scorecard

| Item | Preparation result |
| --- | --- |
| 1 | PASS: retained signatures/defaults; documented boundary changes |
| 2 | PASS: exact ten-name surface, accidental export removed |
| 3 | PASS: 19 doctest examples and executable README/GUIDE results |
| 4 | PASS: strict source/test typing; shipped py.typed |
| 5 | PASS: documented TypeError/ValueError and bounded diagnostics |
| 6 | PASS: 343 tests plus real installed-wheel end-to-end test |
| 7 | PASS: fetched Unicode and spec text, live CPython and GNU programs |
| 8 | PASS: built-wheel external consumer, CLI, PyPI 0.2.0 upgrade |
| 9 | PASS: deterministic fuzz/properties and large-input scaling |
| 10 | PASS for available interpreter; unavailable versions listed above |
| 11 | PASS: README badge, comparisons, absolute links, strict twine check |
| 12 | PASS: 1.0.0 CHANGELOG dated 2026-11-01 |
| 13 | PASS: version, stable classifier, license, URLs, no runtime dependencies |
| 14 | PASS: inspected wheel/sdist, licenses included, no downloaded corpora |
| 15 | PASS: all four gates exit 0 separately |
| 16 | PENDING: independent reviewer is a separate stage |
| 17 | READY: PR #3 and guard CLEAN; merge and publication pending |
| 18 | PASS: 28 distinct mutations killed |
| 19 | PENDING: all five independent QA lenses are a separate stage |

## Review status

No independent reviewer or QA lens has passed the 1.0.0 branch yet. No verdict from
the earlier 0.2.0 review is carried over. Merge and publication have not been performed.

## Handoff

[PR #3](https://github.com/JaviLianes8/tabstops/pull/3) targets `main` from
`release/1.0.0`, titled `tabstops 1.0.0`. The required guard prints `CLEAN: tabstops #3`.
The tested implementation is `b7deab4`; subsequent changes only record this handoff.
Preparation items 1 to 15 and 18 are complete. Independent review, the five QA lenses,
merge and publication remain pending.
