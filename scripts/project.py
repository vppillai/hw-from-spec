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
  scripts/project.py rev                      # the revision that names folders (project.revision, default rev0): <fab_dir>/<rev>/, <production_dir>/<rev>/, collateral/<rev>/
  scripts/project.py scaffold --scope S FILE...   # resolve the {{ee,both}}-style scope tags of copied templates in place: a tagged line stays only
                                              # when S is in its list (tag removed); untagged lines stay; the {{SCOPE}} slot becomes S. Then `slots`.
  scripts/project.py gates-required           # exit 1 when an artefact exists (schematic, board, the STL set) and gates.adopt has no gate line for it
  scripts/project.py slots [FILE|DIR ...]     # the unfilled {{...}} slots per file (default: CLAUDE.md 10-spec/SPEC.md project.yaml docs design — CI workflow
                                              # files are the ci/README's own `{{PROJECT_` grep); lines between
                                              # `<!-- skeleton: begin -->` / `<!-- skeleton: end -->` are skipped; exit 1 while any slot remains
  scripts/project.py kickoff --check          # every answered KICKOFF_ANSWERS row (not n/a, not a slot) has its `Written to` project.yaml keys set
                                              # and a real D row id; exit 1 otherwise
  scripts/project.py env                      # the host row for 90-log/ENV.md: cores, RAM, the heavy-job pool size and memory floor
                                              # scripts/jobs.sh derives (project.yaml host: {jobs_max, min_free_gb} overrides them) — no machine constant lives in the skill
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
    # the layout of record (references/project-yaml.md §Layout): ten numbered folders in the order of the project's life — 00-now (the five
    # answer pages) 10-spec 20-design 30-board 40-case 50-kits 60-orders 70-release 80-reviews 90-log; folders are named for what they hold
    # (a revision is rev0, a kit is its print target), the hash lives inside. A re-layout is a `reorg:` block + scripts/reorg_paths.py.
    "paths": {"now_dir": "00-now", "spec_dir": "10-spec", "spec": "10-spec/SPEC.md", "kickoff_answers": "10-spec/KICKOFF_ANSWERS.md",
              "datasheet_notes": "10-spec/datasheet_notes", "spec_errata": "10-spec/SPEC_ERRATA.md",
              "design_dir": "20-design", "test_plan": "20-design/TEST_PLAN.md", "erc_accept": "20-design/erc_accept.yaml",
              "traceability_yaml": "20-design/traceability.yaml", "dfm_thresholds": "20-design/dfm_thresholds.json",
              "board_dir": "30-board", "layout_dir": "30-board/layout", "fab_dir": "30-board/fab",
              "dfm_items": "30-board/layout/dfm_items.json", "dfm_report": "30-board/layout/dfm.json",
              "case_dir": "40-case", "mech_record": "40-case/*/parts/*.stl",
              "kits_dir": "50-kits", "kits_mirror": "~/Downloads/<project>_kits",   # outside the tree; the kit writer expands <project>
              "orders_dir": "60-orders", "parts_verification": "60-orders/PARTS_VERIFICATION.md", "procurement": "60-orders/PROCUREMENT.md",
              "quotes_dir": "60-orders/quotes",
              "release_dir": "70-release", "production_dir": "70-release", "reports_dir": "70-release/reports",
              "collateral_dir": "70-release/collateral", "marketing_dir": "70-release/marketing",
              "reviews_dir": "80-reviews", "reorg_rewrites": "80-reviews/REORG_REWRITES.txt",
              "log_dir": "90-log", "decisions": "90-log/DECISIONS.md", "status": "90-log/STATUS.md", "gates": "90-log/GATES.md",
              "blockers": "90-log/BLOCKERS.md", "known_issues": "90-log/KNOWN_ISSUES.md", "learnings": "90-log/LEARNINGS_LOG.md",
              "env": "90-log/ENV.md", "traceability_out": "90-log/TRACEABILITY.md"},
    "tools": {"python": ".venv/bin/python", "kicad_cli": "kicad-cli", "kicad_python": "python3"},
}


