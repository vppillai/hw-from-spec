---
name: hw-from-spec
version: 0.11.0
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
   vendor/hw-from-spec/scripts` (or a copy of `scripts/`); a personal clone under `~/.claude/skills/` is for skill discovery only and never the
   project's scripts source; never a submodule AT `scripts/`. **One venv**, the project's `.venv` (gitignored): pyyaml + `numpy trimesh scipy
   shapely rtree networkx mapbox-earcut embreex` in every scope (the smoke runs the print-DFM selftest; the mesh scripts `print_dfm.py` / `thin_wall_census.py`
   / `thin_wall_check.py` / `step2stl.py` need them in mech / both) — `uv venv` + `uv pip install`, or `python3 -m venv` + `pip` when `uv` is absent.
   `tools.python`, the step-5 loop, the smoke and `evals/run_evals.py` use it (the smoke takes the caller's project `.venv` first, the skill's own
   `.venv` only when run from the skill repo, and skips the mesh section with a NOTE when the libraries are absent); the shell gates take the first
   interpreter that imports yaml and print which. **Every Python command in this document that reads `project.yaml` is run as `.venv/bin/python
   scripts/<tool>.py …`** — the scripts are executable, but their shebang is the system `python3`, which has no pyyaml on a stock machine; only
   `scripts/project.py scaffold | slots`, `step2stl.py`, `scad_lint.py` and the two `thin_wall_*` selftests run bare; the `.sh` gates take the first
   interpreter that imports yaml (`$PYTHON`, the project `.venv`, `python3`) and print which.
   **Then the kickoff questionnaire (§0.1)** — A0 scope first, then every owner decision the scope needs, asked up front with recommended
   defaults, written into `project.yaml` and `90-log/DECISIONS.md` before any CAD.
2. **Copy the templates and resolve the scope** — ONE copy block, runnable from the project root: README "Use in a new project" step 4. It sets
   `A0` (the scope), creates the numbered folders the scope needs, copies the templates from the mirrored templates tree (`templates/90-log/*` →
   `90-log/`, …) and ENDS with `scripts/project.py scaffold --scope "$A0" …` over every copied file and `scripts/project.py slots` — template
   lines tagged `{{ee,both}}` / `{{mech,both}}` / `{{mech}}` stay only in their scopes (one template set, no copies). The arrival checklist yaml
   is NOT copied on day 1 (§10.1: at the order). **The slots are filled in two passes**: `scripts/project.py
   slots` lists every unfilled `{{…}}` per file (the STATUS pause-point skeleton between its `<!-- skeleton -->` markers is excluded) — CLAUDE.md,
   project.yaml and the governance records are filled now from the kickoff answers (§0.1), 10-spec/SPEC.md / KICKOFF_ANSWERS / traceability after the spec
   is read (step 6); the count must read **0** before the G0 ask, not before the kickoff. What each scope creates: **ee** — the board
   paths (`paths.board`, `netlist`, `fab_dir`), `fab_dfm`, the PCB report, G1 / G2 gate rows, ERC waivers, the electronics parts seed; no
   `print_targets`, no `case_yaml`. **mech** — `print_targets`, `case_yaml`, `paths.mech_record` (the STL set whose md5 is the record id),
   `mesh_provenance` for the imported STEP / envelope, the case report, M1 / M2 / case-order rows; no CAD project, no ERC / DRC, no fab DFM
   mirror, no electronics parts seed — parts verification stays for hardware (inserts, magnets, feet, screws). **both** — everything, as before.
   The docs/ layout (`references/project-yaml.md` §Layout) is the one the defaults name; re-laying it out later is a decision row + a `reorg:` block +
   `scripts/reorg_paths.py --apply/--check/--proof`, never a hand sweep. `{{SKILL_COMMIT}}` = `git -C vendor/hw-from-spec rev-parse --short HEAD`;
   `{{DATE}}` = today; `{{SKILL_VERSION}}` = the `version:` line of `vendor/hw-from-spec/SKILL.md`; `project.owner` = the person who writes the gate
   cells (`scripts/gate_check.py --release` compares the release line's git author with it); the CC-001 row (the template's own first agent row:
   "process = this skill at commit X") ships in DECISIONS.md — its evidence cell is filled after step 6 (selftests / smoke / adopt gates green at a
   named commit), not before. Slots inside a path (`30-board/kicad/{{BOARD}}/…`) are filled unquoted.
3. **project.yaml** (from `templates/project.yaml`: paths, id prefixes, markers, tools, the day-1 gate lists; the G1/G2 lines stay commented
   until those artefacts exist). Everything a script needs is there; no script carries a project constant (`references/project-yaml.md`).
4. **90-log/ENV.md**: tool versions, the CAD CLI paths, which endpoints answer (verify each by running it); run the CAD CLI once on a trivial
   file and note the file-format version; the host row from `scripts/project.py env` (cores, RAM, the heavy-job pool and memory floor
   `scripts/jobs.sh` derives — `references/agent-ops.md` §8). Put every tool path behind the `tools:` block — twenty generators with hard-coded
   paths cost a CI day later (`references/pitfalls.md` ci/tooling).
5. **Prove the toolchain** (README step 3): `export PYTHONDONTWRITEBYTECODE=1; for s in scripts/*.py; do .venv/bin/python $s --selftest; done; for s in
   scripts/*.sh; do $s --selftest; done; vendor/hw-from-spec/smoke/run_smoke.sh; .venv/bin/python vendor/hw-from-spec/evals/run_evals.py` — all green
   before the spec is read (the smoke's enforcement section proves with negative cases that a tampered record, an uncensused body, a commented
   gate line and a non-owner release line all FAIL).
6. **First records** (the smoke's sequence, in a new project; `PY=.venv/bin/python`): fill the slots of CLAUDE.md / project.yaml / the records
   first (`$PY scripts/project.py slots` names them; an unfilled `project.yaml` is not valid YAML and every reader says so) → `$PY scripts/known_issues.py`
   → `$PY scripts/traceability.py` (**exit 1 = a decision row without a traceability entry or a FAILED check; every D-/CC- row — the kickoff rows
   included — needs an entry in `20-design/traceability.yaml`, add it and rerun**) → `$PY scripts/release_report.py` (DRAFT, record MISSING — correct
   before G1 / M1) → `$PY scripts/now_pages.py` (the five answers of `00-now/`; `--check` is in the day-1 gate list) → commit → `scripts/adopt_gates.sh` (day-1 list + clone gate) green → `$PY scripts/project.py kickoff --check` green (every answered kickoff row landed in project.yaml with a real D row) → fill the
   CC-001 evidence cell and the first STATUS paragraph → commit. Only now read the spec; fill 10-spec/SPEC.md / VERIFY / traceability; `scripts/project.py
   slots` reads 0 before the G0 ask (§1.1 says what happens at G0).
7. **CI (optional, when the repo has a remote)**: `templates/ci/` holds pr-check / nightly / release workflows with `{{PROJECT_*}}` placeholders;
   fill them with the recipe in `templates/ci/README.md` (it copies `setup_linux.sh` / `nightly.sh` / `release_archive.sh` and writes
   `project.env` into the PROJECT-OWNED `ci/`, never under `scripts/` = the submodule; every checkout has `submodules: recursive`), commit under `.github/workflows/`.

### 0.1 The kickoff questionnaire — every owner decision up front, with a recommended answer (`references/kickoff-questionnaire.md`)

Before the spec is read and before any CAD, ask **A0 Scope** alone (`ee` / `mech` / `both`; RECOMMENDED = what the brief implies, `both` when a
board is designed and housed; each option says what it skips), then **every decision class that scope needs**, grouped by phase and asked in up
to twelve batches with the **`AskUserQuestion` tool** (≤ 4 questions per call, ≤ 4 options per question; "accept every recommended answer of this
batch" is the first option of the batch's first question): product / process / material / quantity; PCB build [ee, both]
(layers, copper, impedance, finish, min part size + link policy, assembly sides, test points, panel); enclosure architecture [mech, both] (pieces,
retention = screws + inserts / magnets / none, coupling, feet, labelling = deboss / plate / badge, fan, vents, light pipe, two targets, brand
marks = ironed top-face feature / flush AMS colour body); the manufacturability bar per target and what may be waived (default: zero / zero /
nothing); verification (coupons, dummies, review rounds per gate, visual inspections, vendor API read before the order, FEA); bought parts
(acceptable verification sources, the blocked-source rule, stock floor); software / test posture [ee, both]; release / cut / CI / the retro;
identity, envelope and delegation. **Every question carries its scopes; a question outside the scope is not asked (KICKOFF_ANSWERS row
`n/a (scope)`) and a batch with nothing applicable is skipped.** **Every question lists its RECOMMENDED answer first (marked) and two or three
alternatives with a one-line consequence**; each batch opens with "accept every recommended answer of this batch". Answers go into
`10-spec/KICKOFF_ANSWERS.md` (`templates/10-spec/KICKOFF_ANSWERS.md`), one owner D row each (the agent transcribes the owner's words, quoted;
`accepted recommended` when the default stood), the machine-readable values into `project.yaml` (`project.scope`, the `kickoff:` mapping, the
`board:` block, `fab_dfm.bar`, `print_targets.<t>` incl. `dfm_process`) — every answer class has a landing key in `templates/project.yaml`, and
**`scripts/project.py kickoff --check`** fails on an answered row whose key is unset or whose D row is missing — a traceability entry per row — then commit. A deferred question is an OPEN D row that blocks the phase needing it; an answered question is never
re-asked, and a later change is a superseding D row (rule 2).

## 1. Phase / gate model (per scope)

- **ee**: **G0** spec approved → **G1** schematic approved → **G2** layout approved → **fab DFM** (§7) → **submission** (fab package, order =
  owner's click) → **release cut** → **production cut**. No case gates, no print DFM.
- **mech**: **G0** mechanical spec approved (envelope, interfaces, materials, print / CNC target, fit inputs — a board STEP / mesh or dimensions,
  each tagged [V] or [K]) → **M1** geometry approved (every body generated from `20-design/case.yaml`, six face renders read, clearance rows ≥ 0
  against the fit input of record, census + pinch + slicer clean, vendor DFM clean by API read, hardware [V], `case_dfm` + mechanical-intent
  round merged) → **M2** first article / fit print approved (caliper table, coupons, mating part fitted; a deviation is a yaml knob → new case
  version → M1 re-run) → **case order** (owner's click) → **release cut** → **production cut**. The record id is the STL set's md5
  (`scripts/project.py record`, `paths.mech_record`), never a board md5.
- **both**: the ee chain with the case pipeline (§8) hanging off G2 and the **case order** gate beside the board order, as before.

The release cut = reports RELEASED, collateral, tag; the production cut = document set, tag (§10). Each gate's prerequisites are the row in
`90-log/GATES.md` (`templates/90-log/GATES.md` carries the rows of every scope; `scaffold --scope` keeps yours).

- The owner writes the gate line; agents never do. `90-log/GATES.md` approval cells and the release line (`markers.release_regex`, in the
  Release row's approval cell) are owner text. **`scripts/gate_check.py <gate>`** reads a cell (exit 1 while empty) and **`--release`** the release
  cell plus its git author, which must be `project.owner`; the report banner reads the same function and says **DRAFT** until the owner's committed
  cell exists — a cell an agent wrote or committed stays DRAFT (`scripts/release_report.py`; the clone gate blames the line in the real checkout).
- Do not start the next phase's CAD before the gate line exists: every project generator of the next phase calls `scripts/gate_check.py <gate>` first
  and refuses while it is 1 (the placement script before G1, the case geometry before G0 / M1, the fab package before G2). If the owner delegates
  ("proceed, I retro-approve"), quote the instruction in `90-log/GATES.md` under the table and keep the approval cells empty.
- **One review round precedes every gate** — defined once, used everywhere: for every role of the round's role set, one in-session reviewer +
  two external models of a second model family (or the in-session fallback, said so in the merge), one verifier with record access per role, one
  merged report (§5). "Two reviews" in an older record
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

1. Prerequisites first: the row's prerequisite cell in `90-log/GATES.md` is satisfied and provable (merged review report committed, the scope's
   checker outputs — ERC / DRC files [ee, both], census JSON + `DFM_ROUND.md` [mech, both] —, `scripts/adopt_gates.sh` green at HEAD, KNOWN_ISSUES §2 lists only items the owner has seen). If one is missing, say so and stop.
2. Write the STATUS pause-point paragraph: what was reviewed (commit, SPEC rev / board md5-8), the merged report path, the OPEN rows the owner
   must decide, and the exact ask: *"Please write the Gn / Mn cell in 90-log/GATES.md: `<your name>, <date>, <SPEC rev | schematic commit | board md5-8 | case version + record md5-8>`"*.
3. Ask in one message with that sentence; do not start the next phase's CAD while waiting (other work — docs, tests, tooling — may continue).
4. A valid cell is owner text in the approval column of that row; `_not yet approved_` is empty. **Agents never write approval cells or the
   release line**, not even when told "go ahead" in chat: quote the chat instruction verbatim with date/time under the table, note "cell pending"
   in STATUS, and proceed only if the instruction explicitly delegates (§1 second bullet). The owner fills the cell later; the report banner and
   the release phrase are read only from the cells/lines the owner wrote.
5. After the cell exists: one STATUS paragraph "Gn approved (cell text)", regenerate the records, commit, start the phase.

### 1.2 The manufacturability bar (the gate rule the owner confirms at kickoff)
**Zero errors, zero warnings, no waivers** — recorded as an owner row on day 1 and enforced by the scripts, never by prose: **board** — ERC
`scripts/erc_gate.py` 0 errors / 0 unaccepted warnings (an acceptance is a typed entry of `20-design/erc_accept.yaml` naming a live decision row; a
GUI exclusion or a stale entry fails), CAD DRC 0 errors / 0 unconnected / **0 warnings** unless a dated waiver row + generated accept rule
(`references/pcb-layout-dfm.md` §14), fab DFM mirror **0 open (0 Danger, 0 Warning)** unless a `dfm_accepted` entry with refdes, reason, date and
vendor evidence (`scripts/dfm_check.py` reads `fab_dfm.bar`); **printed enclosure** — census 0 unaccepted FAIL per body per preset (only a dated
`print_targets.<t>.accepted` entry with vendor evidence passes a cluster, re-matched against the yaml every run), `print_dfm.py` PASS on every
body of the STL set against the target's own process row, zero slicer warnings, vendor checker **no flag by API read**, no yellow / red on the heat
map; **CNC** — the vendor's DFM clean. Both mesh gates glob the STL set of record (a body nobody checked fails), verify every record's signature
(a hand-edited record fails) and the rule-set version. `scripts/adopt_gates.sh` fails when a schematic / board / STL set exists and its gate line
is missing or still commented out in `gates.adopt`. `templates/90-log/GATES.md` carries the bar as a prerequisite on G2, the board order and the case
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
  table (commit, step, file md5, content signature); assert the content signature, keep the md5 informational (`references/pitfalls.md` layout).
- Order of the chain after a change to the record of record (copper in ee / both, the STL set in mech): drawing / FEA → collector → commit → `clone_gate.sh --regen` → commit. Reports are regenerated LAST,
  in the same commit as their inputs (`references/release-and-cut.md` §3).
- **Every checker is read-only on the tree.** A `--check` builds in a temp dir and exports nowhere; `scripts/adopt_gates.sh` fails when
  `git status --porcelain` differs before and after the gates, and the PR-check template ends with the same guard (a checker that exports into
  the tree replaces a record). Probe a script's usage from its docstring, never by running it without arguments.
- **Layout changes are generated too.** The docs/ layout the defaults name is in `references/project-yaml.md` §Layout; moving files later is a
  decision row + a `reorg:` block + `scripts/reorg_paths.py --plan → --apply → regenerate → --check → --proof` (zero-loss on two `git ls-files -s`
  dumps); frozen records keep the old paths and `--map` explains them (`references/release-and-cut.md` §9).
- **Iteration tiers keep the fast loop honest.** Inner: after a one-value yaml or emitter change run `scripts/iteration_gate.sh -- "<generator>
  --check" "<grader>"` — the changed generator's `--check` and its direct grader (plus the project's standing set in `gates.iteration.inner`)
  under the same read-only guard as the adopt gates; an empty set is refused. Standard: `scripts/adopt_gates.sh --no-clone` (`make gates`)
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

- Tags: **[V]** verified live this session (fetch of the distributor / fab page: MPN, package, stock, basic/extended), **[K]** known but
  unverified (never fitted; **[K owner-read]** when the OWNER read a distributor page our tools could not fetch — date, who, which page — listed in
  PROCUREMENT and the arrival checklist until a fetch of ours confirms it), **[S]** select-by-parameter (a row without an MPN yet). Never invent a fab part number; every check is a row in
  `60-orders/PARTS_VERIFICATION.md` with date, URL, stock (`references/part-verification.md`). Every scope: electronics on the fab's library
  (ee / both), hardware — inserts, magnets, feet, screws, adhesives — on the manufacturer's page + TDS (mech / both); a mech project's fit input
  (board STEP / envelope) carries the same [V] / [K] tag in SPEC §4 and `paths.mesh_provenance`.
- Gate value ↔ MPN ↔ fab code on every fitted part (the BOM groups by code: a value edited on the symbol does not change the ordered part).
- Stock gate is run-relative: qty per board × boards × attrition for every code, not "> 0" on a few.
- **VERIFY item** = a value or claim in the spec (or in a review finding) that rests on a datasheet, drawing or standard nobody has read yet:
  a current, a pin function, a footprint dimension, a reflow limit, a standard clause. The spec author tags them `VERIFY` in 10-spec/SPEC.md (or the
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
3. Reviewers (the review round of §1): per specialty one in-session agent + two external models of a **second model family** (an agent CLI of another model family
   `--mode ask`, read-only; the in-session fallback when no CLI — say so in the merge), identical inputs = the artefacts + the role's checklist,
   never each other's output, never the author's dispositions, never the decision log. Reports to `80-reviews/<ROUND>_<role>_<model>.md`.
4. **One verifier WITH record access** (DECISIONS, KNOWN_ISSUES, BLOCKERS, SPEC + its errata, the test plan, the netlist / mesh of record) on
   every finding: default REFUTED unless the worktree evidence supports it; classes **CONFIRMED / ALREADY DECIDED** (the row that decided it, and
   whether its number still holds) **/ REFUTED / PARTLY / UNVERIFIABLE**, corrected text and severity, and a **rev-impact column** (changes the
   ordered revision / bench check on arrival / next revision / record only). Reviewers re-find decided items at ~1:1 on a board and ~1:2 on a
   case: the verifier's record pass is what makes the merge cheap. A netlist or mesh claim is re-measured by the verifier (`<cad-cli> sch export
   netlist` + a short parser; trimesh on the STL of record), never taken from the reviewer.
5. Merge into CC rows: dedupe by defect, corroboration matrix (finding × model), classify each item **REQUIRED** (generator/YAML change, exact
   edit) / **OWNER** (proposed DECISIONS row text) / **DOCUMENT** / **ACCEPT** (reason), an explicit verdict (order as is / after REQUIRED / not yet),
   reviewer-quality counts (findings, refuted rate, already-decided rate, empty runs). **Nothing from a review is applied without the verifier's
   row**; a CONFIRMED finding whose closure is a bench step becomes an arrival-checklist row (§10.1), not a silent backlog line. Commit the review
   files with explicit paths.
6. Visual gates READ the images (silk, renders, tiles): geometry checks passed boards with blank bars and mutilated words.

Templates: `workflows/blind-deep-review.js` (roles × models × verifiers × merge), `workflows/routing-inspection.js` (tiles ≥ 40 px/mm, two
inspectors), `workflows/silk-audit-verify.js` (audit → fix → blind verify A/B → merge+fix → re-verify), `workflows/delta-audit.js` (claims list,
changed specialties only). `{{EXTERNAL_MODELS}}` needs at least two distinct models (role i gets entries i and i+1; the template throws otherwise).

**The `case_dfm` role** [mech, both] (in the `board` role set of `blind-deep-review.js`; in mech scope the M1 round's role set = `case_dfm` + mechanical intent): a printed-enclosure DFM specialist whose checklist is
`templates/CENSUS_GATE_ROWS.md` + `references/dfm-printed-enclosure.md` §1 (walls, voids, wedges, opposing faces, inserts, tolerances, orientation,
closed rims, retention present in the mesh); its verifier re-runs `scripts/thin_wall_census.py --target <t>` on the frozen worktree's STLs and
compares with the census JSON of record. Required before the case order (`templates/90-log/GATES.md`).

**The G0 round (spec review)** uses `blind-deep-review.js` with `{{ROLE_SET}}` = `spec`: four roles — spec coherence (requirements, interfaces,
numbers that must agree, the VERIFY list), parts and sourcing (every named part fetchable live, tags, alternates, stock for the run; in mech
scope the hardware lines), mechanical intent (envelope, connectors, case concept, thermal; in mech scope also the fit input's provenance and
tag), test plan (every requirement has a measurable check). The artefact is `10-spec/SPEC.md` (+
`60-orders/PARTS_VERIFICATION.md`, `20-design/TEST_PLAN.md`, the case concept); the hand-off (`templates/REVIEW_HANDOFF.md`) lists 10-spec/SPEC.md with its md5
in §2, and the generated header's board / package / case rows read **MISSING by design** — say so in the hand-off. Verdict options: approve the
spec as is / after the REQUIRED edits / not yet. Merged report `80-reviews/G0_merged.md`; REQUIRED edits go into SPEC (owner text: OWNER rows,
agent proposals: CC rows OPEN), the VERIFY list is closed or BLOCKED (§4), then the G0 ask (§1.1). G1 pack and roles: `references/schematic-phase.md` §4.

## 6. Layout phase and the adopt rule [ee, both] (G1→G2: `references/pcb-layout-dfm.md`; G0→G1: `references/schematic-phase.md`)

The layout chain (placement CSV → router session → post-pass → silk → export → `80-reviews/G2/` pack), the PCB build rules tagged checker / fab
capability / physics / owner choice (stack-up, impedance, copper minimums vs the fab table, via-in-pad, thermal reliefs, mask / paste / stencil,
part-size policy, two-sided assembly, rotation / CPL, fiducials / test points, silk, courtyards, creepage, panel) and the DRC census live in
`references/pcb-layout-dfm.md`. A routed board is adopted only when, on the committed tree: CAD DRC 0 errors / 0 unconnected / **0 warnings
unless a dated waiver row** / schematic parity 0 with the net classes enforced (prove it with a canary rule — a deliberately violated generated
DRC rule that must fire exactly once — the CLI may ignore class patterns), route-quality 0 unjustified HIGH, the fab DFM mirror 0 open (§7, §1.2), silk check 0, every generator `--selftest`
and `--check` green, and the fresh-checkout gate passes on `git archive HEAD`.
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
against the board mesh of record (provenance sidecar `paths.mesh_provenance`: board md5 + mesh md5 in `both`; in `mech` the imported STEP /
mesh or the owner's envelope with its source md5 and [V] / [K] tag — a [K] envelope is a KNOWN_ISSUES §2 item until measured) → FEA → drawings
→ print-service / CNC DFM + quotes. Print-target
presets as `base + overrides` deep-merged before any module reads the yaml; drawing and FEA apply the same merge (`references/case-pipeline.md`).
FEA: Gmsh + scikit-fem; fTetWild for CGAL STLs; caches keyed on content; compact nodes after dropping elements; NaN must read FAIL
(`references/fea-stage.md`). Every md5-stamped consumer runs after the final STL pass (CGAL exports are not byte-stable).
- **Imported body.** A part the owner already has as CAD enters the chain through `scripts/step2stl.py part.step --out …/stl/<piece>.stl --tag V|K`
  (cadquery / FreeCAD CLI / `--canonical` on a CAD STL export; canonical STL + provenance sidecar + the OPEN decision row it prints), then is
  censused and print-DFM-checked like a generated body (`references/case-pipeline.md` §0; the M1 row accepts it under its row).
- **Stability.** Anything that stands, rocks, walks or is set down free gets a CoG-vs-support-polygon row at its WORST pose (`scripts/stability.py`,
  `references/case-pipeline.md` §Stability): centre of gravity from the STL set with an infill factor per body, through the assembly transforms,
  against the hull of the ground footprints; min margin over every pose ≥ a stated value. A render cannot show it: a walker with its drive behind
   the legs tips at the poses where one foot per side is down, and every render looked fine.
- **Point contacts.** Before any mark-shaped body or pocket (inlay plate, badge, deboss) run `scripts/thin_wall_check.py --pinch <stl>`: a traced
  outline of touching shapes pinches to 0.01 mm and the part arrives as lobes; a wall census cannot see it. Bridge with web discs clipped to the
  outline's closing, add the neck row, keep the components = 1 row (`references/case-pipeline.md` §Point contacts).
- **A case-version bump re-runs every keyed stage** (every STL md5 moves, every FEA mesh rebuilds — tens of minutes; the cost table is in
  `references/case-pipeline.md`): run case FEA / PCB FEA / drawings / the alternative preset through the job pool as background jobs and block on
  their EXIT lines; budget it before promising the full pipeline.

### 8.1 DFM for printed enclosures [mech, both] (before the FIRST quote — `references/dfm-printed-enclosure.md`; CNC: `references/cnc-enclosure.md`)

Acceptance bar (§1.2, owner row at kickoff): **0 FAIL / 0 WARN in every check table and census · zero slicer warnings · no vendor flag by API
read · no yellow, no red on the vendor's heat map · every face rendered and looked at · no waivers.** A row is PASS / FAIL on a MEASURED value
(from the MESH, never the yaml) or it is INFO (no verdict, own table, the reason stated); "kept below minimum (listed)" is a waiver, and a waived
sub-minimum wall cracks in service. **Every number is a `project.yaml print_targets.<target>` value** (vendor, process, material, wall /
void / red gates, design margin, tolerance + source, max bbox the rule was calibrated at, checker URL + date, post-process, rating, `accepted`
list) tagged **[checker]** / **[vendor sheet]** / **[physics]** / **[owner bar]** in the reference; the numbers below are one MJF checker's line on
~150 mm parts and a 0.4-nozzle FDM printer's — substitute yours, keep the mechanism.
1. **Two PURE mesh gates on every body of every preset, before the first upload** — the census gates the DESIGN margin, the print-DFM check the
   printability FLOOR; both read the MESH, never the yaml; both glob the STL set of record and sign their records:
   - `scripts/thin_wall_census.py <stl> --target <t> --json 40-case/<set>/checks/census/<piece>.json` (rows `templates/CENSUS_GATE_ROWS.md`; walls AND voids
     against the target's gates, wedges by the width of their sub-gate band, the nearest OPPOSING face in any direction, samples ∝ area, a
     NOISE-FLOOR row, bodies = 1, geometry signature, retention present in the mesh, worst-case clearance per mating pair, six face renders; the
     only exception path is a dated `accepted` entry with vendor evidence, re-matched every run) — the rules: `references/dfm-printed-enclosure.md` §2.
   - `scripts/print_dfm.py --process <row> --out 40-case/<set>/checks/dfm <stl>` → `PASS` or `FLAG` + one line per rule (M C W R Z F K P V H O B S + INFO L Y from
     physics + the cited minimums of `20-design/dfm_processes.yaml`); FLAG = a real sub-minimum region on the mesh: fix the generator, re-export, rerun —
     no waiver field. The rules, the sidecars (`--boxes`, `--supports`) and the loop: `references/print-dfm.md`.
   - In `gates.adopt`: `thin_wall_census.py --gate-dir` and `print_dfm.py --gate` (exit 1 on a body without a same-md5 record, md5 or signature
     drift, a rule-set / threshold mismatch, a FLAG without `--open <tag>/<piece>=<OPEN decision row naming the piece>` or
     `--expect <tag>/<piece>=<reason>` for a body that FLAGs BY DESIGN — both printed on every run, the record still says FLAG).
   - After every vendor verdict: append the row to `60-orders/quotes/dfm_verdicts.yaml`, run `print_dfm.py --validate`; **vendor FLAG + ours PASS =
     RULE DEFECT (exit 1)** — fix the physics in the rule, bump its `VERSION`, re-validate, run `scripts/skill_retro.py`; vendor PASS + ours FLAG =
     stricter, reason recorded, the rule stands. A new vendor or process = ONE cited row in `20-design/dfm_processes.yaml` (`[V]` URL + date or `[K]`
     with the source; a 404 = `null`, the row refuses to gate); kickoff C8a names the row per target (`print_targets.<t>.dfm_process`).
   - Generated code is linted on every emit (`scripts/scad_lint.py`: a mid-line `//` silently drops the rest of the statement line).
