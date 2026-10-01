#!/usr/bin/env python3
"""scripts/gate_check.py — the gate table read by a script, not by prose: a phase's generators call it before they build (SKILL.md §1.1).

  scripts/gate_check.py G1                exit 0 when the G1 row of paths.gates has owner text in its approval cell (4th cell; `_not yet approved_`
                                          / `_not yet written_` / empty = no), 1 otherwise; prints the cell. Any gate name: G0 G1 G2 M1 M2 ...
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

EMPTY = re.compile(r"^\s*(_not yet (approved|written)_|-|—)?\s*$", re.I)


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


def check_gate(P, gate):
    text = open(P.path("gates"), encoding="utf-8").read() if os.path.exists(P.path("gates")) else ""
    cell = gate_cell(text, gate)
    print(f"gate_check: {gate} {'approved: ' + cell if cell else 'NOT approved (empty cell or no row) in ' + P.get('paths.gates')}")
    return 0 if cell else 1


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="hwfs_gc_"); os.makedirs(f"{d}/docs/governance")
    git = lambda *a, **k: subprocess.run(["git", *a], cwd=d, check=True, capture_output=True, **k)
    git("init", "-q")
    open(f"{d}/project.yaml", "w").write("project: {name: t, owner: {name: Owner Person, email: owner@example.com}}\n")
    G = f"{d}/docs/governance/GATES.md"
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
    print("selftest OK (cells not prose, empty markers, release cell + git author = owner, agent author refused, uncommitted refused, missing owner refused)")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("gate", nargs="?"); ap.add_argument("--release", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--project")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if not (a.gate or a.release):
        ap.error("name a gate (G1) or --release")
    P = Project.find(arg=a.project)
    sys.exit(check_release(P) if a.release else check_gate(P, a.gate))
