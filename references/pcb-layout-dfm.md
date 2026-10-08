# pcb-layout-dfm.md — G1 → G2: the PCB build rules, the layout chain and the adopt gate

Every quantitative rule below carries one of four tags, so a reader knows what moves it:

| Tag | Meaning | What changes it |
|---|---|---|
| **[checker]** | what the fab's DFM viewer or the CAD DRC grades (a number the mirror reproduces) | the fab changes its viewer → re-copy `20-design/dfm_thresholds.json` |
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
| **Inputs** | the G1 schematic of record (yaml + generated CAD), `20-design/<board>_board.yaml` (outline, stack-up, design rules, net classes, keep-outs, `dfm_accepted`), `20-design/placement.csv`, `20-design/dfm_thresholds.json`, the fab's rotation table (`20-design/<fab>_rotation.yaml`) |
| **Generators (project `gen/`)** | `place_pcb` (placement CSV → footprints, rule areas, canary) → router (`route_*`, the router session file is the record) → post-pass (stub snap, staircase merge — scripted, never hand edits) → `silk_pass` → `export` (Gerbers/drill/pos, DRC json, parity, route quality, DFM items) → `panelize` → `fab_package` |
| **Outputs** | `30-board/kicad/<board>/<board>.kicad_pcb` (board of record, md5 keys everything), the router session (`*.ses`/`*.dsn`), `80-reviews/G2/` review pack (§1.3), `30-board/layout/dfm_items.json` + `30-board/layout/dfm.json`, `30-board/fab/<rev>/` package (board_id.txt carries the md5) |
| **Gate** | SKILL §6 adopt rule: DRC 0 errors / 0 unconnected, **0 warnings unless a dated waiver row** (§9), schematic parity 0, canary fires exactly once, route quality 0 unjustified HIGH, fab DFM mirror 0 open, silk check 0, every `--selftest` / `--check` green, clone gate on `git archive HEAD`, visual inspection round merged |
| **Decider** | the owner writes the G2 cell after one review round (`board` role set + `routing-inspection.js`) is merged; the agent asks (SKILL §1.1) |

### 1.1 Placement CSV **[convention]**
`20-design/placement.csv` has the columns `ref, x, y, rot, side, locked, group, note`. Positions are mm in the board frame, with the drill/place
origin as origin and Y up. Rotation is in CCW degrees. `side` = top/bottom, `locked` = the part is fixed for the router, `group` = the placement
cluster (connectors, power, mcu, …). The
generator refuses a refdes missing from the schematic or a part outside the outline; a part the spec pins (connector positions, mounting holes,
the cage) is `locked: true` with the spec section in `note`. Placement is regenerated from the CSV — the CAD GUI is never the source.

### 1.2 Router session **[convention]**
The routed board + the router's session file (Freerouting `.ses` with its `.dsn`, or the equivalent) are the artefacts of record; routing is
never re-run to reproduce them (deterministic only with one thread and the same inputs). Re-import (`--import-ses`) is the replay. Keep-outs and
net classes must be exported into the router input — grep the DSN for them after any flag change (`references/pitfalls.md` kicad).

### 1.3 The G2 review pack (`80-reviews/G2/`, generated, committed)
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
- **Stack-up = the fab's named template, copied into the CAD's physical stack-up** **[fab capability]**. The fab publishes templates per
  layer count / thickness / outer / inner copper. JLC 2026-09-13: `JLC04162H-7628` = 4 layers, 1.6 mm, 2 oz outer, 0.5 oz inner, 7628 prepreg
  0.2104 mm, core 1.065 mm, Dk 4.4 / 4.6; total 1.656 mm. Record the template name in `20-design/<board>_board.yaml` and on the order sheet;
  the same template is selected on the quote form.
- **Copper weight is an owner choice with consequences** **[owner choice]**. Heavier outer copper (2 oz) buys current capacity. It costs
  minimum trace/space: JLC 0.15/0.15 at 2 oz vs 0.09/0.09 at 1 oz. It costs mask dam width: 0.20 vs 0.10. It also costs the fab's impedance
  calculator support: JLC's supports 1 oz only (2026-09-13). Inner copper default 0.5 oz **[fab capability]**; 1 oz inner changes prepreg/core
  thickness and therefore impedance geometry — pin one value in the spec before layout.
- Thickness tolerance ±10 % at ≥ 1.0 mm **[fab capability]** (1.6 → 1.44…1.76): a press-fit connector or a card-edge must accept the range.
- Material grade / Tg is selected at order **[owner choice]** (JLC impedance profiles assume a TG155 laminate).

