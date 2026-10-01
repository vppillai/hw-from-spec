# AUDIT 0.10.0 — the whole skill read once (2026-09-30, maintainer + two read-only auditors)

Scope: every file of the repo at `f04cfe8` (the 0.10.0 retro commit). Method: one auditor read `scripts/*` + `evals/run_evals.py` and RAN every
`--help` / `--selftest`; one read `templates/**`, `evals/evals.json`, `workflows/*`, `smoke/*` and RAN the smoke; the maintainer read
`SKILL.md`, `README.md`, `CHANGELOG.md`, every `references/*.md` and wrote `scripts/doc_voice_lint.py` for the owner's rule ("a comprehensive
skill, not a changelog"). Findings carry `file:line` at the audited commit; dispositions are in §9 (filled after the fixes).

## 1. One home per rule — duplicated or contradictory text across SKILL.md / references

| # | Where (copies) | Finding | Fix |
|---|---|---|---|
| D1 | `SKILL.md:294-326` (§8.1 item 1, 34 lines) vs `references/dfm-printed-enclosure.md:101-136` (§2) vs `references/print-dfm.md:11-47` vs `references/case-pipeline.md:63-78` | the census rules (gate − 0.05, wall / wedge by angle, opposing faces, samples ∝ area, noise floor, accepted list) and the print-DFM rule list are spelled out four times | SKILL §8.1 item 1 → the commands + one pointer per mechanism; case-pipeline §Census → pointer to dfm-printed-enclosure §2 |
| D2 | `SKILL.md:337-348` (§8.1 item 4) vs `references/dfm-printed-enclosure.md:160-211` (§7, §7.1) vs `references/vendor-review.md:52-77` (§4) vs `templates/DFM_ROUND.md:8-12` | the quote-page procedure (one STL per session, API verdict at parseStatus 2, flag computed at upload, previewUrl, length dependence, probes) is written four times with drifting detail | home = dfm-printed-enclosure §7 / §7.1; SKILL item 4 → three lines; vendor-review §4 → the ORDER-page facts only + pointer; DFM_ROUND keeps the record fields |
| D3 | `SKILL.md:278-280` vs `references/case-pipeline.md:80-91` vs `references/vendor-review.md:43-50` (§3) | point contacts (`--pinch`, web discs clipped to the closing, the two census rows) written three times | home = case-pipeline §Point contacts; vendor-review §3 → two lines + pointer |
| D4 | `references/fab-dfm.md:45-53` (§4 Panel) vs `references/pcb-layout-dfm.md:178-185` (§13) | panel rules (≥ 70 mm, rails on the long edges, mouse bites, fills, panel-zip DFM) duplicated | home = pcb-layout-dfm §13; fab-dfm §4 → the panel-zip DFM note + pointer |
| D5 | `references/fab-dfm.md:77-90` (§6) vs `references/dfm-printed-enclosure.md` §1 / §11 vs `references/cnc-enclosure.md` §3 | print-service / CNC quote facts repeated | fab-dfm §6 → pointers (the FDM / SLA size refusals stay as the fab-form facts) |
| D6 | `SKILL.md:210-244` (§5) vs `references/agent-ops.md:47-71` (§4) vs `workflows/README.md:44-52` | the review protocol in three places; after 0.10.0 both SKILL §5 and agent-ops §4 carry the full verifier text | SKILL §5 = the procedure (home); agent-ops §4 keeps the mechanics (CLI, packet ceiling, pairing) and points at §5 for the classes |
| D7 | `SKILL.md:349-361` (§8.1 item 5) vs `references/dfm-printed-enclosure.md:221-275` (§8) vs `references/print-kit.md` | the home-FDM preset rules (walls 1.6, legends, coupons, dummies, slicer projects, kit) in SKILL at reference length | SKILL item 5 → the preset's gates + pointers |
| D8 | `references/agent-ops.md:74-76` vs `SKILL.md:403` vs `workflows/README.md` | the per-call ceiling is stated once (§5) and pointed at — OK, kept | — |

## 2. Stale mechanism mentions, wrong counts, history voice

