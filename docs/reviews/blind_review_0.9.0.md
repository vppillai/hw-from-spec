# Blind review — hw-from-spec 0.9.0 (cold `ee` user + enforcement sceptic)

Worktree `/tmp/hwfs_review_wt` (read-only). Read: README.md, SKILL.md, references/, templates/, scripts/, smoke/, evals/, workflows/. Not read: CHANGELOG.md, docs/reviews, docs/retro, git history. Every finding below was reproduced by the command shown; scratch projects live under `…/scratchpad/review/p1…p8`, `skillcopy`, `skillcopy2`. Python 3.13 (`uv`), macOS, zsh.

## What was run

| # | Command (as documented) | Result |
|---|---|---|
| 1 | README Install 1b: `mkdir vendor && ln -s <wt> vendor/hw-from-spec && ln -s vendor/hw-from-spec/scripts scripts` | OK |
| 2 | README Install 2: `uv venv .venv && uv pip install --python .venv/bin/python pyyaml numpy trimesh scipy shapely rtree networkx mapbox-earcut` | OK (trimesh 5.1.0, scipy 1.18.1) |
| 3 | `for s in scripts/*.py; do .venv/bin/python "$s" --selftest; done` | 17/17 `selftest OK`, rc 0 |
| 4 | `scripts/clone_gate.sh --selftest`, `scripts/adopt_gates.sh --selftest` | both `selftest OK` |
| 5 | `vendor/hw-from-spec/smoke/run_smoke.sh` (project venv with mesh libs present) | rc 0 `SMOKE OK`, 45 s; BUT used the **skill's** `.venv`, and printed a yaml traceback mid-run (F3, F6) |
| 6 | same smoke with a project venv holding **pyyaml only** (skill copy without `.venv`) | rc 0, `NOTE: mesh libraries absent … section 0d … SKIPPED`, `(0d SKIPPED: mesh libraries absent)` — skips cleanly and says so; same traceback as 5 |
| 7 | `.venv/bin/python vendor/hw-from-spec/evals/run_evals.py` | `evals: 8 with mechanical checks (0 failed check(s), 0 skipped), 6 manual`, rc 0 |
| 8 | README step 4 copy block with `A0=ee` + `scripts/project.py scaffold --scope ee …` | `scaffold ee: 126 line(s) dropped in 14 file(s)`; no scope tag left |
| 9 | `scripts/project.py slots` | `slots: 169 unfilled in 15 file(s)`, rc 1 (as documented) |
| 10 | `scripts/project.py kickoff --check` (bare, fresh scaffold) | **traceback** `ModuleNotFoundError: No module named 'yaml'` (F1) |
| 11 | `.venv/bin/python scripts/project.py kickoff --check` (fresh scaffold) | **traceback** `yaml.parser.ParserError … project.yaml line 83` (F3) |
| 12 | `scripts/adopt_gates.sh` (fresh scaffold) | same ParserError, `adopt gates: aborted at line 60 (rc 1)` (F3) |
| 13 | SKILL §0 step 6 chain as written: `scripts/known_issues.py` | `ModuleNotFoundError: No module named 'yaml'`, rc 1 (F1) |
| 14 | step 6 with `.venv/bin/python scripts/{known_issues,traceability,release_report}.py` after trivially filling slots | all OK, report `(DRAFT)`; commit; `scripts/adopt_gates.sh` → `adopt gates OK`; `kickoff --check` → `0 problem(s)` once `D-X`→`D-01`; `handoff_header.py` → Board MISSING, tree clean |
| 15 | Same copy block with `A0=mech` | `scaffold mech: 115 line(s) dropped`; GATES rows G0/M1/M2/Case order/Release only; no B*/G*/I3/A3 kickoff rows; no board/fab_dfm/erc keys; CLAUDE/SPEC carry no ERC/DRC/KiCad text — scope isolation OK |
| 16 | (a) `gate_check.py G1` empty / filled; `--release` prose / uncommitted / agent-committed / owner-committed | 1 / 0 / 1 / 1 / 1 / 0 — exactly as claimed; `release_report.py` DRAFT on prose but **RELEASED on the agent-committed cell** (F2) |
| 17 | (b) `erc_gate.py` on hand-made KiCad-format erc.json: error / unaccepted warning / accepted+live decision / unknown decision / REJECTED decision / `excluded: true` / stale entry / wrong field names / missing file | 1 / 1 / 0 / 1 / 1 / 1 / 1 / 1 / 2 — all as claimed |
| 18 | (c) `print_dfm.py --process jlc_mjf_pa12 --out … plate2.stl` / `plate08.stl` | PASS rc 0 / `FLAG … W wall … min 0.799 med 0.8` rc 1 |
| 19 | (c) `--gate <dir>`: body without record / FLAG record / `--open …=WHATEVER` / `--open …=D-08` (APPROVED) / `--open …=D-07` (OPEN) / verdict hand-edited FLAG→PASS / record from `protolabs_mjf_pa12` vs target `jlc_mjf_pa12` / dir whose parent is not a target | 1 / 1 / 1 / 1 / **0** (prints `OPEN D-07 (widen the thin plate)`) / 1 `signature does not verify` / 1 `checked against process row 'protolabs_mjf_pa12' but …dfm_process = 'jlc_mjf_pa12'` / 1 — all as claimed |
| 20 | (c) non-watertight box, two-body STL, two-body with `--bodies 2` | FLAG M rc 1 / FLAG M `2 bodies, expected 1` rc 1 / PASS rc 0 |
| 21 | (d) `thin_wall_census.py --gate-dir`: STL without record / FAIL record / hand-edited `fails: []` / accepted via `print_targets.*.accepted` / acceptance deleted / empty dir | 1 / 1 / 1 `signature does not verify` / 0 / 1 `acceptance was withdrawn` / 1 — all as claimed |
| 22 | (e) `adopt_gates.sh --no-clone`: STL set + no census/print_dfm line; board + no DRC line; schematic + no erc_gate line; erc line commented in yaml | all `GATE FAILED: an artefact exists whose gate line is missing…`; but `echo nodrcyet` satisfies the DRC requirement (F8) |
| 23 | (f) `step2stl.py --canonical plate2.stl --out canon.stl` ×2; `step2stl.py part.step --out x.stl` without cadquery/FreeCAD | identical md5 `f3f0890b…`, sidecar written, decision row printed; rc **2** with the three routes printed — as claimed |
| 24 | (g) `skill_retro.py --project p8 --skill <copy> --out …` with `ids.owner_prefix: OWN`, mixed `-`/`*`/odd bullets | 2 owner topics listed (OWN-01, OWN-02); odd bullet listed in §0 (`line 5`); `--apply` ×2 idempotent for pitfalls + CHANGELOG; NEW process row **silently not folded** when its row line carries a trailing comment (F7) |
| 25 | Doc checks: every `scripts/ templates/ references/ workflows/ smoke/ evals/` path cited in SKILL/README/references/templates exists | 0 missing |
| 26 | README fences balanced (14), fenced lines ≤ 90 chars | OK (0 over) |
| 27 | Source-project identifiers in skill text | none in SKILL/README/templates/scripts; `references/pitfalls.md:3` and `dfm-printed-enclosure.md` §8.2/§8.5 name the source project / its connector family as the labelled worked example (NOTE N5) |

