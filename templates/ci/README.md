# templates/ci — GitHub Actions for a generated-only hardware project

Consumed by the `hw-from-spec` skill: it substitutes the `{{PROJECT_*}}` placeholders from the project's `project.yaml` and writes the result to
`.github/workflows/` of the new project, together with a `scripts/ci/project.env` holding the same constants. Nothing here knows a board name.

| Placeholder | Meaning | Example |
|---|---|---|
| `{{PROJECT_NAME}}` | display name | `MY-BOARD` |
| `{{PROJECT_KICAD_IMAGE}}` | the KiCad CLI container, pinned to the version in the project's ENV record | `kicad/kicad:10.0.5-full` |
| `{{PROJECT_CHECK_CMD}}` | the one PR entry point with stable exit codes | `make check` |
| `{{PROJECT_SETUP_CMD}}` | Linux bootstrap (path shims, fonts, venv from a pinned requirements file) | `make setup-linux` |
| `{{PROJECT_NIGHTLY_CMD}}` | long checks that are still bounded (case chain, FEA *selftests*) | `make nightly` |
| `{{PROJECT_RELEASE_CMD}}` | stages the package of record + release docs and REFUSES licensed vendor files | `make release-archive OUT=out/release_artefacts` |
| `{{PROJECT_TAG_PATTERN}}` | release tag glob | `board-*` |
| `{{PROJECT_VENDOR_EXCLUDE}}` | path prefix of licensed vendor data (SnapEDA/SnapMagic, vendor STEPs) that never leaves the repo | `lib/vendor/<vendor>` |
| `{{PROJECT_ARTEFACT_GLOBS}}` | newline-separated paths uploaded after the PR check (ERC json, PDFs, DRC census) | `out/<board>/erc.json` |
| `{{PROJECT_NIGHTLY_ARTEFACT_GLOBS}}` | case STLs / check reports | `out/<board>/mechanical/case/*/stl/*.stl` |

Rules baked in (from the AEC-CT2 project, LEARNINGS_LOG):
- The gate list lives in the project's `Makefile` / `scripts/ci/*.sh`, not in YAML — the same command runs on the developer's machine.
- Pin the container to the KiCad version recorded in the project's ENV file; the generators' file-format assumptions depend on it.
- CI never routes (the routed board + SES are the record), never runs blind reviews (API keys, rule 8), never fetches live stock (rule 1 wants a
  recorded fetch), never renders with a display, never orders. Say so in the workflow header — rule 10.
- Full FEA solves are release records regenerated under a decision row, not scheduler output; nightly runs the selftests.
- The release job refuses the upload when any vendor path or vendor file NAME is present; no `contents: write`, no secrets — the owner creates the
  GitHub Release by hand until licence/visibility is decided.
- Pin action majors (`actions/checkout@v4`, `actions/upload-artifact@v4`); `fetch-depth: 0` because replay/census gates read git history.
- Say in the header whether the workflow has ever run on a Linux runner. It is honest and it tells the next person where to look when it fails.
