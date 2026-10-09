---
name: hw-from-spec
version: 0.11.15
description: Run a hardware project (a PCB, a printed or CNC enclosure, or both — scope chosen at kickoff; contract fab such as JLCPCB) from a written specification to a production cut with an owner-gated, generated-only, blind-reviewed workflow — a kickoff questionnaire that asks every owner decision up front with recommended answers, a zero-warning manufacturability bar, and a retro that folds each project's learnings back into the skill. Use this whenever someone starts a board or enclosure project from a spec, asks to set up gates, a decision log, generators, part verification, a fab DFM mirror, a case pipeline, FEA, blind reviews, a release report or a production cut for one, or resumes such a project, or wants the skill improved from a finished project — even if they only say "new KiCad board", "order this at JLC", "review the layout", "cut the release" or "what did we learn".
---

# hw-from-spec

A repeatable process for taking a board, an enclosure, or both from a written spec to fabrication and a production document set, with humans
deciding at gates and agents doing everything else through generators. Every rule below cites the reference that carries the detail; read the
reference when you reach that step, not before. Nothing here is specific to one board: project constants live in `project.yaml`
(`references/project-yaml.md`). **Scope** (`project.scope`, kickoff A0): `ee` = PCB / PCBA only, `mech` = enclosure / printed / CNC parts only,
`both` = a housed board. A heading tagged `[ee, both]` or `[mech, both]` applies to those scopes only; an untagged section applies to every scope.

## 0. Day-1 setup (do this before any CAD)

1. **Install — ONE layout, ONE block (README "Install")**: the skill is a submodule at `vendor/hw-from-spec` with a RELATIVE symlink `scripts ->
   vendor/hw-from-spec/scripts` (or a copy of `scripts/`). A personal clone under `~/.claude/skills/` is for skill discovery only and never the
   project's scripts source. Never put a submodule AT `scripts/`. **One venv**, the project's `.venv` (gitignored): pyyaml + `numpy trimesh scipy
   shapely rtree networkx mapbox-earcut embreex` in every scope. The smoke runs the print-DFM selftest. The mesh scripts `print_dfm.py` /
   `thin_wall_census.py` / `thin_wall_check.py` / `step2stl.py` need them in mech / both. Build it with `uv venv` + `uv pip install`, or
   `python3 -m venv` + `pip` when `uv` is absent. `tools.python`, the step-5 loop, the smoke and `evals/run_evals.py` use it. The smoke takes the
   caller's project `.venv` first, and the skill's own `.venv` only when run from the skill repo. It skips the mesh section with a NOTE when the
   libraries are absent. The shell gates take the first interpreter that imports yaml and print which. **Every Python command in this document
   that reads `project.yaml` is run as `.venv/bin/python scripts/<tool>.py …`**. The scripts are executable, but their shebang is the system
   `python3`, which has no pyyaml on a stock machine. Only `scripts/project.py scaffold | slots`, `step2stl.py`, `scad_lint.py` and the two
   `thin_wall_*` selftests run bare. The `.sh` gates take the first interpreter that imports yaml (`$PYTHON`, the project `.venv`, `python3`) and
   print which.
   **Then the kickoff questionnaire (§0.1)** — A0 scope first, then every owner decision the scope needs, asked up front with recommended
   defaults, written into `project.yaml` and `90-log/DECISIONS.md` before any CAD.
2. **Copy the templates and resolve the scope** — ONE copy block, runnable from the project root: README "Use in a new project" step 4. It sets
   `A0` (the scope), creates the numbered folders the scope needs, and copies the templates from the mirrored templates tree (`templates/90-log/*` →
   `90-log/`, …). It ENDS with `scripts/project.py scaffold --scope "$A0" …` over every copied file and `scripts/project.py slots`. Template
   lines tagged `{{ee,both}}` / `{{mech,both}}` / `{{mech}}` stay only in their scopes (one template set, no copies). The arrival checklist yaml
   is NOT copied on day 1 (§10.1: at the order). **The slots are filled in two passes**: `scripts/project.py
   slots` lists every unfilled `{{…}}` per file. The STATUS pause-point skeleton between its `<!-- skeleton -->` markers is excluded. CLAUDE.md,
   project.yaml and the governance records are filled now from the kickoff answers (§0.1). The slots of 10-spec/SPEC.md / KICKOFF_ANSWERS /
   traceability are filled after the spec is read (step 6). The count must read **0** before the G0 ask, not before the kickoff. What each scope creates: **ee** — the board
   paths (`paths.board`, `netlist`, `fab_dir`), `fab_dfm`, the PCB report, G1 / G2 gate rows, ERC waivers, the electronics parts seed; no
   `print_targets`, no `case_yaml`. **mech** — `print_targets`, `case_yaml`, `paths.mech_record` (the STL set whose md5 is the record id),
   `mesh_provenance` for the imported STEP / envelope, the case report, M1 / M2 / case-order rows. Scope mech creates no CAD project, no ERC / DRC,
   no fab DFM mirror and no electronics parts seed. Parts verification stays for hardware (inserts, magnets, feet, screws). **both** — everything, as before.
   The docs/ layout (`references/project-yaml.md` §Layout) is the one the defaults name. Re-laying it out later is a decision row + a `reorg:` block +
   `scripts/reorg_paths.py --apply/--check/--proof`, never a hand sweep. `{{SKILL_COMMIT}}` = `git -C vendor/hw-from-spec rev-parse --short HEAD`.
   `{{DATE}}` = today. `{{SKILL_VERSION}}` = the `version:` line of `vendor/hw-from-spec/SKILL.md`. `project.owner` = the person who writes the gate
   cells (`scripts/gate_check.py --release` compares the release line's git author with it). The CC-001 row ships in DECISIONS.md. It is the
   template's own first agent row: "process = this skill at commit X". Its evidence cell is filled after step 6 (selftests / smoke / adopt gates
   green at a named commit), not before. Slots inside a path (`30-board/kicad/{{BOARD}}/…`) are filled unquoted.
3. **project.yaml** (from `templates/project.yaml`: paths, id prefixes, markers, tools, the day-1 gate lists; the G1/G2 lines stay commented
   until those artefacts exist). Everything a script needs is there; no script carries a project constant (`references/project-yaml.md`).
4. **90-log/ENV.md**: tool versions, the CAD CLI paths, which endpoints answer (verify each by running it). Run the CAD CLI once on a trivial
   file and note the file-format version. ENV.md also holds the host row from `scripts/project.py env`: cores, RAM, the heavy-job pool and memory
   floor `scripts/jobs.sh` derives (`references/agent-ops.md` §8). Put every tool path behind the `tools:` block — twenty generators with hard-coded
   paths cost a CI day later (`references/pitfalls.md` ci/tooling).
5. **Prove the toolchain** (README step 3). Run `export PYTHONDONTWRITEBYTECODE=1; for s in scripts/*.py; do .venv/bin/python $s --selftest; done; for s in
   scripts/*.sh; do $s --selftest; done; vendor/hw-from-spec/smoke/run_smoke.sh; .venv/bin/python vendor/hw-from-spec/evals/run_evals.py`. All must be green
   before the spec is read. The smoke's enforcement section proves with negative cases that a tampered record, an uncensused body, a commented
   gate line and a non-owner release line all FAIL.
