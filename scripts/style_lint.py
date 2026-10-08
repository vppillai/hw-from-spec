#!/usr/bin/env python3
"""scripts/style_lint.py — the skill's prose follows references/writing-style.md (Google developer style, ASD-STE100 precision, Zinsser).

  scripts/style_lint.py [--skill DIR] [--max-words N] [--report] [FILE...]   # default files: SKILL.md, README.md, references/*.md, templates/**/*.md
  scripts/style_lint.py --project ROOT [--max-words N] [--report]            # a project's own texts: every README.md, 90-log/*.md, 60-orders/**/*.md,
                                                                             #   70-release/**/*.md, 50-kits/**/*.md (the skill's output follows the same rules)
  scripts/style_lint.py --selftest
Exit 1 with one line per hit, 0 when clean, 2 when a file is missing. Hard rules (hits):
  1. clutter and Latin: please, very, simply, in order to, utilize, leverage, easily, obviously, of course, note that, etc., e.g., i.e., via,
     and/or, basically, actually, in terms of (Google: no Latin abbreviations, no filler; Zinsser: cut clutter).
  2. sentence length: a prose sentence longer than --max-words (default 40; the target in writing-style.md is 20 for an instruction and 25 for a
     description; the gate tightens as the text improves). Code fences, tables, headings and front matter are skipped; a bullet is prose.
     Hard-wrapped lines are joined into one paragraph before the split; a hit names the line where the sentence starts.
  3. a line may carry `<!-- style: ok -->` (a quoted owner sentence, a command, a list of file names). On a wrapped sentence, the
     marker on any of its lines exempts the sentence.
--report prints per-file counts (sentences, over 25, over the cap, average words, passive-voice hits, "will", em-dashes) without failing.
"""
import argparse, glob, os, re, sys, tempfile

BAN = [(r"\bplease\b", "please"), (r"\bvery\b", "very"), (r"\bsimply\b", "simply"), (r"\bin order to\b", "in order to"), (r"\butili[sz]e", "utilize"),
       (r"\bleverag", "leverage"), (r"\beasily\b", "easily"), (r"\bobviously\b", "obviously"), (r"\bof course\b", "of course"), (r"\bnote that\b", "note that"),
       (r"\betc\.", "etc."), (r"\be\.g\.", "e.g."), (r"\bi\.e\.", "i.e."), (r"(?<!the )(?<!a )(?<!per )(?<!each )(?<!every )(?<!one )(?<!unconnected )(?<!no )(?<!track/)(?<!/)(?<!-)(?<!fan-out )(?<!power )(?<!at )\bvia\b(?![-\s/](?:in-pad|in\b|covering|treatment|plugg|plug|tent|count|work|fill|stitch|hole|size|drill|census|barrel|wall|pad|stub|total|layer|junction|keep|site|ring|whose|\d|/|or\b|PTH))", "via"), (r"\band/or\b", "and/or"), (r"\bbasically\b", "basically"),
       (r"\bactually\b", "actually"), (r"\bin terms of\b", "in terms of")]
PASSIVE = re.compile(r"\b(is|are|was|were|be|been|being)\s+(\w+ed|\w+en)\b")
SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z`(*\"])")


def default_files(skill):
    out = [os.path.join(skill, "SKILL.md"), os.path.join(skill, "README.md")] + sorted(glob.glob(os.path.join(skill, "references", "*.md")))
    out += sorted(glob.glob(os.path.join(skill, "templates", "**", "*.md"), recursive=True))
    return out


def project_files(root):
    pats = ["**/README.md", "90-log/*.md", "60-orders/**/*.md", "70-release/**/*.md", "50-kits/**/*.md"]
    out = set()
    for p in pats:
        out |= {f for f in glob.glob(os.path.join(root, p), recursive=True) if "/build/" not in f and "/.git/" not in f and "/vendor/" not in f}
    return sorted(out)


def prose_lines(text):
    """(line number, line) for prose only: no code fences, tables, headings, front matter, blank lines."""
    fence = False; front = False
    for n, line in enumerate(text.split("\n"), 1):
        s = line.strip()
        if n == 1 and s == "---":
            front = True; continue
        if front:
            if s == "---":
                front = False
            continue
        if s.startswith("```"):
            fence = not fence; continue
        if fence or not s or s.startswith("|") or s.startswith("#") or s.startswith("<!--"):
            continue
        yield n, line


