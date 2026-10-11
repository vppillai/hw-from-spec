# fea-stage.md — structural / thermal checks on the case, the board and the assembly

## Stack (all pip/brew, verified 2026-09-20/21)
Meshing: Gmsh (Python API; boxes, plates from the outline polygon with drilled holes) · **fTetWild** through `wildmeshing` (tetrahedralises
OpenSCAD/CGAL STLs that Gmsh rejects: overlapping/self-intersecting facets, zero dihedral). Solver and tools: scikit-fem (P1/P2 tets, linear
elasticity, heat) · pyamg (SA-AMG + CG for > 60k DOF) · trimesh/rtree/shapely (STL load, ray probes, capped crops) · meshio · matplotlib Agg
(figures). Optional: cadquery to read vendor STEPs for heavy solids (heat sink, cage).

## Recipe
1. **Geometry of record**: case STLs of the build of record (after the FINAL `--stl` pass), the board plate from the CAD outline polygon + drills with
   the CAD's Python in a subprocess, vendor STEP solids where the mass matters. Every case names its inputs; dry-run each case's lookups before a
   long run (a case lost its geometry source silently when a part was removed).
2. **Mesh**: fTetWild for CGAL STLs, Gmsh for analytic geometry. Drop zero-volume slivers, then **compact the node set** (`np.unique(t,
   return_inverse=True)`). An orphan node is a zero row in K → SuperLU "exactly singular", NaN. Do the compaction on the cache-load path too.
3. **Cache keyed on content**: STL md5 for case meshes; copper signature + outline/hole digest for the board (a silk-only hop must not re-solve
   600 s). Per-label result records are merged: `--only <subset>` must never overwrite the full record, so keep one complete
   `fea_results_all_<label>.json` per label.
4. **Solve**: per case in its own process (multiprocessing), pyamg for the big systems; ties between parts as penalty springs with a gap.
   **Derive the tie gap**: `lap clearance + 0.75 × surface node spacing`, with the yaml value as the floor. Below that the tied fraction follows
   the surface mesh. One rim had 23 % tied at a 0.7 gap on a 1.2 mm mesh, and 0.37 to 0.62° twist for one solid. Report the tied fraction of the interface
   nodes, and run one gap and one mesh variant before a tie-coupled number enters a gate.
5. **Status ladder**: `if not isfinite(x): return "FAIL"` comes FIRST in the shared status helper. NaN compares False against every limit and
   shipped as OK once. The helper grades OK / WARN / FAIL against material limits (yield, glass temperature) with the margin printed.
   **Who decides**: the material limits and the required margin come from the TDS and the kickoff answers (owner rows). A WARN or a margin below the
   limit is reported with its number. It is **accepted only by an owner D row** cited in the report; an agent never downgrades a WARN.
   Anisotropy (MJF Z, FDM across layers — `dfm-printed-enclosure.md` §1) is applied as a factor and stated.
   **Gate off the bands (St. Venant)**: gate the von Mises on the tets that touch no load-band, support-band or tie-band node. The bands are
   modelling devices; a sliver tet on a tie-spring node reads ten times its average. Report the band peak as INFO. An INFO above the limit, or a
   2× move on a re-keyed body, is an owner line in the chain report, never a silent cell. After a material change, check every FEA threshold,
   not only the case FEA. A board-assembly case kept the old allowable and read FAIL on the new body. The bare case (no board) is the sensitive
   torsion case; read its row after every body change.
6. **Report**: FEA_REPORT.md is generated with a version-to-version table (previous version's record extracted from the commit that produced
   it). Per case: load, BCs, mesh size, DOF, peak/p99 von Mises, displacement, status, figure paths. Composites (undeformed/deformed pairs ≥
   2000 px + 16:9 slide variants) come from per-case `.npz` sidecars through one shared plotting module.
7. **Selftest**: a cantilever with the analytic deflection within a few %, a NaN case that must read FAIL, a merge of a subset record.