## Findings

### F1 — MAJOR — `scripts/<tool>.py …` is NOT the same command as `.venv/bin/python scripts/<tool>.py …`; SKILL §0 step 6 fails as written
SKILL.md §0 step 1: "Every `scripts/*` is executable: `scripts/<tool>.py …` and `.venv/bin/python scripts/<tool>.py …` are the same command." Every script has `#!/usr/bin/env python3`, so the bare form runs the system interpreter, which on a clean Mac has no pyyaml. §0 step 6 is written entirely in the bare form (`scripts/known_issues.py` → `scripts/traceability.py` → `scripts/release_report.py` → … `scripts/project.py kickoff --check`), and README step 4 relies on `scripts/project.py scaffold / slots` (those two happen to work because of a lazy import).
```
$ scripts/known_issues.py ; echo rc=$?
  File ".../scripts/project.py", line 52, in __init__
    import yaml  # lazy: `scaffold` / `slots` run on a stock python3 ...
ModuleNotFoundError: No module named 'yaml'
rc=1
$ scripts/project.py kickoff --check
ModuleNotFoundError: No module named 'yaml'
```
Fix: either drop the "same command" claim and write every step-6 command as `.venv/bin/python scripts/…` (as README step 3 already does), or make the shebang resolve the project venv (e.g. a tiny `scripts/py` wrapper that `adopt_gates.sh` already knows how to pick).

