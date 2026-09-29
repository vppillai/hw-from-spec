#!/usr/bin/env python3
"""scripts/skill_retro.py — the self-improvement step: what did this project learn that the skill does not carry yet? (SKILL.md §13)

  scripts/skill_retro.py [--project DIR|project.yaml] [--skill SKILL_DIR] [--out DIR] [--since YYYY-MM-DD] [--threshold 0.5]
      Reads the project's docs/governance/LEARNINGS_LOG.md (dated `- YYYY-MM-DD [domain] …` entries) and DECISIONS.md (D / CC rows), classifies
      every entry against the skill's SKILL.md + references/*.md sections by keyword overlap (rare tokens weigh more): CARRIED (the best section
      shares >= --threshold of the entry's distinctive tokens), PARTIAL (>= half of that), NEW. Marks entries whose text names a failure that cost
      a round (cracked / wrong / premature / stale / reorder …). Compares the project's recorded skill version (`skill.version` or `skill_version`
      in project.yaml) with the skill's SKILL.md version. Writes DIR/<project>_<date>.md (default: <skill>/docs/retro/) with: counts, the NEW and
      PARTIAL tables (entry, best section, score), a CHANGELOG entry draft, one reference patch stub per target file (bullets to append), an eval
      stub per costly NEW entry, and the owner decision topics the kickoff questionnaire does not ask yet. Read-only on the project; exit 0
      (a report), 2 when an input is missing.
  scripts/skill_retro.py --selftest
      a fixture project + fixture skill in a temp dir: one carried, one new, one costly entry; version drift; the report file and its sections.

The classifier is a keyword matcher, not an oracle: it lists candidates for a human (or the next agent) to fold into the references — the retro
report is the input to the skill's next CHANGELOG entry, not the entry itself.
"""
import argparse, datetime, json, math, os, re, sys

STOP = set("""that this with from into when then than they them were what which where while will would could should about after before
because between under over every each other only also just more most some such very into onto upon their there these those been being have has
had does done doing make made makes making take took taken give given gave need needs needed must never always still even much many both same
another again here whose ones once first last next like well across against without within through during since until per via not and but for
the its our your one two three four five six seven eight nine zero mm cm the a an of to in on at by or is it as be we you he she do go up so no
yes non any all out off way row rows line lines file files project skill worked example source record records read write written""".split())
COSTLY = re.compile(r"crack|failed|failure|wrong|premature|false|lost|stale|re-?order|reprint|broke|silent|invalid|wasted|would have|went out|twice|"
                    r"three times|nobody|missed|blind spot|unprintable|wrecked|orphan|segfault|corrupt", re.I)
ENTRY = re.compile(r"^\s*-\s+\**(\d{4}-\d{2}-\d{2})\**\s*(?:\[([^\]]+)\])?\**\s*(.*)$")


def tokens(text):
    out = set()
    for w in re.findall(r"[A-Za-z][A-Za-z0-9_./-]{2,}|\d+\.\d+", text):
        w = w.strip("./-").lower()
        if len(w) >= 3 and w not in STOP and not re.fullmatch(r"(cc|d|b|r|t|s|k|v)-?\d+[a-z]?", w):
            out.add(w)
    return out


def read_entries(path, since=None):
    """Dated learnings: `- YYYY-MM-DD [domain] text …` (continuation lines joined) -> [{date, domain, text, line}]."""
    entries, cur = [], None
    for n, line in enumerate(open(path, encoding="utf-8"), 1):
        m = ENTRY.match(line)
        if m:
            if cur:
                entries.append(cur)
            cur = dict(date=m.group(1), domain=(m.group(2) or "").strip(), text=m.group(3).strip(), line=n)
        elif cur and line.strip() and not line.startswith("#") and not line.lstrip().startswith("- "):
            cur["text"] += " " + line.strip()
        elif cur and (not line.strip() or line.startswith("#")):
            entries.append(cur); cur = None
    if cur:
        entries.append(cur)
    return [e for e in entries if not since or e["date"] >= since]


def read_decisions(path, owner_prefix="D"):
    """Table rows -> [{id, date, status, topic, text, owner}] (6-cell decisions table; a backslash-escaped pipe is content)."""
    rows = []
    for line in open(path, encoding="utf-8"):
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in re.split(r"(?<!\\)\|", line.strip())[1:-1]]
        if len(cells) < 5 or cells[0].startswith("---") or cells[0].lower() == "id":
            continue
        m = re.search(r"\b([A-Z]+)-(\d+[a-z]?)\b", cells[0])
        if not m:
            continue
        rows.append(dict(id=f"{m.group(1)}-{m.group(2)}", date=cells[1], status=cells[2], topic=cells[3], text=" ".join(cells[4:]),
                         owner=m.group(1) == owner_prefix))
    return rows


