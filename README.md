# Huey

Huey provides offline WING snapshot comparison, file-only fault planting and a
read-only UDP stand-in bound to **127.0.0.1**. Distribution and command:
`refestramus-huey`; Python import: `refestramus_huey`. Python 3.10+, Linux, MIT.
No runtime dependencies.

This release accepts **synthetic files only**. The owner approved a guarded
assumption: native `snapshot.9` JSON structure from the WING 3.1 manual, with
synthetic WING Rack identity and firmware metadata **3.1.2**. The manual's example
uses older metadata; actual 3.1.2 snapshot compatibility remains unverified.
Other signatures and real-file markers are refused. Different model/firmware
metadata can be diagnosed as not comparable; matching unsupported profiles refuse.
Snapshots omit read-only objects; saved settings are not the complete console state.

## Install and use

```bash
uv venv
uv pip install -e '.[dev]'
refestramus-huey inspect tests/fixtures/synthetic.snap
refestramus-huey plant tests/fixtures/synthetic.snap /ae_data/ch/1/mute 0 /tmp/planted.snap
refestramus-huey compare tests/fixtures/synthetic.snap /tmp/planted.snap
refestramus-huey replay /tmp/planted.snap --port 2223 --discovery-port 2222
```

Planting creates a new file and `<output>.plant.json` record. It refuses missing
identifiers, wrong JSON types and existing outputs. Identifiers use
[JSON Pointer (RFC 6901)](https://www.rfc-editor.org/rfc/rfc6901.html), including
`~1` for slash and `~0` for tilde. Native JSON is preserved, sorted and diffable;
the plant record is separate from console state.

`compare BEFORE AFTER` reports changed, added and removed JSON Pointer identifiers,
both available values, identities, coverage warnings and comparison/ignore counts.
Missing values are omitted; actual JSON null remains null. Empty containers count
as values and arrays use index pointers. Object/array replacements are reported
at their container pointer so structurally different files cannot appear identical.
Ordinary branch-to-scalar changes appear as terminal additions/removals.

Use repeatable `--ignore POINTER` for literal terminal identifiers or
`--ignore-pattern '/ae_data/ch/*'` for case-sensitive whole-pointer globs. Quote
patterns to keep the shell from expanding them; `*` spans `/`. Ignored identifiers
are listed and counted once, including unchanged matches. No timestamps or other
fields are ignored automatically. Model/firmware compatibility is checked first,
even when an ignore would hide those fields.

Comparison exit statuses: 0 identical saved settings, 1 differences, 3 not
comparable, 6 file/validation failure; command syntax errors use 2. Identity
differences and snapshot-coverage limits are printed in every result. Owner
decisions C1/C2 in QUESTIONS.md preserve integer-versus-float representation:
`1` and `1.0` count as different. An ignore list that excludes everything refuses
with a clear nothing-left-to-compare error (status 6).

```python
from refestramus_huey import compare_snapshots

result = compare_snapshots("tests/fixtures/synthetic.snap", "/tmp/planted.snap")
assert result.status == "different"
assert result.differences[0].identifier == "/ae_data/ch/1/mute"
print(result.to_dict())
```

```python
from refestramus_huey import Replayer, load_snapshot, plant

snapshot = load_snapshot("tests/fixtures/synthetic.snap")
assert snapshot.assumed_compatibility
assert snapshot.get("/ae_data/ch/1/mute") == 1

with Replayer(snapshot) as stand_in:
    print(stand_in.address, stand_in.discovery_address)
    # Use an independent localhost OSC client here.
# The context closes sockets and joins the worker.
print(stand_in.counters, stand_in.audit)
```

The replayer defaults to separate ephemeral OSC/discovery ports and reports both.
It never resolves a hostname or binds/sends outside numeric 127.0.0.1. It answers
only its fixed reviewed localhost operations: discovery, identity and channel 1
name/mute/fader. Other requests are refused or logged as unavailable and silent.
Every sent datagram crosses the mandatory final gate. The real-device allow-list
is empty. An optional library `restriction(packet, destination)` can only narrow
the built-in policy. Request rules require exact canonical bytes without tags or
arguments; reply rules require exact approved bytes to the originating local client.
The owner approved this directional distinction in QUESTIONS.md H1.

## Replay evidence and fault simulation

`load_capture` reads a versioned synthetic exchange envelope containing identity,
raw hex, independently checkable decoded messages, timestamps, elapsed time,
failures/skips, a recorded budget and one segment per sitting. It supplements
native snapshots; it does not replace their state format. A `values` supplement
can be planted using JSON Pointer; `planted_addresses` invalidates stale raw
responses. Raw recorded bytes remain available as original evidence. Captures with multiple sittings remain readable as files, but the replayer
refuses them rather than combining segments. Conflicting replies are also refused.
No live recorder or console client is included.

Recorded replies are returned byte for byte. Regenerated replies are logged as
`regenerated`: they express this implementation's understanding, not observed
console behavior. Only documented complete conversions are supplied: channel 1
string name, mute 0/1 and exact channel-1 fader examples -144.0, -1.0, 3.0 and 4.0. Other numeric regeneration is
blocked on H3; unavailable reads stay silent and are logged. No general fader
normalisation is guessed.

Use `--delay SECONDS`, `--drop-rate 0..1`, `--late-every N` and `--late-delay SECONDS`
to simulate a slow/lossy link. The first reply of each N-reply group gets the extra
late delay, so a second request for the same address can be answered first. Library
`seed` makes fractional drops reproducible. Stop with Ctrl-C; `--duration SECONDS`
provides a bounded run. Exit statuses are 0 success, 5 transport refusal and 6
file/usage failure (argparse syntax errors use 2).

No supervised real-console exchanges exist. The byte fixtures are published
illustrative examples, with their original example identity and older firmware
left intact; they are not target-firmware traces. A passing localhost test is
not hardware acceptance or evidence that another control client's subscription
would be unaffected on a console.

## Verification and scope

```bash
pytest
ruff check refestramus_huey tests
```

Tests use synthetic files and localhost sockets only, independently authored
wire bytes and operation inventory, and an audit below the gate. File functions
are tested with sockets prohibited. The suite checks that every emitted library
datagram matches the independent operation inventory and that no other send path
exists. Source/version evidence and Spec Kit workflow records are in
`specs/001-wing-recorder/`.

The [Wing Tools evaluation](specs/001-wing-recorder/wing-tools-evaluation.md) is
written for owner review. Controlled synthetic-file testing needs a licensed
hosted account or offline access and remains unrun. After reviewing that evidence,
the owner released the independently designed local comparison on synthetic files.
Live reads, discovery beyond localhost, tree walking, subscriptions, meters and
every console write are held and have no command implementations.

Real snapshot/capture files contain private names and configuration. Keep them
private and out of repositories. Nothing here publishes a package, changes a
device or demonstrates readiness for a real rig.


The safety-review follow-up also enforces each exact address's documented reply
type tags, rejects ambiguous discovery identity fields and nonfinite JSON numbers,
and protects the required synthetic provenance marker during planting. Sender
instrumentation independently checks reply forms and originating-client requests.
See `specs/001-wing-recorder/review.md` for findings and validation limits.
