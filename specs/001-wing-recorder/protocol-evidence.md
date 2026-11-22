# WING 3.1 protocol verification evidence

Read 2026-11-21. Documentation evidence only; no emulator or hardware run and no device traffic.

Primary PDF: https://cdn-media.empowertribe.com/2106004e217b8eb2639d93672823eef5/WING_Remote-Protocols-3.1-03.pdf

SHA-256: `b4496d27440e47b63729ac16786a631224e4c0a21efb9fda7f378d40ed6589ce`.
Cover: version 3.1.0, firmware 3.1.0 and above. This is a 3.1 edition, not the old 3.0.6 edition. Target firmware is 3.1.2. No edition explicitly versioned 3.1.2 was located here, and the examples are not a trace from 3.1.2; therefore installed-device behavior is still unverified. Generic forward-coverage wording does not independently prove unchanged behavior in a subsequent firmware.

## Reading completed

OSC pp.19–31 in full; communications pp.16–18; snapshot appendix pp.260–263, including rendered images on pp.260 and 262; model-family section pp.11–12; Rack layer table pp.79–80; model-specific monitor annotation p.34 and headphone-output annotation p.51; library/global command table pp.90–91 and Shows/Scenes appendix pp.229–231.

## Confirmed documentation claims and corrections

- W1: UDP OSC 2223 (pp.16,19).
- W2: replies use caller source port; `/%<port>` changes return port, retaining IP (pp.19,21).
- W3: discovery is exact five bytes `WING?` to UDP2222. Response comma fields are IP,name,model,serial,firmware (p.16).
- W4/W5: `/?` identity; a GET can omit the type tag, or carry an empty comma tag (pp.20–21). Replies for enum/string, float, integer are respectively `,s`, `,sff`, `,sfi`.
- W6/W7: typed arguments can set parameters; integer -1 toggles binary integer leaves; originating UDP client does not get its own data echoed (p.22).
- W8: bare node path lists children; root `/` example is p.20.
- W9: special string arguments `*`, `?`, `#` select node dump/description/description-with-values (pp.24–25). No permission to send them to arbitrary leaves follows from this.
- W10: a string argument at root/node can set several values; relative traversal notation uses dots (pp.23–24).
- W11/W12/W12a: single subscription, last requester wins, renewed within 10 seconds (pp.16,30). Wire addresses are `/*b`, `/*s`, `/*S`; the printed tilde represents NULL, not an address character.
- W13 correction: maximum TCP clients is **24**, not the older 16 (p.16). Native TCP port2222 and inactive-connection timeout10sec are documented. No native client is needed for Tier A.
- W14: native channel3 is metering over UDP (p.16); no claim of exhaustive absence of all possible OSC meter leaves is made.
- W15: `/ch/1/fdr`, `/ch/1/mute` exact read examples on p.21; `/bus/1/fdr` appears in node-write illustration p.23 and bus table p.56, not a recorded Rack read.
- OSC bundles are unsupported; packet size multiple4, maximum32k (p.19). Unknown-path GET response is not established by the write-error example on p.23; stand-in should remain silent and log rather than invent response semantics.

## Independently written unsafe-operation inventory

This inventory was written from the manual, not generated from any gate implementation or allow-list.

Proven state-changing despite no arguments (p.30):

| Address | Omitted tag bytes | Empty tag suffix also accepted |
| --- | --- | --- |
| `/*b` | `2f2a6200` | `2c000000` |
| `/*s` | `2f2a7300` | `2c000000` |
| `/*S` | `2f2a5300` | `2c000000` |

The `/%<port>/` prefixed variants also take the subscription and redirect it. Reject all of them, including forms with arguments, and never treat empty type tags as evidence of read-only intent. The chapter establishes no additional zero-argument action/trigger families. That is **not** evidence that no other family exists: all unknown operations remain denied. The exact-listed read approach prevents this unknown inventory from becoming a permissive allow-list.

Other denied syntax/operations: reply-port prefix `/%`; hash addresses `/#<hex>` (p.21); root/node multi-assignment string (pp.23–24); special node string queries (pp.24–25); typed writes/toggle (p.22); blob/native payloads, which can also write (pp.27–29); all bundles, noncanonical spellings, and unconfigured destinations. `/?` is an explicitly documented identity operation, not a general wildcard exemption.

## Independent exact vendor exchange fixtures

Transcribed from printed hex, without encoder code. Hex lengths checked independently. These are the vendor's published examples, not real-rig captures and not 3.1.2 observations. Do not replace their example firmware or model while calling them byte-identical vendor traces.

Identity (p.20):

