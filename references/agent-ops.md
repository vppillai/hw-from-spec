# agent-ops.md — running many agents on one hardware repo

## 1. Ownership
- One coordinator; workers own disjoint FILES (board agent: `kicad/`, `design/<board>_*.yaml`; case agent: `design/case.yaml`, `out/**/case/`; docs
  agent: named docs). The shared record files (DECISIONS, STATUS, LEARNINGS_LOG, KNOWN_ISSUES) are append-only for everyone and committed right after
  each edit.
- Hand a worker its record ID (`CC-nnn`) with the task; an ID is reserved only when its row is in HEAD; `grep -c '^| CC-nnn '` immediately before writing.
- Long tasks are time-boxed; the coordinator keeps a heartbeat (~25 min) and a pause-point paragraph in STATUS with the resume list.

## 2. Commits
- Explicit paths only (`git commit -m … -- <paths>`), never `git add -A` in a shared tree. But explicit paths isolate FILES, not hunks: a shared record
  file carries other agents' uncommitted edits. Before committing one, `git diff -- <file>` and confirm every hunk is yours, or stage the exact edit:
  ```
  cp file /tmp/mine; git show HEAD:file > /tmp/base; <apply your edit to /tmp/base>
  blob=$(git hash-object -w /tmp/base); git update-index --cacheinfo 100644,$blob,file; git commit -m "…"   # index only, no pathspec
  ```
- `git commit -- <path>` commits the working-tree state: a `git rm --cached` untrack is re-added while the file exists on disk → index-only commit.
- Stage and commit a `git rm`/`git mv` set in ONE command; the next agent's bare `git commit` sweeps a staged set into its commit.
- After an explicit-path commit of a generated set: `git status --short <paths>` (globs skip siblings silently).
- Write the commit message from `git show --stat`, not from what you believe you staged.
- **Commit after every meaningful step, gated or not.** A four-hour worker tree (twelve full case rebuilds) sat uncommitted until a `WIP … not yet
  gated` checkpoint; a subagent stops at its turn limit and everything not in HEAD is gone. Checkpoint commits say "not yet gated" in the message;
  the gated commit follows; the coordinator never commits another agent's half-edit but does read the checkpoints when it resumes (SKILL §11.1).
- A worker fork may not spawn agents: it writes the blind-review checklist and the artefact list into its record and hands the round back to the
  coordinator, never skips it silently.
- **A fork subagent stops at ~200 turns.** Plan the task in chunks that each end in a checkpoint commit + a STATUS line; when it stops, resume it (or a
  new agent) from HEAD with the MEASURED state, never from what the coordinator remembers it was doing.
- **One git worktree per parallel agent — never two agents in one working tree.** Two agents regenerating in the same tree corrupt each other's
  kit parity and record gates (a kit mirror compared against a sibling's half-written plate; a `--check` reading the other's STL). Each agent works
  in `git worktree add <dir> -b <agent-branch>`, commits there from a clean HEAD, and the coordinator moves `main` with a mixed reset / fast-forward
  once that worktree's gates are green. A `--copy` / kit-mirror step syncs EVERY plate of record (default, AMS, alternates + sidecars), not only the
  default — a partial mirror is a stale kit the parity gate reports as a design change (source: plug-cap + case agents, 2026-09-29).
- **Tags follow the gated commit.** A tag created on a checkpoint or a WIP commit is re-pointed (`git tag -f <tag> <gated commit>`) once the gated
  commit exists — and the record says so; a tag on a `not yet gated` commit is a false release marker.

## 3. Regenerating shared records
- Re-read (re-grep) the row immediately before replacing a status cell; prefer a suffix append over a full-cell rewrite.
- A matrix/report regenerated while a sibling's yaml is half-written turns every dependent check FAILED: diff the new FAILED ids against HEAD, attribute
  to the one shared cause, restore, report the numbers.