## Drop: derive the stop, never assume it
- An assumed stop distance can ask for more energy than the drop has. At a 0.3 mm stop one unit stored 1480 N mm of elastic energy; its 0.75 m
  drop carried 776 N mm. Check the energy before the stress.
- Energy balance at the deepest point: `m g h = σ_y V(d) + U_el(F)`. Here `F(d) = σ_y A(d)`, and `U_el = U_ref (F / F_ref)²` comes from one
  FEA solution. Solve `d` by bisection, then load the FEA with `F_peak`. The unit's elastic flex took half the drop energy in the worked example.
- `V(d)` comes from the real STL: one capped plane slice behind the corner tip. The real rounds held 0.9 mm³ at 0.3 mm and 14 mm³ at 1 mm; a
  sharp corner reads a smaller force.
- The contact zone is plastic by construction: an INFO row with the crush depth and the Neuber strain against the elongation at break. The far
  field outside the zone and the bands stays gated at yield / margin. A selftest row solves a cube corner against the closed form.

## Thermal: state what the model can credit
- Say what the thermal model reads. A sink-only model with `h` as a yaml constant and the pose as a factor on `h` cannot credit a vent change.
  Print case geometry beside a model number as INFO, never as an input the model does not read.
- State the pass target in the model's own variable: `q` is linear in `h` to 0.1 %, so the target is `h × limit / q`. A row the model cannot
  close needs a bench measurement row (kickoff E4b), not a geometry change.
## Cases that paid for themselves (worked examples)
- Case torsion (two-hand twist): a single bottom dovetail is a hinge; two rail pairs ~17 mm apart gave ~2.5× stiffness.
- Snap tab: the hand formula under-read peak stress by ~1.2× (slit-root concentration); peak ∝ deflection — reduce travel before thickening.
- Pillars / bosses under insert load; press-fit insertion force on the board supported at the pressing points; mating force; USB side load;
  drop. Assembled case + board (+ hood) twist; thermal per power class with hood on / hood off / forced air.
- Composites of the analysis are release collateral (renders index) and are graded by the collector.

## Pitfalls
- md5-stamped consumers (report, drawing sidecar) run after the final STL pass; CGAL exports differ byte-wise between identical runs.
- Coupled cases drift with a rebuilt board mesh while board-alone numbers stay bit-identical — report both, explain the delta.
- A thermal "warn at warning / throttle at alarm − margin" rule with a fixed cap can make WARN unreachable; make the interplay explicit and print both.
- Long solves block-buffer stdout when redirected: judge progress by the process and its output files, or `python -u`.
- `--only <subset>` must not wipe the other cases of a record. Merge per label, and let the stale-case sweep remove only the cases the design
  rules skipped. A report written from a subset run lacks the other rows; run the full set for the report of record. Check the analyses keys after
  every subset run.
- fTetWild is not deterministic between runs (44.5 against 47.9 MPa at the same load). The mesh cache of record is the determinism anchor. A
  worktree has none (gitignored). Create the cache folder and copy the cache files for the same keys before a run that must compare with the
  record. The result's `cached` flag is the tell.
- A geometry change on one body re-keys every case that reads it, and those cases move a few percent. "Unchanged" rows hold only for bodies
  with an unchanged md5.
- `--report-only` in a fresh worktree is not the full run. Check the report diff: only the intended lines may change. A run in a worktree writes
  the report from the merges it holds. Run the full set once on the merged main tree before the record round.
- The drop gate is one element off the fixed set. A regenerated mesh can put a sliver cluster on a band and move the number 4× while the
  displacement field moves 0.2 %. Locate the peak elements before you read a move as a geometry effect.
- Masses are in tonnes (ρ in t/mm³, N = t mm/s²). Convert at one line and name the unit in the comment. A point mass in grams added as kg gave a
  60 g unit and a 935 g load.