class Project:
    def __init__(self, path):
        self.file = os.path.abspath(path)
        self.root = os.path.dirname(self.file)
        import yaml  # lazy: `scaffold` / `slots` run on a stock python3 before any venv exists (blind review 0.8.0 F2)
        with open(self.file, encoding="utf-8") as f:
            try:
                self.cfg = yaml.safe_load(f) or {}
            except yaml.YAMLError as e:
                sys.exit(f"{self.file}: not valid YAML ({str(e).splitlines()[0]}) — unfilled {{{{…}}}} slots? run `scripts/project.py slots` and fill them first")

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
                print("project.yaml not found (walk up from cwd, or set HWFS_PROJECT / --project)", file=sys.stderr); sys.exit(2)
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

    def rev(self):
        """The project revision that names folders (`project.revision`, default rev0): the fab package, the cut, collateral and marketing
        folders are `<dir>/<rev>/`; the record hash lives INSIDE each (board_id.txt, RENDERS.md, MANIFEST), never in a folder name."""
        v = str(self.get("project.revision") or "rev0")
        if not re.fullmatch(r"[A-Za-z0-9._-]+", v):
            sys.exit(f"project.revision must be a folder-safe name (rev0, rev1a), not {v!r} — it names 30-board/fab/<rev>, 70-release/<rev>, …")
        return v

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
            line = line.replace("{{SCOPE}}", scope)
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
    """{id: topic + proposal text} of the decision-log rows whose status cell starts with OPEN (bold stripped) — the only ids `--open` may name;
    the gate also requires the row's text to name the piece (any OPEN row is not a licence for every body)."""
    out = {}
    for line in open(path, encoding="utf-8") if os.path.exists(path) else []:
        if not line.startswith("|"):
            continue
        c = split_row(line)
        if len(c) >= 4 and re.sub(r"\*", "", c[2]).strip().upper().startswith("OPEN"):
            m = re.search(r"\b([A-Z]+-\d+[a-z]?)\b", c[0])
            if m:
                out[m.group(1)] = re.sub(r"\*", "", " ".join(c[3:])).strip()
    return out


def required_gate_lines(P):
    """An artefact that exists must have its gate line in gates.adopt (commented lines are not lines): the schematic -> erc_gate.py, the board ->
    a DRC gate, EVERY STL set of paths.mech_record -> thin_wall_census --gate-dir AND print_dfm --gate naming that set's folder, 20-design/arrival_checklist.yaml -> arrival_checklist.py --check. -> problem list (blind review 0.8.0 F11)."""
    lines = " ".join(str(x) for x in (P.get("gates.adopt") or []))
    bad = []
    sch = P.path("schematic")
    if sch and os.path.exists(sch) and "erc_gate.py" not in lines:
        bad.append(f"schematic {P.get('paths.schematic')} exists but gates.adopt has no `scripts/erc_gate.py` line")
    board = P.path("board")
    if board and os.path.exists(board) and not re.search(r"\bdrc", lines, re.I):   # ponytail: a token starting with drc (drc_gate.py, DRC); a named gates.drc key if a project games it
        bad.append(f"board {P.get('paths.board')} exists but gates.adopt has no DRC gate line")
    pat = P.get("paths.mech_record")
    # per set (40-case/<set>/parts/*.stl -> 40-case/<set>): a census --gate-dir AND a print_dfm --gate argument must sit under that set's folder
    # (its checks dir); a token somewhere in gates.adopt gates only the set it names (review 0.11.0 B-4)
    sets = sorted({os.path.relpath(os.path.dirname(os.path.dirname(f)), P.root) for f in glob.glob(os.path.join(P.root, pat))}) if pat else []
    census = re.findall(r"--gate-dir\s+(\S+)", lines); dfm = re.findall(r"print_dfm\.py\s+--gate\s+(\S+)", lines)
    for st in sets:
        under = lambda args: any(a.startswith(st + "/") for a in args)
        missing = [w for args, w in ((census, f"thin_wall_census.py --gate-dir {st}/checks/census"), (dfm, f"print_dfm.py --gate {st}/checks/dfm")) if not under(args)]
        if missing:
            bad.append(f"STL set {st} has files but gates.adopt has no " + " / ".join(f"`{w}`" for w in missing) + " line")
    ac = P.get("arrival_checklist.yaml", "20-design/arrival_checklist.yaml")
    if os.path.exists(os.path.join(P.root, ac)) and "arrival_checklist.py --check" not in lines:
        bad.append(f"{ac} exists but gates.adopt has no `scripts/arrival_checklist.py --check` line")
    return bad


