# Research: what is known about the devices and protocols

Written 2026-11-21. Copy this file into each feature directory as `research.md` and keep it current. It is the fact base Article IV of the constitution refers to.

## Version policy

Decided by the owner, 2026-11-21: wherever a version matters, assume the latest released version of the device firmware or software, and build against that. If the rig turns out to be older, the rig is updated to match. The specs are not widened to cover older versions.

What this means in practice:

- "Latest" is resolved to an exact number when the work is done. Whoever does a verification task looks up the latest released version, and writes the number and the date in this file. Allow-list entries, fixtures and name maps carry that exact number, never the word "latest".
- Beta and pre-release versions do not count.
- Before any traffic goes to a real device, a person confirms the installed version equals the recorded number. If it does not, the device is updated by a person first, or the evidence is redone for the newer number. Nothing is sent on the strength of "close enough".
- If the latest firmware is newer than the newest protocol document, the document is not evidence for it. Record the gap as Unknown; do not assume nothing changed.

### Latest released versions, looked up 2026-11-21

From a web search, through search summaries. Reported, not Confirmed: re-check each on the vendor's own page and correct the number when the work starts.

| # | Product | Latest release found | Source and caveat |
|---|---|---|---|
| V1 | WING firmware (all models, including the Rack) | 3.1.2, dated 2026-07-29 | Behringer's WING Rack product page lists it as the current download. Earlier: 3.1.1 (2026-06-01), 3.1 (2025-11-07) |
| V2 | WING Remote Protocols document | An edition for firmware 3.1 exists, file name `WING_Remote-Protocols-3.1-03.pdf` | Named by a third-party repository, which says it is on Behringer's WING downloads page. Not located or read. The author also keeps the document at github.com/pmaillot/WingRemoteProtocols |
| V3 | AbleSet | 3.1.9 | From a download-site listing dated 2026-10-25. The official changelog at ableset.com/changelog was not read and may show something newer |
| V4 | Ableton Live | 12.4.16, dated 2026-10-30 or 2026-11-02 (sources differ) | Live 13 is described on Ableton's site as the next major version. Whether it has shipped is Unknown. If it has, the policy above makes it the target |

**V1 and V2 together change the primary source for section 1.** The rows below were read from the edition for firmware 3.0.6. The target firmware is 3.1.2. Find and read the 3.1 edition, and treat every W row as unverified for 3.1.2 until it has been re-read there.

## How to read the status column

| Status | Meaning | May code rely on it? |
|---|---|---|
| Confirmed | An agent or person read the primary source in full, or observed the behaviour on a real or emulated device, and recorded where | Yes |
| Reported | Read on 2026-11-21 through a fetch tool that returns a summary of the page, not the page itself | Only behind a guard, until confirmed |
| Unknown | Not found, or the source did not cover it | No |

**Historical handoff status:** nothing about a device was Confirmed. The direct verification ledger below supersedes the named rows. Rows marked Reported came through a summarising tool. Rows marked "Reported (review)" came from the red-team review of 2026-11-21, which read documentation and source code and gave the citations shown; nobody on this project has yet re-read those passages or tried them on the rig. The first task in each plan is to open the primary source, read the relevant section directly and promote or correct each row.

The review overturned several rows. Where a row below says "Corrected", the old wording was wrong and anything built from it must be rechecked.

## 1. Behringer WING remote control

Primary source read directly: WING Remote Protocols V3.1.0, cover states firmware
3.1.0 and above. Target metadata is 3.1.2; actual-device compatibility is unverified.
https://cdn-media.empowertribe.com/2106004e217b8eb2639d93672823eef5/WING_Remote-Protocols-3.1-03.pdf

OSC chapter pp.19–31 and snapshot appendix pp.260–263 were read, with communications
and model-specific passages. The handoff used 3.0.6; current documentary findings
and remaining gaps are recorded in the direct verification ledger below.

