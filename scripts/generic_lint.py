#!/usr/bin/env python3
"""scripts/generic_lint.py — the skill describes the METHOD for any hardware project, never the one it was learned on (owner rule).

  scripts/generic_lint.py [--skill DIR] [--terms scripts/generic_lint_terms.yaml] [--private-terms FILE] [FILE...]
      default files: every text file of the skill repo — SKILL.md, README.md, CHANGELOG.md, references/, templates/, scripts/, smoke/, evals/,
      workflows/, docs/ — except .git/, .venv/, __pycache__/, LICENSE (the copyright holder is a legal notice) and the term file itself.
      Exit 1 with one line per hit (file:line: <group> `<match>`), 0 when clean, 2 when the term file or a file is missing.
  scripts/generic_lint.py --export DIR [--allow FILE] [--private-terms FILE]
      Fail-closed scan of a public export tree. It needs the private terms (exit 2 without them). It reads every file and every
      file name and symlink target, applies every group everywhere, and skips nothing: no `generic: ok` line, no worked example,
      no history exemption. The allow file holds exact strings, one per line, stripped from a line before the match; a line
      `binary: <relpath>` marks a binary as reviewed. A binary's printable strings are scanned, and an unreviewed binary is a hit
      (its metadata needs a human read). CI writes the private terms from a secret and sets HWFS_PRIVATE_TERMS.
  scripts/generic_lint.py --selftest

The repo is public, so `scripts/generic_lint_terms.yaml` holds only generic SHAPES (id formats, path shapes, a refdes scheme). The names
(project, person, company, order, part, preset, one design's dimensions) live in a private file outside the repo, same group shape:
--private-terms, else $HWFS_PRIVATE_TERMS, else ~/.config/hw-from-spec/private_terms.yaml. The lint merges it when it exists; without it
the lint runs the generic patterns and prints one note line. A group named
`*_as_citations` applies to PROSE only (.md outside smoke/ and templates/): a fixture row in a selftest, the smoke or a template seed row uses the
D-nn / CC-nnn id scheme by design and is not a citation. CHANGELOG.md and docs/ are history: they keep measured numbers and cite the skill's own
review findings, so `design_dimensions` and `review_ids_as_citations` do not apply there — every name, id and people group does. Lines between
`<!-- worked example: begin` and `<!-- worked example: end -->` skip every group except the `*_names` and `*_ids` groups (a worked example keeps
numbers and kinds, never a name) — at most ONE such block per file (a second one is a hit); a line carrying `generic: ok` is skipped (a lint
pattern that must spell a term, a fixture).
"""
import argparse, contextlib, io, os, re, sys, tempfile

BEGIN, END = "<!-- worked example: begin", "<!-- worked example: end -->"
SKIP_DIRS, SKIP_FILES = {".git", ".venv", "__pycache__"}, {".git", "LICENSE", "generic_lint_terms.yaml"}  # .git is a file in a worktree
HISTORY_OK = ("design_dimensions", "review_ids_as_citations")                     # CHANGELOG.md and docs/ keep numbers and the skill's review ids


PRIVATE_DEFAULT = os.path.join("~", ".config", "hw-from-spec", "private_terms.yaml")


def load_terms(*paths):
    import yaml
    out = []
    for path in paths:
        groups = yaml.safe_load(open(path, encoding="utf-8")) or {}
        out += [(g, re.compile(p)) for g, pats in groups.items() for p in (pats or [])]
    return out


def private_terms_path(arg=None):
    """(path or None, source). An explicit --private-terms or HWFS_PRIVATE_TERMS that does not exist is an error (path None,
    source 'MISSING <p>'); only the default home path may be absent (the lint then runs the generic patterns only)."""
    explicit = arg or os.environ.get("HWFS_PRIVATE_TERMS")
    p = os.path.expanduser(explicit or PRIVATE_DEFAULT)
    if os.path.isfile(p):
        return p, ("--private-terms" if arg else "HWFS_PRIVATE_TERMS" if explicit else "default path")
    return None, (f"MISSING {p}" if explicit else "none")


REQUIRED_PRIVATE = ("people_names", "project_names")        # export mode refuses a private file with no pattern in these groups
STRICT_IDS = [("record_ids_strict", re.compile(r"\bCC-\d{3}\b")), ("record_ids_strict", re.compile(r"\bD-\d{2}[a-z]?\b"))]  # no seed-row exemption in an export
BINARY_EXT = (".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".7z", ".zst", ".rar", ".jar", ".whl", ".pdf", ".png", ".jpg", ".jpeg",
              ".gif", ".webp", ".ico", ".bmp", ".tif", ".tiff", ".3mf", ".stl", ".step", ".stp", ".docx", ".xlsx", ".pptx", ".odt")
