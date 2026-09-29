# project.yaml — the one file the generic scripts read

Every script does `Project.find()` (walk up from cwd, or `$HWFS_PROJECT`, or `--project`) and takes paths, id prefixes, markers, tools and gate
lists from here. Missing keys fall back to the defaults in `scripts/project.py` `DEFAULTS`. Paths are root-relative. **The file sits at the git
top level** — the shell gates (`adopt_gates.sh`, `clone_gate.sh`) archive HEAD from there and refuse otherwise. Start from `templates/project.yaml`
(day-1 gate lists); a filled example is `smoke/project.yaml`; the schema:

```yaml
project:
  name: <short name>                      # used in generated headers
  description: <one line>
skill: {repo: <url>, commit: <sha>, version: <SKILL.md version>}   # the hw-from-spec commit + version the project follows; scripts/skill_retro.py reports drift
kickoff: docs/governance/KICKOFF_ANSWERS.md   # the owner's kickoff answers (references/kickoff-questionnaire.md) — D rows before any CAD
ids:
  owner_prefix: D                         # owner decision rows  D-nn
  agent_prefix: CC                        # agent rows           CC-nnn (three digits)
  blocker_prefix: B                       # blockers             B-nn (two digits)
markers:
  release_regex: 'clear[ -]to[ -]build'   # the owner's line in paths.gates that turns reports RELEASED — never quote the phrase in prose
  unverified: [UNVERIFIED, TBD-DRAWING]   # test-plan markers collected into KNOWN_ISSUES §4
  nod_regex: '\(!\)|owner nod'            # status cells "applied ahead of the owner's nod" → KNOWN_ISSUES §2.1
  placed_regex: '\bPLACED\b'              # an owner row with this word + a package folder name = placed order → judged on frozen stock (fab-dfm §8)
  hand_curated: ["<!-- hand-curated: begin -->", "<!-- hand-curated: end -->"]
paths:
  decisions: docs/governance/DECISIONS.md            # 6-cell table (ID | Date | Status | Topic | Proposal | Reason)
  blockers: docs/governance/BLOCKERS.md              # 6-cell table (ID | Date | Item | Tried | Result | Impact)
  gates: docs/governance/GATES.md
  status: docs/governance/STATUS.md
  known_issues: docs/governance/KNOWN_ISSUES.md      # written by scripts/known_issues.py
  test_plan: docs/design/TEST_PLAN.md            # optional
  traceability_yaml: design/traceability.yaml
  traceability_out: docs/governance/TRACEABILITY.md  # written by scripts/traceability.py
  learnings: docs/governance/LEARNINGS_LOG.md  # append-only (CLAUDE.md rule 11)
  erc_waivers: docs/governance/ERC_WAIVERS.md
  env: docs/governance/ENV.md
  parts_verification: docs/parts/PARTS_VERIFICATION.md
  datasheet_notes: docs/datasheet_notes
  reviews_dir: docs/reviews                # hand-offs, per-round reports, merged reports
  quotes_dir: docs/quotes                  # <date>/ fab evidence (quotes, DFM exports, review mails, order screenshots) — never inside a package
  production_dir: docs/production          # <md5-8>/ the production cut
  board: kicad/<board>/<board>.kicad_pcb  # the board of record; its md5 keys packages, collateral, reports
  netlist: out/<board>.xml                # kicadxml netlist for netlist_net checks (optional)
  fab_dir: out/fab                        # packages <date>_<md5-8>/ each with board_id.txt (keys: board, md5, commit, built, + counts)
  release_dir: docs/release
  collateral_dir: docs/release/collateral # <md5-8>/renders/ from scripts/collect_renders.py
  case_yaml: design/case.yaml             # optional; `case.version` is read by handoff_header / collect_renders
  mesh_provenance: out/mechanical/board.stl.provenance.json   # optional; {board_md5, board_commit, mesh_md5, facets}
tools:
  python: .venv/bin/python                # {PY} in traceability commands; a leading "." makes it root-relative
  kicad_cli: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli   # {KICAD_CLI} — the key names are HISTORICAL: put your CAD's CLI here whatever the CAD
  kicad_python: /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3   # {KPY} — the CAD's Python (python3 when it has none)
traceability:
  scratch_links: [lib]                    # symlinked next to the scratch copy of the board dir so ${KIPRJMOD}/../../lib resolves
fab_dfm:                                  # the board's fab-DFM mirror (references/fab-dfm.md); the old block name `dfm:` is still read
  thresholds: design/dfm_thresholds.json  # the fab's numbers, with source URL + date
  items: out/dfm_items.json               # written by the project's measurer
  accept: design/board.yaml               # yaml with key dfm_accepted: [{check, refs: [..] | {REF: n}, reason, date, evidence}]
  report: out/dfm.json                    # written by every plain scripts/dfm_check.py run (--check compares); read by release_report section dfm
  bar: {open: 0, warnings_fail: true, accepted_requires: [reason, date, evidence]}   # the owner's manufacturability bar (SKILL §1.2): an acceptance missing a field is ignored
print_targets:                            # one entry per print target; scripts/thin_wall_census.py --target <name> reads it — no gate constant lives in a script
  jlc_mjf:                                # vendor / process / material / wall_gate / void_gate / red_line [checker]; design_margin [owner bar];
    vendor: JLC3DP                        # wedge_band (convention 1.5); tolerance + tolerance_source [vendor sheet, replaced by the first-article spread];
    process: MJF                          # max_bbox_for_rule (the size the length-dependent rule was calibrated at); checker_url + checker_date;
    material: PA12-HP                     # samples_per_mm2 (census density); post_process; rating {ul94, tg_c, source}; accepted [{class, bbox, reason, date, evidence}]
    wall_gate: 1.2
    void_gate: 1.2
    red_line: 0.5
    design_margin: 0.1
    wedge_band: 1.5
    tolerance: 0.3
    tolerance_source: "<vendor tolerance page>, <date>"
    max_bbox_for_rule: 147
    checker_url: "<quote page>"
    checker_date: 2026-09-28
    samples_per_mm2: 10
    post_process: none
    rating: {ul94: HB, tg_c: 178, source: "<TDS url>"}
    accepted: []
  home_fdm: {vendor: home, process: FDM, material: PLA, printer: "0.4 nozzle, 0.20 mm", wall_gate: 1.6, rib_gate: 1.2, void_gate: 1.0, red_line: 0.5,
             design_margin: 0.0, wedge_band: 1.5, tolerance: 0.2, samples_per_mm2: 10, post_process: none, rating: {ul94: unrated, tg_c: 55, source: "<TDS>"}, accepted: []}
reorg:                                    # scripts/reorg_paths.py — only when the layout changes (decision row first)
  moves: {docs/OLD.md: docs/<folder>/OLD.md}   # old -> new, git mv + literal rewrite (word-boundary guarded, longest first, idempotent)
  trim: [out/old_dir]                     # git rm -r (name the tag that keeps them in the decision row)
  untrack: ['out/**/logs/*.log']          # git rm --cached, files stay on disk
  gitignore: ['out/**/logs/*.log']        # lines appended to .gitignore by --apply (skipped when present; usually = untrack)
  frozen: [out/fab/]                      # never rewritten, never checked (uploaded packages, archived records)
  skip: [lib/]                            # never touched
  allow_old_files: [docs/reviews/REORG_PLAN.md]   # files that legitimately spell the old names (this script and project.yaml are exempt already)
  no_existence: ['.py', '.js', docs/governance/DECISIONS.md, docs/governance/STATUS.md, docs/governance/LEARNINGS_LOG.md, docs/reviews/]
                                          # suffixes / prefixes whose literals are old-literal-checked but need not exist (fixture strings, dated records)
  allow_missing: ['^docs/production/[0-9a-f]{8}/']   # regexes of literals allowed to be dangling (deliverables named before they exist, negative checks)
  rewrites_record: docs/reviews/REORG_REWRITES.txt   # written by --apply; read by --proof
assembly_guide:                           # scripts/assembly_guide.py (release-and-cut §8)
  yaml: design/assembly_guide.yaml        # authored short text: doc, parts, tools, defaults{defs}, pages (before/after), step_defaults, steps{n: camera/parts/tools/check}, where_the_words_are[]
  steps_md: out/mechanical/case/ASSEMBLY.md   # optional generated step source: '### Step N - title (T s)' + paragraph
  scad: out/mechanical/case/<preset>/case.scad   # geometry of record; the md5 of this ONE file keys every render (flatten includes, or accept that they do not move the key)
  out_dir: docs/production/{MD5_8}        # {MD5_8} board md5-8, {CASE_VERSION}
  doc_name: VISUAL_ASSEMBLY_GUIDE.md
  size: '1920,1440'
  render_cmd: "openscad -o {OUT} --camera={CAMERA} --imgsize={SIZE} --colorscheme=Tomorrow {DEFS} out/mechanical/case/<preset>/case.scad"   # {DEFS} = -Dk=v …
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
    - "$PY scripts/reorg_paths.py --check"   # when a reorg: block exists: no old literal, no dangling docs/ path in structural files
    - "$PY scripts/assembly_guide.py --check"   # production cut
    - "$PY scripts/thin_wall_census.py --gate-dir out/<board>/mechanical/case/<preset>/census"   # every printed body: census record md5 = STL of record, 0 unaccepted FAIL, accepted entries dated with evidence
  clone:                                  # scripts/clone_gate.sh: run inside `git archive HEAD`
    - "$PY scripts/release_report.py --check"
  regen:                                  # clone_gate.sh --regen: run inside the archive, then copy regen_copy_back into the tree
    - "$PY scripts/release_report.py"
  regen_copy_back: [docs/release/PCB_DESIGN_REPORT.md]
```