2. **Geometry rules — checker vs material**: no FREE-STANDING wedge (rail tips, lips, non-tangent coves, knife edges) **[checker]**; chamfers
   and **tangent fillets cut into ≥ gate walls are fine and recommended at stress risers** **[physics]**; **snap features are possible in PA12**
   **[physics]** — under a vendor's no-yellow bar the ≥ void-gate slit rarely fits, so screws + inserts or magnets (`§1.1` of the reference) are the
   default; **engraved text is allowed when the stroke ≥ the void gate** (cap ≥ ~6 mm at 1.2), else a label carrier; closed rims (no slot / notch /
   gap on the single part unless it has an obvious job) **[owner bar]**; designed asymmetries rendered + in the order sheet + KNOWN_ISSUES or
   removed; inserts / bosses / magnets per material from the TDS (bore, depth, boss ≥ 2 × insert OD, temperature); post-processing removal and
   the material rating (UL 94 / Tg) named on the order sheet; re-derive every yaml value set against an older print rule; a feature that cannot be
   clean in its space budget goes; every wall change reruns the whole table.
3. **Canonical STL + geometry signature** (own binary writer, sorted triangles, normals from the float32 vertices; volume / area / bbox / facets
   beside the md5) so the md5 IS the geometry; the census gate, vendor uploads and the cut key on it.
