# DECISIONS.md — proposals and decisions log (smoke project)

IDs: **D-nn** = owner decisions (text as issued); **CC-nnn** = agent proposals/decisions. Status: **OPEN** (needs owner), **APPROVED**, **DECIDED** (delegated), **APPLIED (!)** (applied ahead of the owner's nod), **REJECTED**, **SUPERSEDED**. A literal pipe inside a cell is written `\|`.

| ID | Date | Status | Topic | Proposal / decision | Reason |
|---|---|---|---|---|---|
| **D-01 (owner)** | 2026-01-01 | **APPROVED** (owner, spec §1) | Board outline 30 × 50 mm, 2 layers | As specified in SPEC §1; corner radius 1.0 | Owner's word |
| **D-02 (owner)** | 2026-01-01 | **APPROVED** (owner, chat) | USB-C mid-mount at the rear edge | Vendor pattern puts the SMT pad ends on the notch wall; the fab DFM 'Pad to board edge' items for J1 are accepted by refdes | Owner's word |
| **D-03 (owner)** | 2026-01-02 | **APPROVED** | Two-piece FDM case (tray + hood) | 20-design/case.yaml, preset fdm default, jlc preset kept for a print-service build | Owner's word |
| CC-001 | 2026-01-02 | DECIDED (delegated by SPEC §3: copper rules) | Copper minimum 0.16/0.16, via 0.30/0.62 | The fab grades a value EQUAL to its warning threshold as Warning: design strictly greater than the published minimum | references/fab-dfm.md |
| CC-002 | 2026-01-02 | APPLIED (!) owner look wanted — C2 value 1 µF (was 100 nF in the spec draft) | Decoupler value | The LDO datasheet §7.2 asks for ≥ 1 µF on the output; the spec draft said 100 nF | rule 2: proposed, applied with the nod marker, KNOWN_ISSUES §2.1 lists it |
| CC-003 | 2026-01-03 | OPEN (owner question) | Case colour and top-face mark | Black PETG with a top-face two-tone band, or single colour? | owner preference |
