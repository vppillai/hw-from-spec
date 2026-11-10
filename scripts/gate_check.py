#!/usr/bin/env python3
"""scripts/gate_check.py — the gate table read by a script, not by prose: a phase's generators call it before they build (SKILL.md §1.1).

  scripts/gate_check.py G1                exit 0 when the G1 row of paths.gates has owner text in its approval cell (4th cell; `_not yet approved_`
                                          / `_not yet written_` / empty = no), or a `> delegated: G1, ...` line under the table whose committed
                                          git author is project.owner (full gate id per comma field, quoted words excluded; prints DELEGATED),
                                          AND the approval is bound to its artefact as it is now (review 0.12.3): every labelled `commit <sha>`
                                          / `md5 <md5-8>` token of the cell leaves the artefact unchanged (G0 the SPEC, G1 every schematic sheet,
                                          G2 / Order the board, M1 / M2 / Case order the STL set of record). A delegation with no token binds to
                                          the commit that wrote its line. A change = STALE APPROVAL; no token = UNBOUND; both exit 1. A gate
                                          whose artefact does not exist yet needs no token.
  scripts/gate_check.py --md5 G1          print the md5-8 of the gate's artefact, for the owner's cell.
  scripts/gate_check.py --release         exit 0 when the Release row's approval cell matches markers.release_regex AND the line's git author is
                                          project.owner (name or email, case-insensitive; `git blame` on the committed line — an uncommitted
                                          line, another author, or no git history here = 1). The release phrase anywhere else in the file counts
                                          for nothing (a quoted chat line or a STATUS-style sentence once flipped every report).
  scripts/gate_check.py --selftest

A project generator for the next phase refuses to run while `gate_check.py <gate>` is 1 (e.g. the placement script before G1), and
`scripts/release_report.py` reads the Release cell through `release_cell()` for its banner. Agents never write the cells (CLAUDE.md rule 4).
"""
import os, re, subprocess, sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project, split_row  # noqa: E402

EMPTY = re.compile(r"^[\s_*]*(not[\s_]+yet(?![a-z]).*|tbd|pending|n/a|-|—)?[\s_*]*$", re.I)   # a placeholder is not an approval


def gate_rows(text):
    """{gate: (line_no, approval cell)} for every table row whose first cell is a gate name (bold stripped); the LAST row of a name wins."""
    out = {}
    for n, line in enumerate(text.splitlines(), 1):
        if not line.startswith("|"):
            continue
        c = split_row(line)
        if len(c) >= 4:
            name = re.sub(r"\*", "", c[0]).strip()
            if name and not name.startswith("-") and name.lower() != "gate":
                out[name] = (n, c[3].strip())
    return out


def gate_cell(text, gate):
    """The approval cell of `gate` or None when the row is missing or the cell is empty."""
    for name, (n, cell) in gate_rows(text).items():
        if name.lower() == gate.lower():
            return None if EMPTY.match(cell) else cell
    return None


def release_cell(P, text):
    """The Release row's approval cell when it carries the release phrase; None otherwise."""
    cell = gate_cell(text, "Release")
    return cell if cell and re.search(P.get("markers.release_regex"), cell, re.I) else None


def line_author(path, lineno, root=None):
    """(name, email) of the committed line per `git blame`, or None when uncommitted / no git. Inside a `git archive` copy (the clone gate) there is
    no .git: `$HWFS_GIT_ROOT` (exported by clone_gate.sh) names the real checkout and the same relative file is blamed there (HEAD content = the archive)."""
    cands = [(os.path.dirname(path), os.path.basename(path))]
    g = os.environ.get("HWFS_GIT_ROOT")
    if g and root:
        cands.append((g, os.path.relpath(path, root)))
    out = None
    for cwd, rel in cands:
        try:
            out = subprocess.run(["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", "--", rel], cwd=cwd, capture_output=True, text=True, check=True).stdout; break
        except (subprocess.CalledProcessError, FileNotFoundError):
            continue
    if out is None:
        return None
    if "Not Committed Yet" in out or out.startswith("0" * 40):
        return None
    name = re.search(r"^author (.*)$", out, re.M); mail = re.search(r"^author-mail <(.*)>$", out, re.M)
    return (name.group(1).strip() if name else "", mail.group(1).strip() if mail else "")


