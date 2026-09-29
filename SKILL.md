---
name: hw-from-spec
version: 0.5.0
description: Run a hardware project (PCB + printed or CNC enclosure, contract fab such as JLCPCB) from a written specification to a production cut with an owner-gated, generated-only, blind-reviewed workflow — a kickoff questionnaire that asks every owner decision up front with recommended answers, a zero-warning manufacturability bar, and a retro that folds each project's learnings back into the skill. Use this whenever someone starts a board or enclosure project from a spec, asks to set up gates, a decision log, generators, part verification, a fab DFM mirror, a case pipeline, FEA, blind reviews, a release report or a production cut for one, or resumes such a project, or wants the skill improved from a finished project — even if they only say "new KiCad board", "order this at JLC", "review the layout", "cut the release" or "what did we learn".
---

# hw-from-spec

A repeatable process for taking a board + enclosure from a written spec to fabrication and a production document set, with humans deciding at
gates and agents doing everything else through generators. Every rule below cites the reference that carries the detail; read the reference
when you reach that step, not before. Nothing here is specific to one board: project constants live in `project.yaml` (`references/project-yaml.md`).

## 0. Day-1 setup (do this before any CAD)

1. **Install — ONE layout, ONE block (README "Install")**: the skill is a submodule at `vendor/hw-from-spec` with a RELATIVE symlink `scripts ->
   vendor/hw-from-spec/scripts` (or a copy of `scripts/`); a personal clone under `~/.claude/skills/` is for skill discovery only and never the
   project's scripts source; never a submodule AT `scripts/`. Two venvs, both gitignored: the skill's (`vendor/hw-from-spec/.venv`, pyyaml) and
   the project's (`.venv`, pyyaml + `numpy trimesh scipy shapely` for the mesh scripts `thin_wall_census.py` / `thin_wall_check.py`) — `uv venv`
   + `uv pip install`, or `python3 -m venv` + `pip` when `uv` is absent. `tools.python` and the step-5 loop use the project venv; the shell gates
   fall back to the first interpreter that imports yaml (project venv, skill venv, python3) and print which.
   **Then the kickoff questionnaire (§0.1)** — every owner decision a board + enclosure project needs, asked up front with recommended defaults,
   written into `project.yaml` and `docs/governance/DECISIONS.md` before any CAD.
2. **Copy the templates**, then `grep -rn '{{' CLAUDE.md docs project.yaml design` must print nothing:
   `cp templates/CLAUDE.md templates/.gitignore templates/project.yaml .`; `mkdir -p docs/{governance,design,parts,reviews,release,quotes,production} design`;
   `cp templates/{DECISIONS,STATUS,GATES,KNOWN_ISSUES,LEARNINGS_LOG,BLOCKERS,ENV,ERC_WAIVERS}.md docs/governance/`; `cp templates/PARTS_VERIFICATION.md
   docs/parts/`; `cp templates/TEST_PLAN.md docs/design/`; `cp -R templates/datasheet_notes docs/`; `cp templates/design/traceability.yaml design/`.
   The docs/ layout (`references/project-yaml.md` §Layout) is the one the defaults name; re-laying it out later is a decision row + a `reorg:` block +
   `scripts/reorg_paths.py --apply/--check/--proof`, never a hand sweep. `{{SKILL_COMMIT}}` = `git -C vendor/hw-from-spec rev-parse --short HEAD`;
   `{{DATE}}` = today; `{{SKILL_VERSION}}` = the `version:` line of `vendor/hw-from-spec/SKILL.md`; the CC-001 row ships in the template —
   its evidence cell is filled after step 6 (selftests / smoke / adopt gates green at a named commit), not before.
3. **project.yaml** (from `templates/project.yaml`: paths, id prefixes, markers, tools, the day-1 gate lists; the G1/G2 lines stay commented
   until those artefacts exist). Everything a script needs is there; no script carries a project constant (`references/project-yaml.md`).
4. **docs/governance/ENV.md**: tool versions, the CAD CLI paths, which endpoints answer (verify each by running it); run the CAD CLI once on a trivial
   file and note the file-format version. Put every tool path behind the `tools:` block — twenty generators with hard-coded paths cost a CI day
   later (`references/pitfalls.md` ci/tooling).
