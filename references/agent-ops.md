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
- **Long chains run in the BACKGROUND and are waited on by the harness, never by a foreground loop.** Every job writes its own log and ends it
  with `echo EXIT $? >> log` (`python -u` — a redirected Python block-buffers); start the chain with the harness's background-run option (or
  `nohup … &`) and wait on the `^EXIT` line with the harness's completion notification or its monitor primitive. A foreground `sleep` / `until`
  loop is refused by current harnesses and, where a harness still allows it, is bounded by its per-call timeout (600 s per tool call in Claude
  Code) — stated here once, every other mention points here. Several jobs at once only through the pool (§8 item 1; never two FEA pools); a
  non-zero EXIT line stops the chain.
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
A host panics (kernel watchdog) when several agents each run the geometry kernel, the slicer on a stack of plates, headless-browser PDF renders
and the gate set at the same time — stacked per-tool pools, memory pressure and load, not one slow tool. Nothing below is a machine constant:
every number is derived from the host at run time or set in `project.yaml host:`; the host's facts (cores, RAM, the derived pool and floor) are
the ENV.md row `scripts/project.py env` prints on day 1. The rules are in the order they are applied: measure, audit, then change.
1. **ONE heavy-job pool per machine — `scripts/jobs.sh -- <cmd>`**: a slot semaphore (pool = `host.jobs_max`, default max(1, cores // 4)),
   `nice -n 10`, and a gate that does not START a job while free memory < `host.min_free_gb` (default max(2 GB, 15 % of RAM)) or load1 > cores
   (it waits, then exits 2 after `--wait-max`); START / DONE lines with wall time and peak RSS in the pool's log. Every generator chain, slice
   run, render, FEA solve and record round goes through it; **agents never call the geometry kernel, the slicer or the renderer directly**
   (the Makefile pattern `templates/ci/Makefile` wires the targets through it). A generator's own pool (`--jobs`) equals the host pool and nests
   inside ONE slot (a chain holds one slot; a job started inside a held slot passes straight through). **A multithreaded tool (the CAD CLI, the
   slicer, the geometry kernel's parallel passes) counts as a whole slot and still exceeds it**: the load gate, not the slot count, is the control
   that sees it — one CLI selftest or four gate steps can push the 1-min load past twice the core count on its own. **Mesh checks (the census,
   print DFM) and offscreen renders are heavy jobs too**: through the pool, one slot each, never beside a CAD export outside it — a census with
   trimesh's default rtree ray engine holds rays × candidate triangles and needs tens of GB for a large body at the census density (one took a
   24 GB host down); `embreex` in the mesh stack gives trimesh the Embree engine and the same census runs in seconds under 1 GB (`pitfalls.md`).
2. **Measure first, then audit, then change.** (a) Measure serially: a detached worktree replica (`git worktree add --detach`), one stage at a
   time under `nice` with `/usr/bin/time -l` (macOS; `-v` on Linux) and `uptime`, wall + peak RSS per chain, per plate, per record-round step, per
   gate step — the wrapper writes the same two numbers into the pool log on every job, so the retro sees where the time goes before anyone
   parallelises (`pitfalls.md`: a selftest sleeping was most of a "slow" chain; a fresh checkout's one artefact is an mtime freshness guard that
   fails). (b) Audit redundancy from git, not from memory: diff the sidecars per commit over the day — slices on unchanged inputs (a sliced plate
   file carries a fresh UUID, so every redundant slice is a tracked-file change), byte-identical re-renders, record rounds per day. (c) Only then
   change, one knob per commit, and name each gain correctly in the trade table (an incremental-slice rule is a records-churn fix when the slicer
   itself costs seconds; a wrapper is a stability fix; an engine switch is a time fix).
3. **Caching policy.** Previews regenerate on every run (seconds with the preview engine, item 6). **Expensive geometry of record may be cached
   ONLY on an inputs + engine key** (the SCAD text and every file it includes, the preset's merged yaml, the engine binary and its version), and
   every export — cached or fresh — carries the sidecar md5 as a **determinism check**: canonicalise the mesh (`dfm-printed-enclosure.md` §7.2),
   THEN record the md5; a different md5 under an unchanged key is a FAIL row, never a cache miss; `--no-cache` forces the export. Caching of the
   non-geometry steps stays behind a `--check` that re-derives the md5s so skipping is safe by construction: slicer runs (STL md5 + settings md5 in
   the sidecar — the incremental rule is the default, `--all` explicit), browser PDF renders (document md5), index builds. **Regenerating everything
   once is the best audit of the records**: a full regeneration with the caches off is what finds a sampler that was never seeded (every recorded
   census one random draw) and a body that a canonicaliser had left non-watertight for weeks — the caches had hidden both. Do it once per engine
   switch, once per rule-set change, and once before a cut. The job wrapper (item 1) is in place BEFORE a regenerate-everything run so the chain
   cannot overload the host.
4. **Serialize the record round**: one lock on the machine (`make record-round`: an atomic `mkdir` lock), once per batch of commits, never per
   agent or per commit; agents commit generators + outputs and leave the round to the coordinator or the last agent of the batch. The documented
   order (`release-and-cut.md` §3.1) is a fixed point: the second `release_report` pass runs only when `traceability --check` says the matrix
   changed; the index and PDF steps are skipped when their `--check` passes.
5. **Concurrency budget**: at most `host.jobs_max` writing agents with heavy work at once (the pool refuses the next job, not the agent),
   read-only reviewers unlimited but told not to re-slice or re-render; one worktree per writing agent (§2).
6. **Geometry engine — previews on the fast engine, geometry of record on the engine that passes the mesh gates.** The 2021.01 OpenSCAD release's
   CGAL kernel is slow (minutes per body); the snapshot build ships the Manifold backend — `--backend=Manifold` (`openscad --help` of a snapshot
   lists `--backend arg: 'CGAL' (old/slow) [default] or 'Manifold' (new/fast)` **[V, OpenSCAD manual, wikibooks "Using OpenSCAD in a command
   line environment", 2026-09-30]**; `--enable=manifold` on older snapshots **[K]**), installs beside the release (`brew install --cask
   openscad@snapshot` on macOS; the AppImage / `openscad-nightly` package on Linux), **measured 100–270 × faster per body and byte-deterministic
   [V, the worked example below]**. But faster and "the same bbox and volume" is not rule-equivalent: on real bodies the Manifold meshes can carry
   odd edges (not watertight in any export format), a membrane, sub-minimum regions under print DFM and a spurious intersection the CGAL meshes do
   not have — and a signed-volume sum cancels internal faces, so volume agreement proves nothing. **The rule**: Manifold for every PREVIEW / PNG
   (seconds, pixel-indistinguishable); **STL exports OF RECORD stay on the engine that passes the chain's own mesh gates** (watertight, census,
   print DFM, interference) on the bodies of record — an engine is judged by those gates, never by bbox / volume agreement. `engine:` is a
   per-preset yaml key (`case.presets.<name>.engine`, `case-pipeline.md`); the case pipeline detects the snapshot binary (`tools.geometry_cli_snapshot`,
   or `openscad --help | grep -q backend`) and passes the flag for previews. Re-test Manifold per OpenSCAD release (one full regeneration through
   the gates, item 3); when a release passes, the switch is one record round in one commit — "engine switch, md5s re-baselined" — never mixed with
   a geometry change (tessellation differs, every STL md5 moves). `-q` always; per-body exports, never a whole-assembly re-render. With the
   fast engine the CAD export is not the slow step of a chain — a kinematic sweep (hundreds of poses) or an animation becomes affordable as
   previews — and the pool's slots (item 1) go to the mesh checks and the slicer.
7. **Preview, not render, for pictures**: concept / review / kit `faces/` PNGs use the OpenCSG preview (`openscad -o x.png --preview`, seconds);
   `--render` (the full kernel) only for geometry of record — STL exports and gates — and for a picture whose rule needs the booleans resolved
   (a mark coupon's recess floor, a section view): the render set says which it is per image.
8. **Slicer / browser**: the slicer CLI one process per plate, never parallel plates (one plate is already multi-threaded); PDF rendering one
   headless browser instance reused across the document set.
9. **Shorter loop for small tweaks**: a subagent round trip costs minutes of overhead. Criterion: **one yaml value or one emitter string = the
   coordinator edits it and runs ONE preview through the wrapper inline; a new feature, a new gate, or anything touching the records = an agent
   with its own worktree.** Restructures and full rounds are delegated; colour, a position, a label text are not. A value no generator reads (a
   sidecar row, a text cell) is an inline edit with no chain re-run: run the generator whose `--check` says STALE, nothing more. The inner
   tier runner (`scripts/iteration_gate.sh --tier inner -- "<generator> --check" "<grader>"`) is that loop under the read-only guard.
10. **The project's CLAUDE.md carries the five operating lines** (`templates/CLAUDE.md` "Agent operations": wrapper only, ≤ pool writing agents,
    one record round per batch, the caching + engine policy, one-knob changes inline) with the host's pool number filled from `scripts/project.py env`.

<!-- worked example: begin (source project, 2026-09-30 — the one fenced example of this reference; the rules above are the generic form) -->
Worked example — one measured round on a 14-core / 24 GB laptop, three agents, a two-piece printed case with a lid chain and a caps chain:
- Trigger: two kernel watchdog panics in one day at load ~40 — two OpenSCAD chains (each a cores-2 pool), the adopt gates (4 steps) and the
  traceability matrix at once = 36–40 runnable processes on 14 cores. Measured alone: the adopt gates at 4 steps reach load 35; ONE `kicad-cli`
  panelize selftest reaches load 30 (a multithreaded tool counts as one slot and still floods the host).
- Measured serially in a detached worktree replica (`nice`, `/usr/bin/time -l`), cold caches, CGAL 2021.01: lid chain 373 s / 5.2 GB peak RSS
  (65 pair / iso PNG views alone 123–136 s), caps chain 192 s / 8.1 GB, slicer 0.7–6 s per plate, record round 2.5 min, adopt gates 51 s.
- Redundancy audit from the day's 38 commits, sidecars diffed per commit: 93 slices of which 24 on unchanged inputs (the .3mf carries a fresh
  UUID per slice, so each was a tracked-file change), 1119 OpenSCAD runs of which 755 produced byte-identical output, 9 record rounds in one day.
- Changes, one per commit: wrapper (pool = 14 // 4 = 3 slots, floor max(2 GB, 15 % × 24 GB) = 3.6 GB, load gate 14, every OpenSCAD / slicer /
  Chrome / chain / `make check` through it; generator pools 3 instead of 12); incremental slicing by the `--check` rule (20 plates current, 0
  re-sliced on an unchanged tree); `make record-round` under one lock with the second report pass only when the matrix changed.
- Engine test, same SCAD of record, one body at a time: snapshot 2026.09.30 `--backend Manifold` exports 100–270 × faster, bbox equal, volume
  equal to 2.4e-6, PNGs byte-deterministic — and FAILS the chain's own mesh gates: 11 and 6 odd edges on the tray and the shell (not watertight in
  every export format tried), a shell membrane, sub-0.9 mm regions under print DFM, a 18.6 mm³ fixture–board intersection absent from the CGAL
  meshes. Decision: Manifold for every PNG preview (the 65 views 123–136 s → 13–15 s per chain), STL exports of record stay CGAL per preset
  (`engine:` key), re-test per snapshot.
- Regenerating everything once with the caches off found two latent record defects: the census sampler was seeded through `np.random.seed`
  only (trimesh ≥ 4 ignores it — every census JSON of record was one random draw; seeded explicitly, records re-baselined, 0 FAIL everywhere), and
  the STL canonicaliser dropped a 2e-5 mm sliver that carried the connectivity between two near-coincident vertices, leaving one cap non-watertight
  for sixteen releases (snap the closest pair first, then drop what collapsed; bodies without slivers keep their bytes).
- Steady state after the round: lid chain 129 s warm / 5.8 GB through the wrapper, zero panics, one record round per batch.
<!-- worked example: end -->
