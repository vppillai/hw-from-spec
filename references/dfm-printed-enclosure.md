# dfm-printed-enclosure.md — a vendor-clean printed enclosure in ONE DFM round

Rules as MEASURED on one project (AEC-CT2-MINI case v3.12 → v3.16, JLC3DP MJF PA12 + a Bambu Lab P2S at home, 2026-09-21 … 09-28): four vendor
rounds, five cracked trays, one failed home print, twelve full rebuilds. Everything below is what the next project does BEFORE its first quote.
Numbers are the vendor's (JLC3DP, labelled) or the printer's; substitute yours, keep the mechanism. The chain itself is `references/case-pipeline.md`;
the post-order review round is `references/vendor-review.md`; the script is `scripts/thin_wall_census.py`; the records are
`templates/CENSUS_GATE_ROWS.md` (check-table rows) and `templates/DFM_ROUND.md` (one file per quote-page session under `docs/quotes/<date>/`, API verdict + probes).

## 0. The acceptance bar (write it into the decision row before the first census)
**0 FAIL / 0 WARN in every check table and in the census of every body · zero slicer warnings · no vendor flag · no yellow, no red on the vendor's
heat map · every face rendered and looked at.** A WARN is not a verdict: a row either has a threshold (then it is PASS or FAIL on a MEASURED value) or
it has none (then it is **INFO**, in its own table, no verdict). "0 FAIL, 81 WARN" told the owner nothing and hid the row that cracked the part;
the same data as PASS / FAIL + INFO exposed a second defect nobody had seen (a dummy 0.4 mm low).

## 1. MJF (worked example: JLC3DP PA12-HP, grey line 1.2 mm)
- **Every parallel-faced wall ≥ 1.2 — design at 1.3.** A 1.2 nominal samples 1.19 on the mesh and prints 1.1 … 1.3; the map may read it yellow and the
  argument is lost. The 0.1 costs nothing on a 2 mm shell. "Wall" = any skin whose opposite face is within 30° of parallel, whatever the yaml calls it
  (lip, land, skin, floor, ring, cheek).
- **Every void ≥ 1.2.** The map colours voids too: slots, slits, grooves, boss-to-wall gaps, and engraved strokes — every 0.45 glyph was red, the 0.5 slot
  ends red, a 0.5 gap between a Ø8 boss and a wall yellow (web it). A cap-4 engraved stroke is a 0.82 void: **no engraved text on an MJF body** — put
  identity / labels on a label carrier (UV-printed metal plate in a rebate, adhesive label) or raise them on a separate plate.
- **No free-standing wedge.** JLC colours RED a thin edge with no wall behind it: 36° rail tips and lips (yellow / red full length), an added interior 45°
  roof cove (red on every wall), a fillet's thin edge. It leaves GREY a chamfer or 45° ramp cut INTO a ≥ 1.2 wall (tray and shell passed with them).
  So: chamfers into walls yes; added coves, fillets, rails, lips, knife edges no — round the tip or give it a ≥ 1.2 flat land, or remove the feature.
- **No living hinges, slit tabs, compliant detents on MJF.** A snap tab needs a 0.6 slit (a void → red); a rigid detent bump does not deflect in PA12 any
  more than in PETG (F ∝ t³). Fasten with screws into heat-set inserts (boss ring ≥ 1.3 around the bore); key rotation by the asymmetric openings.
- **A 141 mm × 0.88 mm skin WILL crack** (all five trays, from the free ends inward, MJF cooling / depowdering stress on the 4 mm wedge it carried). A long
  skin is a wall, never a "feature": anything spanning > 10 mm is judged at the wall minimum; a knife edge under 10 mm span is a feature — and under the
  no-yellow bar even that gets a flat land.
- **The vendor's metric is length-dependent** (§7.1): a rim over a skirt-lap step passed at 48 mm and failed at 88 / 147 mm with every census clean —
  rim over a lap step ≥ 2.0 OR the undercut filled; calibrate any long-wall profile with full-length probes, never with a coupon.
