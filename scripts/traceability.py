#!/usr/bin/env python3
"""scripts/traceability.py — requirement → evidence matrix (the matrix is GENERATED; the yaml is the source).

  python scripts/traceability.py                 # run every check, write paths.traceability_out, exit 1 on FAILED or unmapped
  python scripts/traceability.py --only D-03     # print the entries whose id/source contain the token, every check detail; nothing written
  python scripts/traceability.py --no-commands   # skip `command` checks (they read SKIPPED → PENDING(--no-commands), never FAILED)
  python scripts/traceability.py --check         # exit 1 when the matrix on disk is stale or any row FAILED / unmapped (adopt gate)
  python scripts/traceability.py --selftest

Inputs  paths.traceability_yaml — `stages:` (ordered mapping: gates that decide PENDING) and `entries:` (one per traceable item)
        paths.decisions        — ID census: every owner / agent row must appear in some entry's `source`
        paths.netlist          — kicadxml netlist for `netlist_net` checks (optional)
Output  paths.traceability_out — the only file written inside the repository

Check types (each: ok/detail)
  exists(path)   image(path)  glob allowed        grep(path, regex[, absent, min_count])  re.S|re.M
  md5_in(path, file, regex)  md5(path) starts with the hex the regex captures in `file` (glob allowed) — the content key for
                             "made from this board"; never use mtimes (they flip on every clone / git archive)
  yaml_key(path, key[, expected|contains])  dotted path, list index `.0`, filter `items[ref=J1].x`
  command(cmd[, expect_rc | [rc, rc], expect_stdout_regex, timeout, label, sandbox: {copy: [...], link: [...]}])
      placeholders {ROOT} {PY} {KICAD_CLI} {KPY} {SCRATCH} {REPO}; a writing command declares `sandbox:` and runs on a scratch
      copy — a check must never rewrite tracked files. Evidence text is ROOT-relative so two checkouts give one matrix.
  netlist_net(node "REF.PIN", net regex; `unconnected` = no net)

Result per entry: VERIFIED / FAILED / PENDING(stage) / PENDING(text: entry `pending:`) / NOT-INCLUDED (entry `status: not_included`
+ `reason`). A NOT-INCLUDED row whose reason starts with OPEN while its decision row is no longer OPEN is FAILED (stale reason).
"""
import argparse, glob, hashlib, os, re, shutil, subprocess, sys, tempfile, xml.etree.ElementTree as ET
from datetime import date

import yaml

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import decision_status as _decision_status, Project, split_row  # noqa: E402


class Ctx:
    def __init__(self, P, scratch, run_commands):
        self.P, self.root, self.scratch, self.run_commands = P, P.root, scratch, run_commands
        self.cmd_cache, self._nets, self._scratch_ready = {}, None, False

    def sub(self, s):
        return (s.replace("{SCRATCH}", self.scratch).replace("{ROOT}", self.root).replace("{PY}", self.P.tool("python") or sys.executable)
                 .replace("{KICAD_CLI}", self.P.tool("kicad_cli") or "kicad-cli").replace("{KPY}", self.P.tool("kicad_python") or "python3"))

    def sandbox(self, spec):
        """{REPO}: a scratch repo of copies (`copy:`) and symlinks (`link:` — big read-only inputs, .venv, .git for `git show HEAD:`)."""
        repo = os.path.join(self.scratch, "repo")
        for kind in ("copy", "link"):
            for rel in spec.get(kind, []):
                src, dst = os.path.join(self.root, rel), os.path.join(repo, rel)
                if os.path.lexists(dst) or not os.path.lexists(src):
                    continue
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                if kind == "link":
                    os.symlink(src, dst)
                elif os.path.isdir(src):
                    shutil.copytree(src, dst, symlinks=True)
                else:
                    shutil.copy2(src, dst)
        return repo

    def prepare_scratch(self):
        """{SCRATCH}/<board dir>: a copy of the board's directory for kicad-cli runs (never the tracked board)."""
        if self._scratch_ready:
            return
        board = self.P.get("paths.board")
        if board:
            rel = os.path.dirname(board)
            dst = os.path.join(self.scratch, rel)
            shutil.rmtree(dst, ignore_errors=True)
            shutil.copytree(os.path.join(self.root, rel), dst)
            for link in self.P.get("traceability.scratch_links", []):
                if os.path.exists(os.path.join(self.root, link)) and not os.path.lexists(os.path.join(self.scratch, link)):
                    os.symlink(os.path.join(self.root, link), os.path.join(self.scratch, link))
        self._scratch_ready = True

    def nets(self):
        if self._nets is None:
            self._nets, nl = {}, self.P.path("netlist")
            if nl and os.path.exists(nl):
                for n in ET.parse(nl).iter("net"):
                    for nd in n.findall("node"):
                        self._nets[(nd.get("ref"), nd.get("pin"))] = n.get("name")
        return self._nets


