# case-pipeline.md — enclosure from one yaml to prints and quotes


## 0. Imported body — the owner already has the CAD (`scripts/step2stl.py`)

The chain of record assumes every body is generated from `20-design/case.yaml`. A part that exists as a STEP (the owner's bracket, a vendor's
housing) enters M1 as a **generated-only exception** (SKILL §2): `scripts/step2stl.py part.step --out 40-case/<target>/parts/<piece>.stl
--tag V|K` converts it (cadquery in the venv, else the FreeCAD CLI, else `--canonical` on an STL exported from the CAD — the routes are printed
when none is available; OpenSCAD cannot read STEP), writes the **canonical STL** (sorted triangles, float32 normals: the md5 is the geometry) and
`<piece>.stl.provenance.json` (source, source md5, tag, converter, tolerance, stl md5, geometry signature, date), and prints the decision row:
OPEN, "imported body <piece>", the chain of record (source md5 → converter → STL md5 + signature; a changed source or signature = a new row).
From there the body is gated like a generated one — `thin_wall_census.py --target <t> --json 40-case/<target>/checks/census/<piece>.json` and `print_dfm.py --process
<row> --out .../dfm` records of the same md5, six face renders, clearance rows — and `gen/<geometry>.py --check` is replaced in the M1 row by
`scripts/step2stl.py --canonical <export> --out <piece>.stl` reproducing the committed md5 (the provenance sidecar's `stl_md5`). A body whose
source changes re-enters through a new conversion and a new row; editing the STL by hand is never a route.

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
A set is one folder per PRINT TARGET under `40-case/<set>/`, named by the `print_targets` KEY (`vendor_mjf`, `home_fdm` — the gates read the
target from the folder name); sets that are not targets (coupons, board_dummy, dfm_validation, fea, board_mesh) carry `--target` on their gate
lines. Never one folder per case version —
the version is a field of the records and the sheets. Inside: `parts/` (the STL set of record, tracked; the kits copy from here), `checks/`
(census + DFM records, clearance and interference checks — the only place the gates look), `pictures/` (previews, faces, assembly renders) and
`build/` (SCAD, logs, slicer scratch, caches — gitignored, recreated by every run; the determinism check compares a regenerated part with its
recorded md5 in `checks/`). Everything under the set is generated; `ASSEMBLY.md` and print sheets are generated with spliced blocks
(`<!-- gen:BEGIN name -->…<!-- gen:END -->`) so prose survives regeneration.

## Board mesh of record (both) / fit input of record (mech)
- **mech scope**: there is no CAD project to export from. The fit input is the imported board STEP (converted to a mesh once, e.g. `trimesh`
  / FreeCAD, canonical STL) or the owner's envelope (a box + hole pattern drawn from the dimensions); its sidecar `paths.mesh_provenance` is
  `{source, source_md5, tag: V|K}` — [V] when measured or from the vendor drawing, [K] when owner-stated; a [K] input is a KNOWN_ISSUES §2 item
  until a first article measures it. The `30-board/layout/` folder level in the paths below is absent in mech (`40-case/<preset>/`).
- Export the board mesh from HEAD (`--export-board --board-ref HEAD`), including tracks and zones, with the as-built 3D models; write a **provenance
  sidecar** `{board_md5, board_commit, exported, mesh_md5, facets, ignore: [...]}` next to it. The mesh itself is untracked (100+ MB); the sidecar is
  tracked and is what gates assert (`md5_in` on the board md5).
- A yaml flag "part not fitted" must ALSO reach the mesh check: the CAD 3D model is the as-shipped P/N, so the exported mesh still carries the
  removed solid → the flag implies a `board_stl.ignore` connected component inside the part's yaml box; "0 components matched = WARN" tells you when
  model and flag disagree.
- "Silk-only hop" describes the last commit, not the distance from the mesh's board: check footprint positions per refdes between the two boards.

## Presets (print targets)
- `case.presets.<name>.overrides` deep-merged into `case:` BEFORE any module reads the yaml (generator, drawing, FEA all apply the same merge —
  otherwise one of them silently describes the other build). `preset_default` picks the build of record; `--preset fdm` writes to its own folder.
- `case.presets.<name>.engine` names the geometry engine of the preset's STL exports of record (the one that passes the chain's mesh gates on its
  bodies); previews use the fast engine regardless (`references/agent-ops.md` §8 item 6).
- A fix that turns out to be for every build belongs in the base block; prove "no geometry change" by diffing the merged dict key by key, not by
  re-exporting (CGAL STLs are not byte-stable).
