#!/usr/bin/env bash
# scripts/jobs.sh — the ONE heavy-job pool of the machine (references/agent-ops.md §8): every OpenSCAD / slicer / renderer / FEA / record-round
# command runs through it, never directly. A slot semaphore (mkdir-atomic, portable: macOS has no flock), `nice -n 10`, and a resource gate —
# a new heavy job does not START while free memory < MIN_FREE_GB or load1 > cores (it waits, then gives up after --wait-max). Start / stop,
# wall time and peak RSS are logged so the retro can see where the time went.
#   scripts/jobs.sh [--max N] [--min-free-gb G] [--wait-max S] [--log FILE] [--tag T] -- <command> [args...]
#   scripts/jobs.sh --status          # slots in use, free memory, load
#   scripts/jobs.sh --selftest
# Nothing here is a machine constant: pool size = --max, else $HWFS_JOBS_MAX, else project.yaml host.jobs_max, else max(1, cores // 4); memory
# floor = --min-free-gb, else $HWFS_MIN_FREE_GB, else project.yaml host.min_free_gb, else max(2 GB, 15 % of RAM) — derived from the host at run
# time (`scripts/project.py env` prints the same numbers for ENV.md). Exit: the command's exit code; 2 = the gate stayed closed for --wait-max
# seconds (nothing started) or usage.
set -u
HERE=$(cd "$(dirname "$0")" && pwd -P)
cores() { sysctl -n hw.ncpu 2>/dev/null || nproc 2>/dev/null || echo 4; }
ram_gb() { if [[ -r /proc/meminfo ]]; then awk '/MemTotal/ {printf "%.0f", $2 / 1048576}' /proc/meminfo; else awk -v b="$(sysctl -n hw.memsize)" 'BEGIN {printf "%.0f", b / 1073741824}'; fi; }
project_get() { local d=$PWD; while [[ "$d" != "/" ]]; do [[ -f "$d/project.yaml" ]] && { "${PYTHON:-python3}" "$HERE/project.py" get "$1" 2>/dev/null; return; }; d=$(dirname "$d"); done; }
load1() { if [[ -r /proc/loadavg ]]; then cut -d' ' -f1 /proc/loadavg; else sysctl -n vm.loadavg | tr -d '{}' | awk '{print $1}'; fi; }
free_gb() {
  if [[ -r /proc/meminfo ]]; then awk '/MemAvailable/ {printf "%.1f", $2 / 1048576}' /proc/meminfo
  else vm_stat | awk -v ps="$(sysctl -n hw.pagesize)" '/Pages (free|inactive|speculative)/ {gsub("\\.", "", $NF); n += $NF} END {printf "%.1f", n * ps / 1073741824}'; fi
}
pool_max() {
  [[ -n "${HWFS_JOBS_MAX:-}" ]] && { echo "$HWFS_JOBS_MAX"; return; }
  local v; v=$(project_get host.jobs_max); [[ -n "$v" ]] && { echo "$v"; return; }
  local c; c=$(cores); echo $(( c / 4 > 0 ? c / 4 : 1 ))
}
min_free_default() {
  [[ -n "${HWFS_MIN_FREE_GB:-}" ]] && { echo "$HWFS_MIN_FREE_GB"; return; }
  local v; v=$(project_get host.min_free_gb); [[ -n "$v" ]] && { echo "$v"; return; }
  awk -v r="$(ram_gb)" 'BEGIN {f = r * 0.15; printf "%.1f", (f > 2 ? f : 2)}'
}
DIR=${HWFS_JOBS_DIR:-${TMPDIR:-/tmp}/hwfs_jobs}; mkdir -p "$DIR"
take_slot() {   # mkdir is atomic; a slot whose owner pid is dead is stale and reclaimed
  local i; for ((i = 1; i <= $1; i++)); do
    if mkdir "$DIR/slot.$i" 2>/dev/null; then echo $$ > "$DIR/slot.$i/pid"; echo "$i"; return 0; fi
    local p; p=$(cat "$DIR/slot.$i/pid" 2>/dev/null || echo 0); if [[ "$p" == 0 ]] || ! kill -0 "$p" 2>/dev/null; then rm -rf "$DIR/slot.$i"; mkdir "$DIR/slot.$i" 2>/dev/null && { echo $$ > "$DIR/slot.$i/pid"; echo "$i"; return 0; }; fi
  done; return 1
}
status() { local n=0 i; for i in "$DIR"/slot.*; do [[ -d "$i" ]] && n=$((n + 1)); done; echo "jobs: $n slot(s) in use (pool $(pool_max) on $(cores) cores / $(ram_gb) GB), free $(free_gb) GB (floor $(min_free_default) GB), load1 $(load1)"; }