| # | Fact | Status |
|---|---|---|
| W1 | OSC uses one UDP port, 2223 | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W2 | Replies go to the port the request came from. Prefixing an address with `/%<port>` sends the reply to another port on the same IP | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W3 | Discovery: send the 5-byte datagram `WING?` to UDP 2222. The reply is `WING,<ip>,<name>,<model>,<serial>,<firmware>` | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W4 | The OSC address `/?` also returns console identity | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W5 | GET: send an address with no arguments and no type tag. The reply carries a type tag and the value in several forms (for example `,sff` for a fader, `,sfi` for a mute) | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W6 | SET: send the address with a type tag and a value. An int of -1 to an on/off parameter toggles it | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W7 | The console does not echo a client's own SET back to that client | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W8 | Sending a node address with no arguments lists its children. `/` lists the root branches | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W9 | A node accepts special string arguments: `*` returns the node in snapshot-file form, `?` a parameter description, `#` a description with current values | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W10 | A single string can set several parameters at once, for example `/ch.1.fdr=-1,mute=0` | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W11 | Only one OSC subscription is active at a time, held by the last requester, and it expires after 10 seconds unless renewed | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W12 | Subscription wire addresses are `/*b`, `/*s` and `/*S`; printed `~` is a NULL byte, not part of the address | Confirmed documentation, 3.1 manual p.30; hardware unverified |
| W12a | **Corrected.** A subscription request carries no arguments. Sending one moves the console's only OSC subscription to the sender. A zero-argument message is therefore not always a read | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W13 | Native TCP 2222; up to 24 TCP clients; 10-second inactivity timeout | Confirmed documentation, 3.1 manual p.16; corrected from 16 |
| W14 | Meters are available through the native protocol over UDP. No OSC meter address was found | Reported |
| W15 | Documented paths: `/ch/1/mute`, `/ch/1/fdr`, `/bus/1/fdr` | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W16 | Paths for channel name, bus mute, channel-to-bus sends, main fader | Unknown (inferred from a node dump, not shown as leaves) |
| W17 | Paths for phantom power, input source, output routing | Unknown |
| W18 | Commands to recall or save snapshots, shows, snippets or library items | Unknown |
| W19 | Any single command that dumps the whole console state | Unknown. The document describes per-node `*` dumps and walking the tree |
| W20 | The console saves its state in its own `.snap` snapshot files, and the document's snapshot appendix describes them | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W20a | A default snapshot holds more than 30,000 identifiers, and snapshots leave out read-only objects | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W21 | **Corrected.** The WING Rack does not answer exactly the same tree as the full-size console. The document lists Rack-specific differences, and parts of the tree change with configuration | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W22 | Reading the whole tree one value at a time is slow. At an illustrative 10 reads a second, 30,000 reads take 50 minutes before retries | Arithmetic from W20a. The real tree size and a tolerable rate are Unknown |
| W23 | Wing Tools, an existing tool, compares the routing in two snapshot files (its "Routing Diff") | Reported (review). Not yet evaluated |
| W24 | `libwing`, an open-source library for accessing the WING, exists on GitHub (dannydulai/libwing and forks) | Reported, from a search result on 2026-11-21. Protocol used, licence and state not checked. Evaluate before writing a client (constitution Article III.4) |

Second source, corroborating W11: the Bitfocus Companion module's help page says the WING "only supports one subscription at a time", with the most recent request being the only receiver.
https://github.com/bitfocus/companion-module-behringer-wing/blob/main/HELP.md

### Consequences for the design

