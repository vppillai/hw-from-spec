# case-pipeline.md — enclosure from one yaml to prints and quotes


## 0. Imported body — the owner already has the CAD (`scripts/step2stl.py`)

The chain of record assumes every body is generated from `20-design/case.yaml`. A part that exists as a STEP (the owner's bracket, a vendor's housing)
enters M1 as a **generated-only exception** (SKILL §2). `scripts/step2stl.py part.step --out 40-case/<target>/parts/<piece>.stl --tag V|K` converts
it. The converter is cadquery in the venv, else the FreeCAD CLI, else `--canonical` on an STL exported from the CAD. The script prints the routes when
none is available; OpenSCAD cannot read STEP. The script writes the **canonical STL** (sorted triangles, float32 normals: the md5 is the geometry). It
also writes `<piece>.stl.provenance.json` (source, source md5, tag, converter, tolerance, stl md5, geometry signature, date). It prints the decision
row: OPEN, "imported body <piece>", and the chain of record (source md5 → converter → STL md5 + signature). A changed source or signature = a new row.
From there the body is gated like a generated one. The gates are `thin_wall_census.py --target <t> --json 40-case/<target>/checks/census/<piece>.json`
and `print_dfm.py --process <row> --out .../dfm` records of the same md5, six face renders, and clearance rows. In the M1 row, `scripts/step2stl.py
--canonical <export> --out <piece>.stl` replaces `gen/<geometry>.py --check`. It must reproduce the committed md5 (the provenance sidecar's
`stl_md5`). A body whose source changes re-enters through a new conversion and a new row. Editing the STL by hand is never a route.

## Chain (one yaml, one generator, every step keyed on content)
```
20-design/case.yaml ──> OpenSCAD source (generated) ──> renders (views) ──> STL per piece
                 │                                          │
                 ├─> census (walls, components, membranes, support area, mass)
                 ├─> interference vs the board mesh of record (provenance sidecar)
                 ├─> clearance_check.md / interference_check.md (rows, FAIL/WARN)
                 ├─> FEA (references/fea-stage.md) ──> FEA_REPORT.md + composites
                 ├─> drawings (silhouettes + sections, yaml numbers on the lines; STEP per piece + assembly)
                 └─> print-service / CNC DFM + quotes (references/fab-dfm.md §6) ──> ORDER_SHEET / PRINT_SHEET per piece
```
A set is one folder per PRINT TARGET under `40-case/<set>/`, named by the `print_targets` KEY (`vendor_mjf`, `home_fdm`). The gates read the target
from the folder name. Sets that are not targets (coupons, board_dummy, dfm_validation, fea, board_mesh) carry `--target` on their gate lines. Never
make one folder per case version; the version is a field of the records and the sheets. Inside a set, `parts/` holds the STL set of record, tracked;
the kits copy from here. `checks/` holds the census + DFM records and the clearance and interference checks; it is the only place the gates look.
`pictures/` holds previews, faces and assembly renders. `build/` holds scratch SCAD, logs, slicer scratch and caches. It is gitignored and recreated by every
run. The SCAD of record stays tracked at the set root, because the assembly-guide renders and the traceability checks key on its md5.
The determinism check compares a regenerated part with its recorded md5 in `checks/`. Everything under the set is generated. `ASSEMBLY.md` and
print sheets are generated with spliced blocks (`<!-- gen:BEGIN name -->…<!-- gen:END -->`) so prose survives regeneration.

## Board mesh of record (both) / fit input of record (mech)
- **mech scope**: there is no CAD project to export from. The fit input is the imported board STEP (converted to a mesh once, for example `trimesh` /
  FreeCAD, canonical STL). Or it is the owner's envelope (a box + hole pattern drawn from the dimensions). Its sidecar `paths.mesh_provenance` is
  `{source, source_md5, tag: V|K}`. The tag is [V] when measured or from the vendor drawing, and [K] when owner-stated. A [K] input is a KNOWN_ISSUES
  §2 item until a first article measures it. The `30-board/layout/` folder level in the paths below is absent in mech (`40-case/<preset>/`).
