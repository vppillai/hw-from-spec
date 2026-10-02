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
Everything downstream is keyed on the record md5 (`scripts/project.py record`: the board in ee / both, the STL set in mech), so:
1. drawing / FEA (long) → 2. `collect_renders` (grades composites) → 3. commit → 4. `clone_gate.sh --regen` (reports from HEAD inputs only) →
5. commit the reports. DECISIONS / KNOWN_ISSUES / traceability records are report inputs: write them BEFORE step 4 or the cycle re-opens. Start the
chain only after the last board-touching workflow of the round (a silk-only merge changes the md5 and orphans everything).

### 3.1 The one-round record chain (production cut) and the fixed-point pass
Generated records read each other, so the LAST round has an order, not a digest (skill scripts in `code`, the project's own generators in
*italics* — a project without one skips that step):
`known_issues` → *order sheet / package notes* → `collect_renders` (the reports hash its index) → `release_report` → `traceability` → `release_report`
(the matrix's report rows flip with the reports' freshness and the report quotes the matrix line: dependent writer, matrix, dependent writer again)
→ *analysis_index* → *render_pdf* (its PDF source md5s) → *production_cut build* LAST (the manifest stamps what the PDF renderer and the collector
wrote) → commit. Afterwards only the pure `--check`s; a `clone_gate.sh --regen` run AFTER the build makes the cut STALE although the reports are
content-identical (`production_cut --check` compares md5s, `release_report --check` strips the volatile lines) — a confirming regen copy-back is
discarded with `git checkout` once its diff is timestamp-only.
- **Fixed point** = run the round twice and diff; "nothing changed" is judged after stripping the volatile cascade (`Generated` → the document's
  md5 → every stamp of that md5 → `Tool commit`), not the timestamp lines alone. Count non-volatile lines per artefact (0); discard round two.
- Registering a NEW deliverable flips a manifest status the analysis index reads: that round is two passes by construction — plan for it.
- Whoever appends a DECISIONS row runs the round: a records-only commit without the regen chain is an unfinished commit (every report reads
  the log). The closer's own row is unmapped the moment it lands — write its traceability entry in the same edit.
- The PDFs are new bytes on every render (CreationDate); key derived PDFs on the SOURCE md5s and expect that churn in the commit.
- A collector that reuses an up-to-date copy must still recompute its GRADE; a generator that sweeps "everything not in my index" from a shared
  folder deletes a sibling's output — register foreign files with their own check instead.
