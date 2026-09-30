# REVIEW_HANDOFF — {{PROJECT}} {{ROUND}} (hand-off v{{N}}, {{DATE}})

This document is the reviewers' ONLY briefing. It is self-contained; every number below is generated or cites the file it was read from.
Reviewers read the frozen worktree `{{FROZEN_WORKTREE}}` only; they never read `docs/reviews/{{REVIEW_TAG}}_*` or earlier merged reviews.

## 0. Identity (generated — paste `scripts/handoff_header.py` output verbatim)
{{HANDOFF_HEADER_TABLE}}
_(G0 round: board, package and case rows read MISSING by design — the artefact is SPEC.md, listed with its md5 in §2.)_

## 1. What the design is
{{THREE_PARAGRAPHS: purpose, architecture, what changed since the previous hand-off}}

## 2. Files of record (path → what it is → md5)
| Path | What | md5 |
|---|---|---|
| `SPEC.md` | the specification (revision {{SPEC_REV}}) — the artefact at G0 | `{{md5}}` |
| `design/<board>.yaml` | schematic source (G1+) | `{{md5}}` | {{ee,both}}
| `kicad/<board>/<board>.kicad_pcb` | board of record | `{{md5}}` | {{ee,both}}
| `out/fab/<date>_<md5-8>/` | fab package of record | `{{md5 of MANIFEST}}` | {{ee,both}}
| `design/case.yaml` / `out/.../case/<preset>/stl/*.stl` | case of record (record md5 = `scripts/project.py record` in mech) | `{{version}}` | {{mech,both}}
| the fit input (`paths.mesh_provenance`: STEP / envelope) | what the case must fit, [V] / [K] | `{{source_md5}}` | {{mech}}
| `docs/governance/DECISIONS.md` rows D-… / CC-… | decision trail for this round | |

## 3. Known / open items with dispositions (from KNOWN_ISSUES.md — generated; do not add prose here)
### 3.1 Applied ahead of the owner's nod
{{KNOWN_ISSUES §2.1 rows}}
### 3.2 OPEN owner rows
{{KNOWN_ISSUES §2 rows}}

## 4. Claims of this round (delta audits) — each with commit + evidence path
| # | Claim | Commit | Evidence |
|---|---|---|---|
| 1 | {{claim}} | `{{sha}}` | `{{path}}` |

## 5. Waivers (one paragraph, no reasoning — so verifiers spend their budget on new defects)
{{WAIVER_LIST}}

## 6. How to check things
CAD Python `{{CAD_PYTHON}}` for parsing board/schematic files (ee / both), `trimesh` for the STLs (mech / both); `grep` for YAML/docs; the Read tool for images (renders under `{{RENDERS_DIR}}`,
tiles under `{{TILES_DIR}}`). Coordinates: {{FRAME_NOTE: board frame vs CAD frame}}.

## 7. Severity
BLOCKER = would make the artefact (board / part) not work, not fit or not build · MAJOR = real functional/robustness/DFM risk before ordering · MINOR = worth fixing · NOTE = observation.
