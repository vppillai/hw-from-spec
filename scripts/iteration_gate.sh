#!/usr/bin/env bash
# scripts/iteration_gate.sh — the three validation tiers, one entry point, every tier read-only on the tree:
#   scripts/iteration_gate.sh --tier inner [-- <command> ...]    the changed generator's --check + its direct grader; the commands come from
#                                                                 `gates.iteration.inner` in project.yaml (a project's standing fast set) and / or
#                                                                 from the command line after `--` (this change's set); empty = refused
#   scripts/iteration_gate.sh --tier standard                     = scripts/adopt_gates.sh --no-clone   (the project's whole check set; `make gates`)
#   scripts/iteration_gate.sh --tier release                      = scripts/adopt_gates.sh              (+ the fresh-archive clone gate; `make check`)
#   scripts/iteration_gate.sh --selftest
# standard and release ARE the adopt list (`gates.adopt`) — one list, one read-only guard (adopt_gates.sh carries it); this runner adds the inner
# tier: an explicit, small command set under the same guard, so a fast loop can never claim what a release-grade check did not run. Heavy
# commands go through the host pool (scripts/jobs.sh) when the project has it.
set -e
HERE=$(cd "$(dirname "$0")" && pwd -P)

if [[ "${1:-}" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_iteration_XXXX); trap 'rm -rf "$T"' EXIT
  mkdir -p "$T/r/scripts"; cd "$T/r"; git init -q
  ln -s "$HERE/iteration_gate.sh" scripts/iteration_gate.sh; ln -s "$HERE/project.py" scripts/project.py
  printf '#!/usr/bin/env bash\necho "adopt_gates $*"\n' > scripts/adopt_gates.sh; chmod +x scripts/adopt_gates.sh      # stub: the alias must pass the flag
  printf '%s\n' 'project: {name: t}' 'gates:' '  iteration:' '    inner: ["echo inner-yaml"]' > project.yaml
  git add -A; git -c user.name=t -c user.email=t@t commit -qm init
  out=$(scripts/iteration_gate.sh --tier inner)
  grep -qx '== echo inner-yaml' <<<"$out" && grep -q 'inner OK' <<<"$out" || { echo "selftest FAILED: inner from project.yaml"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier inner -- "echo inner-cli")
  grep -qx '== echo inner-cli' <<<"$out" && grep -qx '== echo inner-yaml' <<<"$out" || { echo "selftest FAILED: inner from the command line joins the yaml set"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier standard); grep -qx 'adopt_gates --no-clone' <<<"$out" || { echo "selftest FAILED: standard = adopt_gates.sh --no-clone"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier release);  grep -qx 'adopt_gates ' <<<"$out" || { echo "selftest FAILED: release = adopt_gates.sh"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier inner -- "echo changed >> project.yaml" 2>&1 || true); git checkout -q -- project.yaml
  grep -q 'FAILED: the tier wrote to the tree' <<<"$out" || { echo "selftest FAILED: a writing command must fail"; echo "$out"; exit 1; }
  out=$(scripts/iteration_gate.sh --tier inner -- "false" 2>&1 || true); grep -q 'ITERATION FAILED (inner): false' <<<"$out" || { echo "selftest FAILED: a failing command must fail the tier"; echo "$out"; exit 1; }
  printf '%s\n' 'project: {name: t}' > project.yaml; git add -A; git -c user.name=t -c user.email=t@t commit -qm empty
  out=$(scripts/iteration_gate.sh --tier inner 2>&1 || true); grep -q 'has no commands' <<<"$out" || { echo "selftest FAILED: an empty inner tier must be refused"; echo "$out"; exit 1; }
  echo "selftest OK (inner from yaml / from the command line / both, standard + release alias adopt_gates, read-only guard, failing command, empty tier refused)"; exit 0
fi

case "${1:-}" in -h|--help) sed -n '2,11p' "$0"; exit 0;; esac
[[ "${1:-}" == "--tier" && -n "${2:-}" ]] || { echo "usage: scripts/iteration_gate.sh --tier inner [-- <command> ...] | --tier standard | --tier release | --selftest" >&2; exit 2; }
TIER=$2; shift 2
ROOT=$(git rev-parse --show-toplevel); cd "$ROOT"
case "$TIER" in
  standard) exec scripts/adopt_gates.sh --no-clone ;;
  release)  exec scripts/adopt_gates.sh ;;
  inner) ;;
  *) echo "iteration gate: unknown tier '$TIER' (inner|standard|release)" >&2; exit 2 ;;
esac
[[ -f project.yaml ]] || { echo "iteration gate: project.yaml must sit at the git top level ($ROOT)" >&2; exit 1; }
[[ $# == 0 || "$1" == "--" ]] || { echo "iteration gate: commands follow '--'" >&2; exit 2; }
[[ $# == 0 ]] || shift

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
