#!/usr/bin/env bash
# smoke/run_smoke.sh — drive the generic scripts end to end on the smoke project inside a throwaway git repo (never in place), installed the
# way a real project installs the skill: skill at vendor/hw-from-spec (stands in for the submodule; gitignored so `git archive HEAD` carries
# no content there, exactly like a submodule), RELATIVE symlink scripts -> vendor/hw-from-spec/scripts, project .venv -> the skill's venv.
set -e -o pipefail
HERE=$(cd "$(dirname "$0")" && pwd -P); SKILL=$(dirname "$HERE")
T=$(mktemp -d /tmp/hwfs_smoke_XXXX); [[ "$1" == "--keep" ]] || trap 'rm -rf $T' EXIT
R=$T/smoke; cp -R "$HERE" "$R"; rm -f "$R/run_smoke.sh"
mkdir -p "$R/vendor/hw-from-spec"; ln -s "$SKILL/scripts" "$R/vendor/hw-from-spec/scripts"; ln -s vendor/hw-from-spec/scripts "$R/scripts"
if [[ -x "$SKILL/.venv/bin/python" ]]; then ln -s "$SKILL/.venv" "$R/.venv"; export PY="$R/.venv/bin/python"
else echo "NOTE: no $SKILL/.venv (README step 2) — using python3 from PATH"; export PY=python3; fi
"$PY" -c 'import yaml' || { echo "FAIL: $PY has no pyyaml"; exit 1; }
printf 'vendor/hw-from-spec/\n.venv/\n' > "$R/.gitignore"
cd "$R"; git init -q; git add -A; git -c user.name=smoke -c user.email=s@s commit -qm "smoke inputs"
git archive HEAD | tar -tf - | grep -qx scripts || { echo "FAIL: the archive must carry the relative scripts symlink"; exit 1; }
say() { printf -- '\n--- %s\n' "$*"; }
md5of() { "$PY" -c 'import hashlib,sys; print(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
say "0 printed-enclosure DFM contract: the reference carries the measured rules and the census gate selftests without mesh libraries"
REF="$SKILL/references/dfm-printed-enclosure.md"
grep -q 'Every parallel-faced wall ≥ `wall_gate`, designed at `wall_gate + design_margin`' "$REF" || { echo "FAIL: $REF lost the wall rule"; exit 1; }
grep -q 'Every void ≥ `void_gate`' "$REF" || { echo "FAIL: $REF lost the void rule"; exit 1; }
grep -q 'No FREE-STANDING wedge' "$REF" || { echo "FAIL: $REF lost the free-wedge rule"; exit 1; }
grep -q 'Tangent fillets cut into ≥ gate walls are fine' "$REF" || { echo "FAIL: $REF lost the tangent-fillet allowance (B-04)"; exit 1; }
grep -q 'Engraved text is ALLOWED on MJF' "$REF" || { echo "FAIL: $REF lost the engraved-text allowance (B-03)"; exit 1; }
grep -q 'PA12 CAN do them' "$REF" || { echo "FAIL: $REF lost the snap-fit relabel (B-02)"; exit 1; }
grep -q 'One STL per page session' "$REF" || { echo "FAIL: $REF lost the one-STL-per-session rule"; exit 1; }
grep -q 'KEPT BELOW' "$REF" || { echo "FAIL: $REF lost the waiver-row rule"; exit 1; }
grep -q 'parseStatus == 2' "$REF" || { echo "FAIL: $REF lost the API-verdict rule (parseStatus 2)"; exit 1; }
grep -q 'computed at UPLOAD and does not depend on the process / material' "$REF" || { echo "FAIL: $REF lost the flag-independent-of-material rule"; exit 1; }
grep -q 'Save the RAW JSON response' "$REF" || { echo "FAIL: $REF lost the raw-JSON evidence rule (B-17)"; exit 1; }
grep -q 'LENGTH-DEPENDENT' "$REF" || { echo "FAIL: $REF lost the length-dependence rule"; exit 1; }
grep -q 'bbox-relative voxel / sampling resolution' "$REF" || { echo "FAIL: $REF lost the bbox-resolution hypothesis (B-05)"; exit 1; }
grep -q 'rim above a skirt-lap step must be \*\*≥ 2.0 mm\*\*' "$REF" || { echo "FAIL: $REF lost the rim-over-lap-step rule"; exit 1; }
grep -q '40 mm AND to the full part length' "$REF" || { echo "FAIL: $REF lost the full-length probe rule"; exit 1; }
grep -q 'Dimensional tolerance is the vendor' "$REF" || { echo "FAIL: $REF lost the vendor-tolerance rule (B-01)"; exit 1; }
grep -q '^## 11. SLA' "$REF" || { echo "FAIL: $REF lost the SLA rule set (B-09)"; exit 1; }
grep -q 'ironing_type: top` — never `topmost`' "$REF" && grep -q 'flush AMS colour body in the bed layers' "$REF" || { echo "FAIL: $REF lost the brand-mark options (§8.1)"; exit 1; }
grep -q 'filament_colour' "$REF" && grep -q 'No through-hole may open into the protected cavity' "$REF" || { echo "FAIL: $REF lost the Bambu CLI / dust-cap rules (§8.2 / §8.3)"; exit 1; }
grep -q '^\*\*C9 Brand marks' "$SKILL/references/kickoff-questionnaire.md" || { echo "FAIL: the questionnaire lost C9 (brand marks)"; exit 1; }
grep -q 'parseStatus == 2' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md §8.1 lost the API-verdict rule"; exit 1; }
grep -q 'length-dependent' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md §8.1 lost the length-dependence rule"; exit 1; }
grep -q 'Zero errors, zero warnings, no waivers' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the manufacturability bar (§1.2)"; exit 1; }
grep -q '0 Danger / 0 Warning' "$SKILL/templates/GATES.md" || { echo "FAIL: GATES.md lost the zero-warning prerequisite"; exit 1; }
grep -q '^| \*\*Case order\*\*' "$SKILL/templates/GATES.md" || { echo "FAIL: GATES.md lost the Case-order row (B-32)"; exit 1; }
grep -q 'parseStatus == 2' "$SKILL/templates/DFM_ROUND.md" || { echo "FAIL: DFM_ROUND.md lost the API-verdict column"; exit 1; }
grep -q '^## 5. Probes' "$SKILL/templates/DFM_ROUND.md" || { echo "FAIL: DFM_ROUND.md lost the probes section"; exit 1; }
grep -q -- '--gate-dir out/' "$SKILL/templates/CENSUS_GATE_ROWS.md" || { echo "FAIL: CENSUS_GATE_ROWS.md adopt line must use --gate-dir (C-01)"; exit 1; }
grep -q -- '--gate out/' "$SKILL/templates/CENSUS_GATE_ROWS.md" "$SKILL/references/case-pipeline.md" "$REF" && { echo "FAIL: a census adopt line still says --gate (C-01)"; exit 1; }
grep -q '^print_targets:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the print_targets block (B-33)"; exit 1; }
grep -q 'home_fdm:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the home_fdm target"; exit 1; }
grep -q '^fab_dfm:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the fab_dfm block"; exit 1; }
grep -q 'accepted_requires' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the DFM bar"; exit 1; }
grep -q '^## Quick start' "$SKILL/README.md" && grep -q '^## The retro loop' "$SKILL/README.md" && grep -q '^## The kickoff questionnaire' "$SKILL/README.md" || { echo "FAIL: README lost a required section"; exit 1; }
awk '/^```/{f=!f; next} f && length($0) > 90 {bad=1} END {exit bad}' "$SKILL/README.md" || { echo "FAIL: a fenced README line is over 90 characters (GitHub scrolls)"; exit 1; }
grep -q '^version: 0.6.0' "$SKILL/SKILL.md" && grep -q '^## 0.6.0' "$SKILL/CHANGELOG.md" || { echo "FAIL: SKILL.md version and CHANGELOG entry disagree"; exit 1; }
grep -q 'numpy trimesh scipy shapely' "$SKILL/README.md" || { echo "FAIL: README lost the mesh-library install line (C-06)"; exit 1; }
grep -q 'vendor/hw-from-spec/.venv' "$SKILL/README.md" || { echo "FAIL: README lost the one install block (C-02 / C-12)"; exit 1; }
test -f "$SKILL/references/kickoff-questionnaire.md" || { echo "FAIL: references/kickoff-questionnaire.md missing"; exit 1; }
grep -q 'AskUserQuestion' "$SKILL/SKILL.md" && grep -q '^### 0.1 The kickoff questionnaire' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the kickoff step (§0.1)"; exit 1; }
grep -c 'RECOMMENDED' "$SKILL/references/kickoff-questionnaire.md" | awk '$1 >= 30 {ok=1} END {exit !ok}' || { echo "FAIL: the questionnaire lost its recommended answers"; exit 1; }
grep -q '^| D1 | the manufacturability bar' "$SKILL/templates/KICKOFF_ANSWERS.md" || { echo "FAIL: KICKOFF_ANSWERS.md lost the bar row"; exit 1; }
grep -q 'references/pcb-layout-dfm.md' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the layout reference (C-07)"; exit 1; }
grep -q -E 'p2s|presets\.P2S|AEC-CT2|lap\.ring_down' "$SKILL/SKILL.md" "$SKILL/README.md" "$SKILL/templates"/*.md "$SKILL/templates"/*.yaml && { echo "FAIL: a source-project identifier leaked into SKILL / README / templates (C-15 / B-34)"; exit 1; }
grep -q '^## 13. Retro' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the retro phase (§13)"; exit 1; }
"$PY" scripts/thin_wall_census.py --selftest
"$PY" scripts/skill_retro.py --selftest
say "1 fab package of record keyed on the board md5"
MD5=$(md5of kicad/smoke/smoke.kicad_pcb); PKG=out/fab/2026-01-03_${MD5:0:8}; mkdir -p $PKG
printf 'board kicad/smoke/smoke.kicad_pcb\nmd5 %s\ncommit %s\nbuilt 2026-01-03\nsegments 1\nvias 0\n' $MD5 $(git rev-parse --short HEAD) > $PKG/board_id.txt
printf 'PNG-stub-panel-top-render-------------------------------------------------\n' > $PKG/panel_top.png
mkdir -p out/case/v0.1-smoke; printf 'PNG-stub-case-iso-render----------------------------------------------------\n' > out/case/v0.1-smoke/iso.png
say "2 known_issues (generated index)";          $PY scripts/known_issues.py
say "3 traceability (matrix)";                   $PY scripts/traceability.py || true      # exit 1 here would mean FAILED rows: the smoke has none
say "4 dfm_check (grading the measurer's items against fab_dfm.bar; report to fab_dfm.report)"; $PY scripts/dfm_check.py
say "5 collect_renders";                          $PY scripts/collect_renders.py
say "5b assembly_guide (keyed renders via the stub renderer)"; $PY scripts/assembly_guide.py; $PY scripts/assembly_guide.py --check
say "5c reorg_paths --check (layout of record: no old literal, no dangling docs/ path)"; $PY scripts/reorg_paths.py --check
say "6 release_report (DRAFT expected)";          $PY scripts/release_report.py
grep -q '^\*\*STATUS: DRAFT\*\*' docs/release/PCB_DESIGN_REPORT.md || { echo "FAIL: report not DRAFT"; exit 1; }
say "7 every --check must pass";                  $PY scripts/known_issues.py --check; $PY scripts/assembly_guide.py --check; $PY scripts/traceability.py --check; $PY scripts/dfm_check.py --check; $PY scripts/collect_renders.py --check; $PY scripts/release_report.py --check
say "8 commit + handoff header";                  git add -A; git -c user.name=smoke -c user.email=s@s commit -qm "generated records"; $PY scripts/handoff_header.py
$PY scripts/handoff_header.py | grep -q 'MATCH' || { echo "FAIL: handoff header has no MATCH"; exit 1; }
say "9 adopt gates incl. the clone gate on git archive HEAD"; scripts/adopt_gates.sh
say "10 the owner's line flips the banner; --check catches the stale report"
printf '| **Release** | Reports RELEASED | the owner line below | clear to build — owner, 2026-01-04, board %s |\n' ${MD5:0:8} >> docs/governance/GATES.md
if $PY scripts/release_report.py --check >/dev/null; then echo "FAIL: --check missed the stale report"; exit 1; fi
$PY scripts/release_report.py | grep -q RELEASED || { echo "FAIL: not RELEASED"; exit 1; }
say "SMOKE OK — DRAFT report was $R/docs/release/PCB_DESIGN_REPORT.md (RELEASED after the owner line); traceability census:"
grep -A4 '^## Census' docs/governance/TRACEABILITY.md | tail -3
