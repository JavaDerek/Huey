# Feature Specification: Huey, a snapshot comparer, recorder and replayer for the Behringer WING

**Feature directory**: `specs/001-wing-recorder`
**Repository**: Huey (public, MIT). Distributed as `refestramus-huey`; see "Names" below.
**Created**: 2026-11-21
**Status**: Revised after red-team review, 2026-11-21. Tier A is released for an unattended build. Tiers B and C are held.
**Input**: "See what a WING's setup is, compare two nights, and play a setup back later so software can be built and tested with no console in the room. Never change the console."

Governed by the constitution. Facts are in `research.md`; rows are cited as W1, E1 and so on.

## Why this exists

A small band's mixer holds hours of setup: routing, monitor mixes, mutes, names. That state is hard to see as a whole, hard to compare between two nights, and impossible to develop against when the console is in someone else's house.

Huey is a general tool. It knows about the WING and nothing about any particular band.

## What the review changed

1. **A message with no arguments is not always a read.** The console accepts zero-argument subscription requests, and each one moves the console's only OSC subscription to the sender (W12a). The old rule, "send only zero-argument messages", would have let Huey take the event feed from another tool. The rule is now a list of exact operations (FR-004).
2. **The console's own snapshot file comes first.** The console writes `.snap` files (W20). An exported snapshot costs the network nothing. Reading the same state one value at a time could take most of an hour (W22). Huey starts from snapshots and reads live only what a snapshot cannot give.
3. **A tool that compares snapshots may already exist.** Wing Tools has a routing comparison (W23). It is evaluated before Huey's comparison is built (constitution Article III.4). If it covers the need, Story 1 shrinks to whatever it leaves out. The owner makes that call after reading the evaluation, and Story 1 is not built until then.
4. **Huey testing Huey proves little.** Expected results now come from outside the code under test (FR-021 to FR-023).

## Release tiers

| Tier | What | Status |
|---|---|---|
| A | Offline only: read and compare native snapshots, plant faults, replay synthetic and recorded exchanges on localhost. No code in this tier sends anything to a console | Released for the unattended build |
| B | Supervised live reads: console identity and a short list of vetted single reads | Held. Needs the owner's sign-off on the allow-list and evidence for the installed firmware (constitution Article II.4) |
| C | A full live walk of the tree | Held. Needs Tier B run at a rehearsal, a measured traffic budget, and confirmation that audio, remote-control responsiveness and any existing subscription are unaffected |

Code for Tiers B and C is not written in the unattended build. The gate (FR-004) is built in Tier A, because the replayer's tests need it, with an allow-list that contains no live operations.

## Out of scope for this build

- Changing anything on a console. Huey never sends a SET (constitution Article II).
- Subscribing to the console in any form (W11, W12, W12a).
- The special query arguments `*`, `?` and `#` (W9). There is no option to enable them.
- Meters and signal levels. They need the native binary protocol (W14).
- Recalling or saving snapshots on the console (W18). Snapshots are exported by a person at the console and given to Huey as files.
- The native binary protocol on TCP 2222.
- A graphical interface.

## User Scenarios & Testing

### User Story 1: Compare two snapshot files (Priority: P1, Tier A)

A person exports a snapshot at the console on a good night and another tonight, gives Huey both files, and sees exactly what differs.

**Why this priority**: "what changed since the night it worked" is the question that ends most setup problems, and this answers it with no network traffic at all.

**Independent Test**: compare a synthetic snapshot with a copy that has three known changes; exactly those three are reported. The expected differences are written by hand in the test, not produced by Huey.

**Acceptance Scenarios**:

1. **Given** two snapshot files, **When** the person runs a comparison, **Then** Huey lists each identifier whose value differs, with both values, and each identifier present in only one file.
2. **Given** a list of identifiers or patterns to ignore, **When** the comparison runs, **Then** those are left out and the output says how many were ignored and which.
3. **Given** two snapshots from different models or firmware, **When** the comparison runs, **Then** Huey says first that the files may not be comparable, and its exit status is the "not comparable" status, not "identical", whatever the values are.
4. **Given** identical snapshots, **When** the comparison runs, **Then** it says so and exits with success; any difference gives a distinct non-zero status so scripts can branch on it.
5. **Given** any comparison, **When** it finishes, **Then** the output states that a snapshot leaves out read-only objects (W20a), so "identical" means "the saved settings are identical" and nothing more.
6. **Given** a file that is not a valid snapshot, or is from a format version Huey does not know, **When** it is loaded, **Then** Huey refuses with a clear message and never guesses.
7. **Given** any comparison, **When** it runs, **Then** it never opens a network connection.

