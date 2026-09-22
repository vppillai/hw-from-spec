# case-pipeline.md — enclosure from one yaml to prints and quotes

## Chain (one yaml, one generator, every step keyed on content)
```
design/case.yaml ──> OpenSCAD source (generated) ──> renders (views) ──> STL per piece
                 │                                          │
                 ├─> census (walls, components, membranes, support area, mass)
                 ├─> interference vs the board mesh of record (provenance sidecar)
                 ├─> clearance_check.md / interference_check.md (rows, FAIL/WARN)
                 ├─> FEA (references/fea-stage.md) ──> FEA_REPORT.md + composites
                 ├─> drawings (silhouettes + sections, yaml numbers on the lines; STEP per piece + assembly)
                 └─> print-service / CNC DFM + quotes (references/fab-dfm.md §6) ──> ORDER_SHEET / PRINT_SHEET per piece
```
Everything under `out/<board>/mechanical/case/<preset>/` is generated; `ASSEMBLY.md` and print sheets are generated with spliced blocks
(`<!-- gen:BEGIN name -->…<!-- gen:END -->`) so prose survives regeneration.

## Board mesh of record
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
- A fix that turns out to be for every build belongs in the base block; prove "no geometry change" by diffing the merged dict key by key, not by
  re-exporting (CGAL STLs are not byte-stable).
- FDM (owner's printer): walls in extrusion lines (two-line 0.85 mm), colour on TOP faces in ONE Z band per part (a coloured vertical flank costs a
  filament swap per layer), legends as 0.4 mm debosses, supports per print sheet.
- Print service (MJF/SLA): walls ≥ 1.2 mm where the geometry allows; list what stays thinner; part min size per process; two-tone via an **inlay
  plate** (a mark-shaped pocket is its own key when the mark is chiral) or a **badge** (metal plate in a pocket, UV-print or laser artwork as DXF +
  B-rep STEP).

## Census (every row = a check with yaml value, measured value, gate, FAIL/WARN/OK)
- Wall thickness by ray-cast, **bucketed by entry surface** (a blind-hole bottom skin is not the recess floor); report each entry class with its own
  count and gate.
- Connected components per piece (one), membranes (thin sheets), support area, mass from the measured STL volume (not the design estimate — write
  the method next to the number), snap/latch preload volume, mating lens estimates including ramp bands.
- Check-mode totals (`--no-render --interference`) differ from full-run totals (`--stl` adds the mesh rows): quote the mode with the numbers.
- Imported artwork (SVG) is measured from the PATH, not the canvas attributes (`resize(auto)` scales the glyph bbox).

## Interference / clearance
- Voxel/containment first, CGAL boolean only on flagged pairs (minutes per piece otherwise). Whole-piece overlaps empty except designed preloads.
- Guard rows: "board md5 = recorded, mesh md5 = recorded" must be OK or the whole check is about another board.
- Every envelope (connector housings, cage, heat sink, fan, inserts, screws) is a yaml box; the census asserts each is either inside a piece or in
  a declared cut-out.

## Drawings
Silhouettes + sections from the STLs of record (trimesh/shapely), dimension lines carry the yaml numbers (so a yaml change moves the number and the
geometry together), per-piece and assembly STEP (OCP/cadquery), `--check` = md5 sidecar keyed on the STL md5s. Run AFTER the final STL pass.

## Process rules
- A 25–35 min render + STL + interference chain: process pool for views and STL export, `--renders` off in check mode, STL cache by preset hash; kill it
  early when an owner addition arrives.
- Never run a case "check" in the working tree if it writes tracked files — the traceability sandbox copies `gen/ + design/` and symlinks the mesh.
- Print sheets and order sheets list filaments / processes per piece, orientation, supports, insert temperature/time and screw torque placeholders
  `[OWNER: …]` until measured.
- Debug dumps under `out/**/scratch/` (gitignored), never the repo root.
