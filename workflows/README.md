# workflows/ — blind-review workflow templates

Four ES-module scripts for the Claude Code Workflow tool (`agent()`, `parallel()`, `pipeline()`, `phase()`, `log()` are provided by the runner).
They are templates: every `{{PLACEHOLDER}}` must be replaced before a run; a leftover placeholder is a bug (`grep -nE '\{\{[A-Z_*]+\}\}' gen/workflows/*.js`
must print nothing in the instantiated copy). Without a runner that provides `agent()/parallel()/pipeline()`, run the same prompts as sequential
subagents in the order of the phases (Prepare → Review → Verify → Merge). The blindness clauses hold while each reviewer gets the reviewer
part only (`scripts/handoff_header.py --reviewer-copy`).

| Template | Use | Shape |
|---|---|---|
| `blind-deep-review.js` | the **gate round** of the SKILL §5 "Review rounds" table, before a gate / an order; `{{ROLE_SET}}` = `spec` for the G0 round (10-spec/SPEC.md is the artefact), `board` later in ee / both (incl. the `case_dfm` role), `mech` for M1 / M2 / case order in mech scope | seats (≤ `reviews.max_roster`) × (1 in-session + 1 external) → verifier per seat → merge with REQUIRED / OWNER / DOCUMENT / ACCEPT + verdict; throws over the run cap |
| `delta-audit.js` | the **fix-check round** of the same table, or after a bounded change | same shape on the changed files, at most two per gate, filtered to the affected seats, briefed with the round's CLAIMS, merged against the previous audit item by item |
| `routing-inspection.js` | routed copper | tile every layer ≥ 40 px/mm → two blind inspectors (the external one sees ONLY the tiles) → merge to a fix list |
| (no template) double-blind drawing round | M1 of a printed part (SKILL §5) | reviewer A with ONLY the sheet + a one-paragraph intent → verifier B measures every claim on the meshes (VERIFIED / REFUTED / DRAWING DEFECT / JUDGMENT) → merge |
| `silk-audit-verify.js` | silk after a design change | audit → fix through yaml (copper signature unchanged) → blind visual verify A/B → merge + fix → re-verify |

## Instantiate
1. Copy the template to the project (`gen/workflows/<project>-<kind>-<round>.js`); the file is part of the record.
2. Fill the placeholders (`sed` or by hand). The common ones:
   - Identity: `{{PROJECT}}`, `{{PROJECT_ONE_LINE}}`, `{{ROUND}}`, `{{DATE}}`, `{{REPO_ROOT}}`, `{{FROZEN_WORKTREE}}`, `{{HANDOFF_DOC}}`, `{{REVIEW_TAG}}`.
   - Reports: `{{MERGED_REPORT}}`. `{{PREVIOUS_MERGED_REPORTS}}` is a comma-separated list for the deep review ('' for the first round).
     `{{PREVIOUS_MERGED_REPORT}}` is one report for the delta audit.
   - Tools: `{{CAD_PYTHON}}`, `{{CAD_CLI}}`, `{{FALLBACK_MODEL}}`, and `{{EXTERNAL_MODEL}}` (one model, for the inspection and the silk audit).
   - `{{EXTERNAL_MODELS}}`: quoted and comma-separated, at least one second-family model. Seat i gets entry i, cyclic.
   - The load cap: `{{MAX_ROSTER}}` and `{{MAX_RUNS_PER_GATE}}` come from `project.yaml` `reviews:`. `{{RUNS_USED_THIS_GATE}}` counts the
     reviewer runs already spent on this gate. `{{FIXCHECK_ROUND_NUMBER}}` is 1 or 2 (delta audit).
   - `{{PERSONAS_BY_KEY}}`: a JS object from seat key to a persona block of `templates/REVIEWER_PERSONAS.md`. `{}` keeps the titles.
   - `{{ROLE_SET}}`: `spec`, `board` or `mech`. The `mech` set is the M1 / case-order round of a mech-scope project.
   - `{{VERDICT_OPTIONS}}`: for example `order as is / order after the REQUIRED list / do not order yet`. At G0: `approve as is / after the REQUIRED edits / not yet`.
   - `{{BRIEF_*}}`: what each seat looks at (files, nets, interfaces). Never a decision row or a disposition. Numbers come from the hand-off, not the brief.
     The `spec` set: `BRIEF_SPEC`, `BRIEF_PARTS`, `BRIEF_MECH`, `BRIEF_TEST`.
     The `board` set has eight seats: `BRIEF_POWER`, `BRIEF_DIGITAL`, `BRIEF_LAYOUT`, `BRIEF_FAB` + `BRIEF_SILK`, `BRIEF_MECH`,
     `BRIEF_CASE_DFM` (the STL dir, the census and print-DFM records, `print_targets`), `BRIEF_SOFTWARE`, `BRIEF_COHERENCE` + `BRIEF_GATES`.
     The `mech` set: `BRIEF_CASE_DFM`, `BRIEF_MECH`, `BRIEF_PARTS`, `BRIEF_GATES`. The delta audit adds `BRIEF_DOCS`.
   - Delta audit: `{{ROUND_CONTEXT}}`, `{{CLAIMS}}`, `{{DELTA_ROLE_KEYS}}`.
   - Inspection: `{{BOARD_FILE}}`, `{{BOARD_YAML}}`, `{{BOARD_STATE}}`, `{{RULES_OF_RECORD}}`, `{{INSPECTION_DIR}}`, `{{COPPER_LAYERS}}`,
     `{{CHECKLIST_SOURCE}}`, `{{NET_CLASS_HIGHLIGHTS}}`, `{{RUN_TAG}}`.
   - Silk: `{{SILK_REGEN_COMMAND}}`, `{{COPPER_SIGNATURE_COMMAND}}`, `{{EXPORT_COMMAND}}`, `{{CROPS_COMMAND}}`. `{{SILK_DESIGN_INTENT}}` is the board's silk feature set (straps, legends, LED labels).
     `{{SILK_METRICS}}` holds the measured glyph widths and the via-to-ink cost of this board.
