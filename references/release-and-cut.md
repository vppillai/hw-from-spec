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
→ `now_pages` (the five answers of `00-now/` read the gates, decisions, status, blockers, the arrival yaml and the kit sidecars) → *analysis_index* → *render_pdf* (its PDF source md5s) → *production_cut build* LAST (the manifest stamps what the PDF renderer and the collector
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
`collateral/<rev>/renders/` (RENDERS.md's first row names the record md5): CAD 3-D renders (opaque background, named by what the picture shows, each fixed view checked by eye once), panel
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

## 8. Illustrated assembly and use guide (`scripts/assembly_guide.py`)
Beside the text SOP, a picture per step, rendered from the exported meshes of record. Pages, in order: the parts, magnet installation with
polarity (`print-kit.md` §2), loading, closing orientation with the keying feature marked, taking a part out, care. The PDF ships in the release
folder beside the drawing (§12); the kit's START_HERE points to it. Inputs: authored SHORT yaml (parts / tools / check / camera per step, fixed pages before and after), generated
step text (the case generator's `### Step N - title (T s)` + paragraph → the first two sentences), one clean render per page from the geometry of
record (marketing look: clean scheme, the ordered colours, legends readable → cameras on the side the legend is laid out for), keyed on
(geometry md5 of the one scad file named — flatten includes or accept that included files do not move the key, defs, camera, size) so a text edit renders nothing and a case bump re-renders every page (≈ 1 min). Numbers stay in the SOP /
manufacturing spec (one source); the guide names where the words are. Registered in `production_cut.yaml` as a deliverable with its `--check`;
the SOP's companion cell points at it (a pointer, no revision bump).
- **Pages carry real text.** A page is a vector page (SVG or HTML) with the text as text and the picture embedded as a raster; the PDF comes from
  a vector converter (`rsvg-convert`, a headless browser) and the pages are merged (`pypdf`). A page rasterised whole is rejected on first read:
  nothing selects, nothing searches, the fonts blur. Layout: a title page (title, subtitle, one-sentence purpose, date + `git describe`, the hero
  picture, a parts table with quantity and note), then one step per page (numbered badge, title, the picture in a hairline frame, numbered
  instructions, a grey note, a CAUTION box where a hazard exists, a footer with the document name, page N of M, the revision).
- **Illustrations are shaded line drawings, not the marketing render.** The marketing look (dark parts on a dark scheme) is low-contrast on paper and
  on a laptop. Each picture is two passes over the SAME meshes of record: a shaded pass with light part fills (two greys for the two parts, the
  ordered inlay colour, red for arrows and markers) and a flat pass with every part in one grey; the edges of the flat pass (`FIND_EDGES` over a
  threshold, grown one pixel) go black over the shaded pass, on white, cropped with a margin, with a warning when the content touches the frame.
  Mated boards keep their real art mapped on (the showcase's mapping, the same cameras).
- **A recess in a line drawing reads as a raised outline.** Debossed text, pockets and slots on a coupon come out as hollow outlines on a flat face.
  Split the mesh by height — `difference(mesh, inner column)` light and `intersection(mesh, inner column)` dark, the column 0.01 below the top
  face and 1 mm inside the outer walls so the sides stay light — and view it steep enough (about 30 degrees from vertical) that the recess walls
  vanish; the floors then read dark on the light face, the way the printed part reads.
- **An arrangement that a perspective view hides gets a section inset.** Alternating slot heights, a lip inside a rim, a notch above a shoulder:
  ten loaded parts in a perspective view hide the pattern; load a FEW (five of ten, one on its way with an arrow) so the empty slots show the
  floors, and add an inset: a thin slab (2 mm) `intersection()` through the plain region, ORTHOGRAPHIC, seen square on, parts in their two colours.
  In a rendered boolean the colour goes OUTSIDE the `intersection()` / `difference()` (a rendered boolean drops its children's colours). The inset
  sits beside a wide main picture or under a square one, with a short label ("Section across the case"), the position computed from the two sizes.
- **Every number in the text comes from the design parameters** (the same file the meshes come from): counts, magnet size, the pinch band, the
  recess below a face. The guide reads the parameter file the way the drawing does (a regex over `NAME = value;` lines, derived values by one
  `echo()` run); a design change moves the pictures AND the words. Counts are words ("four magnets"), dimensions are digits ("6 x 3 mm").
  Cameras are the one hand-tuned input: a size change that moves a feature out of frame trips the frame warning, not a wrong number.
- **Wording for the reader of the part, not the author of the file**: no axis names, no parameter names. "The front", "a rear corner", "the long
  side", "a high board", "the band above its neighbours" — words a person with the part in hand can follow.

## 9. Repo re-layout and deletions at the order (`scripts/reorg_paths.py`)
When the tree is a mess at the order: phase 1 deletions (superseded generated artefacts; git history + tags keep them), phase 2 re-layout after
the owner sees the proposed tree. Method: decision row → `reorg:` block → `--plan` → `git ls-files -s` BEFORE → `--apply` → regenerate every
generated file that embeds paths (never edit them) → `--check` 0 findings → AFTER dump → `--proof BEFORE AFTER REWRITES` (every blob at its mapped
path with the same sha, or in the rewrite list) → gates → tag. Frozen records keep the old paths (`--map` reads them); an uploaded package's
generator-owned notes are re-derived, its fab files never rebuilt. URLs into the repo are not rewritten (grep `blob/.*/<old>` by hand). Before a deletion: grep basenames AND exact paths, separate live citations
(gen/, design/, CI, live docs) from record citations (DECISIONS / STATUS / merged reviews) — treating records as blockers freezes the tree; a
traceability `exists` check on a file that leaves the tree becomes `git show <tag>:<path> | grep -qF '<same string>'`, nothing weakened.

## 10. The arrival / first-article checklist (`scripts/arrival_checklist.py`) — written at the order, closed as the parts arrive
`20-design/arrival_checklist.yaml` (`templates/20-design/arrival_checklist.yaml`) → `60-orders/ARRIVAL_CHECKLIST_<rev>.md`; `--check` joins `gates.adopt`
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

## 11. A frozen SPEC gets an errata file, never an edit (`templates/10-spec/SPEC_ERRATA.md`)
`10-spec/SPEC_ERRATA.md`: one E-row per deviation of the design of record from the frozen text — the SPEC text, the design of record, the
decision that made the change, where the evidence lives, Status OPEN (owner) → APPROVED <date> → FOLDED <rev> when the next SPEC revision's change
log cites it; a rejected row is struck through with the reason. It records changes already decided (rule 2); it changes nothing. Readers: the
blind-review verifier (a deviation already here is ALREADY DECIDED), the arrival checklist §E (OPEN rows with their trigger), the next spec author.

## 12. The release folder: copies, named by use, written by the cut
- `70-release/<rev>/` (one subfolder per product in both scope: `board/`, `case/`) holds only copies of build outputs. Nothing in it is
  hand-edited. The cut generator (§7) writes every file and the folder's `README.md`.
- The README is the manifest a person reads (MANIFEST.json stays the machine copy): the build date and `git describe`, the design values read
  from the parameter block, each check that passed with its count, the MD5 and size of every file, the print or order procedure as numbered steps.
- Name each subfolder by what a person does with it, never by file type: `<slicer>-projects/multi-colour/`, `<slicer>-projects/single-colour/`,
  `stl-for-other-slicers/`. A `meshes/` folder beside the slicer projects was not understood by the owner **[K]**.
- File names state the filament role: `<part>_body_filament1_<colour>.stl`, `<part>_inlay_filament2_<colour>.stl`, `<part>_single_colour.stl`.
- Every multi-material part also ships as a single-colour variant (the colour body merged into the host), so a printer without a multi-material
  unit has a file. Test prints (coupons, dummies) ship as single-colour projects in the same folder.
- A slicer project written by the slicer CLI embeds timestamps and UUIDs, so its MD5 moves on every run without a design change **[V]**. The
  manifest records the MD5 of the committed copy; the mesh checks prove the geometry identity, never the project hash.

## 13. The order record, beside the manufactured files
`60-orders/ORDER_<rev>.md` records the order so that a reorder needs no memory; the product's release-folder README links it. It carries:
- every vendor option as set on the order page, read from the page: layers, quantity, thickness, colour, silkscreen, finish, copper weight, via <!-- style: ok -->
  covering, order-number removal, tolerance, electrical test, serial number;
- the price at order, the cart line name, the uploaded file name and its MD5;
- reproduction as numbered steps from the release asset: download, compare the MD5, upload, set each option;
- the known deviations of the delivered batch, added at arrival (§10).
Prove that the release asset equals the uploaded file: download the asset, compare the MD5s, write both in the record. An options table in a
README alone did not answer the owner's "are the settings backed up" after the order **[K]**.

## 14. Clean tree, rebuild from empty, the tag-gated CI compare
- After a build that is not a release, restore each committed file of record the build rewrote (`git checkout -- <file>`). `git status --short`
  is then empty and `git describe` carries no `-dirty`; the drawing title block and the manifest print it (`case-pipeline.md` §Drawings).
- A file of record changes only in the commit that changes the record (for a generated board file: the release commit).
- Before a release: delete every `build/` folder, regenerate everything from empty, run the gates, then read `git ls-files` and
  `git status --short --ignored` for strays.
- CI compares a rebuild with the release archive only on the release tag: the step runs when `git describe --tags --exact-match` equals the
  VERSION in the order record. Main moves after the order without a red build.
