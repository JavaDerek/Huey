# Data model

- Snapshot: preserved native JSON tree, root identity and type signature,
  synthetic status derived from native creator_sn marker. Known document format
  only; unknown versions refused. Current target-format assumption is H2.
- PlantRecord: schema_version=1, synthetic=true, source/output names, changes
  with JSON Pointer, old/new JSON values, source hash. Separate from console state.
- Capture: schema_version=1, synthetic marker, identity (address/name/model/
  serial/firmware), exchanges, skipped paths, failures, budget and segments.
- Exchange: request/reply raw hex, decoded forms, timestamp, elapsed seconds and
  segment. A reply may be absent for timeout. No live capture writer/client.
- Message: address, type tags, arguments; an absent type tag differs from empty.
- Gate: immutable direction-specific policy loaded from one allow-list data file;
  no real-device entries. Request bytes must exactly encode a canonical approved
  no-argument operation, not merely parse to one. Reply policy follows the H1 directional clarification.
- Replayer: immutable input data, bound local endpoints, counters and full hex
  audit records; a scheduled queue determines delay/drop/late delivery. Stop closes
  sockets and joins its worker. No mutation of console state is exposed.

`Snapshot` planting changes existing scalar leaves only, preserves exact JSON
types (including bool versus int), never overwrites input/output files, and marks
the output synthetic using native metadata. Files are sorted UTF-8 JSON.
`Exchange` data must validate before starting a socket. `Message` accepts only
strictly padded s/i/f wire forms; bundles and unsupported tags are rejected.
No unknown float display/raw conversion is inferred from JSON.


## Snapshot comparison

- Difference.identifier: canonical RFC 6901 pointer to a terminal JSON value.
  Difference.kind: changed/added/removed. Difference.before/after retain decoded
  values and types; kind distinguishes absent from an existing null. Serialized
  output omits the absent side rather than substituting null for missing data.
- ComparisonResult.status: identical/different/not_comparable. Differences are
  lexically ordered and immutable as a collection. Status is derived from model/
  firmware checks and then unignored terminal differences.
- ComparisonResult.ignored_identifiers: sorted matched union of terminal pointers,
  including unchanged matches; ignored_count is its length. Exact ignores and
  ignore_patterns are recorded separately. No hidden defaults are used.
- ComparisonResult.compared_count: unignored terminal union size; incompatible
  inputs have zero, with reason and identity metadata. All-ignored requests
  refuse with FileError under owner answer C2, never an empty success.
- ComparisonResult.before_identity/after_identity: name/model/serial/firmware/
  address, copied from native metadata. Model/firmware are checked before ignores.
- ComparisonResult.warnings: always includes snapshot omission of read-only objects,
  synthetic-only assumed compatibility and file privacy. Identity-name differences
  are flagged before the difference list but do not imply hardware observations.

Comparison supports Snapshot objects and explicit file paths. Inputs are copied
before processing. Boolean/number and integer/float types stay distinct under
owner answer C1; 1 versus 1.0 is a difference. No numeric coercion/tolerance is
applied. Empty dictionaries/lists are
terminal values, and arrays use index pointers. Nonempty branch-to-leaf changes
are represented by their terminal additions/removals, not duplicate parent deltas.
Object/array type replacements are reported and counted once at their container
pointer with both complete values, suppressing redundant descendants. This retains
the distinction between {"0": 1} and [1] despite equal scalar leaf pointers.
