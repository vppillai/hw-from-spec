#!/usr/bin/env python3
"""scripts/scad_lint.py — lint GENERATED OpenSCAD text for statements hidden behind a `//` comment.

OpenSCAD reads everything after `//` to the end of the line as comment. A generator that emits several assignments on one line and lets a comment
land in the middle (`a = 1; // note  b = [2, 3];`) silently drops every statement after the comment — the yaml says one thing, the SCAD another,
the mesh prints without the feature and no check that reads the yaml notices. Rule: any line where an identifier the CODE uses anywhere (comments
and string literals blanked) is assigned a literal (number, string, bool, [list]) immediately closed by `;` AFTER a `//` is an error. Prose in
comments (`rim = 2.0 - 1.9 ...`, `brand = "plate" (default ...)`) never has that shape. Pair it with emitting ONE statement per line.

  scripts/scad_lint.py <file.scad>...      exit 1 with every offending line, else silent exit 0
  scripts/scad_lint.py --selftest
Importable: `from scad_lint import scad_lint; scad_lint(text)` raises RuntimeError with the lines; returns the text unchanged otherwise.
"""
import re, sys

_RX = re.compile(r'\b([A-Za-z_]\w*)\s*=\s*(?:\[[^;]*\]|-?\d[\d.eE+-]*|""|true|false)\s*;')


def scad_lint(text):
    lines = text.splitlines(); strip = lambda l: re.sub(r'"(?:[^"\\]|\\.)*"', '""', l)
    code = "\n".join(strip(l).split("//", 1)[0] for l in lines)
    names = set(re.findall(r"\b[A-Za-z_]\w*\b", code))
    bad = []
    for n, l in enumerate(lines, 1):
        c = strip(l)
        if "//" not in c or not c.split("//", 1)[0].strip():      # no comment, or a whole-line comment (nothing before it to hide)
            continue
        hits = [m.group(1) for m in _RX.finditer(c.split("//", 1)[1]) if m.group(1) in names]
        if hits:
            bad.append(f"line {n}: statement(s) for {', '.join(hits)} after `//`: {l.strip()[:140]}")
    if bad:
        raise RuntimeError("scad_lint: generated SCAD hides statements behind comments (OpenSCAD drops them):\n  " + "\n  ".join(bad))
    return text


def selftest():
    ok = 'wall = 2.0;   // rim = 2.0 - 1.9 is prose, brand = "plate" (default) too\nbrand = "plate";\nmark_pinch = [1, 2];\nx = wall + 1; // url: http://a/b\n'
    assert scad_lint(ok) == ok
    bad = 'mark_web = 1.4; mark_tip = 0;   // v3.16: webs  mark_web_clip = 4; mark_pinch = [[0, 1], [2, 3]];\nuse_clip = mark_web_clip > 0;\necho(mark_pinch);\n'
    try:
        scad_lint(bad); raise AssertionError("the hidden assignments must be rejected")
    except RuntimeError as e:
        assert "mark_web_clip, mark_pinch" in str(e) and "line 1" in str(e), e
    assert scad_lint('s = "a // b"; t = 1;\n') and scad_lint('// pure comment: x = 1;\nx = 2;\n')     # a `//` inside a string is not a comment; a whole-line comment assigns nothing
    print("selftest OK (prose in comments passes, hidden statements rejected with the names, strings and whole-line comments ignored)")


def main(argv):
    if argv[1:] == ["--selftest"]:
        selftest(); return 0
    if not argv[1:] or argv[1] in ("-h", "--help"):
        print(__doc__); return 0 if argv[1:] else 2
    rc = 0
    for p in argv[1:]:
        try:
            scad_lint(open(p, encoding="utf-8", errors="replace").read())
        except RuntimeError as e:
            print(f"{p}: {e}"); rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv))
