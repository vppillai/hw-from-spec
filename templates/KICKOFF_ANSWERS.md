# KICKOFF_ANSWERS.md — {{PROJECT}} — the owner's answers to `references/kickoff-questionnaire.md` ({{DATE}})

Asked in nine batches with the recommended answer listed first; every row below is an owner decision (D row quoted verbatim) written BEFORE any
CAD. `Answer` is the option chosen; `Rec.` = the recommended default was accepted (`yes`) or overridden (`no` — the owner's reason is in the D
row). A deferred question is `OPEN` here and in the decision log and blocks the phase named in the questionnaire's batch table. Re-asking an
answered question is a defect; changing an answer is a new D row that supersedes the old one and a new line here.

| Q | Question | Answer | Rec. | D row | Written to |
|---|---|---|---|---|---|
| A1 | product class | {{engineering sample}} | yes | D-{{nn}} | `kickoff.product_class`; SPEC §1 |
| A2 | quantity / horizon | {{5 first article, design for 50}} | yes | D-{{nn}} | `kickoff.quantity` |
| A3 | board fab / assembler | {{fab}} | yes | D-{{nn}} | `kickoff.fab` |
| A4 | enclosure targets | {{MJF PA12 at <vendor> + home FDM PLA 0.4}} | yes | D-{{nn}} | `print_targets.{{jlc_mjf}}`, `print_targets.home_fdm` |
| B1 | layers / thickness / stack-up | {{4 L, 1.6, template}} | yes | D-{{nn}} | `board.layers`, `board.stackup_template`; R-M01 |
| B2 | copper weights | {{1 oz / 0.5 oz}} | yes | D-{{nn}} | `board.copper` |
| B3 | controlled impedance | {{none, pairs < N cm}} | yes | D-{{nn}} | `board.impedance` |
| B4 | finish / mask / silk | {{ENIG green white}} | yes | D-{{nn}} | `board.finish` |
| B5 | component size + link policy | {{no 0201, 0402 min, 0603 / 1206 links}} | yes | D-{{nn}} | `board.min_package`, `board.link_parts`; R-P02 |
| B6 | assembly sides | {{both}} | yes | D-{{nn}} | `board.sides`; R-M03 |
| B7 | test points + silk labels | {{per rail / bus, labelled}} | yes | D-{{nn}} | `board.test_points`; R-S01 |
| B8 | panel + fiducials | {{customer panel long rails}} | yes | D-{{nn}} | `board.panel` |
| C1 | pieces | {{tray + shell}} | yes | D-{{nn}} | `kickoff.enclosure.pieces`; SPEC §8 |
| C2 | retention | {{screws + inserts}} | yes | D-{{nn}} | `kickoff.enclosure.retention`; case.yaml |
| C3 | coupling | {{none}} | yes | D-{{nn}} | `kickoff.enclosure.coupling` |
| C4 | feet / mounting | {{4 adhesive flat-top, primer on PA12}} | yes | D-{{nn}} | `kickoff.enclosure.feet`; PROCUREMENT |
| C5 | labelling | {{label carrier + raised FDM legends}} | yes | D-{{nn}} | `kickoff.enclosure.labelling` |
| C6 | fan / vents | {{passive vents}} | yes | D-{{nn}} | `kickoff.enclosure.fan` |
| C7 | light pipes / windows | {{holes, pipe on the backlog}} | yes | D-{{nn}} | `kickoff.enclosure.light_pipe` |
| C8 | two targets, per-preset fits | {{yes}} | yes | D-{{nn}} | `kickoff.enclosure.targets` |
| D1 | the manufacturability bar | {{zero errors / zero warnings / no waivers}} | yes | D-{{nn}} = `{{D-BAR}}` | `fab_dfm.bar`; GATES.md; CLAUDE.md rule 9 |
| D2 | what may be waived | {{nothing}} | yes | D-{{nn}} | `print_targets.*.accepted: []`, `dfm_accepted: []` |
| D3 | design margin / tolerance source | {{+0.1 MJF; first article replaces the vendor sheet}} | yes | D-{{nn}} | `print_targets.*.design_margin / tolerance` |
| E1 | review rounds per gate | {{one round per gate, two external models}} | yes | D-{{nn}} | `kickoff.verification.rounds`; `{{EXTERNAL_MODELS}}` |
| E2 | visual inspections | {{tiles + renders + six faces}} | yes | D-{{nn}} | `kickoff.verification.visual` |
| E3 | coupons / dummies / first article | {{yes}} | yes | D-{{nn}} | `kickoff.verification.coupons` |
| E4 | vendor DFM before order + FEA | {{yes}} | yes | D-{{nn}} | GATES prerequisites |
| F1 | verification sources | {{fab API + manufacturer TDS; owner opens walled sites}} | yes | D-{{nn}} | `kickoff.sourcing.sources` |
| F2 | stock policy / alternates | {{× 1.2, ≥ 1000 jellybeans, Alt_MPN}} | yes | D-{{nn}} | `kickoff.sourcing.stock_floor` |
| G1 | software modes / posture | {{operator + engineering; warn / throttle}} | yes | D-{{nn}} | `kickoff.software`; SOFTWARE_ARCHITECTURE §1 |
| G2 | criteria + codes | {{yaml, owner-approved}} | yes | D-{{nn}} | test_criteria.yaml header |
| H1 | report set | {{generated reports + notes + tag}} | yes | D-{{nn}} | `reports:` |
| H2 | production cut | {{full document set}} | yes | D-{{nn}} | production_cut.yaml |
| H3 | CI / hygiene | {{PR check = adopt gates}} | yes | D-{{nn}} | `templates/ci/` |
| H4 | feedback loop | {{retro at the cut, PR to the skill}} | yes | D-{{nn}} | `skill.version`; SKILL §13 |

Batches asked: {{1–9 with date/time}}. Questions deferred: {{none}}. Owner's closing words: "{{QUOTE}}".