- Export the board mesh from HEAD (`--export-board --board-ref HEAD`), including tracks and zones, with the as-built 3D models. Write a **provenance
  sidecar** `{board_md5, board_commit, exported, mesh_md5, facets, ignore: [...]}` next to it. The mesh itself is untracked (100+ MB). The sidecar is
  tracked, and it is what the gates assert (`md5_in` on the board md5).
- A yaml flag "part not fitted" must ALSO reach the mesh check. The CAD 3D model is the as-shipped P/N, so the exported mesh still carries the removed
  solid. The flag therefore implies a `board_stl.ignore` connected component inside the part's yaml box. "0 components matched = WARN" tells you when
  model and flag disagree.
- "Silk-only hop" describes the last commit, not the distance from the mesh's board: check footprint positions per refdes between the two boards.
- **Board body for a dummy / fit input**: `kicad-cli pcb export stl --board-only --no-components` writes the outline exactly (drill holes included).
  But it writes the body at the stackup CORE thickness (1.46 for a nominal 1.6 board; copper and mask are not in the body) **[K]**. Scale Z to the
  nominal thickness, and to the fab's upper tolerance (1.7) for the fit check. Prefer this export to redrawing the outline; a hand-drawn fillet
  construction sat 0.36 mm off at two corners. Compare two outlines by subtracting each from the other with a 0.01 margin in OpenSCAD, both ways, both
  empty.

## Presets (print targets)
- `case.presets.<name>.overrides` deep-merged into `case:` BEFORE any module reads the yaml (generator, drawing, FEA all apply the same merge —
  otherwise one of them silently describes the other build). `preset_default` picks the build of record; `--preset fdm` writes to its own folder.
- `case.presets.<name>.engine` names the geometry engine of the preset's STL exports of record (the one that passes the chain's mesh gates on its
  bodies); previews use the fast engine regardless (`references/agent-ops.md` §8 item 6).
- A fix that turns out to be for every build belongs in the base block; prove "no geometry change" by diffing the merged dict key by key, not by
  re-exporting (CGAL STLs are not byte-stable).
- A new base key reaches every preset through the merge. Pin a new key in every override that already pins its sibling. After a knob is added,
  compare the volume of every untouched preset body against HEAD. A leaked wall value moved a sibling body on its first export (`pitfalls.md`).
- A preset that nobody rebuilds goes stale under shared code. Rebuild every preset that shares the edited code, in the same batch. One
  preset had missed two days of shared changes, and its rebuild showed a sliver from another change.
- FDM (owner's printer, target `home_fdm`): printer-first rules are FAIL rows, with numbers from `project.yaml print_targets.home_fdm`. Worked
  example, 0.4 nozzle / 0.20 mm / PLA-PETG: walls ≥ 1.6 = 4 perimeters (a two-line 0.85 skirt failed as a product). Every external face is on the bed,
  vertical, or a clean top. Legends are RAISED: cap ≥ 5.1 / stroke ≥ 0.9 / air gaps ≥ 0.9 / 0.6 on a face-up top. The gap metric is an opening of the
  complement. Use screws or magnets over slit tabs. Print coupons and a board dummy before the part. Use slicer projects with embedded presets
  (`references/dfm-printed-enclosure.md` §8). Put colour on TOP faces in ONE Z band per part; a coloured vertical flank costs a filament swap per
  layer. Key the filament slots by ROLE (structure / kinematics / accent / legend) with the colour name + hex as values. A palette change is then a
  yaml-only edit (`dfm-printed-enclosure.md` §8.3).
- Print service (MJF / SLA, target for example `vendor_mjf`): every wall AND every void ≥ the checker's grey line (`print_targets.<t>.wall_gate` /
  `void_gate`). For JLC3DP (2026-09-28) the line is 1.2. Design at the line + `design_margin` under a no-yellow bar. No free-standing wedge (tangent
  fillets into walls are fine). Engraved text only with stroke ≥ the void gate. Snap features only with the slit ≥ the void gate and an engineered
  arm. Closed rims. **Nothing "stays thinner": a listed-below-minimum row is a waiver, and the waived lip cracked on all five parts**
  (`references/dfm-printed-enclosure.md` §1–§4; inserts / magnets §1.1; SLA §11; CNC `references/cnc-enclosure.md`). Part min size per process. Make
  two-tone through an **inlay plate** (a mark-shaped pocket is its own key when the mark is chiral) or a **badge** (metal plate in a pocket, UV-print
  or laser artwork as DXF + B-rep STEP). Put text on a label carrier.