- request,4 bytes: `2f3f0000`
- reply,80 bytes: `2f3f00002c73000057494e472c3139322e3136382e312e37312c50474d2c6e67632d66756c6c2c4e4f5f53455249414c2c312e30372e322d34302d6731623162323932623a646576656c6f7000000000`

Channel1 fader, negative infinity (p.21):

- request,12 bytes: `2f63682f312f666472000000`
- reply,32 bytes: `2f63682f312f6664720000002c736666000000002d6f6f0000000000c3100000`
- decoded reply: address `/ch/1/fdr`, tags `sff`, string `-oo`, normalised float0.0, value float-144.0.

Channel1 mute,on (p.21):

- request,12 bytes: `2f63682f312f6d7574650000`
- reply,32 bytes: `2f63682f312f6d75746500002c73666900000000310000003f80000000000001`
- decoded reply: address `/ch/1/mute`, tags `sfi`, string `1`, normalised float1.0, integer1.

## Snapshot structure established, and gaps

Page260 rendered diagram shows **root-level metadata**, not a `description` object:

`type`, `creator_fw`, `creator_sn`, `creator_model`, `creator_version`, `creator_name`, `created`, `active_show`, `active_scene`, `ae_data`, `ce_data`, `ae_globals`, `ce_globals`, `scopes`, `updated`.

The literal type in that diagram is **`snapshot.9`**. Its example firmware is 2.1 development-era, although the document edition is 3.1.0. No new snapshot type for 3.1.2 is established by this reused example. The exact format signature emitted by firmware3.1.2 is Unknown. Do not invent `snapshot.10`/`snapshot.11` as its latest signature or claim a matching fixture without another primary source.

JSON hierarchy is documented; the image on p.262 puts `cfg`, `io`, `ch`, `aux`, `bus`, `main`, `mtx`, `dca`, `mgrp`, `fx`, `cards`, `play`, `rec` under `ae_data`. No leaf-value JSON excerpt was found in this appendix. The OSC parameter table's `I`/`F`/`S` categories do not prove the JSON scalar representation of each snapshot leaf. Lossless tree reading and typed synthetic planting can use actual JSON types without claiming a universal parameter schema; numeric display/raw-value regeneration needs an explicitly isolated assumption or independently documented transformation.

W20/W20a: file is hierarchical JSON; default file roughly800000bytes/33895lines, over30000 object identifiers; excludes read-only objects (p.260). Scopes are optional provenance strings of plus/space characters, not freely writable console parameters (pp.261–262).

## Rack/configuration differences

- Rack has24 local inputs, no local AUX I/O, four rear headphone pairs mapped to local outputs, no faders and a different custom-control surface (pp.11–12).
- `/$syscfg/$cnscfg` and `$cnsmdl` identify model/configuration; documented examples include wing-rack (p.39).
- Some monitor controls are read-only on full-size hardware with a physical potentiometer but settable on models lacking it (p.34 footnote13). Thus table labels do not give model-independent write/read safety.
- Rack headphone-output range differs (p.51 footnote27).
- Rack control mode is `/$ctl/cfg/rackmode` (p.74); Rack-only layers live at `/$ctl/layer/RCK/...` and differ from full-size/Compact; several range entries are explicitly TBV (pp.79–80).
- Snapshots may retain USER layer/custom-control definitions from multiple models; inapplicable ones are ignored, not removed (p.230).
- Selecting effects/plugins alters available child parameters (p.26). General hardcoded complete-tree claims are unsupported.

## Deferred command research, no implementation

Pages90–91 document `/$ctl/lib/$action` with IDLE/GOPREV/GONEXT/GO/PREV/NEXT/GOTAG and `/$ctl/lib/$actionidx`; GO can load a selected Scene (snap/snippet/preset/audio clip). `/$ctl/$globals/$savenow` saves console data and has an explicit flash-wear warning. These are not allow-list candidates. The manual's table does not establish a complete general OSC API for create/delete/export/import snapshots, shows or library files. The shows appendix describes console UI/MIDI management (pp.229–231), not permission to implement those operations. Keep any missing save/recall operations Unknown and deferred.

## Questions that evidence does not decide

1. Latest snapshot signature/schema on3.1.2: obtain vendor-authored representative format documentation or a supervised authorised export, or approve a deliberately isolated synthetic-only older documented schema; recommendation obtain primary current evidence before claiming3.1.2 snapshot compatibility.
2. Numeric regenerated responses: record exact per-leaf raw-value conversion from primary evidence, or leave unsupported leaves silent; recommendation support byte-exact recorded exchanges first and isolate synthetic regeneration assumptions.
3. Firmware coverage: obtain3.1.2-specific evidence before live operations; no Tier A fixture test can settle this.