### User Story 2: Plant a fault in a snapshot or capture (Priority: P1, Tier A)

A developer makes a modified copy of a file with chosen values changed, to test whether their own software notices.

**Why this priority**: it turns "does preflight catch a muted bus" into an automated test. It works on files only.

**Independent Test**: plant one change, read both files back, and confirm by hand-written expectation that exactly that value differs. This test does not depend on Story 1.

**Acceptance Scenarios**:

1. **Given** a file and an identifier with a new value, **When** the developer runs the plant command, **Then** Huey writes a new file with that value changed and the change recorded in a plant record beside it. The planted file is marked synthetic.
2. **Given** an identifier that is not in the file, **When** the developer tries to plant a value, **Then** Huey refuses and names the nearest existing identifiers.
3. **Given** a value of the wrong type for that identifier, **When** planted, **Then** Huey refuses.
4. **Given** any plant command, **When** it runs, **Then** it never opens a network connection.

### User Story 3: Replay a file as a stand-in console (Priority: P1, Tier A)

A developer starts the replayer with a snapshot or a capture record. Software that expects a WING at that address gets answers in the console's wire format.

**Why this priority**: this is what lets other tools be built on a machine with no console.

**Independent Test**: a plain OSC client, not Huey's own client code, sends the requests from the vendor document's examples and receives the bytes the document shows (FR-022).

**Acceptance Scenarios**:

1. **Given** a replayer serving a capture record, **When** a client sends a request that was recorded, **Then** it receives the recorded reply, byte for byte.
2. **Given** a replayer serving a snapshot, or a capture with planted values, **When** a client requests a value that has no recorded reply, **Then** the replayer builds the reply from the value. Built replies are marked as regenerated in the replayer's log, and the documentation says they show Huey's understanding of the format, not the console's behaviour.
3. **Given** a running replayer, **When** a client sends discovery, **Then** it receives the identity held in the file.
4. **Given** a running replayer, **When** a client sends anything that is not a recorded or regenerable read, **Then** the replayer changes nothing, logs the message in full and counts it. This includes messages with arguments, subscription requests with or without arguments, bundles and special address syntax.
5. **Given** a request for a path that is not in the file, **When** the replayer receives it, **Then** it answers as a real console answers an unknown path if that behaviour is Confirmed, and otherwise stays silent and logs the miss.
6. **Given** a replayer started with a delay, drop-rate or reorder option, **When** clients talk to it, **Then** replies are delayed, dropped or delivered late at that rate, so clients can be tested against a slow or lossy link.
7. **Given** a client that reads the same address twice, **When** the replayer is told to deliver the first reply after the second request, **Then** a correct client does not take the late reply as the answer to the second read (see FR-012).

### User Story 4: Use Huey from other programs (Priority: P2, Tier A for file functions)

A developer imports Huey and uses snapshot loading, comparison, planting and the replayer as functions.

**Why this priority**: other tools build on these functions and must not shell out to a command-line tool.

**Independent Test**: a short script performs each operation using only the documented public interface.

**Acceptance Scenarios**:

1. **Given** the library, **When** a program starts a replayer inside a test, **Then** it can stop it cleanly and read its counters and logs.
2. **Given** the library, **When** a program supplies an additional restriction on what may be sent, **Then** a message goes out only if both Huey's own gate and the caller's restriction allow it. No interface lets a caller replace, bypass or widen Huey's gate.

### User Story 5: Read the console's identity and a few vetted values (Priority: P2, Tier B, held)

A person on the same network as a WING runs one command and sees the console's name, model, serial number, firmware and address, and can read single values from a short vetted list.

**Why held**: this is the first traffic to a real console. It waits for the owner's sign-off on the allow-list and for evidence about the installed firmware.

**Independent Test**: against the replayer. On the console: a supervised run at a rehearsal, with someone listening and another control client connected.

**Acceptance Scenarios**:

1. **Given** a WING on the network, **When** the person runs discovery, **Then** Huey prints one line per console found with name, model, serial, firmware and IP, or "no console found" with a failure status when the timeout passes.
2. **Given** a vetted path and a console whose model and firmware match the allow-list entry, **When** the person reads it, **Then** Huey returns a typed value or a clear "no answer" within a stated timeout.
3. **Given** a console whose model or firmware has no allow-list entries, **When** any read is attempted, **Then** Huey refuses before sending and says why. Discovery is still allowed.
4. **Given** a path that is not on the allow-list, **When** a read is attempted, **Then** the gate refuses it, logs it, and the command fails visibly.
5. **Given** another tool holds the console's subscription, **When** Huey reads, **Then** that tool keeps receiving its events. Hardware acceptance criterion.

