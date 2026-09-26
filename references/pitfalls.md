# pitfalls.md — every recorded learning, one line each, generalised

Source: the AEC-CT2-MINI `docs/governance/LEARNINGS_LOG.md` (2026-09-21/22, ~155 entries). MINI-specific numbers are kept only where they make the
mechanism concrete and are labelled *(worked example)*. Evidence pointers name the source repo's rows/files. Grouped by domain.

## process / gates
- A DFM/DRC rule set at the fab's published limit passes DRC and still lights up the fab's DFM: mirror the fab's checks in-repo and gate on them — CC-124/127/128.
- A value changed on the schematic symbol does not change the ordered part (BOM groups by fab code): gate value ↔ MPN ↔ code — audit #2 F02.
- Blind reviewers must not see the author's dispositions; a hand-off naming a board the frozen worktree does not carry invalidates the review — CC-103, `handoff_header`.
- A visual gate must READ the rendered artefact; geometry-only checks passed 25 blank bars and 26 mutilated words *(worked example)* — SILK_R6G/R6I.
- A rule-2 gate can ship ahead of the nod as an OPTIONAL flag that warns when omitted; the nod becomes `required=True` — CC-142.
- Typed sentences in order remarks rot; generate them from the rule file and the board, keep only the vendor paragraph static — audit #3 R5.
- KNOWN_ISSUES listing only cells that START with OPEN hides "APPLIED — nod wanted" rows: the nod marker needs its own generated section — audit #3 K16.
- A generator keyed on a literal marker re-triggers on prose that DESCRIBES the marker; describe markers indirectly in status cells and gate files — known_issues nod section; smoke GATES.md (this skill).
- A repo-wide grep count is not a work estimate until split by ownership (records that must not change vs live docs) — docs sweep 2026-09-21.
- Hand-routing in parallel works with geographically disjoint clusters, fresh copies + the real DRC per iteration, one shared deletion list, one owner for cross-cluster nets — round 6j.
- Fragment agents + ONE arbiter script (fresh copy + fragment + enforced DRC + baseline delta) merge cleanly; the harness must fail HARD when a fragment does not apply — round 6k.
- Archiving a STATUS section must move the heading with its CLOSED line (or leave a CLOSED pointer): a generator deriving "round open" from headings grew a false banner — CC-151.
- State derived from a heading in a hand-maintained doc breaks the day the paragraph is archived; derive it from every record that can carry the close and selftest the archived case — CC-151/G03.
- Hash-checking generated metadata proves "not hand-edited", not "still derived from today's inputs": `--check` must re-derive and diff; the hash stays for tamper detection — fab_package G15–G17.
- A requirement family ID can collide with an existing spec prefix: grep the prefix census before proposing IDs, log the alternative as OPEN — CC-133.
- Deliverables needing photos, press logs, print settings, test results cannot be written at the end unless filed as they happen: a "capture now" list + records folder before the first build — PRODUCTION_CUT_PLAN §5.3.
- Owner additions arrive mid-run: kill a long render early rather than finish and redo; quoting a superseded file wastes a signed-in browser pass — CC-171.
- A stage gate hides the rows behind it: read PENDING rows' `now k/n` as failures-in-waiting; never pin a gate check to a literal md5 — traceability 2026-09-21.
- A NOT-INCLUDED row whose reason starts "OPEN" flips to FAILED when the decision lands: every owner status sweep needs a reason sweep in the traceability yaml — R6-K01.
- A "stale literal" in a requirement matrix is the check, not the requirement: pin versions with a family regex (`v3\.\d+-`), never `exists` a gitignored file, sort every FAILED row into literal vs real — CC-173.
- Dated "Status:" banners read as current forever; put one generated-fact banner above and mark the old one history; grep retired words in LIVE docs only — release sweep 2026-09-22.
- Hand-written release notes: every number carries its generated source; re-check every citation the same day; `[FINAL: …]` for numbers a concurrent agent still produces — release notes 2026-09-22.
- The reports ↔ matrix cycle closes in two rounds if DECISIONS / KNOWN_ISSUES records are written BEFORE the last round (both are report inputs) — CC-121.1.
- Owner direction "speed up the scripts" → a parallelism/caching plan gated on "reproduce the recorded numbers bit-for-bit or explain the delta" — CC-172.

