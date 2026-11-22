# Implementation Plan: Huey Tier A

**Git branch**: main | **Feature**: 001-wing-recorder | **Date**: 2026-11-21
Input: supplied spec.md and plan-input.md, preserved without regeneration.

## Summary

Implement a small Python file library, command and localhost-only UDP stand-in.
Read native JSON losslessly and plant a new synthetic file plus audit sidecar.
Replay recorded bytes first; regenerate only evidence-backed cases. The initial
build stopped after the Wing Tools evaluation; the owner has now released the
offline synthetic comparison follow-up below.

## Technical Context

- Python 3.10+, setuptools; pytest/pytest-cov/ruff in dev extra; Linux.
- Package/command refestramus-huey, import refestramus_huey. MIT.
- Runtime: stdlib only; JSON, struct, UDP, one worker thread and scheduled replies.
- Target firmware 3.1.2; exact manual V3.1.0 says 3.1.0 and above. Real behavior
  unverified. No real-device operations ship in the allow-list.
- File identifiers use JSON Pointer (RFC 6901), an existing standard. Wire paths
  use canonical OSC notation; no invented real-device parameter schema.
- Capture JSON is an explicitly local, versioned exchange envelope per FR-010,
  with raw hex, decoded messages, timestamp, timing, failures and segments. No
  capture collector is built. Synthetic capture fixtures and loading only.
- Replayer binds IPv4 127.0.0.1 with numeric endpoints only; no hostname resolution,
  broadcast or non-loopback bind/destination. Unknown reads stay silent and logged.
- H1/H2 are answered: separate reply rules and guarded synthetic-format assumption. H3 limits numeric
  regeneration; no arbitrary normalisation or model-independent path claims.

## Constitution Check

Verification first; TDD; independent protocol examples and allowed-operation
inventory; sender instrumentation below the final gate. No real traffic, no
console-write interface. Snapshot comparison is file-only. Synthetic fixtures only. File functions
perform no networking. Existing LICENSE is retained. No commits or publication.
Post-design result: pass within owner-approved H1/H2 limits. H3 remains an explicit
limit on regeneration; no unknown conversion is inferred.

## Phase 0: verification

Read the actual 3.1 PDF (OSC chapter and snapshot appendix), official firmware
listing, libwing README/licence, Wing Tools Routing Diff and service terms.
Independent research agents re-read protocol fixtures and existing tools per
speckit-plan. Results, exact sources and unresolved gaps live in research.md,
protocol-evidence.md and wing-tools-evaluation.md. No emulator is required.

## Phase 1: design and structure

```text
refestramus_huey/{__init__,files,osc,safety,replayer,cli}.py
refestramus_huey/allow-list.json
tests/{test_files,test_osc,test_safety,test_replayer,test_cli}.py
tests/fixtures/{synthetic.snap,synthetic-capture.json,vendor-exchanges.json}
tests/independent-operations.json
specs/001-wing-recorder/{data-model,quickstart,tasks,research}.md
specs/001-wing-recorder/contracts/python-api.md
```

Only the transport module calls socket.sendto. Gate rules apply immediately
above it. A caller can supply a narrower predicate, never replacement policy.
Inputs and counters are available through the library. Delay, loss and late
delivery use monotonic scheduling and deterministic seeds for tests. No client
for consoles is implemented; independent tests use plain local sockets.

## Complexity Tracking

Owner approved the reply-direction clarification and guarded synthetic snapshot
assumption (H1/H2). No real-device exception exists. Use Spec Kit feature metadata
to work on main without a feature branch. No git automation extension installed.


## Story 1 follow-up: independently designed offline comparison

Release: current owner instruction, 2026-11-21. Use the existing supplied Story 1;
do not regenerate the spec or reuse Wing Tools implementation. Prior evaluation
and Linux demo observation satisfy the review milestone; its engine remains
unvalidated. No service dependency, account, payment or upload is introduced.

Language/tooling unchanged, zero new dependencies. New module compare.py exposes
compare_snapshots and result/difference records. CLI compare emits readable JSON.
Comparison uses JSON Pointer terminal identifiers (scalars and empty containers),
with strict decoded type/value comparison and deterministic lexical ordering.
Arrays are indexed; branch-to-leaf replacements appear as added/removed terminal
identifiers. Object ordering and whitespace alone do not create differences.

Two distinct ignore inputs: exact pointer identifiers and fnmatchcase full-pointer
globs; * may span /. Report the matched union once, including unchanged matches,
and show the number of remaining identifiers compared. An all-ignored comparison
refuses rather than emitting success without comparisons. No implicit defaults,
tolerances, timestamp ignores or hidden volatile-field exclusions are introduced.

Read and validate native format/synthetic marker/metadata first, then detect model
or firmware mismatch before ignores. Incompatible files produce metadata plus
not_comparable, no value comparison. For compatible metadata, run the unchanged
H2 synthetic-profile guard on both inputs before comparing any parameters. This
permits safe mismatch diagnostics without accepting a different model/firmware for
successful comparison or replay. Newer/unknown format signatures refuse.

Plan-level CLI statuses: identical=0, different=1, not_comparable=3, file error=6.
Existing argparse syntax status2 and transport-refusal status5 remain unchanged.
No unreachable/device command is added. Every result states omitted read-only
objects, synthetic compatibility limits and file privacy.

TDD: independent hand-written expected differences, additions/removals, typed/null
and empty-container cases, glob/literal ignores, compatibility-before-ignore,
invalid-format/provenance tests, zero-network and source immutability. Verify
several N-fault plant cases independently. Then CLI tests, full existing suite,
ruff and installed-wheel smoke. No runtime gate or allow-list change is needed.
Constitution check before/after design: pass within the approved synthetic scope.
No extension hooks are installed. Exact supported real snapshot format remains
blocked under H2 follow-up and is not claimed by this story's tests.

Implementation clarification: object/array type changes must retain container
structure even when terminal pointers/values coincide. Report such replacements
once at the parent, replacing descendants in comparison/ignore counts. C1/C2 are
now answered owner questions: cross integer/float representation comparisons are
different, including 1 versus 1.0; all-ignored inputs refuse with FileError. T029
tests both library/CLI outcomes before implementing the answers.
