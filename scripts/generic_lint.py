#!/usr/bin/env python3
"""scripts/generic_lint.py — the skill describes the METHOD for any hardware project, never the one it was learned on (owner rule).

  scripts/generic_lint.py [--skill DIR] [--terms scripts/generic_lint_terms.yaml] [FILE...]
      default files: every text file of the skill repo — SKILL.md, README.md, CHANGELOG.md, references/, templates/, scripts/, smoke/, evals/,
      workflows/, docs/ — except .git/, .venv/, __pycache__/, LICENSE (the copyright holder is a legal notice) and the term file itself.
      Exit 1 with one line per hit (file:line: <group> `<match>`), 0 when clean, 2 when the term file or a file is missing.
  scripts/generic_lint.py --selftest

Terms live in `scripts/generic_lint_terms.yaml` (regex per line, grouped: project / part / people names, project ids, machine paths, parts /
refdes, record and review ids used as citations, preset names, one design's dimensions) so a retro can extend them. A group named
`*_as_citations` applies to PROSE only (.md outside smoke/ and templates/): a fixture row in a selftest, the smoke or a template seed row uses the
D-nn / CC-nnn id scheme by design and is not a citation. CHANGELOG.md and docs/ are history: they keep measured numbers and cite the skill's own
review findings, so `design_dimensions` and `review_ids_as_citations` do not apply there — every name, id and people group does. Lines between
`<!-- worked example: begin` and `<!-- worked example: end -->` skip every group except the `*_names` and `*_ids` groups (a worked example keeps
numbers and kinds, never a name) — at most ONE such block per file (a second one is a hit); a line carrying `generic: ok` is skipped (a lint
pattern that must spell a term, a fixture).
"""
import argparse, os, re, sys, tempfile

BEGIN, END = "<!-- worked example: begin", "<!-- worked example: end -->"
SKIP_DIRS, SKIP_FILES = {".git", ".venv", "__pycache__"}, {"LICENSE", "generic_lint_terms.yaml"}
HISTORY_OK = ("design_dimensions", "review_ids_as_citations")                     # CHANGELOG.md and docs/ keep numbers and the skill's review ids


def load_terms(path):
    import yaml
    groups = yaml.safe_load(open(path, encoding="utf-8")) or {}
    return [(g, re.compile(p)) for g, pats in groups.items() for p in (pats or [])]


def default_files(skill):
    out = []
    for dp, dns, fs in os.walk(skill):
        dns[:] = sorted(x for x in dns if x not in SKIP_DIRS)
        for f in sorted(fs):
            p = os.path.join(dp, f)
            if f in SKIP_FILES or b"\0" in open(p, "rb").read(4096):          # binary files carry no prose
                continue
            out.append(p)
    return out


def lint(files, terms, skill):
    hits = []
    for f in files:
        rel = os.path.relpath(f, skill)
        if not os.path.exists(f):
            hits.append((rel, 0, "MISSING", "")); continue
        history = rel == "CHANGELOG.md" or rel.startswith("docs" + os.sep)
        blocks = 0; inside = False
        for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            if line.lstrip().startswith(BEGIN):                                # a marker opens a line; code or prose that quotes it is not a block
                blocks += 1; inside = True
                if blocks > 1:
                    hits.append((rel, n, "worked-example", "a second worked-example block (one per file)"))
            elif line.lstrip().startswith(END):
                inside = False
            if "generic: ok" in line:
                continue
            for g, rx in terms:
                if inside and not g.endswith(("_names", "_ids")):
                    continue                                                    # a worked example keeps numbers and kinds, never a name
                if history and g in HISTORY_OK:
                    continue
                if g.endswith("_as_citations") and (not rel.endswith(".md") or rel.startswith(("smoke/", "templates/"))):
                    continue                                                    # a record id is a CITATION only in prose; fixtures and template seed rows use the id scheme by design
                if g in ("parts_and_refdes", "design_dimensions") and rel.startswith(("smoke/", "evals/")):
                    continue                                                    # the smoke is a fixture project with fake codes; eval 7 is the labelled regression scenario
                m = rx.search(line)
                if m:
                    hits.append((rel, n, g, m.group(0))); break
    return hits


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_generic_")
    for sub in ("references", "scripts", "docs/reviews", ".venv"):
        os.makedirs(f"{d}/{sub}")
    open(f"{d}/scripts/generic_lint_terms.yaml", "w").write("project_names:\n  - '\\bZORBIX-9\\b'\n  - '(?i)acmecorp'\nrefdes:\n  - '\\bJ\\d{3}\\b'\n"
                                                         "design_dimensions:\n  - '\\b147 ?mm\\b'\n")
    open(f"{d}/SKILL.md", "w").write("A rule about the host connector pads.\nThe ZORBIX-9 board did X.\n<!-- worked example: begin (2026) -->\nJ401 sits at Y 136.5.\n"
                                     "The ZORBIX-9 tray.\n<!-- worked example: end -->\nJ401 again. # generic: ok\n")
    open(f"{d}/README.md", "w").write("Generic text.\n")
    open(f"{d}/references/a.md", "w").write("Acmecorp owns it.\n<!-- worked example: begin -->\nx\n<!-- worked example: end -->\n<!-- worked example: begin -->\ny\n<!-- worked example: end -->\n")
    open(f"{d}/CHANGELOG.md", "w").write("A 147 mm tray (history keeps numbers).\nThe ZORBIX-9 retro.\n")   # generic: ok (fixture)
    open(f"{d}/docs/reviews/r.md", "w").write("acmecorp in a review.\n")
    open(f"{d}/LICENSE", "w").write("Copyright Acmecorp\n"); open(f"{d}/.venv/x.md", "w").write("ZORBIX-9\n")
    terms = load_terms(f"{d}/scripts/generic_lint_terms.yaml")
    h = lint(default_files(d), terms, d); msgs = [f"{a}:{b}: {c} `{e}`" for a, b, c, e in h]
    assert any("SKILL.md:2: project_names `ZORBIX-9`" in m for m in msgs), msgs
    assert not any("SKILL.md:4" in m for m in msgs) and not any("SKILL.md:7" in m for m in msgs), ("worked-example numbers and generic: ok lines are skipped", msgs)
    assert any("SKILL.md:5: project_names `ZORBIX-9`" in m for m in msgs), ("a worked example may not carry a project name", msgs)
    assert any("references/a.md:1: project_names `Acmecorp`" in m for m in msgs) and any("worked-example" in m for m in msgs), msgs
    assert any("CHANGELOG.md:2: project_names" in m for m in msgs) and not any("CHANGELOG.md:1" in m for m in msgs), ("CHANGELOG is linted for names, keeps numbers", msgs)
    assert any("docs/reviews/r.md:1" in m for m in msgs), ("docs/ is linted", msgs)
    assert not any("LICENSE" in m or ".venv" in m or "generic_lint_terms" in m for m in msgs), ("LICENSE, .venv and the term file are skipped", msgs)
    assert len(h) == 6, msgs
    print("selftest OK (term groups, whole-repo file set, worked-example block keeps numbers not names, one block per file, history keeps numbers, generic: ok marker)")
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
