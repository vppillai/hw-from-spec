#!/usr/bin/env python3
"""scripts/reorg_paths.py — path migration with a zero-loss proof (references/project-yaml.md `reorg:`; SKILL §2).

The move table lives in project.yaml (`reorg.moves: {old: new}`), so a re-layout is a decision row + one yaml block + one run, and the
same table answers "where did docs/X go?" for every dated record that still spells the old path.

  scripts/reorg_paths.py --plan       dry run: git mv rows, trims, untracks, rewrite counts per file (nothing written)
  scripts/reorg_paths.py --apply      git mv every move, rewrite the literals in every non-frozen tracked text file, git rm the trims,
                                      git rm --cached the untrack globs (files stay on disk), append the gitignore lines; writes reorg.rewrites_record
  scripts/reorg_paths.py --check      exit 1 on (1) any OLD literal left in a non-frozen tracked text file, (2) any literal under a moved top
                                      directory that names a file that does not exist (structural files only; reorg.allow_missing regexes)
  scripts/reorg_paths.py --map        old -> new table, for readers of frozen records
  scripts/reorg_paths.py --proof BEFORE AFTER REWRITES   zero-loss: every `git ls-files -s` row of BEFORE is in AFTER at its mapped path with the
                                      same blob, or its path is in REWRITES (blob legitimately changed) / trim / untrack; exit 1 on any miss
  scripts/reorg_paths.py --selftest

Rewrite rule: the literal `<old>` (longest first; not preceded by a word char, `-` or `<word>/`, so `./docs/X`, `{ROOT}/docs/X`, `HEAD:docs/X`
match and `other-repo/docs/X` does not; not followed by a word char) -> `<new>`; plus the join forms `"docs" / "X"` and `"docs", "X"` for a
one-level old path. Frozen dirs (uploaded packages, archived records) and this script's own files are never touched; binaries never.
Learned the hard way (references/pitfalls.md, process): exempt the rewriter's OWN files from the rewrite, not only from the check; generated text
under out/ embeds docs paths too; a literal rewrite moves the md5 of files other generators stamp — regenerate the chain, do not hand-edit.
Not rewritten: URLs into the repo (`…/blob/main/docs/X.md` — the `<word>/` guard excludes them; grep `blob/.*/<old>` by hand) and binaries.
Paths with non-ASCII characters: run the `git ls-files -s` dumps with `git -c core.quotepath=off`.
"""
import argparse, os, re, subprocess, sys, tempfile

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project  # noqa: E402

TEXT_EXT = {".md", ".py", ".yaml", ".yml", ".js", ".json", ".sh", ".txt", ".csv", ".env", ".rules", ".svg", ".xml", ".scad", ".html", ".css",
            ".toml", ".cfg", ".ini", ".gitignore", ".gitattributes", ".kicad_sch", ".kicad_pro", ".kicad_wks", ".kicad_dru"}
TEXT_NAMES = {"Makefile", ".gitignore", ".gitattributes"}


