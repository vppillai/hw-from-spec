#!/usr/bin/env python3
"""scripts/project.py — the one place every hw-from-spec script reads its project constants from (references/project-yaml.md).

  from project import Project; P = Project.find()      # walks up from cwd (or $HWFS_PROJECT / --project) to a project.yaml
  P.root, P.path("decisions"), P.get("ids.owner_prefix", "D"), P.id_re()

CLI (for shell scripts):
  scripts/project.py get gates.adopt          # prints the value; a list prints one item per line
  scripts/project.py path decisions           # absolute path of paths.<key>
  scripts/project.py root
  scripts/project.py scope                    # ee | mech | both (project.scope, default both)
  scripts/project.py record                   # "<label> <md5>" of the record of record: the board (ee/both) or the STL set paths.mech_record (mech)
  scripts/project.py scaffold --scope S FILE...   # resolve the {{ee,both}}-style scope tags of copied templates in place: a tagged line stays only
                                              # when S is in its list (tag removed); untagged lines stay. Then `grep -rn '{{'` must print nothing.
  scripts/project.py gates-required           # exit 1 when an artefact exists (schematic, board, the STL set) and gates.adopt has no gate line for it
  scripts/project.py --selftest

Record signing (print_dfm / thin_wall_census records): `sig` = sha256 of the canonical JSON body (sorted keys, no `sig`) + the tool VERSION;
`verify_sig(rec, VERSION)` is False for a hand-edited record or one written by another rule set — the PURE gates refuse it.
"""
import glob, hashlib, json, os, re, sys

SCOPES = ("ee", "mech", "both")
SCOPE_TAG = re.compile(r"\{\{((?:ee|mech|both)(?:,(?:ee|mech|both))*)\}\}")

DEFAULTS = {
    "project": {"scope": "both"},   # ee = PCB/PCBA only, mech = enclosure / printed / CNC parts only, both = a housed board (SKILL.md §1)
    "ids": {"owner_prefix": "D", "agent_prefix": "CC", "blocker_prefix": "B"},
    "markers": {"release_regex": r"clear[ -]to[ -]build", "unverified": ["UNVERIFIED", "TBD-DRAWING"],
                "nod_regex": r"\(!\)|owner nod", "placed_regex": r"\bPLACED\b", "hand_curated": ["<!-- hand-curated: begin -->", "<!-- hand-curated: end -->"]},
    # the docs/ layout: governance/ (records the generators read and write), design/ (intent), parts/, reviews/, release/, quotes/<date>/,
    # production/<md5-8>/, datasheet_notes/ — a re-layout is a `reorg:` block + scripts/reorg_paths.py, never a hand sweep
    "paths": {"decisions": "docs/governance/DECISIONS.md", "blockers": "docs/governance/BLOCKERS.md", "gates": "docs/governance/GATES.md",
              "known_issues": "docs/governance/KNOWN_ISSUES.md", "status": "docs/governance/STATUS.md", "learnings": "docs/governance/LEARNINGS_LOG.md",
              "erc_waivers": "docs/governance/ERC_WAIVERS.md", "env": "docs/governance/ENV.md", "traceability_yaml": "design/traceability.yaml",
              "traceability_out": "docs/governance/TRACEABILITY.md", "test_plan": "docs/design/TEST_PLAN.md",
              "parts_verification": "docs/parts/PARTS_VERIFICATION.md", "datasheet_notes": "docs/datasheet_notes", "reviews_dir": "docs/reviews",
              "quotes_dir": "docs/quotes", "production_dir": "docs/production", "fab_dir": "out/fab", "release_dir": "docs/release",
              "collateral_dir": "docs/release/collateral", "mech_record": "out/mechanical/case/*/stl/*.stl"},
    "tools": {"python": ".venv/bin/python", "kicad_cli": "kicad-cli", "kicad_python": "python3"},
}