### F2 — MAJOR — `release_report.py` turns RELEASED on a release cell committed by a NON-owner (and on an uncommitted one)
`templates/GATES.md` line 7–9 tells the owner: "The release reports read this file and stay DRAFT until the owner writes the release phrase … into the Release row's approval cell and commits it as `project.owner` (`scripts/gate_check.py --release` reads the cell and the line's git author …)". Only `gate_check.py` checks the author; the report banner does not.
```
# Release cell written and committed as "Agent Bot <bot@example.com>", project.owner = Owner Person
$ scripts/gate_check.py --release ; echo rc=$?
gate_check: release line `clear to build — Owner Person, 2026-01-04, board abcd1234` — author ('Agent Bot', 'bot@example.com') vs project.owner ['owner person', 'owner@example.com'] -> NOT the owner
rc=1
$ scripts/release_report.py ; grep -o 'STATUS: [A-Z]*' docs/release/R.md
.../docs/release/R.md written (RELEASED)
STATUS: RELEASED
```
(Prose-only phrase → DRAFT, as claimed.) Fix: have `release_report.py` call `gate_check.check_release()` (author check) for the banner, or reword GATES.md / SKILL §1 to say the banner is cell-only and the author is checked only by `--release` / the release-cut gate.

### F3 — MINOR — a freshly scaffolded `project.yaml` is not valid YAML; every yaml-reading script tracebacks until the slots are filled, and the smoke's "template rows FAIL the kickoff check" is proven by that crash
`templates/project.yaml` line 83 `title: {{PROJECT}} PCB design report` parses as a flow mapping. Running the README step-4 sequence then `kickoff --check` or `adopt_gates.sh` (both named in §0 step 6) gives a raw traceback, not a "fill the slots first" message.
```
$ .venv/bin/python scripts/project.py kickoff --check
yaml.parser.ParserError: while parsing a block mapping
  in ".../p1/project.yaml", line 83, column 5
expected <block end>, but found '<scalar>'
$ scripts/adopt_gates.sh
... yaml.parser.ParserError ... adopt gates: aborted at line 60 (rc 1)
```
The same traceback appears inside `run_smoke.sh` output (section 0e, `kick/project.yaml line 83`) while the smoke prints `SMOKE OK`: the negative test `"$PY" scripts/project.py kickoff --check >/dev/null && { FAIL }` passes because the command crashes, not because the check detects template rows. Fix: quote the slot values in the template (`title: "{{PROJECT}} PCB design report"`), catch `yaml.YAMLError` in `Project.__init__` with a "run `project.py slots` first" message, and make the smoke assert on the `KICKOFF:` output rather than on a non-zero rc.

### F4 — MINOR — scaffold leaves `{{SCOPE}}` in five files although the scope was just given, and mangles the SPEC sentence that explains the tags
```
$ grep -rn '{{SCOPE}}' CLAUDE.md SPEC.md project.yaml docs/governance/*.md   # after scaffold --scope ee
CLAUDE.md:3 ... scope **{{SCOPE}}** ...
SPEC.md:12:Scope {{SCOPE}} (kickoff A0): sections tagged  /  are dropped by `scripts/project.py scaffold`; ...
docs/governance/KICKOFF_ANSWERS.md:12:| A0 | scope | {{SCOPE}} | yes | D-{{nn}} | ...
docs/governance/STATUS.md:9: ... scope {{SCOPE}} ...
project.yaml:8:  scope: {{SCOPE}}
```
Template SPEC.md line 12 reads "sections tagged {{ee,both}} / {{mech,both}} are dropped" — the scaffold's tag-stripper eats the literal examples, leaving "tagged  /  ". Fix: `scaffold --scope S` also substitutes `{{SCOPE}}` → S; write the SPEC example tags in a form the regex does not match (e.g. `{{ ee,both }}` or backticked `ee,both`).