| # | file:line | Finding | Fix |
|---|---|---|---|
| S1 | `templates/CENSUS_GATE_ROWS.md:32` | the adopt-list line names only `thin_wall_census.py --gate-dir`; `project.py gates-required` demands `print_dfm.py --gate` too | add the second line |
| S2 | `templates/GATES.md:28,30` (M1, Case order) | prerequisites list census / pinch / slicer / vendor DFM, not `print_dfm.py --gate` PASS, although the bar paragraph requires it | add |
| S3 | `templates/RELEASE_NOTES.md:24` | gates table has a census row and no print-DFM row | add the row |
| S4 | `templates/DFM_ROUND.md:32` | §3 "our own numbers" has no print_dfm verdict column | add |
| S5 | `workflows/blind-deep-review.js:38` | the `case_dfm` verifier "re-runs thin_wall_census" only | + `print_dfm.py --process` |
| S6 | `templates/G1/EVIDENCE.md:8` | "ERC {{0 errors / n waived}}" predates `erc_accept.yaml` | "n accepted (design/erc_accept.yaml)" |
| S7 | `templates/CLAUDE.md:48-49` vs `templates/project.yaml:75-79` | CLAUDE names a slicer CLI slot; `tools:` has no slicer key | add `slicer:` [mech, both] |
| S8 | `evals/evals.json:140` | eval 8 says "nine batches"; the questionnaire has twelve | fixed in the retro commit |
| S9 | `smoke/run_smoke.sh:67` | hard-coded `^version: 0.9.2` | derived from SKILL.md (retro commit) |
| S10 | `smoke/project.yaml:6` | fixture `skill.version: 0.5.0` reads stale | `version: smoke` |
| S11 | `smoke/run_smoke.sh:7` | `mktemp -d /tmp/…` ignores `$TMPDIR` | fixed in the retro commit |
| S12 | `evals/run_evals.py:18` | `--python .venv/bin/python` (relative) fails every check with rc 127 (checks run with cwd = temp dir) | `os.path.abspath` |
| S13 | `references/dfm-printed-enclosure.md:281,283` | `topmost` appears only in the correct negative form — OK | — |
| S14 | README.md, templates, SKILL.md, references | `ERC_WAIVERS` — no stale use (only the negative smoke grep) — OK | — |
| S15 | `README.md:7-9,66,69` | version prose ("0.9.1 mirrors…", "0.9.0 closed…"), hand-typed counts (19 tools, fourteen evals) | one version line; counts removed or derived |
| S16 | `scripts/doc_voice_lint.py` run at `f04cfe8`: **47 hits in 58 files** — `references/dfm-printed-enclosure.md` 21 (blind-review ids `(B-15)` … inside rules, "the old rule", a `(was "SANITY …")` parenthetical), `pitfalls.md` 6 (version numbers in headings), `templates/REVIEW_HANDOFF.md` 2 / `DFM_ROUND.md` 2 ("this round"), `SKILL.md` 2, `fab-dfm.md` 2, one each in `README.md`, `agent-ops.md`, `fdm-print-optimisation.md`, `kickoff-questionnaire.md`, `print-kit.md`, `project-yaml.md`, `templates/CLAUDE.md`, `DECISIONS.md`, `project.yaml`, `design/dfm_processes.yaml`, `design/arrival_checklist.yaml`, `ci/README.md` | the skill narrates its own history inside rules | every hit rewritten as the standing rule; the lint runs in the smoke |

## 3. Source-project residue in templates / workflows / scripts