4. **Vendor quote page** (`references/dfm-printed-enclosure.md` §7, record `templates/DFM_ROUND.md` under `60-orders/quotes/<date>/`): owner consent
   to upload quoted in the decision row; ONE STL per page session; the verdict of record is the vendor's analysis API response, never a page
   reading (the flag is computed at upload, independent of the material on the line — set the material anyway for price and legend); the RAW
   JSON saved; vendor volume / area / bbox = ours; the heat map read on every face; the coordinator re-reads a worker's "no flag" itself; nothing
   saved, carted, agreed or paid. **The vendor's thin-wall metric is length-dependent** (the reference's §7.1): a coupon or short probe passing proves nothing about
   the full-length body — when a body is flagged and the census is clean, slice the body of record into capped slabs and build full-length one-knob
   probes, upload each alone, adopt the first full-length pass.
5. **Home FDM preset (`home_fdm`)** (`references/dfm-printed-enclosure.md` §8–§9, the kit `references/print-kit.md`, slicer knobs
   `references/fdm-print-optimisation.md`; kickoff C9 / C10 / C11): printer-first FAIL rows from `print_targets.home_fdm` (walls, ribs, voids, 2 × line
   width, elephant foot, hole shrink, seam as per-preset `fits` knobs; raised legends; every external face on the bed / vertical / clean top asserted
   from the g-code), coupons and both board dummies (printable stand-ins for the board: a two-piece and a one-piece version) before the part, brand
   marks as an ironed top-face feature or a flush colour body laid down by the printer's multi-filament unit in the bed layers (never a
   bed-face or vertical-wall deboss; mark coupon first; FAIL-gated mark rows), a roof-down piece turned by `rotate()` never `mirror()` (a mirror flips
   handedness and prints every asymmetric mark backwards), slicer projects with
   project-named presets, a floating-region warning = FAIL, auto-orientation. **Every vendor DFM decision is mirrored into this preset the same day**
   under its own version key (hook tokens keep the vendor SCAD byte-identical; every hook variable asserted defined; duplicate yaml keys gated).
   ONE kit folder per print target, `50-kits/<kit>/` (START_HERE at its root, `plates/` + sidecars, `parts/`, `sheets/`; mirrored byte-identical to
   `~/Downloads/<project>_kits/<kit>/`, superseded kit folders reduced to a one-line `SUPERSEDED.md`) = pieces + coupons + both dummies + READMEs **+ a generated START_HERE**, every kit text through the kit text gate (the FAIL check
   over every emitted kit text, `print-kit.md` §3); glued plates rest on the lands (the flat bed-face seats) with the bridged strips one layer below;
   snug fits ship as a bracket plate (one object per candidate value) the owner picks from — the picked value lands in
   `kickoff.enclosure.fit_result` and closes its arrival-checklist row; watertight row per STL; sidecars drift-checked against the 3MF config.
