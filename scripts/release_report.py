#!/usr/bin/env python3
"""scripts/release_report.py — the release-report skeleton: every number read from a file, MISSING printed not guessed, DRAFT until the owner's line.

  python scripts/release_report.py             # rewrite every report listed under project.yaml `reports:`
  python scripts/release_report.py --check     # exit 1 when a committed report differs from the regenerated text (volatile lines stripped)
  python scripts/release_report.py --selftest

project.yaml:
  reports:
    - name: PCB_DESIGN_REPORT              # -> paths.reports_dir/<name>.md
      title: "PCB design report"
      sections: [banner, identity, decisions, known_issues, package, traceability, dfm, renders, inventory]   # any subset/order
      extra_sources: [20-design/board.yaml]   # listed with md5 in the identity section; scalars printed (skips note/notes/description/reason)

Sections: banner (DRAFT/RELEASED from paths.gates via markers.release_regex), identity (board md5, the recorded package commit, sources), decisions (OPEN census
+ every row as a 4-cell table), known_issues (§2 of the generated KNOWN_ISSUES), package (the fab package whose board_id.txt md5 == md5(board):
none -> MISSING, several -> exit 1), traceability (census line of the matrix), dfm (open count from dfm.json), renders (index line of
collateral/<md5-8>/renders/RENDERS.md), inventory (every file read: md5 + bytes). Extend by adding a `section_<name>(ctx, P)` function.
Rule: `--check` must pass on a `git archive HEAD` copy — no mtimes, no absolute paths, no dates outside the volatile `Generated` line.
"""
import glob, hashlib, json, os, re, sys, tempfile

import yaml

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project, split_row  # noqa: E402
from gate_check import release_ok  # noqa: E402

VOLATILE = re.compile(r"^Generated .*$", re.M)


class Ctx:
    """Root-relative file access that records every file touched (for the inventory appendix)."""

    def __init__(self, root):
        self.root, self.seen = root, {}

    def p(self, rel):
        return os.path.join(self.root, rel)

    def read(self, rel):
        if not rel or not os.path.isfile(self.p(rel)):
            return None
        raw = open(self.p(rel), "rb").read()
        self.seen[rel] = (hashlib.md5(raw).hexdigest(), len(raw))
        return raw.decode("utf-8", "replace")

    def src(self, *rels):
        return [f"MISSING: `{rel}`" if self.read(rel) is None else f"Source: `{rel}` md5 `{self.seen[rel][0][:8]}`" for rel in rels]

    def yaml(self, rel):
        t = self.read(rel)
        return yaml.safe_load(t) if t else None

    def json(self, rel):
        t = self.read(rel)
        try:
            return json.loads(t) if t else None
        except ValueError:
            return None


def cut(s, n=120):
    s = re.sub(r"<br\s*/?>", " ", str(s)).replace("|", "/").replace("\n", " ").strip()
    return s if len(s) <= n else s[: n - 1] + "…"


def table_rows(text, id_re=None):
    out = []
    for line in (text or "").splitlines():
        if line.startswith("|") and not re.match(r"^\|\s*-", line):
            cells = split_row(line)
            if id_re is None or (cells and id_re.search(cells[0])):
                out.append(cells)
    return out


def scalars(d, prefix=""):
    out = []
    if isinstance(d, dict):
        for k, v in d.items():
            if str(k).lower() in ("note", "notes", "description", "reason"):
                continue
            out += scalars(v, f"{prefix}{k}.")
    elif isinstance(d, list):
        if all(not isinstance(x, (dict, list)) for x in d):
            out.append(f"{prefix[:-1]}: {d}")
    else:
        out.append(f"{prefix[:-1]}: {d}")
    return out


def board_md5(ctx, P):
    """md5 of the record of record: the board file (ee / both; raw bytes, no text round trip) or the STL set (mech: Project.record_md5)."""
    if P.scope() == "mech":
        return P.record_md5()[1]
    rel = P.get("paths.board")
    return ctx.seen[rel][0] if rel and ctx.read(rel) is not None else None


