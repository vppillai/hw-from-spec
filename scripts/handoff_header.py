#!/usr/bin/env python3
"""scripts/handoff_header.py — the generated header block of the review hand-off (blind-review protocol, references/agent-ops.md).

  python scripts/handoff_header.py [PKG_DIR]     # default: the fab package whose board_id.txt md5 == md5 of the board at HEAD
  python scripts/handoff_header.py --selftest

Prints a markdown table read from the package's board_id.txt (keys: board, md5, commit, built, plus any counts), the committed case
yaml (`case.version`, optional: paths.case_yaml) and the board-mesh provenance sidecar (optional: paths.mesh_provenance). Paste the output
verbatim under "## 0" of the hand-off; nothing in it is typed by hand. A hand-off from a dirty tree, or one that names a board the frozen
worktree does not carry, invalidates the review — both are printed as MISMATCH / DIRTY, never silently.
"""
import datetime, hashlib, json, os, re, subprocess, sys, tempfile

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project import Project  # noqa: E402


def git(root, *a):
    return subprocess.run(["git", *a], cwd=root, capture_output=True, text=True).stdout


def header(P, pkg=None):
    head = git(P.root, "rev-parse", "--short", "HEAD").strip()
    dirty = [l for l in git(P.root, "status", "--short", "--untracked-files=no").splitlines() if l.strip()]
    board = P.get("paths.board")
    head_blob = git(P.root, "show", f"HEAD:{board}")
    head_md5 = hashlib.md5(head_blob.encode()).hexdigest() if head_blob else "(board not in HEAD)"
    fab = P.path("fab_dir")
    pkgs = sorted(p for p in (os.path.join(fab, x) for x in os.listdir(fab)) if os.path.isdir(p)) if os.path.isdir(fab) else []
    pkg = os.path.join(P.root, pkg) if pkg else next((p for p in reversed(pkgs) if p.endswith(head_md5[:8])), pkgs[-1] if pkgs else None)
    rows = []
    if pkg and os.path.exists(os.path.join(pkg, "board_id.txt")):
        bid = dict(l.split(None, 1) for l in open(os.path.join(pkg, "board_id.txt")).read().splitlines() if l.strip())
        counts = ", ".join(f"{k} {v}" for k, v in bid.items() if k not in ("board", "md5", "commit", "built"))
        rows.append(("Board of record", f"`{bid.get('board')}` md5 **`{bid.get('md5')}`** @ commit **{bid.get('commit')}**" + (f", {counts}" if counts else "") + f", built {bid.get('built')}"))
        rows.append(("HEAD board md5 check", f"`git show HEAD:{board} | md5` = `{head_md5}` → " + ("**MATCH**" if head_md5 == bid.get("md5") else
                     f"**MISMATCH — HEAD carries another board; freeze the review worktree at a commit whose board is `{str(bid.get('md5'))[:8]}` (`git log --format=%h -- {board}`) or stop and tell the coordinator**")))
        rows.append(("Fab package", f"`{os.path.relpath(pkg, P.root)}/`"))
    else:
        rows.append(("Board of record", f"**MISSING** — no package under `{P.get('paths.fab_dir')}` carries board_id.txt for HEAD board `{head_md5[:8]}`"))
    cy = P.get("paths.case_yaml")
    if cy:
        case = yaml.safe_load(git(P.root, "show", f"HEAD:{cy}") or "{}") or {}
        rows.append(("Case", f"`case.version: {(case.get('case') or {}).get('version', 'MISSING')}` (committed {cy})"))
    mp = P.get("paths.mesh_provenance")
    if mp:
        t = git(P.root, "show", f"HEAD:{mp}")
        if t:
            prov = json.loads(t)
            rows.append(("Board mesh provenance", f"board md5 `{prov.get('board_md5', '?')[:8]}` @ {prov.get('board_commit')}, mesh md5 `{prov.get('mesh_md5', '?')[:8]}`, {prov.get('facets')} facets"))
        else:
            rows.append(("Board mesh provenance", f"**MISSING** `{mp}` in HEAD"))
    rows.append(("Working tree at hand-off", "**clean** (`git status --short --untracked-files=no` empty — frozen-worktree rule)" if not dirty else
                 f"**DIRTY — {len(dirty)} tracked file(s) modified; commit or stash before freezing the review worktree**: " + "; ".join(l.strip() for l in dirty[:6]) + (" …" if len(dirty) > 6 else "")))
    rows.append(("Generated", f"{datetime.date.today()} by `scripts/handoff_header.py` at HEAD {head}"))
    return "| Item | Value |\n|---|---|\n" + "\n".join(f"| **{k}** | {v} |" for k, v in rows)


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_ho_")
    os.makedirs(f"{d}/kicad/b"); os.makedirs(f"{d}/design")
    open(f"{d}/project.yaml", "w").write("paths: {board: kicad/b/b.kicad_pcb, fab_dir: out/fab, case_yaml: design/case.yaml}\n")
    open(f"{d}/kicad/b/b.kicad_pcb", "w").write("(kicad_pcb (version 1))\n")
    open(f"{d}/design/case.yaml", "w").write("case: {version: v1.0-test}\n")
    md5 = hashlib.md5(open(f"{d}/kicad/b/b.kicad_pcb", "rb").read()).hexdigest()
    pkg = f"{d}/out/fab/2026-01-01_{md5[:8]}"; os.makedirs(pkg)
    open(f"{pkg}/board_id.txt", "w").write(f"board kicad/b/b.kicad_pcb\nmd5 {md5}\ncommit abc1234\nbuilt 2026-01-01\nsegments 12\n")
    run = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True)
    run("init", "-q"); run("add", "-A"); run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    P = Project(f"{d}/project.yaml")
    h = header(P)
    assert "**MATCH**" in h and "segments 12" in h and "v1.0-test" in h and "**clean**" in h, h
    open(f"{d}/kicad/b/b.kicad_pcb", "a").write(";edit\n")
    h = header(P)
    assert "DIRTY" in h and "**MATCH**" in h, "a working-copy edit is DIRTY but HEAD still matches the package"
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "edit")
    assert "MISMATCH" in header(P), "HEAD now carries another board than the package"
    print("selftest OK")


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    else:
        print(header(Project.find(), *[a for a in sys.argv[1:] if not a.startswith("--")]))