## agents / git
- Agents die when the machine sleeps or on API 500s; resume by message with the MEASURED state; heartbeat monitors ~25 min; time-box every long task; parallel router JVMs SIGTERM each other — STATUS 09-18…21.
- Background-task watchers did not wake the coordinator: block in-process with `until ! kill -0 $pid; do sleep 20; done` (≤ 600 s per call, repeat) — 2026-09-22.
- `git commit -- <path>` commits the WORKING-TREE state of the path, not the index: other agents' unstaged hunks in that file are swept in, and a `git rm --cached` is re-added. Stage the exact edit: apply to working copy AND to `git show HEAD:file`, `git hash-object -w`, `update-index --cacheinfo`, commit the index — 2026-09-21/22 (happened three times).
- A staged `git rm`/`git mv` set survives only until the next agent's bare `git commit`: stage and commit in one command — D-61 cleanup.
- Two agents editing one shell script with exact-string edits at different lines is fine; a status-cell edit prepared from a stale read fails: re-grep immediately before replacing, prefer suffix append — CC-149.
- Two agents appending record rows in the same quarter hour collide (`CC-%03d` template literal landed): the ID is reserved when its row is in HEAD; `grep -c` right before writing — CC-159/160.
- `git add dir/*_v3.11.png` silently skips `*_v3.11_slide.png`: `git status --short <paths>` after every explicit-path commit of a generated set — FEA composites.
- A selftest that rewrites and compares shared repo files is flaky while another agent saves the board: selftests work only in their temp dir — fab_package `report=False`.
- Regenerating a matrix while a sibling's half-written yaml sits in the tree turns every check that loads it FAILED: diff the new FAILED ids against HEAD, attribute to one shared cause, restore and report — 2026-09-21.
- Coordinates in a finding may be in the CAD frame (Y down) while the checker reports the board frame: convert before deciding "missing" — 2026-09-21.
- Blind verifiers re-find every waiver each round because the waiver list is not in their input set: hand them the one-paragraph list (no reasoning) — review/process.
- Shared docs carried other agents' hunks: snapshot pre-edit, stage `HEAD + own hunks` — agents/git 2026-09-21.

