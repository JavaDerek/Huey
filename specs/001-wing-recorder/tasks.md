# Tasks: Huey Tier A

Spec Kit 1.4.3, supplied spec and plan-input preserved. No extension hooks.

## Phase 1: setup

- [x] T001 Initialise pinned .specify/ and .agents/skills/ on main and copy supplied specs/001-wing-recorder/spec.md and plan-input.md.
- [x] T002 Read primary evidence and record research.md, protocol-evidence.md and wing-tools-evaluation.md in specs/001-wing-recorder/.
- [x] T003 Execute clarify/plan, record answers H1/H2 and held questions in QUESTIONS.md and feature clarification.md.
- [x] T004 Package refestramus_huey with setuptools and pytest/ruff dev tooling in pyproject.toml.

## Phase 2: independent protocol evidence and codec

- [x] T005 Write exact vendor bytes and independently enumerated operations in tests/fixtures/vendor-exchanges.json and tests/independent-operations.json, without deriving either from the gate.
- [x] T006 Write failing codec tests in tests/test_osc.py, then implement strict no-tag reads and s/i/f replies in refestramus_huey/osc.py per data-model.md Message.

## Phase 3: snapshot reading and Story 2 plant (P1)

Independent test: read original/output JSON and hand-assert exactly changed leaf plus synthetic metadata.

- [x] T007 [US2] Write synthetic snapshot fixture and failing file/type/version/path/non-overwrite tests in tests/test_files.py.
- [x] T008 [US2] Implement native lossless snapshot reading, JSON Pointer access and file-only planting with sidecar in refestramus_huey/files.py per data-model.md Snapshot and PlantRecord; H2 assumption is isolated and named.

## Phase 4: mandatory gate and Story 3 replayer (P1)

Independent test: plain UDP test client checks vendor bytes, all refusals and sender audit.

- [x] T009 [US3] Write failing gate and refusal tests in tests/test_safety.py, including all subscription variants, special args, bundles, malformed packets and wrong destinations.
- [x] T010 [US3] Implement one mandatory send boundary and data-file policy in refestramus_huey/safety.py and allow-list.json per data-model.md Gate; requests/replies separated by H1; real list empty.
- [x] T011 [US3] Write failing synthetic capture and replayer tests in tests/test_replayer.py for exact/regenerated replies, discovery, delay/drop/late delivery, lifecycle and sender inventory.
- [x] T012 [US3] Implement validated capture loading and localhost replayer in refestramus_huey/files.py and replayer.py per data-model.md Capture, Exchange and Replayer; unsupported numeric regeneration stays silent per H3.

## Phase 5: Story 4 library/command (P2)

Independent test: public imports and subprocess CLI against synthetic files only.

- [x] T013 [US4] Write failing library and command tests in tests/test_cli.py, then expose API in refestramus_huey/__init__.py and inspect/plant/replay in cli.py.
- [x] T014 [US4] Document exact supported synthetic scope, privacy, assumptions and run commands in README.md and feature quickstart.md.

## Phase 6: review and validation

- [x] T015 Run pytest/coverage/ruff, inspect sender audit and fixture privacy, and record specs/001-wing-recorder/status.md.
- [x] T016 Write documentation-only proposed identity/read allow-list with exact model/firmware evidence gaps in specs/001-wing-recorder/proposed-allow-list.md; leave runtime real list empty.

## Dependencies and execution

T001–T005 precede implementation; each test task precedes its code. Codec and
file functions are independent after evidence. Gate depends on codec; replayer
depends on files and gate; CLI depends on public APIs. Independent research agents
re-read protocol/tool sources while design proceeded. Do not parallelise edits
to shared source files. MVP is native synthetic reading/plant, then replay.
The initial build stopped after evaluation and owner review. The authorised
comparison follow-up is tracked below.


## Follow-up safety review

- [x] T017 [US2] Reproduce finite-number, decoded-type and provenance-marker failures in tests/test_files.py/tests/test_replayer.py, then repair refestramus_huey/files.py.
- [x] T018 [US3] Reproduce multi-sitting replay and ambiguous identity failures in tests/test_replayer.py, then repair refestramus_huey/replayer.py.
- [x] T019 [US3] Reproduce discovery policy bypass and wrong reply forms in tests/test_safety.py, then repair safety.py/allow-list.json; strengthen independent sender checks in tests/conftest.py.
- [x] T020 [US3] Pin exact-address numeric examples with independent tests/fixtures/vendor-values.json and remove unsupported cross-address regeneration in replayer.py.
- [x] T021 Validate wheel/SPDX metadata and update specs/001-wing-recorder/review.md and wing-tools-evaluation.md with measured demo limits.

## Story 1 follow-up — authorised offline snapshot comparison

Independent test: synthetic files with hand-authored exact expected changes;
several N-planted-fault cases do not derive their expectations from comparison.

- [x] T022 [US1] Run clarify/plan on the supplied feature and record release/evidence boundary in specs/001-wing-recorder/clarification.md and plan.md.
- [x] T023 [US1] Write failing independent comparison tests in tests/test_compare.py for changed/added/removed, decoded types, null, empty containers, arrays and JSON Pointer escaping; cite data-model.md Difference.identifier/kind/before/after.
- [x] T024 [US1] Write failing ignore/compatibility/provenance/invalid-file/no-network/no-mutation tests in tests/test_compare.py per data-model.md ComparisonResult.status/ignored_identifiers/compared_count/warnings.
- [x] T025 [US1] Implement compare_snapshots, Difference and ComparisonResult in refestramus_huey/compare.py per data-model.md, with metadata-first incompatibility handling and unchanged H2 success guard.
- [x] T026 [US4] Write failing CLI status/output/ignore tests in tests/test_cli.py, then export comparison in __init__.py and implement compare command in cli.py per contracts/python-api.md.
- [x] T027 [US1] Document exact synthetic scope, counts, ignored-pointer syntax and example runs in README.md and feature quickstart.md; update research/evaluation release record.
- [x] T028 Run full suite, coverage, ruff, privacy checks and installed-wheel comparison smoke; record specs/001-wing-recorder/comparison-status.md.

Dependencies: T022 precedes tests; T023/T024 must fail before T025; T026 tests
must fail before CLI edits. T027/T028 follow implementation. Source changes to
shared files remain sequential; independent standards research can run alongside
fixture authoring. No live client, comparison service dependency or device work.

- [x] T029 Resolve owner questions C1/C2, write failing selected boundary expectations first, then implement their answers: numeric representation differs, all-ignored refuses with FileError/CLI status 6. Revalidate suite and installed wheel.
