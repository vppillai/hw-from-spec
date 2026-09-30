# Retro — aec-tester → hw-from-spec (2026-09-29)

Project `/Users/vpillai/temp/aec-tester`: 19 dated learnings, 295 decision rows (87 owner rows). Skill `/Users/vpillai/temp/hw-from-spec` at SKILL.md version **0.5.0**; the project recorded skill version **none (add `skill: {version: …}` to project.yaml)**.
Classifier: keyword overlap against 196 sections (threshold 0.5); a human folds the candidates — this report is the input to the next CHANGELOG entry, not the entry itself.

## 1. Counts

| CARRIED | PARTIAL | NEW | NEW and costly (a round, an order, a wrong result) |
|---|---|---|---|
| 0 | 4 | 15 | 5 |

## 2. NEW — learnings the skill does not carry yet

| Date | Domain | Learning | Best section (coverage) | Costly |
|---|---|---|---|---|
| 2026-09-29 | tooling/gates | `gen/fab_package.py --selftest` builds two dated packages in a temp dir and expects one to carry the STALE banner; run across midnight it produced 2026-09-28 and 2026-09-29 folders and failed the PR gate for no design re… | `references/release-and-cut.md` › 7. Production cut (`templates/production_cut.yaml` (0.21) | yes |
| 2026-09-29 | mechanical/msa | The QSFP-DD module (= the plug nose of an AEC cable) is not a plain box: its bottom is open at the leading edge (paddle-card pads exposed) and its top carries the 6 x 1.7 latch recess (MSA Rev 7.1 Fig. 63 / 64, ref/QSFP-… | `references/part-verification.md` › Hardware classes and what to verify per class (0.07) |  |
| 2026-09-29 | process | A drawing page that pdftotext returns empty (MSA Fig. 63 / 64 are pure drawings) still yields its numbers in one step: `pdftoppm -f N -l N -r 110 -png` and read the render; no need to declare the dimension BLOCKED. | `references/pitfalls.md` › sourcing (0.11) |  |
| 2026-09-29 | dfm/branding/measurement | "Minimum gap" of a filled logo with corners is ill-posed: a chord through a boundary point is ~0, the medial axis reaches every convex vertex with width -> 0, and the convex hull minus the ink adds slivers along tangent … | `SKILL.md` › 0. Day-1 setup (do this before any CAD) (0.07) | yes |
| 2026-09-29 | dfm/branding | A logo whose arms touch at points cannot be given a >= 1.2 land at the contacts without adding artwork (discs read as dimples, closing fillets round every inner corner); the owner rejected the dimples and the reference a… | `references/pitfalls.md` › mechanical / case (0.19) |  |
| 2026-09-29 | fdm/branding | A bed-face deboss is never as good as the face around it: the recess ceiling is a bridge underside (strands) beside a glossy bed-contact face - that texture step is the "webbing" people remember on debossed logos. When t… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.17) |  |
| 2026-09-29 | tooling/bambu | Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc -18 "Invalid parameter value(s)", also with a rectilinear pattern; 90 % passes). To make a column solid, raise `top_shell_layers` / `bottom_shell_lay… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.16) | yes |
| 2026-09-29 | dfm/measurement | A mesh footprint measured from facet CENTROIDS under-reads the true extent (the centroids of a rounded rectangle's triangles sit well inside its edges: 11.66 vs 12.53); use the vertices of the selected facets for any bbo… | `references/dfm-printed-enclosure.md` › 7.2 Canonical STL and the geometry signature **[co (0.24) |  |
| 2026-09-29 | fdm/branding/process | "Apply the rule to the other places too" is an audit, not a patch: list EVERY instance of the feature class across the build (here: three Tenstorrent marks - lid plate raised = compliant, hood roof = bed-face deboss = vi… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.16) |  |
| 2026-09-29 | tooling/bambu/ams | Bambu Studio's CLI has no flag for per-part extruders, but it loads a Bambu-style 3MF: one object file per object (production extension), a components object in 3D/3dmodel.model, and Metadata/model_settings.config with `… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.21) |  |
| 2026-09-29 | tooling/bambu/ams | The CLI SEGFAULTS (rc -11, no result.json, log ends after "no filament colors found in projects") on a two-filament plate with the prime tower ON when the filament JSONs given to --load-filaments carry no `filament_colou… | `references/pitfalls.md` › kicad / drc / swig *(worked examples; the mechanis (0.12) | yes |
| 2026-09-29 | fdm/ams | Purge + prime-tower mass is not in Bambu's g-code header; it can be derived as used minus (part volume x density) only for a SOLID part (the 2-3 layer colour mark). A 20 % infill body gives a negative "purge" - report th… | `references/project-yaml.md` › project.yaml — the one file the generic scripts re (0.18) |  |
| 2026-09-29 | fdm/branding/ams | A flush colour mark in the bed layers is the one deboss-free way to get logo and face as the same surface: both colours are bed contact. Two layers of a dark colour on black are opaque and only layer 1 shows; the third l… | `references/pitfalls.md` › mechanical / case (0.18) |  |
| 2026-09-29 | tooling/bambu | Bambu Studio 02.08.02.61's CLI segfaults (rc -11 / 133) on ANY two-filament slice whose project carries no filament colours - a hand-built or merged multi-part project 3MF, `--load-filament-ids`, `--assemble` all crash t… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.14) | yes |
| 2026-09-29 | fdm/branding | A flush colour body in the bed layers is the crispest logo an FDM print can carry (the colour boundary is a first-layer perimeter in XY, no seam, nothing proud), and two layers of an opaque colour are enough - only layer… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.18) |  |

## 3. PARTIAL — carried in part (check the section, extend it if the mechanism is missing)

| Date | Domain | Learning | Best section (coverage) |
|---|---|---|---|
| 2026-09-29 | dfm/branding | The v3.14 web discs that bridge the mark's three point contacts scale with the mark but read as three visible fillet dots at 7 mm; a closing (offset +r / -r) removes the dots but r… | `references/pitfalls.md` › dfm / printed enclosures (0.4.0 — `references/dfm- (0.35) |
| 2026-09-29 | tooling/bambu | Bambu Studio's CLI takes the same STL path N times as N objects (arranged with --arrange 1): a "four caps" plate needs no multi-body STL. The sidecar's input md5 dict dedups the pa… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.26) |
| 2026-09-29 | fdm/branding | A debossed logo belongs on the BED face, not a vertical wall: first-layer perimeters cut the outline in XY at nozzle resolution, while a vertical wall stair-steps every horizontal … | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.29) |
| 2026-09-29 | tooling/bambu | Bambu's `different_settings_to_system` only lists keys whose value differs from the flattened system preset: a project value that happens to equal the system default (elefant_foot_… | `references/dfm-printed-enclosure.md` › 8. FDM at home (worked example: Bambu Lab P2S, 0.4 (0.43) |

