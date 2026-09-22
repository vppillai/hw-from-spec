# smoke/ — the automated dry run of hw-from-spec

One sheet (five parts: LDO, two capacitors, USB-C, a test point), a two-piece printed case, three owner decisions, one agent proposal
applied with the nod marker, one OPEN owner question, one blocker, a test plan with UNVERIFIED markers. No KiCad, OpenSCAD or network is
needed: the board file is a stub whose md5 keys the fab package, the DFM items are a hand-written fixture standing in for the project's
measurer, renders are copied files.

    ./run_smoke.sh            # copies smoke/ to a temp git repo, drives every generic script end to end, prints the DRAFT report path
    ./run_smoke.sh --keep     # keep the temp repo for a look

What it proves: known_issues → traceability → dfm_check → collect_renders → release_report (DRAFT) → every `--check` OK → handoff_header
MATCH/clean → adopt_gates.sh green incl. the clone gate on `git archive HEAD` → an owner clear-to-build line flips the reports to RELEASED
and `--check` catches the stale report until regenerated.