- **A feature that cannot be made vendor-clean inside its space budget goes; it is not thinned.** A stepped dovetail with 1.2 flats on lip AND tongue needs
  2.4 mm of depth; the groove had 2.15 before the next counterbore skin → rail off, screws, plain edges (a wider part with an ENCLOSED pocket rail is the
  owner's option, logged). Thickening one wall moves its neighbours (skirt 1.2 → 1.3 pushed the snap-tab force over its class; fixing that broke the catch
  minimum): **every wall change reruns the whole table, never one row.**
- **Rule drift check.** When the print rule changes (FDM two lines 0.85 → MJF 1.2), re-derive EVERY yaml value that was set against the old rule; a yaml
  comment `>= 0.8` beside a 0.9 wall is the tell (body-rail skin 0.90, cheeks 1.0, hole floors 1.0, a mark debossed 0.8 into a 1.2 band → 0.4 skins).
- **Overshoots become slabs.** A `+ 0.01` extrude used against coplanar-face artefacts is a 0.01 mm slab in the mesh = a RED line on the map (the step-wall
  ledge). Trim the union at the design face (intersection) and let the interference row prove 0.00 mm³; never exempt "coplanar seam slabs" in a check.

## 2. Waivers are not checks — the census is a FAIL gate
- A row `KEPT BELOW 1.2 (listed): …` with verdict `None` and yaml numbers is a waiver nobody signed. The cracked lip's row quoted the MALE profile (tip /
  neck); the female hinge (parting line − groove roof = 0.88) was never a measured quantity; the 0.90 skin next to it was judged against `feature_min`
  0.8 instead of `wall_min` 1.2. **Every thin feature gets a measured number from the MESH (not the yaml), a span and a class (wall / void / wedge).**
- **The ray-cast census is a FAIL gate per print preset** (`scripts/thin_wall_census.py`, `templates/CENSUS_GATE_ROWS.md`), not a one-off review aid:
  inward rays = wall thickness, outward rays = void width; clusters below `gate − 0.05` (at the gate itself the nominal 1.2 walls sampled 1.19 join every
  region into one 145 mm cluster); each cluster classified by the angle between the sample face and the hit face (< 30° = wall, ≥ 30° = wedge); only
  walls and voids gate, wedges are listed and each must be a chamfer / ramp backed by a wall — otherwise remove it. A **SANITY row** = the vendor's
  colouring reproduced: fraction of wall-class surface below `gate − 0.05` and of void-facing surface below it must equal the noise floor measured on a
  known-good primitive (a 1.3 plate + Ø8 boss + Ø3.4 hole: 0.00 % / 0.00 %). Legend lands between debossed strokes are deboss-deep features judged at the
  red band (0.5) and "inside the hull of the lands it touches", not "inside one land" (a block of strings merges into one cluster).
- **A PURE gate in the adopt list**: the census JSON beside each STL carries the STL md5 and the FAIL list; `thin_wall_census.py --gate <dir>` proves
  md5 = the committed STL and 0 FAIL without recomputing (the chain did the census; the gate proves the record matches the mesh of record).
- The census that "passed" the old preset never gated the vendor build: give EVERY preset its FAIL rows on day 1 (the `p2s` preset got them after the
  order; the `jlc` preset after the crack).

