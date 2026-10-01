# Blind review S — hw-from-spec skill v0.8.0 (2026-09-30)

Reviewer: Opus, blind (repo at tag `v0.8.0` + the checklist only; `docs/reviews/`, `docs/retro/` and git history not read).
Scratch: `/private/tmp/claude-502/.../scratchpad/` (throwaway projects `proj/{ee,mech,both}`, `cnt/{ee,mech,both}`, meshes, retro experiments).

## What was run

| Command | Result |
|---|---|
| `smoke/run_smoke.sh` (skill `.venv` with pyyaml + mesh libs) | rc 0, `SMOKE OK`, 25 s |
| `smoke/run_smoke.sh` in a fresh clone, skill `.venv` = pyyaml only (SKILL.md §0 step 1) | **rc 2** — `print_dfm: missing numpy` at section 0d |
| `smoke/run_smoke.sh` in a fresh clone, no skill `.venv` (README Quick start) | **rc 1** — `FAIL: python3 has no pyyaml` |
| `for s in scripts/*.py; do .venv/bin/python $s --selftest; done` + both `.sh --selftest` | 16 / 16 rc 0 |
| `scripts/print_dfm.py --selftest` | rc 0 |
| README steps 1b + 4 verbatim, per scope, in a temp git repo with the skill as a local submodule | `scripts/project.py scaffold` direct call **fails** (`ModuleNotFoundError: yaml`); via `.venv/bin/python` OK: ee 89 / mech 71 / both 22 lines dropped; 0 scope tags left |
| leftover `{{…}}` after scaffold | ee 112 lines / 119 distinct slots, mech 113 / 122, both 142 / 151 |
| trivially-filled slots → `known_issues.py`, `traceability.py`, `release_report.py`, commit, `scripts/adopt_gates.sh` | all three scopes green (DRAFT reports, clone gate OK) |
| `scripts/skill_retro.py` as SKILL §13 writes it, from a project root | **permission denied**; via python: **`MISSING <project>/SKILL.md`** (exit 2) |
| path / flag audit of every `scripts/…`, `references/…`, `templates/…`, `workflows/…` token in SKILL.md, README, references | all exist except `scripts/ci/project.env`, `scripts/ci/*.sh` (see F9) |
| fence pairs + table cell counts in README, SKILL, references | all even / consistent — README renders |

## Findings

### MAJOR

**F1 MAJOR — README Quick start fails at its own last line; SKILL §0 step 1 contradicts README on the skill venv.**
README.md:11-18 creates only the project `.venv`, then runs `vendor/hw-from-spec/smoke/run_smoke.sh`; the smoke looks only at `$SKILL/.venv`
(smoke/run_smoke.sh:10-11), falls back to `python3` → `FAIL: python3 has no pyyaml` (rc 1, reproduced on a fresh clone). SKILL.md:19 says the
skill venv carries pyyaml only; with that venv the smoke stops at `print_dfm: missing numpy` (rc 2, reproduced). README.md:20 says the mesh
libraries are "mech / both only", yet the smoke (which an ee user must run, SKILL §0 step 5) needs them.
Fix: make run_smoke.sh fall back to `$PWD/.venv` (the project venv) and skip §0d with a NOTE when the mesh stack is absent; make SKILL.md:19 say "pyyaml + the mesh libs" or drop the ee/mech split.

**F2 MAJOR — `scripts/project.py scaffold` (README.md:135, SKILL.md:32) fails as written: shebang `/usr/bin/env python3` + top-level `import yaml`.**
`scripts/project.py scaffold --scope ee …` → `ModuleNotFoundError: No module named 'yaml'` on a stock macOS/Homebrew python3. scaffold() needs no yaml.
Fix: write `.venv/bin/python scripts/project.py scaffold …` in both docs, and/or import yaml lazily inside `Project.__init__`.

**F3 MAJOR — five scripts SKILL.md tells the user to execute directly are not executable (git mode 100644).**
`scripts/skill_retro.py` (SKILL §13:396, README:159), `thin_wall_check.py --pinch` (SKILL:256), `thin_wall_census.py --target` (SKILL:216, 272),
`reorg_paths.py --apply` (SKILL:154), `assembly_guide.py` (SKILL:365) — `zsh: permission denied: scripts/skill_retro.py` (reproduced).
Fix: `git update-index --chmod=+x scripts/{assembly_guide,reorg_paths,skill_retro,thin_wall_census,thin_wall_check}.py`; add a smoke line asserting every `scripts/*` is 100755.