- Two versions from one yaml (vendor + home): put variant-only lines behind hook tokens that expand to the original text for the other presets. Give
  each preset its own version key. Prove byte identity of the vendor SCAD against HEAD before committing (`references/dfm-printed-enclosure.md` §9).

## Census (every row = a check with yaml value, measured value, gate, FAIL/WARN/OK) — the gate rules are `references/dfm-printed-enclosure.md` §2
- Wall thickness by ray-cast, **bucketed by entry surface** (a blind-hole bottom skin is not the recess floor); report each entry class with its own
  count and gate.
- Connected components per piece (one), membranes (thin sheets), support area, mass from the measured STL volume (not the design estimate — write
  the method next to the number), snap/latch preload volume, mating lens estimates including ramp bands.
- Check-mode totals (`--no-render --interference`) differ from full-run totals (`--stl` adds the mesh rows): quote the mode with the numbers.
- Imported artwork (SVG) is measured from the PATH, not the canvas attributes (`resize(auto)` scales the glyph bbox).
- Inward ray-cast rule: a ray from a point nudged 1e-3 inside a face hits THAT face at 0.000 for a fraction of samples. Discard hits closer than ~0.02
  mm and take the first beyond (`scripts/thin_wall_check.py --census`, `--self-hit`). Otherwise solid 2 mm chamfers read "0.00 mm walls".
- An STL md5 is not a geometry signature (CGAL export order moves every md5) UNLESS the export is rewritten canonically. The canonical form is sorted
  triangles and an own binary writer with normals recomputed from the float32 vertices (`references/dfm-printed-enclosure.md` §7.2). Without that,
  prove "only piece X changed" by facet count / volume / area / bbox per piece, not by md5s.
- **The census is a FAIL gate per print preset, not a review aid** (`scripts/thin_wall_census.py --target <t>`). `--gate-dir <census dir>` in the
  adopt list proves md5 + 0 unaccepted FAIL against the committed STL. What it gates, how clusters are classed and what the only exception path is:
  `references/dfm-printed-enclosure.md` §2, with rows in `templates/CENSUS_GATE_ROWS.md`. Concentricity and every face render come from the mesh too.