### User Story 6: Record the console's live state (Priority: P3, Tier C, held)

A person runs one command against a console and gets a capture record of the readable tree.

**Why held**: the tree may hold tens of thousands of values (W20a, W22), the Rack's tree differs from the document's (W21), and nobody has measured what the console tolerates while it mixes a live band. This story is specified so the capture record's format is right from the start. It is not built until Tier B has run on the real Rack.

**Acceptance Scenarios**, for when it is released:

1. **Given** a reachable console, **When** the person records, **Then** Huey reads only addresses the gate allows for that model and firmware, takes its paths from an exported snapshot where it can, and lists every path it skipped and why.
2. **Given** a recording in progress, **When** the console stops answering, **Then** Huey backs off, and if the console stays silent, stops and writes what it has, marked incomplete with the last path reached.
3. **Given** an incomplete capture, **When** the person resumes, **Then** Huey first re-reads the console's identity and firmware. If either differs from the capture's, it refuses to resume. If they match, the new readings are stored as a separate segment with its own start time, and the capture says it was made in more than one sitting. Readings from different sittings are never presented as one moment.
4. **Given** a finished recording, **When** the person reads the summary, **Then** it states how many values were read, how many were skipped, how long it took, how many requests timed out, how many sittings it took, and that the file may contain private names.

### Edge Cases

- The console is busy and answers slowly: Huey slows down and never floods (FR-006).
- A reply arrives late, after the same address has been asked again: see FR-012.
- UDP packets are lost: each request has a timeout and a bounded number of retries, and retries draw from the same budget as first attempts.
- A value contains characters that are awkward in the file format: stored losslessly; the raw bytes are always kept.
- Two consoles are on the network: discovery lists both and every other command requires an explicit address.
- A file is from a newer version of Huey: refuse with a clear message.
- The console is replaced by another of the same model between two files: identity differs, and comparisons say so first.

## Requirements

### Functional Requirements

**Safety gate**

- **FR-001**: Every datagram Huey sends MUST pass through one gate at the transport boundary, the last code before the socket. The gate inspects the encoded bytes and the destination address and port.
- **FR-002**: The gate MUST refuse by default. It allows a datagram only if it matches an allow-list entry exactly.
- **FR-003**: Each allow-list entry MUST name: the operation (discovery, identity read, value read); the canonical address, written out in full with no patterns; the argument form, which in this build is always "none"; and the console model and firmware range it was verified on, with the `research.md` row or recorded exchange that verified it.
- **FR-004**: The gate MUST refuse, whatever the allow-list says: any message with arguments or a type tag carrying values; any bundle; any address using special syntax, including the subscription addresses (W12, W12a), the reply-port prefix (W2) and the multi-parameter form (W10); any address that is not canonical; and any destination other than the console address the user configured and the discovery port.
- **FR-005**: The allow-list MUST be data, in one file, reviewed as a unit. In the unattended build it contains no entries for a real console. Entries are added only with the owner's sign-off.
- **FR-006**: All traffic to one console MUST share one budget: discovery, reads, retries and anything a calling program asks for. The default MUST be conservative, the rate MUST be configurable downward by a caller, and Huey MUST slow down automatically when replies slow down or time out. [NEEDS CLARIFICATION: the budget. It is measured on the real Rack, with another control client active, before any walk.]
- **FR-007**: A caller MAY pass an additional restriction that narrows what Huey sends. Huey's own gate MUST still apply to every datagram. No public interface replaces the send function or the gate.
- **FR-008**: A refused datagram MUST be logged in full and MUST make the operation that attempted it fail visibly.

**Files**

- **FR-009**: Huey MUST read the console's native `.snap` snapshot files (W20) as its primary input and MUST NOT define a format of its own for console state. [NEEDS CLARIFICATION: the structure, from verification task 3 in `research.md`.]
- **FR-010**: For live exchanges Huey MUST use a versioned capture record: console identity, model and firmware; for every exchange the raw bytes sent, the raw bytes received, the decoded form, a timestamp and the time taken; every skipped path with its reason; every failure; the budget used; and one segment per sitting. This format is ours, because no existing one holds raw exchanges, and the spec says so (constitution Article III.2).
- **FR-011**: A capture record is a supplement to a snapshot. It MUST NOT be offered as a replacement for one.
- **FR-012**: Replies MUST be matched to requests so that a late reply is never taken as the answer to a later request for the same address. A client reading an address MUST NOT re-ask it while an earlier request for it is outstanding or within its late-reply window. Unmatched replies are logged, never attributed.
- **FR-013**: Huey MUST compare two files and report changed, added and removed entries, with an ignore list, and MUST report "not comparable" when model or firmware differ.
- **FR-014**: Huey MUST write a modified copy of a file with planted values and a plant record, without any network access. Planted files are marked synthetic.
- **FR-015**: Files MUST be diffable as text and stable in ordering.

