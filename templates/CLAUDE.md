# CLAUDE.md — {{PROJECT}} ({{ONE_LINE_DESCRIPTION}})

You are building a hardware project of scope **{{SCOPE}}** ({{SUMMARY}}; `project.yaml project.scope`, kickoff A0) with {{CAD_TOOL}} from a
written specification, for fabrication and assembly at {{FAB}}. Humans review at gates. Read `10-spec/SPEC.md`, `90-log/STATUS.md`, `90-log/DECISIONS.md` before doing anything. The process is the
`hw-from-spec` skill (installed at `{{SKILL_PATH}}`); `project.yaml` carries every project constant. The owner's kickoff answers
(`10-spec/KICKOFF_ANSWERS.md`, D rows) are decisions of record: do not re-ask them, do not deviate silently (rule 2).

## Non-negotiable rules
1. **Never invent a fab or distributor part number** (electronics, and hardware: inserts, magnets, feet, screws). A number enters the BOM only after
   a fetch of its live page in this session confirms MPN, package and stock. Record every check in `60-orders/PARTS_VERIFICATION.md` (date, URL,
   stock, class). Tags: [V] verified, [K] known-unverified ([K owner-read] when the owner read a page we could not fetch), [S] select-by-parameter.
2. **Never change a specified value, part, topology or pin assignment silently.** Write the proposal to `90-log/DECISIONS.md` with the reason, mark it
   OPEN, ask the owner. Apply only after approval (or when the spec delegates the choice); an operating gate may ship as an optional flag that warns.
3. **Every VERIFY item is closed by reading the primary datasheet** before the part is drawn. A VERIFY item is a spec value or claim that rests
   on a datasheet or standard nobody has read yet (definition: skill `SKILL.md` §4); they are listed in 10-spec/SPEC.md (tag `VERIFY`) or `20-design/VERIFY.md`,
   and closed by a `10-spec/datasheet_notes/<part>.md` row (page/section) or a `90-log/BLOCKERS.md` row.
4. **Stop at gates.** The gate table is `90-log/GATES.md` (G0 SPEC → G1 schematic → G2 layout → board order), one review round before each. {{ee}}
4. **Stop at gates.** The gate table is `90-log/GATES.md` (G0 mechanical spec → M1 geometry → M2 first article → case order), one review round before each. {{mech}}
4. **Stop at gates.** The gate table is `90-log/GATES.md` (G0 → G1 → G2 → board order + case order), one review round before each. {{both}}
   Do not start the next phase's CAD before the owner writes the approval into `90-log/GATES.md` — a generator for the next phase calls
   `scripts/gate_check.py <gate>` and refuses while it says NOT approved. **Agents never write approval cells or the release line** — they ask (skill
   `SKILL.md` §1.1) and wait; a chat approval is quoted verbatim under the table, the cell stays the owner's. Never quote the release phrase in prose.
5. **Everything is generated, nothing is hand-edited.** CAD files, reports and indexes come from `gen/` scripts reading `20-design/*.yaml`. A review
   finding changes the YAML or the generator, then regenerates. Every generator has `--check` and `--selftest`. Exceptions are logged decision rows
   with a chain-of-record table. Commit after every meaningful step with a descriptive message and explicit paths.
6. **{{SHEET_AND_REFDES_CONVENTION}}** (e.g. one generated sheet file per instance; refdes = sheet × 100 + n). {{ee,both}}
6. **{{GEOMETRY_CONVENTION}}** (e.g. one module per piece, presets `base + overrides` deep-merged, a version key per preset, canonical STL export). {{mech}}
7. **Validate after every generation:** ERC/DRC via the CAD CLI with all severities, zero errors (`references/schematic-phase.md` §2 has the {{ee,both}}
   command); `scripts/erc_gate.py 30-board/layout/erc.json` green — a warning passes only through an entry of `20-design/erc_accept.yaml` naming its {{ee,both}}
   decision row (no prose waivers; a GUI exclusion is a hidden waiver and fails). {{ee,both}}
