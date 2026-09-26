---
name: hw-from-spec
version: 0.2.1
description: Run a hardware project (PCB + printed or CNC enclosure, contract fab such as JLCPCB) from a written specification to a production cut with an owner-gated, generated-only, blind-reviewed workflow. Use this whenever someone starts a board or enclosure project from a spec, asks to set up gates, a decision log, generators, part verification, a fab DFM mirror, a case pipeline, FEA, blind reviews, a release report or a production cut for one, or resumes such a project — even if they only say "new KiCad board", "order this at JLC", "review the layout" or "cut the release".
---

# hw-from-spec

A repeatable process for taking a board + enclosure from a written spec to fabrication and a production document set, with humans deciding at
gates and agents doing everything else through generators. Every rule below cites the reference that carries the detail; read the reference
when you reach that step, not before. Nothing here is specific to one board: project constants live in `project.yaml` (`references/project-yaml.md`).

## 0. Day-1 setup (do this before any CAD)

1. **Install the skill — one layout.** `git submodule add <skill repo> vendor/hw-from-spec && ln -s vendor/hw-from-spec/scripts scripts`
   (relative link; or `cp -R vendor/hw-from-spec/scripts scripts` and pin `skill.commit` in project.yaml). Never a submodule AT `scripts/`
   (every gate command would need `scripts/scripts/…`). Create the skill's interpreter once: `cd vendor/hw-from-spec && uv venv .venv &&
   uv pip install --python .venv/bin/python pyyaml` (README step 2; the venv is gitignored, it does not ship). Then `uv venv .venv` in the
   project too (the gates use the first interpreter that imports yaml: project venv, skill venv, python3).
2. **Copy the templates**, then `grep -rn '{{' CLAUDE.md docs project.yaml design` must print nothing:
   `cp templates/CLAUDE.md templates/.gitignore templates/project.yaml .`; `mkdir -p docs/{governance,design,parts,reviews,release,quotes,production} design`;
   `cp templates/{DECISIONS,STATUS,GATES,KNOWN_ISSUES,LEARNINGS_LOG,BLOCKERS,ENV,ERC_WAIVERS}.md docs/governance/`; `cp templates/PARTS_VERIFICATION.md
   docs/parts/`; `cp templates/TEST_PLAN.md docs/design/`; `cp -R templates/datasheet_notes docs/`; `cp templates/design/traceability.yaml design/`.
   The docs/ layout (`references/project-yaml.md` §Layout) is the one the defaults name; re-laying it out later is a decision row + a `reorg:` block +
   `scripts/reorg_paths.py --apply/--check/--proof`, never a hand sweep. `{{SKILL_COMMIT}}` = `git -C vendor/hw-from-spec rev-parse --short HEAD`;
   `{{DATE}}` = today; the CC-001 row is written after step 6, not before.
3. **project.yaml** (from `templates/project.yaml`: paths, id prefixes, markers, tools, the day-1 gate lists; the G1/G2 lines stay commented
   until those artefacts exist). Everything a script needs is there; no script carries a project constant (`references/project-yaml.md`).
4. **docs/governance/ENV.md**: tool versions, the CAD CLI paths, which endpoints answer (verify each by running it); run the CAD CLI once on a trivial
   file and note the file-format version. Put every tool path behind the `tools:` block — twenty generators with hard-coded paths cost a CI day
   later (`references/pitfalls.md` ci/tooling).
5. **Prove the toolchain**: `for s in scripts/*.py; do .venv/bin/python $s --selftest; done; scripts/clone_gate.sh --selftest;
   scripts/adopt_gates.sh --selftest; vendor/hw-from-spec/smoke/run_smoke.sh` — all green before the spec is read.
6. **First records** (the smoke's sequence, in a new project): `scripts/known_issues.py` → `scripts/traceability.py` → `scripts/release_report.py`
   (DRAFT, board MISSING — correct before G1) → commit → `scripts/adopt_gates.sh` (day-1 list + clone gate) green → write the CC-001 row and the
   first STATUS paragraph → commit. Only now read the spec (§1.1 says what happens at G0).
7. **CI (optional, when the repo has a remote)**: `templates/ci/` holds pr-check / nightly / release workflows with `{{PROJECT_*}}` placeholders;
   fill them with the `sed` recipe in `templates/ci/README.md`, write `scripts/ci/project.env`, commit under `.github/workflows/`.

## 1. Phase / gate model

Phases: **G0** spec approved → **G1** schematic approved → **G2** layout approved → **submission** (fab package, order = owner's click) →
**release cut** (reports RELEASED, collateral, tag) → **production cut** (document set, tag). Each gate has prerequisites listed in `docs/governance/GATES.md`.

- The owner writes the gate line; agents never do. `docs/governance/GATES.md` approval cells and the release line (`markers.release_regex`) are owner text.
  Reports read that file and say **DRAFT** until the line exists (`scripts/release_report.py`).
- Do not start the next phase's CAD before the gate line exists. If the owner delegates ("proceed, I retro-approve"), quote the instruction in
  `docs/governance/GATES.md` under the table and keep the approval cells empty.
- Blind reviews precede every gate: two reviewers, then a merge (§5).
- Never quote the release phrase in prose anywhere the regex can see it (a GATES.md sentence explaining the rule turned every report RELEASED
  in the smoke project) — describe the marker indirectly (`references/pitfalls.md` process).

### 1.1 At a gate (asking the owner)

1. Prerequisites first: the row's prerequisite cell in `docs/governance/GATES.md` is satisfied and provable (merged review report committed, ERC/DRC files,
   `scripts/adopt_gates.sh` green at HEAD, KNOWN_ISSUES §2 lists only items the owner has seen). If one is missing, say so and stop.
2. Write the STATUS pause-point paragraph: what was reviewed (commit, SPEC rev / board md5-8), the merged report path, the OPEN rows the owner
   must decide, and the exact ask: *"Please write the Gn cell in docs/governance/GATES.md: `<your name>, <date>, <SPEC rev | schematic commit | board md5-8>`"*.
3. Ask in one message with that sentence; do not start the next phase's CAD while waiting (other work — docs, tests, tooling — may continue).
4. A valid cell is owner text in the approval column of that row; `_not yet approved_` is empty. **Agents never write approval cells or the
   release line**, not even when told "go ahead" in chat: quote the chat instruction verbatim with date/time under the table, note "cell pending"
   in STATUS, and proceed only if the instruction explicitly delegates (§1 second bullet). The owner fills the cell later; the report banner and
   the release phrase are read only from the cells/lines the owner wrote.
5. After the cell exists: one STATUS paragraph "Gn approved (cell text)", regenerate the records, commit, start the phase.

## 2. Generated only

- Source of truth = `design/*.yaml` (+ placement CSV, part rows). Generators write CAD files, reports, indexes, order sheets. Nothing under
  `kicad/`, `out/`, generated `docs/*` is hand-edited; a review finding changes the YAML or the generator, then regenerates.
- Every generator has `--check` (regenerate in memory, diff against the committed file, exit 1 when stale) and `--selftest` (works in a temp
  dir only, never touches repo files). A `--check` must pass on `git archive HEAD`: no mtimes, no absolute paths, no live git HEAD, no dates
  outside one volatile `Generated` line (`scripts/release_report.py`, `references/release-and-cut.md` §2).
- Byte-stable output: rewrite UUIDs deterministically, process items in sorted order, pin the locale of every `sort` (`LC_ALL=C`)
  (`references/pitfalls.md` tooling/identity).
- A generator that owns part of a file another generator also writes must re-read and merge that part or refuse to run in place
  (a schematic `--check` that rewrote the project file dropped 400 lines of design rules — `references/pitfalls.md` tooling/gates).
- Exceptions to the rule (an in-place hand-routed board, an owner GUI step) are allowed only as a logged decision row plus a "chain of record"
  table (commit, step, file md5, content signature); assert the content signature, keep the md5 informational (`references/pitfalls.md` layout).
- Order of the chain after a copper change: drawing / FEA → collector → commit → `clone_gate.sh --regen` → commit. Reports are regenerated LAST,
  in the same commit as their inputs (`references/release-and-cut.md` §3).

## 3. Decision log

`docs/governance/DECISIONS.md` is one table, six cells: `ID | Date | Status | Topic | Proposal / decision | Reason`.

- **D-nn** rows are the owner's (text as issued); **CC-nnn** rows are the agent's. Status words: OPEN (needs the owner), APPROVED, DECIDED
  (within delegated authority), APPLIED (!) (applied ahead of the nod — the nod marker), REJECTED, SUPERSEDED, CLOSED. History goes after
  `(was: …)` in the status cell; generators stop reading there.
- Rule 2: a value, part, topology or pin assignment named in the spec is never changed silently. Write the CC row (reason, options, recommendation),
  mark it OPEN, ask. Apply only after approval, or ship it behind an optional flag that warns when omitted so the code path is tested now
  (`references/pitfalls.md` process).
- `docs/governance/KNOWN_ISSUES.md` is generated from the log: OPEN rows, rows mentioning OPEN, provisional rows, the nod section (§2.1), blockers, the
  test plan's UNVERIFIED markers. Section 1 is hand-curated between markers (`scripts/known_issues.py`). Describe the nod marker indirectly in
  status cells or the generator re-triggers on the description.
- A literal `|` inside a cell is `\|`; the generator refuses a row with the wrong cell count. An ID is reserved only when its row is in HEAD:
  `grep -c 'CC-nnn |'` immediately before writing (CC rows; owner rows are bold in the template), hand numbers out with tasks (`references/agent-ops.md` §4).
- One record row per agent task, appended after re-reading the file; commit it right away with the exact-edit staging recipe when other agents
  share the tree (`references/agent-ops.md` §3).

## 4. Parts

- Tags: **[V]** verified live this session (fetch of the distributor / fab page: MPN, package, stock, basic/extended), **[K]** known but
  unverified (never fitted), **[S]** select-by-parameter (a row without an MPN yet). Never invent a fab part number; every check is a row in
  `docs/parts/PARTS_VERIFICATION.md` with date, URL, stock (`references/part-verification.md`).
- Gate value ↔ MPN ↔ fab code on every fitted part (the BOM groups by code: a value edited on the symbol does not change the ordered part).
- Stock gate is run-relative: qty per board × boards × attrition for every code, not "> 0" on a few.
- **VERIFY item** = a value or claim in the spec (or in a review finding) that rests on a datasheet, drawing or standard nobody has read yet:
  a current, a pin function, a footprint dimension, a reflow limit, a standard clause. The spec author tags them `VERIFY` in SPEC.md (or the
  G0 review lists them in `docs/design/VERIFY.md`: item, part, what to read). Each is closed by a row in `docs/datasheet_notes/<part>.md` (page/section,
  value read, matches yes/no — `templates/datasheet_notes/_TEMPLATE.md`) or moved to `docs/governance/BLOCKERS.md` when the source cannot be fetched.
  Rule 3: every VERIFY item touching a part is closed before that part is drawn; G0 requires all closed or BLOCKED; curve-only values are
  marked "not in datasheet text" with the reader named.

## 5. Blind reviews

Protocol (`workflows/README.md`, `references/agent-ops.md` §5):

1. Freeze: commit, `git status --short --untracked-files=no` empty, `git worktree add --detach <frozen> HEAD`, then `git -C <frozen> submodule
   update --init` (otherwise the skill submodule is empty there and `scripts` dangles). Reviewers read only there.
2. Hand-off document = the only briefing. Its header is generated by `scripts/handoff_header.py` (board of record, HEAD md5 MATCH, package,
   case version, clean tree) — a hand-off naming a board the worktree does not carry invalidates the review. Add the one-paragraph waiver list
   (no reasoning) so verifiers do not re-find accepted items each round.
3. Reviewers: per specialty one in-session agent + one or two external models (Cursor agent CLI `--mode ask`, read-only), identical inputs,
   never each other's output, never the author's dispositions. Reports to `docs/reviews/<ROUND>_<role>_<model>.md`.
4. Adversarial verifiers on every BLOCKER/MAJOR: default REFUTED unless the worktree evidence supports it; CONFIRMED / REFUTED / PARTLY /
   UNVERIFIABLE with corrected text and severity.
5. Merge: dedupe by defect, corroboration matrix (finding × model), classify each item **REQUIRED** (generator/YAML change, exact edit) /
   **OWNER** (proposed DECISIONS row text) / **DOCUMENT** / **ACCEPT** (reason), an explicit verdict (order as is / after REQUIRED / not yet),
   reviewer-quality counts (findings, refuted rate, empty runs). Commit the review files with explicit paths.
6. Visual gates READ the images (silk, renders, tiles): geometry checks passed boards with blank bars and mutilated words.

Templates: `workflows/blind-deep-review.js` (roles × models × verifiers × merge), `workflows/routing-inspection.js` (tiles ≥ 40 px/mm, two
inspectors), `workflows/silk-audit-verify.js` (audit → fix → blind verify A/B → merge+fix → re-verify), `workflows/delta-audit.js` (claims list,
changed specialties only). `{{EXTERNAL_MODELS}}` needs at least two distinct models (role i gets entries i and i+1; the template throws otherwise).

**The G0 round (spec review)** uses `blind-deep-review.js` with `{{ROLE_SET}}` = `spec`: four roles — spec coherence (requirements, interfaces,
numbers that must agree, the VERIFY list), parts and sourcing (every named part fetchable live, tags, alternates, stock for the run), mechanical
intent (envelope, connectors, case concept, thermal), test plan (every requirement has a measurable check). The artefact is `SPEC.md` (+
`docs/parts/PARTS_VERIFICATION.md`, `docs/design/TEST_PLAN.md`, the case concept); the hand-off (`templates/REVIEW_HANDOFF.md`) lists SPEC.md with its md5
in §2, and the generated header's board / package / case rows read **MISSING by design** — say so in the hand-off. Verdict options: approve the
spec as is / after the REQUIRED edits / not yet. Merged report `docs/reviews/G0_merged.md`; REQUIRED edits go into SPEC (owner text: OWNER rows,
agent proposals: CC rows OPEN), the VERIFY list is closed or BLOCKED (§4), then the G0 ask (§1.1). G1 pack and roles: `references/schematic-phase.md` §4.

## 6. Adopt rule (layout rounds; G0→G1 content in `references/schematic-phase.md`)

A routed board is adopted only when, on the committed tree: CAD DRC 0 errors / 0 unconnected / schematic parity 0 with the net classes enforced
(prove it with a canary rule that must fire exactly once — the CLI may ignore class patterns), route-quality 0 unjustified HIGH, the fab DFM
mirror 0 open (§7), silk check 0, every generator `--selftest` and `--check` green, and the fresh-checkout gate passes on `git archive HEAD`.
`scripts/adopt_gates.sh` runs the `gates.adopt` list then `scripts/clone_gate.sh`; the routed board + its router session file are the artefacts of
record (routing is never re-run to reproduce them) (`references/pitfalls.md` layout, kicad/drc).

## 7. Fab DFM mirror

Mirror the fab's own DFM checker in-repo before the first quote: copy its thresholds into `design/dfm_thresholds.json` (source + date), let the
project's measurer emit items, grade with `scripts/dfm_check.py`. The rule every viewer used: a value EQUAL to the warning threshold is Warning —
design strictly greater. Acceptances are by refdes with a reason (`dfm_accepted`); bare tracks/vias cannot be accepted. Run the fab's checker on the
PANEL upload too, not only the board (`references/fab-dfm.md`; JLC numbers there as the worked example).

## 8. Case pipeline and FEA

`design/case.yaml` → OpenSCAD source → STL per piece → census (wall thickness by entry surface, connected components, membranes) → interference
against the board mesh of record (provenance sidecar: board md5 + mesh md5) → FEA → drawings → print-service / CNC DFM + quotes. Print-target
presets as `base + overrides` deep-merged before any module reads the yaml; drawing and FEA apply the same merge (`references/case-pipeline.md`).
FEA: Gmsh + scikit-fem; fTetWild for CGAL STLs; caches keyed on content; compact nodes after dropping elements; NaN must read FAIL
(`references/fea-stage.md`). Every md5-stamped consumer runs after the final STL pass (CGAL exports are not byte-stable).

## 9. Software track

Bring-up tool first (a `--selftest` that needs no hardware, `--dry-run`), then the architecture note, criteria as YAML the tool reads, PASS / FAIL
/ INCONCLUSIVE with reason codes the manuals are generated from, safety guards as optional flags before the owner's nod (`references/software-track.md`).

## 10. Release cut and production cut

Release cut: `scripts/release_report.py` (every number from a file, MISSING printed, DRAFT/RELEASED from the gate file), collateral incl. renders
(`scripts/collect_renders.py`, keyed on board md5 + camera args), release notes from `templates/RELEASE_NOTES.md` with a source next to every
number, annotated tag. Production cut: `templates/production_cut.yaml` lists every deliverable (kind, path, check, inputs, required, owner
placeholders) and **one project-side generator** (`gen/production_cut.py` — the contract is `references/release-and-cut.md` §7; the skill ships
the yaml and the contract, not the generator) builds `docs/production/<md5-8>/` with MANIFEST + STATUS; `[OWNER: …]` fields are counted, never
filled by an agent; records (photos, press logs, test results) are filed as they happen under a records folder or the cut cannot be written
(`references/release-and-cut.md`).

## 11. Agent operations

Parallel agents own disjoint files; explicit-path commits do not isolate hunks inside a shared file (stage the exact edit); re-read before every
append; hand out record IDs with the task; block in-process on background jobs (`until ! kill -0 $pid; do sleep 20; done`, ≤ 600 s per call);
heartbeat every ~25 min; time-box every long task; pause points with a resume list in `docs/governance/STATUS.md`; keep the machine awake; resume by message
with the measured state, never from memory; kill a long render early when an owner addition arrives (`references/agent-ops.md`).

### 11.1 Resume (after a crash, a sleep, a new session)

1. `docs/governance/STATUS.md` STATE NOW + the newest paragraph (what was running, the pause list) → 2. `docs/governance/DECISIONS.md` OPEN rows (= owner items; also
`docs/governance/KNOWN_ISSUES.md` §2) → 3. `git status --short` and `git log -3 --stat` (what was left uncommitted; never commit another agent's half-edit)
→ 4. `scripts/handoff_header.py` (board of record vs HEAD, clean/dirty) → 5. `scripts/adopt_gates.sh` (what is green at HEAD) → 6. compare
with STATE NOW: every difference is written into a new STATUS paragraph BEFORE any work resumes (measured state, not remembered state) → 7. if a
gate ask was pending, check the cell; if the owner answered in chat only, §1.1 step 4.

## 12. Before your final commit

Append every non-obvious learning to `docs/governance/LEARNINGS_LOG.md` as `- YYYY-MM-DD [domain] learning — evidence`; one DECISIONS row for the task;
one dated STATUS paragraph; run the `--check` chain; `git status --short <paths>` after every explicit-path commit of a generated set.
Then fold the learnings back into this skill's `references/pitfalls.md` at the next production cut.

## Where to look

| Need | Read |
|---|---|
| project.yaml keys | `references/project-yaml.md` |
| G0→G1: design yaml shape, ERC gate, map checks, G1 pack | `references/schematic-phase.md` |
| part tags, verification table | `references/part-verification.md` |
| fab rules, panel, quote form, DFM export | `references/fab-dfm.md` |
| case yaml → STL → checks → quotes | `references/case-pipeline.md` |
| meshing, solving, caches, reporting | `references/fea-stage.md` |
| bring-up tool, criteria, codes | `references/software-track.md` |
| reports, collateral, tag, cut yaml | `references/release-and-cut.md` |
| orchestration, git, reviews | `references/agent-ops.md` |
| every recorded pitfall, one line each | `references/pitfalls.md` |
| instantiating a workflow | `workflows/README.md` |
| the dry run | `smoke/README.md` |
