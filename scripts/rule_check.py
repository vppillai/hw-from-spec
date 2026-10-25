#!/usr/bin/env python3
"""scripts/rule_check.py — the core rules of a reference stay in the text, and the folklore stays out.

  scripts/rule_check.py RULES.yaml [--skill DIR] [--only GROUP,...]            # exit 1 with one line per problem, 0 when clean
  scripts/rule_check.py RULES.yaml [--skill DIR] [--only GROUP,...] --mutate   # proof: every guarded rule deleted, every banned phrase added,
                                                                               # one at a time in a scratch copy; exit 0 only when each goes red
  scripts/rule_check.py --selftest

RULES.yaml maps a group name to a list of entries: {file, section?, every_bullet?, must: [phrase], never: [phrase]}. `file` is relative
to the skill. `section` is a heading prefix (`## 23. `); the section runs to the next heading of the same or a higher level. Without it
the whole file is the section. A `must` phrase must occur in the section, and a `never` phrase must not occur anywhere in the file.
Phrases match with the whitespace collapsed, so a phrase may wrap. `every_bullet: true` also requires every top-level bullet of the
section to hold a `must` phrase: a new rule then needs its guard, and a deleted rule is always seen.
"""
import argparse, os, re, shutil, sys, tempfile

HEAD = re.compile(r"^(#+) ")


def norm(t):
    return " ".join(t.split())


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


def check_entry(skill, e):
    p = os.path.join(skill, e["file"])
    if not os.path.exists(p):
        return [f"{e['file']}: MISSING"]
    lines = open(p, encoding="utf-8").read().split("\n")
    span = section_span(lines, e.get("section"))
    if span is None:
        return [f"{e['file']}: section `{e['section']}` missing"]
    a, b = span
    sec, whole, probs = norm("\n".join(lines[a:b])), norm("\n".join(lines)), []
    probs += [f"{e['file']}: rule missing: `{m}`" for m in e.get("must", []) if norm(m) not in sec]
    probs += [f"{e['file']}: banned phrase present: `{n}`" for n in e.get("never", []) if norm(n) in whole]
    if e.get("every_bullet"):
        for s, t in blocks(lines, a, b, True):
            text = norm("\n".join(lines[s:t]))
            if not any(norm(m) in text for m in e.get("must", [])):
                probs.append(f"{e['file']}:{s + 1}: unguarded bullet (add a must phrase): `{text[:70]}`")
    return probs


def check(skill, entries):
    return [p for e in entries for p in check_entry(skill, e)]


def mutations(skill, e):
    """Yield (label, new_text): each guarded block deleted, each banned phrase inserted into the section."""
    lines = open(os.path.join(skill, e["file"]), encoding="utf-8").read().split("\n")
    a, b = section_span(lines, e.get("section"))
    paras = blocks(lines, a, b, False)                                          # bullets and plain paragraphs
    targets = blocks(lines, a, b, True) if e.get("every_bullet") else []
    for m in e.get("must", []):
        hit = [c for c in paras if norm(m) in norm("\n".join(lines[c[0]:c[1]]))]
        if not hit:                                                             # a phrase split over two blocks or in a heading
            yield f"no block holds `{m}`", "\n".join(lines); continue
        targets += [h for h in hit[:1] if h not in targets]
    for s, t in targets:
        yield f"delete {e['file']}:{s + 1} `{norm(lines[s])[:60]}`", "\n".join(lines[:s] + lines[t:])
    for n in e.get("never", []):
        yield f"insert `{n}`", "\n".join(lines[:a + 1] + [f"- {n}"] + lines[a + 1:])


def mutate(skill, entries):
    """Each mutation in a scratch copy of the one file; return the labels that stayed green."""
    green, n = [], 0
    with tempfile.TemporaryDirectory(prefix="hwfs_rule_") as d:
        for e in entries:
            dst = os.path.join(d, e["file"]); os.makedirs(os.path.dirname(dst), exist_ok=True)
            for label, text in mutations(skill, e):
                n += 1
                open(dst, "w", encoding="utf-8").write(text)
                if not check_entry(d, e):
                    green.append(label)
            shutil.copy(os.path.join(skill, e["file"]), dst)
    return n, green


def load(path, only):
    import yaml
    groups = yaml.safe_load(open(path, encoding="utf-8")) or {}
    if only:
        missing = set(only) - set(groups)
        if missing:
            raise SystemExit(f"rule_check: unknown group(s) {sorted(missing)}")
        groups = {k: v for k, v in groups.items() if k in only}
    return [e for v in groups.values() for e in v]


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_rule_st_")
    os.makedirs(f"{d}/references")
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds\n  across two lines.\n- Rule two holds.\n\n## 2. B\n- Free text.\n")
    E = [{"file": "references/x.md", "section": "## 1. ", "every_bullet": True, "must": ["one holds across", "Rule two"], "never": ["folklore"]}]
    assert check(d, E) == [], check(d, E)
    n, green = mutate(d, E); assert n == 3 and green == [], (n, green)
    open(f"{d}/references/x.md", "a").write("- folklore here\n")
    assert any("banned" in p for p in check(d, E))
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds\n  across two lines.\n- Rule two holds.\n- Rule three.\n## 2. B\n")
    assert any("unguarded" in p for p in check(d, E)), check(d, E)
    open(f"{d}/references/x.md", "w").write("# x\n## 1. A\n- Rule one holds across.\n- Rule two holds.\n- Rule two again.\n")
    E2 = [{"file": "references/x.md", "section": "## 1. ", "must": ["one holds across", "Rule two"]}]
    n, green = mutate(d, E2); assert green == ["delete references/x.md:4 `- Rule two holds.`"], green   # a duplicated rule survives one deletion
    open(f"{d}/SKILL.md", "w").write("Para one.\nstill one.\n\nPara two has the norm.\n")
    n, green = mutate(d, [{"file": "SKILL.md", "must": ["has the norm"]}]); assert n == 1 and green == [], green
    assert check(d, [{"file": "references/x.md", "section": "## 9. "}]) and check(d, [{"file": "nope.md"}])
    shutil.rmtree(d)
    print("selftest OK (must phrases across a wrap, banned phrases, unguarded bullets, mutation proof incl. a duplicated rule, paragraphs)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("rules", nargs="?"); ap.add_argument("--skill", default=os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    ap.add_argument("--only"); ap.add_argument("--mutate", action="store_true"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if not a.rules:
        ap.error("RULES.yaml is required")
    entries = load(a.rules, a.only.split(",") if a.only else None)
    probs = check(a.skill, entries)
    for p in probs:
        print(p)
    if probs or not a.mutate:
        print(f"rule_check: {len(probs)} problem(s) in {len(entries)} entr{'y' if len(entries) == 1 else 'ies'}")
        return 1 if probs else 0
    n, green = mutate(a.skill, entries)
    for g in green:
        print(f"STAYED GREEN: {g}")
    print(f"rule_check --mutate: {n - len(green)} of {n} mutation(s) went red")
    return 1 if green else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
