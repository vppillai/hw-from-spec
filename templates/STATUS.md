# STATUS.md — resume point

Read this file first, then `docs/DECISIONS.md` (OPEN rows = owner items, listed in `docs/KNOWN_ISSUES.md` §2), then `git status`. The newest dated
paragraph below is the state; earlier paragraphs are history. A **PAUSE POINT** paragraph lists exactly what the owner must do and what an agent
resumes with.

## STATE NOW
- Phase: {{PHASE}} (gate {{NEXT_GATE}} pending — owner line in docs/GATES.md)
- Board of record: `{{BOARD_PATH}}` md5 `{{MD5_OR_NONE}}`; package `{{PACKAGE_OR_NONE}}`; case `{{CASE_VERSION_OR_NONE}}`
- Gates green at HEAD: {{GATES_SUMMARY}}

## Log (newest last)
**{{DATE}} {{TIME}} — project created from the hw-from-spec skill.** project.yaml, templates, scripts installed; selftests + smoke green. Next: SPEC review round 1 (blind ×2) → G0.
