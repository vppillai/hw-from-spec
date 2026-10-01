# smoke/ — the automated dry run of hw-from-spec

One sheet (five parts: LDO, two capacitors, USB-C, a test point), a two-piece printed case, three owner decisions, one agent proposal
applied with the nod marker, one OPEN owner question, one blocker, a test plan with UNVERIFIED markers. No KiCad, OpenSCAD or network is
needed: the board file is a stub whose md5 keys the fab package, the DFM items are a hand-written fixture standing in for the project's
measurer, renders are copied files.

    ./run_smoke.sh            # copies smoke/ to a temp git repo, drives every generic script end to end, prints the DRAFT report path
    ./run_smoke.sh --keep     # keep the temp repo for a look

What it proves: the three scopes scaffold from one template set (ee / mech / both each get their own gate rows, no tag survives, the yaml
parses) → the printed-enclosure DFM reference still carries its measured rules (1.2 / 1.3 walls, voids, free wedges, one STL per session,
the API verdict at parseStatus 2 with the material set first for price and legend only, no waiver rows) and `thin_wall_census.py --selftest` passes without mesh libraries → print DFM (0.8.0: the loop
as commands in SKILL.md §8.1, the cited process table + verdict schema as templates, `print_dfm.py --selftest` + `scad_lint.py --selftest`, eval 14's 0.5-root / 1.3-root pair FLAGs / PASSes through the CLI — needs
the mesh libraries in the interpreter the smoke picks: the caller's project `.venv` first, else the skill's `.venv`, else python3; without them section 0d is SKIPPED with a NOTE) → enforcement negatives (0d / 0e: tampered or missing records, a commented gate line, a non-owner release line, the slot counter, the kickoff check) → known_issues → traceability → dfm_check → collect_renders → assembly_guide (keyed stub renders) → reorg_paths --check (layout of
record) → release_report (DRAFT) → every `--check` OK → handoff_header MATCH/clean → adopt_gates.sh green incl. the clone gate on `git archive HEAD`
and the read-only guard (tree unchanged by the gates) → an owner clear-to-build line flips the reports to RELEASED
and `--check` catches the stale report until regenerated.

Runtime: about two minutes on a laptop with the mesh libraries installed (the print-DFM selftest is ~50 s of it; without the libraries
section 0d is skipped and the run takes ~1 min). Step 0c runs the two skill lints (`doc_voice_lint.py`, `generic_lint.py`); step 5d the arrival checklist.
