# SPEC_ERRATA.md — known deviations of the frozen 10-spec/SPEC.md ({{SPEC_REV}}, frozen under {{FREEZE_ROW}}) from the design of record

> **Status: OPEN — owner approval pending.** A frozen spec is never edited (rule 2; its §0 change log is the only mechanism it has and that
> belongs to the next revision). This file is the errata list the next SPEC revision folds in: every row names the SPEC text, the design of
> record that supersedes it, the decision that made the change and where the evidence lives. Nothing here changes a part, value or topology
> — it RECORDS changes already decided. A row the owner approves becomes `APPROVED <date>` here and the next SPEC revision's change log cites
> it; a rejected row is struck through with the reason. `ARRIVAL_CHECKLIST.md` §E carries the OPEN rows with their trigger.

| E | SPEC text ({{SPEC_REV}}) | Design of record | Decision | Evidence / where the record lives | Status |
|---|---|---|---|---|---|
| E-1 | {{§ and requirement id, the value or part as the spec states it}} | {{what the design actually carries}} | {{D-nn / CC-nnn}} | {{datasheet note, procurement row, design yaml, review}} | OPEN (owner) |

## How this file is used
- A reviewer who finds "the spec says X, the design has Y" checks this table first; a deviation already here is ALREADY DECIDED, not a finding.
- When the SPEC is revised, every APPROVED row is applied to the text and the row is marked `FOLDED <rev>`; the file stays as the trail.
- Generated records that quote the superseded value keep it where it is still the part of record elsewhere (say so in the Evidence cell).