if [[ "${1:-}" == "--selftest" ]]; then
  T=$(mktemp -d "${TMPDIR:-/tmp}/hwfs_jobs_XXXX"); export HWFS_JOBS_DIR=$T/pool HWFS_JOBS_MAX=2; LOG=$T/jobs.log
  # three jobs through a 2-slot pool: never more than 2 slot dirs at once; every job logs wall + rss
  for j in 1 2 3; do "$0" --log "$LOG" --min-free-gb 0 -- bash -c "sleep 0.6; ls -d $T/pool/slot.* | wc -l | tr -d ' ' >> $T/seen" & done; wait
  [[ $(sort -n "$T/seen" | tail -1) -le 2 ]] || { echo "selftest FAILED: more than 2 slots in use ($(cat "$T/seen" | tr '\n' ' '))"; exit 1; }
  [[ $(grep -c '^DONE' "$LOG") == 3 ]] && grep -q 'wall=' "$LOG" && grep -q 'rss_mb=' "$LOG" || { echo "selftest FAILED: log"; cat "$LOG"; exit 1; }
  ls -d $T/pool/slot.* 2>/dev/null | grep -q . && { echo "selftest FAILED: a slot was not released"; exit 1; }
  "$0" --log "$LOG" --min-free-gb 0 -- bash -c 'exit 7'; [[ $? == 7 ]] || { echo "selftest FAILED: the command's exit code must pass through"; exit 1; }
  "$0" --log "$LOG" --min-free-gb 100000 --wait-max 1 -- true; [[ $? == 2 ]] || { echo "selftest FAILED: a closed gate must exit 2 after --wait-max"; exit 1; }
  grep -q '^REFUSED' "$LOG" || { echo "selftest FAILED: the refusal is not logged"; exit 1; }
  mkdir -p "$T/pool/slot.1"; echo 999999 > "$T/pool/slot.1/pid"; HWFS_JOBS_MAX=1 "$0" --log "$LOG" --min-free-gb 0 -- true || { echo "selftest FAILED: a stale slot (dead pid) must be reclaimed"; exit 1; }
  "$0" --status >/dev/null || { echo "selftest FAILED: --status"; exit 1; }
  [[ $(cores) -ge 1 && $(ram_gb) -ge 1 ]] && awk -v f="$(min_free_default)" 'BEGIN {exit !(f + 0 >= 2)}' || { echo "selftest FAILED: host facts"; exit 1; }
  rm -rf "$T"; echo "selftest OK (2-slot pool holds 3 jobs to ≤ 2 at once, slots released, exit code passes through, closed gate exits 2 and is logged, stale slot reclaimed, host-derived floor ≥ 2 GB, --status)"; exit 0
fi
MAX=""; MINFREE=""; WAITMAX=1800; LOG=${HWFS_JOBS_LOG:-}; TAG=""
while [[ $# -gt 0 ]]; do case "$1" in
  --max) MAX=$2; shift 2;; --min-free-gb) MINFREE=$2; shift 2;; --wait-max) WAITMAX=$2; shift 2;; --log) LOG=$2; shift 2;; --tag) TAG=$2; shift 2;;
  --status) status; exit 0;; -h|--help) sed -n '2,10p' "$0"; exit 0;; --) shift; break;; *) echo "jobs.sh: unknown option $1 (use -- before the command)" >&2; exit 2;; esac; done
[[ $# -gt 0 ]] || { sed -n '2,10p' "$0"; exit 2; }
[[ -n "$MAX" ]] || MAX=$(pool_max); [[ -n "$MINFREE" ]] || MINFREE=$(min_free_default); [[ -n "$LOG" ]] || LOG=$DIR/jobs.log
C=$(cores); waited=0
while :; do
  F=$(free_gb); L=$(load1)
  if awk -v f="$F" -v m="$MINFREE" -v l="$L" -v c="$C" 'BEGIN {exit !(f + 0 >= m + 0 && l + 0 <= c + 0)}'; then
    SLOT=$(take_slot "$MAX") && break
    why="pool full ($MAX)"
  else why="free ${F} GB < ${MINFREE} GB or load1 ${L} > cores ${C}"; fi
  if (( waited >= WAITMAX )); then echo "REFUSED $(date +%FT%T) ${TAG:+$TAG }$why: $*" >> "$LOG"; echo "jobs: REFUSED after ${waited}s — $why" >&2; exit 2; fi
  sleep 5; waited=$((waited + 5))
done
trap 'rm -rf "$DIR/slot.$SLOT"' EXIT
echo "START $(date +%FT%T) slot=$SLOT/$MAX ${TAG:+$TAG }free_gb=$F load1=$L: $*" >> "$LOG"
T0=$(date +%s); TF=$(mktemp "${TMPDIR:-/tmp}/hwfs_time_XXXX")
if [[ "$(uname)" == Darwin ]]; then /usr/bin/time -l nice -n 10 "$@" 2> "$TF"; RC=$?; RSS=$(awk '/maximum resident set size/ {printf "%d", $1 / 1048576}' "$TF")
else /usr/bin/time -v nice -n 10 "$@" 2> "$TF"; RC=$?; RSS=$(awk '/Maximum resident set size/ {printf "%d", $NF / 1024}' "$TF"); fi
grep -vE '^[[:space:]]+[0-9.]+[[:space:]]+(real|user|sys|maximum|average|page|block|signals|voluntary|involuntary|messages|swaps|instructions|cycles|peak)|^[[:space:]]*(Command being timed|User time|System time|Percent of CPU|Elapsed|Average|Maximum resident|Major|Minor|Voluntary|Involuntary|Swaps|File system|Socket|Signals|Page size|Exit status)' "$TF" >&2 || true
rm -f "$TF"
echo "DONE  $(date +%FT%T) slot=$SLOT rc=$RC wall=$(( $(date +%s) - T0 ))s rss_mb=${RSS:-?} ${TAG:+$TAG }: $*" >> "$LOG"
exit $RC
