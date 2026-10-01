#!/usr/bin/env bash
# ci/setup_linux.sh — Linux bootstrap for the hw-from-spec gates (copied from templates/ci/; project-owned: extend it, it is yours).
# `NIGHTLY=1` (or the first argument NIGHTLY=1) adds the mesh libraries for print_dfm.py / thin_wall_census.py. Idempotent.
set -e
[[ "$1" == NIGHTLY=1 ]] && NIGHTLY=1
if command -v apt-get >/dev/null; then apt-get update -qq && apt-get install -y -qq git bash python3 python3-venv python3-pip >/dev/null; fi
git config --global --add safe.directory "$PWD"
[[ -x .venv/bin/python ]] || python3 -m venv .venv
.venv/bin/python -m pip install -q --upgrade pip
.venv/bin/python -m pip install -q pyyaml
[[ -n "${NIGHTLY:-}" ]] && .venv/bin/python -m pip install -q numpy trimesh scipy shapely rtree networkx mapbox-earcut
test -e scripts/project.py || { echo "setup_linux: scripts/project.py missing — the submodule is not checked out (actions/checkout needs submodules: recursive)"; exit 1; }
.venv/bin/python -c 'import yaml' && echo "setup_linux: venv ready ($(.venv/bin/python --version))"
