#!/usr/bin/env bash
# ci/release_archive.sh OUT — stage the release artefacts (copied from templates/ci/; project-owned): the fab package of the record md5
# (`scripts/project.py record` -> the paths.fab_dir/<rev>/ whose board_id.txt carries it), paths.release_dir, paths.production_dir/<rev>/. REFUSES the whole stage when any staged
# path starts with $PROJECT_VENDOR_EXCLUDE (licensed vendor data never leaves the repo). Exit 1 when nothing is staged.
set -e -o pipefail
OUT=${1:?usage: ci/release_archive.sh OUT_DIR}; PY=${PYTHON:-.venv/bin/python}
REC=$("$PY" scripts/project.py record); MD5=$(echo "$REC" | sed 's/.*md5 //'); M8=${MD5:0:8}
[[ "$MD5" != MISSING ]] || { echo "release_archive: no record of record ($REC)"; exit 1; }
FAB=$("$PY" scripts/project.py get paths.fab_dir); REL=$("$PY" scripts/project.py get paths.release_dir); PROD=$("$PY" scripts/project.py get paths.production_dir); REV=$("$PY" scripts/project.py rev)
PKG=$(grep -l "^md5 $MD5$" "$FAB"/*/board_id.txt 2>/dev/null | xargs -n1 dirname)   # the package is selected by the md5 INSIDE board_id.txt, never by its name
rm -rf "$OUT"; mkdir -p "$OUT"; n=0
for src in $PKG "$REL" "$PROD/$REV"; do
  [[ -e "$src" ]] || continue
  if [[ -n "${PROJECT_VENDOR_EXCLUDE:-}" ]] && find "$src" -path "*${PROJECT_VENDOR_EXCLUDE}*" | grep -q .; then echo "release_archive: REFUSED — vendor path under $src"; exit 1; fi
  mkdir -p "$OUT/$(dirname "$src")"; cp -R "$src" "$OUT/$src"; n=$((n + 1)); echo "staged $src"
done
(( n > 0 )) || { echo "release_archive: nothing to stage for record $M8"; exit 1; }
echo "release_archive: $n set(s) for record $M8 -> $OUT"
