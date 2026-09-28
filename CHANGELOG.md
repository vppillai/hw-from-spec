# CHANGELOG — hw-from-spec

## 0.4.0 — 2026-09-28 — printed-enclosure DFM: one vendor round instead of four (source project D-79 … D-84, CC-204 / CC-205, learnings 2026-09-27 / 09-28)

The source project's MJF trays cracked on a 0.88 × 141 mm lip that a "kept below minimum (listed)" row had waived, and its FDM preset passed its own
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
  Bambu P2S printer-first preset (walls ≥ 1.6, raised legends cap 4 / stroke 1.0 / 0.6, no rigid bump on a slit tab, fan bosses = holes, hood
  roof-down on screws + inserts, coupons before the case, two-piece AND one-piece board dummy at final dimensions, 3MF projects with project-named
  presets + `different_settings_to_system`, floating-region warning = FAIL, auto-orientation); two versions from one yaml (hook tokens, own version
  key, byte-identical vendor SCAD); the cracked-part post-mortem pattern (measure the ordered STL, intent vs defect, accept-and-ship reply with the
  number, apply design-wide).
- **`scripts/thin_wall_census.py`** — inward rays = walls, outward rays = voids, clusters below `gate − 0.05` classified wall / wedge by the
  opposite-face angle, legend boxes gate at `--box-min`, `--json` record (`stl_md5`, clusters, voids, `fails`), pure `--gate-dir` for `gates.adopt`,
  exit 1 on FAIL; `--selftest` runs the pure core without mesh libraries and three trimesh primitives when installed (1.0 plate FAIL, 45° prism
  wedges only, 2.0 plate 0 FAIL). Validated read-only on the source project's ordered tray (WALL 1.00 × 144 mm + 0.50 detent voids → FAIL 5) and on
  its v3.16 tray (0 FAIL, SANITY 0.00 % / 0.00 %). `thin_wall_check.py --census` stays the quick look and points at the gate.
- **`templates/CENSUS_GATE_ROWS.md`** — the check-table rows every printed body carries (census header, WALL / VOID / wedge clusters, SANITY,
  band-by-design, bodies = 1, concentricity from mesh sections, designed offsets, six face renders) + the adopt-list line.
- **`templates/DFM_ROUND.md`** — one record per vendor quote-page session under `docs/quotes/<date>/`: body, canonical md5, material set before the
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

## 0.3.0 — 2026-09-26 — post-order learnings of the source project (D-70…D-76, CC-190…CC-199, learnings 2026-09-22 late … 09-26)

Both 0.2.1 "Next" candidates plus the learnings logged after the order went in. Everything generic; the source project is cited as the worked example.

### Added
- **docs/ governance layout as the default paths** — `scripts/project.py` DEFAULTS: `docs/governance/` (DECISIONS STATUS GATES BLOCKERS KNOWN_ISSUES
  TRACEABILITY LEARNINGS_LOG ERC_WAIVERS ENV), `docs/design/TEST_PLAN.md`, `docs/parts/PARTS_VERIFICATION.md`, `reviews_dir` / `quotes_dir` /
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

### Fixed (blind review 0.3.0, `docs/reviews/SKILL_REVIEW_0.3.0_merged.md`)
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

Fixes from the skill's own blind double review (`SKILL_REVIEW_merged.md` in the source project, readers A / B / executor + verifier: 5 MUST,
17 SHOULD, 15 COULD; verdict "fix MUST list first"). All five MUST items and 17/17 SHOULD items applied (SHOULD-13 by labelling, not by a new
generator); COULD items applied where trivial.

### MUST
1. **Install layout / clone gate** — `scripts/clone_gate.sh` links the working tree's `scripts` and `.venv` into the archive with `rm -rf` +
   `ln -sfn` (a dangling relative symlink or an empty submodule dir no longer breaks it); one canonical layout in README and SKILL §0
   (submodule at `vendor/hw-from-spec`, relative symlink `scripts`, or a copy; never a submodule at `scripts/`); the clone-gate selftest and
   `smoke/run_smoke.sh` commit that exact layout (relative link into a gitignored `vendor/` dir) and assert the archive carries the link.
2. **G0→G1 content** — new `references/schematic-phase.md` (design yaml shape, ERC command, map checks defined, G1 review pack, G0→G1 order);
   SKILL §5 G0 round paragraph; `workflows/blind-deep-review.js` `{{ROLE_SET}}` = `spec` with four spec roles and a G0 clause in the common
   prompt; "VERIFY item" defined once in SKILL §4 and referenced from `templates/CLAUDE.md` rule 3 and `templates/GATES.md`; rule 4 now says
   "agents never write approval cells or the release line"; hand-off template notes the MISSING rows at G0; `handoff_header.py` prints
   "no board in HEAD" instead of a sliced message.
3. **Model rotation** — `m2 = MODELS[(i + 1) % n]` in both review workflows; both throw unless ≥ 2 distinct models and `m1 !== m2`;
   `workflows/README.md` says so.
4. **dfm_check acceptances** — `accepted()` returns the matching entry; the dict-form budget applies to that entry only; mixed-form selftest.
5. **CI templates** — `templates/ci/README.md` says nothing substitutes the placeholders and gives the `sed` recipe + `project.env`;
   `release.yml` uses `{{PROJECT_CLONE_GATE_CMD}}`; SKILL §0 step 7 names the folder; source-project name removed; both shell gates ported
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
pitfalls.md worked-example labelling and per-call ceiling alignment · `--project` in known_issues / release_report / handoff_header ·
selftests leave `mkdtemp` dirs · plugin manifest example · prompt numbers in `silk-audit-verify.js`.

## 0.1.0 — 2026-09-22 — first cut (`eadc965`, ci templates `83da1ad`)
SKILL.md, references, project.yaml-driven generic scripts with selftests, workflow templates, record templates, smoke dry run, evals.