class Project:
    def __init__(self, path):
        self.file = os.path.abspath(path)
        self.root = os.path.dirname(self.file)
        import yaml  # lazy: `scaffold` / `slots` run on a stock python3 before any venv exists (blind review 0.8.0 F2)
        with open(self.file, encoding="utf-8") as f:
            self.cfg = yaml.safe_load(f) or {}

    @classmethod
    def find(cls, start=None, arg=None):
        p = arg or os.environ.get("HWFS_PROJECT")
        if p:
            return cls(p)
        d = os.path.abspath(start or os.getcwd())
        while True:
            c = os.path.join(d, "project.yaml")
            if os.path.exists(c):
                return cls(c)
            if os.path.dirname(d) == d:
                sys.exit("project.yaml not found (walk up from cwd, or set HWFS_PROJECT / --project)")
            d = os.path.dirname(d)

    def get(self, dotted, default=None):
        keys = dotted.split(".")
        cur = self.cfg
        for k in keys:
            if isinstance(cur, dict) and k in cur:
                cur = cur[k]
            else:
                break
        else:
            return cur
        d = DEFAULTS
        for k in keys:
            if isinstance(d, dict) and k in d:
                d = d[k]
            else:
                return default
        return d

    def path(self, key, default=None):
        rel = self.get(f"paths.{key}", default)
        return os.path.join(self.root, rel) if rel else None

    def tool(self, key):
        v = self.get(f"tools.{key}")
        return os.path.join(self.root, v) if v and v.startswith(".") else v

    def scope(self):
        v = self.get("project.scope") or "both"
        if v not in SCOPES:
            sys.exit(f"project.scope must be one of {SCOPES}, not {v!r}")
        return v

    def record_md5(self):
        """(label, md5) of the record every md5-keyed consumer uses: the board file (ee / both) or, in mech scope, the STL set of record
        (paths.mech_record glob; md5 of the sorted `<relpath> <md5>` lines — moves when any STL moves). md5 None = MISSING."""
        if self.scope() != "mech":
            b = self.path("board")
            return (f"board `{self.get('paths.board')}`", hashlib.md5(open(b, "rb").read()).hexdigest() if b and os.path.exists(b) else None)
        pat = self.get("paths.mech_record")
        files = sorted(glob.glob(os.path.join(self.root, pat)))
        lines = [f"{os.path.relpath(f, self.root)} {hashlib.md5(open(f, 'rb').read()).hexdigest()}" for f in files]
        return (f"mechanical record `{pat}` ({len(files)} files)", hashlib.md5("\n".join(lines).encode()).hexdigest() if files else None)

    def id_re(self):
        o, a, b = (self.get(f"ids.{k}") for k in ("owner_prefix", "agent_prefix", "blocker_prefix"))
        return re.compile(r"\b(%s-\d+[a-z]?|%s-\d{3}|%s-\d{2})\b" % (re.escape(o), re.escape(a), re.escape(b)))

    def decision_re(self):
        o, a = self.get("ids.owner_prefix"), self.get("ids.agent_prefix")
        return re.compile(r"\b(%s-\d+[a-z]?|%s-\d{3})\b" % (re.escape(o), re.escape(a)))


def scaffold(scope, files):
    """Resolve the scope tags of copied templates in place (see the module docstring); returns the number of lines dropped."""
    if scope not in SCOPES:
        sys.exit(f"--scope must be one of {SCOPES}")
    dropped = 0
    for f in files:
        out = []
        for line in open(f, encoding="utf-8"):
            tags = SCOPE_TAG.findall(line)
            if tags and not any(scope in t.split(",") for t in tags):
                dropped += 1; continue
            out.append(SCOPE_TAG.sub("", line).rstrip() + "\n" if tags else line)
        open(f, "w", encoding="utf-8").write("".join(out))
    return dropped


def record_sig(rec, version):
    """sha256 of the canonical JSON body (sorted keys, `sig` excluded) and the tool version."""
    body = {k: v for k, v in rec.items() if k != "sig"}
    return hashlib.sha256((json.dumps(body, sort_keys=True, separators=(",", ":")) + "|" + str(version)).encode()).hexdigest()


def verify_sig(rec, version):
    return isinstance(rec, dict) and rec.get("sig") == record_sig(rec, version)


def open_decisions(path):
    """{id: topic} of the decision-log rows whose status cell starts with OPEN (bold stripped) — the only ids `--open` may name."""
    out = {}
    for line in open(path, encoding="utf-8") if os.path.exists(path) else []:
        if not line.startswith("|"):
            continue
        c = split_row(line)
        if len(c) >= 4 and re.sub(r"\*", "", c[2]).strip().upper().startswith("OPEN"):
            m = re.search(r"\b([A-Z]+-\d+[a-z]?)\b", c[0])
            if m:
                out[m.group(1)] = re.sub(r"\*", "", c[3]).strip()
    return out


def required_gate_lines(P):
    """An artefact that exists must have its gate line in gates.adopt (commented lines are not lines): the schematic -> erc_gate.py, the board ->
    a DRC gate, the STL set (paths.mech_record) -> thin_wall_census --gate-dir AND print_dfm --gate. -> problem list (blind review 0.8.0 F11)."""
    lines = " ".join(str(x) for x in (P.get("gates.adopt") or []))
    bad = []
    sch = P.path("schematic")
    if sch and os.path.exists(sch) and "erc_gate.py" not in lines:
        bad.append(f"schematic {P.get('paths.schematic')} exists but gates.adopt has no `scripts/erc_gate.py` line")
    board = P.path("board")
    if board and os.path.exists(board) and not re.search(r"drc", lines, re.I):
        bad.append(f"board {P.get('paths.board')} exists but gates.adopt has no DRC gate line")
    pat = P.get("paths.mech_record")
    if pat and glob.glob(os.path.join(P.root, pat)):
        for tok, what in (("--gate-dir", "thin_wall_census.py --gate-dir"), ("print_dfm.py --gate", "print_dfm.py --gate")):
            if tok not in lines:
                bad.append(f"STL set {pat} has files but gates.adopt has no `{what}` line")
    return bad


