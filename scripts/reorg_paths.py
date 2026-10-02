#!/usr/bin/env python3
"""scripts/reorg_paths.py — path migration with a zero-loss proof (references/project-yaml.md `reorg:`; SKILL §2).

The move table lives in project.yaml (`reorg.moves: {old: new}`, a file or a whole directory per row), so a re-layout is a decision row +
one yaml block + one run, and the same table answers "where did docs/X go?" for every dated record that still spells the old path.

  scripts/reorg_paths.py --plan       dry run: git mv rows, trims, untracks, rewrite counts per file (nothing written)
  scripts/reorg_paths.py --apply      git mv every move (longest key first, so a file listed out of a moved directory leaves before the
                                      directory goes), rewrite the literals in every non-frozen tracked text file, git rm the trims,
                                      git rm --cached the untrack globs (files stay on disk), append the gitignore lines; writes reorg.rewrites_record
  scripts/reorg_paths.py --check      exit 1 on (1) any OLD literal left in a non-frozen tracked text file, (2) any literal under a moved top
                                      directory that names a file that does not exist (structural files only; reorg.allow_missing regexes)
  scripts/reorg_paths.py --map        old -> new table, for readers of frozen records
  scripts/reorg_paths.py --map docs/quotes/2026-01-01/mail.txt   one path, answered by the longest matching move key (a sub-path of a
                                      moved directory prints under the directory's new name)
  scripts/reorg_paths.py --proof BEFORE AFTER REWRITES   zero-loss: every `git ls-files -s` row of BEFORE is in AFTER at its mapped path with the
                                      same blob, or its path is in REWRITES (blob legitimately changed) / trim / untrack; exit 1 on any miss
  scripts/reorg_paths.py --selftest

Rewrite rule: the literal `<old>` (longest first; not preceded by a word char, `-` or `<word>/`, so `./docs/X`, `{ROOT}/docs/X`, `HEAD:docs/X`
match and `other-repo/docs/X` does not; not followed by a word char, so a directory key rewrites every sub-path under it and leaves
`docs/X_old/` alone) -> `<new>`; plus the join forms `"docs" / "X"` and `"docs", "X"` for a one-level old path. Frozen dirs (uploaded
packages, archived records, quote evidence: `reorg.frozen`, spelled by old or new name, `*` for one path segment) are moved when they
are a move key but never rewritten or checked; this script's own files are never touched; binaries never.
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
        self.olds = olds
        inv = {v: k for k, v in self.moves.items()}
        names = {n for f in self.frozen + self.skip for n in (f, self.map(f), self.map(f, inv))}
        self.frozen_rx = re.compile("^(?:" + "|".join(re.escape(n.rstrip("/")).replace(r"\*", "[^/]*") for n in sorted(names)) + ")(?:/|$)") if names else None
        self.old_rx = re.compile(r"(?<![\w-])(?<!\w/)(" + "|".join(map(re.escape, olds)) + r")(?!\w)") if olds else None
        joins = [(o.split("/", 1)) for o in olds if o.count("/") == 1]
        self.join_rx = re.compile(r'"(' + "|".join(sorted({d for d, _ in joins})) + r')"(\s*[/,]\s*)"(' + "|".join(re.escape(b) for _, b in joins) + r')"') if joins else None
        tops = sorted({n.split("/")[0] for n in self.moves.values()} | {o.split("/")[0] for o in olds})
        self.lit_rx = re.compile(r"(?<![\w-])(?<!\w/)((?:" + "|".join(map(re.escape, tops)) + r")/[A-Za-z0-9_][A-Za-z0-9_./+-]*\.[A-Za-z0-9]{1,10})(?![\w…/])") if tops else None   # `docs/v1.2/x` is a directory segment, not a file

    def map(self, p, moves=None):
        """Where `p` lives after the moves: the longest key equal to `p` or a directory prefix of it, with the remainder appended."""
        moves = self.moves if moves is None else moves
        for old in sorted(moves, key=len, reverse=True):
            if p == old or p.startswith(old.rstrip("/") + "/"):
                return moves[old] + p[len(old):]
        return p

    def frozen_match(self, p):
        return bool(self.frozen_rx and self.frozen_rx.match(p))

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
            if self.frozen_match(p) or p in self.allow_old_files:
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
        for old in self.olds:                       # longest key first: a file listed out of a moved directory leaves before the directory goes
            new = self.moves[old]
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
            q = self.map(p)
            if q not in a:
                missing.append(f"{p} -> {q}: not in AFTER"); continue
            moved += q != p
            if a[q] == sha:
                same += 1
            elif q in rw or p in rw:
                rewritten += 1
            else:
                missing.append(f"{p} -> {q}: blob {sha[:8]} -> {a[q][:8]} but not in the rewrite list")
        new = sorted(set(a) - {self.map(p) for p in b})
        print(f"before {len(b)} / after {len(a)} tracked; moved {moved}; blob-identical {same}; rewritten {rewritten}; removed (git rm — name the tag "
              f"that keeps them in the record) {len(removed)}; untracked-kept-on-disk {len(untracked)}; new in AFTER {len(new)}: {', '.join(new)}")
        print("MISSING:", len(missing)); [print("  ", m) for m in missing]
        [print(f"   removed  {sha}  {p}") for p, sha in removed]; [print(f"   untracked  {sha}  {p}") for p, sha in untracked]
        return 1 if missing else 0


def selftest():
    import io, contextlib
    d = tempfile.mkdtemp(prefix="hwfs_reorg_")
    w = lambda p, s: (os.makedirs(os.path.dirname(f"{d}/{p}"), exist_ok=True), open(f"{d}/{p}", "w").write(s))
    # a docs/-style layout -> the numbered tree: a directory move with one file pulled out of it (longest key first), a one-level file
    # move (join forms), a frozen directory (spelled by its NEW name, as the template does) whose content must survive byte-identical
    w("project.yaml", "project: {name: t}\nreorg:\n  moves: {docs/governance: 90-log, docs/governance/KICKOFF_ANSWERS.md: 10-spec/KICKOFF_ANSWERS.md, "
      "docs/parts_check.json: 60-orders/parts_check.json, docs/quotes: 60-orders/quotes}\n  trim: [out/old]\n  untrack: ['out/logs/*.log']\n"
      "  gitignore: ['out/logs/*.log']\n  frozen: [out/fab/, 60-orders/quotes, '70-release/*/records']\n  no_existence: ['.py', '.js', 90-log/DECISIONS.md]\n"
      "  allow_missing: ['^60-orders/quotes/']\n  rewrites_record: 80-reviews/REORG_REWRITES.txt\n")
    w("docs/governance/DECISIONS.md", "see docs/governance/STATUS.md and ./docs/governance/GATES.md and other-repo/docs/governance/STATUS.md and "
      "docs/governance_2026/x.md and docs/gone.md and docs/quotes/2026-01-01/mail.txt and docs/governance/KICKOFF_ANSWERS.md\n")
    w("docs/governance/STATUS.md", "x\n"); w("docs/governance/GATES.md", "y\n"); w("docs/governance/KICKOFF_ANSWERS.md", "k\n")
    w("docs/parts_check.json", "{}\n"); w("docs/governance_2026/x.md", "z\n")
    w("gen/a.py", 'A = (ROOT / "docs" / "parts_check.json")\nB = os.path.join(R, "docs", "quotes")\nC = "docs/parts_check.json"\nD = "60-orders/quotes/2026-02-02/gone.txt"\n')
    frozen_txt = "see docs/quotes/2026-01-01/mail.txt\n"
    w("docs/quotes/2026-01-01/mail.txt", frozen_txt)
    w("out/fab/old.md", "frozen docs/governance/DECISIONS.md\n"); w("out/old/x.txt", "g\n"); w("out/logs/run.log", "l\n")
    w("design/live.yaml", "path: docs/missing_file.md\nok: 60-orders/quotes/2026-02-02/gone.txt\nver: docs/v1.2/notes\nurl: https://x/blob/main/docs/governance/STATUS.md\n")
    subprocess.run(["git", "init", "-q", d], check=True)
    g = lambda *a: subprocess.run(["git", "-c", "user.email=a@b", "-c", "user.name=t", *a], cwd=d, check=True, capture_output=True, text=True).stdout
    g("add", "-A"); g("commit", "-qm", "0"); before = g("ls-files", "-s")
    R = Reorg(Project(f"{d}/project.yaml"))
    for old, new in {"docs/quotes/2026-01-01/mail.txt": "60-orders/quotes/2026-01-01/mail.txt", "docs/governance/KICKOFF_ANSWERS.md": "10-spec/KICKOFF_ANSWERS.md",
                     "docs/governance/X.md": "90-log/X.md", "docs/governance": "90-log", "docs/governance_2026/x.md": "docs/governance_2026/x.md"}.items():
        assert R.map(old) == new, (old, R.map(old))                                                     # longest prefix; a sibling with a longer name is not a sub-path
    assert R.frozen_match("docs/quotes/2026-01-01/mail.txt") and R.frozen_match("60-orders/quotes/2026-01-01/mail.txt"), "frozen matches old and new spelling"
    assert R.frozen_match("70-release/rev0/records/x.json") and not R.frozen_match("70-release/rev0/x.json") and not R.frozen_match("60-orders/quotes_x/y")
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.check(verbose=True) == 1, "old literals present -> check must fail before the move"
    assert "mail.txt:" not in buf.getvalue(), buf.getvalue()                                            # the frozen file is not checked before the move either
    rw, un = R.apply()
    assert {p for p, _ in rw} == {"90-log/DECISIONS.md", "gen/a.py"}, rw
    t = open(f"{d}/90-log/DECISIONS.md").read()
    assert t == ("see 90-log/STATUS.md and ./90-log/GATES.md and other-repo/docs/governance/STATUS.md and docs/governance_2026/x.md and docs/gone.md and "
                 "60-orders/quotes/2026-01-01/mail.txt and 10-spec/KICKOFF_ANSWERS.md\n"), t
    t = open(f"{d}/gen/a.py").read()
    assert '"60-orders" / "parts_check.json"' in t and '"60-orders", "quotes"' in t and 'C = "60-orders/parts_check.json"' in t, t
    assert os.path.exists(f"{d}/10-spec/KICKOFF_ANSWERS.md") and not os.path.exists(f"{d}/docs/governance"), "file pulled out before its directory moved"
    assert open(f"{d}/60-orders/quotes/2026-01-01/mail.txt").read() == frozen_txt, "frozen directory moved as a whole, content byte-identical"
    assert "frozen docs/governance/DECISIONS.md" in open(f"{d}/out/fab/old.md").read(), "frozen file rewritten"
    assert R.plan() == [], "second pass must be a no-op (idempotent)"
    assert not g("ls-files", "out/old").strip() and not g("ls-files", "out/logs/run.log").strip() and os.path.exists(f"{d}/out/logs/run.log")
    assert "out/logs/*.log" in open(f"{d}/.gitignore").read() and un == ["out/logs/run.log"]
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.check(verbose=True) == 1
    bad_lines = buf.getvalue()
    assert "dangling `docs/missing_file.md`" in bad_lines and "docs/gone.md" not in bad_lines, bad_lines   # DECISIONS is a record (no_existence); live.yaml is structural
    assert "2026-02-02" not in bad_lines and "docs/v1.2" not in bad_lines, bad_lines                        # allow_missing regex; a directory segment is not a file
    assert "blob/main/docs/governance/STATUS.md" in open(f"{d}/design/live.yaml").read(), "URLs are not rewritten (documented)"
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert main(["reorg_paths.py", "--map", "docs/quotes/2026-01-01/mail.txt", "--project", f"{d}/project.yaml"]) == 0
    assert buf.getvalue() == "60-orders/quotes/2026-01-01/mail.txt\n", buf.getvalue()
    g("add", "-A"); g("commit", "-qm", "1"); after = g("ls-files", "-s")
    open(f"{d}/B", "w").write(before); open(f"{d}/A", "w").write(after)
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.proof(f"{d}/B", f"{d}/A", f"{d}/80-reviews/REORG_REWRITES.txt") == 0, buf.getvalue()
    assert "MISSING: 0" in buf.getvalue() and "moved 6" in buf.getvalue(), buf.getvalue()             # 3 under docs/governance + KICKOFF + parts_check + the frozen mail
    row = next(l for l in after.splitlines() if l.endswith("design/live.yaml"))                       # a blob-identical file: corrupt its sha in AFTER
    open(f"{d}/A2", "w").write(after.replace(row, row.replace(row.split()[1], "0" * 40)))              # = changed without being in the rewrite list
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        assert R.proof(f"{d}/B", f"{d}/A2", f"{d}/80-reviews/REORG_REWRITES.txt") == 1
    assert "not in the rewrite list" in buf.getvalue() or "not in AFTER" in buf.getvalue(), buf.getvalue()
    os.remove(f"{d}/design/live.yaml"); g("rm", "-q", "design/live.yaml")
    assert R.check(verbose=False) == 0, "clean fixture must pass"
    print("selftest OK (directory + file moves longest-key first, rewrite idempotent, frozen dir moved whole and byte-identical under old and new "
          "spelling + glob, join forms, URLs untouched, trim/untrack/gitignore, dangling vs record vs allow_missing vs dir segment, --map sub-path, zero-loss proof pass + fail)")
    return 0

def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    for f in ("plan", "apply", "check", "selftest"):
        ap.add_argument("--" + f, action="store_true")
    ap.add_argument("--map", nargs="?", const="", metavar="OLD_PATH", help="the old -> new table, or where one old path (file or sub-path of a moved directory) lives")
    ap.add_argument("--proof", nargs=3, metavar=("BEFORE", "AFTER", "REWRITES"))
    ap.add_argument("--project")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    R = Reorg(Project.find(arg=a.project))
    if not R.moves and a.map is None:
        sys.exit("project.yaml has no reorg.moves — nothing to migrate (references/project-yaml.md `reorg:`)")
    if a.map:
        print(R.map(a.map))
    elif a.map is not None:
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
