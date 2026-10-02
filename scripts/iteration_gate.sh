#!/usr/bin/env bash
# scripts/iteration_gate.sh — the INNER validation tier: the changed generator's --check and its direct grader, read-only on the tree.
#   scripts/iteration_gate.sh [-- <command> ...]     commands = `gates.iteration.inner` in project.yaml (the project's standing fast set) and / or
#                                                     the ones after `--` (this change's set); none at all = refused, so a fast loop can never claim
#                                                     what it did not run. Same read-only guard as scripts/adopt_gates.sh (status + tracked-diff
#                                                     hash before and after); heavy commands go through scripts/jobs.sh when the project has it.
#   scripts/iteration_gate.sh --selftest
# The other tiers are existing commands, not this script: standard = scripts/adopt_gates.sh --no-clone (`make gates`), release =
# scripts/adopt_gates.sh with the clone gate (`make check`).
set -e
HERE=$(cd "$(dirname "$0")" && pwd -P)

if [[ "${1:-}" == "--selftest" ]]; then
  [[ -z "${PYTHON:-}" && -x "$PWD/.venv/bin/python" ]] && "$PWD/.venv/bin/python" -c "import yaml" 2>/dev/null && export PYTHON="$PWD/.venv/bin/python"   # the selftest's temp project has no venv: take the caller's (as adopt_gates.sh)
  T=$(mktemp -d /tmp/hwfs_iteration_XXXX); trap 'rm -rf "$T"' EXIT
  mkdir -p "$T/r/scripts"; cd "$T/r"; git init -q
  ln -s "$HERE/iteration_gate.sh" scripts/iteration_gate.sh; ln -s "$HERE/project.py" scripts/project.py
  printf '%s\n' 'project: {name: t}' 'gates:' '  iteration:' '    inner: ["echo inner-yaml"]' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm init
  out=$(scripts/iteration_gate.sh)
  grep -qx '== echo inner-yaml' <<<"$out" && grep -q 'tier inner OK' <<<"$out" || { echo "selftest FAILED: inner from project.yaml"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh -- "echo inner-cli")
  grep -qx '== echo inner-cli' <<<"$out" && grep -qx '== echo inner-yaml' <<<"$out" || { echo "selftest FAILED: commands after -- join the yaml set"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh -- "echo changed >> project.yaml" 2>&1 || true); git checkout -q -- project.yaml
  grep -q 'FAILED: the tier wrote to the tree' <<<"$out" || { echo "selftest FAILED: a writing command must fail"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh -- "false" 2>&1 || true); grep -q 'ITERATION FAILED (inner): false' <<<"$out" || { echo "selftest FAILED: a failing command must fail the tier"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier standard 2>&1 || true); grep -q 'usage:' <<<"$out" || { echo "selftest FAILED: unknown flags are refused"; echo "$out"; exit 1; }
  printf '%s\n' 'project: {name: t}' > project.yaml; git add -A; git -c user.name=t -c user.email=t@t commit -qm empty
  out=$(scripts/iteration_gate.sh 2>&1 || true); grep -q 'has no commands' <<<"$out" || { echo "selftest FAILED: an empty inner set must be refused"; echo "$out"; exit 1; }
  echo "selftest OK (inner from yaml / from the command line / both, read-only guard, failing command, unknown flag, empty set refused)"; exit 0
fi

case "${1:-}" in -h|--help) sed -n '2,9p' "$0"; exit 0;; esac
[[ $# == 0 || "$1" == "--" ]] || { echo "usage: scripts/iteration_gate.sh [-- <command> ...] | --selftest   (standard = scripts/adopt_gates.sh --no-clone, release = scripts/adopt_gates.sh)" >&2; exit 2; }
[[ $# == 0 ]] || shift
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
[[ -f project.yaml ]] || { echo "iteration gate: project.yaml must sit at the git top level ($ROOT)" >&2; exit 1; }

PY=""
for c in "${PYTHON:-}" "$ROOT/.venv/bin/python" "$HERE/../.venv/bin/python" python3; do
  [[ -n "$c" ]] && "$c" -c 'import yaml' >/dev/null 2>&1 && { PY=$c; break; }
done
[[ -n "$PY" ]] || { echo "iteration gate: no python with pyyaml found (project .venv, skill .venv, python3)" >&2; exit 1; }
export PY PYTHONDONTWRITEBYTECODE=1
get() { "$PY" "$HERE/project.py" get "$1"; }
quiet_regex=$(get gates.quiet_regex); [[ -n "$quiet_regex" ]] || quiet_regex='^$'
quiet() { grep -vE "$quiet_regex" || true; }
snap() { git status --porcelain; git diff HEAD | git hash-object --stdin; }   # as adopt_gates.sh: status letters + the content of every tracked change
J=(); [[ -x scripts/jobs.sh ]] && J=(scripts/jobs.sh --)                     # the host pool when the project has it (references/agent-ops.md §8 item 1)

COMMANDS=()
while IFS= read -r c; do [[ -n "$c" && "$c" != "[]" ]] && COMMANDS+=("$c"); done < <(get gates.iteration.inner)
COMMANDS+=("$@")
[[ ${#COMMANDS[@]} -gt 0 ]] || { echo "iteration gate: the inner tier has no commands — list the changed generator's --check and its grader in gates.iteration.inner or after '--'" >&2; exit 1; }

TREE0=$(snap)
for command in "${COMMANDS[@]}"; do
  echo "== $command"
  "${J[@]}" bash -c "$command" 2>&1 | quiet
  [[ ${PIPESTATUS[0]} == 0 ]] || { echo "ITERATION FAILED (inner): $command" >&2; exit 1; }
done
[[ "$(snap)" == "$TREE0" ]] || { echo "ITERATION FAILED: the tier wrote to the tree (checks must be read-only — build in a temp dir, export nowhere)" >&2; git status --porcelain | head -20; exit 1; }
echo "iteration tier inner OK (${#COMMANDS[@]} command(s), tree unchanged)"