| # | file:line | Finding | Fix |
|---|---|---|---|
| R1 | `templates/project.yaml:112` | `# e.g. "Bambu Lab P2S, …"` — the owner's printer; the smoke's leak guard was case-sensitive and did not scan `templates/design` | `<printer model>`; guard widened (retro commit) |
| R2 | `templates/project.yaml:92,99` | "(JLC3DP 2026-09-28: 1.2)", "(147)" as THE reference values | "read on checker_date (e.g. …)", "the size your first vendor round calibrated at" |
| R3 | `templates/DFM_ROUND.md:8-11,15,17` | `{{VENDOR}}` header, JLC3DP API field names hard-coded in the body | `{{VERDICT_API}}` slot with the JLC3DP worked example in one parenthesis; the smoke grep follows |
| R4 | `templates/VENDOR_REVIEW_RECORD.md:35,42` | "Replace File → upload → Confirm", "audit failed" mails = JLC3DP UI terms under `{{VENDOR}}` | `{{VENDOR_REPLACE_ACTION}}` (e.g. …) |
| R5 | `templates/GATES.md:16,27`, `templates/CLAUDE.md:40`, `templates/project.yaml:85`, `SKILL.md:146,271`, `references/fab-dfm.md:32`, `smoke/run_smoke.sh:55` | "0 Danger / 0 Warning" = JLCPCB's grade names used as THE vocabulary | "0 open at either of the fab's two grades (JLC: Danger / Warning)" |
| R6 | `templates/KICKOFF_ANSWERS.md:33` | recommended `{{jlc_mjf_pa12 + home_fdm_04}}` presupposes JLC | `{{<vendor row> + home_fdm_04}}` |
| R7 | `templates/CENSUS_GATE_ROWS.md:32`, `templates/ci/README.md:17,41` | `out/<board>/mechanical/…` — the source layout; the template record path is `out/mechanical/case/*/stl/*.stl` | drop `<board>/` |
| R8 | `templates/ci/{pr-check,nightly,release}.yml`, `templates/ci/README.md:13,33`, `templates/ENV.md:6` | KiCad presupposed as THE CAD (`{{PROJECT_KICAD_IMAGE}}`, `import pcbnew`) while CLAUDE / project.yaml are CAD-neutral | `{{PROJECT_CAD_IMAGE}}`; ENV row "the CAD's module import" |
| R9 | `templates/project.yaml:64-65`, `templates/design/traceability.yaml:11`, `templates/REVIEW_HANDOFF.md:18` | `kicad/{{BOARD}}/…` while CLAUDE says `<cad>/<board>/` | documented: `kicad/` is the CAD dir name, rename for another CAD (the key names are historical, as `tools:` says) |
| R10 | `templates/design/dfm_processes.yaml:38,45,54` | `[K] JLC3DP engineer mail 2026-09-22` — a private mail no project can re-fetch | tag `[K source-project mail, not reproducible]` |
| R11 | `workflows/silk-audit-verify.js:25,31` | the source board's font / via numbers and silk feature set hard-coded in the prompt | `{{SILK_METRICS}}` placeholder; feature set folded into `{{SILK_DESIGN_INTENT}}` |
| R12 | `templates/SPEC.md:18` | `{{USB-C 5 V 3 A}}` example | `{{interface, e.g. power in}}` |
| R13 | `templates/project.yaml:78` vs `templates/CLAUDE.md:48`, `templates/ENV.md:7` | the mech geometry CLI slot is `{{GEOMETRY_CLI_PATH}}` in one file and `{{CAD_CLI_PATH}}` in two; in `both` scope ENV has two tools in one slot | `{{GEOMETRY_CLI_PATH}}` everywhere |
| R14 | `templates/production_cut.yaml:13` | `{{PRODUCT}}` used nowhere else | `{{PROJECT}}` |
| R15 | `scripts/project.py:187` `SLOT_DEFAULT` | `production_cut.yaml` (copied to `design/`) is covered by `design`; `.github/workflows` / `gen/workflows` are not — placeholders there are the CI README's own grep | documented in `slots` help |
| R16 | `smoke/run_smoke.sh:219` | the yaml-validity probe's slot regex differs from `project.py` SLOT | aligned (retro commit) |
| R17 | `templates/project.yaml:97` vs `templates/design/dfm_processes.yaml:49` | MJF tolerance "±0.3 or ±0.3 %" vs "+/-0.3 mm or 0.4 %" | one cited figure |
| R18 | `scripts/release_report.py:178,180` | reads `dfm.report` (the alias) while `dfm_check.py` writes `fab_dfm.report`: a project with only `fab_dfm:` gets `MISSING` | read `fab_dfm.report` first |
| R19 | `scripts/traceability.py:73` | default `scratch_links: ["lib"]` = the source layout | `[]` |
| R20 | `scripts/print_dfm.py:10,187,354,390,404` | review ids / source episodes in code comments and in a row printed to every user ("the construction that cracked on a 141 mm lip"); `3.5 mm [V Hubs]` as a code fallback | generic wording; the fallback reads the row |
| R21 | `scripts/project.py:221`, `scripts/reorg_paths.py:45` | path defaults hard-coded in code instead of `DEFAULTS["paths"]` | moved |
| R22 | `scripts/skill_retro.py:391-392` | fixture rows quote source-project decisions (magnets, purple badge) | neutral text |
| R23 | `scripts/print_dfm.py:744-857` | the selftest names template rows (`jlc_mjf_pa12`, …) | ACCEPTED — a data table the selftest tests against; renaming a row is a selftest change by design |

