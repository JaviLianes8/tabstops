# tabstops 1.0.0 certification report

Certification finalized 2026-11-02. Base: `0b4ad09` (0.2.0).
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
- [x] Independent reviewer: PASS, round 1
- [x] Five independent QA lenses: all PASS
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
| 16 | PASS: independent reviewer, round 1; scorecard below |
| 17 | PASS for release handoff: PR #3; merge and publication reserved |
| 18 | PASS: 28 distinct mutations killed |
| 19 | PASS: all five independent QA lenses; final verdicts below |

## Review status

All findings from QA lenses a, c and e are closed by their final PASS reports.
The independent reviewer reports PASS with no findings. No verdict from the earlier
0.2.0 review is carried over. Merge and publication have not been performed.

## Final QA verdicts

Report paths are relative to this repository checkout. Each reviewed revision is
an ancestor of `7b38ddd510c96a09f773c76068dd602a6b178b85`.

| Lens | Rounds | Final verdict | Report path | Commit |
| --- | --- | --- | --- | --- |
| a: API and docs | 2 | PASS | `../../scratch/tabstops-cert/lens-a-r2/REPORT.md` | `d624f5277e178e8fad857cc592abcfd80b480b3c` |
| b: correctness and ground truth | 1 | PASS | `../../scratch/tabstops-cert/lens-b-r1/REPORT.md` | `7a8a4e73b903d30b3e7a1b75d8e726da4d31be65` |
| c: robustness | 2 | PASS | `../../scratch/tabstops-cert/lens-c-r2/REPORT.md` | `d624f5277e178e8fad857cc592abcfd80b480b3c` |
| d: packaging and real e2e | 1 | PASS | `../../scratch/tabstops-cert/lens-d-r1/REPORT.md` | `7a8a4e73b903d30b3e7a1b75d8e726da4d31be65` |
| e: contract strength | 4 | PASS | `../../scratch/tabstops-cert/lens-e-r4/REPORT.md` | `7b38ddd510c96a09f773c76068dd602a6b178b85` |

The reviewer reran ground-truth and packaging checks at the final reviewed revision,
supplementing the earlier b/d results. Production code has not changed since the
a/c PASS revision; subsequent fixes add contracts and update this report.

## Independent review scorecard

Round 1, 2026-11-02: PASS, no findings. Report:
`../../scratch/tabstops-cert/review-r1/REPORT.md`.
Reviewed commit: `7b38ddd510c96a09f773c76068dd602a6b178b85`.

The table summarizes the review evidence. Item 17 passes the requested release
handoff scope; the review explicitly records merge as pending. Neither this table
nor the review claims that merge or publication has occurred.

| Item | Final result | Review evidence |
| --- | --- | --- |
| 1. Stable API | PASS | Signatures/defaults retained; documented changes; 18,000 upgrade results agree |
| 2. Public surface | PASS | Exact ten exports; no accidental attributes or private imports in examples |
| 3. Runnable documentation | PASS | 19 doctest examples and README/GUIDE results execute |
| 4. Strict typing | PASS | Strict source/test checks; no public Any; py.typed in both artifacts |
| 5. Errors | PASS | Documented error families, bounded diagnostics and CLI failure checks |
| 6. Contracts | PASS | 384 regular tests and separate installed-wheel e2e pass without skips |
| 7. Ground truth | PASS | Fresh pinned Unicode downloads, exhaustive widths, CPython and live GNU checks |
| 8. Real e2e | PASS | Isolated wheel/sdist installs, external consumers, CLI and PyPI 0.2.0 upgrade |
| 9. Robustness | PASS | Seeded fuzz, properties, hostile inputs and scaling checks |
| 10. Python matrix | PASS | Available CPython 3.14.6 passes; unavailable interpreters disclosed above |
| 11. README | PASS | Strict artifact checks, rendered Markdown, absolute links and badge |
| 12. CHANGELOG | PASS | Dated 1.0.0 section covers stability and intentional behavior changes |
| 13. Metadata | PASS | 1.0.0, stable classifier, Python support, MIT, URLs and no runtime dependencies |
| 14. Contents | PASS | Wheel/sdist inspected; licenses and typing marker included; no scratch or corpora |
| 15. Gates | PASS | Four required commands each exit 0 independently |
| 16. Review | PASS | Fresh review at the pinned revision; no findings |
| 17. Release handoff | PASS | Open PR #3 from release/1.0.0 to main; merge/publication reserved |
| 18. Mutations | PASS | Existing 28-row table verified; 12 independent mutations killed |
| 19. Five QA lenses | PASS | All five reports and supporting evidence verified; all findings closed |