**F4 MAJOR — `skill_retro.py` default `--skill` resolves to the PROJECT through the `scripts` symlink.**
scripts/skill_retro.py (argparse): `default=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))` — abspath keeps the symlink, so from a
project the skill dir is the project root → `skill_retro: MISSING …/proj/ee/SKILL.md`, exit 2. print_dfm.py already uses `realpath` for exactly this
(its line ~83 comment). The smoke never runs retro through a symlinked install, so it is green.
Fix: `os.path.realpath(__file__)`; add the symlink case to the selftest.

**F5 MAJOR — the census and print-DFM gates check the records that exist, not the STL set of record: a body nobody censused passes both.**
Reproduced: `k/pre/stl/{plate2,plate08}.stl`, census + print_dfm run on plate2 only → `thin_wall_census.py --gate-dir k/pre/census` rc 0,
`print_dfm.py --gate k/pre/dfm` rc 0, while the 0.8 mm plate08 (FLAG under every MJF row) sits in the set. `pure_gate()` iterates `*.json`
only (thin_wall_census.py:178-205); `gate()` checks census→dfm, never STL→census (print_dfm.py:362-390). Also `--gate-dir` never re-reads
`print_targets.<t>.accepted`, so deleting an acceptance from project.yaml leaves the old pass standing, contradicting "re-asserted every run" (SKILL:120, 277).
Fix: both gates glob `paths.mech_record` (or the sibling `stl/`) and fail on any STL without a same-md5 record; the census gate re-matches `accepted_fails` against the current target's list.

**F6 MAJOR — `print_targets.<t>.dfm_process` is read by no script; a body checked against a laxer row passes the gate.**
`grep -n dfm_process scripts/*.py` → docstrings only. Reproduced: plate08 (0.8 mm) run with `--process protolabs_mjf_pa12` (wall_min 0.5) into
`h/jlc_mjf/dfm` → `PASS`, `--gate` rc 0, although the target (and kickoff C8a) names `jlc_mjf_pa12` (wall_min 1.0). The record also carries
`version` and `thresholds`, but the gate compares neither with the current rule-set VERSION or table.
Fix: `--gate` resolves the tag dir to its print target, requires `record.process == print_targets.<t>.dfm_process`, `record.version == VERSION`, and `record.thresholds == current row`.

**F7 MAJOR — `--open <tag>/<piece>=<decision id>` accepts any string: an unchecked waiver in a "no waiver field" tool.**
`print_dfm.py --gate g/pre/dfm --open pre/plate08=WHATEVER` → `OPEN WHATEVER … 0 problem(s)`, rc 0. SKILL.md:283 says "no waiver field".
Fix: require the id to be a row in `paths.decisions` whose status is OPEN (or an owner D row); print the row's topic; fail otherwise.

**F8 MAJOR — `print_dfm.py` PASSes non-watertight and multi-body meshes.**
`open.stl` (box with two faces deleted, `watertight False`) → PASS rc 0; `two.stl` (two disjoint plates) → PASS; the L-bracket made of two
overlapping un-unioned boxes (`watertight False`, 2 bodies) → PASS. A STEP→STL export from a user's own CAD (persona 2) is exactly this class.
The census has a bodies = 1 row; print_dfm, the advertised stand-alone entry point (README:22-32), has none.
Fix: add rule `M` (manifold): FLAG when `not mesh.is_watertight` or `len(mesh.split()) != 1` (or `winding_consistent` false); selftest it.