## Layout the defaults name
```
docs/governance/   DECISIONS STATUS GATES BLOCKERS KNOWN_ISSUES TRACEABILITY LEARNINGS_LOG ERC_WAIVERS ENV KICKOFF_ANSWERS   (records the generators read and write)
docs/design/       TEST_PLAN VERIFY SOFTWARE_ARCHITECTURE briefs, design notes, mechanical notes                      (intent)
docs/parts/        PARTS_VERIFICATION PROCUREMENT parts_check.json compliance json
docs/reviews/      REVIEW_HANDOFF, <ROUND>_<role>_<model>.md, *_merged.md, REORG_* inventories
docs/release/      reports, RELEASE_NOTES, collateral/<md5-8>/, marketing/
docs/quotes/<date>/  fab evidence: quote captures, DFM exports, vendor review mails + images, order screenshots (never inside a package)
docs/production/<md5-8>/  the production cut (MANIFEST, STATUS, documents, records/ = THE records folder, pdf/)
docs/datasheet_notes/
```
Every `docs/…` path in SKILL.md / references / templates spells this layout. Changing it later is a decision row + a `reorg:` block +
`scripts/reorg_paths.py` (release-and-cut §9) — never a hand sweep; frozen records keep the old paths and `--map` explains them.

## Conventions the scripts rely on