- **An item text carries no preset or derived value.** The value column or the note carries the number. A value in the item text makes a
  different item per preset. The per-preset check-table diff (the project's look-delta pairing) then drops the row. Pair presets on
  group + item with every free-standing number masked. Keep the digits of a refdes. A digit strip that eats refdes digits merges two
  labels. Two rows that differ only by a number collide on such a key. Stop the pairing on a collision. Worked example (2026-10): the
  diff of two preset tables paired 71 rows. Twelve rows per table carried a value in the item and did not pair. After the move it
  paired 83 rows: the 71, plus the 12, 0 lost.
- A changed item text changes every traceability grep that quotes it. Grep the traceability yaml for the old item text in the same
  commit.

## Point contacts (mark-shaped bodies and pockets: inlay plates, badges, debosses)
- A traced outline of touching shapes (potrace) is ONE path pinched to 0.003–0.03 mm at every contact. Extruded, the body is lobes held by hairlines
  (the fab's review: "B 0.01"). A ridge / distance-transform "thinnest arm" census cannot see it. Test the SECTION polygon:
  `scripts/thin_wall_check.py --pinch <stl>` = non-adjacent boundary vertices closer than ~0.05 mm with > 5 % of the perimeter between them.
- Fix in the generator: a web disc (≥ the process minimum, for example 1.4 mm for 0.8 mm resin) at each contact. INTERSECT it with the outline's
  closing (`offset(r = +R) offset(r = -R)`, R ≈ 3 × web), so each web is a concave fill. A bare disc bulges into the silhouette (a 0.4 mm nub on a 3
  mm arm). The pocket and every deboss that uses the outline follow. Artwork that stays 2-D (UV print, laser) keeps the pure outline.
- Two census rows: the neck through each contact after the webs (`--web D --clip R`; ≥ the minimum) AND `connected components = 1` per body. The
  second caught a disc placed 7 mm off when the neck row measured the wrong frame.
- trimesh `section().to_2D()` RE-ORIGINS the plane (its returned transform carried a 6.9 / 4.6 mm translation): coordinates read off the Path2D are
  not model coordinates until mapped back through that to-3D matrix. Fractions of the mark width travel to the SCAD, which scales them itself.
- Find the contacts once per artwork (cache by the SVG md5); the fdm preset that never prints the mark as a body sets the web to 0.

## Cost of a case-version bump (worked example: one geometry change, one machine, 2026-09-23)
| Stage | Time (worked example) | Why every version pays it |
|---|---|---|
| renders (≈ 70 views) | ≈ 4 min | keyed on the SCAD text |
| STL export + overlaps / interference | ≈ 5 min | every piece re-exported |
| case FEA | ≈ 13 min | every mesh rebuilt — every STL md5 changed, even untouched pieces (export order) |
| PCB / assembly FEA | ≈ 10 min | coupled cases read the case meshes |
| drawings (+ STEP) | ≈ 3 min | keyed on the STL md5s |
| one-round report chain + PDFs | ≈ 10 min | `references/release-and-cut.md` §3.1 |
≈ 45 min. Run case FEA, PCB FEA, drawings and the alternative preset as FOUR background jobs (`python -u … > log 2>&1; echo EXIT $? >> log`). Block on
the EXIT lines in a foreground `until` loop (`references/agent-ops.md` §5). Never run two memory-capped FEA pools at once. Kill early when an owner
addition arrives. Budget the bump before promising "full release pipeline" in the same hour.

## Interference / clearance
- Voxel/containment first, CGAL boolean only on flagged pairs (minutes per piece otherwise). Whole-piece overlaps empty except designed preloads.
- Guard rows: "board md5 = recorded, mesh md5 = recorded" must be OK or the whole check is about another board.
- **Fit test on the EXPORTED meshes by boolean** (never on the design modules): import the STL / 3MF bodies into OpenSCAD at their use positions,
  `intersection()`, `--export-format binstl`; "Current top level object is empty" on stderr = no interference. Clearance ≥ c: intersect the case
  with the part grown by `minkowski(part, cube(2c, center=true))`, lifted by c + 0.01 so a face the part rests on (floor, shoulder) is not
  counted. Two controls or the check has no teeth: a NEGATIVE control (grown by more than the design gap must be NON-empty) and a TOUCH control
  (a mating part lowered by 0.05 must intersect — the part seats where designed). A zero-volume intersection (coplanar resting faces) is contact,
  not interference: measure the intersection's volume (signed tetrahedron sum over the STL) before a FAIL **[K]**.
- **Fit rows per degree of freedom, not per part.** A fit test that places every part at its NOMINAL position proves nothing about the directions the
  part can move in. List each part's degrees of freedom in the assembly: shift along each axis, lift, and the 180° turn of a symmetric part (a lid, a
  cover, a tray). Write one row pair per degree of freedom: a POSITIVE control (moved by less than the designed play: empty) and a NEGATIVE control
  (moved by more than the play: overlaps the stop meant to catch it). A degree of freedom without a stop is a design defect, not a missing row. A rib
  BETWEEN parts guides their faces; only a face ACROSS the slot stops a part along the slot **[K]**. Boards whose "end ribs" sat between the slots
  slid 6.6 mm along their length past a 14-row fit test that passed. A symmetric lid turned 180° about Z can seat on the wrong parts (pads over the
  low slots land on the high parts). The turned pose is a row, or the lid gets a key. Prefer a lid that closes either way: a user turns a lid
  180° without looking. A stagger of every second slot high keyed the lid to one direction **[K]**. A palindrome pattern (low-high-low-high-low,
  then its mirror image) keeps the pinch band on the high parts, and the lid closes either way. The magnets then go in with the SAME pole up
  at both ends; opposite poles were the one-way key.
- **A pocket that opens to air is probed twice**: a body as tall as the inserted part (magnet, insert) at the pocket must be EMPTY, and a thin
  body just BELOW the designed floor must OVERLAP. A probe taller than the pocket pokes into air and proves nothing about the depth.
- **The fit-test shifts come from the values the test reads from the design source**, never from literals: clearance ± 0.05, end play ± 0.05.
  A reader of `NAME = value` lines strips comments first and anchors the name with `\b`. Several values share one line, and a comment repeats a
  value: a reader for `BOSS_H` matched inside `MAG_H = 3.0; ... BOSS_H = 2.6` **[K]**. A relieved parting line gets four checks: lift the
  lid above the pillar tops so the teeth clear, then shift by the clearance ± 0.05 (`dfm-printed-enclosure.md` §8.6).
- **A feature that overlaps the nominal part by design (a preload: a spring finger, a crush rib) is tested with the parts shortened**. Shorten
  the nominal parts by the interference plus 0.2 for the clearance checks, so the preload does not read as a FAIL. Add positive checks: the
  closed lid holds each part at both ends, and a part shifted by the preload is held by the one finger. A probe on the tops of the end blocks
  caught a wedge that sloped the wrong way: "finger tips reach a 1.8 slab" came back empty **[K]** (`dfm-printed-enclosure.md` §8.5).
  **A nominal-mesh preload test does not see print tolerance** **[K]**. Fingers that passed every check jammed the printed lid: a board end
  sat 0.2 inside a finger corner, and the tall thin island printed ± 0.2 or more. When a feature's margin to a part edge is under 0.5, add a
  check with the mating part shifted by the print tolerance (± 0.3) in each direction. Add a check that the guiding features reach lower
  than the holding features (compare their lowest Z), so the parts are aligned before anything pushes on them.
- Every envelope (connector housings, cage, heat sink, fan, inserts, screws) is a yaml box; the census asserts each is either inside a piece or in
  a declared cut-out.
- Planar linkages (mech): the body levels are a graph colouring. Sweep every body pair over the full cycle; an edge = an in-plane crossing, and levels
  = chromatic number. A triangle in the conflict graph → three levels, however the bars are drawn. Compute it before drawing a link.
- Sweep 360 steps of every body PAIR per level with pins / pegs / caps as discs; min distance and overlap area per pair as a CHECKS row (`contacts = 0`).
  A bar-only sweep or any single-pose render misses touching bosses and a peg grazing a bar. A sweep run per side in the PART plane cannot see
  a mirrored side or a D turned 180° in its socket — those are the assembly-model rows (§Assembly model), run on the 4×4 placements.
- Static raised features are in the sweep too: a moving part's envelope against every raised legend, boss and lug on the faces it passes, with the
  axial play added. The arm that scraped its legends had 0.5 mm of designed gap to the flat face and −0.1 to the 0.6 mm letters.

## Assembly model (every instance placement, every mating pair) — buildability is PROVEN, never looked at
The assembly model (`assembly.json`: body, colour, 4×4 placement per instance, per pose) is the only record of how a part is TURNED between its print
(or stock) frame and the machine. Renders, face sets and animations are drawn from it and inherit every error in it. Three transform-level rows gate
it before any render is trusted. They are pure arithmetic on the placement matrices and the part-frame feature directions:
1. **Every instance placement is a proper rotation (det +1) — a CHECKS row, FAIL.** `det(M[:3,:3]) < 0` is a MIRROR, and a mirror cannot be made. The
   render shows a part no plate or stock can produce. The row is `scripts/stability.py improper_placements([(label, M), …]) == []`. If the generator
   has no stability module, write five lines inline: `np.linalg.det(np.array(M)[:3, :3])` per instance, count `< 0`, row = `0`. The mirror is
   invisible to everything downstream. A flat part reads as plausible mirrored (its outline is the same shape). A per-side 2D interference sweep runs
   in the part plane, where a mirror is a no-op. The kit prints the body, not the transform. A symmetric assembly built from identical parts is the
   usual way in: "part +z outward" on both sides of the machine makes one side improper. A part that can only be drawn mirrored needs a mirrored BODY
   (`mirror([1,0,0])` of the design body, its own identifier mark, `dfm-printed-enclosure.md` §1.5), never a mirrored transform. *Worked example:* one
   project drew one whole side as a mirror image through three days of renders and an animation. Nothing but the owner holding a printed part against
   the guide caught it.
2. **A FIT row per mating pair the design knows about** (shaft ↔ bore, D ↔ D socket, peg ↔ hole, tab ↔ slot, pin ↔ pivot, key ↔ keyway). Map the
   DIRECTION of the feature and the direction of its mate through the REAL placements into the machine frame. The two must agree within a stated
   tolerance (a flat vs its socket flat ≤ 1°; an axis vs its bore axis ≤ 1°, offset ≤ the fit clearance). The interference sweep says two bodies do
   not overlap. It never says a feature goes INTO its mate. This row, not the eye, decides a chiral feature's hand (a twist, a thread, a one-way
   tooth). Generic form: a pair is (feature direction in its part frame, its placement) vs (mate direction in its part frame, its placement):
   ```python
   from math import atan2, degrees
   import numpy as np

   def machine_dir(M, v):                              # a part-frame direction -> machine frame (rotation only)
       R = np.array(M, float)[:3, :3]; w = R @ np.array(v, float); return w / np.linalg.norm(w)
   def fit_rows(pairs, tol_deg=1.0):                   # pairs: [(label, v_feature, M_feature, v_mate, M_mate)] -> CHECKS rows
       rows = []
       for label, vf, Mf, vm, Mm in pairs:
           a, b = machine_dir(Mf, vf), machine_dir(Mm, vm)
           diff = degrees(atan2(np.linalg.norm(np.cross(a, b)), np.dot(a, b)))     # unsigned angle; sign it against a reference axis if the pair is planar
           rows.append(("fit", f"{label}: feature direction vs mate direction (deg)", f"{diff:.1f}", f"<= {tol_deg}", diff <= tol_deg))
       return rows
   ```
   The feature directions come from the geometry of record (the same segment list or outline the CAD is generated from). The row therefore cannot
   agree with a drawing the mesh contradicts. A feature whose mate is not in reach is a FAIL row, not a skipped one. A row of this kind, written after
   the first article, has failed every end of a mating-pair type at once (180° off). That row then decided the hand of the chiral part.
