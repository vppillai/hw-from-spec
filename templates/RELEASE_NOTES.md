# RELEASE_NOTES — {{PROJECT}} rev {{REV}} ({{DATE}})

> **State at this release (generated facts):** board `{{BOARD_PATH}}` md5 `{{MD5}}` (content signature `{{SIG}}`), package `{{PACKAGE_DIR}}`,
> case `{{CASE_VERSION}}`, decisions md5 `{{DECISIONS_MD5}}`, tag `{{TAG}}`. Every number below names the file it was read from; a value a
> concurrent agent is still producing is written `[FINAL: …]` rather than copied early.

## What this is
{{two paragraphs: purpose, form factor, what is in the box}}

## What is being ordered / built
- PCB: {{layers, thickness, copper, finish, mask}} — `{{PACKAGE_DIR}}/ORDER_PARAMETERS.md`
- Assembly: {{sides, part count}} BOM `{{n}}` lines / CPL `{{n}}` rows — `{{PACKAGE_DIR}}/bom.csv`, `cpl.csv`
- Case: `{{CASE_VERSION}}` {{pieces, process, material}} — `{{ORDER_SHEET}}`
- Owner-supplied parts: {{list}} — `docs/parts/PROCUREMENT.md`

## Gates at this release
| Gate | State | Evidence |
|---|---|---|
| DRC (classes enforced, canary ×1) | {{0 err / 0 unconnected / parity 0}} | `{{PACKAGE_DIR}}/drc_summary.md` |
| Fab DFM mirror | {{0 open}} | `out/dfm.json` |
| Route quality | {{0 HIGH}} | `{{path}}` |
| Traceability | {{VERIFIED n / FAILED 0 / unmapped none}} | `docs/governance/TRACEABILITY.md` |
| Blind reviews | {{rounds, last merged report}} | `docs/reviews/{{merged}}` |
| Adopt + clone gate | green at `{{sha}}` | `scripts/adopt_gates.sh` transcript in DECISIONS {{row}} |

## Known issues at release
Generated index: `docs/governance/KNOWN_ISSUES.md` §1 (operator-facing), §2 (OPEN owner rows), §2.1 (applied ahead of the nod — must be empty to order).

## Changes since {{PREVIOUS_REV_OR_NONE}}
{{bullet list, each with its decision row}}

## Owner actions
- Write the gate lines in `docs/governance/GATES.md`; place the order; file records under `docs/release/records/{{MD5_8}}/` as they happen.
