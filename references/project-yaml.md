# project.yaml — the one file the generic scripts read

Every script does `Project.find()` (walk up from cwd, or `$HWFS_PROJECT`, or `--project`) and takes paths, id prefixes, markers, tools and gate
lists from here. Missing keys fall back to the defaults in `scripts/project.py` `DEFAULTS`. Paths are root-relative. **The file sits at the git
top level** — the shell gates (`adopt_gates.sh`, `clone_gate.sh`) archive HEAD from there and refuse otherwise. Start from `templates/project.yaml`
(day-1 gate lists); a filled example is `smoke/project.yaml`; the schema:

```yaml
project:
  name: <short name>                      # used in generated headers
  description: <one line>
skill: {repo: <url>, commit: <sha>}       # the hw-from-spec commit the project follows (informational; README "Use in a new project")
ids:
  owner_prefix: D                         # owner decision rows  D-nn
  agent_prefix: CC                        # agent rows           CC-nnn (three digits)
  blocker_prefix: B                       # blockers             B-nn (two digits)
markers:
  release_regex: 'clear[ -]to[ -]build'   # the owner's line in paths.gates that turns reports RELEASED — never quote the phrase in prose
  unverified: [UNVERIFIED, TBD-DRAWING]   # test-plan markers collected into KNOWN_ISSUES §4
  nod_regex: '\(!\)|owner nod'            # status cells "applied ahead of the owner's nod" → KNOWN_ISSUES §2.1
  hand_curated: ["<!-- hand-curated: begin -->", "<!-- hand-curated: end -->"]
paths:
  decisions: docs/DECISIONS.md            # 6-cell table (ID | Date | Status | Topic | Proposal | Reason)
  blockers: docs/BLOCKERS.md              # 6-cell table (ID | Date | Item | Tried | Result | Impact)
  gates: docs/GATES.md
  status: docs/STATUS.md
  known_issues: docs/KNOWN_ISSUES.md      # written by scripts/known_issues.py
  test_plan: docs/TEST_PLAN.md            # optional
  traceability_yaml: design/traceability.yaml
  traceability_out: docs/TRACEABILITY.md  # written by scripts/traceability.py
  board: kicad/<board>/<board>.kicad_pcb  # the board of record; its md5 keys packages, collateral, reports
  netlist: out/<board>.xml                # kicadxml netlist for netlist_net checks (optional)
  fab_dir: out/fab                        # packages <date>_<md5-8>/ each with board_id.txt (keys: board, md5, commit, built, + counts)
  release_dir: docs/release
  collateral_dir: docs/release/collateral # <md5-8>/renders/ from scripts/collect_renders.py
  case_yaml: design/case.yaml             # optional; `case.version` is read by handoff_header / collect_renders
  mesh_provenance: out/mechanical/board.stl.provenance.json   # optional; {board_md5, board_commit, mesh_md5, facets}
tools:
  python: .venv/bin/python                # {PY} in traceability commands; a leading "." makes it root-relative
  kicad_cli: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli   # {KICAD_CLI}
  kicad_python: /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3   # {KPY}
traceability:
  scratch_links: [lib]                    # symlinked next to the scratch copy of the board dir so ${KIPRJMOD}/../../lib resolves
dfm:
  thresholds: design/dfm_thresholds.json  # the fab's numbers, with source URL + date (references/fab-dfm.md)
  items: out/dfm_items.json               # written by the project's measurer
  accept: design/board.yaml               # yaml with key dfm_accepted: [{check, refs: [..] | {REF: n}, reason}]
  report: out/dfm.json                    # written by every plain scripts/dfm_check.py run (--check compares); read by release_report section dfm
renders:                                  # scripts/collect_renders.py rules; {MD5_8} {CASE_VERSION} {BOARD} {KICAD_CLI} {OUT} expand
  - {name: pcb_top, kind: kicad_render, args: ["--side", "top", "--quality", "high", "--background", "opaque"]}
  - {name: pcb_iso, kind: kicad_render, args: ["--side", "top", "--perspective", "--rotate", "-45,0,135"]}
  - {name: panel_top, kind: copy, src: "out/fab/*_{MD5_8}/panel/panel_top.png"}
  - {name: case_iso, kind: copy, src: "out/case/{CASE_VERSION}/renders/iso.png", sub: case, min_bytes: 2000}
reports:                                  # scripts/release_report.py; one file per entry under paths.release_dir
  - name: PCB_DESIGN_REPORT
    title: PCB design report
    sections: [banner, identity, decisions, known_issues, package, traceability, dfm, renders, inventory]
    extra_sources: [design/board.yaml, design/parts.yaml]
gates:
  quiet_regex: 'Fontconfig|wxApp|Debug:'  # stderr lines filtered per line by adopt_gates.sh (never a whole-stream 2>/dev/null)
  adopt:                                  # scripts/adopt_gates.sh: run in order, exit 1 on the first failure; $PY is exported
    - "$PY scripts/known_issues.py --selftest"
    - "$PY scripts/known_issues.py --check"
    - "$PY scripts/traceability.py --check"
    - "$PY scripts/dfm_check.py --check"   # G2+: needs the measurer's items; day 1 uses the shorter list of templates/project.yaml
    - "$PY scripts/collect_renders.py --check"
    - "$PY scripts/release_report.py --check"
  clone:                                  # scripts/clone_gate.sh: run inside `git archive HEAD`
    - "$PY scripts/release_report.py --check"
  regen:                                  # clone_gate.sh --regen: run inside the archive, then copy regen_copy_back into the tree
    - "$PY scripts/release_report.py"
  regen_copy_back: [docs/release/PCB_DESIGN_REPORT.md]
```

## Conventions the scripts rely on

- `board_id.txt` in a fab package: one `key value` per line; `md5` = md5 of the board file; `commit` = the generator commit. Packages are
  selected by md5, never by mtime (all mtimes are equal on a fresh clone).
- The decisions table's third cell is the status; text after `(was:` is history and ignored.
- `traceability.yaml`: `stages:` is an ordered mapping (`requires:` + `reached:` checks); `entries:` carry `id, source, requirement, lands_in,
  stage, checks` and optionally `status: not_included` + `reason`, `pending: <text>`. Every decision row must be cited by some entry's `source`.
- Shell gate commands run with cwd = repo root (or the archive) and `$PY` set; write them root-relative. `$PY` is the first interpreter that
  imports `yaml` among `$PYTHON`, the project `.venv`, the skill's `.venv`, `python3` (printed at the top of every run).
- Which scripts are generators and which are graders: `known_issues`, `traceability`, `release_report`, `collect_renders`, `dfm_check` have
  `--check`; `handoff_header.py` prints a header (nothing to check); `project.py` is the reader.

## Adding a project-specific script

Put it in the project's own `gen/`; make it read `project.yaml` through `scripts/project.py` (`from project import Project`) rather than
hard-coding paths; give it `--check` and `--selftest`; add its `--selftest` and `--check` to `gates.adopt`.
