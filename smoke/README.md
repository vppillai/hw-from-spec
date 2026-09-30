# smoke/ — the automated dry run of hw-from-spec

One sheet (five parts: LDO, two capacitors, USB-C, a test point), a two-piece printed case, three owner decisions, one agent proposal
applied with the nod marker, one OPEN owner question, one blocker, a test plan with UNVERIFIED markers. No KiCad, OpenSCAD or network is
needed: the board file is a stub whose md5 keys the fab package, the DFM items are a hand-written fixture standing in for the project's
measurer, renders are copied files.

    ./run_smoke.sh            # copies smoke/ to a temp git repo, drives every generic script end to end, prints the DRAFT report path
    ./run_smoke.sh --keep     # keep the temp repo for a look

What it proves: the three scopes scaffold from one template set (ee / mech / both each get their own gate rows, no tag survives, the yaml
parses) → the printed-enclosure DFM reference still carries its measured rules (1.2 / 1.3 walls, voids, free wedges, one STL per session,
the API verdict at parseStatus 2 with the material set first for price and legend only, no waiver rows) and `thin_wall_census.py --selftest` passes without mesh libraries → known_issues → traceability → dfm_check → collect_renders → assembly_guide (keyed stub renders) → reorg_paths --check (layout of
record) → release_report (DRAFT) → every `--check` OK → handoff_header MATCH/clean → adopt_gates.sh green incl. the clone gate on `git archive HEAD`
and the read-only guard (tree unchanged by the gates) → an owner clear-to-build line flips the reports to RELEASED
and `--check` catches the stale report until regenerated.