- **W12a means "no arguments" is not a safety rule.** The gate allows exact operations at exact addresses for a verified model and firmware, and refuses the rest, including every subscription address. See constitution Article II.3 and Huey FR-004.
- **W9 is dangerous if misapplied.** If `*`, `?` or `#` is sent as a string argument to a leaf that holds a string (a channel name, for example), it may be taken as a SET and overwrite the value. This release sends none of them, and has no option to turn them on.
- **W20, W20a and W22 mean snapshots first.** A snapshot the operator exports at the console costs the network nothing and is the console's own format. Start there, and add live reads only for the few values a check needs. A full live walk is held until it has been measured on the real Rack.
- **W20a also means a snapshot is not the whole state.** Read-only objects are missing from it. Any check that needs one of those needs a live read.
- **W21 means a path is only verified for the model and firmware it was verified on.**
- **W23 means evaluate Wing Tools before building a snapshot comparison** (constitution Article III.4).
- **W8 means paths need not be hard-coded,** but see W22: discovering them by walking is the expensive way.
- **W11 means polling, never subscribing.** See constitution Article VII.
- **W14 means no signal-present check in this build.** Line check and any "is signal arriving" test are deferred.

### Verification tasks (do these first)

0. Confirm the latest released WING firmware on Behringer's own page (V1 says 3.1.2). Get the protocol document's edition for firmware 3.1 (V2) and use it as the primary source in place of the 3.0.6 edition. If no edition covers 3.1.2 exactly, say so.
1. Read the OSC chapter of the primary source in full (pp. 19 to 30 at least) and promote or correct W1 to W15 and W12a.
2. From that reading, write the list of every address or address form that does something other than return a value when sent with no arguments: subscriptions, triggers, actions. This list is written by whoever does the reading, separately from the gate's allow-list, and becomes the independent check in constitution Article IV.6.
3. Read the snapshot appendix and record the `.snap` structure (W20, W20a), including which objects it leaves out.
4. Find the snapshot, show and library commands (W18) and record them for the deferred write features. Do not implement them.
5. Record the Rack-specific differences and the configuration-dependent parts of the tree (W21).
6. Confirm whether the chosen OSC library can send a message with no type tag at all (W5), or whether the message must be encoded by hand.
7. Evaluate Wing Tools' Routing Diff on synthetic snapshot files (W23): what it compares, what it misses, its licence, and whether it runs on Linux. Record the result before any snapshot comparison is written.
8. Collect the document's own example exchanges, byte for byte, as protocol fixtures.

## 2. WING emulators

| # | Fact | Status |
|---|---|---|
| E1 | Sidecar is a desktop mixing console that emulates the WING, for Windows, macOS 11+ and Linux x86_64 (glibc 2.38+) | Reported |
| E2 | Sidecar is licensed AGPL-3.0 | Reported |
| E3 | Sidecar's notes say it is incomplete and can differ from a real console | Reported |
| E4 | Sidecar uses WING-style paths such as `/ch/<n>/in/conn/grp` and answers discovery | Reported |
| E5 | Whether Sidecar listens on UDP 2223 and 2222 and answers zero-argument GETs as a real console does | Unknown |
| E6 | Whether Sidecar can run without a display | Unknown. Only a graphical interface is described |
| E7 | `wingemul`, an emulator for Linux, is published by the protocol document's author among his WING tools | Reported (review). How much of the OSC interface it covers is Unknown |

Source for E1 to E6: https://github.com/Audbol/Sidecar/releases
Source for E7: https://behringer.world/viewtopic.php?p=14914

Verification task, optional: install Sidecar or `wingemul` on the build machine, find out whether it can run there (Sidecar may need a virtual display), and record exactly which requests it answers. Run either as a separate program only (constitution Article IX.5).

An emulator run can find incompatibilities. It cannot show that anything is safe or correct on the Rack. Only the Rack decides whether a feature is ready for rehearsal.

## 3. AbleSet

Primary source: AbleSet's released documentation, Locator Notation and OSC sections. The original rows below came from the beta documentation in single-page form (https://beta.ableset.com/docs/all), of which roughly the first 60 percent was read. Use the released documentation. The target is the latest released AbleSet, Pro edition (see the version policy); record its exact number here.

### Locator notation