def yaml_get(doc, key):
    cur = doc
    for tok in re.findall(r"[^.\[\]]+(?:\[[^\]]*\])?", key):
        m = re.match(r"([^\[]+)(?:\[(\w+)=([^\]]+)\])?$", tok)
        name, fk, fv = m.group(1), m.group(2), m.group(3)
        cur = cur[int(name)] if isinstance(cur, list) and name.isdigit() else cur[name]
        if fk:
            cur = next(x for x in cur if str(x.get(fk)) == fv)
    return cur


def same(a, b):
    try:
        return float(a) == float(b)
    except (TypeError, ValueError):
        return str(a) == str(b)


def files_of(ctx, p):
    p = ctx.sub(p)
    full = p if os.path.isabs(p) else os.path.join(ctx.root, p)
    return [f for f in (glob.glob(full) if any(ch in p for ch in "*?[") else [full]) if os.path.exists(f)], p


def run_check(c, ctx):
    t = c["type"]
    try:
        if t in ("exists", "image"):
            hits, p = files_of(ctx, c["path"])
            return bool(hits), f"{t} {'✓' if hits else '✗'} {p}"
        if t == "md5_in":
            files, p = files_of(ctx, c["file"])
            src = os.path.join(ctx.root, c["path"])
            if not files or not os.path.exists(src):
                return False, f"md5_in ✗ {os.path.basename(c['path'])} in {p} (missing file)"
            h = hashlib.md5(open(src, "rb").read()).hexdigest()
            caught = [m for f in files for m in re.findall(c["regex"], open(f, errors="replace").read(), re.M)]
            ok = any(h.startswith(m.lower()) for m in caught)
            return ok, f"md5_in {'✓' if ok else '✗'} {os.path.basename(c['path'])} {h[:8]} recorded in {os.path.basename(p)}" + ("" if ok else f" (found {[m[:8] for m in caught][:3] or 'none'})")
        if t == "grep":
            files, p = files_of(ctx, c["path"])
            if not files:
                return False, f"grep ✗ {p} (missing file)"
            text = "\n".join(open(f, errors="replace").read() for f in files)
            n = len(re.findall(c["regex"], text, re.S | re.M))
            ok = (n == 0) if c.get("absent") else n >= c.get("min_count", 1)
            label = "absent" if c.get("absent") else f"×{n}" if c.get("min_count") else ""
            return ok, f"grep {'✓' if ok else '✗'} {os.path.basename(p)} /{c['regex'][:60]}/ {label}"
        if t == "yaml_key":
            doc = yaml.safe_load(open(os.path.join(ctx.root, c["path"])))
            try:
                v = yaml_get(doc, c["key"])
            except (KeyError, IndexError, StopIteration, TypeError):
                return False, f"yaml ✗ {os.path.basename(c['path'])}:{c['key']} (absent)"
            if "expected" in c:
                ok = same(v, c["expected"])
                return ok, f"yaml {'✓' if ok else '✗'} {c['key']} = {str(v)[:40]}" + ("" if ok else f" (want {c['expected']})")
            if "contains" in c:
                ok = c["contains"] in (v if isinstance(v, (list, dict)) else str(v))
                return ok, f"yaml {'✓' if ok else '✗'} {c['key']} ∋ {c['contains']}"
            return True, f"yaml ✓ {c['key']} present"
        if t == "netlist_net":
            ref, pin = c["node"].split(".", 1)
            net = ctx.nets().get((ref, pin))
            if net is None:
                return False, f"net ✗ {c['node']} (no such node)"
            want = c["net"]
            ok = net.startswith("unconnected-") if want == "unconnected" else bool(re.fullmatch(want, net) or re.fullmatch(want, net.rsplit("/", 1)[-1]))
            return ok, f"net {'✓' if ok else '✗'} {c['node']} → {net.rsplit('/', 1)[-1]}" + ("" if ok else f" (want {want})")
        if t == "command":
            if not ctx.run_commands:
                return False, "command SKIPPED (--no-commands)"
            if "{SCRATCH}" in c["cmd"]:
                ctx.prepare_scratch()
            cmd = ctx.sub(c["cmd"])
            if "sandbox" in c:
                cmd = cmd.replace("{REPO}", ctx.sandbox(c["sandbox"]))
            if cmd not in ctx.cmd_cache:
                r = subprocess.run(cmd, shell=True, cwd=ctx.root, capture_output=True, text=True, timeout=c.get("timeout", 600))
                ctx.cmd_cache[cmd] = (r.returncode, (r.stdout or "") + (r.stderr or ""))
            rc, out = ctx.cmd_cache[cmd]
            want = c.get("expect_rc", 0)
            ok = rc in want if isinstance(want, list) else rc == want
            hit = ""
            if "expect_stdout_regex" in c:
                m = re.search(c["expect_stdout_regex"], out, re.M)
                ok = ok and bool(m)
                tail = (out.strip().splitlines() or [""])[-1][:70]
                hit = f" «{m.group(0)[:70]}»" if m else f" (pattern not found; last line «{tail}»)"
            short = (c.get("label") or c["cmd"].split("&&")[0].strip())[:70]   # the UNSUBSTITUTED text: ROOT-relative, identical in every checkout
            return ok, f"cmd {'✓' if ok else '✗'} `{short}` rc={rc}{hit}"
        return False, f"unknown check type {t}"
    except Exception as e:  # a broken check is a failed check, never a crash
        return False, f"{t} ✗ error: {str(e)[:80]}"


