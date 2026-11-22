# Wing Tools Routing Diff evaluation

Verified from primary web pages on 2026-11-21. This is an evaluation of an existing service, not a specification or implementation of its features. No account was created, no subscription bought, no snapshot uploaded, and no console client or bridge run.

## Availability and evidence

The current [official changelog](https://wingtools.theta-tontechnik.de/changelog) labels the service **3.1** as latest. It does not expose a build hash that could pin a hosted deployment.

The [actual Routing Diff entry page](https://wingtools.theta-tontechnik.de/tools/routing-diff) requires Premium for comparing user snapshots. It offers a no-account demonstration using supplied sample data. This is not a controlled test with independently authored synthetic snapshots.

The [Getting Started requirements](https://wingtools.theta-tontechnik.de/docs/01-getting-started) name modern Chrome, Firefox, Safari or Edge. A follow-up actually exercised the public demo in headless Linux Chromium; details below. No Linux standalone/offline Routing Diff package was identified. WingBridge is a separate live-console helper and was not installed or run.

## What its documentation establishes

The [Routing Diff manual](https://wingtools.theta-tontechnik.de/docs/06-routing-diff), read directly in full, documents:

- Comparison of input assignments, names, sends, output patches, and added/removed routing; Premium covers channels, auxes, buses, mains and matrices. Pro additionally covers FX and hardware inserts.
- List, matrix and side-by-side views; change filters and a send-level threshold. Its default threshold is 3 dB, so a complete saved-value check would require different settings and independent verification.
- A warning when model or version metadata differs, while still permitting comparison. This does not establish the distinct machine-readable incompatibility status required of an offline library.

This is documented scope, not measured coverage. An exhaustive identifier-level comparison of arbitrary saved parameters is not established. Coverage of mutes, phantom power, EQ, dynamics, miscellaneous configuration, unknown identifiers and malformed snapshots remains unverified. No claim that these fields are actually omitted has been demonstrated.

## Licence and reuse

The service's [Terms of Use](https://wingtools.theta-tontechnik.de/TERMS.txt), **1.2**, effective 2026-06-01, describe a limited service-use licence, with paid commercial use. Section 4 grants product-development usage rights over non-commercial uploads; commercial uploads are excluded from that grant. These are material terms for an owner considering upload of any private file.

The documentation footer reserves copyright and expressly disallows using its content to recreate competing software. No open-source licence for Routing Diff itself was found. The [Licenses page](https://wingtools.theta-tontechnik.de/licenses) redirects toward a third-party notices page; such notices do not establish permission to reuse the service's implementation. No source or documentation was copied into implementation code.

## Controlled synthetic evaluation: blocked

No comparison engine run was performed against controlled synthetic files: the documented workflow uploads user files to the hosted service and requires a paid account. The scope of this evaluation excludes both. A sample-data demo cannot substitute for the required known-change fixtures.

Proposed future acceptance matrix, with expected results authored independently from the WING protocol specification: unchanged files; one routing change; one small level change; mute/phantom/EQ changes; an added/removed identifier; model/firmware mismatch; unsupported snapshot signature. Every row is **not run**. No result is evidence about console behavior.

### Owner question WT-1

Which route should be taken before releasing snapshot comparison?

- A: Owner performs or authorizes a licensed hosted evaluation with synthetic files, then decides whether the service covers the need.
- B: Owner arranges an offline evaluation or written permission with the provider.
- C: Owner releases a separately designed local comparison based only on the WING vendor format, after reviewing this incomplete evaluation.

Recommendation: A if hosted use is acceptable, otherwise B. Keep snapshot comparison held. No option has been selected; no comparison has been implemented.

## libwing evaluation

The original repository URL redirects to [dannyfiresnake/libwing](https://github.com/dannyfiresnake/libwing). Sources were read at commit **36d713e360ea8c37f210e4bb5f3a9a161b65ba17**.

The [README Protocols section](https://github.com/dannyfiresnake/libwing/blob/36d713e360ea8c37f210e4bb5f3a9a161b65ba17/README.md#protocols) explicitly implements native and discovery protocols and excludes OSC. It exposes Rust and C interfaces. Its property map comes from Compact firmware 3.0.5, not independently verified Rack 3.1.2 evidence. Some utilities write values or automatically discover consoles; none was run.

The [crate registry metadata](https://crates.io/api/v1/crates/libwing) confirms **1.0.6**, released **2026-10-30**, as latest stable and not yanked; the repository's [changelog](https://github.com/dannyfiresnake/libwing/blob/36d713e360ea8c37f210e4bb5f3a9a161b65ba17/CHANGELOG.md) agrees.

Licensing is inconsistent: [Cargo.toml](https://github.com/dannyfiresnake/libwing/blob/36d713e360ea8c37f210e4bb5f3a9a161b65ba17/Cargo.toml) and registry metadata declare MIT, while [LICENSE](https://github.com/dannyfiresnake/libwing/blob/36d713e360ea8c37f210e4bb5f3a9a161b65ba17/LICENSE) contains Apache-2.0. Do not describe it simply as MIT without resolving this discrepancy.

Reuse recommendation for the released localhost OSC work: no dependency on libwing, because its implemented protocols do not supply the required OSC codec/replayer. No library was installed or copied. Before any future native-protocol reuse, record the licence discrepancy as a question with options to obtain clarification or select another library; no upstream issue was opened.


## Follow-up: observed Linux public demo — 2026-11-21

The no-account [Routing Diff demo](https://wingtools.theta-tontechnik.de/tools/routing-diff)
was exercised in a fresh Linux browser context (Chrome for Testing 151.0.7922.34),
hosted build **v3.1-46**. List, Matrix and Side-by-Side views worked; changing the
threshold from 3 dB to 6 dB filtered the sample display. An audit recorded 32
provider GET/HEAD requests, zero comparison-API calls and no page errors. Uploads,
non-read requests, WebSockets and external-domain requests were blocked.

The demo loads precomputed sample results. This establishes usable Linux UI,
not comparison-engine accuracy, current firmware compatibility or independent
synthetic-fixture coverage. WT-1's acceptance matrix remains unrun. Proprietary
scripts/screenshots are evaluation artifacts kept outside the repository; none
was copied into this implementation or public test fixtures.

Decision-ready conclusion: the evidence does not yet qualify the service as a
validated replacement for exhaustive offline saved-value comparison. Recommendation:
keep the current code independent and comparison held while the owner chooses
licensed controlled testing, offline access, or a later local-comparison release.
No purchase, provider contact, upload or product/release decision was made.

## Owner decision after evaluation

The owner has now released an independent local snapshot comparison using the
existing synthetic-only compatibility guard (QUESTIONS.md WT-1). The earlier
hold/recommendation above records the evaluation stage, not the current release.
The hosted engine remains unvalidated; no code, assets or proprietary algorithms
were reused. No account, subscription, upload or new device authority follows.
