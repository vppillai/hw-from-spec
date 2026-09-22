# fea-stage.md — structural / thermal checks on the case, the board and the assembly

## Stack (all pip/brew, verified 2026-09-20/21)
Gmsh (Python API; boxes, plates from the outline polygon with drilled holes) · **fTetWild** via `wildmeshing` (tetrahedralises OpenSCAD/CGAL STLs
that Gmsh rejects: overlapping/self-intersecting facets, zero dihedral) · scikit-fem (P1/P2 tets, linear elasticity, heat) · pyamg (SA-AMG + CG for
> 60k DOF) · trimesh/rtree/shapely (STL load, ray probes, capped crops) · meshio · matplotlib Agg (figures). Optional: cadquery to read vendor STEPs
for heavy solids (heat sink, cage).

## Recipe
1. **Geometry of record**: case STLs of the build of record (after the FINAL `--stl` pass), the board plate from the CAD outline polygon + drills via
   the CAD's Python in a subprocess, vendor STEP solids where the mass matters. Every case names its inputs; dry-run each case's lookups before a
   long run (a case lost its geometry source silently when a part was removed).
2. **Mesh**: fTetWild for CGAL STLs, Gmsh for analytic geometry; drop zero-volume slivers, then **compact the node set** (`np.unique(t,
   return_inverse=True)`) — an orphan node is a zero row in K → SuperLU "exactly singular", NaN; do the compaction on the cache-load path too.
3. **Cache keyed on content**: STL md5 for case meshes; copper signature + outline/hole digest for the board (a silk-only hop must not re-solve 600 s);
   per-label result records merged (`--only <subset>` must never overwrite the full record: one complete `fea_results_all_<label>.json` per label).
4. **Solve**: per case in its own process (multiprocessing), pyamg for the big systems; ties between parts as penalty springs with a gap.
5. **Status ladder**: `if not isfinite(x): return "FAIL"` FIRST in the shared status helper (NaN compares False against every limit and shipped as OK
   once); OK / WARN / FAIL against material limits (yield, glass temperature) with the margin printed.
6. **Report**: FEA_REPORT.md generated with a version-to-version table (previous version's record extracted from the commit that produced it),
   per-case: load, BCs, mesh size, DOF, peak/p99 von Mises, displacement, status, figure paths; composites (undeformed/deformed pairs ≥ 2000 px + 16:9
   slide variants) from per-case `.npz` sidecars via one shared plotting module.
7. **Selftest**: a cantilever with the analytic deflection within a few %, a NaN case that must read FAIL, a merge of a subset record.

## Cases that paid for themselves (worked examples)
- Case torsion (two-hand twist): a single bottom dovetail is a hinge; two rail pairs ~17 mm apart gave ~2.5× stiffness.
- Snap tab: the hand formula under-read peak stress by ~1.2× (slit-root concentration); peak ∝ deflection — reduce travel before thickening.
- Pillars / bosses under insert load; press-fit insertion force on the board supported at the pressing points; mating force; USB side load; drop;
  assembled case + board (+ hood) twist; thermal per power class with hood on / hood off / forced air.
- Composites of the analysis are release collateral (renders index) and are graded by the collector.

## Pitfalls
- md5-stamped consumers (report, drawing sidecar) run after the final STL pass; CGAL exports differ byte-wise between identical runs.
- Coupled cases drift with a rebuilt board mesh while board-alone numbers stay bit-identical — report both, explain the delta.
- A thermal "warn at warning / throttle at alarm − margin" rule with a fixed cap can make WARN unreachable; make the interplay explicit and print both.
- Long solves block-buffer stdout when redirected: judge progress by the process and its output files, or `python -u`.
