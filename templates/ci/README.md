# templates/ci — GitHub Actions for a generated-only hardware project

Three workflow templates with `{{PROJECT_*}}` placeholders. **Nothing substitutes them for you**: fill them by hand or with the `sed` recipe below,
copy the result to `.github/workflows/` of the project, and write `scripts/ci/project.env` yourself (`KEY=value` lines the jobs source, e.g.
`PROJECT_VENDOR_EXCLUDE=lib/vendor/`). Nothing here knows a board name. Skill `SKILL.md` §0 step 7 is where this happens.

```sh
S=vendor/hw-from-spec/templates/ci; mkdir -p .github/workflows scripts/ci
for f in pr-check nightly release; do
  sed -e 's|{{PROJECT_NAME}}|MY-BOARD|g' -e 's|{{PROJECT_KICAD_IMAGE}}|kicad/kicad:10.0.5-full|g' -e 's|{{PROJECT_SETUP_CMD}}|scripts/ci/setup_linux.sh|g' \
      -e 's|{{PROJECT_CHECK_CMD}}|scripts/adopt_gates.sh --no-clone|g' -e 's|{{PROJECT_CLONE_GATE_CMD}}|scripts/clone_gate.sh|g' \
      -e 's|{{PROJECT_NIGHTLY_CMD}}|scripts/ci/nightly.sh|g' -e 's|{{PROJECT_RELEASE_CMD}}|scripts/ci/release_archive.sh out/release_artefacts|g' \
      -e 's|{{PROJECT_TAG_PATTERN}}|board-*|g' -e 's|{{PROJECT_VENDOR_EXCLUDE}}|lib/vendor/|g' \
      -e 's|{{PROJECT_ARTEFACT_GLOBS}}|out/*/erc.json|g' -e 's|{{PROJECT_NIGHTLY_ARTEFACT_GLOBS}}|out/*/mechanical/case/*/stl/*.stl|g' $S/$f.yml > .github/workflows/$f.yml
done
printf 'PROJECT_VENDOR_EXCLUDE=lib/vendor/\n' > scripts/ci/project.env
grep -n '{{PROJECT_' .github/workflows/*.yml && echo "unfilled placeholders" || echo "ci templates filled"   # '{{PROJECT_' only: GitHub's own ${{ github.ref }} expressions must stay
```

| Placeholder | Meaning | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | display name | `MY-BOARD` |
| `{{PROJECT_KICAD_IMAGE}}` | the KiCad CLI container, pinned to the version in the project's ENV record | `kicad/kicad:10.0.5-full` |
| `{{PROJECT_CHECK_CMD}}` | the one PR entry point with stable exit codes | `scripts/adopt_gates.sh --no-clone` or `make check` |
| `{{PROJECT_CLONE_GATE_CMD}}` | the fresh-checkout gate run on tags (release.yml) | `scripts/clone_gate.sh` |
| `{{PROJECT_SETUP_CMD}}` | Linux bootstrap (path shims, fonts, venv from a pinned requirements file) | `make setup-linux` |
| `{{PROJECT_NIGHTLY_CMD}}` | long checks that are still bounded (case chain, FEA *selftests*) | `make nightly` |
| `{{PROJECT_RELEASE_CMD}}` | stages the package of record + release docs and REFUSES licensed vendor files | `make release-archive OUT=out/release_artefacts` |
| `{{PROJECT_TAG_PATTERN}}` | release tag glob | `board-*` |
| `{{PROJECT_VENDOR_EXCLUDE}}` | path prefix of licensed vendor data (SnapEDA/SnapMagic, vendor STEPs) that never leaves the repo | `lib/vendor/<vendor>` |
| `{{PROJECT_ARTEFACT_GLOBS}}` | newline-separated paths uploaded after the PR check (ERC json, PDFs, DRC census) | `out/<board>/erc.json` |
| `{{PROJECT_NIGHTLY_ARTEFACT_GLOBS}}` | case STLs / check reports | `out/<board>/mechanical/case/*/stl/*.stl` |

Rules baked in (from the source project's learnings log):
- The gate list lives in `project.yaml gates:` (run by `scripts/adopt_gates.sh`) or the project's `Makefile` / `scripts/ci/*.sh`, not in the workflow
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
