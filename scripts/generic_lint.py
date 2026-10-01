#!/usr/bin/env python3
"""scripts/generic_lint.py — the skill describes the METHOD for any hardware project, never the one it was learned on (owner rule).

  scripts/generic_lint.py [--skill DIR] [--terms scripts/generic_lint_terms.yaml] [FILE...]
      default files: SKILL.md, README.md, references/*.md, templates/** (text), scripts/* (docstrings and comments are part of the skill text).
      Exit 1 with one line per hit (file:line: <group> `<match>`), 0 when clean, 2 when the term file or a file is missing.
  scripts/generic_lint.py --selftest

Terms live in `scripts/generic_lint_terms.yaml` (regex per line, grouped: project names, parts / refdes, record ids used as citations, owner /
machine, preset names, this design's dimensions) so a retro can extend them. A group named `*_as_citations` applies to PROSE only (SKILL.md, README,
references/*.md): a fixture row in a selftest, the smoke or a template seed row uses the D-nn / CC-nnn id scheme by design and is not a citation. Lines between `<!-- worked example: begin` and
`<!-- worked example: end -->` are skipped — at most ONE such block per file (a second one is a hit); a line carrying `generic: ok` is skipped
(a lint pattern that must spell a term, a fixture). CHANGELOG.md, docs/retro/, docs/reviews/
and this term file are never linted: history and reviews are allowed to name the project.
"""
import argparse, glob, os, re, sys, tempfile

BEGIN, END = "<!-- worked example: begin", "<!-- worked example: end -->"


def load_terms(path):
    import yaml
    groups = yaml.safe_load(open(path, encoding="utf-8")) or {}
    return [(g, re.compile(p)) for g, pats in groups.items() for p in (pats or [])]


def default_files(skill):
    out = [os.path.join(skill, "SKILL.md"), os.path.join(skill, "README.md")] + sorted(glob.glob(os.path.join(skill, "references", "*.md")))
    for sub, exts in (("templates", (".md", ".yaml", ".yml", ".sh", ".js", ".gitignore")), ("scripts", (".py", ".sh")), ("workflows", (".js", ".md")), ("evals", (".json", ".py")), ("smoke", (".sh", ".md", ".yaml"))):
        for dp, _, fs in os.walk(os.path.join(skill, sub)):
            out += sorted(os.path.join(dp, f) for f in fs if f.endswith(exts) and not f.startswith("generic_lint") and "__pycache__" not in dp)
    return out


def lint(files, terms, skill):
    hits = []
    for f in files:
        rel = os.path.relpath(f, skill)
        if not os.path.exists(f):
            hits.append((rel, 0, "MISSING", "")); continue
        blocks = 0; inside = False
        for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            if BEGIN in line:
                blocks += 1; inside = True
                if blocks > 1:
                    hits.append((rel, n, "worked-example", "a second worked-example block (one per file)"))
                continue
            if END in line:
                inside = False; continue
            if inside or "generic: ok" in line:
                continue
            for g, rx in terms:
                if g.endswith("_as_citations") and (not rel.endswith(".md") or rel.startswith(("smoke/", "templates/"))):
                    continue                                                    # a record id is a CITATION only in prose; fixtures and template seed rows use the id scheme by design
                if g in ("parts_and_refdes", "design_dimensions") and rel.startswith(("smoke/", "evals/")):
                    continue                                                    # the smoke is a fixture project with fake codes; eval 7 is the labelled regression scenario
                m = rx.search(line)
                if m:
                    hits.append((rel, n, g, m.group(0))); break
    return hits


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_generic_"); os.makedirs(f"{d}/references"); os.makedirs(f"{d}/scripts")
    open(f"{d}/scripts/generic_lint_terms.yaml", "w").write("names:\n  - '\\bAEC-CT2\\b'\n  - '(?i)tenstorrent'\nrefdes:\n  - '\\bJ\\d{3}\\b'\n")
    open(f"{d}/SKILL.md", "w").write("A rule about the host connector pads.\nThe AEC-CT2 board did X.\n<!-- worked example: begin (source project, 2026) -->\nJ401 sits at Y 136.5.\n<!-- worked example: end -->\nJ401 again. # generic: ok\n")
    open(f"{d}/README.md", "w").write("Generic text.\n")
    open(f"{d}/references/a.md", "w").write("Tenstorrent owns it.\n<!-- worked example: begin -->\nx\n<!-- worked example: end -->\n<!-- worked example: begin -->\ny\n<!-- worked example: end -->\n")
    terms = load_terms(f"{d}/scripts/generic_lint_terms.yaml")
    h = lint(default_files(d), terms, d); msgs = [f"{a}:{b}: {c} `{e}`" for a, b, c, e in h]
    assert any("SKILL.md:2: names `AEC-CT2`" in m for m in msgs), msgs
    assert not any("SKILL.md:4" in m for m in msgs) and not any("SKILL.md:6" in m for m in msgs), ("worked example and generic: ok lines are skipped", msgs)
    assert any("references/a.md:1: names `Tenstorrent`" in m for m in msgs) and any("worked-example" in m for m in msgs), msgs
    assert len(h) == 3, msgs
    print("selftest OK (term groups, worked-example block skipped, one block per file, generic: ok marker, default file set)")
    return 0


def main(argv):
    skill_default = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--skill", default=skill_default)
    ap.add_argument("--terms"); ap.add_argument("files", nargs="*"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    tp = a.terms or os.path.join(a.skill, "scripts", "generic_lint_terms.yaml")
    if not os.path.exists(tp):
        print(f"generic_lint: MISSING term file {tp}", file=sys.stderr); return 2
    files = [os.path.abspath(f) for f in a.files] or default_files(a.skill)
    hits = lint(files, load_terms(tp), a.skill)
    for rel, n, g, m in hits:
        print(f"{rel}:{n}: {g} `{m}`" if g != "MISSING" else f"{rel}: MISSING")
    print(f"generic_lint: {len(hits)} hit(s) in {len(files)} file(s)")
    return 2 if any(g == "MISSING" for _, _, g, _ in hits) else (1 if hits else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
