<!-- the briefing every reviewer received (identical inputs); 2026-10-08 -->
# Blind review brief — hw-from-spec 0.11.13 (frozen copy)

You review a Claude Code skill that runs hardware projects (a PCB, a printed enclosure, or both) from a written spec to a production cut.
The artefact is the frozen tree at SKILL_DIR (a `git archive` of the release; no .git). Read only there. Write only your report file.

Rules
- Do not edit anything under SKILL_DIR. Do not run any git command that changes state. Do not read `SKILL_DIR/docs/reviews/*` (earlier reviews) and do not search the internet for this skill. Your own scratch work goes under WORK_DIR.
- Every finding carries evidence you produced: a file:line you read, or a command and its output. Separate MEASURED (you ran it / read it) from JUDGMENT (your opinion). No finding without a reproduction.
- Severity: BLOCKER (a user cannot complete the step / a rule is wrong in a way that ships a defect), MAJOR (wrong, contradictory or missing in a way that costs a round), MINOR, NOTE.
- Also report what you checked and found correct (one line each), so the merge knows the coverage.
- An empty finding list is a valid result if you state what you tried.

Report format (markdown, to REPORT_PATH)
```
<!-- blind reviewer ROLE_ID: MODEL_NAME; artefact + checklist only; 2026-10-08 -->
# Blind review ROLE_ID — hw-from-spec 0.11.13 (ROLE_NAME)
## Setup (what you ran, where)
## Findings
| id | sev | where | what | evidence | suggested fix |
## Checked and correct
## Coverage limits (what you could not run or read)
```
Number findings ROLE_ID-1, ROLE_ID-2, …  Keep each cell under ~60 words. Write the report incrementally (append as you go) so a timeout still leaves a partial report.

# Role A — cold user, both scopes (ee, mech, both)
You are an engineer who has never seen this skill. You have the README, SKILL.md, references, templates and scripts. Do what the README and SKILL.md §0 tell a new user to do, literally, in WORK_DIR, for each scope you can (`both` first, then `ee`, then `mech`). Use the Python at PYTHON (pyyaml available; mesh libraries may be absent - say so where it matters).
Check and report:
1. Day 1: can you create a project folder the way README "Use in a new project" + SKILL §0 say, resolve the scope, fill the templates, and run the day-1 gate list green? Every command that fails, every path that does not exist, every step whose wording you could not follow = a finding with the command and output.
2. The kickoff questionnaire: can you answer it from the text alone? Are the recommended answers there? Any question that needs information the skill never tells you to gather?
3. Gates: for each gate (G0/G1/G2 or M1/M2) is it clear WHO writes the approval WHERE, and does a script refuse the next phase when it is missing? Try to skip a gate and see what stops you.
4. Scripts: run every `--selftest` and `--check` the README names, from a fresh project and from the skill folder. Report any traceback, any silent pass on bad input you can construct, any script the docs name that does not exist, any flag the docs name that the script lacks.
5. Writing: the skill claims to follow `references/writing-style.md`. Where did the text make you guess (an actor missing, a pronoun with no referent, a step out of order, a number without a unit or a source tag)? Quote the sentence.
6. The 0.11.12/0.11.13 changes (writing standard, style lint): does `scripts/style_lint.py` behave as `references/writing-style.md` and SKILL §0 step 9 describe (default files, `--project ROOT`, a relative file argument, `--report`, the `<!-- style: ok -->` marker)? Does the skill's own text pass its own lint?
7. Anything a first-time user would get wrong because two files disagree (paths, folder names, gate names, versions).

# Role B — domain expert (PCB fab DFM, printed-enclosure DFM, process)
You are a senior hardware engineer who has shipped boards at contract fabs and printed enclosures (FDM, MJF, SLA). Read SKILL.md and every file under references/ and templates/ as a reviewer of RULES, NUMBERS and PROCESS, not as a user. Use PYTHON for any check you want to run (pyyaml available; mesh libraries may be absent).
Check and report:
1. Every rule with a number (a wall thickness, a clearance, a cap height, a stock floor, a tolerance): is it physically right for the process it names, is its source tagged ([physics], [vendor], [measured], [convention], [owner]), and does any other file state a different number for the same thing? Quote both.
2. Contradictions between SKILL.md and a reference, or between two references (order of steps, who approves, what a gate requires).
3. Rules the text states but no script enforces, where the text claims enforcement. Rules a script enforces that the text never states.
4. Process gaps that cost a fab round: steps a contract fab (PCBA engineer questions, placement confirmation, print-vendor file review) needs that the skill does not prepare for. Say what is missing and where it belongs.
5. The writing standard (`references/writing-style.md`, 0.11.12): read the rewritten references (pitfalls.md, dfm-printed-enclosure.md, vendor-review.md, case-pipeline.md, pcb-layout-dfm.md, fab-dfm.md). Did any sentence lose a condition, a qualifier (never / only / must / may), an actor or a threshold in the split? Quote the sentence and say what a reader would now do differently. Does the text follow its own rules (one instruction per sentence, active voice, actor named)?
6. Scripts that measure (thin_wall_census.py, print_dfm.py, stability.py, style_lint.py, heatmap_count.py and any other measuring script): read the measuring code; is the metric what the docs say it is? Any off-by-one, unit, sign or sampling error you can show with a small constructed input?
7. What you checked and found right (one line each).