| # | Fact | Status |
|---|---|---|
| A1 | A Locator with a plain name is a song | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A2 | A Locator starting with `>` is a section; `>>` is a quick-jump section | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A3 | Text in curly brackets is a description, for example `{Tuning: C, Capo 1}` | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A4 | Tags are written with `#`, for example `#rock` | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A5 | Square brackets hold a duration (`[3:20]`) or a colour name (`[blue]`) | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A6 | Flags: `+LOOP`, `+LOOP:4`, `+PAUSE`, `+SKIP` | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A7 | A Locator named `STOP` stops playback; `SONG END` jumps to the next song | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A7a | **Corrected.** A leading dot is written on a song's own Locator. That Locator is still a song. The dot tells AbleSet to stop playback at that boundary, before the song starts. Treating a dotted Locator as "not a song" loses a song from the set | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A8 | A leading `*` makes AbleSet ignore the Locator | Confirmed documentation, released Locator Notation read 2026-11-21; hardware unverified |
| A9 | Sections can also be defined by MIDI clips on a track named "Sections" or flagged `+SECTIONS` (Live 11 or later) | Reported |
| A10 | A track flagged `+LYRICS` holds one clip per lyric line, with the line as the clip name | Reported |
| A11 | There is no built-in way to mark a section as sung | Reported |
| A12 | Current released docs also say ClyphX locators are ignored. Q125-1 deliberately preserves ambiguous bracketed text with a warning | Confirmed documentation, Locator Notation, Ignored Locators |
| A13 | The complete grammar, including order of elements and escaping | Unknown |
| A14 | `AUTOSTOP`, `[nosong]`, `>>>` transitions, `+END`, `+LOOPFULL` and CSS classes are documented; see the direct verification ledger and fixture table | Confirmed documentation, released Locator Notation |
| A15 | AbleSet reports display names for songs and sections over OSC (A23), already cleaned of notation | Reported |

### OSC interface

| # | Fact | Status |
|---|---|---|
| A20 | A client subscribes with `/subscribe [ip] [port] [name]`; the IP may be `auto` or omitted | Reported |
| A21 | Optional extra arguments set fine updates (a boolean or a millisecond throttle) and glob filters, with `!` to exclude | Reported |
| A22 | `/unsubscribe` stops updates. `/heartbeat` is sent every 2 seconds. `/getHeartbeat` and `/getValues` request on demand | Reported |
| A23 | State addresses: `/setlist/activeSongName`, `/setlist/activeSongIndex`, `/setlist/nextSongName`, `/setlist/nextSongIndex`, `/setlist/activeSectionName`, `/setlist/activeSectionIndex`, `/setlist/songs`, `/setlist/sections` | Reported |
| A24 | State addresses: `/global/isPlaying`, `/global/isPaused`, `/global/isConnected`, `/global/tempo`, `/global/timeSignature`, `/global/beatsPosition`, `/global/humanPosition`, `/global/finePosition` | Reported |
| A25 | Version addresses: `/version/app`, `/version/live`, `/version/plugin` | Reported |
| A26 | Command addresses exist that change playback: `/global/stop`, `/setlist/go`, `/setlist/jumpBySongs`, `/setlist/jumpBySections`, `/setlist/jumpToLocator`, `/setlist/jumpToQueued` | Reported. These are writes. Not to be sent in this build |
| A27 | AbleSet listens for OSC on UDP 39051, in the Standard and Pro editions | Reported (review). AbleSet OSC documentation |
| A28 | Several clients can be registered at once | Reported (review). Whether they are fully isolated from each other is a hardware acceptance criterion |
| A29 | **Corrected.** Subscribing is visible. AbleSet shows a connection notice and lists the subscriber under Devices | Reported (review) |
| A30 | The 2-second heartbeat goes to subscribers. A heartbeat shows that AbleSet is responding. It does not show that AbleSet is connected to Live or that the position is current | Reported (review) |
| A31 | How AbleSet replies to `/getValues` from a client that has not subscribed, on the installed version | Unknown. Verify before the adapter is built |
| A32 | Whether a subscription is cleaned up when the client disappears, and how it behaves after AbleSet or Live restarts | Unknown. Hardware acceptance criterion |

