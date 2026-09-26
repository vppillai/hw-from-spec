# SKILL_REVIEW_0.3.0_merged — blind double review of hw-from-spec 0.3.0 (HEAD 790326b + uncommitted pitfalls header), 2026-09-26

Two independent general-purpose reviewer agents; each received ONLY the repo path and a checklist (completeness vs CHANGELOG, project-agnosticism,
selftests, SKILL consistency, no source-project leakage; B additionally read the three new scripts line by line and probed the gate guard).
Neither saw the other's output nor the author's reasoning. Reports: A = 16 findings (2 MUST / 7 SHOULD / 7 COULD), B = 30 findings
(4 MUST / 17 SHOULD / 9 COULD). Both verdicts: **RELEASE AFTER THE MUST LIST**. Both ran every selftest, both shell selftests and the smoke: green
(A saw one unreproduced clone-gate abort in five smoke runs → ERR trap added).

## Corroboration (finding × reviewer) and disposition

| Defect | A | B | Class | Disposition |
|---|---|---|---|---|
| `known_issues.py` / `release_report.py` `--help` runs the default WRITE action (no argparse); `handoff_header.py` no usage | A-01 MUST | — | REQUIRED | argparse on all three; agent-ops §3 sentence rewritten |
| pitfalls.md header stale at HEAD (fix only in the working tree) | A-02 MUST | B-14 SHOULD | REQUIRED | committed with the fix round |
| `reorg_paths --check` false positive on `docs/v1.2/x` (directory segment) | — | B-01 MUST | REQUIRED | `(?![\w…/])`; selftest row |
| `allow_missing` path never reached by the selftest | — | B-02 MUST | REQUIRED | literal moved into a structural fixture file; asserted |
| empty / mistyped `gates.adopt` prints "adopt gates OK" | — | B-03 MUST | REQUIRED | fail with a message; selftest case |
| `thin_wall_check` mesh modes die with a raw ModuleNotFoundError | — | B-04 MUST | REQUIRED | `need()` → exit 2 with the install hint |
| SKILL cites agent-ops §4/§3/§5 for §1/§2/§4 | A-03 | B-11 | REQUIRED | numbers fixed |
| assembly guide "registered in production_cut.yaml" but no row in the template | A-04 | B-15 | REQUIRED | VG-001 row added |
| day-1 recipe: project venv never gets pyyaml → step 5 ImportError | A-05 | B-16 | REQUIRED | step 1 installs pyyaml in the project venv too |
| clone_gate / adopt_gates abort without naming the line | A-06 | — | REQUIRED | ERR traps |
| vendor-review names two homes for the mapping / replacement tables | A-07 | — | REQUIRED | tables live in the record (§2 / §4) |
| script docstrings cite source-project decision ids | A-08 | B-20 | REQUIRED | cite pitfalls / case-pipeline instead |
| `reorg.gitignore` key undocumented | A-09 | B-12 | REQUIRED | schema row |
| read-only guard blind to a re-modified already-dirty file; gitignored writes unseen | — | B-05 | REQUIRED (partly) | `git diff HEAD` hash added to the snapshot + selftest; gitignored paths stay unwatched and the failure message says so (ACCEPT: watching ignored paths would flag every scratch write) |
| pr-check guard assumes a clean tree after Bootstrap; silent pass on a failing `git status` | — | B-06 | REQUIRED | snapshot after Bootstrap, diff, `|| exit 1` |
| `--pinch` searches exteriors only: two separate lobes / a touching hole → exit 0 | — | B-07 | REQUIRED | cross-ring pass + exit 1 on > 1 polygon; selftest |
| `to_2D()` map-back translation-only; `section()` None → AttributeError | A-16 | B-08 | REQUIRED | full 2-D affine part; None → message |
| `guide.json` never pruned: orphan renders ship | — | B-09 | REQUIRED | pruned on build, flagged on `--check`; selftest |
| render key = one scad file; `include <…>` edits do not move it | — | B-10 | DOCUMENT | stated in docstring, project-yaml.md, release-and-cut §8 |
| un-migrated `docs/SOFTWARE_ARCHITECTURE.md` literal | — | B-13 | REQUIRED | → docs/design/ |
| "≈ 45 min" stated as a rule in SKILL; source-project piece names / one vendor's wording in vendor-review; project-side generators named as if skill scripts in §3.1 | — | B-17/18/19 | REQUIRED | generic wording; italics for project-side generators |
| same-repo URLs to moved files neither rewritten nor flagged | — | B-21 | DOCUMENT | docstring + release-and-cut §9 |
| "62 literals" rotting count; `datasheet_notes` missing from a comment; eval fixture name `ct1`; smoke README / README / CHANGELOG counts | A-10/13/14/15 | B-28/29 | REQUIRED (trivial) | applied |
| selftest messages stronger than their assertions (assembly "stales all", thin_wall "self-hit") | A-11 | B-26 | REQUIRED | every stem asserted; `{SIZE}` in the fixture; messages name the uncovered mesh wrappers |
| `--proof` failure branches untested | — | B-23 | REQUIRED | one corrupted-sha case |
| dead `"*{<>$"` clause in `--check` | — | B-22 | REQUIRED | removed |
| `{SIZE}` unquoted; other braces in `render_cmd`; yaml booleans → `True` | — | B-25 | REQUIRED | quoted; documented; lowered |
| `pinch_points` O(n²) | — | B-27 | DOCUMENT | ponytail ceiling comment |
| selftests leave mkdtemp dirs | — | B-30 | ACCEPT | deferred since 0.2.0 (temp dirs, harmless) |
| CRLF normalisation / `core.quotepath` in `--proof` | — | B-24 | DOCUMENT (partly) | quotepath documented; CRLF: ACCEPT (a rewritten file is in the rewrite list either way) |

Clean per both: leak grep (order ids, names, e-mails, account numbers, board hashes) — zero hits outside CHANGELOG (record) and the labelled
worked-example line in pitfalls.md; frontmatter = README = CHANGELOG version; every referenced file exists; placed_regex identical everywhere;
vendor boundaries identical in reference / template / SKILL; every 0.3.0 CHANGELOG artefact present (except the VG-001 row, fixed).

## Verdict
All six MUST items and every REQUIRED row above applied in the fix round; selftests (10 py + 2 sh) and the smoke re-run green; `--help` on every
script in a copy of the smoke project leaves `git status --porcelain` empty. **Release 0.3.0.** Reviewer quality: A 16 findings / 0 refuted,
B 30 / 0 refuted (two of B's proposed fixture assertions were adjusted for correct behaviour, not refuted); no empty runs.
