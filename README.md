# hw-from-spec

A Claude Code skill that takes a board + enclosure from a written spec to a production cut:
owner-gated phases, generated-only artefacts, a zero-warning manufacturability bar, blind reviews,
and a retro that folds every project's learnings back into the skill.

`version 0.6.0` · MIT · `SKILL.md` is the procedure, everything else is reference, template or tool.

## Quick start

```sh
git submodule add https://github.com/vppillai/hw-from-spec.git vendor/hw-from-spec
ln -s vendor/hw-from-spec/scripts scripts
uv venv .venv
uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy shapely
vendor/hw-from-spec/smoke/run_smoke.sh
```

Then `SKILL.md` §0: templates, the kickoff questionnaire, first records — before any CAD.

## What you get

- A gate model (G0 spec → G1 schematic → G2 layout → order → release → production cut) where the
  owner writes every approval and agents never do.
- A kickoff questionnaire: every owner decision a board + enclosure project needs, asked up front
  with a recommended answer (`references/kickoff-questionnaire.md`).
- A manufacturability bar enforced by scripts: DRC 0 / 0 / 0 warnings, fab DFM 0 Danger / 0 Warning,
  printed-enclosure census 0 unaccepted FAIL, vendor checker no flag by API read — no prose waivers.
- Build rules tagged checker / fab capability / physics / owner choice for the PCB
  (`references/pcb-layout-dfm.md`) and for MJF / FDM / SLA / CNC enclosures.
- Generic, `project.yaml`-driven scripts with `--selftest` and read-only `--check`: decision log
  index, traceability matrix, DFM grader, thin-wall census gate, release report, collateral,
  illustrated assembly guide, re-layout with a zero-loss proof, the retro.
- FDM brand marks as two first-class options (ironed top-face feature or flush AMS colour body in
  the bed layers) with FAIL-gated mark rows, dust-cap rules and the Bambu Studio CLI facts.
- Blind-review workflow templates (in-session + external models, adversarial verifiers, merge).
- A dry run (`smoke/`) that drives every script and greps every rule the skill must not lose.

## Repository map

| Path | What |
|---|---|
| `SKILL.md` | the procedure: setup + kickoff, gates, generated-only, decisions, parts, reviews, layout, DFM, case, software, release, agents, retro |
| `references/` | detail per topic, read on demand (project-yaml, kickoff-questionnaire, schematic-phase, pcb-layout-dfm, fab-dfm, case-pipeline, dfm-printed-enclosure, cnc-enclosure, fea-stage, part-verification, software-track, release-and-cut, vendor-review, agent-ops, pitfalls) |
| `templates/` | CLAUDE.md, project.yaml, SPEC / VERIFY / KICKOFF_ANSWERS / governance records, review hand-off, DFM round, vendor review, census rows, production cut yaml, CI workflows |
| `scripts/` | 15 generic tools driven by `project.yaml` (`references/project-yaml.md` lists which are generators, graders, gates) |
| `workflows/` | four blind-review workflow templates + how to instantiate them |
| `smoke/` | the automated dry run (`run_smoke.sh`) |
| `evals/` | ten skill evals (start, review, release, vendor mail, re-layout, first DFM round, census-blind flag, kickoff, retro, AMS mark plate) |
| `docs/retro/` | retro reports, one per project fed back into the skill |
| `CHANGELOG.md` | what changed per version and what was deliberately not done |

## Install

Requirements: git, bash ≥ 3.2, Python ≥ 3.11, `uv` (or `python3 -m venv` + `pip`). The generic
scripts need `pyyaml`; the two mesh scripts need `numpy trimesh scipy shapely`. CAD, OpenSCAD, FEA
and browser tooling belong to the project and are recorded in its `docs/governance/ENV.md`.

The skill lives in ONE place inside a project: a submodule at `vendor/hw-from-spec` with a relative
symlink `scripts -> vendor/hw-from-spec/scripts`. A personal clone under `~/.claude/skills/` makes
the skill discoverable to Claude Code and is never a project's scripts source.