3. **An ORIENTATION row per part type with a one-sided feature** (a slot that opens one way, pegs or bosses on one face, a working face that must
   point at its mate, a flat that must face a fixed direction). The feature's axis through the placement must point at its mate or at the ground:
   `np.dot(machine_dir(M, axis), expected) > cos(tol)`. Write one row per part type, with `expected` from the geometry of record (the mate's position,
   `−z` for a ground face). A flat render reads an inverted one-sided part as fine; the row does not.
4. **Renders and animations are not evidence of buildability.** They are previews of the model; rows 1–3 are the evidence, and the assembly
   guide's 3D view is the owner's last look, not the gate.

## Stability (anything that stands, rocks, walks or is set down free)
- A free-standing piece has a support polygon (the convex hull of what touches the ground) and a centre of gravity. It stays up only while the CoG's
  ground projection lies inside that polygon by a margin. This is GEOMETRY, computed from the STL set of record, never judged from a render.
  `scripts/stability.py` has `cog_of_assembly([(stl, 4x4, density)])`: volume centroids through the assembly transforms, with an infill factor per
  body. Sparse-infill plates weigh 0.5–0.7 of solid, and pins and bars ~1.0. The factor matters only where it differs front to back. The script also
  has `support_margin(cog_xy, footprints)` → signed distance to the hull edge. A CHECKS row: **min margin over every pose ≥ a stated value**. For a
  walker, check every crank angle with the feet in their ground phase as footprints. For a rocking or hinged piece, check every position. For a part
  set down, check each face it can rest on. A piece that moves is judged at its WORST pose. A six-leg walker stands on one foot per side for a third
  of the cycle, and there the hull is the length of one foot.
