# GATES.md — owner approvals

The owner writes the approval cells and the release line; **agents never write either** — they ask (skill `SKILL.md` §1.1) and wait. A valid
approval cell reads `<owner name>, <YYYY-MM-DD>, <what was approved: SPEC rev / schematic commit / board md5-8 / case version>`; an empty cell is
`_not yet approved_`. The release reports read this file and stay DRAFT until the owner writes the release line here (the words named by
`markers.release_regex` in project.yaml — do not quote them in prose anywhere in this file). A chat approval is quoted verbatim (date/time) under
the table; the cell stays the owner's.

**One review round** (skill `SKILL.md` §5) = for every role of the round's role set, one in-session reviewer + two external models (or the
in-session fallback), an adversarial verifier per role, one merged report in `docs/reviews/<round>_merged.md`. Every gate below needs one.

**The manufacturability bar** (owner decision {{D-BAR}} from the kickoff questionnaire; default = zero / zero / no waivers): board — CAD DRC
0 errors / 0 unconnected / **0 warnings**, fab DFM mirror **0 open (0 Danger, 0 Warning)** unless a dated `dfm_accepted` entry with reason and
vendor evidence names the refdes; printed enclosure — census **0 unaccepted FAIL** per body per preset, zero slicer warnings, vendor checker
**no flag by API read**, no yellow / red on the heat map; CNC — vendor DFM clean. A waiver is a dated decision row plus a machine-readable
accept entry, never prose.

| Gate | Meaning | Prerequisites | Owner approval (name, date, revision approved) |
|---|---|---|---|
| **G0** | SPEC approved for schematic capture | SPEC complete (`SPEC.md` from the skeleton, every `VERIFY` tag listed in `docs/design/VERIFY.md`), kickoff answers recorded (`docs/governance/KICKOFF_ANSWERS.md` → D rows, `project.yaml print_targets` / `fab_dfm`), one review round (role set `spec`) merged in `docs/reviews/G0_merged.md`, SPEC revised, `docs/parts/PARTS_VERIFICATION.md` with no [K] left, every VERIFY item (skill `SKILL.md` §4) closed in `docs/datasheet_notes/` or BLOCKED | _not yet approved_ |
| **G1** | Schematic approved for layout | ERC zero errors (`docs/governance/ERC_WAIVERS.md` for the warnings), map checks pass (`references/schematic-phase.md` §3), `out/G1/` review pack (§4 there, incl. `EVIDENCE.md` + `REVIEW_NOTES.md`), one review round merged in `docs/reviews/G1_merged.md`, critical footprints verified against vendor drawings — one row per part in `docs/datasheet_notes/<part>.md` (pinout / package check) | _not yet approved_ |
| **G2** | Layout approved for fabrication outputs | DRC 0 errors / 0 unconnected / 0 warnings unless a dated waiver row (canary fires exactly once, classes enforced), schematic parity 0, route quality 0 unjustified HIGH, **fab DFM mirror 0 open (0 Danger / 0 Warning; accepted items dated with vendor evidence)**, silk check 0 + legibility read, `out/G2/` review pack (`references/pcb-layout-dfm.md` §1.3), one review round merged + the routing inspection, adopt gates + clone gate green | _not yet approved_ |
| **Order (board)** | The fab order | package of record built and checked, **the fab's own DFM viewer run on the board AND the panel upload with 0 Danger / 0 Warning or a dated accepted row per item** (PDF under `docs/quotes/<date>/`), quote captured, stock verified live with the run-relative minimum, KNOWN_ISSUES §2.1 empty, rotation preview checked for every polarised part | owner's click — never an agent's |
| **Case order** | The enclosure order (print service / CNC) | census `--gate-dir` green on every preset (0 unaccepted FAIL), `DFM_ROUND.md` verdict PASS with the raw API JSON filed per body (no flag, no yellow / red), coupons printed and recorded (fit, text, insert + torque), worst-case clearance rows ≥ 0, material rating per target on the order sheet, KNOWN_ISSUES §1 lists every designed asymmetry, owner consent to upload quoted, `case_dfm` review role merged | owner's click — never an agent's |
| **Release** | Reports RELEASED | the owner's release line below | _not yet written_ |

Owner instructions quoted verbatim (with date/time) go here when the owner delegates a step; the cells above stay empty until the owner fills them.