## 3. Vendor heat map = strength finding
A heat map yellow "full length" along a feature is a strength finding, not cosmetic: file it as an owner decision **with the number** ("the lip hangs on
0.88 × 141; it may crack; accept?") or fix it. "Kept (design geometry)" with no strength argument is how the order went out. The vendor's picture is
evidence only together with the uploaded file's md5 AND the API's `parseStatus 2` / `thinWall` for that upload (§7); the material on the line does not change the flag.

## 4. Closed rims (the owner's visual bar)
Every rim and wall reads CLOSED on the single part: no through-slot, notch, key gap or slit visible from any face unless it has an obvious job
(connector, vent, LED, switch, screw). A coupling groove open along a wall, a lead-in notch at a sill, a key notch at a skirt edge, a snap-tab slit —
all functional, all read as "literal gaps … a broken design" by the owner in the vendor's viewer. Coupling features that need a slot belong INSIDE a wall
as an enclosed pocket, in a wider part, or not at all.

## 5. Designed asymmetries and the visual review
- A designed asymmetry that looks like a defect (foot pockets 1.0 mm inboard beside concentric counterbores) is **rendered, printed in the order sheet
  and listed in KNOWN_ISSUES §1** — a yaml note, a passing check row and one guide sentence did not stop the owner reading the printed part as "holes not
  concentric". Better: remove the asymmetry when the reason for it goes (no groove → concentric pockets); measure concentricity from the mesh (circle fit
  in sections, families within 0.2).
- **Render every face, the sole included** (six orthographic faces per piece, `faces/`), and ask of each "will a technician or the vendor photograph
  this and read it as broken?". The sole with the off-centre pockets HAD been rendered; nobody asked the question.

## 6. INFO vs WARN, and the numbers in the rows
- Verdict table: PASS / FAIL only, every row a measured value against a stated threshold. INFO table: measured values with no threshold (heights, cone
  angles, supported ceilings, feasibility notes). `None` must render as INFO, never as WARN.
- Accepted-with-note items (a wall printed AT the minimum, shrunk legends) are PASS rows whose note says so and whose value is measured, not a WARN.
- Quote the mode with every number (check mode vs full `--stl` run totals differ) and the STL md5 the census describes.

## 7. Vendor quote-page procedure (worked example: JLC3DP, 2026-09-28, corrected the same evening — verify live, they change)
1. **One STL per page session, reload between uploads.** With several lines present the page opened the wrong file's analysis twice. The hidden
   `input[type=file]` can be unhidden by script (`el.classList.remove('hidden')` / `style.display=''`) and given the file without the file chooser;
   uploads and the analysis work **signed out** — the DFM read needs no login (ordering does). Name the uploaded copy `<piece>_<version><round>_<md5-8>.stl`.
2. **The verdict of record is the analysis API, not the page.** The page polls `GET …/tdpFile/getFileAnalyzeResult?fileAccessId=…`; read it from the
   browser's network log (or re-request the same URL) and accept it only when `parseStatus == 2` (analysis complete). Then `modelAnalysisVO.thinWall`
   (bool) IS the flag; `modelAnalysisVO.previewUrl` opens the heat-map viewer directly (the Analysis Results tab), `volume` / bbox must equal yours.
   **A DOM reading taken before parseStatus 2 is invalid**: two "no flag" rows were read that way and the API later said `thinWall: true` on the same
   file — the tray would have been ordered on a false pass. A verdict without `parseStatus 2` + file md5 in the record is not evidence.
3. **The flag is computed at UPLOAD and does not depend on the process / material chosen on the line.** Setting MJF / PA12-HP on the line (Edit
   dialog SAVED — form state, not a cart) is still done first: it gives the price of the order and the legend of the material's heat map, and the
   record names the material on the line BEFORE reading anything. But changing the material never flips `thinWall`; a verdict that "changed with the
   material" was two different reads (one premature). The page defaults to **9600 Resin** after an upload.
4. **Open the heat map on every face** even when `thinWall` is false (`previewUrl` exists either way): inside, sole, iso top, front; the legend is a
   colour scale (grey ≥ 1.2, yellow 0.5–1.2, red < 0.5) — the census turns a colour into a number.
5. **Save screenshots named `<piece>_<round>_<md5-8>_<material>_heatmap_<face>.png`** plus `quote_page_<round>_flags.png`, keep the uploaded STL beside
   them, and write `templates/DFM_ROUND.md` into `docs/quotes/<date>/` with the API fields (`parseStatus`, `thinWall`, volume) per body.