- `board_id.txt` in a fab package: one `key value` per line; `md5` = md5 of the board file; `commit` = the generator commit. Packages are
  selected by md5, never by mtime (all mtimes are equal on a fresh clone).
- The decisions table's third cell is the status; text after `(was:` is history and ignored.
- `traceability.yaml`: `stages:` is an ordered mapping (`requires:` + `reached:` checks); `entries:` carry `id, source, requirement, lands_in,
  stage, checks` and optionally `status: not_included` + `reason`, `pending: <text>`. Every decision row must be cited by some entry's `source`.
- Shell gate commands run with cwd = repo root (or the archive) and `$PY` set; write them root-relative. `$PY` is the first interpreter that
  imports `yaml` among `$PYTHON`, the project `.venv`, the skill's `.venv`, `python3` (printed at the top of every run).
- Which scripts are generators and which are graders: `known_issues`, `traceability`, `release_report`, `collect_renders`, `dfm_check`,
  `assembly_guide` have `--check`; `reorg_paths --check` is a grader (no generator side); `thin_wall_check` is a measurer (`--census`, `--pinch`,
  exit 1 on a finding); `thin_wall_census` is the printed-body GATE (`<stl> --target <print target> --json out/…/census/<piece>.json`, exit 1 on a
  WALL / VOID / WEDGE-band / OPPOSING cluster below its gate that no dated `accepted` entry covers) plus a PURE `--gate-dir <census dir>` for
  `gates.adopt` (md5 of the STL beside the record + empty `fails` + every accepted entry still dated with evidence); `skill_retro` reads a
  project's learnings and decisions and drafts the skill's next changes (no --check);
  `handoff_header.py` prints a header (nothing to check); `project.py` is the reader.
- Every `--check` is read-only on the tree (`adopt_gates.sh` fails when `git status --porcelain` changes across the gates); every `--selftest`
  works in a temp dir only.

## Adding a project-specific script

Put it in the project's own `gen/`; make it read `project.yaml` through `scripts/project.py` (`from project import Project`) rather than
hard-coding paths; give it `--check` and `--selftest`; add its `--selftest` and `--check` to `gates.adopt`.