3. Freeze: commit, `git status --short --untracked-files=no` empty, `git worktree add --detach <frozen> HEAD`, then
   `git -C <frozen> submodule update --init` (a detached worktree leaves the skill submodule empty and the `scripts` link dangling); write the
   hand-off with `scripts/handoff_header.py` output under §0 (HEAD md5 MATCH, clean tree; at G0 board/package/case read MISSING by design) and
   the one-paragraph waiver list.
4. Run the workflow; the merge phase commits the review files with explicit paths.
5. After the round: dispositions into the decision log (OWNER rows), generator/YAML changes for REQUIRED items, the merged report path into the
   verifier annex of the next hand-off (never the reviewer part).

## External models
The templates call the Cursor agent CLI (`agent -p --mode ask --model <m> --output-format text "<prompt>"`), read-only, from the frozen worktree.
The inspection runs it from a scratch dir that holds only the tiles. `{{EXTERNAL_MODELS}}` needs at least one entry. Seat i gets entry i
(cyclic), so two or more entries rotate the vendors between seats. The templates throw on an empty list. A fallback model replaces an
empty report. The wrapper agent never judges the artefact itself. Keep the prompt at about 30 kB or less, and name the files in it.
The packet ceiling is about 440 kB: above it the CLI returns 0 bytes with no error. macOS has no `timeout`. Run the CLI in the
background with an EXIT line in its log, and wait on the completion notification or the `^EXIT` line.

**In-session-only fallback** (no CLI, no API keys): keep the in-session reviewer, replace each `external()` call with a second in-session agent
given a different persona and a different reading order (`{ label: 'review:<role>:claude-2' }`), keep the verifier and the merge unchanged. It is
weaker (same model family) — say so in the merged report's reviewer-quality section.

## The two paragraphs every template repeats (kept inline in each file because a template runs alone)
- **Wrapper contract** (every `external()` / wrapper agent). Run the external CLI from the frozen worktree, or from a scratch dir that holds
  only the tiles. Keep the prompt at about 30 kB or less, and name the files in it. Launch it in the background with an EXIT line in the log.
  Wait on the harness's completion notification or the `^EXIT` line, never a foreground sleep loop (`references/agent-ops.md` §5).
  Then `test -s` the report. An EMPTY or error-only report is a failure: retry once with the fallback model and note the substitution.
  If the retry fails too, write the failure into the report and return zero findings. The wrapper never judges the artefact itself.
- **Blindness clause** (every reviewer prompt). The only briefing is the reviewer copy of the hand-off in the frozen worktree
  (`<handoff>.reviewer.md`, written by `scripts/handoff_header.py --reviewer-copy` in the Prepare phase). Never read the full hand-off, `90-log/DECISIONS.md`, `90-log/KNOWN_ISSUES.md`, `10-spec/SPEC_ERRATA.md`,
  `80-reviews/<TAG>_*` or earlier merged reviews. Never read the live repo, except to write the own report. Every finding cites
  file + line / coordinate / refdes / net and says how it was checked. Severity is BLOCKER / MAJOR / MINOR / NOTE, as the hand-off defines them.

## Why these shapes
- Blindness is structural: a detached worktree, the reviewer part of the hand-off as the only briefing, forbidden file patterns named in the prompt, reports written
  outside the worktree. Reviews that read the author's dispositions or another reviewer's output found what they were told to find.
- Adversarial verification (default REFUTED) removed ~30–50 % of BLOCKER/MAJOR claims per round in one measured project; the merge lists refuted
  items with the reason so they are not re-raised.
- Visual gates read images; geometric silk checks passed boards with blank bars and mutilated words.
- Every round is a file set in `80-reviews/` plus one merged report; the hand-off version bumps; the workflow file itself is committed.