- The CoG goes where the heavy parts are, not where the designer looks. A drive, gears, winders and bands hung behind the legs put a walker's CoG
  behind its hip (a negative margin at a third of the poses). Fix by LAYOUT (drive over the feet, frame extended forward), never by ballast bolted on
  afterwards; then the row proves it. Kickoff **C12** asks whether the piece stands free; the row is mandatory when it does.
- Lateral stability follows from symmetric feet; the longitudinal margin is the one that fails. State the mass model (solid density × infill
  factors) on the row so a heavier print (more walls) or a bought part (a band, a battery) is re-judged, not assumed.
- A foot move changes the support hull. Rerun the stability row after every foot move. A cable that pulls on the piece is an external
  force. State its size, direction and height on the row. State the minimum ratio of restoring to tipping moment. On one case, a foot
  move away from the cable end cut the cable-on moment ratio from 2.63 to 1.09. A move toward it raised the ratio to 6.41.

## Drawings
Silhouettes + sections from the STLs of record (trimesh/shapely), dimension lines carry the yaml numbers (so a yaml change moves the number and the
geometry together), per-piece and assembly STEP (OCP/cadquery), `--check` = md5 sidecar keyed on the STL md5s. Run AFTER the final STL pass.
- **Generate the sheet from the exported meshes**: projections and sections through the CAD's own projection of the STL set of record, every
  number from the parameter block or ONE echo run of the generator, never typed. A self-check on every sheet: each dimension end point lies on
  the mesh linework within 0.03 mm, and every outer size equals the mesh bounding box. REV from `git describe`; regenerate from a clean tree
  before release (a dirty tree stamps `-dirty`).
