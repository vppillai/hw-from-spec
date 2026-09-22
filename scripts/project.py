#!/usr/bin/env python3
"""scripts/project.py — the one place every hw-from-spec script reads its project constants from (references/project-yaml.md).

  from project import Project; P = Project.find()      # walks up from cwd (or $HWFS_PROJECT / --project) to a project.yaml
  P.root, P.path("decisions"), P.get("ids.owner_prefix", "D"), P.id_re()

CLI (for shell scripts):
  scripts/project.py get gates.adopt          # prints the value; a list prints one item per line
  scripts/project.py path decisions           # absolute path of paths.<key>
  scripts/project.py root
  scripts/project.py --selftest
"""
import os, re, sys

import yaml

DEFAULTS = {
    "ids": {"owner_prefix": "D", "agent_prefix": "CC", "blocker_prefix": "B"},
    "markers": {"release_regex": r"clear[ -]to[ -]build", "unverified": ["UNVERIFIED", "TBD-DRAWING"],
                "nod_regex": r"\(!\)|owner nod", "hand_curated": ["<!-- hand-curated: begin -->", "<!-- hand-curated: end -->"]},
    "paths": {"decisions": "docs/DECISIONS.md", "blockers": "docs/BLOCKERS.md", "gates": "docs/GATES.md",
              "known_issues": "docs/KNOWN_ISSUES.md", "test_plan": "docs/TEST_PLAN.md", "status": "docs/STATUS.md",
              "traceability_yaml": "design/traceability.yaml", "traceability_out": "docs/TRACEABILITY.md",
              "fab_dir": "out/fab", "release_dir": "docs/release", "collateral_dir": "docs/release/collateral"},
    "tools": {"python": ".venv/bin/python", "kicad_cli": "kicad-cli", "kicad_python": "python3"},
}


class Project:
    def __init__(self, path):
        self.file = os.path.abspath(path)
        self.root = os.path.dirname(self.file)
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

    def id_re(self):
        o, a, b = (self.get(f"ids.{k}") for k in ("owner_prefix", "agent_prefix", "blocker_prefix"))
        return re.compile(r"\b(%s-\d+[a-z]?|%s-\d{3}|%s-\d{2})\b" % (re.escape(o), re.escape(a), re.escape(b)))

    def decision_re(self):
        o, a = self.get("ids.owner_prefix"), self.get("ids.agent_prefix")
        return re.compile(r"\b(%s-\d+[a-z]?|%s-\d{3})\b" % (re.escape(o), re.escape(a)))


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
    assert P.path("decisions") == f"{d}/d/D.md" and P.path("gates") == f"{d}/docs/GATES.md" and P.path("zz") is None
    assert P.tool("python") == f"{d}/.venv/bin/python" and P.tool("kicad_cli") == "kicad-cli"
    assert P.id_re().findall("D-01 AG-002 B-03 CC-004") == ["D-01", "AG-002", "B-03"] and P.decision_re().findall("D-2a AG-002 B-03") == ["D-2a", "AG-002"]
    assert split_row("| a | b \\| c | d |") == ["a", "b \\| c", "d"], "an escaped pipe is content"
    print("selftest OK")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        sys.exit(selftest())
    if len(argv) < 2 or argv[1] not in ("get", "path", "root"):
        sys.exit(__doc__)
    P = Project.find()
    if argv[1] == "root":
        print(P.root)
    elif argv[1] == "path":
        print(P.path(argv[2]) or "")
    else:
        v = P.get(argv[2], "")
        print("\n".join(str(x) for x in v) if isinstance(v, list) else v)


if __name__ == "__main__":
    main(sys.argv)