6. **When a verdict flips between two uploads, diff the meshes before touching the generator**: the r3 tray read RED where the r2 tray had passed —
   same 4088 triangles, every vertex within 7.7e-6 mm (ASCII vs binary container). The coordinator's candidate fixes were plausible and all wrong; the
   real difference was a premature DOM read (step 2). An ASCII twin of the identical geometry is the cheap A/B for container sensitivity.
7. **Canonical STL, or the md5 means nothing.** OpenSCAD 2021.01 writes the same CGAL geometry in a different triangle order on every export (three
   exports = three md5s); trimesh's exporter writes run-dependent NORMALS for identical vertices. Write the binary STL yourself: round vertices, rotate
   each triangle to its smallest vertex, sort triangles, recompute normals from the float32 vertices, 50-byte records — prove idempotence AND equality on
   a copy from another run before calling a hash "the geometry". The census gate, the vendor uploads and the production cut key on that md5.
8. **A coordinator verifies a worker's "no flag" claim itself** (re-request the API for the md5 in the record) before a decision row says PASS — the
   false passes above were relayed claims (`references/agent-ops.md` §6).

### 7.1 The vendor's thin-wall metric is LENGTH-DEPENDENT — calibrate with probes, in one round (worked example: JLC3DP MJF PA12-HP, 147 mm tray)
Three independent ray-cast censuses (60 k … 400 k samples) found nothing under 1.37 mm on a tray JLC read RED along both long walls: the trip was a
**rim 1.4 mm above a skirt-lap step with a 0.9 mm inward undercut** — opposing faces that never overlap, and a metric that reads a long wall differently
from a short one. **An identical wall profile passed at 48 mm and failed at 88 and 147 mm.** A wall that passes on a coupon can fail on the part; a
40 mm probe that passes proves nothing about a 147 mm body.
- **Calibrated rule (MJF PA12 at ~150 mm parts):** a rim above a skirt-lap step must be **≥ 2.0 mm** (1.4 fails; 2.0 passes with the step AND the inward
  undercut kept — probes K2 wall 2.6 / rim 2.0 and K5 lap 0.9 / rim 2.0 both `thinWall: false`), **OR the undercut is filled** so the inner wall runs
  straight from the floor to the rim top (`lap.ring_down: true` — then a 1.25 … 1.3 rim above the step passed on the full tray; the mating skirt still
  registers on the kept step, partner overlap 0 mm³). Stay grey: plain 2.0 walls, 2.0 floors, boss rings, chamfers cut into ≥ 1.2 walls, 45° dish
  ramps. Red: free-standing wedges (rail tips, lips, added coves / fillets). A rim thinner than 2.0 over an undercut is the one geometry every census
  passed and the vendor failed — put it in the census as a named row (`rim over a lap step ≥ 2.0 OR undercut filled`).
- **The probe method (converges in ONE quote-page round, ~2 h):**
  1. *Localise*: cut the FAILING body of record (the archived md5 file) into capped slabs with `trimesh.intersections.slice_mesh_plane(mesh, n, o,
     cap=True)` — front / middle / rear, 40 … 60 mm each, then an 88 mm and the full length — upload each ALONE, read the API. The slice that first
     turns `true` localises the feature AND shows the length threshold (here ≤ 60 false, 88 true).
  2. *Isolate*: build plain-profile probes with OpenSCAD — one 2-D `polygon()` of the wall section (floor, wall, lap step, rim, undercut) extruded
     to **40 mm AND to the full part length**, closed box with 2.0 end walls, no bosses, **one knob per probe** (`WALL_T`, `LAP`, `RIM_IN`, `FILL` via
     `-D`): as-is, rim flush 2.0, wall +0.6, undercut filled, rim 2.0 via the lap. Upload each alone; the API answers in seconds.
  3. *Decide*: the first knob whose FULL-LENGTH probe reads false and whose geometry the mating part tolerates becomes the yaml change; the census gets
     the rule as a row; the probe folder (`docs/quotes/<date>/<round>/probe/` with the `.scad`, `.stl`, heat-map PNGs and a `PROBES.md` table
     probe | what | thinWall) is the evidence. A scaled-down copy of the body (0.6 ×) is not informative (every wall scales).
  4. *Record*: `PROBES.md` names the method (API, parseStatus 2, one file per session), every probe with its knob and verdict, the rule adopted, and
     the re-verification of every body of record by the API — the round's DFM_ROUND.md points at it.

