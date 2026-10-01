# Print DFM — the vendor-independent manufacturability check and its self-improvement loop (`scripts/print_dfm.py`)

**Why it exists.** A vendor's upload-time checker is a free, fast second opinion — and it is weaker than its own engineer (it passed a plate whose
logo arms touched at 0.01 mm; the engineer refused it), length-tolerant (a 0.5 mm root under a rim passed up to ~60 mm and flagged at
longer lengths — a long lip built that way cracked on five parts), and tied to one vendor. The owner's framing: *"this need not be tuned to JLC, just
that that is where we saw good results."* So the rules are physics + the published process minimums, one row per process in
`design/dfm_processes.yaml` with a citation on every number; the vendors' verdicts are a **validation set**, never a fitting target. The tool
runs on the exported MESH (never the yaml) before every upload, and the census (`thin_wall_census.py`) keeps the DESIGN margin (`wall_gate`,
the vendor's grey line) — print DFM gates the printability floor, the census gates the margin; both are PURE adopt gates.

## 1. What it measures and the rules (one row each in the record)

Per surface sample (area-weighted, fixed seed): `t_ray` = thickness along the inverse normal (the census ray, origin nudged 1e-3 INTO the material —
nudged outward it hit its own face and read inf on every sample for a day while the ball covered every wall); `t_med` = the largest ball tangent
at the sample that no OPPOSING face (normal within 45° of the inverse normal) enters — reads a root / neck no ray sees and leaves convex 90° edges
alone; `t = min`; `t_k` = the same ball against ANY face that faces back (`COS_K` 0.05) = the knife-edge field. Both cast outward = void width `g`.
Sub-threshold samples link (radius `max(3 sample spacings, 2.5 mm)` — a purely density-scaled radius broke a long root band into 25 pieces) into
REGIONS with area, extent, min / median and class (wall < 30° limiting face, else wedge; on a layer process a wall whose normals lie within 30° of
the print Z is a **skin**). A **sliver** = area < `sliver_area` AND extent ≤ 2 × its thickness (a tangency / boolean patch); anything longer is a
feature however small its area (a Ø0.4 × 3.5 pin is 4.4 mm²).

| Rule | Fires when | Physics |
|---|---|---|
| **M manifold / bodies** | an edge not shared by exactly two faces (located; those inside legend boxes listed), inconsistent winding, or a solid count ≠ `--bodies N` (default 1) | an open mesh has no inside (every thickness below is unreliable); two solids touching at a vertex / edge / face without a union print as pieces |
| **C closed cavity** | an inward-facing closed shell | traps un-fused powder / resin (FLAG on `media: powder / resin`, escape hole ≥ 3.5 mm [V Hubs]); INFO on FDM (the slicer hollows it) |
| **W wall** | wall-class region, median `t < wall_min`, extent ≥ `slender × t` | [K] slenderness heuristic: a sub-minimum strip ~10 × longer than it is thick bends / cracks in depowdering and handling (the cracked long lip). Every FLAG row carries a `fix:` (thicken, widen, chamfer, re-orient) for a CAD part as much as a generated one |
| **R root** | a W region whose RAY median ≥ `wall_min` | a rim set inboard of its wall over a step stands on the overlap only; every ray reads the full rim |
| **Z skin** (layer processes) | skin-class region (normals within 30° of the print Z), median `< skin_min_layers × layer` | a horizontal skin is a LAYER count, not a perimeter count: a 0.6 sheet flat is three layers and prints, stood up it is a 0.6 wall (W); fewer than three layers = pinholes / sag |
| **F feature** | short wall-class region, median `< feature_min`, not a sliver | below the smallest formable feature it does not form or breaks off (a Ø0.4 × 3.5 pin) |
| **K knife edge** | `t_k` wedge region whose tip band `feature_min / (2 tan(a/2))` > `feature_min` (included angle < 53°) over ≥ `slender × feature_min` | a ridge of included angle a reads `2 s tan(a/2)` at distance s from its tip: the band below `feature_min` is what the tip loses — 30° frays 0.93, 50° 0.54, 60° 0.43 (passes), a square edge 0.25 (rounds, reads as nothing); a chamfer whose thin end stays ≥ `feature_min` has no band |
| **P point contact** | two surfaces ≤ `neck_max` apart on 15 section planes (neck or hairline slit) | arrives as two parts or cracks there — the engineer's finding, not the checker's |
| **V void / slot** | `g < detail_min` anywhere; on `media: powder / resin` also `detail_min ≤ g < void_min` over ≥ `slender × void_min` | an engraved stroke closes (MJF / SLA fuse it; FDM: one line width, the squish / gap fill closes it); a long slot does not clear powder / resin. FDM has **no long-slot rule** (`void_min: null`): a slot wider than one line is two walls with air between, nothing to clear |
| **H hole** | a round void (normals in two directions) `< hole_min` | closes or does not clear |
| **O overhang** (layer processes) | down-faces steeper than `overhang_max_deg` (+1° tolerance) whose footprint reaches further than `bridge_max` across | a steep region spanning less than `bridge_max` is bridged from its edges (a slot's round top, a shallow recess roof — listed). FLAG when the BODY prints with `supports: none` (`--supports` overrides the row), INFO otherwise |
| **B bridge** (layer processes) | a horizontal ceiling above the bed whose SPAN > `bridge_max` | the span is measured by rays from the ceiling sample nearest its inscribed-circle centre: both in-plane axes on material → min(inscribed circle, chord_x, chord_y) (a merged debossed word reads its stroke width, a rectangle its inscribed circle); exactly one axis → that chord (a pi roof open at the ends reads its width, a 2 × 40 tunnel roof 2 mm, a rebate split by full-height glue lands one strip, never the whole-rebate bbox); no axis → the inscribed circle (a relief ring reads its width). Never a bbox extent and never a raster run through the footprint mask (a run through a merged cluster reads any row of it; the dilation erases lands thinner than two cells) |
| **S size** | bbox outside `part_min` .. `build_max` | the vendor refuses the file |
| **L** INFO | regions, contacts and non-manifold edges inside legend boxes; slivers | legend boxes belong to the coupon rule; a tangency / boolean remnant has nothing to lose |
| **Y** INFO | wall-class surface between `wall_min` and `wall_reco` | the vendor's yellow band = the design margin; `print_targets.<t>.wall_gate` + the census own it |

**Legend boxes** are 3-D — `(x0, y0, z0, x1, y1, z1)` in the print frame, the legend's own Z band (a full-height box would exempt the wall under
the legend; the generator must not draw one). The generator writes them beside the record as `<piece>.boxes.json`; `--boxes <file>` loads them,
so a CLI run reproduces the gated record **byte for byte** (no run time inside the record — `_seconds` is printed, not written). `--land x0 y0 x1 y1`
is the legacy spelling (spans every Z). Inside a box: wall limit `legend_land_min`, void limit `legend_void_min`, every rule's findings listed in row L
instead of flagged; a region is inside when ≥ 50 % of its samples are. Every rule respects the boxes, W and R included.

Heat maps (`--render`, matplotlib): per-FACE minimum in the vendors' palette (grey ≥ `wall_reco`, yellow, red < `feature_min`, narrow voids dark
red), six faces + two isos — a per-sample field looks nothing like the vendor's picture; per-face MIN does.

