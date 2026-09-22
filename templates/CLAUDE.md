# CLAUDE.md — {{PROJECT}} ({{ONE_LINE_DESCRIPTION}})

You are building a {{CAD_TOOL}} hardware project ({{BOARD_SUMMARY}} + {{ENCLOSURE_SUMMARY}}) from a written specification, for fabrication and
assembly at {{FAB}}. Humans review at gates. Read `SPEC.md`, `docs/STATUS.md`, `docs/DECISIONS.md` before doing anything. The process is the
`hw-from-spec` skill (installed at `{{SKILL_PATH}}`); `project.yaml` carries every project constant.

## Non-negotiable rules
1. **Never invent a fab part number.** A number enters the BOM only after a fetch of its live page in this session confirms MPN, package and stock.
   Record every check in `docs/PARTS_VERIFICATION.md` (date, URL, stock, class). Tags: [V] verified, [K] known-unverified, [S] select-by-parameter.
2. **Never change a specified value, part, topology or pin assignment silently.** Write the proposal to `docs/DECISIONS.md` with the reason, mark it
   OPEN, ask the owner. Apply only after approval (or when the spec delegates the choice); an operating gate may ship as an optional flag that warns.
3. **Every VERIFY item is closed by reading the primary datasheet** (page/section cited in `docs/datasheet_notes/<part>.md`) before the part is drawn.
4. **Stop at gates.** G0 = SPEC approved (after two blind reviews). G1 = schematic approved. G2 = layout approved. Do not start the next phase's CAD
   before the owner writes the gate line into `docs/GATES.md`. The release line in that file is the owner's too; never quote its phrase in prose.
5. **Everything is generated, nothing is hand-edited.** CAD files, reports and indexes come from `gen/` scripts reading `design/*.yaml`. A review
   finding changes the YAML or the generator, then regenerates. Every generator has `--check` and `--selftest`. Exceptions are logged decision rows
   with a chain-of-record table. Commit after every meaningful step with a descriptive message and explicit paths.
6. **{{SHEET_AND_REFDES_CONVENTION}}** (e.g. one generated sheet file per instance; refdes = sheet × 100 + n).
7. **Validate after every generation:** ERC/DRC via the CAD CLI with all severities, zero errors; warnings fixed or justified in `docs/ERC_WAIVERS.md`.
8. **Blind reviews are really blind.** Reviewers get the frozen worktree and the hand-off only — never each other's output, never the author's
   reasoning. Verify BLOCKER/MAJOR adversarially, merge in `docs/reviews/`.
9. **Fab constraints are hard:** {{FAB_CONSTRAINTS}} (sides, minimum package, link parts, no BGA, parts on the verified list, fab code field on every
   fitted part, DNP marked and excluded from BOM/CPL). Mirror the fab's DFM checker in-repo (`design/dfm_thresholds.json`, `scripts/dfm_check.py`).
10. **Say what you don't know.** If a datasheet, drawing or page cannot be fetched, mark the item BLOCKED in `docs/BLOCKERS.md` and continue elsewhere.
11. **Capture learnings.** Before your final commit, append every non-obvious learning as a dated, domain-tagged line to `docs/LEARNINGS_LOG.md`.

## Environment (verify on first run, record in docs/ENV.md)
- CAD CLI: `{{CAD_CLI_PATH}}`; CAD Python: `{{CAD_PYTHON_PATH}}`; project venv `.venv` (Python ≥ 3.11) with {{VENV_PACKAGES}}.
- All tool paths live in `project.yaml tools:`; generators read them from there (`scripts/project.py`), never hard-code them.

## Repository layout
```
CLAUDE.md  SPEC.md  project.yaml  parts_seed.csv
design/        <board>.yaml parts.yaml <board>_board.yaml placement.csv case.yaml traceability.yaml dfm_thresholds.json
gen/           project generators (build_sch, place_pcb, export, fab_package, case, fea, drawings, …) — each with --check / --selftest
scripts/       hw-from-spec generic scripts (submodule or copy)
lib/           fetched symbols/footprints/3D (vendor-licensed data never leaves the repo)
kicad/<board>/ generated project      out/           generated packages, renders, checks
docs/          ENV DECISIONS BLOCKERS GATES STATUS KNOWN_ISSUES TRACEABILITY LEARNINGS_LOG PARTS_VERIFICATION datasheet_notes/ reviews/ release/
```

## Conventions
- Net names, sheet numbers, refdes ranges, pin maps: exactly as in the spec unless a logged decision changes them.
- Symbol fields: `MPN, Manufacturer, {{FAB_CODE_FIELD}}, Datasheet, Confidence, Alt_MPN, Alt_{{FAB_CODE_FIELD}}`.
- Units mm, µF/nF/pF, `4.7k` not `4k7`. Every sheet has a title block and a NOTES block (intent, key values, rework links, test points, checklist).
- Decision rows: 6 cells, `\|` for a literal pipe; status history after `(was: …)`; the nod marker in a status cell means "applied, owner look wanted".
