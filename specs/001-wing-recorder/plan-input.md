# Plan input: Huey

Technical direction for the planning step. The spec says what and why; this says what is already decided about how. Anything not listed here is the planner's choice, within the constitution.

Revised 2026-11-21 after red-team review. The unattended build covers Tier A of the spec only: files and a localhost replayer. Nothing in it sends to a console.

## Decided

- **Language**: Python 3.10 or later.
- **Packaging and tooling**: setuptools, ruff, pytest, pytest-cov, matching music-video-pipeline.
- **Licence**: MIT.
- **Package and command name**: distribution `refestramus-huey`, import `refestramus_huey`, command `refestramus-huey`. Decided by the owner; `huey` is taken on PyPI (`research.md` P1).
- **Transport**: UDP sockets. The console's OSC port and discovery port are in `research.md` (W1, W3).
- **Tests**: Linux, localhost only, no hardware.

## Constraints

- One private send function, with the gate directly above the socket call. It is not replaceable. Callers may pass a narrowing restriction (FR-007). Tests count datagrams below the gate.
- The gate's allow-list and the independent list of allowed operations (FR-021) are two files written by two separate tasks. Neither is generated from the other.
- The allow-list ships with no entries for a real console.
- No dependency on Sidecar, `wingemul` or any emulator at import or install time. Emulator runs are optional, skipped when the emulator is absent, and run it as a separate process (constitution Article IX.5). Their findings go in `research.md` as incompatibilities found, never as proof of correctness.
- The message encoder must be able to produce a request with no type tag at all (W5). Many OSC libraries always add an empty type tag. Verification task 6 in `research.md` decides whether a library can be used or the few bytes are encoded by hand. Either way, a test pins the exact bytes against the vendor document's example.
- Files must be diffable as text and stable in ordering.

## Suggested order

1. Verification tasks 1, 2, 3, 5, 6, 7 and 8 from `research.md`. Update the table. For task 7, write the Wing Tools evaluation as its own note: what it compares, what it misses, its licence, whether it runs on Linux.
2. Snapshot reading, with synthetic fixtures built from the documented structure.
3. Plant. **Do not build the comparison (Story 1).** The owner reads the Wing Tools evaluation first and decides how much of it Huey builds. Tests for plant check the changed value by reading the file back, not by comparing.
4. Message encoding and decoding, pinned to the vendor examples.
5. The gate, the independent list, and the refusal tests in FR-023.
6. The replayer: recorded replies, regenerated replies, delay, loss and late delivery.
7. Command-line interface and library documentation.
8. Optional emulator compatibility run.

Stop there. Write a status note listing what Tier B would need: the proposed allow-list entries for identity and for the handful of reads a monitor, routing and mute check needs, each with its evidence, for the owner to review.

## Not to do

- Do not build the snapshot comparison before the owner has answered the Wing Tools question.
- Do not write a client that sends to anything but the localhost replayer.
- Do not add an allow-list entry for a real console.
- Do not add a write, a subscription, a special-query option, a tree walk, a meter reader or a native-protocol client.
- Do not commit a snapshot or capture from a real console.
- Do not publish to PyPI or make the repository public. The owner does both.
