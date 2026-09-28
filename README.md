# hw-from-spec — v0.4.0

A Claude Code skill + generic scripts + workflow templates for running a hardware project (PCB + printed/CNC enclosure, contract fab such as
JLCPCB) from a written specification to a production cut: owner-gated phases, generated-only artefacts, live part verification, a fab-DFM mirror,
blind double reviews with external models, a release report and a production document set. Distilled from one complete project
(a KiCad 10 QSFP-DD test dongle, 200+ decision rows, five audit rounds, ~230 logged learnings, one vendor review round after the order and four
printed-enclosure DFM rounds — folded into one procedure so the next case is vendor-clean before its first quote); nothing project-specific ships
here except as labelled worked examples.

```
SKILL.md          the procedure (≤ 500 lines): phases/gates, generated-only rule, decision log, parts, blind reviews, adopt rule, DFM mirror,
                  case + FEA, printed-enclosure DFM (§8.1), software track, release/production cut, agent operations
references/       detail per topic, loaded on demand: project-yaml, schematic-phase, part-verification, fab-dfm, case-pipeline,
                  dfm-printed-enclosure (MJF / FDM rules as measured, census gate, heat-map procedure, coupons, dummies, post-mortem), fea-stage,
                  software-track, release-and-cut, vendor-review, agent-ops, pitfalls (every recorded learning, one line each)
scripts/          generic generators driven by a project.yaml — known_issues, traceability, handoff_header, dfm_check (grading engine),
                  release_report (skeleton), collect_renders, reorg_paths (layout migration + zero-loss proof), thin_wall_check (quick census +
                  point contacts), thin_wall_census (the printed-body FAIL gate: walls / voids / wedges, --json record, pure --gate-dir),
                  assembly_guide (illustrated guide), clone_gate.sh, adopt_gates.sh (read-only guard); each has --selftest
workflows/        four blind-review workflow templates ({{PLACEHOLDERS}}) + README on instantiating them
templates/        CLAUDE.md rules, project.yaml (day-1 gate lists), .gitignore, DECISIONS / STATUS / GATES / KNOWN_ISSUES / LEARNINGS_LOG /
                  BLOCKERS / PARTS_VERIFICATION / ENV / TEST_PLAN / ERC_WAIVERS seeds, datasheet_notes/, design/traceability.yaml seed,
                  hand-off, vendor-review record, DFM_ROUND record, CENSUS_GATE_ROWS check-table rows and release-notes skeletons,
                  production_cut.yaml; templates/ci/ = CI workflow templates (fill with the sed recipe there)
smoke/            the automated dry run: a five-part one-sheet project with a two-piece case; run_smoke.sh drives every script to a DRAFT report
evals/            skill-creator eval prompts (start a project / blind review / release / vendor mail / re-layout / first printed-enclosure DFM round)
```

## Install

Requirements: Python ≥ 3.11 with `pyyaml`, git, bash ≥ 3.2 (macOS `/bin/bash` and any Linux). Nothing else for the generic scripts; the CAD,
OpenSCAD, FEA and browser tooling belong to the project that uses the skill and are recorded in its `docs/governance/ENV.md`.

```sh
git clone <this repo> ~/.claude/skills/hw-from-spec        # 1. as a Claude Code skill (personal); or
mkdir -p .claude/skills && git submodule add <this repo> .claude/skills/hw-from-spec   #    per project (the skill is then also your scripts source)
cd <skill dir> && uv venv .venv && uv pip install --python .venv/bin/python pyyaml      # 2. the scripts' interpreter
for s in scripts/*.py; do .venv/bin/python $s --selftest; done; scripts/clone_gate.sh --selftest; scripts/adopt_gates.sh --selftest
smoke/run_smoke.sh                                          # 3. the dry run — green before you start a project
```
As a plugin: point a Claude Code plugin manifest at this directory (the skill is `SKILL.md`); the scripts stay usable from the plugin path.

## Use in a new project

One canonical layout — the skill under `vendor/hw-from-spec`, a RELATIVE symlink `scripts` (or a copy of `scripts/`), `project.yaml` at the git
top level. This is the layout the smoke run and `clone_gate.sh --selftest` exercise (`git archive HEAD` carries the symlink but no submodule
content; the clone gate links the working tree's scripts and venv into the archive).

```sh
cd <new project repo>                                        # git init done, project.yaml will sit here (top level)
git submodule add <this repo> vendor/hw-from-spec && ln -s vendor/hw-from-spec/scripts scripts      # or: cp -R vendor/hw-from-spec/scripts scripts
(cd vendor/hw-from-spec && uv venv .venv && uv pip install --python .venv/bin/python pyyaml)      # the skill's venv (gitignored, does not ship)
T=vendor/hw-from-spec/templates; mkdir -p docs/{governance,design,parts,reviews,release,quotes,production} design
cp $T/CLAUDE.md $T/.gitignore $T/project.yaml . && cp $T/{DECISIONS,STATUS,GATES,KNOWN_ISSUES,LEARNINGS_LOG,BLOCKERS,ENV,ERC_WAIVERS}.md docs/governance/
cp $T/PARTS_VERIFICATION.md docs/parts/ && cp $T/TEST_PLAN.md docs/design/ && cp -R $T/datasheet_notes docs/ && cp $T/design/traceability.yaml design/
grep -rn '{{' CLAUDE.md project.yaml docs design                  # fill every slot until this prints nothing
```
Then follow `SKILL.md` §0 (day-1 setup: venv, selftests, smoke, first records, adopt gates). The scripts find `project.yaml` by walking up from the
cwd (or `HWFS_PROJECT=…`); the shell gates use the first interpreter that imports `yaml` among `$PYTHON`, the project `.venv`, the skill's `.venv`,
`python3`, and print which. Pin the skill commit in `project.yaml skill: {repo, commit}`. Never put the submodule AT `scripts/`.

Project-specific generators (schematic builder, placement, routing, export, fab package, panel, silk, case, drawings, FEA measurer) stay in the
project's `gen/`; they read constants through `scripts/project.py` and are added to `gates.adopt` with their `--selftest` and `--check`.

## What is and is not here

Generic: the gate model, the decision log discipline, verification tags, the review protocol and its workflow shapes, the adopt rule, the report
and cut generators' shape, agent operations, every pitfall as a mechanism. Worked examples (labelled): JLCPCB numbers and form traps, KiCad 10 /
SWIG quirks, Freerouting facts, the source project's case and FEA cases. Not here: vendor-licensed library data, quotes, part numbers of the
source project, its board hashes (only in `references/pitfalls.md` as labelled examples where the mechanism needs them).

Feedback loop: every project appends to its `docs/governance/LEARNINGS_LOG.md`; at its production cut the entries are folded into `references/pitfalls.md`
here (one generalised line + evidence pointer), and the skill is re-reviewed blind.

Licence: `LICENSE` is a placeholder until the owner chooses one — the repo is not yet redistributable. Changes: `CHANGELOG.md`.