## 3. Controlled impedance and differential pairs
- **When it is required** **[physics]**: any pair whose length exceeds ~1/10 of the signal's rise-time wavelength on FR-4. Examples are USB 2.0
  90 Ω pairs longer than a few cm, any multi-Gb/s lane, and RF. Short pairs (a few cm) care more about skew and stubs than about ±10 %
  impedance. Write the requirement per net class in the spec (`R-Exx: 90 Ω ±10 % differential`), or the row "no controlled impedance — every pair < N cm"
  as a D row.
- **Recording the calculation** **[convention]**: use the CAD's calculator on the fab's stack-up (coupled microstrip / stripline with the mask
  layer). Cross-check it with the fab's own calculator where that calculator supports the copper weight. The result (w / s / layer / reference
  plane / Z / tool) is a row in `20-design/<board>_board.yaml net_classes` with the source, and the pack quotes it. Keep w ≥ 0.20 mm so the
  fab's ±20 % width tolerance **[fab capability]** stays inside ±10 % Z.
- Differential rules the CAD enforces: pair gap, uncoupled length ≤ N mm, skew ≤ N mm, no via stubs on the pair, reference plane continuous
  (an In2 signal over an In1 antipad edge is a route-quality HIGH, §10). Impedance control is an order option **[fab capability]**: ask for it
  on the quote form; if the form refuses it for the copper weight, that is a decision row, not a silent drop.

## 4. Trace / space / via / annular / drill minimums vs the fab table
Copy the fab's table into `20-design/dfm_thresholds.json` (source URL + date) and design strictly greater **[checker]**. Worked example
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
- **Thermal reliefs** **[physics + owner choice]**: always on PTH pads into pours. A solid connection wicks heat from the joint and tombstones
  a hand-soldered pin. On SMD pads into pours, the default is solid for power/GND pads under ICs (thermal path) and relief spokes on small
  passives (reflow balance). Record the choice per zone in `20-design/<board>_board.yaml zones`, with spoke width ≥ the track minimum + margin.
  A class clearance larger than the fill's zone clearance is unenforceable — write the as-built geometry into scoped rules
  (`references/pitfalls.md` kicad).
- **Teardrops** **[owner choice]**: on at the track/pad and track/via junctions of the fine-pitch escape when the ring is at the fab minimum.
  They buy annular-ring margin against drill wander. Record them as a generator flag so the replay reproduces them. The DRC and the fab mirror
  run on the board WITH teardrops, because teardrops change spacing.

## 7. Solder mask, paste and stencil
- **Mask expansion 0 (pad-defined openings)** **[fab capability, LDI]**; keep ≥ 0.09 mm between an opening and a neighbouring trace (JLC).
- **Mask dam (bridge) minimum** **[fab capability]**: 0.20 mm at 2 oz any colour; 0.10 mm at 1 oz for standard colours, 0.13 black/white
  (JLC 2026-09-13). Below the dam minimum the fab gangs the openings — a 0.4 mm pitch QFN with 0.2 mm pads at 2 oz has exactly 0.20 → zero
  margin: state "gang opening accepted" or move to 1 oz as a decision row. **Pin mask = copper on fine-pitch parts**; a +0.05 expansion cuts
  the webs below the minimum (`references/pitfalls.md` silk).
- **Paste** **[convention]**: paste = pad by default. Reduce paste (−10…−30 %) on large thermal pads. On QFN centre pads, windowpane the paste
  into 4–9 apertures at ≤ 50–70 % coverage **[physics]**, or the part floats / voids. No paste on NPTH annuli or test pads. Export the paste
  layer on both sides for a two-sided assembly.
- **Stencil thickness** is the fab's choice for its own assembly (JLC prices one stencil per side). State it only when the design needs it
  (0.10 mm for 0.4 mm pitch, 0.12–0.15 mm general) **[physics]**, as a remark, and only when the fab lets the customer choose.
- Exposed copper area above the fab's percentage (JLC: 30 % for ENIG) is a surcharge **[fab capability]** — keep pours under the mask, expose
  pads, test points and designed artwork only.

## 8. Component size and link-part policy **[owner choice]**
Defaults the questionnaire proposes:
- **No 0201** (Economic PCBA minimum is 0402 at JLC; 0201 is Standard-only and hand-rework-hostile); **0402 minimum**, 0603 where the value is
  likely to be reworked (pull-up options, series terminations near an edge).
