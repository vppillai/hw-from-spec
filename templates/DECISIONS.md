# DECISIONS.md — proposals and decisions log

IDs: **D-nn** = owner decisions (text as issued by the owner); **CC-nnn** = agent proposals/decisions. Status values: **OPEN** (needs the owner),
**APPROVED** (owner approved, applied), **DECIDED** (within delegated authority, applied), **APPLIED (!)** (applied ahead of the owner's nod — the
marker puts the row into KNOWN_ISSUES §2.1), **REJECTED**, **SUPERSEDED**, **CLOSED**. History goes after `(was: …)`. A literal pipe in a cell is `\|`.
An ID is reserved only when its row is in HEAD — `grep -c '^| CC-nnn ' docs/governance/DECISIONS.md` immediately before writing (CC rows; owner rows are bold).

| ID | Date | Status | Topic | Proposal / decision | Reason |
|---|---|---|---|---|---|
| **D-01 (owner)** | {{DATE}} | **APPROVED** (owner, SPEC {{SPEC_REV}}) | Project start: SPEC {{SPEC_REV}} is the input | Owner: "{{OWNER_QUOTE}}" | Owner's word |
| CC-001 | {{DATE}} | DECIDED (process) | Process = hw-from-spec skill commit {{SKILL_COMMIT}} (SKILL.md version {{SKILL_VERSION}}) | project.yaml written; templates seeded; evidence cell filled AFTER SKILL §0 step 6: `{{EVIDENCE: selftests / smoke / adopt gates green at <sha>}}` | one process, generated only |
