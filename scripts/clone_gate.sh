#!/bin/zsh
# scripts/clone_gate.sh — fresh-checkout gate: the COMMITTED tree must pass the project's `gates.clone` commands.
# `git archive HEAD` (no .git, no untracked files, fresh mtimes — exactly what a clone gives another machine) is unpacked into a scratch
# dir at a path of the SAME LENGTH as the repo root (generated text that truncates paths stays byte-identical), .venv symlinked, and every
# command of `gates.clone` in project.yaml runs there with cwd = the archive. Exit 1 on the first failure.
#   scripts/clone_gate.sh            run the clone gate on HEAD
#   scripts/clone_gate.sh --regen    first run `gates.regen` inside the archive (HEAD inputs only) and copy `gates.regen_copy_back` files
#                                    back into the working tree for the next commit; then the checks
#   scripts/clone_gate.sh --selftest
set -e -o pipefail
HERE=$(cd "$(dirname "$0")" && pwd -P)
if [[ "$1" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_cg_XXXX); trap 'rm -rf $T' EXIT
  mkdir -p $T/r/docs && cd $T/r && git init -q && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
  printf 'project: {name: t}\ngates:\n  clone: ["test -f docs/A.md", "grep -q ok docs/A.md"]\n  regen: ["printf ok > docs/A.md"]\n  regen_copy_back: [docs/A.md]\n' > project.yaml
  printf 'stale' > docs/A.md; git add -A; git -c user.name=t -c user.email=t@t commit -qm files
  ln -s "$HERE" scripts
  if scripts/clone_gate.sh >/dev/null 2>&1; then echo "selftest FAILED: gate should fail on 'stale'"; exit 1; fi
  scripts/clone_gate.sh --regen >/dev/null && [[ "$(cat docs/A.md)" == "ok" ]] || { echo "selftest FAILED: regen copy-back"; exit 1; }
  git add -A; git -c user.name=t -c user.email=t@t commit -qm regen
  scripts/clone_gate.sh >/dev/null || { echo "selftest FAILED: gate should pass after regen commit"; exit 1; }
  echo "selftest OK"; exit 0
fi
ROOT=$(python3 -c 'import sys; print(sys.argv[1])' "$(git rev-parse --show-toplevel)")
cd "$ROOT"
PY=${PYTHON:-$ROOT/.venv/bin/python}; [[ -x $PY ]] || PY=$HERE/../.venv/bin/python; [[ -x $PY ]] || PY=python3   # project venv, else the skill repo venv
get() { $PY "$HERE/project.py" get "$1"; }
H=$(git rev-parse --short HEAD)
BASE=$(mktemp -d /tmp/hwfs_cg_XXXX); trap 'rm -rf $BASE' EXIT
# same-length path as ROOT (pad the leaf name) so truncated path labels in generated text match the working tree byte for byte
LEAF=$(basename "$ROOT"); PADLEN=$(( ${#ROOT} - ${#BASE} - 1 )); (( PADLEN < ${#LEAF} )) && PADLEN=${#LEAF}
A="$BASE/$(printf '%-*s' $PADLEN "$LEAF" | tr ' ' '_')"
echo "== git archive HEAD ($H) -> $A  ($(date '+%Y-%m-%d %H:%M'))"
mkdir -p "$A"; git archive HEAD | tar -x -C "$A"
[[ -e "$ROOT/.venv" && ! -e "$A/.venv" ]] && ln -s "$ROOT/.venv" "$A/.venv"
[[ -e "$ROOT/scripts" && ! -e "$A/scripts" ]] && ln -s "$ROOT/scripts" "$A/scripts"
export HWFS_PROJECT="$A/project.yaml"
if [[ "$1" == "--regen" ]]; then
  get gates.regen | while IFS= read -r c; do [[ -n $c ]] || continue; echo "== regen: $c"; (cd "$A" && eval "$c"); done
  get gates.regen_copy_back | while IFS= read -r f; do [[ -n $f ]] || continue; mkdir -p "$ROOT/$(dirname $f)"; cp "$A/$f" "$ROOT/$f"; echo "   copied back: $f"; done
fi
RC=0
get gates.clone | while IFS= read -r c; do
  [[ -n $c ]] || continue
  echo "== clone gate: $c"
  (cd "$A" && eval "$c") || { echo "clone gate FAILED (HEAD $H): $c"; exit 1; }
done || RC=1
[[ $RC == 0 ]] && echo "clone gate OK (HEAD $H)" || exit 1