## 2. Commands, what they print, what a FAIL means

| Command | Output | FAIL means |
|---|---|---|
| `scripts/print_dfm.py --list` | the process rows and their thresholds (BLOCKED rows named) | — |
| `scripts/print_dfm.py --process <row> <stl>... [--out DIR] [--boxes <piece>.boxes.json] [--supports none\|interior\|any] [--bodies N] [--render]` | one `PASS` / `FLAG` line per body, then one line per rule (`value \| limit \| where` with area × extent, min / median, bbox, span / tip band); `DIR/<piece>.json` (+ `<piece>.boxes.json`, + PNGs) | exit 1: a FLAG row names a real sub-minimum region on the MESH and ends with `fix:` (thicken / widen / chamfer / re-orient) — change the CAD or the generator (never the yaml alone), re-export, rerun. No waiver field exists; exit 2 = usage / configuration |
| `scripts/print_dfm.py --gate <dfm_dir>... [--open <tag>/<piece>=<id>] [--expect <tag>/<piece>=<reason>]` (adopt list) | `print_dfm gate: N bodies, M problem(s)`; every `OPEN <id>` and `EXPECTED FLAG (<reason>)` printed on every run; a stale `--open` / `--expect` entry is noted | exit 1: a record missing for a censused piece, an STL of the record set without a same-md5 record, a signature / rule-set version / threshold mismatch, a record against a row other than `print_targets.<t>.dfm_process`, or a verdict FLAG without `--open` naming an OPEN decision row that names the piece or `--expect` with the reason the body FLAGs BY DESIGN (a coupon that tests the limit, a dummy with real-part dimensions). Neither is a waiver: the record still says FLAG. A dir without a sibling `census/` is a record-only dir (coupons, dummies, colour bodies) and is checked the same way; `*.boxes.json` sidecars are skipped |
| `scripts/print_dfm.py --validate` | `[val] <stl> <verdict> <s>` per uncached body, the unique-geometry count, confusion matrix + rules fired as JSON, `RULE DEFECT: …` lines; writes `docs/reviews/PRINT_DFM_VALIDATION.md` (body table per GEOMETRY, confusion matrix, rules fired, §3a coverage per mechanism, §3b thresholds with their `[V]` / `[K]` tags and the tool's judgment constants; the `<!-- hand: begin -->` reading is kept) | exit 1: a geometry the vendor FLAGGED that we PASS = a rule is missing physics. Fix the rule, re-validate, `skill_retro.py` |
| `scripts/print_dfm.py --selftest` | `selftest OK: …` — a positive AND a negative construct per rule (the ray reads 0.8 on a 0.8 plate and R stays silent; the 0.5 root FLAGs W + R, 1.3 passes; pins Ø0.4 / Ø0.3 F, Ø1.2 pass; ridges 30 / 40 / 50° K, 60 / 90° read but pass; 0.6 sheet flat skin PASS, 0.4 Z, stood up W; 2 mm tunnel span 2, 15 mm B; tee arms read their inscribed width and stay silent, pi roof 32 mm bridge, pi 6 × 40 silent, a lands-split rebate 3 × 6.1 silent, a 1.4 relief ring and an open groove read 1.4, debossed 1.0 strokes read 1.0; 2 mm slot roof bridged, 24 mm O; cavity C; open mesh / touching cubes M; gate incl. `--expect`; validate incl. twin grouping) | the tool or its dependencies are broken — nothing else runs. A dead measure passes a verdict-only selftest (the ray read inf for a day while the ball covered every wall): assert every measure finite and near a known value, and assert the rule SILENT where it must be |
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

## 4. Validation on record (the first validation set: 42 labelled JLC3DP MJF / SLA files = 37 geometries, 27 with a verdict)

**Grouping by geometry first**: four uploads of one tray (OpenSCAD triangle order, an ASCII twin) are ONE data point; `--validate` unions files
whose face count is equal and whose volume (0.05 mm³), area (0.5 mm²) and bbox (0.01 mm) agree — a hash splits twins at a rounding boundary. On the
unique geometries: 0 looser, 20 agree, 7 stricter — every stricter case has a reason; the coverage table (§3a) says which mechanisms the agreement
rests on (5 rim-on-root / thin wall, 3 knife edges, 3 mixed) — "0 looser" is a statement about those, not about every rule. **W / R validated both ways**: the 0.5 root under a rim flagged at the long lengths,
the fixed roots (≥ 1.1) and the bodies of record passed at the vendor and here. **Length dependence**: the same 0.4–0.5 root over 40–58 mm passed
the vendor's checker and flags here (L/t ≥ 10 → 5 mm for a 0.5 root); stricter by design — the part that cracked was built exactly so. **K validated
both ways** (rail wedges, 36° rail tips and cove lips flag by their tip band; chamfers into ≥ 1.3 walls pass); two 0.04 mm chamfer tips the vendor
missed were found independently by a blind review the same day. **R separated from W only once the ray was alive**: with the ray dead, R fired on
every W region; alive, a scaled-down tray whose rim is itself the thin wall reads W only, the real roots keep W + R. **The one body of record whose
verdict moved** under the corrected rules was a genuine one-layer (0.2 mm) horizontal skin the dead ray had hidden behind a "wall sliver" — rule Z. **P validated by the engineer**, not the checker (the checker passed 0.003–0.018 mm arm contacts). **V / H not
decidable** (every V body also failed W; H never fired); **F / S / C / Z / O / B not exercised** by any vendor — their numbers are the published minimums and their positive / negative constructs live in `--selftest` (FDM rows carry `validated_on: []` until a print verdict is recorded). Heat maps per
face matched the vendor's pictures: a red inner wall floor-to-ledge from a 0.5 root at its top edge, and the "hairline at the wall foot" was the
same face at a grazing angle.

## 5. Adding a vendor in one sitting

1. Fetch its design guide / capability page; one row with `[V]` lines (URL + date) for `wall_min`, `feature_min`, `detail_min`, `hole_min`,
   `build_max` / `part_min`; `[K]` with the source named for the rest; `validated_on: []`. 2. `--list` shows it; `--process <row>` on a body of
   record. 3. Kickoff C8 names the row per print target (`print_targets.<t>.dfm_process`). 4. The first verdict → (b). 5. Retro carries the row.

Row fields a new process needs beyond the minimums: `media` (powder / resin / none — rules C and V), `layer` + `skin_min_layers` on a layer process
(rule Z), `void_min: null` on FDM (the long-slot rule is a media rule), `supports` as the process DEFAULT (the generator passes the body's own setting),
and a colour-body row (`skin_min_layers: 1`, `supports: none`) when multi-material accents or marks are gated as bodies of their own.

Dependencies (project venv): `numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml`; `matplotlib` for `--render`.