## tooling / determinism
- The file md5 of an in-place CAD step is write-order dependent; assert a sorted content signature, keep the md5 informational — CC-143.
- Any identity hash built from `sort` must pin the locale (`LC_ALL=C`): the same copper gave two signatures under two locales; re-stamp every recorded value in the SAME commit as the recipe — round 6l.
- A `--check` that embeds anything a clone changes (mtimes, absolute paths, `{PY}` expanded) never passes on a fresh checkout; test by `os.utime()` every input and by running from two checkout locations and diffing — G02, CC-173.
- Gate the committed tree with `git archive HEAD | tar -x` (no .git, no untracked, fresh mtimes), not `git clone --local`; unpack at a path of the SAME LENGTH as the repo root when labels truncate — clone_gate, CC-173.
- A "check" that calls a writing generator rewrites tracked files: run writers in a sandbox copy (`gen/ + design/` copied, big inputs symlinked); find the input list empirically from `FileNotFoundError` — G08.
- Generated records print paths ROOT-relative — the absolute interpreter path leaked into 26 rows and defeated the fixed point — CC-173.
- `open(p, "w").write(banner + open(p).read())` truncates before the inner read; read into a variable first; selftest that the body survives — fab_package stamp.
- A record that copies identity fields only after a gate returns loses them on refusal: identity first, gate second — CC-142.
- "Newest by mtime" picks the wrong package on a fresh checkout: select by the md5 in `board_id.txt`, print MISSING when none — audit #3 R9.
- A MANIFEST hashing a gitignored file never verifies on a clone: skip such files and flag a manifest that lists one — audit #3 R8.
- A MANIFEST must be the LAST file written; every later stamp re-hashes — package/manifest.
- md5-keyed evidence written mid-chain names an intermediate file: take every evidence file as the last step or key on the content signature — kicad/drc/evidence.
- `git archive` flattens mtimes: a `newer()` gate fails and rows fall PENDING; the content key is `md5_in(path, file, regex)` — round 6l R5.
- A traceability matrix generated in the working tree reads other agents' uncommitted files: generate it from the archive at an equal-length path; the matrix is a HEAD artefact — 755eea9.
- A `type: command` check via `shell=True`: backticks in the regex are command substitution (`\x60`); a python heredoc doubles every backslash in YAML regexes; in a YAML single-quoted scalar a backslash is literal — write `'\('`, probe with `--only` — traceability yaml.
- When a fix changes a sentence, re-read the selftest that guarded the OLD sentence; assert the exact wording that must be gone — tooling/selftests.
- `assert "x.png" not in text` fails when a note names the skipped file; assert on the table cell — selftest.
- A glob over a collateral folder returns sub-directories; filter `isfile` wherever a glob feeds a hash — release_report.
- An idempotent collector keyed only on the source md5 keeps a stale image when the CAMERA changes; put the render arguments into the freshness key — collateral/idempotence.
- A collector keyed on the board md5 misses case-only artefacts; case pieces need their own key (version tag); walk the tree once, relative paths — collector.
- Redirected Python block-buffers stdout: a 15-min run shows an empty log; judge by `kill -0 $pid` and output files, or `python -u` — twice.
- macOS/zsh: no `timeout(1)`; `echo ====` is command-name expansion (use `printf --`); an unquoted `$c` does not word-split (`${=c}`); BSD `du` has no `--exclude`; `sips --cropOffset` unreliable — shell.
- A `set -e` export chain aborted on a failing DFM step before the exports: record the exit and continue — round 6g-Cu (6).
- Twenty generators hard-coded the macOS CAD paths and `md5 -q`; put `KICAD_CLI` / `KICAD_PYTHON` / `md5` behind one env module on day 1, CI wrapper before the tenth generator, gate list in a Makefile the developer runs locally — ci/tooling 2026-09-22.
- A schematic `--check` that regenerates the project file drops the rules a later generator wrote there: check into a scratch `--out`; a generator sharing a file must merge or refuse in place; keep ERC waivers in a repo doc, not only in the project file — tooling/gates 2026-09-22.
- A python generator with no `__main__` exits 0 silently and writes nothing: check the census header line changed, not the exit code; quote check-mode vs full-run totals with the mode — case/tooling.
- An export script's `rm -f $O/*.json` swept a cache another `--check` requires (it never writes one): rebuild the cache after every export on a new md5 — export/process.

## kicad / drc / swig *(worked examples; the mechanism generalises to any CAD CLI)*
- `kicad-cli pcb drc` honours ONLY explicit `netclass_assignments`, never `netclass_patterns`, and NO DRC exclusions: emit per-net assignments from the generator, assert a canary rule fires exactly once; accepted residue = a generated RULE (`enclosedByArea`, not `insideArea` which is an intersection test — prove with a negative construction in `--selftest`) — audit #4 G01, CC-148.
- Enforcing net classes for the first time on a "DRC 0" board showed 202 errors; a class clearance larger than the fill's zone clearance is unenforceable by construction: write the as-built geometry into scoped rules general → specific (later rule wins), log the relaxation — round 6k.
- `pcbnew.LoadBoard()` reports netclass Default for every net: resolve class patterns yourself and selftest with a Power net carrying one thin segment — audit #3 P02.
- A standalone schematic regeneration rewrites the `.kicad_pro` to the skeleton (rules, classes gone): restore from HEAD or make the writer leave it alone; "netlist unchanged" = md5 of the `<nets>` block, not the file — kicad/gen.
- A `.kicad_dru` rule stricter than the net class is invisible to the autorouter and appears as errors afterwards; an unconditional custom clearance rule REPLACES every class clearance — build v2/v3.
- A malformed `.kicad_dru` (unknown property) is silently ignored: the canary rule — CC-010.
- DRC on a COPY of the board in another dir reports "footprint library not enabled" (`${KIPRJMOD}` paths): run in place or copy the lib table with absolute paths — v3 notes.
- SWIG: `BOARD.Remove()` breaks `Tracks()` iteration in-process (order add → clip → remove → fill → save); a second `LoadBoard` of the same file segfaults; `ZONE.SetOutline(poly)` takes ownership (`thisown = False`); proxies of deleted items segfault; `GetStart()` aliases the live member (copy before revert); `PCB_VIA.GetEffectiveShape()` without a layer is the HOLE; `SHAPE.Collide(VECTOR2I)` segfaults; bbox-filtered collision probes miss long segments; footprint rule areas are not in `board.Zones()`; `GetBoundingBox()` temporary must outlive its origin read; a bare `BOARD()` after a project load corrupts the settings manager — gen/README lessons 7–14, round 6d/6k.
- Zone fills without `BuildConnectivity()` starve pours silently (island removal deletes pieces) — audit #2 F01.
- `kicad-cli pcb render` PNGs default transparent (black mask vanishes in dark viewers): `--background opaque`; name a view by what it shows, check each fixed view by eye once; `--rotate -45,0,45` put every legend upside down — renders.
- A disputed clearance is one `GetEffectiveShape(layer).Collide(other, clearance)` bisection; a review number about copper carries the script that produced it — drc/measurement.
- Freerouting: deterministic with one thread + same DSN + long enough timeout; the routed board + SES are the record, regenerate by `--import-ses`; planes in the DSN make it skip pads over same-net plane polygons; keep-outs must be exported (grep the DSN); its "violations" count is against its own class model — ENV Freerouting, CC-069.