def split_row(line):
    """Cells of a markdown table row; a backslash-escaped pipe inside a cell is content, not a separator."""
    return [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="hwfs_pr_")
    open(f"{d}/project.yaml", "w").write("project: {name: t}\nids: {agent_prefix: AG}\npaths: {decisions: d/D.md}\ntools: {python: .venv/bin/python, kicad_cli: kicad-cli}\n")
    P = Project.find(start=d)
    assert P.get("ids.agent_prefix") == "AG" and P.get("ids.owner_prefix") == "D", "explicit key wins, missing key falls back to DEFAULTS"
    assert P.get("markers.release_regex") and P.get("nope.x", 7) == 7
    assert P.path("decisions") == f"{d}/d/D.md" and P.path("gates") == f"{d}/docs/governance/GATES.md" and P.path("zz") is None
    assert P.tool("python") == f"{d}/.venv/bin/python" and P.tool("kicad_cli") == "kicad-cli"
    assert P.id_re().findall("D-01 AG-002 B-03 CC-004") == ["D-01", "AG-002", "B-03"] and P.decision_re().findall("D-2a AG-002 B-03") == ["D-2a", "AG-002"]
    assert split_row("| a | b \\| c | d |") == ["a", "b \\| c", "d"], "an escaped pipe is content"
    # scope + record id: board md5 in ee / both, the STL set in mech, MISSING when absent
    assert P.scope() == "both" and P.record_md5()[1] is None, "no board: MISSING"
    os.makedirs(f"{d}/out/mechanical/case/v1/stl"); open(f"{d}/out/mechanical/case/v1/stl/a.stl", "wb").write(b"A")
    P.cfg["project"] = {"scope": "mech"}
    lbl, m = P.record_md5(); assert m and "1 files" in lbl and P.scope() == "mech"
    open(f"{d}/out/mechanical/case/v1/stl/b.stl", "wb").write(b"B"); assert P.record_md5()[1] != m, "a new STL moves the mech record md5"
    open(f"{d}/t.md", "w").write("all\n| G1 | {{ee,both}}\n| M1 | {{mech}}\n{{ee,both}}{{mech}} either\n")
    assert scaffold("mech", [f"{d}/t.md"]) == 1 and open(f"{d}/t.md").read() == "all\n| M1 |\n either\n", open(f"{d}/t.md").read()
    # record signing, OPEN rows, required gate lines
    r = dict(a=1, b=[1.5, "x"]); r["sig"] = record_sig(r, "1.0"); assert verify_sig(r, "1.0") and not verify_sig(dict(r, a=2), "1.0") and not verify_sig(r, "1.1")
    open(f"{d}/D.md", "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-07** | d | **OPEN** | widen root | p | r |\n| CC-010 | d | APPLIED | x | p | r |\n| CC-011 | d | OPEN (owner) | y | p | r |\n")
    assert open_decisions(f"{d}/D.md") == {"D-07": "widen root", "CC-011": "y"}, open_decisions(f"{d}/D.md")
    P.cfg["paths"] = {"mech_record": "out/mechanical/case/*/stl/*.stl", "schematic": "k/k.kicad_sch"}; P.cfg["gates"] = {"adopt": ["$PY scripts/known_issues.py --check"]}
    bad = required_gate_lines(P); assert len(bad) == 2 and "--gate-dir" in bad[0] and "print_dfm.py --gate" in bad[1], bad
    P.cfg["gates"]["adopt"] += ["$PY scripts/thin_wall_census.py --gate-dir out/x/census", "$PY scripts/print_dfm.py --gate out/x/dfm"]
    assert required_gate_lines(P) == []
    os.makedirs(f"{d}/k"); open(f"{d}/k/k.kicad_sch", "w").write("x"); assert "erc_gate.py" in required_gate_lines(P)[0]
    print("selftest OK (defaults, paths, ids, scope, record md5, scaffold, record signing, OPEN rows, required gate lines)")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        sys.exit(selftest())
    if len(argv) > 1 and argv[1] in ("--help", "-h"):
        print(__doc__); return
    if len(argv) < 2 or argv[1] not in ("get", "path", "root", "scope", "record", "scaffold", "gates-required"):
        sys.exit(__doc__)
    if argv[1] == "scaffold":
        if len(argv) < 5 or argv[2] != "--scope":
            sys.exit(__doc__)
        print(f"scaffold {argv[3]}: {scaffold(argv[3], argv[4:])} line(s) dropped in {len(argv) - 4} file(s)"); return
    P = Project.find()
    if argv[1] == "gates-required":
        bad = required_gate_lines(P)
        for b in bad:
            print("GATES REQUIRED:", b)
        sys.exit(1 if bad else 0)
    if argv[1] == "root":
        print(P.root)
    elif argv[1] == "scope":
        print(P.scope())
    elif argv[1] == "record":
        lbl, m = P.record_md5(); print(f"{lbl} md5 {m or 'MISSING'}")
    elif argv[1] == "path":
        print(P.path(argv[2]) or "")
    else:
        v = P.get(argv[2], "")
        print("\n".join(str(x) for x in v) if isinstance(v, list) else v)


if __name__ == "__main__":
    main(sys.argv)
