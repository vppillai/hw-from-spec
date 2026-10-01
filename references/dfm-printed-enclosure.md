# dfm-printed-enclosure.md — a vendor-clean printed enclosure in ONE DFM round

Rules as MEASURED on one project (the source project's two-piece case, MJF PA12 at JLC3DP + a home FDM printer, 2026-09-21 … 09-28): four vendor
rounds, five cracked trays, one failed home print, twelve full rebuilds. Everything below is what the next project does BEFORE its first quote.
The chain itself is `references/case-pipeline.md`; the post-order review round is `references/vendor-review.md`; the script is
`scripts/thin_wall_census.py`; the records are `templates/CENSUS_GATE_ROWS.md` (check-table rows) and `templates/DFM_ROUND.md` (one file per
quote-page session under `docs/quotes/<date>/`). SLA is §11, CNC is `references/cnc-enclosure.md`.

**Every number here carries a tag** — the same four as `references/pcb-layout-dfm.md`: **[checker]** = what the vendor's thin-wall map colours
(JLC3DP, read 2026-09-28, on ~150 mm parts); **[vendor sheet: URL, date]** = a published capability or tolerance; **[physics]** = the material;
**[owner bar]** = the bar the owner set (no yellow on the map, closed rims); **[convention]** = what the scripts rely on. **No number lives in a
script**: every gate value is read from `project.yaml print_targets.<target>` (`references/project-yaml.md`), and the numbers quoted below are the
source project's targets, labelled.

## 0. The acceptance bar (an owner decision at kickoff; written into the decision row before the first census)
**0 FAIL / 0 WARN in every check table and in the census of every body · zero slicer warnings · no vendor flag (API read) · no yellow, no red on
the vendor's heat map · every face rendered and looked at · no waivers.** A WARN is not a verdict: a row either has a threshold (then it is PASS
or FAIL on a MEASURED value) or it has none (then it is **INFO**, in its own table, no verdict, **with the reason it has no threshold**). "0 FAIL,
81 WARN" told the owner nothing and hid the row that cracked the part; the same data as PASS / FAIL + INFO exposed a second defect nobody had
seen (a dummy 0.4 mm low). The only exception path is the machine-readable `accepted` list (§2) — dated, with the vendor's written evidence.

## 1. MJF rules (worked example: JLC3DP PA12-HP; checker grey line 1.2 mm)
- **Three numbers, three sources — never confuse them** (B-15): the vendor's **published printable minimum** (JLC review mail: "nylon ≥ 1.0";
  Shapeways / Sculpteo / HP direct list 0.6–1.0 for PA12) **[vendor sheet]**; the **checker's yellow line** (JLC3DP heat map: grey ≥ 1.2, yellow
  0.5–1.2, red < 0.5) **[checker]**; and the **owner's bar** (no yellow → design at `wall_gate + design_margin` = 1.2 + 0.1 = 1.3) **[owner bar]**.
  A team at another vendor or without the no-yellow bar designs to a different number; the mechanism (design above the line the checker
  flags, by a margin the sampling and the process spread need) is what generalises. A 1.2 nominal samples 1.19 on the mesh; the 0.1 margin
  costs nothing on a 2 mm shell.
- **Every parallel-faced wall ≥ `wall_gate`, designed at `wall_gate + design_margin`** **[checker + owner bar]**. "Wall" = any skin whose opposite
  face is within 30° of parallel, whatever the yaml calls it (lip, land, skin, floor, ring, cheek).
- **Every void ≥ `void_gate`** **[checker]** — the map colours voids too: slots, slits, grooves, boss-to-wall gaps, engraved strokes (every 0.45
  glyph red, 0.5 slot ends red, a 0.5 gap between a Ø8 boss and a wall yellow → web it).
- **Engraved text is ALLOWED on MJF** (standard practice: stroke ~0.8–1.0, depth ~0.5 per vendor guides **[vendor sheet]**) **when the stroke ≥
  `void_gate`** — at 1.2 that means cap height ≥ ~6 mm. Under a no-yellow bar with cap 4 (a 0.82 stroke) it does not fit → widen the text, or a
  label carrier (UV-printed plate in a rebate, adhesive label), or raised text on a separate plate. Do not delete legibility the space allows.
- **No FREE-STANDING wedge** **[checker]**: the map colours RED a thin edge with no wall behind it — 36° rail tips and lips (yellow / red full
  length), an interior roof cove unioned without tangency (a knife-edge sliver), the 0.01 mm overshoot slab. It leaves GREY a chamfer or 45° ramp
  cut INTO a ≥ `wall_gate` wall. **Tangent fillets cut into ≥ gate walls are fine and recommended at stress risers** (they lower the ~1.2× slit-
  root concentration the FEA reference reports) **[physics]**; what went red was a non-tangent cove body and a fillet's exposed thin edge. So:
  chamfers and tangent fillets into walls yes; added free edges, rails, lips, knife edges no — round the tip, give it a ≥ gate flat land, or
  remove the feature.
- **Snap fits, living hinges, compliant detents: PA12 CAN do them** **[physics]** (E ≈ 1.7 GPa, elongation at break 15–25 %; HP's MJF design
  guide shows both). What killed them on the source project was (a) the ≥ `void_gate` slit a no-yellow bar demands at JLC3DP, which rarely fits
  the space budget, and (b) a rigid bump with no arm length (F ∝ t³ — a stiff bump blocks, in PA12 as in PETG). Allowed when the slit ≥ the void
  gate and the arm is engineered (length, root fillet, FEA); otherwise screws into inserts or magnets (§1.1). On PLA / FDM: screws.
- **A long thin skin is a wall, never a "feature"** **[owner bar + physics]**: a 141 mm × 0.88 mm skin **cracked on 5 / 5 parts** of one geometry
  (from the free ends inward; likely causes cooling / depowdering stress on the 4 mm wedge it carried — not fractographed, see §10). Design
  consequence: anything spanning > 10 mm is judged at the wall minimum; a knife edge under 10 mm span is a feature — and under the no-yellow bar
  even that gets a flat land.
- **The vendor's metric is length-dependent** (§7.1) **[checker]**: a rim over a skirt-lap step passed at 48 mm and failed at 88 / 147 mm with
  every census clean — rim over a lap step ≥ 2.0 OR the undercut filled; calibrate any long-wall profile with full-length probes, never a coupon.