- Pick each section plane through a plain region of the part: a plane through a scallop or a cut-out draws a seated lid as unseated. One
  numbering convention for repeated features (slots, ribs) on every view; no text over an arrow.
- The sheet is reviewed by the double-blind drawing round (SKILL §5): the sheet gets a reader who has nothing else, and a verifier measures
  every claim on the meshes.

## Feature views (sections for what a flat face hides)
- An orthographic face renders every flat face in one shade. A pocket, a boss, a chamfer, a deboss or a tab inside a wall does not show. Six
  faces do not show such a feature. A picture column that names a face for such a row is not evidence.
- One section per designed asymmetry: a 1 mm slab through the feature. The generator takes a section axis and a cut position. The worked
  example's generator has a slab mode per axis and a cut-position key. Render it orthographic, in a light colour, through the same faces
  loop. The cut face renders in one shade and a floor below it in another. A pocket floor reads at once. An edge view on the fast engine
  draws recess edges where a raking light on a dark body shows nothing.
- Measure the feature on the mesh before you promise a picture. A land that fills 0.02 of a round shows in no render; the row states the
  number. Read the mesh for the value and cite the picture for the look. A top face renders +Y up, so its legends read upside down: turn the
  plot 180°, never mirror it.
- A render-only run must not rewrite the check records. Check that the SCAD of record equals the yaml's SCAD. Then render the views alone
  from it. The worked example's generator has a features-only flag for that.
## Process rules
- The render + STL + interference chain runs through the job pool (`references/agent-ops.md` §8). Previews regenerate on every run on the fast engine.
  STL exports of record run on the preset's `engine:` (the one that passes the mesh gates). They are cached only on the inputs + engine key, with the
  sidecar md5 as a determinism check (`--no-cache` forces). Use `--render` for geometry of record. Kill the chain early when an owner addition
  arrives.
- The SCAD text embeds the generator and asset paths, and the export cache keys on that text. A layout change therefore re-exports every STL.
  The stop rule makes a re-layout safe for an ordered set: every STL of record comes back byte-identical, or the work stops.
- Never run a case "check" in the working tree if it writes tracked files — the traceability sandbox copies `gen/ + 20-design/` and symlinks the mesh.
- Print sheets and order sheets list filaments / processes per piece, orientation, supports, post-process, and the material rating (UL 94 / HDT from
  the TDS). They list insert type / bore / temperature per material (from the insert TDS, `dfm-printed-enclosure.md` §1.1). They carry the insert
  temperature/time and screw torque as `[OWNER: …]` placeholders until the insert + torque coupon measured them.
