# GATES.md — owner approvals

The owner writes the approval cells and the release line; **agents never write either** — they ask (skill `SKILL.md` §1.1) and wait. A valid
approval cell reads `<owner name>, <YYYY-MM-DD>, <what was approved: SPEC rev / schematic commit / board md5-8>`; an empty cell is `_not yet approved_`.
The release reports read this file and stay DRAFT until the owner writes the release line here (the words named by `markers.release_regex` in
project.yaml — do not quote them in prose anywhere in this file). A chat approval is quoted verbatim (date/time) under the table; the cell stays the owner's.

| Gate | Meaning | Prerequisites | Owner approval (name, date, revision approved) |
|---|---|---|---|
| **G0** | SPEC approved for schematic capture | SPEC complete, one blind review round (`{{ROLE_SET}}` = spec: skill `SKILL.md` §5) merged in `docs/reviews/G0_merged.md`, SPEC revised, `docs/parts/PARTS_VERIFICATION.md` with no [K] left, every VERIFY item (skill `SKILL.md` §4) closed in `docs/datasheet_notes/` or BLOCKED | _not yet approved_ |
| **G1** | Schematic approved for layout | ERC zero errors (`docs/governance/ERC_WAIVERS.md` for the warnings), map checks pass (`references/schematic-phase.md` §3), `out/G1/` review pack (§4 there), blind review round merged in `docs/reviews/G1_merged.md`, critical footprints verified against vendor drawings | _not yet approved_ |
| **G2** | Layout approved for fabrication outputs | DRC zero errors with classes enforced (canary fires once), fab DFM mirror 0 open, route quality 0 HIGH, `out/G2/` review pack, two blind reviews merged, adopt gates + clone gate green | _not yet approved_ |
| **Order** | The fab order | package of record built and checked, quote captured under `docs/quotes/<date>/`, KNOWN_ISSUES §2.1 empty | owner's click — never an agent's |
| **Release** | Reports RELEASED | the owner's release line below | _not yet written_ |

Owner instructions quoted verbatim (with date/time) go here when the owner delegates a step; the cells above stay empty until the owner fills them.