7. **Validate after every generation:** census `--gate-dir` 0 unaccepted FAIL on every body of every preset, `print_dfm.py --process <row>` PASS on {{mech}}
   every body before any upload (`--gate` in the adopt list; a vendor verdict → `dfm_verdicts.yaml` → `--validate`, a RULE DEFECT fixes the rule), {{mech}}
   `thin_wall_check.py --pinch` on every mark-shaped body, `scad_lint.py` on every generated SCAD, slicer log 0 warnings, every face rendered and {{mech}}
   looked at (`references/dfm-printed-enclosure.md`, `references/print-dfm.md`). {{mech}}
8. **Blind reviews are really blind.** Reviewers get the frozen worktree and the hand-off only — never each other's output, never the author's
   reasoning. Verify BLOCKER/MAJOR adversarially, merge in `80-reviews/`.
9. **Fab constraints are hard:** {{FAB_CONSTRAINTS}}. **The manufacturability bar is zero / zero / no waivers** (owner row {{D-BAR}}), enforced by scripts:
   board — assembly sides, minimum package, link parts, excluded package families, parts on the verified list, fab code field on every fitted part, {{ee,both}}
   DNP marked and excluded from BOM/CPL, the fab's DFM checker mirrored in-repo (`20-design/dfm_thresholds.json`, `scripts/dfm_check.py`); DRC 0 errors / {{ee,both}}
   0 warnings and fab DFM 0 open at either of the fab's grades unless a dated `dfm_accepted` entry with vendor evidence (`references/pcb-layout-dfm.md`). {{ee,both}}
   printed enclosure — wall / void / red gates, tolerance and rating per print target (`project.yaml print_targets`, never in a script); census 0 {{mech,both}}
   unaccepted FAIL, `print_dfm.py` PASS, slicer log clean, vendor checker no flag by API read; CNC — vendor DFM clean (`references/dfm-printed-enclosure.md`). {{mech,both}}
10. **Say what you don't know.** If a datasheet, drawing or page cannot be fetched, mark the item BLOCKED in `90-log/BLOCKERS.md` and continue elsewhere.
11. **Capture learnings.** Before your final commit, append every non-obvious learning as a dated, domain-tagged line to `90-log/LEARNINGS_LOG.md`.

## Environment (verify on first run, record in 90-log/ENV.md)
- CAD CLI: `{{CAD_CLI_PATH}}`; CAD Python: `{{CAD_PYTHON_PATH}}`; project venv `.venv` (Python ≥ 3.11) with {{VENV_PACKAGES}}. {{ee,both}}
- Geometry CLI: `{{GEOMETRY_CLI_PATH}}` (e.g. openscad); slicer CLI: `{{SLICER_CLI_PATH}}`; project venv `.venv` (Python ≥ 3.11) with {{VENV_PACKAGES}}. {{mech}}
- All tool paths live in `project.yaml tools:`; generators read them from there (`scripts/project.py`), never hard-code them.
- Heavy tools (geometry kernel, slicer, renderer, FEA, the record round) run through `scripts/jobs.sh -- <cmd>` (one pool per machine, sized from
  the host; `make <target>`), never directly — the "Agent operations" block below (`references/agent-ops.md` §8).

## Agent operations
- **Heavy jobs only via `scripts/jobs.sh`** (geometry kernel, slicer, headless browser, chains, FEA, `make check`): slot pool = {{JOBS_POOL}}
  (cores // 4), memory floor {{MIN_FREE_GB}} GB, load gate = cores, `nice`; the generators and the Makefile route through it — never a bare
  geometry / slicer / chain call, never a `--jobs` above the pool. Numbers from `scripts/project.py env` (the ENV.md host row).
- **At most {{JOBS_POOL}} agents writing or running chains at once**; readers are free. Stacked per-tool pools panic the host.
- **One record round per batch** (`make record-round`, locked), after the last generator of the batch — never one per commit.
- **Caching policy:** previews regenerate every run (the fast engine, seconds); STL exports of record stay on the preset's `engine:` (the one that
  passes the mesh gates), cached only on the inputs + engine key, and the sidecar md5 is a determinism check on every export (`--no-cache`
  forces; drift under an unchanged key = FAIL). Cache only the slicer / PDF / index steps, each behind its `--check`; slice incrementally by default.
- **One-knob changes are inline edits** (a yaml value, a sidecar row, a text cell): no chain re-run for a value no generator reads; run the
  generator whose `--check` says STALE, nothing more.

