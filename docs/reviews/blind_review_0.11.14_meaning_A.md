<!-- blind meaning reviewer A: Claude Opus (Agent tool); the 0.11.13 -> 0.11.14 prose diff only; 2026-10-08 -->
# Meaning review, skill 0.11.13 → 0.11.14 (blind, diff only)

| file | hunk (first words of removed text) | verdict | before → after |
|---|---|---|---|
| README.md | "A Claude Code skill that takes a board…" (@@ -1) | SAME | (version line ignored) |
| README.md | "vendors' verdicts (a vendor flag we pass…" (@@ -41) | SAME | |
| README.md | "## Use in a new project" / "4. Copy the templates…" (@@ -104) | CHANGED | Heading moved below the step-3 selftest note, and a new paragraph added: (none) → "Run the kickoff questionnaire first (`SKILL.md` §0.1, `references/kickoff-questionnaire.md`). Its A0 answer sets the scope of the copy block in step 4. Write the other answers into the records after the copy." (new sequencing instruction: kickoff before the copy). Also "`project.py slots` counts the unfilled slots per file — CLAUDE.md / project.yaml / records now, SPEC + KICKOFF_ANSWERS after…" (describes what the count covers) → "Fill CLAUDE.md / project.yaml / records now, and SPEC + KICKOFF_ANSWERS after…" (an instruction). |
| README.md | "5. Follow `SKILL.md` §0: the kickoff questionnaire, ENV record…" / gen/ sentence / fast iterations (@@ -134) | CHANGED | "Follow `SKILL.md` §0: the kickoff questionnaire, ENV record …" → "Follow `SKILL.md` §0 from step 3: project.yaml, ENV record …". The kickoff leaves step 5's list, project.yaml joins it, and a start point ("from step 3") is added: a sequence change that matches the @@ -104 move. The gen/ sentence and the fast-iterations paragraph are SAME. |
| README.md | "Before the spec is read, the agent asks the scope (A0), then…" / retro loop (@@ -154) | SAME | "deleted once folded: the repo carries no project retro" → "deleted once folded, because the repo carries no project retro" (the colon already read as the reason). |
| SKILL.md | version line (@@ -1) | SAME | ignored (version) |
| SKILL.md | "vendor/hw-from-spec/scripts` (or a copy…" §0 steps 1–8, §0.1, §1 mech chain (@@ -15) | SAME | All steps, order (slots → known_issues → traceability → release_report → now_pages → commit → adopt_gates → kickoff --check), scopes and conditions preserved. Mech chain restructured into G0 / M1 / M2 "covers" sentences with every item kept. |
| SKILL.md | "Release row's approval cell) are owner text. … One review round…" (@@ -113) | SAME | "(or the in-session fallback, said so in the merge)" → "The in-session fallback may stand in for the external models, and the merge says so." |
| SKILL.md | "1. Prerequisites first…" §1.1 + §1.2 bar (@@ -141) | INTENDED (who enforces what) | "enforced by the scripts, never by prose" → "enforced by a named check, never by prose" + new "**Who enforces each item:** the skill's scripts enforce ERC, the fab DFM mirror, the census and print DFM; `kicad-cli pcb drc` enforces DRC. The project's slicer wrapper enforces zero slicer warnings. No skill script reads the vendor API flag or the heat map. The owner reads both at the case-order gate … counted by `scripts/heatmap_count.py`." Rest of hunk SAME. |
| SKILL.md | "table (commit, step, file md5, content signature); assert…" (@@ -177) | SAME | |
| SKILL.md | "Tags: **[V]** verified live this session…" (@@ -217) | SAME | |
| SKILL.md | "3. Reviewers (the review round of §1)…" (@@ -241) | SAME | |
| SKILL.md | "**The `case_dfm` role** [mech, both] (in the `board` role set…" (@@ -261) | SAME | |
| SKILL.md | "`references/pcb-layout-dfm.md`. A routed board is adopted only when…" (@@ -287) | SAME | "(prove it with a canary rule — … — the CLI may ignore class patterns)" → "…, because the CLI may ignore class patterns" (dash aside read as reason; kept) |
| SKILL.md | "against the board mesh of record (provenance sidecar…" §8, §8.1, §9, §10 (@@ -305) | INTENDED (who enforces what; tg_c → hdt_c rating) | "the census gates the DESIGN margin" → "the census gates `wall_gate` (the checker's line) … No script reads `design_margin`: the case generator draws walls at `wall_gate + design_margin`, and the owner's heat-map read checks it". "material rating (UL 94 / Tg)" → "(UL 94 / HDT)". Everything else in the hunk SAME. |
| SKILL.md | "hole-calibrated pad-1 overlay before the owner submits; its deltas…" (@@ -434) | SAME | `design_margin` ≥ 0.3 unchanged in both. |
| SKILL.md | "After every production cut … `scripts/skill_retro.py`…" (@@ -503) | SAME | |
| references/agent-ops.md | "One coordinator; workers own disjoint FILES (board agent: `kicad/`…" (@@ -1) | INTENDED (path remap) | `kicad/`, `design/<board>_*.yaml`, `out/**/case/` → `30-board/kicad/`, `20-design/<board>_*.yaml`, `40-case/` |
| references/agent-ops.md | "**A fork subagent stops at ~200 turns.**…" / worktree / tags (@@ -23) | SAME | |
| references/agent-ops.md | "Every checker is READ-ONLY on the tree…" §3–§5 (@@ -39) | CHANGED (plus INTENDED path remap) | Path `erc.json` into `out/` → into `30-board/layout/` (INTENDED). Print-kit pairing: "…measures the meshes …; merged; fixed by ONE author agent…" (no actor for the merge) → "The coordinator merged both reports. ONE author agent fixed the findings…" (actor added). Rest SAME. |
| references/agent-ops.md | "**The DevTools-driven browser is its own profile**…" §6–§8 (@@ -111) | SAME | All pool numbers (cores // 4, max(2 GB, 15 %), load1 > cores, exit 2), engine rule and item 9 criterion preserved. |
| references/agent-ops.md | "Measured serially in a detached worktree replica…" worked example (@@ -206) | SAME | |
| references/case-pipeline.md | "The chain of record assumes every body is generated…" §0 (@@ -3) | SAME | |
| references/case-pipeline.md | "A set is one folder per PRINT TARGET…" + board mesh (@@ -25) | SAME | |
| references/case-pipeline.md | "FDM (owner's printer, target `home_fdm`)…" (@@ -58) | SAME | 1.2 line, Z-band, legend numbers kept. |
| references/case-pipeline.md | "Inward ray-cast rule…" / census / point contacts (@@ -80) | SAME | |
| references/case-pipeline.md | "≈ 45 min. Run case FEA, PCB FEA…" (@@ -111) | SAME | |
| references/case-pipeline.md | "**Fit rows per degree of freedom, not per part.**…" / assembly model (@@ -124) | SAME | |
| references/case-pipeline.md | "The feature directions come from the geometry of record…" / stability (@@ -176) | SAME | |
| references/case-pipeline.md | "The render + STL + interference chain…" process rules (@@ -215) | INTENDED (path remap; tg_c → hdt_c rating) | `gen/ + design/` → `gen/ + 20-design/`; `out/**/scratch/` → `build/**/_check/`; "UL 94 / Tg" → "UL 94 / HDT". Rest SAME. |
| references/cnc-enclosure.md | "Short by design: the one quote behind it…" / geometry rules (@@ -1) | SAME | |
| references/cnc-enclosure.md | "The vendor's DFM clean (no manual-quote fallback…" (@@ -34) | SAME | |
| references/dfm-printed-enclosure.md | "**Every number here carries a tag** — the same four…" / §0 bar / §1 three numbers (@@ -6) | INTENDED (design margin 0.1 → 0.3) | "the 0.1 margin costs nothing on a 2 mm shell" → "the 0.3 margin costs little on a 2 mm shell". Tag list, §0 bar and the three-sources bullet SAME. |
| references/dfm-printed-enclosure.md | "**No FREE-STANDING wedge** **[checker]**: the map colours RED…" (@@ -33) | SAME | |
| references/dfm-printed-enclosure.md | "must exist in the exported mesh…" / §1.2 / §1.3 (@@ -79) | INTENDED (tg_c → hdt_c rating) | "**UL 94 rating and Tg / softening point** (PA12 MJF: typically HB; …)" → "**UL 94 rating and HDT at 0.45 MPa** (the `hdt_c` key). PA12 MJF: typically HB, HDT ~175 °C **[K]**, Tg ~50 °C **[physics]**." The two PA12 values are new facts carried by the fix. Note: §1.2 still says "a `wall_gate + 0.1` wall" (unchanged, both sides). |
| references/dfm-printed-enclosure.md | "the part has no ONE-SIDED feature: integral pegs…" §1.5 (@@ -100) | SAME | |
| references/dfm-printed-enclosure.md | "The census gates the DESIGN margin per `print_targets.<t>`…" §2 (@@ -115) | CHANGED (plus INTENDED who-enforces) | INTENDED: "The census gates the DESIGN margin" → "The census gates `wall_gate` … No script reads `design_margin`. The case generator draws walls at `wall_gate + design_margin`, and the owner's six-view heat-map read checks the result". CHANGED (not on the fix list): new rule added, (none) → "**The band is an axis-aligned measure**: the census takes the second-largest extent of the cluster's axis-aligned bounding box. It is valid only for a straight edge that runs along X, Y or Z … reads 1.0 along X and 28.28 at 45° … A ring around a hole reads its diameter … Re-measure a diagonal or ring wedge FAIL across the edge before you accept or fix it." Also added to the `--gate-dir` bullet: (none) → "It re-matches every accepted FAIL by class and bbox (1 mm tolerance) against the current yaml." (new fact for this bullet; consistent with SKILL §1.2 "re-matched against the yaml every run"). |
| references/dfm-printed-enclosure.md | "3. **The flag is computed at UPLOAD**…" §7 steps 3–5, §7.1, §7.2, §8 (@@ -188) | INTENDED (heat-map colour read) | Step 4 adds "It reads each pixel in HSV, so shaded faces and amber count too." Rest SAME (worked example 1.4 fails / 2.0 passes kept). |
| references/dfm-printed-enclosure.md | "**Colour bodies are their own print target**…" + coupons, board dummy, §8.1 (@@ -282) | INTENDED (colour wall gate 0.6 → 0.4) | "The wall gate is the body's THICKNESS (0.6 = 3 layers)" → "The wall gate is the body's THICKNESS: colour layers × layer height (default 2 × 0.20 = 0.4, §8.1; 3 layers = 0.6)". Coupons, coupon labels (always debossed), board dummy, slicer, kit handover, §8.1 NEVER list SAME. |
| references/dfm-printed-enclosure.md | "**Print MOUTH DOWN**…" §8.2 (@@ -392) | SAME | |
| references/dfm-printed-enclosure.md | "unless every filament profile carries `filament_colour`…" (@@ -407) | SAME | |
| references/dfm-printed-enclosure.md | "(`ConfigBase::load_from_json`) throws…" / §8.4 / §8.5 / §9 (@@ -438) | SAME | |
| references/dfm-printed-enclosure.md | "4. **Reply template**…" §10–§13 (@@ -536) | SAME | `design_margin` ≥ 0.3 unchanged. |
| references/fab-dfm.md | "CAD DRC at the fab's published capability limit passes…" (@@ -1) | SAME | |
| references/fab-dfm.md | "4. **Acceptances** by refdes…" (@@ -27) | SAME | |
| references/fab-dfm.md | "Pre-empt the questions the desk always asks…" / holes in a remark (@@ -62) | SAME | |
| references/fab-dfm.md | "is the **checker's** colouring…" §6 / §7 / §8 (@@ -79) | SAME | |
| references/fab-dfm.md | "A PCBA fab's engineer asks the same questions…" §9 (@@ -111) | SAME | |
| references/fdm-print-optimisation.md | "**The rule.** Every knob used is set in the plate yaml…" (@@ -4) | SAME | |
| references/fea-stage.md | "Gmsh (Python API; boxes…" stack + recipe 2–6 (@@ -1) | SAME | Group labels "Meshing:" / "Solver and tools:" added; no tool, number or rule changed. |
| references/kickoff-questionnaire.md | "Owner's words (2026-09-28)…" / scope first (@@ -1) | SAME | |
| references/kickoff-questionnaire.md | "**A0 Project scope.**…" (@@ -34) | SAME | |
| references/kickoff-questionnaire.md | "**A4 Enclosure process and material**…" (@@ -53) | SAME | |
| references/kickoff-questionnaire.md | "**B7 Test points and self-documenting silk**…" / B8 (@@ -82) | SAME | "3 fiducials" → "Three fiducials". |
| references/kickoff-questionnaire.md | "**Owner inputs (a symmetric assembly…, C1–C2):**…" (@@ -100) | SAME | |
| references/kickoff-questionnaire.md | "**Owner inputs (colour):**…" (@@ -116) | SAME | |
| references/kickoff-questionnaire.md | "**C8a — which `20-design/dfm_processes.yaml` row…" C8a–C12, D1–D3 (@@ -128) | INTENDED (design margin 0.1 → 0.3) | D3 "walls at the checker's line + 0.1 (MJF)" → "walls at the checker's line + 0.3 (`design_margin` ≥ 0.3)"; reason added ("A wall at the line read yellow … §13"); alternative "+ 0.3 everywhere — heavy, slow, unnecessary on a 2 mm shell" → "+ 0.1 — lighter; the vendor map reads yellow near the gate". Note: the "(MJF)" scope qualifier on the recommendation is dropped. C8a–C12, D1, D2 SAME. |
| references/kickoff-questionnaire.md | "**E4 Vendor DFM before the order and FEA.**…" / F1 (@@ -187) | SAME | |
| references/kickoff-questionnaire.md | "`[OWNER]` records, analysis index…" H2–H4, I2, I4, answers table (@@ -213) | INTENDED (path remap) | Table: `design/<board>_board.yaml`, `design/dfm_thresholds.json` → `20-design/…`. Rest SAME. |
| references/part-verification.md | "dealers** (price, stock). So: verify on the manufacturer's site…" (@@ -49) | SAME | |
| references/part-verification.md | "The `PARTS_VERIFICATION.md` columns…" (@@ -62) | SAME | |
| references/pcb-layout-dfm.md | "\| **[checker]** \| … re-copy `design/dfm_thresholds.json`" (@@ -4) | INTENDED (path remap) | `design/` → `20-design/` |
| references/pcb-layout-dfm.md | "\| **Inputs** \| the G1 schematic of record…" / §1.1 (@@ -19) | INTENDED (path remap) | `design/…` → `20-design/…`; `out/G2/` → `80-reviews/G2/`; `out/dfm_items.json` + `out/dfm.json` → `30-board/layout/…`. §1.1 rewording SAME. |
| references/pcb-layout-dfm.md | "### 1.3 The G2 review pack (`out/G2/`…" (@@ -36) | INTENDED (path remap) | `out/G2/` → `80-reviews/G2/` |
| references/pcb-layout-dfm.md | "**Stack-up = the fab's named template**…" §2–§4 (@@ -50) | INTENDED (path remap) | `design/` → `20-design/`; rest SAME. |
| references/pcb-layout-dfm.md | "**Thermal reliefs**…" / teardrops (@@ -97) | INTENDED (path remap) | `design/` → `20-design/`; "(they change spacing)" → "because teardrops change spacing" SAME. |
| references/pcb-layout-dfm.md | "**Paste** **[convention]**…" / stencil (@@ -112) | SAME | |
| references/pcb-layout-dfm.md | "**Signal 0 Ω links: 0603**…" §8–§18 (@@ -124) | CHANGED (plus INTENDED path remap) | INTENDED: `design/<fab>_rotation.yaml` → `20-design/…`. CHANGED: "What one order taught: …" → "One order taught four facts." (a count is added; the list does hold four items, so the count is correct, but it is a new fact). Rest SAME (two-sided, CPL, polarity, silk, courtyards, creepage, panel, DRC census, canary, route quality, parity, §17, §18). |
| references/pitfalls.md | "FREE-STANDING wedges are RED…" / "Design every gated wall 0.1 over…" / "Snap tabs and detents died…" (@@ -9) | CHANGED (plus INTENDED margin 0.1 → 0.3) | INTENDED: "Design every gated wall 0.1 over the vendor's threshold (1.3 for a 1.2 grey line)" → "at least 0.3 over … (1.5 for a 1.2 grey line) … A 0.1 margin is not enough: a 1.20 wall read yellow on the map (the jlc/3dp map entry below)". CHANGED: the snap-tab line drops its trailing source tag "— (g)" → (none). The empty trailing ", ." citations on the wedge line are removed (SAME). |
| references/pitfalls.md | "The vendor's thin-wall metric is LENGTH-DEPENDENT…" / probe method (@@ -37) | SAME | Empty ", ." citation removed; empty code span "tabulated in ``" → "tabulated in one probe table" (fills a blank, no rule change). |
| references/pitfalls.md | "`.gitignore` has no inline comments (`out/x/ # note`…" (@@ -55) | INTENDED (path remap) | `out/x/` → `build/x/` in the example. |
| references/pitfalls.md | "A removal census separates LIVE citations (gen/, design/…" (@@ -129) | INTENDED (path remap) | `design/` → `20-design/` |
| references/pitfalls.md | "A `--check` that embeds anything a clone changes…" (@@ -167) | INTENDED (path remap) | `gen/ + design/` → `gen/ + 20-design/`; empty ", ." citations removed (SAME). |
| references/pitfalls.md | "Freerouting: deterministic with one thread…" (@@ -222) | SAME | Empty ", ." citation removed. |
| references/pitfalls.md | "Root-sheet NOTES … `design/*.yaml` + `docs/*.md`…" (@@ -253) | INTENDED (path remap) | `design/*.yaml` + `docs/*.md` → `20-design/*.yaml` + "the markdown docs". Note: the glob `docs/*.md` became the unbounded "the markdown docs" (scope now any markdown doc, not one folder). |
| references/pitfalls.md | "Debug mesh dumps go under `out/**/scratch/`…" (@@ -309) | INTENDED (path remap) | `out/**/scratch/` → `build/**/_check/` |
| references/print-dfm.md | "**Why it exists.** A vendor's upload-time checker…" / §1 fields (@@ -1) | INTENDED (who enforces what) | "the census … keeps the DESIGN margin (`wall_gate`, the vendor's grey line) — print DFM gates the printability floor, the census gates the margin" → "the census … gates `wall_gate` (the vendor's grey line). Print DFM gates the printability floor, the census gates `wall_gate`; the generator applies `design_margin`". §1 field rewording SAME. |
| references/print-dfm.md | "is the legacy spelling (spans every Z). Inside a box: wall limit…" (@@ -40) | INTENDED (legend boxes with a Z band) | "the census's 2-D `[x0, y0, x1, y1, gate]` is the same idea for `--box-min`" → "`thin_wall_census.py --boxes` reads the same 6- or 8-tuple. Its legacy 2-D `[x0, y0, x1, y1(, gate)]` spans every Z and prints a WARNING." Rest SAME. |
| references/print-dfm.md | "**(c) A new vendor or process** = ONE new row…" (@@ -72) | SAME | |
| references/print-dfm.md | "**Grouping by geometry first**…" (@@ -81) | SAME | |
| references/print-dfm.md | "Row fields a new process needs…" (@@ -101) | SAME | Prose turned into a list; same five fields and rule letters. |
| references/print-kit.md | "The kit is a folder of the repo, `50-kits/<kit>/`…" (@@ -4) | SAME | |
| references/print-kit.md | "3. **Assembly sequence**…" / 4. report-back (@@ -19) | SAME | Same step order and the same five criteria. |
| references/print-kit.md | "engineer's; the technician sorts a pile…" (@@ -34) | SAME | |
| references/print-kit.md | "Every plate carries a sidecar…" / snug-fit / §4.1 (@@ -66) | CHANGED | "(three caps …, three sliders …), tried on ONE production-size mating feature" (no actor) → "The technician tries them on ONE production-size mating feature." (actor added; consistent with the next sentence "The technician keeps the one that seats…"). Rest SAME. |
| references/project-yaml.md | "thresholds: design/dfm_thresholds.json…" / rating comment (@@ -61) | INTENDED (path remap; tg_c → hdt_c) | `design/…`, `out/dfm_items.json`, `out/dfm.json` → `20-design/…`, `30-board/layout/…`; "rating {ul94, tg_c, source}" → "rating {ul94, hdt_c (HDT at 0.45 MPa, °C), source}". |
| references/project-yaml.md | "rating: {ul94: HB, tg_c: 178…" (@@ -83) | INTENDED (tg_c → hdt_c) | `tg_c: 178` → `hdt_c: 178` + comment "HDT at 0.45 MPa [K] until read from the TDS; PA12 Tg is ~50 °C, 178 °C is near its melting point"; home_fdm `tg_c: 55` → `hdt_c: 55`. Reorg comment: legacy-path marker only. |
| references/project-yaml.md | "out/<board>/layout: 30-board/layout…" reorg rows (@@ -111) | SAME | Only `<!-- legacy-path: ok -->` markers added (ignored). |
| references/project-yaml.md | "- {name: case_iso, … src: "out/case/{CASE_VERSION}/renders/iso.png"…" (@@ -139) | INTENDED (path remap) | → `40-case/vendor_mjf/pictures/iso.png`. Note: the `{CASE_VERSION}` placeholder is dropped and the target is now fixed to `vendor_mjf`. |
| references/project-yaml.md | "the hash lives inside … Two exceptions, both inside their folder…" (@@ -197) | SAME | |
| references/project-yaml.md | "**A README in every folder.**…" (@@ -210) | SAME | |
| references/project-yaml.md | "`assembly_guide` have `--check`; `reorg_paths --check` is a grader…" (@@ -229) | INTENDED (who enforces what; path remap) | "`thin_wall_census` is the printed-body design-margin GATE (`… --json out/…/census/<piece>.json`" → "the printed-body `wall_gate` GATE: `… --json 40-case/<set>/checks/census/<piece>.json`". Rest SAME. |
| references/release-and-cut.md | "Generated records read each other, so the LAST round has an order…" §3.1 (@@ -21) | SAME | Same step order (known_issues → … → release_report → traceability → release_report → now_pages → analysis_index → render_pdf → production_cut LAST → commit). |
| references/release-and-cut.md | "`collateral/<rev>/renders/` (RENDERS.md's first row…" §4 (@@ -41) | SAME | |
| references/release-and-cut.md | "One command builds `<production_dir>/<rev>/`…" §7 (@@ -55) | SAME | |
| references/release-and-cut.md | "folder beside the drawing (§12); … Inputs: authored SHORT yaml…" §8 (@@ -95) | CHANGED (count only) | "Inputs: authored SHORT yaml …, generated step text …, one clean render …" → "The inputs are three. First, … Second, … Third, …" (a count is added; it matches the list). Pages, illustrations, recess and section-inset bullets SAME. |
| references/release-and-cut.md | "generated file that embeds paths … (gen/, design/, CI, live docs)…" §9–§12 (@@ -130) | INTENDED (path remap) | `design/` → `20-design/` in the live-citation list. §9 order (… → `--check` 0 → AFTER dump → `--proof` → gates → tag), §10 sections, §11, §12 SAME. |
| references/schematic-phase.md | "## 1. Design yaml … (`design/<board>.yaml`…" (@@ -4) | INTENDED (path remap) | `design/` → `20-design/` |
| references/schematic-phase.md | "- {no: 1, name: power, file: design/sheets/power.yaml}…" (@@ -17) | INTENDED (path remap) | `design/sheets/` → `20-design/sheets/` |
| references/schematic-phase.md | "Rules the generator enforces…" (@@ -37) | SAME | |
| references/schematic-phase.md | "A "map" is any table in the spec or in `design/`…" / "## 4. The G1 review pack (`out/G1/`…" (@@ -59) | INTENDED (path remap) | `design/` → `20-design/`; `out/G1/` → `80-reviews/G1/`. Map-check wording SAME. |
| references/schematic-phase.md | "1. G0 cell written by the owner → 2. `design/*.yaml`…" (@@ -84) | INTENDED (path remap) | `design/*.yaml` → `20-design/*.yaml` |
| references/software-track.md | "1. **Bring-up tool**…" / 3. / 4. (@@ -3) | SAME | |
| references/vendor-review.md | "never cancel.** Reading the order pages is fine; …" §1 / §2 steps 1–2 (@@ -7) | SAME | "and decides fault with the table" → "The agent decides fault with the table" (same actor as the drafting clause). |
| references/vendor-review.md | "6. **Replace on the order**…" (@@ -33) | SAME | |
| references/vendor-review.md | "The quote-page DFM procedure (one STL per session…" §4 (@@ -46) | SAME | |
| references/vendor-review.md | "The assembly fab's engineer mails a numbered question…" §5 (@@ -67) | CHANGED | "For every queried part read pad 1's position, the footprint's pin-1 meaning (…) and its nets from the board file" → "For every queried part, read three things from the board file: pad 1's position, the footprint's pin-1 meaning, and its nets." A count ("three") is added, and "from the board file" now plainly covers all three items (before, the pin-1 meaning came with its own parenthetical about the footprint library and could be read as a separate source). Rest SAME. |
| references/vendor-review.md | "silent timer (…) — no mail announces it…" Round 4 / §6 (@@ -100) | SAME | |
| references/vendor-review.md | "**The order remark carries the fab-side decisions**…" (@@ -143) | SAME | |
| templates/.gitignore | "out/scratch/" (@@ -3) | INTENDED (path remap) | `out/scratch/` → `build/`. Note: the ignore scope widens from one scratch folder to every `build/` folder (makes the `40-case/*/build/` line redundant). |
| templates/10-spec/KICKOFF_ANSWERS.md | "\| D3 \| design margin … {{+0.1 MJF…}}" / F2 / G1 (@@ -37) | CHANGED (plus INTENDED margin) | INTENDED: D3 `{{+0.1 MJF; …}}` → `{{+0.3 MJF; …}}`. CHANGED (not on the fix list): F2 landing key `kickoff.sourcing.stock_floor` → `kickoff.sourcing.stock_floor`, `kickoff.sourcing.attrition`; G1 landing key `kickoff.software.modes` → `kickoff.software.modes`, `kickoff.software.posture`. Two new landing keys (and so two new things `project.py kickoff --check` can require). |
| templates/10-spec/SPEC.md | "Every requirement has an ID (`R-<family><nn>`…" (@@ -1) | SAME | |
| templates/10-spec/datasheet_notes/_TEMPLATE.md | "Datasheet: … read on {{DATE}} by <agent>." (@@ -1) | CHANGED | "read on {{DATE}}" → "read on <date>". A `{{…}}` scaffold slot (counted by `project.py slots`, filled at copy time) becomes a hand-filled `<…>` placeholder. Probably a deliberate fix (the template is copied per part, later than day 1), but it is not on the listed fixes. |
| templates/20-design/traceability.yaml | "reached: [{type: exists, path: design/{{BOARD}}.yaml}]" (@@ -5) | INTENDED (path remap) | `design/` → `20-design/` |
| templates/90-log/GATES.md | "`_not yet approved_`. The release reports read this file…" + gate table (@@ -4) | INTENDED (path remap; drawing round in gate rows) | G1/G2 `out/G1/`, `out/G2/` → `80-reviews/G1/`, `80-reviews/G2/`. M1 adds ", the double-blind drawing round merged (skill `SKILL.md` §5)". Case order adds ", (both) the double-blind drawing round merged (skill `SKILL.md` §5)". Prose (release phrase, review round, bar) SAME. |
| templates/CENSUS_GATE_ROWS.md | "are the project's check table … `{{MARGIN}}` = `design_margin` (owner bar, 0.1)…" (@@ -1) | INTENDED (design margin 0.1 → 0.3) | "(owner bar, 0.1)" → "(owner bar, ≥ 0.3)" |
| templates/CENSUS_GATE_ROWS.md | "INFO table (no threshold — each row says why)…" / adopt-list lines (@@ -24) | INTENDED (tg_c → hdt_c) | "material rating (UL 94 / Tg from the TDS…)" → "UL 94 / HDT at 0.45 MPa from the TDS". Rest SAME. |
| templates/CLAUDE.md | "on a datasheet or standard nobody has read yet (definition…" rules 3–4 (@@ -12) | SAME | |
| templates/CLAUDE.md | "command); `scripts/erc_gate.py 30-board/layout/erc.json` green…" rules 7, 9 (@@ -26) | SAME | |
| templates/CLAUDE.md | "**Heavy jobs only through `scripts/jobs.sh`**…" / caching (@@ -52) | SAME | |
| templates/DFM_ROUND.md | "uploaded, canonical STL), `<md5-8>_analyze.json`…" (@@ -3) | SAME | |
| templates/DFM_ROUND.md | "**{{PASS / NOT YET}}** — acceptance bar…" / rating (@@ -34) | INTENDED (tg_c → hdt_c) | "Tg / softening {{TG}} °C" → "HDT (0.45 MPa) {{HDT}} °C". Bar wording SAME. |
| templates/RELEASE_NOTES.md | "> **State at this release (generated facts):** record … (`scripts/project.py record`; content signature `{{SIG}}`)" (@@ -1) | UNCLEAR | "md5 `{{MD5}}` (`scripts/project.py record`; content signature `{{SIG}}`)" (two separate parentheticals) → "`scripts/project.py record` gives the record md5 and the content signature `{{SIG}}`." The new text says `project.py record` produces the content signature; the diff alone cannot show whether the script does that. |
| templates/REVIEW_HANDOFF.md | "\| `20-design/case.yaml` / `out/.../case/<preset>/stl/*.stl` \|…" (@@ -17) | INTENDED (path remap) | → `40-case/<set>/parts/*.stl` |
| templates/ci/README.md | "-e 's\|{{PROJECT_RELEASE_CMD}}\|ci/release_archive.sh out/release_artefacts\|g'…" (@@ -12) | INTENDED (path remap) | `out/release_artefacts` → `build/release_artefacts`; `out/*/erc.json` → `30-board/layout/erc.json` (a glob becomes one fixed path). |
| templates/ci/README.md | "\| `{{PROJECT_RELEASE_CMD}}` \| … `ci/release_archive.sh out/release_artefacts`" (@@ -35) | INTENDED (path remap) | `out/` → `build/` |
| templates/ci/release.yml | "run: test "$(find out/release_artefacts…" (@@ -29) | INTENDED (path remap) | `out/release_artefacts` → `build/release_artefacts` (twice) |
| templates/production_cut.yaml | "manufacturing_spec … material rating UL94/Tg…" (@@ -30) | INTENDED (tg_c → hdt_c) | "UL94/Tg" → "UL94/HDT" in the both and mech rows |
| templates/project.yaml | "sourcing: {sources: …, stock_floor: …}" / "software: {modes: …, criteria: …}" (@@ -31) | CHANGED | New keys and new recommendations: `sourcing` gains `attrition: {{F2_ATTRITION}}` with "attrition = the run multiplier on qty × boards (F2 recommends 1.2)"; `software` gains `posture: {{G1_POSTURE}}` with "posture = warn / throttle / refuse (G1 recommends warn + throttle until the criteria are approved)". Two new `{{…}}` slots, so `project.py slots` counts more. |
| templates/project.yaml | "rating: {ul94: {{UL94}}, tg_c: {{TG}}…" (@@ -118) | INTENDED (tg_c → hdt_c) | `tg_c: {{TG}}` → `hdt_c: {{HDT}}` + "hdt_c = HDT at 0.45 MPa (°C) from the TDS" |
| templates/project.yaml | "rating: {ul94: unrated, tg_c: 55…" (@@ -135) | INTENDED (tg_c → hdt_c) | `tg_c: 55` → `hdt_c: 55` |
| templates/project.yaml | "#   wall_gate: 0.6 …" (@@ -143) | INTENDED (colour wall gate 0.6 → 0.4) | `wall_gate: 0.6` (3 layers) → `wall_gate: 0.4` (colour layers × layer height, default 2 × 0.20) |
| templates/project.yaml | "#     out/<board>/fab/…" reorg example (@@ -166) | SAME | Only `<!-- legacy-path: ok -->` markers added (ignored). |

## Counts

| Hunks reviewed | SAME | INTENDED | CHANGED | UNCLEAR |
|---|---|---|---|---|
| 133 | 75 | 45 | 12 | 1 |

A hunk that holds a deliberate fix and also an unlisted change is counted CHANGED (6 of the 12: agent-ops @@ -39, dfm-printed-enclosure @@ -115, pcb-layout-dfm @@ -124, pitfalls @@ -9, KICKOFF_ANSWERS @@ -37, and README @@ -134 by its link to @@ -104).

## Substantive CHANGED items (rules, keys, sequence)
1. README @@ -104 / @@ -134: the kickoff questionnaire moves before the copy block ("Run the kickoff questionnaire first … Its A0 answer sets the scope of the copy block"), and step 5 becomes "§0 from step 3: project.yaml, ENV record …".
2. dfm-printed-enclosure §2 @@ -115: a new census rule, "**The band is an axis-aligned measure** … valid only for a straight edge that runs along X, Y or Z … Re-measure a diagonal or ring wedge FAIL across the edge before you accept or fix it". There is also a new `--gate-dir` fact: "re-matches every accepted FAIL by class and bbox (1 mm tolerance) against the current yaml".
3. KICKOFF_ANSWERS F2 / G1 and templates/project.yaml @@ -31: new landing keys `kickoff.sourcing.attrition` and `kickoff.software.posture`, with recommendations "F2 recommends 1.2" and "G1 recommends warn + throttle until the criteria are approved".
4. datasheet_notes/_TEMPLATE: `{{DATE}}` → `<date>`, so the slot leaves the `project.py slots` count.

## Minor CHANGED items (an actor, a count or a source tag added or dropped; the rules are the same)
5. agent-ops @@ -39: "merged" → "The coordinator merged both reports" (actor added).
6. print-kit @@ -66: "tried on ONE production-size mating feature" → "The technician tries them on ONE …" (actor added).
7. pcb-layout-dfm @@ -124: "What one order taught:" → "One order taught four facts." (count added; it is correct).
8. release-and-cut @@ -95: "Inputs: …" → "The inputs are three." (count added; it is correct).
9. vendor-review @@ -67: "read three things from the board file" (count added; "from the board file" now plainly covers the pin-1 meaning too).
10. pitfalls @@ -9: the snap-tab line loses its trailing source tag "— (g)".

## Notes on INTENDED rows (no verdict change, worth a look)
- kickoff D3: the recommendation drops its "(MJF)" scope qualifier ("+ 0.1 (MJF)" → "+ 0.3 (`design_margin` ≥ 0.3)").
- dfm-printed-enclosure §1.2 still says "a `wall_gate + 0.1` wall" (unchanged on both sides). It is an example of post-processing loss and not the margin rule, but it now reads like the old 0.1 margin.
- project-yaml renders: `out/case/{CASE_VERSION}/renders/iso.png` → `40-case/vendor_mjf/pictures/iso.png` (the version placeholder is dropped; the preset is now fixed).
- templates/.gitignore: `out/scratch/` → `build/` widens the ignore scope to every `build/` folder.
- pitfalls @@ -253: `docs/*.md` → "the markdown docs" (a bounded glob becomes an open scope).
- ci/README: `out/*/erc.json` (a glob) → `30-board/layout/erc.json` (one path).
