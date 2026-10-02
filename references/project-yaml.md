# project.yaml — the one file the generic scripts read

Every script does `Project.find()` (walk up from cwd, or `$HWFS_PROJECT`, or `--project`) and takes paths, id prefixes, markers, tools and gate
lists from here. Missing keys fall back to the defaults in `scripts/project.py` `DEFAULTS`. Paths are root-relative. **The file sits at the git
top level** — the shell gates (`adopt_gates.sh`, `clone_gate.sh`) archive HEAD from there and refuse otherwise. Start from `templates/project.yaml`
(day-1 gate lists); a filled example is `smoke/project.yaml`; the schema:

```yaml
project:
  name: <short name>                      # used in generated headers
  description: <one line>
  owner: {name: <who writes the gate cells>, email: <their git email>}   # scripts/gate_check.py --release: the release line's git author must be this person
  scope: both                             # kickoff A0: ee (PCB / PCBA only) | mech (enclosure / printed / CNC parts only) | both — SKILL.md §1;
                                          # `scripts/project.py scaffold --scope` resolves the templates' {{ee,both}} / {{mech,both}} / {{mech}} line tags
skill: {repo: <url>, commit: <sha>, version: <SKILL.md version>}   # the hw-from-spec commit + version the project follows; scripts/skill_retro.py reports drift
kickoff:                                  # the owner's kickoff answers, machine-readable (templates/project.yaml carries every class as a slot;
  answers: 10-spec/KICKOFF_ANSWERS.md   #   `scripts/project.py kickoff --check` proves each answered row landed): product_class, quantity, fab,
  product_class: engineering sample       #   enclosure{pieces … fit_decider}, verification{rounds, visual, fea}, coupons, sourcing{…}, software{…},
  # …                                     #   release{…}, identity{envelope, branding, delegation}, debug_access
board: {layers: 4, thickness_mm: 1.6, copper: "1 oz / 0.5 oz", …}   # ee / both: the PCB build from kickoff B1–B8 (SPEC R-M01 cites it)
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
  decisions: 90-log/DECISIONS.md            # 6-cell table (ID | Date | Status | Topic | Proposal | Reason)
  blockers: 90-log/BLOCKERS.md              # 6-cell table (ID | Date | Item | Tried | Result | Impact)
  gates: 90-log/GATES.md
  status: 90-log/STATUS.md
  known_issues: 90-log/KNOWN_ISSUES.md      # written by scripts/known_issues.py
  test_plan: 20-design/TEST_PLAN.md            # optional
  traceability_yaml: 20-design/traceability.yaml
  traceability_out: 90-log/TRACEABILITY.md  # written by scripts/traceability.py
  learnings: 90-log/LEARNINGS_LOG.md  # append-only (CLAUDE.md rule 11)
  erc_accept: 20-design/erc_accept.yaml       # ee / both: the machine-checked ERC acceptances scripts/erc_gate.py reads (no prose waivers)
  schematic: 30-board/kicad/<board>/<board>.kicad_sch   # ee / both: once it exists, gates.adopt must carry the erc_gate.py line (scripts/project.py gates-required)
  env: 90-log/ENV.md
  parts_verification: 60-orders/PARTS_VERIFICATION.md
  datasheet_notes: 10-spec/datasheet_notes
  reviews_dir: 80-reviews                # hand-offs, per-round reports, merged reports
  quotes_dir: 60-orders/quotes                  # <date>/ fab evidence (quotes, DFM exports, review mails, order screenshots) — never inside a package
  production_dir: 70-release          # <md5-8>/ the production cut
  board: 30-board/kicad/<board>/<board>.kicad_pcb  # ee / both: the board of record; its md5 keys packages, collateral, reports (`scripts/project.py record`)
  mech_record: "40-case/*/parts/*.stl"   # mech: the STL set of record; record md5 = md5 of the sorted "<relpath> <md5>" lines (moves when any STL moves)
  netlist: 30-board/layout/<board>.xml                # kicadxml netlist for netlist_net checks (optional)
  fab_dir: 30-board/fab                        # packages <date>_<md5-8>/ each with board_id.txt (keys: board, md5, commit, built, + counts)
  release_dir: 70-release
  collateral_dir: 70-release/collateral # <md5-8>/renders/ from scripts/collect_renders.py
  case_yaml: 20-design/case.yaml             # optional; `case.version` is read by handoff_header / collect_renders
  mesh_provenance: 40-case/board_mesh/board.stl.provenance.json   # optional; {board_md5, board_commit, mesh_md5, facets} (both) or, for an imported STEP / envelope (mech), {source, source_md5, tag: V|K}
tools:
  python: .venv/bin/python                # {PY} in traceability commands; a leading "." makes it root-relative
  kicad_cli: /Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli   # {KICAD_CLI} — the key names are HISTORICAL: put your CAD's CLI here whatever the CAD
  kicad_python: /Applications/KiCad/KiCad.app/Contents/Frameworks/Python.framework/Versions/Current/bin/python3   # {KPY} — the CAD's Python (python3 when it has none)
traceability:
  scratch_links: [lib]                    # symlinked next to the scratch copy of the board dir so ${KIPRJMOD}/../../lib resolves
fab_dfm:                                  # the board's fab-DFM mirror (references/fab-dfm.md); `dfm:` is read as an alias of this block
  thresholds: design/dfm_thresholds.json  # the fab's numbers, with source URL + date
  items: out/dfm_items.json               # written by the project's measurer
  accept: 20-design/board.yaml               # yaml with key dfm_accepted: [{check, refs: [..] | {REF: n}, reason, date, evidence}]
  report: out/dfm.json                    # written by every plain scripts/dfm_check.py run (--check compares); read by release_report section dfm
  bar: {open: 0, warnings_fail: true, accepted_requires: [reason, date, evidence]}   # the owner's manufacturability bar (SKILL §1.2): an acceptance missing a field is ignored
print_targets:                            # one entry per print target; scripts/thin_wall_census.py --target <name> reads it — no gate constant lives in a script; `dfm_process` names the 20-design/dfm_processes.yaml row scripts/print_dfm.py gates on
  vendor_mjf:                             # vendor / process / material / wall_gate / void_gate / red_line [checker]; design_margin [owner bar];
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
  # Worked example: a project laid out as `docs/<topic>/` + `out/<board>/` moving to the numbered tree. Each row is a file or a WHOLE
  # directory; `--apply` runs them longest key first, so a file listed out of a directory leaves before the directory goes, and a
  # directory whose destination already exists is merged file by file. Literals under a moved directory are rewritten with the prefix
  # (`docs/quotes/<date>/mail.txt` -> `60-orders/quotes/<date>/mail.txt`) in every non-frozen tracked text file.
  moves:
    docs/governance/KICKOFF_ANSWERS.md: 10-spec/KICKOFF_ANSWERS.md   # the one governance file that belongs to the spec stage
    docs/governance: 90-log                                           # the append logs: DECISIONS STATUS GATES BLOCKERS KNOWN_ISSUES LEARNINGS_LOG TRACEABILITY ENV
    SPEC.md: 10-spec/SPEC.md
    FINDINGS.md: 10-spec/FINDINGS.md
    docs/spec_sections: 10-spec/spec_sections
    docs/datasheet_notes: 10-spec/datasheet_notes
    docs/design: 20-design                                            # briefs, notes, test plan beside the yaml sources of truth
    design: 20-design                                                 # the yaml sources (merged into the directory the row above created)
    docs/parts: 60-orders                                             # PARTS_VERIFICATION PROCUREMENT parts_check.json
    docs/production/ORDER.md: 60-orders/ORDER_rev0.md
    docs/production/ARRIVAL_CHECKLIST.md: 60-orders/ARRIVAL_CHECKLIST_rev0.md
    docs/quotes: 60-orders/quotes                                     # fab evidence by date: frozen (below)
    docs/production/<md5-8>: 70-release/rev0                          # the cut: the folder takes the revision name, the hash stays inside (MANIFEST, records/)
    docs/release/collateral/<md5-8>: 70-release/collateral/rev0
    docs/release/marketing/<md5-8>_<ver>: 70-release/marketing/rev0
    docs/release: 70-release/reports                                  # design reports, release notes (collateral and marketing left first)
    docs/reviews: 80-reviews                                          # then one folder per round by hand, the merged file at its root
    kicad: 30-board/kicad
    out/<board>/layout: 30-board/layout
    out/<board>/fab/<date>_<md5-8>: 30-board/fab/rev0                 # board_id.txt inside keeps the md5 + commit
    out/<board>/mechanical/<set>: 40-case/<set>                       # one row per print target; parts/ checks/ pictures/ build/ are split afterwards
  frozen: [60-orders/quotes, '70-release/*/records']   # moved as whole folders when they are a move key; content never rewritten, never checked;
                                          # spelled by old or new name (both match), `*` = one path segment
  gitignore: ['40-case/*/build/']         # lines appended to .gitignore by --apply (skipped when present): SCAD, logs, slicer scratch, caches
  allow_missing: ['^60-orders/quotes/', '^70-release/rev[0-9]+/']   # regexes of literals allowed to be dangling (dated rows quoting evidence, deliverables named before they exist)
  rewrites_record: 80-reviews/REORG_REWRITES.txt   # written by --apply; read by --proof
  trim: [out/old_dir]                     # git rm -r (name the tag that keeps them in the decision row)
  untrack: ['40-case/**/build/*.log']     # git rm --cached, files stay on disk (usually = gitignore)
  skip: [lib/]                            # never touched
  allow_old_files: [80-reviews/REORG_PLAN.md]   # files that legitimately spell the old names (this script and project.yaml are exempt already)
  no_existence: ['.py', '.js', 90-log/DECISIONS.md, 90-log/STATUS.md, 90-log/LEARNINGS_LOG.md, 80-reviews/]
                                          # suffixes / prefixes whose literals are old-literal-checked but need not exist (fixture strings, dated records)
  # `--map docs/quotes/<date>/mail.txt` answers `60-orders/quotes/<date>/mail.txt` (longest matching key) for every dated row that still
  # spells a pre-move path; `--proof BEFORE AFTER REWRITES` on two `git ls-files -s` dumps shows every blob at its mapped path or in the rewrite list.
assembly_guide:                           # scripts/assembly_guide.py (release-and-cut §8)
  yaml: 20-design/assembly_guide.yaml        # authored short text: doc, parts, tools, defaults{defs}, pages (before/after), step_defaults, steps{n: camera/parts/tools/check}, where_the_words_are[]
  steps_md: 40-case/ASSEMBLY.md   # optional generated step source: '### Step N - title (T s)' + paragraph
  scad: 40-case/<preset>/case.scad   # geometry of record; the md5 of this ONE file keys every render (flatten includes, or accept that they do not move the key)
  out_dir: 70-release/{MD5_8}        # {MD5_8} board md5-8, {CASE_VERSION}
  doc_name: VISUAL_ASSEMBLY_GUIDE.md
  size: '1920,1440'
  render_cmd: "openscad -o {OUT} --camera={CAMERA} --imgsize={SIZE} --colorscheme=Tomorrow {DEFS} 40-case/<preset>/case.scad"   # {DEFS} = -Dk=v …
renders:                                  # scripts/collect_renders.py rules; {MD5_8} {CASE_VERSION} {BOARD} {KICAD_CLI} {OUT} expand
  - {name: pcb_top, kind: kicad_render, args: ["--side", "top", "--quality", "high", "--background", "opaque"]}
  - {name: pcb_iso, kind: kicad_render, args: ["--side", "top", "--perspective", "--rotate", "-45,0,135"]}
  - {name: panel_top, kind: copy, src: "30-board/fab/*_{MD5_8}/panel/panel_top.png"}
  - {name: case_iso, kind: copy, src: "out/case/{CASE_VERSION}/renders/iso.png", sub: case, min_bytes: 2000}
reports:                                  # scripts/release_report.py; one file per entry under paths.release_dir
  - name: PCB_DESIGN_REPORT
    title: PCB design report
    sections: [banner, identity, decisions, known_issues, package, traceability, dfm, renders, inventory]
    extra_sources: [20-design/board.yaml, 20-design/parts.yaml]
gates:
  quiet_regex: 'Fontconfig|wxApp|Debug:'  # stderr lines filtered per line by adopt_gates.sh (never a whole-stream 2>/dev/null)
  iteration:                              # scripts/iteration_gate.sh [-- <cmd> ...]: the INNER tier (fast loop), read-only guarded (as adopt_gates.sh)
    inner:                                # the project's standing fast set; a change's own commands follow `--` on the command line; empty + none given = refused
      - "$PY gen/case.py --check"
      - "$PY scripts/print_dfm.py --gate 40-case/<preset>/dfm"
                                          # the other tiers are existing commands: standard = scripts/adopt_gates.sh --no-clone (make gates), release = scripts/adopt_gates.sh (make check)
  adopt:                                  # scripts/adopt_gates.sh: run in order, exit 1 on the first failure; $PY is exported
    - "$PY scripts/known_issues.py --selftest"
    - "$PY scripts/known_issues.py --check"
    - "$PY scripts/traceability.py --check"
    - "$PY scripts/dfm_check.py --check"   # G2+: needs the measurer's items; day 1 uses the shorter list of templates/project.yaml
    - "$PY scripts/collect_renders.py --check"
    - "$PY scripts/release_report.py --check"
    - "$PY scripts/reorg_paths.py --check"   # when a reorg: block exists: no old literal, no dangling docs/ path in structural files
    - "$PY scripts/assembly_guide.py --check"   # production cut
    - "$PY scripts/thin_wall_census.py --gate-dir 40-case/<set>/checks/census"   # every printed body: census record md5 = STL of record, 0 unaccepted FAIL, accepted entries dated with evidence
    - "$PY scripts/print_dfm.py --gate 40-case/<set>/checks/dfm"   # every censused body: a print_dfm record of the same md5, verdict PASS (or --open <tag>/<piece>=<decision>)
    - "$PY scripts/scad_lint.py 40-case/<set>/build/*.scad"       # generated SCAD: no statement behind a `//`
  clone:                                  # scripts/clone_gate.sh: run inside `git archive HEAD`
    - "$PY scripts/release_report.py --check"
  regen:                                  # clone_gate.sh --regen: run inside the archive, then copy regen_copy_back into the tree
    - "$PY scripts/release_report.py"
  regen_copy_back: [70-release/reports/PCB_DESIGN_REPORT.md]
