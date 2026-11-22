# Library and command contract

Library: load_snapshot, compare_snapshots, plant, load_capture, parse_message,
encode_read, encode_reply, Replayer; ComparisonResult and Difference records.
No console client or state-changing console API.

`compare_snapshots(before, after, *, ignore=(), ignore_patterns=())` accepts native
snapshot paths or Snapshot objects. `ignore` contains literal JSON Pointers;
`ignore_patterns` uses case-sensitive full-pointer fnmatchcase globs (* spans /).
Inputs are not mutated; no network socket opens. ComparisonResult.to_dict()
provides JSON-safe output including both identities, reason, warnings, counts,
requested ignores, actual ignored identifiers and ordered differences. Missing
sides of added/removed differences are omitted; actual null is retained as null.

The command refestramus-huey offers inspect, compare, plant and replay. Compare
arguments: BEFORE AFTER, repeatable --ignore POINTER and --ignore-pattern GLOB.
It prints JSON to stdout, status first. Identical=0, different=1,
not_comparable=3, gate refusal=5, file/usage failure=6; argparse syntax errors=2.
No unreachable/device command or placeholder is implemented.

Compatibility is checked before masking differences. Known-format synthetic inputs
with differing model/firmware return not_comparable from metadata alone; no
parameter values are compared. Both matching profiles must pass the unchanged H2
synthetic snapshot.9/wing-rack/3.1.2 guard for success. Unknown format/provenance
refuses. Owner answers C1/C2: integer/float representation changes are differences
(including 1 versus 1.0); all-ignored inputs raise FileError and CLI status 6.

Output always warns that snapshots omit read-only objects, actual 3.1.2 schema
compatibility is unverified and real console files contain private information.
Plant creates a new file and sidecar, never edits the input. Replay remains
localhost-only and generated replies remain labelled as synthetic interpretation.