def pkg_for_board(ctx, P, md5=None):
    """The fab package whose board_id.txt md5 EQUALS the board's md5 (default: the working-tree board) — never the newest by mtime."""
    md5 = md5 or board_md5(ctx, P)
    hits = []
    for bid in sorted(glob.glob(ctx.p(f"{P.get('paths.fab_dir')}/*/board_id.txt"))):
        rel = os.path.relpath(bid, ctx.root)
        d = dict(l.split(None, 1) for l in (ctx.read(rel) or "").splitlines() if l.strip())
        if md5 and d.get("md5") == md5:
            hits.append((os.path.dirname(rel), d))
    if len(hits) > 1:
        sys.exit(f"several packages carry board md5 {md5[:8]}: {[h[0] for h in hits]} — keep one package of record")
    return hits[0] if hits else (None, None)


# ---------------------------------------------------------------- sections
def section_banner(ctx, P, rep):
    gates = ctx.read(P.get("paths.gates")) or ""
    released, _ = release_ok(P, gates)                      # the Release row's approval cell, committed by project.owner — the phrase anywhere else, or anyone else's commit, counts for nothing
    return [f"**STATUS: {'RELEASED (the owner release line is in the Release row of ' + P.get('paths.gates') + ', committed by the owner)' if released else 'DRAFT'}** — {rep.get('title', rep['name'])}. "
            f"The banner turns RELEASED only when the owner writes the release line into the Release row's approval cell of `{P.get('paths.gates')}` (regex `{P.get('markers.release_regex')}`) and commits it as `project.owner` (`scripts/gate_check.py --release`); agents never write it.", ""]


def section_identity(ctx, P, rep):
    md5 = board_md5(ctx, P)
    rel, bid = pkg_for_board(ctx, P)   # recorded identity only — never the live git HEAD (the commit that adds this report would make it stale)
    L = ["## Identity", "", f"- {P.record_md5()[0][0].upper() + P.record_md5()[0][1:]} md5 **`{md5 or 'MISSING'}`**"]
    if P.scope() != "mech":   # the fab package is a board artefact; a mech project keys on the STL set alone
        L.append(f"- Built at commit `{bid.get('commit', 'MISSING')}` (recorded in `{rel}/board_id.txt`)" if rel else "- Built at commit: MISSING (no package of record)")
    L += [f"- {s}" for s in ctx.src(P.get("paths.decisions"), P.get("paths.gates"), *(rep.get("extra_sources") or []))]
    for rel in rep.get("extra_sources") or []:
        d = ctx.yaml(rel) if rel.endswith((".yaml", ".yml")) else None
        if d:
            L += ["", f"`{rel}` scalars:", "", *[f"    {s}" for s in scalars(d)[:60]]]
    return L + [""]


def section_decisions(ctx, P, rep):
    rows = table_rows(ctx.read(P.get("paths.decisions")), P.decision_re())
    st = lambda c: re.sub(r"\*\*", "", c[2]).strip()
    opened = [c for c in rows if len(c) > 2 and st(c).startswith("OPEN")]
    L = ["## Decision log", "", f"{len(rows)} rows, **{len(opened)} OPEN** (owner items pending): " + (", ".join(P.decision_re().search(c[0]).group(1) for c in opened) or "none"), "",
         "| ID | Date | Status | Topic |", "|---|---|---|---|"]
    L += [f"| {P.decision_re().search(c[0]).group(1)} | {c[1]} | {cut(st(c), 70)} | {cut(c[3], 110)} |" for c in rows if len(c) >= 4]
    return L + [""]


def section_known_issues(ctx, P, rep):
    t = ctx.read(P.get("paths.known_issues"))
    if t is None:
        return ["## Known issues", "", f"MISSING: `{P.get('paths.known_issues')}`", ""]
    body = t.split("## 2.", 1)[-1]
    body = body.split("## 3.", 1)[0]
    return ["## Known issues (generated index §2)", "", *[l for l in body.splitlines() if l.startswith("|")], ""]


def section_package(ctx, P, rep):
    rel, d = pkg_for_board(ctx, P)
    if not rel:
        return ["## Fab package of record", "", f"MISSING: no package under `{P.get('paths.fab_dir')}` carries board md5 `{(board_md5(ctx, P) or 'MISSING')[:8]}`", ""]
    L = ["## Fab package of record", "", f"`{rel}/` — " + ", ".join(f"{k} {v}" for k, v in d.items() if k != "board"), ""]
    for f in sorted(os.listdir(ctx.p(rel))):
        if os.path.isfile(ctx.p(f"{rel}/{f}")):
            ctx.read(f"{rel}/{f}")
            L.append(f"- `{f}` md5 `{ctx.seen[f'{rel}/{f}'][0][:8]}` {ctx.seen[f'{rel}/{f}'][1]} bytes")
    return L + [""]