SLOT = re.compile(r"\{\{[^{}]*\}\}")
SLOT_DEFAULT = ("CLAUDE.md", "project.yaml", "10-spec", "20-design", "60-orders", "90-log")


def slots(paths, root="."):
    """{relpath: sorted distinct slots} for every text file under `paths` (dirs walked; .md / .yaml / .yml / .json / .csv), skeleton blocks skipped."""
    out = {}
    files = []
    for p in paths:
        q = os.path.join(root, p)
        if os.path.isdir(q):
            files += sorted(os.path.join(dp, f) for dp, _, fs in os.walk(q) for f in fs if f.endswith((".md", ".yaml", ".yml", ".json", ".csv")))
        elif os.path.isfile(q):
            files.append(q)
    for f in files:
        found, skip = set(), False
        for line in open(f, encoding="utf-8", errors="replace"):
            if "<!-- skeleton: begin" in line:
                skip = True
            if not skip:
                found.update(SLOT.findall(line))
            if "<!-- skeleton: end" in line:
                skip = False
        if found:
            out[os.path.relpath(f, root)] = sorted(found)
    return out


KEY_RE = re.compile(r"`((?:project|kickoff|board|print_targets|fab_dfm)\.[A-Za-z0-9_.*<>{}/ -]+?)`(?:\s*\(((?:ee|mech|both)(?:\s*/\s*(?:ee|mech|both))*)\))?")   # `key` (ee / both) = the key belongs to those scopes


def kickoff_check(P):
    """Every answered row of the kickoff answers file names project.yaml keys in `Written to`; each must exist (print_targets.<t>.x / .*.x = some
    target has x). A row whose answer or D-row cell is still a slot, whose D-row cell has no owner-prefix id, or whose D row is not in the decision log,
    is a problem. The A0 answer must equal project.scope. -> problem list."""
    ans = P.get("kickoff.answers") if isinstance(P.get("kickoff"), dict) else None
    path = os.path.join(P.root, ans) if ans else P.path("kickoff_answers")
    if not os.path.exists(path):
        return [f"kickoff answers file missing: {os.path.relpath(path, P.root)}"]
    own = re.compile(r"\b%s-\d+[a-z]?\b" % re.escape(P.get("ids.owner_prefix")))   # only an owner decision row counts (D-nn, not CC-nnn)
    dec_ids = set()
    dp = P.path("decisions")
    for line in open(dp, encoding="utf-8") if dp and os.path.exists(dp) else []:
        if line.startswith("|"):
            m = own.search(split_row(line)[0] if split_row(line) else "")
            if m:
                dec_ids.add(m.group(0))
    bad = []; n = 0
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        c = split_row(line)
        if len(c) < 6 or not re.fullmatch(r"[A-I]\d+[a-z]?", c[0]):
            continue
        q, answer, drow, written = c[0], c[2], c[4], c[5]
        if answer.lower().startswith("n/a") or answer.upper() == "OPEN":
            continue
        n += 1
        if SLOT.search(answer):
            bad.append(f"{q}: answer still a slot ({answer})"); continue
        if q == "A0" and answer.strip("`* ").split(" ")[0].lower() != P.scope():
            bad.append(f"{q}: answer `{answer}` differs from project.scope `{P.scope()}`")
        ids = own.findall(drow)
        if SLOT.search(drow) or not ids:
            bad.append(f"{q}: no D row id (owner prefix {P.get('ids.owner_prefix')}-) in `{drow}`")
        elif dec_ids and not any(i in dec_ids for i in ids):
            bad.append(f"{q}: D row {ids[0]} is not in {P.get('paths.decisions')}")
        for key, scopes in KEY_RE.findall(written):
            if scopes and P.scope() not in [x.strip() for x in scopes.split("/")]:
                continue
            key = key.split(":")[0].strip().replace("print_targets.<t>", "print_targets.*")
            if key.startswith("print_targets.*") or key.startswith("print_targets.{{"):
                sub = key.split(".", 2)[2] if key.count(".") >= 2 else None
                ts = P.get("print_targets") or {}
                ok = bool(ts) and (sub is None or any(isinstance(t, dict) and _has(t, sub.split("/")[0].strip()) for t in ts.values()))
            else:
                ok = P.get(key.split(" ")[0].split("/")[0].strip()) is not None
            if not ok:
                bad.append(f"{q}: `{key}` is not set in project.yaml")
    if n == 0:
        bad.append("no answered rows in the kickoff answers file")
    return bad