## Repository layout
```
CLAUDE.md  10-spec/SPEC.md  project.yaml  .gitignore   (parts_seed.csv: the spec's part list, if the owner supplies one) {{ee,both}}
CLAUDE.md  10-spec/SPEC.md  project.yaml  .gitignore   (the fit input: the board STEP / envelope named in paths.mesh_provenance) {{mech}}
20-design/     <board>.yaml parts.yaml <board>_board.yaml placement.csv traceability.yaml erc_accept.yaml dfm_thresholds.json   (references/schematic-phase.md §1) {{ee}}
20-design/     <board>.yaml parts.yaml <board>_board.yaml placement.csv case.yaml traceability.yaml erc_accept.yaml dfm_thresholds.json   (references/schematic-phase.md §1) {{both}}
20-design/     case.yaml parts.yaml (hardware) traceability.yaml   (references/case-pipeline.md) {{mech}}
gen/           project generators (build_sch, check_maps, place_pcb, export, fab_package, …) — each with --check / --selftest {{ee}}
gen/           project generators (build_sch, check_maps, place_pcb, export, fab_package, case, fea, drawings, …) — each with --check / --selftest {{both}}
gen/           project generators (case geometry, drawings, fea, kits, production_cut) — each with --check / --selftest {{mech}}
vendor/hw-from-spec/  the skill (submodule);  scripts -> vendor/hw-from-spec/scripts  (relative symlink; or a copy of scripts/)
lib/           fetched symbols/footprints/3D (vendor-licensed data never leaves the repo) {{ee,both}}
lib/           vendor STEPs, TDS PDFs, hardware drawings (vendor-licensed data never leaves the repo) {{mech}}
00-now/        the five answers (where things stand, blocked on owner, what to print / order / check on arrival) — generated, never edited
10-spec/       SPEC, FINDINGS, KICKOFF_ANSWERS, SPEC_ERRATA, spec_sections/, datasheet_notes/
20-design/     the yaml sources of truth + briefs, TEST_PLAN, VERIFY (generators read ONLY from here)
30-board/      kicad/ (the CAD project)  layout/ (gerbers, drc, renders, drawings)  fab/<rev>/ (the uploaded package) {{ee,both}}
40-case/       <set>/ per print target: parts/ (STL of record = the record id in mech)  checks/ (census, DFM = what the gates read)  pictures/  build/ (ignored) {{mech,both}}
50-kits/       <kit>/ per print target: START_HERE.md  plates/  parts/  sheets/ — mirrored to ~/Downloads/<project>_kits/<kit>/ {{mech,both}}
60-orders/     PROCUREMENT, PARTS_VERIFICATION, ORDER_<rev>, ARRIVAL_CHECKLIST_<rev>, quotes/<date>/ (fab evidence, frozen)
70-release/    <rev>/ (the cut)  reports/  collateral/<rev>/  marketing/<rev>/
80-reviews/    <round>/ (one folder per review round)  REVIEW_HANDOFF
90-log/        DECISIONS STATUS GATES BLOCKERS KNOWN_ISSUES TRACEABILITY LEARNINGS_LOG ENV — the append logs the generators read and write
               The tree is the navigation (skill `references/project-yaml.md` §Layout): names are nouns, one current thing per path, records beside
               what they describe, numbers = the order of the project's life. A re-layout is a decision row + project.yaml `reorg:` +
               `scripts/reorg_paths.py`; frozen records keep the old paths, `--map` reads them
```

## Conventions
- Net names, sheet numbers, refdes ranges, pin maps: exactly as in the spec unless a logged decision changes them. {{ee,both}}
- Symbol fields: `MPN, Manufacturer, {{FAB_CODE_FIELD}}, Datasheet, Confidence, Alt_MPN, Alt_{{FAB_CODE_FIELD}}`. {{ee,both}}
- Units mm, µF/nF/pF, `4.7k` not `4k7`. Every sheet has a title block and a NOTES block (intent, key values, rework links, test points, checklist). {{ee,both}}
- Envelope, interface positions, materials and fits: exactly as in the spec / fit input of record unless a logged decision changes them; units mm. {{mech}}
- Decision rows: 6 cells, `\|` for a literal pipe; status history after the `(was:` marker; the nod marker in a status cell means "applied, owner look wanted".
