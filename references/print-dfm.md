# Print DFM — the vendor-independent manufacturability check and its self-improvement loop (`scripts/print_dfm.py`)

**Why it exists.** A vendor's upload-time checker is a free, fast second opinion — and it is weaker than its own engineer (it passed a plate whose
logo arms touched at 0.01 mm; the engineer refused it), length-tolerant (a 0.5 mm root under a rim passed up to ~60 mm and flagged at 90 and
147 mm — the 141 mm lip built that way cracked on five parts), and tied to one vendor. The owner's framing: *"this need not be tuned to JLC, just
that that is where we saw good results."* So the rules are physics + the published process minimums, one row per process in
`design/dfm_processes.yaml` with a citation on every number; the vendors' verdicts are a **validation set**, never a fitting target. The tool
runs on the exported MESH (never the yaml) before every upload, and the census (`thin_wall_census.py`) keeps the DESIGN margin (`wall_gate`,
the vendor's grey line) — print DFM gates the printability floor, the census gates the margin; both are PURE adopt gates.

## 1. What it measures and the rules (one row each in the record)

Per surface sample (area-weighted, fixed seed): `t_ray` = thickness along the inverse normal (the census ray); `t_med` = the largest ball tangent
at the sample that no OPPOSING face (normal within 45° of the inverse normal) enters — reads a root / neck no ray sees and leaves convex 90° edges
alone; `t = min`. Both cast outward = void width `g`. Sub-threshold samples link (radius `max(3 sample spacings, 2.5 mm)` — a purely
density-scaled radius broke a 147 mm root band into 25 pieces) into REGIONS with area, extent, min / median and class (wall < 30° limiting face, else wedge).

| Rule | Fires when | Physics |
|---|---|---|
| **W wall** | wall-class region, median `t < wall_min`, extent ≥ `slender × t` | Kirchhoff thin plate (L/t ≥ 10) — bends / cracks in depowdering and handling. Every FLAG row carries a `fix:` (thicken, widen, chamfer, re-orient) for a CAD part as much as a generated one |
| **R root** | a W region whose RAY median ≥ `wall_min` | a rim set inboard of its wall over a step stands on the overlap only; every ray reads the full rim |
| **F feature** | short wall-class region, median `< feature_min`, area ≥ `sliver_area` | below the smallest formable feature it does not form or breaks off |
| **K knife edge** | wedge-class region, thin end `< feature_min` over ≥ `slender × feature_min` | a free taper the process cannot form (rail tips, cove lips); a chamfer whose thin end stays ≥ `feature_min` is a listed INFO wedge |
| **P point contact** | two surfaces ≤ `neck_max` apart on 15 section planes (neck or hairline slit) | arrives as two parts or cracks there — the engineer's finding, not the checker's |
| **V void / slot** | `g < detail_min` anywhere; `detail_min ≤ g < void_min` over ≥ `slender × void_min` | an engraved stroke closes; a long slot does not clear powder / resin |
| **H hole** | a round void (normals in two directions) `< hole_min` | closes or does not clear |
| **O / B** (FDM) | down-faces steeper than `overhang_max_deg`; ceilings longer than `bridge_max` | FLAG when `supports: none`, INFO otherwise (the slicer g-code check owns visible faces) |
| **S size** | bbox outside `part_min` .. `build_max` | the vendor refuses the file |
| **L** INFO | regions inside `--land` boxes; slivers `< sliver_area` | legend lands belong to the coupon rule; a tangency / boolean remnant has nothing to lose |
| **Y** INFO | wall-class surface between `wall_min` and `wall_reco` | the vendor's yellow band = the design margin; `print_targets.<t>.wall_gate` + the census own it |

Heat maps (`--render`, matplotlib): per-FACE minimum in the vendors' palette (grey ≥ `wall_reco`, yellow, red < `feature_min`, narrow voids dark
red), six faces + two isos — a per-sample field looks nothing like the vendor's picture; per-face MIN does.

## 2. Commands, what they print, what a FAIL means

| Command | Output | FAIL means |
|---|---|---|
| `scripts/print_dfm.py --list` | the process rows and their thresholds (BLOCKED rows named) | — |
| `scripts/print_dfm.py --process <row> <stl>... [--out DIR] [--render]` | one `PASS` / `FLAG` line per body, then one line per rule (`value \| limit \| where` with area × extent, min / median, bbox); `DIR/<piece>.json` (+ PNGs) | exit 1: a FLAG row names a real sub-minimum region on the MESH and ends with `fix:` (thicken / widen / chamfer / re-orient) — change the CAD or the generator (never the yaml alone), re-export, rerun. No waiver field exists; exit 2 = usage / configuration |
| `scripts/print_dfm.py --gate <dfm_dir>...` (adopt list) | `print_dfm gate: N bodies, M problem(s)` | exit 1: a record missing for a censused piece, an STL that changed since its record (md5), or a verdict FLAG without an `--open <tag>/<piece>=<decision id>` naming the OPEN decision. `--open` is not a waiver: the record still says FLAG, the gate prints `OPEN <id>` and the decision row owns the fix |
| `scripts/print_dfm.py --validate` | `[val] <stl> <verdict> <s>` per uncached body, the confusion matrix + rules fired as JSON, `RULE DEFECT: …` lines; writes `docs/reviews/PRINT_DFM_VALIDATION.md` (generated sections; the `<!-- hand: begin -->` reading is kept) | exit 1: a body the vendor FLAGGED that we PASS = a rule is missing physics. Fix the rule, re-validate, `skill_retro.py` |
| `scripts/print_dfm.py --selftest` | `selftest OK: …` (0.8 plate FLAG, 2.0 plate PASS, 0.5 root under a 2.0 rim × 90 mm FLAG W + R, root 1.3 PASS, SLA size, gate, validate) | the tool or its dependencies are broken — nothing else runs |
| `scripts/scad_lint.py <generated.scad>...` | silent, or every line with a statement hidden behind `//` | exit 1: the generator emitted code after a comment; OpenSCAD dropped it (a plate lost its webs for two days while the yaml read right) — one statement per line, lint on every emit |

