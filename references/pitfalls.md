# pitfalls.md — every recorded learning, one line each, generalised

Source: the source project's (AEC-CT2-MINI, the worked example) learnings log, 2026-09-21 … 09-28, ~230 entries; 0.3.0 folded the late 09-22, 09-23 and 09-26 entries;
0.4.0 folded 09-27 / 09-28 (the printed-enclosure DFM rounds: D-79 … D-84, CC-204 / CC-205 — the new section *dfm / printed enclosures* and the agents / git and
tooling additions); 0.4.1 folded the late 09-28 entries (the API verdict, the length-dependent metric + probes, the home-preset mirror, the one-piece dummy,
bought-hardware sourcing, CC-206 / B-11). Project-specific numbers are kept only where they make the mechanism concrete and are labelled *(worked example)*. **Evidence pointers (CC-nnn,
D-nn, round names, review file names) name the SOURCE project's records: they are provenance for the maintainer, not files a new project can
open — read the mechanism, ignore the pointer.** The home-printer preset is called `home_fdm` in the skill (the source project's key was its
printer's model name). Grouped by domain.

## dfm / printed enclosures (0.4.0 — `references/dfm-printed-enclosure.md` carries the rules; one line each here)
- A "kept below minimum (listed)" row with verdict None is a waiver nobody signed: it quoted the MALE profile while the female hinge was 0.88 × 141 mm, judged against `feature_min` 0.8 instead of `wall_min` 1.2 — all five MJF trays cracked there — D-83 / CC-205, TRAY_ISSUE.
- Every thin feature gets a measured number from the MESH with span and class (wall / void / wedge); the ray-cast census is a FAIL gate per print preset, never a one-off review aid — CC-205, `thin_wall_census.py`.
- A census that clusters everything below the gate is useless AT the gate (nominal 1.2 walls sample 1.19 and join every region into one 145 mm cluster): cluster below `gate − 0.05`, classify by the opposite-face angle (< 30° wall, else wedge), gate walls only — 2026-09-28 [dfm/census].
- The vendor's heat map colours VOIDS too (every 0.45 glyph red, 0.5 slot ends red, a 0.5 boss-to-wall gap yellow): cast the rays both ways; engraved text on an MJF body under a no-yellow bar needs a stroke ≥ the void gate (cap ≥ ~6 mm at 1.2) — else a label carrier — 2026-09-28 [dfm/mjf/heat-map].
- FREE-STANDING wedges are RED (36° rail tips and lips full length, a non-tangent interior 45° roof cove on every wall); chamfers, ramps and TANGENT fillets cut INTO a ≥ gate wall stay grey — no free thin edges on an MJF body; fillets at stress risers are fine — 2026-09-28 [dfm/mjf/vendor-map], JLC_RULES 3D.
- Design every gated wall 0.1 over the vendor's threshold (1.3 for a 1.2 grey line): a 1.2 nominal samples 1.19 and prints 1.1 … 1.3; the argument is lost at the map — 2026-09-28 [dfm/margin].
- A vendor heat map yellow "full length" along a feature is a strength finding: an owner decision row with the number ("may crack; accept?") or a fix — "kept (design geometry)" is how the order went out — CC-171 → D-83.
- When the print rule changes (FDM two lines → MJF 1.2), re-derive EVERY yaml value set against the old rule; a `>= 0.8` yaml comment beside a 0.9 wall is the tell (rail skin 0.90, cheeks 1.0, hole floors 1.0, a mark debossed 0.8 into a 1.2 band) — 2026-09-28 [dfm/mjf].
- A feature that cannot be vendor-clean inside its space budget goes, it is not thinned (a 1.2-flat dovetail needs 2.4 of depth in a 2.15 groove → rail off, screws); a Ø8 boss 4 mm from a wall leaves a 0.5 void (web it) — 2026-09-28 [dfm/mjf/features].
- Thickening one wall moves its neighbours (skirt 1.3 → snap-tab 6.1 N → deflection fix → catch minimum broken → tab width carried it): every wall change reruns the whole table — 2026-09-28 [generator/coupled-knobs].
- Snap tabs and detents died under a no-yellow bar at JLC3DP, not from PA12 physics: the 0.6 slit is a sub-gate void (red) and a rigid 1.1 bump on a 0.5-slit tab does not deflect (F ∝ t³); PA12 snaps fine with a ≥ void-gate slit and an engineered arm — otherwise screws into inserts or magnets — CC-204 / CC-205 (g).
- Closed rims: a coupling groove open along a wall, a lead-in notch at a sill, a key notch at a skirt edge, a snap-tab slit all read as "literal gaps … a broken design" in the vendor's viewer; only openings with an obvious job may show — 2026-09-28 [dfm/closed-rim].
- Designed asymmetries that look like defects (1.0 mm inboard foot pockets beside concentric counterbores) must be RENDERED and printed in the order sheet + KNOWN_ISSUES §1 — a yaml note, a passing row and a guide sentence did not stop "holes not concentric"; render every face incl. the sole — 2026-09-28 [ux/review].
- A `+ 0.01` extrude overshoot is a 0.01 mm slab in the mesh and a RED line on the map: trim the union at the design face, never exempt "seam slabs" in a check — 2026-09-28 [generator/overshoot].
- "0 FAIL, 81 WARN" tells the owner nothing: a row with a threshold is PASS / FAIL on a measured value, a row without one is INFO in its own table; `None` must never render as WARN — the split exposed a dummy sitting 0.4 low that no WARN had shown — 2026-09-28 [process/warnings], [process/rows].
- A census that passes on paper is not a print: the FDM preset had 0 FAIL and failed as a product (0.85 two-line walls, 0.45 debossed strokes at cap 2.2, supports on visible faces, 3 bosses under a 4-hole fan, a rigid detent) — printer-first FAIL rows: external faces on the bed / vertical / clean top, walls ≥ 1.6, legends raised cap 4 / stroke 1.0 / 0.6 — D-79 / CC-204.
- Raised text cannot print face-down (the plate bridges over the glyphs); a hood roof recess printed roof-down is a ceiling (drop it, the fan locates on its screws); consumer 30 mm fans have 4 holes even when one SKU drawing shows 3 — 2026-09-27 [case/FDM design rules].
- Any point set drawn in two places (SCAD `for` over four corners vs a Python 3-point list) diverges — pass it to the SCAD as ONE vector; a `#` inside a one-line YAML flow mapping comments out the rest of the mapping — 2026-09-28 [generator/hooks].
- Print 15–25 min test coupons BEFORE the part, generated from the SAME yaml numbers and SCAD modules; make what they decide a yaml parameter block so the answer is a 3-number edit; list what the generator DROPPED at the current numbers — 2026-09-27 [process/coupon-first].
- Never hand a raw CAD mesh to a printer (0.25 mm sheet metal, 0402s, 0.1 mm pins wrecked the print): a generated dummy — slab + holes + envelopes + fins at printable thickness — in the same frame, bbox stated against the mesh of record — 2026-09-27 [process/handover].
- Compensating a locating pocket with a plinth lifts the mating part's overhang off the bed (a floating-region warning on a piece that had sliced clean): a scribed ring outside the footprint locates it; a break-away shim (1.2 block, 1.2 × 1.2 posts across a 0.4 gap) carries a nose overhang on a one-piece dummy — 2026-09-28 [fdm/home-preset/board-dummy].
- A slicer project naming a SYSTEM preset with an empty `different_settings_to_system` is reconciled back to system values when the GUI opens it (supports OFF → "floating regions"; the CLI slice was clean): project-specific preset name + the differing keys listed; File → Open Project, never Import — 2026-09-28 [bambu/3mf].
- Slicer CLI facts *(worked example, Bambu Studio 02.08)*: `--export-3mf <bare name>` into `--outputdir` (an absolute path fails), `--slice 0` headless; system profiles must be FLATTENED (`inherits`) before `--load-settings`; PETG needs the textured-plate `curr_bed_type`; a 36° overhang triggers the floating-region warning at the 30° threshold — 2026-09-27 [tooling/bambu].
- A variant print target in a generator whose default output is md5-keyed: variant-only lines behind hook tokens that expand to the ORIGINAL text for the other presets, own version key per preset (a `case.version` bump alone re-keys every cached STL of record); prove `scad() == git show HEAD:<scad>` — 2026-09-27 [generator/byte-identity].
- A plate the owner must rotate by hand is a generator defect: auto-orient every non-text piece (score face-down choices by down-facing area above the bed, then bed contact; bake it into the STL); a floating-region warning is a build FAIL with no exception left at release — D-82.
- Two-piece AND one-piece board dummies at FINAL dimensions, coupons in every kit, ONE kit folder (a moved folder keeps a `README_MOVED.md`) — D-84.
- OpenSCAD 2021.01 writes the same CGAL geometry in a different triangle order on every export (three exports = three md5s), and trimesh's STL exporter writes run-dependent NORMALS for identical vertices: an STL md5 identifies a geometry only after a canonical rewrite with your OWN binary writer (sorted triangles, normals from the float32 vertices), proven idempotent AND equal on a copy from another run — 2026-09-28 [tooling/openscad], [tooling/stl].
- A vendor heat-map verdict is evidence only with the uploaded file's md5 AND the API's `parseStatus 2` / `thinWall` for that upload (the material on the line sets price and legend, not the flag); when a verdict flips, confirm both reads were API reads, then diff the meshes before touching the generator (the red r3 tray WAS the grey r2 tray — a premature DOM read) — 2026-09-28 [dfm/vendor-map].
- Upload ONE STL per quote-page session and reload between uploads: with several lines present the page opened the wrong file's analysis twice — 2026-09-28 [dfm/mjf/vendor-map].
- The vendor's quote-page verdict is valid only from the analysis API at `parseStatus == 2` (`getFileAnalyzeResult` → `modelAnalysisVO.thinWall`, read in the network log or re-requested); every DOM "no flag" read before that was premature — two PASS rows were, and the API said TRUE on the same file — 2026-09-28 [dfm/vendor-map].
- The thin-wall flag is computed at UPLOAD and does not depend on the material chosen on the line afterwards; set the order's material anyway (price, map legend) and never explain a flipped verdict by the material — 2026-09-28 [dfm/vendor-map].
- `modelAnalysisVO.previewUrl` opens the heat-map viewer (Analysis Results tab) directly even when `thinWall` is false; the hidden `input[type=file]` can be unhidden by script; uploads and analysis work signed out — the DFM read needs no login, ordering does — 2026-09-23 / 09-28 [jlc/3dp].
- The vendor's thin-wall metric is LENGTH-DEPENDENT: an identical rim-over-lap-step profile passed at 48 mm and failed at 88 and 147 mm while three ray-cast censuses (up to 400 k samples) found nothing under 1.37 — a wall that passes on a coupon can fail on the part; a 40 mm probe proves nothing about a 147 mm body — 2026-09-28 [dfm/vendor-map], PROBES.md.
- Calibrated MJF PA12 rule at ~150 mm: a rim above a skirt-lap step ≥ 2.0 (1.4 fails; 2.0 passes with step + inward undercut kept) OR the undercut filled so the inner wall runs straight to the rim top (`lap.ring_down`, then 1.25 … 1.3 above the step passed); plain 2.0 walls / floors, boss rings, chamfers into ≥ 1.2 walls, 45° dish ramps grey; free-standing wedges red — 2026-09-28 [dfm/geometry].
- Probe method that converges in one round: slice the failing body of record into capped slabs (`trimesh slice_mesh_plane`) to localise + find the length threshold, then plain-profile OpenSCAD polygon extrusions at 40 mm AND full length with ONE knob each (`-D`), each uploaded alone, API-read, tabulated in `PROBES.md`; a 0.6 × scaled body is not informative — 2026-09-28 [dfm/probes].
- Opposing faces that never overlap (a ledge underside 0.5 from a step top, a ring face 0.4 from a wall plane, a rim ring's 0.4 root) are invisible to a normal-direction ray census and visible to the vendor; `thin_wall_census.py` gates the nearest opposing face in ANY direction (exact point-to-face distance over KD-tree sample pairs) — 2026-09-28 [dfm/geometry].
- Every vendor DFM decision (rails off, key off, closed rim, undercut filled, feet concentric, hood on screws) is mirrored into the home-printer preset (`home_fdm`) the same day, in the same yaml, under its own version key with the deciding round in the comment; its census (1.6 / 1.2 / 1.0) and the slicer log must be clean; the kit folder regenerates — D-83 addendum / CC-205.
- One-piece board dummy (D-84): cage fused to the slab at final dimensions, the nose overhang on a break-away shim (1.2 block on the bed, inset 0.5 from the nose sides, 0.6 clear of the board edge, 8 posts 1.2 × 1.2 across a 0.4 two-layer gap); the README says the shim looks like a "PCB lip" and comes off — the owner read it as the board; prove one-piece = two-piece by section symmetric difference 0 mm² and both bboxes against the cage envelope of record; keep both versions — D-84.
- A vendor-only geometry change (a fill that MJF needed) is a divergence between two mating presets: prove partner overlap 0 mm³ after it, or mirror it — CC-205 r5.
- A coordinator's "no flag" decision row built on a subagent's relayed claim was wrong twice: re-read the API for the md5 in the record before writing PASS — 2026-09-28 [agents/verify].
- Post-mortem of a cracked part: measure the ORDERED STL (sections + census), separate design intent from defect (the vendor's "designed gap" was right AND the crack beside it was ours), draft the accept-and-ship reply with the number, apply the learning design-wide — TRAY_ISSUE_D2026092246500217, D-83.
- A cluster-based census hides findings under a false class: one cluster chained across the body through chamfer flanks read "wedge" and swallowed a 1.0 … 1.2 lip and 1.3 slot lands; cluster wall-class and wedge-class samples SEPARATELY, never classify a mixed cluster — retro 2026-09-28 [dfm/census].
- A rim ring set inboard of its wall stands on a root the width of the overlap however thick ring and wall are (1.3 × 0.4 root, invisible to normal rays — the construction that cracked the earlier lip): the opposing-face metric measures it; a check row that read the yaml passed a hood whose STL carried no bosses — every row measures the MESH — retro 2026-09-28 [dfm/geometry], [records].
- PyYAML keeps the LAST of two duplicate keys silently (`body_rail: {enabled: false}` then `body_rail: {land: …}` re-enabled a rail every document said was off): a duplicate-aware SafeLoader gates every design yaml — retro 2026-09-28 [tooling/yaml].
- `mirror([0,0,1])` puts a roof on the bed and flips handedness (every asymmetric mark printed backwards): `rotate([180,0,0])`, then a proper-vs-improper rigid-match row against the board-frame mesh — retro 2026-09-28 [fdm/export].
- A SCAD hook naming a variable the preset never defines expands to NOTHING (a hood shipped a day without counterbores): assert every hook variable per preset; a generator that keeps the OLD artefact on a failed run leaves every later analysis reading the old file — check the md5 the sidecar names first — retro 2026-09-28 [tooling/openscad], [tooling/slicer].
- "No support on a visible face" is asserted from the g-code in the 3MF (`; FEATURE: Support` outside the outer-wall hull), not from the mesh's intent — retro 2026-09-28 [fdm/slicer].
- Hobby magnet sizes (Ø6 × 3, Ø4 × 2) come only in 80 °C grades from login-free vendors; a debossed polarity dot beside a pocket leaves sub-gate lands — key polarity by an asymmetric boss — retro 2026-09-28 [parts/magnets], [dfm/mjf/polarity].
- Two owner rules colliding in one feature (lip inset ≥ 0.6 vs web inset ≤ 0.45) are resolved by honest classification (a plate's webs are ribs), never by a thinner wall under a friendlier name — retro 2026-09-28 [fdm/design].
- A FEA record that merges the previous results of the same label keeps stale rows for cases the design no longer has (snap tab of a screwed hood): a skip must pop the entry; the completeness test counts only applicable cases — 2026-09-28 [fea/records].
- `.gitignore` has no inline comments (`out/x/   # note` ignores a path ending in the comment); zsh aborts a whole `git add a b c/*.json` when one glob has no match — 2026-09-28 [tooling/git].

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
- The morning after an order the live stock gate turns against its own package (the shelf shows what the order consumed): a PLACED order is judged on stock records frozen at the build, hashed in the manifest; the selftest runs on a stock fixture, never the live file — D-74 follow-up, `fab-dfm.md` §8.
- A vendor's post-order review is a review round with a wall: file the mail + images, map every flag on the STLs of record, decide per line in the log, fix through the generator, re-run the vendor's DFM before uploading, Replace File only on the owner's word — D-74/D-75, `vendor-review.md`.
- "Order Dxxx audit failed — please replace files" is the vendor's wording for *Replace File enabled*; the approvals follow minutes after the upload — ORDER_STATUS 2026-09-24.
- A one-geometry-change case bump costs ≈ 45 min machine time (every STL md5 moves → every FEA mesh rebuilds): four background jobs, block on EXIT lines — 2026-09-23, `case-pipeline.md`.
- An 'order prep' hand-over that stops one click before the cart: agent records every field / upload / dialog / price with screenshots; the owner reads deviations; the account never sees an agent-side purchase — 2026-09-22.
- Re-layout at the order: decision row → `reorg:` table → `git mv` + literal rewrite → regenerate embedders → `--check` 0 → `--proof` on two `git ls-files -s` dumps (blob identity, not presence) — D-70/D-72/D-73, `reorg_paths.py`.
- A removal census separates LIVE citations (gen/, design/, CI, live docs) from RECORD citations (DECISIONS / STATUS / merged reviews); grep basenames AND exact paths (basenames over-report across generations) — D-70 phase 1: 368 candidates, 4 real.
- A traceability `exists` check on a file that leaves the tree becomes `git show <tag>:<path> | grep -qF '<same string>'` — nothing weakened — D-73.
- A DELETE-NOW item deleted once is not gone when a generator re-dumps it: guard in the generator or an ignore line, not `rm` — CC-151 follow-up.
- The tag commit's hash cannot be written into a file the commit contains: "the commit holding this row" + `git describe --tags` — CC-185/186.
- Whoever appends a DECISIONS row runs the record round; a records-only commit without the regen chain is unfinished (`adopt_gates` stops at traceability) — 2026-09-22 [process/concurrency].

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
- A four-hour agent tree (twelve full case rebuilds) sat uncommitted until a `WIP … not yet gated` checkpoint: commit after every meaningful step, gated or not, and say "not yet gated" in the message — source commit 19a7f7f0 → c4db982b, 2026-09-28.
- A subagent has a turn limit (~200 turns for a fork) and a worker fork may not spawn agents: everything not in HEAD when it stops is gone — checkpoint commits inside the task, resume from HEAD with measured state, blind reviews handed back to the coordinator — CASE_MJF_DFM_v3.16 §6.
- A tag created on a checkpoint before the final gated commit must be re-pointed to the gated commit (`git tag -f`) and the record must say so — production-cut.10, 2026-09-28.
- The DevTools-driven browser can be restarted or re-used by another agent between turns: page ids, tabs and the signed-in state vanish — re-list pages, re-derive the id and re-check sign-in before every upload / read — 2026-09-28 [agents/browser].
- First Linux CI run of a macOS-authored gate set = twelve parity fixes: `$GITHUB_ENV` takes KEY=value only, no `make` in the CAD image, shim every hard-coded path, `git config safe.directory`, pin EVERY lazily imported package (one failure per push), install the renderer where a check renders, a proprietary font cannot ship (count font-aware, exclude silk-text items cross-host), gitignored inputs absent = NOTE; reproduce with `docker run --platform linux/amd64 <the CI image>` first (3 min vs 8–10 per push) — 2026-09-27 [process/ci].
- A history rewrite (filter-repo) must remap every hash a TOOL uses functionally (replay defaults, freeze-stock build commits), not only record hashes: commit the old→new map and resolve through it; push tags oldest-first (GitHub's 2 GB pack limit) — 2026-09-27 [process/git].

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
- A `--check` that builds in a temp dir but EXPORTS into the tree is a write: it replaced the ERC of record (0/0) with a temp copy's 58 lib-link warnings; every checker must be provably read-only (`git status --porcelain` before/after in `adopt_gates.sh`, last PR-check step) — CC-198.
- A script without argparse runs its default WRITE action when probed with `--help` (four artefacts + 13 PDFs regenerated mid-task): read the docstring with `sed -n 1,12p`, never run to ask — 2026-09-22 [tooling/cli].
- The one-round record chain is an ORDER: renders → reports → matrix → reports → analysis index → PDFs → cut build LAST → commit; a regen after the build makes the cut STALE on content-identical reports; judge the fixed point after stripping the volatile cascade (Generated → md5 → every stamp → tool commit) and discard round two — `release-and-cut.md` §3.1.
- Registering a new deliverable flips a manifest status the analysis index reads: that round is two passes by construction — 2026-09-22 [tooling/manifest].
- A collector reusing an up-to-date copy must recompute its GRADE (15 captures read OK against a newer case for a day); a generator sweeping "everything not in my index" from a shared folder deletes a sibling's output — register foreign files with their own check — 2026-09-22 [process/generator].
- `kicad-cli sch export pdf` orders pages by sheet uuid, not sheet number; read the page ↔ sheet map from the PDF outline (nested under the root entry); the PDF carries a CreationDate — key the export on the SOURCE md5s — CC-194.
- An idempotent per-output key must include the drawing-code version, not only input md5s (slides kept after the layout fix) — 2026-09-22 [process/generator].
- A one-word fix in generated text reachable only through the whole `--stl` chain rewrites the census, the non-byte-stable exports and the sidecar: keep the target, `git checkout` the rest, say so; the durable fix is a single-artefact flag — 2026-09-22 [tooling/regen].
- Profile before parallelising: 25.1 of 25.8 s was a selftest SLEEPING in timing tests; `real` vs `user` first — a gap is a sleep or a wait — CC-172.
- A serial check set carries invisible invariants (two rows writing the same scratch file): grep shared outputs before pooling, lock per output path, validate the pooled result against the serial one on the real data — 2026-09-22 [tooling/pool].
- A key on the generator's md5 invalidates every cache on a doc-only edit: key OpenSCAD outputs on the generated SCAD text + imported files + argument list — 2026-09-22 [tooling/cache].
- A `__main__` script also imported by name has TWO module instances: a `global` set in one is invisible in the other — 2026-09-22 [tooling/python].
- Two agents committing the same generator: commit only your hunk (`git show HEAD:file` + your edit → `hash-object` → `update-index`) — 2026-09-22 [process/concurrency].

## kicad / drc / swig *(worked examples; the mechanism generalises to any CAD CLI)*
- `kicad-cli pcb drc` honours ONLY explicit `netclass_assignments`, never `netclass_patterns`, and NO DRC exclusions: emit per-net assignments from the generator, assert a canary rule fires exactly once; accepted residue = a generated RULE (`enclosedByArea`, not `insideArea` which is an intersection test — prove with a negative construction in `--selftest`) — audit #4 G01, CC-148.
- Enforcing net classes for the first time on a "DRC 0" board showed 202 errors; a class clearance larger than the fill's zone clearance is unenforceable by construction: write the as-built geometry into scoped rules general → specific (later rule wins), log the relaxation — round 6k.
- `pcbnew.LoadBoard()` reports netclass Default for every net: resolve class patterns yourself and selftest with a Power net carrying one thin segment — audit #3 P02.
- A standalone schematic regeneration rewrites the `.kicad_pro` to the skeleton (rules, classes gone): restore from HEAD or make the writer leave it alone; "netlist unchanged" = md5 of the `<nets>` block, not the file — kicad/gen.
- `kicad-cli pcb render`: `--pivot` is in cm from the board centre; the `--floor` shadow survives in the alpha of a transparent render (dark variant = same render on a gradient); an unquoted zsh `$OPTS` passes every flag as ONE argument — marketing pack CC-192.
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
- McMaster-Carr is login-walled for automation (JS shell + "please log in" in a real Chromium); Digi-Key (Cloudflare), Mouser, Newark, Farnell, RS, Keystone, Essentra block fetches: verify bought hardware on the manufacturer's site + PDF TDS + plain-HTML dealers, tag snippet-only prices [K], BLOCKERS row with the exact URL + filters for the owner to open logged in, never invent a number — CC-206 / B-11.
- Feet over screws: a Ø8 foot in a Ø8.5 pocket whose floor is opened by a Ø6.3 counterbore bonds on a 0.85 mm ring (38 % of its adhesive) — flat-top cylinders over hemispheres there, and the ±0.5 mm moulding tolerance eats a 0.5 mm pocket margin at worst case — 2026-09-28 [mechanical/feet].
- A parts task catches count drift (yaml five feet, guide / order sheet / other preset four): flag the disagreement in the decision row, never pick one silently — 2026-09-28 [records].
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
- A potrace outline of touching shapes pinches to 0.003–0.03 mm at the contacts: an extruded plate is lobes held by hairlines (fab "B 0.01"); a ridge "thinnest arm" census cannot see it — test the section polygon for non-adjacent vertices < 0.05 mm apart (`thin_wall_check.py --pinch`) before the outline becomes a body or pocket — D-74/CC-196.
- Bridge a point contact with a disc INTERSECTED with the outline's closing (offset +R, −R; R ≈ 3 × web), never a bare disc (a 0.4 mm nub on the silhouette) — CC-197.
- trimesh `section().to_2D()` re-origins the plane (a 6.9 / 4.6 mm translation): map the Path2D back through the returned to-3D transform; the `connected components = 1` row caught the 7 mm mis-placed disc — 2026-09-23 [mesh/geometry].
- Inward ray-cast census: a ray nudged 1e-3 inside a face hits that face at 0.000 for some samples — discard hits < 0.02 mm, take the first beyond (`--self-hit`) or solid chamfers read "0.00 mm" — 2026-09-22 [mesh/dfm].
- An STL md5 is not a geometry signature (CGAL export order): prove "only piece X changed" by facets / volume / area / bbox per piece — 2026-09-22 [case/stl].
- Legends on a lid read in ONE direction: every camera that shows the lid sits on that side, or the guide's pictures read upside down — CC-192/CC-199.
- A CAD GLB export is thousands of face groups per footprint, not solids: a "component inside a box" rule written for STL connected components swallows connector pins and heat-sink skin — rebuild the solid first (merge the family's groups, `merge_vertices`, split by face adjacency), then apply the box rule — CC-203, 2026-09-27 [mesh/glb].
- Vertex colours bleed across shared vertices (a 0.02 mm proud purple artwork painted the whole plate top): unshare the vertices (one per face corner) before per-face colour on a baked mesh — 2026-09-27 [viewer/colours].
- OpenSCAD 2021.01 PNG export costs the same ≈ 8 s at 3840 × 2880 as at 1600 × 1200 (CGAL bound); colour schemes only move the background; user schemes load only from the config dir — CC-192.
- The vendor's engineer review mail has no attachments: the marked-up heat maps are `<img>` links fetchable without login; hood-local Z = body Z − split plane; it asks "risk acceptable?" per material (nylon ≥ 1.0, resin ≥ 0.8) and opens Replace File only after a reply — 2026-09-22 [jlc/3dp].

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
- Manuals written before the software they describe: the "what you should see" lines go under an explicit banner naming the fake backend that produced them — 2026-09-22 [documentation].
- Time-driven polls are testable by swapping `time.sleep` for a no-op in `try/finally` and feeding the sensor from an iterator hooked on the exact read shape — software/selftest.
- Identity fields into the record first, gate second — CC-142.

## documentation
- Every mention of a retired string across live docs after a design change: grep, not memory; logs and reviews keep stale words on purpose — docs sweep.
- A NOTES-only schematic regen is cheap to prove harmless: `<nets>` block md5 identical; project file restored from HEAD — docs/silk.
- An illustrated assembly guide is generated, not drawn: authored short yaml + the SOP generator's step text + one keyed render per page; numbers stay in the SOP (one source) — D-76/CC-199.
- A hand-written SOP that copies a generated seed inherits the seed's stale number three revisions later: cite the seed's file + md5, or generate the block — 2026-09-22 [docs/seeds].
- "Software of record = `git log -1 -- tools/`" moves the stamp in seven documents on a README fix: stamp the md5 of the files that matter — 2026-09-22 [docs/provenance].
- Markdown → PDF for a document set with wide tables and Ω / ≤ / ✓: a headless browser + CSS beat the installed TeX; `overflow-wrap: anywhere` breaks part numbers mid-word — 2026-09-22 [tooling/pdf].
- The JLC / LCSC part-page JSON carries RoHS (`isRohsCert` + certificate URLs) and MSL fields: a compliance table is fetched at cut time from those, no declaration claimed — 2026-09-22 [parts/compliance].