- `--check` gates in the main checkout while others regenerate say nothing about the committed tree: judge on `git archive HEAD` (clone gate).
- Rows that describe a marker (the nod marker, the release phrase) re-trigger the generator that keys on it: describe indirectly.
- Every checker is READ-ONLY on the tree: `--check` builds in a temp dir and exports nowhere (a schematic `--check --out /tmp` that still wrote
  `erc.json` into `out/` replaced the ERC of record with a temp copy's 58 lib-link warnings). `scripts/adopt_gates.sh` fails when
  `git status --porcelain` differs before/after the gates; the PR-check template ends with the same guard. Every skill script answers `--help` read-only (argparse); a project script must too — a
  script without argparse runs its default WRITE action on `--help`, so until it has one, probe its usage with `sed -n 1,12p` of its docstring.

## 4. Blind reviews (the protocol; templates in `workflows/`)
- Freeze: clean tree (`git status --short --untracked-files=no` empty), `git worktree add --detach <frozen> HEAD`, then
  `git -C <frozen> submodule update --init` (the skill submodule is empty in a fresh worktree and the `scripts` link dangles until then);
  reviewers read only there and write only their own report file in the live repo.
- Hand-off document v-n: generated header (`scripts/handoff_header.py`: board of record, HEAD md5 MATCH, package, case version, clean tree), the
  scope per specialty, the known/open list with dispositions, the claims of the round (for a delta audit) — the ONLY briefing. Plus the one-paragraph
  waiver list without reasoning so verifiers spend their budget on new defects.
- Reviewers never read other reviewers' output nor the author's reasoning (name the forbidden file patterns explicitly in the prompt).
- External models via the Cursor agent CLI: `agent -p --mode ask --model <m> --output-format text "<prompt>"` from the frozen worktree (ask/plan
  modes are read-only; `-p` alone has shell access — never for reviews); prompt ≤ ~30 kB naming the files (the model reads them; observed CLI
  limit, unversioned); packet ceiling ≈ 440 kB (observed: the CLI returns 0 bytes above it); rotate two vendors per role; an EMPTY report is a
  failure → retry once with the fallback model, note the substitution, else write the failure into the report and return zero findings. macOS has
  no `timeout`: background + PID + until-loop within the §5 ceiling.
- **Pairing that worked for a print kit (2026-09-30):** a **technician persona on the kit folders AS RECEIVED** (no repo, no git, unzips the
  3MFs, measures the STLs; "print the fit-check set and tell the engineer whether it fits") in parallel with an **FDM DFM persona measuring the
  meshes** (orientation, overhang angles, seat datums, slicer keys from the embedded config, not the sidecars); merged; fixed by ONE author agent
  in two phases (generators, then outputs + kits) with small commits. The technician found the two BLOCKERs (an un-instructed irreversible step, a
  hardware list into the wrong pocket) that every mesh check had passed; the DFM persona found the seat that rocked. Trust the reviewer's
  measurements, re-measure only where the geometry changed, and state every deviation from a disposition openly in the decision row.
- **The standard protocol** (SKILL.md §5 is the home; the mechanics live here): reviewers = a second model family where one
  is available (Opus beside Claude Code, a Cursor CLI model) + the in-session agent, briefed with the artefacts and the role's checklist ONLY — no
  decision log, no earlier reviews; **one verifier WITH record access** (DECISIONS, KNOWN_ISSUES, BLOCKERS, SPEC + `SPEC_ERRATA.md`, the test plan,
  netlist / mesh of record) classifies every finding **CONFIRMED / ALREADY DECIDED (row id; does its number still hold?) / REFUTED / PARTLY /
  UNVERIFIABLE** with a **rev-impact** column (ordered revision / arrival bench check / next revision / record only); the merge writes CC rows and
  **nothing is applied from a review without the verifier's row**. A CONFIRMED item whose closure is a bench step becomes an
  `ARRIVAL_CHECKLIST` row (`release-and-cut.md` §10). Record the already-decided rate per reviewer beside the refuted rate: a high rate means the
  decision rows do not name the fact they rest on, which is the cheaper fix.
- Adversarial verification detail: default REFUTED; open the cited files; a number about copper carries the script that produced it (a disputed
  clearance is one `Collide` bisection); a netlist claim is re-exported and parsed by the verifier (`<cad-cli> sch export netlist` + a 20-line
  parser), a mesh claim re-measured with trimesh on the STL of record; convert coordinate frames before calling a site "missing".
- Merge: verifier verdicts applied (REFUTED → rejected table with reason; ALREADY DECIDED → the row cited, no new row), dedupe by defect,
  corroboration matrix, REQUIRED / OWNER (proposed row text) / DOCUMENT / ACCEPT, explicit verdict, reviewer quality (findings, refuted rate,
  already-decided rate, empty runs per model), counts; commit with explicit paths.
- Visual inspections: tiles ≥ 40 px/mm with a mm legend burned in, per-net-class highlight renders, the external inspector sees ONLY the tiles
  (copy them into a fresh directory and run the CLI there).

## 5. Background jobs and the machine
- **The per-call wait ceiling is the harness's Bash timeout: 600 s per tool call (Claude Code, platform limit; the workflow templates' "≤ 8 min"
  waits are the same limit with margin).** Stated here once; every other mention points here. Block in-process, `until ! kill -0 $pid; do sleep
  20; done` per ≤ 600 s call, repeat, continue in the same turn.
