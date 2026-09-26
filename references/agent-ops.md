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

## 3. Regenerating shared records
- Re-read (re-grep) the row immediately before replacing a status cell; prefer a suffix append over a full-cell rewrite.
- A matrix/report regenerated while a sibling's yaml is half-written turns every dependent check FAILED: diff the new FAILED ids against HEAD, attribute
  to the one shared cause, restore, report the numbers.
- `--check` gates in the main checkout while others regenerate say nothing about the committed tree: judge on `git archive HEAD` (clone gate).
- Rows that describe a marker (the nod marker, the release phrase) re-trigger the generator that keys on it: describe indirectly.
- Every checker is READ-ONLY on the tree: `--check` builds in a temp dir and exports nowhere (a schematic `--check --out /tmp` that still wrote
  `erc.json` into `out/` replaced the ERC of record with a temp copy's 58 lib-link warnings). `scripts/adopt_gates.sh` fails when
  `git status --porcelain` differs before/after the gates; the PR-check template ends with the same guard. Probe a script's usage with
  `sed -n 1,12p` of its docstring, never by running it: a script without argparse runs its default WRITE action on `--help`.

## 4. Blind reviews (the protocol; templates in `workflows/`)
- Freeze: clean tree (`git status --short --untracked-files=no` empty), `git worktree add --detach <frozen> HEAD`, then
  `git -C <frozen> submodule update --init` (the skill submodule is empty in a fresh worktree and the `scripts` link dangles until then);
  reviewers read only there and write only their own report file in the live repo.
- Hand-off document v-n: generated header (`scripts/handoff_header.py`: board of record, HEAD md5 MATCH, package, case version, clean tree), the
  scope per specialty, the known/open list with dispositions, the claims of the round (for a delta audit) — the ONLY briefing. Plus the one-paragraph
  waiver list without reasoning so verifiers spend their budget on new defects.
- Reviewers never read other reviewers' output nor the author's reasoning (name the forbidden file patterns explicitly in the prompt).
- External models via the Cursor agent CLI: `agent -p --mode ask --model <m> --output-format text "<prompt>"` from the frozen worktree (ask/plan
  modes are read-only; `-p` alone has shell access — never for reviews); prompt ≤ ~30 kB naming the files (the model reads them); packet ceiling
  ≈ 440 kB; rotate two vendors per role; an EMPTY report is a failure → retry once with the fallback model, note the substitution, else write the
  failure into the report and return zero findings. macOS has no `timeout`: background + PID + until-loop ≤ 8 min per call.
- Adversarial verifier per specialty on every BLOCKER/MAJOR: default REFUTED; open the cited files; a number about copper carries the script that
  produced it (a disputed clearance is one `Collide` bisection); convert coordinate frames before calling a site "missing".
- Merge: verifier verdicts applied (REFUTED → rejected table with reason), dedupe by defect, corroboration matrix, REQUIRED / OWNER (proposed row
  text) / DOCUMENT / ACCEPT, explicit verdict, reviewer quality (findings, refuted rate, empty runs per model), counts; commit with explicit paths.
- Visual inspections: tiles ≥ 40 px/mm with a mm legend burned in, per-net-class highlight renders, the external inspector sees ONLY the tiles
  (copy them into a fresh directory and run the CLI there).

## 5. Background jobs and the machine
- Task watchers may not wake the agent: block in-process, `until ! kill -0 $pid; do sleep 20; done` (≤ 600 s per call, repeat), continue in the same turn.
- Redirected Python block-buffers: `python -u` or judge by `kill -0` + output files. Long chains: `python -u … > log 2>&1; echo EXIT $? >> log`
  per job, several jobs in parallel when they do not share memory ceilings (never two FEA pools), then one foreground
  `until grep -q '^EXIT' a.log && grep -q '^EXIT' b.log; do sleep 30; done` per ≤ 600 s call; a non-zero EXIT line stops the chain.
- Keep the machine awake (`caffeinate -dimsu` in a background shell) while agents run overnight; agents die on sleep and on API 500s — resume by
  message with the MEASURED state (board md5, counts, last commit), never from memory.
- Parallel router JVMs SIGTERM each other; one JVM at a time, `-mt 1` for determinism.
- Owner offline: list owner-only items (orders, gate cells, hardware records) at the pause point, never attempt them; kill a long chain early when an
  owner addition arrives through the coordinator.

## 6. Reporting
- Report before/after per class, not one number (a repo-wide grep count is not a work estimate).
- "Already done by <agent>" in the manifest instead of editing twice; re-read each target line before editing on a multi-agent day.
- Numbers in a record carry the mode they were measured in (check mode vs full run) and the file md5 they refer to.

## 7. Memory, pause points, owner lists
- **Auto-memory (`MEMORY.md` + topic files)** holds what must survive a session: the project's resume pointer (which files to read first), owner
  feedback that changes how to work ("verify live, never cached"; "use parallel agents while I sleep"; "read the rendered image, not the geometry"),
  never project facts that live in the repo (those go to STATUS / DECISIONS). One file per feedback item with the date and the owner's words.
- **Pause point** (`docs/governance/STATUS.md`, numbered): what happened (rows, commits, tag), what is green, an **owner list** (numbered, each
  item owner-only: gate cells, payments, replies to the vendor, hardware records) that is struck through with date/time + record path as items
  close, and a **Resume** line (nothing running / what is running with its log path; read order). Written whenever the owner says they are going
  offline and at every tag.
- **Owner list discipline:** an item the agent may not do is listed, never attempted; when the owner delegates one in chat ("do it"), quote the
  words in the decision row, do exactly the named actions, record clicked / not clicked (`references/vendor-review.md` §1).
- **Resume by message with the measured state** (§5): board md5, package, case version, last commit, gates green — read from the repo, not
  remembered; a difference with STATE NOW becomes a STATUS paragraph before any work.
- **Paths in old records:** after a re-layout, frozen paragraphs spell the old paths; the pause point says "paths older than this: `scripts/reorg_paths.py --map`".