def section_traceability(ctx, P, rep):
    t = ctx.read(P.get("paths.traceability_out"))
    if t is None:
        return ["## Traceability", "", f"MISSING: `{P.get('paths.traceability_out')}`", ""]
    census = re.search(r"## Census\n\n(\|.*\n\|.*\n\|.*\n)", t)
    unm = re.search(r"^Unmapped decision rows.*$", t, re.M)
    return ["## Traceability", "", *(census.group(1).splitlines() if census else ["(no census)"]), "", unm.group(0) if unm else "", *ctx.src(P.get("paths.traceability_out")), ""]


def section_dfm(ctx, P, rep):
    d = ctx.json(P.get("fab_dfm.report") or P.get("dfm.report", "out/dfm.json"))
    if d is None:
        return ["## Fab DFM mirror", "", f"MISSING: `{P.get('fab_dfm.report') or P.get('dfm.report', 'out/dfm.json')}`", ""]
    return ["## Fab DFM mirror", "", f"Open (not accepted) items: **{d.get('open')}** of {len(d.get('items', []))} measured; thresholds `{d.get('thresholds')}`", ""]


def section_renders(ctx, P, rep):
    md5 = board_md5(ctx, P)
    rel = f"{P.get('paths.collateral_dir')}/{md5[:8]}/renders/RENDERS.md" if md5 else None
    t = ctx.read(rel)
    if t is None:
        return ["## Renders", "", f"MISSING: `{rel}`", ""]
    return ["## Renders", "", *[l for l in t.splitlines() if l.startswith("|")][:40], *ctx.src(rel), ""]


def section_inventory(ctx, P, rep):
    return ["## Inventory of every file read", "", "| File | md5 | bytes |", "|---|---|---|", *[f"| `{k}` | `{v[0][:8]}` | {v[1]} |" for k, v in sorted(ctx.seen.items())], ""]


SECTIONS = {k[8:]: v for k, v in dict(globals()).items() if k.startswith("section_")}


def render(P, rep):
    ctx = Ctx(P.root)
    L = [f"# {rep.get('title', rep['name'])} — {P.get('project.name', 'project')}", "",
         f"Generated by `scripts/release_report.py`; every number is read from a file (md5 named per section), a missing input prints MISSING. Regenerate, never edit.", ""]
    for s in rep.get("sections", ["banner", "identity", "decisions", "package", "inventory"]):
        if s == "inventory":
            continue
        L += SECTIONS[s](ctx, P, rep) if s in SECTIONS else [f"## {s}", "", f"MISSING: no section_{s} in scripts/release_report.py", ""]
    if "inventory" in rep.get("sections", ["inventory"]):
        L += section_inventory(ctx, P, rep)
    return "\n".join(L) + "\n"


