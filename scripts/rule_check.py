#!/usr/bin/env python3
"""scripts/rule_check.py — the core rules of a reference stay in the text, and the folklore stays out.

  scripts/rule_check.py RULES.yaml [--skill DIR] [--only GROUP,...]            # exit 1 with one line per problem, 0 when clean
  scripts/rule_check.py RULES.yaml [--skill DIR] [--only GROUP,...] --mutate   # proof: mutate each guarded unit in a scratch copy,
                                                                               # one at a time; exit 0 only when each one goes red
  scripts/rule_check.py --sentences FILE SECTION   # print the sentences of a section as yaml list items (to refresh an every_sentence guard)
  scripts/rule_check.py --selftest

RULES.yaml maps a group name to a list of entries: {file, section?, every_bullet?, every_sentence?, must: [phrase], never: [phrase],
never_re: [regex]}. `file` is relative to the skill. `section` is a heading prefix (`## 23. `); the section runs to the next heading of
the same or a higher level. Without it the whole file is the section. A `must` phrase must occur in the section. A `never` phrase, or
a `never_re` regex, must not occur anywhere in the file. Phrases match with the whitespace collapsed, so a phrase may wrap.
- `every_bullet: true`: every top-level bullet of the section holds a `must` phrase.
- `every_sentence: true`: every sentence of the section (intro paragraphs included) holds a `must` phrase. With the whole sentences
  as the must list (`--sentences`), any deletion, rewording or added sentence goes red; an edit of the section is a deliberate edit
  of the guard file too.
`--mutate` deletes each guarded block (every_bullet) or each sentence (every_sentence), or the block that holds each must phrase. In
every_sentence mode it also flips one verdict word per sentence (PASS / FAIL / INCONCLUSIVE, never / always, not). It inserts each
banned phrase. It reports the mutations that stayed green. It proves only what the guards cover: text outside a guarded section,
and a meaning kept under new words outside an every_sentence section, are not seen.
"""
import argparse, os, re, shutil, sys, tempfile