- **Signal 0 Ω links: 0603; power-path links: 1206** (a named basic-library code of the fab). The size is the current rating and the
  rework handle. A link that may be cut later is a **bridged solder-jumper net-tie footprint** (allowed, DFM-clean), never a 0 Ω resistor
  drawn as a wire.
- Every fitted part is rated for the fab's reflow profile **[fab capability]** (JLC Economic 255 ± 5 °C not adjustable; Standard 240 ± 5 °C).
  The parts-vetting checklist carries "≥ 260 °C peak per J-STD-020". A part at zero margin gets a bake / profile remark.
- Basic vs extended library: each unique extended part costs a feeder fee **[fab capability]** — the BOM report counts them; prefer basic /
  preferred parts for jellybeans (a stock floor per code is an owner choice, `references/part-verification.md`).

## 9. Two-sided SMT assembly
- The **owner chooses** single / two-sided **[owner choice]** (two-sided buys 30–40 % board area). Two-sided implies the
  fab's Standard tier (setup + second stencil fees) and requires edge rails / fiducials. A press-fit or THT step then needs a **fixture band**
  on the bottom: no bottom part within ±2 mm of a press-fit row over its length, and boss / screw-head keep-outs drawn on BOTH sides.
- **Part height per side** **[physics + convention]**: the side that reflows first (usually the lighter, smaller-part side) reflows a second
  time upside down. Parts heavier than ~30 g per square inch of pad area or tall parts (electrolytics, inductors > 4.5 mm) go on the second
  side or get glue. Glue is a remark, and the fab decides. Record per-side max height in the board yaml, because the case reads it.
- THT: unused PTH stay solder-free (say so in the remark); hand-installed parts are DNP in the BOM and marked on the fab drawing.

## 10. Polarity, rotation and the CPL **[convention + fab capability]**
- CPL file: `Designator, Mid X, Mid Y, Rotation, Layer`, mm, 4 decimals. Position = pad-bounding-box centre relative to the drill/place origin,
  Y up. Rotation is **CCW positive viewed from the top**; bottom rows use `(180 − rotation) mod 360`. BOM: `Comment, Designator, Footprint, <fab part
  field>`. DNP is excluded from both. **The generator hard-fails on an empty fab-code field on a fitted part. It never falls back to the MPN.**
- **The fab has no per-package zero-rotation table**: "zero = tape/reel orientation, corrected per the silkscreen" (JLC). Two community
  rotation databases disagree by 180° on SOT-23 and QFN. So the project keeps a **project-owned rotation table** (`20-design/<fab>_rotation.yaml`,
  footprint-name regex → offset, seeded from two databases, only agreeing rows `review: false`). The pack carries `rotation_log.csv`, which
  lists every applied offset. **The fab's 3-D placement preview is the only authoritative check** before paying. It is a G2 checklist item; a
  +90 for 1×N headers was confirmed only there.
- **The table grows from the fab's own rows, with a selftest** **[measured]**. After every assembled order, diff the fab's engineering file
  (`vendor-review.md` §5 round 4: `ec` vs `oc` per designator). Group the deltas by footprint. Write them into the rotation table as rules, with
  the order id as the source. The CPL generator's selftest regenerates the file and asserts every polarized part against the engineer rows.
  The next order of these packages then ships right the first time. One order taught four facts. A vendor-made (EasyEDA) footprint does not
  sit at the fab's zero just because the fab drew it. LQFP-64 needed +270, as the community tables said for the stock footprint. The `-BL` /
  `-BR` suffix of a vendor footprint is a different pin-1 corner and needs its own offset (SOT-23-6: `-BL` 0, `-BR` +90). The fab's package
  ORIGIN is not the pad-bbox centre (a USB-C receptacle +2.345 mm, slide switches +0.127 mm toward the board edge). A rule key `shift: [dx, dy]`
  covers it, in the footprint frame, rotated with the part and mirrored on the bottom. Two-pin passives come back normalised by 180° either
  way; ignore them. The
  board file needs no change for any of this — the table is the design file that was missing, and the ordered package stays frozen as evidence.
- Polarity mark on the silk of **every** polarised footprint. The fab places per silkscreen when it conflicts with the CPL. The marks: pin-1
  dot on every IC, cathode band / triangle on diodes, + on electrolytics, pin 1 on headers. The F.Fab layer carries the same marks for the
  assembly drawing.