- Redirected Python block-buffers: `python -u` or judge by `kill -0` + output files. Long chains: `python -u … > log 2>&1; echo EXIT $? >> log`
  per job, several jobs in parallel when they do not share memory ceilings (never two FEA pools), then one foreground
  `until grep -q '^EXIT' a.log && grep -q '^EXIT' b.log; do sleep 30; done` per ≤ 600 s call; a non-zero EXIT line stops the chain.
- Keep the machine awake (`caffeinate -dimsu` in a background shell) while agents run overnight; agents die on sleep and on API 500s — resume by
  message with the MEASURED state (board md5, counts, last commit), never from memory.
- **The machine can panic under load** (two macOS kernel watchdog panics on one review day: slicer + mesh checks + several agents): commit small
  and often (one commit per generator change, one per regenerated output set), write review reports INCREMENTALLY to their file (a finding at a
  time, not at the end), one worktree per agent, never two mesh / slicer pools at once. After a panic: resume from the MEASURED state (`git status`,
  last commit, the report file on disk), never from memory.
- Parallel router JVMs SIGTERM each other; one JVM at a time, `-mt 1` for determinism.
- Owner offline: list owner-only items (orders, gate cells, hardware records) at the pause point, never attempt them; kill a long chain early when an
  owner addition arrives through the coordinator.

## 6. Reporting
- Report before/after per class, not one number (a repo-wide grep count is not a work estimate).
- "Already done by <agent>" in the manifest instead of editing twice; re-read each target line before editing on a multi-agent day.
- Numbers in a record carry the mode they were measured in (check mode vs full run) and the file md5 they refer to.
- **The coordinator verifies a subagent's claim independently before it becomes a decision row.** Two "vendor: no flag" claims were premature DOM
  reads; re-requesting the vendor's analysis API for the md5 in the record flipped them (`references/dfm-printed-enclosure.md` §7). A claim of PASS
  names its evidence (API field, file md5, log line) or it is a claim, not a result.
- **Browser sessions are shared state.** The DevTools-driven browser can be restarted or re-used by another agent between two of your turns: page
  ids, tabs and the signed-in state are then gone. Re-list the pages, re-derive the id, re-check the sign-in (a fresh tab on the account URL) before
  every upload / read — never act on a page id from an earlier turn.

## 7. Memory, pause points, owner lists
- **Auto-memory (`MEMORY.md` + topic files)** holds what must survive a session: the project's resume pointer (which files to read first), owner
  feedback that changes how to work ("verify live, never cached"; "use parallel agents while I sleep"; "read the rendered image, not the geometry"),
  never project facts that live in the repo (those go to STATUS / DECISIONS). One file per feedback item with the date and the owner's words.
- **Pause point** (`docs/governance/STATUS.md`, numbered; skeleton at the end of `templates/STATUS.md`): what happened (rows, commits, tag), what is green, an **owner list** (numbered, each
  item owner-only: gate cells, payments, replies to the vendor, hardware records) that is struck through with date/time + record path as items
  close, and a **Resume** line (nothing running / what is running with its log path; read order). Written whenever the owner says they are going
  offline and at every tag.
- **Owner list discipline:** an item the agent may not do is listed, never attempted; when the owner delegates one in chat ("do it"), quote the
  words in the decision row, do exactly the named actions, record clicked / not clicked (`references/vendor-review.md` §1).
- **Resume by message with the measured state** (§5): board md5, package, case version, last commit, gates green — read from the repo, not
  remembered; a difference with STATE NOW becomes a STATUS paragraph before any work.
- **Paths in old records:** after a re-layout, frozen paragraphs spell the old paths; the pause point says "paths older than this: `scripts/reorg_paths.py --map`".

