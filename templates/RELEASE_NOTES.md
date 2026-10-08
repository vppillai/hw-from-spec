# RELEASE_NOTES — {{PROJECT}} rev {{REV}} ({{DATE}})

> **State at this release (generated facts):** record `{{BOARD_PATH_OR_STL_SET}}` md5 `{{MD5}}`,
> package `{{PACKAGE_DIR}}`, {{ee,both}}
> case `{{CASE_VERSION}}`, {{mech,both}}
> decisions md5 `{{DECISIONS_MD5}}`, tag `{{TAG}}`. `scripts/project.py record` gives the record md5. The content signature is `{{SIG}}`.
> Every number below names the file it was read from; a value a concurrent agent is still producing is written `[FINAL: …]` rather than copied early.

## What this is
{{two paragraphs: purpose, form factor, what is in the box}}

## What is being ordered / built
- PCB: {{layers, thickness, copper, finish, mask}} — `{{PACKAGE_DIR}}/ORDER_PARAMETERS.md` {{ee,both}}
- Assembly: {{sides, part count}} BOM `{{n}}` lines / CPL `{{n}}` rows — `{{PACKAGE_DIR}}/bom.csv`, `cpl.csv` {{ee,both}}
- Case: `{{CASE_VERSION}}` {{pieces, process, material}} — `{{ORDER_SHEET}}` {{mech,both}}
- Owner-supplied parts: {{list}} — `60-orders/PROCUREMENT.md`

## Gates at this release
| Gate | State | Evidence |
|---|---|---|
| DRC (classes enforced, canary ×1) | {{0 err / 0 unconnected / parity 0}} | `{{PACKAGE_DIR}}/drc_summary.md` | {{ee,both}}
| Fab DFM mirror | {{0 open}} | `30-board/layout/dfm.json` | {{ee,both}}
| Route quality | {{0 HIGH}} | `{{path}}` | {{ee,both}}
| Census `--gate-dir` per preset + vendor DFM | {{0 unaccepted FAIL; DFM_ROUND verdict}} | `40-case/<set>/checks/census/`, `60-orders/quotes/<date>/DFM_ROUND.md` | {{mech,both}}
| `print_dfm.py --gate` per preset | {{PASS on n bodies, rule set VERSION}} | `40-case/<set>/checks/dfm/` | {{mech,both}}
| Traceability | {{VERIFIED n / FAILED 0 / unmapped none}} | `90-log/TRACEABILITY.md` |
| Blind reviews | {{rounds, last merged report}} | `80-reviews/{{merged}}` |
| Adopt + clone gate | green at `{{sha}}` | `scripts/adopt_gates.sh` transcript in DECISIONS {{row}} |

## Known issues at release
Generated index: `90-log/KNOWN_ISSUES.md` §1 (operator-facing), §2 (OPEN owner rows), §2.1 (applied ahead of the nod — must be empty to order).

## Changes since {{PREVIOUS_REV_OR_NONE}}
{{bullet list, each with its decision row}}

## Owner actions
- Write the gate lines in `90-log/GATES.md`; place the order; file records under `70-release/{{REV}}/records/` (the cut's `records_dir`) as they happen — the only records folder.
