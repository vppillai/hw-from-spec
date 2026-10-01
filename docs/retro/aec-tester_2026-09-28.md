# Retro — aec-tester → hw-from-spec (2026-09-28)

Project `aec-tester`: 48 dated learnings, 292 decision rows (86 owner rows). Skill `hw-from-spec` at SKILL.md version **0.4.1**; the project recorded skill version **none (add `skill: {version: …}` to project.yaml)**.
Classifier: keyword overlap against 196 sections (threshold 0.5); a human folds the candidates — this report is the input to the next CHANGELOG entry, not the entry itself.

## 1. Counts

| CARRIED | PARTIAL | NEW | NEW and costly (a round, an order, a wrong result) |
|---|---|---|---|
| 31 | 14 | 3 | 1 |

## 2. NEW — learnings the skill does not carry yet

| Date | Domain | Learning | Best section (coverage) | Costly |
|---|---|---|---|---|
| 2026-09-28 | tooling/slicer | A generator that refuses to overwrite its artefact of record on a failed run is right - and every analysis you then run on 'the 3MF' runs on the OLD file. Two hours of support-outside forensics on the p2s body chased a g… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.23) | yes |
| 2026-09-28 | parts/magnets | Hobby-standard neodymium discs (Ø6 x 3, Ø4 x 2) exist only in N35..N52 (80 °C) at the vendors whose pages render without a login (supermagnete, first4magnets, K&J, AMF); the SH grades start at 2 x 2 / 4 x 4 (first4magnet… | `references/dfm-printed-enclosure.md` › 1.1 Retention hardware: inserts, screws, magnets — (0.21) |  |
| 2026-09-28 | tooling/records | A `\|` inside a DECISIONS cell (`<jlc\|p2s>`) is a seventh column: `gen/known_issues.py --check` caught it the moment it ran. Write `<jlc or p2s>`, and run the check before committing a record edit. | `references/release-and-cut.md` › 3.1 The one-round record chain (production cut) an (0.14) |  |

## 3. PARTIAL — carried in part (check the section, extend it if the mechanism is missing)

| Date | Domain | Learning | Best section (coverage) |
|---|---|---|---|
| 2026-09-27 | process/ci | First Linux run of a macOS-authored gate set: twelve parity fixes, none a design change. Checklist for the skill: `$GITHUB_ENV` takes KEY=value only; the KiCad image has no `make`;… | `references/pitfalls.md` › agents / git (0.44) |
| 2026-09-27 | mesh/glb | A KiCad GLB export is not a set of solids but thousands of face groups per footprint (31 790 for this board), so any "component inside a box" rule written for STL connected compone… | `references/pitfalls.md` › mechanical / case (0.44) |
| 2026-09-27 | process/coupon-first | Print 15-25 min test coupons (text strokes x caps in the real font, wall thicknesses, dovetail clearances) BEFORE the part, generated from the SAME yaml numbers and SCAD modules as… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.49) |
| 2026-09-27 | tooling/bambu | Bambu Studio 02.08's CLI builds a complete project (`--export-3mf <bare name>` lands in `--outputdir`; an absolute path fails with rc -13) and slices it headless (`--slice 0`, resu… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.42) |
| 2026-09-27 | generator/byte-identity | Adding a print-target variant to a generator whose default output is keyed by md5 (production cut, marketing pack): put every variant-only line behind hook tokens that expand to th… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.49) |
| 2026-09-28 | dfm/mjf | The census on the v3.16 bodies found five more sub-gate walls no row had ever measured: the flank lock-up mark reached 2.7 mm into the 1.2 mm skirt band (0.4 skins under its 0.8 de… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.37) |
| 2026-09-28 | tooling/openscad | OpenSCAD 2021.01 writes the same CGAL geometry in a different triangle order on every export - three exports of one tray gave three md5s (cc7bb69f / 9c01b0ba / e8a57086). An STL md… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.33) |
| 2026-09-28 | dfm/vendor-map | JLC3DP flagged the r3 tray (379893c9, binary canonical STL) with a RED hairline along both inner wall feet while the r2 tray (5dddeb10, OpenSCAD ASCII) had passed - and a `trimesh`… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.31) |
| 2026-09-28 | process/warnings | A check table that ends with "0 FAIL, 81 WARN" tells the owner nothing - every WARN was either a real threshold (then it is PASS or FAIL) or a number with no threshold (then it is … | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.5) |
| 2026-09-28 | records | A parts task caught count drift: the jlc preset says five feet, the assembly guide / MINI_ORDER / p2s say four. Flag count disagreements in the decision row instead of picking one … | `references/pitfalls.md` › sourcing (0.32) |
| 2026-09-28 | dfm/geometry | The tray's long-wall build (2.0 wall, 1.25 rim ring overhanging the wall inner face by 0.9, lap recess 1.65 from outside) read RED at JLC while three independent ray-cast metrics (… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.45) |
| 2026-09-28 | tooling/cache | `ScadCache.key()` hashed the absolute SCAD path, so every `--check` that relies on the sidecar (coupons, dummy) read STALE on CI (checkout under /__w/...) and on any clone - the PR… | `references/pitfalls.md` › tooling / determinism (0.36) |
| 2026-09-28 | tooling/openscad | A SCAD hook that references a variable the preset never defines expands to NOTHING - no error, no warning in the build log we read, an export with the feature simply missing. The j… | `references/dfm-printed-enclosure.md` › 9. Two versions from one yaml (vendor MJF + home F (0.31) |
| 2026-09-28 | dfm/mjf/polarity | A debossed polarity dot beside a Ø6.4 pocket in a Ø10 boss leaves 0.25 mm lands - JLC yellow - and a raised dot in the 0.3 mm lap gap collides. The honest keying is an asymmetric b… | `references/dfm-printed-enclosure.md` › 1.1 Retention hardware: inserts, screws, magnets — (0.48) |

## 4. CHANGELOG entry draft

### Added (from aec-tester, learnings 2026-09-27 … 2026-09-28)
- **`references/dfm-printed-enclosure.md`**: A generator that refuses to overwrite its artefact of record on a failed run is right - and every analysis you then run on 'the 3MF' runs on; Hobby-standard neodymium discs (Ø6 x 3, Ø4 x 2) exist only in N35..N52 (80 °C) at the vendors whose pages render without a login (supermagne
- **`references/release-and-cut.md`**: A `|` inside a DECISIONS cell (`<jlc|p2s>`) is a seventh column: `gen/known_issues.py --check` caught it the moment it ran. Write `<jlc or p

### Changed
- (sections the PARTIAL entries extend: `references/dfm-printed-enclosure.md`, `references/pitfalls.md`)

## 5. Reference patch stubs (bullets to append; generalise the numbers, label the worked example, keep the evidence pointer at the end)

### references/dfm-printed-enclosure.md
- 2026-09-28 [tooling/slicer] A generator that refuses to overwrite its artefact of record on a failed run is right - and every analysis you then run on 'the 3MF' runs on the OLD file. Two hours of support-outside forensics on the p2s body chased a groove ceiling that no longer existed, because the failed slices had never replaced the 3MF on disk while the sidecar JSON described the new one. Keep the rejected output under another name (`*.FAILED.3mf`) and analyse THAT; better, make the checker print which input md5 it measured.
- 2026-09-28 [parts/magnets] Hobby-standard neodymium discs (Ø6 x 3, Ø4 x 2) exist only in N35..N52 (80 °C) at the vendors whose pages render without a login (supermagnete, first4magnets, K&J, AMF); the SH grades start at 2 x 2 / 4 x 4 (first4magnets) or 1/4 x 1/8 in (K&J D42SH). Decide the size first, then the grade - and read the temperature limit against the FEA rows, not against the 'high temp' wish. Magnet-to-magnet touching force is ~1.6x the pull-to-steel a vendor prints (K&J publishes both: D42 1.04 / 1.68 kgf); derate for the gap with (Bz(gap/2)/Bz(0))^2 on the axial field of the cylinder - and label it an estimate with a first-article pull test.

### references/release-and-cut.md
- 2026-09-28 [tooling/records] A `|` inside a DECISIONS cell (`<jlc|p2s>`) is a seventh column: `gen/known_issues.py --check` caught it the moment it ran. Write `<jlc or p2s>`, and run the check before committing a record edit.

## 6. Eval stubs — one per NEW learning that cost a round (fill prompt / assertions from the entry; add to evals/evals.json)

```json
{"id": "R1", "name": "a-generator-that-refuses-to-overwrite-its-artefact-of-record", "prompt": "A project hits this situation: A generator that refuses to overwrite its artefact of record on a failed run is . Handle it.", "expected_output": "A generator that refuses to overwrite its artefact of record on a failed run is right - and every analysis you then run on 'the 3MF' runs on the OLD file. Two hours of support-outside forensics on the p2s body chased a groove ceiling that no longer existed, because the failed slices had never replaced the 3MF on disk while the sidecar JSON described the new one. Keep the rejected output under anot", "assertions": ["the agent applies: A generator that refuses to overwrite its artefact of record on a failed run is right - and every analysis you then run on 'the 3MF' runs on the OLD file. Two hours of support-outside forensics on the", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
```

## 7. Owner decision topics the kickoff questionnaire does not ask yet (candidates for a new question with a recommended answer)

| Row | Date | Topic | Best question section (coverage) |
|---|---|---|---|
| D-04 | 2026-09-13 | AEC-CT2-MINI form factor: **cage-sized stick** | — |
| D-05 | 2026-09-13 | Enclosure is a design input for the MINI stick — dimensions and clearances | — |
| D-06 | 2026-09-13 | MINI silk screen: self-documenting labels; no silk over pads | — |
| D-10 | 2026-09-13 | Final thorough review after design + implementation | — |
| D-11 | 2026-09-13 | Reviewer hand-off document for external deep reviews | — |
| D-13 | 2026-09-13 | USB-C receptacle: clearances and mechanical reinforcement for many insertions | — |
| D-14 | 2026-09-13 | Case: latch two MINI units together into a two-end cable jig | `A2 Quantity and horizon` (0.16) |
| D-09a | 2026-09-13 | Premium aesthetics and a thought-through user experience apply to the MAIN board too | `kickoff-questionnaire.md — every owner decision a board + en` (0.16) |
| D-16 | 2026-09-13 | External FTDI/pod path = backup debug path, not a mode of operation; pluggable, compact, case need not expose it | `I. Identity, envelope, delegation (added by the first retro ` (0.14) |
| D-18 | 2026-09-13 | EXT/LA connectors and EXT pinout: CC-057 set with the 1.27 mm LA pair; CC-056 Total Phase order | `B3 Controlled impedance` (0.13) |
| D-20 | 2026-09-13 | MINI stick dimensions are secondary: grow the board as required to route cleanly; functionality, electrical and signal i | `B1 Layers and thickness` (0.08) |
| D-22 | 2026-09-13 | Deep layer-by-layer, trace-by-trace visual inspection of the routing after final routing | `F2 Stock policy and alternates` (0.21) |
| D-24 | 2026-09-14 | MINI printed case: two-tone, per-colour AMS printing, assembly-friendly for 50+ units | `A2 Quantity and horizon` (0.16) |
| D-25 | 2026-09-14 | Product name: AEC-CT2 = AEC Cable Tester 2 | — |
| D-26 | 2026-09-14 | MINI USB-C receptacles: CC-052 option B (mid-mount XYECONN C20883026) | — |
| D-27 | 2026-09-14 | Fan: none fitted, provision kept for a specific part sourced outside JLC | `C6 Fan, vents, thermal` (0.16) |
| D-29 | 2026-09-14 | Credo evidence: one real cable in hand, no vendor documents | — |
| D-30 | 2026-09-14 | MINI: remaining open items take the coordinator's recommendations; provisional decisions confirmed | `kickoff-questionnaire.md — every owner decision a board + en` (0.24) |
| D-31 | 2026-09-15 | MINI case v3: two-part, single-material, supportless; colour as a print-time option | — |
| D-32 | 2026-09-15 | MINI case: 13.4 mm finger dish (one-span D-12 bridge exception) + short switch names | `B7 Test points and self-documenting silk` (0.17) |
| D-33 | 2026-09-15 | MINI case fastening: heat-set (hot press-fit) M3 inserts + standard screws | `A2 Quantity and horizon` (0.12) |
| D-34 | 2026-09-15 | MINI case: print supports allowed → two-piece case (tray + one top shell) | `C1 Pieces` (0.18) |
| D-37 | 2026-09-17 | After the D-36 simplification: stricter on waivers, strengthen the design | — |
| D-38 | 2026-09-18 | Blanket 'go with recommended' on every open recommendation at PAUSE POINT 4: CC-088 (a)–(k), coherence Q1–Q5, CC-086 (a) | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-39 | 2026-09-19 | MINI_ORDER §2.7 stock gate stays at ≥ 5 000 (or the alternate) for C27882 / C11133 | — |
| D-40 | 2026-09-19 | Fix the D-22 run-3 review findings (CC-095 MINOR list) — round 6d authorised, in parallel with the JLC quote pass | — |
| D-41 | 2026-09-19 | Extensive, parallelised double-blind reviews of the round-6 design with the best external models via the Cursor `agent`  | `E1 Review rounds per gate` (0.14) |
| D-42 | 2026-09-20 | Owner answers to the post-review items | — |
| D-43 | 2026-09-20 | After every change/re-route round: full verification gauntlet before the order — double-blind reviews, deep visual inspe | `F2 Stock policy and alternates` (0.11) |
| D-44 | 2026-09-20 | Two case tracks: keep the local single-colour FDM case (v3.6.x) for own printing/assembly; **complete re-design and re-e | `kickoff-questionnaire.md — every owner decision a board + en` (0.1) |
| D-45 | 2026-09-20 | Removable top portion over the QSFP-DD heat sink (both case tracks) + secondary logos so branding survives with the hood | `I. Identity, envelope, delegation (added by the first retro ` (0.11) |
| D-47 | 2026-09-20 | JLCDFM: every danger AND warning on the board of record is to be fixed, and our own DRC/checks must catch them | — |
| D-48 | 2026-09-20 | Local FDM case: coloured marks only on top-facing (Z-up) surfaces printed in the same top layers as the legends; no colo | `B7 Test points and self-documenting silk` (0.09) |
| D-49 | 2026-09-20 | Case: CC-120 A+B (full-height tray dovetail + matching body rail), CC-113 v3.7 snap-hood consequences accepted, CC-115 ( | `I. Identity, envelope, delegation (added by the first retro ` (0.13) |
| D-50 | 2026-09-20 | (1) Free FEA as a generated case-pipeline stage; (2) generated clear-to-build reports for the PCB and the case | `0. Batches (ask in this order; one AskUserQuestion call per ` (0.15) |
| D-51 | 2026-09-21 | Final product uses the Amphenol-provided connector/cage data (Amphenol_data/): connector **V36-ADZ01-301100T** (ExtremeP | `I. Identity, envelope, delegation (added by the first retro ` (0.04) |
| D-52 | 2026-09-21 | Software track for test/validation and production deployment: an ENGINEERING / R&D mode (low-level, detailed options) an | — |
| D-53 | 2026-09-21 | (1) Cage part number confirmed: **UE36-C16211-05A3A** = the 6.5 mm fin-pin heat-sink model (single light pipe, EMI sprin | `H4 The feedback loop into the skill` (0.06) |
| D-54 | 2026-09-21 | Power budget: research how to raise it (MINI and/or the full tester); the MINI must support ALL standalone cable tests ( | — |
| D-55 | 2026-09-21 | End-of-project deliverable set = the **production cut**: detailed product manual, user manual for developers, user manua | `H2 Production cut` (0.08) |
| D-56 | 2026-09-21 | Post-release: if the project is worth it, GitHub workflows (CI) so people can clone, prompt (AI-agent-driven) and update | `What the answers write` (0.12) |
| D-57 | 2026-09-21 | Post-release activity: build a reusable SKILL that captures every learning and process of this project (electrical, mech | `What the answers write` (0.07) |
| D-58 | 2026-09-21 | Connector J401 = **Amphenol V36-ADZ01-301000T** (45° contact lead-in), JLC **C22416096**, instead of the owner-supplied  | `F1 Acceptable verification sources` (0.07) |
| D-59 | 2026-09-21 | Every FEA/simulation report leads with pictures: colour-mapped 3D renderings (heat maps, deformed shapes, stress fields) | — |
| D-60 | 2026-09-21 | Morning answers: CC-136 (a) light pipe not fitted; CC-130/CC-140 no software refusal — software warns/throttles from the | `I. Identity, envelope, delegation (added by the first retro ` (0.07) |
| D-61 | 2026-09-21 | Blanket approval of the recommended answers in `docs/archive/OWNER_DETAILS_2026-09-21.md` §B–§E where low-risk; J401 sto | `F2 Stock policy and alternates` (0.18) |
| D-62 | 2026-09-21 | Renderings are part of the collected release/production-cut data (amends D-50 / D-55 / D-59) | — |
| D-65 | 2026-09-21 | First-pass case build at JLC3DP/JLCCNC; two-tone by parts: (1) legend / mark INLAY PLATES (SLA white, e.g. LEDO 6060 / 9 | `I. Identity, envelope, delegation (added by the first retro ` (0.18) |
| D-66 | 2026-09-21 | Release cut before the order: converge → final case checks → final cleanup + docs + reports → git tag → owner places the | `E2 Visual inspections` (0.2) |
| D-67 | 2026-09-22 | Production-cut phase pulled forward: run the D-55 / D-56 / D-57 plan now (docs/production/PRODUCTION_CUT_PLAN.md) plus t | `A2 Quantity and horizon` (0.13) |
| D-68 | 2026-09-22 | CC-183 option (A): lid START triangle for MODSEL aligned to L (`ui.start.SW302: L`) | `C1 Pieces` (0.2) |
| D-69 | 2026-09-22 | JLC board order PLACED for rev 0: board ed9431d7 / package out/MINI/fab/2026-09-22_ed9431d7 — PCB 5 panels (70 × 136, 1  | — |
| D-70 | 2026-09-22 | Repo re-organisation at the order: remove superseded case and PCB versions from the working tree (git history + tags kee | `C8 Two print targets and their fits` (0.11) |
| D-71 | 2026-09-22 | JLC case orders PLACED for rev 0 (case v3.13, tag mini-rev0-production-cut.1): JLC3DP — tray / shell / hood MJF PA12-HP  | `B4 Finish, mask colour, silk` (0.1) |
| D-72 | 2026-09-22 | D-70 phase 2 with the recommended answers ((a) docs/design kept, (b) early-era out/ dirs deleted except plan_smoke, (c)  | `I. Identity, envelope, delegation (added by the first retro ` (0.09) |
| D-73 | 2026-09-22 | Archive folders become deletions: superseded material leaves the working tree entirely; git history and the tags (mini-r | `E3 Coupons, dummies, first article` (0.14) |
| D-64 | 2026-09-21 | All (!) items of CC-143 / CC-148 / CC-157 / CC-166 nodded as recommended; each accepted deviation becomes a rev-1 backlo | `C7 Light pipes / windows / switch access` (0.25) |
| D-01 | 2026-09-13 | Firmware-controlled source selection, bus bridge, LED quiet | — |
| D-02 | 2026-09-13 | QSFP-DD connector and cage fixed to the Blackhole Galaxy UBB parts | — |
| D-03 | 2026-09-13 | AEC-CT2-MINI — the footprint coupon becomes a single-port FT2232H bench dongle | — |

## 8. What to do with this report

1. Fold every NEW row into the reference named in §5 (one generalised line; the source's number stays as the labelled worked example).
2. Extend the PARTIAL sections where the mechanism is missing.
3. Add one eval per §6 stub; run the smoke; bump SKILL.md `version`; write the CHANGELOG entry from §4.
4. Add a questionnaire question (with a recommended answer) per §7 topic that will recur.
5. Blind-review the skill again (two lenses), then tag.
