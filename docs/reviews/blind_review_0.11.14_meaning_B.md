<!-- blind meaning reviewer B: GPT-5.6 Terra (GitHub Copilot CLI); the 0.11.13 -> 0.11.14 prose diff only; 2026-10-08 -->
| file | hunk (first words of the removed text) | verdict | before -> after (for CHANGED / UNCLEAR / INTENDED) |
|---|---|---|---|
| README.md | A Claude Code skill that takes | SAME | |
| README.md | vendors' verdicts (a vendor flag | SAME | |
| README.md | ## Use in a new project | CHANGED | `## Use in a new project` → `Run the kickoff questionnaire first ... Its A0 answer sets the scope of the copy block in step 4.` |
| README.md | 5. Follow `SKILL.md` §0: the kickoff questionnaire | CHANGED | `Follow ... the kickoff questionnaire, ENV record ...` → `Follow ... from step 3: project.yaml, ENV record ...` |
| README.md | Before the spec is read, the agent asks | SAME | |
| SKILL.md | Install — ONE layout, ONE block | SAME | |
| SKILL.md | The owner writes the gate line | SAME | |
| SKILL.md | 1. Prerequisites first | INTENDED | Added the named enforcement allocation: `Who enforces each item ... The owner reads both at the case-order gate ...` |
| SKILL.md | A generator that owns part | SAME | |
| SKILL.md | Tags: **[V]** verified live | SAME | |
| SKILL.md | 3. Reviewers (the review round | SAME | |
| SKILL.md | **The `case_dfm` role** | SAME | |
| SKILL.md | `references/pcb-layout-dfm.md`. A routed board | SAME | |
| SKILL.md | `20-design/case.yaml` → OpenSCAD source | SAME | |
| SKILL.md | hole-calibrated pad-1 overlay | SAME | |
| SKILL.md | After every production cut | SAME | |
| references/agent-ops.md | One coordinator; workers own disjoint FILES | INTENDED | `kicad/`, `design/<board>_*.yaml`, `out/**/case/` → `30-board/kicad/`, `20-design/<board>_*.yaml`, `40-case/` (numbered-tree path remap) |
| references/agent-ops.md | **A fork subagent stops | SAME | |
| references/agent-ops.md | Every checker is READ-ONLY | INTENDED | `erc.json` into `out/` → `erc.json` into `30-board/layout/` (numbered-tree path remap) |
| references/agent-ops.md | Freeze: clean tree | SAME | |
| references/agent-ops.md | Worked example — one measured round | SAME | |
| references/case-pipeline.md | The chain of record assumes every body | SAME | |
| references/case-pipeline.md | A set is one folder per PRINT TARGET | SAME | |
| references/case-pipeline.md | FDM (owner's printer, target | SAME | |
| references/case-pipeline.md | Inward ray-cast rule | SAME | |
| references/case-pipeline.md | ≈ 45 min. Run case FEA | SAME | |
| references/case-pipeline.md | **Fit rows per degree of freedom | SAME | |
| references/case-pipeline.md | The feature directions come from | SAME | |
| references/case-pipeline.md | The render + STL + interference chain | INTENDED | `UL 94 / Tg` → `UL 94 / HDT` (rating-key correction); `out/**/scratch/` → `build/**/_check/` (numbered-tree path remap) |
| references/cnc-enclosure.md | Short by design: the one quote | SAME | |
| references/cnc-enclosure.md | The vendor's DFM clean | SAME | |
| references/dfm-printed-enclosure.md | **Every number here carries a tag** | INTENDED | `the 0.1 margin` → `the 0.3 margin`; `design_margin` remains `≥ 0.3` (design-margin correction) |
| references/dfm-printed-enclosure.md | **Engraved text is ALLOWED on MJF** | SAME | |
| references/dfm-printed-enclosure.md | Retention is a kickoff question | SAME | |
| references/dfm-printed-enclosure.md | A symmetric assembly built from identical | INTENDED | `UL 94 rating and Tg / softening point` → `UL 94 rating and HDT at 0.45 MPa (the hdt_c key)` (rating-key correction) |
| references/dfm-printed-enclosure.md | The census gates the DESIGN margin | CHANGED | No axis-aligned-band condition or special diagonal/ring handling → `The band is an axis-aligned measure ... Re-measure a diagonal or ring wedge FAIL across the edge before you accept or fix it.` |
| references/dfm-printed-enclosure.md | 3. **The flag is computed at UPLOAD | INTENDED | `scripts/heatmap_count.py ... must print 0 / 0` → `It reads each pixel in HSV, so shaded faces and amber count too.` (heat-map colour-read fix) |
| references/dfm-printed-enclosure.md | numbers are **[owner bar]** | INTENDED | `wall gate ... (0.6 = 3 layers)` → `colour layers × layer height (default 2 × 0.20 = 0.4; 3 layers = 0.6)` (colour-wall gate correction) |
| references/dfm-printed-enclosure.md | **Print MOUTH DOWN** | SAME | |
| references/dfm-printed-enclosure.md | `sparse_infill_density: 100%` | SAME | |
| references/dfm-printed-enclosure.md | --assemble --arrange 0 | SAME | |
| references/dfm-printed-enclosure.md | 4. **Reply template** | SAME | |
| references/fab-dfm.md | A PCB fab's engineer asks | SAME | |
| references/fab-dfm.md | CAD DRC at the fab's published capability | SAME | |
| references/fab-dfm.md | 1. **Thresholds file** | SAME | |
| references/fab-dfm.md | 4. **Acceptances** by refdes | SAME | |
| references/fab-dfm.md | The morning after an order is placed | SAME | |
| references/fdm-print-optimisation.md | **The rule.** Every knob used | SAME | |
| references/fea-stage.md | Gmsh (Python API; boxes | SAME | |
| references/kickoff-questionnaire.md | Owner's words (2026-09-28) | SAME | |
| references/kickoff-questionnaire.md | `AskUserQuestion` tool | SAME | |
| references/kickoff-questionnaire.md | **A4 Enclosure process and material | SAME | |
| references/kickoff-questionnaire.md | **B7 Test points and self-documenting silk** | SAME | |
| references/kickoff-questionnaire.md | **Owner inputs (a symmetric assembly | SAME | |
| references/kickoff-questionnaire.md | **Owner inputs (colour):** | SAME | |
| references/kickoff-questionnaire.md | **C8a — which `20-design/dfm_processes.yaml` | SAME | |
| references/kickoff-questionnaire.md | **E4 Vendor DFM before | SAME | |
| references/kickoff-questionnaire.md | **F1 Acceptable verification sources. | SAME | |
| references/part-verification.md | dealers** (price, stock). So: | SAME | |
| references/part-verification.md | The `PARTS_VERIFICATION.md` columns | SAME | |
| references/pcb-layout-dfm.md | Every quantitative rule below | INTENDED | `design/dfm_thresholds.json` → `20-design/dfm_thresholds.json` (numbered-tree path remap) |
| references/pcb-layout-dfm.md | warning threshold as Warning) | SAME | |
| references/pcb-layout-dfm.md | The routed board + the router's | INTENDED | `design/...`, `out/G2/`, `out/dfm_items.json` / `out/dfm.json` → `20-design/...`, `80-reviews/G2/`, `30-board/layout/...` (numbered-tree path remap) |
| references/pcb-layout-dfm.md | net classes must be exported | SAME | |
| references/pcb-layout-dfm.md | Copy the fab's table into | INTENDED | `design/dfm_thresholds.json` → `20-design/dfm_thresholds.json` (numbered-tree path remap) |
| references/pcb-layout-dfm.md | Copy the fab's table into | INTENDED | References to `design/<board>_board.yaml` and `out/G2/` → `20-design/<board>_board.yaml` and `80-reviews/G2/` (numbered-tree path remap) |
| references/pcb-layout-dfm.md | Copy the fab's table into | INTENDED | `design/<fab>_rotation.yaml` → `20-design/<fab>_rotation.yaml` (numbered-tree path remap) |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | INTENDED | `Design every gated wall 0.1 over` → `Design every gated wall at least 0.3 over` (design-margin correction) |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | SAME | |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | INTENDED | `out/` paths → numbered-tree/build paths (numbered-tree path remap) |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | SAME | |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | SAME | |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | INTENDED | `design/` → `20-design/` (numbered-tree path remap) |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | INTENDED | `out/**/scratch/` → `build/**/_check/` (numbered-tree path remap) |
| references/pitfalls.md | that project's records and in CHANGELOG.md. | SAME | |
| references/print-dfm.md | **Why it exists.** A vendor's | SAME | |
| references/print-dfm.md | feature however small its area | INTENDED | 2-D legacy legend boxes that `spans every Z` → documented 3-D `(x0, y0, z0, x1, y1, z1, ...)` legend boxes (Z-band box fix) |
| references/print-dfm.md | project has none yet), verdicts | SAME | |
| references/print-dfm.md | same face at a grazing angle. | SAME | |
| references/print-dfm.md | same face at a grazing angle. | SAME | |
| references/print-kit.md | A kit is reviewed as a technician | SAME | |
| references/print-kit.md | 3. **Assembly sequence**, numbered | SAME | |
| references/print-kit.md | Rules the entry point makes checkable: | SAME | |
| references/print-kit.md | START_HERE, every print sheet | SAME | |
| references/project-yaml.md | tools: | INTENDED | `out/dfm_items.json` / `out/dfm.json` → `30-board/layout/dfm_items.json` / `30-board/layout/dfm.json` (numbered-tree path remap) |
| references/project-yaml.md | print_targets: | INTENDED | `tg_c` → `hdt_c` (rating-key correction) |
| references/project-yaml.md | reorg: | INTENDED | Legacy `out/<board>/...` path-map annotations retained/remapped with allowed markers (numbered-tree path remap) |
| references/project-yaml.md | renders: | INTENDED | `out/case/{CASE_VERSION}/renders/iso.png` → `40-case/vendor_mjf/pictures/iso.png` (numbered-tree path remap) |
| references/project-yaml.md | gen/ scripts/ tools/ lib/ | SAME | |
| references/project-yaml.md | Seven rules make the tree | SAME | |
| references/project-yaml.md | is this layout. Changing it later | INTENDED | `out/.../census` → `40-case/<set>/checks/census/...` (numbered-tree path remap) |
| references/release-and-cut.md | Everything downstream is keyed | SAME | |
| references/release-and-cut.md | discarded with `git checkout` | SAME | |
| references/release-and-cut.md | Annotated tag (`<board>-rev<n>-order` | SAME | |
| references/release-and-cut.md | orderable state and does not substitute | SAME | |
| references/release-and-cut.md | the SOP's companion cell points | INTENDED | `design/` in re-layout live-citation scope → `20-design/` (numbered-tree path remap) |
| references/schematic-phase.md | The schematic generator is project code | INTENDED | `design/` paths → `20-design/` paths (numbered-tree path remap) |
| references/schematic-phase.md | board: | SAME | |
| references/schematic-phase.md | no_connect: [U1.7] | INTENDED | `design/` → `20-design/` (numbered-tree path remap) |
| references/schematic-phase.md | feeds the `netlist_net` checks | SAME | |
| references/schematic-phase.md | board as MISSING at G1 | INTENDED | `out/G1/` → `80-reviews/G1/` (numbered-tree path remap) |
| references/software-track.md | 1. **Bring-up tool** | SAME | |
| references/vendor-review.md | the owner's account. Record template: | SAME | |
| references/vendor-review.md | the owner's account. Record template: | SAME | |
| references/vendor-review.md | any mark-shaped body or pocket | SAME | |
| references/vendor-review.md | any mark-shaped body or pocket | SAME | |
| references/vendor-review.md | drafts it into the record. | SAME | |
| references/vendor-review.md | exchange. At G2 / package build | SAME | |
| templates/.gitignore | out/scratch/ | INTENDED | `out/scratch/` → `build/` (numbered-tree path remap) |
| templates/10-spec/KICKOFF_ANSWERS.md | answered question is a defect | CHANGED | `kickoff.sourcing.stock_floor` → `kickoff.sourcing.stock_floor, kickoff.sourcing.attrition`; `kickoff.software.modes` → `kickoff.software.modes, kickoff.software.posture` |
| templates/10-spec/SPEC.md | Every requirement has an ID | SAME | |
| templates/10-spec/datasheet_notes/_TEMPLATE.md | Datasheet: <live URL | SAME | |
| templates/20-design/traceability.yaml | stages: | INTENDED | `design/{{BOARD}}.yaml` → `20-design/{{BOARD}}.yaml` (numbered-tree path remap) |
| templates/90-log/GATES.md | `_not yet approved_`. The release reports | INTENDED | M1 prerequisite adds `the double-blind drawing round merged`; Case order adds `(both) the double-blind drawing round merged` (drawing-round gate-row fix) |
| templates/CENSUS_GATE_ROWS.md | `(`references/project-yaml.md`): `{{GATE}}` | INTENDED | `design_margin` owner bar `0.1` → `≥ 0.3` (design-margin correction) |
| templates/CENSUS_GATE_ROWS.md | INFO table (no threshold | INTENDED | `UL 94 / Tg` → `UL 94 / HDT at 0.45 MPa` (rating-key correction) |
| templates/CLAUDE.md | written specification, for fabrication | SAME | |
| templates/CLAUDE.md | written specification, for fabrication | SAME | |
| templates/CLAUDE.md | written specification, for fabrication | SAME | |
| templates/DFM_ROUND.md | uploaded, canonical STL) | INTENDED | `Tg / softening {{TG}}` → `HDT (0.45 MPa) {{HDT}}` (rating-key correction) |
| templates/DFM_ROUND.md | same body: confirm both reads | SAME | |
| templates/RELEASE_NOTES.md | > **State at this release | SAME | |
| templates/REVIEW_HANDOFF.md | _(G0 round: board, package | INTENDED | `out/.../case/<preset>/stl/*.stl` → `40-case/<set>/parts/*.stl` (numbered-tree path remap) |
| templates/ci/README.md | cp "$S"/{setup_linux,nightly,release_archive}.sh | INTENDED | `out/release_artefacts` / `out/*/erc.json` → `build/release_artefacts` / `30-board/layout/erc.json` (numbered-tree path remap) |
| templates/ci/README.md | grep -n '{{PROJECT_' | INTENDED | `out/release_artefacts` → `build/release_artefacts` (numbered-tree path remap) |
| templates/ci/release.yml | jobs: | INTENDED | `out/release_artefacts` → `build/release_artefacts` (numbered-tree path remap) |
| templates/production_cut.yaml | deliverables: | INTENDED | `UL94/Tg` → `UL94/HDT` (rating-key correction) |
| templates/project.yaml | kickoff: | CHANGED | Added `attrition: {{F2_ATTRITION}}` to sourcing and `posture: {{G1_POSTURE}}` to software; neither key existed before. |
| templates/project.yaml | print_targets: | INTENDED | `tg_c` → `hdt_c` (rating-key correction) |
| templates/project.yaml | print_targets: | INTENDED | `tg_c` → `hdt_c` (rating-key correction) |
| templates/project.yaml | print_targets: | INTENDED | `wall_gate: 0.6` → `wall_gate: 0.4` (colour-wall gate correction) |
| templates/project.yaml | arrival_checklist: | INTENDED | Legacy `out/<board>/...` mappings annotated with allowed legacy-path markers (numbered-tree path remap) |

**Counts:** hunks reviewed **132**; SAME **85**; INTENDED **42**; CHANGED **5**; UNCLEAR **0**. The version-only `SKILL.md` hunk is excluded as instructed.

| file | hunk (first words of the removed text) | verdict | before -> after |
|---|---|---|---|
| README.md | ## Use in a new project | CHANGED | `## Use in a new project` → `Run the kickoff questionnaire first ... Its A0 answer sets the scope of the copy block in step 4.` |
| README.md | 5. Follow `SKILL.md` §0: the kickoff questionnaire | CHANGED | `Follow ... the kickoff questionnaire, ENV record ...` → `Follow ... from step 3: project.yaml, ENV record ...` |
| references/dfm-printed-enclosure.md | The census gates the DESIGN margin | CHANGED | No axis-aligned-band condition or special diagonal/ring handling → `The band is an axis-aligned measure ... Re-measure a diagonal or ring wedge FAIL across the edge before you accept or fix it.` |
| templates/10-spec/KICKOFF_ANSWERS.md | answered question is a defect | CHANGED | `kickoff.sourcing.stock_floor` → `kickoff.sourcing.stock_floor, kickoff.sourcing.attrition`; `kickoff.software.modes` → `kickoff.software.modes, kickoff.software.posture` |
| templates/project.yaml | kickoff: | CHANGED | Added `attrition: {{F2_ATTRITION}}` to sourcing and `posture: {{G1_POSTURE}}` to software; neither key existed before. |
