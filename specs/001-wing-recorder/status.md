# Current follow-up — 2026-11-21

Fresh code/safety review repairs and regression tests are complete: **123 tests
passed**, **87.47% coverage**, ruff and fresh installed-wheel smoke checks passed.
See review.md. The public Wing Tools demo ran on Linux (build v3.1-46), but it
uses precomputed data and does not close WT-1. H3 and actual-device compatibility
remain open. Work is uncommitted on main. The initial build record below is
historical; its Linux-demo and numeric-example statements are superseded here.

# Session status — 2026-11-21

Verified: the official WING Rack listing names firmware 3.1.2. The actual 3.1
protocol PDF was downloaded and read, including OSC and snapshot chapters;
independent vendor bytes and unsafe-operation inventory are recorded. Corrected
subscription wire spellings and the 24-client TCP limit. Read Wing Tools Routing
Diff/terms and libwing primary sources. Spec Kit 1.4.3 was pinned, trialled in
scratch and used for clarify, plan, tasks and implementation; supplied spec and
plan-input are byte-for-byte unchanged. Work remains on main.

Built: refestramus-huey 0.1.0 / refestramus_huey, native synthetic snapshot reading,
typed scalar planting with JSON Pointer and separate audit record, synthetic
capture loading/planting, strict OSC codec, mandatory directional gate and a
localhost-only replayer with byte-exact recorded replies, bounded documented
regeneration, delay/drop/late delivery, counters and full refusal/send audit.
Library and inspect/plant/replay command are documented. No comparison exists.

Validation: **106 tests passed**, **86.39% branch-aware coverage**, ruff passed.
Every real socket send in the suite was constrained to localhost and package sends
were counted below the gate against an independent operation inventory. File
tests forbid sockets. Wheel build succeeded; a fresh isolated environment outside
the checkout imported the installed wheel and ran inspect/replay successfully,
including its packaged allow-list. Development environment: Python 3.12.13,
pytest 9.2.0, pytest-cov 7.1.0, coverage 7.17.4, ruff 0.17.6.

Answered: H1 separates request/reply rules; H2 permits the explicitly guarded
synthetic snapshot.9 assumption with 3.1.2 metadata. Neither is hardware evidence.

Blocked/held:

- **WT-1**: controlled synthetic-file Wing Tools evaluation was not run because
  hosted use needs a paid account/upload workflow. The written evaluation is
  ready for owner review; snapshot comparison stays held.
- **H3**: general numeric reply regeneration lacks complete per-leaf conversion
  evidence. Only documented complete cases are regenerated; other reads stay
  silent and log the missing evidence.
- **H2 follow-up / H4**: actual firmware 3.1.2 snapshot schema, Rack interoperability,
  live allow-list, budget and hardware acceptance remain unverified. No real
  traffic is authorised. The real-device allow-list is empty.
- **H5**: libwing's licence metadata differs from its LICENSE; no dependency used.

No real-device traffic, emulator run, package publication, visibility change,
commit, push or pull request. No code or status file was written in the source
specification repository.
