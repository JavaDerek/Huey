# Offline comparison session — 2026-11-21

## Verified

Personally re-read the primary Python fnmatch documentation and RFCs 6901/8259;
links and findings are in research.md. Used pinned Spec Kit 1.4.3 clarify, plan,
tasks and implement workflows against the supplied feature. spec.md and
plan-input.md remain byte-for-byte identical to their supplied originals.

Linux, Python 3.12.13: **165 passed**, **89.73%** branch-inclusive coverage; Ruff
passes. Hand-written expectations cover one/two/three planted changes, typed
values, added/removed versus null, empty containers, object/array replacements,
pointer escaping, exact/glob ignores, model/firmware checks before ignores and
invalid-file refusals. Tests prohibit sockets and verify unchanged source files
and input objects. Existing sender/gate/refusal tests still pass.

Built refestramus-huey 0.1.0 locally, installed the rebuilt wheel in a separate
temporary environment, and exercised its public library and CLI outside the
checkout: identical=0, different=1, ignored difference=0, incompatible=3. The
installed real-device allow-list is empty. Privacy scan found no private project
name, people's names or rig-specific terms in the public-bound code/docs.

Owner answers C1/C2 are now applied. First reproduced six failures against the
approved numeric/all-ignored outcomes, then removed the pending-policy numeric
guard and finalised the all-ignored error. New tests preserve integer/float types
in both directions and check CLI statuses. Rebuilt/reinstalled wheel smoke passed
outside the checkout: numeric representation difference=1, exact ignore=0,
all-ignored=6 with no success output. The installed real-device list remains empty.

## Built

compare_snapshots, Difference and ComparisonResult; compare CLI with deterministic
JSON output, exact/pattern ignores and explicit counts/coverage warnings. Known
synthetic model/firmware mismatch produces metadata-only not_comparable before
ignores. Matching profiles still pass the unchanged H2 success guard. Empty
containers survive traversal; object/array replacements retain structure even
when scalar pointers coincide. Missing sides are omitted rather than fabricated
as null. No runtime dependencies or transport-policy changes were added.

## Answered

- **C1:** integer/float representation counts as a difference, including 1 versus
  1.0, under the owner's explicit policy. Both values retain their decoded types.
- **C2:** all identifiers ignored raises FileError, CLI status 6, with a clear
  nothing-left-to-compare error. No identical result is emitted.

## Blocked and held

- **H2 follow-up:** actual exported snapshot/model/firmware evidence. Successful
  comparison remains the approved assumed synthetic snapshot.9 / wing-rack /
  3.1.2 profile; no real-file compatibility is claimed.
- **H3:** general numeric OSC regeneration evidence, unrelated to ordinary JSON
  comparison. Unsupported numeric replay remains silent/logged.
- **H4:** supervised release, allow-list and traffic-budget evidence. No device
  client or real traffic is implemented or authorised.

WT-1's owner review released independent local comparison. Wing Tools' hosted
engine remains unvalidated; no proprietary implementation was reused. Work stays
on main, uncommitted. No messages sent, package published, repository visibility
changed, device contacted or held write feature scaffolded.
