#!/usr/bin/env bash
# scripts/clone_gate.sh — fresh-checkout gate: the COMMITTED tree must pass the project's `gates.clone` commands.
# `git archive HEAD` (no .git, no untracked files, no submodule content, fresh mtimes — exactly what a clone gives another machine) is unpacked
# into a scratch dir at a path of the SAME LENGTH as the repo root (generated text that truncates paths stays byte-identical). The working
# tree's `scripts` and `.venv` are then linked into the archive — replacing whatever the archive carries there (a dangling relative symlink
# from the submodule install, an empty submodule dir) — and every command of `gates.clone` runs there with cwd = the archive. Exit 1 on the
# first failure. project.yaml must sit at the git top level (the archive root).
#   scripts/clone_gate.sh            run the clone gate on HEAD
#   scripts/clone_gate.sh --regen    first run `gates.regen` inside the archive (HEAD inputs only) and copy `gates.regen_copy_back` files
#                                    back into the working tree for the next commit; then the checks
#   scripts/clone_gate.sh --selftest
set -e -o pipefail
trap 'echo "clone gate: aborted at line $LINENO (rc $?)" >&2' ERR
HERE=$(cd "$(dirname "$0")" && pwd -P)
case "${1:-}" in -h|--help) sed -n '2,12p' "$0"; exit 0;; ""|--selftest|--regen) ;; *) echo "clone_gate.sh: unknown option $1 (usage: scripts/clone_gate.sh [--regen] | --selftest)" >&2; exit 2;; esac
if [[ "$1" == "--selftest" ]]; then
  T=$(mktemp -d /tmp/hwfs_cg_XXXX); trap 'rm -rf $T' EXIT
  mkdir -p $T/r/docs $T/r/vendor/hw-from-spec && cd $T/r && git init -q && git -c user.name=t -c user.email=t@t commit -q --allow-empty -m init
  # the documented install layout: skill at vendor/hw-from-spec (a submodule — empty in `git archive`, so ignored here), RELATIVE symlink scripts/
  ln -s "$HERE" vendor/hw-from-spec/scripts; ln -s vendor/hw-from-spec/scripts scripts; printf 'vendor/hw-from-spec/\n.venv/\n' > .gitignore
  printf 'project: {name: t}\ngates:\n  clone: ["test -f docs/A.md", "grep -q ok docs/A.md", "test -f scripts/clone_gate.sh"]\n  regen: ["printf ok > docs/A.md"]\n  regen_copy_back: [docs/A.md]\n' > project.yaml
  printf 'stale' > docs/A.md; git add -A; git -c user.name=t -c user.email=t@t commit -qm files
  git archive HEAD | tar -tf - | grep -qx scripts || { echo "selftest FAILED: the archive should carry the scripts symlink"; exit 1; }
  if scripts/clone_gate.sh >/dev/null 2>&1; then echo "selftest FAILED: gate should fail on 'stale'"; exit 1; fi
  scripts/clone_gate.sh --regen >/dev/null && [[ "$(cat docs/A.md)" == "ok" ]] || { echo "selftest FAILED: regen copy-back"; exit 1; }
  git add -A; git -c user.name=t -c user.email=t@t commit -qm regen
  scripts/clone_gate.sh >/dev/null || { echo "selftest FAILED: gate should pass after regen commit (dangling scripts link in the archive?)"; exit 1; }
  echo "selftest OK"; exit 0
fi
ROOT=$(git rev-parse --show-toplevel)
[[ -f "$ROOT/project.yaml" ]] || { echo "clone gate: project.yaml must sit at the git top level ($ROOT) — the archive root is what a clone sees"; exit 1; }
cd "$ROOT"
# interpreter: $PYTHON, else the project venv, else the skill's venv, else python3 — the first one that imports yaml
PY=""; for c in "${PYTHON:-}" "$ROOT/.venv/bin/python" "$HERE/../.venv/bin/python" python3; do
  [[ -n "$c" ]] && "$c" -c 'import yaml' >/dev/null 2>&1 && { PY=$c; break; }
done
[[ -n "$PY" ]] || { echo "clone gate: no python with pyyaml found (project .venv, skill .venv, python3)"; exit 1; }
export PY
get() { "$PY" "$HERE/project.py" get "$1"; }
H=$(git rev-parse --short HEAD)
BASE=$(mktemp -d /tmp/hwfs_cg_XXXX); trap 'rm -rf $BASE' EXIT
# same-length path as ROOT (pad the leaf name) so truncated path labels in generated text match the working tree byte for byte
LEAF=$(basename "$ROOT"); PADLEN=$(( ${#ROOT} - ${#BASE} - 1 )); (( PADLEN < ${#LEAF} )) && PADLEN=${#LEAF}
A="$BASE/$(printf '%-*s' $PADLEN "$LEAF" | tr ' ' '_')"
echo "== git archive HEAD ($H) -> $A  ($(date '+%Y-%m-%d %H:%M'))  python: $PY"
mkdir -p "$A"; git archive HEAD | tar -x -C "$A"
# link the working tree's scripts and .venv over whatever the archive carries (dangling relative link, empty submodule dir, nothing)
for d in scripts .venv; do
  [[ -e "$ROOT/$d" ]] && { rm -rf "$A/$d"; ln -sfn "$ROOT/$d" "$A/$d"; }
done
export HWFS_PROJECT="$A/project.yaml" HWFS_GIT_ROOT="$ROOT"   # the archive has no .git: gate_check blames the release line in the real checkout (HEAD = the archive)
if [[ "$1" == "--regen" ]]; then
  while IFS= read -r c; do [[ -n $c ]] || continue; echo "== regen: $c"; (cd "$A" && eval "$c"); done < <(get gates.regen)
  while IFS= read -r f; do [[ -n $f ]] || continue; mkdir -p "$ROOT/$(dirname "$f")"; cp "$A/$f" "$ROOT/$f"; echo "   copied back: $f"; done < <(get gates.regen_copy_back)
fi
while IFS= read -r c; do
  [[ -n $c ]] || continue
  echo "== clone gate: $c"
  (cd "$A" && eval "$c") || { echo "clone gate FAILED (HEAD $H): $c"; exit 1; }
done < <(get gates.clone)
echo "clone gate OK (HEAD $H)"