1a. Personal install (skill discovery only):

```sh
git clone https://github.com/vppillai/hw-from-spec.git ~/.claude/skills/hw-from-spec
```

1b. In a project (`<repo>` is the project's git top level, where `project.yaml` will sit):

```sh
cd <repo>
git submodule add https://github.com/vppillai/hw-from-spec.git vendor/hw-from-spec
ln -s vendor/hw-from-spec/scripts scripts
```

2. Two virtual environments, both gitignored. Without `uv`: `python3 -m venv <dir>` then
`<dir>/bin/pip install …` with the same packages.

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
mkdir -p docs/governance docs/design docs/parts docs/reviews docs/release docs/quotes
mkdir -p docs/production design
cp "$T/CLAUDE.md" "$T/.gitignore" "$T/project.yaml" "$T/SPEC.md" .
cp "$T"/{DECISIONS,STATUS,GATES,KNOWN_ISSUES}.md docs/governance/
cp "$T"/{LEARNINGS_LOG,BLOCKERS,ENV,ERC_WAIVERS,KICKOFF_ANSWERS}.md docs/governance/
cp "$T/PARTS_VERIFICATION.md" "$T/parts/PROCUREMENT.md" docs/parts/
cp "$T/TEST_PLAN.md" "$T/design/VERIFY.md" docs/design/
cp "$T/design/SOFTWARE_ARCHITECTURE.md" docs/design/
cp -R "$T/datasheet_notes" docs/
cp "$T/design/traceability.yaml" design/
grep -rn '{{' CLAUDE.md project.yaml SPEC.md docs design
```

5. Follow `SKILL.md` §0: the kickoff questionnaire, ENV record, first records, adopt gates, then
G0. Scripts find `project.yaml` by walking up from the cwd (or `HWFS_PROJECT=…`); the shell gates
print which interpreter they use. Never put the submodule AT `scripts/`.

Project-specific generators (schematic builder, placement, routing, export, fab package, panel,
silk, case, drawings, FEA measurer) stay in the project's `gen/`, read constants through
`scripts/project.py`, and join `gates.adopt` with their `--selftest` and `--check`.

## The kickoff questionnaire

Before the spec is read, the agent asks every decision class up front — product, PCB build,
enclosure architecture, the manufacturability bar, verification, bought parts, software, release,
identity — in ten `AskUserQuestion` batches, each question with a marked RECOMMENDED answer and the
alternatives' consequences. Answers become owner rows in `DECISIONS.md`, values in `project.yaml`
(`kickoff`, `board`, `fab_dfm.bar`, `print_targets`) and `docs/governance/KICKOFF_ANSWERS.md`.
Detail: `references/kickoff-questionnaire.md`, `SKILL.md` §0.1.

## The retro loop

After a production cut, `scripts/skill_retro.py --project <root>` reads the project's learnings log
and decision log, lists what the skill does not carry yet, and drafts the CHANGELOG entry, the
reference patches, the evals and the questionnaire questions for the next version
(`docs/retro/<project>_<date>.md`). The project pins the skill version it ran in
`project.yaml skill: {repo, commit, version}`. Detail: `SKILL.md` §13.

## Versioning

`SKILL.md` carries `version:`; `CHANGELOG.md` has one entry per version with Changed / Added /
Not done. A project pins `skill.commit` and `skill.version`; the retro reports drift. Numbers that
come from a vendor (fab table, checker line, tolerance) are dated in the text and in
`project.yaml`, and re-fetched before use.

## Licence and contributing

MIT (`LICENSE`). Contributions arrive as retro PRs: run `scripts/skill_retro.py` on a finished
project, fold its report into the references, add the evals, keep `smoke/run_smoke.sh` green, bump
the version, write the CHANGELOG entry, and open the PR with the retro report attached.
