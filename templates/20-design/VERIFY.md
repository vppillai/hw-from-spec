# VERIFY.md — every spec value or claim that rests on a source nobody has read yet (skill `SKILL.md` §4, rule 3)

Seeded from `grep -n VERIFY 10-spec/SPEC.md` and the G0 review's list; one row per item; closed by a row in `10-spec/datasheet_notes/<part>.md` (page /
section, value read, matches yes / no) or moved to `90-log/BLOCKERS.md`. G0 requires every row CLOSED or BLOCKED. Rule 3: an item that
touches a part is closed BEFORE the part is drawn.

| ID | Spec item (R-xx) | Part / standard | What to read (document, section) | Value expected | Status (OPEN / CLOSED → note row / BLOCKED → B-nn) | Date |
|---|---|---|---|---|---|---|
| V-01 | {{R-E02 Iq}} | {{MPN}} | datasheet §{{n}} table {{n}} | {{55 µA}} | OPEN | {{DATE}} |
