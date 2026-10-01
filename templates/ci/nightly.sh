#!/usr/bin/env bash
# ci/nightly.sh — bounded long checks (copied from templates/ci/; project-owned): every skill and gen/ selftest, then the adopt gates without the
# clone gate (release.yml runs that). Full FEA solves, renders and routing are release records, never CI output.
set -e -o pipefail
PY=${PYTHON:-.venv/bin/python}
for s in scripts/*.py gen/*.py; do
  [[ -f "$s" ]] || continue
  grep -q -- '--selftest' "$s" || continue
  echo "== $s --selftest"; "$PY" "$s" --selftest
done
scripts/clone_gate.sh --selftest; scripts/adopt_gates.sh --selftest
scripts/adopt_gates.sh --no-clone
