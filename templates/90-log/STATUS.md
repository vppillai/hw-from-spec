# STATUS.md — resume point

Read this file first, then `90-log/DECISIONS.md` (OPEN rows = owner items, listed in `90-log/KNOWN_ISSUES.md` §2), then `git status`. The newest dated
paragraph below is the state; earlier paragraphs are history. A **PAUSE POINT** paragraph lists exactly what the owner must do and what an agent
resumes with.

## STATE NOW
- Phase: {{PHASE}} (gate {{NEXT_GATE}} pending — owner line in 90-log/GATES.md)
- Record of record (`scripts/project.py record`; scope {{SCOPE}}): `{{BOARD_PATH_OR_STL_SET}}` md5 `{{MD5_OR_NONE}}`
- Package `{{PACKAGE_OR_NONE}}` {{ee,both}}
- Case `{{CASE_VERSION_OR_NONE}}` {{mech,both}}
- Gates green at HEAD: {{GATES_SUMMARY}} (day 1: `scripts/adopt_gates.sh` with the template's G0 list)

## Log (newest last)
**{{DATE}} {{TIME}} — project created from the hw-from-spec skill (commit {{SKILL_COMMIT}}).** project.yaml, templates, scripts installed; selftests + smoke + adopt gates green. Next: G0 spec review round (SKILL §5, ROLE_SET spec) → ask the owner for the G0 cell.

<!-- skeleton: begin — copied and filled per pause point; `scripts/project.py slots` ignores the slots between these markers -->
## PAUSE POINT n — {{DATE}} {{TIME}} (skeleton: copy, number, fill; `references/agent-ops.md` §7)
**What happened:** rows {{IDS}}, commits {{SHAS}}, tag {{TAG_OR_NONE}}. **Green at HEAD:** {{GATES}} (adopt gates, clone gate, --checks).
**Owner list** (owner-only items; struck through with date/time + record path as they close):
1. {{gate cell / payment / vendor reply / hardware record}}
**Resume:** nothing running | {{JOB}} running, log `{{LOG_PATH}}`; read order: STATUS → DECISIONS OPEN rows → `git status` → `scripts/handoff_header.py` → `scripts/adopt_gates.sh`.
Paths older than {{DATE}}: `scripts/reorg_paths.py --map` (only after a re-layout).
<!-- skeleton: end -->
