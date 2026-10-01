# ENV.md — the environment this project was built in (verify every line by running the command; record what answered)

| Tool | Version (command that printed it) | Path | Date |
|---|---|---|---|
| CAD CLI | `{{CAD_CLI_PATH}} version` → {{CAD_CLI_VERSION}} | `{{CAD_CLI_PATH}}` | {{DATE}} | {{ee,both}}
| CAD Python | `{{CAD_PYTHON_PATH}} -c '<import of the CAD module, print its version>'` → … | `{{CAD_PYTHON_PATH}}` | {{DATE}} | {{ee,both}}
| Geometry CLI | `{{GEOMETRY_CLI_PATH}} --version` → … (e.g. openscad) | `{{GEOMETRY_CLI_PATH}}` | {{DATE}} | {{mech,both}}
| Slicer CLI | `{{SLICER_CLI_PATH}} --version` → … (home FDM preset) | `{{SLICER_CLI_PATH}}` | {{DATE}} | {{mech,both}}
| Project venv | `.venv/bin/python --version` → … ; packages: {{VENV_PACKAGES}} | `.venv/` | {{DATE}} |
| hw-from-spec | commit `{{SKILL_COMMIT}}` (`git -C {{SKILL_PATH}} rev-parse --short HEAD`) | `{{SKILL_PATH}}` | {{DATE}} |
| git, bash | `git --version`, `bash --version` (the shell gates need bash ≥ 3.2) | | {{DATE}} |
{{HOST_ROW}}   <!-- paste the line `scripts/project.py env` prints: cores, RAM, the heavy-job pool size and memory floor scripts/jobs.sh derives (references/agent-ops.md §8); project.yaml `host:` overrides -->

## Endpoints that answered (rule 1: live part verification)
| Endpoint | Purpose | Answered on | Notes |
|---|---|---|---|
| _(none yet)_ | | | |

## File-format versions seen
| File kind | Version string | First seen |
|---|---|---|
| _(run the CAD / geometry CLI once on a trivial file and record the header)_ | | |
