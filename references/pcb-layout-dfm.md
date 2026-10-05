# pcb-layout-dfm.md — G1 → G2: the PCB build rules, the layout chain and the adopt gate

Every quantitative rule below carries one of four tags, so a reader knows what moves it:

| Tag | Meaning | What changes it |
|---|---|---|
| **[checker]** | what the fab's DFM viewer or the CAD DRC grades (a number the mirror reproduces) | the fab changes its viewer → re-copy `design/dfm_thresholds.json` |
| **[fab capability: URL, date]** | a published limit of the fab, fetched live and dated | the fab's capability page → re-fetch before every quote |
| **[physics]** | a material or process fact independent of the vendor | never silently; a decision row with a source |
| **[owner choice]** | a bar the owner set (recorded as a D row from the kickoff questionnaire) | the owner |
| **[convention]** | a shape the scripts and templates rely on | a decision row + the generator |

The worked example throughout is JLCPCB, numbers fetched **2026-09-13** from `jlcpcb.com/capabilities/pcb-capabilities` and the PCBA
capability page; they are the values that were live then — **fetch the current page before using any of them** (`references/fab-dfm.md` §7).
The design margin rule for every fab number: **design strictly greater than the published minimum** (the viewer grades a value EQUAL to its
warning threshold as Warning) — limit + 0.01 mm for copper rules, one full step for drills.

## 1. The G1 → G2 chain (inputs, outputs, gate, decider)

| | |
|---|---|
| **Inputs** | the G1 schematic of record (yaml + generated CAD), `design/<board>_board.yaml` (outline, stack-up, design rules, net classes, keep-outs, `dfm_accepted`), `design/placement.csv`, `design/dfm_thresholds.json`, the fab's rotation table (`design/<fab>_rotation.yaml`) |
| **Generators (project `gen/`)** | `place_pcb` (placement CSV → footprints, rule areas, canary) → router (`route_*`, the router session file is the record) → post-pass (stub snap, staircase merge — scripted, never hand edits) → `silk_pass` → `export` (Gerbers/drill/pos, DRC json, parity, route quality, DFM items) → `panelize` → `fab_package` |
| **Outputs** | `30-board/kicad/<board>/<board>.kicad_pcb` (board of record, md5 keys everything), the router session (`*.ses`/`*.dsn`), `out/G2/` review pack (§1.3), `out/dfm_items.json` + `out/dfm.json`, `30-board/fab/<rev>/` package (board_id.txt carries the md5) |
| **Gate** | SKILL §6 adopt rule: DRC 0 errors / 0 unconnected, **0 warnings unless a dated waiver row** (§9), schematic parity 0, canary fires exactly once, route quality 0 unjustified HIGH, fab DFM mirror 0 open, silk check 0, every `--selftest` / `--check` green, clone gate on `git archive HEAD`, visual inspection round merged |
| **Decider** | the owner writes the G2 cell after one review round (`board` role set + `routing-inspection.js`) is merged; the agent asks (SKILL §1.1) |

### 1.1 Placement CSV **[convention]**
`design/placement.csv`: `ref, x, y, rot, side, locked, group, note` — mm in the board frame (origin the drill/place origin, Y up), rotation CCW
degrees, `side` = top/bottom, `locked` = the part is fixed for the router, `group` = the placement cluster (connectors, power, mcu, …). The
generator refuses a refdes missing from the schematic or a part outside the outline; a part the spec pins (connector positions, mounting holes,
the cage) is `locked: true` with the spec section in `note`. Placement is regenerated from the CSV — the CAD GUI is never the source.

### 1.2 Router session **[convention]**
The routed board + the router's session file (Freerouting `.ses` with its `.dsn`, or the equivalent) are the artefacts of record; routing is
never re-run to reproduce them (deterministic only with one thread and the same inputs). Re-import (`--import-ses`) is the replay. Keep-outs and
net classes must be exported into the router input — grep the DSN for them after any flag change (`references/pitfalls.md` kicad).