Consequences for the design:

- **A29 means subscribing is not side-effect free.** A monitoring tool starts with bounded, filtered state requests. Subscribing is a separate decision that needs the approval of whoever runs the show computer.
- **A30 means a heartbeat is not a position.** Position is current only when AbleSet reports it is connected to Live and not loading, the fields themselves are fresh, and they have been re-read since the last reconnect.
- **A15 means a tool reading a running AbleSet shows the names AbleSet reports** and does not re-derive them from Locator text.

Verification tasks:
1. Read the released Locator Notation section in full and write the grammar down as a table of examples (A13, A7a, A14). This becomes the fixture set for music-video-pipeline #125.
2. Read the released OSC section in full; confirm the port (A27), the reply behaviour for requests without a subscription (A31), and the filter syntax (A21).

## 4. AbletonOSC

Primary source: https://github.com/ideoforms/AbletonOSC (README). MIT licence. Target: its latest release, with the latest released Ableton Live.

| # | Fact | Status |
|---|---|---|
| L1 | Requires Ableton Live 11 or later, installed as a remote script and selected as a control surface | Reported |
| L2 | Listens on UDP 11000 and replies on UDP 11001, to the IP that sent the request | Reported |
| L3 | `/live/test` replies `ok` and shows a message in Live | Reported |
| L4 | `/live/application/get/version` returns major and minor version | Reported |
| L5 | `/live/song/get/tempo`, `/live/song/get/is_playing`, `/live/song/get/current_song_time` | Reported |
| L6 | `/live/song/get/cue_points` returns name and time pairs | Reported |
| L7 | `/live/song/get/num_tracks`, `/live/song/get/track_names` | Reported |
| L8 | `/live/track/get/devices/name`, `/class_name`, `/type` take a track index | Reported |
| L9 | `/live/track/get/mute`, `/arm`, `/output_routing_type`, `/output_routing_channel` | Reported |
| L10 | `/live/song/start_listen/<property>` pushes changes to `/live/song/get/<property>` | Reported |
| L11 | `/live/song/get/track_data` is a bulk query over a track range | Reported |
| L12 | Write addresses exist under `/live/.../set/...`, and `/live/song/cue_point/jump` | Reported. Not to be sent in this build |
| L13 | The time in L6 is in beats. AbletonOSC returns `CuePoint.time` directly, and the Live Object Model documents `CuePoint.time` in beats | Reported (review). AbletonOSC's cue-point code; Live Object Model reference |
| L14 | Whether a plugin that failed to load can be detected through this interface | Unknown |
| L15 | Whether `/live/test` showing a message in Live is acceptable during a show | Unknown. It is visible to the operator; avoid it in routine polling |
| L16 | Whether AbletonOSC and AbleSet's own control surface script run side by side | Unknown |

Verification task: read the full API reference in the repository and promote or correct each row. L16 can only be answered on a real Mac with both installed, and must be tried on a Mac that is not the show Mac first; record it in `QUESTIONS.md`.

AbletonOSC is not used in the first release. The Ableton side is read through AbleSet only.

## 5. music-video-pipeline

Read directly from a clone on 2026-11-21. These rows are Confirmed for that date; re-check against the current head before building.