- A generated document can carry a fetch-time stamp a yaml bump does not move (a compliance table's "case version" written at fetch time):
  every consumer of the version string is re-run in the bump.

## 4. Collateral (`scripts/collect_renders.py`)
`collateral/<md5-8>/renders/`: CAD 3-D renders (opaque background, named by what the picture shows, each fixed view checked by eye once), panel
preview, silk PNGs, case renders, FEA composites, drawing PDFs, fab-viewer captures carrying the md5. Freshness key = source md5 + full argument
string; case items keyed on the case version; index with md5 + grade; orphans listed, never deleted; PNGs ≤ 2400 px; size budget per set.
Quotes and captures the fab produced live under `60-orders/quotes/<date>/`, never inside a regenerable package (a rebuild wipes the folder).

## 5. Release notes (`templates/RELEASE_NOTES.md`)
Hand-written prose is allowed only with a generated source next to every number and a same-day re-check of every citation; `[FINAL: …]` for values a
concurrent agent is still producing. One generated-fact banner (board md5 / copper signature / package / case version) above any dated status.

## 6. Tag
Annotated tag (`<board>-rev<n>-order`, later `…-production-cut`) with the board md5, package path, case version in the message; it records the
orderable state and does not substitute for the owner's gate cells.

## 7. Production cut (`templates/production_cut.yaml` → one generator)
- One command builds `<production_dir>/<rev>/` (`70-release/rev0/`; `{rev}` = `project.revision`, `{md5}` = the record md5 — both expand in the
  yaml, the folder carries the revision and the hash sits inside): MANIFEST.json/.md (md5 + bytes + source + board/case/decisions md5 + tool commit + CAD CLI version),
  STATUS.md (banner, package of record, per-artefact disposition OF-RECORD / STALE / MISSING / WAIVED, OPEN census, the owner line quoted),
  the documents listed in the yaml.
- Deliverable row: `id, doc_id, title, kind (generated | hand-written | template | collected), path (glob ok), check (the owner generator's --check),
  inputs (md5-stamped), required (true | release), owner_placeholders (allowed | forbidden)`.
- Templates (records: photos, press logs, insert temperature/time, torque, the first-article caliper table, test results, calibration, order
  screenshots) are written ONCE with `[OWNER: …]` fields, never overwritten, never filled by an agent; the manifest counts the placeholders; a
  RELEASED cut fails `--check` on a placeholder in a `forbidden` document. **The one records folder is `70-release/<rev>/records/`**
  (`records_dir` in the cut yaml; RELEASE_NOTES and the "capture now" list point there — never a second home under `70-release/reports/`).
- **Labelling and regulatory marks are a DFM item**: the manufacturing spec names where the serial / model label, any claimed CE / FCC / WEEE mark
  and warning icons sit on the enclosure (a recess label + 1 mm each side, a flat land, reading orientation), what carries them (label carrier,
  engraving ≥ the void gate, UV print) and what is NOT claimed (no DoC); the case yaml carries the recess.
- **Packaging, shipping, storage** (one paragraph in the manufacturing spec): ESD bag for the assembled unit; printed parts wrapped or in card
  (MJF parts ship loose and scuff, SLA plates warp in a hot van); PA12 moisture uptake before insert installation (dry 4 h at 80 °C or install
  within a day of unpacking); PLA storage below 40 °C; magnets kept paired and away from the boards.
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
- **The home-FDM print kit is a deliverable row** (`kind: generated`, `check` = the kit text gate + the mirror md5 list): `START_HERE.md`, print
  sheets named for their `.3mf`, READMEs, sidecars, the generated ASSEMBLY.md — all from the knobs (`references/print-kit.md`). A kit text that
  carries `None` / `nan` / a `{name}` brace, a repo path, a dead file reference or a token of a feature the preset disables (snap tab / screws
  under `fastener: magnets`, PETG under PLA) fails the cut like a placeholder in a `forbidden` document. The ASSEMBLY / QA prose is generated from
  the preset like the geometry (a hand-kept SOP said "0 magnets, PETG, snap tabs" three fastener changes later).
- A PLACED order's package is frozen: notes may be re-derived (`--refresh-notes`), fab files / panel / board_id never rebuilt; its stock gate reads
  the frozen order-day records (`references/fab-dfm.md` §8).
- After the order the vendor's engineering review may arrive: `references/vendor-review.md` (agents never pay / agree / cart; Replace File only on
  the owner's word); the case bump it may force costs ≈ 45 min of machine time (`references/case-pipeline.md`).

## 8. Illustrated assembly guide (`scripts/assembly_guide.py`)
Beside the text SOP, a picture per step: authored SHORT yaml (parts / tools / check / camera per step, fixed pages before and after), generated
step text (the case generator's `### Step N - title (T s)` + paragraph → the first two sentences), one clean render per page from the geometry of
record (marketing look: clean scheme, the ordered colours, legends readable → cameras on the side the legend is laid out for), keyed on
(geometry md5 of the one scad file named — flatten includes or accept that included files do not move the key, defs, camera, size) so a text edit renders nothing and a case bump re-renders every page (≈ 1 min). Numbers stay in the SOP /
manufacturing spec (one source); the guide names where the words are. Registered in `production_cut.yaml` as a deliverable with its `--check`;
the SOP's companion cell points at it (a pointer, no revision bump).

## 9. Repo re-layout and deletions at the order (`scripts/reorg_paths.py`)
When the tree is a mess at the order: phase 1 deletions (superseded generated artefacts; git history + tags keep them), phase 2 re-layout after
the owner sees the proposed tree. Method: decision row → `reorg:` block → `--plan` → `git ls-files -s` BEFORE → `--apply` → regenerate every
generated file that embeds paths (never edit them) → `--check` 0 findings → AFTER dump → `--proof BEFORE AFTER REWRITES` (every blob at its mapped
path with the same sha, or in the rewrite list) → gates → tag. Frozen records keep the old paths (`--map` reads them); an uploaded package's
generator-owned notes are re-derived, its fab files never rebuilt. URLs into the repo are not rewritten (grep `blob/.*/<old>` by hand). Before a deletion: grep basenames AND exact paths, separate live citations
(gen/, design/, CI, live docs) from record citations (DECISIONS / STATUS / merged reviews) — treating records as blockers freezes the tree; a
traceability `exists` check on a file that leaves the tree becomes `git show <tag>:<path> | grep -qF '<same string>'`, nothing weakened.

## 10. The arrival / first-article checklist (`scripts/arrival_checklist.py`) — written at the order, closed as the parts arrive
`20-design/arrival_checklist.yaml` (`templates/design/arrival_checklist.yaml`) → `60-orders/ARRIVAL_CHECKLIST_rev0.md`; `--check` joins `gates.adopt`
the moment the yaml exists (`project.py gates-required`), the markdown is a cut deliverable (`production_cut.yaml` REC-002). Sections in the order of
the day: **before shipment** (the fab's assembly photos: polarity vs silk, the critical connector's seating, holes that must stay open — a paid
"confirm production file / placement" option is not guaranteed to raise a dialog, so the photo confirmation is the one human look), **bench checks in
gate order** (each row names the instrument / net / expected value, what to do on FAIL, and what it `opens`: nothing is powered or plugged before
the row that opens it is DONE), **software gates before the first high-power step** (each with the commit that closed it), **case first article**
(the caliper table that replaces the vendor's tolerance, fit by hand, retention cycles, coupons read by their printed text), **owner decisions still
OPEN** with the measurement that resolves each (the bracket-print fit knob → `kickoff.enclosure.fit_result`; SPEC errata rows). The rows come from
the merged blind reviews ("what the boards decide" = the CONFIRMED items whose closure is a bench step) and the OPEN decision rows — written BEFORE
the parts arrive, never reconstructed afterwards. Every row carries `status` (TODO / DONE <date> / N/A / APPLIED <date> while the owner's veto
window is open) and `evidence`; the script refuses a DONE without evidence, a duplicate id, a status outside the grammar. Closing a row = yaml edit,
regenerate, commit.

## 11. A frozen SPEC gets an errata file, never an edit (`templates/SPEC_ERRATA.md`)
`10-spec/spec_sections/SPEC_ERRATA.md`: one E-row per deviation of the design of record from the frozen text — the SPEC text, the design of record, the
decision that made the change, where the evidence lives, Status OPEN (owner) → APPROVED <date> → FOLDED <rev> when the next SPEC revision's change
log cites it; a rejected row is struck through with the reason. It records changes already decided (rule 2); it changes nothing. Readers: the
blind-review verifier (a deviation already here is ALREADY DECIDED), the arrival checklist §E (OPEN rows with their trigger), the next spec author.