def decision_status(P):
    """id -> status cell up to the first history marker, bold stripped (project.decision_status with the project's id regex)."""
    return _decision_status(P.path("decisions"), P.decision_re())


def md(s):
    return str(s).replace("|", "\\|").replace("\n", " ")


def build(P, ctx, only=None):
    ty = P.path("traceability_yaml")
    if not os.path.exists(ty):
        print(f"MISSING: {ty} — seed it from the skill's templates/20-design/traceability.yaml (one entry per decision row)"); sys.exit(2)
    spec = yaml.safe_load(open(ty))
    entries = spec.get("entries", [])
    if only:
        entries = [e for e in entries if only in e["id"] or only in str(e.get("source", ""))]
    stages, reached, gate_detail = spec.get("stages", {}) or {}, {}, {}
    for s, g in stages.items():   # yaml order = stage order
        res = [run_check(c, ctx) for c in (g or {}).get("reached", [])]
        reached[s] = all(r[0] for r in res) and all(reached.get(q, False) for q in (g or {}).get("requires", []))
        gate_detail[s] = res
    status = decision_status(P)
    dre = P.decision_re()
    rows, counts, only_lines = [], {}, []
    for e in entries:
        checks = [run_check(c, ctx) for c in e.get("checks", [])]
        ok_n = sum(1 for r in checks if r[0])
        cited = dre.findall(f"{e['id']} {e.get('source', '')}")
        if e.get("status") == "not_included":
            reason = str(e.get("reason", ""))
            stale = reason.upper().startswith("OPEN") and cited and not any(status.get(i, "").upper().startswith("OPEN") for i in cited)
            res = "FAILED" if stale else "NOT-INCLUDED"
            detail = ("stale reason: the cited row is no longer OPEN — " if stale else "") + reason
        elif e.get("stage") and not reached.get(e["stage"], False):
            res, detail = f"PENDING({e['stage']})", f"now {ok_n}/{len(checks)}"
        elif ok_n == len(checks):
            res = "VERIFIED" + (" (provisional)" if any(status.get(i, "").upper().startswith("OPEN") for i in cited) else "")
            detail = "; ".join(r[1] for r in checks)
        elif e.get("pending"):
            res, detail = f"PENDING({e['pending']})", "; ".join(r[1] for r in checks if not r[0])
        elif all(r[1].startswith("command SKIPPED") for r in checks if not r[0]):
            res, detail = "PENDING(--no-commands)", "; ".join(r[1] for r in checks if not r[0])
        else:
            res, detail = "FAILED", "; ".join(r[1] for r in checks if not r[0])
        key = res.split("(")[0].split(" ")[0]
        counts[key] = counts.get(key, 0) + 1
        rows.append((e, res, detail, checks))
        if only:
            only_lines.append(f"{e['id']}: {res}\n  " + "\n  ".join(r[1] for r in checks) + (f"\n  reason: {e.get('reason')}" if e.get("reason") else ""))
    all_sources = " ".join(f"{e['id']} {e.get('source', '')}" for e in spec.get("entries", []))
    mapped = set(dre.findall(all_sources))
    unmapped = [i for i in decision_status(P) if i not in mapped]
    L = [f"# {os.path.basename(P.get('paths.traceability_out'))} — requirement → evidence matrix ({P.get('project.name', 'project')})", "",
         f"GENERATED by `scripts/traceability.py` from `{P.get('paths.traceability_yaml')}` on {date.today()}. Do not edit; change the yaml and regenerate. "
         "Result words: VERIFIED (every check passes), FAILED, PENDING(stage) (gate not reached; checks still shown as now k/n), PENDING(text) (known gap with a logged fix), NOT-INCLUDED (owner row still OPEN or out of scope).", "",
         "## Stages", "", "| Stage | Reached | Gate checks |", "|---|---|---|"]
    L += [f"| {s} | {'yes' if reached[s] else 'no'} | {md('; '.join(r[1] for r in gate_detail[s])) or '—'} |" for s in stages]
    L += ["", "## Census", "", "| " + " | ".join(sorted(counts)) + " |", "|" + "---|" * len(counts), "| " + " | ".join(str(counts[k]) for k in sorted(counts)) + " |", "",
          "Unmapped decision rows (no entry cites them): " + (", ".join(unmapped) or "none"), "",
          "## Entries", "", "| ID | Source | Requirement | Lands in | Stage | Result | Evidence |", "|---|---|---|---|---|---|---|"]
    L += [f"| {e['id']} | {md(e.get('source', ''))} | {md(e.get('requirement', ''))} | {md(e.get('lands_in', ''))} | {e.get('stage', '')} | **{res}** | {md(detail)} |" for e, res, detail, _ in rows]
    failed = counts.get("FAILED", 0)
    return "\n".join(L) + "\n", failed, unmapped, only_lines


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--only"); ap.add_argument("--no-commands", action="store_true"); ap.add_argument("--check", action="store_true")
    ap.add_argument("--scratch"); ap.add_argument("--project"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    P = Project.find(arg=a.project)
    scratch = a.scratch or tempfile.mkdtemp(prefix="hwfs_trace_")
    text, failed, unmapped, only_lines = build(P, Ctx(P, os.path.abspath(scratch), not a.no_commands), a.only)
    if a.only:
        print("\n".join(only_lines) or f"no entry matches {a.only}")
        return 0
    out = P.path("traceability_out")
    strip = lambda s: re.sub(r"on \d{4}-\d{2}-\d{2}\.", "", s)
    if a.check:
        old = open(out, encoding="utf-8").read() if os.path.exists(out) else ""
        if strip(old) != strip(text):
            print(f"STALE: {out} differs from the regenerated matrix — run scripts/traceability.py and commit"); return 1
        if failed or unmapped:
            print(f"FAILED rows: {failed}; unmapped: {unmapped}"); return 1
        print(f"OK: {out} up to date, 0 FAILED, 0 unmapped"); return 0
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(text)
    print(f"{out} written; FAILED {failed}; unmapped {unmapped or 'none'}")
    return 1 if failed or unmapped else 0


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_tr_")
    os.makedirs(f"{d}/90-log"); os.makedirs(f"{d}/20-design"); os.makedirs(f"{d}/30-board/kicad/b"); os.makedirs(f"{d}/out")
    open(f"{d}/project.yaml", "w").write("project: {name: t}\npaths: {board: 30-board/kicad/b/b.kicad_pcb}\ntools: {python: %s}\n" % sys.executable)
    open(f"{d}/30-board/kicad/b/b.kicad_pcb", "w").write("(kicad_pcb)\n")
    h = hashlib.md5(open(f"{d}/30-board/kicad/b/b.kicad_pcb", "rb").read()).hexdigest()
    open(f"{d}/out/EVIDENCE.md", "w").write(f"board md5 `{h}`\n")
    open(f"{d}/20-design/board.yaml", "w").write("board: {width: 42.0}\nitems: [{ref: J1, x: 3}]\n")
    open(f"{d}/90-log/DECISIONS.md", "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-01 (owner)** | d | **APPROVED** | t | p | r |\n"
                                             "| CC-001 | d | OPEN | t | p | r |\n| CC-002 | d | DECIDED (was: OPEN) | t | p | r |\n| CC-003 | d | OPEN | unmapped | p | r |\n")
    open(f"{d}/20-design/traceability.yaml", "w").write(f"""
stages:
  schematic: {{reached: [{{type: exists, path: 20-design/board.yaml}}]}}
  placement: {{requires: [schematic], reached: [{{type: md5_in, path: 30-board/kicad/b/b.kicad_pcb, file: out/EVIDENCE.md, regex: 'board md5 `([0-9a-f]{{32}})`'}}]}}
  routing: {{requires: [placement], reached: [{{type: exists, path: out/drc.json}}]}}
entries:
  - {{id: D-01.1, source: D-01, requirement: width 42, lands_in: board.yaml, stage: schematic, checks: [{{type: yaml_key, path: 20-design/board.yaml, key: board.width, expected: 42}}, {{type: yaml_key, path: 20-design/board.yaml, key: 'items[ref=J1].x', expected: 3}}]}}
  - {{id: D-01.2, source: D-01, requirement: routed, lands_in: board, stage: routing, checks: [{{type: grep, path: 30-board/kicad/b/b.kicad_pcb, regex: segment}}]}}
  - {{id: CC-001.1, source: CC-001, requirement: q, lands_in: —, stage: schematic, status: not_included, reason: OPEN owner question}}
  - {{id: CC-002.1, source: CC-002, requirement: q, lands_in: —, stage: schematic, status: not_included, reason: OPEN owner question}}
  - {{id: CC-002.2, source: CC-002, requirement: cmd, lands_in: —, stage: placement, checks: [{{type: command, label: echo, cmd: '{{PY}} -c "print(1+1)"', expect_stdout_regex: '^2$'}}]}}
""")
    P = Project(f"{d}/project.yaml")
    text, failed, unmapped, _ = build(P, Ctx(P, tempfile.mkdtemp(), True))
    assert "| D-01.1 |" in text and "**VERIFIED**" in text, text
    assert "| D-01.2 | D-01 | routed | board | routing | **PENDING(routing)** | now 0/1 |" in text, text
    assert "| CC-001.1 |" in text and "**NOT-INCLUDED**" in text
    assert "CC-002.1 | CC-002 | q | — | schematic | **FAILED** | stale reason" in text, "a NOT-INCLUDED reason starting OPEN on a decided row must FAIL"
    assert "**VERIFIED** | cmd ✓ `echo` rc=0 «2»" in text
    assert unmapped == ["CC-003"] and failed == 1, (unmapped, failed)
    t2, failed2, *_ = build(P, Ctx(P, tempfile.mkdtemp(), False))
    assert "| CC-002.2 | CC-002 | cmd | — | placement | **PENDING(--no-commands)** | command SKIPPED (--no-commands) |" in t2, t2
    assert failed2 == 1, "--no-commands must not FAIL a command row (the one FAILED is the stale-reason row)"
    P2 = Project(f"{d}/project.yaml"); P2.cfg["paths"]["traceability_yaml"] = "20-design/none.yaml"
    try:
        build(P2, Ctx(P2, tempfile.mkdtemp(), False)); raise AssertionError("missing yaml must exit with MISSING")
    except SystemExit as e:
        assert e.code == 2, "a missing traceability yaml exits 2"
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
