# GATES.md — owner approvals

The owner writes the approval cells; agents never edit them. The release reports read the Release row's approval cell: they say DRAFT until the owner writes the release phrase there (the three words the regex in project.yaml `markers.release_regex` names — never quote them in prose) and commits it as `project.owner` (`scripts/gate_check.py --release`).

| Gate | Meaning | Prerequisites | Owner approval (name, date, revision) |
|---|---|---|---|
| **G0** | SPEC approved for schematic capture | one review round merged, PARTS_VERIFICATION with no [K] left | _not yet approved_ |
| **G1** | Schematic approved for layout | ERC 0 errors, review pack, one review round merged | _not yet approved_ |
| **G2** | Layout approved for fabrication outputs | DRC 0 errors, fab DFM mirror 0 open, one review round merged | _not yet approved_ |
