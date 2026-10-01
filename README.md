# hw-from-spec

A Claude Code skill that takes a board, an enclosure, or both from a written spec to a production cut:
owner-gated phases, generated-only artefacts, a zero-warning manufacturability bar, blind reviews with
a record-reading verifier, and a retro that folds every project's learnings back into the skill.

`version 0.10.1` · MIT · `SKILL.md` is the procedure; everything else is reference, template or tool.
What changed per version: `CHANGELOG.md` (its first section is the current state).

## Quick start

```sh
git submodule add https://github.com/vppillai/hw-from-spec.git vendor/hw-from-spec
ln -s vendor/hw-from-spec/scripts scripts
uv venv .venv
uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy shapely \
  rtree networkx mapbox-earcut
vendor/hw-from-spec/smoke/run_smoke.sh
```

ONE venv, the project's, mesh libraries included (without them the smoke skips the print-DFM section
with a NOTE). Then `SKILL.md` §0: templates, the kickoff questionnaire, first records — before any CAD.

No project yet, just a bracket STL and a vendor in mind? Clone, one venv, one command:

```sh
git clone https://github.com/vppillai/hw-from-spec.git && cd hw-from-spec
uv venv .venv && uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy \
  shapely rtree networkx mapbox-earcut
.venv/bin/python scripts/print_dfm.py --list                 # the process rows
.venv/bin/python scripts/print_dfm.py --process xometry_mjf_pa12 ~/bracket.stl
```

Exit 0 = PASS, 1 = FLAG with one line per rule (measured | limit | where | fix): `references/print-dfm.md`.

## What you get

- Three scopes chosen at kickoff — `ee` (G0 spec → G1 schematic → G2 layout → order), `mech` (G0 →
  M1 geometry → M2 first article → case order), `both` — from one template set; the owner writes every approval.
- A kickoff questionnaire: every owner decision up front, each with a recommended answer.
- A manufacturability bar enforced by scripts, not prose: DRC 0 / 0 / 0, fab DFM 0 open, printed
  enclosure census 0 unaccepted FAIL + print DFM PASS, vendor checker no flag by API read.
- A vendor-independent print DFM check on the mesh before every upload, validated against the
  vendors' verdicts (a vendor flag we pass = a rule defect); build rules for PCB and MJF / FDM / SLA /
  CNC enclosures tagged checker / fab capability / physics / owner choice; slicer knobs with a proof row each.
- Generic `project.yaml`-driven scripts (every one with `--selftest` and a read-only `--check`) for the
  records, gates, release and production cut, the arrival checklist, the job pool and the retro.
- Blind-review workflow templates with a record-reading verifier; a two-minute dry run (`smoke/`) that
  drives every script, greps every rule and runs the two lints that keep the skill generic and present-tense.

## Repository map

| Path | What |
|---|---|
| `SKILL.md` | the procedure: setup + kickoff, gates, generated-only, decisions, parts, reviews, layout, DFM, case, software, release, agents, retro |
| `references/` | detail per topic, read on demand (the Where-to-look table at the end of `SKILL.md` maps needs to files) |
| `templates/` | CLAUDE.md, project.yaml, SPEC / VERIFY / KICKOFF_ANSWERS / governance records, review hand-off, DFM round, vendor review, census rows, process table, arrival checklist, spec errata, production-cut yaml, CI + Makefile |
| `scripts/` | the generic tools driven by `project.yaml` (`references/project-yaml.md` lists which are generators, graders, gates) |
| `workflows/` | blind-review workflow templates + how to instantiate them |
| `smoke/` | the automated dry run (`run_smoke.sh`, about two minutes) |
| `evals/` | the skill evals + `run_evals.py` (every eval carries mechanical checks) |
| `docs/retro/`, `docs/reviews/` | retro reports and blind reviews of the skill, one index file each |
| `CHANGELOG.md` | the current state, then what changed per version |

## Install

Requirements: git, bash ≥ 3.2, Python ≥ 3.11, `uv` (or `python3 -m venv` + `pip`); `pyyaml` for every
script, `numpy trimesh scipy shapely rtree networkx mapbox-earcut` for the mesh scripts (`matplotlib`
for heat-map PNGs). CAD, OpenSCAD, FEA and browser tooling belong to the project (`docs/governance/ENV.md`).
The skill lives in ONE place inside a project: a submodule at `vendor/hw-from-spec` with a relative
symlink `scripts -> vendor/hw-from-spec/scripts`; a personal clone under `~/.claude/skills/` is for
skill discovery only, never a project's scripts source.

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

2. ONE venv, the project's `.venv` (gitignored); the smoke, the evals and every gate use it; Python
commands in `SKILL.md` that read `project.yaml` are written `.venv/bin/python scripts/<tool>.py`.

```sh
uv venv .venv
uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy shapely \
  rtree networkx mapbox-earcut
```

3. Prove the toolchain before reading the spec:

```sh
export PYTHONDONTWRITEBYTECODE=1   # no __pycache__ written into the submodule
for s in scripts/*.py; do .venv/bin/python "$s" --selftest; done
for s in scripts/*.sh; do "$s" --selftest; done
vendor/hw-from-spec/smoke/run_smoke.sh
.venv/bin/python vendor/hw-from-spec/evals/run_evals.py
```

## Use in a new project

4. Copy the templates and resolve the scope (`T` is the templates folder); `project.py slots` counts
the unfilled `{{…}}` slots per file — CLAUDE.md / project.yaml / records now, SPEC + KICKOFF_ANSWERS
after the kickoff and the spec; 0 before the G0 ask:

```sh
T=vendor/hw-from-spec/templates
mkdir -p docs/governance docs/design docs/parts docs/reviews docs/release docs/quotes
mkdir -p docs/production design
cp "$T/CLAUDE.md" "$T/.gitignore" "$T/project.yaml" "$T/SPEC.md" .
cp "$T"/{DECISIONS,STATUS,GATES,KNOWN_ISSUES}.md docs/governance/
cp "$T"/{LEARNINGS_LOG,BLOCKERS,ENV,KICKOFF_ANSWERS}.md docs/governance/
cp "$T/PARTS_VERIFICATION.md" docs/parts/
cp "$T/TEST_PLAN.md" "$T/design/VERIFY.md" docs/design/
cp -R "$T/datasheet_notes" docs/
cp "$T/design/traceability.yaml" "$T/production_cut.yaml" design/
cp "$T/design/dfm_processes.yaml" design/                # mech, both
cp "$T/docs/quotes/dfm_verdicts.yaml" docs/quotes/       # mech, both
cp "$T/design/erc_accept.yaml" design/                  # ee, both
cp "$T/design/SOFTWARE_ARCHITECTURE.md" docs/design/     # ee, both
cp "$T/parts/PROCUREMENT.md" docs/parts/                 # mech, both
cp "$T/ci/Makefile" .                       # make check / case / slice / record-round
scripts/project.py scaffold --scope "$A0" CLAUDE.md SPEC.md project.yaml \
  docs/governance/*.md design/*.yaml                  # A0=ee | mech | both
scripts/project.py slots                              # the count to drive to 0 (fill
```                                                   #  project.yaml before any reader runs)

5. Follow `SKILL.md` §0: the kickoff questionnaire, ENV record (`scripts/project.py env` prints the
host row), first records, adopt gates, then G0. Fill slots that sit inside a path unquoted
(`kicad/sensor/sensor.kicad_pcb`). `templates/design/arrival_checklist.yaml` is copied at the order (SKILL §10.1). Scripts find `project.yaml` by walking up from the
cwd (or `HWFS_PROJECT=…`); the shell gates print which interpreter they use. Never put the submodule
AT `scripts/`. Project-specific generators (schematic builder, placement, routing, export, fab
package, panel, silk, case, drawings, FEA measurer) stay in the project's `gen/`, read constants
through `scripts/project.py`, and join `gates.adopt` with their `--selftest` and `--check`.

## The kickoff questionnaire

Before the spec is read, the agent asks the scope (A0), then every decision class that scope needs —
product, PCB build, enclosure architecture, the manufacturability bar, verification, bought parts,
software, release, identity, slicer optimisation — in up to twelve `AskUserQuestion` batches of at
most four, each question with a marked RECOMMENDED answer and the alternatives' consequences. Answers
become owner rows in `DECISIONS.md`, values in `project.yaml` (`project.py kickoff --check` proves they
landed) and `docs/governance/KICKOFF_ANSWERS.md`. Detail: `references/kickoff-questionnaire.md`, `SKILL.md` §0.1.

## The retro loop

After a production cut, `scripts/skill_retro.py --project <root>` reads the project's learnings log
and decision log, lists what the skill does not carry yet, and drafts the CHANGELOG entry, the
reference patches, the evals and the questionnaire questions for the next version
(`docs/retro/<project>_<date>.md`); `--apply` folds the mechanical part (pitfalls lines, new process
rows, a CHANGELOG stub), the rest stays a draft a maintainer reads. The project pins the skill version
it ran in `project.yaml skill: {repo, commit, version}`. Detail: `SKILL.md` §13.

## Versioning, licence, contributing

`SKILL.md` carries `version:`; `CHANGELOG.md` has one entry per version with Changed / Added / Not done
and a current-state section on top. A project pins `skill.commit` and `skill.version`; the retro
reports drift. Numbers that come from a vendor (fab table, checker line, tolerance) are dated in the
text and in `project.yaml`, and re-fetched before use. MIT (`LICENSE`). Contributions arrive as retro
PRs: run `scripts/skill_retro.py` on a finished project, fold its report into the references, add the
evals, keep `smoke/run_smoke.sh` and the two lints (`scripts/doc_voice_lint.py`,
`scripts/generic_lint.py`) green, bump the version, write the CHANGELOG entry, open the PR.