- **A feature that cannot be vendor-clean inside its space budget goes; it is not thinned.** A stepped dovetail with 1.2 flats on lip AND tongue
  needs 2.4 mm of depth; the groove had 2.15 → rail off, screws, plain edges (a wider part with an ENCLOSED pocket rail is the owner's option).
  Thickening one wall moves its neighbours (skirt 1.2 → 1.3 pushed the snap-tab force over its class; fixing that broke the catch minimum):
  **every wall change reruns the whole table, never one row.**
- **Two owner rules can collide inside one feature** (a legend-plate lip needed inset ≥ 0.6 against a top fillet, its web beside a dish needed
  inset ≤ 0.45 to stay a "wall"): the way out is honest classification — a plate is a plate, its webs are ribs at the rib gate — never a thinner
  wall under a friendlier name.
- **Rule drift check.** When the print rule changes (FDM two lines 0.85 → MJF 1.2), re-derive EVERY yaml value set against the old rule; a yaml
  comment `>= 0.8` beside a 0.9 wall is the tell.
- **Overshoots become slabs.** A `+ 0.01` extrude against coplanar-face artefacts is a 0.01 mm slab in the mesh = a RED line on the map. Trim
  the union at the design face (intersection); never exempt "coplanar seam slabs" in a check.
- **Dimensional tolerance is the vendor's, not ±0.1** (B-01) **[vendor sheet]**: MJF PA12 is typically ±0.3 mm or ±0.3 % (HP: ±0.2 mm below
  100 mm, worse above — cite the vendor's sheet with URL + date in `print_targets.<t>.tolerance_source`). A 1.3 wall can print 1.0–1.1. "A 1.2
  nominal prints 1.1 … 1.3" is an **assumption until the first-article caliper table exists** (§10 step 1); the measured spread of every gated wall
  and bore on the received parts feeds `print_targets.<t>.tolerance` and the design margin — until then the margin row is INFO, not PASS.
- **Build orientation and anisotropy** (B-38) **[vendor sheet + physics]**: MJF Z-direction strength is ~10–20 % below XY (HP data — check the
  vendor's sheet), FDM 30–50 % across layers; ask the vendor for the build orientation / position when the part matters (a cantilever, a boss under
  screw preload) and record it in `DFM_ROUND.md`. Draft angles: **n/a for MJF / SLA / FDM**; required if the design is ever moulded — say so in the
  brief so a reader does not think it was forgotten.

### 1.1 Retention hardware: inserts, screws, magnets — per material
| Material | Insert / fastener | Bore and depth | Boss OD / wall | Notes |
|---|---|---|---|---|
| **MJF PA12** | thread-forming screws for plastics (Delta PT / Remform class) into a plain pilot are the usual choice **[vendor sheet]**; heat-set inserts work but at a higher iron temperature (Tm ≈ 178 °C **[physics]**) — set the temperature from the insert TDS; press-fit / self-tapping inserts also fine | from the insert or screw manufacturer's TDS, never a rule of thumb; insert 0.1–0.2 below flush | boss OD ≥ 2 × insert OD (~3 mm wall around an M3 insert) **[physics]**; the source project's 1.3 ring is marginal for hoop stress at insertion — labelled so | pull-out / torque to failure on the coupon (§8) before the value goes on the SOP as `[OWNER: …]` |
| **PLA (FDM)** | heat-set inserts at the TDS temperature; **creep under screw preload above ~45 °C** **[physics]** → the FDM preset is a fit / assembly mock-up unless PETG / ASA and the thermal case says otherwise | TDS bore, drilled/reamed if hole shrink (§8) matters | ≥ 1.6 boss wall at 0.4 nozzle (4 perimeters) — a 1.3 ring around an M3 heat-set insert in PLA is a known crack site | insert + torque coupon in the kit (B-42) |
| **PETG** | as PLA; softens ~75–80 °C **[physics]** | | | |
| **Magnets** (D-85 pattern) | Ø6 × 3 N42 / N45 disc pairs (a standard, easy-to-find size), Ni coating; **max operating temperature N35/N42 ≈ 80 °C, N35H / N42H 120 °C** **[vendor sheet]** — record grade + coating on the BOM line | pocket Ø = magnet Ø + fit: **MJF glued (CA) Ø + 0.4, PLA light press Ø + 0.1** (drill / ream the 6.35 imperial size if that is what arrives); depth = magnet + 0.3 recess each side | pocket walls ≥ `wall_gate`; boss OD ≥ pocket + 2 × wall | **pull force vs gap** from the supplier's curve at (2 × recess + lap gap), stated on the row ("15.7 N at touch, N at 0.9 mm"); **polarity keying** by an asymmetric boss (Ø10 left / Ø11 right) — a debossed dot beside a Ø6.4 pocket in a Ø10 boss leaves 0.25 mm lands (yellow) and a raised dot in a 0.3 lap gap collides; hobby-standard discs (Ø6 × 3, Ø4 × 2) exist only in N35 … N52 (80 °C) at vendors whose pages render without a login — the H / SH grades start at 2 × 2 / 4 × 4 and need a distributor; the mating part's steel counterpart (screw head, plate) is the cheap half |

Retention is a kickoff question (`references/kickoff-questionnaire.md`): screws + inserts (recommended for a part that is opened for service),
magnets (tool-free, for a hood the technician lifts daily), none (friction lap only — a fit mock-up). Whatever is chosen, **the retention feature
must exist in the exported mesh of the version ordered** — a blind review found a "retained" hood whose STLs carried no bosses (the check rows had
read the yaml, not the mesh — every retention row measures the MESH).

### 1.2 Post-processing effects (B-16) **[vendor sheet + physics]**
Dyeing adds no dimension; **bead-blast / vapour smoothing removes 0.05–0.15 mm per surface and rounds edges** — a `wall_gate + 0.1` wall and a
1.0 legend stroke lose that; SLA post-cure warps thin flat plates; FDM sanding / ironing of a top face flattens raised legends. Rule: **every
post-process is named on the order sheet and on the print target (`print_targets.<t>.post_process`) and is subtracted in the census margin.**

### 1.3 Material rating and thermal (B-36) **[vendor sheet + owner bar]**
An enclosure holding a powered board: state per target on the order sheet **UL 94 rating and Tg / softening point** (PA12 MJF: typically HB;
PLA: unrated, softens ~55–60 °C; PETG ~75–80 °C; resins per the TDS), keep vents away from the hot zone, and record the owner's acceptance
**"engineering sample, not a rated enclosure"** as a decision row (the questionnaire asks it). A hood over a hot module in PLA is a fit mock-up.

### 1.4 Tolerance stack (B-37) **[convention]**
The interference check proves 0 mm³ overlap on NOMINAL meshes. Add a **worst-case clearance row per mating pair**: nominal clearance −
Σ tolerances ≥ 0 (case ±`tolerance` from the target, board outline ±0.2, insert position, connector float, post-process removal). A pair that
binds at worst case is a FAIL row, not a note. **Fit clearances are per-preset knobs** (`presets.<p>.overrides.fits.*`), never numbers in the
base block: FDM holes shrink ~0.1–0.3, MJF ±0.3, SLA ~0.1 — the coupon decides each (B-23).

## 2. Waivers are not checks — the census is a FAIL gate

The census gates the DESIGN margin per `print_targets.<t>`; the printability FLOOR (walls, roots, knife edges, point contacts, voids, holes,
size — from physics + the cited process minimums, vendor-independent) is `scripts/print_dfm.py --process <row>` on the same mesh before every
upload, with the verdict → validate → rule-fix → retro loop in `references/print-dfm.md`. Both are PURE adopt gates; neither reads the yaml.
- A row `KEPT BELOW 1.2 (listed): …` with verdict `None` and yaml numbers is a waiver nobody signed. The cracked lip's row quoted the MALE profile
  (tip / neck); the female hinge (parting line − groove roof = 0.88) was never a measured quantity. **Every thin feature gets a measured number from
  the MESH (not the yaml), a span and a class (wall / void / wedge / opposing).**
- **The ray-cast census is a FAIL gate per print preset** (`scripts/thin_wall_census.py --target <t>`, rows `templates/CENSUS_GATE_ROWS.md`):
  inward rays = wall thickness, outward rays = void width; clusters below `gate − 0.05` (**convention**: at the gate itself the nominal 1.2 walls
  sampled 1.19 join every region into one 145 mm cluster); each sample classified by the angle between the sample face and the hit face (< 30°
  = wall, ≥ 30° = wedge — the 30° is a **convention**, not calibrated) and **the two classes clustered separately** (one mixed cluster that chained
  across a body through chamfer flanks was labelled "wedge" and swallowed a 1.0 … 1.2 lip and 1.3 slot lands; when the rail went, both surfaced); **walls and voids FAIL below their gates; wedges FAIL when the band of
  surface below the gate is wider than `wedge_band`** (default 1.5 mm — the width from the thin edge to where thickness reaches the gate; a
  chamfer cut into a wall has a band of ~1 mm and no free edge, a 35° free rail flank has ~1.8) unless an `accepted` entry names the backing
  wall (B-12); **the nearest OPPOSING face in ANY direction is gated too** (B-14): two faces whose normals oppose within 30° and whose distance is
  below the gate FAIL whether or not a normal ray from one hits the other — the ledge underside 0.5 from a step top, a ring face 0.4 from a wall
  plane, the 0.4 mm root of a rim ring set inboard of its wall: the class the vendor found and the normal-ray census did not (§7.1).
- **Samples scale with surface area** (`samples_per_mm2`, default 10; 60 000 fixed samples on a 150 mm tray were 1–2 / mm² and a 0.6 × 4 mm slit
  gets a handful) (B-13). **Recall is selftested**: a plate with one 0.8 mm rib and one 0.6 mm slit must produce one WALL FAIL and one VOID FAIL.
- **The NOISE-FLOOR row** (was "SANITY = the vendor's colouring reproduced" — it is not; it measures false positives, not recall): fraction of
  wall-class surface below `gate − 0.05` and of void-facing surface below it, equal to the floor measured on a known-good primitive (a plate +
  boss + hole at the gate + margin: 0.00 % / 0.00 %). **Known blind spots** of the census, listed here so nobody calls it complete: bbox-scale
  effects of the vendor's own resolution (§7.1), contacts under 0.05 mm (`thin_wall_check.py --pinch`), and anything a *slicer* adds (supports
  on visible faces are read from the g-code, §8).
