#!/usr/bin/env bash
# smoke/run_smoke.sh — drive the generic scripts end to end on the smoke project inside a throwaway git repo (never in place), installed the
# way a real project installs the skill: skill at vendor/hw-from-spec (stands in for the submodule; gitignored so `git archive HEAD` carries
# no content there, exactly like a submodule), RELATIVE symlink scripts -> vendor/hw-from-spec/scripts, project .venv -> the skill's venv.
set -e -o pipefail
HERE=$(cd "$(dirname "$0")" && pwd -P); SKILL=$(dirname "$HERE"); CALLER=$PWD
T=$(mktemp -d "${TMPDIR:-/tmp}/hwfs_smoke_XXXX"); [[ "$1" == "--keep" ]] || trap 'rm -rf $T' EXIT
R=$T/smoke; cp -R "$HERE" "$R"; rm -f "$R/run_smoke.sh"
mkdir -p "$R/vendor/hw-from-spec"; ln -s "$SKILL/scripts" "$R/vendor/hw-from-spec/scripts"; ln -s vendor/hw-from-spec/scripts "$R/scripts"
# interpreter: the skill's .venv, else the caller's project .venv (README Quick start runs the smoke from the project root), else python3 — the first with pyyaml
VENV=""; for c in "$CALLER/.venv" "$SKILL/.venv"; do [[ -x "$c/bin/python" ]] && "$c/bin/python" -c 'import yaml' 2>/dev/null && { VENV=$c; break; }; done
if [[ -n "$VENV" ]]; then ln -s "$VENV" "$R/.venv"; export PY="$R/.venv/bin/python"; echo "python: $VENV/bin/python"
else echo "NOTE: no .venv with pyyaml at $SKILL or $CALLER — using python3 from PATH"; export PY=python3; fi
export PYTHON="$PY"                                       # the shell gates (adopt_gates.sh / clone_gate.sh) honour $PYTHON first
"$PY" -c 'import yaml' || { echo "FAIL: $PY has no pyyaml (README Install step 2: uv pip install --python .venv/bin/python pyyaml ...)"; exit 1; }
if "$PY" -c 'import numpy, trimesh, scipy, shapely, rtree, networkx, mapbox_earcut' 2>/dev/null; then MESH=1; else MESH=""; echo "NOTE: mesh libraries absent in $PY — section 0d (print DFM on meshes) will be SKIPPED; install numpy trimesh scipy shapely rtree networkx mapbox-earcut to run it"; fi
md5of_py() { "$PY" -c 'import hashlib,sys; print(hashlib.md5(open(sys.argv[1],"rb").read()).hexdigest())' "$1"; }
printf 'vendor/hw-from-spec/\n.venv/\n' > "$R/.gitignore"
cd "$R"; git init -q; git add -A; git -c user.name=smoke -c user.email=s@s commit -qm "smoke inputs"
git archive HEAD | tar -tf - | grep -qx scripts || { echo "FAIL: the archive must carry the relative scripts symlink"; exit 1; }
say() { printf -- '\n--- %s\n' "$*"; }
md5of() { md5of_py "$1"; }
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
grep -q 'bbox-relative resolution' "$REF" || { echo "FAIL: $REF lost the bbox-resolution hypothesis (B-05)"; exit 1; }
grep -q 'rim above a skirt-lap step ≥ 2.0 mm' "$REF" || { echo "FAIL: $REF lost the rim-over-lap-step rule"; exit 1; }
grep -q 'a short length AND to the full part' "$REF" || { echo "FAIL: $REF lost the full-length probe rule"; exit 1; }
grep -q 'Dimensional tolerance is the vendor' "$REF" || { echo "FAIL: $REF lost the vendor-tolerance rule (B-01)"; exit 1; }
grep -q '^## 11. SLA' "$REF" || { echo "FAIL: $REF lost the SLA rule set (B-09)"; exit 1; }
grep -q 'ironing_type: top` — never `topmost`' "$REF" && grep -q 'flush AMS colour body in the bed layers' "$REF" || { echo "FAIL: $REF lost the brand-mark options (§8.1)"; exit 1; }
grep -q 'filament_colour' "$REF" && grep -q 'No through-hole may open into the protected cavity' "$REF" || { echo "FAIL: $REF lost the Bambu CLI / dust-cap rules (§8.2 / §8.3)"; exit 1; }
grep -q '^\*\*C9 Brand marks' "$SKILL/references/kickoff-questionnaire.md" || { echo "FAIL: the questionnaire lost C9 (brand marks)"; exit 1; }
grep -q '^\*\*C10 Print kit' "$SKILL/references/kickoff-questionnaire.md" || { echo "FAIL: the questionnaire lost C10 (print kit)"; exit 1; }
KIT="$SKILL/references/print-kit.md"; test -f "$KIT" || { echo "FAIL: references/print-kit.md missing"; exit 1; }
grep -q 'Stack-and-mark polarity rule' "$KIT" && grep -q 'Dry attract check before any CA' "$KIT" && grep -q 'feet LAST' "$KIT" || { echo "FAIL: print-kit.md lost the magnet / feet sequence"; exit 1; }
grep -q '`None`, `nan`, a `{name}` brace' "$KIT" && grep -q 'Print-sheet names = project-file names' "$KIT" && grep -q 'Watertight row per exported STL' "$KIT" || { echo "FAIL: print-kit.md lost the kit text gate / naming / watertight rules"; exit 1; }
grep -q 'bridged strips sit one layer BELOW them' "$REF" && grep -q 'exactly 45.0° is AT the overhang limit' "$REF" && grep -q 'Ship a bracket plate' "$REF" || { echo "FAIL: $REF lost §8.4 / §8.5 (plate seat, 45° limit, bracket plate)"; exit 1; }
grep -q 'print kit is a deliverable row' "$SKILL/references/release-and-cut.md" || { echo "FAIL: release-and-cut.md lost the kit deliverable row"; exit 1; }
grep -q 'The machine can panic under load' "$SKILL/references/agent-ops.md" || { echo "FAIL: agent-ops.md lost the small-commits rule"; exit 1; }
grep -q "the vendor's analysis API response, never a page" "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md §8.1 lost the API-verdict rule"; exit 1; }
grep -q 'length-dependent' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md §8.1 lost the length-dependence rule"; exit 1; }
grep -q 'Zero errors, zero warnings, no waivers' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the manufacturability bar (§1.2)"; exit 1; }
grep -q "0 open at either of the fab's grades" "$SKILL/templates/GATES.md" || { echo "FAIL: GATES.md lost the zero-warning prerequisite"; exit 1; }
grep -q '^| \*\*Case order\*\*' "$SKILL/templates/GATES.md" || { echo "FAIL: GATES.md lost the Case-order row (B-32)"; exit 1; }
grep -q '{{VERDICT_API}}' "$SKILL/templates/DFM_ROUND.md" && grep -q 'parseStatus == 2' "$SKILL/templates/DFM_ROUND.md" || { echo "FAIL: DFM_ROUND.md lost the API-verdict slot"; exit 1; }
grep -q '^## 5. Probes' "$SKILL/templates/DFM_ROUND.md" || { echo "FAIL: DFM_ROUND.md lost the probes section"; exit 1; }
grep -q -- '--gate-dir out/' "$SKILL/templates/CENSUS_GATE_ROWS.md" && grep -q -- 'print_dfm.py --gate out/' "$SKILL/templates/CENSUS_GATE_ROWS.md" || { echo "FAIL: CENSUS_GATE_ROWS.md must carry both adopt lines (census --gate-dir + print_dfm --gate)"; exit 1; }
grep -q -- 'thin_wall_census.py --gate out/' "$SKILL/templates/CENSUS_GATE_ROWS.md" "$SKILL/references/case-pipeline.md" "$REF" && { echo "FAIL: a census adopt line says --gate instead of --gate-dir"; exit 1; }
grep -q '^print_targets:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the print_targets block (B-33)"; exit 1; }
grep -q 'home_fdm:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the home_fdm target"; exit 1; }
grep -q '^fab_dfm:' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the fab_dfm block"; exit 1; }
grep -q 'accepted_requires' "$SKILL/templates/project.yaml" || { echo "FAIL: templates/project.yaml lost the DFM bar"; exit 1; }
grep -q '^## Quick start' "$SKILL/README.md" && grep -q '^## The retro loop' "$SKILL/README.md" && grep -q '^## The kickoff questionnaire' "$SKILL/README.md" || { echo "FAIL: README lost a required section"; exit 1; }
awk '/^```/{f=!f; next} f && length($0) > 90 {bad=1} END {exit bad}' "$SKILL/README.md" || { echo "FAIL: a fenced README line is over 90 characters (GitHub scrolls)"; exit 1; }
V=$(sed -n 's/^version: //p' "$SKILL/SKILL.md"); [[ -n "$V" ]] && grep -q "^## $V " "$SKILL/CHANGELOG.md" && grep -q "version $V" "$SKILL/README.md" || { echo "FAIL: SKILL.md version ($V) has no CHANGELOG entry or README line"; exit 1; }
grep -q 'numpy trimesh scipy shapely rtree networkx mapbox-earcut' "$SKILL/README.md" || { echo "FAIL: README lost the mesh-library install line (C-06 / 0.8.0 print DFM deps)"; exit 1; }
grep -q 'ONE venv' "$SKILL/README.md" && grep -qi 'one venv' "$SKILL/SKILL.md" || { echo "FAIL: README / SKILL.md lost the one-venv rule (review 0.8.0 F1)"; exit 1; }
# every script is executable with a shebang, has a --selftest, and --help / a probe never writes (review 0.8.0 F3)
for s in "$SKILL"/scripts/*.py "$SKILL"/scripts/*.sh; do
  [[ -x "$s" ]] || { echo "FAIL: $s is not executable"; exit 1; }; head -1 "$s" | grep -q '^#!' || { echo "FAIL: $s has no shebang"; exit 1; }
  grep -q -- '--selftest' "$s" || { echo "FAIL: $s has no --selftest"; exit 1; }
done
(cd "$SKILL" && git ls-files -s scripts | awk '$4 !~ /\.yaml$/ && $1 != "100755" {bad=1; print "FAIL: git mode " $1 " on " $4} END {exit bad}') || exit 1   # the lint term file is data
grep -q 'abspath(__file__)' "$SKILL"/scripts/*.py && { echo "FAIL: a script resolves its own path with abspath (a symlinked scripts/ points at the project, not the skill — F4)"; exit 1; }
python3 "$SKILL/scripts/project.py" scaffold --scope ee /dev/null >/dev/null || { echo "FAIL: project.py scaffold must run on a stock python3 without pyyaml (F2)"; exit 1; }
grep -q 'kickoff --check' "$SKILL/SKILL.md" && grep -q '^kickoff:' "$SKILL/templates/project.yaml" && grep -q '^board:' "$SKILL/templates/project.yaml" || { echo "FAIL: the kickoff answers lost their machine-readable home (F10)"; exit 1; }
grep -q 'erc_accept' "$SKILL/templates/project.yaml" && test -f "$SKILL/templates/design/erc_accept.yaml" && ! test -f "$SKILL/templates/ERC_WAIVERS.md" || { echo "FAIL: ERC acceptances must be the yaml the gate reads, not a prose table (F11)"; exit 1; }
grep -rq 'ERC_WAIVERS' "$SKILL/SKILL.md" "$SKILL/README.md" "$SKILL/templates" "$SKILL/references" && { echo "FAIL: a prose ERC waiver table is still referenced (F11)"; exit 1; }
grep -q 'submodules: recursive' "$SKILL/templates/ci/pr-check.yml" "$SKILL/templates/ci/nightly.yml" "$SKILL/templates/ci/release.yml" && ! grep -q 'scripts/ci' "$SKILL/templates/ci/README.md" "$SKILL/SKILL.md" || { echo "FAIL: CI templates must init the submodule and keep project files out of scripts/ (F9)"; exit 1; }
"$PY" "$SKILL/evals/run_evals.py" --python "$PY" >/dev/null || { echo "FAIL: evals/run_evals.py reports a failed mechanical check (F27)"; exit 1; }
test -f "$SKILL/references/kickoff-questionnaire.md" || { echo "FAIL: references/kickoff-questionnaire.md missing"; exit 1; }
grep -q 'AskUserQuestion' "$SKILL/SKILL.md" && grep -q '^### 0.1 The kickoff questionnaire' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the kickoff step (§0.1)"; exit 1; }
grep -c 'RECOMMENDED' "$SKILL/references/kickoff-questionnaire.md" | awk '$1 >= 30 {ok=1} END {exit !ok}' || { echo "FAIL: the questionnaire lost its recommended answers"; exit 1; }
grep -q '^| D1 | the manufacturability bar' "$SKILL/templates/KICKOFF_ANSWERS.md" || { echo "FAIL: KICKOFF_ANSWERS.md lost the bar row"; exit 1; }
grep -q 'references/pcb-layout-dfm.md' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the layout reference (C-07)"; exit 1; }
LEAK='(^|[^a-z0-9])p2s([^a-z0-9]|$)|presets\.P2S|lap\.ring_down|aec[-_]tester|tenstorrent'   # generic: ok (the lint patterns themselves)
grep -rqiE "$LEAK" "$SKILL/SKILL.md" "$SKILL/README.md" "$SKILL/templates" "$SKILL/workflows" "$SKILL/evals" && { echo "FAIL: a source-project identifier leaked into SKILL / README / templates (C-15 / B-34)"; exit 1; }
grep -q '^## 13. Retro' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the retro phase (§13)"; exit 1; }
# 0.10.0: the arrival checklist, the spec errata, the review protocol with a record-reading verifier, the owner-read tag, the slicer optimisation home
grep -q '^### 10.1 Before the order ships' "$SKILL/SKILL.md" && test -f "$SKILL/templates/design/arrival_checklist.yaml" && test -f "$SKILL/templates/SPEC_ERRATA.md" || { echo "FAIL: SKILL.md / templates lost the arrival checklist or the SPEC errata (0.10.0)"; exit 1; }
# 0.10.1: the engine rule (previews fast, geometry of record on the gate-passing engine), the per-preset engine key, the CLAUDE.md agent-ops block, the seeded sampler
grep -q 'passes the chain.s own mesh gates' "$SKILL/references/agent-ops.md" && grep -q 'case.presets.<name>.engine' "$SKILL/references/case-pipeline.md" && grep -q '^## Agent operations' "$SKILL/templates/CLAUDE.md" && grep -q 'sample_surface(m, samples, seed=seed)' "$SKILL/scripts/thin_wall_census.py" || { echo "FAIL: the engine / caching rule of 0.10.1 is missing (agent-ops §8, case-pipeline, CLAUDE.md template, census seed)"; exit 1; }
grep -q 'ALREADY DECIDED' "$SKILL/SKILL.md" && grep -q "'ALREADY DECIDED'" "$SKILL/workflows/blind-deep-review.js" && grep -q 'rev_impact' "$SKILL/workflows/blind-deep-review.js" || { echo "FAIL: the review protocol lost the record-reading verifier (ALREADY DECIDED / rev impact)"; exit 1; }
grep -q 'K owner-read' "$SKILL/SKILL.md" && grep -q 'K owner-read' "$SKILL/references/part-verification.md" || { echo "FAIL: the [K owner-read] tag is missing"; exit 1; }
OPT="$SKILL/references/fdm-print-optimisation.md"; test -f "$OPT" && grep -q 'flush_into_infill' "$OPT" && grep -q 'HAVE sparse infill' "$OPT" && grep -q 'longest' "$SKILL/scripts/print_dfm.py" || { echo "FAIL: fdm-print-optimisation.md (flush-into-infill rule) or the chord span is missing"; exit 1; }
grep -q 'fdm-print-optimisation.md' "$SKILL/SKILL.md" "$SKILL/references/print-kit.md" "$SKILL/references/dfm-printed-enclosure.md" || { echo "FAIL: the optimisation reference is not linked from SKILL / print-kit / dfm-printed-enclosure"; exit 1; }
grep -q '^\*\*C11 Slicer optimisation' "$SKILL/references/kickoff-questionnaire.md" && grep -q '^| C11 |' "$SKILL/templates/KICKOFF_ANSWERS.md" && grep -q 'optimise:' "$SKILL/templates/project.yaml" && grep -q 'fit_result:' "$SKILL/templates/project.yaml" || { echo "FAIL: kickoff C11 / the fit_result landing key missing"; exit 1; }
grep -q 'arrival_checklist' "$SKILL/templates/production_cut.yaml" && grep -c 'ARRIVAL_CHECKLIST' "$SKILL/templates/GATES.md" | grep -q '^2$' || { echo "FAIL: the arrival checklist is not a cut deliverable / an order prerequisite"; exit 1; }
say "0b every generic script selftest"
for s in "$SKILL"/scripts/*.py "$SKILL"/scripts/*.sh; do
  case "$(basename "$s")" in
    print_dfm.py|stability.py) [[ -n "$MESH" ]] || continue ;;
  esac
  case "$s" in
    *.py) "$PY" "$s" --selftest ;;
    *.sh) "$s" --selftest ;;
  esac
done
"$PY" scripts/thin_wall_census.py --selftest
"$PY" scripts/skill_retro.py --selftest
say "0c the skill reads as the current, generic procedure: no changelog voice, no version numbers in prose, no source-project names / parts / ids / dimensions outside the fenced worked examples"
"$PY" "$SKILL/scripts/doc_voice_lint.py" --selftest >/dev/null && "$PY" "$SKILL/scripts/doc_voice_lint.py" || { echo "FAIL: doc_voice_lint hits (the skill narrates its history inside a rule)"; exit 1; }
"$PY" "$SKILL/scripts/generic_lint.py" --selftest >/dev/null && "$PY" "$SKILL/scripts/generic_lint.py" || { echo "FAIL: generic_lint hits (the skill names the project it was learned on)"; exit 1; }
say "0d print DFM: the loop is in SKILL.md as commands, the table and verdict record ship as templates, the tool and the SCAD lint selftest, eval 14's pair flags / passes through the CLI"
PD="$SKILL/references/print-dfm.md"; test -f "$PD" || { echo "FAIL: references/print-dfm.md missing"; exit 1; }
grep -q 'RULE DEFECT' "$PD" && grep -q '^## 3. The loop' "$PD" && grep -q 'read the MESH, never the yaml' "$PD" || { echo "FAIL: print-dfm.md lost the loop / RULE DEFECT / mesh-not-yaml rules"; exit 1; }
grep -q 'print_dfm.py --validate' "$SKILL/SKILL.md" && grep -q 'RULE DEFECT' "$SKILL/SKILL.md" && grep -q 'scad_lint.py' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md §8.1 lost the print-DFM loop commands"; exit 1; }
grep -q '^\*\*C8a' "$SKILL/references/kickoff-questionnaire.md" && grep -q '^| C8a |' "$SKILL/templates/KICKOFF_ANSWERS.md" && grep -q 'dfm_process:' "$SKILL/templates/project.yaml" || { echo "FAIL: kickoff C8a (print-DFM process row) missing"; exit 1; }
"$PY" - "$SKILL" <<'PYEOF'
import sys, yaml, re
t = yaml.safe_load(open(sys.argv[1] + "/templates/design/dfm_processes.yaml"))["processes"]; txt = open(sys.argv[1] + "/templates/design/dfm_processes.yaml").read()
assert all(r.get("validated_on") == [] for r in t.values()), "every template row ships validated_on: []"
assert {"jlc_mjf_pa12", "home_fdm_04", "xometry_mjf_pa12"} <= set(t), sorted(t)
for row, r in t.items():
    for k in ("wall_min", "feature_min", "detail_min", "hole_min"):
        if r.get(k) is not None:
            line = [l for l in txt.splitlines() if re.match(rf"^\s+{k}:", l)]
            assert line, (row, k)
assert len(re.findall(r"\[V\]", txt)) >= 15 and "BLOCKED" in txt, "citations: [V] with URL + date, BLOCKED rows kept null"
v = yaml.safe_load(open(sys.argv[1] + "/templates/docs/quotes/dfm_verdicts.yaml")); assert v == {"verdicts": []}, v
print("templates: dfm_processes.yaml rows", len(t), "all validated_on: []; dfm_verdicts.yaml schema OK")
PYEOF
"$PY" scripts/scad_lint.py --selftest
if [[ -n "$MESH" ]]; then
"$PY" scripts/print_dfm.py --selftest
"$PY" scripts/stability.py --selftest
"$PY" - <<'PYEOF'
import sys, os; sys.path.insert(0, "scripts"); import trimesh, print_dfm
trimesh.creation.extrude_polygon(print_dfm.rim_profile(0.5), 90.0).export("out/eval14_root05.stl"); trimesh.creation.extrude_polygon(print_dfm.rim_profile(1.3), 90.0).export("out/eval14_root13.stl")
PYEOF
if "$PY" scripts/print_dfm.py --process jlc_mjf_pa12 --samples 40000 out/eval14_root05.stl > out/eval14_flag.txt; then echo "FAIL: the 0.5 root under a 2.0 rim must FLAG (exit 1)"; cat out/eval14_flag.txt; exit 1; fi
grep -q '^  FLAG  R root under a rim' out/eval14_flag.txt && grep -q '^  FLAG  W wall' out/eval14_flag.txt || { echo "FAIL: eval 14 FLAG lacks the W + R rows"; cat out/eval14_flag.txt; exit 1; }
"$PY" scripts/print_dfm.py --process jlc_mjf_pa12 --samples 40000 out/eval14_root13.stl | grep -q 'eval14_root13.stl: PASS' || { echo "FAIL: the same geometry at root 1.3 must PASS"; exit 1; }
"$PY" scripts/print_dfm.py --list | grep -q 'xometry_mjf_pa12' || { echo "FAIL: --list must show the template rows outside a project table"; exit 1; }
# enforcement (review 0.8.0 F5 / F6 / F7 / F8 / F28), negative tests on a throwaway mech project: a tampered record, an uncensused body, a laxer process
# row than the target's, --open with a non-OPEN id, an open mesh — each must FAIL the gate / the check
E=$T/enf; mkdir -p $E/out/mechanical/case/pre/stl $E/out/mechanical/case/pre/dfm $E/docs/governance; ln -s "$SKILL/scripts" $E/scripts
printf 'project: {name: enf, scope: mech}\npaths: {mech_record: "out/mechanical/case/*/stl/*.stl"}\nprint_targets: {pre: {dfm_process: jlc_mjf_pa12}}\n' > $E/project.yaml
printf '| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-07** | d | **OPEN** | thicken plate08 | p | r |\n| **D-08** | d | **OPEN** | another body | p | r |\n| CC-010 | d | APPLIED | x | p | r |\n' > $E/docs/governance/DECISIONS.md
"$PY" - "$E" <<'PYEOF'
import sys, trimesh
E = sys.argv[1]; trimesh.creation.box((30.0, 30.0, 2.0)).export(f"{E}/out/mechanical/case/pre/stl/plate2.stl"); trimesh.creation.box((30.0, 30.0, 0.8)).export(f"{E}/out/mechanical/case/pre/stl/plate08.stl")
b = trimesh.creation.box((20.0, 20.0, 5.0)); b.faces = b.faces[2:]; b.export(f"{E}/open.stl")
PYEOF
(cd $E
 "$PY" scripts/print_dfm.py --process jlc_mjf_pa12 --samples 20000 --out out/mechanical/case/pre/dfm out/mechanical/case/pre/stl/plate2.stl >/dev/null || { echo "FAIL: the 2.0 plate must PASS"; exit 1; }
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm >/dev/null && { echo "FAIL (F5): plate08 sits in the STL set without a record and the gate passed"; exit 1; }
 "$PY" scripts/print_dfm.py --process protolabs_mjf_pa12 --samples 20000 --out out/mechanical/case/pre/dfm out/mechanical/case/pre/stl/plate08.stl >/dev/null 2>&1 || true
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm >/dev/null && { echo "FAIL (F6): a record against a laxer row than print_targets.pre.dfm_process passed"; exit 1; }
 "$PY" scripts/print_dfm.py --process jlc_mjf_pa12 --samples 20000 --out out/mechanical/case/pre/dfm out/mechanical/case/pre/stl/plate08.stl >/dev/null && { echo "FAIL: the 0.8 plate must FLAG"; exit 1; }
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm --open pre/plate08=WHATEVER >/dev/null && { echo "FAIL (F7): --open with a free string passed"; exit 1; }
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm --open pre/plate08=CC-010 >/dev/null && { echo "FAIL (F7): --open with an APPLIED row passed"; exit 1; }
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm --open pre/plate08=D-08 >/dev/null && { echo "FAIL (N2 0.9.0): an OPEN row that does not name plate08 passed"; exit 1; }
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm --open pre/plate08=D-07 >/dev/null || { echo "FAIL: --open with the OPEN row D-07 must pass"; exit 1; }
 sed -i.bak 's/"verdict": "FLAG"/"verdict": "PASS"/' out/mechanical/case/pre/dfm/plate08.json
 "$PY" scripts/print_dfm.py --gate out/mechanical/case/pre/dfm >/dev/null && { echo "FAIL (F28): a record edited FLAG->PASS by hand passed the gate"; exit 1; }
 "$PY" scripts/print_dfm.py --process jlc_mjf_pa12 --samples 5000 open.stl > open.txt && { echo "FAIL (F8): an open mesh must FLAG"; exit 1; }
 grep -q '^  FLAG  M manifold' open.txt || { echo "FAIL (F8): rule M did not fire on the open mesh"; cat open.txt; exit 1; }
 rc=0; "$PY" scripts/print_dfm.py --process jlc_mjf_pa12 nonexist.stl >/dev/null 2>&1 || rc=$?; [[ $rc == 2 ]] || { echo "FAIL (F21): a missing file must exit 2 (got $rc)"; exit 1; }
 echo "enforcement (mesh): uncensused body, laxer row, free --open, tampered record, open mesh, missing file -> all FAIL as required")
rm -f out/eval14_*
else echo "   (0d SKIPPED: mesh libraries absent)"; fi
say "0e enforcement without mesh libraries: a tampered / missing census record, a commented gate line, an unauthorised release line, the slot counter and the kickoff check"
N=$T/nomesh; mkdir -p $N/out/mechanical/case/pre/stl $N/out/mechanical/case/pre/census $N/docs/governance; ln -s "$SKILL/scripts" $N/scripts
printf 'solid a\nendsolid a\n' > $N/out/mechanical/case/pre/stl/a.stl; printf 'solid b\nendsolid b\n' > $N/out/mechanical/case/pre/stl/b.stl
printf 'project: {name: nomesh, scope: mech, owner: {name: smoke, email: s@s}}\npaths: {mech_record: "out/mechanical/case/*/stl/*.stl"}\nprint_targets: {pre: {wall_gate: 1.2, void_gate: 1.2, accepted: []}}\ngates: {adopt: ["echo step1"], clone: []}\n' > $N/project.yaml
"$PY" - "$N" <<'PYEOF'
import sys, json, hashlib, os; N = sys.argv[1]; sys.path.insert(0, f"{N}/scripts"); from project import record_sig; from thin_wall_census import VERSION as V
for p in ("a", "b"):
    stl = f"{N}/out/mechanical/case/pre/stl/{p}.stl"
    r = dict(version=V, stl=stl, stl_md5=hashlib.md5(open(stl, "rb").read()).hexdigest(), target="pre", fails=[], accepted_fails=[]); r["sig"] = record_sig(r, V)
    json.dump(r, open(f"{N}/out/mechanical/case/pre/census/{p}.json", "w"))
PYEOF
(cd $N
 "$PY" scripts/thin_wall_census.py --gate-dir out/mechanical/case/pre/census >/dev/null || { echo "FAIL: two signed clean census records must pass"; exit 1; }
 rm out/mechanical/case/pre/census/b.json
 "$PY" scripts/thin_wall_census.py --gate-dir out/mechanical/case/pre/census >/dev/null && { echo "FAIL (F5): b.stl has no census record and the gate passed"; exit 1; }
 sed -i.bak 's/"fails": \[\]/"fails": ["WALL 0.88 < 1.2"]/' out/mechanical/case/pre/census/a.json; sed -i.bak 's/"fails": \["WALL 0.88 < 1.2"\]/"fails": []/' out/mechanical/case/pre/census/a.json
 "$PY" - <<'PYEOF'
import json; p = "out/mechanical/case/pre/census/a.json"; r = json.load(open(p)); r["accepted_fails"] = [dict(fail="WALL 0.9", reason="r", date="2026-01-01", evidence="e")]; json.dump(r, open(p, "w"))   # body changed, sig kept
PYEOF
 rm out/mechanical/case/pre/stl/b.stl
 "$PY" scripts/thin_wall_census.py --gate-dir out/mechanical/case/pre/census >/dev/null && { echo "FAIL (F28): a census record edited after signing passed the gate"; exit 1; }
 git init -q && git add -A && git -c user.name=smoke -c user.email=s@s commit -qm nomesh
 out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true); echo "$out" | grep -q "GATE FAILED: an artefact exists whose gate line is missing" || { echo "FAIL (F11): an STL set with no census / print-DFM gate line in gates.adopt was green"; echo "$out"; exit 1; }
 printf '# GATES\n| Gate | Meaning | Prerequisites | Owner approval |\n|---|---|---|---|\n| **G0** | spec | x | _not yet approved_ |\n| **Release** | reports | y | _not yet written_ |\n' > docs/governance/GATES.md
 "$PY" scripts/gate_check.py G0 >/dev/null && { echo "FAIL (F12): an empty G0 cell read as approved"; exit 1; }
 printf '| **Release** | reports | y | clear to build — smoke, 2026-01-04, record 0000 |\n' >> docs/governance/GATES.md
 "$PY" scripts/gate_check.py --release >/dev/null && { echo "FAIL (F12): an UNCOMMITTED release line passed"; exit 1; }
 git add -A && git -c user.name=agent -c user.email=a@a commit -qm "agent wrote the release line"
 "$PY" scripts/gate_check.py --release >/dev/null && { echo "FAIL (F12): a release line committed by a non-owner passed"; exit 1; }
 printf '\n' >> docs/governance/GATES.md; git add -A && git -c user.name=agent -c user.email=a@a commit -qm "touch"
 printf '| **Release** | reports | y | clear to build — smoke, 2026-01-05, record 0001 |\n' >> docs/governance/GATES.md; git add -A && git -c user.name=smoke -c user.email=s@s commit -qm "owner line"
 "$PY" scripts/gate_check.py --release >/dev/null || { echo "FAIL: the owner's committed release line must pass gate_check --release"; exit 1; }
 echo "enforcement (no mesh): missing census record, tampered census record, commented gate line, empty gate cell, uncommitted / agent-authored release line -> all FAIL; owner line passes")
# the slot counter: a scaffolded ee project shows its slots; trivially filled, zero (F24); the kickoff check fails on template rows and passes on filled ones (F10)
K=$T/kick; mkdir -p $K/docs/governance $K/design; ln -s "$SKILL/scripts" $K/scripts
cp "$SKILL/templates"/{project.yaml,CLAUDE.md,SPEC.md,STATUS.md} $K/; cp "$SKILL/templates"/{GATES,KICKOFF_ANSWERS,DECISIONS}.md $K/docs/governance/; cp "$SKILL/templates/design/traceability.yaml" $K/design/
(cd $K
 "$PY" scripts/project.py scaffold --scope ee project.yaml CLAUDE.md SPEC.md STATUS.md docs/governance/*.md design/*.yaml >/dev/null
 grep -q '{{SCOPE}}' project.yaml CLAUDE.md SPEC.md docs/governance/*.md && { echo "FAIL (0.9.0 F4): scaffold --scope must fill the {{SCOPE}} slot"; exit 1; }
 grep -q '^  scope: ee' project.yaml || { echo "FAIL (0.9.0 F4): project.scope not set by scaffold"; exit 1; }
 "$PY" scripts/project.py slots >/dev/null && { echo "FAIL (F24): a fresh scaffold has slots; the counter must exit 1"; exit 1; }
 { "$PY" scripts/project.py slots || true; } | tail -1 | grep -q 'unfilled in' || { echo "FAIL (F24): slots must print the per-file count"; exit 1; }
 out=$("$PY" scripts/project.py kickoff --check 2>&1 || true); echo "$out" | grep -q 'not valid YAML.*slots' || { echo "FAIL (0.9.0 F3): an unfilled project.yaml must name the slots as the cause, not traceback"; echo "$out" | tail -3; exit 1; }
 for f in project.yaml CLAUDE.md SPEC.md STATUS.md docs/governance/*.md design/*.yaml; do sed -i.bak -E 's/\{\{[^{}]*\}\}/X/g' "$f"; rm -f "$f.bak"; done
 { "$PY" scripts/project.py slots || true; } | tail -1 | grep -q '^slots: 0 unfilled' || { echo "FAIL (F24): a trivially filled project must show zero slots"; "$PY" scripts/project.py slots | tail -3 || true; exit 1; }
 out=$("$PY" scripts/project.py kickoff --check 2>&1 || true); echo "$out" | grep -q '^KICKOFF: .*no D row id\|^KICKOFF: .*is not in' || { echo "FAIL (F10): kickoff rows with D-X ids passed the kickoff check"; echo "$out" | tail -3; exit 1; }
 printf '| **D-02** | d | **APPROVED** | kickoff | owner | words |\n' >> docs/governance/DECISIONS.md; sed -i.bak 's/D-X/D-02/g' docs/governance/KICKOFF_ANSWERS.md
 "$PY" scripts/project.py kickoff --check >/dev/null || { echo "FAIL (F10): a filled ee project must pass the kickoff check"; "$PY" scripts/project.py kickoff --check | tail -5 || true; exit 1; }
 echo "slots: fresh ee scaffold -> exit 1 with counts; trivially filled -> 0; kickoff --check: unfilled yaml names the slots, D-X rows FAIL, filled rows pass")
say "0b scope: A0 asked first, every scope scaffolds from ONE template set and gets its own gate rows"
grep -q '^\*\*A0 Project scope' "$SKILL/references/kickoff-questionnaire.md" && grep -q '^| A0 | scope' "$SKILL/templates/KICKOFF_ANSWERS.md" || { echo "FAIL: kickoff A0 (scope) missing"; exit 1; }
grep -q '^## 1. Phase / gate model (per scope)' "$SKILL/SKILL.md" && grep -q '^## 6. Layout phase and the adopt rule \[ee, both\]' "$SKILL/SKILL.md" && grep -q '^## 8. Case pipeline and FEA \[mech, both\]' "$SKILL/SKILL.md" || { echo "FAIL: SKILL.md lost the scope model / heading tags"; exit 1; }
"$PY" scripts/project.py --selftest
for sc in ee mech both; do
  S=$T/scope_$sc; mkdir -p $S; cp "$SKILL/templates"/{project.yaml,CLAUDE.md,GATES.md,SPEC.md,STATUS.md,KICKOFF_ANSWERS.md,ENV.md,production_cut.yaml,REVIEW_HANDOFF.md,RELEASE_NOTES.md} "$SKILL/templates/design/traceability.yaml" $S/
  "$PY" scripts/project.py scaffold --scope $sc $S/* >/dev/null
  grep -l '{{\(ee\|mech\|both\)\(,\(ee\|mech\|both\)\)*}}' $S/* && { echo "FAIL: a scope tag survived scaffold --scope $sc"; exit 1; }
  G=$(grep -o '^| \*\*[A-Za-z0-9 ()]*\*\*' $S/GATES.md | tr -d '*|' | tr -s ' \n' ' ')
  case $sc in
    ee)   [[ "$G" == " G0 G1 G2 Order (board) Release " ]] || { echo "FAIL: ee gates = '$G'"; exit 1; }
          grep -q '^print_targets:' $S/project.yaml && { echo "FAIL: ee project.yaml carries print_targets"; exit 1; };;
    mech) [[ "$G" == " G0 M1 M2 Case order Release " ]] || { echo "FAIL: mech gates = '$G'"; exit 1; }
          grep -q '^fab_dfm:\|^  board:' $S/project.yaml && { echo "FAIL: mech project.yaml carries board paths / fab_dfm"; exit 1; }
          grep -q 'mech_record' $S/project.yaml || { echo "FAIL: mech project.yaml lost paths.mech_record"; exit 1; }
          grep -q 'ERC\|pcbnew\|parts_seed' $S/CLAUDE.md $S/ENV.md && { echo "FAIL: mech CLAUDE.md / ENV.md still names ERC / pcbnew / a parts seed"; exit 1; }
          grep -v '^#' $S/production_cut.yaml | grep -q '{pkg}\|technician_manual\|developer_manual' && { echo "FAIL: mech production_cut.yaml keeps a fab-package input or a software-track / board deliverable"; exit 1; };;
    ee)   grep -q 'assembly_sop\|case_stl\|fea_case' $S/production_cut.yaml && { echo "FAIL: ee production_cut.yaml keeps a case deliverable"; exit 1; };;
    both) [[ "$G" == " G0 G1 G2 Order (board) Case order Release " ]] || { echo "FAIL: both gates = '$G'"; exit 1; };;
  esac
  sed 's/{{[A-Za-z0-9_ -]*}}/X/g' $S/project.yaml | "$PY" -c 'import sys,yaml; yaml.safe_load(sys.stdin)' || { echo "FAIL: scaffolded project.yaml ($sc) is not valid yaml"; exit 1; }
done
# the ee scaffold must have dropped the same lines the ee grep above checks; a stray `ee`-only or `both`-only tag is caught by the tag grep
say "0c mech scope end to end: the STL set is the record id (report identity, collateral, hand-off), no fab-package line, the fit input printed"
M=$T/mech; mkdir -p $M/out/mechanical/case/v1/stl $M/out/mechanical $M/design $M/docs/governance $M/vendor/hw-from-spec; ln -s "$SKILL/scripts" $M/vendor/hw-from-spec/scripts; ln -s vendor/hw-from-spec/scripts $M/scripts
printf 'solid a\nendsolid a\n' > $M/out/mechanical/case/v1/stl/bracket.stl; printf '{"source": "in/board.step", "source_md5": "abcdef0123456789", "tag": "V"}\n' > $M/out/mechanical/board.stl.provenance.json
printf 'case: {version: v1}\n' > $M/design/case.yaml; printf '# GATES\n| Gate | Meaning | Prerequisites | Owner approval |\n|---|---|---|---|\n' > $M/docs/governance/GATES.md
printf '# D\n| ID | Date | Status | Topic | Proposal | Reason |\n|---|---|---|---|---|---|\n| **D-01** | 2026-01-01 | **APPROVED** | start | owner | word |\n' > $M/docs/governance/DECISIONS.md
cat > $M/project.yaml <<YAML
project: {name: mech_smoke, scope: mech}
paths: {case_yaml: design/case.yaml, mesh_provenance: out/mechanical/board.stl.provenance.json, collateral_dir: docs/release/collateral}
renders: [{name: case_iso, kind: copy, src: "out/mechanical/case/{CASE_VERSION}/iso.png", sub: case}]
reports: [{name: CASE_DESIGN_REPORT, title: mech case report, sections: [banner, identity, decisions, renders, inventory], extra_sources: [design/case.yaml]}]
YAML
printf 'PNG-stub-------------------------------------------------------------------\n' > $M/out/mechanical/case/v1/iso.png
(cd $M && git init -q && git add -A && git -c user.name=smoke -c user.email=s@s commit -qm mech >/dev/null
 REC=$("$PY" scripts/project.py record); echo "$REC"; [[ "$REC" == mechanical\ record*md5\ [0-9a-f]* ]] || { echo "FAIL: mech record id is not the STL set"; exit 1; }
 M8=$(echo "$REC" | sed 's/.*md5 //' | cut -c1-8)
 "$PY" scripts/collect_renders.py >/dev/null && test -f docs/release/collateral/$M8/renders/RENDERS.md || { echo "FAIL: mech collateral not keyed on the STL-set md5"; exit 1; }
 "$PY" scripts/release_report.py >/dev/null; grep -q "Mechanical record .* md5 \*\*\`" docs/release/CASE_DESIGN_REPORT.md || { echo "FAIL: mech report identity is not the mechanical record"; exit 1; }
 grep -q 'no package of record' docs/release/CASE_DESIGN_REPORT.md && { echo "FAIL: mech report carries a fab-package line"; exit 1; }
 H=$("$PY" scripts/handoff_header.py); echo "$H" | grep -q 'Fit input of record.*in/board.step.*\[V\]' && echo "$H" | grep -q 'Mechanical record' || { echo "FAIL: mech hand-off header lacks the fit input / mechanical record rows"; exit 1; })
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
say "5d arrival_checklist (yaml -> md; DONE needs evidence; gates-required demands the adopt line)"; $PY scripts/arrival_checklist.py; $PY scripts/arrival_checklist.py --check
grep -q '| E-2 | case first-article clearance |' docs/production/ARRIVAL_CHECKLIST.md && grep -q '| \*\*all\*\* | 4 | 1 | 0 | 3 |' docs/production/ARRIVAL_CHECKLIST.md || { echo "FAIL: ARRIVAL_CHECKLIST.md rows / counts wrong"; exit 1; }
cp design/arrival_checklist.yaml /tmp/ac.$$ && sed -i.bak 's/evidence: "records\/first_article.md (caliper table)"/evidence: ""/' design/arrival_checklist.yaml && rm -f design/arrival_checklist.yaml.bak
$PY scripts/arrival_checklist.py --check >/dev/null && { echo "FAIL: a DONE row without evidence must fail the checklist"; exit 1; }; mv /tmp/ac.$$ design/arrival_checklist.yaml
sed -i.bak 's/scripts\/arrival_checklist.py --check/true/' project.yaml && rm -f project.yaml.bak; $PY scripts/project.py gates-required >/dev/null && { echo "FAIL: gates-required must demand the arrival_checklist line while the yaml exists"; exit 1; }; git checkout -q -- project.yaml
say "6 release_report (DRAFT expected)";          $PY scripts/release_report.py
grep -q '^\*\*STATUS: DRAFT\*\*' docs/release/PCB_DESIGN_REPORT.md || { echo "FAIL: report not DRAFT"; exit 1; }
say "7 every --check must pass";                  $PY scripts/known_issues.py --check; $PY scripts/assembly_guide.py --check; $PY scripts/arrival_checklist.py --check; $PY scripts/traceability.py --check; $PY scripts/dfm_check.py --check; $PY scripts/collect_renders.py --check; $PY scripts/release_report.py --check
say "8 commit + handoff header";                  git add -A; git -c user.name=smoke -c user.email=s@s commit -qm "generated records"; $PY scripts/handoff_header.py
$PY scripts/handoff_header.py | grep -q 'MATCH' || { echo "FAIL: handoff header has no MATCH"; exit 1; }
say "9 adopt gates incl. the clone gate on git archive HEAD"; scripts/adopt_gates.sh
say "10 the owner's line in the Release row flips the banner; --check catches the stale report; gate_check --release wants the owner's commit"
printf 'A sentence that quotes the words clear to build must not flip anything.\n' >> docs/governance/STATUS.md
printf '| **Release** | Reports RELEASED | the owner line below | clear to build — owner, 2026-01-04, board %s |\n' ${MD5:0:8} >> docs/governance/GATES.md
$PY scripts/release_report.py | grep -q DRAFT || { echo "FAIL (0.9.0 F2): an UNCOMMITTED release cell must stay DRAFT"; exit 1; }
$PY scripts/gate_check.py --release >/dev/null && { echo "FAIL: an uncommitted release line passed gate_check"; exit 1; }
git add -A; git -c user.name=agent -c user.email=a@a commit -qm "an agent commits the owner's cell"
$PY scripts/release_report.py | grep -q DRAFT || { echo "FAIL (0.9.0 F2): a release cell committed by a non-owner must stay DRAFT"; exit 1; }
printf '| **Release** | Reports RELEASED | the owner line below | clear to build — owner, 2026-01-05, board %s |\n' ${MD5:0:8} >> docs/governance/GATES.md
git add -A; git -c user.name=smoke -c user.email=s@s commit -qm "owner release line"
if $PY scripts/release_report.py --check >/dev/null; then echo "FAIL: --check missed the stale report"; exit 1; fi
$PY scripts/release_report.py | grep -q RELEASED || { echo "FAIL: not RELEASED after the owner's commit"; exit 1; }
$PY scripts/gate_check.py --release || { echo "FAIL: the owner's committed release line must pass"; exit 1; }
HWFS_PROJECT=$PWD/project.yaml scripts/clone_gate.sh --regen >/dev/null || { echo "FAIL: the clone gate must regenerate RELEASED from the archive (HWFS_GIT_ROOT blame)"; exit 1; }
grep -q '^\*\*STATUS: RELEASED' docs/release/PCB_DESIGN_REPORT.md || { echo "FAIL: the archive regen lost the RELEASED banner"; exit 1; }
$PY scripts/gate_check.py G0 >/dev/null && { echo "FAIL: G0 has no owner cell in the smoke and must read NOT approved"; exit 1; }
say "SMOKE OK — DRAFT report was $R/docs/release/PCB_DESIGN_REPORT.md (RELEASED after the owner line); traceability census:"
grep -A4 '^## Census' docs/governance/TRACEABILITY.md | tail -3
