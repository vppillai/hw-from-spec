# hw-from-spec — v0.4.1

A Claude Code skill + generic scripts + workflow templates for running a hardware project (PCB + printed/CNC enclosure, contract fab such as
JLCPCB) from a written specification to a production cut: owner-gated phases, generated-only artefacts, live part verification, a fab-DFM mirror,
blind double reviews with external models, a release report and a production document set. Distilled from one complete project
(a KiCad 10 QSFP-DD test dongle, 200+ decision rows, five audit rounds, ~230 logged learnings, one vendor review round after the order and five
printed-enclosure DFM rounds — folded into one procedure with the vendor's API verdict and length-calibration probes so the next case is vendor-clean
before its first quote); nothing project-specific ships
here except as labelled worked examples.

```
SKILL.md          the procedure (≤ 500 lines): phases/gates, generated-only rule, decision log, parts, blind reviews, adopt rule, DFM mirror,
                  case + FEA, printed-enclosure DFM (§8.1), software track, release/production cut, agent operations
references/       detail per topic, loaded on demand: project-yaml, schematic-phase, part-verification, fab-dfm, case-pipeline,
                  dfm-printed-enclosure (MJF / FDM rules as measured, census gate, API-verdict quote-page procedure, length-dependent metric + probes,
                  home-preset mirror, coupons, dummies, post-mortem), fea-stage,
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
evals/            skill-creator eval prompts (start a project / blind review / release / vendor mail / re-layout / first printed-enclosure DFM round /
                  a vendor flag the census cannot see)
```

## Install

Requirements: git, bash ≥ 3.2, Python ≥ 3.11, and `uv` (or `python3 -m venv` + `pip`). The generic
scripts need only `pyyaml`; the two mesh scripts (`thin_wall_census.py`, `thin_wall_check.py`) need
`numpy trimesh scipy shapely`. CAD, OpenSCAD, FEA and browser tooling belong to the project and are
recorded in its `docs/governance/ENV.md`.

The skill lives in ONE place inside a project: a submodule at `vendor/hw-from-spec` with a relative
symlink `scripts -> vendor/hw-from-spec/scripts`. A personal clone under `~/.claude/skills/` only
makes the skill discoverable to Claude Code; it is never a project's scripts source.

1a. Personal install (skill discovery only):

```sh
git clone https://github.com/vppillai/hw-from-spec.git ~/.claude/skills/hw-from-spec
```

1b. In a project (the layout every gate command assumes; `<repo>` is your project's git top level):

```sh
cd <repo>
git submodule add https://github.com/vppillai/hw-from-spec.git vendor/hw-from-spec
ln -s vendor/hw-from-spec/scripts scripts
```

2. Two virtual environments, both gitignored (the skill's for its selftests, the project's for
`tools.python` and the mesh scripts). Without `uv`: `python3 -m venv .venv && .venv/bin/pip install …`.

```sh
uv venv vendor/hw-from-spec/.venv
uv pip install --python vendor/hw-from-spec/.venv/bin/python pyyaml
uv venv .venv
uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy shapely
```

3. Prove the toolchain before reading the spec:

```sh
for s in scripts/*.py; do .venv/bin/python "$s" --selftest; done
scripts/clone_gate.sh --selftest
scripts/adopt_gates.sh --selftest
vendor/hw-from-spec/smoke/run_smoke.sh
```

## Use in a new project

4. Copy the templates and fill every `{{…}}` slot (`T` is the templates folder):

```sh
T=vendor/hw-from-spec/templates
mkdir -p docs/governance docs/design docs/parts docs/reviews docs/release docs/quotes docs/production design
cp "$T/CLAUDE.md" "$T/.gitignore" "$T/project.yaml" "$T/SPEC.md" .
cp "$T"/{DECISIONS,STATUS,GATES,KNOWN_ISSUES,LEARNINGS_LOG,BLOCKERS,ENV,ERC_WAIVERS}.md docs/governance/
cp "$T/PARTS_VERIFICATION.md" "$T/parts/PROCUREMENT.md" docs/parts/
cp "$T/TEST_PLAN.md" "$T/design/VERIFY.md" "$T/design/SOFTWARE_ARCHITECTURE.md" docs/design/
cp -R "$T/datasheet_notes" docs/
cp "$T/design/traceability.yaml" design/
grep -rn '{{' CLAUDE.md project.yaml SPEC.md docs design
```

5. Follow `SKILL.md` §0: the kickoff questionnaire (every owner decision up front), ENV record,
first records, adopt gates, then G0. The scripts find `project.yaml` by walking up from the cwd
(or `HWFS_PROJECT=…`); the shell gates print which interpreter they use. Pin the skill in
`project.yaml skill: {repo, commit, version}`. Never put the submodule AT `scripts/`.

Project-specific generators (schematic builder, placement, routing, export, fab package, panel,
silk, case, drawings, FEA measurer) stay in the project's `gen/`; they read constants through
`scripts/project.py` and join `gates.adopt` with their `--selftest` and `--check`.

## What is and is not here

Generic: the gate model, the decision log discipline, verification tags, the review protocol and its workflow shapes, the adopt rule, the report
and cut generators' shape, agent operations, every pitfall as a mechanism. Worked examples (labelled): JLCPCB numbers and form traps, KiCad 10 /
SWIG quirks, Freerouting facts, the source project's case and FEA cases. Not here: vendor-licensed library data, quotes, part numbers of the
source project, its board hashes (only in `references/pitfalls.md` as labelled examples where the mechanism needs them).

Feedback loop: every project appends to its `docs/governance/LEARNINGS_LOG.md`; at its production cut the entries are folded into `references/pitfalls.md`
here (one generalised line + evidence pointer), and the skill is re-reviewed blind.

Licence: `LICENSE` is a placeholder until the owner chooses one — the repo is not yet redistributable. Changes: `CHANGELOG.md`.