- **The `accepted` list** (`print_targets.<t>.accepted`, B-31) mirrors the board's `dfm_accepted`: entries `{class, bbox, reason, date, evidence}`
  — a FAIL cluster whose bbox lies inside an entry's bbox (1 mm tolerance) with the same class is machine-matched every run and listed as
  ACCEPTED (with the entry's evidence path: the vendor's written acceptance, a first-article measurement); an entry without date / reason /
  evidence does not count. Nothing else moves a FAIL.
- **A PURE gate in the adopt list**: the census JSON beside each STL carries the STL md5 and the FAIL list; `thin_wall_census.py --gate-dir <dir>`
  proves md5 = the committed STL and 0 unaccepted FAIL without recomputing.
- Give EVERY preset its FAIL rows on day 1 (the home preset got them after the order; the vendor preset after the crack).
- Legend lands between debossed strokes are deboss-deep features judged at the red band (`red_line`) and "inside the hull of the lands it
  touches", not "inside one land" (a block of strings merges into one cluster).
- **INFO rows added since the previous round are listed in the gate merge** (B-29) — an INFO table is the new escape hatch if a row can move
  there by deleting its threshold; each INFO row states why it has none.

## 3. Vendor heat map = strength finding
A heat map yellow "full length" along a feature is a strength finding, not cosmetic: file it as an owner decision **with the number** ("the lip
hangs on 0.88 × 141; it may crack; accept?") or fix it. "Kept (design geometry)" with no strength argument is how the order went out. The vendor's
picture is evidence only together with the uploaded file's md5 AND the API's `parseStatus 2` / `thinWall` for that upload (§7).

## 4. Closed rims (the owner's visual bar) **[owner bar]**
Every rim and wall reads CLOSED on the single part: no through-slot, notch, key gap or slit visible from any face unless it has an obvious job
(connector, vent, LED, switch, screw). Coupling features that need a slot belong INSIDE a wall as an enclosed pocket, in a wider part, or not at all.

## 5. Designed asymmetries and the visual review
- A designed asymmetry that looks like a defect (foot pockets 1.0 mm inboard beside concentric counterbores) is **rendered, printed in the order
  sheet and listed in KNOWN_ISSUES §1** — or removed when the reason for it goes. Measure concentricity from the mesh (circle fit in sections;
  families within `concentricity` — 0.2 mm is a **convention** from one part family).
- **Render every face, the sole included** (six orthographic faces per piece, `faces/`), and ask of each "will a technician or the vendor photograph
  this and read it as broken?".

## 6. INFO vs WARN, and the numbers in the rows
- Verdict table: PASS / FAIL only, every row a measured value against a stated threshold. INFO table: measured values with no threshold and the
  reason (heights, cone angles, supported ceilings, feasibility notes). `None` must render as INFO, never as WARN.
- Accepted-with-note items (a wall printed AT the minimum, shrunk legends) are PASS rows whose note says so and whose value is measured.
- Quote the mode with every number (check mode vs full `--stl` run totals differ) and the STL md5 the census describes.

## 7. Vendor quote-page procedure (worked example: JLC3DP, 2026-09-28 — verify live, they change)
0. **Consent first** (B-19): uploading a design to a third-party quote page is a disclosure. The decision row that opens the round quotes the
   owner's consent to upload and cites the vendor's terms page (read once, URL + date); a vendor whose terms claim rights to uploaded files is a
   BLOCKER, not a shrug.
1. **One STL per page session, reload between uploads.** With several lines present the page opened the wrong file's analysis twice. The hidden
   `input[type=file]` can be unhidden by script; uploads and the analysis work **signed out** (ordering does not). Name the uploaded copy
   `<piece>_<version><round>_<md5-8>.stl`.
2. **The verdict of record is the analysis API, not the page.** The page polls `GET …/tdpFile/getFileAnalyzeResult?fileAccessId=…`; read it from
   the browser's network log (or re-request the same URL) and accept it only when `parseStatus == 2`. Then `modelAnalysisVO.thinWall` (bool) IS
   the flag; `modelAnalysisVO.previewUrl` opens the heat-map viewer; `volume`, surface area and bbox must equal yours (**same geometry parsed, same
   scale — a 10 × unit error gives a clean map and a wrong quote**). **A DOM reading before parseStatus 2 is invalid**: two "no flag" rows were read
   that way and the API later said `thinWall: true` on the same file. **Save the RAW JSON response** to `docs/quotes/<date>/<md5-8>_analyze.json`
   with URL, timestamp and response headers — not three fields (B-17). **Site-changed branch**: endpoint or field missing → BLOCKERS row, the
   verdict class downgrades to "page popover + screenshot", the round is NOT YET until the API read is restored or the owner accepts the weaker
   evidence in a D row. **Capability-page snapshot** once per round: PDF / print of the vendor's published design rules with the date, so the
   numbers in `print_targets` can be re-derived when the site changes.
3. **The flag is computed at UPLOAD and does not depend on the process / material chosen on the line.** Setting the material (Edit dialog SAVED —
   form state, not a cart) is still done first: it gives the price and the legend of the material's heat map; the record names the material on the
   line and **the quote price per body** before reading anything. Changing the material never flips `thinWall`. The page defaults to a resin.
4. **Open the heat map on every face** even when `thinWall` is false: inside, sole, iso top, front; record **the legend thresholds as displayed
   that day** — the census turns a colour into a number.
5. **Save screenshots named `<piece>_<round>_<md5-8>_<material>_heatmap_<face>.png`** plus `quote_page_<round>_flags.png`, keep the uploaded STL
   beside them, and write `templates/DFM_ROUND.md` into `docs/quotes/<date>/` with the API fields, the browser / UA / signed-in state per body.
6. **When a verdict flips between two uploads, diff the meshes before touching the generator**: the r3 tray read RED where the r2 tray had passed —
   same 4088 triangles, every vertex within 7.7e-6 mm. The real difference was a premature DOM read (step 2).
7. **A coordinator verifies a worker's "no flag" claim itself** (re-request the API for the md5 in the record) before a decision row says PASS.

### 7.1 The vendor's thin-wall metric is LENGTH-DEPENDENT — calibrate with probes, in one round (JLC3DP checker, 2026-09-28, 147 mm tray)
Three independent ray-cast censuses (60 k … 400 k samples) found nothing under 1.37 mm on a tray JLC read RED along both long walls: the trip was a
**rim 1.4 mm above a skirt-lap step with a 0.9 mm inward undercut** — opposing faces that never overlap. **An identical wall profile passed at
48 mm and failed at 88 and 147 mm.**
- **Hypothesis and its test** (B-05): a checker with **bbox-relative voxel / sampling resolution** produces exactly this — on a 147 mm body each
  voxel is coarser, so a 1.4 mm rim over a 0.9 undercut smears below 1.2. If so: (a) the margin needed scales with the LARGEST bbox dimension,
  not the wall's length; (b) probes must match the body's bbox in all three axes (a full-length but shallower probe reads finer); (c) ANY
  near-threshold feature on a larger next part will flip, not only a rim over a lap step. **Test**: the same profile at the same length in a taller
  / wider closed box; if the taller box flips, the rule is "margin ∝ max bbox dimension" and `print_targets.<t>.max_bbox_for_rule` records the
  size the rule was calibrated at. Until tested, the calibrated rule below is stated for ~150 mm parts only.
- **Calibrated rule (this checker, this size):** a rim above a skirt-lap step must be **≥ 2.0 mm** (1.4 fails; 2.0 passes with the step AND the
  inward undercut kept), **OR the undercut is filled** so the inner wall runs straight from the floor to the rim top (a yaml `undercut filled`
  knob — then a 1.25 … 1.3 rim above the step passed on the full tray; the mating skirt still registers on the kept step, partner overlap 0 mm³).
  Stay grey: plain 2.0 walls, 2.0 floors, boss rings, chamfers cut into ≥ 1.2 walls, 45° dish ramps. Put it in the census as a named row and in the
  opposing-face metric (§2), which measures the ring root the normal rays missed.
- **The probe method (converges in ONE quote-page round, ~2 h):**
  1. *Localise*: cut the FAILING body of record (the archived md5 file) into capped slabs with `trimesh.intersections.slice_mesh_plane(mesh, n, o,
     cap=True)` — front / middle / rear, 40 … 60 mm each, then an 88 mm and the full length — upload each ALONE, read the API. The slice that first
     turns `true` localises the feature AND shows the length threshold.
  2. *Isolate*: plain-profile probes with OpenSCAD — one 2-D `polygon()` of the wall section extruded to **40 mm AND to the full part length**,
     closed box with 2.0 end walls, no bosses, **one knob per probe** (`-D`): as-is, rim flush 2.0, wall +0.6, undercut filled. Upload each alone.
  3. *Decide*: the first knob whose FULL-LENGTH probe reads false and whose geometry the mating part tolerates becomes the yaml change; the census
     gets the rule as a row; the probe folder (`docs/quotes/<date>/<round>/probe/` with `.scad`, `.stl`, PNGs and `PROBES.md`) is the evidence. A
     scaled-down copy of the body is not informative (every wall scales).
  4. *Record*: `PROBES.md` names the method, every probe with its knob and verdict, the rule adopted, and the API re-verification of every body.

### 7.2 Canonical STL and the geometry signature **[convention]**
OpenSCAD 2021.01 writes the same CGAL geometry in a different triangle order on every export (three exports = three md5s); trimesh's exporter
writes run-dependent NORMALS for identical vertices. Write the binary STL yourself: round vertices, rotate each triangle to its smallest vertex,
sort triangles, recompute normals from the float32 vertices, 50-byte records — prove idempotence AND equality on a copy from another run before
calling a hash "the geometry". The census gate, the vendor uploads and the production cut key on that md5. **Beside the md5 record a geometry
signature** (volume, area, bbox, facet count, rounded to 1e-3) (B-20): two STLs that differ by a 1e-6 vertex jitter are "different geometry" to
the md5 and identical to the signature — a flipped verdict on "identical" geometry is diagnosed in one line instead of a mesh diff.

## 8. FDM at home (worked example: Bambu Lab P2S, 0.4 nozzle, 0.20 mm layers, PLA / PETG, Bambu Studio 02.08) — printer-first preset
A census that passes on paper is not a print: the FDM preset had 0 FAIL and failed as a product (bad finish, supports on visible faces, illegible
text, 3 bosses under a 4-hole fan, a detent that blocked the slide, a raw board mesh that wrecked the print). Rules enforced as FAIL rows — the
numbers are **[owner bar]** for a 0.4 nozzle at 0.20 mm and live in `print_targets.home_fdm`:
- Every EXTERNAL face on the bed, vertical, or a clean top — **asserted from the sliced g-code in the 3MF** (`; FEATURE: Support` extrusions
  outside the outer-wall hull = a scar on a visible face), not only from the mesh's down-facing analysis; visible bridges ≤ 10 mm; interior
  support area stated per body.
- **Walls ≥ 1.6** (4 perimeters; a two-line 0.85 skirt / rim / tab is a FAIL), ribs ≥ 1.2, voids ≥ 1.0 (a 0.4 nozzle clears a 1.0 slot);
  **minimum feature = 2 × line width** (0.8–0.9 at 0.42 line) **[physics]**.
- **Elephant foot** (B-11): the first 2–3 layers flare 0.1–0.15 mm on a textured plate at 55 °C — a 0.30 lap clearance loses that at the seam;
  chamfer the bottom edge 0.3–0.5 × 45° on mating skirts or use the slicer's elephant-foot compensation (0.1), recorded on the print sheet.
- **Hole shrink**: vertical holes print 0.1–0.3 mm under nominal **[physics]** — compensate in the preset's `fits` block (per-preset, coupon-decided)
  or ream; state which on the print sheet.
- **Seam placement**: the seam is set to the rear / a hidden edge in the slicer project (recorded key), never on a legend face.
- **Layer anisotropy**: a tab or boss loaded across layers is 30–50 % weaker; boss walls shear along layers — orient bosses so the load is in-plane
  where possible, and read the FEA with the anisotropy factor.
- **Legends RAISED**: cap 4 / stroke ≥ 1.0 / height 0.6 on a face-up top (a 0.4-deep, 0.45-wide debossed void at cap 2.2 is illegible on a 0.4
  nozzle); raised text cannot print face-down — a face-down face gets a flush colour body (§8.1 option b), never a deboss (its recess ceiling is a bridge underside). A fit filter keeps a legend only where it
  fits its land and LISTS what it dropped.
- No rigid bump on a slit tab (it blocks, F ∝ t³); screws + heat-set inserts in ≥ 1.6 boss walls, or magnets (§1.1), instead of snap tabs where the
  arm cannot be long enough.
- **Fan boss count = fan hole count** (consumer 30 mm fans have 4 holes even when one SKU drawing shows 3); any point set drawn in two places is
  passed to the SCAD as ONE vector.
- Hood ROOF-DOWN with no supports: a roof recess printed roof-down is a ceiling → drop it; **put the roof on the bed by `rotate([180,0,0])`, never
  `mirror()`** — a mirror flips handedness and every asymmetric mark prints backwards; check the export against the board-frame mesh with a
  proper-vs-improper rigid-match row.
- **Test coupons BEFORE the part** (15–25 min prints, generated from the SAME yaml numbers and SCAD modules): text strokes × caps in the real font
  (raised face-up, debossed face-up, debossed face-down), wall thicknesses, mating clearances, **an insert + screw coupon (three bosses: install,
  torque to failure, record)** (B-42); the numbers they decide are a yaml parameter block. Ship the coupons in every kit.
- **Coupons are self-documenting** (owner rule, 2026-09-30): every test coupon and every variant on a bracket plate carries its own
  identifier and the value it tests ON the part — debossed or raised text with the number (e.g. `W1.6 R0.20`, `WALL 1.6`, `CLR 0.30`), on an
  ironed top face or a face-up plate, cap ≥ 4 mm, stroke ≥ 1.0 raised / ≥ 0.45 debossed, lands ≥ 0.45 between glyphs (measured, FAIL-gated),
  never on a bridge underside or a deep inner wall. A coupon the user has to look up in a README to identify is a coupon that gets mixed up on
  the bench; the slicer's object names are gone the moment the part comes off the plate. The marker is generated from the same yaml value it
  tests, so it cannot disagree with the geometry.
- **Board dummy, never the raw CAD mesh** (sheet metal, 0402s, 0.1 mm pins are unprintable): slab + holes + solid envelopes + fins at printable
  thickness, in the board frame, bbox stated against the mesh of record. **Two versions, both kept**: the two-piece glue version (a scribed locator
  ring 0.6 × 0.2 OUTSIDE the tall part's footprint locates it without a pocket — a compensating plinth lifts an overhang off the bed = a
  floating-region warning) AND the **one-piece version**: cage / sink fused to the slab at FINAL dimensions; a nose that overhangs the board edge
  stands on a **break-away shim** (worked example: a 1.2 mm block on the bed, inset 0.5 from the nose sides, 0.6 clear of the board edge, joined
  through 8 posts 1.2 × 1.2 across a 0.4 mm two-layer perforation gap; the shim snaps off in one piece). **Say in the README that the shim looks
  like a "PCB lip" and comes off.** Verify one-piece vs two-piece by **section symmetric difference = 0 mm²** at several Z and both bboxes against
  the envelope of record. Model compressible envelopes (EMI springs) at the compressed width or the dummy jams the bezel.
- **Slicer projects with every setting embedded** (Bambu Studio 02.08 specifics, labelled): flatten the system presets (`inherits` chains), give
  the project preset ITS OWN NAME and list the differing keys in `different_settings_to_system` (a project naming a system preset with that list
  empty is reconciled back to system values when the GUI opens it — supports OFF → "floating regions"). Open with File → Open Project, never
  Import. Slice every object ALONE headless; **a floating-region warning is a build FAIL**. Auto-orient every non-text piece and bake the rotation
  into the STL. One material knob (PLA / PETG) read by the 3MF builder, the print sheets and every README, with the material caveat printed
  (§1.3). **A generator that refuses to overwrite its artefact on a failed run leaves the OLD 3MF on disk while the sidecar describes the new
  one** — the analysis must read the file it names (md5 in the sidecar checked before any forensics).
- Hand over ONE kit folder: case pieces + coupons + BOTH board dummies (each with its 3MF) + every project file + READMEs **+ a generated
  `START_HERE.md`** (print order with the project-file names, assembly sequence, numeric report-back with a recipient) and the **kit text gate**
  over every emitted text — `references/print-kit.md`; a moved folder keeps a `README_MOVED.md` pointer; a stale kit folder is named for deletion
  in the record.

### 8.1 Brand marks / logos on FDM parts — an OWNER choice at kickoff (questionnaire C9); worked example: a filled chevron mark 10–18 mm wide, three marks on one product, 2026-09-29
The finish of a mark is decided by WHICH FACE carries it and HOW that face is built, not by the slicer profile. Two options are first-class
(owner: "ironed surface and bottom ams are both viable options"); pick one per product, or ship both as plates when the printer has an AMS:
- **(a) TOP-face feature under ironing.** The mark is a deboss 0.6 deep (= 3 whole layers at 0.20, measured on the mesh) or a raised body 0.6
  high on a face that is a TOP face of the print, and the plate profile irons **ALL top surfaces: `ironing_type: top` — never `topmost`**
  (`topmost` irons only the highest face and skips the recess floor, which recreates the very texture mismatch the option exists to avoid).
  **Top shell ≥ recess depth + 1.0** (worked example: `top_shell_layers 7` = 1.4 under a 0.6 recess) so no sparse infill shows through the
  recess floor; floor and face are then both topmost solid surfaces built by the same pass. **Orient the part so the marked face IS a top
  face**: a cap prints mouth down (blind pocket rising from the bed, flange on the bed, the closed end = the marked top face, §8.2); a plate
  prints face-up. The mark is read directly, not mirrored. Cost: one filament, ironing adds ~5 min on a small plate.
- **(b) BOTTOM-face flush AMS colour body in the bed layers.** The marked face goes ON THE BED and the mark is a separate solid body in the second
  filament occupying the first N layers of that face — flush, no recess, no bridge, no ironing: both colours are bed contact and the colour
  boundary is a first-layer perimeter in XY, the crispest mark FDM can make. **The mark is mirrored in the model** (proved by a render from −Z
  against the artwork as drawn). **Default 2 layers = 0.4** (a dark mark on a dark body is opaque at two layers; only layer 1 is ever seen);
  **3 layers for a light mark on a dark body**. Cost = 2 filament changes per 2 colour layers + purge (worked example: the third layer = +2
  swaps, +0.66 g purge, +3 min); it scales with the coloured layer count, not with the mark area — keep the count a knob, slice every variant.
- **NEVER:** a **bed-face deboss** (the recess ceiling is a bridge underside — strands beside a glossy bed-contact face: the "webbing" people
  remember on debossed logos); a **vertical-wall deboss** (stair-steps every horizontal edge at the layer height); **webs / discs / closing
  fillets that alter the artwork** to satisfy a land rule (they read as dimples — fix the rule set to the artwork, never the artwork to the rule
  set: point contacts stay point contacts and fuse over one line width, which is the artwork's own look).
- **The mark must sit on a bed face and there is no AMS → a separate face-up printed PLATE glued into a keyed rebate** (worked example: plate
  41 × 22 × 1.6, rebate 0.4 deep + 0.2/side clearance leaving ≥ the wall gate of roof, one chamfered corner = rotation key, glued chamfer to
  chamfer). A bed-face rebate on a roof-down body is a bridge ceiling even when hidden: **split any rebate span > 10 mm with full-height lands
  that double as glue lands** (worked example: 22.4 mm split by two 2.0 lands into three 6.1 mm bridges) instead of filing a covered-face
  exemption — an unsplit span sags into the rebate and rocks the plate.
- **All marks on one product share the reader orientation of the legends** — rotate, never mirror; prove each with a render against the
  artwork as drawn (proper-vs-improper rigid-match row: proper ≈ 0, mirror ≫ 0). "Apply the rule to the other marks too" is an AUDIT, not a
  patch: list EVERY instance of the feature class across every body and preset, state each verdict in a FAIL-gated row, then change.

**Mark geometry rows (FAIL-gated; measured on the same 2D polygon the CAD imports and on the exported mesh).** "Minimum gap" of a filled mark is
ill-posed (a chord through a boundary point is ~0; the medial axis reaches every convex vertex with width → 0; hull minus ink adds slivers) —
measure the FAILURE MODE instead:

| Row | Gate | Failure it guards |
|---|---|---|
| recess span = largest inscribed circle of each recessed region | ≤ 6.0 mm wherever the recess ceiling is a bridge; kept on an ironed top-face recess (a compact recess irons flat) — reduce the mark width, never the depth | bridge sag / an un-ironed floor |
| enclosed first-layer island (a solid region the recess or the colour body encloses), inscribed Ø | ≥ 2.5 mm, else close the recess over it | the island joins the body only above the recess |
| colour-region width, EITHER colour (option b) | ≥ 0.84 mm = two 0.42 first-layer lines; separate lobes touching at points are fine (a colour region is not a void) | a one-line region does not print |
| point-contact necks | INFO: they fuse over ~one line width at the print | the artwork's own look |
| mark to every edge of its face (and to a lug root) | ≥ 1.5 mm (≥ 1.0 to a lug) | the face's perimeter lines |
| depth / height | whole layers on the MESH (0.6 = 3.00 × 0.20) | a partial layer is a slicer guess |
| material behind a recess | ≥ the target's `rib_gate` (1.2) AND ≥ the profile's top shell | strength; infill show-through |
| chirality | proper rigid match ≈ 0 against the artwork; mirror ≫ 0 | a mirrored brand |

A mesh footprint measured from facet CENTROIDS under-reads the extent (11.66 vs 12.53 on a rounded rectangle) — every bbox row uses the
VERTICES of the selected facets. **A mark COUPON prints first on the plate** — the marked face alone (worked example: the cap's 2.0 mm closed
end with the identical mark). It checks the PRINTER-dependent part (first-layer squish, ironing quality / recess-floor finish, colour opacity);
the geometry rows guarantee the rest — the report says which is which.

### 8.2 Dust caps / protective covers (worked example: a QSFP-DD plug cap, 2026-09-29)
- **No through-hole may open into the protected cavity** — a lanyard hole is a dust path. Tether = an **external lug outside the cavity**,
  support-free: standing on the bed, hole axis vertical, wall around the hole ≥ the wall gate (1.6) outboard and inboard to the mouth.
- **Print MOUTH DOWN**: the lip flange flat on the bed, mouth chamfer ≤ 45°, **ribs / crush beads start ≥ 1.0 above the bed** so elephant foot
  never widens a fit surface, the pocket tip face is the ONLY bridge (≤ 10 mm; sag lands in the tip gap); profile: elephant-foot compensation
  0.15 + 0.5 mm first-layer lines, thin-wall detection on for the mouth rim, thick bridges off. FAIL rows: chamfer angle, lip footprint = the
  full lip (vertex extents), rib start Z, bridge span, material under the mark (§8.1).
- The pocket corner radius comes from the mating part's DRAWING, not a print rule of thumb (a module corner R 0.15 is clipped by a pocket
  R > 0.66); ribs bear on the faces the drawing shows SOLID (a QSFP-DD module is open at its bottom leading edge and recessed on top).
- The README states the first-print knobs, one per print (fit clearance OR rib proud), with the expected calliper readings.

### 8.3 Bambu Studio CLI facts (02.08.x, 2026-09-29 — verify on your build)
- `sparse_infill_density: 100%` is **rejected by the validator (rc -18 "Invalid parameter value(s)")** with any pattern; 90 % passes. Force a
  solid column with `top_shell_layers` / `bottom_shell_layers` (or their thickness keys) instead.
- A **two-filament slice with the prime tower on SEGFAULTS (rc -11 / 133, no result.json, log ends "no filament colors found in projects")**
  unless every filament profile carries `filament_colour`: write **one filament JSON per slot with its colour** (or `--filament-colour
  '#RRGGBB;#RRGGBB'`, undocumented in `--help`). One filament, or two without the tower, slice fine. Bisect a crash or a rejected 3MF on the
  temp inputs (5 s per run), one variable / key group per run, before touching the generator.
- **Multi-material = ONE multi-part object with a per-part `extruder`.** The CLI has no flag for it but loads a Bambu-style 3MF (the source
  project's `write_ams_3mf`; copy the package layout from a file Studio exported, ids are global):
  ```
  [Content_Types].xml, _rels/.rels                 standard OPC
  3D/3dmodel.model         <model … xmlns:p="…/3dmanufacturing/production/2015/06" requiredextensions="p">
                             <resources><object id="O" type="model"><components>
                               <component p:path="/3D/Objects/object_n.model" objectid="P1" transform="1 0 0 0 1 0 0 0 1 0 0 0"/>
                               <component p:path="/3D/Objects/object_n.model" objectid="P2" …/></components></object></resources>
                             <build><item objectid="O" transform="1 0 0 0 1 0 0 0 1 x y z"/></build></model>
  3D/Objects/object_n.model   <object id="P1" type="model"><mesh>…</mesh></object>  one per part (body, mark)
  3D/_rels/3dmodel.model.rels one Relationship per object file
  Metadata/model_settings.config
      <config><object id="O"><metadata key="extruder" value="1"/>
        <part id="P1" subtype="normal_part"><metadata key="extruder" value="1"/></part>
        <part id="P2" subtype="normal_part"><metadata key="extruder" value="2"/></part></object>
      <plate><metadata key="plater_id" value="1"/><model_instance><metadata key="object_id" value="O"/>
        <metadata key="instance_id" value="0"/></model_instance></plate></config>
  ```
  Slice with `--arrange 0` (the parts stay where the layout put them). Alternative route: pre-placed part STLs with `--load-filament-ids 1,2
  --assemble --arrange 0` — same colour requirement.
- **Report filament per colour and purge per plate**: per-filament grams from `Metadata/slice_info.config`, filament changes from the g-code
  (`M620 S..A`). Purge + tower mass is NOT in the header — derive it as used − (part volume × density) **only for a SOLID part** (the 2–3 layer
  colour mark); a 20 % infill body gives a negative "purge" — report the mark filament's share and say the body's cannot be separated.
- The CLI takes the same STL path N times as N objects (`--arrange 1`) — a "four caps" plate needs no multi-body STL; the object count comes
  from the CLI's `objects` list, not from the (deduplicated) inputs.
- `different_settings_to_system` lists only keys whose value differs from the flattened system preset: a project value equal to the system
  default is embedded but not listed — prove a setting from the embedded value, not from the list.
- State per plate in the kit README: minutes, grams per filament, filament changes, purge — ironing adds ~5 min on a small plate; each extra
  coloured layer adds swaps + purge + minutes.

### 8.4 Glued plates in rebates on a bed face (worked example: hood mark plate 40.8 × 21.8 × 1.4 in a 41.4 × 22.4 rebate, 2026-09-30)
- **The lands are the datum, the bridged strips sit one layer BELOW them.** A plate whose grooves rest on the land tops while its underside
  touches the bridge ceilings stands on the sag humps (0.1..0.3 at a 6 mm span) and rocks. Strip ceiling = land top − `sag_gap` (0.2 = one layer)
  under the part, so sag cannot lift the plate; FAIL rows: seat datum (gap 0.20), proud height (1.2), **working clearance after elephant-foot
  compensation on BOTH parts ≥ 0.1** (0.3 − 2 × 0.1 EF … measured on the meshes, not the yaml).
- **Clearance for a glued plate: 0.3 per side** (CA fills; 0.2 was a 0.0..0.1 working fit after EF). **Widen the PLATE's clearance by shrinking
  the plate, never by widening the rebate**: the rebate lip to the roof fillet is a census wall — +0.1 per side took a 1.6 lip to 1.53 = FAIL. The
  rebate footprint stays where the census approved it (41.4 × 22.4); the plate went 41 × 22 → 40.8 × 21.8.
- If deepening the strips would thin the roof under the span below the wall gate (1.4 under 6 × 41 mm), **thin the PLATE instead** (1.6 → 1.4
  keeps proud 1.2 and the skin over a groove = the rib floor 1.2). No waiver: the equivalent geometry with the same datum logic.
- One chamfered corner = the rotation key; "a rotated plate stands on the corner — do not force" is on the sheet; CA on the lands only.

### 8.5 Snug-fit features (crush ribs, press lips) and the 45° limit (worked example: QSFP-DD cap ribs, 2026-09-30)
- **Ship a bracket plate, let the owner pick after one print**: the fit knob at three values (rib proud 0.20 / 0.25 / 0.30), one object each,
  named by its value in the 3MF; START_HERE: bracket → coupon → plate (`references/print-kit.md` §4). An **interference-window row per variant**:
  rib-to-rib vs the mating part's tolerance (module 18.35 ± 0.1) AND the print tolerance (± 0.15) → per-side interference nominal ± 0.125; a
  window that reaches 0 or a knife edge at either end is a FAIL, not a note.
- **A face at exactly 45.0° is AT the overhang limit, not under it**, and the same face changes class with the orientation: a lip cone faces UP
  on the mouth-down cap (harmless) and DOWN on the closed-end-down AMS cap (a visible overhang). **Orientation-dependent knob** (`lip.cone_deg_ams`
  50 where it is an overhang, 45 where it is not) plus a **measured steepest-overhang row per print orientation** (bridges and the deliberate side
  debosses excluded). A rib lead-in taper scales with the rib height (a fixed 0.30 taper on a 0.30 rib was exactly 45.0°).
- **Watertight row per exported STL** and a `legend_edge` margin for raised legend items (§ print-kit.md §5): a slicer drops or fills a
  non-manifold sliver silently and still says "clean".

## 9. Two versions from one yaml (vendor MJF + home FDM)
Presets `base + overrides` deep-merged before any module reads the yaml (`references/case-pipeline.md` §Presets); the geometry may differ wherever
the printer needs it (split legend plate, raised legends, 1.6 walls, screws or magnets) while the envelope, bezel and windows stay shared —
**fit clearances are NOT shared numbers** (§1.4): every mating dimension is a per-preset `fits` knob, the coupon decides each. Every
variant-only generator line sits behind **hook tokens that expand to the ORIGINAL text for the other presets**, and the variant gets **its own
version key** (`presets.<p>.version`). **A hook that references a variable the preset never defines expands to NOTHING** — no error, a body
exported with the feature missing (a hood shipped a day without counterbores): every hook variable is asserted defined per preset, and every
check row reads the MESH, not the yaml. **Duplicate yaml keys are gated**: PyYAML keeps the LAST of two duplicate keys silently (`body_rail:
{enabled: false}` followed by `body_rail: {land: …}` re-enabled a rail the README said was off) — load every design yaml through a
duplicate-aware SafeLoader and fail on a duplicate. Prove byte identity before committing: `Case(base).scad() == git show HEAD:<scad>`.

- **The home preset (`home_fdm`) mirrors every vendor DFM decision the same day** (owner: "once that closes apply those findings to the home
  version as well"): rails off, key off, closed rims, undercut filled, feet concentric, hood on screws or magnets — applied to the home preset in
  the SAME yaml with its own version key and a comment naming the vendor round that decided it. Its gate is its own census (`print_targets.home_fdm`)
  + the slicer log clean on every plate. A vendor-only fix is a divergence the two-units-must-mate check proves harmless (partner overlap 0 mm³).

## 10. Post-mortem pattern (when the vendor reports cracked / deformed parts)
1. **Measure the RECEIVED part** (B-21a): a caliper / pin-gauge table of every gated wall and bore on the failed part AND on a good region —
   that table is the real process spread and feeds `print_targets.<t>.tolerance` (§1). **Photo protocol**: scale bar in frame, raking light, the
   feature ID written on the part, both sides of a crack, one overview per face. **Fractography basics**: origin vs propagation direction (river
   marks, the fastest region is the origin), brittle vs ductile surface, crack path relative to the build layers (along a layer plane = cooling /
   layer bond; through layers = overload / handling). **Ask the vendor** for the build orientation / position in the build and the post-process
   route. **Retain the failed parts**, labelled with the order line id.
2. **Measure the ordered STL** (the archived md5, not the current file): sections through the failure with the numbers on them, the census with
   span and class; photos mapped feature by feature to the model.
3. **Separate design intent from defect**, then decide who is at fault with the table:

   | Finding | Vendor at fault | Our file |
   |---|---|---|
   | a dimension outside the vendor's published tolerance | yes — reprint or credit | |
   | the part is not the file (missing feature, wrong scale, wrong material / colour) | yes | |
   | contamination, unfused powder, layer delamination in a ≥ gate wall | yes (process) | |
   | a wall / feature below the vendor's published minimum that the checker did not flag | shared — say so | fix the design anyway |
   | a designed feature the checker coloured and the round accepted | | ours: "that is our file, please ship" |
   | a designed asymmetry read as a defect | | ours: render + order-sheet line |

4. **Reply template** (the owner sends it; wording lives in `templates/VENDOR_REVIEW_RECORD.md` §3): facts (order, line, file md5), what we
   measured (numbers, photos), what we changed (new md5, what moved), what we ask (ship as is / reprint at our cost / reprint at the vendor's cost /
   credit), what we do NOT accept. Never claim a printing defect for a designed feature; a goodwill credit is the owner's call.
5. **Apply the learning design-wide, not to the failed feature**: census every body of every preset, re-derive every value set against the old
   rule, turn every waiver row into a measured row, render every face, then the vendor's own DFM on every replacement body — and only then a new
   order. Expect ~12 full builds for the first design-wide pass; commit after each.

## 11. SLA (resin) rule set (worked example: JLC3DP 8000 / 9600 resins, 2026-09-22 … 23 — verify live) **[vendor sheet + physics]**
- **Two minimums, two meanings** (B-09): the quote page's Edit dialog refuses a PART smaller than 2 mm in its thinnest overall dimension (a
  plate); the review mail asks for **walls ≥ 0.8** ("resin ≥ 0.8"). Design walls at 1.0 (0.8 + margin), plates ≥ 2 mm thick, and record both
  numbers in `print_targets.<sla target>` with the page and mail as sources.
- **Minimum feature / emboss 0.3–0.5, engraved stroke ≥ 0.4, hole Ø ≥ 0.5** (vendor guides); a point contact (0.01 mm) is a broken part: `--pinch`.
- **Hollow bodies need drain holes** (≥ 2 × Ø3 at the lowest print point) or the part traps resin and cups; a large flat face parallel to the
  plate causes **cupping / suction** — orient at 10–20° or accept the support scars on that face (the vendor decides orientation; ask and record).
- **Supports** land on the down-facing faces the vendor chooses: state the visible faces on the order sheet ("no supports on the top face")
  and accept a scar elsewhere.
- **Post-cure warp**: thin flat plates (< 2 mm, > 40 mm span) warp 0.2–0.5 mm after UV post-cure — rib them or accept; **UV yellowing** of clear
  resin within weeks in daylight; **brittleness**: the standard 8000 / 9600 class resins are stiff and brittle (elongation a few %) — no snap
  fits, no press fits, no thin cantilevers; the inlay plate that arrived "in pieces" was point-contact geometry in a brittle resin.
- Colour / dye adds a day; the material rating (§1.3) per the TDS — most standard resins are unrated and soften < 60 °C.