### F5 — MINOR — README and SKILL.md disagree on which venv the smoke / evals use, and the smoke prefers the skill's
README Install 2: "ONE venv, the project's `.venv` …; the smoke and every gate use it (a `vendor/hw-from-spec/.venv` is for developing the skill only)". SKILL.md §0 step 1: "the smoke falls back from the skill's own `.venv` to the project's". `smoke/README.md`: "needs the mesh libraries in the skill venv". Observed from a project that has its own `.venv`:
```
$ vendor/hw-from-spec/smoke/run_smoke.sh | head -1
python: /private/tmp/hwfs_review_wt/.venv/bin/python        # the SKILL's venv, not p1/.venv
$ sed -n 11p vendor/hw-from-spec/smoke/run_smoke.sh
VENV=""; for c in "$SKILL/.venv" "$CALLER/.venv"; do ...
$ sed -n 18p vendor/hw-from-spec/evals/run_evals.py
    py = a.python or (os.path.join(SKILL, ".venv", "bin", "python") if os.path.exists(...) else sys.executable)
```
So the toolchain proof of step 3 may run against a venv that is not the one `tools.python` and the gates use. Fix: order `"$CALLER/.venv"` first in the smoke, default `run_evals.py` to `sys.executable` (the README already invokes it with `.venv/bin/python`), and align the three sentences.

### F6 — MINOR — `run_smoke.sh` prints a 40-line Python traceback and still ends `SMOKE OK`
Reproduced in both runs (mesh venv and pyyaml-only venv): lines 72–115 of the output are `Traceback … yaml.parser.ParserError … kick/project.yaml line 83` (see F3) followed by `slots: fresh ee scaffold -> exit 1 …`. A cold user reading the log cannot tell a real failure from this expected one. Fix: `2>/dev/null` on that one negative probe (or assert on the message, F3).

### F7 — MINOR — `skill_retro.py --apply` silently skips a NEW process row whose row-name line carries a trailing comment
Docstring and SKILL §13: "`--apply` … every NEW process row with its citations into the template". With a project row written as `  acme_mjf_pa11:   # NEW vendor row …` (the style `templates/project.yaml` itself uses for `{{VENDOR_TARGET}}:  # e.g. jlc_mjf`):
```
$ skill_retro.py --project p8 --skill skillcopy2 --out p8/retro            # §8 of the report
| NEW | `acme_mjf_pa11` | (row) | ACME / MJF: wall_min 1.1, ... | - |
$ skill_retro.py ... --apply | tail -1
skill_retro --apply: 1 pitfalls line(s) -> references/pitfalls.md; CHANGELOG stub -> CHANGELOG.md      # no process row
$ grep -c acme_mjf_pa11 skillcopy2/templates/design/dfm_processes.yaml
0
# strip the trailing comment from the row-name line and rerun:
skill_retro --apply: process row acme_mjf_pa11 -> templates/design/dfm_processes.yaml
```
Cause: `row_block()` matches `^  <row>:\s*$`. Pitfalls / CHANGELOG folds were idempotent across two `--apply` runs (md5 identical). Fix: match `^  <row>:\s*(#.*)?$` and print a WARNING when a NEW row yields an empty block.

### F8 — MINOR — the "board needs a DRC gate line" check is a case-insensitive substring `drc` anywhere in `gates.adopt`
```
$ cat project.yaml
project: {name: t, scope: ee}
paths: {board: kicad/b/b.kicad_pcb}
gates: {adopt: ["echo nodrcyet"], clone: []}
$ scripts/adopt_gates.sh --no-clone | tail -1
adopt gates OK
```
(`scripts/project.py required_gate_lines`: `re.search(r"drc", lines, re.I)`.) The census / print_dfm / erc checks look for the real token (`--gate-dir`, `print_dfm.py --gate`, `erc_gate.py`) and did fail correctly in every negative case, including a line commented out in the yaml. Fix: require a token such as `drc_gate` / `--drc` or a `gates.drc_line` key the project names.