def run(P, check):
    rc = 0
    for rep in P.get("reports", []) or []:
        out = os.path.join(P.path("reports_dir"), f"{rep["name"]}.md")
        new = render(P, rep)
        if check:
            old = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
            if VOLATILE.sub("", old) != VOLATILE.sub("", new):
                print(f"STALE: {out} differs from scripts/release_report.py output"); rc = 1
            else:
                print(f"OK: {out} up to date")
        else:
            os.makedirs(os.path.dirname(out), exist_ok=True)
            open(out, "w", encoding="utf-8").write(new)
            print(f"{out} written ({'RELEASED' if '**STATUS: RELEASED' in new else 'DRAFT'})")
    return rc


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_rr_")
    for sub in ("90-log", "30-board/kicad/b", "30-board/fab/2026-01-01_x", "20-design"):
        os.makedirs(f"{d}/{sub}")
    import subprocess
    subprocess.run(["git", "init", "-q"], cwd=d, check=True)
    open(f"{d}/project.yaml", "w").write("project: {name: t, owner: {name: owner, email: o@o}}\npaths: {board: 30-board/kicad/b/b.kicad_pcb}\nreports:\n  - {name: R, title: test report, sections: [banner, identity, decisions, known_issues, package, traceability, dfm, renders, inventory], extra_sources: [20-design/case.yaml]}\n")
    open(f"{d}/30-board/kicad/b/b.kicad_pcb", "wb").write(b"(kicad_pcb)\n\xe9\r\n")   # a non-UTF-8 byte and a CRLF: the md5 is of the raw bytes
    md5 = hashlib.md5(b"(kicad_pcb)\n\xe9\r\n").hexdigest()
    open(f"{d}/30-board/fab/2026-01-01_x/board_id.txt", "w").write(f"board 30-board/kicad/b/b.kicad_pcb\nmd5 {md5}\ncommit abc\n")
    open(f"{d}/90-log/DECISIONS.md", "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-01 (owner)** | d | **APPROVED** | t | p | r |\n| CC-001 | d | OPEN q | t2 | p | r |\n")
    open(f"{d}/90-log/GATES.md", "w").write("prose: clear to build must not count here\n| **G0** | spec | x | _not yet approved_ |\n| **Release** | reports | y | _not yet written_ |\n")
    open(f"{d}/20-design/case.yaml", "w").write("case: {version: v1, pieces: [tray, hood], note: skip me}\n")
    P = Project(f"{d}/project.yaml")
    assert run(P, False) == 0
    t = open(f"{d}/70-release/reports/R.md").read()
    assert "**STATUS: DRAFT**" in t and f"md5 **`{md5}`**" in t and "**1 OPEN**" in t and "CC-001" in t, t
    assert "`30-board/fab/2026-01-01_x/` — md5" in t and "case.version: v1" in t and "case.pieces: ['tray', 'hood']" in t and "skip me" not in t
    assert "MISSING: `90-log/KNOWN_ISSUES.md`" in t and "MISSING: `90-log/TRACEABILITY.md`" in t and "MISSING: `out/dfm.json`" in t and "MISSING: `70-release/collateral/" in t
    assert run(P, True) == 0
    for f in glob.glob(f"{d}/**/*", recursive=True):
        os.utime(f, (0, 0))
    assert run(P, True) == 0, "--check must survive a mtime change (git archive / clone)"
    open(f"{d}/90-log/GATES.md", "a").write("| **Release** | reports | y | clear to build — owner, 2026-01-02 |\n")
    assert run(P, True) == 1, "a changed input makes the report STALE"
    run(P, False)
    assert "**STATUS: DRAFT" in open(f"{d}/70-release/reports/R.md").read(), "an UNCOMMITTED release cell stays DRAFT"
    subprocess.run(["git", "add", "-A"], cwd=d, check=True); subprocess.run(["git", "-c", "user.name=agent", "-c", "user.email=a@a", "commit", "-qm", "agent"], cwd=d, check=True)
    run(P, False); assert "**STATUS: DRAFT" in open(f"{d}/70-release/reports/R.md").read(), "a release cell committed by a non-owner stays DRAFT (blind review 0.9.0 F2)"
    open(f"{d}/90-log/GATES.md", "a").write("| **Release** | reports | y | clear to build — owner, 2026-01-03 |\n")
    subprocess.run(["git", "add", "-A"], cwd=d, check=True); subprocess.run(["git", "-c", "user.name=owner", "-c", "user.email=o@o", "commit", "-qm", "owner"], cwd=d, check=True)
    run(P, False); assert "**STATUS: RELEASED" in open(f"{d}/70-release/reports/R.md").read(), "the owner's committed cell releases"
    open(f"{d}/30-board/fab/2026-01-01_x/board_id.txt", "a").write("")
    os.makedirs(f"{d}/30-board/fab/2026-01-02_y"); open(f"{d}/30-board/fab/2026-01-02_y/board_id.txt", "w").write(f"md5 {md5}\n")
    try:
        run(P, False); raise AssertionError("two packages for one board must refuse")
    except SystemExit as e:
        assert "several packages" in str(e)
    print("selftest OK")
    return 0


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--check", action="store_true"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--project")
    a = ap.parse_args()   # an unknown flag or --help exits here: the default write action never runs on a probe
    sys.exit(selftest() if a.selftest else run(Project.find(arg=a.project), a.check))
