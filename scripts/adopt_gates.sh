#!/bin/zsh
# scripts/adopt_gates.sh — the adopt rule in one run: every `gates.adopt` command of project.yaml (selftests first, then the --check gates),
# exit 1 on the FIRST failing gate with its output shown (no whole-stream 2>/dev/null — noise is filtered by line via `gates.quiet_regex`),
# then the fresh-checkout gate (scripts/clone_gate.sh) unless --no-clone, then the frozen-worktree note (a hand-off needs a clean tree).
#   scripts/adopt_gates.sh [--no-clone]
#   scripts/adopt_gates.sh --selftest
set -e
HERE=$(cd "$(dirname "$0")" && pwd -P)
if [[ "$1" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_ag_XXXX); trap 'rm -rf $T' EXIT
  mkdir -p $T/r && cd $T/r && git init -q
  printf 'project: {name: t}\ngates:\n  quiet_regex: "Fontconfig"\n  adopt: ["echo step1", "sh -c \\"echo Fontconfig warning >&2; exit 0\\"", "false"]\n  clone: []\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm init; ln -s "$HERE" scripts
  out=$(scripts/adopt_gates.sh --no-clone 2>&1 || true)
  echo "$out" | grep -q "GATE FAILED: false" || { echo "selftest FAILED: expected the third step to fail"; echo "$out"; exit 1; }
  echo "$out" | grep -qx "Fontconfig warning" && { echo "selftest FAILED: quiet_regex not applied"; exit 1; }
  printf 'project: {name: t}\ngates:\n  adopt: ["echo step1"]\n  clone: ["test -f project.yaml"]\n' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm ok
  scripts/adopt_gates.sh | grep -q "adopt gates OK" || { echo "selftest FAILED: green path"; exit 1; }
  echo "selftest OK"; exit 0
fi
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
PY=${PYTHON:-$ROOT/.venv/bin/python}; [[ -x $PY ]] || PY=$HERE/../.venv/bin/python; [[ -x $PY ]] || PY=python3   # project venv, else the skill repo venv
get() { $PY "$HERE/project.py" get "$1"; }
Q=$(get gates.quiet_regex); [[ -n $Q ]] || Q='^$'
quiet() { grep -vE "$Q" || true; }
step() { echo "== $1"; eval "$1" 2>&1 | quiet; [[ ${pipestatus[1]} == 0 ]] || { echo "GATE FAILED: $1"; exit 1; }; }
get gates.adopt | while IFS= read -r c; do [[ -n $c ]] && step "$c"; done
if [[ "$1" != "--no-clone" ]]; then
  step "$HERE/clone_gate.sh"
fi
[[ -z "$(git status --short --untracked-files=no)" ]] || { echo "NOTE: working tree has uncommitted tracked changes — a review hand-off needs a clean tree (frozen-worktree rule)"; git status --short --untracked-files=no | head -20; }
echo "adopt gates OK"