## layout
- A 0.62 via ring at 0.16 rules cannot sit on every other pin of a 0.5 mm pitch part; alternate in/out, GND to the pour *(worked example)* — CC-125/126.
- A plane fan-out that skips "pads touched by a locked pre-route" un-fans every pad whose pre-route is a pad-to-pad link without a via: ask "does the locked copper reach a via?" — CC-143.
- Dead ends propped up by a stacked duplicate escape every end-point test: cluster ends per layer, flag an unanchored cluster with ≤ 1 neighbour; prune in two passes — D-22 M-04.
- Dump rule areas (board AND footprint) and silk texts before choosing a via site; silk vetoes sites the copper allows — round 6j.
- Detours are pocket problems, not routing problems: read the pocket on all layers at both ends before promising a length — round 7.
- A DRC-arbitrated width sweep (set every under-class segment to class width, revert step-wise where ANY error names it) widened 105 of 145 segments in one run; path-scoped allow rows keep tap chains intact — round 6k.
- A power-via checker filtering by "attached copper ≥ trunk width" is blind for a net whose pads are thinner: emit an explicit "0 transitions" row per net; calibrate per-net thresholds at the pad-strip width — tooling/gates.
- A GND pad inside a higher-priority pour's OUTLINE gets no pour; keep-outs sized from pad extents, not footprint centres; a locked fan-out via whose attachments lie on one layer is dangling — iteration 6.
- Router keep-outs deleted by a clean-up before the export loop: grep the DSN for keepout polygons after any flag change — iteration 4.
- Via-in-pad: re-siting EVERY via to clear pads moved vias across pour pieces and re-solved neighbours — touch only the offending sites — round 6e.
- Silk labels follow their footprint: measure label bounding boxes before nudging a labelled part — round 6f.
- A pre-route stub starts at the pad END for pads on a notch wall (the centre trips the edge rule) — round 2.
- Reserved sites: hold a future part's area with a rule area + a checker entry; delete both when the part arrives — CC-066.

