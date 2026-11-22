# Constitution: Huey, Dewey and the private tool built on them

Version 1.2.0. Written 2026-11-21, revised the same day after red-team review and the owner's decisions. Changes are made by the project owner.

Copy this file to `.specify/memory/constitution.md` in each of the three repositories: Huey, Dewey, and the private show-monitoring tool that uses them, called "the private tool" here. It also governs the two features built in music-video-pipeline (issues #124 and #125), alongside that repository's own `CLAUDE.md`, which wins where the two differ.

This copy is generic and may go into a public repository. The private repository adds a preamble of its own that carries the band's purpose statement. That preamble never leaves the private repository.

The order of the articles is the order of priority. When two articles pull in different directions, the lower-numbered one wins.

## Purpose

| Who benefits | How | Where it lives |
|---|---|---|
| Everyone | Contributions to existing projects | Upstream |
| Small bands | Huey, Dewey and, if he happens, Louie | Public repositories |
| One band | The private tool, with that band's own baselines and name map | Private repositories |

## Article I: The show must go on

1. No audio, video or timing signal ever passes through this software. It observes and, in later phases, nudges. Ableton Live, AbleSet and the mixer keep time and carry signal.
2. If any of this software crashes, hangs or is unplugged, the performance continues exactly as it would have without it.
3. The software holds no state the rig depends on. After a restart it re-reads everything from the rig and from files on disk.

## Article II: Read-only until rehearsed

1. This build is read-only. No code path may change the state of the mixer, Ableton Live or AbleSet. "State" includes who holds a device's subscription or event feed, and anything a device shows to a performer.
2. Write features (restore, snapshot recall, mute, transport, cues) are specified as deferred. They are not to be implemented, stubbed, scaffolded or hidden behind a flag in this build. The code for them does not exist yet.
3. Every datagram sent to a device passes through one choke point, the safety gate, at the transport boundary: the last code before the socket.
   1. The gate holds an allow-list of exact operations: destination, canonical address and argument form, each tied to the device model and firmware it was verified on. It is not a list of message shapes. "No arguments" does not mean "read": the mixer accepts zero-argument requests that change who receives its event feed.
   2. The gate inspects the encoded datagram and its destination, not a description of what the caller meant to send.
   3. Everything not on the list is refused: unknown addresses, special address syntax, arguments, bundles, and any destination other than the configured device.
   4. A library's own gate is mandatory. A caller may add a further restriction on top of it and can never remove or replace it.
   5. A test proves that no other path to the network exists.
4. Sending any traffic to a real device needs the owner's sign-off on the allow-list and evidence for the firmware installed on that device. Until then the software talks to stand-ins and files only.
5. A write feature becomes buildable only when the owner says so in writing, after the rehearsal gates in the private tool's spec have been met.

## Article III: Use the standard that exists

1. Never invent a file format, naming rule, marker convention, protocol or message when the device, its vendor or the wider live-production world already has one.
2. Before defining anything new, search for the existing form and record what was found. If none exists, say so in the spec and mark the new thing as ours.
3. Where a device has its own way of saving or describing its state, use that form in preference to one of ours.
4. Prefer contributing to an existing open-source project over starting a new one. Before building a tool, evaluate the ones that already do the job and record the result.

## Article IV: Facts come with sources

1. Every claim about how a device or protocol behaves cites where it came from: a document and section, or a recorded exchange with a real or emulated device.
2. `research.md` lists each fact as Confirmed, Reported or Unknown. Only Confirmed facts may be relied on without a guard.
3. Code that depends on a Reported or Unknown fact is isolated in one clearly named function, and its tests say in their names that the behaviour is assumed.
4. The first tasks in every plan are the verification tasks listed in `research.md`. No dependent feature starts before its facts are Confirmed or explicitly accepted as assumptions.
5. A passing test proves the code matches the test. It does not prove the code matches the device. Say which of the two has been shown.
6. A client and a stand-in written from the same understanding can share the same error and pass together. Expected results come from somewhere independent of the code under test: the vendor's own examples, a list of allowed operations written separately from the gate, or sanitised exchanges recorded from the real device under supervision.
7. A criterion that only the real device can settle is labelled a hardware acceptance criterion. Stand-in tests never mark it met.

## Article V: Stop and ask

1. When a requirement is ambiguous, contradictory or missing, do not choose. Write the question to `QUESTIONS.md` at the repository root with the options and a recommendation, then continue with work that does not depend on the answer.
2. Never resolve a `[NEEDS CLARIFICATION]` marker by guessing.
3. Never widen scope because something looked useful. Record the idea in `QUESTIONS.md`.

## Article VI: Tests first

1. Write the failing test, then the code.
2. Tests run on Linux with no hardware, no Ableton Live, no AbleSet and no network beyond localhost.
3. Every fixture is synthetic and safe to publish. Real captures of a band's rig never enter a public repository or its history.
4. Each read-only guarantee in Article II has a test that fails if a write is ever attempted. Outgoing traffic is counted at the sender and compared with the independently written list in Article IV.6. A stand-in's own count of refused writes is supporting evidence, not the proof.

## Article VII: A good neighbour on the rig

1. Never take the mixer's subscription. The WING has one OSC subscription, held by the latest requester, and other tools on the rig may hold it. Never send a subscription request in any form, including the zero-argument ones. Poll instead.
2. All traffic to one device shares one budget: discovery, polling, retries and requests started by a person or by Claude all draw from it. Defaults must be conservative and configurable, and the software must back off when the device is slow to answer.
3. Never show a stale value as current. When a device stops answering, its state is "unknown", shown as such.
4. Never show a result as good on incomplete evidence. Green means every required check was read fresh, in one run, from the expected device, and compared with a compatible baseline.
5. Assume the control network may be shared with phones and tablets. Do not assume a wired link, and report the quality of the link that is found. Anything reachable from that network that can start device traffic or change local files needs authorisation.

## Article VIII: The privacy line

1. Huey and Dewey are public. They contain nothing about any band's rig or shows: no channel names, no setlists, no captures, no venue details. The publishing band's name may appear as the publisher only: in the package names, the licence and the README credit. The private tool's name does not appear.
2. Nothing from any private repository appears in a public repository, its issues, its commit messages or its fixtures.
3. Captures and baselines of a real rig are private data. Tools that produce them must say so in their output and documentation.
4. Rig data returned to Claude enters a conversation that is stored outside the rig. Results are bounded and redacted by default, and the owner decides which fields may be returned.

## Article IX: Small and plain

1. Python 3.10 or later. Packaging, linting and test conventions follow music-video-pipeline: setuptools, ruff, pytest.
2. Few dependencies, each one justified in the plan. Heavy or optional ones go in extras.
3. No clustering, failover or orchestration layers. Two computers with fixed jobs do not need them.
4. Public repositories are MIT licensed.
5. Third-party code is used under its own licence. Sidecar is AGPL-3.0: run it as a separate program in tests and never copy code from it. AbletonOSC is MIT.
6. One implementation of each shared thing. The AbleSet notation parser and the Live set reader live in music-video-pipeline and nowhere else.

## Governance

Changes to this constitution are made by the owner. An agent that believes an article is wrong for a given task records that in `QUESTIONS.md` and follows the article in the meantime.