LIST = re.compile(r"\s*(?:[-*+]|\d+[.)])\s")


def paragraphs(text):
    """[(line numbers, joined text)]: hard-wrapped prose lines joined into one paragraph. A non-prose line (blank, fence, table, heading,
    comment, front matter) or a list-item start ends a paragraph. A line joins the one before when it is indented two spaces or more, or
    starts with anything but a capital letter (a lowercase word, a backtick, a bracket); an unindented capitalised line starts a new one."""
    out, last = [], None
    for n, line in prose_lines(text):
        joins = last == n - 1 and out and not LIST.match(line) and (line.startswith("  ") or not line[:1].isupper())
        if joins:
            out[-1][0].append(n); out[-1][1].append(line.strip())
        else:
            out.append(([n], [line.strip()]))
        last = n
    return [(ns, parts) for ns, parts in out]


def sentences(line):
    for s in SPLIT.split(line.strip()):
        words = re.findall(r"[\w'`/.\-]+", s)
        if len(words) >= 3:
            yield len(words), s


def para_sentences(ns, parts):
    """(first line, lines spanned, words, sentence) for each sentence of a joined paragraph."""
    text = " ".join(parts); starts = []; off = 0
    for p in parts:
        starts.append(off); off += len(p) + 1
    line_at = lambda o: ns[max(i for i, st in enumerate(starts) if st <= o)]
    pos = 0
    for chunk in SPLIT.split(text):
        b = text.index(chunk, pos); e = b + len(chunk); pos = e
        words = re.findall(r"[\w'`/.\-]+", chunk)
        if len(words) >= 3:
            a, z = line_at(b), line_at(max(b, e - 1))
            yield a, range(a, z + 1), len(words), chunk


