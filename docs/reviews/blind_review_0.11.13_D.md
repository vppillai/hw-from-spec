<!-- blind reviewer D: GPT-5.4 (GitHub Copilot CLI); artefact + checklist only; 2026-10-08 -->
# Blind review D — hw-from-spec 0.11.13 (domain expert (PCB and printed-enclosure DFM, process))
## Setup (what you ran, where)
- Initialized report at `<scratch>/reports/D_gpt-5.4.md`; review scope is `SKILL_DIR=<scratch>/skill`.
- Read `SKILL.md`, `references/*`, `templates/*`, and the measuring / lint scripts with `view`/`rg`; extracted numeric lines to `WORK_DIR/numeric_extract.tsv`.
- Ran selftests with `<project>/.venv/bin/python` for `heatmap_count.py`, `style_lint.py`, `doc_voice_lint.py`, `stability.py`, `thin_wall_census.py`, `print_dfm.py`, and `thin_wall_check.py`.
- Ran two probes in `WORK_DIR`: one against `thin_wall_census.pure_gate()` for acceptance re-match behavior, one against `style_lint.py` for passive / future-tense coverage.

## Findings
| id | sev | where | what | evidence | suggested fix |
|---|---|---|---|---|---|
| D-1 | BLOCKER | `SKILL.md:353`; `references/dfm-printed-enclosure.md:142`; `scripts/thin_wall_census.py:24-25,267-268` | The pure census gate does not re-match accepted clusters by class+bbox as the docs promise; it only checks reason/date/evidence text. A moved acceptance bbox can still pass adopt. | **M:** docs say “re-matched every run” / bbox+class match; code at `267-268` checks only `reason,date,evidence`. Probe: Python import of `pure_gate()` returned `[]` with current yaml bbox moved to `[100..110]`. **J:** stale thin-wall waivers can ship. | In `pure_gate()`, re-check current `accepted` entries against stored class+bbox, not only reason/date/evidence; add a selftest for bbox drift. |
| D-2 | MAJOR | `references/dfm-printed-enclosure.md:25,609`; `templates/CENSUS_GATE_ROWS.md:7` | The worked-example owner-bar margin is contradictory: the rule says `design_margin ≥ 0.3`, but the emitted census-row template still documents `design_margin` as `0.1`. | **M:** reference: “`design_margin` ≥ 0.3”; template: “owner bar, 0.1”. **J:** a user who copies the row text can rebuild the exact yellow-at-gate failure the rule was meant to prevent. | Update `templates/CENSUS_GATE_ROWS.md` to 0.3 and align any nearby worked-example prose. |
| D-3 | MAJOR | `references/dfm-printed-enclosure.md:548-550`; `templates/20-design/dfm_processes.yaml:56-59` | The SLA reference and the actual SLA process row disagree on minimum feature / hole numbers. The prose allows `hole Ø ≥ 0.5`; the shipped row gates holes at `1.0` and long slots at `1.0`. | **M:** prose: “feature 0.3–0.5… hole Ø ≥ 0.5”; row: `feature_min 0.5`, `detail_min 0.5`, `void_min 1.0`, `hole_min 1.0`. **J:** one source is wrong; users will either over-design or fail the gate unexpectedly. | Pick one SLA floor, cite the source on both files, and keep the prose and `jlc_sla_9600` row byte-consistent. |
| D-4 | MAJOR | `references/pcb-layout-dfm.md:15,77,86` | The PCB DFM rule says “design strictly greater than the published minimum”, but the worked-example table sets inner PTH hole-to-copper to the published limit `0.30`. | **M:** rule text says strict-greater; table row says `0.20 via / 0.30 PTH | 0.30`. **J:** if the fab viewer warns on equality, this advice recreates the exact round-trip the mirror is meant to avoid. | Raise the worked-example design value above `0.30` or document a narrow exception and why equality is safe for that check. |
| D-5 | MAJOR | `references/dfm-printed-enclosure.md:244,333,452`; `scripts/*.py` search | The home-FDM text claims g-code / 3MF enforcement that the release does not ship: visible-face support detection, floating-region FAIL, and purge / filament extraction. | **M:** docs require `; FEATURE: Support`, floating-region FAIL, and `slice_info.config` / g-code reads; script search found only `now_pages.py` consuming sidecar fields, no parser/checker. **J:** support scars and bad slice states can escape to the print bench. | Add a slicer-result checker script and wire it into the FDM adopt / kit flow; or downgrade the prose from “asserted / FAIL” to manual review. |
| D-6 | MINOR | `SKILL.md:78,500`; `references/writing-style.md:5,12,20`; `scripts/style_lint.py:8-13` | The day-1 style gate does not fail future tense or passive voice, although the writing standard says the measurable rules are checked and the gate is mandatory. | **M:** probe file `You will read… / The file is opened…` returned `style_lint: 0 hit(s)`; `--report` showed `passive 1`, `will 1`. **J:** the gate reports these smells but does not enforce them. | Either tighten `style_lint.py` to fail configured `will` / passive hits, or narrow the docs to the rules it actually gates. |

## Checked and correct
- `scripts/print_dfm.py --selftest` passed; the fixtures exercised W/R/Z/F/K/P/V/H/O/B/S/C/M, gate behavior, and validation grouping.
- `scripts/thin_wall_census.py --selftest` passed; wall / wedge / void / opposing / legend-box / pure-gate cases behaved as documented.
- `scripts/stability.py --selftest` passed; volume-centroid, support-margin, and improper-placement checks matched the documented math.
- `scripts/heatmap_count.py --selftest` passed for RGB and RGBA PNG inputs.
- The rewritten references `pitfalls.md`, `dfm-printed-enclosure.md`, `vendor-review.md`, `case-pipeline.md`, `pcb-layout-dfm.md`, and `fab-dfm.md` passed both `style_lint.py` and `doc_voice_lint.py`.
- `scripts/print_dfm.py` point-contact implementation matches `references/print-dfm.md`: 15 section planes and `10 × neck_max` ring-path separation.

## Coverage limits (what you could not run or read)
- Did not read `SKILL_DIR/docs/reviews/*` per brief.
- Did not run KiCad, OpenSCAD, a slicer, or live vendor quote pages per brief; CAD-bound measurers and live form behavior were reviewed from frozen prose/scripts only.
- Did not verify cited vendor numbers against the live web because the brief forbids internet research on this skill.