5. **Prove the toolchain**: `for s in scripts/*.py; do .venv/bin/python $s --selftest; done; scripts/clone_gate.sh --selftest;
   scripts/adopt_gates.sh --selftest; vendor/hw-from-spec/smoke/run_smoke.sh` — all green before the spec is read.
6. **First records** (the smoke's sequence, in a new project): `scripts/known_issues.py` → `scripts/traceability.py` (**exit 1 = a decision row
   without a traceability entry or a FAILED check; every D-/CC- row — the kickoff rows included — needs an entry in `design/traceability.yaml`,
   add it and rerun**) → `scripts/release_report.py` (DRAFT, board MISSING — correct before G1) → commit → `scripts/adopt_gates.sh` (day-1 list +
   clone gate) green → fill the CC-001 evidence cell and the first STATUS paragraph → commit. Only now read the spec (§1.1 says what happens at G0).
7. **CI (optional, when the repo has a remote)**: `templates/ci/` holds pr-check / nightly / release workflows with `{{PROJECT_*}}` placeholders;
   fill them with the `sed` recipe in `templates/ci/README.md`, write `scripts/ci/project.env`, commit under `.github/workflows/`.

### 0.1 The kickoff questionnaire — every owner decision up front, with a recommended answer (`references/kickoff-questionnaire.md`)

Before the spec is read and before any CAD, ask the owner **every decision class a board + enclosure project needs**, grouped by phase and asked
in ten batches with the **`AskUserQuestion` tool** (≤ 4 questions per call): product / process / material / quantity; PCB build (layers, copper,
impedance, finish, min part size + link policy, assembly sides, test points, panel); enclosure architecture (pieces, retention = screws + inserts /
magnets / none, coupling, feet, labelling = deboss / plate / badge, fan, vents, light pipe, two targets); the manufacturability bar per target and
what may be waived (default: zero / zero / nothing); verification (coupons, dummies, review rounds per gate, visual inspections, vendor API read
before the order, FEA); bought parts (acceptable verification sources, the blocked-source rule, stock floor); software / test posture; release /
cut / CI / the retro; identity, envelope and delegation. **Every question lists its RECOMMENDED answer first (marked) and two or three alternatives with a one-line consequence**;
each batch opens with "accept every recommended answer of this batch". Answers go into `docs/governance/KICKOFF_ANSWERS.md`
(`templates/KICKOFF_ANSWERS.md`), one owner D row each (words quoted; `accepted recommended` when the default stood), the machine-readable values
into `project.yaml` (`kickoff`, `board`, `fab_dfm.bar`, `print_targets`), a traceability entry per row — then commit. A deferred question is an
OPEN D row that blocks the phase needing it; an answered question is never re-asked, and a later change is a superseding D row (rule 2).

## 1. Phase / gate model