### 1.3 The G2 review pack (`out/G2/`, generated, committed)
| File | Produced by | Why the reviewer needs it |
|---|---|---|
| `<board>.kicad_pcb` md5 + `board_id.txt` | export | identity: the board of record |
| `drc.json` + `drc_summary.md` | `<cad-cli> pcb drc --severity-all --format json` | 0 errors / 0 unconnected / 0 warnings-or-waived, with the canary line |
| `parity.md` | export (schematic ↔ board field + net diff) | 0 differences |
| `route_quality.md` | `gen/route_quality.py` | per-net table, HIGH list with justification rows |
| `dfm.json` / `dfm_items.json` | measurer + `scripts/dfm_check.py` | fab DFM mirror 0 open; accepted items by refdes with reason |
| `silk_check.md` + silk PNGs | silk pass | geometry + a READ legibility pass |
| `gerbers/`, `<board>.drl`, `pos.csv`, `bom_jlc.csv`, `cpl_jlc.csv`, `rotation_log.csv` | export | what the fab receives; rotation offsets applied per footprint listed for the reviewer |
| `renders/` (top, bottom, iso, opaque background) + `tiles/` (≥ 40 px/mm) | render + tiler | the visual gates read images |
| `EVIDENCE.md`, `REVIEW_NOTES.md` | generator / hand-written | md5 of every file above; what changed since the last round |

## 2. Stack-up and copper weight
- **Stack-up = the fab's named template, copied into the CAD's physical stack-up** **[fab capability]**: the fab publishes templates per
  layer count / thickness / outer / inner copper (JLC 2026-09-13: `JLC04162H-7628` = 4 layers, 1.6 mm, 2 oz outer, 0.5 oz inner, 7628 prepreg
  0.2104 mm, core 1.065 mm, Dk 4.4 / 4.6; total 1.656 mm). Record the template name in `design/<board>_board.yaml` and on the order sheet;
  the same template is selected on the quote form.
- **Copper weight is an owner choice with consequences** **[owner choice]**: heavier outer copper (2 oz) buys current capacity and costs
  minimum trace/space (JLC: 0.15/0.15 at 2 oz vs 0.09/0.09 at 1 oz), mask dam width (0.20 vs 0.10) and the fab's impedance calculator support
  (JLC's supports 1 oz only, 2026-09-13). Inner copper default 0.5 oz **[fab capability]**; 1 oz inner changes prepreg/core thickness and
  therefore impedance geometry — pin one value in the spec before layout.
- Thickness tolerance ±10 % at ≥ 1.0 mm **[fab capability]** (1.6 → 1.44…1.76): a press-fit connector or a card-edge must accept the range.
- Material grade / Tg is selected at order **[owner choice]** (JLC impedance profiles assume a TG155 laminate).

## 3. Controlled impedance and differential pairs
- **When it is required** **[physics]**: any pair whose length exceeds ~1/10 of the signal's rise-time wavelength on FR-4 (USB 2.0 90 Ω pairs
  longer than a few cm, any multi-Gb/s lane, RF); short pairs (a few cm) care more about skew and stubs than about ±10 % impedance. Write the
  requirement per net class in the spec (`R-Exx: 90 Ω ±10 % differential`), or the row "no controlled impedance — every pair < N cm" as a D row.
- **Recording the calculation** **[convention]**: the CAD's calculator on the fab's stack-up (coupled microstrip / stripline with the mask
  layer), cross-checked by the fab's own calculator where it supports the copper weight; the result (w / s / layer / reference plane / Z / tool)
  is a row in `design/<board>_board.yaml net_classes` with the source, and the pack quotes it. Keep w ≥ 0.20 mm so the fab's ±20 % width
  tolerance **[fab capability]** stays inside ±10 % Z.
- Differential rules the CAD enforces: pair gap, uncoupled length ≤ N mm, skew ≤ N mm, no via stubs on the pair, reference plane continuous
  (an In2 signal over an In1 antipad edge is a route-quality HIGH, §10). Impedance control is an order option **[fab capability]**: ask for it
  on the quote form; if the form refuses it for the copper weight, that is a decision row, not a silent drop.

