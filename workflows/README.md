# workflows/ — blind-review workflow templates

Four ES-module scripts for the Claude Code Workflow tool (`agent()`, `parallel()`, `pipeline()`, `phase()`, `log()` are provided by the runner).
They are templates: every `{{PLACEHOLDER}}` must be replaced before a run; a leftover double brace is a bug (`grep -n '{{' gen/workflows/*.js`
must print nothing in the instantiated copy). Without a runner that provides `agent()/parallel()/pipeline()`, run the same prompts as sequential
subagents in the order of the phases (Review → Verify → Merge) — the blindness clauses hold as long as each reviewer gets only the hand-off.

| Template | Use | Shape |
|---|---|---|
| `blind-deep-review.js` | **one review round** (SKILL §5: the unit every gate needs) before a gate / an order; `{{ROLE_SET}}` = `spec` for the G0 round (SPEC.md is the artefact), `board` later in ee / both (incl. the `case_dfm` role), `mech` for M1 / M2 / case order in mech scope | roles × (1 in-session + 2 external) → verifier per role → merge with REQUIRED / OWNER / DOCUMENT / ACCEPT + verdict |
| `delta-audit.js` | after a bounded change | same, filtered to the affected roles, briefed with the round's CLAIMS, merged against the previous audit item by item |
| `routing-inspection.js` | routed copper | tile every layer ≥ 40 px/mm → two blind inspectors (the external one sees ONLY the tiles) → merge to a fix list |
| `silk-audit-verify.js` | silk after a design change | audit → fix through yaml (copper signature unchanged) → blind visual verify A/B → merge + fix → re-verify |

## Instantiate
1. Copy the template to the project (`gen/workflows/<project>-<kind>-<round>.js`); the file is part of the record.
2. Fill the placeholders (`sed` or by hand). Common ones:
   `{{PROJECT}}`, `{{PROJECT_ONE_LINE}}`, `{{ROUND}}`, `{{DATE}}`, `{{REPO_ROOT}}`, `{{FROZEN_WORKTREE}}`, `{{HANDOFF_DOC}}`, `{{REVIEW_TAG}}`,
   `{{MERGED_REPORT}}`, `{{PREVIOUS_MERGED_REPORTS}}` (deep review, comma-separated, '' for the first round) / `{{PREVIOUS_MERGED_REPORT}}` (delta, one),
   `{{CAD_PYTHON}}`, `{{CAD_CLI}}`, `{{EXTERNAL_MODELS}}` (quoted, comma-separated, **at least two distinct models** — role i gets entries i and i+1),
   `{{EXTERNAL_MODEL}}` (one model: inspection, silk), `{{FALLBACK_MODEL}}`, `{{ROLE_SET}}` (`spec` | `board` | `mech` — the M1 / case-order round of a mech-scope project: case_dfm, mechanical intent, hardware, gates),
   `{{VERDICT_OPTIONS}}` (e.g. `order the <md5> package as is / order after the REQUIRED list / do not order yet`; at G0 `approve the spec as is / after the REQUIRED edits / not yet`),
   `{{BRIEF_*}}` (what each specialty looks at: files, nets, decision rows — numbers come from the hand-off, not the brief; G0 uses `BRIEF_SPEC`, `BRIEF_PARTS`, `BRIEF_MECH`, `BRIEF_TEST`; the board set adds `BRIEF_CASE_DFM`: the STL dir, the census JSONs, `print_targets`),
   `{{ROUND_CONTEXT}}` / `{{CLAIMS}}` / `{{DELTA_ROLE_KEYS}}` (delta), `{{BOARD_FILE}}`, `{{BOARD_YAML}}`, `{{BOARD_STATE}}`, `{{RULES_OF_RECORD}}`,
   `{{INSPECTION_DIR}}`, `{{COPPER_LAYERS}}`, `{{CHECKLIST_SOURCE}}`, `{{NET_CLASS_HIGHLIGHTS}}`, `{{RUN_TAG}}`,
   `{{SILK_REGEN_COMMAND}}`, `{{COPPER_SIGNATURE_COMMAND}}`, `{{EXPORT_COMMAND}}`, `{{CROPS_COMMAND}}`, `{{SILK_DESIGN_INTENT}}`, `{{RECROP_DIR}}`.
3. Freeze: commit, `git status --short --untracked-files=no` empty, `git worktree add --detach <frozen> HEAD`, then
   `git -C <frozen> submodule update --init` (a detached worktree leaves the skill submodule empty and the `scripts` link dangling); write the
   hand-off with `scripts/handoff_header.py` output under §0 (HEAD md5 MATCH, clean tree; at G0 board/package/case read MISSING by design) and
   the one-paragraph waiver list.
4. Run the workflow; the merge phase commits the review files with explicit paths.
5. After the round: dispositions into the decision log (OWNER rows), generator/YAML changes for REQUIRED items, the merged report path into the
   hand-off's known/open list for the next round.

## External models
The templates call the Cursor agent CLI (`agent -p --mode ask --model <m> --output-format text "<prompt>"`), read-only, from the frozen worktree
(or, for the inspection, from a scratch dir holding only the tiles). `{{EXTERNAL_MODELS}}` needs at least two distinct entries: role i gets
entries i and i+1 (cyclic), so every role sees two vendors for any list length ≥ 2 (the templates throw otherwise); a fallback model on an empty report; the wrapper
agent never judges the artefact itself. Prompt ≤ ~30 kB naming the files; packet ceiling ≈ 440 kB (the CLI returns 0 bytes above it without an
error). macOS has no `timeout`: background + PID + until-loops.

**In-session-only fallback** (no CLI, no API keys): keep the in-session reviewer, replace each `external()` call with a second in-session agent
given a different persona and a different reading order (`{ label: 'review:<role>:claude-2' }`), keep the verifier and the merge unchanged. It is
weaker (same model family) — say so in the merged report's reviewer-quality section.

## Why these shapes
- Blindness is structural: a detached worktree, a hand-off as the only briefing, forbidden file patterns named in the prompt, reports written
  outside the worktree. Reviews that read the author's dispositions or another reviewer's output found what they were told to find.
- Adversarial verification (default REFUTED) removed ~30–50 % of BLOCKER/MAJOR claims per round in the source project; the merge lists refuted
  items with the reason so they are not re-raised.
- Visual gates read images; geometric silk checks passed boards with blank bars and mutilated words.
- Every round is a file set in `docs/reviews/` plus one merged report; the hand-off version bumps; the workflow file itself is committed.