def index_skill(skill):
    """SKILL.md + references/*.md split by heading -> [{file, heading, tokens}], plus idf per token."""
    sections = []
    files = [os.path.join(skill, "SKILL.md")] + sorted(os.path.join(skill, "references", f) for f in os.listdir(os.path.join(skill, "references")) if f.endswith(".md"))
    for f in files:
        heading, buf = "(top)", []
        for line in open(f, encoding="utf-8"):
            if line.startswith("#") or re.match(r"^\*\*[A-H]\d+ ", line):          # headings, and the questionnaire's bold question markers
                if buf:
                    sections.append(dict(file=os.path.relpath(f, skill), heading=heading, tokens=tokens(" ".join(buf))))
                heading, buf = (line.strip("# \n") if line.startswith("#") else line.strip("*\n").split(".**")[0].split("**")[0]), []
            else:
                buf.append(line)
        if buf:
            sections.append(dict(file=os.path.relpath(f, skill), heading=heading, tokens=tokens(" ".join(buf))))
    df = {}
    for s in sections:
        for t in s["tokens"]:
            df[t] = df.get(t, 0) + 1
    n = max(1, len(sections))
    idf = {t: math.log(1 + n / c) for t, c in df.items()}
    return sections, idf


def classify(text, sections, idf, threshold):
    """-> (class, coverage, best section): coverage = idf-weighted share of the entry's distinctive tokens found in the best section."""
    tk = tokens(text)
    if not tk:
        return "NEW", 0.0, None
    unknown = math.log(1 + len(sections))                       # a token no section has: the strongest evidence of novelty
    w = {t: idf.get(t, unknown) for t in tk}
    med = sorted(w.values())[len(w) // 2]
    distinct = {t: x for t, x in w.items() if x >= med} or w
    total = sum(distinct.values())
    best, best_cov = None, 0.0
    for s in sections:
        cov = sum(x for t, x in distinct.items() if t in s["tokens"]) / total
        if cov > best_cov:
            best, best_cov = s, cov
    cls = "CARRIED" if best_cov >= threshold else ("PARTIAL" if best_cov >= threshold / 2 else "NEW")
    return cls, round(best_cov, 2), best


def skill_version(skill):
    for line in open(os.path.join(skill, "SKILL.md"), encoding="utf-8"):
        m = re.match(r"^version:\s*([0-9][0-9.]*)", line)
        if m:
            return m.group(1)
    return "?"


def project_version(root):
    p = os.path.join(root, "project.yaml")
    if not os.path.exists(p):
        return None
    try:
        import yaml
        cfg = yaml.safe_load(open(p, encoding="utf-8")) or {}
    except Exception:  # noqa: BLE001 — a project.yaml the reader cannot parse is reported, not fatal
        return None
    return str((cfg.get("skill") or {}).get("version") or cfg.get("skill_version") or "") or None


def target_file(entry, best):
    """Where a NEW learning belongs: the best-matching reference when it exists, else by domain tag, else pitfalls."""
    if best and best["file"] != "SKILL.md" and best["heading"] != "(top)":
        return best["file"]
    d = entry.get("domain", "").lower()
    for key, f in (("dfm", "references/dfm-printed-enclosure.md"), ("mjf", "references/dfm-printed-enclosure.md"), ("fdm", "references/dfm-printed-enclosure.md"),
                   ("case", "references/case-pipeline.md"), ("mesh", "references/case-pipeline.md"), ("fea", "references/fea-stage.md"),
                   ("layout", "references/pcb-layout-dfm.md"), ("silk", "references/pcb-layout-dfm.md"), ("drc", "references/pcb-layout-dfm.md"),
                   ("jlc", "references/fab-dfm.md"), ("fab", "references/fab-dfm.md"), ("parts", "references/part-verification.md"),
                   ("sourcing", "references/part-verification.md"), ("agents", "references/agent-ops.md"), ("git", "references/agent-ops.md"),
                   ("process", "references/release-and-cut.md"), ("software", "references/software-track.md"), ("tooling", "references/pitfalls.md")):
        if key in d:
            return f
    return "references/pitfalls.md"


def generalise(text):
    """Move the evidence pointer (' — CC-nnn', ' — D-nn', trailing references) to the end in italics; keep the mechanism."""
    parts = re.split(r"\s+—\s+(?=(?:CC|D|B)-\d)", text, maxsplit=1)
    return parts[0].strip() if len(parts) == 1 else f"{parts[0].strip()} *(evidence: {parts[1].strip()})*"


def build_report(project, root, skill, entries, decisions, sections, idf, threshold, today):
    classified = []
    for e in entries:
        cls, cov, best = classify(e["text"], sections, idf, threshold)
        classified.append(dict(e, cls=cls, cov=cov, best=best, costly=bool(COSTLY.search(e["text"]))))
    new = [c for c in classified if c["cls"] == "NEW"]; partial = [c for c in classified if c["cls"] == "PARTIAL"]
    carried = [c for c in classified if c["cls"] == "CARRIED"]
    # owner decision topics vs the kickoff questionnaire
    q_path = os.path.join(skill, "references", "kickoff-questionnaire.md")
    q_sections = [s for s in sections if s["file"].endswith("kickoff-questionnaire.md")]
    unasked = []
    for d in decisions:
        if not d["owner"]:
            continue
        cls, cov, best = classify(d["topic"], q_sections or sections, idf, threshold)      # the short topic cell; the text is project narrative
        if cls == "NEW":
            unasked.append(dict(d, cov=cov, best=best))
    pv, sv = project_version(root), skill_version(skill)
    L = [f"# Retro — {project} → hw-from-spec ({today})", "",
         f"Project `{root}`: {len(entries)} dated learnings, {len(decisions)} decision rows ({sum(d['owner'] for d in decisions)} owner rows). "
         f"Skill `{skill}` at SKILL.md version **{sv}**; the project recorded skill version **{pv or 'none (add `skill: {version: …}` to project.yaml)'}**"
         + (" — **drift: the project ran an older skill; every NEW entry below may already be carried by a later version**" if pv and pv != sv else "") + ".",
         f"Classifier: keyword overlap against {len(sections)} sections (threshold {threshold}); a human folds the candidates — this report is the input to the next CHANGELOG entry, not the entry itself.", "",
         "## 1. Counts", "", "| CARRIED | PARTIAL | NEW | NEW and costly (a round, an order, a wrong result) |", "|---|---|---|---|",
         f"| {len(carried)} | {len(partial)} | {len(new)} | {sum(c['costly'] for c in new)} |", "",
         "## 2. NEW — learnings the skill does not carry yet", "", "| Date | Domain | Learning | Best section (coverage) | Costly |", "|---|---|---|---|---|"]
    for c in new:
        b = f"`{c['best']['file']}` › {c['best']['heading'][:50]} ({c['cov']})" if c["best"] else "—"
        L.append(f"| {c['date']} | {c['domain']} | {c['text'][:220].replace('|', chr(92) + '|')}{'…' if len(c['text']) > 220 else ''} | {b} | {'yes' if c['costly'] else ''} |")
    L += ["", "## 3. PARTIAL — carried in part (check the section, extend it if the mechanism is missing)", "", "| Date | Domain | Learning | Best section (coverage) |", "|---|---|---|---|"]
    for c in partial:
        b = f"`{c['best']['file']}` › {c['best']['heading'][:50]} ({c['cov']})" if c["best"] else "—"
        L.append(f"| {c['date']} | {c['domain']} | {c['text'][:180].replace('|', chr(92) + '|')}{'…' if len(c['text']) > 180 else ''} | {b} |")
    L += ["", "## 4. CHANGELOG entry draft", "", f"### Added (from {project}, learnings {min((e['date'] for e in entries), default='—')} … {max((e['date'] for e in entries), default='—')})"]
    by_file = {}
    for c in new:
        by_file.setdefault(target_file(c, c["best"]), []).append(c)
    for f, cs in sorted(by_file.items()):
        L.append(f"- **`{f}`**: " + "; ".join(generalise(c["text"])[:140] for c in cs[:6]) + (f"; +{len(cs) - 6} more" if len(cs) > 6 else ""))
    L += ["", "### Changed", "- (sections the PARTIAL entries extend: " + ", ".join(sorted({f"`{c['best']['file']}`" for c in partial if c["best"]})) + ")", "",
          "## 5. Reference patch stubs (bullets to append; generalise the numbers, label the worked example, keep the evidence pointer at the end)", ""]
    for f, cs in sorted(by_file.items()):
        L.append(f"### {f}"); L += [f"- {c['date']} [{c['domain'] or 'general'}] {generalise(c['text'])}" for c in cs]; L.append("")
    costly_new = [c for c in new if c["costly"]]
    L += ["## 6. Eval stubs — one per NEW learning that cost a round (fill prompt / assertions from the entry; add to evals/evals.json)", "", "```json"]
    for i, c in enumerate(costly_new, 1):
        head = re.split(r"[:—-]", c["text"], maxsplit=1)[0].strip()[:80]
        L.append(json.dumps({"id": f"R{i}", "name": re.sub(r"[^a-z0-9]+", "-", head.lower()).strip("-")[:60] or "retro-eval",
                             "prompt": f"A project hits this situation: {head}. Handle it.",
                             "expected_output": generalise(c["text"])[:400],
                             "assertions": [f"the agent applies: {generalise(c['text'])[:200]}", "the mechanism is written to the project's LEARNINGS_LOG with evidence"]}, ensure_ascii=False))
    L += ["```", "", "## 7. Owner decision topics the kickoff questionnaire does not ask yet (candidates for a new question with a recommended answer)", "",
          "| Row | Date | Topic | Best question section (coverage) |", "|---|---|---|---|"]
    for d in unasked[:60]:
        b = f"`{d['best']['heading'][:60]}` ({d['cov']})" if d["best"] else "—"
        L.append(f"| {d['id']} | {d['date']} | {d['topic'][:120].replace('|', chr(92) + '|')} | {b} |")
    if not os.path.exists(q_path):
        L.append("| — | — | (no references/kickoff-questionnaire.md in this skill) | — |")
    L += ["", "## 8. What to do with this report", "",
          "1. Fold every NEW row into the reference named in §5 (one generalised line; the source's number stays as the labelled worked example).",
          "2. Extend the PARTIAL sections where the mechanism is missing.", "3. Add one eval per §6 stub; run the smoke; bump SKILL.md `version`; write the CHANGELOG entry from §4.",
          "4. Add a questionnaire question (with a recommended answer) per §7 topic that will recur.", "5. Blind-review the skill again (two lenses), then tag."]
    return "\n".join(L) + "\n", dict(new=len(new), partial=len(partial), carried=len(carried), costly=len(costly_new), unasked=len(unasked), drift=bool(pv and pv != sv))


def run(project_arg, skill, out_dir, since, threshold, today=None):
    today = today or datetime.date.today().isoformat()
    root = project_arg or os.getcwd()
    if root.endswith(".yaml"):
        root = os.path.dirname(os.path.abspath(root))
    root = os.path.abspath(root)
    learn = os.path.join(root, "docs", "governance", "LEARNINGS_LOG.md"); dec = os.path.join(root, "docs", "governance", "DECISIONS.md")
    if os.path.exists(os.path.join(root, "project.yaml")):
        try:
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from project import Project
            P = Project(os.path.join(root, "project.yaml")); learn = P.path("learnings") or learn; dec = P.path("decisions") or dec
        except Exception:  # noqa: BLE001 — fall back to the default layout
            pass
    for p in (learn, dec, os.path.join(skill, "SKILL.md")):
        if not os.path.exists(p):
            print(f"skill_retro: MISSING {p}"); return 2
    project = os.path.basename(root)
    sections, idf = index_skill(skill)
    entries = read_entries(learn, since); decisions = read_decisions(dec)
    text, counts = build_report(project, root, skill, entries, decisions, sections, idf, threshold, today)
    out_dir = out_dir or os.path.join(skill, "docs", "retro"); os.makedirs(out_dir, exist_ok=True)
    out = os.path.join(out_dir, f"{project}_{today}.md")
    open(out, "w", encoding="utf-8").write(text)
    print(f"{out}: {len(entries)} learnings -> NEW {counts['new']} / PARTIAL {counts['partial']} / CARRIED {counts['carried']}; costly NEW {counts['costly']}; "
          f"owner topics not in the questionnaire {counts['unasked']}; version drift {counts['drift']}")
    return 0


def selftest():
    import tempfile
    d = tempfile.mkdtemp(prefix="hwfs_retro_")
    skill = os.path.join(d, "skill"); os.makedirs(os.path.join(skill, "references"))
    open(os.path.join(skill, "SKILL.md"), "w").write("---\nname: x\nversion: 9.9.9\n---\n# x\n## Rules\nEvery checker is read-only on the tree.\n")
    open(os.path.join(skill, "references", "dfm.md"), "w").write("# dfm\n## Census gate\nThe ray-cast census clusters thin samples below the gate and classifies wall versus wedge by the opposite-face angle; walls FAIL, wedges are listed.\n")
    open(os.path.join(skill, "references", "kickoff-questionnaire.md"), "w").write("# q\n## C2 Retention\nscrews into inserts, magnets, none — recommended screws.\n")
    proj = os.path.join(d, "proj"); os.makedirs(os.path.join(proj, "docs", "governance"))
    open(os.path.join(proj, "project.yaml"), "w").write("project: {name: proj}\nskill: {version: 1.0.0}\n")
    open(os.path.join(proj, "docs", "governance", "LEARNINGS_LOG.md"), "w").write(
        "# log\n\n## 2026-09-28\n"
        "- 2026-09-28 [dfm/census] A ray-cast census that clusters thin samples below the gate must classify each cluster wall versus wedge by the opposite-face angle; walls FAIL, wedges are listed — CC-205.\n"
        "- 2026-09-28 [tooling/yaml] PyYAML keeps the LAST of two duplicate keys in a mapping without a word; a duplicate-aware SafeLoader gates every design yaml — commit abc.\n"
        "- 2026-09-28 [fdm/export] mirror([0,0,1]) flips handedness and every asymmetric mark printed backwards, the WRONG way to put a roof on the bed; use rotate([180,0,0])\n"
        "  and check the export against the board-frame mesh — D-84.\n"
        "- 2026-09-01 [old] an entry before --since that must be filtered out — x.\n")
    open(os.path.join(proj, "docs", "governance", "DECISIONS.md"), "w").write(
        "| ID | Date | Status | Topic | Proposal | Reason |\n|---|---|---|---|---|---|\n"
        "| **D-85 (owner)** | 2026-09-28 | APPROVED | Hood retention by magnets, standard easy-to-find size | Owner: magnets | words |\n"
        "| **D-86 (owner)** | 2026-09-28 | APPROVED | Purple anodised aluminium badge with laser artwork | Owner: badge | words |\n"
        "| CC-208 | 2026-09-28 | APPLIED | magnet pockets | two pairs | D-85 |\n")
    sections, idf = index_skill(skill)
    assert len(sections) == 4 and "census" in idf, sections   # frontmatter = a (top) section
    ents = read_entries(os.path.join(proj, "docs", "governance", "LEARNINGS_LOG.md"), since="2026-09-02")
    assert len(ents) == 3 and ents[2]["text"].endswith("D-84.") and "board-frame" in ents[2]["text"], ents
    c0 = classify(ents[0]["text"], sections, idf, 0.5); c1 = classify(ents[1]["text"], sections, idf, 0.5)
    assert c0[0] == "CARRIED" and c0[2]["heading"] == "Census gate", c0
    assert c1[0] == "NEW", c1
    decs = read_decisions(os.path.join(proj, "docs", "governance", "DECISIONS.md"))
    assert [x["id"] for x in decs] == ["D-85", "D-86", "CC-208"] and decs[0]["owner"] and not decs[2]["owner"], decs
    assert generalise(ents[0]["text"]).endswith("*(evidence: CC-205.)*") and COSTLY.search(ents[2]["text"]) and not COSTLY.search(ents[0]["text"])
    out = os.path.join(d, "retro")
    assert run(proj, skill, out, "2026-09-02", 0.5, today="2026-09-28") == 0
    rep = open(os.path.join(out, "proj_2026-09-28.md")).read()
    assert "| 1 | " in rep.split("## 1. Counts")[1].split("## 2.")[0], rep                      # 1 carried
    assert "PyYAML keeps the LAST" in rep.split("## 2. NEW")[1].split("## 3.")[0], "the duplicate-key learning is NEW"
    assert "drift" in rep and "1.0.0" in rep and "9.9.9" in rep, "version drift reported"
    assert '"name": "mirror-0-0-1-flips-handedness' in rep or '"id": "R1"' in rep, "an eval stub for the costly NEW entry"
    assert "D-86" in rep.split("## 7.")[1], "the badge decision is not asked by the fixture questionnaire"
    assert "### references/pitfalls.md" in rep or "### references/dfm.md" in rep, "patch stubs per target file"
    assert run(os.path.join(d, "nowhere"), skill, out, None, 0.5) == 2
    print("selftest OK (entries + continuation lines, --since, CARRIED / NEW classification, owner rows, costly marker, version drift, report sections, eval stub, unasked decision topics)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--project", help="project root or its project.yaml (default: cwd)"); ap.add_argument("--skill", default=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    ap.add_argument("--out"); ap.add_argument("--since"); ap.add_argument("--threshold", type=float, default=0.5); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    return run(a.project, a.skill, a.out, a.since, a.threshold)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