class Reorg:
    def __init__(self, P):
        self.P, self.root = P, P.root
        r = P.get("reorg") or {}
        self.moves = dict(r.get("moves") or {})
        self.trim = list(r.get("trim") or []); self.untrack = list(r.get("untrack") or []); self.gitignore = list(r.get("gitignore") or [])
        self.frozen = tuple(r.get("frozen") or ()); self.skip = tuple(r.get("skip") or ())
        self.allow_old_files = set(r.get("allow_old_files") or ()) | {"scripts/reorg_paths.py", "project.yaml"}
        self.no_existence = tuple(r.get("no_existence") or (".py", ".js"))
        self.allow_missing = [re.compile(p) for p in (r.get("allow_missing") or [])]
        self.record = r.get("rewrites_record") or P.get("paths.reorg_rewrites")
        olds = sorted(self.moves, key=len, reverse=True)
        self.old_rx = re.compile(r"(?<![\w-])(?<!\w/)(" + "|".join(map(re.escape, olds)) + r")(?!\w)") if olds else None
        joins = [(o.split("/", 1)) for o in olds if o.count("/") == 1]
        self.join_rx = re.compile(r'"(' + "|".join(sorted({d for d, _ in joins})) + r')"(\s*[/,]\s*)"(' + "|".join(re.escape(b) for _, b in joins) + r')"') if joins else None
        tops = sorted({n.split("/")[0] for n in self.moves.values()} | {o.split("/")[0] for o in olds})
        self.lit_rx = re.compile(r"(?<![\w-])(?<!\w/)((?:" + "|".join(map(re.escape, tops)) + r")/[A-Za-z0-9_][A-Za-z0-9_./+-]*\.[A-Za-z0-9]{1,10})(?![\w…/])") if tops else None   # `docs/v1.2/x` is a directory segment, not a file

    def sub(self, text):
        if self.old_rx:
            text = self.old_rx.sub(lambda m: self.moves[m.group(1)], text)
        if self.join_rx:
            def join(m):
                old = f"{m.group(1)}/{m.group(3)}"
                if old not in self.moves:
                    return m.group(0)
                parts = self.moves[old].split("/")
                return m.group(2).join(f'"{p}"' for p in parts)
            text = self.join_rx.sub(join, text)
        return text

    def git(self, *a, check=True):
        return subprocess.run(["git", *a], cwd=self.root, capture_output=True, text=True, check=check).stdout

    def tracked_text(self):
        for p in self.git("ls-files").splitlines():
            if p.startswith(self.frozen + self.skip) or p in self.allow_old_files:
                continue
            if (os.path.basename(p) in TEXT_NAMES or os.path.splitext(p)[1] in TEXT_EXT) and os.path.isfile(os.path.join(self.root, p)):
                yield p

    def read(self, p):
        try:
            return open(os.path.join(self.root, p), encoding="utf-8").read()
        except UnicodeDecodeError:
            return None

    def plan(self, write=False):
        out = []
        for p in self.tracked_text():
            t = self.read(p)
            if t is None or not self.old_rx:
                continue
            n = len(self.old_rx.findall(t)) + (len(self.join_rx.findall(t)) if self.join_rx else 0)
            if n:
                out.append((p, n))
                if write:
                    open(os.path.join(self.root, p), "w", encoding="utf-8").write(self.sub(t))
        return out

    def apply(self):
        for old, new in self.moves.items():
            if self.git("ls-files", old).strip():
                os.makedirs(os.path.dirname(os.path.join(self.root, new)) or self.root, exist_ok=True)
                self.git("mv", old, new)
        rewrites = self.plan(write=True)            # after the move: the corpus is enumerated from the index, which now holds the new paths
        for p in self.trim:
            if self.git("ls-files", p).strip():
                self.git("rm", "-r", "-q", p)
        untracked = []
        for g in self.untrack:
            for p in self.git("ls-files", g).splitlines():
                self.git("rm", "--cached", "-q", p); untracked.append(p)
        if self.gitignore:
            gi = os.path.join(self.root, ".gitignore"); cur = open(gi).read() if os.path.exists(gi) else ""
            add = [l for l in self.gitignore if l not in cur.splitlines()]
            if add:
                open(gi, "a").write("\n".join(add) + "\n")
        rec = os.path.join(self.root, self.record); os.makedirs(os.path.dirname(rec), exist_ok=True)
        open(rec, "w").write("\n".join(p for p, _ in rewrites) + "\n")
        return rewrites, untracked

    def check(self, verbose=True):
        bad = []
        for p in self.tracked_text():
            t = self.read(p)
            if t is None:
                continue
            for n, line in enumerate(t.splitlines(), 1):
                for m in (self.old_rx.finditer(line) if self.old_rx else ()):
                    bad.append(f"{p}:{n}: old literal `{m.group(0)}` -> `{self.moves[m.group(1)]}`")
                for m in (self.join_rx.finditer(line) if self.join_rx else ()):
                    if f"{m.group(1)}/{m.group(3)}" in self.moves:
                        bad.append(f"{p}:{n}: old join form `{m.group(0)}`")
            if not self.lit_rx or p.endswith(tuple(x for x in self.no_existence if x.startswith("."))) or p.startswith(tuple(x for x in self.no_existence if not x.startswith("."))):
                continue
            for n, line in enumerate(t.splitlines(), 1):
                for m in self.lit_rx.finditer(line):
                    lit = m.group(1).rstrip(".")
                    if any(a.search(lit) for a in self.allow_missing):
                        continue
                    if not os.path.exists(os.path.join(self.root, lit)):
                        bad.append(f"{p}:{n}: dangling `{lit}`")
        if verbose:
            print(*bad, sep="\n") if bad else None
            print(f"reorg_paths --check: {'FAILED ' + str(len(bad)) + ' finding(s)' if bad else 'OK 0 findings'}")
        return 1 if bad else 0

    def proof(self, before, after, rewrites):
        def load(f):
            return {l.rstrip("\n").split(None, 3)[3]: l.split()[1] for l in open(f) if l.strip()}
        b, a = load(before), load(after)
        rw = {l.strip() for l in open(rewrites) if l.strip()}
        trims = tuple(t.rstrip("/") + "/" for t in self.trim); trim_files = set(self.trim)
        untrack_rx = [re.compile("^" + re.escape(g).replace(r"\*\*/", "(?:.*/)?").replace(r"\*", "[^/]*") + "$") for g in self.untrack]
        missing, moved, same, rewritten, removed, untracked = [], 0, 0, 0, [], []
        for p, sha in b.items():
            if p in trim_files or p.startswith(trims):
                removed.append((p, sha)); continue
            if any(r.match(p) for r in untrack_rx):
                f = os.path.join(self.root, p); untracked.append((p, sha))
                if not os.path.exists(f):
                    missing.append(f"{p}: untracked but gone from disk")
                continue
            q = self.moves.get(p, p)
            if q not in a:
                missing.append(f"{p} -> {q}: not in AFTER"); continue
            moved += q != p
            if a[q] == sha:
                same += 1
            elif q in rw or p in rw:
                rewritten += 1
            else:
                missing.append(f"{p} -> {q}: blob {sha[:8]} -> {a[q][:8]} but not in the rewrite list")
        new = sorted(set(a) - {self.moves.get(p, p) for p in b})
        print(f"before {len(b)} / after {len(a)} tracked; moved {moved}; blob-identical {same}; rewritten {rewritten}; removed (git rm — name the tag "
              f"that keeps them in the record) {len(removed)}; untracked-kept-on-disk {len(untracked)}; new in AFTER {len(new)}: {', '.join(new)}")
        print("MISSING:", len(missing)); [print("  ", m) for m in missing]
        [print(f"   removed  {sha}  {p}") for p, sha in removed]; [print(f"   untracked  {sha}  {p}") for p, sha in untracked]
        return 1 if missing else 0


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_reorg_")
    w = lambda p, s: (os.makedirs(os.path.dirname(f"{d}/{p}"), exist_ok=True), open(f"{d}/{p}", "w").write(s))
    w("project.yaml", "project: {name: t}\nreorg:\n  moves: {docs/DECISIONS.md: docs/governance/DECISIONS.md, docs/STATUS.md: docs/governance/STATUS.md, "
      "docs/GATES.md: docs/governance/GATES.md, docs/parts_check.json: docs/parts/parts_check.json}\n  trim: [out/old]\n  untrack: ['out/logs/*.log']\n"
      "  gitignore: ['out/logs/*.log']\n  frozen: [out/fab/]\n  no_existence: ['.py', '.js', docs/governance/DECISIONS.md]\n"
      "  allow_missing: ['^docs/production/[0-9a-f]{8}/']\n  rewrites_record: docs/reviews/REORG_REWRITES.txt\n")
    w("docs/DECISIONS.md", "see docs/STATUS.md and ./docs/GATES.md and other-repo/docs/STATUS.md and docs/STATUS_2026.md and docs/gone.md\n")
    w("docs/STATUS.md", "x\n"); w("docs/GATES.md", "y\n"); w("docs/parts_check.json", "{}\n"); w("docs/STATUS_2026.md", "z\n")
    w("gen/a.py", 'A = (ROOT / "docs" / "parts_check.json")\nB = os.path.join(R, "docs", "DECISIONS.md")\nC = "docs/parts_check.json"\nD = "docs/production/0123abcd/STATUS.md"\n')
    w("out/fab/old.md", "frozen docs/DECISIONS.md\n"); w("out/old/x.txt", "g\n"); w("out/logs/run.log", "l\n")
    w("design/live.yaml", "path: docs/missing_file.md\nok: docs/production/0123abcd/STATUS.md\nver: docs/v1.2/notes\nurl: https://x/blob/main/docs/STATUS.md\n")
    subprocess.run(["git", "init", "-q", d], check=True)
    g = lambda *a: subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", *a], cwd=d, check=True, capture_output=True, text=True).stdout
    g("add", "-A"); g("commit", "-qm", "0"); before = g("ls-files", "-s")
    R = Reorg(Project(f"{d}/project.yaml"))
    assert R.check(verbose=False) == 1, "old literals present -> check must fail before the move"
    rw, un = R.apply()
    assert {p for p, _ in rw} == {"docs/governance/DECISIONS.md", "gen/a.py"}, rw
    t = open(f"{d}/docs/governance/DECISIONS.md").read()
    assert t == "see docs/governance/STATUS.md and ./docs/governance/GATES.md and other-repo/docs/STATUS.md and docs/STATUS_2026.md and docs/gone.md\n", t
    t = open(f"{d}/gen/a.py").read()
    assert '"docs" / "parts" / "parts_check.json"' in t and '"docs", "governance", "DECISIONS.md"' in t and 'C = "docs/parts/parts_check.json"' in t, t
    assert "frozen docs/DECISIONS.md" in open(f"{d}/out/fab/old.md").read(), "frozen file rewritten"
    assert R.plan() == [], "second pass must be a no-op (idempotent)"
    assert not g("ls-files", "out/old").strip() and not g("ls-files", "out/logs/run.log").strip() and os.path.exists(f"{d}/out/logs/run.log")
    assert "out/logs/*.log" in open(f"{d}/.gitignore").read() and un == ["out/logs/run.log"]
    import io, contextlib
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.check(verbose=True) == 1
    bad_lines = buf.getvalue()
    assert "dangling `docs/missing_file.md`" in bad_lines and "docs/gone.md" not in bad_lines, bad_lines   # DECISIONS is a record (no_existence); live.yaml is structural
    assert "0123abcd" not in bad_lines and "docs/v1.2" not in bad_lines, bad_lines                          # allow_missing regex; a directory segment is not a file
    assert "blob/main/docs/STATUS.md" in open(f"{d}/design/live.yaml").read(), "URLs are not rewritten (documented)"
    g("add", "-A"); g("commit", "-qm", "1"); after = g("ls-files", "-s")
    open(f"{d}/B", "w").write(before); open(f"{d}/A", "w").write(after)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.proof(f"{d}/B", f"{d}/A", f"{d}/docs/reviews/REORG_REWRITES.txt") == 0, buf.getvalue()
    assert "MISSING: 0" in buf.getvalue() and "moved 4" in buf.getvalue(), buf.getvalue()
    row = next(l for l in after.splitlines() if l.endswith("design/live.yaml"))                       # a blob-identical file: corrupt its sha in AFTER
    open(f"{d}/A2", "w").write(after.replace(row, row.replace(row.split()[1], "0" * 40)))              # = changed without being in the rewrite list
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.proof(f"{d}/B", f"{d}/A2", f"{d}/docs/reviews/REORG_REWRITES.txt") == 1
    assert "not in the rewrite list" in buf.getvalue() or "not in AFTER" in buf.getvalue(), buf.getvalue()
    os.remove(f"{d}/design/live.yaml"); g("rm", "-q", "design/live.yaml")
    assert R.check(verbose=False) == 0, "clean fixture must pass"
    print("selftest OK (move + rewrite idempotent, frozen untouched, join forms, URLs untouched, trim/untrack/gitignore, dangling vs record vs allow_missing vs dir segment, zero-loss proof pass + fail)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for f in ("plan", "apply", "check", "map", "selftest"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--proof", nargs=3, metavar=("BEFORE", "AFTER", "REWRITES"))
    ap.add_argument("--project")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    R = Reorg(Project.find(arg=a.project))
    if not R.moves and not a.map:
        sys.exit("project.yaml has no reorg.moves — nothing to migrate (references/project-yaml.md `reorg:`)")
    if a.map:
        [print(f"{k} -> {v}") for k, v in R.moves.items()]
        print("removed (git rm; name the tag that keeps them):", *R.trim, sep="\n  ") if R.trim else None
        print("untracked (kept on disk):", *R.untrack, sep="\n  ") if R.untrack else None
    elif a.plan:
        [print(f"git mv {k} {v}") for k, v in R.moves.items()]; [print(f"git rm -r {p}") for p in R.trim]; [print(f"git rm --cached {g}") for g in R.untrack]
        rw = R.plan(); [print(f"{n:5d}  {p}") for p, n in sorted(rw, key=lambda x: -x[1])]
        print(f"{sum(n for _, n in rw)} literals in {len(rw)} files")
    elif a.apply:
        rw, un = R.apply()
        print(f"moved {len(R.moves)}; rewrote {sum(n for _, n in rw)} literals in {len(rw)} files ({R.record}); trimmed {len(R.trim)}; untracked {len(un)}. "
              f"Next: regenerate every generated file that embeds paths, then --check, then --proof on the two `git ls-files -s` dumps.")
    elif a.proof:
        return R.proof(*a.proof)
    else:
        return R.check()
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