## 8. Resource budget and speed — without losing quality or the machine
The source project's host panicked twice (kernel watchdog) when several agents each ran the geometry kernel, the slicer on a stack of plates,
headless-browser PDF renders and the gate set at the same time — memory pressure, not CPU, is the likely trigger. Nothing below is a machine
constant: every number is derived from the host at run time or set in `project.yaml host:`; the host's facts (cores, RAM, the derived pool and
floor) are the ENV.md row `scripts/project.py env` prints on day 1.
1. **ONE heavy-job pool per machine — `scripts/jobs.sh -- <cmd>`**: a slot semaphore (pool = `host.jobs_max`, default max(1, cores // 4)),
   `nice -n 10`, and a gate that does not START a job while free memory < `host.min_free_gb` (default max(2 GB, 15 % of RAM)) or load1 > cores
   (it waits, then exits 2 after `--wait-max`); START / DONE lines with wall time and peak RSS in the pool's log. Every generator chain, slice
   run, render, FEA solve and record round goes through it; **agents never call the geometry kernel, the slicer or the renderer directly**
   (the Makefile pattern `templates/ci/Makefile` wires the targets through it).
2. **Caching policy — regenerate the geometry, cache only the expensive non-geometry steps.** With a fast geometry engine (the Manifold backend,
   item 5) the geometry of record and every row computed on it — STL exports, census, print DFM, clearances, previews — are regenerated on every
   chain run: a cache there is a source of stale-record and kit-parity defects, and the regeneration is cheap. A previous-md5 file may remain only
   as a DETERMINISM check (same SCAD → same md5; a difference is a finding, not a cache miss). Caching is reserved for expensive steps that are
   deterministic in their inputs and not geometry: slicer runs (keyed on STL md5 + settings md5, both in the sidecar — `--only-changed` the default,
   `--all` explicit), browser PDF renders (document md5), index builds; each cached step ships a `--check` that re-derives the md5s, so skipping is
   safe by construction. The job wrapper (item 1) is in place BEFORE the regenerate-everything policy, so a chain cannot overload the host. With a
   slow engine (a CGAL-only install) the policy inverts for STL exports only — exports keyed on the SCAD text, every consumer re-run after the final
   export pass (`case-pipeline.md`) — and the project says so in ENV.md.
3. **Serialize the record round**: one lock on the machine (`make record-round`: an atomic `mkdir` lock), once per batch of commits, never per
   agent; agents commit generators + outputs and leave the round to the coordinator or the last agent. The documented order (`release-and-cut.md`
   §3.1) is a fixed point: the second `release_report` pass runs only when `traceability --check` says the matrix changed.
4. **Concurrency budget**: ≤ 3 writing agents with heavy work at once (the pool refuses the fourth job, not the agent), read-only reviewers
   unlimited but told not to re-slice or re-render; one worktree per writing agent (§2).
5. **Geometry engine**: the 2021.01 OpenSCAD release's CGAL kernel is the slow part (minutes per body); the snapshot build ships the Manifold
   backend — `--backend=Manifold` (`openscad --help` of a snapshot lists `--backend arg: 'CGAL' (old/slow) [default] or 'Manifold' (new/fast)`
   **[V, OpenSCAD manual, wikibooks "Using OpenSCAD in a command line environment", 2026-09-30]**; `--enable=manifold` on older snapshots **[K]**),
   typically 10–100 × faster on the same files **[K, source project's reading]**, installs beside the release (`brew install --cask
   openscad@snapshot` on macOS; the AppImage / `openscad-nightly` package on Linux). The case pipeline detects the snapshot binary
   (`tools.geometry_cli_snapshot`, or `openscad --help | grep -q backend`) and passes the flag; tessellation differs slightly, so every STL md5
   moves on the first regeneration — acceptable (records regenerate per run) but **an engine switch is followed by one record round in one commit:
   "engine switch, md5s re-baselined"**, never mixed with a geometry change. `-q` always; per-body exports, never a whole-assembly re-render.
6. **Preview, not render, for pictures**: concept / review / kit `faces/` PNGs use the OpenCSG preview (`openscad -o x.png --preview`, seconds);
   `--render` (the full kernel) only for geometry of record — STL exports and gates — and for a picture whose rule needs the booleans resolved
   (a mark coupon's recess floor, a section view): the render set says which it is per image.
7. **Slicer / browser**: the slicer CLI one process per plate, never parallel plates (one plate is already multi-threaded); PDF rendering one
   headless browser instance reused across the document set.
8. **Measure**: every chain prints its wall time and peak RSS (`/usr/bin/time -l` on macOS, `-v` on Linux — the wrapper does it) into its sidecar /
   the pool log, so the retro can see where the time goes before anyone parallelises (`pitfalls.md`: 25.1 of 25.8 s was a selftest sleeping).
9. **Shorter loop for small tweaks**: a subagent round trip costs minutes of overhead. Criterion: **one yaml value or one emitter string = the
   coordinator edits it and runs ONE preview through the wrapper inline; a new feature, a new gate, or anything touching the records = an agent
   with its own worktree.** Restructures and full rounds are delegated; colour, a position, a label text are not.