Phases: **G0** spec approved → **G1** schematic approved → **G2** layout approved → **submission** (fab package, order = owner's click) →
**release cut** (reports RELEASED, collateral, tag) → **production cut** (document set, tag). Each gate has prerequisites listed in `docs/governance/GATES.md`.

- The owner writes the gate line; agents never do. `docs/governance/GATES.md` approval cells and the release line (`markers.release_regex`) are owner text.
  Reports read that file and say **DRAFT** until the line exists (`scripts/release_report.py`).
- Do not start the next phase's CAD before the gate line exists. If the owner delegates ("proceed, I retro-approve"), quote the instruction in
  `docs/governance/GATES.md` under the table and keep the approval cells empty.
- **One review round precedes every gate** — defined once, used everywhere: for every role of the round's role set, one in-session reviewer +
  two external models (or the in-session fallback), an adversarial verifier per role, one merged report (§5). "Two reviews" in an older record
  means one round.
- Never quote the release phrase in prose anywhere the regex can see it (a GATES.md sentence explaining the rule turned every report RELEASED
  in the smoke project) — describe the marker indirectly (`references/pitfalls.md` process).

**Who decides what** (the owner writes D rows; agents write CC rows and ask):

| Phase / item | Decider | Where it is recorded |
|---|---|---|
| kickoff answers (product, process, materials, enclosure architecture, DFM bar, verification, sourcing, software, release) | owner | `docs/governance/KICKOFF_ANSWERS.md` → D rows, `project.yaml` |
| G0 / G1 / G2 cells, the board order click, the case order click, the release line | owner | `docs/governance/GATES.md` |
| a spec value, part, topology, pin change | owner (agent proposes a CC row OPEN) | DECISIONS |
| the manufacturability bar and any waiver of it | owner (default zero / zero / no waivers) | D row + `fab_dfm.bar`, `print_targets.<t>.accepted`, `dfm_accepted` |
| print-target numbers (`print_targets`), design margin, first-article tolerance | owner (agent proposes from the vendor sheet) | `project.yaml`, D row |
| an FEA WARN / a margin below the limit | owner (agent reports the number, never accepts) | D row cited in `FEA_REPORT.md` |
| test criteria limits (T-nn) and the software's refuse-vs-warn posture | owner (agent drafts from the spec) | `design/test_criteria.yaml`, D row |
| FEA case set, review roles, generator design, delegated copper rules | agent (CC DECIDED within the delegation) | CC rows |

### 1.2 The manufacturability bar (the gate rule the owner confirms at kickoff)
**Zero errors, zero warnings, no waivers** — recorded as an owner row on day 1 and enforced by the scripts: **board** — CAD DRC 0 errors / 0
unconnected / **0 warnings** unless a dated waiver row + generated accept rule (`references/pcb-layout-dfm.md` §14), fab DFM mirror **0 open
(0 Danger, 0 Warning)** unless a `dfm_accepted` entry with refdes, reason, date and vendor evidence (`scripts/dfm_check.py` reads
`fab_dfm.bar`); **printed enclosure** — census 0 unaccepted FAIL per body per preset (only a dated `print_targets.<t>.accepted` entry with
vendor evidence passes a cluster), zero slicer warnings, vendor checker **no flag by API read**, no yellow / red on the heat map; **CNC** — the
vendor's DFM clean. `templates/GATES.md` carries the bar as a prerequisite on G2, the board order and the case order. A WARN that is "known" is
not a bar; it is either fixed or a dated, evidence-bearing acceptance the checker re-asserts every run.

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
- **Every checker is read-only on the tree.** A `--check` builds in a temp dir and exports nowhere; `scripts/adopt_gates.sh` fails when
  `git status --porcelain` differs before and after the gates, and the PR-check template ends with the same guard (a schematic `--check` once
  replaced the ERC of record with a temp copy's warnings). Probe a script's usage from its docstring, never by running it without arguments.
- **Layout changes are generated too.** The docs/ layout the defaults name is in `references/project-yaml.md` §Layout; moving files later is a
  decision row + a `reorg:` block + `scripts/reorg_paths.py --plan → --apply → regenerate → --check → --proof` (zero-loss on two `git ls-files -s`
  dumps); frozen records keep the old paths and `--map` explains them (`references/release-and-cut.md` §9).

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
  `grep -c '^| CC-nnn '` immediately before writing (CC rows; owner rows are bold in the template), hand numbers out with tasks (`references/agent-ops.md` §1).
- One record row per agent task, appended after re-reading the file; commit it right away with the exact-edit staging recipe when other agents
  share the tree (`references/agent-ops.md` §2).

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

Protocol (`workflows/README.md`, `references/agent-ops.md` §4):

1. Freeze: commit, `git status --short --untracked-files=no` empty, `git worktree add --detach <frozen> HEAD`, then `git -C <frozen> submodule
   update --init` (otherwise the skill submodule is empty there and `scripts` dangles). Reviewers read only there.
2. Hand-off document = the only briefing. Its header is generated by `scripts/handoff_header.py` (board of record, HEAD md5 MATCH, package,
   case version, clean tree) — a hand-off naming a board the worktree does not carry invalidates the review. Add the one-paragraph waiver list
   (no reasoning) so verifiers do not re-find accepted items each round.
3. Reviewers (the review round of §1): per specialty one in-session agent + two external models (Cursor agent CLI `--mode ask`, read-only; the in-session fallback when no CLI), identical inputs,
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

**The `case_dfm` role** (in the `board` role set of `blind-deep-review.js`): a printed-enclosure DFM specialist whose checklist is
`templates/CENSUS_GATE_ROWS.md` + `references/dfm-printed-enclosure.md` §1 (walls, voids, wedges, opposing faces, inserts, tolerances, orientation,
closed rims, retention present in the mesh); its verifier re-runs `scripts/thin_wall_census.py --target <t>` on the frozen worktree's STLs and
compares with the census JSON of record. Required before the case order (`templates/GATES.md`).

**The G0 round (spec review)** uses `blind-deep-review.js` with `{{ROLE_SET}}` = `spec`: four roles — spec coherence (requirements, interfaces,
numbers that must agree, the VERIFY list), parts and sourcing (every named part fetchable live, tags, alternates, stock for the run), mechanical
intent (envelope, connectors, case concept, thermal), test plan (every requirement has a measurable check). The artefact is `SPEC.md` (+
`docs/parts/PARTS_VERIFICATION.md`, `docs/design/TEST_PLAN.md`, the case concept); the hand-off (`templates/REVIEW_HANDOFF.md`) lists SPEC.md with its md5
in §2, and the generated header's board / package / case rows read **MISSING by design** — say so in the hand-off. Verdict options: approve the
spec as is / after the REQUIRED edits / not yet. Merged report `docs/reviews/G0_merged.md`; REQUIRED edits go into SPEC (owner text: OWNER rows,
agent proposals: CC rows OPEN), the VERIFY list is closed or BLOCKED (§4), then the G0 ask (§1.1). G1 pack and roles: `references/schematic-phase.md` §4.

## 6. Layout phase and the adopt rule (G1→G2: `references/pcb-layout-dfm.md`; G0→G1: `references/schematic-phase.md`)

The layout chain (placement CSV → router session → post-pass → silk → export → `out/G2/` pack), the PCB build rules tagged checker / fab
capability / physics / owner choice (stack-up, impedance, copper minimums vs the fab table, via-in-pad, thermal reliefs, mask / paste / stencil,
part-size policy, two-sided assembly, rotation / CPL, fiducials / test points, silk, courtyards, creepage, panel) and the DRC census live in
`references/pcb-layout-dfm.md`. A routed board is adopted only when, on the committed tree: CAD DRC 0 errors / 0 unconnected / **0 warnings
unless a dated waiver row** / schematic parity 0 with the net classes enforced (prove it with a canary rule that must fire exactly once — the CLI
may ignore class patterns), route-quality 0 unjustified HIGH, the fab DFM mirror 0 open (§7, §1.2), silk check 0, every generator `--selftest`
and `--check` green, and the fresh-checkout gate passes on `git archive HEAD`.
`scripts/adopt_gates.sh` runs the `gates.adopt` list then `scripts/clone_gate.sh`; the routed board + its router session file are the artefacts of
record (routing is never re-run to reproduce them) (`references/pitfalls.md` layout, kicad/drc).

## 7. Fab DFM mirror

Mirror the fab's own DFM checker in-repo before the first quote: copy its thresholds into `design/dfm_thresholds.json` (source + date), let the
project's measurer emit items, grade with `scripts/dfm_check.py`. The rule every viewer used: a value EQUAL to the warning threshold is Warning —
design strictly greater. **0 Danger / 0 Warning is the bar** (§1.2): acceptances are by refdes with reason, date and vendor evidence
(`dfm_accepted`, fields named by `fab_dfm.bar.accepted_requires`); bare tracks/vias cannot be accepted. Run the fab's own checker on the board AND
the PANEL upload before the order and diff its counts against the mirror (`references/fab-dfm.md`; JLC numbers there as the worked example).

## 8. Case pipeline and FEA

`design/case.yaml` → OpenSCAD source → STL per piece → census (wall thickness by entry surface, connected components, membranes) → interference
against the board mesh of record (provenance sidecar: board md5 + mesh md5) → FEA → drawings → print-service / CNC DFM + quotes. Print-target
presets as `base + overrides` deep-merged before any module reads the yaml; drawing and FEA apply the same merge (`references/case-pipeline.md`).
FEA: Gmsh + scikit-fem; fTetWild for CGAL STLs; caches keyed on content; compact nodes after dropping elements; NaN must read FAIL
(`references/fea-stage.md`). Every md5-stamped consumer runs after the final STL pass (CGAL exports are not byte-stable).
- **Point contacts.** Before any mark-shaped body or pocket (inlay plate, badge, deboss) run `scripts/thin_wall_check.py --pinch <stl>`: a traced
  outline of touching shapes pinches to 0.01 mm and the part arrives as lobes; a wall census cannot see it. Bridge with web discs clipped to the
  outline's closing, add the neck row, keep the components = 1 row; `--census` turns a fab heat-map colour into a number (`references/case-pipeline.md`).
- **A case-version bump re-runs every keyed stage** (every STL md5 moves, every FEA mesh rebuilds — ≈ 45 min on the source project's machine, the
  worked example in `references/case-pipeline.md`): run case FEA / PCB FEA / drawings / the alternative preset as background jobs and block on
  their EXIT lines; budget it before promising the full pipeline.

### 8.1 DFM for printed enclosures (before the FIRST quote — `references/dfm-printed-enclosure.md`; CNC: `references/cnc-enclosure.md`)

Acceptance bar (§1.2, owner row at kickoff): **0 FAIL / 0 WARN in every check table and census · zero slicer warnings · no vendor flag by API
read · no yellow, no red on the vendor's heat map · every face rendered and looked at · no waivers.** A row is PASS / FAIL on a MEASURED value
(from the MESH, never the yaml) or it is INFO (no verdict, own table, the reason stated); "kept below minimum (listed)" is a waiver, and the waived
0.88 × 141 mm lip cracked on five parts. **Every number is a `project.yaml print_targets.<target>` value** (vendor, process, material, wall /
void / red gates, design margin, tolerance + source, max bbox the rule was calibrated at, checker URL + date, post-process, rating, `accepted`
list) tagged **[checker]** / **[vendor sheet]** / **[physics]** / **[owner bar]** in the reference; the worked-example numbers below are JLC3DP's
checker (2026-09-28, ~150 mm parts) and a 0.4-nozzle FDM printer — substitute yours, keep the mechanism.
1. **Census as a FAIL gate on every body of every preset** (`scripts/thin_wall_census.py --target <t> --json`, rows `templates/CENSUS_GATE_ROWS.md`,
   pure `--gate-dir` in `gates.adopt`): walls AND voids ≥ the target's gates (MJF checker 1.2 → design 1.3 under a no-yellow bar; FDM 1.6 / voids
   1.0 at 0.4 nozzle), **wedges gated by the width of their sub-gate band**, **the nearest opposing face in ANY direction gated** (the ring-root /
   ledge class every normal-ray census missed), samples ∝ surface area, a NOISE-FLOOR row (not a recall proof), bodies = 1, geometry signature
   beside the md5, concentricity, retention feature present in the mesh, worst-case clearance per mating pair, six face renders. The only
   exception path is a dated `accepted` entry with vendor evidence, re-asserted every run.
2. **Geometry rules — checker vs material**: no FREE-STANDING wedge (rail tips, lips, non-tangent coves, knife edges) **[checker]**; chamfers
   and **tangent fillets cut into ≥ gate walls are fine and recommended at stress risers** **[physics]**; **snap features are possible in PA12**
   **[physics]** — under a no-yellow bar at JLC3DP the ≥ void-gate slit rarely fits, so screws + inserts or magnets (`§1.1` of the reference) are the
   default; **engraved text is allowed when the stroke ≥ the void gate** (cap ≥ ~6 mm at 1.2), else a label carrier; closed rims (no slot / notch /
   gap on the single part unless it has an obvious job) **[owner bar]**; designed asymmetries rendered + in the order sheet + KNOWN_ISSUES or
   removed; inserts / bosses / magnets per material from the TDS (bore, depth, boss ≥ 2 × insert OD, temperature); post-processing removal and
   the material rating (UL 94 / Tg) named on the order sheet; re-derive every yaml value set against an older print rule; a feature that cannot be
   clean in its space budget goes; every wall change reruns the whole table.
3. **Canonical STL + geometry signature** (own binary writer, sorted triangles, normals from the float32 vertices; volume / area / bbox / facets
   beside the md5) so the md5 IS the geometry; the census gate, vendor uploads and the cut key on it.
4. **Vendor quote page**: owner consent to upload quoted in the decision row; ONE STL per session (reload between uploads; uploads work signed
   out), process + material set on the line first (price, map legend — the flag itself is computed at upload and does not depend on it),
   **verdict = the analysis API at `parseStatus == 2` (`getFileAnalyzeResult` → `modelAnalysisVO.thinWall`) — a DOM read before that is invalid**,
   the RAW JSON saved with URL + timestamp, vendor volume / area / bbox = ours (scale sanity), the price per body, the legend thresholds as
   displayed, a capability-page snapshot per round, then the heat map (`previewUrl`) on every face, screenshots named with the md5, one
   `templates/DFM_ROUND.md` per session under `docs/quotes/<date>/`; endpoint gone → BLOCKERS row, verdict class downgraded, round NOT YET; a
   verdict that flips → both reads API reads, then compare signatures and diff the meshes, before touching the generator; the coordinator re-reads
   a worker's "no flag" itself. Nothing saved, carted, agreed or paid (§10 boundaries).
   **The vendor's thin-wall metric is length-dependent** (`references/dfm-printed-enclosure.md` §7.1, with the bbox-resolution hypothesis and its
   test): a rim over a skirt-lap step ≥ 2.0 OR the undercut filled (JLC3DP checker, 147 mm part); a coupon or 40 mm probe that passes proves
   nothing about a 150 mm body — when a body is flagged and the census is clean, slice the body of record into capped slabs and build 40 mm AND
   full-length one-knob profile probes, upload each alone, read the API, adopt the first full-length pass.