HEAD = re.compile(r"^(#+) ")
SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(`\"*−-])")
SWAPS = [(r"\bINCONCLUSIVE\b", "PASS"), (r"\bFAIL\b", "PASS"), (r"\bPASS\b", "FAIL"), (r"\bNever\b", "Always"), (r"\bnever\b", "always"),
         (r"\bnot\b ", ""), (r"\bcannot\b", "can"), (r"\bonly\b ", "")]


def norm(t):
    return " ".join(t.split())


def sentences(text):
    return [x for x in SPLIT.split(norm(text)) if x]


def section_span(lines, prefix):
    """(start, end) line indexes of the section, or None. No prefix = the whole file."""
    if not prefix:
        return 0, len(lines)
    for i, l in enumerate(lines):
        if l.startswith(prefix):
            lvl = len(HEAD.match(l).group(1)) if HEAD.match(l) else 99
            for j in range(i + 1, len(lines)):
                m = HEAD.match(lines[j])
                if m and len(m.group(1)) <= lvl:
                    return i, j
            return i, len(lines)
    return None


def blocks(lines, a, b, bullets_only):
    """Top-level bullets (a '- ' line and its indented continuation) or, without bullets_only, also plain paragraphs: [(start, end)]."""
    out, i = [], a
    while i < b:
        l = lines[i]
        if l.startswith("- ") or (not bullets_only and l.strip() and not HEAD.match(l)):
            j = i + 1
            while j < b and lines[j].strip() and not lines[j].startswith("- ") and not HEAD.match(lines[j]) and (lines[j].startswith(" ") or not l.startswith("- ")):
                j += 1
            out.append((i, j)); i = j
        else:
            i += 1
    return out


def block_text(lines, s, t):
    txt = norm("\n".join(lines[s:t]))
    return txt[2:] if txt.startswith("- ") else txt


def check_text(text, e):
    lines = text.split("\n")
    span = section_span(lines, e.get("section"))
    if span is None:
        return [f"{e['file']}: section `{e['section']}` missing"]
    a, b = span
    sec, whole, probs = norm("\n".join(lines[a:b])), norm(text), []
    probs += [f"{e['file']}: rule missing: `{m}`" for m in e.get("must", []) if norm(m) not in sec]
    probs += [f"{e['file']}: banned phrase present: `{n}`" for n in e.get("never", []) if norm(n) in whole]
    probs += [f"{e['file']}: banned pattern present: `{r}`" for r in e.get("never_re", []) if re.search(r, whole)]
    must = [norm(m) for m in e.get("must", [])]
    if e.get("every_bullet"):
        for s, t in blocks(lines, a, b, True):
            if not any(m in block_text(lines, s, t) for m in must):
                probs.append(f"{e['file']}:{s + 1}: unguarded bullet (add a must phrase): `{block_text(lines, s, t)[:70]}`")
    if e.get("every_sentence"):
        for s, t in blocks(lines, a + (1 if e.get("section") else 0), b, False):
            for x in sentences(block_text(lines, s, t)):
                if not any(m in x for m in must):
                    probs.append(f"{e['file']}:{s + 1}: unguarded sentence (add a must phrase): `{x[:70]}`")
    return probs


def check_entry(skill, e):
    p = os.path.join(skill, e["file"])
    if not os.path.exists(p):
        return [f"{e['file']}: MISSING"]
    return check_text(open(p, encoding="utf-8").read(), e)


def check(skill, entries):
    return [p for e in entries for p in check_entry(skill, e)]


def mutations(text, e):
    """Yield (label, new_text) for one entry."""
    lines = text.split("\n")
    a, b = section_span(lines, e.get("section"))
    for n in e.get("never", []):
        yield f"insert `{n}`", "\n".join(lines[:a + 1] + [f"- {n}"] + lines[a + 1:])
    if e.get("every_sentence"):
        body = blocks(lines, a + (1 if e.get("section") else 0), b, False)
        units = [(i, ("- " if lines[s].startswith("- ") else ""), sentences(block_text(lines, s, t))) for i, (s, t) in enumerate(body)]

        def rebuild(bi, si, new):
            out = []
            for i, pre, ss in units:
                ss = list(ss)
                if i == bi:
                    ss[si:si + 1] = [new] if new else []
                if ss:
                    out.append(pre + " ".join(ss))
            return "\n".join(lines[:body[0][0]] + out + lines[body[-1][1]:])
        yield "flatten only (control)", rebuild(-1, 0, None)
        for i, pre, ss in units:
            for k, x in enumerate(ss):
                yield f"delete sentence {e['file']}: `{x[:60]}`", rebuild(i, k, None)
                for rx, rep in SWAPS:
                    if re.search(rx, x):
                        yield f"flip `{rx}` in {e['file']}: `{x[:50]}`", rebuild(i, k, re.sub(rx, rep, x, count=1))
                        break
        return
    paras = blocks(lines, a, b, False)
    targets = blocks(lines, a, b, True) if e.get("every_bullet") else []
    for m in e.get("must", []):
        hit = [c for c in paras if norm(m) in norm("\n".join(lines[c[0]:c[1]]))]
        if not hit:
            yield f"no block holds `{m}`", text; continue
        targets += [h for h in hit[:1] if h not in targets]
    for s, t in targets:
        yield f"delete {e['file']}:{s + 1} `{norm(lines[s])[:60]}`", "\n".join(lines[:s] + lines[t:])


def mutate(skill, entries):
    """Each mutation checked on its text; return (count, labels that stayed green, problems of the controls)."""
    green, bad_control, n = [], [], 0
    for e in entries:
        text = open(os.path.join(skill, e["file"]), encoding="utf-8").read()
        for label, new in mutations(text, e):
            probs = check_text(new, e)
            if label.startswith("flatten"):
                if probs:
                    bad_control.append(f"{e['file']}: the flattened copy is not green: {probs[:2]}")
                continue
            n += 1
            if not probs:
                green.append(label)
    return n, green, bad_control


def load(path, only):
    import yaml
    groups = yaml.safe_load(open(path, encoding="utf-8")) or {}
    if only:
        missing = set(only) - set(groups)
        if missing:
            raise SystemExit(f"rule_check: unknown group(s) {sorted(missing)}")
        groups = {k: v for k, v in groups.items() if k in only}
    return [e for v in groups.values() for e in v]


def print_sentences(path, prefix):
    lines = open(path, encoding="utf-8").read().split("\n")
    a, b = section_span(lines, prefix)
    for s, t in blocks(lines, a + (1 if prefix else 0), b, False):
        for x in sentences(block_text(lines, s, t)):
            print("      - " + ("'" + x.replace("'", "''") + "'"))


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_rule_st_")
    os.makedirs(f"{d}/references")
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds\n  across two lines.\n- Rule two holds.\n\n## 2. B\n- Free text.\n")
    E = [{"file": "references/x.md", "section": "## 1. ", "every_bullet": True, "must": ["one holds across", "Rule two"], "never": ["folklore"]}]
    assert check(d, E) == [], check(d, E)
    n, green, bad = mutate(d, E); assert n == 3 and green == [] and not bad, (n, green, bad)
    open(f"{d}/references/x.md", "a").write("- folklore here\n")
    assert any("banned" in p for p in check(d, E))
    assert any("banned pattern" in p for p in check(d, [{"file": "references/x.md", "never_re": [r"(?i)folk\s*lore"]}]))
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds\n  across two lines.\n- Rule two holds.\n- Rule three.\n## 2. B\n")
    assert any("unguarded bullet" in p for p in check(d, E)), check(d, E)
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds across.\n- Rule two holds.\n- Rule two again.\n")
    E2 = [{"file": "references/x.md", "section": "## 1. ", "must": ["one holds across", "Rule two"]}]
    n, green, _ = mutate(d, E2); assert green == ["delete references/x.md:4 `- Rule two holds.`"], green   # a duplicated rule survives one deletion
    # every_sentence: the intro paragraph and each sentence are guarded; a deletion, a verdict flip and an added sentence go red
    open(f"{d}/references/y.md", "w").write("# y\n## 3. C\nIntro says why.\n- A bad window is INCONCLUSIVE. Never average\n  the ratios.\n- Keep it.\n## 4. D\n")
    E3 = [{"file": "references/y.md", "section": "## 3. ", "every_sentence": True,
           "must": ["Intro says why.", "A bad window is INCONCLUSIVE.", "Never average the ratios.", "Keep it."]}]
    assert check(d, E3) == [], check(d, E3)
    n, green, bad = mutate(d, E3); assert n == 6 and green == [] and not bad, (n, green, bad)   # 4 deletions + 2 flips
    open(f"{d}/references/y.md", "a").write("")
    t = open(f"{d}/references/y.md").read().replace("- Keep it.", "- Keep it. Use short windows.")
    assert any("unguarded sentence" in p for p in check_text(t, E3[0]))
    t = open(f"{d}/references/y.md").read().replace("is INCONCLUSIVE", "is PASS")
    assert check_text(t, E3[0]), "a reversed verdict word goes red"
    E4 = [{"file": "references/y.md", "section": "## 3. ", "every_sentence": True, "must": ["window", "Never average", "Keep"]}]
    assert any("Intro" in p for p in check(d, E4)), "the intro paragraph is guarded too"
    open(f"{d}/SKILL.md", "w").write("Para one.\nstill one.\n\nPara two has the norm.\n")
    n, green, _ = mutate(d, [{"file": "SKILL.md", "must": ["has the norm"]}]); assert n == 1 and green == [], green
    assert check(d, [{"file": "references/x.md", "section": "## 9. "}]) and check(d, [{"file": "nope.md"}])
    assert sentences("Rate 1.5 is fine. Then 53.125 GBd. (2026-10): ok. A step.") == ["Rate 1.5 is fine.", "Then 53.125 GBd.", "(2026-10): ok.", "A step."]
    shutil.rmtree(d)
    print("selftest OK (must phrases across a wrap, banned phrases and patterns, unguarded bullets and sentences, the intro guarded, "
          "mutation proof incl. a duplicated rule, sentence deletions and verdict flips, paragraphs)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("rules", nargs="?"); ap.add_argument("--skill", default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    ap.add_argument("--only"); ap.add_argument("--mutate", action="store_true"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--sentences", nargs=2, metavar=("FILE", "SECTION"))
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.sentences:
        print_sentences(*a.sentences); return 0
    if not a.rules:
        ap.error("RULES.yaml is required")
    entries = load(a.rules, a.only.split(",") if a.only else None)
    probs = check(a.skill, entries)
    for p in probs:
        print(p)
    if probs or not a.mutate:
        print(f"rule_check: {len(probs)} problem(s) in {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
        return 1 if probs else 0
    n, green, bad = mutate(a.skill, entries)
    for g in green:
        print(f"STAYED GREEN: {g}")
    for b in bad:
        print(f"CONTROL: {b}")
    print(f"rule_check --mutate: {n - len(green)} of {n} mutation(s) went red")
    return 1 if green or bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