| # | Fact | Status |
|---|---|---|
| M1 | MIT licence. Python 3.10 or later. setuptools build. Dev extras provide pytest, pytest-cov and ruff | Confirmed |
| M2 | `music_video_maker/markers.py` defines `Marker`, `MarkerTrack`, the `MarkerSource` protocol, `MarkerCsvSource`, `parse_marker_time`, `read_marker_csv`, `parse_marker_csv`, `MarkerSection`, `marker_sections`, `to_alignment_result`, `format_marker_csv` | Confirmed |
| M3 | `music_video_maker/ableton.py` defines `AbletonError`, `AbletonLocatorSource`, `read_tempo_bpm`, `read_ableton_locators` | Confirmed |
| M4 | `ableton.py` reads Locators only and converts beats to seconds with one constant tempo | Confirmed |
| M4a | **Corrected.** The refusal of tempo automation has gaps. `read_tempo_bpm` looks at the first `<Tempo>` element it finds, counts tempo events under that element only, and refuses when there is more than one there. `read_ableton_locators` catches any tempo-read error, including that refusal, and carries on when the caller supplied `tempo_bpm` | Confirmed by reading `ableton.py` at commit f39d9df on 2026-11-21 |
| M4b | Where the installed versions of Live write the tempo envelope in a set file | Unknown. If it is not under the first `<Tempo>` element, a set with tempo changes is read today as constant tempo with no refusal |
| M5 | `ableton.py` returns each Locator's name, stripped of surrounding spaces, as the marker label, with no parsing | Confirmed |
| M6 | `ableton.py` has only been run against a synthetic fixture, `tests/fixtures/markers/synthetic_live_set.als.xml` | Confirmed (stated in its own docstring) |
| M7 | Issues #124 (tempo automation) and #125 (AbleSet notation) are open | Confirmed |

## 6. Spec Kit

