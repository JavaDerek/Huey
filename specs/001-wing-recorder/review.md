# Code and safety review follow-up — 2026-11-21

Scope: file provenance and typed JSON, mandatory final send boundary, independent
wire evidence, capture segments, localhost replayer lifecycle and wheel packaging.
This is a fresh agent review with independent primary-source checks, not an
external audit. No actual-device acceptance is established.

| Finding | Severity | Location | Resolution |
| --- | --- | --- | --- |
| Disjoint reads from multiple sittings could be merged into one replay | High | replayer.py _responses | Fixed: files remain readable, replay requires exactly one segment |
| Discovery returned before checking for an allow-list entry | Medium | safety.py check_request | Fixed: default deny also applies to discovery |
| Approved reply bytes could still carry the wrong per-address type form | Medium | safety.py _Transport | Fixed: policy pins documented reply tags |
| Below-gate audit accepted broad tag families without matching origin | Medium | tests/conftest.py | Fixed: independent per-address forms and prior request/source endpoint checked |
| JSON exponent overflow loaded infinity despite NaN-token rejection | Medium | files.py _load | Fixed: finite-number validation, including public object input |
| Python bool/int equality accepted misleading decoded evidence | Medium | files.py _validate_capture | Fixed: exact JSON-type equality |
| Plant could report changing the synthetic serial marker then silently restore it | Medium | files.py plant | Fixed: marker is protected and the operation refuses |
| Commas/control bytes could make discovery identity fields ambiguous | Medium | replayer.py _responses | Fixed: refuse instead of inventing escaping |
| Channel-2 fader example was applied to channel 1 | Medium | replayer.py _regenerate_documented_value | Removed that case; exact channel-1 documented examples are tested separately |

Findings were reproduced with failing tests before fixes. All real sends remain
in one transport call immediately after the gate. Every library socket send in
the suite is counted below that gate and checked against a separately maintained
operation inventory and originating localhost request. The data-file list for
real devices remains empty. Bad requests cannot be admitted by an extra caller
predicate. No write, comparison or native-protocol client is scaffolded.

H3 remains open: per-address examples are not a general normalisation law.
All JSON fixtures are now checked for explicit synthetic provenance. The
independent vendor-values fixture retains exact original addresses; printed
decimal examples are not described as byte-exact hardware traces. WT-1 now has
observed Linux demo UI evidence, while controlled-file comparison remains unrun.
The public screenshots/provider scripts stay outside repositories.

Validation: **123 tests passed**, **87.47% coverage**, ruff passed. A fresh wheel
was built and installed outside the checkout; inspect and bounded localhost replay
ran successfully and the packaged policy/SPDX MIT metadata were checked. Native
3.1.2 schema and actual Rack behavior remain unverified under H2/H4.

No real traffic, uploads, paid access, messages, commits, pushes or publication.
