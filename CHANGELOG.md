# CHANGELOG — hw-from-spec

## Current state (0.11.5) — read this instead of replaying the entries below

- **Procedure** `SKILL.md`: day-1 setup + the kickoff questionnaire (A0 scope, then every owner decision the scope needs, recommended answers,
  twelve batches at most), the gate model per scope (ee: G0 → G1 → G2 → order; mech: G0 → M1 → M2 → case order; both), the manufacturability bar
  (zero errors / zero warnings / no waivers, enforced by scripts), generated-only, the decision log, parts tags [V] / [K] / [K owner-read] / [S],
  blind reviews with a record-reading verifier, layout + fab DFM mirror, the case pipeline with two PURE mesh gates (census margin, print-DFM
  floor), the stability row for anything that stands free (kickoff C12) and the three assembly-model rows (every placement det +1, a fit row per
  mating pair, an orientation row per one-sided part type — renders are not evidence of buildability), the software track, release cut + production cut + the arrival checklist + spec errata, agent operations with a measured resource budget
  (measure → audit → change; previews on the fast engine, geometry of record on the engine that passes the mesh gates; caches as determinism checks), the retro,
  the PCBA fab after the order (engineer questions answered on pad-1 positions, the production-file package diffed per layer) and its upfront
  half (`ASSEMBLY_NOTES` in the package, the fab's-eye silk pass, hole sizes in the order remark, arrival rows A-0 / A-5), the fab's second
  round pixel-diffed before an answer, colour / cosmetic inserts (the whole face, host frame + lip + sill, the edge budget, fused STL for DFM
  and colour 3MF for the order) and the at-the-gate map rule (design 0.3 above the vendor's gate; six views counted by `heatmap_count`).
- **Scripts** (`project.yaml`-driven, every one with `--selftest`, exit 0 / 1 / 2): `project.py` (reader, scaffold, slots, kickoff --check,
  gates-required, record, env), `known_issues`, `traceability`, `release_report`, `collect_renders`, `assembly_guide`, `reorg_paths`, `dfm_check`,
  `erc_gate`, `gate_check`, `handoff_header`, `thin_wall_census` (design-margin gate), `print_dfm` (printability-floor gate + `--validate`),
  `thin_wall_check` (quick look + pinch), `heatmap_count` (yellow / red of a vendor map capture, stdlib), `stability` (CoG vs support hull at the worst pose; `improper_placements` = the det +1 row), `scad_lint`, `step2stl`, `arrival_checklist`, `skill_retro` (+ `--apply`), `jobs.sh` (the heavy-job
  pool), `adopt_gates.sh`, `clone_gate.sh`, `doc_voice_lint`, `generic_lint`. Mesh stack: `numpy trimesh scipy shapely rtree networkx
  mapbox-earcut embreex` (the Embree ray engine keeps a census in seconds under 1 GB).
- **Layout** (`references/project-yaml.md` §Layout): ten numbered folders in the order of the project's life — `00-now` (five generated answer
  pages) `10-spec` `20-design` `30-board` `40-case` `50-kits` `60-orders` `70-release` `80-reviews` `90-log` — plus the machinery (`gen/ scripts/
  tools/ lib/ Makefile CLAUDE.md`). Names are nouns (a revision is `rev0`, a kit is its print target, the hash lives inside the folder), one current
  thing per path, records beside what they describe; every path is a `paths:` key with these defaults; the templates folder mirrors the tree.
- **Templates**: CLAUDE.md, project.yaml (kickoff / board / print_targets / fab_dfm / arrival_checklist / host), SPEC + VERIFY + SPEC_ERRATA,
  the governance records, PARTS_VERIFICATION + PROCUREMENT, TEST_PLAN, REVIEW_HANDOFF, DFM_ROUND, VENDOR_REVIEW_RECORD, CENSUS_GATE_ROWS,
  design/{traceability, erc_accept, dfm_processes, arrival_checklist}.yaml, production_cut.yaml, datasheet note, G1 pack, CI workflows + Makefile.
- **References**: project-yaml, kickoff-questionnaire, schematic-phase, pcb-layout-dfm, fab-dfm, case-pipeline, dfm-printed-enclosure,
  print-dfm, print-kit, fdm-print-optimisation, cnc-enclosure, fea-stage, part-verification, software-track, release-and-cut, vendor-review,
  agent-ops, pitfalls — one home per rule, the others link.
- **Checks**: three read-only tiers — inner `scripts/iteration_gate.sh [-- <cmd> ...]` (a change's `--check` + grader set), standard
  `scripts/adopt_gates.sh --no-clone` (`make gates`), release `scripts/adopt_gates.sh` (`make check`); `smoke/run_smoke.sh` runs every script selftest, the rule greps, the enforcement negatives, both lints
  and the evals; 18 evals
  with mechanical checks; `docs/reviews/INDEX.md` lists every blind review of the skill.
- **Generic by rule**: the skill names no project, part, board, order, account or person — `scripts/generic_lint.py` reads the whole repo
  (CHANGELOG and docs included; history keeps its measured numbers), a fenced worked example keeps numbers and kinds but never a name, and the
  repo carries no project retro (a retro report is folded, then deleted).

## 0.11.5 — 2026-10-05 — Colour inserts, the vendor's map at the gate, and the fab's second round

Source: one case moved its whole UI face to a full-colour MJF insert (owner: "design the entire UI with the full color inserts that I can glue in.
there should be guides for repeatability ... professional and clean"), the vendor's heat map rejected a wall the API had passed, the full-colour
line refused a 1.5 mm plate at the form, and the PCBA fab's "updated DFM" was the first render re-titled.

### Added
- `references/dfm-printed-enclosure.md` §12 **full-colour / multi-material inserts**: the insert is the whole functional face; the host keeps a
  frame ≥ gate, a lip ≥ gate × ≥ gate, a sill; glue gap 0.3 self-centres, the hanging block keys rotation; the **edge budget** (host wall + gap +
  land ≥ 2 × gate + gap) and the way out when the span is short (features run out through the insert's edge); files (fused STL for the analyser
  and the census, colour 3MF with basematerials and fixed zip timestamps for the order, colour-split bodies never censused, the insert routed
  through the inlay path); the full-colour line facts (min bbox 2 × 2 × 10 at the form, colours read, 14-day build, HDT 80 = cosmetic only, tone
  judged on arrival with a designed fallback); a pocket over cuts from the other face; a logotype is never a deboss. §13 **the map at the gate**:
  a wall at the gate reads yellow (design 0.3 above, six views counted by `scripts/heatmap_count.py`), the opposing-sample metric reads convex steps
  (slice the mesh before changing geometry; remove the step, never thin), the odd-one-out pass on repeated features.
- `scripts/heatmap_count.py`: yellow / red pixel count of a vendor heat-map capture outside the legend box (`--legend-x/-y` fractions),
  exit 1 on any; `--selftest`.
- `references/vendor-review.md` §5 **round 2**: the "updated DFM" diffed pixel-wise against the first, the ambiguous picture (labels turned,
  marks unchanged) answered with a request to state the cathode position and the fab's picture marked red / green, skipped confirmations
  re-asked, no release on an ambiguous picture; §4: signing in empties the quote (reload all lines in one upload), the order-detail page as the
  record of line ids by text capture.
- `templates/20-design/arrival_checklist.yaml` FA-3b: colour / cosmetic inserts dry-fitted before glue, legends crisp, tone judged beside the body.
- `references/pitfalls.md`: jlc / fab (at-the-gate yellow, full-colour min bbox, round-2 re-title, sign-in empties the quote) and mechanical /
  case (insert edge budget, inlay ≠ piece, pocket over the other face's cuts, odd-one-out, two OpenSCAD traps: `[0:-1]` on an empty list, a
  `//` comment swallowing a one-line module's brace). `SKILL.md`: one bullet for the insert + the gate rule, one sentence for round 2.

## 0.11.4 — 2026-10-05 — PCBA fab after the order: engineer questions, the production-file package, and pre-answering both before the order

Owner: "do it. but also make it so that we proactively do things upfront as well whenever possible". Source: one board order whose assembly
engineer asked for a connector placement picture and the polarity of sixteen parts (two of one footprint family were drawn 180° off in the
fab's picture), then sent the CAM production package for approval.

### Added
- `references/vendor-review.md` §5 **engineer questions**: the snapshot convention (`+` anode, `−` cathode, dot pin 1, flag, bottom mirrored),
  read against the board's pad-1 positions and nets, never the CPL rotation; answer per part class; a body-on-their-snapshot picture for a
  custom-footprint connector; the reply format and the follow-up rows. §6 **production-file package**: what the package is (CAM Gerbers, ODB++
  job, the upload, the order-parameter file), the per-layer XOR method with difference components mapped to the drill table, the compensation
  read from the aperture headers, the list of expected CAM differences (compensation ring, inner non-functional pad removal, rail-slot mask
  relief, via-plug layer, code placeholders, drill oversizes), the order-parameter comparison, the APPROVED-with-two-confirmations reply.
  §7 **upfront**: the same questions answered in the package before the fab asks.
- `references/fab-dfm.md` §9: the `ASSEMBLY_NOTES` contract (project-side generator; renders with the cathode end / pin-1 corner per part
  class, custom-footprint connector bodies with pin 1 and mating direction, empty / unplated holes with finished sizes and tolerances, keyed on
  the board md5 + models). `templates/production_cut.yaml`: deliverable `assembly_notes` (MFG-004, `{{ASSEMBLY_NOTES_CHECK}}` slot, ee / both).
- `templates/20-design/arrival_checklist.yaml` §A: A-0 (production-file package reviewed the day it arrived, before the fab's approval reply),
  A-5 (the engineer-question answers seen in the fab's final photos); B-2 checks the rotated parts first on the bench. `templates/90-log/GATES.md`:
  G2 prerequisite "fab's-eye polarity pass", board-order row `ASSEMBLY_NOTES` in the package and the order remark pointing at it. `templates/VENDOR_REVIEW_RECORD.md` §7: the per-part and per-layer tables.
- `references/pcb-layout-dfm.md` §10: the fab's-eye silk pass (a mark only on the bottom at an odd rotation, a mark under mask, a custom
  footprint without a body outline = a production-hold question) and the pointer to the notes. `SKILL.md` §10: one bullet for both halves.
- `references/pitfalls.md` jlc / fab: two rows (snapshot reading; CAM package review).

### Changed
- Nothing measured; no script changed.

## 0.11.3 — 2026-10-04 — the skill is generic: no project, part, board, order or person named anywhere in the repo, project retros removed from the repo, the generic lint covers the whole repo

Owner: "clean up the skill, not to refer to specific projects, but to be a generic skill". A wording and naming pass: no measured value,
threshold, rule or code path changed.

### Changed
- Every reference, script docstring and comment, template, smoke fixture, eval note and workflow comment that cited the project the skill was learned on (or
  a project, board, case or part by name) now states the rule generically and attributes the number to its kind of evidence ("a measured first
  article on a 0.4-nozzle desktop printer", "one vendor-MJF tray", "a six-leg desk walker"); the numbers are unchanged. Part labels become their
  generic kind (sliders, feet, bearing necks, pins); the two worked-example block markers lose their project tag.
- The smoke fixture set is renamed `40-case/vendor_mjf/` (the fixture's print-target key; the geometry is unchanged), and the
  `project.py` selftest's set likewise; the smoke's leak grep keeps the preset patterns and leaves project names to the lint's term file.
- **`scripts/generic_lint.py`**: default file set = every text file of the repo except `.git/`, `.venv/`, `__pycache__/`, `LICENSE` (the
  copyright holder is a legal notice) and the term file — `CHANGELOG.md` and `docs/` are no longer skipped; a worked-example block still skips the
  number groups but NOT the `*_names` / `*_ids` groups (a block may not carry a project name); a marker counts only when it opens a line (so the
  lint can read its own source); CHANGELOG and `docs/` keep their measured numbers and the skill's own review finding ids (`design_dimensions`,
  `review_ids_as_citations` do not apply there). Selftest: whole-repo walk, a name inside a block is a hit, history keeps numbers, LICENSE /
  `.venv` / term file skipped.
- **`scripts/generic_lint_terms.yaml`**: regrouped — `project_names` (every project, board and case name the skill was learned on, and the
  phrase that stood for them), `part_names` (one project's part labels and body ids), `project_ids` (board md5s, order / account ids),
  `people_names`, `machine_paths`, plus the existing parts / refdes, record-id, review-id, preset and dimension groups.
- `CHANGELOG.md`: history kept, names removed — the three projects are "a hand-crank engine model project (mech scope)", "a desk-walker project
  (mech scope)" and "a board-and-enclosure project (both scope)"; part names became their kind; decision, order and account ids removed.
- `docs/reviews/*.md`, `docs/superpowers/*`: project nouns scrubbed the same way (the layout spec's example set and kit names are neutral;
  scratch paths read `$SCRATCH`).
- SKILL §13, README, `skill_retro.py` docstring: the retro report in `docs/retro/` is working material — fold it, then delete it.

### Removed
- `docs/retro/` — `INDEX.md` and the six per-project retro reports (three board-and-enclosure retros of 2026-09-28 … 2026-09-30 plus its 0.7.1
  retro, one engine-model retro of 2026-09-30, one desk-walker retro of 2026-10-01). Their learnings are already in the references; git history
  keeps the files.

### Not done
- The lints stay word lists: a new project's names enter `generic_lint_terms.yaml` at its retro, before the fold.

## 0.11.2 — 2026-10-04 — the assembly model is gated, not looked at: every placement det +1, a fit row per mating pair, an orientation row per one-sided part; mirror bodies are a parts-list decision; parts named by their marks

Source: a desk-walker project's first article (mech scope, home FDM), its `LEARNINGS_LOG.md` entries of 2026-10-03 and 2026-10-04 and three of
its decision rows. The owner, assembling from the 3D guide, held a printed lower triangle against the guide's view: "the L piece
seems to be mirrored … either the print is wrong or the guide is". The print was right. The assembly model's flat-part placement for the +y
side (`print XY → machine XZ, print +z outward`) had determinant −1 — a mirror — and so had the standing-part placement for that side: 28 of
the machine's placements (14 flat + 14 standing) drew a right side no plate can print, in every render and the walking GIF for three days.
Written after the fact, a pin-to-socket check failed 12 of 12 D ends (each 180° from its web socket) and reversed the hands of the two
chiral twisted pins, which had been chosen by eye from the mirrored drawing. The day before, the foot had sat sole-up with its slot toward
the desk in every render. Cost: four plates and six triangles reprinted. The owner's question — *why were these issues not identified
before?* — has four answers, each now a rule:
1. The model was only ever LOOKED AT (renders, GIF), never checked for being physically realisable; the per-side 2D sweeps run in the part
   plane where a mirror is a no-op, and a mirrored flat part looks plausible → every placement is a proper rotation, one CHECKS row, FAIL.
2. Nothing compared a MATING FEATURE to its counterpart in 3D → a FIT row per mating pair through the real transforms.
3. Print orientation ≠ assembled orientation and the transform is the only record of the turn → an ORIENTATION row per one-sided part type.
4. The parts list never asked whether a flat part with a one-sided feature serves BOTH sides of a symmetric machine → the parts-list decision
   (turn over / mirror body with its own mark / separate pin) before the first plate, asked at kickoff.

### Added
- **`case-pipeline.md` §Assembly model** (before §Stability): (1) every placement det +1 — a CHECKS row, FAIL, with the five-line inline form and
  why the mirror is invisible downstream; (2) a FIT row per mating pair (D shaft ↔ D socket ≤ 1°, peg ↔ hole, tab ↔ slot) computed through
  the placements from the geometry of record, with a generic `fit_rows(pairs)` — a pair = (feature direction, placement) vs (mate direction,
  placement) → angle ≤ tolerance (the project's own fit-row helper abstracted; the walker appears only in one labelled worked example per section);
  (3) an ORIENTATION row per part type with a one-sided feature (slot opening, peg direction, sole normal → its mate or the ground); (4) renders
  and GIFs are previews, rows 1–3 are the evidence. The interference bullet points at it (a per-side sweep in the part plane cannot see a mirror
  or a D turned in its socket).
- **`scripts/stability.py improper_placements([(label, M)])`** → `[(label, det)]` for every placement that is a mirror (det < 0) or not rigid
  (|det| ≠ 1); the JSON CLI fails on one; selftest: a flat part laid print +z → +y flagged at det −1, the same part turned over passes, a 90°
  turn passes, a scale is flagged. The module already weighs the CoG through these transforms, so the det row lives beside it.
- **`dfm-printed-enclosure.md` §1.5 "One-sided parts on BOTH sides of a symmetric assembly"**: a decision-row TABLE (part type | one-sided
  feature | serves both sides? | turn-over / mirror body / separate pin | mark for the mirror body) filled before the first plate; a mirror body
  carries its own distinct mark, and marks on narrow members stay short (two glyphs side by side on a 4 mm member read as a tapering land to the
  census — the project used one glyph twice side by side). Kickoff **C1–C2 owner input** asks it.
- **`print-kit.md` §1**: parts are named by the mark pressed into them, never by the generator's body id; every display name derives from the
  marks table in one place; a mirror body is listed under its own mark; a bare body id in owner text is a kit-text-gate hit (the project's kinked
  bar had one letter in the yaml and carried another as its mark — "bar I (k, …)" read as a mix-up; the reference states the rule without the letters).
- **SKILL §8 "Assembly model"** bullet (the three rows, the mirror-body decision, renders are not evidence).
- `pitfalls.md`: four 2026-10-04 rows (mirror transform, unchecked mating features, print-vs-assembled orientation, one-sided parts on both
  sides), each with its detection rule, phrased for any mechanism (the project nouns stay in this entry).
- `smoke/run_smoke.sh` §0: greps for the assembly-model rows, §1.5, the mark-naming rule and the SKILL bullet.

### Not done
- No generic script computes fit or orientation rows: the mating pairs and one-sided features are the project's (its segment lists, its
  outlines), so the rows live in the project generator as the reference's worked example shows; `improper_placements` is the one rule general
  enough for the skill.
- No yaml key for the mirror-body decision; it is a decision row (the kit lists hands as plates), as the reference says.

## 0.11.1 — 2026-10-02 — a desk-walker project's first-article plates 1 / 1b folded: raised legends gate air gaps at 0.9 (the 0.9.2 "lands ≥ 0.45" withdrawn), the gap metric is an opening of the complement, coupons bracket the KNOB, filament slots keyed by role, a measured hole-shrink row

Source: a desk-walker project's `LEARNINGS_LOG.md` entries of 2026-10-02 and three of its decision rows (mech scope, a desktop FDM printer,
0.4 nozzle, 0.20 mm, PLA Basic, 4 walls; two coupon plates printed and read by the owner). The gap metric ships as the required shapely test with
its three fixtures (the skill has no legend script; the legend gates live in the project generator). One script change so that ONE part can carry
both kinds of legend under the new numbers — a legend box may carry its OWN limits: `print_dfm.py` `(x0, y0, z0, x1, y1, z1, land_min, void_min)`,
`thin_wall_census.py` `[x0, y0, x1, y1, gate]`; boxes without them take the row's `legend_land_min` / `legend_void_min` (now the raised 0.9 / 0.9)
or `--box-min`, so a coupon's always-debossed labels (0.45 / 0.45) sit beside a raised colour word on one STL. Records of plain boxes are
byte-identical to 0.11.0 (selftests in both scripts).

### Changed
- **`dfm-printed-enclosure.md` §8 "Legends RAISED"**: cap ≥ 5.1 / stroke ≥ 0.9 / **air gap between strokes ≥ 0.9** (two 0.42 perimeters + margin;
  a Latin capital is three strokes and two gaps; a closed "4" needs 5.6). The printer closed every 0.5–0.6 mm gap of the cap-4 bold letters (E / B /
  S / 8) the 0.9.2 rule allowed. Font by measurement at the cap (Avenir Next Demi Bold the only pass of 24 system fonts at cap 5.2 / pad 0.08; DIN
  Alternate Bold / Helvetica / Arial / Verdana bold fail on gaps); pad ≤ 0.1 — it trades stroke for gap one-to-one. The same numbers in the
  "small cap" bullet, the coupon self-documenting bullet (raised: cap ≥ 5.1 / stroke ≥ 0.9 / gap ≥ 0.9; debossed unchanged), `case-pipeline.md`,
  SKILL §8 item 5, and `templates/20-design/dfm_processes.yaml` `legend_land_min` 0.45 → 0.9 and `legend_void_min` 0.4 → 0.9 on both home rows
  (the raised numbers; a debossed label's box carries 0.45 / 0.45 itself) / `templates/project.yaml` colour-body `void_gate` 0.45 → 0.9.
- **The gap METRIC** (new bullet): a closing of the glyph (`buffer(h).buffer(-h) − glyph`) saturates at ~0.45 because every concave corner reads as
  a gap above that — it could never enforce a stricter gate and silently passed the labels that printed closed. Required test: the complement's
  thin regions under an opening by g/2 (`C − C.buffer(−g/2).buffer(g/2 + 0.02)`), parts with area > 0.5 g² (corner slivers are ~0.2 g²); the
  pad around the complement scales with g. Fixtures stated: an E at cap 4 bold FAILs at 0.9, a 1.2 mm slot passes, a bare concave corner counts
  0 (run at the merge with shapely 2.1.2 on synthetic polygons: 2 / 0 (1 at g = 1.3) / 0).
- **Second-order legend rows**: the legend body inside the LENGTH of its surface (a rail word at 3/4 of the rail would have run off the end as the
  cap grew); label pitch derived from the measured label width (pitch 19 nearly touched at cap 5.2 — 20 mm labels need ≥ 23).
- **Coupons bracket the KNOB, not the mating feature** (§8 new bullet, §8.5, `print-kit.md` §4, SKILL §8 item 5): three variants OF THE PART THAT
  CARRIES THE KNOB (three caps with three holes, three sliders with three slots) on ONE production-size mating feature; press / push brackets centred
  on zero nominal clearance until hole shrink is measured; variants too small for text marked by SIZE (outer Ø 9 / 10 / 11, ski 28 / 31 / 34).
  Plate 1 varied the pegs and tabs for one production hole / slot, both production values were outside the bracket and the plate said "none".
- **Hole shrink, measured** (§8 "Hole shrink", dated, printer named): Ø5 hole +0.3 free pivot; D6 socket +0.2 snug / +0.3 falls out; 3 mm plate
  in a slot +0.1 snug lap / +0.0 push-fit stays / +0.3 falls off; Ø5 press cap hole +0.0 by thumb and holds, −0.15 would not go on.
- **Filament slots keyed by ROLE** (§8.3, `case-pipeline.md`, `print-kit.md` §1 header, kickoff C5 owner inputs): structure / kinematics / accent /
  legend with colour name + hex as values; a palette change is a yaml-only edit (two palette changes touched 11 files while colour names were the
  keys). Roles matched to SPOOL SIZE (structure ~60 % of the grams = a full spool; accent ~5 % fits a small one); the kickoff colour question asks
  which spools are full and which are small.
- `pitfalls.md`: five 2026-10-02 rows (gap rule, saturating metric, bracket-the-knob, role-keyed filaments, second-order legend rows); the
  2026-10-01 "counters ≥ 0.45" row marked superseded.

## 0.11.0 — 2026-10-02 — the navigable layout is the default: a numbered lifecycle tree, revision-named folders, the five answer pages of `00-now/`, the kit of record, the case set shape

Spec: `docs/superpowers/specs/2026-10-02-navigable-layout-design.md`; plan: `docs/superpowers/plans/2026-10-02-navigable-layout-skill.md`
(owner: "a better organization of the output from the skill that is intuitive to navigate … without a README").

### Added
- **`scripts/now_pages.py`**: `00-now/WHERE_THINGS_STAND.md`, `BLOCKED_ON_OWNER.md`, `WHAT_TO_PRINT.md`, `WHAT_TO_ORDER.md`,
  `WHAT_TO_CHECK_ON_ARRIVAL.md` — each the answer to its own name, derived from the gates, decisions, status log, blockers, the arrival yaml, the
  procurement table and the kit plate sidecars; `--check` fails the gates when a page is stale (template `gates.adopt`, smoke step 5e, the record
  chain in `release-and-cut.md` §3.1, eval 18). Scope-aware: an ee project's print page says so; an empty project says "nothing" on every page.
- **`project.revision`** (`Project.rev()`, default `rev0`) names the fab package (`30-board/fab/<rev>/`), the cut (`70-release/<rev>/`),
  collateral and marketing folders; the record hash stays inside each (`board_id.txt`, `RENDERS.md`, `MANIFEST`); packages are still selected by
  the md5 in `board_id.txt`, never by a folder name or an mtime.
- **The kit of record** (`references/print-kit.md` §1): `50-kits/<kit>/` per print target with `START_HERE.md` at the root, `plates/` (+ `.3mf.json`
  sidecars with `print_time_s`, `filament_g`, `objects`, optional `filament_changes`, `proves`, `order`), `parts/`, `sheets/`; mirrored
  byte-identical to `~/Downloads/<project>_kits/<kit>/`; superseded kit folders reduced to a one-line `SUPERSEDED.md`.
- **The case set shape** (`references/case-pipeline.md` Chain): `40-case/<set>/` per print target with `parts/` (STL of record), `checks/` (the only
  place the census / print-DFM / interference gates look), `pictures/`, `build/` (gitignored, `templates/.gitignore`).
- `templates/project.yaml`: the commented `paths:` block listing every default; `templates/CLAUDE.md`: the tree as the project's map.

### Changed
- `scripts/project.py` `DEFAULTS["paths"]`: every default under the numbered tree (`decisions: 90-log/DECISIONS.md`, `mech_record:
  40-case/*/parts/*.stl`, `kits_dir: 50-kits`, `reports_dir: 70-release/reports`, …); an explicit key still wins unchanged.
- Every path SKILL.md, README, the references, the templates, the scripts' fixtures, the smoke and the evals spell is the new tree (the sweep
  table is in the plan, Task 3); the templates folder mirrors it (`templates/10-spec/`, `20-design/`, `60-orders/`, `90-log/`); the design
  reports are written to `reports_dir`.
- `scripts/reorg_paths.py`: whole-directory moves with frozen content, `--map` for sub-paths; the `reorg:` reference carries the migration from
  a `docs/`-style layout to this tree as its worked example.

### Review round (double-blind, before the merge — `docs/reviews/blind_review_0.11.0_{A,B,C,verified}.md`)
Three blind reviewers on two model families and three setups (an Agent-tool reviewer without the mesh libraries, one with them, and the GitHub
Copilot CLI on gpt-5.4) got the committed tree and a checklist only; a verifier with the spec, the plan and the tree classified the 61 finding
ids into 39 rows (20 CONFIRMED, 10 PARTLY, 4 ALREADY DECIDED, 5 REFUTED). All five reviewers' agreements were real: the smoke assumed a git
checkout; `iteration_gate.sh --selftest` found no yaml-capable Python; the README copy-and-scaffold path was broken (lost scaffold line, dead
`design/` glob, the arrival yaml copied on day 1); pre-layout `design/` / `out/` literals survived the sweep in templates and references (plus
a container image and two domain tags rewritten as paths); and a fresh project was not green on day 1 — the template's two order cells shipped
prose that both parsers read as an approval. Fixed: GATES cells `_not yet approved_`; README step 4 scoped by `A0` and ending with scaffold +
slots; SKILL §0 step 6 runs `now_pages.py`; one records spelling `40-case/<set>/{parts,checks/census,checks/dfm}` everywhere and the gates
locate `parts/` from `checks/`; set and kit folders are named by the `print_targets` key (non-target sets pass `--target`); `gates-required`
demands a gate line per set; `SPEC_ERRATA` has one home; `ARRIVAL_CHECKLIST_<rev>`; cut deliverables per scope; `project.revision` validated;
new `paths:` keys for the DFM mirror files and the kit mirror; `tools.geometry_cli`; plate sidecars carry `stl_md5s` + `case_version` and
broken plates are listed as such; the smoke runs on a non-git copy, fails on a `SyntaxWarning`, and greps for the old roots; `stability.py`
exits 2 without the mesh libraries. Acceptance: fresh `ee`, `mech` and `both` projects from the README block are green on day 1 (adopt + clone
gates, five pages present, no gate approved).

### Not done
- Existing projects are migrated by their own `reorg:` block (two phases: documents / kits / release / now-pages, then the `out/` split); this
  release changes no record's content, md5 or rule-set version.

## 0.10.7 — 2026-10-02 — the inner-tier runner only; standard / release are the existing adopt-gates commands

### Changed
- `scripts/iteration_gate.sh` drops `--tier`: it is the INNER tier (`scripts/iteration_gate.sh [-- <command> ...]`, the standing set in
  `gates.iteration.inner` plus this change's commands, read-only guarded, empty refused). The `--tier standard` / `--tier release` aliases of
  0.10.6 added no capability over `scripts/adopt_gates.sh --no-clone` (`make gates`) and `scripts/adopt_gates.sh` (`make check`) and are gone
  (owner: "do we even need that alias?" — no). README, SKILL §2, `project-yaml.md`, the template, `agent-ops.md` §8 item 9 and the Makefile
  target comments name the three tiers as three existing commands.

## 0.10.6 — 2026-10-02 — explicit fast validation tiers

### Added
- `scripts/iteration_gate.sh`: one entry point for the three validation tiers. **inner** runs the changed generator's `--check` and its
  direct grader — the project's standing set in `gates.iteration.inner` plus this change's commands after `--` — under the adopt gates'
  read-only guard (status + tracked-diff hash before and after), through the host pool when the project has one; an empty set is refused,
  so an unconfigured fast path cannot report success. **standard** and **release** are aliases of `scripts/adopt_gates.sh --no-clone` and
  `scripts/adopt_gates.sh` (= `make gates` / `make check`): the `gates.adopt` list is the one list of record, no second yaml list to drift
  (the PR's `standard:` / `release:` yaml lists were folded into these aliases in review). Template and reference carry `gates.iteration.inner`;
  SKILL §2, README "Fast, safe iterations", `agent-ops.md` §8 item 9 point at it.

### Not done
- Tier selection is explicit rather than inferred from a diff: the agent names the generator and grader a bounded change affects, on the
  command line or in the project's standing inner set.

## 0.10.5 — 2026-10-02 — execute every tool selftest in smoke

### Changed
- `smoke/run_smoke.sh` executes every script's `--selftest` (21 scripts, Python and shell), rather than only verifying that the flag is
  declared and running eight of them; `print_dfm.py` / `stability.py` run when the mesh libraries are present (the census selftest carries its
  own pure-core path without them). The two explicit selftest lines the loop made redundant are gone.

### Fixed
- Eval 17's second check ran `stability.py --selftest` unconditionally and failed the no-mesh smoke path (the check is `needs-mesh:` now, as the
  runner's skip rule requires).

### Not done
- The smoke fixture still skips mesh-dependent execution when its optional mesh stack is
  unavailable; the full documented environment runs those selftests.

## 0.10.4 — 2026-10-02 — first-article learnings of two mechanical-only projects (2026-10-01): raised features in the moving-part sweep, operating side vs viewing window, coupon labels in the body's own colour

### Changed
- **`dfm-printed-enclosure.md` §8**: coupon labels are ALWAYS debossed (the self-documenting coupon rule now says debossed, not "debossed or
  raised"), unless the coupon also tests colour — then ONE short raised word in the second colour proves the colour path and the values stay
  debossed (the raised-label coupon plate cost 3.9 g of the second colour and 8 changes for 0.4 g of letters); nothing that moves may sweep a
  raised feature (a crank arm scraped its plate's legends and jammed with 0.5 mm of play to the flat face); the operating side of a display
  mechanism is the side away from the viewing window. **`case-pipeline.md` §Interference**: static raised features (legends, bosses, lugs) are
  bodies in the moving-part sweep, with the axial play added. **Kickoff C4**: a hand-held / stands-on-its-own-face alternative tied to C12, and
  the window-vs-operating-side rule. Three pitfall lines.

## 0.10.3 — 2026-10-01 — static stability as a gate (owner rule: anything that stands, rocks, walks or is set down free carries a CoG-vs-support row at its worst pose); print-DFM rule P ignores tessellation detours (rule set 0.10.3)

### Added
- **`scripts/stability.py`**: centre of gravity of an assembly from the STL set of record (volume centroids through the assembly transforms, a
  density / infill factor per body) and the signed margin of its ground projection against the support polygon (convex hull of the footprints);
  `sweep()` over poses names the worst one; `--selftest`. SKILL §8 bullet, `case-pipeline.md` §Stability, kickoff **C12** "does the piece stand
  free" (→ `kickoff.enclosure.stands_free`, a commented slot in `templates/project.yaml`, a row in `templates/10-spec/KICKOFF_ANSWERS.md`), one pitfall.
  Owner rule: anything that stands, rocks, walks or is set down free carries a CoG-vs-support row at its worst pose; a render cannot show it.
  Found on a desk walker: drive behind the legs, CoG 21 mm behind the hip, −17 mm margin at a third of the crank angles; fixed by moving the drive
  over the feet and the frame forward, then proven by the row.

### Fixed
- **`scripts/print_dfm.py` rule P** read a tessellation detour as a neck: where a section plane crosses a plate's bottom edge at a slant, the ring
  carries two vertices ~0.02 mm apart two steps along the ring, facing away from each other, and every such plate FLAGged "neck 0.006". The pair
  now also needs the shorter ring path between the two points to exceed 10 × `neck_max` — a neck has material on both sides of it. Selftest: a
  slab turned 7° produces no P finding; the touching-cube and hairline constructs still FLAG.
  The measure changed, so the rule-set `VERSION` is 0.10.3: the gate refuses records of the old rule set and every body is re-recorded
  (`references/print-dfm.md` rule P names the condition).
- **`scripts/stability.py`** (review of PR #2 before merge): the mass centre is `center_mass` (the VOLUME centroid); trimesh's `centroid` is the
  area-weighted average of the triangle centroids and read 8.2 for a body whose volume centroid is 6.0 — an asymmetric selftest body now
  separates the two, and an open mesh is refused (its volume is undefined). Smoke runs the selftest; eval 17 asks the question.

## 0.10.2 — 2026-10-01 — two mechanical-only project retros folded (2026-09-30 and 2026-10-01): census OPP rows honour legend lands, `embreex`, legend geometry, colour-body target, linkage sweeps, arranger facts; `--gate-dir` resolves STLs in its own tree

Sources: two retro reports (since removed from the repo) — a hand-crank engine model project (mech scope; 11 bodies, 3 plates, scope `mech` on 0.8.0 → 0.9.0; 15 learnings,
10 NEW / 5 PARTIAL; two host restarts and three census rounds) and a desk-walker project (mech scope; 36 bodies, 7 plates, three
AMS colours, scope `mech` on 0.9.2; 25 learnings, 14 NEW / 7 PARTIAL / 4 CARRIED — three CARRIED rows folded because the number they carry is new;
three census / print-DFM rounds on the colour bodies and two aborted slices). Opened as PR #1 against 0.9.2 and merged onto 0.10.1 here;
`generic_lint_terms.yaml` lists the project names now.

### Fixed
- **`scripts/thin_wall_census.py --gate-dir`** followed the ABSOLUTE `stl` path stored in a record, so a gate run from another checkout path read
  the other tree's STLs (`git archive` scratch copy): the gate resolves the sibling `stl/<basename>` of the record set first, then a
  project-relative path, and honours a stored absolute path only inside this project's root; new records store the path project-relative.
  Selftest: a record pointing into another tree passes on this tree's STL, fails on the other body's md5, and an absolute path outside the tree
  without a sibling is "not found". Record VERSION unchanged (no rule changed; old records still gate).
- **`scripts/thin_wall_census.py`**: opposing-face rows honour `--boxes` legend lands (`in_box_frac`, gate = `--box-min` inside a land) — a 1.3 mm
  raised stroke is two faces 1.3 apart, not a thin wall; the WALL / VOID rows already did. Selftest case added.

### Changed
- **README / SKILL §0 install**: `embreex` joins the mesh stack — trimesh's rtree ray engine needs > 12 GB for a 15 000 mm² body at 10 samples/mm²
  (it took a 24 GB host down); with Embree the same census runs in 2.7 s at 755 MB. `agent-ops.md` §8 item 1: mesh checks and offscreen renders
  are pool jobs too; item 6: with the fast engine the slots go to the mesh checks and the slicer.
- **`agent-ops.md` §5**: long chains run in the background with an `EXIT` line per job and are waited on by the harness (completion notification
  / monitor primitive), never by a foreground `sleep` loop (current harnesses refuse it; where allowed it is bounded by the per-call timeout).
- **`dfm-printed-enclosure.md` §8**: legend geometry meets the void gate (closing at the gate after placement, inter-letter gap row, letters along
  a curved band anchored by polar angle); a legend at a small cap — `text(size=)` vs cap height (one H per font), font chosen by measured stroke /
  counter, SVG glyph holes by ring coverage, morphology OPEN → CLOSE → neck thickening, gaps filled ~0.05 over the gate (the mesh tools read under
  the polygon), thin-REGION rows instead of an erosion area ratio; **colour bodies as their own print target** (`print_targets.home_fdm_colour`,
  a commented example block in `templates/project.yaml`, → process row `home_fdm_04_colour_body`) with the body's thickness as the wall gate.
  **§8.3**: the arranger nests concave outlines ("gcode path conflicts" → pre-place with `--arrange 0`), a self-placed multi-colour plate hits the
  wipe tower (leave those to the arranger), `result.json` empty for pre-placed plates, `M620` counted against the designed number.
- **`case-pipeline.md`**: Interference — planar linkage levels as a conflict-graph colouring, the 360-step body-PAIR sweep per level with pins /
  pegs / caps as discs; Process rules — the fast engine makes sweeps and animations affordable as previews while the exports of record keep the
  preset's `engine:`; its two watertightness traps (hull of thin slabs, unioned D-shafts) are what the engine rule's watertight row catches.
- **`pitfalls.md`**: 28 lines (legend fonts and glyph geometry, curved-exit feather edges → flat flange blocks, ring-shaped wedge clusters and the
  `band` metric, concave-bore floor margin, hairline junction notches → closing + `simplify(0.02)`, census memory, process-table exhaustion, arc
  anchoring on a concave waist, tip-limited internal gears → running-clearance row, the eccentric-shaft inequality, full-height flank dishes,
  cap height vs `size`, font measurement, erosion ratio, ring coverage, morphology order, under-reading, colour-body gate, the arranger, graph
  colouring, pair sweep, local-vs-machine frame, chirality + ratchet facing, centroid bistability rows, sagitta / kinked slot, Manifold traps,
  absolute paths in gate records).
- `scripts/generic_lint_terms.yaml`: `other_source_projects` (the two projects' names, bar / joint labels, local paths) — 0 hits.

### Not folded
- The twisted-band motor vs spool-and-loop energy budget (a drive choice for one piece, not a skill rule), the Homebrew cask coexistence note
  (install trivia), the project-created / selftests-green bookkeeping line, and the O-rule cantilever bevel (`print-dfm.md` rule O carries it).

## 0.10.1 — 2026-10-01 — a board-and-enclosure project's measured performance round folded (its PERF analysis of 2026-09-30 and decision row, `jobs.sh`, `make record-round`, the perf / tools / cache learnings)

### Changed (corrects 0.10.0's engine rule)
- **Manifold caveat** (`agent-ops.md` §8 item 6, `case-pipeline.md` Presets + Process rules, `pitfalls.md`): the snapshot's Manifold backend is
  measured 100–270 × faster per body and byte-deterministic — the speed claim is [V] with the numbers in the worked example — but on the source
  project's bodies it was NOT rule-equivalent to CGAL (odd edges = not watertight on two bodies in every export format, a membrane, sub-minimum
  regions under print DFM, a 18.6 mm³ spurious intersection, with bbox and volume equal). Rule: Manifold for every PREVIEW / PNG; STL exports OF
  RECORD stay on the engine that passes the chain's own mesh gates (watertight, census, print DFM, interference) — an engine is judged by those
  gates, never by bbox / volume agreement; `engine:` is a per-preset yaml key (`case.presets.<name>.engine`); re-test per OpenSCAD release.
- **Caching policy refined** (§8 item 3, SKILL §11, CLAUDE.md template): previews regenerate every run; expensive geometry of record may be
  cached ONLY on an inputs + engine key with the sidecar md5 as a determinism check (canonicalise the mesh, then record; `--no-cache` forces);
  slicer / PDF / index caches behind `--check`; one locked record round per batch (`make record-round`); regenerating everything once with the
  caches off is the best audit of the records (it found an unseeded census sampler and a non-watertight body the caches had hidden).
- **Measurement method** (§8 item 2 — the rules are in the order applied): measure serially in a detached worktree replica (`nice`,
  `/usr/bin/time -l`), audit redundancy from sidecar diffs per commit (slices on unchanged inputs, byte-identical re-renders, record rounds per
  day), then change one knob per commit and name each gain correctly; a multithreaded tool counts as a whole slot and still exceeds it — the load
  gate, not the slot count, is the control that sees it (item 1). Concurrency budget = `host.jobs_max` writing agents (item 5), no fixed number.
- **Agent-ops block in the project's CLAUDE.md** (`templates/CLAUDE.md` "Agent operations"; §8 item 10): heavy jobs only via the wrapper, at most
  `{{JOBS_POOL}}` writing agents, one record round per batch, the caching + engine policy, one-knob changes inline — the pool and floor are slots
  filled from `scripts/project.py env`.
- `agent-ops.md` carries its one fenced worked example (the measured round: panics at load ~40 from stacked cores-2 pools, chain / plate / round
  timings, 24 of 93 slices and 755 of 1119 kernel runs redundant, the engine test's gate failures, the two latent record defects, the steady state).

### Fixed (the skill shipped one of the pitfalls)
- `scripts/thin_wall_census.py` and `scripts/thin_wall_check.py` seeded only `np.random`; trimesh ≥ 4 ignores it, so every census was one random
  draw. The sampler takes `seed=` now and the census selftest asserts two runs of one STL are byte-identical. <!-- voice: ok -->
- `dfm-printed-enclosure.md` §7.2: gate watertightness AFTER canonicalisation, on the recorded file (a sliver-dropping canonicaliser can open a mesh;
  snap the closest vertex pair first, then drop what collapsed).

### Added
- Six pitfalls lines (Manifold rule-equivalence, the cache key + canonicalise-then-record, regenerate-everything as the records audit, the trimesh
  seed, the sliver canonicaliser, stacked pools + multithreaded tools under a process-count pool, the .3mf UUID churn named as a records fix).

## 0.10.0 — 2026-09-30 — the fifth retro folded, the skill audited and made generic

### Added (retro of the board-and-enclosure project's landing round)
- **Arrival / first-article checklist, generated** (`scripts/arrival_checklist.py`, `templates/20-design/arrival_checklist.yaml`; SKILL §10.1,
  `release-and-cut.md` §10; cut deliverable REC-002; `project.py gates-required` demands the `--check` line once the yaml exists): before shipment
  (the fab's photos), bench checks in gate order with what each row opens, software gates with their closing commit, case first article, owner
  decisions still OPEN with their trigger; status grammar + evidence enforced; smoke step 5d, eval 15.
- **SPEC errata** (`templates/10-spec/SPEC_ERRATA.md`, `release-and-cut.md` §11): a frozen spec's deviations as OPEN E-rows, never an edit; the
  hand-off's §3.3 and the arrival checklist §E carry them.
- **`[K owner-read]`** tag (SKILL §4, `part-verification.md`, CLAUDE.md rule 1).
- **Review protocol with a record-reading verifier** (SKILL §5, `agent-ops.md` §4, `blind-deep-review.js`): reviewers of a second model family get
  artefacts + checklist only; one verifier with record access classifies CONFIRMED / ALREADY DECIDED / REFUTED / PARTLY / UNVERIFIABLE with a
  `rev_impact` column; every finding is verified; nothing is applied without the verifier's row; a CONFIRMED bench item becomes a checklist row.
- Kickoff **C10** `fit_result` landing key (an owner-picks-after-a-print answer has a home) and **C11** slicer optimisation target.
- **`references/fdm-print-optimisation.md`** (owner addition): waste / strength / quality knobs, each with what it buys, costs, when it applies, how
  it is PROVEN from the g-code / sidecar, and the slicer keys; default knob sets per C11 answer; flush-into-infill only where the change sits above
  the first infill layer. Sources fetched (Bambu wiki, Prusa KB) tagged [V] / [K]. Linked from SKILL §8, `print-kit.md` §4.1, the enclosure
  reference §8. Eval 16.
- **`print_dfm.py` rule B**: an open-ended ceiling's span by rays from the inscribed-circle centre (bounded all round → inscribed circle; one axis
  with both ends on material → that chord; never a bbox extent or a raster run); constructs: pi 32 FLAG / pi 6 silent / tunnel 2 + 15 /
  lands-split rebate ~6 / relief ring + open groove 1.4 / debossed word letters separate. Rule-set VERSION 0.10.0.
- **Resource budget** (owner addition; `agent-ops.md` §8, `scripts/jobs.sh`, `templates/ci/Makefile`, `project.py env`, ENV host row): one heavy-job
  pool per machine sized from the host (cores // 4, memory floor max(2 GB, 15 % RAM), nice, load gate, wall + RSS logged), caching policy
  (regenerate geometry, cache only slicer / PDF / index steps with a `--check`), serialized record round, Manifold backend (`--backend=Manifold` [V]),
  previews not renders for pictures, inline edits for one-value tweaks.
- 18 pitfalls lines (generalised by hand); the two project-named process rows of the retro were not carried (the template's `home_fdm_04` rows
  are the generic equivalents).

### Changed (audit — `80-reviews/AUDIT_0.10.0.md`)
- **One home per rule**: SKILL §8.1 items 1 / 4 / 5 trimmed to commands + pointers; `vendor-review.md` §3 / §4, `fab-dfm.md` §4 / §6 and
  `case-pipeline.md` §Census shortened to pointers at their homes.
- **Present tense, no history in rules**: `scripts/doc_voice_lint.py` (changelog voice + version numbers in prose; 47 hits → 0) runs in the smoke;
  README carries one version line and no counts.
- **Generic, not one project**: `scripts/generic_lint.py` + `scripts/generic_lint_terms.yaml` (project names, parts, record ids as citations, owner /
  machine, preset names, this design's dimensions; one fenced worked-example block per file; 181 hits → 0) runs in the smoke; pitfalls.md's evidence
  pointers replaced by dates; the enclosure reference keeps one worked-example block (§7.1).
- Stale mentions fixed: `print_dfm.py --gate` beside the census line in CENSUS_GATE_ROWS, GATES M1 / Case order, RELEASE_NOTES, DFM_ROUND, the
  `case_dfm` verifier; ERC wording in G1/EVIDENCE; `tools.slicer` key; the fab's grade names ("Danger / Warning") no longer the vocabulary; CAD-neutral
  CI image placeholder (`{{PROJECT_CAD_IMAGE}}`) and ENV row; `{{GEOMETRY_CLI_PATH}}` in every mech file; `doc_id_prefix: {{PROJECT}}`; the smoke's
  record path without `<board>/`; workflow README lists every `{{BRIEF_*}}` and the shared wrapper / blindness paragraphs; `{{SILK_METRICS}}`.
- Scripts: `Project.find` exits 2 (ten scripts at once), every usage / missing-input path exits 2, `print_dfm --processes PATH` that does not
  exist is an error, `handoff_header` takes one package, `collect_renders` has a description, the shell gates answer `-h` and refuse unknown flags,
  `run_evals.py --selftest` + absolute `--python`, `release_report` reads `fab_dfm.report`, `scratch_links` default `[]`, defaults in `DEFAULTS`,
  `thin_wall_check` imports its core from `thin_wall_census`, `skill_retro` uses `project.split_row`, dead imports / no-op lines removed.
- Evals 2 / 3 / 4 / 5 / 7 / 10 gained mechanical checks (16 of 16 carry them); eval 8's batch count corrected.

### Not done
- No shared `_common.py`: the duplicated helpers net under 100 lines once written; `decision_status` moved into `project.py`, the rest stays.
- `print_dfm.py`'s selftest keeps naming template rows (a data table under test by design).
- The two lints are word lists, not grammars: a sentence can narrate history without a listed word; the blind review reads for that.

## 0.9.2 — 2026-09-30 — self-documenting coupons

### Added
- Owner rule: every test coupon and bracket variant carries its identifier and the value it tests as printed text on the part (ironed top face or
  face-up plate, legibility thresholds FAIL-gated, generated from the same yaml value) — `references/dfm-printed-enclosure.md` coupon block,
  `references/print-kit.md` §4, one pitfall line.

## 0.9.1 — 2026-09-30 — print DFM rule set mirrored from a board-and-enclosure project (its M-B blind review + two decision rows; `scripts/print_dfm.py` VERSION 0.9.1)

That project's `gen/print_dfm.py` (rule set 2026-09-30f) was revised in parallel with 0.9.0 after a blind review tested the tool against
constructs its author never built (a plate, a pin, a 50° ridge, a tunnel, a sealed void, two touching cubes) and found a dead measurement behind
a green gate. Every rule change below is physics, not vendor tuning; 0.9.0's enforcement (record signature, `--open` only against an OPEN
decision row naming the piece, STL-set and `print_targets.<t>.dfm_process` checks, `fix:` on every FLAG row, project-root paths, the cantilever test) is kept.

### Mirrored (`scripts/print_dfm.py`)
- Ray origin nudged INTO the material — already fixed in 0.9.0 (blind review F1 = the project's own decision row); verified, now asserted finite and near 0.8 on the 0.8 plate with R SILENT.
- Knife-edge field `COS_K` 0.05 (any face that faces back) + rule K by the tip band `feature_min / (2 tan(a/2))` > `KNIFE_BAND × feature_min` (included angle < 53°) over ≥ `slender × feature_min`: ridges 30 / 40 / 50° FLAG, 60 / 90° read but pass; the former 45° cone cut-off is gone.
- Sliver exemption needs the aspect test: area < `sliver_area` AND extent ≤ 2 × thickness; a Ø0.4 × 3.5 or Ø0.3 × 2.9 pin is rule F, a Ø1.2 pin passes.
- 3-D legend boxes `(x0, y0, z0, x1, y1, z1)` in the print frame: `--boxes file.json`, the `<piece>.boxes.json` sidecar written / removed beside the record, `--land` kept as the every-Z spelling; W and R respect the boxes like every other rule; non-manifold edges and point contacts inside boxes listed in row L.
- No run time inside the record (`_seconds` printed, not written, not signed): a CLI rerun reproduces the gated record byte for byte (asserted).
- Process fields `media` (powder / resin / none), `layer` + `skin_min_layers` -> rule **Z** (a horizontal skin is a layer count: 0.6 flat = 3 layers PASS, 0.4 -> Z, 0.6 stood up -> W); FDM `void_min: null` = no long-slot rule, with the rule stated in the row and the yaml.
- Bridge span = the shortest crossing between SUPPORTED edges (inscribed circle of a footprint bounded all round, the supported axis of one open at the ends): a 2 × 40 tunnel roof bridges 2 mm, a 15 mm tunnel FLAGs B with `supports: none`, a 32 mm pi roof open at the ends is a 32 mm bridge (not 10); steep overhangs judged by reach ≤ `bridge_max` (a 2 mm slot top is bridged, a 24 mm one FLAGs O); `--supports none|interior|any` per body overrides the row; 0.9.0's cantilever (< 2 supported ends) kept under O.
- Rule **C** sealed cavity: FLAG on powder / resin (escape hole ≥ 3.5 mm [V Hubs]), INFO on FDM.
- Rule **M** merged with 0.9.0's: non-manifold / open edges located (in-box exempt), inconsistent winding, solid count vs `--bodies` (cavities not counted as bodies); two cubes touching at a vertex (2 solids) or along an edge (a 4-face edge) FLAG, `--bodies 2` passes the vertex case.
- Gate: `--expect <tag>/<piece>=<reason>` for bodies that FLAG by design (coupons, dummies), printed on every run; record-only dirs (no sibling `census/`) checked the same way; `*.boxes.json` skipped; a stale `--open` / `--expect` entry noted; the 0.9.0 signature / version / threshold / process-row checks kept.
- `--validate` groups the labelled files by GEOMETRY (faces equal, volume 0.05 mm³, area 0.5 mm², bbox 0.01) and counts agreement on unique geometries; §3a coverage per mechanism, §3b thresholds with their `[V]` / `[K]` tags + the tool's judgment constants; exit 1 on any LOOSER geometry (kept).
- Selftest: a positive AND a negative construct per rule (plate / rib / root / pins / ridges / sheets / slot / tunnels / tee / pi / pitched roofs / cavity / touching cubes / gate incl. `--expect` and the sidecar / validate incl. twin grouping); 45 s.
- `--list` shows `media` and `layer × skin_min_layers`; `[K]` "slenderness heuristic" replaces the Kirchhoff citation (the L/t ≥ 10 of plate theory is a validity condition, not a manufacturability number).

### Templates / references
- `templates/20-design/dfm_processes.yaml`: `media` on every row, `layer` / `skin_min_layers` / `void_min: null` on the FDM rows with the rule stated, `home_fdm_04_colour_body` (skin_min_layers 1, supports none), header fields for media / layer / skin / boxes / supports-per-body, sliver aspect test and slenderness heuristic in the comments.
- `references/print-dfm.md`: rules table (M C W R Z F K P V H O B S + L Y), legend-box sidecar, `--expect`, the geometry grouping and coverage reading; `references/pitfalls.md` +3 (negative selftest case, sliver aspect test, validation deduped by geometry).

### Not done
- The project's record paths (`out/<board>/...`) and its 42-file validation set stay in the project; the skill ships the schema and the selftest constructs.
- `thin_wall_census.py` VERSION stays 0.9.0 (no census rule changed).

## 0.9.0 — 2026-09-30 — gates enforced by scripts, every documented command runs as written (closes blind review S of 0.8.0)

Blind review S (`80-reviews/OPUS_blind_review_S_skill_0.8.0_2026-09-30.md`, Opus, cold personas: EE user, mech user with a bracket STEP, sceptical
manager, skill maintainer): 28 findings, every one reproduced with a command. Owner's bar for the release: gates enforced by scripts not prose, "no
waivers" true in code, a cold user runs README + SKILL.md as written. Every finding re-run before and after the fix (`smoke/run_smoke.sh` section 0e
and 0d carry the negative cases as permanent checks).

### Per-finding disposition

| # | Sev | Finding (short) | Disposition |
|---|---|---|---|
| F1 | MAJOR | README Quick start smoke fails without a skill venv; SKILL says pyyaml-only venv | FIXED — ONE venv (the project's, mesh libs included); the smoke falls back to the caller's `.venv`, skips the mesh section with a NOTE when the libs are absent |
| F2 | MAJOR | `scripts/project.py scaffold` fails on a stock python3 (`import yaml`) | FIXED — lazy import; the smoke runs scaffold with `python3` |
| F3 | MAJOR | five scripts not executable | FIXED — all 100755; smoke asserts mode, shebang and `--selftest` on every `scripts/*` |
| F4 | MAJOR | `skill_retro.py` default `--skill` resolves through the symlink to the project | FIXED — `realpath(__file__)` in every script (smoke greps `abspath(__file__)`); retro selftest runs through a symlinked `scripts/` |
| F5 | MAJOR | census / print-DFM gates check the records that exist, not the STL set; a deleted acceptance keeps passing | FIXED — both gates glob the sibling `stl/` + `paths.mech_record` under the tag and FAIL on a body without a same-md5 record; the census gate re-matches `accepted_fails` against the live `print_targets.<t>.accepted` |
| F6 | MAJOR | `dfm_process` read by no script; record version / thresholds not compared | FIXED — `--gate` requires `record.process == print_targets.<t>.dfm_process`, `record.version == VERSION`, `record.thresholds ==` the current row |
| F7 | MAJOR | `--open <tag>/<piece>=<anything>` accepted | FIXED — the id must be an OPEN row of `paths.decisions` (topic printed); any other string, an APPLIED row, or no decision log = exit 1 |
| F8 | MAJOR | non-watertight and multi-body meshes PASS | FIXED — rule **M** (watertight, consistent winding, body count = `--bodies N`, default 1); selftest: open box, two plates |
| F9 | MAJOR | CI recipe writes into the submodule; workflows never init it; three scripts missing | FIXED — project-owned `ci/` (`project.env` + copied scripts), `submodules: recursive` on every checkout, `setup_linux.sh` / `nightly.sh` / `release_archive.sh` shipped |
| F10 | MAJOR | kickoff answers have no machine-readable home | FIXED — `kickoff:` mapping + `board:` block in `templates/project.yaml` (every class a slot); `scripts/project.py kickoff --check` fails on an answered row without its key or D row |
| F11 | MAJOR | ERC warnings waived in prose; mesh / DRC gates are opt-in comments | FIXED — `scripts/erc_gate.py` + `design/erc_accept.yaml` (typed entry naming a live decision row; stale entries and GUI exclusions fail; `ERC_WAIVERS.md` removed); `adopt_gates.sh` fails when a schematic / board / STL set exists and its gate line is missing or commented (`project.py gates-required`) |
| F12 | MAJOR | gate cells and the release line unenforceable; regex matched anywhere in the file | FIXED — `scripts/gate_check.py <gate>` reads the cell per row; `--release` = the Release row's cell AND `git blame` author == `project.owner`; `release_report` banner reads the Release cell only; generators of the next phase call it |
| F13 | MAJOR | no route for an existing STEP in mech scope | FIXED — `scripts/step2stl.py` (cadquery / FreeCAD CLI / `--canonical`, canonical STL, provenance sidecar, the OPEN decision row printed); `references/case-pipeline.md` §0; M1 row accepts an imported body under its row |
| F14 | MINOR | the `{{` grep cannot pass right after copying | FIXED — `scripts/project.py slots` replaces the grep; two passes (records now, SPEC / KICKOFF after the spec), 0 before the G0 ask; STATUS skeleton between `<!-- skeleton -->` markers is excluded |
| F15 | MINOR | scope leaks after scaffold (KICKOFF rows, CLAUDE rules 4 / 9, GATES header / bar, MFG-003) | FIXED — tagged per scope; out-of-scope KICKOFF rows are dropped; `evals/run_evals.py` checks evals 11 / 12 on a real scaffold |
| F16 | MINOR | scaffold mangles its own explanatory comment | FIXED — the comment names the tags without spelling them |
| F17 | MINOR | batch 5 has five questions, C10 in no batch, A4 beyond the option limit, "accept all" unspecified | FIXED — twelve batches of ≤ 4, C8a / C9 / C10 / D3 in batch 6, A4 folded to four options, accept-all = first option of the batch's first question; eval 8 checks the table mechanically |
| F18 | MINOR | SKILL §0 step 2 copy block differs from README, misses VERIFY.md | FIXED — SKILL points at the one README block (incl. `design/VERIFY.md`, `design/erc_accept.yaml`) |
| F19 | MINOR | retro ignores `ids.owner_prefix`, drops `* YYYY-MM-DD (domain)` bullets silently, hard-codes ids / paths | FIXED — prefix and `paths.dfm_processes` from project.yaml, `- * +` bullets with `[ ]` / `( )` domains and bold dates, unparsed dated bullets listed in §0 + a stdout WARNING, any id prefix generalised, 30 domain tags |
| F20 | MINOR | every fold is a hand edit | FIXED (bounded) — `--apply`: pitfalls lines, NEW process rows with citations (`validated_on: []`), a CHANGELOG stub, idempotent; PARTIAL / CHANGED / evals / questions stay listed candidates by design |
| F21 | MINOR | missing file exits 1, docstring says 2 | FIXED |
| F22 | MINOR | no `mech` role set in the review workflow | FIXED — `ROLE_SET = 'mech'` (case_dfm, mechanical intent, hardware, gates) |
| F23 | MINOR | §1.2 before §1.1; "the owner writes D rows" contradicts §0.1 | FIXED — reordered; "the agent transcribes the owner's words into D rows, quoted" |
| F24 | NOTE | 119 / 122 / 151 hand-filled slots | ACCEPTED, made visible — `scripts/project.py slots` lists them per file and exits 1 while any remain; the smoke proves a trivially filled project reads 0 (the kickoff / board slots added for F10 raise the raw count: every answer now has a key) |
| F25 | NOTE | cantilevers reported as bridges | FIXED — a ceiling with < 2 supported ends (horizontal ray from each end) is a cantilever under O; B keeps two-ended bridges; selftest: T-section 2 cantilevers / 0 bridges, inverted U 1 bridge |
| F26 | NOTE | project residue (openscad default, port_a / port_b, absolute paths in retro reports) | FIXED — mech CLI is a slot, generic `channel_a` / `channel_b`, retro prints basenames; the three shipped reports scrubbed |
| F27 | NOTE | evals not executed | FIXED — `evals/run_evals.py` runs `checks:` (8 evals carry them), lists 6 as manual |
| F28 | NOTE | pure gates trust the JSON | FIXED — every record carries `sig = sha256(canonical body \| VERSION)`; both gates refuse a record that fails it (tampered FLAG→PASS = FAIL) |

### Blind review of 0.9.0 (`80-reviews/blind_review_0.9.0.md`, one cold EE-user + enforcement-sceptic lens, 10 findings + 6 notes, all reproduced)
Both MAJORs fixed before the tag: SKILL §0 step 6 was written as bare `scripts/<tool>.py` while the shebang is the system python (now `.venv/bin/python …`
everywhere a script reads project.yaml); the RELEASED banner flipped on a release cell an agent had committed (now the banner reads `gate_check.release_ok()`
— cell + git author = owner; the clone gate exports `HWFS_GIT_ROOT` so the archive regen can blame). Also: an unfilled project.yaml says "run `slots`" instead
of a YAML traceback, `scaffold` fills `{{SCOPE}}`, the smoke prefers the caller's `.venv`, `--apply` folds rows whose name line carries a comment, the DRC
token is word-start, `kickoff.answers` is read, `--open` rows must name the piece, no `__pycache__` in the submodule. Dispositions per finding in the review file.

### Added
- `scripts/gate_check.py`, `scripts/erc_gate.py`, `scripts/step2stl.py`, `evals/run_evals.py`, `templates/20-design/erc_accept.yaml`,
  `templates/ci/{setup_linux,nightly,release_archive}.sh`; `scripts/project.py` `slots` / `kickoff --check` / `gates-required` + `record_sig` /
  `verify_sig` / `open_decisions`; `print_dfm.py` rule M + `--bodies` + `--target`; `skill_retro.py --apply`; `blind-deep-review.js` `mech` role
  set; `project.owner`, `paths.schematic`, `paths.erc_accept`, the `kickoff:` mapping and `board:` block in `templates/project.yaml`.
- Smoke: section 0e (enforcement without mesh libs: missing / tampered census record, commented gate line, empty gate cell, uncommitted and
  agent-authored release lines, slots → 0, kickoff --check negative + positive) and the 0d negatives (uncensused body, laxer row, free `--open`,
  tampered record, open mesh, missing file); mode / shebang / selftest / `abspath` / stock-python3 scaffold checks; `run_evals.py` in the smoke.

### Changed
- `print_dfm.py` rule-set `VERSION` 0.9.0 (rule M, O / B split) — every record is re-made; `thin_wall_census.py` records carry `version` + `sig`.
- The release line counts only in the Release row's approval cell (`release_report.py` banner); `templates/90-log/GATES.md` says so.
- `ERC_WAIVERS.md` is gone from templates, paths and docs; `paths.erc_waivers` → `paths.erc_accept`.

### Not done
- `--apply` does not touch PARTIAL sections, CHANGED numbers, evals or questionnaire questions (a human reads the report; deliberate).
- Evals 2, 3, 4, 5, 7, 10 stay manual (they need an agent run against the prompt).
- `print_dfm.py` has no `--target <t>` shortcut for the process row on analysis (the gate reads it; one flag, add when asked).
- `step2stl.py` ships no converter: it calls cadquery or FreeCAD when present and prints the routes otherwise.

## 0.8.0 — 2026-09-30 — print DFM: a vendor-independent manufacturability check for printed bodies, and the loop that improves it

Owner: "since the tool is reusable for future designs, should it go into the skill repo and we leave commands in there to self improve as the
skill is used and new things are identified?" — yes. Source: the fourth retro of a board-and-enclosure project (one of its rounds: 44 bodies, 32 labelled
vendor verdicts, 0 looser / 24 agree / 8 stricter).

### Added
- **`scripts/print_dfm.py`** (project-agnostic; paths default to the nearest `project.yaml`, the process table falls back to the skill template):
  ray + opposing-face tangent-ball thickness (a root under a rim that every ray misses), regions linked at an absolute 2.5 mm, rules W wall / R
  root / F feature / K knife edge / P point contact (section planes) / V void / H hole / O overhang / B bridge / S size + INFO rows L (legend lands,
  slivers) and Y (the vendor's yellow band = the design margin the census owns); per-face MIN heat maps in the vendors' palette (`--render`);
  `--gate` PURE adopt gate (record md5 = STL = census, PASS or `--open <tag>/<piece>=<decision>`); `--validate` against every labelled vendor
  verdict → `PRINT_DFM_VALIDATION.md` (confusion matrix, rules fired, hand-written reading kept) with **a vendor FLAG we PASS printed as `RULE
  DEFECT`, exit 1**; `--list`; `--selftest` (eval 14's pair among its cases). Rule-set `VERSION` keys the validation cache.
- **`templates/20-design/dfm_processes.yaml`**: seven rows (JLC3DP MJF / SLA / FDM, home FDM 0.4, Xometry MJF, Protolabs MJF, HP guide BLOCKED),
  every number `[V]` with URL + date or `[K]` with the source named, `validated_on: []` each. **`templates/docs/quotes/dfm_verdicts.yaml`**: the
  verdict row schema (stl, md5, process, vendor, date, verdict, evidence, note).
- **`scripts/scad_lint.py`**: a statement after a mid-line `//` in generated OpenSCAD is dropped silently (a plate lost its mark webs for two days
  while the yaml and the check row read right) — rejects it, names the identifiers; `--selftest`.
- **The loop as commands** — SKILL.md §8.1 (a) PASS before every upload + `--gate` in the adopt list, (b) every vendor verdict → `dfm_verdicts.yaml`
  → `--validate` → RULE DEFECT = fix the rule from physics, re-validate, `skill_retro.py`; stricter cases listed with their reason, (c) a new vendor
  = one cited row with `validated_on: []`, (d) check rows read the MESH, generated code is linted. **`references/print-dfm.md`** (short): rules
  table, commands with their output and what FAIL means, the loop, the validation on record, adding a vendor in one sitting.
- **`scripts/skill_retro.py` §8**: diffs the project's `design/dfm_processes.yaml` against the template — NEW rows, CHANGED numbers (with the
  citation on the line), VALIDATED rows — as retro items; selftest covers the three kinds.
- Kickoff **C8a** (the process row per print target → `print_targets.<t>.dfm_process`), KICKOFF_ANSWERS row, `templates/project.yaml`
  (`dfm_process`, the two adopt lines), `templates/CLAUDE.md` mech rule 7, `references/project-yaml.md`, `references/dfm-printed-enclosure.md`
  §2 pointer, 8 pitfall lines, eval 14 (0.5 mm root under a 2 mm rim × 90 mm FLAGs W + R under `jlc_mjf_pa12`, the same at 1.3 PASSes), smoke
  step 0d (templates parse, every row `validated_on: []`, both selftests, the eval-14 pair through the CLI, `--list` outside a project).
- README: version, the feature line, the dependency note (`rtree networkx mapbox-earcut` join the mesh set; `matplotlib` optional), the no-project
  quick path for a cold user with a bracket STL.

- **Blind review** (`80-reviews/blind_review_0.8.0_print_dfm.md`, one cold-user lens, 15 findings, 13 fixed, 1 partly, 1 fixed by rule):
  the BLOCKER was a dead measure — the census ray's origin was nudged OUTSIDE the surface, so every ray hit its own face, read inf, and rule R
  fired on every thin wall while the tangent ball kept the verdicts right. Fixed (nudge into the side the ray travels); the selftest now asserts the
  ray reads ~0.8 on a 0.8 plate and that a free 0.6 × 60 rib is W-only. Also from the review: numeric limits and a `fix:` hint on every rule row,
  exit codes 0 / 1 / 2, the no-project README block, Xometry's build volume corrected to the usable 356 × 279 × 330, citation rule for untagged
  repeats. The same ray defect exists in the project's own copy — reported there as an OPEN decision row, not patched silently.

### Changed
- `thin_wall_census.py` stays: `print_dfm.py` does not import it and does not replace it — the census gates the DESIGN margin
  (`print_targets.<t>.wall_gate`, wedge band, bodies, concentricity, retention, clearances), print DFM gates the printability FLOOR; both PURE.
  Its retirement was considered and rejected for that reason (not a deferral).
- The skill venv takes the mesh libraries too (README step 2) so `smoke/run_smoke.sh` can run the print-DFM selftest; `thin_wall_census.py
  --selftest` still needs none.

### Not done
- No `--target <print target>` shortcut reading `print_targets.<t>.dfm_process` from `project.yaml` (one flag; add when two projects want it).
- The project's 32 verdicts and their STLs are not shipped (project data); their reading is `references/print-dfm.md` §4. A probe generator
  for one-knob profiles stays project-side (`rim_profile()` in the selftest is the one shipped shape).
- `--validate` writes only the generated sections; the stricter-case reasons are hand-written under the marker, as in the project of the retro.

## 0.7.1 — 2026-09-30 — the print kit as a deliverable: START_HERE, kit text gate, plate seat datum, bracket plate

Third retro on a board-and-enclosure project (its retro report, since removed: 8 learnings, 3 NEW / 5 PARTIAL, from the two blind reviews of
the home-FDM kit — a technician persona on the kit as received and an FDM DFM persona on the meshes).

### Added
- **`references/print-kit.md`** (new, short): the kit's ONE generated entry point (`START_HERE.md`: print-order table step / project file /
  objects / time + mass / check-before-next, assembly sequence, report-back table with numeric pass criteria and a recipient), every kit text from
  the knobs; the **kit text gate** (`None` / `nan` / `{name}` residue, repo paths, dead file references, tokens of features the preset disables —
  snap tab / screws under magnets, PETG under PLA — = FAIL); hardware lists derived from the fastener knobs; print-sheet names = project-file
  names; the magnet procedure (stack-and-mark polarity, asymmetric boss keying, dry attract check before CA, magnets before glue, feet last);
  coupon → ONE part → plate; watertight row per STL; sidecars carrying and drift-checking every slicer key a rule depends on.
- **`references/dfm-printed-enclosure.md` §8.4** glued plates in rebates on a bed face: the lands are the datum, bridged strips one layer BELOW
  (sag gap 0.2), clearance 0.3 for a glued plate, rebate footprint fixed while the plate shrinks (the rebate lip is a census wall: +0.1/side took
  1.6 to 1.53), thin the plate rather than the roof, working clearance after EF on both parts ≥ 0.1 as a row. **§8.5** snug-fit features: bracket
  plate at three values with named objects and an interference-window row (part ± 0.1, print ± 0.15), the owner picks after one print; a face at
  exactly 45.0° is at the limit — orientation-dependent knob (50° where it is an overhang) + a measured steepest-overhang row per orientation.
- `references/release-and-cut.md` §7: the kit is a deliverable row whose `check` is the text gate + the mirror md5 list; ASSEMBLY / QA prose
  generated from the preset. `references/agent-ops.md` §4 the review pairing that worked (technician on the kit as received + FDM DFM on the
  meshes, parallel, merged, one author in two phases); §5 kernel panics under load → small commits, incremental review reports, one worktree per
  agent. Kickoff **C10** (kit hand-over recipient, who picks the fit knob). SKILL.md §8 step 5 and the Where-to-look row. 11 pitfall lines.
  `evals/evals.json` #13 (print kit entry point and text gate); smoke greps for the new rules.

### Not done
- No generic `kit_text_gate.py` in `scripts/` — the gate is five token classes over a folder and each project's emitter knows its knobs; add it
  when a second project needs the same tokens. No `print_targets.home_fdm.kit` yaml block (recipient + fit decider live in `kickoff.enclosure`).
- No blind review of the skill this version (a one-topic retro); the next full retro reviews 0.6.0 … 0.7.1 with both lenses.

## 0.7.0 — 2026-09-30 — project scope: ee, mech or both

Owner's directive (2026-09-29): "the skill should be able to do ee only, mechanical only or both together."

### Added
- **Kickoff A0 Scope**, asked alone before batch 1 (`references/kickoff-questionnaire.md`): `ee` (PCB / PCBA only), `mech` (enclosure /
  printed / CNC parts only, from a brief or an imported board STEP / envelope), `both` (the previous flow; RECOMMENDED when a board is designed
  and housed). Every question carries its scopes (`[ee, both]` / `[mech, both]` / none); a question outside the scope is not asked and reads
  `n/a (scope)` in KICKOFF_ANSWERS; a batch with nothing applicable is skipped.
- **Phase / gate model per scope** (SKILL.md §1): ee = G0 → G1 → G2 → fab DFM → order → cuts; mech = G0 mechanical spec → **M1** geometry
  approved → **M2** first article / fit print approved → case order → cuts; both unchanged. `templates/90-log/GATES.md` carries the M1 / M2 rows.
- **Scope tags on template lines** (`{{ee,both}}`, `{{mech,both}}`, `{{mech}}`, `{{ee}}`, `{{both}}`) in `templates/project.yaml`, `CLAUDE.md`,
  `GATES.md`, `SPEC.md`, `production_cut.yaml`, `design/traceability.yaml` — one template set, resolved in place by
  **`scripts/project.py scaffold --scope <A0>`**; the existing `grep -rn '{{'` proves the tags are gone.
- **Record id per scope**: `Project.scope()`, `Project.record_md5()` and the CLI verbs `scope` / `record` in `scripts/project.py`;
  `paths.mech_record` (the STL set of record) is the md5 in mech scope. `release_report` identity, `collect_renders` folder and
  `handoff_header` read it; `skill_retro` / `traceability` never assumed a board.
- SKILL.md §0 lists what each scope creates; board-only / case-only sections carry a heading tag (§6, §7, §9 `[ee, both]`; §8, §8.1, the
  `case_dfm` role `[mech, both]`); §8 names the mech fit input (imported STEP / envelope with source md5 + [V] / [K]).
- `evals/evals.json` #11 (a mech-only bracket from a board STEP) and #12 (an ee-only sensor board with no case); smoke: scaffold + gate grep
  for each of the three scopes; `80-reviews/blind_review_0.7.0_scope.md`.

### Not done
- No separate SKILL.md per scope, no scope-aware reader beyond `record_md5` — the templates and the questionnaire carry the branching.
- `both` keeps its gate set (no M1 / M2 rows); the case order row remains its case gate.

## 0.6.1 — 2026-09-29 — fab remark for two readers

### Added
- `references/fab-dfm.md` §5: the order remark has two readers - a plain-words paragraph (functions, not refdes) ahead of the generated technical
  block; pre-empt the customer-service questions (which part a hole belongs to, wave soldering of THT on a two-sided SMT board, the ship-loose
  fallback); file the desk's screenshot links the same day. Source: a PCBA order clarification thread, three mails, 2026-09-29.
- `references/pitfalls.md`: one line.

## 0.6.0 — 2026-09-29 — FDM brand marks (ironed top face / AMS bed layers), dust caps, Bambu CLI facts, one worktree per agent

Second retro on a board-and-enclosure project (its retro report, since removed: 19 learnings, 15 NEW, 5 costly). The owner's directive: "push the
learnings into the hw-from-spec skill as well. ironed surface and bottom ams are both viable options."

### Added
- **`references/dfm-printed-enclosure.md` §8.1 Brand marks / logos on FDM parts** — two first-class options chosen at kickoff: (a) a TOP-face
  feature (deboss or raised 0.6 = 3 layers) under `ironing_type: top` — never `topmost` (it skips recess floors), top shell ≥ recess + 1.0, the
  part oriented so the marked face is a top face; (b) a flush AMS colour body in the bed layers (face on the bed, mark mirrored, 2 layers for a
  dark mark / 3 for a light one, cost = 2 swaps per 2 layers + purge). NEVER a bed-face deboss (bridge-ceiling "webbing"), a vertical-wall deboss
  (stair-steps) or webs / discs that alter the artwork; the glued face-up plate in a keyed rebate (spans > 10 mm split by glue lands) when the mark
  must sit on a bed face without an AMS; one reader orientation for every mark (rotate, never mirror; render vs the artwork). **FAIL-gated mark
  rows** (recess span ≤ 6.0, enclosed island Ø ≥ 2.5, colour region ≥ 0.84, edge ≥ 1.5, whole-layer depth on the mesh, floor ≥ rib gate and
  ≥ top shell, chirality; necks INFO; bbox rows from vertices, not centroids) and the **mark coupon** first on the plate (printer-dependent vs
  geometry-guaranteed, stated in the report).
- **§8.2 Dust caps / protective covers**: no through-hole into the protected cavity (a lanyard hole is a dust path), external support-free tether
  lug, mouth-down print (flange on the bed, chamfer ≤ 45°, ribs start ≥ 1.0, the tip face the only bridge ≤ 10, elephant-foot 0.15 + 0.5 lines),
  pocket radius from the mating part's drawing.
- **§8.3 Bambu Studio CLI facts (02.08.x)**: `sparse_infill_density` 100 % rejected (rc -18) → shell thickness; two-filament + prime tower
  segfaults (rc -11) without `filament_colour` → one filament JSON per slot with its colour; multi-material = ONE multi-part object with per-part
  `extruder` in `Metadata/model_settings.config` (the package pattern documented; the skill ships no slicing helper, the project's writer is the
  worked example); filament per colour + purge per plate (purge derivable for a SOLID part only); N × the same STL = N objects;
  `different_settings_to_system` omits system-default values; ironing ~ +5 min on a small plate.
- **Kickoff questionnaire C9 Brand marks on FDM parts** (RECOMMENDED: ironed top-face feature; alts: AMS colour body, both plates, glued plate;
  never-list) in batch 6 with the bar; `templates/10-spec/KICKOFF_ANSWERS.md` C9 row; `kickoff.enclosure.marks`.
- **`references/agent-ops.md` §2**: one git worktree per parallel agent, commit from a clean HEAD worktree, move `main` with a mixed reset /
  fast-forward; a `--copy` / kit mirror syncs EVERY plate of record, not only the default.
- `references/pitfalls.md`: the 09-29 lines (branding, measurement, dust cap, Bambu CLI, worktrees, date-stamped selftest across midnight,
  `pdftoppm` for drawing-only PDF pages, the pluggable-module-is-not-a-box rule).
- `evals/evals.json` #10: the webbed bed-face logo on an AMS printer (the costly Bambu CLI class).
- `smoke/run_smoke.sh`: greps for §8.1 (`ironing_type: top` — never `topmost`, the AMS option), §8.2 / §8.3 (`filament_colour`, the cavity
  rule) and C9.

### Changed
- `references/dfm-printed-enclosure.md` §8 "Legends RAISED": a face-down face gets a flush colour body, never a deboss (was "debosses or flush
  colour bodies"). SKILL §0.1 / §8 step 5 / Where-to-look name the brand-mark options; README feature line + eval count.

### Not done
- No slicing helper in `scripts/` (the 3MF writer stays a documented pattern: the skill ships mesh gates, not slicer drivers).
- The 72 owner topics the retro listed are project decisions (form factor, part numbers, order lines), not recurring questions — only the
  brand-mark decision recurred (three marks, two rounds) and became C9.
- No blind review of the skill this version (a one-topic retro; the next full retro reviews 0.6.0 with both lenses).

## 0.5.0 — 2026-09-28 — two blind reviews of 0.4.1 fixed, the kickoff questionnaire, the zero-warning bar, PCB build rules, the retro loop

Two blind reviews of 0.4.1 (`80-reviews/blind_review_A_0.4.1_cold_user.md`, 30 findings; `…_B_0.4.1_dfm_expert.md`, 42 findings) found a
pasted gate line that did not parse, two install stories, rules calibrated on one vendor's checker stated as material physics, a "±0.1
tolerance" waiver dressed as a PASS, an untested census with two blind spots, and no PCB build rules at all. The owner asked for three things the
same day: every question up front with recommended answers, a skill that improves with each project, and "0 DFM errors and warnings" as the bar.

### Changed
- **One install block** (README, SKILL §0 step 1): vendor/hw-from-spec + relative `scripts` symlink is the only project layout; a personal clone is
  for discovery; two venvs (skill: pyyaml; project: pyyaml + numpy trimesh scipy shapely); `uv` or `python3 -m venv` (C-02 / C-06 / C-12).
- **"One review round" defined once** (SKILL §1) and used in GATES / CLAUDE / workflows / smoke (C-04); **deciders per phase** table (C-17);
  **the manufacturability bar** as SKILL §1.2 (zero errors / zero warnings / no waivers; board DRC + fab DFM, printed enclosure census + slicer +
  vendor API, CNC) — an owner row from the questionnaire, a prerequisite on G2, the board order and the new **Case order** gate row (B-32).
- **`references/dfm-printed-enclosure.md` rewritten with tags** [checker] / [vendor sheet] / [physics] / [owner bar] / [convention] on every number
  (C-09 / C-10 / B-15 / B-35): snap features, engraved text ≥ the void gate and tangent fillets are ALLOWED options; the 1.2 / 1.3 / 2.0 numbers are
  JLC3DP's checker at ~150 mm plus the owner's no-yellow bar (B-02 / B-03 / B-04); the ±0.1 PASS-by-design row is gone — vendor tolerance from the
  sheet, first-article spread feeds the margin, INFO until then (B-01); the "141 × 0.88 cracked" cause marked as not fractographed (B-07); the
  bbox-resolution hypothesis and its test for the length-dependent metric (B-05); §7.7 → §7.2 canonical STL + geometry signature (C-20 / B-20).
- **`scripts/thin_wall_census.py`**: no gate constant in the script — `--target <name>` reads `project.yaml print_targets` (B-33); wedges gated by the
  width of the sub-gate band; **nearest opposing face in any direction** gated (exact point-to-face distance over KD-tree sample pairs; the ring-root
  / ledge class every normal-ray census missed); samples ∝ surface area; wall-class and wedge-class samples clustered separately (retro); a dated
  `accepted` list with vendor evidence is the only pass (B-31); SANITY row renamed NOISE FLOOR; recall primitives in `--selftest` (0.8 rib and 0.6
  slit must FAIL, a 0.4 rim-ring root must FAIL through the opposing metric, an accepted root passes) (B-12 / B-13 / B-14). Needs scipy.
- **`scripts/dfm_check.py`** reads `fab_dfm:` (`dfm:` still accepted) and `fab_dfm.bar`: an acceptance without every `accepted_requires` field
  (reason, date, evidence) is ignored and listed; `scripts/project.py --help` exits 0 (C-24).
- `templates/CENSUS_GATE_ROWS.md` (`--gate-dir`, C-01; the new rows: wedge band, opposing faces, accepted, geometry signature, retention in the
  mesh, worst-case clearance; INFO rows state why), `templates/DFM_ROUND.md` (raw API JSON, site-changed branch, capability snapshot, bbox / area /
  scale sanity, price, browser / UA, consent line, legend as displayed, material rating, build orientation, bbox-hypothesis probe; B-17 … B-19,
  B-29, B-36 … B-38), `templates/90-log/GATES.md` (round definition, bar, Case order, literal `spec`, footprint-verification record location; C-21 / C-28),
  `templates/project.yaml` (`skill.version`, `kickoff`, `fab_dfm` + `bar`, `print_targets` incl. `home_fdm`, historical CAD key names explained,
  `quiet_regex` aligned; C-16), `templates/90-log/DECISIONS.md` (anchored grep, CC-001 evidence cell; C-13 / C-19), `templates/RELEASE_NOTES.md` +
  `production_cut.yaml` + `release-and-cut.md` (**one records home** `70-release/<md5-8>/records/`; C-05), `templates/90-log/STATUS.md` (PAUSE POINT
  skeleton; C-30), `templates/VENDOR_REVIEW_RECORD.md` (reply template; B-22), `templates/CLAUDE.md` (bar in rule 9, kickoff answers as decisions).
- `references/pitfalls.md`: the retracted material-before-flag line replaced by the corrected mechanism (C-03); a provenance note on the source
  pointers (C-27); snap / wedge / engraved-text lines relabelled; `home_fdm` naming; `references/agent-ops.md`: the per-call ceiling stated once
  (600 s, platform limit) and every other mention points there (C-18); `references/fea-stage.md` / `software-track.md`: who accepts a WARN, who
  approves T-nn limits (C-17); `references/fab-dfm.md` / `vendor-review.md`: checker line vs published minimum vs owner bar (B-15), SLA 2 mm part
  vs 0.8 wall (B-09), acceptances need date + evidence; `references/case-pipeline.md`: `--gate-dir`, §7.2, targets by name.
- Smoke: `smoke/design/case.yaml` labelled FIXTURE and at 1.6 (C-11); MFG-003 doc id (C-22); README wording (C-23); `fab_dfm` + `print_targets` in
  `smoke/project.yaml`; the dfm acceptance dated with an evidence file; greps for every rule above and for source-identifier leaks (C-15 / B-34).
- Evals: 1 says "fab part number" (C-25); 6 and 7 re-worded for targets, accepted list, allowed options; 7 labelled as the source scenario.
- README rewritten: title block, what you get, five-line quick start, repository map as a table, install as numbered steps with one command per
  line (no fenced line over 90 characters — the old blocks scrolled on GitHub), the questionnaire, the retro loop, versioning, MIT (C-29), retro PRs.

### Added
- **`references/pcb-layout-dfm.md`** (owner: "are the PCB building rules captured" — they were not): the G1→G2 chain (placement CSV, router session,
  `out/G2/` pack, decider) and the PCB build rules tagged checker / fab capability (dated, URL) / physics / owner choice — stack-up and copper
  weights, controlled impedance and differential pairs, trace / space / via / annular / drill vs the fab table with margins, via-in-pad and
  tenting, thermal reliefs and teardrops, mask / paste / stencil, component size and link-part policy (no 0201, 0402 min, 0603 signal links, 1206
  power links as owner choices), two-sided assembly, polarity / rotation / CPL and the fab's rotation table, fiducials and test points, silk,
  courtyards and tombstoning, creepage, panelization, the DRC census (0 / 0 / 0 warnings unless a dated waiver row), route-quality classes,
  parity, the canary rule, the fab DFM mirror before the order, the stock freeze (C-07 widened).
- **`references/kickoff-questionnaire.md` + `templates/10-spec/KICKOFF_ANSWERS.md` + SKILL §0.1**: 40 decision classes in ten `AskUserQuestion` batches
  (product / process / material / quantity; PCB build ×8; enclosure architecture ×8 incl. retention screws+inserts / magnets / none, labelling
  deboss / plate / badge, fan, vents, light pipe; the bar and what may be waived — default nothing; verification; bought parts; software; release;
  identity / envelope / delegation), each with a RECOMMENDED answer and 2–3 alternatives with consequences; answers → D rows, `project.yaml`,
  traceability, before any CAD.
- **`scripts/skill_retro.py` + SKILL §13 + `docs/retro/`**: the self-improvement step (classify a project's learnings against the skill, draft the
  CHANGELOG / reference patches / evals / questionnaire questions; version drift); first run on a board-and-enclosure project folded in (per-class census
  clustering, magnet grades and polarity keying, colliding owner rules, eight pitfalls lines, questionnaire batch 10).
- **`references/cnc-enclosure.md`** (B-10): corner radii, pocket depth, walls, threads, tolerances, anodising build-up, quote page, case-order gate.
- **`references/dfm-printed-enclosure.md`** §1.1 retention hardware per material (inserts: type / bore / depth / boss OD from the TDS, temperature;
  magnets: one project's decision pattern — grade, coating, max temperature, pull vs gap, pocket fits glued MJF / pressed PLA, polarity by an asymmetric boss),
  §1.2 post-processing effects, §1.3 material rating and thermal, §1.4 tolerance stack + per-preset fits, §8 FDM elephant foot / hole shrink / seam /
  2 × line width / anisotropy / g-code as the support record / rotate not mirror / insert + torque coupon, §10 post-mortem with the received-part
  caliper table, photo protocol, fractography, vendor-fault decision table, §11 SLA rule set (B-08 / B-09 / B-11 / B-16 / B-21 / B-23 / B-24 / B-28 /
  B-36 … B-38 / B-42); `references/part-verification.md` hardware line schema, hardware classes table, adhesive substrate compatibility on PA12
  (B-26 / B-27 / B-28); `references/release-and-cut.md` labels / regulatory marks and packaging (B-40 / B-41); `pcb-layout-dfm.md` §12 creepage and
  the EMI / grounding row as a decision prompt (B-39).
- Templates: `SPEC.md`, `design/VERIFY.md`, `G1/EVIDENCE.md`, `G1/REVIEW_NOTES.md`, `parts/PROCUREMENT.md`, `design/SOFTWARE_ARCHITECTURE.md` (C-08).
- Workflows: the `case_dfm` role in the board role set (B-30). Evals 8 (kickoff) and 9 (retro). Smoke: `skill_retro.py --selftest`.

### Not done (deferred)
`gate_status.py` (gate cells stay free text) · a probe generator (the recipe is §7.1) · a `--slabs` mode in the census · the bbox-resolution test
itself (hypothesis and test stated, not run) · a KD-tree-free opposing metric (scipy is now a mesh-script dependency) · the questionnaire's
owner-topic matcher is a keyword scorer (71 of 87 source owner rows still listed as candidates — most are project narrative, batch 10 took the
recurring ones) · `pitfalls.md` still names source rows as provenance (a note explains them; a footnote file was judged not worth it) · the SLA
and CNC references are literature + two quote sessions, not received parts · evals 6 / 7 stay the source scenario as regression tests.

## 0.4.1 — 2026-09-28 — vendor quote-page verdicts done right, the length-dependent thin-wall metric, home-preset mirror, one-piece dummy, bought hardware (a board-and-enclosure project, late 2026-09-28: two case rounds, its decision and blocker rows, PROBES.md)

0.4.0 shipped the same evening the project found that two of its "no flag" quote-page readings were false, that JLC3DP's thin-wall metric
depends on part LENGTH, and that its home-printer preset had to carry every vendor decision. Owner's words: "the skill we are developing should handle
home-printer and vendor operations properly" (paraphrased: the owner named the printer and the vendor). 0.4.1 corrects the procedure and adds the probe method that closes such a round in one pass. No script changes.

### Changed
- **`references/dfm-printed-enclosure.md` §7 (quote-page procedure) rewritten**: the verdict of record is the analysis API response
  `getFileAnalyzeResult` at `parseStatus == 2` → `modelAnalysisVO.thinWall`, read from the browser's network log or re-requested; **a DOM reading before
  parseStatus 2 is invalid** (a false "no flag" happened twice); **the flag is computed at UPLOAD and does not depend on the material chosen on the
  line** (material is still set first — for the price and the map legend; 0.4.0 had attributed a flipped verdict to the resin default);
  `modelAnalysisVO.previewUrl` opens the heat map (Analysis Results tab) directly; one STL per page session with a reload between uploads; the hidden
  `input[type=file]` can be unhidden by script; uploads and analysis work signed out (ordering does not); the coordinator re-reads a worker's PASS
  from the API before a decision row says so. §3 evidence = md5 + parseStatus 2 (not md5 + material).
- **`references/vendor-review.md` §4**, **SKILL.md §8.1 items 4 / 5**, **`templates/DFM_ROUND.md`** (new column `API parseStatus / thinWall (how
  read)`, rows without it have no verdict, material column marked "price + legend; not the flag", flip rule = check both reads first) follow.

### Added
- **`dfm-printed-enclosure.md` §7.1 — the thin-wall metric is LENGTH-DEPENDENT** (an identical rim-over-lap-step profile passed at 48 mm, failed at 88
  and 147 mm while three ray-cast censuses found nothing under 1.37): calibrated MJF PA12 rule at ~150 mm parts — **rim above a skirt-lap step ≥ 2.0
  (1.4 fails; 2.0 passes with step + inward undercut kept) OR the undercut filled so the inner wall runs straight to the rim top (`lap.ring_down`,
  then 1.25 … 1.3 above the step passed)**; grey set (plain 2.0 walls / floors, boss rings, chamfers into ≥ 1.2 walls, 45° dish ramps) and red set
  (free-standing wedges). **The probe method** that converges in one round: slice the failing body of record into capped slabs
  (`trimesh slice_mesh_plane`) to localise the feature and the length threshold, then plain-profile OpenSCAD polygon extrusions at **40 mm AND full
  length with ONE knob each**, each uploaded alone and API-read, tabulated in `probe/PROBES.md`; a 40 mm pass proves nothing about a 147 mm body; a
  scaled body is not informative. `templates/DFM_ROUND.md` §5 Probes; §1 pointer line.
- **§9 home-preset mirror**: every vendor DFM decision (rails off, key off, closed rim, undercut filled, feet concentric, hood on screws) applied to the home
  preset the same day in the SAME yaml under its own version key with the deciding round in the comment; its census gate (walls 1.6 / ribs 1.2 /
  voids 1.0) and slicer log clean; a vendor-only geometry fix must prove partner overlap 0 mm³.
- **§8 one-piece board dummy pattern**: cage / sink fused to the slab at final dimensions; the nose overhang on a break-away shim (1.2 mm block
  on the bed, inset 0.5 from the nose sides, 0.6 clear of the board edge, 8 posts 1.2 × 1.2 across a 0.4 mm two-layer perforation gap); **the README
  says the shim looks like a "PCB lip" and comes off** (the owner read it as the board); one-piece vs two-piece proven by section symmetric
  difference 0 mm² and both bboxes against the cage envelope of record; both versions kept; kit folder = case pieces + coupons + BOTH dummies (with
  their 3MFs) + READMEs, the stale kit named for deletion.
- **`references/part-verification.md` "Bought hardware"**: McMaster-Carr is login-walled for automation (JS shell + "please log in" in a real
  Chromium), Digi-Key (Cloudflare) / Mouser / Newark / Farnell / RS / Keystone / Essentra block fetches → verify on the manufacturer's site (3M product
  pages rendered in a real browser) + the manufacturer's PDF TDS by curl + plain-HTML dealers; snippet-only prices and numbers [K]; a BLOCKERS row
  with the exact URL + filter set for the owner to open logged in; never invent a number; fit numbers beside the part; count drift between records
  flagged in the decision row.
- **`references/agent-ops.md`** §2: a fork subagent stops at ~200 turns → chunked tasks with checkpoint commits, resume from HEAD with measured
  state; tags created before the final gated commit are re-pointed (`git tag -f`) and the record says so. §6: the coordinator verifies a subagent's
  claim independently before it becomes a decision row (the "no flag" claims were re-read); the DevTools browser is shared state — another agent
  can restart it between turns, so page ids and sign-in are re-derived before every upload / read.
- **`references/pitfalls.md`**: +12 dfm lines (API verdict, flag at upload, previewUrl / unhide / signed out, length dependence, calibrated rim rule,
  probe method, opposing faces in any direction, home-preset mirror, one-piece dummy, vendor-only divergence, coordinator re-read), +3 agents / git (turn
  limit, tag re-point, browser restart), +3 sourcing (McMaster / distributors, feet-over-screws bond ring, count drift); header 0.4.1.
- **Smoke step 0** greps the API-verdict, flag-independent-of-material, LENGTH-DEPENDENT, rim-over-lap-step and full-length-probe rules in the
  reference, SKILL §8.1 and `DFM_ROUND.md` §5. **Eval 6** re-worded (API verdict, no "material flips the flag" claim, coordinator re-read, home-preset mirror,
  kit contents); **eval 7** "vendor flags a body the census calls clean" (probe method, one knob each, both presets, named census row, API
  re-verification, partner overlap 0).

### Not done (deferred)
A probe-generator script (the polygon-extrusion probes stay project-side; the recipe is §7.1) · a `--slabs` mode in `thin_wall_census.py` (the
`slice_mesh_plane` call is one line in the reference) · the census "opposing face in any direction" metric as a skill script (recorded, not gated,
on the project — over-reads on 0.4 offsets the vendor accepts) · the 0.4.0 deferrals stand.

## 0.4.0 — 2026-09-28 — printed-enclosure DFM: one vendor round instead of four (a board-and-enclosure project's decision and case rows, learnings 2026-09-27 / 09-28)

A board-and-enclosure project's MJF trays cracked on a 0.88 × 141 mm lip that a "kept below minimum (listed)" row had waived, and its FDM preset passed its own
census and failed as a print. Four vendor rounds and twelve full rebuilds later every rule was measured; 0.4.0 ships them so the next enclosure is
vendor-clean before its first quote. Owner's words: "include all the learnings into the skills so that next time we reduce the number of iterations".

### Added
- **`references/dfm-printed-enclosure.md`** — the acceptance bar (0 FAIL / 0 WARN in tables and census, zero slicer warnings, no vendor flag, no
  yellow / red, every face looked at; INFO-vs-WARN split); MJF rules as measured at JLC3DP (every parallel-faced wall ≥ 1.2 designed 1.3, every void
  ≥ 1.2, no free-standing wedge — chamfers into walls stay grey, no slit tabs / detents / living hinges, no engraved text, a 141 × 0.88 skin cracks,
  a feature that cannot be clean in its space budget goes, rule-drift re-derivation, coupled knobs, overshoot slabs); waivers are not checks — the
  census is a FAIL gate per preset with wall / wedge / void classes, span, SANITY row and a pure adopt gate; heat map = strength finding; closed
  rims; designed asymmetries rendered + in the order sheet + KNOWN_ISSUES; every face incl. the sole; the JLC3DP quote-page procedure (ONE STL per
  session, process + material set BEFORE reading the flag — the default is resin and its map differs, flag first, viewer → Analysis Results → Thin
  Wall Heatmap on every face, screenshots named with the md5, verdict flips → diff the meshes, canonical STL so the md5 is the geometry); the FDM /
  home-printer-first preset (one desktop printer) (walls ≥ 1.6, raised legends cap 4 / stroke 1.0 / 0.6, no rigid bump on a slit tab, fan bosses = holes, hood
  roof-down on screws + inserts, coupons before the case, two-piece AND one-piece board dummy at final dimensions, 3MF projects with project-named
  presets + `different_settings_to_system`, floating-region warning = FAIL, auto-orientation); two versions from one yaml (hook tokens, own version
  key, byte-identical vendor SCAD); the cracked-part post-mortem pattern (measure the ordered STL, intent vs defect, accept-and-ship reply with the
  number, apply design-wide).
- **`scripts/thin_wall_census.py`** — inward rays = walls, outward rays = voids, clusters below `gate − 0.05` classified wall / wedge by the
  opposite-face angle, legend boxes gate at `--box-min`, `--json` record (`stl_md5`, clusters, voids, `fails`), pure `--gate-dir` for `gates.adopt`,
  exit 1 on FAIL; `--selftest` runs the pure core without mesh libraries and three trimesh primitives when installed (1.0 plate FAIL, 45° prism
  wedges only, 2.0 plate 0 FAIL). Validated read-only on the project's ordered tray (WALL 1.00 × 144 mm + 0.50 detent voids → FAIL 5) and on
  its v3.16 tray (0 FAIL, SANITY 0.00 % / 0.00 %). `thin_wall_check.py --census` stays the quick look and points at the gate.
- **`templates/CENSUS_GATE_ROWS.md`** — the check-table rows every printed body carries (census header, WALL / VOID / wedge clusters, SANITY,
  band-by-design, bodies = 1, concentricity from mesh sections, designed offsets, six face renders) + the adopt-list line.
- **`templates/DFM_ROUND.md`** — one record per vendor quote-page session under `60-orders/quotes/<date>/`: body, canonical md5, material set before the
  flag, flag, heat-map screenshots per face, colour → feature mapping, our numbers, verdict.
- SKILL §8.1 "DFM for printed enclosures" + Where-to-look row; §11 commit after every meaningful step (uncommitted four-hour trees, subagent turn
  limits → checkpoint commits); `agent-ops.md` §2 the same + a worker fork hands the blind review back.
- `references/pitfalls.md`: new section *dfm / printed enclosures* (32 lines) + agents/git (checkpoint commits, turn limits, Linux CI parity checklist,
  filter-repo hash remap) + mechanical (GLB face groups, vertex-colour bleed); header now 09-21 … 09-28.
- `references/case-pipeline.md`: the print-service bullet no longer says "list what stays thinner" — no waiver, census gate, canonical STL, two
  versions; `references/vendor-review.md` §4: material first, one file per session, wall / void / free-wedge colouring, verdict-flip rule;
  `references/project-yaml.md`: the census gate as a measurer + adopt-list example.
- Smoke step 0: the reference must carry the 1.2 / 1.3, void, free-wedge, one-STL-per-session, material-first and waiver-row rules and
  `thin_wall_census.py --selftest` passes without mesh libraries. Eval 6: first DFM round of a printed enclosure.

### Not done (deferred)
The census "backed vs free" wedge attribute (today every free wedge is removed by design and the listed wedges are the vendor-confirmed grey set) ·
a canonical-STL writer as a skill script (the contract is in the reference §7.7; the writer stays project-side next to the exporter) · coupon,
board-dummy and 3MF generators (project-side; their rules are in the reference §8) · concentricity / face-render measurers (project-side; rows in
`CENSUS_GATE_ROWS.md`) · a workflow `.js` for the DFM round (prose + `DFM_ROUND.md`).

## 0.3.0 — 2026-09-26 — post-order learnings of a board-and-enclosure project (its decision and change rows, learnings 2026-09-22 late … 09-26)

Both 0.2.1 "Next" candidates plus the learnings logged after the order went in. Everything generic; the project is cited as the worked example.

### Added
- **docs/ governance layout as the default paths** — `scripts/project.py` DEFAULTS: `90-log/` (DECISIONS STATUS GATES BLOCKERS KNOWN_ISSUES
  TRACEABILITY LEARNINGS_LOG ERC_WAIVERS ENV), `20-design/TEST_PLAN.md`, `60-orders/PARTS_VERIFICATION.md`, `reviews_dir` / `quotes_dir` /
  `production_dir` / `datasheet_notes` keys; every `docs/<FILE>.md` literal in SKILL / references / templates / workflows / evals / smoke migrated;
  install recipes copy per folder; `references/project-yaml.md` §Layout.
- **`scripts/reorg_paths.py`** — project.yaml `reorg:` block (moves, trim, untrack, gitignore, frozen, skip, allow_old_files, no_existence, allow_missing):
  `--plan / --apply / --check / --map / --proof BEFORE AFTER REWRITES / --selftest`; word-boundary-guarded longest-first idempotent rewrite incl. the
  `"docs" / "X"` join forms; own files exempt; zero-loss proof by blob identity. `release-and-cut.md` §9 (method, live vs record citations, tag checks).
- **`scripts/thin_wall_check.py`** — `--census` (inward ray-cast with the < 0.02 mm self-hit discard, histogram, feature clusters) and `--pinch`
  (point contacts on the section outline: non-adjacent vertices < 0.05 mm; necks after web discs clipped to the closing; `to_2D()` re-origin mapped
  back); pure-python `--selftest`. `case-pipeline.md` §Point contacts + the ≈ 45 min version-bump cost table (background jobs, EXIT lines).
- **`scripts/assembly_guide.py`** + `assembly_guide:` block — illustrated guide: authored short yaml + generated `### Step N` text + one render per
  page keyed on (geometry md5, defs, camera, size); `--check`; `release-and-cut.md` §8; smoke fixture with a stub renderer.
- **`references/vendor-review.md` + `templates/VENDOR_REVIEW_RECORD.md`** — the fab's post-order review: file mail + images → map every flag on the
  STLs of record → decide per line → fix through the generator → re-run the vendor's DFM on the replacements → Replace File / chat only on the
  owner's explicit word; hard boundaries (never pay / agree / cart / change a line); quote-page mechanics (`getFileAnalyzeResult` `previewUrl`,
  Edit dialog saved = form state, "audit failed" mail = Replace File enabled) as the JLC3DP worked example.
- **Placed-order stock freeze** — `markers.placed_regex`; `fab-dfm.md` §8 contract: a PLACED package is judged on `stock_snapshot.json` frozen at the
  build and hashed in the manifest; selftest on a stock fixture; fab files never rebuilt.
- **Read-only checkers** — `adopt_gates.sh` fails when `git status --porcelain` changes across the gates (selftest case); `templates/ci/pr-check.yml`
  final "tree unchanged" step; `agent-ops.md` §3, SKILL §2.
- **One-round record chain + fixed point** — `release-and-cut.md` §3.1 (order, analysis index ↔ cut build ↔ PDF render, volatile cascade, "whoever
  appends a row runs the round").
- **Memory / pause-point / owner-list conventions** — `agent-ops.md` §7; SKILL §11.
- `references/pitfalls.md`: +40 lines (process, tooling, kicad render, mechanical/point contacts, documentation, sourcing/compliance).
- Smoke: docs moved to the layout, `reorg:` + `assembly_guide:` blocks, new gates (three selftests, `reorg_paths --check`, `assembly_guide` build + `--check`).
  Evals: 4 (vendor review mail — boundaries), 5 (re-layout — zero loss).

### Fixed (blind review 0.3.0, `80-reviews/SKILL_REVIEW_0.3.0_merged.md`)
- `known_issues.py` / `release_report.py` / `handoff_header.py` gained argparse: `--help` or an unknown flag never runs the default write (A-01).
- `reorg_paths --check`: a directory segment (`docs/v1.2/x`) is not a dangling file; `allow_missing` and the `--proof` failure branch are selftested; URLs documented as not rewritten (B-01/02/21).
- `adopt_gates.sh`: empty `gates.adopt` is a failure; the read-only guard also hashes `git diff HEAD` (a re-modified dirty file shows); ERR traps name the line (B-03/05, A-06).
  `pr-check.yml` snapshots the tree after Bootstrap and diffs (B-06).
- `thin_wall_check`: missing trimesh / numpy / shapely exits 2 with the install hint; `--pinch` also tests between rings and fails on > 1 polygon; the
  `to_2D()` map-back uses the full 2-D affine part; a plane that misses the mesh is a message (B-04/07/08, A-16).
- `assembly_guide`: orphan renders pruned / flagged; `{SIZE}` quoted; yaml booleans lowered (B-09/25).
- Templates / docs: `production_cut.yaml` VG-001 row; SKILL agent-ops § numbers; project venv gets pyyaml; vendor-review tables live in the record;
  generic wording for the bump cost and the vendor frame; project-side generators italicised in §3.1; `reorg.gitignore` documented.

### Changed
- `templates/project.yaml`, `templates/CLAUDE.md` layout block, `smoke/project.yaml`, SKILL §0 step 2 / §2 / §8 / §10 / §11 / Where to look; README layout + version.

### Not done (deferred)
`scripts/production_cut.py` and the fab-package generator stay project-side (contracts only) · `gate_status.py` · a workflow `.js` for the vendor
round (the flow is prose + a record template; the blind machinery is unchanged) · marketing-pack and schematic-pack generators (project-side;
their pitfalls are in `pitfalls.md`).

## 0.2.1 — 2026-09-22
- MUST-5 ci fill check greps `{{PROJECT_` only; SHOULD-14 dfm_check INVALID-ITEM instead of KeyError; gate_status.py deferred.

## 0.2.0 — 2026-09-22 — blind-review fix round

Fixes from the skill's own blind double review (`SKILL_REVIEW_merged.md` in the project, readers A / B / executor + verifier: 5 MUST,
17 SHOULD, 15 COULD; verdict "fix MUST list first"). All five MUST items and 17/17 SHOULD items applied (SHOULD-13 by labelling, not by a new
generator); COULD items applied where trivial.

### MUST
1. **Install layout / clone gate** — `scripts/clone_gate.sh` links the working tree's `scripts` and `.venv` into the archive with `rm -rf` +
   `ln -sfn` (a dangling relative symlink or an empty submodule dir no longer breaks it); one canonical layout in README and SKILL §0
   (submodule at `vendor/hw-from-spec`, relative symlink `scripts`, or a copy; never a submodule at `scripts/`); the clone-gate selftest and
   `smoke/run_smoke.sh` commit that exact layout (relative link into a gitignored `vendor/` dir) and assert the archive carries the link.
2. **G0→G1 content** — new `references/schematic-phase.md` (design yaml shape, ERC command, map checks defined, G1 review pack, G0→G1 order);
   SKILL §5 G0 round paragraph; `workflows/blind-deep-review.js` `{{ROLE_SET}}` = `spec` with four spec roles and a G0 clause in the common
   prompt; "VERIFY item" defined once in SKILL §4 and referenced from `templates/CLAUDE.md` rule 3 and `templates/90-log/GATES.md`; rule 4 now says
   "agents never write approval cells or the release line"; hand-off template notes the MISSING rows at G0; `handoff_header.py` prints
   "no board in HEAD" instead of a sliced message.
3. **Model rotation** — `m2 = MODELS[(i + 1) % n]` in both review workflows; both throw unless ≥ 2 distinct models and `m1 !== m2`;
   `workflows/README.md` says so.
4. **dfm_check acceptances** — `accepted()` returns the matching entry; the dict-form budget applies to that entry only; mixed-form selftest.
5. **CI templates** — `templates/ci/README.md` says nothing substitutes the placeholders and gives the `sed` recipe + `project.env`;
   `release.yml` uses `{{PROJECT_CLONE_GATE_CMD}}`; SKILL §0 step 7 names the folder; project name removed; both shell gates ported
   from zsh to bash (≥ 3.2), README requirement updated.

### SHOULD
`dfm_check.py` writes `dfm.report` on every plain run and has `--check`; unknown check names are warned about and the items schema is a table in
`fab-dfm.md` §2 (`fab_counts` dropped) · shell gates probe `import yaml` before accepting an interpreter and print the choice · `collect_renders.py
--check` (alias `--dry`) exits 1 when a rule would be redone; no `nomd5/` folder when there is no board · `silk-audit-verify.js` re-verify uses
`merged.recrop_dir` (MERGE schema field) · SKILL §1.1 "At a gate" and §11.1 "Resume" protocols · day-1 templates: `project.yaml` (G0 gate list,
commented G1/G2 blocks), `design/traceability.yaml`, `.gitignore`, `ENV.md`, `TEST_PLAN.md`, `ERC_WAIVERS.md`, `datasheet_notes/_TEMPLATE.md`;
`known_issues.py` warns when the test plan is missing · SKILL §0 step 6 "first records" sequence · `traceability.py --no-commands` → PENDING,
MISSING message for a missing yaml · `handoff_header.py` selects the package by content match on the HEAD board md5 (`release_report.pkg_for_board
(md5=…)`), hashes bytes (CRLF / non-UTF-8 safe) · `release_report.board_md5` uses the raw md5 already recorded · KNOWN_ISSUES §2.1 lists APPLIED
rows only · shell gates refuse a `project.yaml` that is not at the git top level (clear message) · production cut labelled "project-side
generator; contract in release-and-cut §7" · `project.py --selftest` · freeze recipe adds `git submodule update --init` (SKILL, agent-ops,
workflows/README).

### COULD (trivial ones)
Banner no longer prints the release phrase · smoke: portable md5 (`$PY`), venv fallback with a message, census tail shows the numbers row, the
owner line appended as a 4-cell row · SKILL §0 step order (venv before selftests) · ID-reservation grep matches CC rows explicitly · placeholder
hygiene (`{{EXTERNAL_MODEL}}`, split `PREVIOUS_MERGED_REPORT(S)`, no literal double brace in the js comment) · `project.yaml skill: {repo, commit}`
key; undeclared `paths.dfm_thresholds` read removed · "fill every `{{}}`" rule, `SKILL_COMMIT` instead of the undefined `SKILL_VERSION`, CC-001
row written after the gates ran · no-runner fallback sentence · skill `.gitignore` trimmed; README says the licence is pending.

### Not done (deferred)
`scripts/production_cut.py` (contract only) · `gate_status.py` / `markers.gate_regex` (gate cells stay free text; the protocol is prose) ·
pitfalls.md worked-example labelling and per-call ceiling alignment (both done in 0.5.0) · `--project` in known_issues / release_report / handoff_header (done in 0.3.x) ·
selftests leave `mkdtemp` dirs · plugin manifest example · prompt numbers in `silk-audit-verify.js`.

## 0.1.0 — 2026-09-22 — first cut (`eadc965`, ci templates `83da1ad`)
SKILL.md, references, project.yaml-driven generic scripts with selftests, workflow templates, record templates, smoke dry run, evals.