MAGIC = (b"%PDF", b"PK\x03\x04", b"\x1f\x8b", b"BZh", b"\xfd7zXZ", b"7z\xbc\xaf", b"\x28\xb5\x2f\xfd", b"Rar!", b"\x89PNG",
         b"\xff\xd8\xff", b"GIF8", b"RIFF", b"II*\x00", b"MM\x00*", b"\x00\x00\x01\x00")


def classify(rel, data):
    """'text', 'utf16' or 'binary', by name and content, never by a NUL byte alone."""
    if data[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(data) > 3 and data[1:200:2].count(0) > 0.8 * len(data[1:200:2]) and data[0:200:2].count(0) == 0):
        return "utf16"
    if rel.lower().endswith(BINARY_EXT) or data.startswith(MAGIC) or data[257:262] == b"ustar":
        return "binary"
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        return "binary"
    return "binary" if "\0" in t else "text"


def binary_strings(data):
    """The readable text of a binary: ASCII and UTF-16LE runs of 6+, and every PNG text chunk (zTXt / iTXt decompressed)."""
    import zlib
    out = [m.decode("ascii") for m in re.findall(rb"[\x20-\x7e]{6,}", data)]
    out += [m.decode("utf-16le") for m in re.findall(rb"(?:[\x20-\x7e]\x00){6,}", data)]
    if data.startswith(b"\x89PNG"):
        i = 8
        while i + 8 <= len(data):
            n = int.from_bytes(data[i:i + 4], "big"); kind = data[i + 4:i + 8]; body = data[i + 8:i + 8 + n]; i += 12 + n
            try:
                if kind == b"zTXt":
                    k, _, rest = body.partition(b"\0"); out.append(k.decode("latin-1") + " " + zlib.decompress(rest[1:]).decode("latin-1"))
                elif kind == b"iTXt":
                    k, _, rest = body.partition(b"\0"); flag = rest[0]; rest = rest[2:]
                    rest = rest.split(b"\0", 2)[-1]
                    out.append(k.decode("latin-1") + " " + (zlib.decompress(rest) if flag else rest).decode("utf-8", "replace"))
            except Exception:
                out.append(f"<unreadable {kind!r} chunk>")
    return out


def parse_allow(lines, private_terms):
    """Typed allow entries -> (strings, reviewed binaries, errors). url: / key: values are exact strings of 12+ characters that no
    private pattern matches as a whole; binary: names a reviewed binary; any other line is an error."""
    strings, reviewed, errs = [], set(), []
    for ln in lines:
        kind, _, val = ln.partition(": "); val = val.strip()
        if kind == "binary" and val:
            reviewed.add(val)
        elif kind in ("url", "key") and val:
            if len(val) < 12:
                errs.append(f"allow entry too short (12+ characters): `{ln}`")
            elif any(rx.fullmatch(val) or (m := rx.search(val)) and m.group(0) == val for _, rx in private_terms):
                errs.append(f"allow entry is a private term: `{ln}`")
            else:
                strings.append(val)
        else:
            errs.append(f"allow entry needs a type (url: / key: / binary:): `{ln}`")
    return strings, reviewed, errs


def lint_export(root, terms, strings, reviewed):
    """Every file under root: path, symlink target, every match on every text line (allowed strings stripped), binary strings.
    Returns (hits, files, use count per allowed string)."""
    hits, n, used = [], 0, {x: 0 for x in strings}

    def scan(rel, ln, text):
        for x in strings:
            used[x] += text.count(x); text = text.replace(x, "")
        for g, rx in terms:
            hits.extend((rel, ln, g, m.group(0)) for m in rx.finditer(text))

    for dp, dns, fs in os.walk(root):
        dns.sort()
        for f in sorted(fs + [x for x in dns if os.path.islink(os.path.join(dp, x))]):
            p = os.path.join(dp, f); rel = os.path.relpath(p, root); n += 1
            scan(rel, 0, rel)                                                   # the path itself
            if os.path.islink(p):
                scan(rel, 0, os.readlink(p)); continue
            data = open(p, "rb").read(); kind = classify(rel, data)
            if kind == "text":
                for ln, line in enumerate(data.decode("utf-8").split("\n"), 1):
                    scan(rel, ln, line)
                continue
            for s_ in (data.decode("utf-16", "replace").split("\n") if kind == "utf16" else binary_strings(data)):
                scan(rel, 0, s_)
            if rel not in reviewed:
                hits.append((rel, 0, "binary-review", f"{kind}: read its metadata (exiftool -a -G1), then allow it as `binary: {rel}`"))
    return hits, n, used


