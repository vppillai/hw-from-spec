# release-and-cut.md — the release report, the collateral, the tag, the production cut

## 1. Release report (`scripts/release_report.py`)
- Every number is read from a file; each section names its sources with md5; a missing input prints `MISSING: <path>` — never an exception, never a
  guess. Sections are functions (`section_<name>`), listed per report in `project.yaml reports:`.
- **DRAFT / RELEASED** from the gate file: the owner writes a line matching `markers.release_regex`; agents never write it and never quote the
  phrase in prose (a GATES.md sentence explaining the rule released every report in the smoke project).
- **Package of record** = the fab package whose `board_id.txt` md5 EQUALS md5(board); none → MISSING; several → exit 1 (one package of record).
  Never "newest by mtime".
- Identity carries RECORDED values (the package's commit), never live git HEAD — the commit that adds the report would make it stale.
- `--check` compares with volatile lines stripped and must pass on `git archive HEAD` (`scripts/clone_gate.sh`); selftest `os.utime()`s every input.

## 2. Determinism rules for every generated record
No mtimes; no absolute paths (`{PY}` printed unexpanded); no live HEAD; dates only on one volatile `Generated` line; sorted iteration; locale-pinned
sort; hash the LAST-written file last. Test: run twice from two checkout locations and diff.

## 3. Order of the chain after a copper change
Everything downstream is keyed on the board md5, so:
1. drawing / FEA (long) → 2. `collect_renders` (grades composites) → 3. commit → 4. `clone_gate.sh --regen` (reports from HEAD inputs only) →
5. commit the reports. DECISIONS / KNOWN_ISSUES / traceability records are report inputs: write them BEFORE step 4 or the cycle re-opens. Start the
chain only after the last board-touching workflow of the round (a silk-only merge changes the md5 and orphans everything).

## 4. Collateral (`scripts/collect_renders.py`)
`collateral/<md5-8>/renders/`: CAD 3-D renders (opaque background, named by what the picture shows, each fixed view checked by eye once), panel
preview, silk PNGs, case renders, FEA composites, drawing PDFs, fab-viewer captures carrying the md5. Freshness key = source md5 + full argument
string; case items keyed on the case version; index with md5 + grade; orphans listed, never deleted; PNGs ≤ 2400 px; size budget per set.
Quotes and captures the fab produced live under `docs/quotes/<date>/`, never inside a regenerable package (a rebuild wipes the folder).

## 5. Release notes (`templates/RELEASE_NOTES.md`)
Hand-written prose is allowed only with a generated source next to every number and a same-day re-check of every citation; `[FINAL: …]` for values a
concurrent agent is still producing. One generated-fact banner (board md5 / copper signature / package / case version) above any dated status.

## 6. Tag
Annotated tag (`<board>-rev<n>-order`, later `…-production-cut`) with the board md5, package path, case version in the message; it records the
orderable state and does not substitute for the owner's gate cells.

## 7. Production cut (`templates/production_cut.yaml` → one generator)
- One command builds `docs/production/<md5-8>/`: MANIFEST.json/.md (md5 + bytes + source + board/case/decisions md5 + tool commit + CAD CLI version),
  STATUS.md (banner, package of record, per-artefact disposition OF-RECORD / STALE / MISSING / WAIVED, OPEN census, the owner line quoted),
  the documents listed in the yaml.
- Deliverable row: `id, doc_id, title, kind (generated | hand-written | template | collected), path (glob ok), check (the owner generator's --check),
  inputs (md5-stamped), required (true | release), owner_placeholders (allowed | forbidden)`.
- Templates (records: photos, press logs, insert temperature/time, torque, test results, calibration, order screenshots) are written ONCE with
  `[OWNER: …]` fields, never overwritten, never filled by an agent; the manifest counts the placeholders; a RELEASED cut fails `--check` on a
  placeholder in a `forbidden` document.
- Document set (contents checklists live in the project's plan): product manual, developer manual (guards + overrides with record trail),
  technician manual (reason-code table generated from the code list, set equality asserted), manufacturing specification (order-form values from the
  package's ORDER_PARAMETERS, acceptance classes with standard revisions), assembly SOP (photos per step, fixture use, measured values), incoming
  inspection SOP (criteria file by name + sha256), analysis index (every report: source md5, of-record grade, disposition ACCEPTED / WAIVED-id /
  OPEN-CC / SUPERSEDED; OPEN without a CC row is an error), compliance statements evidence-bound (RoHS table from live supplier pages fetched at cut
  time; no declaration of conformity claimed).
- Standards cited from memory carry a VERIFY tag until checked against the primary text; a RELEASED cut may not carry a VERIFY tag in a normative
  statement (`grep VERIFY` is the check).
- Requirement family for the deliverables gets its own prefix after a prefix census of the spec (a collision happened once).
- Retention: the cut folder, the fab package of record and the records folder are kept; superseded packages are dropped when every consumer selects
  by md5 and the evidence lives outside them.
