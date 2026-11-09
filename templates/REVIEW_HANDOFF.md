# REVIEW_HANDOFF — {{PROJECT}} {{ROUND}} (hand-off v{{N}}, {{DATE}})

This document has two parts. The reviewer part (§0 to §7) is the reviewers' ONLY briefing. The annex is for the verifier only.
Send a reviewer the reviewer part alone: cut the file at the "Verifier annex" heading. A reviewer never gets the decision log,
the known-issue dispositions or the errata (skill `SKILL.md` §5 step 3).
Every number below is generated or cites the file it was read from.
Reviewers read the frozen worktree `{{FROZEN_WORKTREE}}` only. They never read `80-reviews/{{REVIEW_TAG}}_*`, earlier merged reviews,
`90-log/DECISIONS.md`, `90-log/KNOWN_ISSUES.md` or `10-spec/SPEC_ERRATA.md`. Name these patterns in the reviewer prompt.

## 0. Identity (generated — paste `scripts/handoff_header.py` output verbatim)
{{HANDOFF_HEADER_TABLE}}
_(G0 round: board, package and case rows read MISSING by design — the artefact is 10-spec/SPEC.md, listed with its md5 in §2.)_

## 1. What the design is
{{THREE_PARAGRAPHS: purpose, architecture, what changed since the previous hand-off}}

## 2. Files of record (path → what it is → md5)
| Path | What | md5 |
|---|---|---|
| `10-spec/SPEC.md` | the specification (revision {{SPEC_REV}}) — the artefact at G0 | `{{md5}}` |
| `20-design/<board>.yaml` | schematic source (G1+) | `{{md5}}` | {{ee,both}}
| `30-board/kicad/<board>/<board>.kicad_pcb` | board of record | `{{md5}}` | {{ee,both}}
| `30-board/fab/<rev>/` | fab package of record (board_id.txt md5 = the HEAD board) | `{{md5 of MANIFEST}}` | {{ee,both}}
| `20-design/case.yaml` / `40-case/<set>/parts/*.stl` | case of record (record md5 = `scripts/project.py record` in mech) | `{{version}}` | {{mech,both}}
| the fit input (`paths.mesh_provenance`: STEP / envelope) | what the case must fit, [V] / [K] | `{{source_md5}}` | {{mech}}

## 3. The role's checklist
{{ROLE_CHECKLIST: the persona block and its checklist rows; no author reasoning}}

## 4. Claims of the round (delta audits) — each with commit + evidence path
| # | Claim | Commit | Evidence |
|---|---|---|---|
| 1 | {{claim}} | `{{sha}}` | `{{path}}` |

## 5. Waivers (one paragraph, no reasoning — so reviewers and verifiers spend their budget on new defects)
{{WAIVER_LIST}}

## 6. How to check things
CAD Python `{{CAD_PYTHON}}` for parsing board/schematic files (ee / both), `trimesh` for the STLs (mech / both); `grep` for YAML/docs; the Read tool for images (renders under `{{RENDERS_DIR}}`,
tiles under `{{TILES_DIR}}`). Coordinates: {{FRAME_NOTE: board frame vs CAD frame}}.

## 7. Severity
BLOCKER = would make the artefact (board / part) not work, not fit or not build · MAJOR = real functional/robustness/DFM risk before ordering · MINOR = worth fixing · NOTE = observation.

## Verifier annex (verifier only — never sent to a reviewer)
### V.1 Decision trail
`90-log/DECISIONS.md` rows D-… / CC-… for the round.
### V.2 Known / open items with dispositions (from KNOWN_ISSUES.md — generated; do not add prose here)
Applied ahead of the owner's nod: {{KNOWN_ISSUES §2.1 rows}}

OPEN owner rows: {{KNOWN_ISSUES §2 rows}}
### V.3 Spec errata (decided deviations of the frozen SPEC — `10-spec/SPEC_ERRATA.md`; a deviation listed here is ALREADY DECIDED, not a finding)
{{SPEC_ERRATA rows or "none"}}