def export_main(root, tp, pp, allow_path):
    """The fail-closed export gate. Exit 2 on a setup fault, 1 on any hit, 0 when clean."""
    if not os.path.isdir(root) or not os.listdir(root):
        print(f"generic_lint --export: {root} is not an existing, non-empty folder", file=sys.stderr); return 2
    gits = [os.path.relpath(os.path.join(dp, x), root) for dp, dns, fs in os.walk(root) for x in dns + fs if x == ".git"]
    if gits:
        print(f"generic_lint --export: refused, {gits[0]} in the export tree; scan the outgoing commit metadata on its own", file=sys.stderr); return 2
    if not pp:
        print("generic_lint --export: needs the private terms (CI: write them from a secret, set HWFS_PRIVATE_TERMS)", file=sys.stderr); return 2
    priv = load_terms(pp); counts = {}
    for g, _ in priv:
        counts[g] = counts.get(g, 0) + 1
    print("generic_lint --export: private patterns per group: " + (", ".join(f"{g} {c}" for g, c in sorted(counts.items())) or "none"), file=sys.stderr)
    missing = [g for g in REQUIRED_PRIVATE if not counts.get(g)]
    if missing:
        print(f"generic_lint --export: refused, the private term file has no pattern in {missing}", file=sys.stderr); return 2
    lines = [x.rstrip("\n") for x in open(allow_path, encoding="utf-8") if x.strip()] if allow_path else []
    strings, reviewed, errs = parse_allow(lines, priv)
    if errs:
        for e in errs:
            print(f"generic_lint --export: {e}", file=sys.stderr)
        return 2
    hits, n, used = lint_export(root, load_terms(tp) + priv + STRICT_IDS, strings, reviewed)
    if n == 0:
        print("generic_lint --export: no file scanned", file=sys.stderr); return 2
    for rel, ln, g, m in hits:
        print(f"{rel}:{ln}: {g} `{m}`")
    for x, c in used.items():
        print(f"allow used {c}x: {x}")
    print(f"generic_lint --export: {len(hits)} hit(s) in {n} file(s)")
    return 1 if hits else 0