```

## Layout the defaults name
```
00-now/          WHERE_THINGS_STAND.md  BLOCKED_ON_OWNER.md  WHAT_TO_PRINT.md  WHAT_TO_ORDER.md  WHAT_TO_CHECK_ON_ARRIVAL.md
                 generated every record round from 90-log/ and the kits (scripts/now_pages.py); never edited; a stale page fails the gates
10-spec/         SPEC.md  FINDINGS.md  KICKOFF_ANSWERS.md  SPEC_ERRATA.md  spec_sections/  datasheet_notes/
20-design/       the yaml sources of truth (case, board, parts, erc_accept, traceability, arrival_checklist, dfm_processes), briefs, design notes,
                 TEST_PLAN, VERIFY, SOFTWARE_ARCHITECTURE, the drawings index
30-board/        kicad/ (the CAD project)   layout/ (gerbers, drc, dxf, renders, inspection, drawings)   fab/<rev>/ (the uploaded package;
                 board_id.txt = md5 + commit)                                                                                         [ee, both]
40-case/         <set>/ per print target (mjf_case, p2s_case, plug_caps, coupons, board_dummy, dfm_validation, fea, board_mesh)         [mech, both]
                 each set: parts/ (STL of record, tracked)  checks/ (census + DFM records, clearance, interference = what the gates read)
                           pictures/ (previews, faces, assembly renders)  build/ (SCAD, logs, slicer scratch, caches — gitignored)
