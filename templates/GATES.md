# GATES.md — owner approvals

The owner writes the approval line; agents do not edit the approval cells. The release reports read this file and stay DRAFT until the owner writes
the release line here (the words named by `markers.release_regex` in project.yaml — do not quote them in prose anywhere in this file).

| Gate | Meaning | Prerequisites | Owner approval (name, date, revision approved) |
|---|---|---|---|
| **G0** | SPEC approved for schematic capture | SPEC complete, two blind reviews merged in `docs/reviews/G0_merged.md`, SPEC revised, `docs/PARTS_VERIFICATION.md` with no [K] left, all VERIFY items closed or BLOCKED | _not yet approved_ |
| **G1** | Schematic approved for layout | ERC zero errors, map checks pass, `out/G1/` review pack, two blind reviews merged, critical footprints verified against vendor drawings | _not yet approved_ |
| **G2** | Layout approved for fabrication outputs | DRC zero errors with classes enforced (canary fires once), fab DFM mirror 0 open, route quality 0 HIGH, `out/G2/` review pack, two blind reviews merged, adopt gates + clone gate green | _not yet approved_ |
| **Order** | The fab order | package of record built and checked, quote captured under `docs/quotes/<date>/`, KNOWN_ISSUES §2.1 empty | owner's click — never an agent's |
| **Release** | Reports RELEASED | the owner's release line below | _not yet written_ |

Owner instructions quoted verbatim (with date/time) go here when the owner delegates a step; the cells above stay empty until the owner fills them.