6. **When a vendor reports a cracked part**: measure the RECEIVED part (caliper table → the target's tolerance), photo protocol, fractography
   basics, then the ORDERED STL (sections + census with span and class), separate design intent from defect with the vendor-fault table, draft the
   reply from the template for the owner, then apply the learning design-wide (every body, every preset), not to the failed feature
   (`references/dfm-printed-enclosure.md` §10).

## 9. Software track [ee, both] (optional)

Bring-up tool first (a `--selftest` that needs no hardware, `--dry-run`), then the architecture note, criteria as YAML the tool reads, PASS / FAIL
/ INCONCLUSIVE with reason codes the manuals are generated from, safety guards as optional flags before the owner's nod (`references/software-track.md`).

## 10. Release cut and production cut

**The record id** every md5-keyed consumer uses (collateral folder, report identity, tag message, `70-release/<rev>/`) is
`scripts/project.py record`: the board file in ee / both, the STL set of record (`paths.mech_record`, md5 of the sorted `<path> <md5>` lines) in
mech — a moved STL moves the id, exactly as a copper change does.
Release cut: `scripts/release_report.py` (every number from a file, MISSING printed, DRAFT/RELEASED from the gate file), collateral incl. renders
(`scripts/collect_renders.py`, keyed on the record md5 + camera args), release notes from `templates/RELEASE_NOTES.md` with a source next to every
number, annotated tag. Production cut: `templates/production_cut.yaml` lists every deliverable (kind, path, check, inputs, required, owner
placeholders) and **one project-side generator** (`gen/production_cut.py` — the contract is `references/release-and-cut.md` §7; the skill ships
the yaml and the contract, not the generator) builds `70-release/<rev>/` with MANIFEST + STATUS; `[OWNER: …]` fields are counted, never
filled by an agent; records (photos, press logs, the first-article caliper table, test results) are filed as they happen under **the one records
folder `70-release/<rev>/records/`** (the cut yaml's `records_dir`; RELEASE_NOTES points there) or the cut cannot be written
(`references/release-and-cut.md`).

- **The last round is an order, then a fixed-point pass:** records → renders → reports → matrix → reports → analysis index → PDFs → cut build LAST → commit;
  afterwards only `--check`s; run the round twice and diff after stripping the volatile cascade (`references/release-and-cut.md` §3.1). Whoever
  appends a decision row runs the round.
- **Placed order = frozen package** [ee, both]. Once an owner row says the order is PLACED (`markers.placed_regex` + the package name), the fab-package gate
  judges stock on the records frozen at the build (`stock_snapshot.json`, hashed in the manifest), never on the live shelf; its selftest runs on a
  stock fixture (`references/fab-dfm.md` §8). Fab files are never rebuilt; prose may be re-derived.
- **Vendor review after the order** (`references/vendor-review.md`, record `templates/VENDOR_REVIEW_RECORD.md`): file the mail + images under
  `60-orders/quotes/<date>/`, map every flag on the files of record (STLs [mech, both]; gerbers / BOM [ee, both]), decide per line in the log, fix through the generator, re-run the vendor's DFM on
  the replacements before uploading, then Replace File / chat **only on the owner's explicit word** — agents never pay, agree, cart or change a line.
- **Illustrated assembly guide** [mech, both] beside the text SOP: `scripts/assembly_guide.py` (authored short yaml + generated step text + one keyed render per
  page, `--check`), registered as a cut deliverable (`references/release-and-cut.md` §8).

### 10.1 Before the order ships: the arrival checklist and the spec errata
- **The arrival / first-article checklist is GENERATED** (copy `templates/20-design/arrival_checklist.yaml` to `20-design/` AT THE ORDER, not on day 1 →
  `scripts/arrival_checklist.py` → `60-orders/ARRIVAL_CHECKLIST_<rev>.md`; uncomment the `--check` line in `gates.adopt` the same commit —
  `project.py gates-required` demands it once the yaml exists; a cut deliverable). Written at the order, from the merged reviews' "what the parts must prove" rows and the OPEN decision rows, in the order of the day:
  **before shipment** (the fab's assembly photos — a paid "confirm placement" option is not guaranteed to raise a dialog, the photo confirmation is
  the one human polarity look) → **bench checks in gate order** [ee, both] (each row says what it `opens`; nothing powered or plugged before its row)
  → **software gates before the first high-power step** [ee, both] (each with the commit that closed it) → **case first article** [mech, both]
  (caliper table, fit, retention, coupons read by their printed text) → **owner decisions still OPEN** with the trigger that resolves each (the
  bracket-print fit knob = `kickoff.enclosure.fit_result`, the SPEC errata rows). Every row: `status` TODO / DONE date / N/A / APPLIED date (veto
  window) + `evidence`; closing a row = editing the yaml, regenerating, committing (`references/release-and-cut.md` §10).
- **A frozen SPEC is never edited**: deviations of the design of record from the frozen text are **E-rows in `10-spec/SPEC_ERRATA.md`**
  (`templates/10-spec/SPEC_ERRATA.md`), OPEN until the owner approves, folded into the next SPEC revision's change log; the arrival checklist §E carries them;
  a reviewer reads the errata before calling a deviation a finding (ALREADY DECIDED).

## 11. Agent operations

Parallel agents own disjoint files; explicit-path commits do not isolate hunks inside a shared file (stage the exact edit); re-read before every
append; hand out record IDs with the task; **commit after every meaningful step** (a subagent that hits its turn limit loses everything not in
HEAD — `WIP … not yet gated` checkpoint commits, then the gated one);
block in-process on background jobs (`until ! kill -0 $pid; do sleep 20; done`; the per-call ceiling is stated once in `references/agent-ops.md` §5);
heartbeat every ~25 min; time-box every long task; pause points with a resume list in `90-log/STATUS.md`; keep the machine awake; resume by message
with the measured state, never from memory; kill a long render early when an owner addition arrives (`references/agent-ops.md`).
Memory holds resume pointers and owner feedback, never project facts; a numbered PAUSE POINT carries an owner list (owner-only items, struck
through with date + record as they close) and a Resume line; an owner-only item is listed, never attempted, and a chat delegation is quoted in the
decision row before the named actions are done (`references/agent-ops.md` §7). **Resources**: every heavy command runs through the one job pool
`scripts/jobs.sh` (sized from the host, memory / load gate — the control that also sees a multithreaded tool —, wall + RSS logged), measure
serially and audit the sidecars before changing anything, previews regenerate every run on the fast engine while STL exports of record stay on
the engine that passes the mesh gates (cached only on an inputs + engine key with the sidecar md5 as a determinism check), slicer / PDF / index
caches live behind `--check`, one locked record round per batch, and a one-value tweak is done inline rather than delegated; the pool log is
`${TMPDIR:-/tmp}/hwfs_jobs/jobs.log` or `jobs.sh --log FILE` (`references/agent-ops.md` §8; the project's CLAUDE.md "Agent operations" block).

### 11.1 Resume (after a crash, a sleep, a new session)

1. `90-log/STATUS.md` STATE NOW + the newest paragraph (what was running, the pause list) → 2. `90-log/DECISIONS.md` OPEN rows (= owner items; also
`90-log/KNOWN_ISSUES.md` §2) → 3. `git status --short` and `git log -3 --stat` (what was left uncommitted; never commit another agent's half-edit)
→ 4. `scripts/handoff_header.py` (board of record vs HEAD, clean/dirty) → 5. `scripts/adopt_gates.sh` (what is green at HEAD) → 6. compare
with STATE NOW: every difference is written into a new STATUS paragraph BEFORE any work resumes (measured state, not remembered state) → 7. if a
gate ask was pending, check the cell; if the owner answered in chat only, §1.1 step 4.

## 12. Before your final commit

Append every non-obvious learning to `90-log/LEARNINGS_LOG.md` as `- YYYY-MM-DD [domain] learning — evidence`; one DECISIONS row for the task;
one dated STATUS paragraph; run the `--check` chain; `git status --short <paths>` after every explicit-path commit of a generated set.
Then the retro (§13) folds the learnings back into this skill at the next production cut.

## 13. Retro — the skill improves with each project (owner: "self improving, gets better with each new project we successfully build")

After every production cut (and after any round that cost an order or a reprint): `scripts/skill_retro.py --project <root> --since <the project's
first day>` reads the project's `LEARNINGS_LOG.md` and `DECISIONS.md`, classifies every dated entry against this skill's sections (CARRIED /
PARTIAL / NEW, "costly" when the text names a failure that cost a round), compares the skill version the project recorded (`project.yaml skill:
{version}`) with `SKILL.md`, and writes `docs/retro/<project>_<date>.md` in the skill repo: the NEW and PARTIAL tables, a CHANGELOG entry draft,
one reference patch stub per target file, an eval stub per costly NEW entry, the owner decision topics the kickoff questionnaire does not
ask yet, and the DFM process-table drift (`20-design/dfm_processes.yaml` vs the skill's template: NEW rows, CHANGED numbers with their citation,
VALIDATED rows — §8.1 item 1); every dated bullet it cannot parse is listed in §0, never dropped; the project's `ids.owner_prefix` and
`paths.dfm_processes` are honoured. **`--apply`** then performs the mechanical folds in the skill repo, idempotently: one pitfalls line per NEW
learning, every NEW process row with its citations into the template (`validated_on: []`), a CHANGELOG `UNRELEASED` stub. Then, by hand: fold
the NEW lines into the named reference (generalised, the source number as the labelled worked example), extend the PARTIAL sections, add the
evals, add a questionnaire question per recurring owner topic, run the smoke + `evals/run_evals.py`, bump `version`, finish the CHANGELOG entry,
blind-review the skill (a cold-user lens and a DFM-expert lens), open the PR. The project pins the new version in `project.yaml` and its CC-001
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
| the fab's review mail after the order, Replace File boundaries, quote-page DFM mechanics | `references/vendor-review.md` |
| orchestration, git, reviews, read-only checkers, memory / pause points, the resource budget (job pool, measure-audit-change, caching + engine policy, serialized record round, preview vs render, inline vs agent) | `references/agent-ops.md`, `scripts/jobs.sh`, `templates/ci/Makefile` |
| every recorded pitfall, one line each | `references/pitfalls.md` |
| the retro after a cut: what the project learned that the skill lacks | `scripts/skill_retro.py`, `docs/retro/` |
| instantiating a workflow | `workflows/README.md` |
| the dry run | `smoke/README.md` |