def owner_matches(P, author):
    o = P.get("project.owner")
    if not o:
        return False, "project.owner is not set in project.yaml (name / email of the person who writes the gate cells)"
    names = {str(o).strip().lower()} if not isinstance(o, dict) else {str(v).strip().lower() for v in o.values() if v}
    hit = author and any(a and a.lower() in names for a in author)
    return bool(hit), f"author {author!r} vs project.owner {sorted(names)}"


def release_ok(P, text=None):
    """(released: bool, reason) — the Release cell carries the phrase AND its committed git author is project.owner. release_report's banner reads this."""
    if text is None:
        text = open(P.path("gates"), encoding="utf-8").read() if os.path.exists(P.path("gates")) else ""
    cell = release_cell(P, text)
    if not cell:
        return False, f"no release phrase in the Release row's approval cell of {P.get('paths.gates')}"
    n = next(v[0] for k, v in gate_rows(text).items() if k.lower() == "release")
    author = line_author(P.path("gates"), n, P.root)
    if author is None:
        return False, f"the release line ({P.get('paths.gates')}:{n}) is not committed, or there is no git history here — the owner commits it; run in the working tree (the clone gate exports HWFS_GIT_ROOT)"
    ok, why = owner_matches(P, author)
    return ok, f"release line `{cell}` — {why} -> {'OWNER' if ok else 'NOT the owner'}"


def check_release(P):
    ok, why = release_ok(P)
    print("gate_check:", why)
    return 0 if ok else 1


def delegation_lines(text):
    """[(line_no, {gate ids})] for every `> delegated:` line under the gate table; one full gate id per comma field (0.11.18 [gates/gate-ids]).
    The quoted owner words are not split: `"yes, G1"` inside the quote names no gate."""
    last = max((n for n, _ in gate_rows(text).values()), default=0)
    return [(n, {f.strip().strip("*").lower() for f in l[len("> delegated:"):].split('"')[0].split(",")})
            for n, l in enumerate(text.splitlines(), 1) if n > last and l.startswith("> delegated:")]


def gate_approved(P, text, gate):
    """(how, detail, line_no): ("cell", cell, n) for an owner cell, ("DELEGATED", line, n) for a `> delegated: <gate>` line committed by
    project.owner, (None, reason, 0) otherwise. Approval only; gate_status() adds the binding. Review 0.12.3."""
    cell = gate_cell(text, gate)
    if cell:
        return "cell", cell, next(v[0] for k, v in gate_rows(text).items() if k.lower() == gate.lower())
    why = "empty cell or no row, and no `> delegated: " + gate + "` line committed by project.owner"
    for n, ids in delegation_lines(text):
        if gate.lower() in ids:
            author = line_author(P.path("gates"), n, P.root)
            ok, w = owner_matches(P, author) if author else (False, "the line is not committed")
            if ok:
                return "DELEGATED", text.splitlines()[n - 1], n
            why = f"delegation line {n}: {w}"
    return None, why, 0


def line_commit(path, lineno, root=None):
    """The commit that last wrote line `lineno` (git blame), or None."""
    g = os.environ.get("HWFS_GIT_ROOT")
    for cwd, rel in [(os.path.dirname(path), os.path.basename(path))] + ([(g, os.path.relpath(path, root))] if g and root else []):
        r = subprocess.run(["git", "blame", "-L", f"{lineno},{lineno}", "--porcelain", "--", rel], cwd=cwd, capture_output=True, text=True)
        if r.returncode == 0 and r.stdout and not r.stdout.startswith("0" * 40):
            return r.stdout.split()[0]
    return None