## 8. FDM at home (worked example: Bambu Lab P2S, 0.4 nozzle, PLA / PETG) — printer-first preset
A census that passes on paper is not a print: the FDM preset had 0 FAIL and failed as a product (bad finish, supports on visible faces, illegible text,
3 bosses under a 4-hole fan, a detent that blocked the slide, a raw board mesh that wrecked the print). Rules now enforced as FAIL rows:
- Every EXTERNAL face on the bed, vertical, or a clean top — the mesh outer-face assertion (0 support-touched outer clusters), not a WARN; visible bridges
  ≤ 10 mm; interior support area stated per body.
- **Walls ≥ 1.6** (a two-line 0.85 skirt / rim / tab is a FAIL, not "thin"); ribs ≥ 1.2; voids ≥ 1.0 (a 0.4 nozzle clears a 1.0 slot).
- **Legends RAISED**: cap 4 / stroke ≥ 1.0 / height 0.6 on a face-up top (a 0.4-deep, 0.45-wide debossed void at cap 2.2 is illegible on a 0.4 nozzle however
  good the printer); raised text cannot print face-down (the plate bridges over the glyphs) — a face-down face gets debosses or flush colour bodies. A fit
  filter keeps a legend only where it fits its land and LISTS what it dropped so the owner sees what a coupon answer buys back.
- No rigid bump on a slit tab (it blocks, F ∝ t³); screws + heat-set inserts in ≥ 1.6 boss walls instead of snap tabs where the arm cannot be long enough.
- **Fan boss count = fan hole count** (consumer 30 mm fans have 4 holes even when one SKU drawing shows 3); any point set drawn in two places (SCAD `for`
  over four corners vs a Python 3-point list) is passed to the SCAD as ONE vector.
- Hood ROOF-DOWN with no supports: a roof recess printed roof-down is a ceiling → drop it (the fan locates on its screws); screws + inserts hold the hood.
- **Test coupons BEFORE the part** (15–25 min prints, generated from the SAME yaml numbers and SCAD modules as the part): text strokes × caps in the real
  font (raised face-up, debossed face-up, debossed face-down), wall thicknesses, mating clearances; the numbers they decide are a yaml parameter block
  (legend cap / stroke / depth, rail clearance) so the answer is a 3-number edit + regenerate. Ship the coupons in every kit.
- **Board dummy, never the raw CAD mesh** (0.25 mm sheet metal, 0402s, 0.1 mm pins are unprintable): slab + holes + solid envelopes + fins at printable
  thickness, in the board frame, bbox stated against the mesh of record. **Two versions, both kept**: the two-piece glue version (a scribed locator ring
  0.6 × 0.2 OUTSIDE the tall part's footprint locates it without a pocket — a compensating plinth lifts an overhang off the bed = a floating-region
  warning; a pocket stacks the glued part low by its depth) AND the **one-piece version (D-84 pattern)**: cage / sink fused to the slab in its exact
  position at FINAL dimensions; a nose that overhangs the board edge stands on a **break-away shim** — a 1.2 mm block on the bed, inset 0.5 from the
  nose sides, 0.6 clear of the board edge, joined to the nose floor through 8 posts 1.2 × 1.2 across a 0.4 mm two-layer perforation gap (the bottom
  layer bridges ≤ 5 mm between posts without a warning; the shim snaps off in one piece, stubs trimmed flush). **Say in the README that the shim looks
  like a "PCB lip" and comes off** — the owner read it as part of the board. Verify the one-piece against the two-piece by **section symmetric
  difference = 0 mm²** at several Z (slab, cage, sink) and both bboxes against the cage envelope of record; the generator asserts the bbox equality.
