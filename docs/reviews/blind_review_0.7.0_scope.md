# Blind review 0.7.0 — project scope (ee / mech / both) — 2026-09-30

One reviewer sub-agent, fresh context, given only the repo path (at WIP commit 3299743) and two persona questions:
(1) a mechanical-only user with a board STEP and a bracket brief — can they run the skill end to end without meeting a board-only
instruction? (2) an EE-only user — do they ever get a case gate? Numbered findings only; no author reasoning shared. Dispositions
below; FIXED items landed in the 0.7.0 commit, ACCEPT items carry the reason.

| # | Sev | Finding (file) | Disposition |
|---|---|---|---|
| 1 | BLOCKER | `production_cut.yaml` manufacturing_spec untagged, `{pkg}` input a mech project can never have | FIXED — two rows: `{{ee,both}}` with the fab-package input, `{{mech}}` with `design/case.yaml` |
| 2 | MAJOR | assembly_sop / visual_assembly_guide (OpenSCAD-rendered, inserts / torque) reach the ee cut | FIXED — both rows `{{mech,both}}`; SKILL §10 bullet tagged `[mech, both]` |
| 3 | MAJOR | `handoff_header.py` prints `board md5 ? @ None` for the mech sidecar `{source, source_md5, tag}` | FIXED — "Fit input of record" row when `source` is present; asserted in the smoke's mech step |
| 4 | MAJOR | `release_report.py` identity: "Built at commit: MISSING (no package of record)" in every mech report | FIXED — package line skipped in mech scope; smoke asserts its absence |
| 5 | MAJOR | `ENV.md` `import pcbnew` line scaffolded into mech | FIXED — CAD rows `{{ee,both}}`, geometry / slicer CLI rows `{{mech,both}}` |
| 6 | MAJOR | `SPEC.md` R-M02 "agrees with case.yaml" and R-E01 "case window" in the ee scaffold | FIXED — cell reads `case.yaml (both) / the customer's fixture drawing (ee)`, cross-ref `R-M02` |
| 7 | MAJOR | README step 4 copies ERC_WAIVERS / SOFTWARE_ARCHITECTURE / PROCUREMENT for every scope, `--scope both` hard-coded | FIXED — scope-commented copy lines, `--scope "$A0"` |
| 8 | MAJOR | `production_cut.yaml` never copied or scaffolded by SKILL §0 step 2 / README | FIXED — `cp … templates/production_cut.yaml design/` and `design/*.yaml` in the scaffold list |
| 9 | MAJOR | smoke: no mech-scoped run of release_report / collect_renders / handoff_header; short-circuit bug in the ERC grep | FIXED — step 0c: a mech mini project (STL set, `{source…}` sidecar) asserts record id = STL set, collateral folder keyed on it, report identity, no fab-package line, fit-input row; ERC grep made independent |
| 10 | MINOR | SKILL §1.1 step 1 "ERC/DRC files" at every gate | FIXED — "the scope's checker outputs — ERC / DRC files [ee, both], census JSON + DFM_ROUND [mech, both]" |
| 11 | MINOR | SKILL §10 "Placed order = frozen package" untagged | FIXED — `[ee, both]` |
| 12 | MINOR | SKILL §10 vendor review "map every flag on the STLs of record" for ee | FIXED — "files of record (STLs [mech, both]; gerbers / BOM [ee, both])" |
| 13 | MINOR | SKILL §2 "after a copper change" / release-and-cut §3 "keyed on the board md5" | FIXED — "record of record (copper in ee / both, the STL set in mech)"; §3 keyed on `scripts/project.py record` |
| 14 | MINOR | CLAUDE.md layout: parts_seed.csv and `lib/ symbols/footprints` in mech | FIXED — tagged lines, mech variants (fit input; vendor STEPs / TDS) |
| 15 | MINOR | STATUS.md one line with package and case slots for every scope | FIXED — split into tagged lines |
| 16 | MINOR | REVIEW_HANDOFF.md files-of-record rows board+case in every scope, "board" severity wording | FIXED — rows tagged, a mech fit-input row, §6 / §7 generalised; SKILL §0 names it for the scaffold at the first review |
| 17 | MINOR | RELEASE_NOTES.md board / package / DRC / DFM lines untagged | FIXED — tagged; a `{{mech,both}}` census + vendor-DFM gate row |
| 18 | MINOR | technician / developer manuals (software track) required in the mech cut; incoming inspection "criteria file" | FIXED — manuals `{{ee,both}}`; inspection title names the criteria per scope |
| 19 | MINOR | `case-pipeline.md` "Board mesh of record" only knows the CAD export; `out/<board>/` path level | PARTLY — a "fit input of record (mech)" paragraph added (import, sidecar, [K] = KNOWN_ISSUES item) and the `<board>/` level called out as absent in mech. ACCEPT the path spelling in `project-yaml.md` §gates and `CENSUS_GATE_ROWS.md`: the source project's layout, documented as such; changing it is a re-layout of the worked example, not a scope defect |
| 20 | MINOR | GATES.md header sentence lacks the M1 / M2 cell form | FIXED — "case version + record md5-8 (M1, M2)" |
| 21 | MINOR | evals 11 / 12 would not catch 1, 2, 5, 18 | FIXED — one assertion added to each |
| 22 | NIT | CHANGELOG cites this file before it existed | FIXED — this file |
| 23 | NIT | README quick start installs the mesh stack for every scope | FIXED — one line: mesh libraries serve mech / both (the install line itself stays, the smoke greps it) |

Verdict after the fixes: a mech-only user scaffolds with `--scope mech` and meets no KiCad / ERC / fab-package / board-md5 instruction that the
text does not mark `[ee, both]`; an ee-only user gets no case gate, print target, census or case deliverable. Residual: `<board>/` in two
worked-example paths (19), documented.