def artefact(P, gate):
    """(label, [pathspec globs relative to the root]) of the artefact a gate approves, or None (SKILL.md §1.1 step 2):
    G0 the SPEC, G1 every schematic sheet beside paths.schematic, G2 / Order (board) the board, M1 / M2 / Case order the STL set of record."""
    g = gate.lower()
    if g == "g0" and P.get("paths.spec"):
        return "SPEC", [P.get("paths.spec")]
    if g == "g1" and P.get("paths.schematic"):
        return "schematic sheets", [os.path.join(os.path.dirname(P.get("paths.schematic")), "*.kicad_sch")]
    if g in ("g2", "order (board)", "order") and P.get("paths.board"):
        return "board", [P.get("paths.board")]
    if g in ("m1", "m2", "case order") and P.get("paths.mech_record"):
        return "STL set", [P.get("paths.mech_record")]
    return None


def artefact_md5(P, globs):
    """md5 of the sorted `<relpath> <md5>` lines of every file the globs match (one file: its own md5), or None when none exists."""
    import glob, hashlib
    files = sorted({f for gl in globs for f in glob.glob(os.path.join(P.root, gl)) if os.path.isfile(f)})
    if not files:
        return None
    if len(files) == 1:
        return hashlib.md5(open(files[0], "rb").read()).hexdigest()
    lines = [f"{os.path.relpath(f, P.root)} {hashlib.md5(open(f, 'rb').read()).hexdigest()}" for f in files]
    return hashlib.md5("\n".join(lines).encode()).hexdigest()


TOKEN = re.compile(r"\b(commit|md5(?:-8)?)\s*[:=]?\s*`?([0-9a-f]{7,40})\b", re.I)   # labelled tokens only: a bare date or order number never binds


def binding(P, gate, text, commit=None):
    """(state, note): state "ok" | "STALE" | "UNBOUND" | "none" (no artefact to bind). Every labelled `commit <sha>` / `md5 <hex>` token of the
    approval text must match the artefact now; `commit` (a delegation line's own commit) is used when the text has no token."""
    a = artefact(P, gate)
    if not a or artefact_md5(P, a[1]) is None:
        return "none", f"no artefact of record for {gate} yet"
    label, globs = a
    cwd = os.environ.get("HWFS_GIT_ROOT") or P.root
    toks = TOKEN.findall(text) or ([("commit", commit)] if commit else [])
    if not toks:
        return "UNBOUND", f"no `commit <sha>` or `md5 <md5-8>` for the {label}; `scripts/gate_check.py --md5 {gate}` prints the md5-8"
    m = artefact_md5(P, globs)
    notes = []
    for kind, tok in toks:
        if kind.lower() == "commit":
            if subprocess.run(["git", "rev-parse", "-q", "--verify", tok + "^{commit}"], cwd=cwd, capture_output=True).returncode != 0:
                return "STALE", f"commit {tok} is not in this history"
            same = subprocess.run(["git", "diff", "--quiet", tok, "--", *[f":(glob){g}" for g in globs]], cwd=cwd).returncode == 0
            notes.append(f"{label} {'unchanged' if same else 'CHANGED'} since commit {tok}")
        else:
            same = m.startswith(tok.lower())
            notes.append(f"{label} md5 {m[:8]} vs {tok}")
        if not same:
            return "STALE", "; ".join(notes)
    return "ok", "; ".join(notes)


def gate_status(P, text, gate):
    """(ok, word, detail) — the one reader for gate_check and project.py gates-required: approved (cell or owner-committed delegation)
    AND bound to the artefact as it is now. word: approved | DELEGATED | NOT approved | STALE APPROVAL | UNBOUND."""
    how, detail, n = gate_approved(P, text, gate)
    if not how:
        return False, "NOT approved", detail
    state, note = binding(P, gate, detail, line_commit(P.path("gates"), n, P.root) if how == "DELEGATED" else None)
    word = {"STALE": "STALE APPROVAL", "UNBOUND": "UNBOUND"}.get(state, "DELEGATED" if how == "DELEGATED" else "approved")
    return state in ("ok", "none"), word, f"{detail} — {note}"