def export_selftest(d, priv, generic):
    """Fixtures for the export gate (synthetic terms only)."""
    import zlib
    q = contextlib.redirect_stderr(io.StringIO()); q2 = contextlib.redirect_stdout(io.StringIO())
    e = f"{d}/exp"; os.makedirs(f"{e}/src"); os.makedirs(f"{e}/docs")
    open(f"{e}/src/a.py", "w").write("x = 1  # fixed per CC-287 and D-61, see R1-05 generic: ok\n")
    open(f"{e}/src/b.js", "w").write("// ask qwyzzle\n")
    open(f"{e}/CHANGELOG.md", "w").write("Seed CC-001 and D-01 leak too.\n")
    open(f"{e}/README.md", "w").write("Repo: github.com/qwyzzle/pub (public)\n")
    open(f"{e}/docs/qwyzzle_notes.txt", "w").write("plain\n")
    open(f"{e}/u16.txt", "wb").write("ask qwyzzle\n".encode("utf-16"))
    z = b"Comment\0\0" + zlib.compress(b"/Users/qwyzzle/x")   # generic: ok (fixture)
    open(f"{e}/logo.png", "wb").write(b"\x89PNG\r\n\x1a\n" + len(z).to_bytes(4, "big") + b"zTXt" + z + b"\0\0\0\0")
    open(f"{e}/doc.pdf", "wb").write(b"%PDF-1.4 /Author (Qwyzzle)")
    allow = f"{d}/allow.txt"; open(allow, "w").write("url: github.com/qwyzzle/pub\n")
    T = load_terms(generic) + load_terms(priv) + STRICT_IDS
    s, r, err = parse_allow([x for x in open(allow).read().split("\n") if x], load_terms(priv)); assert not err, err
    h, n, used = lint_export(e, T, s, r); got = {(a, g) for a, _, g, _ in h}
    for want in [("src/a.py", "record_ids_as_citations"), ("src/a.py", "review_ids_as_citations"), ("src/b.js", "people_names"),
                 ("CHANGELOG.md", "record_ids_strict"), ("docs/qwyzzle_notes.txt", "people_names"), ("u16.txt", "people_names"),
                 ("u16.txt", "binary-review"), ("logo.png", "machine_paths"), ("logo.png", "binary-review"), ("doc.pdf", "people_names"),
                 ("doc.pdf", "binary-review")]:
        assert want in got, (want, got)
    assert sum(1 for a, _, g, _ in h if a == "src/a.py" and g == "record_ids_as_citations") == 2, "every match on a line is reported"
    assert not any(a == "README.md" for a, *_ in h) and used["github.com/qwyzzle/pub"] == 1, ("the typed exact string is stripped", h, used)
    for bad in ["qwyzzle", "url: qwyzzle", "url: abc", "key: Qwyzzle Jones Ltd"]:
        assert parse_allow([bad], load_terms(priv) + [("people_names", re.compile(r"(?i)qwyzzle jones ltd"))])[2], bad
    with q, q2:
        empty = f"{d}/empty.yaml"; open(empty, "w").write("{}\n")
        assert export_main(e, generic, empty, allow) == 2, "an empty private file is refused"
        assert export_main(f"{d}/nope", generic, priv, allow) == 2 and export_main(f"{d}/references", generic, priv, None) in (0, 1)
        os.makedirs(f"{d}/emptydir"); assert export_main(f"{d}/emptydir", generic, priv, None) == 2, "an empty export folder is refused"
        os.makedirs(f"{e}/.git"); assert export_main(e, generic, priv, allow) == 2, "a .git in the export is refused"
    os.rmdir(f"{e}/.git")


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
    priv = f"{d}/private.yaml"; open(priv, "w").write("people_names:\n  - '(?i)qwyzzle'\nproject_names:\n  - '\\bZYXPROJ\\b'\n")   # a synthetic private term
    open(f"{d}/references/b.md", "w").write("Ask Qwyzzle.\n")
    gen_only = lint(default_files(d), terms, d)
    assert not any("references/b.md" in a for a, *_ in gen_only), "without the private file the private term is not known"
    old = os.environ.get("HWFS_PRIVATE_TERMS")
    try:
        os.environ["HWFS_PRIVATE_TERMS"] = priv
        assert private_terms_path() == (priv, "HWFS_PRIVATE_TERMS") and private_terms_path(f"{d}/absent.yaml")[0] is None
        merged = lint(default_files(d), load_terms(f"{d}/scripts/generic_lint_terms.yaml", private_terms_path()[0]), d)
        os.environ["HWFS_PRIVATE_TERMS"] = f"{d}/typo.yaml"
        assert private_terms_path() == (None, f"MISSING {d}/typo.yaml"), "a set but missing env var is an error, not a silent skip"
        with contextlib.redirect_stderr(io.StringIO()):
            assert main(["x", "--skill", d]) == 2
        del os.environ["HWFS_PRIVATE_TERMS"]
        export_selftest(d, priv, os.path.join(os.path.dirname(os.path.realpath(__file__)), "generic_lint_terms.yaml"))
    finally:
        os.environ.pop("HWFS_PRIVATE_TERMS", None)
        if old is not None:
            os.environ["HWFS_PRIVATE_TERMS"] = old
    assert any(a == "references/b.md" and g == "people_names" for a, _, g, _ in merged), merged
    print("selftest OK (term groups, whole-repo file set, worked-example block keeps numbers not names, one block per file, history keeps numbers, generic: ok marker, private terms merged from outside the repo, a missing explicit path fails, export mode fail-closed: empty or patternless private file, missing or empty folder, .git refused; every match per line; seed ids; UTF-16, PDF and PNG zTXt read; typed allow entries)")
    return 0


def main(argv):
    skill_default = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--skill", default=skill_default)
    ap.add_argument("--terms"); ap.add_argument("--private-terms"); ap.add_argument("files", nargs="*"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--export"); ap.add_argument("--allow")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    tp = a.terms or os.path.join(skill_default if a.export else a.skill, "scripts", "generic_lint_terms.yaml")
    if not os.path.exists(tp):
        print(f"generic_lint: MISSING term file {tp}", file=sys.stderr); return 2
    pp, src = private_terms_path(a.private_terms)
    if src.startswith("MISSING"):
        print(f"generic_lint: {src} (private term file named but absent)", file=sys.stderr); return 2
    print(f"generic_lint: terms: generic ({os.path.basename(tp)}) + private: {src}", file=sys.stderr)
    if a.export:
        return export_main(os.path.abspath(a.export), tp, pp, a.allow)
    if not pp:
        print("generic_lint: note: no private term file; generic patterns only (set HWFS_PRIVATE_TERMS)", file=sys.stderr)
    files = [os.path.abspath(f) for f in a.files] or default_files(a.skill)
    hits = lint(files, load_terms(tp, *([pp] if pp else [])), a.skill)
    for rel, n, g, m in hits:
        print(f"{rel}:{n}: {g} `{m}`" if g != "MISSING" else f"{rel}: MISSING")
    print(f"generic_lint: {len(hits)} hit(s) in {len(files)} file(s)")
    return 2 if any(g == "MISSING" for _, _, g, _ in hits) else (1 if hits else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
