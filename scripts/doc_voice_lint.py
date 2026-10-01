#!/usr/bin/env python3
"""scripts/doc_voice_lint.py — the skill reads as the CURRENT procedure, not as a changelog (owner rule: "it should be just a comprehensive skill").

  scripts/doc_voice_lint.py [--skill DIR] [FILE...]   # default: SKILL.md, README.md, references/*.md, templates/** (text files)
  scripts/doc_voice_lint.py --selftest
Exit 1 with one line per hit (file:line: the phrase), 0 when clean, 2 when a file is missing. Two checks:
  1. changelog voice — a word list (`was changed`, `now`, `previously`, `fixed in`, `added in`, `this round`, `we did`, `replaces the old`, …) matched
     as whole words; a line may carry `<!-- voice: ok -->` when the phrase is part of a quoted owner sentence or a command name.
  2. version numbers in prose — `0.9.1`, `v0.8.0`, `0.10.0 added`, `since 0.x` outside CHANGELOG.md, docs/, and exactly ONE README line
     (the version line `version X.Y.Z`); SKILL.md's frontmatter `version:` is the one allowed occurrence there. A process-row or tool version
     (`VERSION`, `02.08`, `2021.01`, `KiCad 10.0.5`) is not a skill version: only `\\b0\\.\\d+\\.\\d+\\b` and `v0\\.\\d+\\.\\d+` count.
The reason a rule exists stays as a short clause (physics / a pitfall); the episode goes to pitfalls.md as a dated one-liner (pitfalls.md is
exempt from check 1 — it IS the dated record) or to CHANGELOG.md.
"""
import argparse, glob, os, re, sys, tempfile

VOICE = [r"\bwas changed\b", r"\bhas been changed\b", r"\bis now\b", r"\bare now\b", r"\bnow (reads|carries|has|have|uses|takes|runs|lists|says|needs|writes|ships|prints|checks|fails|refuses|requires|holds|gains|points)\b",
         r"\bpreviously\b", r"\bformerly\b", r"\bused to\b", r"\bno longer\b", r"\bfixed in\b", r"\badded in\b", r"\badded by\b", r"\bsince 0\.\d", r"\b0\.\d+\.\d+ (added|closed|fixed|mirrors|folded|introduced|ships|changed|removed|rewrote|rewritten)\b",
         r"\breplaces the old\b", r"\bthe old (block|name|spelling|rule|path|form)\b", r"\bwe did\b", r"\bthis round\b", r"\bthis version\b", r"\bthe (previous|last) version\b",
         r"\(was:? [^)]*\)", r"\bwas (a|the) (waiver|bug|defect)\b", r"\bretracted\b", r"\bdeprecated\b", r"\b(blind )?review 0\.\d+\.\d+\b", r"\((B|C|F)-?\d{1,2}(?: / (B|C|F)-?\d{1,2})*\)"]
VERSION_IN_PROSE = re.compile(r"(?<![\w.])v?0\.\d+\.\d+(?![\w.])")
EXEMPT_VOICE = ("references/pitfalls.md",)


def default_files(skill):
    out = [os.path.join(skill, "SKILL.md"), os.path.join(skill, "README.md")] + sorted(glob.glob(os.path.join(skill, "references", "*.md")))
    for dp, _, fs in os.walk(os.path.join(skill, "templates")):
        out += sorted(os.path.join(dp, f) for f in fs if f.endswith((".md", ".yaml", ".yml", ".sh", ".js")))
    return out


def lint(files, skill):
    hits = []
    for f in files:
        rel = os.path.relpath(f, skill)
        if not os.path.exists(f):
            hits.append((rel, 0, "MISSING")); continue
        readme = rel == "README.md"; version_lines = 0
        for n, line in enumerate(open(f, encoding="utf-8"), 1):
            if "<!-- voice: ok -->" in line:
                continue
            if rel not in EXEMPT_VOICE:
                for pat in VOICE:
                    m = re.search(pat, line, re.I)
                    if m:
                        hits.append((rel, n, f"changelog voice `{m.group(0)}`")); break
                else:
                    pass
                if hits and hits[-1][:2] == (rel, n):
                    continue                                                    # one hit per line
            if rel == "SKILL.md" and re.match(r"^version:\s*0\.", line):
                continue
            for m in VERSION_IN_PROSE.finditer(line):
                if readme and re.search(r"\bversion\b", line) and version_lines == 0:
                    version_lines += 1; break
                hits.append((rel, n, f"version number in prose `{m.group(0)}`")); break
    return hits


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_voice_"); os.makedirs(f"{d}/references"); os.makedirs(f"{d}/templates")
    open(f"{d}/SKILL.md", "w").write("---\nversion: 0.10.0\n---\nThe gate reads the cell. The census is a FAIL gate. <!-- voice: ok --> this is now fine\n")
    open(f"{d}/README.md", "w").write("# x\n`version 0.10.0` · MIT\n0.9.1 mirrors the rule set.\n")
    open(f"{d}/references/a.md", "w").write("The rule was changed in 0.9.0.\nA clean rule.\nPreviously the gate was prose.\n")
    open(f"{d}/references/pitfalls.md", "w").write("- 2026-09-30 the gate was changed — pitfalls may narrate.\n")
    open(f"{d}/templates/t.md", "w").write("Tools run through the pool (Bambu Studio 02.08, KiCad 10.0.5, OpenSCAD 2021.01).\n")
    h = lint(default_files(d), d)
    msgs = [f"{a}:{b}: {c}" for a, b, c in h]
    assert any("README.md:3" in m for m in msgs), msgs                                    # the second README version mention (voice or version, one hit per line)
    assert not any("README.md:2" in m for m in msgs), msgs                                 # the one version line
    assert any("references/a.md:1" in m and "was changed" in m for m in msgs) and any("references/a.md:3" in m and "Previously" in m for m in msgs), msgs
    assert not any("pitfalls.md" in m for m in msgs) and not any("SKILL.md" in m for m in msgs) and not any("templates/t.md" in m for m in msgs), msgs
    assert len(h) == 3, msgs
    print("selftest OK (voice words, one README version line, SKILL frontmatter exempt, tool versions ignored, pitfalls exempt, voice: ok marker)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--skill", default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    ap.add_argument("files", nargs="*"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    files = [os.path.abspath(f) for f in a.files] or default_files(a.skill)
    hits = lint(files, a.skill)
    for rel, n, what in hits:
        print(f"{rel}:{n}: {what}")
    print(f"doc_voice_lint: {len(hits)} hit(s) in {len(files)} file(s)")
    return 2 if any(w == "MISSING" for _, _, w in hits) else (1 if hits else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
