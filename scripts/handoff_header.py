#!/usr/bin/env python3
"""scripts/handoff_header.py — the generated header block of the review hand-off (blind-review protocol, references/agent-ops.md).

  python scripts/handoff_header.py [PKG_DIR]     # default: the fab package whose board_id.txt md5 == md5 of the board at HEAD (content match, release_report.pkg_for_board)
  python scripts/handoff_header.py --selftest

Prints a markdown table read from the package's board_id.txt (keys: board, md5, commit, built, plus any counts), the committed case
yaml (`case.version`, optional: paths.case_yaml) and the board-mesh provenance sidecar (optional: paths.mesh_provenance). Paste the output
verbatim under "## 0" of the hand-off; nothing in it is typed by hand. A hand-off from a dirty tree, or one that names a board the frozen
worktree does not carry, invalidates the review — both are printed as MISMATCH / DIRTY, never silently.
"""
import datetime, hashlib, json, os, subprocess, sys, tempfile

import yaml

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project  # noqa: E402
from release_report import Ctx as RCtx, pkg_for_board  # noqa: E402


def git(root, *a):
    return subprocess.run(["git", *a], cwd=root, capture_output=True).stdout   # bytes: CRLF and non-UTF-8 boards hash as committed


def header(P, pkg=None):
    head = git(P.root, "rev-parse", "--short", "HEAD").decode().strip()
    dirty = [l for l in git(P.root, "status", "--short", "--untracked-files=no").decode("utf-8", "replace").splitlines() if l.strip()]
    board = P.get("paths.board")
    head_blob = git(P.root, "show", f"HEAD:{board}") if board else b""
    head_md5 = hashlib.md5(head_blob).hexdigest() if head_blob else None
    if pkg:
        pkg = os.path.join(P.root, pkg)
    elif head_md5:
        rel, _ = pkg_for_board(RCtx(P.root), P, md5=head_md5)   # content match on the HEAD board, never a folder-name suffix
        pkg = os.path.join(P.root, rel) if rel else None
    rows = []
    if pkg and os.path.exists(os.path.join(pkg, "board_id.txt")):
        bid = dict(l.split(None, 1) for l in open(os.path.join(pkg, "board_id.txt")).read().splitlines() if l.strip())
        counts = ", ".join(f"{k} {v}" for k, v in bid.items() if k not in ("board", "md5", "commit", "built"))
        rows.append(("Board of record", f"`{bid.get('board')}` md5 **`{bid.get('md5')}`** @ commit **{bid.get('commit')}**" + (f", {counts}" if counts else "") + f", built {bid.get('built')}"))
        rows.append(("HEAD board md5 check", f"`git show HEAD:{board} | md5` = `{head_md5}` → " + ("**MATCH**" if head_md5 == bid.get("md5") else
                     f"**MISMATCH — HEAD carries another board; freeze the review worktree at a commit whose board is `{str(bid.get('md5'))[:8]}` (`git log --format=%h -- {board}`) or stop and tell the coordinator**")))
        rows.append(("Fab package", f"`{os.path.relpath(pkg, P.root)}/`"))
    elif P.scope() == "mech":
        label, m = P.record_md5()   # the STL set of record; the clean-tree row below makes it the HEAD set
        rows.append(("Mechanical record", f"{label} md5 **`{m}`**" if m else f"**MISSING** — no file matches `{P.get('paths.mech_record')}`; expected before M1"))
    else:
        rows.append(("Board of record", f"**MISSING** — no package under `{P.get('paths.fab_dir')}` carries board_id.txt for the HEAD board `{head_md5[:8]}`" if head_md5
                     else f"**MISSING** — no board in HEAD (`{board}`); expected before G1 (spec review: the briefing is 10-spec/SPEC.md, see references/schematic-phase.md)"))
    cy = P.get("paths.case_yaml")
    if cy:
        case = yaml.safe_load(git(P.root, "show", f"HEAD:{cy}").decode("utf-8", "replace") or "{}") or {}
        rows.append(("Case", f"`case.version: {(case.get('case') or {}).get('version', 'MISSING')}` (committed {cy})"))
    mp = P.get("paths.mesh_provenance")
    if mp:
        t = git(P.root, "show", f"HEAD:{mp}").decode("utf-8", "replace")
        if t:
            prov = json.loads(t)
            if "source" in prov:   # mech scope: an imported STEP / envelope {source, source_md5, tag: V|K}
                rows.append(("Fit input of record", f"`{prov.get('source')}` md5 `{str(prov.get('source_md5', '?'))[:8]}` [{prov.get('tag', 'K')}]"))
            else:
                rows.append(("Board mesh provenance", f"board md5 `{prov.get('board_md5', '?')[:8]}` @ {prov.get('board_commit')}, mesh md5 `{prov.get('mesh_md5', '?')[:8]}`, {prov.get('facets')} facets"))
        else:
            rows.append(("Board mesh provenance", f"**MISSING** `{mp}` in HEAD"))
    rows.append(("Working tree at hand-off", "**clean** (`git status --short --untracked-files=no` empty — frozen-worktree rule)" if not dirty else
                 f"**DIRTY — {len(dirty)} tracked file(s) modified; commit or stash before freezing the review worktree**: " + "; ".join(l.strip() for l in dirty[:6]) + (" …" if len(dirty) > 6 else "")))
    rows.append(("Generated", f"{datetime.date.today()} by `scripts/handoff_header.py` at HEAD {head}"))
    return "| Item | Value |\n|---|---|\n" + "\n".join(f"| **{k}** | {v} |" for k, v in rows)


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_ho_")
    os.makedirs(f"{d}/30-board/kicad/b"); os.makedirs(f"{d}/20-design")
    open(f"{d}/project.yaml", "w").write("paths: {board: 30-board/kicad/b/b.kicad_pcb, fab_dir: 30-board/fab, case_yaml: 20-design/case.yaml}\n")
    open(f"{d}/30-board/kicad/b/b.kicad_pcb", "wb").write(b"(kicad_pcb (version 1))\r\n\xe9\n")   # CRLF + a non-UTF-8 byte: hashed as bytes
    open(f"{d}/20-design/case.yaml", "w").write("case: {version: v1.0-test}\n")
    md5 = hashlib.md5(open(f"{d}/30-board/kicad/b/b.kicad_pcb", "rb").read()).hexdigest()
    pkg = f"{d}/30-board/fab/rev0"; os.makedirs(pkg)   # the folder is the revision; board_id.txt carries the md5
    open(f"{pkg}/board_id.txt", "w").write(f"board 30-board/kicad/b/b.kicad_pcb\nmd5 {md5}\ncommit abc1234\nbuilt 2026-01-01\nsegments 12\n")
    run = lambda *a: subprocess.run(["git", *a], cwd=d, capture_output=True, text=True, check=True)
    run("init", "-q"); run("add", "-A"); run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "init")
    other = f"{d}/30-board/fab/rev1"; os.makedirs(other)   # a NEWER package for another board: must not be picked
    open(f"{other}/board_id.txt", "w").write("board 30-board/kicad/b/b.kicad_pcb\nmd5 0000\ncommit ffff\nbuilt 2026-01-02\n")
    run("add", "-A"); run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "pkg2")
    P = Project(f"{d}/project.yaml")
    h = header(P)
    assert "**MATCH**" in h and "segments 12" in h and "v1.0-test" in h and "**clean**" in h and "`30-board/fab/rev0/`" in h and "rev1" not in h, h
    open(f"{d}/30-board/kicad/b/b.kicad_pcb", "a").write(";edit\n")
    h = header(P)
    assert "DIRTY" in h and "**MATCH**" in h, "a working-copy edit is DIRTY but HEAD still matches the package"
    run("-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qam", "edit")
    h = header(P)
    assert "MISSING" in h and "no package" in h, ("HEAD now carries a board no package records", h)
    P.cfg["paths"]["board"] = "30-board/kicad/none.kicad_pcb"
    assert "no board in HEAD" in header(P), "a project before G1 has no board: say so, no slicing of a message"
    print("selftest OK")


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--project"); ap.add_argument("args", nargs="?")
    a = ap.parse_args()
    sys.exit(selftest() if a.selftest else print(header(Project.find(arg=a.project), a.args)))
