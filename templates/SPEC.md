# SPEC.md — {{PROJECT}} rev {{SPEC_REV}} ({{DATE}}) — the artefact at G0

Every requirement has an ID (`R-<family><nn>`: E electrical, M mechanical, P parts, S silk/UX, T test, W software; run `grep -o 'R-[A-Z]*' -r docs`
before choosing a new family — a prefix collision happened once), a measurable statement, and a `VERIFY` tag where the value rests on a
datasheet, drawing or standard nobody has read yet (skill `SKILL.md` §4; each is closed in `docs/datasheet_notes/<part>.md` or BLOCKED).
Numbers that must agree between sections are cross-referenced by ID, never repeated. Owner choices from the kickoff questionnaire are cited
by their D row, not re-stated.

## 1. Purpose and product class
{{one paragraph: what it is, who uses it, engineering sample / product; D row for the product class}}

## 2. Interfaces (connectors, buses, power in / out)
| ID | Interface | Connector / part | Signals / rails | Numbers that must agree with |
|---|---|---|---|---|
| R-E01 | {{USB-C 5 V 3 A}} | {{MPN or [S] parameters}} `VERIFY` | | R-M02 (case window), R-T01 |

## 3. Electrical requirements
| ID | Requirement | Value / limit | Source | VERIFY |
|---|---|---|---|---|
| R-E02 | {{rail}} | {{V, A, ripple}} | {{datasheet §}} | `VERIFY` |

## 4. Mechanical requirements (board outline, mounting, enclosure inputs)
| ID | Requirement | Value | Agrees with |
|---|---|---|---|
| R-M01 | board: layers {{n}}, thickness {{mm}}, copper {{oz}} outer / {{oz}} inner, finish {{ENIG}}, mask {{colour}} — stack-up template `{{FAB_TEMPLATE}}` | | D-{{nn}} (kickoff), `references/pcb-layout-dfm.md` §2 |
| R-M02 | outline {{W × L}}, corner R, mounting holes {{n × M3}}, keep-outs | | case.yaml |
| R-M03 | assembly sides {{top-only / both}}; press-fit fixture bands | | D-{{nn}} |

## 5. Parts policy
| ID | Rule | Reason |
|---|---|---|
| R-P01 | every fitted part [V] on the fab's library before it is drawn; no invented numbers | skill rule 1 |
| R-P02 | min package {{0402}}, no {{0201}}; signal links {{0603}}, power links {{1206}} | D-{{nn}} (kickoff) |
| R-P03 | design rules per `references/pcb-layout-dfm.md` §4 at the fab's {{date}} table + margin | |

## 6. Silk / UX
R-S01 self-documenting labels at every switch, jumper, test point, header; R-S02 polarity mark on every polarised part; …

## 7. Software / test
R-W01 bring-up tool with `--selftest` / `--dry-run`; R-T01 every requirement above has a T-nn row in `docs/design/TEST_PLAN.md`.

## 8. Enclosure concept (inputs the case generator reads)
Pieces, retention, coupling, feet, labelling, fan / vents / light pipe — as decided at kickoff (D rows); print targets = `project.yaml print_targets`.

## 9. VERIFY list (generated view: `grep -n VERIFY SPEC.md` → `docs/design/VERIFY.md`)
## 10. Open questions (each becomes a CC row OPEN, never a silent assumption)
