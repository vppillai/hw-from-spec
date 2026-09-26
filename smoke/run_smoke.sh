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
say "1 fab package of record keyed on the board md5"
MD5=$(md5of kicad/smoke/smoke.kicad_pcb); PKG=out/fab/2026-01-03_${MD5:0:8}; mkdir -p $PKG
printf 'board kicad/smoke/smoke.kicad_pcb\nmd5 %s\ncommit %s\nbuilt 2026-01-03\nsegments 1\nvias 0\n' $MD5 $(git rev-parse --short HEAD) > $PKG/board_id.txt
printf 'PNG-stub-panel-top-render-------------------------------------------------\n' > $PKG/panel_top.png
mkdir -p out/case/v0.1-smoke; printf 'PNG-stub-case-iso-render----------------------------------------------------\n' > out/case/v0.1-smoke/iso.png
say "2 known_issues (generated index)";          $PY scripts/known_issues.py
say "3 traceability (matrix)";                   $PY scripts/traceability.py || true      # exit 1 here would mean FAILED rows: the smoke has none
say "4 dfm_check (grading the measurer's items; report to dfm.report)"; $PY scripts/dfm_check.py
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
