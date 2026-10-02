<!-- blind reviewer A: Agent tool, Claude Opus, venv without the mesh libraries; artefact + checklist only; 2026-10-02 -->
# Blind review A — hw-from-spec `layout-0.11.0` (cold user, venv without mesh libraries)

Scratch: `$R=/private/tmp/claude-502/-Users-vpillai-temp-aec-tester/d3f10fc6-10e5-4769-b4fd-2330e8da1aae/scratchpad/review_A`.
Projects: `$R/proj` (both), `$R/proj_ee`, `$R/proj_mech`; each = README step 4 copy block verbatim, skill copied to `vendor/hw-from-spec`,
relative `scripts` symlink, `.venv` -> the skill's pyyaml-only venv. Slots filled mechanically by `$R/fill.py` for the day-1 gate run.

## Findings

| id | sev | where | what | evidence | suggested fix |
|---|---|---|---|---|---|
| A-1 | BLOCKER | `smoke/run_smoke.sh:75` | The smoke needs the skill folder to be a git repo (`cd "$SKILL" && git ls-files -s scripts`). From a `git archive` / tarball / "Download ZIP" copy it dies at section 0 with no FAIL line or SMOKE verdict. | `scripts/jobs.sh -- smoke/run_smoke.sh` in `$R/skill` -> rc 1, last line `fatal: not a git repository (or any of the parent directories): .git`. Same tree after `git init && commit` (`$R/skill_git`) -> `SMOKE OK`. | Skip the mode check with a NOTE when `$SKILL` is not a work tree, or check modes with `test -x`. |
| A-2 | MAJOR | `templates/project.yaml:217` vs README:124 | README step 4 copies `20-design/arrival_checklist.yaml` on day 1. The template keeps `arrival_checklist.py --check` commented, and `gates-required` demands that line once the yaml exists, so a fresh project is red on day 1. README:133 says the yaml is "copied at the order (SKILL §10.1)", which contradicts the copy block. | `scripts/adopt_gates.sh --no-clone` -> `GATES REQUIRED: 20-design/arrival_checklist.yaml exists but gates.adopt has no ... --check line` / `GATE FAILED`. | Pick one: drop the yaml from the day-1 copy, or ship the gate line uncommented and make step 6 render the checklist. |
| A-3 | MAJOR | SKILL.md §0 step 6 (l.59-65) | The first-records sequence names known_issues, traceability and release_report only. The day-1 `gates.adopt` also runs `now_pages.py --check` (and, per A-2, `arrival_checklist.py --check`). Following the sequence exactly gives a red adopt run. | After step 6, adopt -> `STALE: 00-now/WHERE_THINGS_STAND.md ... GATE FAILED: $PY scripts/now_pages.py --check`. Then `arrival_checklist --check: ... stale or missing`. Green only after running `now_pages.py` and `arrival_checklist.py` too. | Add `now_pages.py` (last) and `arrival_checklist.py` to step 6. Better: one `make records` / `record round` command that step 6 names. |
| A-4 | MAJOR | `scripts/now_pages.py:82` + `templates/90-log/GATES.md:28,31` | WHERE_THINGS_STAND reports the order gates as **approved** on day 1. The template cell "owner's click — never an agent's" is neither empty, `_…`, nor "not yet", so it reads as an approval. This is the first page a cold reader opens. | `00-now/WHERE_THINGS_STAND.md` (both, ee, mech): `- Order (board): approved — owner's click — never an agent's`, `- Case order: approved — …`. | Put `_not yet approved_` in the template cells (move the prose to the Meaning column), and/or make now_pages parse an approval as `name, YYYY-MM-DD, …`. |
| A-5 | MAJOR | `scripts/iteration_gate.sh:13-16,39` | `--selftest` builds a temp repo whose `scripts/` symlinks the files. `$HERE/../.venv` then points into the temp dir, and unlike adopt_gates it does not take the caller's `.venv`. README step 3's loop (`for s in scripts/*.sh; do "$s" --selftest`) fails on a stock machine. | `scripts/iteration_gate.sh --selftest` -> `iteration gate: no python with pyyaml found (project .venv, skill .venv, python3)` rc 1. With `PYTHON=$PWD/.venv/bin/python` -> `selftest OK`. | Copy adopt_gates.sh's line: export the caller's `$PWD/.venv/bin/python` as PYTHON before the cd. |
| A-6 | MAJOR | `templates/production_cut.yaml:22,25` | Cross-scope deliverables survive `scaffold`. In mech scope, `case_drawing` points at `30-board/layout/drawings/CASE_DRAWING.pdf`, but mech has no 30-board. In ee scope, `fea_pcb` (required: true) points at `40-case/board_mesh/pcb_fea/…`, but ee has no 40-case. | `grep 30-board $R/proj_mech/20-design/production_cut.yaml` -> l.19 case_drawing; `grep 40-case $R/proj_ee/20-design/production_cut.yaml` -> l.19 fea_pcb. | Move the drawings to `20-design/drawings/` or the owning stage, and give fea_pcb a scope-neutral home (`30-board/layout/fea/`). |
| A-7 | MAJOR | `templates/project.yaml:82,97-100`; `references/project-yaml.md:64-67`; `references/fab-dfm.md:10,14`; `references/pcb-layout-dfm.md:22-29`; `SKILL.md:278`; `references/schematic-phase.md:7,20-25` | Pre-layout paths survive in the shipped project.yaml and the references: `design/dfm_thresholds.json`, `design/<board>_board.yaml`, `design/placement.csv`, `design/sheets/*.yaml`, `out/dfm_items.json`, `out/dfm.json`, `out/<board>.xml`. There is no `design/` or `out/` folder in the layout. The smoke's own project uses `20-design/dfm_thresholds.json` and `30-board/layout/dfm_items.json`. This contradicts project-yaml.md §Layout ("Every path SKILL.md / the references / the templates spell is this layout"). | `$R/paths.py` -> 97 unresolved paths; old-root ones: design/ 6 distinct (9 refs to dfm_thresholds), out/ 11, docs/ 16. | Rewrite to `20-design/…` and `30-board/layout/…`. Add a smoke grep that fails on `` `design/`` / `` `out/`` in SKILL, references and templates. |
| A-8 | MAJOR | `templates/ci/README.md:13,33`; `SKILL.md:274`; `references/pitfalls.md:207` | The layout rewrite mangled non-paths: the CI container image became `30-board/kicad/kicad:10.0.5-full` (should be `kicad/kicad:10.0.5-full`), and the pitfall domain tags `kicad/drc` and `kicad/gen` became `30-board/kicad/drc` and `30-board/kicad/gen`. A user who pastes the ci/README sed recipe gets a broken image name in all three workflows. | `grep -rn "kicad/kicad" templates/ci` -> the two lines above. Pitfalls heading l.203 is `## kicad / drc / swig`. | Restore them, and add `kicad/kicad:` to the reorg tool's no-rewrite list. |
| A-9 | MAJOR | SPEC_ERRATA home: README:119 + `references/project-yaml.md:178` say `10-spec/SPEC_ERRATA.md`; `SKILL.md:410`, `references/release-and-cut.md:127`, `templates/REVIEW_HANDOFF.md:29`, `templates/20-design/arrival_checklist.yaml:48` say `10-spec/spec_sections/SPEC_ERRATA.md` | Two homes for one record. The copied file lands at `10-spec/SPEC_ERRATA.md`, but the generated arrival page points the technician at a path that does not exist. | `00-now/WHAT_TO_CHECK_ON_ARRIVAL.md`: `E-SPEC: SPEC errata E-rows (10-spec/spec_sections/SPEC_ERRATA.md)`; `ls 10-spec/spec_sections` -> absent. | Make it one path, and add a `paths.spec_errata` default. |
| A-10 | MAJOR | `SKILL.md:32-33` | The scaffold command as written globs `design/*.yaml` and names `design/VERIFY.md`, but the folder is `20-design/`. Under zsh the glob aborts; under bash `project.py scaffold` crashes with a traceback on the literal path. Either way nothing in `20-design/`, `60-orders/` or `10-spec/KICKOFF_ANSWERS.md` is scaffolded. | zsh: `no matches found: design/*.yaml` rc 1. bash: `FileNotFoundError: [Errno 2] No such file or directory: 'design/*.yaml'`. | Put the scaffold line into the README step 4 block with the real globs (`10-spec/*.md 20-design/*.{md,yaml} 60-orders/*.md 60-orders/quotes/*.yaml 90-log/*.md`). Make scaffold skip a missing file with a message. |
| A-11 | MAJOR | README "Install" / "Use in a new project" | README never names `project.py scaffold`. The step-4 block copies tagged templates and stops, and only SKILL §0 step 2 says to resolve the scope. A README-only user keeps every scope's tagged lines (`{{ee,both}}` text in GATES, project.yaml and the arrival yaml) and a GATES.md with three title lines. | `grep -n scaffold README.md` -> nothing. | Add the scaffold line (A-10) as the last line of the step-4 block. |
| A-12 | MAJOR | `references/project-yaml.md:197` vs `references/print-dfm.md:61`; `templates/production_cut.yaml:23` vs `paths.mech_record` | More drifted homes: the DFM-validation records are `40-case/dfm_validation/` in one file and `out/dfm_validation/` in another. The STL set of record is `40-case/*/parts/*.stl` (DEFAULTS) but `40-case/{case_tag}*/stl/*.stl` in the production-cut deliverable, and RENDERS.json sits at the set root although the layout puts renders in `pictures/`. | `$R/paths.py` output; the DEFAULTS dump in project.py. | Make every path a DEFAULTS key and reference keys, not spellings. |
| A-13 | MINOR | `scripts/stability.py:81` | `--selftest` without numpy is an uncaught `ModuleNotFoundError` traceback. print_dfm.py gives a clean message but exits 2, so the README step-3 loop is never all green without mesh libs, and nothing says which non-zero codes mean "skipped". | `.venv/bin/python scripts/stability.py --selftest` -> traceback; print_dfm -> rc 2 `missing numpy — install …`. | Use print_dfm's guard, and give the "libs absent" case one exit code that the loop and smoke treat as SKIP. |
| A-14 | MINOR | `scripts/collect_renders.py:16` | `SyntaxWarning: invalid escape sequence '\`'` on every import (Python 3.12+), printed four times in the smoke log. | Smoke tail below. | Use a raw docstring or drop the backslashes. |
| A-15 | MINOR | README:129 | The step-4 code fence is followed by a stray fragment, ```` ```   #  project.yaml before any reader runs) ````. It breaks the rendering, and the sentence it belongs to is lost. | `sed -n 129p README.md`. | Delete the fragment or restore the sentence. |
| A-16 | MINOR | README:62 | The repository map lists `80-reviews/` for the skill's reviews, but the skill repo has `docs/reviews/` (also the reorg rewrite). | `ls $R/skill/docs` -> `retro reviews superpowers`. | Change it to `docs/reviews/`. |
| A-17 | MINOR | `templates/project.yaml:89` | The comment says learnings, env, parts_verification and the rest "default to the docs/ layout". The defaults are now the 60-orders and 90-log folders. | Line text. | Change it to "the numbered layout". |
| A-18 | MINOR | `references/project-yaml.md:181`, `templates/60-orders/quotes/dfm_verdicts.yaml:13-17`, SKILL:343,395, GATES.md:28 | NAMES rule: "no date names a folder at the top of a tree", yet `60-orders/quotes/<date>/` is the only quotes structure (26 references; the smoke ships `quotes/2026-01-01/`). The layout block also lists non-targets (`coupons, board_dummy, dfm_validation, fea, board_mesh`) as "sets per print target". The dfm_verdicts example uses a set named `v1`. | The grep in item 3 below. | Either state the exception for frozen quote evidence in the rule itself, or name rounds (`quotes/<vendor>_r1/`, date inside). Call 40-case children "sets", not print targets. |
| A-19 | MINOR | README:116-128 vs SKILL:31-33 | The copy block is described twice and the descriptions differ. SKILL says PROCUREMENT is mech/both only and names `design/VERIFY.md`, while README copies `60-orders/*.md` (PROCUREMENT included) in every scope. | Side by side. | Keep the list in README only; SKILL points to it. |
| A-20 | NOTE | Cold reader (e) | Nothing on day 1 tells a technician where assembly lives. There are three future homes, `50-kits/<kit>/START_HERE.md`, `40-case/ASSEMBLY.md` (assembly_guide.steps_md) and `70-release/<rev>/ASSEMBLY_SOP.md` + `VISUAL_ASSEMBLY_GUIDE.md`, and no 00-now page. | Walk below. | Add a 00-now `HOW_TO_ASSEMBLE.md` pointer page, or make the five pages say where it will appear. |
| A-21 | NOTE | `templates/90-log/GATES.md:4` (both scope) | The approval-cell grammar mentions "(M1, M2)" although the both table has no M1/M2 rows. `10-spec/FINDINGS.md` and `60-orders/ORDER_<rev>.md` are named in the layout but have no template. | Scaffolded `$R/proj/90-log/GATES.md`. | Tag the phrase `{{mech}}`, and say who creates the two files. |
| A-22 | NOTE | `scripts/clone_gate.sh` | The clone dir name pads with underscores (`/tmp/hwfs_cg_ZTK4/proj____…`, about 100 characters), which looks broken in logs. | Adopt output. | Truncate the name instead of padding it. |

Item 6 (one home): drift points are A-3 (day-1 records: SKILL step 6 vs `gates.adopt`), A-7/A-12 (layout spelled in DEFAULTS + the project.yaml comment block +
project-yaml.md §Layout + inline in references), A-9 (SPEC_ERRATA), A-19 (copy block), and the venv package list, which appears four times
(README quick start ×2, README Install, SKILL §0 step 1). The toolchain-proof loop is in README step 3 and SKILL §0 step 5. The interpreter rule is said twice
inside SKILL §0 step 1.

Item 4 (scopes): **pass on folders and gate tables**. ee -> dirs `00-now 10-spec 20-design 30-board 60-orders 70-release 80-reviews 90-log` (no 40/50),
GATES title `G0 → G1 → G2 → board order → release`, rows `G0 G1 G2 Order (board) Release`. mech -> dirs without 30-board, title `G0 → M1 → M2 →
case order → release`, rows `G0 M1 M2 Case order Release`. both -> `G0 G1 G2 Order (board) Case order Release`. Residue: A-6, A-21, and ee `.gitignore`
carries `40-case/*/build/` (harmless). After A-2/A-3 workarounds, ee and mech day-1 adopt gates -> `adopt gates OK` (both carry A-4).

Item 1 day-1 verdict: **not green**. As shipped, a fresh both project fails adopt in this order: invalid YAML (expected until slots are filled),
`GATES REQUIRED` (A-2), `known_issues STALE` (closed by step 6), `now_pages STALE` (A-3), `arrival_checklist stale` (A-2/A-3). It goes green
(`clone gate OK … adopt gates OK`) only after uncommenting the arrival line and running `now_pages.py` + `arrival_checklist.py`, which no instruction says.
`kickoff --check` fails (45 problems) with dummy fills, which is expected.

## Cold-reader walk (`$R/proj`, both, folder names only)

1. `ls $R/proj` -> `00-now 10-spec 20-design 30-board 40-case 50-kits 60-orders 70-release 80-reviews 90-log`. The numbered names read well.
2. (a) where things stand -> `00-now/` -> **empty on day 1** (dead end: nothing tells me it is generated, or by what).
3. Fallback `90-log/` ("log" did not say "status") -> `90-log/STATUS.md` -> STATE NOW is all slots. Usable after filling.
4. (b) blocked on owner -> `90-log/BLOCKERS.md` (empty table) -> `90-log/GATES.md` (G0 pending) -> `90-log/DECISIONS.md`. Three files, no single answer.
5. After `now_pages.py`: `00-now/WHERE_THINGS_STAND.md` -> answers (a), but **wrongly says both orders are approved** (A-4).
6. `00-now/BLOCKED_ON_OWNER.md` -> answers (b) (arrival rows E-1, E-FIT; decisions "nothing").
7. (c) what to print -> `50-kits/` (empty) -> `40-case/` (empty) -> `00-now/WHAT_TO_PRINT.md` -> "nothing: no plate sidecar under `50-kits/<kit>/plates/`". Clear.
8. (d) what to order -> `60-orders/` -> `60-orders/PROCUREMENT.md` -> `00-now/WHAT_TO_ORDER.md` ("1 screw: … × …" from the template's example row). Clear.
9. (e) assembly for a technician -> `50-kits/` (empty) -> `40-case/` (empty) -> `70-release/` (only `reports/`) -> `00-now/` (no assembly page). **Dead end** (A-20).
10. `00-now/WHAT_TO_CHECK_ON_ARRIVAL.md` -> E-SPEC row points at `10-spec/spec_sections/SPEC_ERRATA.md`, which does not exist. **Dead end** (A-9); the file is at `10-spec/SPEC_ERRATA.md`.
11. Expected files not found: `10-spec/FINDINGS.md`, `60-orders/ORDER_rev0.md` (named by the layout, no template), and any `design/` or `out/` that the project.yaml `fab_dfm` block points at (A-7).

## Item 2/3 raw (abridged)
`$R/paths.py` (SKILL + references + templates, backticked roots; placeholders/globs/DEFAULTS/existing excluded) -> 97 paths in `$R/paths_out.txt`.
Most are artefacts created later (gen/*.py, 30-board/layout/erc.json, 80-reviews/G0_merged.md, ci/*) and are acceptable. The defects are the old-root ones (A-7, A-8, A-9, A-12).
Date folders: `grep -E '/(<date>|20\d\d-\d\d-\d\d)/'` -> `60-orders/quotes/<date>/` in cnc-enclosure:34, dfm-printed-enclosure:7,171,182,201, fab-dfm:36,
pcb-layout-dfm:216,225, pitfalls:264, release-and-cut:47, vendor-review:6,24,28, SKILL:343,395, GATES.md:28, RELEASE_NOTES.md:24, dfm_verdicts.yaml:13,17.
Hash folders: only inside `reorg:` examples (old side) and `40-case/dfm_validation/` (declared exception). Revisions are `rev0` everywhere else.

## Item 5 raw outputs (tail)

`scripts/jobs.sh -- smoke/run_smoke.sh` in `$R/skill` (as set up, no .git):
```
python: …/review_A/skill/.venv/bin/python
NOTE: mesh libraries absent in …/hwfs_smoke_4jET/smoke/.venv/bin/python — section 0d (print DFM on meshes) will be SKIPPED; install …
--- 0 printed-enclosure DFM contract: the reference carries the measured rules and the census gate selftests without mesh libraries
fatal: not a git repository (or any of the parent directories): .git
rc=1
```
Same tree after `git init; git add -A; git commit` (`$R/skill_git`):
```
clone gate OK (HEAD 1be1741)
adopt gates OK
--- 10 the owner's line in the Release row flips the banner; --check catches the stale report; gate_check --release wants the owner's commit
gate_check: release line `clear to build — owner, 2026-01-05, board 6180595f` — author ('smoke', 's@s') vs project.owner ['s@s', 'smoke'] -> OWNER
--- SMOKE OK — DRAFT report was …/smoke/70-release/reports/PCB_DESIGN_REPORT.md (RELEASED after the owner line); traceability census:
| NOT-INCLUDED | PENDING | VERIFIED |
| 1 | 1 | 5 |
…/scripts/collect_renders.py:16: SyntaxWarning: invalid escape sequence '\`'   (×4)
rc=0
```
Selftests in `$R/skill` (rc, script, last line):
```
0 arrival_checklist  0 assembly_guide  0 collect_renders  0 dfm_check  0 doc_voice_lint  0 erc_gate  0 gate_check  0 generic_lint
0 handoff_header  0 known_issues  0 now_pages  0 project  0 release_report  0 reorg_paths  0 scad_lint  0 skill_retro  0 step2stl
0 thin_wall_census  0 thin_wall_check  0 traceability  0 adopt_gates.sh  0 clone_gate.sh  0 jobs.sh
2 print_dfm.py :: print_dfm: missing numpy — install into the project venv: pip install numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml
1 stability.py :: ModuleNotFoundError: No module named 'numpy'
1 iteration_gate.sh :: iteration gate: no python with pyyaml found (project .venv, skill .venv, python3)
```
`evals/run_evals.py`: `evals: 18 with mechanical checks (0 failed check(s), 2 skipped), 0 manual`.
