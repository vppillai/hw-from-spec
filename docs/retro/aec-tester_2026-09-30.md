# Retro — aec-tester → hw-from-spec (2026-09-30)

Project `aec-tester`: 8 dated learnings, 297 decision rows (87 owner rows). Skill `hw-from-spec` at SKILL.md version **0.7.0**; the project recorded skill version **none (add `skill: {version: …}` to project.yaml)**.
Classifier: keyword overlap against 201 sections (threshold 0.5); a human folds the candidates — this report is the input to the next CHANGELOG entry, not the entry itself.

## 1. Counts

| CARRIED | PARTIAL | NEW | NEW and costly (a round, an order, a wrong result) |
|---|---|---|---|
| 0 | 5 | 3 | 0 |

## 2. NEW — learnings the skill does not carry yet

| Date | Domain | Learning | Best section (coverage) | Costly |
|---|---|---|---|---|
| 2026-09-30 | kit/ux | A kit needs ONE entry point the technician can follow without the repo: print order with the PROJECT file names (the print sheets were named `shell` / `plate_ui` while the projects were `case_body` / `case_legend_plate`)… | `references/dfm-printed-enclosure.md` › 8.3 Bambu Studio CLI facts (02.08.x, 2026-09-29 —  (0.14) |  |
| 2026-09-30 | fdm/design | Bridge ceilings must sit BELOW the datum lands they neighbour: the hood plate rested on three 6 mm bridge undersides (sag 0.1..0.3 toward the plate) while its grooves sat on the flat land tops - the plate stood on the sa… | `references/dfm-printed-enclosure.md` › 8.1 Brand marks / logos on FDM parts — an OWNER ch (0.16) |  |
| 2026-09-30 | fdm/design | A 45.0 deg face is AT the overhang limit, not under it, and the same face changes class with the orientation: the thumb lip's cone faces UP on the mouth-down cap (harmless) and DOWN on the closed-end-down AMS cap (a visi… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.17) |  |

## 3. PARTIAL — carried in part (check the section, extend it if the mechanism is missing)

| Date | Domain | Learning | Best section (coverage) |
|---|---|---|---|
| 2026-09-30 | kit/ux/gates | Template leftovers reach the technician: the kit README said the magnet pockets sit "at Y None" because the hood bullet read the SCREW dict (`c.hscrew`) while the fastener knob was… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.26) |
| 2026-09-30 | kit/hardware | Hardware lists must be GENERATED from the fastener knobs, never typed: "6 inserts, 2 in the hood bosses" survived two fastener changes (screws -> magnets) in the README, eight prin… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.28) |
| 2026-09-30 | fdm/design | Widening a glued plate's clearance widens the REBATE, and the rebate lip to the roof fillet is a census wall: +0.1 per side took the 1.6 lip to 1.53 = FAIL. Keep the rebate footpri… | `references/dfm-printed-enclosure.md` › 1. MJF rules (worked example: JLC3DP PA12-HP; chec (0.34) |
| 2026-09-30 | kit/ux | Raised legend items may not run to a plate edge: three 1.0 x 1.2 switch triangles starting 0.05 inside the outline became non-watertight 0.66 mm stubs that Bambu Studio sliced "cle… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.29) |
| 2026-09-30 | process/records | ASSEMBLY / QA prose must be generated from the preset like the geometry: the p2s ASSEMBLY.md still said "0 magnets, Material: PETG, the two snap tabs click" three fastener changes … | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.27) |

## 4. CHANGELOG entry draft

