# Clarification execution — 2026-11-21

Executed Spec Kit 1.4.3 speckit-clarify using check-prerequisites.sh --json
--paths-only with SPECIFY_FEATURE_DIRECTORY=specs/001-wing-recorder. The supplied
spec is preserved. The user's QUESTIONS.md procedure replaces interactive spec
rewriting. No extension hooks or checklists are installed.

Scope is clear: snapshot reading, file-only plant, synthetic localhost replayer,
codec and mandatory gate. Comparison stays held pending evaluation review.
Live client, subscriptions, meters, native protocol and writes stay held.
H1/H2 were asked and answered: separate request/reply rules, and allow the guarded
synthetic snapshot.9 / 3.1.2 assumption. Answers are recorded in QUESTIONS.md.
H3 (numeric regeneration) is isolated from byte-exact recorded replay and generic
JSON reading. H4 is held work. No ambiguity has been silently resolved.


## Story 1 release — 2026-11-21

The owner has selected the independently designed local snapshot comparison after
reviewing the Wing Tools evaluation and summary. Re-ran the pinned clarify path
prerequisite. H2 remains unchanged: successful comparison is synthetic snapshot.9
with target metadata 3.1.2 only. Real-file compatibility and H3 are not needed to
compare JSON values without interpreting numeric console units.

Exact ignores use JSON Pointers; glob ignores are a separate API/CLI option using
stdlib fnmatchcase. Comparison includes scalar leaves and empty containers,
retains decoded number types, reports both values and never mutates inputs.
Model/firmware compatibility precedes all ignores. Mismatch reports metadata only
and cannot produce identical. Equal but unsupported profiles still refuse. Unknown
formats/real markers refuse. These are explicit plan-level implementation choices;
no device semantics or new format are inferred. Source spec and plan-input remain
unchanged. Subsequent standards review exposed two policy questions, C1/C2 in
QUESTIONS.md: mixed integer/float representation and all identifiers ignored.
Owner answers received 2026-11-21: preserve numeric representation (1 versus 1.0
is different) and refuse all-ignored requests. T029 applies both answers using
tests written red before source changes. H2 and all real-device holds remain.
