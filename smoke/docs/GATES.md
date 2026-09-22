# GATES.md — owner approvals

The owner writes the approval line; agents never edit the approval cells. The release reports read this file: they say DRAFT until the owner writes the release line here (the three words the regex in project.yaml `markers.release_regex` names — never quote them in prose, or the report turns RELEASED by accident).

| Gate | Meaning | Prerequisites | Owner approval (name, date, revision) |
|---|---|---|---|
| **G0** | SPEC approved for schematic capture | two blind reviews merged, PARTS_VERIFICATION with no [K] left | _not yet approved_ |
| **G1** | Schematic approved for layout | ERC 0 errors, review pack, two blind reviews merged | _not yet approved_ |
| **G2** | Layout approved for fabrication outputs | DRC 0 errors, fab DFM mirror 0 open, two blind reviews merged | _not yet approved_ |