## 4. Trace / space / via / annular / drill minimums vs the fab table
Copy the fab's table into `design/dfm_thresholds.json` (source URL + date) and design strictly greater **[checker]**. Worked example
(JLCPCB, 2 oz outer, multilayer, 2026-09-13) **[fab capability]**:

| Rule | Fab limit | Design value (limit + margin) |
|---|---|---|
| track width / spacing | 0.15 / 0.15 | DRC min 0.16 / 0.16; net-class default 0.20 |
| via drill / pad | 0.15 possible, 0.20 preferred, < 0.30 surcharge; ring ≥ +0.10 | default 0.30 / 0.62 (ring 0.16); constrained 0.25 / 0.50 only where a fan-out needs it, ordered with the matching min-via option |
| PTH annular ring | 0.254 (2 oz) | ≥ 0.30 |
| hole-to-hole | 0.20 via / 0.45 PTH | 0.50 |
| hole to copper (inner) | 0.20 via / 0.30 PTH | 0.30 |
| PTH hole to track | 0.28 min, 0.35 recommended | 0.35 |
| copper to routed edge / to V-cut | 0.20 / 0.40 | 0.30 / 0.50 |
| PTH hole tolerance | +0.13 / −0.08; press-fit option ±0.05 (multilayer ENIG, circular, listed in the remark) | press-fit holes per the connector drawing, named in the order remark |
| same-net spacing | 0.25 | 0.25 (no CAD rule — avoid parallel same-net slivers) |
| min SMD pad | 0.25 × 0.25 | never below the datasheet pad |

## 5. Via-in-pad and tenting
- Tented (mask-covered) vias by default, ≤ 0.5 mm, none inside SMD pads **[fab capability + convention]**; via-in-pad needs the fab's filled-and-
  capped process (an order option and a surcharge) — a decision row, never an accident of a fan-out. Mask-plugged vias: no opening either side,
  ≥ 0.35 mm from other mask openings (JLC).
- A via under a silk text cell is a silk defect (§11); a via in a fiducial's clearance ring is a placement defect.

## 6. Thermal reliefs and teardrops
- **Thermal reliefs** **[physics + owner choice]**: on PTH pads into pours always (a solid connection wicks heat from the joint and tombstones
  a hand-soldered pin); on SMD pads into pours the default is solid for power/GND pads under ICs (thermal path) and relief spokes on small
  passives (reflow balance) — record the choice per zone in `design/<board>_board.yaml zones`, with spoke width ≥ the track minimum + margin.
  A class clearance larger than the fill's zone clearance is unenforceable — write the as-built geometry into scoped rules
  (`references/pitfalls.md` kicad).
- **Teardrops** **[owner choice]**: on at the track/pad and track/via junctions of the fine-pitch escape when the ring is at the fab minimum
  (they buy annular-ring margin against drill wander); recorded as a generator flag so the replay reproduces them; the DRC and the fab mirror
  run on the board WITH teardrops (they change spacing).

## 7. Solder mask, paste and stencil
- **Mask expansion 0 (pad-defined openings)** **[fab capability, LDI]**; keep ≥ 0.09 mm between an opening and a neighbouring trace (JLC).
- **Mask dam (bridge) minimum** **[fab capability]**: 0.20 mm at 2 oz any colour; 0.10 mm at 1 oz for standard colours, 0.13 black/white
  (JLC 2026-09-13). Below the dam minimum the fab gangs the openings — a 0.4 mm pitch QFN with 0.2 mm pads at 2 oz has exactly 0.20 → zero
  margin: state "gang opening accepted" or move to 1 oz as a decision row. **Pin mask = copper on fine-pitch parts**; a +0.05 expansion cuts
  the webs below the minimum (`references/pitfalls.md` silk).
- **Paste** **[convention]**: paste = pad by default; reduce paste (−10…−30 %) on large thermal pads (QFN centre pads: windowpane the paste
  into 4–9 apertures at ≤ 50–70 % coverage **[physics]**, or the part floats / voids); no paste on NPTH annuli or test pads; paste layer
  exported on both sides for a two-sided assembly.