def _has(d, dotted):
    for k in dotted.split("."):
        if not isinstance(d, dict) or k not in d:
            return False
        d = d[k]
    return d is not None


def host_facts():
    """cores, RAM GB of this host (sysctl on macOS, /proc on Linux) and the derived heavy-job pool size max(1, cores // 4) + memory floor
    max(2 GB, 15 % of RAM) — what scripts/jobs.sh uses unless project.yaml host: overrides it."""
    import subprocess
    try:
        cores = int(subprocess.run(["sysctl", "-n", "hw.ncpu"], capture_output=True, text=True).stdout or 0) or os.cpu_count() or 1
        ram = int(subprocess.run(["sysctl", "-n", "hw.memsize"], capture_output=True, text=True).stdout or 0) / 2**30
    except FileNotFoundError:
        cores = os.cpu_count() or 1; ram = 0
    if not ram and os.path.exists("/proc/meminfo"):
        ram = next((int(l.split()[1]) / 2**20 for l in open("/proc/meminfo") if l.startswith("MemTotal")), 0)
    return dict(cores=cores, ram_gb=round(ram), jobs_max=max(1, cores // 4), min_free_gb=round(max(2.0, 0.15 * ram), 1))


def host_row(h=None):
    h = h or host_facts(); import datetime
    return (f"| Host | {h['cores']} cores, {h['ram_gb']} GB RAM (`sysctl hw.ncpu / hw.memsize`, `nproc` + `/proc/meminfo` on Linux) → heavy-job pool {h['jobs_max']} "
            f"(cores // 4), memory floor {h['min_free_gb']} GB (max of 2 GB, 15 % of RAM) — `scripts/jobs.sh`; project.yaml `host:` overrides | this machine | {datetime.date.today().isoformat()} |")


def decision_status(path, id_re=None):
    """{id: status cell with bold stripped and the history after `(was:` dropped} of a decision log; ids by `id_re` (default: any PREFIX-nn)."""
    out = {}
    rx = id_re or re.compile(r"\b([A-Z]+-\d+[a-z]?)\b")
    for line in open(path, encoding="utf-8") if path and os.path.exists(path) else []:
        if line.startswith("|"):
            c = split_row(line)
            if len(c) >= 3:
                st = re.split(r"\(was:", re.sub(r"\*", "", c[2]), maxsplit=1)[0].strip()
                for i in rx.findall(c[0]):
                    out.setdefault(i, st)
    return out


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
    assert P.path("decisions") == f"{d}/d/D.md" and P.path("gates") == f"{d}/90-log/GATES.md" and P.path("zz") is None
    # the layout of record: every default sits under one of the ten numbered folders; an explicit old-layout key wins unchanged; rev defaults to rev0
    top = {"00-now", "10-spec", "20-design", "30-board", "40-case", "50-kits", "60-orders", "70-release", "80-reviews", "90-log"}
    for k, v in DEFAULTS["paths"].items():
        assert k == "kits_mirror" or v.split("/")[0] in top, (k, v)
    assert P.get("paths.mech_record") == "40-case/*/parts/*.stl" and P.path("kits_dir") == f"{d}/50-kits" and P.rev() == "rev0"
    assert P.path("spec_errata") == f"{d}/10-spec/SPEC_ERRATA.md" and P.path("dfm_thresholds") == f"{d}/20-design/dfm_thresholds.json"
    assert P.path("dfm_items") == f"{d}/30-board/layout/dfm_items.json" and P.path("dfm_report") == f"{d}/30-board/layout/dfm.json"
    assert P.get("paths.kits_mirror") == "~/Downloads/<project>_kits", "the kit writer expands <project>"
    P.cfg.setdefault("paths", {})["gates"] = "legacy/GATES.md"; P.cfg.setdefault("project", {})["revision"] = "rev1"
    assert P.path("gates") == f"{d}/legacy/GATES.md" and P.rev() == "rev1", "an explicit path / revision wins over the layout default"
    for v in (None, ""):
        P.cfg["project"]["revision"] = v; assert P.rev() == "rev0", f"revision {v!r} -> rev0"
    P.cfg["project"]["revision"] = "a b"
    try:
        P.rev(); assert False, "a space in revision must exit"
    except SystemExit as e:
        assert "folder-safe" in str(e)
    del P.cfg["paths"]["gates"]; P.cfg["project"].pop("revision")
    assert P.tool("python") == f"{d}/.venv/bin/python" and P.tool("kicad_cli") == "kicad-cli"
    assert P.id_re().findall("D-01 AG-002 B-03 CC-004") == ["D-01", "AG-002", "B-03"] and P.decision_re().findall("D-2a AG-002 B-03") == ["D-2a", "AG-002"]
    assert split_row("| a | b \\| c | d |") == ["a", "b \\| c", "d"], "an escaped pipe is content"
    open(f"{d}/DS.md", "w").write("| ID | Date | Status | T | P | R |\n|---|---|---|---|---|---|\n| **D-03** | d | **APPROVED** (was: OPEN) | t | p | r |\n| CC-010 | d | APPLIED (!) | t | p | r |\n")
    assert decision_status(f"{d}/DS.md") == {"D-03": "APPROVED", "CC-010": "APPLIED (!)"} and decision_status(f"{d}/nope.md") == {}, decision_status(f"{d}/DS.md")
    # scope + record id: board md5 in ee / both, the STL set in mech, MISSING when absent
    assert P.scope() == "both" and P.record_md5()[1] is None, "no board: MISSING"
    os.makedirs(f"{d}/40-case/vendor_mjf/parts"); open(f"{d}/40-case/vendor_mjf/parts/a.stl", "wb").write(b"A")
    P.cfg["project"] = {"scope": "mech"}
    lbl, m = P.record_md5(); assert m and "1 files" in lbl and P.scope() == "mech"
    open(f"{d}/40-case/vendor_mjf/parts/b.stl", "wb").write(b"B"); assert P.record_md5()[1] != m, "a new STL moves the mech record md5"
    open(f"{d}/t.md", "w").write("all {{SCOPE}}\n| G1 | {{ee,both}}\n| M1 | {{mech}}\n{{ee,both}}{{mech}} either\n")
    assert scaffold("mech", [f"{d}/t.md"]) == 1 and open(f"{d}/t.md").read() == "all mech\n| M1 |\n either\n", open(f"{d}/t.md").read()
    # record signing, OPEN rows, required gate lines
    r = dict(a=1, b=[1.5, "x"]); r["sig"] = record_sig(r, "1.0"); assert verify_sig(r, "1.0") and not verify_sig(dict(r, a=2), "1.0") and not verify_sig(r, "1.1")
    open(f"{d}/D.md", "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-07** | d | **OPEN** | widen root | p | r |\n| CC-010 | d | APPLIED | x | p | r |\n| CC-011 | d | OPEN (owner) | y | p | r |\n")
    assert open_decisions(f"{d}/D.md") == {"D-07": "widen root p r", "CC-011": "y p r"}, open_decisions(f"{d}/D.md")
    P.cfg["paths"] = {"mech_record": "40-case/*/parts/*.stl", "schematic": "k/k.kicad_sch"}; P.cfg["gates"] = {"adopt": ["$PY scripts/known_issues.py --check"]}
    bad = required_gate_lines(P); assert len(bad) == 1 and "40-case/vendor_mjf" in bad[0] and "--gate-dir" in bad[0] and "print_dfm.py --gate" in bad[0], bad
    P.cfg["gates"]["adopt"] += ["$PY scripts/thin_wall_census.py --gate-dir out/x/census", "$PY scripts/print_dfm.py --gate out/x/dfm"]
    bad = required_gate_lines(P); assert len(bad) == 1 and "40-case/vendor_mjf" in bad[0], ("a gate line must name the set's checks dir", bad)
    P.cfg["gates"]["adopt"] += ["$PY scripts/thin_wall_census.py --gate-dir 40-case/vendor_mjf/checks/census", "$PY scripts/print_dfm.py --gate 40-case/vendor_mjf/checks/dfm"]
    assert required_gate_lines(P) == []
    os.makedirs(f"{d}/40-case/other/parts"); open(f"{d}/40-case/other/parts/x.stl", "wb").write(b"X")   # a second set with STLs and no gate line
    bad = required_gate_lines(P); assert len(bad) == 1 and "40-case/other" in bad[0] and "vendor_mjf" not in bad[0], bad
    P.cfg["gates"]["adopt"] += ["$PY scripts/thin_wall_census.py --gate-dir 40-case/other/checks/census --x", "$PY scripts/print_dfm.py --gate 40-case/other/checks/dfm"]
    assert required_gate_lines(P) == []
    os.makedirs(f"{d}/k"); open(f"{d}/k/k.kicad_sch", "w").write("x"); assert "erc_gate.py" in required_gate_lines(P)[0]
    os.makedirs(f"{d}/20-design"); open(f"{d}/20-design/arrival_checklist.yaml", "w").write("sections: []\n"); assert any("arrival_checklist.py" in b for b in required_gate_lines(P))
    P.cfg["gates"]["adopt"] += ["$PY scripts/arrival_checklist.py --check"]; assert not any("arrival_checklist" in b for b in required_gate_lines(P))
    # slots (skeleton skipped) and the kickoff check
    open(f"{d}/S.md", "w").write("a {{X}} b {{Y}}\n<!-- skeleton: begin -->\n{{SKEL}}\n<!-- skeleton: end -->\n{{X}}\n")
    assert slots(["S.md", "nope.md"], d) == {"S.md": ["{{X}}", "{{Y}}"]}, slots(["S.md"], d)
    os.makedirs(f"{d}/90-log"); os.makedirs(f"{d}/10-spec"); open(f"{d}/10-spec/KICKOFF_ANSWERS.md", "w").write(
        "| Q | Question | Answer | Rec. | D row | Written to |\n|---|---|---|---|---|---|\n| A1 | product class | sample | yes | D-02 | `kickoff.product_class`; SPEC §1 |\n"
        "| B1 | layers | 4 | yes | D-03 | `board.layers`, `board.thickness_mm` |\n| C2 | retention | n/a (scope) | - | - | `kickoff.enclosure.retention` |\n"
        "| C8a | rows | jlc | yes | D-{{nn}} | `print_targets.<t>.dfm_process` |\n| D1 | bar | {{zero}} | yes | D-04 | `fab_dfm.bar` |\n"
        "| D2 | waived | nothing | yes | D-02 | `print_targets.*.accepted` (mech / both), `fab_dfm.bar` (ee / both) |\n")
    P.cfg.update(kickoff={"answers": "10-spec/KICKOFF_ANSWERS.md", "product_class": "sample"}, board={"layers": 4}, print_targets={"t": {"dfm_process": "x"}}, fab_dfm={"bar": {"open": 0}})
    P.cfg["paths"]["decisions"] = "D.md"; open(f"{d}/D.md", "a").write("| **D-02** | d | **APPROVED** | a | p | r |\n| **D-03** | d | **APPROVED** | b | p | r |\n")
    P.cfg["project"]["scope"] = "ee"
    bad = kickoff_check(P); assert len(bad) == 3 and "board.thickness_mm" in bad[0] and bad[1].startswith("C8a: no D row id") and bad[2].startswith("D1: answer still a slot"), bad
    P.cfg["board"]["thickness_mm"] = 1.6; open(f"{d}/10-spec/KICKOFF_ANSWERS.md", "a").write("| E1 | rounds | one | yes | D-99 | `kickoff.verification.rounds` |\n")
    bad = kickoff_check(P); assert any("D-99 is not in" in b for b in bad) and any("kickoff.verification.rounds" in b for b in bad), bad
    open(f"{d}/10-spec/KICKOFF_ANSWERS.md", "a").write("| A0 | scope | mech | yes | D-02 | `project.scope` |\n| E2 | log | agent | yes | CC-001 | `board.layers` |\n")
    bad = kickoff_check(P); assert any(b.startswith("A0: answer `mech` differs from project.scope `ee`") for b in bad), bad
    assert any(b.startswith("E2: no D row id") for b in bad), bad                     # an agent id is not the owner's row
    P.cfg["project"]["scope"] = "mech"; assert not any(b.startswith("A0:") for b in kickoff_check(P)); P.cfg["project"]["scope"] = "ee"
    h = host_facts(); assert h["cores"] >= 1 and h["jobs_max"] >= 1 and h["min_free_gb"] >= 2 and "| Host |" in host_row(h), h
    assert host_row(dict(cores=14, ram_gb=24, jobs_max=3, min_free_gb=3.6)).startswith("| Host | 14 cores, 24 GB RAM")
    print("selftest OK (defaults, paths, ids, scope, record md5, scaffold, record signing, OPEN rows, required gate lines, slots, kickoff check (owner ids only, A0 = project.scope), host row)")
    return 0


def main(argv):
    if len(argv) > 1 and argv[1] == "--selftest":
        sys.exit(selftest())
    if len(argv) > 1 and argv[1] in ("--help", "-h"):
        print(__doc__); return
    if len(argv) > 1 and argv[1] == "env":
        print(host_row()); return
    if len(argv) < 2 or argv[1] not in ("get", "path", "root", "scope", "rev", "record", "scaffold", "gates-required", "slots", "kickoff"):
        sys.exit(__doc__)
    if argv[1] == "scaffold":
        if len(argv) < 5 or argv[2] != "--scope":
            sys.exit(__doc__)
        print(f"scaffold {argv[3]}: {scaffold(argv[3], argv[4:])} line(s) dropped in {len(argv) - 4} file(s)"); return
    if argv[1] == "slots":
        found = slots(argv[2:] or list(SLOT_DEFAULT), os.getcwd()); total = sum(len(v) for v in found.values())
        for f, v in found.items():
            print(f"{f}: {len(v)} slot(s): {' '.join(v)[:200]}")
        print(f"slots: {total} unfilled in {len(found)} file(s)"); sys.exit(1 if total else 0)
    P = Project.find()
    if argv[1] == "kickoff":
        if argv[2:] != ["--check"]:
            sys.exit(__doc__)
        bad = kickoff_check(P)
        for b in bad:
            print("KICKOFF:", b)
        print(f"kickoff check: {len(bad)} problem(s)"); sys.exit(1 if bad else 0)
    if argv[1] == "gates-required":
        bad = required_gate_lines(P)
        for b in bad:
            print("GATES REQUIRED:", b)
        sys.exit(1 if bad else 0)
    if argv[1] == "root":
        print(P.root)
    elif argv[1] == "scope":
        print(P.scope())
    elif argv[1] == "rev":
        print(P.rev())   # the revision that names the fab package, the cut, collateral and marketing folders
    elif argv[1] == "record":
        lbl, m = P.record_md5(); print(f"{lbl} md5 {m or 'MISSING'}")
    elif len(argv) < 3:
        sys.exit(__doc__)
    elif argv[1] == "path":
        print(P.path(argv[2]) or "")
    else:
        v = P.get(argv[2], "")
        print("\n".join(str(x) for x in v) if isinstance(v, list) else v)


if __name__ == "__main__":
    main(sys.argv)
