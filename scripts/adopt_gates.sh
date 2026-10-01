#!/usr/bin/env bash
# scripts/adopt_gates.sh — the adopt rule in one run: every `gates.adopt` command of project.yaml (selftests first, then the --check gates),
# exit 1 on the FIRST failing gate with its output shown (no whole-stream 2>/dev/null — noise is filtered by line via `gates.quiet_regex`),
# then the fresh-checkout gate (scripts/clone_gate.sh) unless --no-clone, then the READ-ONLY guard (a checker that writes into the tree is a
# write, not a check: `git status --porcelain` must be identical before and after the gates — a PR check once replaced the ERC of record with a
# temp copy's warnings), then the frozen-worktree note (a hand-off needs a clean tree). project.yaml must sit at the git top level.
#   scripts/adopt_gates.sh [--no-clone]
#   scripts/adopt_gates.sh --selftest
set -e
trap 'echo "adopt gates: aborted at line $LINENO (rc $?)" >&2' ERR
HERE=$(cd "$(dirname "$0")" && pwd -P)
if [[ "$1" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_ag_XXXX); trap 'rm -rf $T' EXIT
  mkdir -p $T/r && cd $T/r && git init -q
  printf 'project: {name: t}\ngates:\n  quiet_regex: "Fontconfig"\n  adopt: ["echo step1", "sh -c \\"echo Fontconfig warning >&2; exit 0\\"", "false", "echo never"]\n  clone: []\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm init; ln -s "$HERE" scripts
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true)
  echo "$out" | grep -q "GATE FAILED: false" || { echo "selftest FAILED: expected the third step to fail"; echo "$out"; exit 1; }
  echo "$out" | grep -q "never" && { echo "selftest FAILED: must stop at the first failing gate"; exit 1; }
  echo "$out" | grep -qx "Fontconfig warning" && { echo "selftest FAILED: quiet_regex not applied"; exit 1; }
  printf 'project: {name: t}\ngates:\n  adopt: ["echo step1"]\n  clone: ["test -f project.yaml"]\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm ok
  scripts/adopt_gates.sh | grep -q "adopt gates OK" || { echo "selftest FAILED: green path"; exit 1; }
  printf 'project: {name: t}\ngates:\n  adopt: ["echo x >> project.yaml"]\n  clone: []\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm rw
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true); git checkout -q -- project.yaml
  echo "$out" | grep -q "GATE FAILED: the gates wrote to the tree" || { echo "selftest FAILED: a writing gate must fail the read-only guard"; echo "$out"; exit 1; }
  printf 'project: {name: t}\ngates:\n  adopt: ["echo x >> dirty.txt"]\n  clone: []\n' > project.yaml; printf 'a\n' > dirty.txt
  git add -A; git -c user.name=t -c user.email=t@t commit -qm rw2; printf 'b\n' >> dirty.txt   # already dirty before the gates run
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true); git checkout -q -- dirty.txt
  echo "$out" | grep -q "GATE FAILED: the gates wrote to the tree" || { echo "selftest FAILED: a gate modifying an already-dirty tracked file must fail the guard"; echo "$out"; exit 1; }
  printf 'project: {name: t}\ngates:\n  clone: []\n' > project.yaml; git add -A; git -c user.name=t -c user.email=t@t commit -qm empty
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true)
  echo "$out" | grep -q "gates.adopt is empty" || { echo "selftest FAILED: an empty gate list must not be green"; echo "$out"; exit 1; }
  # review 0.8.0 F11: an STL set with the census / print-DFM gate lines still commented out is a FAILING adopt run, not a green one
  mkdir -p out/mechanical/case/v1/stl; printf 'solid a\nendsolid a\n' > out/mechanical/case/v1/stl/a.stl
  printf 'project: {name: t, scope: mech}\npaths: {mech_record: "out/mechanical/case/*/stl/*.stl"}\ngates:\n  adopt: ["echo step1"]\n  clone: []\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm stl
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true)
  echo "$out" | grep -q "GATE FAILED: an artefact exists whose gate line is missing" || { echo "selftest FAILED: an STL set without its gate lines must fail"; echo "$out"; exit 1; }
  rm -rf out
  printf 'project: {name: t}\ngates:\n  adopt: ["echo step1"]\n  clone: ["test -f project.yaml"]\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm ok2
  mkdir sub && (cd sub && ../scripts/adopt_gates.sh --no-clone | grep -q "adopt gates OK") || { echo "selftest FAILED: run from a subdirectory"; exit 1; }
  echo "selftest OK"; exit 0
fi
ROOT=$(git rev-parse --show-toplevel)
[[ -f "$ROOT/project.yaml" ]] || { echo "adopt gates: project.yaml must sit at the git top level ($ROOT)"; exit 1; }
cd "$ROOT"
PY=""; for c in "${PYTHON:-}" "$ROOT/.venv/bin/python" "$HERE/../.venv/bin/python" python3; do   # the first interpreter that imports yaml
  [[ -n "$c" ]] && "$c" -c 'import yaml' >/dev/null 2>&1 && { PY=$c; break; }
done
[[ -n "$PY" ]] || { echo "adopt gates: no python with pyyaml found (project .venv, skill .venv, python3)"; exit 1; }
export PY
echo "== python: $PY"
export PYTHONDONTWRITEBYTECODE=1
snap() { git status --porcelain; git diff HEAD | git hash-object --stdin; }   # status letters + the content of every tracked change: a re-modified dirty file shows too
TREE0=$(snap)
get() { "$PY" "$HERE/project.py" get "$1"; }
Q=$(get gates.quiet_regex); [[ -n $Q ]] || Q='^$'
quiet() { grep -vE "$Q" || true; }
step() { echo "== $1"; eval "$1" 2>&1 | quiet; [[ ${PIPESTATUS[0]} == 0 ]] || { echo "GATE FAILED: $1"; exit 1; }; }
L=$(get gates.adopt); [[ -n "$L" ]] || { echo "adopt gates: gates.adopt is empty — nothing checked (a green gate that ran nothing is a failing check)"; exit 1; }
"$PY" "$HERE/project.py" gates-required || { echo "GATE FAILED: an artefact exists whose gate line is missing or still commented out in gates.adopt (schematic -> erc_gate.py, board -> a DRC gate, STL set -> census --gate-dir + print_dfm --gate)"; exit 1; }
while IFS= read -r c; do [[ -n $c ]] && step "$c"; done <<< "$L"
if [[ "$1" != "--no-clone" ]]; then
  step "$HERE/clone_gate.sh"
fi
[[ "$(snap)" == "$TREE0" ]] || { echo "GATE FAILED: the gates wrote to the tree (checkers must be read-only — build in a temp dir, export nowhere; gitignored paths are not watched):"; git status --porcelain | head -20; exit 1; }
[[ -z "$(git status --short --untracked-files=no)" ]] || { echo "NOTE: working tree has uncommitted tracked changes — a review hand-off needs a clean tree (frozen-worktree rule)"; git status --short --untracked-files=no | head -20; }
echo "adopt gates OK"
