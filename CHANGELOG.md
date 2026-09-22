# CHANGELOG — hw-from-spec

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