- FDM (owner's printer, target `home_fdm`): printer-first rules as FAIL rows, numbers from `project.yaml print_targets.home_fdm` (worked example,
  0.4 nozzle / 0.20 mm / PLA-PETG: walls ≥ 1.6 = 4 perimeters — a two-line 0.85 skirt failed as a product), every external face on the bed /
  vertical / clean top, legends RAISED cap ≥ 5.1 / stroke ≥ 0.9 / air gaps ≥ 0.9 / 0.6 on a face-up top (the gap metric is an opening of the complement), screws or magnets over slit tabs, coupons and a board dummy before
  the part, slicer projects with embedded presets (`references/dfm-printed-enclosure.md` §8). Colour on TOP faces in ONE Z band per part (a coloured vertical
  flank costs a filament swap per layer); filament slots keyed by ROLE (structure / kinematics / accent / legend) with the colour name + hex as
  values, so a palette change is a yaml-only edit (`dfm-printed-enclosure.md` §8.3).
- Print service (MJF / SLA, target e.g. `vendor_mjf`): every wall AND every void ≥ the checker's grey line (`print_targets.<t>.wall_gate` /
  `void_gate`; JLC3DP 2026-09-28: 1.2 — design at + `design_margin` under a no-yellow bar), no free-standing wedge (tangent fillets into walls are
  fine), engraved text only with stroke ≥ the void gate, snap features only with the slit ≥ the void gate and an engineered arm, closed rims;
  **nothing "stays thinner" — a listed-below-minimum row is a waiver, and the waived lip cracked on all five parts**
  (`references/dfm-printed-enclosure.md` §1–§4; inserts / magnets §1.1; SLA §11; CNC `references/cnc-enclosure.md`). Part min size per process; two-tone via an **inlay plate** (a mark-shaped pocket is its own key when
  the mark is chiral) or a **badge** (metal plate in a pocket, UV-print or laser artwork as DXF + B-rep STEP); text on a label carrier.
- Two versions from one yaml (vendor + home): variant-only lines behind hook tokens that expand to the original text for the other presets, own version
  key per preset, byte identity of the vendor SCAD proven against HEAD before committing (`references/dfm-printed-enclosure.md` §9).

## Census (every row = a check with yaml value, measured value, gate, FAIL/WARN/OK) — the gate rules are `references/dfm-printed-enclosure.md` §2
- Wall thickness by ray-cast, **bucketed by entry surface** (a blind-hole bottom skin is not the recess floor); report each entry class with its own
  count and gate.
- Connected components per piece (one), membranes (thin sheets), support area, mass from the measured STL volume (not the design estimate — write
  the method next to the number), snap/latch preload volume, mating lens estimates including ramp bands.
- Check-mode totals (`--no-render --interference`) differ from full-run totals (`--stl` adds the mesh rows): quote the mode with the numbers.
- Imported artwork (SVG) is measured from the PATH, not the canvas attributes (`resize(auto)` scales the glyph bbox).
- Inward ray-cast rule: a ray from a point nudged 1e-3 inside a face hits THAT face at 0.000 for a fraction of samples — discard hits closer than
  ~0.02 mm and take the first beyond (`scripts/thin_wall_check.py --census`, `--self-hit`), or solid 2 mm chamfers read "0.00 mm walls".
- An STL md5 is not a geometry signature (CGAL export order moves every md5) UNLESS the export is rewritten canonically (sorted triangles, own binary
  writer with normals recomputed from the float32 vertices — `references/dfm-printed-enclosure.md` §7.2); without that, "only piece X changed" is
  proven by facet count / volume / area / bbox per piece, not by md5s.
- **The census is a FAIL gate per print preset, not a review aid** (`scripts/thin_wall_census.py --target <t>`; `--gate-dir <census dir>` in the adopt
  list proves md5 + 0 unaccepted FAIL against the committed STL): what it gates, how clusters are classed and what the only exception path is —
  `references/dfm-printed-enclosure.md` §2, rows in `templates/CENSUS_GATE_ROWS.md`. Concentricity and every face render come from the mesh too.