- **Pre-answer the fab's engineer** **[convention]**: at G2, run a fab's-eye pass beside the silk check. Look for a polarised footprint whose
  only mark is on the bottom at an odd rotation, a mark under mask or a pad, or a custom footprint with no body outline on the fab layer. Each
  is a production-hold question waiting to happen; fix the footprint. The package ships `ASSEMBLY_NOTES` (`references/fab-dfm.md` §9). It
  holds renders with the cathode end / pin-1 corner per part class, body + pin 1 + mating direction of every custom-footprint connector, and
  the empty / unplated holes with finished sizes and tolerances. The order remark points at it. When the fab's engineer questions still come,
  answer them on the board's pad-1 positions, never on the CPL rotation (`references/vendor-review.md` §5–§7).

## 11. Fiducials, test points, silk, courtyards
- **Fiducials** **[fab capability]**: 3 per side that carries parts (1 mm copper, 3 mm mask opening, ≥ 5 mm from the edge, not on a symmetry
  axis), on the panel rails when panelised; Standard PCBA requires them, Economic does not.
- **Test points** **[owner choice + convention]**: one per rail and per bus line the bring-up tool reads (the criteria yaml names them). Pad
  ≥ 1.0 mm, ≥ 2.54 mm pitch where a probe clip is expected. Label each with the net name and purpose on the silk (self-documenting labels).
  Group them in a field with a legend grid. The test plan lists the coverage (T-nn ↔ TP).
- **Silk** **[fab capability + checker]**: line ≥ 0.15 (design 0.16+), text height ≥ 1.0 mm (labels 1.1–1.2), width:height 1:6, silk-to-pad /
  mask ≥ 0.15 (design 0.20). **No silk over pads, no via or PTH under a text cell.** Keep vias out of the text bbox at route time; clipping is
  for hairlines only. Check silk-to-edge against the TRUE outline polygon (notches). Check glyph stroke ≥ the minimum by a morphological
  opening. The font is either shipped with the repo or count-aware in CI, because a proprietary system font cannot run on the runner. A
  legibility gate READS the rendered PNG. Order number: "specify location" on a silk box or removed **[owner choice]**.
- **Placed artwork inside the outline** **[convention]**: an unsigned distance-to-outline test lets an off-board point pass. A "free space" test
  for placed copper or silk art combines point-in-polygon with the distance. The generator asserts every placed item lies inside the
  outline by the edge clearance. DRC did not flag copper outside the edge: marks across two tapered corners sat 1.68 mm outside the outline on
  a shipped board **[K]**. Gate row per layer: the Gerber copper bounding box lies inside the Edge.Cuts bounding box by the edge clearance.
- **Courtyards and tombstoning** **[fab capability + physics]**: body-to-body spacing per the fab's SMD spacing table (JLC: 0402↔0402 0.18,
  0603↔0603 0.25, chip↔QFN 1.0, QFN↔QFN 1.0, BGA↔BGA 2.0). In practice: ≥ 0.30 passives body-to-body, 0.50 where hand rework is expected,
  ≥ 1.5 mm around tall parts. Use symmetric pads and equal thermal mass on both ends of a chip part. One pad into a pour without relief
  tombstones the part. Courtyard overlap = DRC error, no exceptions.

## 12. Creepage and clearance for the voltage class **[physics + owner choice]**
Below 60 V DC / 30 V AC (SELV) the fab minimum spacing governs. Above it, the spec names the standard (IEC 60664-1 / IPC-2221 tables: pollution
degree, material group, working voltage). The layout then carries the creepage / clearance as a **generated rule** (a net-class-to-net-class
clearance), plus a slot where creepage needs it. State the class in the spec even when it is "SELV only — no creepage rule" (a decision row the
reviewer can read); an isolated section (USB isolator, mains) gets a keep-out zone on every layer and a drawn isolation barrier.

## 13. Panelization **[fab capability]**
- Standard PCBA needs every side ≥ 70 mm (JLC 2026-09-13), and the fab's automatic rails land on the SHORT edges. A narrow board needs a
  **customer panel**: 1-up + rails on the LONG edges (5 mm rails, Ø2 tooling holes, 1 mm fiducials on the rails). Use **mouse bites** (5 × Ø0.5
  tabs) where copper is < 0.40 mm from the break line (V-cut needs ≥ 0.40), with routed 2 mm slots between. Keep the drill/place origin
  unchanged so the panel CPL = board CPL + rail offset.