- **Stencil thickness** is the fab's choice for its own assembly (JLC prices one stencil per side); state it only when the design needs it
  (0.10 mm for 0.4 mm pitch, 0.12–0.15 mm general) **[physics]**, as a remark, and only when the fab lets the customer choose.
- Exposed copper area above the fab's percentage (JLC: 30 % for ENIG) is a surcharge **[fab capability]** — keep pours under the mask, expose
  pads, test points and designed artwork only.

## 8. Component size and link-part policy **[owner choice]**
Defaults the questionnaire proposes:
- **No 0201** (Economic PCBA minimum is 0402 at JLC; 0201 is Standard-only and hand-rework-hostile); **0402 minimum**, 0603 where the value is
  likely to be reworked (pull-up options, series terminations near an edge).
- **Signal 0 Ω links: 0603; power-path links: 1206** (a named basic-library code of the fab) — the size is the current rating and the
  rework handle; a link that may be cut later is a **bridged solder-jumper net-tie footprint** (allowed, DFM-clean), never a 0 Ω resistor
  drawn as a wire.
- Every fitted part rated for the fab's reflow profile **[fab capability]** (JLC Economic 255 ± 5 °C not adjustable; Standard 240 ± 5 °C):
  "≥ 260 °C peak per J-STD-020" in the parts-vetting checklist; a part at zero margin gets a bake / profile remark.
- Basic vs extended library: each unique extended part costs a feeder fee **[fab capability]** — the BOM report counts them; prefer basic /
  preferred parts for jellybeans (a stock floor per code is an owner choice, `references/part-verification.md`).

## 9. Two-sided SMT assembly
- The **owner chooses** single / two-sided **[owner choice]** (two-sided buys 30–40 % board area). Two-sided implies the
  fab's Standard tier (setup + second stencil fees), edge rails / fiducials required, and a press-fit or THT step that needs a **fixture band**
  on the bottom: no bottom part within ±2 mm of a press-fit row over its length, boss / screw-head keep-outs drawn on BOTH sides.
- **Part height per side** **[physics + convention]**: the side that reflows first (usually the lighter, smaller-part side) is reflowed a second
  time upside down — parts heavier than ~30 g per square inch of pad area or tall parts (electrolytics, inductors > 4.5 mm) go on the second
  side or get glue (a remark, the fab decides); record per-side max height in the board yaml (the case reads it).
- THT: unused PTH stay solder-free (say so in the remark); hand-installed parts are DNP in the BOM and marked on the fab drawing.

## 10. Polarity, rotation and the CPL **[convention + fab capability]**
- CPL file: `Designator, Mid X, Mid Y, Rotation, Layer`, mm, 4 decimals, position = pad-bounding-box centre relative to the drill/place origin,
  Y up, rotation **CCW positive viewed from the top**, bottom rows `(180 − rotation) mod 360`; BOM `Comment, Designator, Footprint, <fab part
  field>`; DNP excluded from both; **the generator hard-fails on an empty fab-code field on a fitted part — never falls back to the MPN**.
- **The fab has no per-package zero-rotation table**: "zero = tape/reel orientation, corrected per the silkscreen" (JLC). Two community
  rotation databases disagree by 180° on SOT-23 and QFN. So: a **project-owned rotation table** (`design/<fab>_rotation.yaml`, footprint-name
  regex → offset, seeded from two databases, only agreeing rows `review: false`), `rotation_log.csv` in the pack listing every applied offset,
  and **the fab's 3-D placement preview is the only authoritative check** before paying — a G2 checklist item (a +90 for 1×N headers was
  confirmed only there).
- Polarity mark on the silk of **every** polarised footprint (the fab places per silkscreen when it conflicts with the CPL): pin-1 dot on every
  IC, cathode band / triangle on diodes, + on electrolytics, pin 1 on headers; the F.Fab layer carries the same marks for the assembly drawing.