Paths default to the project root (the nearest `project.yaml`): table `design/dfm_processes.yaml` (falls back to the skill's template when the
project has none yet), verdicts `docs/quotes/dfm_verdicts.yaml`, records `out/dfm_validation/`, doc `docs/reviews/PRINT_DFM_VALIDATION.md`;
`--processes / --verdicts / --val-dir / --val-doc` override. Run time: 5–20 s per body (60 k–300 k samples ∝ area), ~1.5 s per heat-map view.

## 3. The loop (SKILL.md §8.1 — the commands are the procedure)

- **(a) Before every vendor upload**: `scripts/print_dfm.py --process <row> --out out/.../dfm <stl>` must PASS; `--gate out/.../dfm` sits in
  `gates.adopt` beside the census `--gate-dir`. The vendor's PASS is necessary, never sufficient.
- **(b) After every vendor verdict**: append the row to `docs/quotes/dfm_verdicts.yaml` (stl, md5-8, process, vendor, date, verdict, evidence =
  the saved API JSON / screenshot / mail path), run `--validate`. Vendor FLAG + ours PASS = **RULE DEFECT**: find the physics the rule lacks (a
  measure that cannot see the feature, a missing class), fix it in `print_dfm.py`, bump `VERSION`, re-validate, run `scripts/skill_retro.py` so the
  change flows back to the skill. Vendor PASS + ours FLAG = **stricter**: write the physical reason under the hand marker of the validation doc;
  the rule stands (the vendor's checker is the weaker instrument). Never move a threshold to match a vendor.
- **(c) A new vendor or process** = ONE new row in `design/dfm_processes.yaml`: its published minimums `[V]` with URL + date (a 404 = BLOCKED,
  value `null`, the row refuses to gate), the rest `[K]` with the source named, `validated_on: []`. The retro (`skill_retro.py` §8) diffs the
  project's table against `templates/design/dfm_processes.yaml` and lists NEW rows, CHANGED numbers (with the citation on the line) and
  VALIDATED rows as items to carry into the template.
- **(d) Check rows read the MESH, never the yaml** — a row that quotes a design number proves nothing about the part; generated code is linted
  (`scad_lint.py` on every emitted SCAD) because the yaml and the mesh can disagree silently.

## 4. Validation on record (worked example: 32 labelled JLC3DP MJF / SLA verdicts, 2026-09-22 … 30)

0 looser, 24 agree, 8 stricter — every stricter case has a reason. **W / R validated both ways**: the 0.5 root under a rim flagged at 90 and 147 mm,
the fixed roots (≥ 1.1) and the bodies of record passed at the vendor and here. **Length dependence**: the same 0.4–0.5 root over 40–58 mm passed
the vendor's checker and flags here (L/t ≥ 10 → 5 mm for a 0.5 root); stricter by design — the part that cracked was built exactly so. **K validated
both ways** (rail wedges, cove lips flag; chamfers into ≥ 1.3 walls pass); two 0.04 mm chamfer tips the vendor missed were found independently
by a blind review the same day. **P validated by the engineer**, not the checker (the checker passed 0.003–0.018 mm arm contacts). **V / H not
decidable** (every V body also failed W; H never fired); **F / S / O / B not exercised** — their numbers are the published minimums. Heat maps per
face matched the vendor's pictures: a red inner wall floor-to-ledge from a 0.5 root at its top edge, and the "hairline at the wall foot" was the
same face at a grazing angle.

## 5. Adding a vendor in one sitting

1. Fetch its design guide / capability page; one row with `[V]` lines (URL + date) for `wall_min`, `feature_min`, `detail_min`, `hole_min`,
   `build_max` / `part_min`; `[K]` with the source named for the rest; `validated_on: []`. 2. `--list` shows it; `--process <row>` on a body of
   record. 3. Kickoff C8 names the row per print target (`print_targets.<t>.dfm_process`). 4. The first verdict → (b). 5. Retro carries the row.

Dependencies (project venv): `numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml`; `matplotlib` for `--render`.