5. **Home FDM preset (`home_fdm`)** (printer-first, its own version key, hook tokens keep the vendor SCAD byte-identical; every hook variable
   asserted defined per preset; duplicate yaml keys gated): coupons (text, walls, fits, insert + torque) and a board dummy (two-piece AND one-piece
   at final dimensions — the one-piece nose on a break-away shim the README calls out as a removable "PCB lip"; section symmetric difference 0 mm²
   between the two) before the part; walls ≥ 1.6 / ribs 1.2 / voids 1.0 at 0.4 nozzle, min feature 2 × line width, elephant foot, hole shrink and
   seam handled as per-preset `fits` knobs; raised legends cap 4 / stroke 1.0 / 0.6; fan bosses = fan holes; hood roof-down by `rotate()`, never
   `mirror()`; slicer projects with project-named presets + `different_settings_to_system`; floating-region warning = FAIL; supports read from the
   g-code, not the intent; auto-orientation. **Every vendor DFM decision is mirrored into this preset the same day** in the same yaml under its own
   version key; its census + slicer log clean; ONE kit folder = pieces + coupons + BOTH dummies + READMEs.
6. **When a vendor reports a cracked part**: measure the RECEIVED part (caliper table → the target's tolerance), photo protocol, fractography
   basics, then the ORDERED STL (sections + census with span and class), separate design intent from defect with the vendor-fault table, draft the
   reply from the template for the owner, then apply the learning design-wide (every body, every preset), not to the failed feature
   (`references/dfm-printed-enclosure.md` §10).

## 9. Software track

Bring-up tool first (a `--selftest` that needs no hardware, `--dry-run`), then the architecture note, criteria as YAML the tool reads, PASS / FAIL
/ INCONCLUSIVE with reason codes the manuals are generated from, safety guards as optional flags before the owner's nod (`references/software-track.md`).

## 10. Release cut and production cut

Release cut: `scripts/release_report.py` (every number from a file, MISSING printed, DRAFT/RELEASED from the gate file), collateral incl. renders
(`scripts/collect_renders.py`, keyed on board md5 + camera args), release notes from `templates/RELEASE_NOTES.md` with a source next to every
number, annotated tag. Production cut: `templates/production_cut.yaml` lists every deliverable (kind, path, check, inputs, required, owner
placeholders) and **one project-side generator** (`gen/production_cut.py` — the contract is `references/release-and-cut.md` §7; the skill ships
the yaml and the contract, not the generator) builds `docs/production/<md5-8>/` with MANIFEST + STATUS; `[OWNER: …]` fields are counted, never
filled by an agent; records (photos, press logs, the first-article caliper table, test results) are filed as they happen under **the one records
folder `docs/production/<md5-8>/records/`** (the cut yaml's `records_dir`; RELEASE_NOTES points there) or the cut cannot be written
(`references/release-and-cut.md`).

- **The last round is an order, then a fixed-point pass:** records → renders → reports → matrix → reports → analysis index → PDFs → cut build LAST → commit;
  afterwards only `--check`s; run the round twice and diff after stripping the volatile cascade (`references/release-and-cut.md` §3.1). Whoever
  appends a decision row runs the round.
- **Placed order = frozen package.** Once an owner row says the order is PLACED (`markers.placed_regex` + the package name), the fab-package gate
  judges stock on the records frozen at the build (`stock_snapshot.json`, hashed in the manifest), never on the live shelf; its selftest runs on a
  stock fixture (`references/fab-dfm.md` §8). Fab files are never rebuilt; prose may be re-derived.
- **Vendor review after the order** (`references/vendor-review.md`, record `templates/VENDOR_REVIEW_RECORD.md`): file the mail + images under
  `docs/quotes/<date>/`, map every flag on the STLs of record, decide per line in the log, fix through the generator, re-run the vendor's DFM on
  the replacements before uploading, then Replace File / chat **only on the owner's explicit word** — agents never pay, agree, cart or change a line.
- **Illustrated assembly guide** beside the text SOP: `scripts/assembly_guide.py` (authored short yaml + generated step text + one keyed render per
  page, `--check`), registered as a cut deliverable (`references/release-and-cut.md` §8).

## 11. Agent operations

Parallel agents own disjoint files; explicit-path commits do not isolate hunks inside a shared file (stage the exact edit); re-read before every
append; hand out record IDs with the task; **commit after every meaningful step** (a four-hour agent tree sat uncommitted through twelve rebuilds
until a `WIP … not yet gated` checkpoint; a subagent that hits its turn limit loses everything not in HEAD — checkpoint commits, then the gated one);
block in-process on background jobs (`until ! kill -0 $pid; do sleep 20; done`; the per-call ceiling is stated once in `references/agent-ops.md` §5);
heartbeat every ~25 min; time-box every long task; pause points with a resume list in `docs/governance/STATUS.md`; keep the machine awake; resume by message
with the measured state, never from memory; kill a long render early when an owner addition arrives (`references/agent-ops.md`).
Memory holds resume pointers and owner feedback, never project facts; a numbered PAUSE POINT carries an owner list (owner-only items, struck
through with date + record as they close) and a Resume line; an owner-only item is listed, never attempted, and a chat delegation is quoted in the
decision row before the named actions are done (`references/agent-ops.md` §7).

### 11.1 Resume (after a crash, a sleep, a new session)

1. `docs/governance/STATUS.md` STATE NOW + the newest paragraph (what was running, the pause list) → 2. `docs/governance/DECISIONS.md` OPEN rows (= owner items; also
`docs/governance/KNOWN_ISSUES.md` §2) → 3. `git status --short` and `git log -3 --stat` (what was left uncommitted; never commit another agent's half-edit)
→ 4. `scripts/handoff_header.py` (board of record vs HEAD, clean/dirty) → 5. `scripts/adopt_gates.sh` (what is green at HEAD) → 6. compare
with STATE NOW: every difference is written into a new STATUS paragraph BEFORE any work resumes (measured state, not remembered state) → 7. if a
gate ask was pending, check the cell; if the owner answered in chat only, §1.1 step 4.

## 12. Before your final commit

Append every non-obvious learning to `docs/governance/LEARNINGS_LOG.md` as `- YYYY-MM-DD [domain] learning — evidence`; one DECISIONS row for the task;
one dated STATUS paragraph; run the `--check` chain; `git status --short <paths>` after every explicit-path commit of a generated set.
Then the retro (§13) folds the learnings back into this skill at the next production cut.

## 13. Retro — the skill improves with each project (owner: "self improving, gets better with each new project we successfully build")

After every production cut (and after any round that cost an order or a reprint): `scripts/skill_retro.py --project <root> --since <the project's
first day>` reads the project's `LEARNINGS_LOG.md` and `DECISIONS.md`, classifies every dated entry against this skill's sections (CARRIED /
PARTIAL / NEW, "costly" when the text names a failure that cost a round), compares the skill version the project recorded (`project.yaml skill:
{version}`) with `SKILL.md`, and writes `docs/retro/<project>_<date>.md` in the skill repo: the NEW and PARTIAL tables, a CHANGELOG entry draft,
one reference patch stub per target file, an eval stub per costly NEW entry, and the owner decision topics the kickoff questionnaire does not
ask yet. Then, in the skill repo: fold every NEW line into the named reference (generalised, the source number as the labelled worked example),
extend the PARTIAL sections, add the evals, add a questionnaire question per recurring owner topic, run the smoke, bump `version`, write the
CHANGELOG entry from the draft, blind-review the skill (a cold-user lens and a DFM-expert lens), open the PR. The project pins the new version in
`project.yaml` and its CC-001 row. The classifier is a keyword matcher: the report is the input to the change, never the change itself.

## Where to look

| Need | Read |
|---|---|
| project.yaml keys (`print_targets`, `fab_dfm`, `kickoff`, `skill.version`) | `references/project-yaml.md` |
| day 0: the kickoff questionnaire (every owner decision, recommended defaults, batches) | `references/kickoff-questionnaire.md`, `templates/KICKOFF_ANSWERS.md` |
| G0: SPEC / VERIFY skeletons, the spec review round | `templates/SPEC.md`, `templates/design/VERIFY.md`, §5 |
| G0→G1: design yaml shape, ERC gate, map checks, G1 pack | `references/schematic-phase.md`, `templates/G1/` |
| G1→G2: placement CSV, router session, G2 pack, PCB build rules (stack-up … panel), DRC census, route quality, parity, canary | `references/pcb-layout-dfm.md` |
| part tags, verification table | `references/part-verification.md` |
| fab rules, panel, quote form, DFM export | `references/fab-dfm.md` |
| case yaml → STL → checks → quotes | `references/case-pipeline.md` |
| printed-enclosure DFM: MJF / FDM / SLA rules tagged checker / vendor / physics / owner, inserts + magnets, post-processing, tolerance stack, census gate, heat-map procedure, probes, coupons, dummies, post-mortem | `references/dfm-printed-enclosure.md` |
| machined enclosure: corner radii, walls, threads, anodising, quote page, case-order gate | `references/cnc-enclosure.md` |
| bought hardware: line schema, hardware classes (inserts, magnets, feet, labels), adhesive on PA12 | `references/part-verification.md` |
| meshing, solving, caches, reporting | `references/fea-stage.md` |
| bring-up tool, criteria, codes | `references/software-track.md` |
| reports, collateral, tag, cut yaml, one-round chain, assembly guide, re-layout | `references/release-and-cut.md` |
| the fab's review mail after the order, Replace File boundaries, quote-page DFM mechanics | `references/vendor-review.md` |
| orchestration, git, reviews, read-only checkers, memory / pause points | `references/agent-ops.md` |
| every recorded pitfall, one line each | `references/pitfalls.md` |
| the retro after a cut: what the project learned that the skill lacks | `scripts/skill_retro.py`, `docs/retro/` |
| instantiating a workflow | `workflows/README.md` |
| the dry run | `smoke/README.md` |