- Gate the panel on its STORED fills (`BuildConnectivity()` before every fill or pours starve). The gate: per-zone area within 1 % of the
  source, Gerber region count equal, DRC 0/0. Run the fab DFM on the PANEL zip too. A merged drill cannot mark mouse-bite holes NPTH; a remark
  settles the "unconnected via" warnings. Panel by customer REQUIRES the panel format field on the quote form.

## 14. DRC census: 0 errors / 0 warnings unless a dated waiver row
- Run `<cad-cli> pcb drc --severity-all --format json` on the committed board with **classes enforced**. KiCad honours only explicit
  `netclass_assignments`, never patterns, and no DRC exclusions: emit per-net assignments and rules from the generator. The census counts
  every severity per rule name (`gen/drc_count.py` style, cross-host: silk-text items dropped only when the font is absent, with a NOTE).
- **Zero errors, zero unconnected, zero warnings.** A warning that stays is a **dated waiver row** in `90-log/DECISIONS.md` (rule,
  item, reason, owner). A generated accept rule mirrors the row (`enclosedByArea` marker rule area per accepted item, not `insideArea`). DRC
  and the route-quality gate then accept exactly the same copper. A prose waiver the matrix cannot read does not count. The G2 cell and the board order
  require this bar (`templates/90-log/GATES.md`).
- **The canary rule** **[convention]**: one deliberately violated generated rule (a `CANARY` text or a marker area) must fire **exactly
  once** in every DRC run. It proves the rule file was parsed and the classes are enforced. A malformed `.kicad_dru` is silently ignored. A
  stricter rule than the class is invisible to the router and appears afterwards.

## 15. Route-quality classes **[convention + owner choice]**
Per net: routed / direct (MST over pads) meander ratio, segments, vias, layer changes, min/max width vs class, stubs, acute corners, layers used.
Board level: via total, copper per layer, inner-layer signal length not over solid reference copper, sensitive-net proximity (I²C / control /
sense / USB) to switching nodes and the crystal, and power corridor cross-section. The corridor needs ≥ N mm² per rail and ≥ 2 vias per
transition. Flags are graded
HIGH / MED / LOW; **0 unjustified HIGH** at G2, each HIGH either fixed through
the generator or a dated waiver row + accept rule (§14). The report is `route_quality.md` in the pack.

## 16. Schematic ↔ layout parity **[convention]**
Every symbol field is copied to the footprint as a hidden property (MPN, fab code, Confidence, DNP, Alt_*). Footprint attributes mirror the
symbol: DNP does not imply exclude-from-BOM, so set both. Net names and pin nets match between the exported netlist and the board. The parity
check lists every difference and G2 requires 0. A schematic regeneration must not rewrite the board-side project file (rules, classes) —
restore it from HEAD or merge (`references/pitfalls.md` tooling/gates).

## 17. Fab DFM mirror before the order, and the order-time stock freeze
- **Before the first quote and at every adopt**: mirror the fab's checker in-repo (`references/fab-dfm.md`). The mirror holds a thresholds
  JSON with source + date, a project measurer → items, the `scripts/dfm_check.py` grader, and acceptances by refdes with **date + reason +
  evidence**. Bare tracks / vias are never accepted. The mirror shows **0 open**: every item of either fab grade is fixed or accepted with
  vendor evidence. Then the fab's
  own viewer on the board AND the panel upload, counts diffed against the mirror, PDF export filed under `60-orders/quotes/<date>/`.
- **Stock**: every fitted code verified live with the run-relative minimum (`qty × boards × attrition`), owner floors on jellybeans; **once the
  order is PLACED the package is judged on the frozen `stock_snapshot.json`**, never on the live shelf (`references/fab-dfm.md` §8).

## 18. Where the numbers come from (worked example, JLCPCB 2026-09-13)
The PCB numbers come from `jlcpcb.com/capabilities/pcb-capabilities` (copper, drill, mask, silk, outline, tolerances). The PCBA numbers come
from `…/capabilities/pcb-assembly-capabilities` (Economic vs Standard: sides, min package 0402 / 0201, min pitch 0.4 / 0.35, reflow 255 / 240 °C,
rails + fiducials). The rest come from the help articles `pick-place-file-for-pcb-assembly`, `pcb-assembly-faqs-part-2` (rotation = tape
orientation, silkscreen governs polarity), `minimum-spacing-for-smd-components`, `Panelizing-your-PCB-for-Assembly`,
`in-what-cases-will-there-be-charged-extra`, and the stack-up template API (`getImpedanceTemplateSettings`). Fetch again, cite the date, and
keep the raw responses under `60-orders/quotes/<date>/`.