- Debug dumps under `build/**/_check/` (gitignored), never the repo root.
- The fast engine (`--backend=Manifold` on a snapshot build, `tools.openscad_args`) exports a body in well under a second where the release kernel
  takes minutes. A 360-step sweep and an animation become affordable as PREVIEWS. The pool's slots go to the mesh checks and the slicer
  (`references/agent-ops.md` §8 items 1 / 6). STL exports of record stay on the preset's `engine:`, the one that passes the mesh gates. Two constructs
  break watertightness under Manifold. The first is `hull()` of two thin slabs; draw a solid wedge or a bevelled cut instead. The second is a standing
  D-shaft as D-extrude + cylinder + ramp unions (many shells). ONE cylinder minus bevelled flat cuts is manifold by construction. The watertight row
  per STL catches both, which is what the engine rule gates on. A third: straight rib faces that meet an end plane. The Manifold export carried 20–40
  zero-area sliver triangles (trimesh `split`: 41 "bodies", not watertight) where CGAL exported one watertight body in 9 s **[K]**. Removing the
  degenerate triangles afterwards leaves open edges. Post-processing is not a fix; the kernel of record is.
- **CSG construction order** (OpenSCAD, any CSG tree) **[K]**: (1) a positive feature unioned INSIDE the `difference()` that cuts the cavity is
  removed by the cut. Bosses on a ceiling vanished, and their pocket read 0.7 mm deep instead of 3.2. Add positive features AFTER the cut. Then cut
  their pockets through the feature AND the plate it stands on; a pocket cut through the boss only is as deep as the boss is tall. (2) `hull()` of the
  full-depth cavity outline with a wider rim outline is a DRAFT over the whole depth, not a lead-in chamfer. The mating gap read 0.5–0.6 instead of
  0.2. Confine the hull to the last 0.4 mm of the rim. Both traps passed the fit test and print DFM. Acceptance rows on the MESH catch them: pocket
  depth by the two probes of §Interference, cavity width 1 mm above the rim = nominal.
- **A through-opening cutter runs past the face** **[K]**. Do not stack a coplanar overlap box on a frustum that ends at the face. A box
  0.001 wider than the frustum top leaves a 0.001 × 0.001 step ring around the opening. Every index read passed (shells, watertight,
  volume, the vendor API). The vendor map painted the slivers beside it. Extrude one shape `c + 1` tall with the scale adjusted. Here `c`
  is the chamfer depth and the 1 the overlap past the face. One solid then cuts the chamfer and the air above it. Keep an overlap box
  only on a `hull()` mouth, where the box ends inside the cavity. That branch read 0 / 0 with its box. Count the vertical faces under
  0.002 mm tall before an export. The gate is 0. The 0.002 is twice the 0.001 overlap, so it catches the ring on either side. Worked
  example (JLC3DP analyser, 2026-10): 40 micro-faces around five slots. The ring split the chamfer faces into 12640 slivers. The fixed
  cutter left 2920. That sliver count is the INFO measure of `dfm-printed-enclosure.md` §12, not this gate (§13.1).
- A partial chain run (`--pieces <one>`) rewrites the shared records with that run's rows only. The shared records are the clearance table, the
  kit README and the render index. Commit the piece artefacts; leave the shared files to the full chain, or restore them before the commit.
- A census VERSION bump makes every record at the old version a gate problem. Run every generator that writes a census, the ones outside the
  chains too, before the adopt gate.
- OpenSCAD 2021.01's preview aborts CSG normalisation past its `openCSGLimit` preference (100 000 elements by default). It writes a blank PNG
  and exits 0. Render previews with the fast engine, and fail the run on an empty frame.
- A merge can carry a SCAD of record from an intermediate generator state. Run the chains after every merge, before a vendor upload.
- A gate whose prerequisites are physical (a mock-up timed, a lift read) is carried by the record: `release-and-cut.md` §3.1.
- A bought part's dimensions live in one yaml block that every pocket and the kit text read. Pockets cut for a Ø6.0 disc met Ø6.35
  discs. With one block, a part change is one edit, not a hunt through the presets.
- Key a cache on the inputs its output reads, no more. A coupon key that read the whole case SCAD went STALE on every deck change with
  identical geometry. An export that embeds a timestamp changes its md5 on every run. Strip the timestamp, or check the geometry instead.
- Read the case order's hardware lines live through the dealer's API before the order sheet is final.
  The rules are in `part-verification.md` §Bought hardware; the API keys live in an untracked env file.
