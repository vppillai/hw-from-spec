# CLAUDE.md — {{PROJECT}} ({{ONE_LINE_DESCRIPTION}})

You are building a {{CAD_TOOL}} hardware project ({{BOARD_SUMMARY}} + {{ENCLOSURE_SUMMARY}}) from a written specification, for fabrication and
assembly at {{FAB}}. Humans review at gates. Read `SPEC.md`, `docs/governance/STATUS.md`, `docs/governance/DECISIONS.md` before doing anything. The process is the
`hw-from-spec` skill (installed at `{{SKILL_PATH}}`); `project.yaml` carries every project constant.

## Non-negotiable rules
1. **Never invent a fab part number.** A number enters the BOM only after a fetch of its live page in this session confirms MPN, package and stock.
   Record every check in `docs/parts/PARTS_VERIFICATION.md` (date, URL, stock, class). Tags: [V] verified, [K] known-unverified, [S] select-by-parameter.
2. **Never change a specified value, part, topology or pin assignment silently.** Write the proposal to `docs/governance/DECISIONS.md` with the reason, mark it
   OPEN, ask the owner. Apply only after approval (or when the spec delegates the choice); an operating gate may ship as an optional flag that warns.
3. **Every VERIFY item is closed by reading the primary datasheet** before the part is drawn. A VERIFY item is a spec value or claim that rests
   on a datasheet or standard nobody has read yet (definition: skill `SKILL.md` §4); they are listed in SPEC.md (tag `VERIFY`) or `docs/design/VERIFY.md`,
   and closed by a `docs/datasheet_notes/<part>.md` row (page/section) or a `docs/governance/BLOCKERS.md` row.
4. **Stop at gates.** G0 = SPEC approved (after a blind review round). G1 = schematic approved. G2 = layout approved. Do not start the next phase's
   CAD before the owner writes the approval into `docs/governance/GATES.md`. **Agents never write approval cells or the release line** — they ask (skill
   `SKILL.md` §1.1) and wait; a chat approval is quoted verbatim under the table, the cell stays the owner's. Never quote the release phrase in prose.
5. **Everything is generated, nothing is hand-edited.** CAD files, reports and indexes come from `gen/` scripts reading `design/*.yaml`. A review
   finding changes the YAML or the generator, then regenerates. Every generator has `--check` and `--selftest`. Exceptions are logged decision rows
   with a chain-of-record table. Commit after every meaningful step with a descriptive message and explicit paths.
6. **{{SHEET_AND_REFDES_CONVENTION}}** (e.g. one generated sheet file per instance; refdes = sheet × 100 + n).
7. **Validate after every generation:** ERC/DRC via the CAD CLI with all severities, zero errors (`references/schematic-phase.md` §2 has the
   command); warnings fixed or justified in `docs/governance/ERC_WAIVERS.md`.
8. **Blind reviews are really blind.** Reviewers get the frozen worktree and the hand-off only — never each other's output, never the author's
   reasoning. Verify BLOCKER/MAJOR adversarially, merge in `docs/reviews/`.
9. **Fab constraints are hard:** {{FAB_CONSTRAINTS}} (state them: assembly sides, minimum package, link parts, excluded package families, parts on
   the verified list, fab code field on every fitted part, DNP marked and excluded from BOM/CPL). Mirror the fab's DFM checker in-repo
   (`design/dfm_thresholds.json`, `scripts/dfm_check.py`).
10. **Say what you don't know.** If a datasheet, drawing or page cannot be fetched, mark the item BLOCKED in `docs/governance/BLOCKERS.md` and continue elsewhere.
11. **Capture learnings.** Before your final commit, append every non-obvious learning as a dated, domain-tagged line to `docs/governance/LEARNINGS_LOG.md`.

## Environment (verify on first run, record in docs/governance/ENV.md)
- CAD CLI: `{{CAD_CLI_PATH}}`; CAD Python: `{{CAD_PYTHON_PATH}}`; project venv `.venv` (Python ≥ 3.11) with {{VENV_PACKAGES}}.
- All tool paths live in `project.yaml tools:`; generators read them from there (`scripts/project.py`), never hard-code them.

## Repository layout
```
CLAUDE.md  SPEC.md  project.yaml  .gitignore   (parts_seed.csv: the spec's part list, if the owner supplies one)
design/        <board>.yaml parts.yaml <board>_board.yaml placement.csv case.yaml traceability.yaml dfm_thresholds.json   (references/schematic-phase.md §1)
gen/           project generators (build_sch, check_maps, place_pcb, export, fab_package, case, fea, drawings, …) — each with --check / --selftest
vendor/hw-from-spec/  the skill (submodule);  scripts -> vendor/hw-from-spec/scripts  (relative symlink; or a copy of scripts/)
lib/           fetched symbols/footprints/3D (vendor-licensed data never leaves the repo)
<cad>/<board>/ generated CAD project (e.g. kicad/<board>/)      out/   generated packages, renders, checks, G1/ and G2/ review packs
docs/          governance/ (ENV DECISIONS BLOCKERS GATES STATUS KNOWN_ISSUES TRACEABILITY ERC_WAIVERS LEARNINGS_LOG)  design/ (TEST_PLAN VERIFY briefs)
               parts/ (PARTS_VERIFICATION PROCUREMENT parts_check.json)  reviews/ (hand-offs, merged reports)  release/ (reports, collateral/<md5-8>/)
               quotes/<date>/ (fab evidence, never inside a package)  production/<md5-8>/ (the cut)  datasheet_notes/
               — a re-layout is a decision row + project.yaml `reorg:` + `scripts/reorg_paths.py`; frozen records keep the old paths, `--map` reads them
```

## Conventions
- Net names, sheet numbers, refdes ranges, pin maps: exactly as in the spec unless a logged decision changes them.
- Symbol fields: `MPN, Manufacturer, {{FAB_CODE_FIELD}}, Datasheet, Confidence, Alt_MPN, Alt_{{FAB_CODE_FIELD}}`.
- Units mm, µF/nF/pF, `4.7k` not `4k7`. Every sheet has a title block and a NOTES block (intent, key values, rework links, test points, checklist).
- Decision rows: 6 cells, `\|` for a literal pipe; status history after `(was: …)`; the nod marker in a status cell means "applied, owner look wanted".