## silk / dfm
- The fab's DFM grades a value EQUAL to its warning threshold as Warning: design strictly greater — D-47 thresholds JSON.
- "THT to SMD" applies to EVERY plated/non-plated pad incl. round header pins, mounting-hole annuli and slots (read as SMD) — CC-128.
- Clipping silk around every via hole mutilates glyphs: the rule is "no via under a silk text cell" (via keep-out from the text bbox), clipping only for hairlines — SILK_R6I M-1.
- A 1.0 mm stroke text is ~1.9 mm wide across its lines; a 1.1 mm TrueType label is 0.75–0.8 mm per character; a via costs 0.37 mm from centre to ink *(worked example)* — round 6c/6i.
- A silk-to-edge test on the outline bounding box cannot see notches: test against the true outline polygon; selftest with a notched outline — SILK_R6J S1.
- A hit/no-hit checker cannot rank candidates: bisect `Collide` over obstacles + every OTHER silk item and print the legal RANGE — CC-170.
- "No cell there" claims age with the copper: re-measure every historical position override before carrying it into a new hop — CC-087/170.
- In-memory probe glyphs differ ~0.02 mm from the saved file: pick with ≥ 0.05 margin, re-measure on the saved board — silk/measurement.
- A legend word in front of a pad column must read TOWARD the pads (item order, not nearest glyph); ≥ 1.0 mm between labels of different owners — silk/ux.
- A TP courtyard is a zero-clearance obstacle for hairlines: assign a word to a pad by flush placement, never by a tick — silk/tooling.
- `clip_silk_at_holes` must be the LAST silk step, on the RELOADED board (TrueType exists only in the saved file) — round 6g-Cu.
- KiCad's `text_thickness` warning is an estimate on TrueType; the morphological glyph-stroke test is the gate — round 6i.
- Root-sheet NOTES and design notes quote silk strings by hand: grep the merged strings across `design/*.yaml` + `docs/*.md` after every silk merge — docs/silk.
- Mask expansion +0.05 cuts 0.5 mm pitch webs below the fab's bridge minimum: pin mask = copper on fine-pitch parts — round 6g-Cu.
- Silk footprint strokes below the fab minimum: widen at build time, move to Fab what reaches a pad — round 6d.
- Silk labels that read from the connector side need a reading-frame flag (180° on every label) — silk pass.
- Don't add a custom silk clearance DRU rule: it tests silk against Fab texts and courtyards too — silk pass.