## 4. Scripts — dead code, duplicated helpers, CLI conventions, docstring vs behaviour

Dead code (9): `thin_wall_census.py:50 first_hit_beyond` (unused there — now the shared copy `thin_wall_check` imports), `handoff_header.py:12 import re`,
`reorg_paths.py:25 import hashlib`, `step2stl.py:16-17 HERE + sys.path.insert`, `arrival_checklist.py:118-119` (unused `P`, chdir inside an assert),
`reorg_paths.py:204 bad_lines = []` (overwritten), `collect_renders.py:121` no-op write, `skill_retro.py:79-82` re-implements `project.split_row`,
`print_dfm.py:721 rim_profile` / `thin_wall_check.py:34 histogram` reached only from selftests (kept, cosmetic).

Duplicated helpers (10 groups, ≈ 180 gross / 100–120 net lines): md5-of-file ×10, decision-table rows + status normalisation ×8, `need()` ×2,
`first_hit_beyond / histogram / union-find clustering` (`thin_wall_check` ≡ `thin_wall_census`), walk-up-to-project.yaml ×4, `cut()` ×2, `git()` ×3,
the `--check` stale-compare block ×6, argparse boilerplate ×13. **Verdict: no new shared module** (the net saving is under the 100-line bar once the
shared definitions are written). Folds done where a copy already exists: `thin_wall_check` imports the four helpers from `thin_wall_census`;
`skill_retro` uses `project.split_row`.

