# Linux validation

Install locally with `uv venv` then `uv pip install -e '.[dev]'`. Run `pytest`
and `ruff check .`. Tests use only synthetic data and localhost UDP sockets.

Inspect a synthetic snapshot; plant an existing JSON Pointer into a new filename;
load the output to check its exact changed value and synthetic metadata. Starting
and stopping a Replayer in a context manager must close its ports and expose
all refused/sent/dropped/regenerated records. A plain UDP test client exercises
the byte-exact vendor fixtures and verifies silent refusal for every unsafe form.

H1/H2 were answered and applied. Native synthetic reading/plant and localhost
wire examples pass. Unsupported numeric regeneration remains limited by H3.
No real console, emulator or hardware acceptance criterion is validated here.

## Offline comparison

```bash
refestramus-huey compare tests/fixtures/synthetic.snap tests/fixtures/synthetic.snap
refestramus-huey plant tests/fixtures/synthetic.snap /ae_data/ch/1/mute 0 /tmp/changed.snap
refestramus-huey compare tests/fixtures/synthetic.snap /tmp/changed.snap
refestramus-huey compare tests/fixtures/synthetic.snap /tmp/changed.snap --ignore /ae_data/ch/1/mute
```

Expected statuses: 0, 0, 1, 0. The third command reports exactly one changed
identifier, before 1 and after 0. Use a fresh output filename for plant. Repeatable
--ignore-pattern uses case-sensitive full-pointer globs; quote the pattern.
Compared/ignored counts include saved terminal identifiers (empty containers
included); object/array type replacements count at the container instead of its
descendants. Known synthetic model/firmware mismatch returns 3 before ignores.
Unknown format or non-synthetic provenance returns file error 6.

All results warn about read-only objects omitted from snapshots, privacy and the
unverified actual 3.1.2 schema. Owner answers C1/C2: 1 versus 1.0 is different;
all-ignored requests refuse with status 6. Both matching
profiles must still satisfy the H2 guard; incompatible metadata never admits new
profiles for successful comparison, inspection or replay.