**Replayer**

- **FR-016**: The replayer MUST return recorded replies byte for byte, and MUST build replies for values that have no recorded reply, marking them regenerated.
- **FR-017**: The replayer MUST refuse, log and count everything that is not a read it can answer, and change nothing.
- **FR-018**: The replayer MUST be able to simulate delay, loss and late delivery.
- **FR-019**: The replayer listens on localhost by default.

**Evidence**

- **FR-020**: Huey's output and documentation MUST state that a snapshot or capture of a real console contains private information and should not be published. The repository MUST contain only synthetic fixtures, and a test MUST fail if a fixture carries the marker of a real file.
- **FR-021**: The test suite MUST count every datagram at the sender, below the gate, and compare the full list with a separately written list of allowed operations. That list is written from the protocol document by whoever does verification task 2, in its own file, and is not generated from the gate's allow-list.
- **FR-022**: The test suite MUST include protocol fixtures taken byte for byte from the vendor document's examples, for both the client and the replayer.
- **FR-023**: Tests MUST include, for the gate: a zero-argument request to each subscription address; a message with each special query argument; a bundle; a non-canonical spelling of an allowed address; an allowed address sent to the wrong destination. Each MUST be refused.
- **FR-024**: Once supervised tests have run on the installed firmware, sanitised exchanges from them MUST be added as replay fixtures. Until then the README says none exist.

**Interface**

- **FR-025**: Huey MUST provide a command-line interface and an importable library with the same capabilities. Commands exit with distinct statuses for success, differences found, not comparable, device unreachable, refused by the gate and usage error.

### Key Entities

- **Console identity**: name, model, serial, firmware, address.
- **Snapshot**: the console's own saved state, read from a `.snap` file. Marked real or synthetic.
- **Capture record**: identity, exchanges, skipped paths, failures and segments from live reads.
- **Exchange**: one request and its reply or timeout, with raw bytes, decoded form, timestamp and timing.
- **Allow-list entry**: operation, canonical address, argument form, model, firmware range, evidence.
- **Difference**: an identifier with its value in each file, or present in only one.
- **Plant record**: the deliberate changes made to a file.

## Success Criteria

Shown by tests in this build:

- **SC-001**: Comparing a snapshot with a copy holding N planted faults reports exactly N differences, for a range of N, against hand-written expectations.
- **SC-002**: Across the whole test suite, every datagram counted at the sender is on the independently written list, and a test fails if that ever changes.
- **SC-003**: Every case in FR-023 is refused.
- **SC-004**: The vendor document's example exchanges pass in both directions.
- **SC-005**: The whole test suite runs on Linux with no hardware and no network beyond localhost.
- **SC-006**: A reader of `research.md` can tell, for every protocol behaviour the code depends on, whether it is Confirmed and where from.

Hardware acceptance criteria. Only the real Rack can meet these, under supervision. Stand-in tests never mark them met:

- **HC-001**: Another client's subscription keeps delivering while Huey reads identity and vetted values.
- **HC-002**: At the chosen budget, with another control client active, nobody hears or sees an effect: no audio artefact and no sluggishness in the remote-control app.
- **HC-003**: A client that works against the replayer needs no code change to read the same values from the Rack.
- **HC-004**: A full recording, if Tier C is ever released, finishes in a time short enough to do at soundcheck. [NEEDS CLARIFICATION: target duration, once the tree size is known.]

## Assumptions

- The console's OSC interface is as `research.md` reports. No row is Confirmed at the time of writing.
- The target console runs the latest released firmware (`research.md`, version policy). Allow-list entries carry that exact number. Older firmware is not supported; the console is updated instead.
- The WING Rack's tree differs from the document's general description (W21). Nothing verified on another model counts for the Rack.
- An emulator can find incompatibilities. It is not evidence about a real console.

## Names

`huey` is taken on PyPI by an unrelated project (P1). Decided by the owner: the distribution is `refestramus-huey`, the import name is `refestramus_huey`, and the command is `refestramus-huey`. The band's name appears here as the publisher only (constitution Article VIII.1).

## Deferred (do not build)

- Tiers B and C, until released as described above.
- A stateful replayer mode in which writes change an in-memory copy.
- Reading meters.
- Any command that changes a console.