## jlc / fab *(the worked example; the pattern is: verify the fab's form live, mirror its checker, never trust the published limit)*
- Published 2 oz outer minimum 0.16/0.16; the board sat at 0.15 believing it was the limit — CC-101/D-47.
- Standard PCBA needs every board side ≥ 70 mm; auto rails land on the SHORT edges; a customer panel with long-edge rails is mandatory for a narrow board; V-cut impossible below 0.40 copper-to-edge → mouse bites — CC-097.
- Press-fit hole option and "Edge Rails/Fiducials = Added by Customer" are easy to miss on the quote form; the first quotes were wrong — JLC_QUOTES.
- Run the fab DFM on the PANEL zip: merged drill files cannot mark mouse-bite holes NPTH (30 "unconnected via"), fiducials add warnings; a remark sentence settles it — dfm/panel.
- Library zero of a 1×N pin header runs along the row (KiCad's along −Y): +90° CPL offset visible only in the fab's placement preview; keep `review: true` until confirmed; the REVIEW list follows the rule, not the side — JLC/CPL.
- A part with a stock shortfall is auto-deselected; PCBA qty is a free field; a catalogue part without a fab footprint shows nothing until the paid step — jlc/pcba.
- Browser session expires within hours: the decisive signed-in check is a fresh tab on the orders URL (passport redirect = signed out); reload the quote tab after re-sign-in — jlc/browser.
- Quote form is Vue: `.click()` registers on leaf spans but NEXT needs a real click; "Panel by Customer" REQUIRES the panel format field; branded material lists re-order — click by text, never by position — jlc/browser.
- DFM viewer: rows read "Unanalyzed" until its own button is pressed; "Export analysis report" is an icon-only `li[title]` — jlc/dfm.
- Print service (JLC3DP): DFM is a thin-wall heat map + one yes/no risk gate — compare process rule sets, not colours; FDM refuses parts < 30×30×10 mm; SLA refuses < 2 mm at the Edit dialog, not at upload; a mandatory customs cascader makes Save a silent no-op; pricing is linear in qty — jlc/3dp.
- CNC (JLCCNC): a faceted STL-sewn STEP goes to manual quote; a true B-rep STEP quotes instantly; UV-print finish drops the mandatory drawing upload whenever the finish select changes — jlc/cnc.
- Rebuilding a package folder wipes hand-saved evidence: quotes and captures live under `docs/quotes/<date>/`, never in the package — fab_package rebuild rule.
- Stock gate run-relative for EVERY code (stock 4 for a 5-board run passed "> 0") — audit #3 R6.
- BOM ⊂ CPL is the right assertion (fiducials and owner-supplied parts are CPL-only) — fab_package.
- DNP no longer forces exclude-from-BOM; footprint attributes mirror the symbol 1:1 for schematic parity — CC-067.

## sourcing
- The vendor's own library footprint and its customer drawing disagreed (drill sizes); the drawing governs; the vendor STEP is the only source for a height — D-51/D-53.
- A datasheet note from the `pdftotext` layer must mark curve-only values "not in datasheet text" and attribute figure readings to whoever read them — 2026-09-21.

## mechanical / case
- Coloured marks on vertical FDM flanks cost a filament swap per layer; keep colour on top faces in one Z band per part — D-48.
- A single bottom dovetail is a hinge under torsion; two rail pairs ~17 mm apart give ~2.5× stiffness *(worked example)* — CC-120/123.
- A "part not fitted" yaml flag must also reach the mesh check (the CAD 3D model still carries the solid): flag → `board_stl.ignore` component; "0 components matched = WARN" — mech/case v3.11.
- OpenSCAD/CGAL STL exports are not byte-stable: every md5-stamped consumer runs AFTER the final `--stl` pass — tooling/mesh.
- Batch numbers in generated docs come from the artefact (measured STL volume), not the design intent; write the method next to the number — mech/docs.
- Check-mode census totals differ from full-run totals (mesh rows only with `--stl`): quote the mode with the numbers — case/tooling.
- "Silk-only hop" describes the last commit, not the distance from the mesh's board: check `footprint (at …)` per refdes between the two boards — mech/case.
- A ray-cast thickness census must bucket rays by ENTRY surface (a blind-hole bottom skin masqueraded as a thin floor) — case/census.
- `resize(... auto=true) import(svg)` scales the GLYPH bbox, not the canvas: measure imported artwork from the path — case/generator.
- Print-target presets as `base + overrides` deep-merged before the generator reads anything; drawing and FEA must apply the same merge; a fix for every build belongs in the base block (prove with a key-by-key merged-dict diff) — CC-171, case/presets.
- A thicker snap tab needs the FEA, not the hand formula (slit-root concentration ~1.2×) — case/fea.
- Debug mesh dumps go under `out/**/scratch/` (gitignored), never the repo root; the board mesh is untracked for size, reviewers regenerate it from HEAD and gates assert the provenance sidecar — REPO_CLEANUP K/L.
- The same 126 MB mesh was tracked twice under two paths: md5 every same-size file before untracking — repo/hygiene.
- Generated packages keyed by md5 are safe to drop when every consumer selects by md5, gates are globs, evidence lives outside — repo/hygiene.

## fea
- Gmsh refuses CGAL STLs as volume boundaries; fTetWild meshes them; drop zero-volume slivers or K is singular — CASE_V3_NOTES §18.
- Dropping tets leaves orphan nodes = zero rows in K (SuperLU "exactly singular", NaN): compact nodes (`np.unique(t, return_inverse=True)`) on the cache-load path too — fea/mesh.
- NaN compares False against every threshold, so a failed solve reads OK: `if not isfinite(x): return "FAIL"` first, in the shared helper — fea/status.
- A case can lose its geometry source silently: dry-run each case's input lookups before a long run; re-point at the source of record rather than drop — fea/inputs.
- `--only <subset>` overwrote the whole record: per-label merge + one complete record file per label — fea/records.
- Caches keyed on the board FILE md5 re-solve on a silk-only hop: key on the copper signature + outline/hole digest — CC-159.
- Coupled cases drift with a rebuilt board mesh while board-alone numbers are bit-identical: report both — pcb_fea.

## software
- A fixed jig cap makes the WARN level unreachable when THROTTLE = min(alarm − margin, cap): make the interplay explicit and print both levels — software/thermal.
- Time-driven polls are testable by swapping `time.sleep` for a no-op in `try/finally` and feeding the sensor from an iterator hooked on the exact read shape — software/selftest.
- Identity fields into the record first, gate second — CC-142.

## documentation
- Every mention of a retired string across live docs after a design change: grep, not memory; logs and reviews keep stale words on purpose — docs sweep.
- A NOTES-only schematic regen is cheap to prove harmless: `<nets>` block md5 identical; project file restored from HEAD — docs/silk.