**F9 MAJOR — CI recipe writes into the skill submodule and the CI templates never init it.**
SKILL.md:54-55 and templates/ci/README.md:8,16 `mkdir -p scripts/ci; printf … > scripts/ci/project.env` — `scripts` is the symlink into
`vendor/hw-from-spec`, so the file lands untracked in the submodule and is absent in CI. All three workflows use `actions/checkout@v4` with no
`submodules: true` (templates/ci/*.yml:18-25) → `scripts` dangles, every gate and `cat scripts/ci/project.env` fails. The sed recipe also names
`scripts/ci/setup_linux.sh`, `nightly.sh`, `release_archive.sh`, which ship nowhere.
Fix: put `project.env` and the CI scripts under `ci/` (project-owned), add `submodules: recursive` to every checkout, or ship the three scripts.

**F10 MAJOR — the kickoff answers' machine-readable home does not exist: `kickoff:` is a string, `board:` is not a top-level key.**
references/kickoff-questionnaire.md:66-74 and SKILL.md:71 write answers to `kickoff.product_class`, `kickoff.enclosure.*`, `board.layers …`; the
template has `kickoff: docs/governance/KICKOFF_ANSWERS.md` (templates/project.yaml:10, references/project-yaml.md:15) — a scalar, so
`kickoff.product_class` cannot be written without changing the type, and no script reads any `kickoff.*` / `board.*` value. The answers land as prose only.
Fix: `kickoff: {answers: docs/governance/KICKOFF_ANSWERS.md, product_class: …, enclosure: {…}}` + a `board:` block in the template and project-yaml.md; have release_report print them.

**F11 MAJOR — "zero WARN, no waivers" is contradicted by the ERC rule, and the gates the bar names are opt-in comments.**
CLAUDE.md template rule 7 and GATES.md G1 row: "ERC zero errors (ERC_WAIVERS.md for the warnings)"; references/schematic-phase.md:54 "Warnings → fix,
or one row in ERC_WAIVERS.md" — a prose waiver table no script reads, versus SKILL.md:114-120 "no prose waivers". Separately, the census /
print_dfm / scad_lint / ERC / DRC gates are commented out in the day-1 `gates.adopt` (templates/project.yaml mech lines 100-105); nothing fails
when STLs or a board exist and the lines are still commented (adopt gates green on a scaffold with `print_targets` set and no census line).
Fix: a generated `erc_accept.yaml` checked like `dfm_accepted`; `adopt_gates.sh` fails when `paths.mech_record` matches files but no `--gate-dir` / `--gate` step is listed (same for `paths.board` + DRC).

**F12 MAJOR — gate approvals and the release line are unenforceable by script; "do not start the next phase's CAD" is prose.**
No script reads a G0/G1/G2/M1/M2 cell (`grep GATES scripts/*.py` → release_report only). release_report.py:116-117 flips to RELEASED on
`re.search(release_regex, GATES.md, re.I)` anywhere in the file — an agent's edit, a quoted chat line or a STATUS-style sentence all count; no
author check. Fix: a `scripts/gate_check.py G1` that generators call (exit 1 when the cell is empty), cells parsed per row, and the release line accepted only from a commit whose author matches `project.owner` in project.yaml.

**F13 MAJOR — mech scope has no route for a part that already exists as CAD (persona 2's bracket STEP).**
M1 (SKILL.md:80, GATES M1 row) requires "every body generated from `design/case.yaml`" via OpenSCAD; `paths.mesh_provenance` covers only the FIT
input. No reference says how to bring the owner's own STEP in as the body of record (STEP→STL conversion, units, canonical STL writer from
§8.1 item 3, generated-only exception row). eval 11 only covers a board STEP as fit input.
Fix: a "§8.0 imported body" path: decision row + `chain of record` exception (SKILL §2 already has the mechanism), a `scripts/step_to_stl.py` (cadquery/OCP) emitting the canonical STL + provenance.

### MINOR

**F14 MINOR — the "grep `{{` must print nothing" check at §0 step 2 cannot pass at that point.** SKILL.md:26 demands it right after copying, but
SPEC.md (18 tags), KICKOFF_ANSWERS (43 rows of `D-{{nn}}`), STATUS's PAUSE-POINT skeleton ("copy, number, fill", STATUS.md:16-21) and the
traceability `{{BOARD}}` paths can only be filled after the kickoff / after reading the spec (step 6: "Only now read the spec"). Fix: scope the grep to CLAUDE.md, project.yaml, governance records; check SPEC/KICKOFF at G0; mark skeleton blocks `<!-- skeleton -->` and exclude them.

**F15 MINOR — scope leaks after scaffold.** ee project: KICKOFF_ANSWERS keeps A4, C1–C9, D2/D3 rows with mech defaults (`{{tray + shell}}`, `{{screws + inserts}}`); CLAUDE.md rules 4 and 9 carry M1/M2, census, slicer, "printed enclosure census" and the layout block lists `case.yaml`, `gen/ case, fea`; GATES.md header + bar paragraph and the G0 row's "`project.yaml print_targets`"; production_cut.yaml MFG-003 "case incl. material rating". mech project: the reverse in GATES bar, KICKOFF B rows. eval 12 assertions 4/7 and eval 11 assertion 8 are partly violated by the shipped scaffold. Fix: tag those lines (`{{ee,both}}`, `{{mech,both}}`) and pre-fill out-of-scope KICKOFF rows as `n/a (scope)` via the tag.

**F16 MINOR — scaffold mangles its own explanatory comment.** templates/project.yaml:3 explains the tags with literal tags; after scaffold it reads
"a line ending in  /  /  belongs to those scopes only". Fix: escape the example (`{ {ee,both} }`) or exclude comment lines starting with `# Scope tags`.

**F17 MINOR — kickoff batches break their own limits.** Batch 5 = C5, C6, C7, C8, C8a = 5 questions (> "≤ 4 per call", SKILL:61); C10 is in no
batch and has no KICKOFF_ANSWERS row (the answer lands nowhere); the table has 11 batches (0–10) vs "up to ten"; A4 has 6 options + the
"accept every recommended" option, beyond AskUserQuestion's option limit; how "accept all" is presented (an option per question or a 5th question) is unspecified.
Fix: move C8a to batch 6 or merge into C8, add C10 to batch 5/6 and the answers template, cap options at 4 (collapse A4's alts), state "accept all" = first option of the batch's first question.

**F18 MINOR — SKILL.md §0 step 2's copy commands differ from README and are not runnable from the project root.** SKILL.md:27-32 uses `templates/…`
(exists only inside the skill), omits `templates/design/VERIFY.md` (G0 requires `docs/design/VERIFY.md`), and gives `SOFTWARE_ARCHITECTURE.md` / `PROCUREMENT.md` no destination. Fix: one `T=vendor/hw-from-spec/templates` block, identical to README:120-137.

**F19 MINOR — retro classifier does not survive a second project's conventions.** Reproduced with `ids.owner_prefix: OWN`: `read_decisions()` is
called with the default `"D"` (skill_retro.py run()), so §7 "owner topics not asked" = 0; a `* 2026-09-03 (dfm) …` learning (the costly one) is
silently skipped (`ENTRY` regex accepts only `- YYYY-MM-DD [tag]`) with no warning; `generalise()` hard-codes `CC|D|B` ids; `target_file()` maps only
the source project's domain tags (`jlc`, `mjf`, …); the DFM drift reads the hard-coded `design/dfm_processes.yaml`. Fix: pass `P.get("ids.*")`,
count and print unparsed bullet lines, read the table path from project.yaml. (Positive: after folding a generalised line into `references/fab-dfm.md`
the same entry re-classified CARRIED — the loop closes for well-formed input.)

**F20 MINOR — the retro is a candidate list; every fold is a hand edit.** SKILL.md:405 says so; README:159-163 / SKILL §13 heading ("the skill improves
with each project") read as automatic. On the source project it lists 88 NEW / 149 PARTIAL / 76 unasked owner topics — ~300 human judgements, and
§8 drift rows are not applied to `templates/design/dfm_processes.yaml` even when cited. Fix: an `--apply-dfm` that writes cited NEW/CHANGED rows, and README wording "drafts" not "folds".

**F21 MINOR — `print_dfm.py` exit code for a missing file is 1, docstring says 2.** `--process xometry_mjf_pa12 ~/nonexist.stl` → rc 1
("no such file"), docstring line "2 usage / configuration (missing file, …)"; a CI can't tell FLAG from typo. Fix: `sys.exit(2)`.

**F22 MINOR — mech M1 review role set is not in the workflow.** SKILL.md:213 "in mech scope the M1 round's role set = case_dfm + mechanical intent";
blind-deep-review.js:24-43 knows only `spec` | `board` (board includes electrical roles). Fix: add `ROLE_SET = 'mech'`.

**F23 MINOR — SKILL.md section order 1.2 before 1.1** (SKILL.md:113 / 122), and §1 says "the owner writes D rows" while §0.1 has the agent write
one owner D row per kickoff answer. Fix: renumber; say "the agent transcribes the owner's words into D rows, quoted".

### NOTE

**F24 NOTE — hand-edit count for a new project:** after scaffold, 112 / 113 / 142 lines holding 119 / 122 / 151 distinct `{{…}}` slots (ee /
mech / both); plus ~43 kickoff rows → 43 D rows → 43 traceability entries; ~45 workflow placeholders per review round (workflows/README.md:18-26);
11 CI placeholders + 3 missing scripts; the commented gate lines to uncomment per phase; the schematic generator `gen/build_sch.py` and every other
generator are project code (schematic-phase.md:3) — for an ee user, G1 starts with writing a KiCad schematic generator from scratch.

**F25 NOTE — FDM cantilevers are reported as "bridges".** A T-section with 18 mm free cantilevers on `home_fdm_04` → B "2 horizontal ceilings …
longer than bridge_max 10", INFO (supports = interior); a cantilever needs support, a bridge has two ends. Orientation = STL Z is assumed. Fix: split ceilings with one supported edge into an overhang row.

**F26 NOTE — residue of the source project in generic text.** `tools: kicad_cli: openscad` in mech scope (templates/project.yaml); `port_a / port_b`
sheets in the generic design-yaml example (schematic-phase.md §1); the retro report embeds absolute local paths (`Project /Users/…`) that a retro PR would publish.

**F27 NOTE — evals are not executed.** evals/evals.json (14 entries, 5–9 assertions) has no runner; the smoke greps rules but no eval is graded. The kickoff/scope evals 11/12 would currently fail on F15.

**F28 NOTE — pure gates trust the JSON.** Editing `"verdict": "FLAG"` → `"PASS"` in a print_dfm record passes `--gate` (reproduced); acceptable for a pure gate only if the clone gate or nightly re-runs the measure — the day-1 `gates.clone` does not.

## Persona verdicts

**(1) Cold EE-only user, KiCad 10.** Reaches G0 only after hitting three wrong instructions in the first hour: the Quick start's smoke fails (F1),
the scaffold command fails on system python (F2), and SKILL §0 step 2's copy block and grep check do not work as written (F14, F18). Each has a
work-around visible elsewhere in README (Install section, `.venv/bin/python`), and once past them the day-1 chain (known_issues → traceability →
release_report → adopt gates + clone gate) is genuinely green on a template-only ee project. The scaffold leaves enclosure text in CLAUDE.md, GATES
and 13 kickoff rows (F15), and the G0 review needs the Cursor agent CLI with two distinct models (or the weaker in-session fallback). Verdict: reachable, but not "without meeting a
wrong instruction"; fix F1/F2/F14/F18 and it is.

**(2) Mechanical-only user with a bracket STEP and a Bambu printer.** The stand-alone path (clone, venv, `print_dfm.py --process … bracket.stl`)
works and the output is clear — but it PASSes a non-watertight, two-body bracket (F8), and there is no STEP→STL step. The project path assumes the
skill generates every body from `case.yaml` in OpenSCAD; an owner's existing STEP has no route to M1 (F13). The Bambu/FDM guidance (home_fdm preset,
slicer facts, brand marks, print kit) is rich but entirely prose; no shipped script reads a slicer log. Verdict: usable as a DFM checker after F8;
not usable as a project flow for an existing part until F13.

**(3) Sceptical engineering manager.** The board fab-DFM bar is real (`dfm_check.py` enforces `fab_dfm.bar`, refdes-scoped acceptances with
evidence fields); the read-only guard and the clone gate are real and tested. Everything else in the bar is weaker than the text: ERC warnings are
waived in prose (F11), the mesh gates are opt-in comments and pass a body nobody checked (F5, F11), the process row is self-selected (F6), `--open`
is a free-text waiver (F7), acceptances need only a non-empty "evidence" string, and gate cells / the release line are honour-system (F12).
Verdict: "zero FAIL / zero WARN, no waivers" is enforceable for the board DFM mirror today; for ERC, prints and gates it is aspirational until F5–F7, F11, F12.

**(4) Skill maintainer.** `skill_retro.py` is a sound, deterministic candidate lister (it ran on the source project in 0.14 s: 358 learnings, 88 NEW,
76 unasked owner topics; a folded line re-classifies CARRIED), but it does not carry anything back by itself (F20), it cannot be run from a project
as documented (F3, F4), and a second project with another id prefix or bullet style loses owner topics and costly learnings silently (F19). Verdict:
the loop is a good input generator; "without hand-editing" is not met by design, and "two projects with different conventions" fails until F19.
