# docs/reviews — blind reviews and audits of the skill itself (newest first)

| File | Date | Lens | Outcome |
|---|---|---|---|
| `blind_review_0.11.0_A.md`, `_B.md` (Agent tool, Claude Opus; A without the mesh libraries, B with), `_C.md` (GitHub Copilot CLI, gpt-5.4), `_verified.md` | 2026-10-02 | the navigable layout release 0.11.0 (branch layout-0.11.0 at 32a0408), checklist-only, three setups | 61 finding ids → 39 merged rows: 20 CONFIRMED (3 BLOCKER, 10 MAJOR, 7 MINOR), 10 PARTLY, 4 ALREADY DECIDED, 5 REFUTED; all CONFIRMED and the MAJOR PARTLY parts fixed before the merge (CHANGELOG 0.11.0 "Review round") |
| `blind_review_0.10.0.md` | 2026-09-30 | one cold user, both scopes, repro commands only | see the file (findings numbered, dispositions per finding) |
| `AUDIT_0.10.0.md` | 2026-09-30 | whole-skill audit: duplication, stale mentions, residue, scripts, evals, smoke, workflows, voice | findings with file:line; §9 dispositions; two lints added (`doc_voice_lint.py`, `generic_lint.py`) |
| `OPUS_blind_review_S_skill_0.8.0_2026-09-30.md` | 2026-09-30 | Opus, four cold personas (EE user, mech user with a STEP, sceptical manager, maintainer) | 28 findings, every one reproduced; closed by 0.9.0 (gates enforced by scripts) |
| `blind_review_0.9.0.md` | 2026-09-30 | cold EE user + enforcement sceptic | 10 findings + 6 notes; both MAJORs fixed before the tag |
| `blind_review_0.8.0_print_dfm.md` | 2026-09-30 | cold user with a bracket STL | 15 findings, 13 fixed, 1 partly, 1 by rule; the BLOCKER was a dead measurement (ray origin) |
| `blind_review_0.7.0_scope.md` | 2026-09-30 | mech-only and ee-only users | scope templates and gates per scope confirmed; fixes in 0.7.0 |
| `blind_review_A_0.4.1_cold_user.md` | 2026-09-28 | cold user | 30 findings; fixed in 0.5.0 (one install block, the bar, the questionnaire) |
| `blind_review_B_0.4.1_dfm_expert.md` | 2026-09-28 | DFM expert | 42 findings; fixed in 0.5.0 (tags on every number, waiver rows removed, census selftests) |
| `SKILL_REVIEW_0.3.0_merged.md` | 2026-09-26 | readers A / B + executor + verifier | 5 MUST / 17 SHOULD / 15 COULD; applied in 0.2.0 … 0.3.0 |