50-kits/         <kit>/ per print target — START_HERE.md  plates/ (.3mf + .3mf.json sidecar)  parts/ (STL copies, md5-checked)  sheets/  [mech, both]
                 the one kit of record; mirrored byte-identical to ~/Downloads/<project>_kits/<kit>/
60-orders/       PROCUREMENT.md  PARTS_VERIFICATION.md  parts_check.json  ORDER_<rev>.md  ARRIVAL_CHECKLIST_<rev>.md  quotes/<date>/ (frozen)
70-release/      <rev>/ (the cut: MANIFEST, STATUS, manuals, SOPs, pdf/, records/ = THE records folder)   reports/ (the design reports,
                 RELEASE_NOTES)   collateral/<rev>/   marketing/<rev>/
80-reviews/      <round>/ — one folder per review round (the merged file at its root), REVIEW_HANDOFF, REORG_* inventories
90-log/          DECISIONS  STATUS (append log)  GATES  BLOCKERS  KNOWN_ISSUES  TRACEABILITY  LEARNINGS_LOG  ENV — the records the generators read and write
gen/  scripts/  tools/  lib/  Makefile  CLAUDE.md        the machinery
```
Four rules make the tree the navigation, so no README is needed to use it:
- **Names are nouns a technician knows.** No hash and no date names a folder at the top of a tree; a revision is `rev0`, a kit is its print target;
  the hash lives inside (`board_id.txt`, `RENDERS.md`, `MANIFEST`). `40-case/dfm_validation/` is the one hash-named place, inside its set.
- **One current thing per path.** Superseded kits, cuts and case versions are not kept beside the current one; git history holds them.
- **Records sit next to what they describe.** A part's census and DFM verdict are in `checks/` beside its STL, never in a parallel tree.
- **Order follows the life of the project.** The numbers fix the reading order in every project; a scope that lacks a stage has no folder at that
  number (ee: no `40-case/`, `50-kits/`; mech: no `30-board/`).
Every path is a `paths:` key (`scripts/project.py` DEFAULTS; the commented block in `templates/project.yaml` lists them) and the templates folder
mirrors the tree (`templates/90-log/DECISIONS.md` is copied to `90-log/DECISIONS.md`). Every path SKILL.md / the references / the templates spell
is this layout. Changing it later is a decision row + a `reorg:` block + `scripts/reorg_paths.py` (release-and-cut §9, the `reorg:` section below)
— never a hand sweep; frozen records keep the old paths and `--map` explains them.
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
  exit 1 on a finding); `print_dfm` is the printability-floor GATE on the mesh (`--process <row> <stl> --out DIR`, exit 1 on FLAG; PURE `--gate DIR`; `--validate`
  exit 1 on a RULE DEFECT); `scad_lint` is a grader of generated SCAD; `thin_wall_census` is the printed-body design-margin GATE (`<stl> --target <print target> --json out/…/census/<piece>.json`, exit 1 on a
  WALL / VOID / WEDGE-band / OPPOSING cluster below its gate that no dated `accepted` entry covers) plus a PURE `--gate-dir <census dir>` for
  `gates.adopt` (md5 of the STL beside the record + empty `fails` + every accepted entry still dated with evidence); `skill_retro` reads a
  project's learnings and decisions and drafts the skill's next changes (no --check);
  `handoff_header.py` prints a header (nothing to check); `project.py` is the reader (+ `scope`, `record` = the record label and md5 per scope,
  `scaffold --scope` = the one write it does: resolving template scope tags in place on copied files).
- **Record md5 per scope** (`Project.record_md5()`; used by `release_report` identity, `collect_renders` folder, `handoff_header`, the cut id):
  ee / both → md5 of the board file's raw bytes; mech → the `paths.mech_record` set. MISSING (None) until the artefact exists.
- Every `--check` is read-only on the tree (`adopt_gates.sh` fails when `git status --porcelain` changes across the gates); every `--selftest`
  works in a temp dir only.

## Adding a project-specific script

Put it in the project's own `gen/`; make it read `project.yaml` through `scripts/project.py` (`from project import Project`) rather than
hard-coding paths; give it `--check` and `--selftest`; add its `--selftest` and `--check` to `gates.adopt`.