## 4. CHANGELOG entry draft

### Added (from aec-tester, learnings 2026-09-29 … 2026-09-29)
- **`references/dfm-printed-enclosure.md`**: "Minimum gap" of a filled logo with corners is ill-posed: a chord through a boundary point is ~0, the medial axis reaches every convex verte; Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc -18 "Invalid parameter value(s)", also with a rectilinear pattern; 90; A mesh footprint measured from facet CENTROIDS under-reads the true extent (the centroids of a rounded rectangle's triangles sit well inside; Bambu Studio's CLI has no flag for per-part extruders, but it loads a Bambu-style 3MF: one object file per object (production extension), a ; A flush colour body in the bed layers is the crispest logo an FDM print can carry (the colour boundary is a first-layer perimeter in XY, no 
- **`references/part-verification.md`**: The QSFP-DD module (= the plug nose of an AEC cable) is not a plain box: its bottom is open at the leading edge (paddle-card pads exposed) a
- **`references/pitfalls.md`**: A drawing page that pdftotext returns empty (MSA Fig. 63 / 64 are pure drawings) still yields its numbers in one step: `pdftoppm -f N -l N -; A logo whose arms touch at points cannot be given a >= 1.2 land at the contacts without adding artwork (discs read as dimples, closing fille; A bed-face deboss is never as good as the face around it: the recess ceiling is a bridge underside (strands) beside a glossy bed-contact fac; "Apply the rule to the other places too" is an audit, not a patch: list EVERY instance of the feature class across the build (here: three Te; The CLI SEGFAULTS (rc -11, no result.json, log ends after "no filament colors found in projects") on a two-filament plate with the prime tow; A flush colour mark in the bed layers is the one deboss-free way to get logo and face as the same surface: both colours are bed contact. Two; +1 more
- **`references/project-yaml.md`**: Purge + prime-tower mass is not in Bambu's g-code header; it can be derived as used minus (part volume x density) only for a SOLID part (the
- **`references/release-and-cut.md`**: `gen/fab_package.py --selftest` builds two dated packages in a temp dir and expects one to carry the STALE banner; run across midnight it pr

### Changed
- (sections the PARTIAL entries extend: `references/dfm-printed-enclosure.md`, `references/pitfalls.md`)

## 5. Reference patch stubs (bullets to append; generalise the numbers, label the worked example, keep the evidence pointer at the end)

### references/dfm-printed-enclosure.md
- 2026-09-29 [dfm/branding/measurement] "Minimum gap" of a filled logo with corners is ill-posed: a chord through a boundary point is ~0, the medial axis reaches every convex vertex with width -> 0, and the convex hull minus the ink adds slivers along tangent edges - three metrics in a row said nothing. What is well-posed for a bed-face deboss: the largest inscribed circle of each recessed lobe (bridge span), the inscribed circle of every solid region the recess encloses (first-layer island), the ink width through each point contact (neck) - all from shapely on the same polygon the SCAD imports. Measure what the failure mode is, not "the gap".
- 2026-09-29 [tooling/bambu] Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc -18 "Invalid parameter value(s)", also with a rectilinear pattern; 90 % passes). To make a column solid, raise `top_shell_layers` / `bottom_shell_layers` to cover it - and bisect a rejected 3MF by re-slicing subsets of the settings into a scratch dir, one key group at a time.
- 2026-09-29 [dfm/measurement] A mesh footprint measured from facet CENTROIDS under-reads the true extent (the centroids of a rounded rectangle's triangles sit well inside its edges: 11.66 vs 12.53); use the vertices of the selected facets for any bbox row.
- 2026-09-29 [tooling/bambu/ams] Bambu Studio's CLI has no flag for per-part extruders, but it loads a Bambu-style 3MF: one object file per object (production extension), a components object in 3D/3dmodel.model, and Metadata/model_settings.config with `<part id><metadata key="extruder" value="N"/>` - that is enough for a multi-part two-colour object placed where you put it (no --arrange). Copy the package layout from a file Studio exported; the ids are global.
- 2026-09-29 [fdm/branding] A flush colour body in the bed layers is the crispest logo an FDM print can carry (the colour boundary is a first-layer perimeter in XY, no seam, nothing proud), and two layers of an opaque colour are enough - only layer 1 is ever seen; keep the layer count a knob (owner: 'we can reduce the number of colored layers if need be') and slice every variant, because the AMS cost (tool changes, purge) scales with the coloured layer count, not with the logo area.

### references/part-verification.md
- 2026-09-29 [mechanical/msa] The QSFP-DD module (= the plug nose of an AEC cable) is not a plain box: its bottom is open at the leading edge (paddle-card pads exposed) and its top carries the 6 x 1.7 latch recess (MSA Rev 7.1 Fig. 63 / 64, ref/QSFP-DD-Hardware-Rev7.1.pdf p. 91-92). Anything that grips a plug must bear on the two SIDE faces. The cross-section corners are R 0.15..0.60, so a pocket corner radius above 0.66 clips a legal module - take the pocket radius from the drawing, not from the print rule of thumb (gen/plug_cap.py, CC-209).

### references/pitfalls.md
- 2026-09-29 [process] A drawing page that pdftotext returns empty (MSA Fig. 63 / 64 are pure drawings) still yields its numbers in one step: `pdftoppm -f N -l N -r 110 -png` and read the render; no need to declare the dimension BLOCKED.
- 2026-09-29 [dfm/branding] A logo whose arms touch at points cannot be given a >= 1.2 land at the contacts without adding artwork (discs read as dimples, closing fillets round every inner corner); the owner rejected the dimples and the reference artwork itself has the arms touching - so the contacts stay point contacts and the print fuses them over one line width, which is the artwork's own look. Fix the rule set to the artwork before fixing the artwork to the rule set.
- 2026-09-29 [fdm/branding] A bed-face deboss is never as good as the face around it: the recess ceiling is a bridge underside (strands) beside a glossy bed-contact face - that texture step is the "webbing" people remember on debossed logos. When the recess floor must match the face, put the mark in the TOP face and iron ALL top surfaces (`ironing_type` top; `topmost` skips the recess floor) - then both are topmost solid surfaces built by the same pass. Design the part so it can print that way up (blind pocket rising from the bed, flange flat on the bed, one short bridge) rather than fixing it in the profile (CC-209 addendum 4).
- 2026-09-29 [fdm/branding/process] "Apply the rule to the other places too" is an audit, not a patch: list EVERY instance of the feature class across the build (here: three Tenstorrent marks - lid plate raised = compliant, hood roof = bed-face deboss = violation, sole = text = out of scope) and state each verdict in a FAIL-gated row before changing anything; the fix then reuses the geometry another preset already proved (the jlc badge pocket + key became the p2s rebate + printed plate, and the jlc SCAD stayed byte-identical through SCAD hook tokens - verified in-process against the committed file before and after the edit). A bed-face pocket on a roof-down print is a bridge ceiling even when it is hidden: split it with full-height lands that double as glue lands (3 x 6.1 mm here) rather than filing a covered-face exemption - an unsplit 22 mm bridge sags into the rebate and rocks the plate. Mesh rows that read pocket strips as section holes must filter by the pocket footprint (the Ø2.2 fan through-holes 7 mm away were counted as strips at first) and test hole containment against the outer ring (a hole's representative point is never inside the polygon that owns it).
- 2026-09-29 [tooling/bambu/ams] The CLI SEGFAULTS (rc -11, no result.json, log ends after "no filament colors found in projects") on a two-filament plate with the prime tower ON when the filament JSONs given to --load-filaments carry no `filament_colour`; one filament, or two without the tower, slice fine. Write one filament JSON per slot with its colour and the tower works. Bisect a crash by subsetting settings into a scratch outputdir, one variable per run.
- 2026-09-29 [fdm/branding/ams] A flush colour mark in the bed layers is the one deboss-free way to get logo and face as the same surface: both colours are bed contact. Two layers of a dark colour on black are opaque and only layer 1 shows; the third layer buys nothing for purple but is needed for a light mark on black - and costs a filament change per layer (here +2 swaps, +0.66 g purge, +3 min).
- 2026-09-29 [tooling/bambu] Bambu Studio 02.08.02.61's CLI segfaults (rc -11 / 133) on ANY two-filament slice whose project carries no filament colours - a hand-built or merged multi-part project 3MF, `--load-filament-ids`, `--assemble` all crash the same way, and the only hint is the last log line "no filament colors found in projects". Give the colours (a `filament_colour` in each slot's filament JSON, or `--filament-colour '#RRGGBB;#RRGGBB'`, undocumented in --help) and every route works - the multi-part project 3MF (one object, part extruders in model_settings.config) as well as the CLI's own `--load-filament-ids 1,2 --assemble --arrange 0` on pre-placed part STLs. Bisect with the CLI directly on the temp inputs (5 s per run) before touching the generator, and reuse the one writer two agents need instead of a second implementation.

### references/project-yaml.md
- 2026-09-29 [fdm/ams] Purge + prime-tower mass is not in Bambu's g-code header; it can be derived as used minus (part volume x density) only for a SOLID part (the 2-3 layer colour mark). A 20 % infill body gives a negative "purge" - report the mark filament's share and say the body's cannot be separated.

### references/release-and-cut.md
- 2026-09-29 [tooling/gates] `gen/fab_package.py --selftest` builds two dated packages in a temp dir and expects one to carry the STALE banner; run across midnight it produced 2026-09-28 and 2026-09-29 folders and failed the PR gate for no design reason. A date-stamped artefact test must pin the date (or the gate must tolerate a rollover); re-running after midnight passed.

## 6. Eval stubs — one per NEW learning that cost a round (fill prompt / assertions from the entry; add to evals/evals.json)

```json
{"id": "R1", "name": "gen-fab-package-py", "prompt": "A project hits this situation: `gen/fab_package.py. Handle it.", "expected_output": "`gen/fab_package.py --selftest` builds two dated packages in a temp dir and expects one to carry the STALE banner; run across midnight it produced 2026-09-28 and 2026-09-29 folders and failed the PR gate for no design reason. A date-stamped artefact test must pin the date (or the gate must tolerate a rollover); re-running after midnight passed.", "assertions": ["the agent applies: `gen/fab_package.py --selftest` builds two dated packages in a temp dir and expects one to carry the STALE banner; run across midnight it produced 2026-09-28 and 2026-09-29 folders and failed the PR g", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R2", "name": "minimum-gap-of-a-filled-logo-with-corners-is-ill", "prompt": "A project hits this situation: \"Minimum gap\" of a filled logo with corners is ill. Handle it.", "expected_output": "\"Minimum gap\" of a filled logo with corners is ill-posed: a chord through a boundary point is ~0, the medial axis reaches every convex vertex with width -> 0, and the convex hull minus the ink adds slivers along tangent edges - three metrics in a row said nothing. What is well-posed for a bed-face deboss: the largest inscribed circle of each recessed lobe (bridge span), the inscribed circle of eve", "assertions": ["the agent applies: \"Minimum gap\" of a filled logo with corners is ill-posed: a chord through a boundary point is ~0, the medial axis reaches every convex vertex with width -> 0, and the convex hull minus the ink adds sl", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R3", "name": "bambu-studio-s-cli-validator-rejects-sparse-infill-density-1", "prompt": "A project hits this situation: Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc. Handle it.", "expected_output": "Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc -18 \"Invalid parameter value(s)\", also with a rectilinear pattern; 90 % passes). To make a column solid, raise `top_shell_layers` / `bottom_shell_layers` to cover it - and bisect a rejected 3MF by re-slicing subsets of the settings into a scratch dir, one key group at a time.", "assertions": ["the agent applies: Bambu Studio's CLI validator rejects `sparse_infill_density` 100 % (rc -18 \"Invalid parameter value(s)\", also with a rectilinear pattern; 90 % passes). To make a column solid, raise `top_shell_layers`", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R4", "name": "the-cli-segfaults-rc", "prompt": "A project hits this situation: The CLI SEGFAULTS (rc. Handle it.", "expected_output": "The CLI SEGFAULTS (rc -11, no result.json, log ends after \"no filament colors found in projects\") on a two-filament plate with the prime tower ON when the filament JSONs given to --load-filaments carry no `filament_colour`; one filament, or two without the tower, slice fine. Write one filament JSON per slot with its colour and the tower works. Bisect a crash by subsetting settings into a scratch o", "assertions": ["the agent applies: The CLI SEGFAULTS (rc -11, no result.json, log ends after \"no filament colors found in projects\") on a two-filament plate with the prime tower ON when the filament JSONs given to --load-filaments carr", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
{"id": "R5", "name": "bambu-studio-02-08-02-61-s-cli-segfaults-rc", "prompt": "A project hits this situation: Bambu Studio 02.08.02.61's CLI segfaults (rc. Handle it.", "expected_output": "Bambu Studio 02.08.02.61's CLI segfaults (rc -11 / 133) on ANY two-filament slice whose project carries no filament colours - a hand-built or merged multi-part project 3MF, `--load-filament-ids`, `--assemble` all crash the same way, and the only hint is the last log line \"no filament colors found in projects\". Give the colours (a `filament_colour` in each slot's filament JSON, or `--filament-colou", "assertions": ["the agent applies: Bambu Studio 02.08.02.61's CLI segfaults (rc -11 / 133) on ANY two-filament slice whose project carries no filament colours - a hand-built or merged multi-part project 3MF, `--load-filament-ids`, `--a", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}
```

## 7. Owner decision topics the kickoff questionnaire does not ask yet (candidates for a new question with a recommended answer)

| Row | Date | Topic | Best question section (coverage) |
|---|---|---|---|
| D-04 | 2026-09-13 | AEC-CT2-MINI form factor: **cage-sized stick** | — |
| D-05 | 2026-09-13 | Enclosure is a design input for the MINI stick — dimensions and clearances | — |
| D-06 | 2026-09-13 | MINI silk screen: self-documenting labels; no silk over pads | — |
| D-10 | 2026-09-13 | Final thorough review after design + implementation | — |
| D-11 | 2026-09-13 | Reviewer hand-off document for external deep reviews | — |
| D-13 | 2026-09-13 | USB-C receptacle: clearances and mechanical reinforcement for many insertions | — |
| D-14 | 2026-09-13 | Case: latch two MINI units together into a two-end cable jig | `A2 Quantity and horizon` (0.16) |
| D-09a | 2026-09-13 | Premium aesthetics and a thought-through user experience apply to the MAIN board too | `kickoff-questionnaire.md — every owner decision a board + en` (0.16) |
| D-16 | 2026-09-13 | External FTDI/pod path = backup debug path, not a mode of operation; pluggable, compact, case need not expose it | `I. Identity, envelope, delegation (added by the first retro ` (0.14) |
| D-18 | 2026-09-13 | EXT/LA connectors and EXT pinout: CC-057 set with the 1.27 mm LA pair; CC-056 Total Phase order | `B3 Controlled impedance` (0.13) |
| D-20 | 2026-09-13 | MINI stick dimensions are secondary: grow the board as required to route cleanly; functionality, electrical and signal i | `B1 Layers and thickness` (0.08) |
| D-22 | 2026-09-13 | Deep layer-by-layer, trace-by-trace visual inspection of the routing after final routing | `F2 Stock policy and alternates` (0.21) |
| D-24 | 2026-09-14 | MINI printed case: two-tone, per-colour AMS printing, assembly-friendly for 50+ units | `A2 Quantity and horizon` (0.16) |
| D-25 | 2026-09-14 | Product name: AEC-CT2 = AEC Cable Tester 2 | — |
| D-26 | 2026-09-14 | MINI USB-C receptacles: CC-052 option B (mid-mount XYECONN C20883026) | — |
| D-27 | 2026-09-14 | Fan: none fitted, provision kept for a specific part sourced outside JLC | `C6 Fan, vents, thermal` (0.16) |
| D-29 | 2026-09-14 | Credo evidence: one real cable in hand, no vendor documents | — |
| D-30 | 2026-09-14 | MINI: remaining open items take the coordinator's recommendations; provisional decisions confirmed | `kickoff-questionnaire.md — every owner decision a board + en` (0.24) |
| D-31 | 2026-09-15 | MINI case v3: two-part, single-material, supportless; colour as a print-time option | — |
| D-32 | 2026-09-15 | MINI case: 13.4 mm finger dish (one-span D-12 bridge exception) + short switch names | `B7 Test points and self-documenting silk` (0.17) |
| D-33 | 2026-09-15 | MINI case fastening: heat-set (hot press-fit) M3 inserts + standard screws | `A2 Quantity and horizon` (0.12) |
| D-34 | 2026-09-15 | MINI case: print supports allowed → two-piece case (tray + one top shell) | `C1 Pieces` (0.18) |
| D-37 | 2026-09-17 | After the D-36 simplification: stricter on waivers, strengthen the design | — |
| D-38 | 2026-09-18 | Blanket 'go with recommended' on every open recommendation at PAUSE POINT 4: CC-088 (a)–(k), coherence Q1–Q5, CC-086 (a) | `I. Identity, envelope, delegation (added by the first retro ` (0.17) |
| D-39 | 2026-09-19 | MINI_ORDER §2.7 stock gate stays at ≥ 5 000 (or the alternate) for C27882 / C11133 | — |
| D-40 | 2026-09-19 | Fix the D-22 run-3 review findings (CC-095 MINOR list) — round 6d authorised, in parallel with the JLC quote pass | — |
| D-41 | 2026-09-19 | Extensive, parallelised double-blind reviews of the round-6 design with the best external models via the Cursor `agent`  | `E1 Review rounds per gate` (0.14) |
| D-42 | 2026-09-20 | Owner answers to the post-review items | — |
| D-43 | 2026-09-20 | After every change/re-route round: full verification gauntlet before the order — double-blind reviews, deep visual inspe | `F2 Stock policy and alternates` (0.11) |
| D-44 | 2026-09-20 | Two case tracks: keep the local single-colour FDM case (v3.6.x) for own printing/assembly; **complete re-design and re-e | `kickoff-questionnaire.md — every owner decision a board + en` (0.1) |
| D-45 | 2026-09-20 | Removable top portion over the QSFP-DD heat sink (both case tracks) + secondary logos so branding survives with the hood | `I. Identity, envelope, delegation (added by the first retro ` (0.11) |
| D-47 | 2026-09-20 | JLCDFM: every danger AND warning on the board of record is to be fixed, and our own DRC/checks must catch them | — |
| D-48 | 2026-09-20 | Local FDM case: coloured marks only on top-facing (Z-up) surfaces printed in the same top layers as the legends; no colo | `B7 Test points and self-documenting silk` (0.09) |
| D-49 | 2026-09-20 | Case: CC-120 A+B (full-height tray dovetail + matching body rail), CC-113 v3.7 snap-hood consequences accepted, CC-115 ( | `I. Identity, envelope, delegation (added by the first retro ` (0.13) |
| D-50 | 2026-09-20 | (1) Free FEA as a generated case-pipeline stage; (2) generated clear-to-build reports for the PCB and the case | `0. Batches (ask in this order; one AskUserQuestion call per ` (0.15) |
| D-51 | 2026-09-21 | Final product uses the Amphenol-provided connector/cage data (Amphenol_data/): connector **V36-ADZ01-301100T** (ExtremeP | `I. Identity, envelope, delegation (added by the first retro ` (0.04) |
| D-52 | 2026-09-21 | Software track for test/validation and production deployment: an ENGINEERING / R&D mode (low-level, detailed options) an | — |
| D-53 | 2026-09-21 | (1) Cage part number confirmed: **UE36-C16211-05A3A** = the 6.5 mm fin-pin heat-sink model (single light pipe, EMI sprin | `H4 The feedback loop into the skill` (0.06) |
| D-54 | 2026-09-21 | Power budget: research how to raise it (MINI and/or the full tester); the MINI must support ALL standalone cable tests ( | — |
| D-55 | 2026-09-21 | End-of-project deliverable set = the **production cut**: detailed product manual, user manual for developers, user manua | `H2 Production cut` (0.08) |
| D-56 | 2026-09-21 | Post-release: if the project is worth it, GitHub workflows (CI) so people can clone, prompt (AI-agent-driven) and update | `What the answers write` (0.12) |
| D-57 | 2026-09-21 | Post-release activity: build a reusable SKILL that captures every learning and process of this project (electrical, mech | `What the answers write` (0.07) |
| D-58 | 2026-09-21 | Connector J401 = **Amphenol V36-ADZ01-301000T** (45° contact lead-in), JLC **C22416096**, instead of the owner-supplied  | `F1 Acceptable verification sources` (0.07) |
| D-59 | 2026-09-21 | Every FEA/simulation report leads with pictures: colour-mapped 3D renderings (heat maps, deformed shapes, stress fields) | — |
| D-60 | 2026-09-21 | Morning answers: CC-136 (a) light pipe not fitted; CC-130/CC-140 no software refusal — software warns/throttles from the | `I. Identity, envelope, delegation (added by the first retro ` (0.07) |
| D-61 | 2026-09-21 | Blanket approval of the recommended answers in `docs/archive/OWNER_DETAILS_2026-09-21.md` §B–§E where low-risk; J401 sto | `F2 Stock policy and alternates` (0.18) |
| D-62 | 2026-09-21 | Renderings are part of the collected release/production-cut data (amends D-50 / D-55 / D-59) | — |
| D-65 | 2026-09-21 | First-pass case build at JLC3DP/JLCCNC; two-tone by parts: (1) legend / mark INLAY PLATES (SLA white, e.g. LEDO 6060 / 9 | `I. Identity, envelope, delegation (added by the first retro ` (0.18) |
| D-66 | 2026-09-21 | Release cut before the order: converge → final case checks → final cleanup + docs + reports → git tag → owner places the | `E2 Visual inspections` (0.2) |
| D-67 | 2026-09-22 | Production-cut phase pulled forward: run the D-55 / D-56 / D-57 plan now (docs/production/PRODUCTION_CUT_PLAN.md) plus t | `A2 Quantity and horizon` (0.13) |
| D-68 | 2026-09-22 | CC-183 option (A): lid START triangle for MODSEL aligned to L (`ui.start.SW302: L`) | `C1 Pieces` (0.2) |
| D-69 | 2026-09-22 | JLC board order PLACED for rev 0: board ed9431d7 / package out/MINI/fab/2026-09-22_ed9431d7 — PCB 5 panels (70 × 136, 1  | — |
| D-70 | 2026-09-22 | Repo re-organisation at the order: remove superseded case and PCB versions from the working tree (git history + tags kee | `C8 Two print targets and their fits` (0.11) |
| D-71 | 2026-09-22 | JLC case orders PLACED for rev 0 (case v3.13, tag mini-rev0-production-cut.1): JLC3DP — tray / shell / hood MJF PA12-HP  | `B4 Finish, mask colour, silk` (0.1) |
| D-72 | 2026-09-22 | D-70 phase 2 with the recommended answers ((a) docs/design kept, (b) early-era out/ dirs deleted except plan_smoke, (c)  | `I. Identity, envelope, delegation (added by the first retro ` (0.09) |
| D-73 | 2026-09-22 | Archive folders become deletions: superseded material leaves the working tree entirely; git history and the tags (mini-r | `E3 Coupons, dummies, first article` (0.14) |
| D-64 | 2026-09-21 | All (!) items of CC-143 / CC-148 / CC-157 / CC-166 nodded as recommended; each accepted deviation becomes a rev-1 backlo | `C7 Light pipes / windows / switch access` (0.25) |
| D-01 | 2026-09-13 | Firmware-controlled source selection, bus bridge, LED quiet | — |
| D-02 | 2026-09-13 | QSFP-DD connector and cage fixed to the Blackhole Galaxy UBB parts | — |
| D-03 | 2026-09-13 | AEC-CT2-MINI — the footprint coupon becomes a single-port FT2232H bench dongle | — |

## 8. What to do with this report

1. Fold every NEW row into the reference named in §5 (one generalised line; the source's number stays as the labelled worked example).
2. Extend the PARTIAL sections where the mechanism is missing.
3. Add one eval per §6 stub; run the smoke; bump SKILL.md `version`; write the CHANGELOG entry from §4.
4. Add a questionnaire question (with a recommended answer) per §7 topic that will recur.
5. Blind-review the skill again (two lenses), then tag.