def check_gate(P, gate):
    text = open(P.path("gates"), encoding="utf-8").read() if os.path.exists(P.path("gates")) else ""
    ok, word, detail = gate_status(P, text, gate)
    print(f"gate_check: {gate} {word}: {detail}" + ("" if ok or word != "NOT approved" else f" in {P.get('paths.gates')}"))
    return 0 if ok else 1


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="hwfs_gc_"); os.makedirs(f"{d}/90-log")
    git = lambda *a, **k: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, **k)
    git("init", "-q")
    open(f"{d}/project.yaml", "w").write("project: {name: t, owner: {name: Owner Person, email: owner@example.com}}\n")
    G = f"{d}/90-log/GATES.md"
    rows = "| Gate | Meaning | Prerequisites | Owner approval |\n|---|---|---|---|\n| **G0** | spec | x | _not yet approved_ |\n| **G1** | sch | x | Owner Person, 2026-01-02, abc123 |\n| **Release** | reports | y | _not yet written_ |\n"
    open(G, "w").write("# GATES\nA sentence that must not count: clear to build is the phrase.\n\n" + rows)
    P = Project(f"{d}/project.yaml")
    assert check_gate(P, "G1") == 0 and check_gate(P, "G0") == 1 and check_gate(P, "G2") == 1, "cells, not prose"
    assert check_release(P) == 1, "the phrase in prose counts for nothing"
    open(G, "a").write("| **Release** | reports | y | clear to build — Owner Person, 2026-01-04, board abcd1234 |\n")
    assert check_release(P) == 1, "uncommitted release line"
    git("add", "-A"); git("-c", "user.name=Agent Bot", "-c", "user.email=bot@example.com", "commit", "-qm", "agent wrote it")
    assert check_release(P) == 1, "an agent's commit is not the owner's"
    t = open(G).read().replace("board abcd1234", "board abcd1235"); open(G, "w").write(t)
    git("add", "-A"); git("-c", "user.name=Owner Person", "-c", "user.email=owner@example.com", "commit", "-qm", "owner line")
    assert check_release(P) == 0, "the owner's committed line releases"
    P.cfg["project"]["owner"] = "owner@example.com"; assert check_release(P) == 0, "a plain string owner (email) matches too"
    P.cfg["project"]["owner"] = None; assert check_release(P) == 1, "no owner named = no release"
    assert release_cell(Project(f"{d}/project.yaml"), rows) is None and gate_cell(rows, "G1").startswith("Owner Person")
    # review 0.12.3: a delegation line counts only when the owner committed it; full gate id per comma field
    P = Project(f"{d}/project.yaml")
    open(G, "a").write('\n> delegated: G0 (case spec), Owner Person, 2026-01-05 09:00, "go"\n> delegated: G2, Owner Person, 2026-01-05 09:00, "lay it out"\n')
    assert check_gate(P, "G2") == 1, "an uncommitted delegation line"
    git("add", "-A"); git("-c", "user.name=Agent Bot", "-c", "user.email=bot@example.com", "commit", "-qm", "agent quotes")
    assert check_gate(P, "G2") == 1, "a delegation line an agent committed"
    open(G, "a").write('> delegated: G2, Owner Person, 2026-01-05 10:00, "lay it out"\n')
    git("add", "-A"); git("-c", "user.name=Owner Person", "-c", "user.email=owner@example.com", "commit", "-qm", "owner delegates")
    assert check_gate(P, "G2") == 0 and gate_approved(P, open(G).read(), "G2")[0] == "DELEGATED", "the owner's committed delegation"
    assert check_gate(P, "G0") == 1, "`G0 (case spec)` is not G0"
    # review 0.12.3: the quoted owner words name no gate
    open(G, "a").write('> delegated: G0 (case spec), Owner Person, 2026-01-05 10:00, "yes, G1"\n')
    git("add", "-A"); git("-c", "user.name=Owner Person", "-c", "user.email=owner@example.com", "commit", "-qm", "quote")
    assert check_gate(P, "G1") == 0 and "approved" in gate_status(P, open(G).read(), "G1")[1], "G1 keeps its own cell"
    assert gate_approved(P, open(G).read().replace("| **G1** | sch | x | Owner Person, 2026-01-02, abc123 |", ""), "G1")[0] is None, "a gate id inside the quote"
    # review 0.12.3: a cell binds to its artefact by a labelled commit or md5; a change after it is STALE APPROVAL; no token is UNBOUND
    def owner_commit(msg):
        git("add", "-A"); git("-c", "user.name=Owner Person", "-c", "user.email=owner@example.com", "commit", "-qm", msg)
    os.makedirs(f"{d}/10-spec"); S = f"{d}/10-spec/SPEC.md"; open(S, "w").write("spec r1\n"); owner_commit("spec")
    head = git("rev-parse", "--short=8", "HEAD", text=True).stdout.strip(); m8 = artefact_md5(P, ["10-spec/SPEC.md"])[:8]
    for tok in (f"commit {head}", f"md5 {m8}", f"20260106, md5-8 `{m8}`"):
        open(G, "a").write(f"| **G0** | spec | x | Owner Person, 2026-01-06, {tok} |\n")
        assert check_gate(P, "G0") == 0, f"bound to {tok}, unchanged (a bare compact date is no token)"
        open(S, "w").write("spec r2\n"); assert gate_status(P, open(G).read(), "G0")[1] == "STALE APPROVAL", f"after the spec moved ({tok})"
        open(S, "w").write("spec r1\n")
    open(G, "a").write("| **G0** | spec | x | Owner Person, 2026-01-06, SPEC r1 |\n"); assert gate_status(P, open(G).read(), "G0")[1] == "UNBOUND", "no token"
    # G1 binds every sheet beside the root; M1 the STL set; a delegation binds to the commit that wrote it
    P.cfg.setdefault("paths", {}).update({"schematic": "k/k.kicad_sch", "mech_record": "40-case/*/parts/*.stl"})
    os.makedirs(f"{d}/k"); open(f"{d}/k/k.kicad_sch", "w").write("root"); open(f"{d}/k/port_a.kicad_sch", "w").write("a"); owner_commit("sch")
    open(G, "a").write(f"| **G1** | sch | x | Owner Person, 2026-01-07, md5 {artefact_md5(P, ['k/*.kicad_sch'])[:8]} |\n")
    assert check_gate(P, "G1") == 0; open(f"{d}/k/port_a.kicad_sch", "w").write("a2"); assert check_gate(P, "G1") == 1, "a sub-sheet edit makes G1 stale"
    os.makedirs(f"{d}/40-case/v/parts"); open(f"{d}/40-case/v/parts/lid.stl", "w").write("solid"); owner_commit("stl")
    open(G, "a").write('> delegated: M1, Owner Person, 2026-01-08 09:00, "print it"\n'); owner_commit("owner delegates M1")
    assert gate_status(P, open(G).read(), "M1")[1] == "DELEGATED", "bound to the commit that wrote the line"
    open(f"{d}/40-case/v/parts/lid.stl", "w").write("solid2"); assert gate_status(P, open(G).read(), "M1")[1] == "STALE APPROVAL", "the STL moved after the delegation"
    for ph in ("TBD", "pending", "Pending", "not yet approved", "Not yet", "_not yet approved_", "not_yet_approved", "**TBD**", "n/a", "", "—"):
        assert gate_cell(f"| **G2** | pcb | x | {ph} |\n", "G2") is None, f"placeholder {ph!r} read as approved"
    print("selftest OK (cells not prose, empty markers and placeholders (TBD, pending, not yet), release cell + git author = owner, agent author refused, uncommitted refused, missing owner refused, owner-committed delegation = DELEGATED, agent or uncommitted delegation refused, labelled commit / md5 binding, STALE APPROVAL and UNBOUND, sub-sheets, STL set, bound delegations, quoted words)")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("gate", nargs="?"); ap.add_argument("--release", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--project"); ap.add_argument("--md5", metavar="GATE")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.gate or a.release or a.md5):
        ap.error("name a gate (G1), --md5 GATE or --release")
    P = Project.find(arg=a.project)
    if a.md5:
        ar = artefact(P, a.md5); m = artefact_md5(P, ar[1]) if ar else None
        print(f"md5 {m[:8]}" if m else f"no artefact of record for {a.md5}"); sys.exit(0 if m else 1)
    sys.exit(check_release(P) if a.release else check_gate(P, a.gate))