- **Pre-answer the fab's engineer** **[convention]**: at G2, beside the silk check, a fab's-eye pass — a polarised footprint whose only mark is on the
  bottom at an odd rotation, a mark under mask or a pad, a custom footprint with no body outline on the fab layer — each is a production-hold
  question waiting to happen; fix the footprint. The package ships `ASSEMBLY_NOTES` (renders with the cathode end / pin-1 corner per part class,
  body + pin 1 + mating direction of every custom-footprint connector, the empty / unplated holes with finished sizes and tolerances;
  `references/fab-dfm.md` §9), the order remark points at it, and the fab's engineer questions, when they still come, are answered on the board's
  pad-1 positions, never on the CPL rotation (`references/vendor-review.md` §5–§7).

## 11. Fiducials, test points, silk, courtyards
- **Fiducials** **[fab capability]**: 3 per side that carries parts (1 mm copper, 3 mm mask opening, ≥ 5 mm from the edge, not on a symmetry
  axis), on the panel rails when panelised; Standard PCBA requires them, Economic does not.
- **Test points** **[owner choice + convention]**: one per rail and per bus line the bring-up tool reads (the criteria yaml names them), pad
  ≥ 1.0 mm, ≥ 2.54 mm pitch where a probe clip is expected, labelled with the net name and purpose on the silk (self-documenting labels), grouped
  in a field with a legend grid; coverage listed in the test plan (T-nn ↔ TP).
- **Silk** **[fab capability + checker]**: line ≥ 0.15 (design 0.16+), text height ≥ 1.0 mm (labels 1.1–1.2), width:height 1:6, silk-to-pad /
  mask ≥ 0.15 (design 0.20), **no silk over pads, no via or PTH under a text cell** (via keep-out from the text bbox at route time; clipping is
  for hairlines only), silk-to-edge against the TRUE outline polygon (notches), glyph stroke ≥ the minimum by a morphological opening, font
  either shipped with the repo or count-aware in CI (a proprietary system font cannot run on the runner). A legibility gate READS the rendered
  PNG. Order number: "specify location" on a silk box or removed **[owner choice]**.
- **Courtyards and tombstoning** **[fab capability + physics]**: body-to-body spacing per the fab's SMD spacing table (JLC: 0402↔0402 0.18,
  0603↔0603 0.25, chip↔QFN 1.0, QFN↔QFN 1.0, BGA↔BGA 2.0; ≥ 0.30 passives body-to-body in practice, 0.50 where hand rework is expected,
  ≥ 1.5 mm around tall parts); symmetric pads and equal thermal mass on both ends of a chip part (one pad into a pour without relief tombstones
  the part); courtyard overlap = DRC error, no exceptions.

## 12. Creepage and clearance for the voltage class **[physics + owner choice]**
Below 60 V DC / 30 V AC (SELV) the fab minimum spacing governs; above, the spec names the standard (IEC 60664-1 / IPC-2221 tables: pollution
degree, material group, working voltage) and the layout carries the creepage / clearance as a **generated rule** (a net-class-to-net-class
clearance) plus a slot where creepage needs it. State the class in the spec even when it is "SELV only — no creepage rule" (a decision row the
reviewer can read); an isolated section (USB isolator, mains) gets a keep-out zone on every layer and a drawn isolation barrier.

## 13. Panelization **[fab capability]**
- Standard PCBA needs every side ≥ 70 mm (JLC 2026-09-13) and the fab's automatic rails land on the SHORT edges; a narrow board needs a
  **customer panel**: 1-up + rails on the LONG edges (5 mm rails, Ø2 tooling holes, 1 mm fiducials on the rails), **mouse bites** (5 × Ø0.5
  tabs) where copper is < 0.40 mm from the break line (V-cut needs ≥ 0.40), routed 2 mm slots between, drill/place origin unchanged so the panel
  CPL = board CPL + rail offset.
- Gate the panel on its STORED fills (`BuildConnectivity()` before every fill or pours starve), per-zone area within 1 % of the source, Gerber
  region count equal, DRC 0/0; run the fab DFM on the PANEL zip too (a merged drill cannot mark mouse-bite holes NPTH — a remark settles the
  "unconnected via" warnings). Panel by customer REQUIRES the panel format field on the quote form.