- **Slicer projects with every setting embedded**: flatten the system presets (`inherits` chains), give the project preset ITS OWN NAME (`<system> - <project>
  <plate>`) and list the differing keys in `different_settings_to_system` — a project naming a system preset with that list empty is reconciled back to
  the system values when the GUI opens it (supports OFF → "floating regions", while the CLI slice was clean). Open with File → Open Project, never Import.
  Slice every object ALONE headless; **a floating-region warning is a build FAIL** (a 36° overhang triggers it at the 30° threshold), the only exceptions are
  documented per plate and none should be left at release. Auto-orient every non-text piece (score the face-down choices by down-facing area above the
  bed, then bed contact; bake the rotation into the STL): a plate the owner must rotate by hand is a generator defect. One material knob (PLA / PETG) read by
  the 3MF builder, the print sheets and every README, with the material caveat printed (PLA softens ~55–60 °C: a hood over a hot module is a fit mock-up).
- Hand over ONE kit folder: case pieces + coupons + BOTH board dummies (two-piece and one-piece, each with its 3MF) + every project file + READMEs
  (case, coupons, dummy); a moved folder keeps a `README_MOVED.md` pointer. The kit is regenerated with the preset — a stale kit folder from the
  previous version is named for deletion in the record.

## 9. Two versions from one yaml (vendor MJF + home FDM)
Presets `base + overrides` deep-merged before any module reads the yaml (`references/case-pipeline.md` §Presets); the geometry may differ wherever the
printer needs it (split legend plate, raised legends, 1.6 walls, screws) while the envelope, bezel, windows and any coupling stay shared. Every
variant-only generator line sits behind **hook tokens that expand to the ORIGINAL text for the other presets** (`HOOKS_DEFAULT` / `HOOKS_<preset>`), and the
variant gets **its own version key** (`presets.<p>.version`) instead of bumping `case.version` — the SCAD header carries the version, so a bump alone
re-keys every cached STL of record. Prove byte identity before committing: `Case(base).scad() == git show HEAD:<scad>`.

- **The home preset mirrors every vendor DFM decision the same day** (owner: "once that closes apply those findings to the p2s version as well"):
  rails off, key off, closed rims, undercut filled (`lap.ring_down`), feet concentric, hood on screws — applied to the p2s preset in the SAME yaml with
  its own version key (`presets.p2s.version`) and a comment naming the vendor round that decided it. Its gate is its own census (walls 1.6 / ribs 1.2 /
  voids 1.0, legends by the coupon rule) + the slicer log clean on every plate; the STLs, 3MFs and the kit folder regenerate with it. A vendor-only
  fix (a fill that exists only where MJF needed it) is a divergence the two-units-must-mate check has to prove harmless (partner overlap 0 mm³).

## 10. Post-mortem pattern (when the vendor reports cracked / deformed parts)
1. **Measure the ordered STL** (the archived md5, not the current file): sections through the failure with the numbers on them, the census with span and
   class; photos mapped feature by feature to the model (a table: photo feature | model | designed / defect).
2. **Separate design intent from defect**: the "designed gap" the vendor points at may be correct AND the crack beside it may be yours; the off-centre hole
   may be designed and still a finding (it looks broken). Say which is which, with numbers.
3. **Write the accept-and-ship reply with the number** ("the lifted strips are the 0.9 mm skin over 141 mm cracking; that is our file, please ship") — the
   owner sends it; do not claim a printing defect for a designed feature; a goodwill credit is the owner's call.
4. **Apply the learning design-wide, not to the failed feature**: census every body of every preset, re-derive every value set against the old rule, turn
   every waiver row into a measured row, render every face, then the vendor's own DFM on every replacement body — and only then a new order. Expect ~12
   full builds for the first design-wide pass; commit after each (`references/agent-ops.md` §2).
