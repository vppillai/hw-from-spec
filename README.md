# hw-from-spec

A Claude Code skill + generic scripts + workflow templates for running a hardware project (PCB + printed/CNC enclosure, contract fab such as
JLCPCB) from a written specification to a production cut: owner-gated phases, generated-only artefacts, live part verification, a fab-DFM mirror,
blind double reviews with external models, a release report and a production document set. Distilled from one complete project
(a KiCad 10 QSFP-DD test dongle, 170+ decision rows, five audit rounds, ~155 logged learnings); nothing project-specific ships here except as
labelled worked examples.

```
SKILL.md          the procedure (≤ 500 lines): phases/gates, generated-only rule, decision log, parts, blind reviews, adopt rule, DFM mirror,
                  case + FEA, software track, release/production cut, agent operations
references/       detail per topic, loaded on demand: project-yaml, part-verification, fab-dfm, case-pipeline, fea-stage, software-track,
                  release-and-cut, agent-ops, pitfalls (every recorded learning, one line each)
scripts/          generic generators driven by a project.yaml — known_issues, traceability, handoff_header, dfm_check (grading engine),
                  release_report (skeleton), collect_renders, clone_gate.sh, adopt_gates.sh; each has --selftest
workflows/        four blind-review workflow templates ({{PLACEHOLDERS}}) + README on instantiating them
templates/        CLAUDE.md rules, DECISIONS / STATUS / GATES / KNOWN_ISSUES / LEARNINGS_LOG / BLOCKERS / PARTS_VERIFICATION seeds,
                  hand-off and release-notes skeletons, production_cut.yaml; templates/ci/ = CI workflow templates
smoke/            the automated dry run: a five-part one-sheet project with a two-piece case; run_smoke.sh drives every script to a DRAFT report
evals/            skill-creator eval prompts (start a project / run a blind review / cut a release)
```

## Install

Requirements: Python ≥ 3.11 with `pyyaml`, git, zsh (macOS default). Nothing else for the generic scripts; the CAD, OpenSCAD, FEA and browser
tooling belong to the project that uses the skill and are recorded in its `docs/ENV.md`.

```sh
git clone <this repo> ~/.claude/skills/hw-from-spec        # 1. as a Claude Code skill (personal); or
mkdir -p .claude/skills && git submodule add <this repo> .claude/skills/hw-from-spec   #    per project (the skill is then also your scripts source)
cd <skill dir> && uv venv .venv && uv pip install --python .venv/bin/python pyyaml      # 2. the scripts' interpreter
for s in scripts/*.py; do .venv/bin/python $s --selftest; done; scripts/clone_gate.sh --selftest; scripts/adopt_gates.sh --selftest
smoke/run_smoke.sh                                          # 3. the dry run — green before you start a project
```
As a plugin: point a Claude Code plugin manifest at this directory (the skill is `SKILL.md`); the scripts stay usable from the plugin path.

## Use in a new project

```sh
cd <new project repo>
git submodule add <this repo> vendor/hw-from-spec && ln -s vendor/hw-from-spec/scripts scripts   # or copy scripts/ and pin the skill commit in project.yaml
cp vendor/hw-from-spec/templates/{CLAUDE.md,DECISIONS.md,STATUS.md,GATES.md,KNOWN_ISSUES.md,LEARNINGS_LOG.md,BLOCKERS.md,PARTS_VERIFICATION.md} .   # then move docs to docs/
cp vendor/hw-from-spec/smoke/project.yaml project.yaml       # edit paths / ids / tools / gates (references/project-yaml.md)
```
Then follow `SKILL.md` §0 (day-1 setup). The scripts find `project.yaml` by walking up from the cwd (or `HWFS_PROJECT=…`); shell gates use the
project's `.venv` if it has pyyaml, else the skill's.

Project-specific generators (schematic builder, placement, routing, export, fab package, panel, silk, case, drawings, FEA measurer) stay in the
project's `gen/`; they read constants through `scripts/project.py` and are added to `gates.adopt` with their `--selftest` and `--check`.

## What is and is not here

Generic: the gate model, the decision log discipline, verification tags, the review protocol and its workflow shapes, the adopt rule, the report
and cut generators' shape, agent operations, every pitfall as a mechanism. Worked examples (labelled): JLCPCB numbers and form traps, KiCad 10 /
SWIG quirks, Freerouting facts, the source project's case and FEA cases. Not here: vendor-licensed library data, quotes, part numbers of the
source project, its board hashes (only in `references/pitfalls.md` as labelled examples where the mechanism needs them).

Feedback loop: every project appends to its `docs/LEARNINGS_LOG.md`; at its production cut the entries are folded into `references/pitfalls.md`
here (one generalised line + evidence pointer), and the skill is re-reviewed blind.

Licence: see `LICENSE` (owner's choice pending).
