# templates/ci — GitHub Actions for a generated-only hardware project

Three workflow templates with `{{PROJECT_*}}` placeholders and three minimal CI scripts. **Nothing substitutes the placeholders for you**: fill
them with the recipe below, which copies the result to `.github/workflows/` and the scripts + `project.env` to the PROJECT-OWNED **`ci/`** directory
(`KEY=value` lines the jobs source). Never write under `scripts/` — that is the skill submodule (a file written there is untracked in the project
and absent in CI). Every checkout uses `submodules: recursive` so `scripts -> vendor/hw-from-spec/scripts` resolves. Nothing
here knows a board name. Skill `SKILL.md` §0 step 7 is where this happens.

```sh
S=vendor/hw-from-spec/templates/ci; mkdir -p .github/workflows ci
cp "$S"/{setup_linux,nightly,release_archive}.sh ci/            # project-owned copies: edit them, they are yours
for f in pr-check nightly release; do
  sed -e 's|{{PROJECT_NAME}}|MY-BOARD|g' -e 's|{{PROJECT_CAD_IMAGE}}|kicad/kicad:10.0.5-full|g' -e 's|{{PROJECT_SETUP_CMD}}|ci/setup_linux.sh|g' \
      -e 's|{{PROJECT_CHECK_CMD}}|scripts/adopt_gates.sh --no-clone|g' -e 's|{{PROJECT_CLONE_GATE_CMD}}|scripts/clone_gate.sh|g' \
      -e 's|{{PROJECT_NIGHTLY_CMD}}|ci/nightly.sh|g' -e 's|{{PROJECT_RELEASE_CMD}}|ci/release_archive.sh build/release_artefacts|g' \
      -e 's|{{PROJECT_TAG_PATTERN}}|board-*|g' -e 's|{{PROJECT_VENDOR_EXCLUDE}}|lib/vendor/|g' \
      -e 's|{{PROJECT_ARTEFACT_GLOBS}}|30-board/layout/erc.json|g' -e 's|{{PROJECT_NIGHTLY_ARTEFACT_GLOBS}}|40-case/*/parts/*.stl|g' $S/$f.yml > .github/workflows/$f.yml
done
printf 'PROJECT_VENDOR_EXCLUDE=lib/vendor/\n' > ci/project.env
grep -n '{{PROJECT_' .github/workflows/*.yml && echo "unfilled placeholders" || echo "ci templates filled"   # '{{PROJECT_' only: GitHub's own ${{ github.ref }} expressions must stay
```

| Script (copied to `ci/`) | Does | Edit when |
|---|---|---|
| `Makefile` (copied to the project ROOT) | `make check` = the adopt gates (the PR entry point), `case` / `slice` / `renders` / `pdf` through the one heavy-job pool `scripts/jobs.sh` (`--only-changed` by default), `record-round` under one lock (`references/agent-ops.md` §8) | the project's generator names differ (they are placeholders for `gen/…`) |
| `setup_linux.sh` | apt `git python3-venv python3-pip bash`, `python3 -m venv .venv` + `pip install pyyaml` (+ the mesh libs with `NIGHTLY=1`), `git config safe.directory` | the project needs more (fonts, a slicer CLI, a pinned requirements file) |
| `nightly.sh` | every `scripts/*.py --selftest`, the gen/ selftests it finds, `scripts/adopt_gates.sh --no-clone` | the case chain / FEA selftests join |
| `release_archive.sh OUT` | stages the fab package of record (`scripts/project.py record` md5 → `paths.fab_dir`), `70-release/reports/`, `70-release/<rev>/` into OUT; REFUSES when any staged path starts with `$PROJECT_VENDOR_EXCLUDE` | the deliverable set changes |

| Placeholder | Meaning | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | display name | `MY-BOARD` |
| `{{PROJECT_CAD_IMAGE}}` | the CAD CLI container, pinned to the version in the project's ENV record | `kicad/kicad:10.0.5-full` |
| `{{PROJECT_CHECK_CMD}}` | the one PR entry point with stable exit codes | `scripts/adopt_gates.sh --no-clone` or `make check` |
| `{{PROJECT_CLONE_GATE_CMD}}` | the fresh-checkout gate run on tags (release.yml) | `scripts/clone_gate.sh` |
| `{{PROJECT_SETUP_CMD}}` | Linux bootstrap (path shims, fonts, venv from a pinned requirements file) | `ci/setup_linux.sh` |
| `{{PROJECT_NIGHTLY_CMD}}` | long checks that are still bounded (case chain, FEA *selftests*) | `ci/nightly.sh` |
| `{{PROJECT_RELEASE_CMD}}` | stages the package of record + release docs and REFUSES licensed vendor files | `ci/release_archive.sh build/release_artefacts` |
| `{{PROJECT_TAG_PATTERN}}` | release tag glob | `board-*` |
| `{{PROJECT_VENDOR_EXCLUDE}}` | path prefix of licensed vendor data (SnapEDA/SnapMagic, vendor STEPs) that never leaves the repo | `lib/vendor/<vendor>` |
| `{{PROJECT_ARTEFACT_GLOBS}}` | newline-separated paths uploaded after the PR check (ERC json, PDFs, DRC census) | `30-board/layout/erc.json` |
| `{{PROJECT_NIGHTLY_ARTEFACT_GLOBS}}` | case STLs / check reports | `40-case/*/parts/*.stl` |

Rules baked in (from measured learnings logs):
- The gate list lives in `project.yaml gates:` (run by `scripts/adopt_gates.sh`) or the project's `Makefile` / `ci/*.sh`, not in the workflow
  YAML — the same command runs on the developer's machine. The skill's shell gates are bash (≥ 3.2); the container needs `bash`, `git`, a Python
  with `pyyaml` — install them in `{{PROJECT_SETUP_CMD}}` (`apt-get install -y git python3-yaml` on Debian-based images).
- Pin the container to the KiCad version recorded in the project's ENV file; the generators' file-format assumptions depend on it.
- CI never routes (the routed board + SES are the record), never runs blind reviews (API keys, rule 8), never fetches live stock (rule 1 wants a
  recorded fetch), never renders with a display, never orders. Say so in the workflow header — rule 10.
- Full FEA solves are release records regenerated under a decision row, not scheduler output; nightly runs the selftests.
- The release job refuses the upload when any vendor path or vendor file NAME is present; no `contents: write`, no secrets — the owner creates the
  GitHub Release by hand until licence/visibility is decided.
- Pin action majors (`actions/checkout@v4`, `actions/upload-artifact@v4`); `fetch-depth: 0` because replay/census gates read git history.
- Say in the header whether the workflow has ever run on a Linux runner. It is honest and it tells the next person where to look when it fails.