CLI conventions (measured): every script answers `--help` read-only except the two shell gates (an unknown flag ran the gates); `--selftest` on all
20 scripts, total **59 s** (print_dfm 47 s = 80 %; after 0.10.0's six new constructs 54 s); exit codes: `project.py:70 Project.find` exits 1 on a
missing project.yaml (should be 2 — fixes ten scripts at once), `print_dfm.py` `sys.exit(str)` at :136,:341,:344,:667,:674 exits 1 where the docstring
says 2, `thin_wall_check.py:108 need()` exits 1 (docstring: 2), `thin_wall_census.py:251,:493` usage → 1, `known_issues.py:116` / `traceability.py:204` /
`dfm_check.py:144` / `assembly_guide.py:77,84` missing input → 1 (should be 2), `handoff_header.py:101 nargs="*"` with a one-argument `header()`,
`collect_renders.py:138` argparse without a description, `evals/run_evals.py` has no `--selftest`. `skill_retro.py` with no arguments writes a report
into the skill repo (documented, kept — the report is the retro's artefact). Docstring vs behaviour (6): `run_evals.py:6` claims a `.venv` fallback
it does not have; `print_dfm.py:75` exit-code claim; `print_dfm.py:54,891` an explicit nonexistent `--processes PATH` silently falls back to the
template; `thin_wall_check.py:101`; `project.py:18` documents `kickoff --check` but dispatches on `kickoff` alone; `handoff_header.py:4` `[PKG_DIR]`.

## 5. Evals

8 mechanical / 6 manual at `6d93d54`; after the retro commit **16 / 0 manual** (every eval carries a `checks:` list; the agent-behaviour assertions stay
for a human after an agent run, as documented in `run_evals.py`). Eval 8's batch count corrected. `run_evals.py --python` relative-path bug (S12).

## 6. Smoke

`smoke/run_smoke.sh`: **OK, exit 0, 2 min 00 s wall** at `6d93d54` (section 0d ran with the mesh libraries); after the retro commit 2 min 05 s. Negative
cases proven: 31 (listed in the auditor's report; unchanged). Dependencies outside the repo: the caller's `.venv`, `python3`, git, sed, awk, tar — no
network, no path into the source project.

## 7. Workflows

`README.md:23` documents 5 of 14 `{{BRIEF_*}}` slots (board set: POWER DIGITAL LAYOUT FAB SILK SOFTWARE COHERENCE GATES; delta: DOCS undocumented);
`:27` lists `{{RECROP_DIR}}` which no template uses; `:4` the leftover-brace grep would flag a GitHub `${{ }}` expression. Duplicated prompt text
(wrapper contract ×4, blindness clause ×2, `FINDINGS` / `VERDICT` schemas ×2, `pair()` ×2, `verify()` ×2) — the prompt text must stay inline per file
(each template runs alone); the README gains the two shared paragraphs and the files point at them.

## 8. README / CHANGELOG / docs folders

README 183 lines with version prose and typed counts; CHANGELOG 556 lines, nine entries a reader must replay to know the current state, plus the
retro's UNRELEASED stub; `docs/reviews/` (7 files) and `docs/retro/` (4 files) without an index.

## 9. Disposition (after the fixes, commit "0.10.0 audit")

| Item | Result |
|---|---|
| D1–D7 | one home each: SKILL.md §8.1 items 1 / 4 / 5 rewritten as commands + pointers (SKILL 500 → 473 lines while gaining §10.1 and the resource paragraph); `vendor-review.md` §3 / §4, `fab-dfm.md` §4 / §6, `case-pipeline.md` §Census → pointers; D8 kept |
| S1–S7, S10, S12 | fixed (CENSUS_GATE_ROWS both adopt lines, GATES M1 / Case order, RELEASE_NOTES row, DFM_ROUND column, `case_dfm` verifier, G1/EVIDENCE wording, `tools.slicer`, smoke fixture version, `run_evals --python` absolutised) |
| S8, S9, S11 | fixed in the retro commit |
| S16 voice | `scripts/doc_voice_lint.py`: **47 → 0** hits (58 files); the lint runs in the smoke (step 0c) |
| generic (owner rule, added during the audit) | `scripts/generic_lint.py` + `generic_lint_terms.yaml`: **308 raw → 181 scoped → 0** hits (105 files; the raw count included fixture ids in selftests / smoke / template seed rows, which use the id scheme by design and are scoped out); pitfalls.md's 112 evidence pointers replaced by dates; `dfm-printed-enclosure.md` keeps ONE fenced worked-example block (§7.1); the lint runs in the smoke |
| R1–R14, R17–R22 | fixed; R9 / R15 documented in place; R23 accepted |
| Scripts | dead code: 8 of 9 removed (the two selftest-only helpers kept); folds: `thin_wall_check` imports `first_hit_beyond / histogram / grid_groups / need` from `thin_wall_census` (−43 lines), `skill_retro` uses `project.split_row`, `decision_status` shared from `project.py` (erc_gate + traceability); CLI: `Project.find` exits 2, every usage / missing-input `sys.exit(str)` → print + 2 (print_dfm ×5, census ×3, traceability, known_issues, dfm_check, assembly_guide ×2), `--processes PATH` must exist, `handoff_header nargs="?"`, `collect_renders` description, `adopt_gates.sh` / `clone_gate.sh` answer `-h` and refuse unknown flags with 2, `run_evals.py --selftest` (schema) + absolute `--python`, `kickoff --check` parsed, defaults `kickoff_answers` / `reorg_rewrites` in `DEFAULTS`, `release_report` reads `fab_dfm.report` first, `scratch_links` `[]`, source episodes out of `print_dfm` strings |
| Evals | 16 / 16 with mechanical checks (2 / 3 / 4 / 5 / 7 / 10 gained them; 15 / 16 new); runtime of `run_evals.py` ≈ 70 s (print_dfm selftest twice: eval 14 + the smoke's own run) |
| Smoke | OK; 2 min 05 s before the audit, **2 min 27 s** after it (the two lints and the arrival-checklist step included); `smoke/README.md` states the runtime |
| Workflows | README documents all 14 `{{BRIEF_*}}` slots, drops `{{RECROP_DIR}}`, gains `{{SILK_METRICS}}` and the two shared paragraphs (wrapper contract, blindness clause); the prompt text stays inline per template by design |
| README / CHANGELOG / docs | README 183 → 169 lines, one version line, no counts; CHANGELOG 556 → 619 lines (the **Current state** section + the 0.10.0 entry; the nine earlier entries kept verbatim as history); `docs/reviews/INDEX.md`, `docs/retro/INDEX.md` |

Line counts (before → after the audit fixes): SKILL.md 500 → 473 · README 183 → 169 · references 2586 → 2561 (18 files; `fdm-print-optimisation.md` +57
is in both) · templates .md 677 → 679 · templates yaml / ci 697 → 698 (+Makefile) · scripts 5185 → 5317 (24 files; +`generic_lint.py` 93, +terms yaml 64,
+`doc_voice_lint.py` 89; the audited scripts themselves −36) · evals 434 → 446 · workflows 279 → 288 · smoke 406 → 409 · docs 1238 → 1386 (+this file, +two indexes).