## Point contacts (mark-shaped bodies and pockets: inlay plates, badges, debosses)
- A traced outline of touching shapes (potrace) is ONE path pinched to 0.003–0.03 mm at every contact; extruded, the body is lobes held by
  hairlines (the fab's review: "B 0.01"), and a ridge / distance-transform "thinnest arm" census cannot see it. Test the SECTION polygon:
  `scripts/thin_wall_check.py --pinch <stl>` = non-adjacent boundary vertices closer than ~0.05 mm with > 5 % of the perimeter between them.
- Fix in the generator: a web disc (≥ the process minimum, e.g. 1.4 mm for 0.8 mm resin) at each contact, INTERSECTED with the outline's
  closing (`offset(r = +R) offset(r = -R)`, R ≈ 3 × web) so each web is a concave fill — a bare disc bulges into the silhouette (a 0.4 mm nub on
  a 3 mm arm). The pocket and every deboss that uses the outline follow; artwork that stays 2-D (UV print, laser) keeps the pure outline.
- Two census rows: the neck through each contact after the webs (`--web D --clip R`; ≥ the minimum) AND `connected components = 1` per body —
  the second caught a disc placed 7 mm off when the neck row measured the wrong frame.
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
≈ 45 min. Run case FEA, PCB FEA, drawings and the alternative preset as FOUR background jobs (`python -u … > log 2>&1; echo EXIT $? >> log`) and
block on the EXIT lines in a foreground `until` loop (`references/agent-ops.md` §5); never two memory-capped FEA pools at once. Kill early when an
owner addition arrives. Budget the bump before promising "full release pipeline" in the same hour.

## Interference / clearance
- Voxel/containment first, CGAL boolean only on flagged pairs (minutes per piece otherwise). Whole-piece overlaps empty except designed preloads.
- Guard rows: "board md5 = recorded, mesh md5 = recorded" must be OK or the whole check is about another board.
- Every envelope (connector housings, cage, heat sink, fan, inserts, screws) is a yaml box; the census asserts each is either inside a piece or in
  a declared cut-out.
- Planar linkages (mech): the body levels are a graph colouring — sweep every body pair over the full cycle, edge = an in-plane crossing, levels =
  chromatic number (a triangle in the conflict graph → three levels, however the bars are drawn); compute it before drawing a link.
- Sweep 360 steps of every body PAIR per level with pins / pegs / caps as discs; min distance and overlap area per pair as a CHECKS row (`contacts = 0`).
  A bar-only sweep or any single-pose render misses touching bosses and a peg grazing a bar.
- Static raised features are in the sweep too: a moving part's envelope against every raised legend, boss and lug on the faces it passes, with
  the axial play added (the arm that scraped its legends had 0.5 mm of designed gap to the flat face and −0.1 to the 0.6 mm letters).

## Stability (anything that stands, rocks, walks or is set down free)
- A free-standing piece has a support polygon (the convex hull of what touches the ground) and a centre of gravity; it stays up only while the
  CoG's ground projection lies inside that polygon by a margin. This is GEOMETRY, computed from the STL set of record — never judged from a render.
  `scripts/stability.py`: `cog_of_assembly([(stl, 4x4, density)])` (volume centroids through the assembly transforms, an infill factor per body:
  sparse-infill plates weigh 0.5–0.7 of solid, pins and bars ~1.0; the factor matters only where it differs front to back) and
  `support_margin(cog_xy, footprints)` → signed distance to the hull edge. A CHECKS row: **min margin over every pose ≥ a stated value**
  (a walker: every crank angle with the feet in their ground phase as footprints; a rocking or hinged piece: every position; a part set down: each
  face it can rest on). A piece that moves is judged at its WORST pose — a six-leg walker stands on one foot per side for a third of the cycle, and
  there the hull is the length of a shoe.
- The CoG goes where the heavy parts are, not where the designer looks: a drive, gears, winders and bands hung behind the legs put a walker's CoG
  behind its hip (a negative margin at a third of the poses). Fix by LAYOUT (drive over the feet, frame extended forward), never by ballast
  bolted on afterwards; then the row proves it. Kickoff **C12** asks whether the piece stands free; the row is mandatory when it does.
- Lateral stability follows from symmetric feet; the longitudinal margin is the one that fails. State the mass model (solid density × infill
  factors) on the row so a heavier print (more walls) or a bought part (a band, a battery) is re-judged, not assumed.

## Drawings
Silhouettes + sections from the STLs of record (trimesh/shapely), dimension lines carry the yaml numbers (so a yaml change moves the number and the
geometry together), per-piece and assembly STEP (OCP/cadquery), `--check` = md5 sidecar keyed on the STL md5s. Run AFTER the final STL pass.

## Process rules
- The render + STL + interference chain runs through the job pool (`references/agent-ops.md` §8): previews regenerated on every run on the fast
  engine; STL exports of record on the preset's `engine:` (the one that passes the mesh gates), cached only on the inputs + engine key with the
  sidecar md5 as a determinism check (`--no-cache` forces); `--render` for geometry of record; kill it early when an owner addition arrives.
- Never run a case "check" in the working tree if it writes tracked files — the traceability sandbox copies `gen/ + design/` and symlinks the mesh.
- Print sheets and order sheets list filaments / processes per piece, orientation, supports, post-process, the material rating (UL 94 / Tg from the
  TDS), insert type / bore / temperature per material (from the insert TDS, `dfm-printed-enclosure.md` §1.1), and the insert temperature/time and
  screw torque `[OWNER: …]` placeholders until the insert + torque coupon measured them.
- Debug dumps under `out/**/scratch/` (gitignored), never the repo root.
- The fast engine (`--backend=Manifold` on a snapshot build, `tools.openscad_args`) exports a body in well under a second where the release
  kernel takes minutes: a 360-step sweep and an animation become affordable as PREVIEWS, and the pool's slots go to the mesh checks and the slicer
  (`references/agent-ops.md` §8 items 1 / 6). STL exports of record stay on the preset's `engine:` — the one that passes the mesh gates. Two
  constructs that break watertightness under Manifold: `hull()` of two thin slabs (draw a solid wedge or a bevelled cut instead) and a standing
  D-shaft as D-extrude + cylinder + ramp unions (many shells — ONE cylinder minus bevelled flat cuts is manifold by construction); the watertight
  row per STL catches both, which is what the engine rule gates on.
