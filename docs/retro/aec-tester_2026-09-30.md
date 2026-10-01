# Retro — aec-tester → hw-from-spec (2026-09-30)

Project `aec-tester`: 41 dated learnings, 306 decision rows (89 owner rows). Skill `hw-from-spec` at SKILL.md version **0.9.2**; the project recorded skill version **none (add `skill: {version: …}` to project.yaml)**.
Classifier: keyword overlap against 217 sections (threshold 0.5); a human folds the candidates — this report is the input to the next CHANGELOG entry, not the entry itself (`--apply` does the mechanical folds: pitfalls lines, NEW process rows, a CHANGELOG stub).

## 1. Counts

| CARRIED | PARTIAL | NEW | NEW and costly (a round, an order, a wrong result) |
|---|---|---|---|
| 12 | 17 | 12 | 4 |

## 2. NEW — learnings the skill does not carry yet

| Date | Domain | Learning | Best section (coverage) | Costly |
|---|---|---|---|---|
| 2026-09-30 | tooling/bambu | Per-object print settings DO work headless: write them as Bambu object-level `<metadata key="..." value="..."/>` entries under `<object>` in Metadata/model_settings.config of a generic 3MF - the CLI applies supports, iro… | `references/dfm-printed-enclosure.md` › 8.3 Bambu Studio CLI facts (02.08.x, 2026-09-29 —  (0.15) | yes |
| 2026-09-30 | tooling/bambu/proof | A "did my setting land" proof must be spatial and comparative: per-object footprints from the exported plate json, feature points (Ironing / Support) inside them, and the layer-1 outer-wall CONTOUR compared with the same… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.21) |  |
| 2026-09-30 | mechanical/msa/safety | A dust cap cannot damage a QSFP-DD plug if it only ever meets the smooth 18.35 x 8.5 shell: the paddle card is recessed >= 2.2 behind the leading edge and sits 1.7 / ~5.8 inside the shell planes, and the first latch feat… | `references/pitfalls.md` › mechanical / case (0.1) |  |
| 2026-09-30 | materials/esd | "ESD-safe" on a filament page is not a class: the CNT-loaded flexible grades with datasheets (3DXTech ESD-TPU 60D 10^3 Ω/sq IEC 62631-3-2, Essentium TPU 74D-Z 8E2..5E7 Ω) are CONDUCTIVE, not dissipative, and the rigid CN… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.07) |  |
| 2026-09-30 | sources/fetch | Vendor TDS PDFs on Shopify / bblcdn CDNs fetch fine with curl + a browser UA and read with `pdftotext -layout`; WebFetch returns binary garbage for them. Bambu's bambulab.com and wiki refuse automated reads (403 / 402) b… | `references/part-verification.md` › Bought hardware (feet, screws, inserts, labels) —  (0.16) |  |
| 2026-09-30 | review/verification | Blind reviewers re-find decided items at a 1:1 ratio (H-A: 16 of 27 were on record, H-B: 4 of 28) — the merge is cheap when every decision row names the netlist fact it rests on; the two findings that mattered (slide end… | `references/pcb-layout-dfm.md` › 15. Route-quality classes **[convention + owner ch (0.09) | yes |
| 2026-09-30 | jlc/order | JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are not guaranteed to raise a dialog or mail — the order went Reviewed → In Production in 14 h with neither step ever offered (ORDER_STATUS 2026-… | `references/pitfalls.md` › process / gates (0.08) | yes |
| 2026-09-30 | mechanical/verification | A footprint's 3D model can sit off its pads and nobody notices until a blind reviewer measures the exported mesh: the XYECONN USB-C STEP is 1.07 mm inboard of the pad-derived face, the pad-by-pad check (USB-C_receptacle.… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.18) | yes |
| 2026-09-30 | review/verification | Blind mechanical reviews re-find decided items at ~1:2 (10 of 23 were owner decisions whose numbers still hold, 2 refuted); the two that mattered (open-ended plate strip, magnet discs pulled toward their open pockets) we… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.24) |  |
| 2026-09-30 | mech/CSG | Two 'robust CSG' habits made the two p2s shell slivers: a cutter overshoot (+1 above the trough floor) that is air inside the channel but a 0.2 mm skin where the hole runs under a wall, and a fill clipped 0.01 short of t… | `references/dfm-printed-enclosure.md` › 1. MJF rules (worked example: JLC3DP PA12-HP; chec (0.11) |  |
| 2026-09-30 | process | One-liner coordinator rules land as generator features, not as hand edits: 'coupons are self-documenting' became a yaml marker block + a shared TextMeter.lands gate + legend boxes carried through the auto-orientation tra… | `SKILL.md` › 8.1 DFM for printed enclosures [mech, both] (befor (0.23) |  |
| 2026-09-30 | sw/selftest | A fake that NACKs for 50 ms after EVERY write breaks read_id before the code under test is reached; model the hold-off from the write you want to test (a hook on 13h:171) and make a 'module pulled' fake NACK from the 3rd… | `references/pitfalls.md` › mechanical / case (0.08) |  |

## 3. PARTIAL — carried in part (check the section, extend it if the mechanism is missing)

| Date | Domain | Learning | Best section (coverage) |
|---|---|---|---|
| 2026-09-30 | process/records | ASSEMBLY / QA prose must be generated from the preset like the geometry: the p2s ASSEMBLY.md still said "0 magnets, Material: PETG, the two snap tabs click" three fastener changes … | `references/print-kit.md` › 3. Kit text gate (a FAIL row over every emitted ki (0.47) |
| 2026-09-30 | fdm/test-markers | Test-print identifiers belong on an IRONED TOP face, debossed 3 layers in the legend font of record (Inter Bold cap 4, faux-bold to a 1.0 stroke) - never on a bridge underside (a b… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.31) |
| 2026-09-30 | tooling/bambu | A per-plate `material:` is a pure profile swap: flatten that filament's profile into the run dir, hand it to the CLI instead of the kit default, record it in the sidecar and compar… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.27) |
| 2026-09-30 | dfm/metric | A thickness measured along the surface normal cannot see a ROOT: a rim ring 0.9 inboard of its wall over a lap step read >= 1.37 along every ray while it stood on a 0.5 mm overlap … | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.33) |
| 2026-09-30 | dfm/vendor-map | JLC3DP's heat map colours WHOLE triangles by the thinnest reading on them: the K0 probe's inner wall face is red floor-to-ledge (2.6 mm tall, 147 long) from a 0.5 mm root at its to… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.31) |
| 2026-09-30 | dfm/process | Owner: "this need not be tuned to jlc, just that that is where we saw good results." A check built to reproduce one vendor's verdicts is a classifier with no physics in it (the fir… | `references/pitfalls.md` › documentation (0.42) |
| 2026-09-30 | dfm/sources | Design-guide pages move: HP's MJF design guidelines, Formlabs' design specs and the Bambu wiki all returned 404 / 402 this session; JLC3DP MJF, Protolabs MJF (page + design tip), X… | `references/pitfalls.md` › documentation (0.33) |
| 2026-09-30 | tooling/openscad/generator | A mid-line `//` in GENERATED SCAD silently drops every statement after it on that line - the v3.16 emitter put `mark_web_clip = 4; mark_pinch = [...]` behind a comment and the SLA … | `references/pitfalls.md` › documentation (0.36) |
| 2026-09-30 | fdm/legends | Debossed text at the legend cap can fail the one-line land rule BETWEEN glyphs, not inside them: Inter Bold's default advance leaves 0.21..0.34 mm between W\|1, 6\|. and R\|0 at cap 4… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.32) |
| 2026-09-30 | dfm/tooling/selftest | `gen/print_dfm.py` carried a dead measure for a day: the census ray's origin was nudged OUTSIDE the surface, every ray hit its own face and read inf, and nobody noticed because `t … | `references/pitfalls.md` › documentation (0.41) |
| 2026-09-30 | governance/gates | A DECISIONS row with a missing cell (CC-215 had 5 of 6) breaks `gen/known_issues.py --check` for everyone after it; the row writer should count pipes before committing (a one-line … | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.29) |
| 2026-09-30 | mechanical/review | 'Intended' is not a verdict: CC-211 recorded the legend plate's 1.35 mm web as 'the plate wrapping the dish opening … intended' because it met the rib rule; a ray in X at a dozen Y… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.29) |
| 2026-09-30 | dfm/rules | A sliver exemption needs an ASPECT test, not an area floor alone: a 5 mm2 floor silenced a Ø0.4 x 3.5 pin (4.4 mm2) and a Ø0.3 x 2.9 pin (2.7 mm2) that no powder process forms. A t… | `references/pitfalls.md` › documentation (0.43) |
| 2026-09-30 | dfm/validation | A validation set must be deduped by GEOMETRY before any agreement is counted: OpenSCAD writes the same CGAL solid in a different triangle order (and ASCII twins) on every export, s… | `references/print-dfm.md` › 4. Validation on record (worked example: 42 labell (0.45) |
| 2026-09-30 | kit/fdm | Two filaments on one Bambu plate are NOT "two colours without an AMS swap": every layer that holds both colours is a filament change (plus a prime tower the embedded profile switch… | `references/dfm-printed-enclosure.md` › 8.3 Bambu Studio CLI facts (02.08.x, 2026-09-29 —  (0.34) |
| 2026-09-30 | mech/caps | A wall preset that shrinks a face invalidates every [S] gate tuned on the old face: the slim cap's 12.00 face took the auto-fitted mark to 8.9 and the inner-V island under 2.5 - th… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.25) |
| 2026-09-30 | tools/dfm | OpenSCAD re-exports byte-different STLs with identical geometry (facet order); a records chain keyed on md5 then re-slices unchanged parts. Prove 'identical' with faces / volume / … | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.32) |

## 4. CHANGELOG entry draft

### Added (from aec-tester, learnings 2026-09-30 … 2026-09-30)
- **`references/dfm-printed-enclosure.md`**: Per-object print settings DO work headless: write them as Bambu object-level `<metadata key="..." value="..."/>` entries under `<object>` in; A "did my setting land" proof must be spatial and comparative: per-object footprints from the exported plate json, feature points (Ironing /; Two 'robust CSG' habits made the two p2s shell slivers: a cutter overshoot (+1 above the trough floor) that is air inside the channel but a 
- **`references/part-verification.md`**: Vendor TDS PDFs on Shopify / bblcdn CDNs fetch fine with curl + a browser UA and read with `pdftotext -layout`; WebFetch returns binary garb
- **`references/pcb-layout-dfm.md`**: Blind reviewers re-find decided items at a 1:1 ratio (H-A: 16 of 27 were on record, H-B: 4 of 28) — the merge is cheap when every decision r
- **`references/pitfalls.md`**: A dust cap cannot damage a QSFP-DD plug if it only ever meets the smooth 18.35 x 8.5 shell: the paddle card is recessed >= 2.2 behind the le; "ESD-safe" on a filament page is not a class: the CNT-loaded flexible grades with datasheets (3DXTech ESD-TPU 60D 10^3 Ω/sq IEC 62631-3-2, E; JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are not guaranteed to raise a dialog or mail — the order went Rev; A footprint's 3D model can sit off its pads and nobody notices until a blind reviewer measures the exported mesh: the XYECONN USB-C STEP is ; Blind mechanical reviews re-find decided items at ~1:2 (10 of 23 were owner decisions whose numbers still hold, 2 refuted); the two that mat; A fake that NACKs for 50 ms after EVERY write breaks read_id before the code under test is reached; model the hold-off from the write you wa
- **`references/release-and-cut.md`**: One-liner coordinator rules land as generator features, not as hand edits: 'coupons are self-documenting' became a yaml marker block + a sha

### Changed
- (sections the PARTIAL entries extend: `references/dfm-printed-enclosure.md`, `references/pitfalls.md`, `references/print-dfm.md`, `references/print-kit.md`)

## 5. Reference patch stubs (bullets to append; generalise the numbers, label the worked example, keep the evidence pointer at the end)

### references/dfm-printed-enclosure.md
- 2026-09-30 [tooling/bambu] Per-object print settings DO work headless: write them as Bambu object-level `<metadata key="..." value="..."/>` entries under `<object>` in Metadata/model_settings.config of a generic 3MF - the CLI applies supports, ironing, top shell, elephant-foot compensation and first-layer line width per object. What it does not do: keep your positions (a generic 3MF is arranged on load), and tagging the file `Application=BambuStudio-<ver>` to be treated as a project segfaults the CLI (rc -11). Read positions back from the exported plate_1.json and gate on those.
- 2026-09-30 [tooling/bambu/proof] A "did my setting land" proof must be spatial and comparative: per-object footprints from the exported plate json, feature points (Ironing / Support) inside them, and the layer-1 outer-wall CONTOUR compared with the same object sliced alone (orientation-agnostic - the arranger may rotate it 90 deg). A layer-1 vs layer-2 bbox growth cannot separate elephant-foot compensation from a sole round or a roof chamfer.
- 2026-09-30 [mech/CSG] Two 'robust CSG' habits made the two p2s shell slivers: a cutter overshoot (+1 above the trough floor) that is air inside the channel but a 0.2 mm skin where the hole runs under a wall, and a fill clipped 0.01 short of the solid it should merge into (0.04 mm triangle at the step-wall corner). Rule: an overshoot must only reach into AIR or into SOLID it is meant to remove; a fill must end INSIDE the neighbouring solid, never at its face. (D-89 / CC-217 (b))

### references/part-verification.md
- 2026-09-30 [sources/fetch] Vendor TDS PDFs on Shopify / bblcdn CDNs fetch fine with curl + a browser UA and read with `pdftotext -layout`; WebFetch returns binary garbage for them. Bambu's bambulab.com and wiki refuse automated reads (403 / 402) but the store pages and their store.bblcdn.com TDS links carry the same numbers plus the AMS "Cautions for Use" line — go to the store, not the wiki. A search hit named like a datasheet (farnell 1512999.pdf for "add:north ESD") was an antistatic-tape sheet: read the first line of every PDF before quoting it.

### references/pcb-layout-dfm.md
- 2026-09-30 [review/verification] Blind reviewers re-find decided items at a 1:1 ratio (H-A: 16 of 27 were on record, H-B: 4 of 28) — the merge is cheap when every decision row names the netlist fact it rests on; the two findings that mattered (slide end sense, diode polarity) were the ones whose *closure* was a bench step nobody had scheduled before the first module. Verify a reviewer's netlist claims yourself (`kicad-cli sch export netlist` + a 20-line parser) before accepting a 'not realised' verdict: here SPEC R-E03 said 'both boards' and the shared fragment never got the part.

### references/pitfalls.md
- 2026-09-30 [mechanical/msa/safety] A dust cap cannot damage a QSFP-DD plug if it only ever meets the smooth 18.35 x 8.5 shell: the paddle card is recessed >= 2.2 behind the leading edge and sits 1.7 / ~5.8 inside the shell planes, and the first latch feature is >= 33.2 behind the nose (MSA Fig. 42 / 63 / 64 / 78) - so a 17 mm cap with side ribs needs no relief. The real risks are elsewhere: PLA slivers from the ribs (45 deg lead-ins, capped interference, blow out before use), ESD (PLA insulates), heat (PLA softens at ~55 C) and people pulling the cable by the cap - all README items, not geometry.
- 2026-09-30 [materials/esd] "ESD-safe" on a filament page is not a class: the CNT-loaded flexible grades with datasheets (3DXTech ESD-TPU 60D 10^3 Ω/sq IEC 62631-3-2, Essentium TPU 74D-Z 8E2..5E7 Ω) are CONDUCTIVE, not dissipative, and the rigid CNT PETGs drift from 1.6E7 to <1E4 Ω as the nozzle goes 250 → 290 °C (Polymaker TDS table). Score ESD on the TDS surface-resistance row WITH its method and the print temperature it was measured at, treat "below the window" as a fail of a different kind (bridging), and lock the nozzle temperature in the plate profile when the window depends on it. Product pages contradict their own TDS (3DXTech page "10^4-10^9" vs TDS "10^7-10^9") — the TDS governs.
- 2026-09-30 [jlc/order] JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are not guaranteed to raise a dialog or mail — the order went Reviewed → In Production in 14 h with neither step ever offered (ORDER_STATUS 2026-09-25), so every order-checklist row that depends on them (MINI_ORDER 1.20 / 2.8 / 2.9) silently went unexecuted. Capture the bottom-side placement preview yourself before paying, and treat the 'Photo Confirmation' advanced option as the only human-in-the-loop polarity check for a bottom-side SOD-123.
- 2026-09-30 [mechanical/verification] A footprint's 3D model can sit off its pads and nobody notices until a blind reviewer measures the exported mesh: the XYECONN USB-C STEP is 1.07 mm inboard of the pad-derived face, the pad-by-pad check (USB-C_receptacle.md) never looked at the model, and the case interference scan inherited the error for two weeks. Once per connector: compare the model's mating face with the face the pads imply (drawing datum + pad position) — a one-line cadquery bbox against the footprint frame.
- 2026-09-30 [review/verification] Blind mechanical reviews re-find decided items at ~1:2 (10 of 23 were owner decisions whose numbers still hold, 2 refuted); the two that mattered (open-ended plate strip, magnet discs pulled toward their open pockets) were in geometry that had passed every census — the census measures thickness, not what a hand does to the part. Keep one 'what will a user break first' pass per print, hands on the mesh.
- 2026-09-30 [sw/selftest] A fake that NACKs for 50 ms after EVERY write breaks read_id before the code under test is reached; model the hold-off from the write you want to test (a hook on 13h:171) and make a 'module pulled' fake NACK from the 3rd poll ON, not only at the 3rd - the retry-until-ACK of SW-4 otherwise swallows the single NACK and the test is timing-dependent. (CC-216 SW-4 / SW-6)

### references/release-and-cut.md
- 2026-09-30 [process] One-liner coordinator rules land as generator features, not as hand edits: 'coupons are self-documenting' became a yaml marker block + a shared TextMeter.lands gate + legend boxes carried through the auto-orientation transform - and the test words had to be excluded from the marker spacing, or the coupon stops testing the case legend as drawn. (CC-219)

## 6. Eval stubs — one per NEW learning that cost a round (fill prompt / assertions from the entry; add to evals/evals.json)

```json
{"id": "R1", "name": "per", "prompt": "A project hits this situation: Per. Handle it.", "expected_output": "Per-object print settings DO work headless: write them as Bambu object-level `<metadata key=\"...\" value=\"...\"/>` entries under `<object>` in Metadata/model_settings.config of a generic 3MF - the CLI applies supports, ironing, top shell, elephant-foot compensation and first-layer line width per object. What it does not do: keep your positions (a generic 3MF is arranged on load), and tagging the fil", "assertions": ["the agent applies: Per-object print settings DO work headless: write them as Bambu object-level `<metadata key=\"...\" value=\"...\"/>` entries under `<object>` in Metadata/model_settings.config of a generic 3MF - the CLI a", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R2", "name": "blind-reviewers-re", "prompt": "A project hits this situation: Blind reviewers re. Handle it.", "expected_output": "Blind reviewers re-find decided items at a 1:1 ratio (H-A: 16 of 27 were on record, H-B: 4 of 28) — the merge is cheap when every decision row names the netlist fact it rests on; the two findings that mattered (slide end sense, diode polarity) were the ones whose *closure* was a bench step nobody had scheduled before the first module. Verify a reviewer's netlist claims yourself (`kicad-cli sch exp", "assertions": ["the agent applies: Blind reviewers re-find decided items at a 1:1 ratio (H-A: 16 of 27 were on record, H-B: 4 of 28) — the merge is cheap when every decision row names the netlist fact it rests on; the two findings that", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R3", "name": "jlc-s-paid-confirm-production-file-and-confirm-parts-placeme", "prompt": "A project hits this situation: JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are n. Handle it.", "expected_output": "JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are not guaranteed to raise a dialog or mail — the order went Reviewed → In Production in 14 h with neither step ever offered (ORDER_STATUS 2026-09-25), so every order-checklist row that depends on them (MINI_ORDER 1.20 / 2.8 / 2.9) silently went unexecuted. Capture the bottom-side placement preview yourself before paying, ", "assertions": ["the agent applies: JLC's paid 'Confirm Production file' and 'Confirm Parts Placement' options are not guaranteed to raise a dialog or mail — the order went Reviewed → In Production in 14 h with neither step ever offered", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R4", "name": "a-footprint-s-3d-model-can-sit-off-its-pads-and-nobody-notic", "prompt": "A project hits this situation: A footprint's 3D model can sit off its pads and nobody notices until a blind rev. Handle it.", "expected_output": "A footprint's 3D model can sit off its pads and nobody notices until a blind reviewer measures the exported mesh: the XYECONN USB-C STEP is 1.07 mm inboard of the pad-derived face, the pad-by-pad check (USB-C_receptacle.md) never looked at the model, and the case interference scan inherited the error for two weeks. Once per connector: compare the model's mating face with the face the pads imply (d", "assertions": ["the agent applies: A footprint's 3D model can sit off its pads and nobody notices until a blind reviewer measures the exported mesh: the XYECONN USB-C STEP is 1.07 mm inboard of the pad-derived face, the pad-by-pad chec", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
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
| D-12 | 2026-09-13 | Case: single-nozzle FDM friendly; colour by separate glued pieces | `A2 Quantity and horizon` (0.22) |
| D-13 | 2026-09-13 | USB-C receptacle: clearances and mechanical reinforcement for many insertions | `A0 Project scope` (0.17) |
| D-14 | 2026-09-13 | Case: latch two MINI units together into a two-end cable jig | `A2 Quantity and horizon` (0.25) |
| D-09a | 2026-09-13 | Premium aesthetics and a thought-through user experience apply to the MAIN board too | `A4 Enclosure process and material (per target)` (0.17) |
| D-16 | 2026-09-13 | External FTDI/pod path = backup debug path, not a mode of operation; pluggable, compact, case need not expose it | `0. Batches (ask in this order; one AskUserQuestion call per ` (0.13) |
| D-18 | 2026-09-13 | EXT/LA connectors and EXT pinout: CC-057 set with the 1.27 mm LA pair; CC-056 Total Phase order | `B3 Controlled impedance` (0.14) |
| D-19 | 2026-09-13 | External models for the double-blind reviews via the installed `agent` CLI | `E1 Review rounds per gate` (0.23) |
| D-20 | 2026-09-13 | MINI stick dimensions are secondary: grow the board as required to route cleanly; functionality, electrical and signal i | `B1 Layers and thickness` (0.09) |
| D-22 | 2026-09-13 | Deep layer-by-layer, trace-by-trace visual inspection of the routing after final routing | `F2 Stock policy and alternates` (0.21) |
| D-24 | 2026-09-14 | MINI printed case: two-tone, per-colour AMS printing, assembly-friendly for 50+ units | `A2 Quantity and horizon` (0.19) |
| D-25 | 2026-09-14 | Product name: AEC-CT2 = AEC Cable Tester 2 | — |
| D-26 | 2026-09-14 | MINI USB-C receptacles: CC-052 option B (mid-mount XYECONN C20883026) | — |
| D-27 | 2026-09-14 | Fan: none fitted, provision kept for a specific part sourced outside JLC | `C6 Fan, vents, thermal` (0.19) |
| D-29 | 2026-09-14 | Credo evidence: one real cable in hand, no vendor documents | — |
| D-30 | 2026-09-14 | MINI: remaining open items take the coordinator's recommendations; provisional decisions confirmed | `kickoff-questionnaire.md — every owner decision a board and ` (0.24) |
| D-31 | 2026-09-15 | MINI case v3: two-part, single-material, supportless; colour as a print-time option | — |
| D-32 | 2026-09-15 | MINI case: 13.4 mm finger dish (one-span D-12 bridge exception) + short switch names | `B7 Test points and self-documenting silk` (0.2) |
| D-33 | 2026-09-15 | MINI case fastening: heat-set (hot press-fit) M3 inserts + standard screws | `A2 Quantity and horizon` (0.16) |
| D-34 | 2026-09-15 | MINI case: print supports allowed → two-piece case (tray + one top shell) | `C1 Pieces` (0.19) |
| D-37 | 2026-09-17 | After the D-36 simplification: stricter on waivers, strengthen the design | — |
| D-38 | 2026-09-18 | Blanket 'go with recommended' on every open recommendation at PAUSE POINT 4: CC-088 (a)–(k), coherence Q1–Q5, CC-086 (a) | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-39 | 2026-09-19 | MINI_ORDER §2.7 stock gate stays at ≥ 5 000 (or the alternate) for C27882 / C11133 | — |
| D-40 | 2026-09-19 | Fix the D-22 run-3 review findings (CC-095 MINOR list) — round 6d authorised, in parallel with the JLC quote pass | — |
| D-41 | 2026-09-19 | Extensive, parallelised double-blind reviews of the round-6 design with the best external models via the Cursor `agent`  | `E1 Review rounds per gate` (0.14) |
| D-42 | 2026-09-20 | Owner answers to the post-review items | — |
| D-43 | 2026-09-20 | After every change/re-route round: full verification gauntlet before the order — double-blind reviews, deep visual inspe | `F2 Stock policy and alternates` (0.11) |
| D-44 | 2026-09-20 | Two case tracks: keep the local single-colour FDM case (v3.6.x) for own printing/assembly; **complete re-design and re-e | `kickoff-questionnaire.md — every owner decision a board and ` (0.1) |
| D-45 | 2026-09-20 | Removable top portion over the QSFP-DD heat sink (both case tracks) + secondary logos so branding survives with the hood | `0. Batches (ask in this order; one AskUserQuestion call per ` (0.13) |
| D-46 | 2026-09-20 | JLC-manufactured case: ultra-premium look, feel and material | — |
| D-47 | 2026-09-20 | JLCDFM: every danger AND warning on the board of record is to be fixed, and our own DRC/checks must catch them | — |
| D-48 | 2026-09-20 | Local FDM case: coloured marks only on top-facing (Z-up) surfaces printed in the same top layers as the legends; no colo | `C9 Brand marks / logos on FDM parts` (0.1) |
| D-49 | 2026-09-20 | Case: CC-120 A+B (full-height tray dovetail + matching body rail), CC-113 v3.7 snap-hood consequences accepted, CC-115 ( | `I. Identity, envelope, delegation (added by the first retro ` (0.12) |
| D-50 | 2026-09-20 | (1) Free FEA as a generated case-pipeline stage; (2) generated clear-to-build reports for the PCB and the case | `0. Batches (ask in this order; one AskUserQuestion call per ` (0.15) |
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
| D-65 | 2026-09-21 | First-pass case build at JLC3DP/JLCCNC; two-tone by parts: (1) legend / mark INLAY PLATES (SLA white, e.g. LEDO 6060 / 9 | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-66 | 2026-09-21 | Release cut before the order: converge → final case checks → final cleanup + docs + reports → git tag → owner places the | `E2 Visual inspections` (0.19) |
| D-67 | 2026-09-22 | Production-cut phase pulled forward: run the D-55 / D-56 / D-57 plan now (docs/production/PRODUCTION_CUT_PLAN.md) plus t | `A2 Quantity and horizon` (0.14) |
| D-68 | 2026-09-22 | CC-183 option (A): lid START triangle for MODSEL aligned to L (`ui.start.SW302: L`) | `C1 Pieces` (0.21) |
| D-69 | 2026-09-22 | JLC board order PLACED for rev 0: board ed9431d7 / package out/MINI/fab/2026-09-22_ed9431d7 — PCB 5 panels (70 × 136, 1  | — |
| D-70 | 2026-09-22 | Repo re-organisation at the order: remove superseded case and PCB versions from the working tree (git history + tags kee | `C8 Two print targets and their fits` (0.11) |
| D-71 | 2026-09-22 | JLC case orders PLACED for rev 0 (case v3.13, tag mini-rev0-production-cut.1): JLC3DP — tray / shell / hood MJF PA12-HP  | `B4 Finish, mask colour, silk` (0.1) |
| D-72 | 2026-09-22 | D-70 phase 2 with the recommended answers ((a) docs/design kept, (b) early-era out/ dirs deleted except plan_smoke, (c)  | `I. Identity, envelope, delegation (added by the first retro ` (0.1) |
| D-73 | 2026-09-22 | Archive folders become deletions: superseded material leaves the working tree entirely; git history and the tags (mini-r | `E3 Coupons, dummies, first article` (0.14) |

## 8. DFM process table drift — `design/dfm_processes.yaml` vs the skill's `templates/design/dfm_processes.yaml` (SKILL.md §8.1 (c))

| Kind | Row | Key | Project value (citation) | Template value |
|---|---|---|---|---|
| VALIDATED | `jlc_mjf_pa12` | validated_on | JLC3DP thinWall verdicts 2026-09-22..28 (docs/quotes/dfm_verdicts.yaml): W / R / K validated; F, P, V, H not decidable from the JLC data (see PRINT_DFM_VALIDATION.md section 4) | [] |
| VALIDATED | `jlc_sla_9600` | validated_on | JLC3DP verdicts on the plate_top_mark bodies (2 labelled): the automatic check passed the 0.01 mm arm contacts its engineer flagged - P is validated by the ENGINEER, not by the automatic verdict | [] |
| NEW | `bambu_p2s_pla` | (row) | in-house Bambu Lab P2S / FDM PLA / PETG 0.4 nozzle (the p2s preset): wall_min 0.9, wall_reco 1.2, feature_min 0.45, detail_min 0.45, hole_min 1.0, neck_max 0.05, slender 10, sliver_area 5.0, overhang_max_deg 45, bridge_max 10, supports interior, legend_land_min 0.45, legend_void_min 0.4 | - |
| NEW | `bambu_p2s_colour_body` | (row) | in-house Bambu Lab P2S / FDM PLA colour body fused into a host part (AMS multi-part object, gen/bambu_3mf.write_ams_3mf) - the hood accents and the cap marks: wall_min 0.9, wall_reco 1.2, feature_min 0.45, detail_min 0.45, hole_min 1.0, neck_max 0.05, slender 10, sliver_area 5.0, overhang_max_deg 45, bridge_max 10, supports none, legend_land_min 0.45, legend_void_min 0.4 | - |
| CHANGED | `xometry_mjf_pa12` | build_max | [380, 284, 380]  ([V] Protolabs individual part maximum 13.5 x 10.4 x 13.7 in) | [356, 279, 330] |

NEW rows and CHANGED numbers go into the template WITH their [V] / [K] citation; a VALIDATED row's evidence goes into `references/print-dfm.md` §4 (the template keeps `validated_on: []`). A CHANGED number without a citation on its line is not carried.

## 9. What to do with this report

1. Fold every NEW row into the reference named in §5 (one generalised line; the source's number stays as the labelled worked example).
2. Extend the PARTIAL sections where the mechanism is missing.
3. Add one eval per §6 stub; run the smoke; bump SKILL.md `version`; write the CHANGELOG entry from §4.
4. Add a questionnaire question (with a recommended answer) per §7 topic that will recur.
5. Carry every §8 row into templates/design/dfm_processes.yaml (cited) / references/print-dfm.md.
6. Blind-review the skill again (two lenses), then tag.

## 10. Disposition (maintainer, 2026-09-30, folded into 0.10.0)

- `--apply` folded 12 pitfalls lines and a CHANGELOG stub; the lines were REWRITTEN generalised by hand (section *records / arrival / review*), the stub became the 0.10.0 entry.
- The two NEW process rows (`bambu_p2s_pla`, `bambu_p2s_colour_body`) were NOT carried: they are the source project's printer-named copies of the template's `home_fdm_04` / `home_fdm_04_colour_body` rows (same numbers, same citations). The `xometry_mjf_pa12 build_max` CHANGED item cites a Protolabs page for a Xometry row — not carried (citation does not match the row). The two VALIDATED items are recorded in `references/print-dfm.md` §4 already (0.9.1).
- Patterns landed as rules / templates / scripts: (a) the generated arrival checklist (`scripts/arrival_checklist.py`, `templates/design/arrival_checklist.yaml`, SKILL §10.1, release-and-cut §10, cut deliverable REC-002, gates-required); (b) `templates/SPEC_ERRATA.md` + release-and-cut §11; (c) the `[K owner-read]` tag (SKILL §4, part-verification); (d) software gates with their closing commit = checklist §C; (e) the review protocol with a record-reading verifier (SKILL §5, agent-ops §4, `blind-deep-review.js` VERDICT enum + `rev_impact`); (f) the bridge-span rule stays the 0.9.1 one in the skill — the project copy's EDT-only span is flagged for back-port to the project (not the skill's job) — and the coordinator's correction (open-ended footprint = longest in-footprint chord) is applied in `print_dfm.py` 0.10.0 with the four selftest constructs; (g) `kickoff.enclosure.fit_result` landing key + checklist row E-FIT; (h) owner addition: `references/fdm-print-optimisation.md` + kickoff C11 + eval 16.
- The 78 "unasked owner topics" are project narrative (form factor, part numbers, order lines) as in every earlier retro; only C11 recurred.