## 14. DRC census: 0 errors / 0 warnings unless a dated waiver row
- `<cad-cli> pcb drc --severity-all --format json` on the committed board, **classes enforced** (KiCad honours only explicit
  `netclass_assignments`, never patterns, and no DRC exclusions: emit per-net assignments and rules from the generator) — the census counts
  every severity per rule name (`gen/drc_count.py` style, cross-host: silk-text items dropped only when the font is absent, with a NOTE).
- **Zero errors, zero unconnected, zero warnings.** A warning that stays is a **dated waiver row** in `90-log/DECISIONS.md` (rule,
  item, reason, owner) mirrored by a generated accept rule (`enclosedByArea` marker rule area per accepted item, not `insideArea`), so DRC and
  the route-quality gate accept exactly the same copper; a prose waiver the matrix cannot read does not count. The G2 cell and the board order
  require this bar (`templates/90-log/GATES.md`).
- **The canary rule** **[convention]**: one deliberately violated generated rule (a `CANARY` text or a marker area) that must fire **exactly
  once** in every DRC run — proves the rule file was parsed and the classes are enforced (a malformed `.kicad_dru` is silently ignored; a
  stricter rule than the class is invisible to the router and appears afterwards).

## 15. Route-quality classes **[convention + owner choice]**
Per net: routed / direct (MST over pads) meander ratio, segments, vias, layer changes, min/max width vs class, stubs, acute corners, layers used.
Board level: via total, copper per layer, inner-layer signal length not over solid reference copper, sensitive-net proximity (I²C / control /
sense / USB) to switching nodes and the crystal, power corridor cross-section (≥ N mm² per rail, ≥ 2 vias per transition). Flags are graded
HIGH / MED / LOW; **0 unjustified HIGH** at G2, each HIGH either fixed through
the generator or a dated waiver row + accept rule (§14). The report is `route_quality.md` in the pack.

## 16. Schematic ↔ layout parity **[convention]**
Every symbol field is copied to the footprint as a hidden property (MPN, fab code, Confidence, DNP, Alt_*), footprint attributes mirror the
symbol (DNP does not imply exclude-from-BOM — set both), net names and pin nets equal between the exported netlist and the board; the parity
check lists every difference and G2 requires 0. A schematic regeneration must not rewrite the board-side project file (rules, classes) —
restore it from HEAD or merge (`references/pitfalls.md` tooling/gates).

## 17. Fab DFM mirror before the order, and the order-time stock freeze
- **Before the first quote and at every adopt**: the fab's checker mirrored in-repo (`references/fab-dfm.md`: thresholds JSON with source +
  date, project measurer → items, `scripts/dfm_check.py` grader, acceptances by refdes with **date + reason + evidence**, bare tracks / vias
  never accepted), **0 open** — every item of either fab grade fixed or accepted with vendor evidence. Then the fab's
  own viewer on the board AND the panel upload, counts diffed against the mirror, PDF export filed under `60-orders/quotes/<date>/`.
- **Stock**: every fitted code verified live with the run-relative minimum (`qty × boards × attrition`), owner floors on jellybeans; **once the
  order is PLACED the package is judged on the frozen `stock_snapshot.json`**, never on the live shelf (`references/fab-dfm.md` §8).

## 18. Where the numbers come from (worked example, JLCPCB 2026-09-13)
`jlcpcb.com/capabilities/pcb-capabilities` (copper, drill, mask, silk, outline, tolerances), `…/capabilities/pcb-assembly-capabilities`
(Economic vs Standard: sides, min package 0402 / 0201, min pitch 0.4 / 0.35, reflow 255 / 240 °C, rails + fiducials), help articles
`pick-place-file-for-pcb-assembly`, `pcb-assembly-faqs-part-2` (rotation = tape orientation, silkscreen governs polarity),
`minimum-spacing-for-smd-components`, `Panelizing-your-PCB-for-Assembly`, `in-what-cases-will-there-be-charged-extra`, the stack-up template
API (`getImpedanceTemplateSettings`). Fetch again, cite the date, and keep the raw responses under `60-orders/quotes/<date>/`.