6. **First records** (the smoke's sequence, in a new project; `PY=.venv/bin/python`). First fill the slots of CLAUDE.md / project.yaml / the
   records. `$PY scripts/project.py slots` names them. An unfilled `project.yaml` is not valid YAML, and every reader says so. Then run
   `$PY scripts/known_issues.py` → `$PY scripts/traceability.py`. **Exit 1 = a decision row without a traceability entry or a FAILED check. Every
   D-/CC- row, the kickoff rows included, needs an entry in `20-design/traceability.yaml`: add it and rerun**. Then run `$PY scripts/release_report.py`
   (DRAFT, record MISSING: correct before G1 / M1) → `$PY scripts/now_pages.py` (the five answers of `00-now/`; `--check` is in the day-1 gate list)
   → commit. Then `scripts/adopt_gates.sh` (day-1 list + clone gate) green → `$PY scripts/project.py kickoff --check` green. That check passes when
   every answered kickoff row has landed in project.yaml with a real D row. Then fill the
   CC-001 evidence cell and the first STATUS paragraph → commit. Only now read the spec. Fill 10-spec/SPEC.md / VERIFY / traceability. `scripts/project.py
   slots` reads 0 before the G0 ask (§1.1 says what happens at G0).
7. **CI (optional, when the repo has a remote)**: `templates/ci/` holds pr-check / nightly / release workflows with `{{PROJECT_*}}` placeholders.
   Fill them with the recipe in `templates/ci/README.md`. The recipe copies `setup_linux.sh` / `nightly.sh` / `release_archive.sh` and writes
   `project.env` into the PROJECT-OWNED `ci/`, never under `scripts/` = the submodule. Every checkout has `submodules: recursive`. Commit the
   workflows under `.github/workflows/`.
8. **Repository conventions, all on day 1** (kickoff H3 carries them as defaults; `references/project-yaml.md` §Layout rules 5–7,
   `references/release-and-cut.md` §12–§14). One folder per product and the machinery split the same way (`gen/board/`, `gen/case/`); never one
   `tools/` folder that mixes products; never a generated CAD file or a build script at the repository root. Shared inputs (concept image, logo,
   font outlines) in one `assets/` folder whose README names the product that uses each file. Build output gitignored and deletable; each check
   keeps its scratch under its product's `build/_check/`. A `README.md` in every folder. The release folder written by the cut, named by use, its
   README the manifest. The order record beside the manufactured files. A clean tree after every build. A project that adopts the skill late
   does all of it in ONE pass. One project spent six restructuring passes, one per owner question. The questions were "why is the release folder not structured",
   "the files are not identifiable" and "there is still a top-level tools folder". Then came "is the version we sent a release asset", "are the order
   settings backed up" and "a README in every folder".
9. **Write to the standard** (`references/writing-style.md`): every README, record, kit text, vendor reply and chat report follows the Google
   developer style, ASD-STE100 sentences and Zinsser's four principles; `scripts/style_lint.py --project <root>` is in the day-1 gate list.

### 0.1 The kickoff questionnaire — every owner decision up front, with a recommended answer (`references/kickoff-questionnaire.md`)

Before the spec is read and before any CAD, ask **A0 Scope** alone (`ee` / `mech` / `both`). RECOMMENDED = what the brief implies, `both` when a
board is designed and housed; each option says what it skips. Then ask **every decision class that scope needs**, grouped by phase. Ask them in up
to twelve batches with the **`AskUserQuestion` tool** (≤ 4 questions per call, ≤ 4 options per question). "accept every recommended answer of this
batch" is the first option of the batch's first question. The classes are: product / process / material / quantity. PCB build [ee, both]:
layers, copper, impedance, finish, min part size + link policy, assembly sides, test points, panel. Enclosure architecture [mech, both]: pieces,
retention = screws + inserts / magnets / none, coupling, feet, labelling = deboss / plate / badge, fan, vents, light pipe, two targets, brand
marks = ironed top-face feature / flush AMS colour body. The manufacturability bar per target and what may be waived (default: zero / zero /
nothing). Verification: coupons, dummies, review rounds per gate, visual inspections, vendor API read before the order, FEA. Bought parts:
acceptable verification sources, the blocked-source rule, stock floor. Software / test posture [ee, both]. Release / cut / CI / the retro.
Identity, envelope and delegation. **Every question carries its scopes. A question outside the scope is not asked (KICKOFF_ANSWERS row
`n/a (scope)`), and a batch with nothing applicable is skipped.** **Every question lists its RECOMMENDED answer first (marked) and two or three
alternatives with a one-line consequence**. Each batch opens with "accept every recommended answer of this batch". Answers go into
`10-spec/KICKOFF_ANSWERS.md` (`templates/10-spec/KICKOFF_ANSWERS.md`), one owner D row each. The agent transcribes the owner's words, quoted, or
writes `accepted recommended` when the default stood. The machine-readable values go into `project.yaml`: `project.scope`, the `kickoff:` mapping, the
`board:` block, `fab_dfm.bar`, `print_targets.<t>` incl. `dfm_process`. Every answer class has a landing key in `templates/project.yaml`.
**`scripts/project.py kickoff --check`** fails on an answered row whose key is unset or whose D row is missing. Each row also gets a traceability
entry. Then commit. A deferred question is an OPEN D row that blocks the phase needing it; an answered question is never
re-asked, and a later change is a superseding D row (rule 2).

## 1. Phase / gate model (per scope)

- **ee**: **G0** spec approved → **G1** schematic approved → **G2** layout approved → **fab DFM** (§7) → **submission** (fab package, order =
  owner's click) → **release cut** → **production cut**. No case gates, no print DFM.
- **mech**: **G0** mechanical spec approved → **M1** geometry approved → **M2** first article / fit print approved → **case order** (owner's
  click) → **release cut** → **production cut**. G0 covers envelope, interfaces, materials, print / CNC target, and fit inputs: a board STEP /
  mesh or dimensions, each tagged [V] or [K]. M1 covers every body generated from `20-design/case.yaml`, six face renders read, clearance rows ≥ 0
  against the fit input of record, and a fit row pair per degree of freedom. M1 also covers census + pinch + slicer clean, vendor DFM clean by API
  read, hardware [V], `case_dfm` + mechanical-intent round merged, and the double-blind drawing round merged. M2 covers the caliper table,
  coupons and the mating part fitted. A deviation is a yaml knob → new case version → M1 re-run. The record id is the STL set's md5
  (`scripts/project.py record`, `paths.mech_record`), never a board md5.
- **both**: the ee chain with the case pipeline (§8) hanging off G2 and the **case order** gate beside the board order, as before.

The release cut = reports RELEASED, collateral, tag; the production cut = document set, tag (§10). Each gate's prerequisites are the row in
`90-log/GATES.md` (`templates/90-log/GATES.md` carries the rows of every scope; `scaffold --scope` keeps yours).

- The owner writes the gate line; agents never do. `90-log/GATES.md` approval cells and the release line (`markers.release_regex`, in the
  Release row's approval cell) are owner text. **`scripts/gate_check.py <gate>`** reads a cell (exit 1 while empty). **`--release`** reads the release
  cell plus its git author, which must be `project.owner`. The report banner reads the same function and says **DRAFT** until the owner's committed
  cell exists. A cell an agent wrote or committed stays DRAFT (`scripts/release_report.py`; the clone gate blames the line in the real checkout).
  The author check holds only while agents commit under their own identity (`git -c user.name='<agent>' -c user.email=<agent>@localhost commit`).
  The owner's commits keep the owner's identity.
- Do not start the next phase's CAD before the gate line exists. Every project generator of the next phase calls `scripts/gate_check.py <gate>` first
  and refuses while it is 1 (the placement script before G1, the case geometry before G0 / M1, the fab package before G2). If the owner delegates
  ("proceed, I retro-approve"), quote the instruction under the table of `90-log/GATES.md`. Keep the approval cells empty.
  The quote is one line that names its gate: `> delegated: <gate>, <owner>, <YYYY-MM-DD HH:MM>, "<owner words>"`. A G1 line does not cover G0.
  `scripts/project.py gates-required` fails while a next-phase artefact exists and its gate has neither a cell nor that line.
- **One review round precedes every gate**. It is defined once and used everywhere. For every role of the round's role set, a round has one
  in-session reviewer + two external models of a second model family. The in-session fallback may stand in for the external models, and the merge
  says so. Each role also gets one verifier with record access. The round produces one merged report (§5). "Two reviews" in an older record
  means one round.
- Never quote the release phrase in prose anywhere the regex can see it (a sentence that explains the rule matches the regex) — describe the
  marker indirectly (`references/pitfalls.md` process).

**Who decides what** (D rows carry the owner's decisions — the agent transcribes the owner's words into them, quoted; agents write CC rows and ask):

| Phase / item | Decider | Where it is recorded |
|---|---|---|
| kickoff answers (scope, product, process, materials, enclosure architecture, DFM bar, verification, sourcing, software, release) | owner | `10-spec/KICKOFF_ANSWERS.md` → D rows, `project.yaml` |
| G0 / G1 / G2 / M1 / M2 cells, the board order click, the case order click, the release line | owner | `90-log/GATES.md` |
| a spec value, part, topology, pin change | owner (agent proposes a CC row OPEN) | DECISIONS |
| the manufacturability bar and any waiver of it | owner (default zero / zero / no waivers) | D row + `fab_dfm.bar`, `print_targets.<t>.accepted`, `dfm_accepted` |
| print-target numbers (`print_targets`), design margin, first-article tolerance | owner (agent proposes from the vendor sheet) | `project.yaml`, D row |
| an FEA WARN / a margin below the limit | owner (agent reports the number, never accepts) | D row cited in `FEA_REPORT.md` |
| test criteria limits (T-nn) and the software's refuse-vs-warn posture | owner (agent drafts from the spec) | `20-design/test_criteria.yaml`, D row |
| FEA case set, review roles, generator design, delegated copper rules | agent (CC DECIDED within the delegation) | CC rows |

### 1.1 At a gate (asking the owner)

1. Prerequisites first: the row's prerequisite cell in `90-log/GATES.md` is satisfied and provable. The proof is the merged review report committed and the scope's
   checker outputs: ERC / DRC files [ee, both], census JSON + `DFM_ROUND.md` [mech, both]. `scripts/adopt_gates.sh` is green at HEAD, and
   KNOWN_ISSUES §2 lists only items the owner has seen. If one is missing, say so and stop.
2. Write the STATUS pause-point paragraph. It names what was reviewed (commit, SPEC rev / board md5-8), the merged report path and the OPEN rows
   the owner must decide. It ends with the exact ask: *"Write the Gn / Mn cell in 90-log/GATES.md: `<your name>, <date>, <SPEC rev | schematic commit | board md5-8 | case version + record md5-8>`"*.
3. Ask in one message with that sentence; do not start the next phase's CAD while waiting (other work — docs, tests, tooling — may continue).
4. A valid cell is owner text in the approval column of that row; `_not yet approved_` is empty. **Agents never write approval cells or the
   release line**, not even when told "go ahead" in chat. Quote the chat instruction verbatim under the table as a `> delegated: <gate>` line (§1), and note
   "cell pending" in STATUS. Proceed only if the instruction explicitly delegates (§1 second bullet). The owner fills the cell later; the report banner and
   the release phrase are read only from the cells/lines the owner wrote.
5. After the cell exists: one STATUS paragraph "Gn approved (cell text)", regenerate the records, commit, start the phase.

### 1.2 The manufacturability bar (the gate rule the owner confirms at kickoff)
**Zero errors, zero warnings, no waivers**. The bar is recorded as an owner row on day 1 and enforced by a named check, never by prose. **board** — ERC
`scripts/erc_gate.py` 0 errors / 0 unaccepted warnings. An acceptance is a typed entry of `20-design/erc_accept.yaml` naming a live decision row; a
GUI exclusion or a stale entry fails. CAD DRC 0 errors / 0 unconnected / **0 warnings**, unless a dated waiver row + generated accept rule exists
(`references/pcb-layout-dfm.md` §14). Fab DFM mirror **0 open (0 Danger, 0 Warning)**, unless a `dfm_accepted` entry with refdes, reason, date and
vendor evidence exists (`scripts/dfm_check.py` reads `fab_dfm.bar`). **printed enclosure** — census 0 unaccepted FAIL per body per preset. Only a dated
`print_targets.<t>.accepted` entry with vendor evidence passes a cluster, re-matched against the yaml every run. `print_dfm.py` PASS on every
body of the STL set against the target's own process row, zero slicer warnings, vendor checker **no flag by API read**, no yellow / red on the heat
map. **CNC** — the vendor's DFM clean. **Who enforces each item:** the skill's scripts enforce ERC, the fab DFM mirror, the census and
print DFM; `kicad-cli pcb drc` enforces DRC. The project's slicer wrapper enforces zero slicer warnings. `scripts/vendor_gate.py` enforces the vendor API
flag and the heat map. Every STL md5 of record needs its filed reply (`<md5-8>_analyze.json`: success, parseStatus 2, thinWall false, the
same fileMd5) and six captures at 0 yellow / 0 red. Its line waits commented in `gates.adopt`; uncomment it with the first vendor round, before the case order. Both mesh gates glob the STL set of record (a body nobody checked fails), verify every record's signature
(a hand-edited record fails) and the rule-set version. `scripts/adopt_gates.sh` fails when a schematic / board / STL set exists and its gate line
is missing or still commented out in `gates.adopt`. It also fails when a next-phase artefact exists and its gate has no cell and no `> delegated:` line. `templates/90-log/GATES.md` carries the bar as a prerequisite on G2, the board order and the case
order. A WARN that is "known" is not a bar; it is either fixed or a dated, evidence-bearing acceptance the checker re-asserts every run.

## 2. Generated only

- Source of truth = `20-design/*.yaml` (+ placement CSV, part rows). Generators write CAD files, reports, indexes, order sheets. Nothing under
  `30-board/`, `40-case/`, the generated records is hand-edited; a review finding changes the YAML or the generator, then regenerates.
- Every generator has `--check` (regenerate in memory, diff against the committed file, exit 1 when stale) and `--selftest` (works in a temp
  dir only, never touches repo files). A `--check` must pass on `git archive HEAD`: no mtimes, no absolute paths, no live git HEAD, no dates
  outside one volatile `Generated` line (`scripts/release_report.py`, `references/release-and-cut.md` §2).
- Byte-stable output: rewrite UUIDs deterministically, process items in sorted order, pin the locale of every `sort` (`LC_ALL=C`)
  (`references/pitfalls.md` tooling/identity).
- A generator that owns part of a file another generator also writes must re-read and merge that part or refuse to run in place
  (a generator rewriting a shared file drops the other generator's content — `references/pitfalls.md` tooling/gates).
- Exceptions to the rule (an in-place hand-routed board, an owner GUI step) are allowed only as a logged decision row plus a "chain of record"
  table (commit, step, file md5, content signature). Assert the content signature and keep the md5 informational (`references/pitfalls.md` layout).
- Order of the chain after a change to the record of record (copper in ee / both, the STL set in mech): drawing / FEA → collector → commit → `clone_gate.sh --regen` → commit. Reports are regenerated LAST,
  in the same commit as their inputs (`references/release-and-cut.md` §3).
- **Every checker is read-only on the tree.** A `--check` builds in a temp dir and exports nowhere. `scripts/adopt_gates.sh` fails when
  `git status --porcelain` differs before and after the gates. The PR-check template ends with the same guard, because a checker that exports into
  the tree replaces a record. Probe a script's usage from its docstring, never by running it without arguments.
- **The tree is clean after every build** (`references/release-and-cut.md` §14). A build that rewrites a committed file of record without a design
  change (a re-saved board file, a stamp) is reverted with `git checkout -- <file>`; the file of record changes only in the commit that changes the
  record. A dirty tree stamps `-dirty` into every `git describe` a drawing or a manifest prints. Before a release, delete every `build/` folder,
  regenerate from empty and read `git ls-files` for strays.
- **Layout changes are generated too.** The docs/ layout the defaults name is in `references/project-yaml.md` §Layout. Moving files later is a
  decision row + a `reorg:` block + `scripts/reorg_paths.py --plan → --apply → regenerate → --check → --proof` (zero-loss on two `git ls-files -s`
  dumps). Frozen records keep the old paths, and `--map` explains them (`references/release-and-cut.md` §9).
- **Iteration tiers keep the fast loop honest.** Inner: after a one-value yaml or emitter change, run `scripts/iteration_gate.sh -- "<generator>
  --check" "<grader>"`. It runs the changed generator's `--check` and its direct grader (plus the project's standing set in `gates.iteration.inner`)
  under the same read-only guard as the adopt gates. It refuses an empty set. Standard: `scripts/adopt_gates.sh --no-clone` (`make gates`)
  before a delta audit. Release: `scripts/adopt_gates.sh` with the clone gate (`make check`) before a gate, order or cut. One `gates.adopt`
  list, never a second one; heavy commands go through the host pool (`references/agent-ops.md` §8 items 1 and 9).

## 3. Decision log

`90-log/DECISIONS.md` is one table, six cells: `ID | Date | Status | Topic | Proposal / decision | Reason`.

- **D-nn** rows are the owner's (text as issued); **CC-nnn** rows are the agent's. Status words: OPEN (needs the owner), APPROVED, DECIDED
  (within delegated authority), APPLIED (!) (applied ahead of the owner's look — the `(!)` is "the nod marker": the owner's nod is still wanted),
  REJECTED, SUPERSEDED, CLOSED. History follows the
  literal history marker `(was:` inside the status cell; generators stop reading there.
- Rule 2: a value, part, topology or pin assignment named in the spec is never changed silently. Write the CC row (reason, options, recommendation),
  mark it OPEN, ask. Apply only after approval, or ship it behind an optional flag that warns when omitted so the code path is tested now
  (`references/pitfalls.md` process).
- `90-log/KNOWN_ISSUES.md` is generated from the log: OPEN rows, rows mentioning OPEN, provisional rows, the nod section (KNOWN_ISSUES §2.1), blockers, the
  test plan's UNVERIFIED markers. Section 1 is hand-curated between markers (`scripts/known_issues.py`). Describe the nod marker indirectly in
  status cells or the generator re-triggers on the description.
- A literal `|` inside a cell is `\|`; the generator refuses a row with the wrong cell count. An ID is reserved only when its row is in HEAD:
  `grep -c '^| CC-nnn '` immediately before writing (CC rows; owner rows are bold in the template), hand numbers out with tasks (`references/agent-ops.md` §1).
- One record row per agent task, appended after re-reading the file; commit it right away with the exact-edit staging recipe when other agents
  share the tree (`references/agent-ops.md` §2).

## 4. Parts

- Tags: **[V]** verified live this session (fetch of the distributor / fab page: MPN, package, stock, basic/extended). **[K]** known but
  unverified (never fitted). **[K owner-read]** applies when the OWNER read a distributor page our tools could not fetch. It records date, who and
  which page, and stays listed in PROCUREMENT and the arrival checklist until a fetch of ours confirms it. **[S]** select-by-parameter (a row
  without an MPN yet). Never invent a fab part number; every check is a row in
  `60-orders/PARTS_VERIFICATION.md` with date, URL, stock (`references/part-verification.md`). Every scope: electronics on the fab's library
  (ee / both), hardware (inserts, magnets, feet, screws, adhesives) on the manufacturer's page + TDS (mech / both). A mech project's fit input
  (board STEP / envelope) carries the same [V] / [K] tag in SPEC §4 and `paths.mesh_provenance`.
- Gate value ↔ MPN ↔ fab code on every fitted part (the BOM groups by code: a value edited on the symbol does not change the ordered part).
- Stock gate is run-relative: qty per board × boards × attrition for every code, not "> 0" on a few.
- **VERIFY item** = a value or claim in the spec (or in a review finding) that rests on a datasheet, drawing or standard nobody has read yet.
  Examples: a current, a pin function, a footprint dimension, a reflow limit, a standard clause. The spec author tags them `VERIFY` in 10-spec/SPEC.md (or the
  G0 review lists them in `20-design/VERIFY.md`: item, part, what to read). Each is closed by a row in `10-spec/datasheet_notes/<part>.md` (page/section,
  value read, matches yes/no — `templates/10-spec/datasheet_notes/_TEMPLATE.md`) or moved to `90-log/BLOCKERS.md` when the source cannot be fetched.
  Rule 3: every VERIFY item touching a part is closed before that part is drawn; G0 requires all closed or BLOCKED; curve-only values are
  marked "not in datasheet text" with the reader named.

## 5. Blind reviews

Protocol (`workflows/README.md`, `references/agent-ops.md` §4):

1. Freeze: commit, `git status --short --untracked-files=no` empty, `git worktree add --detach <frozen> HEAD`, then `git -C <frozen> submodule
   update --init` (otherwise the skill submodule is empty there and `scripts` dangles). Reviewers read only there.
2. Hand-off document = the only briefing. Its header is generated by `scripts/handoff_header.py` (board of record, HEAD md5 MATCH, package,
   case version, clean tree) — a hand-off naming a board the worktree does not carry invalidates the review. Add the one-paragraph waiver list
   (no reasoning) so verifiers do not re-find accepted items each round.
3. Reviewers (the review round of §1): per specialty one in-session agent + two external models of a **second model family**. An external model is an agent CLI of another model family
   in `--mode ask`, read-only. When no CLI exists, use the in-session fallback and say so in the merge. Inputs are identical: the artefacts + the
   role's checklist, never each other's output, never the author's dispositions, never the decision log. Reports to `80-reviews/<ROUND>_<role>_<model>.md`.
4. **One verifier WITH record access** (DECISIONS, KNOWN_ISSUES, BLOCKERS, SPEC + its errata, the test plan, the netlist / mesh of record) on
   every finding. The default is REFUTED unless the worktree evidence supports it. The classes are **CONFIRMED / ALREADY DECIDED** (the row that
   decided it, and whether its number still holds) **/ REFUTED / PARTLY / UNVERIFIABLE**. The verifier adds corrected text and severity, and a
   **rev-impact column** (changes the ordered revision / bench check on arrival / next revision / record only). Reviewers re-find decided items at ~1:1 on a board and ~1:2 on a
   case: the verifier's record pass is what makes the merge cheap. A netlist or mesh claim is re-measured by the verifier (`<cad-cli> sch export
   netlist` + a short parser; trimesh on the STL of record), never taken from the reviewer.
5. Merge into CC rows. Dedupe by defect and build a corroboration matrix (finding × model). Classify each item **REQUIRED** (generator/YAML
   change, exact edit) / **OWNER** (proposed DECISIONS row text) / **DOCUMENT** / **ACCEPT** (reason). Give an explicit verdict (order as is / after
   REQUIRED / not yet) and reviewer-quality counts (findings, refuted rate, already-decided rate, empty runs). **Nothing from a review is applied without the verifier's
   row**; a CONFIRMED finding whose closure is a bench step becomes an arrival-checklist row (§10.1), not a silent backlog line. Commit the review
   files with explicit paths.
6. Visual gates READ the images (silk, renders, tiles): geometry checks passed boards with blank bars and mutilated words.

Templates: `workflows/blind-deep-review.js` (roles × models × verifiers × merge), `workflows/routing-inspection.js` (tiles ≥ 40 px/mm, two
inspectors), `workflows/silk-audit-verify.js` (audit → fix → blind verify A/B → merge+fix → re-verify), `workflows/delta-audit.js` (claims list,
changed specialties only). `{{EXTERNAL_MODELS}}` needs at least two distinct models (role i gets entries i and i+1; the template throws otherwise).

**The `case_dfm` role** [mech, both] is a printed-enclosure DFM specialist. It is in the `board` role set of `blind-deep-review.js`; in mech
scope the M1 round's role set = `case_dfm` + mechanical intent. Its checklist is
`templates/CENSUS_GATE_ROWS.md` + `references/dfm-printed-enclosure.md` §1 (walls, voids, wedges, opposing faces, inserts, tolerances, orientation,
closed rims, retention present in the mesh). Its verifier re-runs `scripts/thin_wall_census.py --target <t>` on the frozen worktree's STLs and
compares with the census JSON of record. Required before the case order (`templates/90-log/GATES.md`).

**The double-blind drawing round** [mech, both] (the M1 round for a printed part, beside `case_dfm`): the drawing sheet is generated from the
exported meshes with its self-checks (`references/case-pipeline.md` §Drawings). Reviewer A gets ONLY the sheet and a one-paragraph design
intent, and reports what the sheet says the part does and where it cannot. Verifier B measures every claim of A on the meshes of record and
classes each **VERIFIED / REFUTED / DRAWING DEFECT / JUDGMENT**. Cost: about one agent-hour. On a case with 14 passing fit rows and a clean print
DFM one round found two design defects (a board free to slide along its slot, bosses removed by the cavity cut) and a dozen drawing defects.
A design defect becomes a fit or mesh row before the fix (`references/case-pipeline.md` §Interference, §Process rules).

**The G0 round (spec review)** uses `blind-deep-review.js` with `{{ROLE_SET}}` = `spec`. It has four roles. Spec coherence covers requirements, interfaces,
numbers that must agree and the VERIFY list. Parts and sourcing covers every named part fetchable live, tags, alternates and stock for the run; in
mech scope it covers the hardware lines. Mechanical intent covers envelope, connectors, case concept and thermal; in mech scope also the fit input's
provenance and tag. Test plan checks that every requirement has a measurable check. The artefact is `10-spec/SPEC.md` (+
`60-orders/PARTS_VERIFICATION.md`, `20-design/TEST_PLAN.md`, the case concept); the hand-off (`templates/REVIEW_HANDOFF.md`) lists 10-spec/SPEC.md with its md5
in §2, and the generated header's board / package / case rows read **MISSING by design** — say so in the hand-off. Verdict options: approve the
spec as is / after the REQUIRED edits / not yet. Merged report `80-reviews/G0_merged.md`; REQUIRED edits go into SPEC (owner text: OWNER rows,
agent proposals: CC rows OPEN), the VERIFY list is closed or BLOCKED (§4), then the G0 ask (§1.1). G1 pack and roles: `references/schematic-phase.md` §4.

## 6. Layout phase and the adopt rule [ee, both] (G1→G2: `references/pcb-layout-dfm.md`; G0→G1: `references/schematic-phase.md`)

The layout chain (placement CSV → router session → post-pass → silk → export → `80-reviews/G2/` pack), the PCB build rules tagged checker / fab
capability / physics / owner choice (stack-up, impedance, copper minimums vs the fab table, via-in-pad, thermal reliefs, mask / paste / stencil, <!-- style: ok -->
part-size policy, two-sided assembly, rotation / CPL, fiducials / test points, silk, courtyards, creepage, panel) and the DRC census live in
`references/pcb-layout-dfm.md`. A routed board is adopted only when all of these hold on the committed tree. CAD DRC 0 errors / 0 unconnected / **0 warnings
unless a dated waiver row**. Schematic parity 0 with the net classes enforced. Prove it with a canary rule, a deliberately violated generated
DRC rule that must fire exactly once, because the CLI may ignore class patterns. Route-quality 0 unjustified HIGH, the fab DFM mirror 0 open
(§7, §1.2), silk check 0. Every generator `--selftest` and `--check` green, and the fresh-checkout gate passes on `git archive HEAD`.
`scripts/adopt_gates.sh` runs the `gates.adopt` list then `scripts/clone_gate.sh`; the routed board + its router session file are the artefacts of
record (routing is never re-run to reproduce them) (`references/pitfalls.md` layout, kicad/drc).

## 7. Fab DFM mirror [ee, both]

Mirror the fab's own DFM checker in-repo before the first quote: copy its thresholds into `20-design/dfm_thresholds.json` (source + date), let the
project's measurer emit items, grade with `scripts/dfm_check.py`. The rule every viewer used: a value EQUAL to the warning threshold is Warning —
design strictly greater. **0 Danger / 0 Warning is the bar** (§1.2): acceptances are by refdes with reason, date and vendor evidence
(`dfm_accepted`, fields named by `fab_dfm.bar.accepted_requires`); bare tracks/vias cannot be accepted. Run the fab's own checker on the board AND
the PANEL upload before the order and diff its counts against the mirror (`references/fab-dfm.md`; JLC numbers there as the worked example).

## 8. Case pipeline and FEA [mech, both]

`20-design/case.yaml` → OpenSCAD source → STL per piece → census (wall thickness by entry surface, connected components, membranes) → interference
against the board mesh of record → FEA → drawings → print-service / CNC DFM + quotes. The interference step reads the provenance sidecar
`paths.mesh_provenance`: board md5 + mesh md5 in `both`. In `mech` the sidecar holds the imported STEP / mesh or the owner's envelope with its
source md5 and [V] / [K] tag. A [K] envelope is a KNOWN_ISSUES §2 item until measured. Print-target
presets as `base + overrides` deep-merged before any module reads the yaml; drawing and FEA apply the same merge (`references/case-pipeline.md`).
FEA: Gmsh + scikit-fem; fTetWild for CGAL STLs; caches keyed on content; compact nodes after dropping elements; NaN must read FAIL
(`references/fea-stage.md`). Every md5-stamped consumer runs after the final STL pass (CGAL exports are not byte-stable).
- **Imported body.** A part the owner already has as CAD enters the chain through `scripts/step2stl.py part.step --out …/stl/<piece>.stl --tag V|K`.
  Its back ends: cadquery / FreeCAD CLI / `--canonical` on a CAD STL export. Its outputs: canonical STL + provenance sidecar + the OPEN decision
  row it prints. Then the body is censused and print-DFM-checked like a generated body (`references/case-pipeline.md` §0; the M1 row accepts it under its row).
- **Stability.** Anything that stands, rocks, walks or is set down free gets a CoG-vs-support-polygon row at its WORST pose (`scripts/stability.py`,
  `references/case-pipeline.md` §Stability). The row takes the centre of gravity from the STL set with an infill factor per body, through the
  assembly transforms, against the hull of the ground footprints. The min margin over every pose is ≥ a stated value. A render cannot show it: a walker with its drive behind
   the legs tips at the poses where one foot per side is down, and every render looked fine.
- **Assembly model.** Renders and animations are previews of the model, not evidence that it can be built. The three transform rows are these
  (`references/case-pipeline.md` §Assembly model). (1) Every instance placement is a proper rotation: `det +1`, one CHECKS row, FAIL
  (`scripts/stability.py improper_placements`). A det −1 placement is a mirror no process can make. A part that only fits mirrored needs a
  mirror BODY with its own mark, decided on the parts list before the first plate (`references/dfm-printed-enclosure.md` §1.5, kickoff C1–C2).
  (2) A FIT row per mating pair the design knows about (shaft ↔ bore, D ↔ D socket, peg ↔ hole, tab ↔ slot, pin ↔ pivot). It compares feature
  direction vs mate direction through the real placements, within a stated tolerance (≤ 1°). (3) An ORIENTATION row per part type with a one-sided
  feature (slot opening, peg direction, a face that must point at its mate or the ground). A whole side drawn mirrored, every mating flat 180° off its
  socket and an inverted one-sided part each survived days of renders and a per-side 2D sweep. The rows catch them in seconds.
- **Fit rows per degree of freedom.** A fit test at nominal positions proves nothing about the directions a part moves in. Per part, write one row
  pair per degree of freedom (each shift, lift, the 180° turn of a symmetric part). The row moved less than the play is empty; the row moved more
  overlaps its stop (`references/case-pipeline.md` §Interference).
- **Point contacts.** Before any mark-shaped body or pocket (inlay plate, badge, deboss) run `scripts/thin_wall_check.py --pinch <stl>`: a traced
  outline of touching shapes pinches to 0.01 mm and the part arrives as lobes; a wall census cannot see it. Bridge with web discs clipped to the
  outline's closing, add the neck row, keep the components = 1 row (`references/case-pipeline.md` §Point contacts).
- **A case-version bump re-runs every keyed stage**. Every STL md5 moves and every FEA mesh rebuilds, which takes tens of minutes (the cost
  table is in `references/case-pipeline.md`). Run case FEA / PCB FEA / drawings / the alternative preset through the job pool as background jobs
  and block on their EXIT lines. Budget it before promising the full pipeline.

### 8.1 DFM for printed enclosures [mech, both] (before the FIRST quote — `references/dfm-printed-enclosure.md`; CNC: `references/cnc-enclosure.md`)

Acceptance bar (§1.2, owner row at kickoff): **0 FAIL / 0 WARN in every check table and census · zero slicer warnings · no vendor flag by API
read**. It also needs **no yellow, no red on the vendor's heat map · every face rendered and looked at · no waivers**. A row is PASS / FAIL on a MEASURED value
(from the MESH, never the yaml) or it is INFO (no verdict, own table, the reason stated). "kept below minimum (listed)" is a waiver, and a waived
sub-minimum wall cracks in service. **Every number is a `project.yaml print_targets.<target>` value**: vendor, process, material, wall /
void / red gates, design margin, tolerance + source, max bbox the rule was calibrated at, checker URL + date, post-process, rating, `accepted`
list. The reference tags each **[checker]** / **[vendor sheet]** / **[physics]** / **[owner bar]**. The numbers below are one MJF checker's line on
~150 mm parts and a 0.4-nozzle FDM printer's. Substitute yours and keep the mechanism.
1. **Two PURE mesh gates on every body of every preset, before the first upload** — the census gates `wall_gate` (the checker's line), the print-DFM check the
   printability FLOOR. The case generator draws walls at `wall_gate + design_margin`. The census FAILs a nominal wall under `wall_gate + design_margin − 0.05` (row MARGIN; 0.05 is the census's sampling noise).
   A wall drawn at the gate therefore FAILs before the vendor upload (`references/dfm-printed-enclosure.md` §2).
   Both gates read the MESH, never the yaml; both glob the STL set of record and sign their records:
   - `scripts/thin_wall_census.py <stl> --target <t> --json 40-case/<set>/checks/census/<piece>.json` (rows `templates/CENSUS_GATE_ROWS.md`). It checks walls AND voids
     against the target's gates, wedges by the width of their sub-gate band, and the nearest OPPOSING face in any direction, with samples ∝ area.
     It also has a NOISE-FLOOR row and rows for bodies = 1, geometry signature, retention present in the mesh, worst-case clearance per mating pair
     and six face renders. The only exception path is a dated `accepted` entry with vendor evidence, re-matched every run. The rules:
     `references/dfm-printed-enclosure.md` §2.
   - `scripts/print_dfm.py --process <row> --out 40-case/<set>/checks/dfm <stl>` → `PASS` or `FLAG` + one line per rule. The rules are M C W R Z F K P V H O B S + INFO L Y, from
     physics + the cited minimums of `20-design/dfm_processes.yaml`. FLAG = a real sub-minimum region on the mesh: fix the generator, re-export, rerun.
     There is no waiver field. The rules, the sidecars (`--boxes`, `--supports`) and the loop: `references/print-dfm.md`.
   - In `gates.adopt`: `thin_wall_census.py --gate-dir` and `print_dfm.py --gate`. They exit 1 on a body without a same-md5 record, md5 or signature
     drift, or a rule-set / threshold mismatch. They also exit 1 on a FLAG without `--open <tag>/<piece>=<OPEN decision row naming the piece>` or
     `--expect <tag>/<piece>=<reason>` for a body that FLAGs BY DESIGN. Both flags are printed on every run, and the record still says FLAG.
   - After every vendor verdict: append the row to `60-orders/quotes/dfm_verdicts.yaml`, then run `print_dfm.py --validate`. **vendor FLAG + ours PASS =
     RULE DEFECT (exit 1)**: fix the physics in the rule, bump its `VERSION`, re-validate, run `scripts/skill_retro.py`. Vendor PASS + ours FLAG =
     stricter, reason recorded, the rule stands. A new vendor or process = ONE cited row in `20-design/dfm_processes.yaml` (`[V]` URL + date or `[K]`
     with the source). A 404 = `null`, and the row refuses to gate. Kickoff C8a names the row per target (`print_targets.<t>.dfm_process`).
   - Generated code is linted on every emit (`scripts/scad_lint.py`: a mid-line `//` silently drops the rest of the statement line).
2. **Geometry rules — checker vs material**: no FREE-STANDING wedge (rail tips, lips, non-tangent coves, knife edges) **[checker]**. Chamfers
   and **tangent fillets cut into ≥ gate walls are fine and recommended at stress risers** **[physics]**. **Snap features are possible in PA12**
   **[physics]**, but under a vendor's no-yellow bar the ≥ void-gate slit rarely fits. So screws + inserts or magnets (`§1.1` of the reference) are
   the default. **Engraved text is allowed when the stroke ≥ the void gate** (cap ≥ ~6 mm at 1.2), else use a label carrier. Closed rims: no slot /
   notch / gap on the single part unless it has an obvious job **[owner bar]**. Designed asymmetries are rendered + in the order sheet + KNOWN_ISSUES,
   or removed. Inserts / bosses / magnets are sized per material from the TDS (bore, depth, boss ≥ 2 × insert OD, temperature). Post-processing
   removal and the material rating (UL 94 / HDT) are named on the order sheet. Re-derive every yaml value set against an older print rule. A feature
   that cannot be clean in its space budget goes. Every wall change reruns the whole table.
3. **Canonical STL + geometry signature** (own binary writer, sorted triangles, normals from the float32 vertices; volume / area / bbox / facets
   beside the md5), so the md5 IS the geometry. The census gate, vendor uploads and the cut key on it.
4. **Vendor quote page** (`references/dfm-printed-enclosure.md` §7, record `templates/DFM_ROUND.md` under `60-orders/quotes/<date>/`). Owner consent
   to upload is quoted in the decision row. ONE STL per page session. The verdict of record is the vendor's analysis API response, never a page
   reading. The flag is computed at upload, independent of the material on the line; set the material anyway for price and legend. The RAW
   JSON is saved. Vendor volume / area / bbox = ours. The heat map is read on every face. The coordinator re-reads a worker's "no flag" itself.
   Nothing is saved, carted, agreed or paid. **The vendor's thin-wall metric is length-dependent** (the reference's §7.1). A coupon or short probe
   passing proves nothing about the full-length body. When a body is flagged and the census is clean, slice the body of record into capped slabs
   and build full-length one-knob probes. Upload each alone and adopt the first full-length pass.
5. **Home FDM preset (`home_fdm`)** (`references/dfm-printed-enclosure.md` §8–§9, the kit `references/print-kit.md`, slicer knobs
   `references/fdm-print-optimisation.md`; kickoff C9 / C10 / C11). It has printer-first FAIL rows from `print_targets.home_fdm`: walls, ribs, voids, 2 × line
   width, elephant foot, hole shrink, seam as per-preset `fits` knobs. Raised legends need cap ≥ 5.1 and strokes AND air gaps ≥ 0.9, with the gap
   read as an opening of the complement. Every external face on the bed / vertical / clean top is asserted from the g-code. Coupons and both board
   dummies (printable stand-ins for the board: a two-piece and a one-piece version) come before the part. Brand marks are an ironed top-face
   feature or a flush colour body laid down by the printer's multi-filament unit in the bed layers. Never use a bed-face or vertical-wall deboss
   for a mark. Print the mark coupon first. The mark rows are FAIL-gated. A roof-down piece is turned by `rotate()`, never `mirror()`, because a
   mirror flips handedness and prints every asymmetric mark backwards. The preset also has slicer projects with project-named presets, a
   floating-region warning = FAIL, and auto-orientation. **Every vendor DFM decision is mirrored into this preset the same day** under its own
   version key. Hook tokens keep the vendor SCAD byte-identical, every hook variable is asserted defined, and duplicate yaml keys are gated.
   ONE kit folder per print target, `50-kits/<kit>/` = pieces + coupons + both dummies + READMEs **+ a generated START_HERE**. The folder holds
   START_HERE at its root, `plates/` + sidecars, `parts/` and `sheets/`. It is mirrored byte-identical to `~/Downloads/<project>_kits/<kit>/`, and
   superseded kit folders are reduced to a one-line `SUPERSEDED.md`. Every kit text goes through the kit text gate (the FAIL check over every
   emitted kit text, `print-kit.md` §3). Glued plates rest on the lands (the flat bed-face seats) with the bridged strips one layer below. Snug
   fits ship as a bracket plate the owner picks from: one object per candidate value, each a copy of the part that CARRIES the knob, tried on one
   production mating feature. The picked value lands in `kickoff.enclosure.fit_result` and closes its arrival-checklist row. Each STL has a
   watertight row. Sidecars are drift-checked against the 3MF config.
6. **When a vendor reports a cracked part**: measure the RECEIVED part (caliper table → the target's tolerance), photo protocol, fractography
   basics. Then measure the ORDERED STL (sections + census with span and class). Separate design intent from defect with the vendor-fault table.
   Draft the reply from the template for the owner. Then apply the learning design-wide (every body, every preset), not to the failed feature
   (`references/dfm-printed-enclosure.md` §10).

## 9. Software track [ee, both] (optional)

Bring-up tool first (a `--selftest` that needs no hardware, `--dry-run`). Then the architecture note, criteria as YAML the tool reads, and PASS / FAIL
/ INCONCLUSIVE with reason codes the manuals are generated from. Safety guards stay optional flags before the owner's nod (`references/software-track.md`).

## 10. Release cut and production cut

**The record id** every md5-keyed consumer uses (collateral folder, report identity, tag message, `70-release/<rev>/`) is
`scripts/project.py record`. It is the board file in ee / both, and the STL set of record (`paths.mech_record`, md5 of the sorted `<path> <md5>`
lines) in mech. A moved STL moves the id, exactly as a copper change does.
Release cut: `scripts/release_report.py` (every number from a file, MISSING printed, DRAFT/RELEASED from the gate file), collateral incl. renders
(`scripts/collect_renders.py`, keyed on the record md5 + camera args), release notes from `templates/RELEASE_NOTES.md` with a source next to every
number, annotated tag. Production cut: `templates/production_cut.yaml` lists every deliverable (kind, path, check, inputs, required, owner
placeholders). **One project-side generator** (`gen/production_cut.py`) builds `70-release/<rev>/` with MANIFEST + STATUS. The contract is
`references/release-and-cut.md` §7; the skill ships the yaml and the contract, not the generator. `[OWNER: …]` fields are counted, never
filled by an agent. Records (photos, press logs, the first-article caliper table, test results) are filed as they happen under **the one records
folder `70-release/<rev>/records/`** (the cut yaml's `records_dir`; RELEASE_NOTES points there), or the cut cannot be written
(`references/release-and-cut.md`).

- **The last round is an order, then a fixed-point pass:** records → renders → reports → matrix → reports → analysis index → PDFs → cut build LAST → commit;
  afterwards only `--check`s; run the round twice and diff after stripping the volatile cascade (`references/release-and-cut.md` §3.1). Whoever
  appends a decision row runs the round.
- **Placed order = frozen package** [ee, both]. Once an owner row says the order is PLACED (`markers.placed_regex` + the package name), the fab-package gate
  judges stock on the records frozen at the build (`stock_snapshot.json`, hashed in the manifest), never on the live shelf. Its selftest runs on a
  stock fixture (`references/fab-dfm.md` §8). Fab files are never rebuilt; prose may be re-derived.
- **Vendor review after the order** (`references/vendor-review.md`, record `templates/VENDOR_REVIEW_RECORD.md`): file the mail + images under
  `60-orders/quotes/<date>/`, map every flag on the files of record (STLs [mech, both]; gerbers / BOM [ee, both]), decide per line in the log, fix through the generator, re-run the vendor's DFM on
  the replacements before uploading, then Replace File / chat **only on the owner's explicit word** — agents never pay, agree, cart or change a line.
  [ee, both] A PCBA fab's **engineer questions** (polarity, placement, "okay to proceed?") are answered on the board's pad-1 positions, never on
  the CPL rotation, class by class, with a body-on-their-snapshot picture for any custom-footprint connector; its **production-file package** is
  diffed per layer against the upload the day it arrives (compensation, drill oversizes, inner pad removal, mask relief, via plugging = expected; <!-- style: ok -->
  anything else = finding) and approved with at most two confirmations (`references/vendor-review.md` §5–§6). **Both are pre-answered upfront**:
  `ASSEMBLY_NOTES` in the package (a cut deliverable, `references/fab-dfm.md` §9), a fab's-eye silk pass at G2 (a G2 prerequisite), the fab-side hole sizes and
  via treatment in the order remark, arrival-checklist §A rows A-0 / A-5 (`references/vendor-review.md` §7). The fab's second round ("we <!-- style: ok -->
  updated the DFM") is pixel-diffed against the first before any answer; an ambiguous picture gets a request to state the change, never a release.
  The order-history "Confirm Parts Placement" step (silent timer) is read from the fab's engineering file (`ec` vs `oc` per designator) and a
  hole-calibrated pad-1 overlay before the owner submits. Its deltas go into the rotation table with a selftest (`references/vendor-review.md`
  §5 round 4, `references/pcb-layout-dfm.md` §10).
  [mech, both] A **colour / cosmetic insert** is the whole functional face. Its edge is budgeted, and it goes through the inlay path
  (`references/dfm-printed-enclosure.md` §12). Its colour file is ONE shell with the colours on the triangles (never one object per colour). Its
  legends keep a cap hierarchy and the switch-well layout rule of §12. A print-orientation sheet goes with every order line
  (`references/vendor-review.md` §4). A wall AT the vendor's gate reads yellow. `design_margin` ≥ 0.3 and the six-view read of §7
  step 4 is the gate (§13).
- **Illustrated assembly and use guide** [mech, both] beside the text SOP: `scripts/assembly_guide.py`. It builds the guide from an authored short yaml + generated step text + one keyed
  render per page from the exported meshes, and has `--check`. The guide covers the parts, magnet installation with polarity, loading, closing
  orientation with the keying feature marked, taking a part out, care. Pages are vector pages with real text (selectable, searchable) around
  embedded line drawings. The drawings use light fills with black edges from the meshes of record, a recess shown dark by a height split, and a
  section inset where a perspective view hides an arrangement. Every number comes from the design parameters. The PDF ships in the release folder beside the drawing; the kit's START_HERE points
  to it; a cut deliverable (`references/release-and-cut.md` §8).
- **The release folder holds copies, named by use** (`references/release-and-cut.md` §12). The cut generator writes it; it is never hand-edited. Its
  README is the manifest (build date, `git describe`, design values, checks with counts, MD5 + size per file, the procedure). Subfolders are
  named by what a person does with them, files by filament role. Every multi-material part has a single-colour variant [mech, both].
- **The order record sits beside the manufactured files** (`references/release-and-cut.md` §13). It holds every vendor option as set on the order page,
  the price, the cart line, the uploaded file name + MD5, reproduction steps from the release asset, and the delivered batch's deviations. The
  downloaded release asset's MD5 equals the local file's. CI compares a rebuild with the release archive only on the release tag (§14).

### 10.1 Before the order ships: the arrival checklist and the spec errata
- **The arrival / first-article checklist is GENERATED** and is a cut deliverable. Copy `templates/20-design/arrival_checklist.yaml` to
  `20-design/` AT THE ORDER, not on day 1 → `scripts/arrival_checklist.py` → `60-orders/ARRIVAL_CHECKLIST_<rev>.md`. Uncomment the `--check`
  line in `gates.adopt` the same commit, because `project.py gates-required` demands it once the yaml exists. It is written at the order, from
  the merged reviews' "what the parts must prove" rows and the OPEN decision rows, in the order of the day. First come checks **before
  shipment**: the fab's assembly photos. A paid "confirm placement" option is not guaranteed to raise a dialog. The photo confirmation is the one
  human polarity look. Then **bench checks in gate order** [ee, both]: each row says what it `opens`, and nothing is powered or plugged before its
  row. Then **software gates before the first high-power step** [ee, both], each with the commit that closed it. Then **case first article**
  [mech, both]: caliper table, fit, retention, coupons read by their printed text. Last come **owner decisions still OPEN** with the trigger that
  resolves each (the bracket-print fit knob = `kickoff.enclosure.fit_result`, the SPEC errata rows). Every row: `status` TODO / DONE date / N/A / APPLIED date (veto
  window) + `evidence`; closing a row = editing the yaml, regenerating, committing (`references/release-and-cut.md` §10).
- **A frozen SPEC is never edited**. Deviations of the design of record from the frozen text are **E-rows in `10-spec/SPEC_ERRATA.md`**
  (`templates/10-spec/SPEC_ERRATA.md`). They stay OPEN until the owner approves and fold into the next SPEC revision's change log. The arrival
  checklist §E carries them. A reviewer reads the errata before calling a deviation a finding (ALREADY DECIDED).

## 11. Agent operations

Parallel agents own disjoint files. Explicit-path commits do not isolate hunks inside a shared file, so stage the exact edit. Re-read before
every append. Hand out record IDs with the task. **Commit after every meaningful step**: a subagent that hits its turn limit loses everything not
in HEAD. Use `WIP … not yet gated` checkpoint commits, then the gated one.
Block in-process on background jobs (`until ! kill -0 $pid; do sleep 20; done`; the per-call ceiling is stated once in `references/agent-ops.md` §5).
Heartbeat every ~25 min. Time-box every long task. Keep pause points with a resume list in `90-log/STATUS.md`. Keep the machine awake. Resume by
message with the measured state, never from memory. Kill a long render early when an owner addition arrives (`references/agent-ops.md`).
Memory holds resume pointers and owner feedback, never project facts. A numbered PAUSE POINT carries an owner list (owner-only items, struck
through with date + record as they close) and a Resume line. An owner-only item is listed, never attempted. A chat delegation is quoted in the
decision row before the named actions are done (`references/agent-ops.md` §7). **Resources**: every heavy command runs through the one job pool
`scripts/jobs.sh`. The pool is sized from the host and has a memory / load gate, the control that also sees a multithreaded tool; it logs wall +
RSS. Measure serially and audit the sidecars before changing anything. Previews regenerate every run on the fast engine, while STL exports of
record stay on the engine that passes the mesh gates. They are cached only on an inputs + engine key, with the sidecar md5 as a determinism check.
Slicer / PDF / index caches live behind `--check`. Run one locked record round per batch. Do a one-value tweak inline rather than delegate it. The
pool log is `${TMPDIR:-/tmp}/hwfs_jobs/jobs.log` or `jobs.sh --log FILE` (`references/agent-ops.md` §8; the project's CLAUDE.md "Agent operations" block).

### 11.1 Resume (after a crash, a sleep, a new session)

1. `90-log/STATUS.md` STATE NOW + the newest paragraph (what was running, the pause list) → 2. `90-log/DECISIONS.md` OPEN rows (= owner items; also
`90-log/KNOWN_ISSUES.md` §2) → 3. `git status --short` and `git log -3 --stat` (what was left uncommitted; never commit another agent's half-edit)
→ 4. `scripts/handoff_header.py` (board of record vs HEAD, clean/dirty) → 5. `scripts/adopt_gates.sh` (what is green at HEAD) → 6. Compare
with STATE NOW. Every difference is written into a new STATUS paragraph BEFORE any work resumes (measured state, not remembered state) → 7. If a
gate ask was pending, check the cell. If the owner answered in chat only, see §1.1 step 4.

## 12. Before your final commit

Append every non-obvious learning to `90-log/LEARNINGS_LOG.md` as `- YYYY-MM-DD [domain] learning — evidence`; one DECISIONS row for the task;
one dated STATUS paragraph; run the `--check` chain; `git status --short <paths>` after every explicit-path commit of a generated set.
Run `scripts/style_lint.py --project <root>` over the texts you wrote (`references/writing-style.md`: Google developer style, ASD-STE100
sentences, Zinsser's four principles). Fix every hit. The same rules shape your chat report.
Then the retro (§13) folds the learnings back into this skill at the next production cut.

## 13. Retro — the skill improves with each project (owner: "self improving, gets better with each new project we successfully build")

After every production cut (and after any round that cost an order or a reprint), run `scripts/skill_retro.py --project <root> --since <the
project's first day>`. It reads the project's `LEARNINGS_LOG.md` and `DECISIONS.md` and classifies every dated entry against this skill's sections
(CARRIED / PARTIAL / NEW, "costly" when the text names a failure that cost a round). It compares the skill version the project recorded
(`project.yaml skill: {version}`) with `SKILL.md`. It writes `docs/retro/<project>_<date>.md` in the skill repo. That file is working material:
fold it, then delete it, because the skill repo carries no project retro and the generic lint reads the whole repo. The file holds the NEW and
PARTIAL tables, a CHANGELOG entry draft, one reference patch stub per target file, an eval stub per costly NEW entry, and the owner decision
topics the kickoff questionnaire does not ask yet. It also holds the DFM process-table drift (`20-design/dfm_processes.yaml` vs the skill's
template: NEW rows, CHANGED numbers with their citation, VALIDATED rows — §8.1 item 1). Every dated bullet it cannot parse is listed in §0, never
dropped. The project's `ids.owner_prefix` and `paths.dfm_processes` are honoured. **`--apply`** then performs the mechanical folds in the skill repo, idempotently: one pitfalls line per NEW
learning, every NEW process row with its citations into the template (`validated_on: []`), a CHANGELOG `UNRELEASED` stub. Then, by hand: fold
the NEW lines into the named reference (generalised, the source number as the labelled worked example) and extend the PARTIAL sections. Add the
evals, and add a questionnaire question per recurring owner topic. Run the smoke + `evals/run_evals.py`, bump `version` and finish the CHANGELOG
entry. Blind-review the skill (a cold-user lens and a DFM-expert lens), then open the PR. The project pins the new version in `project.yaml` and its CC-001
row. The classifier is a keyword matcher: the report is the input to the change; `--apply` drafts, a human reads.

## Where to look

| Need | Read |
|---|---|
| project.yaml keys (`project.scope`, `paths.mech_record`, `print_targets`, `fab_dfm`, `kickoff`, `skill.version`) | `references/project-yaml.md` |
| the scope (ee / mech / both): what is created, asked and gated per scope | §0 step 2, §0.1 A0, §1; `scripts/project.py scaffold` / `slots` / `kickoff --check` / `gates-required` |
| gate cells and the release line read by script; ERC acceptances as yaml | `scripts/gate_check.py`, `scripts/erc_gate.py`, `templates/20-design/erc_accept.yaml` |
| an existing STEP as a body of record | `scripts/step2stl.py`, `references/case-pipeline.md` §0 |
| the evals and what is checked mechanically | `evals/evals.json`, `evals/run_evals.py` |
| day 0: the kickoff questionnaire (every owner decision, recommended defaults, batches) | `references/kickoff-questionnaire.md`, `templates/10-spec/KICKOFF_ANSWERS.md` |
| G0: SPEC / VERIFY skeletons, the spec review round | `templates/10-spec/SPEC.md`, `templates/20-design/VERIFY.md`, §5 |
| G0→G1: design yaml shape, ERC gate (`erc_gate.py` + `20-design/erc_accept.yaml`), map checks, G1 pack | `references/schematic-phase.md`, `templates/G1/` |
| G1→G2: placement CSV, router session, G2 pack, PCB build rules (stack-up … panel), DRC census, route quality, parity, canary | `references/pcb-layout-dfm.md` |
| part tags, verification table | `references/part-verification.md` |
| fab rules, panel, quote form, DFM export | `references/fab-dfm.md` |
| case yaml → STL → checks → quotes | `references/case-pipeline.md` |
| printed-enclosure DFM: MJF / FDM / SLA rules tagged checker / vendor / physics / owner, inserts + magnets, post-processing, tolerance stack, census gate, heat-map procedure, probes, coupons, dummies, brand marks (ironed top face / AMS bed layers), dust caps, Bambu CLI facts, post-mortem | `references/dfm-printed-enclosure.md` |
| the print kit as a deliverable: START_HERE, kit text gate, hardware from the knobs, magnet procedure, bracket plate, watertight / sidecar rows | `references/print-kit.md` |
| slicer-level optimisation: waste (flush into infill / support, flush calibration, prime tower, grouped colour changes), strength (walls, infill, modifiers), quality (EF / XY compensation, seam, ironing, fuzzy skin, per-object overrides) — every knob with its proof row; kickoff C11 default sets | `references/fdm-print-optimisation.md` |
| the arrival / first-article checklist (yaml → md, --check), the SPEC errata file | `scripts/arrival_checklist.py`, `templates/20-design/arrival_checklist.yaml`, `templates/10-spec/SPEC_ERRATA.md`, `references/release-and-cut.md` §10 |
| print DFM before every upload: rules W R F K P V H O B S (+ INFO L Y) from physics + cited process rows, the commands and what a FAIL means, the verdict → validate → rule-fix → retro loop, adding a vendor row, the generated-SCAD lint | `references/print-dfm.md`, `scripts/print_dfm.py`, `scripts/scad_lint.py`, `templates/20-design/dfm_processes.yaml` |
| machined enclosure: corner radii, walls, threads, anodising, quote page, case-order gate | `references/cnc-enclosure.md` |
| bought hardware: line schema, hardware classes (inserts, magnets, feet, labels), adhesive on PA12 | `references/part-verification.md` |
| meshing, solving, caches, reporting | `references/fea-stage.md` |
| bring-up tool, criteria, codes | `references/software-track.md` |
| reports, collateral, tag, cut yaml, one-round chain, assembly guide, re-layout | `references/release-and-cut.md` |
| repository conventions: one folder per product, `assets/`, a README in every folder, build output ignored, release folder by use, order record, clean tree | §0 step 8, `references/project-yaml.md` §Layout, `references/release-and-cut.md` §12–§14 |
| writing: sentences, voice, words, where the rules apply, how to fix a lint hit | `references/writing-style.md`, `scripts/style_lint.py` |
| the fab's review mail after the order, Replace File boundaries, quote-page DFM mechanics | `references/vendor-review.md` |
| orchestration, git, reviews, read-only checkers, memory / pause points, the resource budget (job pool, measure-audit-change, caching + engine policy, serialized record round, preview vs render, inline vs agent) | `references/agent-ops.md`, `scripts/jobs.sh`, `templates/ci/Makefile` |
| every recorded pitfall, one line each | `references/pitfalls.md` |
| the retro after a cut: what the project learned that the skill lacks | `scripts/skill_retro.py` (its report in `docs/retro/` is deleted once folded) |
| instantiating a workflow | `workflows/README.md` |
| the dry run | `smoke/README.md` |
