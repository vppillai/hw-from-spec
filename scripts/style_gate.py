#!/usr/bin/env python3
"""scripts/style_gate.py - the writing-standard gate for a project with old records: a dated baseline keyed on file md5 (references/writing-style.md §4).

`scripts/style_lint.py --project <root>` reports every hit in the project's own texts. Old records can carry hundreds of hits that nobody
rewrites, so the plain lint cannot gate. This gate freezes a BASELINE: for every file with hits, its md5 and its hit count on the baseline day.
A file whose md5 still equals its baseline md5 passes with its frozen hits. Every other file (new, or edited since the baseline) lints at 0.
The baseline shrinks as files are touched. `--write` never runs on its own: freeze once at adoption, or after an owner decision row.

  scripts/style_gate.py              the gate: exit 1 on any new or edited file with hits
  scripts/style_gate.py --write      freeze today's baseline (paths.style_baseline, default 90-log/STYLE_BASELINE.json)
  scripts/style_gate.py --selftest

project.yaml `style_gate.exclude`: fnmatch globs on the relative path of generated records that are linted at their source (the generator's
text), never as files. Exit 0 = clean, 1 = a file must lint at 0, 2 = style_lint could not run.
"""
import argparse, datetime, fnmatch, hashlib, json, os, re, subprocess, sys

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)
from project import Project  # noqa: E402

LINT = os.path.join(HERE, "style_lint.py")


def md5(p):
    return hashlib.md5(open(p, "rb").read()).hexdigest()


def lint_hits(root):
    """{relpath: hit count} from `style_lint.py --project <root>` (lines `path:line: message`)."""
    r = subprocess.run([sys.executable, LINT, "--project", root], capture_output=True, text=True)
    if r.returncode == 2:
        print(f"style_gate: style_lint --project failed: {r.stdout.strip()} {r.stderr.strip()}"); sys.exit(2)
    hits = {}
    for line in r.stdout.splitlines():
        m = re.match(r"^(.+?):(\d+): ", line)
        if m:
            p = os.path.relpath(m.group(1) if os.path.isabs(m.group(1)) else os.path.join(root, m.group(1)), root)
            hits[p] = hits.get(p, 0) + 1
    return hits


def gate(root, base_path, hits, exclude=()):
    base = json.load(open(base_path)) if os.path.exists(base_path) else {"date": None, "files": {}}
    bad = []
    for p, n in sorted(hits.items()):
        if any(fnmatch.fnmatch(p, g) for g in exclude):
            continue
        b = base["files"].get(p); fp = os.path.join(root, p)
        if b and os.path.exists(fp) and md5(fp) == b["md5"]:
            continue                                                            # unchanged since the baseline: its frozen hits stand
        bad.append((p, n, "edited since the baseline" if b else "not in the baseline"))
    return base, bad


def write_baseline(root, base_path, hits, date, exclude=()):
    files = {p: {"md5": md5(os.path.join(root, p)), "hits": n} for p, n in sorted(hits.items())
             if os.path.exists(os.path.join(root, p)) and not any(fnmatch.fnmatch(p, g) for g in exclude)}
    os.makedirs(os.path.dirname(base_path), exist_ok=True)
    json.dump({"date": date, "rule": "a file with its baseline md5 keeps its hits; every new or edited file lints at 0", "files": files},
              open(base_path, "w"), indent=1)
    return files


def run(P, write=False):
    root = P.root; base_path = P.path("style_baseline"); exclude = list(P.get("style_gate.exclude") or [])
    hits = lint_hits(root)
    if write:
        files = write_baseline(root, base_path, hits, datetime.date.today().isoformat(), exclude)
        print(f"style_gate: baseline written, {len(files)} file(s) with {sum(f['hits'] for f in files.values())} frozen hit(s) -> {os.path.relpath(base_path, root)}")
        return 0
    base, bad = gate(root, base_path, hits, exclude)
    frozen = len(set(hits) - {b[0] for b in bad})
    for p, n, why in bad:
        print(f"style_gate: {p}: {n} hit(s), {why} -> must lint at 0")
    print(f"style_gate: {len(bad)} file(s) FAIL, {frozen} file(s) on the baseline of {base.get('date')} with frozen hits")
    return 1 if bad else 0


def selftest():
    import tempfile, io, contextlib
    d = tempfile.mkdtemp(prefix="hwfs_style_gate_")
    w = lambda p, s, m="w": (os.makedirs(os.path.dirname(f"{d}/{p}") or d, exist_ok=True), open(f"{d}/{p}", m).write(s))
    long = "This is one sentence that goes on and on and on with many many words to pass the forty word cap of the lint " * 2 + "end.\n"
    w("project.yaml", "project: {name: t}\nstyle_gate: {exclude: ['70-release/reports/*']}\n")
    w("90-log/OLD.md", "# Old\n\n" + long); w("README.md", "# Top\n\nShort line.\n"); w("70-release/reports/GEN.md", "# Gen\n\n" + long)
    P = Project(f"{d}/project.yaml"); base = f"{d}/90-log/STYLE_BASELINE.json"; ex = P.get("style_gate.exclude")
    assert P.path("style_baseline") == base, P.path("style_baseline")
    hits = lint_hits(d)
    assert hits.get("90-log/OLD.md", 0) >= 1 and "README.md" not in hits and "70-release/reports/GEN.md" in hits, hits
    q = contextlib.redirect_stdout(io.StringIO())
    with q:
        assert run(P) == 1, "no baseline: every file with hits fails"
        assert run(P, write=True) == 0 and run(P) == 0, "frozen hits pass"
    assert "70-release/reports/GEN.md" not in json.load(open(base))["files"], "an excluded file is never frozen"
    w("90-log/OLD.md", "\nAnother line.\n", "a")
    _, bad = gate(d, base, lint_hits(d), ex); assert [b[2] for b in bad] == ["edited since the baseline"], bad
    w("90-log/OLD.md", "# Old\n\nShort now.\n")
    _, bad = gate(d, base, lint_hits(d), ex); assert bad == [], ("an edited file at 0 hits passes", bad)
    w("60-orders/NEW.md", "# New\n\n" + long)
    _, bad = gate(d, base, lint_hits(d), ex); assert [b[:1] + b[2:] for b in bad] == [("60-orders/NEW.md", "not in the baseline")], bad
    print("style_gate selftest OK (no baseline fails, --write freezes, an unchanged file keeps its hits, an edited file lints at 0, a new file "
          "lints at 0, style_gate.exclude skips a generated record)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true", help="freeze the baseline from the current tree (dated today)")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--project")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    return run(Project.find(arg=a.project), a.write)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