### Added (from aec-tester, learnings 2026-09-30 … 2026-09-30)
- **`references/dfm-printed-enclosure.md`**: A kit needs ONE entry point the technician can follow without the repo: print order with the PROJECT file names (the print sheets were named; Bridge ceilings must sit BELOW the datum lands they neighbour: the hood plate rested on three 6 mm bridge undersides (sag 0.1..0.3 toward th
- **`references/pitfalls.md`**: A 45.0 deg face is AT the overhang limit, not under it, and the same face changes class with the orientation: the thumb lip's cone faces UP 

### Changed
- (sections the PARTIAL entries extend: `references/dfm-printed-enclosure.md`, `references/pitfalls.md`)

## 5. Reference patch stubs (bullets to append; generalise the numbers, label the worked example, keep the evidence pointer at the end)

### references/dfm-printed-enclosure.md
- 2026-09-30 [kit/ux] A kit needs ONE entry point the technician can follow without the repo: print order with the PROJECT file names (the print sheets were named `shell` / `plate_ui` while the projects were `case_body` / `case_legend_plate`), objects and minutes per plate, the check between prints, the assembly sequence with the order-critical facts (inserts from below, magnets dry before CA, feet LAST because they cover the screw heads) and a numeric report-back block with a recipient. Written by the slicer wrapper (it owns the minutes) from a facts JSON the geometry generator writes - the numbers come from the sidecars, the prose from the knobs.
- 2026-09-30 [fdm/design] Bridge ceilings must sit BELOW the datum lands they neighbour: the hood plate rested on three 6 mm bridge undersides (sag 0.1..0.3 toward the plate) while its grooves sat on the flat land tops - the plate stood on the sag humps and rocked. Make the flat bed-face lands the datum and give the bridged strips a sag gap (here 0.2 = one layer) under the part; if deepening the strips would thin a wall below the rule, thin the PLATE instead (t 1.6 -> 1.4 kept the proud height and the skin rule).

### references/pitfalls.md
- 2026-09-30 [fdm/design] A 45.0 deg face is AT the overhang limit, not under it, and the same face changes class with the orientation: the thumb lip's cone faces UP on the mouth-down cap (harmless) and DOWN on the closed-end-down AMS cap (a visible 45.0 deg overhang). Orientation-dependent knobs (`lip.cone_deg_ams` 50) plus a measured steepest-overhang row per orientation, not one angle for both prints.

## 6. Eval stubs — one per NEW learning that cost a round (fill prompt / assertions from the entry; add to evals/evals.json)

```json
```

## 7. Owner decision topics the kickoff questionnaire does not ask yet (candidates for a new question with a recommended answer)

| Row | Date | Topic | Best question section (coverage) |
|---|---|---|---|
| D-04 | 2026-09-13 | AEC-CT2-MINI form factor: **cage-sized stick** | — |
| D-05 | 2026-09-13 | Enclosure is a design input for the MINI stick — dimensions and clearances | — |
| D-06 | 2026-09-13 | MINI silk screen: self-documenting labels; no silk over pads | — |
| D-09 | 2026-09-13 | Product look and feel: premium, for the MINI stick and the main board | `A4 Enclosure process and material (per target)` (0.19) |
| D-10 | 2026-09-13 | Final thorough review after design + implementation | — |
| D-11 | 2026-09-13 | Reviewer hand-off document for external deep reviews | — |
| D-12 | 2026-09-13 | Case: single-nozzle FDM friendly; colour by separate glued pieces | `A2 Quantity and horizon` (0.24) |
| D-13 | 2026-09-13 | USB-C receptacle: clearances and mechanical reinforcement for many insertions | `A0 Project scope` (0.17) |
| D-14 | 2026-09-13 | Case: latch two MINI units together into a two-end cable jig | `A2 Quantity and horizon` (0.25) |
| D-09a | 2026-09-13 | Premium aesthetics and a thought-through user experience apply to the MAIN board too | `kickoff-questionnaire.md — every owner decision a board and ` (0.17) |
| D-16 | 2026-09-13 | External FTDI/pod path = backup debug path, not a mode of operation; pluggable, compact, case need not expose it | `I. Identity, envelope, delegation (added by the first retro ` (0.13) |
| D-18 | 2026-09-13 | EXT/LA connectors and EXT pinout: CC-057 set with the 1.27 mm LA pair; CC-056 Total Phase order | — |
| D-19 | 2026-09-13 | External models for the double-blind reviews via the installed `agent` CLI | `E1 Review rounds per gate` (0.23) |
| D-20 | 2026-09-13 | MINI stick dimensions are secondary: grow the board as required to route cleanly; functionality, electrical and signal i | `B1 Layers and thickness` (0.08) |
| D-22 | 2026-09-13 | Deep layer-by-layer, trace-by-trace visual inspection of the routing after final routing | `F2 Stock policy and alternates` (0.21) |
| D-24 | 2026-09-14 | MINI printed case: two-tone, per-colour AMS printing, assembly-friendly for 50+ units | `A2 Quantity and horizon` (0.19) |
| D-25 | 2026-09-14 | Product name: AEC-CT2 = AEC Cable Tester 2 | — |
| D-26 | 2026-09-14 | MINI USB-C receptacles: CC-052 option B (mid-mount XYECONN C20883026) | — |
| D-27 | 2026-09-14 | Fan: none fitted, provision kept for a specific part sourced outside JLC | `C6 Fan, vents, thermal` (0.18) |
| D-29 | 2026-09-14 | Credo evidence: one real cable in hand, no vendor documents | — |
| D-30 | 2026-09-14 | MINI: remaining open items take the coordinator's recommendations; provisional decisions confirmed | `kickoff-questionnaire.md — every owner decision a board and ` (0.24) |
| D-31 | 2026-09-15 | MINI case v3: two-part, single-material, supportless; colour as a print-time option | — |
| D-32 | 2026-09-15 | MINI case: 13.4 mm finger dish (one-span D-12 bridge exception) + short switch names | `B7 Test points and self-documenting silk` (0.19) |
| D-33 | 2026-09-15 | MINI case fastening: heat-set (hot press-fit) M3 inserts + standard screws | `A2 Quantity and horizon` (0.15) |
| D-34 | 2026-09-15 | MINI case: print supports allowed → two-piece case (tray + one top shell) | `C1 Pieces` (0.21) |
| D-35 | 2026-09-16 | MINI routing closure: board size may increase slightly if it helps; the case follows | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-37 | 2026-09-17 | After the D-36 simplification: stricter on waivers, strengthen the design | — |
| D-38 | 2026-09-18 | Blanket 'go with recommended' on every open recommendation at PAUSE POINT 4: CC-088 (a)–(k), coherence Q1–Q5, CC-086 (a) | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-39 | 2026-09-19 | MINI_ORDER §2.7 stock gate stays at ≥ 5 000 (or the alternate) for C27882 / C11133 | — |
| D-40 | 2026-09-19 | Fix the D-22 run-3 review findings (CC-095 MINOR list) — round 6d authorised, in parallel with the JLC quote pass | — |
| D-41 | 2026-09-19 | Extensive, parallelised double-blind reviews of the round-6 design with the best external models via the Cursor `agent`  | — |
| D-42 | 2026-09-20 | Owner answers to the post-review items | — |
| D-43 | 2026-09-20 | After every change/re-route round: full verification gauntlet before the order — double-blind reviews, deep visual inspe | `F2 Stock policy and alternates` (0.1) |
| D-44 | 2026-09-20 | Two case tracks: keep the local single-colour FDM case (v3.6.x) for own printing/assembly; **complete re-design and re-e | `kickoff-questionnaire.md — every owner decision a board and ` (0.1) |
| D-45 | 2026-09-20 | Removable top portion over the QSFP-DD heat sink (both case tracks) + secondary logos so branding survives with the hood | `I. Identity, envelope, delegation (added by the first retro ` (0.15) |
| D-46 | 2026-09-20 | JLC-manufactured case: ultra-premium look, feel and material | — |
| D-47 | 2026-09-20 | JLCDFM: every danger AND warning on the board of record is to be fixed, and our own DRC/checks must catch them | — |
| D-48 | 2026-09-20 | Local FDM case: coloured marks only on top-facing (Z-up) surfaces printed in the same top layers as the legends; no colo | `C9 Brand marks / logos on FDM parts` (0.1) |
| D-49 | 2026-09-20 | Case: CC-120 A+B (full-height tray dovetail + matching body rail), CC-113 v3.7 snap-hood consequences accepted, CC-115 ( | `I. Identity, envelope, delegation (added by the first retro ` (0.12) |
| D-50 | 2026-09-20 | (1) Free FEA as a generated case-pipeline stage; (2) generated clear-to-build reports for the PCB and the case | `What the answers write` (0.14) |
| D-51 | 2026-09-21 | Final product uses the Amphenol-provided connector/cage data (Amphenol_data/): connector **V36-ADZ01-301100T** (ExtremeP | `I. Identity, envelope, delegation (added by the first retro ` (0.05) |
| D-52 | 2026-09-21 | Software track for test/validation and production deployment: an ENGINEERING / R&D mode (low-level, detailed options) an | `A0 Project scope` (0.08) |
| D-53 | 2026-09-21 | (1) Cage part number confirmed: **UE36-C16211-05A3A** = the 6.5 mm fin-pin heat-sink model (single light pipe, EMI sprin | `H4 The feedback loop into the skill` (0.07) |
| D-54 | 2026-09-21 | Power budget: research how to raise it (MINI and/or the full tester); the MINI must support ALL standalone cable tests ( | — |
| D-55 | 2026-09-21 | End-of-project deliverable set = the **production cut**: detailed product manual, user manual for developers, user manua | `H2 Production cut` (0.08) |
| D-56 | 2026-09-21 | Post-release: if the project is worth it, GitHub workflows (CI) so people can clone, prompt (AI-agent-driven) and update | `What the answers write` (0.12) |
| D-57 | 2026-09-21 | Post-release activity: build a reusable SKILL that captures every learning and process of this project (electrical, mech | `What the answers write` (0.07) |
| D-58 | 2026-09-21 | Connector J401 = **Amphenol V36-ADZ01-301000T** (45° contact lead-in), JLC **C22416096**, instead of the owner-supplied  | `F1 Acceptable verification sources` (0.08) |
| D-59 | 2026-09-21 | Every FEA/simulation report leads with pictures: colour-mapped 3D renderings (heat maps, deformed shapes, stress fields) | — |
| D-60 | 2026-09-21 | Morning answers: CC-136 (a) light pipe not fitted; CC-130/CC-140 no software refusal — software warns/throttles from the | `I. Identity, envelope, delegation (added by the first retro ` (0.07) |
| D-61 | 2026-09-21 | Blanket approval of the recommended answers in `docs/archive/OWNER_DETAILS_2026-09-21.md` §B–§E where low-risk; J401 sto | `F2 Stock policy and alternates` (0.19) |
| D-62 | 2026-09-21 | Renderings are part of the collected release/production-cut data (amends D-50 / D-55 / D-59) | — |
| D-65 | 2026-09-21 | First-pass case build at JLC3DP/JLCCNC; two-tone by parts: (1) legend / mark INLAY PLATES (SLA white, e.g. LEDO 6060 / 9 | `I. Identity, envelope, delegation (added by the first retro ` (0.19) |
| D-66 | 2026-09-21 | Release cut before the order: converge → final case checks → final cleanup + docs + reports → git tag → owner places the | `E2 Visual inspections` (0.2) |
| D-67 | 2026-09-22 | Production-cut phase pulled forward: run the D-55 / D-56 / D-57 plan now (docs/production/PRODUCTION_CUT_PLAN.md) plus t | `A2 Quantity and horizon` (0.13) |
| D-68 | 2026-09-22 | CC-183 option (A): lid START triangle for MODSEL aligned to L (`ui.start.SW302: L`) | `C1 Pieces` (0.2) |
| D-69 | 2026-09-22 | JLC board order PLACED for rev 0: board ed9431d7 / package out/MINI/fab/2026-09-22_ed9431d7 — PCB 5 panels (70 × 136, 1  | — |
| D-70 | 2026-09-22 | Repo re-organisation at the order: remove superseded case and PCB versions from the working tree (git history + tags kee | `C8 Two print targets and their fits` (0.11) |
| D-71 | 2026-09-22 | JLC case orders PLACED for rev 0 (case v3.13, tag mini-rev0-production-cut.1): JLC3DP — tray / shell / hood MJF PA12-HP  | `B4 Finish, mask colour, silk` (0.1) |
| D-72 | 2026-09-22 | D-70 phase 2 with the recommended answers ((a) docs/design kept, (b) early-era out/ dirs deleted except plan_smoke, (c)  | `I. Identity, envelope, delegation (added by the first retro ` (0.09) |

## 8. What to do with this report

1. Fold every NEW row into the reference named in §5 (one generalised line; the source's number stays as the labelled worked example).
2. Extend the PARTIAL sections where the mechanism is missing.
3. Add one eval per §6 stub; run the smoke; bump SKILL.md `version`; write the CHANGELOG entry from §4.
4. Add a questionnaire question (with a recommended answer) per §7 topic that will recur.
5. Blind-review the skill again (two lenses), then tag.
