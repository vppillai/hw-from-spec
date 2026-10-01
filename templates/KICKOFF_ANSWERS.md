# KICKOFF_ANSWERS.md — {{PROJECT}} — the owner's answers to `references/kickoff-questionnaire.md` ({{DATE}})

Asked in up to twelve batches (A0 first; batches outside the scope are skipped) with the recommended answer listed first; every row below is an owner decision (D row quoted verbatim) written BEFORE any
CAD. `Answer` is the option chosen; `Rec.` = the recommended default was accepted (`yes`) or overridden (`no` — the owner's reason is in the D
row). A deferred question is `OPEN` here and in the decision log and blocks the phase named in the questionnaire's batch table. Re-asking an
answered question is a defect; changing an answer is a new D row that supersedes the old one and a new line here. A question outside the scope
(questionnaire tags `[ee, both]` / `[mech, both]`) is not asked: `scripts/project.py scaffold --scope` drops its row (a row kept by hand reads
`n/a (scope)`). `scripts/project.py kickoff --check` proves every answered row's `Written to` key exists in project.yaml.

| Q | Question | Answer | Rec. | D row | Written to |
|---|---|---|---|---|---|
| A0 | scope | {{SCOPE}} | yes | D-{{nn}} | `project.scope`; CLAUDE.md; GATES.md rows |
| A1 | product class | {{engineering sample}} | yes | D-{{nn}} | `kickoff.product_class`; SPEC §1 |
| A2 | quantity / horizon | {{5 first article, design for 50}} | yes | D-{{nn}} | `kickoff.quantity` |
| A3 | board fab / assembler | {{fab}} | yes | D-{{nn}} | `kickoff.fab` | {{ee,both}}
| A4 | enclosure targets | {{MJF PA12 at <vendor> + home FDM PLA 0.4}} | yes | D-{{nn}} | `print_targets.<t>` (vendor, process, material, rating), `print_targets.home_fdm` | {{mech,both}}
| B1 | layers / thickness / stack-up | {{4 L, 1.6, template}} | yes | D-{{nn}} | `board.layers`, `board.thickness_mm`, `board.stackup_template`; R-M01 | {{ee,both}}
| B2 | copper weights | {{1 oz / 0.5 oz}} | yes | D-{{nn}} | `board.copper` | {{ee,both}}
| B3 | controlled impedance | {{none, pairs < N cm}} | yes | D-{{nn}} | `board.impedance` | {{ee,both}}
| B4 | finish / mask / silk | {{ENIG green white}} | yes | D-{{nn}} | `board.finish`, `board.mask`, `board.silk` | {{ee,both}}
| B5 | component size + link policy | {{no 0201, 0402 min, 0603 / 1206 links}} | yes | D-{{nn}} | `board.min_package`, `board.link_parts`; R-P02 | {{ee,both}}
| B6 | assembly sides | {{both}} | yes | D-{{nn}} | `board.sides`; R-M03 | {{ee,both}}
| B7 | test points + silk labels | {{per rail / bus, labelled}} | yes | D-{{nn}} | `board.test_points`; R-S01 | {{ee,both}}
| B8 | panel + fiducials | {{customer panel long rails}} | yes | D-{{nn}} | `board.panel` | {{ee,both}}
| C1 | pieces | {{tray + shell}} | yes | D-{{nn}} | `kickoff.enclosure.pieces`; SPEC §8 | {{mech,both}}
| C2 | retention | {{screws + inserts}} | yes | D-{{nn}} | `kickoff.enclosure.retention`; case.yaml | {{mech,both}}
| C3 | coupling | {{none}} | yes | D-{{nn}} | `kickoff.enclosure.coupling` | {{mech,both}}
| C4 | feet / mounting | {{4 adhesive flat-top, primer on PA12}} | yes | D-{{nn}} | `kickoff.enclosure.feet`; PROCUREMENT | {{mech,both}}
| C5 | labelling | {{label carrier + raised FDM legends}} | yes | D-{{nn}} | `kickoff.enclosure.labelling` | {{mech,both}}
| C6 | fan / vents | {{passive vents}} | yes | D-{{nn}} | `kickoff.enclosure.fan` | {{mech,both}}
| C7 | light pipes / windows | {{holes, pipe on the backlog}} | yes | D-{{nn}} | `kickoff.enclosure.light_pipe` | {{mech,both}}
| C8 | two targets, per-preset fits | {{yes}} | yes | D-{{nn}} | `kickoff.enclosure.targets` | {{mech,both}}
| C8a | print-DFM process row per target | {{<vendor row> + home_fdm_04}} | yes | D-{{nn}} | `print_targets.<t>.dfm_process`; `design/dfm_processes.yaml` | {{mech,both}}
| C9 | brand marks on FDM parts | {{ironed top-face feature}} | yes | D-{{nn}} | `kickoff.enclosure.marks`; slicer plate profile (`ironing_type: top`) | {{mech,both}}
| C10 | print kit hand-over: report-back recipient, fit decider | {{owner; owner}} | yes | D-{{nn}} | `kickoff.enclosure.kit_recipient`, `kickoff.enclosure.fit_decider`, `kickoff.enclosure.fit_result` ("pending: bracket print" until the owner picks; ARRIVAL_CHECKLIST E-FIT); START_HERE | {{mech,both}}
| C11 | slicer optimisation target | {{minimal waste}} | yes | D-{{nn}} | `kickoff.enclosure.optimise`; the plate yaml `optimise:` block (`references/fdm-print-optimisation.md` §4) | {{mech,both}}
| D1 | the manufacturability bar | {{zero errors / zero warnings / no waivers}} | yes | D-{{nn}} = `{{D-BAR}}` | `fab_dfm.bar` (ee / both), `print_targets.*.accepted` (mech / both); GATES.md; CLAUDE.md rule 9 |
| D2 | what may be waived | {{nothing}} | yes | D-{{nn}} | `print_targets.*.accepted: []` (mech / both), `dfm_accepted: []` (ee / both) |
| D3 | design margin / tolerance source | {{+0.1 MJF; first article replaces the vendor sheet}} | yes | D-{{nn}} | `print_targets.*.design_margin / tolerance` | {{mech,both}}
| E1 | review rounds per gate | {{one round per gate, two external models}} | yes | D-{{nn}} | `kickoff.verification.rounds`; `{{EXTERNAL_MODELS}}` |
| E2 | visual inspections | {{tiles + renders + six faces}} | yes | D-{{nn}} | `kickoff.verification.visual` |
| E3 | coupons / dummies / first article | {{yes}} | yes | D-{{nn}} | `kickoff.coupons` | {{mech,both}}
| E4 | vendor DFM before order + FEA | {{yes}} | yes | D-{{nn}} | `kickoff.verification.fea`; GATES prerequisites |
| F1 | verification sources | {{fab API + manufacturer TDS; owner opens walled sites}} | yes | D-{{nn}} | `kickoff.sourcing.sources` |
| F2 | stock policy / alternates | {{× 1.2, ≥ 1000 jellybeans, Alt_MPN}} | yes | D-{{nn}} | `kickoff.sourcing.stock_floor` |
| G1 | software modes / posture | {{operator + engineering; warn / throttle}} | yes | D-{{nn}} | `kickoff.software.modes`; SOFTWARE_ARCHITECTURE §1 | {{ee,both}}
| G2 | criteria + codes | {{yaml, owner-approved}} | yes | D-{{nn}} | `kickoff.software.criteria`; test_criteria.yaml header | {{ee,both}}
| H1 | report set | {{generated reports + notes + tag}} | yes | D-{{nn}} | `kickoff.release.reports`; `reports:` |
| H2 | production cut | {{full document set}} | yes | D-{{nn}} | `kickoff.release.cut`; production_cut.yaml |
| H3 | CI / hygiene | {{PR check = adopt gates}} | yes | D-{{nn}} | `kickoff.release.ci`; `templates/ci/` |
| H4 | feedback loop | {{retro at the cut, PR to the skill}} | yes | D-{{nn}} | `kickoff.release.retro`; `skill.version`; SKILL §13 |
| I1 | envelope fixed or grows | {{grows, connectors fixed}} | yes | D-{{nn}} | `kickoff.identity.envelope`; SPEC §4 |
| I2 | branding / look | {{name + logo lock-up, legend grid}} | yes | D-{{nn}} | `kickoff.identity.branding`; SPEC §6 |
| I3 | debug / service access | {{wire header + straps, hood off}} | yes | D-{{nn}} | `kickoff.debug_access` | {{ee,both}}
| I4 | delegation while offline | {{recommended option below a named class}} | yes | D-{{nn}} | `kickoff.identity.delegation`; pause-point owner list |

Batches asked: {{0–11 with date/time}}. Questions deferred: {{none}}. Owner's closing words: "{{QUOTE}}".
