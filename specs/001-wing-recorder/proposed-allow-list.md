# Proposed supervised reads — documentation only, not released

Target for review: **WING Rack, firmware 3.1.2**. The 3.1 manual claims firmware
3.1.0 and above; no 3.1.2-specific exchange evidence exists. The runtime file has
**zero real-device entries**. This note is not sign-off and enables nothing.

Source: WING Remote Protocols V3.1.0, linked and hashed in protocol-evidence.md.
Every proposed request is address-only with no type tag/arguments; every address
is fully spelled out, without patterns or special syntax. Destination would be
the single explicitly configured console address at UDP 2223, subject to owner
approval. No discovery broadcast is proposed. The example indices are generic,
not a statement about anyone's channel or bus assignments.

| Operation | Canonical address | Documentary evidence | Target-device evidence |
| --- | --- | --- | --- |
| Identity | `/?` | pp.20–21, exact example | Missing for Rack 3.1.2 |
| Mute check | `/ch/1/mute` | p.21 exchange; p.48 table | Missing |
| Monitor bus mute | `/bus/1/mute` | p.56 table | Missing |
| Monitor bus level | `/bus/1/fdr` | p.56 table | Missing |
| Source group | `/ch/1/in/conn/grp` | p.47 table | Missing |
| Source group index | `/ch/1/in/conn/in` | p.47 table | Missing |
| Send enabled | `/ch/1/send/1/on` | p.51 table | Missing |
| Send level | `/ch/1/send/1/lvl` | p.51 table | Missing |

Before any live entry: owner selects the actual minimal checks/addresses, verifies
installed model/firmware, signs the exact operations and destination, and supervises
a measured small-read trial while audio and another control client are active.
The traffic budget, retry limits and late-reply window remain undecided (H4).
No polling/client code is built here. Existing subscriptions must stay unaffected;
only hardware can establish that. A few vetted reads cannot certify a whole rig.

Never propose subscription addresses, redirected ports, node wildcards, string
queries, hash aliases, bundles, tree walks, meters, writes or library actions.