### F9 — MINOR — `references/project-yaml.md` documents `kickoff:` as a string; the template and `kickoff --check` use a mapping, and the mapping's `answers:` key is never read
```
$ grep -n '^kickoff' templates/project.yaml references/project-yaml.md
templates/project.yaml:11:kickoff:                                      # ... `scripts/project.py kickoff --check`
references/project-yaml.md:16:kickoff: docs/governance/KICKOFF_ANSWERS.md   # the owner's kickoff answers ...
$ grep -n 'kickoff.answers' scripts/project.py
215:    path = P.path("kickoff.answers") if isinstance(P.get("kickoff"), dict) else None    # = paths.kickoff.answers -> None -> default
```
A project that moves KICKOFF_ANSWERS.md and sets `kickoff.answers` is still checked at the default path. Fix: document the mapping in the reference; read `P.get("kickoff.answers")`.

### F10 — MINOR — the documented selftest loop writes `__pycache__` into the submodule
```
$ for s in scripts/*.py; do .venv/bin/python "$s" --selftest; done; ls -d /tmp/hwfs_review_wt/scripts/__pycache__
/tmp/hwfs_review_wt/scripts/__pycache__
```
Harmless for git (the skill's `.gitignore` lists `__pycache__/`) but it is a write into `vendor/hw-from-spec` from a loop SKILL §2 calls read-only; `adopt_gates.sh` sets `PYTHONDONTWRITEBYTECODE=1`, the README loop does not. Fix: `PYTHONDONTWRITEBYTECODE=1 for s in …` in README step 3 / SKILL step 5. (Removed after the review.)

### N1 — NOTE — a G1/G2 approval cell is text-only; an uncommitted cell written by anyone unlocks the next phase
`gate_check.py G1` → rc 0 on `Owner Person, 2026-01-02, abc123` before any commit (`(a2)` above). Documented behaviour (only `--release` checks the author), but the "agents never write approval cells" rule for G0–G2 rests on discipline, not on the script.

### N2 — NOTE — `--open <tag>/<piece>=<id>` accepts any OPEN row, whatever its topic
`--open jlc_mjf/plate08=D-07` passed with D-07 = "widen the thin plate"; any other OPEN row (e.g. an unrelated OPEN owner question) would pass the same way. The id is tied to a decision, not to the body.

### N3 — NOTE — retro report / markers are named after the project DIRECTORY, not `project.name`
`p8_2026-09-30.md`, `## Retro p8 …`, `<!-- retro: p8 … -->` although `project.name: retroproj` (`skill_retro.py:341 project = os.path.basename(root)`). Two projects in folders named `hw/` collide.

### N4 — NOTE — classifier marked three plausible-new learnings CARRIED
With `--threshold 0.5` the magnet-pocket undersize learning and the vendor-rim learning were CARRIED (0 NEW) until an absurd "zebra toroidal quench harness" entry was added. Expected of a keyword matcher and the report says so; a cold user should not read "NEW 0" as "nothing to fold".

### N5 — NOTE — source-project names in references
`references/pitfalls.md:3` ("the source project's (AEC-CT2-MINI, the worked example) learnings log…"), `references/dfm-printed-enclosure.md` §8.2 / §8.5 and `pitfalls.md:263` name a QSFP-DD cap as the worked example. Labelled as worked examples, not leaked constants; SKILL/README/templates/scripts are clean (the smoke greps for this).

### N6 — NOTE — things that worked exactly as claimed (so the sceptic found nothing to add)
`erc_gate.py` (all nine cases incl. GUI exclusion, REJECTED decision, stale entry, wrong field names → `lacks ref, reason`), `print_dfm.py --gate` (signature, md5, process-row mismatch, laxer row, uncensused body, unknown target dir, empty dir), `thin_wall_census.py --gate-dir` (signature, withdrawn acceptance, uncensused body, empty dir), `step2stl.py` (rc 2 + routes; canonical md5 deterministic; the bare executable works without pyyaml), `adopt_gates.sh` read-only guard + `gates-required` for STL/schematic, the mech scaffold's scope isolation, `project.py slots` default set, README fence lengths, every cited path exists, batch count "twelve" = 0–11 in the questionnaire.

## Persona verdict
As a KiCad/JLC engineer starting an `ee` project from the README alone: install and the step-3 proof run green in ~2 minutes, and the enforcement scripts do what they say — every tamper I tried on a census or print-DFM record, every unaccepted ERC warning, every non-owner release line was refused with a message that named the fix. The two things that would stop me cold are F1 (SKILL §0 step 6 is written in a form that cannot run on a stock Mac — I had to guess `.venv/bin/python`) and F3/F6 (the first time I run `kickoff --check` or `adopt_gates.sh` after the copy block I get a YAML traceback with no hint that the slots must be filled first, and the smoke shows the same traceback under `SMOKE OK`). F2 is the one enforcement claim that is false as the owner would read it in GATES.md: a release report goes RELEASED on a cell an agent committed. Fix F1–F3 and reword F5, and the README path is honest end to end; the rest are polish.

## Dispositions (author, after the review; every fix re-run through the reviewer's command)

| # | Sev | Disposition |
|---|---|---|
| F1 | MAJOR | FIXED — SKILL §0 step 1 states the rule (every project.yaml-reading Python command is `.venv/bin/python scripts/<tool>.py`; only scaffold / slots / step2stl / scad_lint / the thin_wall selftests / the .sh gates run bare), step 6 is written in that form; the false "same command" sentence is gone |
| F2 | MAJOR | FIXED — `release_report` banner reads `gate_check.release_ok()`: RELEASED only when the Release cell is committed by `project.owner`; an uncommitted cell and an agent-committed cell stay DRAFT (selftest + smoke step 10); `clone_gate.sh` exports `HWFS_GIT_ROOT` so the archive regen blames the line in the real checkout |
| F3 | MINOR | FIXED — the two report titles are quoted; `Project.__init__` turns a YAML error into one line naming `scripts/project.py slots`; the smoke asserts that message, then fills the slots and asserts the real `KICKOFF:` failures |
| F4 | MINOR | FIXED — `scaffold --scope S` substitutes `{{SCOPE}}`; the SPEC sentence no longer spells the tags; smoke asserts |
| F5 | MINOR | FIXED — the smoke takes the caller's `.venv` first, `run_evals.py` defaults to the interpreter it runs under; README, SKILL §0 and smoke/README say the same thing |
| F6 | MINOR | FIXED with F3 (no traceback in the smoke output; `grep -c Traceback` = 0) |
| F7 | MINOR | FIXED — `row_block()` accepts a trailing comment on the row line; a row that is still not found prints a WARNING; selftest fixture carries the comment |
| F8 | MINOR | FIXED (bounded) — the DRC requirement needs a token starting with `drc` (`\bdrc`): `echo nodrcyet` no longer satisfies it; a project that games it with `echo drc` has gamed its own gate list |
| F9 | MINOR | FIXED — `references/project-yaml.md` documents the `kickoff:` mapping and `board:`; `kickoff --check` reads `kickoff.answers` |
| F10 | MINOR | FIXED — `export PYTHONDONTWRITEBYTECODE=1` precedes the selftest loop in README step 3 and SKILL step 5 |
| N1 | NOTE | ACCEPTED — G0–G2 cells are text by design (the owner types them); the release line is the one with a git-author check because it is the one that flips a record. A per-cell author check is one `line_author` call away if a project wants it |
| N2 | NOTE | FIXED — `--open` requires the OPEN row's topic / proposal to name the piece; an OPEN row about another body fails (selftest + smoke) |
| N3 | NOTE | FIXED — the retro uses `project.name` when project.yaml has it |
| N4 | NOTE | ACCEPTED — the classifier is a keyword matcher; the report says so and lists CARRIED items too |
| N5 | NOTE | ACCEPTED — labelled worked examples in references are the retro's design (the smoke bans identifiers from SKILL / README / templates / scripts) |
| N6 | NOTE | — (confirmations) |
