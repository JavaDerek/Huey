# Questions

## H1: Gate direction for replayer replies (answered 2026-11-21)

FR-001 sends every datagram through a gate; FR-004 disallows arguments, but OSC
replies must contain arguments. Options: distinguish no-argument requests from
replies to originating localhost clients, validating each reply against the
replayer's approved data; forbid arguments in every direction (blocks replayer).
Recommendation: distinguish directions and keep one mandatory transport gate.
Answer: separate request/reply rules. Requests keep the strict no-argument gate;
replies go only to originating localhost clients and must match approved data.

## H2: Current snapshot signature and JSON leaf encoding (answered 2026-11-21)

The 3.1 manual's p.260 diagram uses snapshot.9 and an older development firmware.
It does not establish the signature emitted by firmware 3.1.2 or all JSON leaf
encodings. Options: allow an isolated, explicitly assumed synthetic snapshot.9
fixture carrying target metadata 3.1.2; hold snapshot-dependent work until current
primary evidence is available. Recommendation: allow the guarded synthetic
assumption without claiming compatibility. Answer: allow guarded synthetic
assumption. Only synthetic snapshot.9 inputs with target metadata 3.1.2 are
accepted by the assumed-compatibility boundary; real/current-format compatibility
is still Unknown and unclaimed.

## H3: Numeric response regeneration (open)

The OSC examples show display/raw/value triples, but a JSON number by itself
does not establish its normalised raw value. Options: regenerate only documented
cases with complete conversions; accept a named synthetic assumption for others;
leave unsupported numeric leaves silent and logged. Recommendation: documented
cases only, with recorded replies preferred and unsupported values logged. No
general float normalisation rule is selected. Follow-up: exact channel-1 examples
-144.0/-1.0/3.0/4.0 are supported. The prior channel-1 0.0 assumption was removed
because that printed example belongs to channel 2.

## WT-1: Review Wing Tools before snapshot comparison (answered 2026-11-21)

See specs/001-wing-recorder/wing-tools-evaluation.md. The public precomputed demo was exercised on Linux, build v3.1-46; controlled synthetic-file
comparison was not run: the service requires a paid account and hosted uploads.
Options: owner arranges a licensed hosted synthetic evaluation; obtain offline
access/permission; release an independently designed local comparison after
reviewing the incomplete evaluation. Recommendation: licensed evaluation if
hosted use is acceptable, otherwise request offline access.
Answer: after reviewing the written evaluation and follow-up summary, the owner
authorised the independently designed offline snapshot comparison on synthetic
fixtures. This selects the local implementation route. It does not claim that
Wing Tools' engine was validated, or authorise hosted uploads, paid access,
real-file compatibility or device traffic. H2's existing success guard remains.

## H4: Real-device release and traffic budget (held)

Options: maintain an empty real-device allow-list; authorise a supervised small
read set after firmware/model evidence and a measured budget. Recommendation:
keep it empty throughout Tier A. Live client, tree walking and write operations
are held; they are not scaffolded here. Documentation-only candidates go in the
proposed-allow-list note, never the runtime data file.

## H5: libwing licence metadata (non-blocking)

libwing 1.0.6 metadata says MIT; its repository LICENSE is Apache-2.0. Options:
obtain clarification before future reuse; choose another native library.
Recommendation: no dependency for Tier A, because libwing implements no OSC.

## C1 — Numeric representation in comparisons (answered 2026-11-21)

JSON uses one number grammar; the existing decoded-evidence check preserves
Python integer/float representation. Options: count 1 versus 1.0 as different,
or normalize mathematically equal numbers. Recommendation: preserve the decoded
representation, consistent with existing evidence validation. Answer: owner
accepted the recommendation. Compare 1 versus 1.0 as different, preserving both
decoded types and values. This is an owner policy, not a requirement of the RFC.

## C2 — Every identifier ignored (answered 2026-11-21)

Options: refuse because nothing remains to compare, or return identical with
zero compared and an explicit ignored count. Recommendation: refuse, avoiding a
success assertion without compared evidence. Answer: owner accepted the
recommendation. Raise FileError with a clear nothing-left-to-compare message;
CLI returns the existing file/validation failure status 6, never identical.