## QA lenses, round 1 fixes

Date: 2026-11-01. Reviewed base: `7a8a4e73b903d30b3e7a1b75d8e726da4d31be65`.
Fix commit: `13a4ba2b1191b412330a2b441e8a050b77080dc1`
(`fix large integer tab handling and strengthen qa contracts`).
All seven supplied findings are addressed; none are disputed.

| Finding | Change and contract |
| --- | --- |
| A-01, low | GUIDE and expansion docstring distinguish column-rule compatibility from the C-integer restriction. README wording is consistent. Boundary cases cover `2**31 - 1`, `2**31`, `2**63`, and `10**100`. |
| C-01, medium | Cache unexpansion boundaries and track local offsets, including after enormous tab jumps. The contract bounds stop calculations across 16,000 blanks split into chunks, with tab, text and backspace prefixes. Large listed-stop tails and resets are covered. |
| C-02, medium | Restrict the native expansion fast path to integers at most `2**31 - 1`; larger intervals use the engine. Empty and tab-free input now agrees with `TabStops`, `Expander`, and streaming calls. |
| C-03, low | Reject unsupported constructor containers with a generic `TypeError` before tuple conversion. Contracts also preserve legacy sequence iteration and exceptions raised by caller-written iterators. |
| E-01, medium | Add an initial-only `Expander` reuse contract after nonblank input and `flush`. Existing reset behavior is retained. |
| E-02, medium | Assert exact expansion output lists for empty chunks, zero-size tab removal, and mixed chunks. Existing one-output-per-chunk behavior is retained. |
| E-03, medium | Assert CLI unexpansion of an ambiguous-width character with and without `--ambiguous-wide`, both through a subprocess and the installed wheel. Existing option forwarding is retained. |

Before implementation changes, the new regression file produced 14 failures and
9 passes: nine oversized-integer expansion cases, four repeated-arithmetic cases,
and the constructor diagnostic failed. After the fixes and four additional
compatibility cases, all 27 new contracts pass. CHANGELOG records all three
implementation behavior changes; the E findings require tests only.

The three surviving mutations from lens e were applied separately in a scratch copy
and each failed an assertion in the new contract suite. No timeout or collection
error was counted as a kill:

| Lens e mutation | Regression that catches it |
| --- | --- |
| M24: omit initial-only reset on flush | `test_initial_expander_starts_over_after_flush` |
| M26: omit empty expansion chunks | `test_expand_stream_preserves_empty_results` |
| M55: omit CLI ambiguous-width forwarding | `test_cli_unexpand_ambiguous_width` |

Three-sample median timings for `unexpand(' ' * n, 10**n)`, with text and integer
construction outside the timed region, were 0.0242 / 0.0651 / 0.0911 / 0.1861 seconds
at n = 16,000 / 32,000 / 64,000 / 128,000. Endpoint growth is 7.69x for 8x input,
compared with the reported 60x. With a leading tab jumping to the huge interval,
the same sizes took 0.0152 / 0.0310 / 0.0335 / 0.0703 seconds. Every output was
checked exactly. Timing is supplementary evidence; the shipped work-bound test
does not depend on wall-clock thresholds.

Verification on CPython 3.14.6: each required gate exited 0 independently:
`ruff format --check .`, `ruff check .`, `mypy --strict src`, and `pytest`
(370 passed, 1 opt-in e2e test deselected). Strict typing of both source and tests
also passed. The installed-wheel build, PyPI 0.2.0 upgrade and CLI checks passed
separately (1 passed, 370 deselected). GNU and pinned Unicode comparisons ran in
the full suite. All pytest invocations used a 300-second per-test timeout.

Local evidence is under `../../scratch/tabstops-cert/fix-r1/`:
`before.log`, `scaling.json`, and `M24.log`, `M26.log`, `M55.log`. Test basetemps,
build temporary files and the mutation copy also remain under that scratch directory.

## QA lenses, round 2 fixes

Date: 2026-11-01. Reviewed base: `d624f5277e178e8fad857cc592abcfd80b480b3c`.
Fix commit: `2e5b00698bee375357e4fdb217fc1af67b688350`
(`cover huge interval expansion failure contracts`).
The supplied finding E-04 is addressed; none are disputed.