| # | Fact | Status |
|---|---|---|
| S1 | The constitution lives at `.specify/memory/constitution.md` | Reported |
| S2 | Each feature lives in `specs/NNN-feature-name/` with `spec.md`, then `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, `contracts/` and `tasks.md` produced by later commands | Reported |
| S3 | The workflow is constitution, specify, clarify, plan, tasks, analyze, implement | Reported |

Sources: https://www.mintlify.com/github/spec-kit/commands/overview and https://learn.microsoft.com/en-us/training/modules/spec-driven-development-github-spec-kit-enterprise-developers/3-examine-github-spec-kit

Verification task: pin the latest released Spec Kit version, run `specify init` with the chosen integration in a scratch repository on the build machine, and adjust the layout of this pack to what that version produces. Do this before the unattended agent is started.

## 7. Claude connector

| # | Fact | Status |
|---|---|---|
| C1 | A Claude connector is a Model Context Protocol server | Reported, from general knowledge, not checked this session |
| C2 | The Claude desktop app supports local Model Context Protocol servers on the same machine | Reported (review). Claude Desktop local MCP documentation |
| C2a | What a local server returns still becomes part of a Claude conversation, which is stored outside the rig | Reported (review) |
| C3 | Current SDK names, transports and configuration | Unknown |

Verification task: read the current Model Context Protocol documentation and the official Python SDK before planning the connector.

## 8. Names and packaging

| # | Fact | Status |
|---|---|---|
| P1 | The names `huey` and `dewey` are both taken on PyPI by unrelated projects | Confirmed. pypi.org answered for both on 2026-11-21 |
| P1a | The names `refestramus-huey` and `refestramus-dewey` were free on PyPI on 2026-11-21 | Confirmed for that date. Re-check before publishing |
| P2 | PyPI does not accept a package whose metadata depends on a direct URL, such as a Git reference | Reported (review). Setuptools dependency rules |

Decided by the owner, 2026-11-21: Huey is distributed as `refestramus-huey` and imported as `refestramus_huey`. Dewey is distributed as `refestramus-dewey` and imported as `refestramus_dewey`. Each command-line command has the same name as its distribution. "Huey" and "Dewey" remain the names used in prose.

Consequences: A pinned Git reference to music-video-pipeline is fine while a repository is private and unpublished. A package published to PyPI must not carry that reference in its metadata.


## Direct verification ledger — 2026-11-21

This ledger supersedes historical handoff statuses only for the rows named here.
Confirmed below means a primary document was read, not device behavior observed.
No real device traffic, emulation or hardware acceptance was performed.

| Rows | Status and primary evidence |
| --- | --- |
| V1 | Confirmed listing: WING RACK firmware 3.1.2 on https://www.behringer.com/en/products/0604-AAE, Firmware section |
| V2 | Confirmed: WING Remote Protocols V3.1.0, cover states FW 3.1.0 and above. PDF SHA-256 b4496d27440e47b63729ac16786a631224e4c0a21efb9fda7f378d40ed6589ce. No edition explicitly 3.1.2 located. |
| V3 | Confirmed: AbleSet 3.1.9 is latest listed on https://ableset.com/changelog |
| V4 | Not reverified; no new Live-version-dependent functionality built |
| W1–W12a, W15 | Confirmed documentation claims: 3.1 manual OSC chapter pp.19–31, communications pp.16–18; actual Rack 3.1.2 behavior remains Unknown |
| W12 | Subscription wire addresses are `/*b`, `/*s` and `/*S`; printed `~` is a NULL byte, not part of the address | Confirmed documentation, 3.1 manual p.30; hardware unverified |
| W13 | Native TCP 2222; up to 24 TCP clients; 10-second inactivity timeout | Confirmed documentation, 3.1 manual p.16; corrected from 16 |
| W14 | Confirmed documentation: native UDP metering on channel 3; exhaustive absence of OSC meter addresses not established |
| W16–W19 | Not needed for released parser/file work. Known deferred action references recorded separately; no save/recall or complete-state command assumed |
| W20/W20a | Confirmed JSON tree and omitted read-only objects, pp.260–263. Root metadata and snapshot.9 appear in the diagram. Current 3.1.2 format signature and numeric JSON encoding remain Unknown |
| W21 | Confirmed documentation, 3.1 manual; exact pages in direct ledger/protocol-evidence.md; hardware unverified |
| W22 | Arithmetic only, not a measured supported polling rate |
| W23 | Read Wing Tools Routing Diff, terms and entry page directly. Hosted service 3.1; controlled synthetic-file comparison not run. Comparison remains held |
| W24 | Read libwing README, Cargo.toml and LICENSE directly: 1.0.6, native/discovery only, no OSC. Metadata MIT versus Apache-2.0 LICENSE discrepancy; no code reused |
| A1–A8, A12, A14 | Confirmed released Locator Notation page, read in full at https://ableset.com/docs/locator-notation, page modified 2026-02-08. A12 corrected: current released page also mentions ClyphX |
| A9–A11 | Held track-reading behavior; not newly verified or implemented |
| A13 | Formal grammar Unknown: docs do not specify escaping, scalar duplicate precedence or broad ClyphX recognition. Preserve unknown text and warn per spec; Q125-1 answered preserve with warning |
| A15 | Running AbleSet names are for display; parser is for raw Locators. No running service tested |
| A20–A32 | OSC docs read for request/subscription section, but adapter behavior not tested; no new adapter built. A31 remains Unknown on installed hardware |
| L1–L16 | Held; no AbletonOSC implementation or reliance added |
| M1–M6 | Current local pyproject.toml, markers.py, ableton.py and synthetic fixture re-read. Existing constant-tempo override refusal gap remains held under issue #124 |
| S1–S3 | Confirmed by Spec Kit 1.4.3 actual init in /tmp scratch using Codex skills integration and sh scripts; installed pinned release commit 980b3d027f4bd7958c35f97f618d854b41320e3f |

Primary WING PDF:
https://cdn-media.empowertribe.com/2106004e217b8eb2639d93672823eef5/WING_Remote-Protocols-3.1-03.pdf

Spec Kit 1.4.3 uses `.specify/feature.json` feature_directory (or
SPECIFY_FEATURE_DIRECTORY), independent of the actual git branch. Its generated
skills are the clarify/plan/tasks/implement workflows, executed by the agent,
not shell executables. Supplied specs were copied, never regenerated. Actual
repositories remain on main. No extension hooks or git automation installed.

Encoder verification task 6: no OSC library selected. A small strict codec can
omit the type tag directly; exact independent vendor hex fixtures pin bytes.
Emulators are optional and were not installed. Confirmed documentation is never
promoted to hardware acceptance by a passing test.

## Approved assumptions and installed tooling

Owner answered H1: separate request/reply policy. Owner answered H2: allow a
strict synthetic-only snapshot.9 format assumption with target metadata 3.1.2.
`assumed_snapshot_9_for_synthetic_3_1_2` isolates this boundary; tests use assumed
in their names. This never promotes real/latest-format compatibility to Confirmed.
Numeric regeneration uses only fully documented examples; general conversions
remain Unknown under H3. JSON Pointer RFC 6901 sections 3–4 and 7 were read
directly; malformed/negative/noncanonical array indices are refused.

Installed local test tools: Python 3.12.13, pytest 9.2.0, pytest-cov 7.1.0,
coverage 7.17.4, ruff 0.17.6. Distribution version 0.1.0; no publication.

## Hotel review follow-up — 2026-11-21

Primary manual pp21–24 re-read; additional exact-address channel-1 fader examples
-1.0/raw0.725, 3.0/raw0.825 and 4.0/raw0.85 are tested. The initial 0.0 mapping
came from a channel-2 example and was removed from channel-1 regeneration instead
of relabelling the evidence. Channel-2 examples stay in the independent fixture
with their original addresses. No general transfer law is established; H3 stays
open. The p30 aggregate $mute example demonstrates that arbitrary integer values
cannot be used as their own normalised raw float.

The Linux public Wing Tools demo is now observed, build v3.1-46, browser
151.0.7922.34. It loads precomputed data and does not close controlled-input WT-1.
See the evaluation follow-up. No provider implementation was reused.

Packaging uses SPDX `license = "MIT"` and project.license-files, supported since
setuptools 77.0.0 per its official pyproject configuration documentation:
https://setuptools.pypa.io/en/latest/userguide/pyproject_config.html .

## Offline comparison implementation verification — 2026-11-21

Primary sources personally re-read for Story 1:
[Python fnmatch documentation](https://docs.python.org/3.12/library/fnmatch.html)
confirms case-sensitive fnmatchcase and slash-crossing wildcards;
[RFC 6901 sections 3–5/7](https://www.rfc-editor.org/rfc/rfc6901.html)
confirms pointer escaping, exact names and array indices;
[RFC 8259 sections 3–6](https://www.rfc-editor.org/rfc/rfc8259.html)
confirms JSON types, empty containers, ordered arrays and the number grammar.
These are Confirmed language/identifier facts, not WING compatibility evidence.
JSON has one number grammar; numeric representation equality is owner question
C1. All identifiers ignored is owner question C2. Both have now been answered:
preserve integer/float differences and refuse all-ignored requests. These are
owner comparison policies, not claims imposed by either RFC or the console.

Independent hand-written synthetic expectations cover three planted changes,
added/removed versus null, empty values, object/array type changes, escaped keys,
exact/glob ignores and compatibility before ignores. File bytes and loaded input
objects are unchanged, sockets are prohibited during comparison tests. The H2
success guard remains exact; metadata-only not_comparable results do not validate
unsupported model/firmware files. No actual firmware/schema fact is promoted.

## Owner decisions and version recheck — 2026-11-21

QUESTIONS.md C1/C2 are answered and implemented: decoded integer/float
representation changes are differences; all identifiers ignored refuses with
FileError/CLI status 6. Red tests preceded the source changes. Full suite: 165
passed, 89.73% coverage, Ruff clean. Rebuilt installed-wheel library/CLI checks
passed outside the checkout. None of this validates real snapshots or devices.

The official [WING Rack product page](https://behringer.com/en/products/0604-AAE)
still lists firmware 3.1.2. [AbleSet downloads](https://ableset.com/download) list
3.1.9. [Live 12 release notes](https://www.ableton.com/en/release-notes/live-12/)
list 12.4.16 dated 2026-10-30, and [Live 13's FAQ](https://www.ableton.com/en/live/)
explicitly schedules release in early 2027. These personally read sources confirm
the current released targets; H2's actual installed format/firmware evidence is
still unknown. No fixture profile, transport policy or real-device scope changed.
