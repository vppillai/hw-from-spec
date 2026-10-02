#!/usr/bin/env bash
# scripts/iteration_gate.sh — run one configured read-only iteration tier from project.yaml:
#   scripts/iteration_gate.sh --tier inner|standard|release
#   scripts/iteration_gate.sh --selftest
# `gates.iteration.<tier>` is a list of root-relative commands. An inner tier is a targeted
# generator/check pair; standard is the scoped check set for a bounded change; release includes
# the full adopt/clone chain before a gate, order, or cut. The runner refuses an empty tier and
# a command that changes the tracked tree.
set -e
trap 'echo "iteration gate: aborted at line $LINENO (rc $?)" >&2' ERR
HERE=$(cd "$(dirname "$0")" && pwd -P)

if [[ "${1:-}" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_iteration_XXXX); trap 'rm -rf "$T"' EXIT
  mkdir -p "$T/r"; cd "$T/r"; git init -q
  printf '%s\n' \
    'project: {name: t}' \
    'gates:' \
    '  iteration:' \
    '    inner: ["echo inner"]' \
    '    standard: ["echo standard"]' \
    '    release: ["echo release"]' > project.yaml
  git add project.yaml; git -c user.name=t -c user.email=t@t commit -qm init
  ln -s "$HERE" scripts
  out=$(scripts/iteration_gate.sh --tier inner)
  grep -qx '== echo inner' <<<"$out" && ! grep -q 'standard\|release' <<<"$out" || { echo "selftest FAILED: inner tier must run only its commands"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier standard)
  grep -qx '== echo standard' <<<"$out" || { echo "selftest FAILED: standard tier"; exit 1; }
  printf '%s\n' \
    'project: {name: t}' \
    'gates:' \
    '  iteration:' \
    '    inner: ["echo changed >> project.yaml"]' > project.yaml
  git add project.yaml; git -c user.name=t -c user.email=t@t commit -qm writes
  out=$(scripts/iteration_gate.sh --tier inner 2>&1 || true); git checkout -q -- project.yaml
  grep -q 'FAILED: the tier wrote to the tree' <<<"$out" || { echo "selftest FAILED: a writing command must fail"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier release 2>&1 || true)
  grep -q 'has no commands' <<<"$out" || { echo "selftest FAILED: an empty tier must fail"; echo "$out"; exit 1; }
  echo "selftest OK (tier selection, no implicit wider tier, read-only guard, empty tier refused)"; exit 0
fi

[[ "${1:-}" == "--tier" && $# == 2 ]] || { echo "usage: scripts/iteration_gate.sh --tier inner|standard|release | --selftest" >&2; exit 2; }
TIER=$2
case "$TIER" in inner|standard|release) ;; *) echo "iteration gate: unknown tier '$TIER' (inner|standard|release)" >&2; exit 2;; esac

ROOT=$(git rev-parse --show-toplevel)
[[ -f "$ROOT/project.yaml" ]] || { echo "iteration gate: project.yaml must sit at the git top level ($ROOT)" >&2; exit 1; }
cd "$ROOT"
PY=""
for c in "${PYTHON:-}" "$ROOT/.venv/bin/python" "$HERE/../.venv/bin/python" python3; do
  [[ -n "$c" ]] && "$c" -c 'import yaml' >/dev/null 2>&1 && { PY=$c; break; }
done
[[ -n "$PY" ]] || { echo "iteration gate: no python with pyyaml found (project .venv, skill .venv, python3)" >&2; exit 1; }
export PY PYTHONDONTWRITEBYTECODE=1
get() { "$PY" "$HERE/project.py" get "$1"; }
quiet_regex=$(get gates.quiet_regex); [[ -n "$quiet_regex" ]] || quiet_regex='^$'
quiet() { grep -vE "$quiet_regex" || true; }
snap() { git status --porcelain; git diff HEAD | git hash-object --stdin; }
TREE0=$(snap)
COMMANDS=$(get "gates.iteration.$TIER")
[[ -n "$COMMANDS" && "$COMMANDS" != "[]" ]] || { echo "iteration gate: gates.iteration.$TIER has no commands — configure the tier in project.yaml" >&2; exit 1; }

while IFS= read -r command; do
  [[ -n "$command" ]] || continue
  echo "== $command"
  eval "$command" 2>&1 | quiet
  [[ ${PIPESTATUS[0]} == 0 ]] || { echo "ITERATION FAILED ($TIER): $command" >&2; exit 1; }
done <<<"$COMMANDS"
[[ "$(snap)" == "$TREE0" ]] || { echo "ITERATION FAILED: the tier wrote to the tree (checks must be read-only)" >&2; git status --porcelain | head -20; exit 1; }
echo "iteration tier $TIER OK"