| Finding | Change and contract |
| --- | --- |
| E-04, medium | Add `test_large_integer_expansion_rejects_impossible_output_size` and `test_large_integer_expansion_rejects_non_text`. They require `OverflowError` or `MemoryError` for `expand('\t', 2**100)` and `TypeError` for `expand(None, 2**100)`. |

Both contracts pass on the reviewed production code. This finding concerns missing
coverage, so production behavior and the API are unchanged; no behavior change needs
a CHANGELOG entry. The size exceeds `Py_ssize_t` to fail before a huge allocation.

N03 was applied in a scratch copy immediately before the engine fallback: return the
input unchanged when `tabs` is an integer greater than `2**31 - 1`. Both new contracts
fail with `DID NOT RAISE` (2 failed, 27 deselected). This is a behavioral kill, not an
import failure or timeout. The scratch source was restored and compared byte for
byte with the repository source. Evidence: `fix-r2/N03.log` and `fix-r2/check_n03.py`
under `../../scratch/tabstops-cert/`.

Lens e's round 3 report confirms E-04 is fixed. Its round 2 report confirms
that E-01, E-02 and E-03 are fixed.

Verification on CPython 3.14.6: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `pytest -o addopts= -q --timeout=300` each exited 0.
The complete suite passed: 373 tests, including installed-wheel installation,
the PyPI 0.2.0 upgrade, GNU comparisons and pinned Unicode checks, with no skips.
`mypy --strict src tests` also passed. TEMP, TMP and pytest basetemps were under
the round's scratch directory; all execution was local.

## QA lenses, round 3 fixes

Date: 2026-11-01. Reviewed base: `0d37f46ba2e738dcabc60e47eaf0c2340955457e`.
Fix commit: `d5c6c1c436b1afa445c6458d3669227722df5a5c`
(`cover large interval expansion option validation`).
The supplied finding E-05 is addressed; none are disputed. Lens e's round 3 report
confirms E-04 is fixed. Its round 4 PASS report confirms E-05 is fixed.

| Finding | Change and contract |
| --- | --- |
| E-05, medium | Add `test_large_integer_expansion_rejects_ambiguous_wide_without_display` and `test_large_integer_expansion_rejects_invalid_width`. Both require `ValueError` for empty and nonempty tab-free text with intervals `2**31`, `2**63`, and `2**100`. The former uses `ambiguous_wide=True` with default width; the latter uses `width="cells"`. |

All 12 new cases pass on the reviewed implementation. The two E-04 contracts remain
in place. This is a coverage correction: production behavior and the public API are
unchanged, so no behavior change needs a CHANGELOG entry.

The exact N10 mutation was inserted before `expand()` constructs its engine in a
scratch copy: return tab-free strings unchanged when the integer interval exceeds
`2**31 - 1`. All 12 new cases fail with `DID NOT RAISE ValueError` (12 failed,
29 deselected), establishing a behavioral kill without collection errors or timeouts.
The complete QA contract file passes before mutation and after restoration
(41 passed each). Restored source matches the repository source byte for byte.

| Lens e mutation | Regression that catches it |
| --- | --- |
| N10: bypass option validation for tab-free large-integer expansion | Both new option-validation contracts, all 12 parameter combinations |

Verification on CPython 3.14.6: `ruff format --check .`, `ruff check .`,
`mypy --strict src`, and `pytest -o addopts= -q --timeout=300` each exited 0.
The complete suite passed: 385 tests, including installed-wheel installation,
the PyPI 0.2.0 upgrade, GNU comparisons and pinned Unicode checks, with no skips.
`mypy --strict src tests` also passed. Every pytest invocation used a 300-second
per-test timeout. TEMP, TMP, TMPDIR, pip cache and pytest basetemps were under
the round's scratch directory; all execution was local.

Evidence: `check_n10.py`, `baseline.log`, `N10.log`, and `restored.log` under
`../../scratch/tabstops-cert/fix-r3/`.

## Handoff

[PR #3](https://github.com/JaviLianes8/tabstops/pull/3) targets `main` from
`release/1.0.0`, titled `tabstops 1.0.0`. The required guard prints `CLEAN: tabstops #3`.
The preparation implementation was `b7deab4`; round 1 fixes and their tested commit
are recorded above. All certification checks, independent review and QA
re-verification are complete. Merge and publication remain separate steps.