def lint(files, skill, max_words=40):
    hits, stats = [], []
    for f in files:
        rel = os.path.relpath(f, skill)
        if not os.path.exists(f):
            hits.append((rel, 0, "MISSING")); continue
        text = open(f, encoding="utf-8").read()
        n_s = over25 = over = total = passive = will = dash = 0
        okl = set()
        for n, line in prose_lines(text):
            ok = "<!-- style: ok -->" in line
            if ok:
                okl.add(n)
            passive += len(PASSIVE.findall(line)); will += len(re.findall(r"\bwill\b", line)); dash += line.count("—")
            if not ok:
                for pat, name in BAN:
                    if re.search(pat, line, re.I):
                        hits.append((rel, n, f"clutter `{name}`")); break
        for ns, parts in paragraphs(text):                      # sentence length is measured on joined paragraphs, not physical lines
            for n, span, w, s in para_sentences(ns, parts):
                n_s += 1; total += w; over25 += w > 25
                if w > max_words:
                    over += 1
                    if not okl.intersection(span):
                        hits.append((rel, n, f"{w} words in one sentence (cap {max_words}): {s[:70]}…"))
        stats.append((rel, n_s, over25, over, round(total / max(n_s, 1), 1), passive, will, dash))
    return hits, stats


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_style_"); os.makedirs(f"{d}/references"); os.makedirs(f"{d}/templates")
    open(f"{d}/SKILL.md", "w").write("---\nversion: 0.1.0\n---\nRun the gate. Please read the log. <!-- style: ok -->\nVia the API, read the stock.\n```\nplease do not lint code e.g. this\n```\n| a | please in a table |\n")
    long = "Word " + " ".join(["word"] * 44) + "."
    open(f"{d}/README.md", "w").write(f"# x\nShort line.\n{long}\n")
    open(f"{d}/references/a.md", "w").write("The census is a FAIL gate. The vendor reads the file. A via-in-pad row and the via covering option pass; so does a via per pad.\n")
    w92 = " ".join(["word"] * 92).split(" ")
    wrap = "Start " + " ".join(w92[:30]) + "\n  " + " ".join(w92[30:60]) + "\nand " + " ".join(w92[63:]) + " end.\n"   # 3 lines, 92 words
    w20 = "Run the gate on the board file\n  and read every hit it prints\nbefore you commit the change set.\n"           # 3 lines, 20 words
    okw = "Keep " + " ".join(["word"] * 30) + "\n  " + " ".join(["word"] * 30) + " end. <!-- style: ok -->\n"            # marker on the 2nd line
    open(f"{d}/references/w.md", "w").write(f"# w\n{wrap}\n{w20}\n{okw}\n- A list item.\n- Another item.\n")
    hits, stats = lint(default_files(d), d)
    msgs = [f"{a}:{b}: {c}" for a, b, c in hits]
    assert any("SKILL.md:5" in m and "via" in m for m in msgs), msgs                      # clutter outside a marked line
    assert not any("SKILL.md:4" in m for m in msgs), msgs                                   # style: ok marker
    assert not any("SKILL.md:7" in m or "SKILL.md:9" in m for m in msgs), msgs              # code fence and table skipped
    assert any("README.md:3" in m and "45 words" in m for m in msgs), msgs                  # long sentence
    assert any("references/w.md:2: 92 words" in m for m in msgs), msgs                     # a 3-line 92-word sentence hits at its first line
    assert not any("references/w.md:6" in m or "references/w.md:10" in m for m in msgs), msgs  # wrapped 20 words; style: ok on a later line
    assert not any("references/a.md" in m for m in msgs) and len(hits) == 3, msgs
    st = {s[0]: s for s in stats}; assert st["references/a.md"][1] == 3 and st["README.md"][3] == 1, stats
    assert st["references/w.md"][1] == 5 and st["references/w.md"][3] == 2, stats           # list items stay separate sentences
    cwd = os.getcwd(); os.chdir(d)
    try:
        import io, contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = main(["README.md"])                                                        # a relative file argument resolves against the working directory, not the skill
        assert rc == 1 and "README.md:3" in buf.getvalue() and "MISSING" not in buf.getvalue(), buf.getvalue()
    finally:
        os.chdir(cwd)
    print("selftest OK (clutter words, the PCB noun via exempt, style: ok marker, fences / tables / front matter skipped, sentence cap on wrapped paragraphs, per-file stats, relative file args)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--skill", default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    ap.add_argument("files", nargs="*"); ap.add_argument("--selftest", action="store_true"); ap.add_argument("--max-words", type=int, default=40); ap.add_argument("--report", action="store_true")
    ap.add_argument("--project", help="lint a project's own texts (READMEs, 90-log, 60-orders, 70-release, 50-kits) instead of the skill")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()
    base = a.project or a.skill
    files = [os.path.abspath(f) for f in a.files] or (project_files(a.project) if a.project else default_files(a.skill))
    hits, stats = lint(files, base if not a.files else os.getcwd(), a.max_words)
    if a.report:
        print("file | sentences | >25 | >cap | avg words | passive | will | em-dashes")
        for s in sorted(stats, key=lambda s: -s[2]):
            print(" | ".join(str(x) for x in s))
        t = [sum(s[i] for s in stats) for i in (1, 2, 3, 5, 6, 7)]
        print(f"TOTAL sentences {t[0]}, >25 {t[1]}, >cap {t[2]}, passive {t[3]}, will {t[4]}, em-dashes {t[5]}")
        return 0
    for rel, n, msg in hits:
        print(f"{rel}:{n}: {msg}")
    missing = any(m == "MISSING" for _, _, m in hits)
    print(f"style_lint: {len(hits)} hit(s) in {len(files)} file(s)")
    return 2 if missing else (1 if hits else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
