#!/usr/bin/env python3
"""scripts/generic_lint.py — the skill describes the METHOD for any hardware project, never the one it was learned on (owner rule).

  scripts/generic_lint.py [--skill DIR] [--terms scripts/generic_lint_terms.yaml] [--private-terms FILE] [FILE...]
      default files: every text file of the skill repo — SKILL.md, README.md, CHANGELOG.md, references/, templates/, scripts/, smoke/, evals/,
      workflows/, docs/ — except .git/, .venv/, __pycache__/, LICENSE (the copyright holder is a legal notice) and the term file itself.
      Exit 1 with one line per hit (file:line: <group> `<match>`), 0 when clean, 2 when the term file or a file is missing.
  scripts/generic_lint.py --export DIR [--allow FILE] [--private-terms FILE]
      Fail-closed scan of a public export tree; release-and-cut §15 is the procedure. It pins the skill's generic rules (--terms is
      refused) and needs a private term file with a pattern in every promised group (exit 2 without). It refuses a .git anywhere. It
      reads every file, file name and symlink target; decodes zip / 3MF / Office / gzip / svgz / bz2 / xz members and PDF Flate
      streams; matches after Unicode NFKC with the invisible format characters removed, and across each line break. A part it cannot
      decode is a hit. It skips nothing: no `generic: ok` line, no worked example, no history file. Allow entries are typed: `url:` and
      `key:` exact strings (12+ characters, no term match inside), `binary: <path> <sha256>` for a binary a human has read. A
      changed binary or an allow entry that matches nothing fails the run.
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
        if not isinstance(groups, dict):
            raise ValueError(f"{path}: not a mapping of group -> list of patterns")
        for g, pats in groups.items():
            if pats is not None and (not isinstance(pats, list) or not all(isinstance(p, str) and p for p in pats)):
                raise ValueError(f"{path}: group `{g}` must be a list of non-empty pattern strings")
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


REQUIRED_PRIVATE = ("people_names", "project_names", "project_ids", "parts_and_refdes")   # every promised private group needs a pattern
REQUIRED_GENERIC = ("machine_paths", "project_ids", "parts_and_refdes", "record_ids_as_citations", "review_ids_as_citations")
STRICT_IDS = [("record_ids_strict", re.compile(r"\bCC-\d{3}\b")), ("record_ids_strict", re.compile(r"\bD-\d{2}[a-z]?\b"))]  # no seed-row exemption in an export
ZIP_EXT = (".zip", ".3mf", ".docx", ".xlsx", ".pptx", ".odt", ".ods", ".jar", ".whl")
OPAQUE_EXT = (".tar", ".tgz", ".7z", ".zst", ".rar", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".bmp", ".tif", ".tiff", ".stl",
              ".step", ".stp")
MAGIC = (b"%PDF", b"PK\x03\x04", b"\x1f\x8b", b"BZh", b"\xfd7zXZ", b"7z\xbc\xaf", b"\x28\xb5\x2f\xfd", b"Rar!", b"\x89PNG",
         b"\xff\xd8\xff", b"GIF8", b"RIFF", b"II*\x00", b"MM\x00*", b"\x00\x00\x01\x00")
CF = re.compile(r"[\u00ad\u200b-\u200f\u2060-\u2064\ufeff\u202a-\u202e]")


def clean(text):
    """NFKC, then the invisible format characters (soft hyphen, zero-width, bidi marks) removed."""
    import unicodedata
    return CF.sub("", unicodedata.normalize("NFKC", text))


def decode_any(rel, data, depth=0):
    """[(name, text, kind)] for one file: kind 'text', or 'binary' (needs a human read). Containers and compressed files are
    opened and their members decoded too. A part that cannot be decoded comes back as kind 'undecodable'."""
    import bz2, gzip, io as _io, lzma, zipfile, zlib
    if depth > 4:
        return [(rel, "", "undecodable")]
    low = rel.lower()
    if data[:2] in (b"\xff\xfe", b"\xfe\xff") or (len(data) > 3 and data[1:200:2].count(0) > 0.8 * len(data[1:200:2]) and data[0:200:2].count(0) == 0):
        return [(rel, data.decode("utf-16", "replace"), "binary")]
    try:
        if data.startswith(b"PK\x03\x04") or low.endswith(ZIP_EXT):
            out = [(rel, "", "binary")]
            with zipfile.ZipFile(_io.BytesIO(data)) as z:
                for m in z.namelist():
                    out += [(f"{rel}!{n}", t, k) for n, t, k in decode_any(m, z.read(m), depth + 1)]
            return out
        for magic, ext, fn in ((b"\x1f\x8b", (".gz", ".svgz", ".tgz"), gzip.decompress), (b"BZh", (".bz2",), bz2.decompress),
                               (b"\xfd7zXZ", (".xz",), lzma.decompress)):
            if data.startswith(magic) or low.endswith(ext):
                inner = fn(data)
                return [(rel, "", "binary")] + decode_any(rel.rsplit(".", 1)[0] if not low.endswith(".svgz") else rel[:-1], inner, depth + 1)
    except Exception:
        return [(rel, "", "undecodable")]
    if data.startswith(b"%PDF") or low.endswith(".pdf"):
        out = [(rel, " ".join(m.decode("latin-1") for m in re.findall(rb"[\x20-\x7e]{4,}", data)), "binary")]
        for hdr, body in re.findall(rb"<<(.{0,400}?)>>\s*stream\r?\n(.*?)endstream", data, re.S):
            if b"FlateDecode" in hdr:
                try:
                    out.append((rel + "!stream", zlib.decompress(body).decode("latin-1"), "binary"))
                except Exception:
                    out.append((rel + "!stream", "", "undecodable"))
            elif b"Filter" in hdr and b"DCTDecode" not in hdr and b"JPXDecode" not in hdr:
                out.append((rel + "!stream", "", "undecodable"))            # an LZW or other filter this gate cannot read
        return out
    if data.startswith(MAGIC) or low.endswith(OPAQUE_EXT):
        return [(rel, "\n".join(binary_strings(data)), "binary")]
    try:
        t = data.decode("utf-8")
    except UnicodeDecodeError:
        return [(rel, "\n".join(binary_strings(data)), "binary")]
    return [(rel, "\n".join(binary_strings(data)), "binary")] if "\0" in t else [(rel, t, "text")]


def binary_strings(data):
    """The readable text of a binary: ASCII and UTF-16LE runs of 4+, and every PNG text chunk (tEXt, zTXt, iTXt)."""
    import zlib
    out = [m.decode("ascii") for m in re.findall(rb"[\x20-\x7e]{4,}", data)]
    out += [m.decode("utf-16le") for m in re.findall(rb"(?:[\x20-\x7e]\x00){4,}", data)]
    if data.startswith(b"\x89PNG"):
        i = 8
        while i + 8 <= len(data):
            n = int.from_bytes(data[i:i + 4], "big"); kind = data[i + 4:i + 8]; body = data[i + 8:i + 8 + n]; i += 12 + n
            try:
                if kind == b"zTXt":
                    k, _, rest = body.partition(b"\0"); out.append(k.decode("latin-1") + " " + zlib.decompress(rest[1:]).decode("latin-1"))
                elif kind == b"iTXt":
                    k, _, rest = body.partition(b"\0"); flag = rest[0]; rest = rest[2:].split(b"\0", 2)[-1]
                    out.append(k.decode("latin-1") + " " + (zlib.decompress(rest) if flag else rest).decode("utf-8", "replace"))
                elif kind == b"tEXt":
                    out.append(body.replace(b"\0", b" ").decode("latin-1"))
            except Exception:
                out.append("<unreadable PNG text chunk>")
    return out


def parse_allow(lines, all_terms):
    """Typed allow entries -> (strings, {path: sha256}, errors). A url: / key: value is an exact string of 12+ characters in
    which no term matches anywhere. binary: names a path and its sha256. Any other line is an error."""
    strings, reviewed, errs = [], {}, []
    for ln in lines:
        kind, _, val = ln.partition(": "); val = val.strip()
        if kind == "binary":
            parts = val.split()
            if len(parts) == 2 and re.fullmatch(r"[0-9a-f]{64}", parts[1]):
                reviewed[parts[0]] = parts[1]
            else:
                errs.append(f"binary entry needs `binary: <path> <sha256>`: `{ln}`")
        elif kind in ("url", "key") and val:
            hit = next((m.group(0) for _, rx in all_terms if (m := rx.search(clean(val)))), None)
            if len(val) < 12:
                errs.append(f"allow entry too short (12+ characters): `{ln}`")
            elif hit:
                errs.append(f"allow entry contains a term match `{hit}`: `{ln}`")
            elif kind == "url" and not re.fullmatch(r"[A-Za-z0-9.-]+\.[A-Za-z]{2,}(/[^\s]*)?|https?://[^\s]+", val):
                errs.append(f"url entry is not a url: `{ln}`")
            else:
                strings.append(val)
        else:
            errs.append(f"allow entry needs a type (url: / key: / binary:): `{ln}`")
    return strings, reviewed, errs


def lint_export(root, terms, strings, reviewed):
    """Every file under root: path, symlink target, decoded members, every match on every line and across each line break.
    Returns (hits, files, use count per allow entry)."""
    import hashlib
    hits, n, used = [], 0, {x: 0 for x in list(strings) + [f"binary: {p}" for p in reviewed]}

    def scan(rel, ln, text, prev=None):
        text = clean(text)
        for x in strings:
            used[x] += text.count(x); text = text.replace(x, "")
        for g, rx in terms:
            hits.extend((rel, ln, g, m.group(0)) for m in rx.finditer(text))
            if prev is not None:                                                # a match across the line break
                j = prev + " " + text.lstrip()
                hits.extend((rel, ln, g, m.group(0)) for m in rx.finditer(j) if m.start() < len(prev) < m.end())
        return text

    for dp, dns, fs in os.walk(root):
        dns.sort()
        for f in sorted(fs + [x for x in dns if os.path.islink(os.path.join(dp, x))]):
            p = os.path.join(dp, f); rel = os.path.relpath(p, root); n += 1
            scan(rel, 0, rel)
            if os.path.islink(p):
                scan(rel, 0, os.readlink(p)); continue
            data = open(p, "rb").read(); parts = decode_any(rel, data); binary = False
            for name, text, kind in parts:
                if kind == "undecodable":
                    hits.append((name, 0, "undecodable", "a part this gate cannot decode: extract it by hand, or leave it out")); continue
                binary |= kind == "binary"
                prev = None
                for ln, line in enumerate(text.split("\n"), 1):
                    prev = scan(name, ln, line, prev).rstrip()
            if binary:
                sha = hashlib.sha256(data).hexdigest()
                if rel not in reviewed:
                    hits.append((rel, 0, "binary-review", f"read its text and metadata, then allow it as `binary: {rel} {sha}`"))
                elif reviewed[rel] != sha:
                    hits.append((rel, 0, "binary-changed", f"the file changed since its review (sha256 {sha})"))
                else:
                    used[f"binary: {rel}"] += 1
    return hits, n, used


def export_main(root, tp, pp, allow_path, terms_given=False):
    """The fail-closed export gate. Exit 2 on a setup fault, 1 on any hit or unused allow entry, 0 when clean."""
    if terms_given:
        print("generic_lint --export: --terms is refused; the export pins the skill's generic rules", file=sys.stderr); return 2
    if not os.path.isdir(root) or not os.listdir(root):
        print(f"generic_lint --export: {root} is not an existing, non-empty folder", file=sys.stderr); return 2
    gits = [os.path.relpath(os.path.join(dp, x), root) for dp, dns, fs in os.walk(root) for x in dns + fs if x == ".git"]
    if gits:
        print(f"generic_lint --export: refused, {gits[0]} in the export tree; copy the tree to an empty folder", file=sys.stderr); return 2
    if not pp:
        print("generic_lint --export: needs the private terms (CI: write them from a secret, set HWFS_PRIVATE_TERMS)", file=sys.stderr); return 2
    try:
        priv, gen = load_terms(pp), load_terms(tp)
    except ValueError as e:
        print(f"generic_lint --export: {e}", file=sys.stderr); return 2
    for label, terms, need in (("private", priv, REQUIRED_PRIVATE), ("generic", gen, REQUIRED_GENERIC)):
        counts = {}
        for g, _ in terms:
            counts[g] = counts.get(g, 0) + 1
        print(f"generic_lint --export: {label} patterns per group: " + (", ".join(f"{g} {c}" for g, c in sorted(counts.items())) or "none"), file=sys.stderr)
        missing = [g for g in need if not counts.get(g)]
        if missing:
            print(f"generic_lint --export: refused, the {label} term file has no pattern in {missing}", file=sys.stderr); return 2
    lines = [x.rstrip("\n") for x in open(allow_path, encoding="utf-8") if x.strip()] if allow_path else []
    all_terms = gen + priv + STRICT_IDS
    strings, reviewed, errs = parse_allow(lines, all_terms)
    for e in errs:
        print(f"generic_lint --export: {e}", file=sys.stderr)
    if errs:
        return 2
    hits, n, used = lint_export(root, all_terms, strings, reviewed)
    if n == 0:
        print("generic_lint --export: no file scanned", file=sys.stderr); return 2
    for rel, ln, g, m in hits:
        print(f"{rel}:{ln}: {g} `{m}`")
    unused = [x for x, c in used.items() if c == 0]
    for x, c in used.items():
        print(f"allow used {c}x: {x}")
    for x in unused:
        print(f"allow entry matched nothing: {x}")
    print(f"generic_lint --export: {len(hits)} hit(s), {len(unused)} unused allow entr{'y' if len(unused) == 1 else 'ies'} in {n} file(s)")
    return 1 if hits or unused else 0


def export_selftest(d, priv, generic):
    """Fixtures for the export gate (synthetic terms and ids only)."""
    import gzip, hashlib, zipfile, zlib
    q = contextlib.redirect_stderr(io.StringIO()); q2 = contextlib.redirect_stdout(io.StringIO())
    e = f"{d}/exp"; os.makedirs(f"{e}/src"); os.makedirs(f"{e}/docs")
    open(f"{e}/src/a.py", "w").write("x = 1  # fixed per CC-999 and D-98, see R1-99 generic: ok\n")
    open(f"{e}/src/b.js", "w").write("// ask qwyzzle\n")
    open(f"{e}/CHANGELOG.md", "w").write("Seed CC-001 and D-01 leak too.\n")
    open(f"{e}/README.md", "w").write("Repo: github.com/zzpublic/pub (public)\nqwy\u00adzzle and qwy\u200bzzle hide; the source\nproject wraps\n")
    open(f"{e}/docs/qwyzzle_notes.txt", "w").write("plain\n")
    open(f"{e}/u16.txt", "wb").write("ask qwyzzle\n".encode("utf-16"))
    z = b"Comment\0\0" + zlib.compress(b"/Users/zz/x")   # generic: ok (fixture)
    open(f"{e}/logo.png", "wb").write(b"\x89PNG\r\n\x1a\n" + len(z).to_bytes(4, "big") + b"zTXt" + z + b"\0\0\0\0")
    fl = zlib.compress(b"BT (made by qwyzzle) Tj ET")
    open(f"{e}/doc.pdf", "wb").write(b"%PDF-1.4\n1 0 obj << /Filter /FlateDecode /Length 9 >> stream\n" + fl + b"\nendstream\n"
                                     b"2 0 obj << /Filter /LZWDecode >> stream\nxx\nendstream\n")
    with zipfile.ZipFile(f"{e}/plate.3mf", "w") as zf:
        zf.writestr("Metadata/model_settings.config", "<config path='C:\\Users\\zz\\ZYXPROJ.scad'/>")   # generic: ok (fixture)
    open(f"{e}/icon.svgz", "wb").write(gzip.compress(b"<svg><title>ZYXPROJ</title></svg>"))
    open(f"{e}/broken.gz", "wb").write(b"\x1f\x8bnot gzip")
    allow = f"{d}/allow.txt"; open(allow, "w").write("url: github.com/zzpublic/pub\n")
    T = load_terms(generic) + load_terms(priv) + STRICT_IDS
    s, r, err = parse_allow([x for x in open(allow).read().split("\n") if x], T); assert not err, err
    h, n, used = lint_export(e, T, s, r); got = {(a, g) for a, _, g, _ in h}
    for want in [("src/a.py", "record_ids_as_citations"), ("src/a.py", "review_ids_as_citations"), ("src/b.js", "people_names"),
                 ("CHANGELOG.md", "record_ids_strict"), ("docs/qwyzzle_notes.txt", "people_names"), ("u16.txt", "people_names"),
                 ("u16.txt", "binary-review"), ("logo.png", "machine_paths"), ("logo.png", "binary-review"), ("doc.pdf!stream", "people_names"),
                 ("doc.pdf!stream", "undecodable"), ("plate.3mf!Metadata/model_settings.config", "project_names"),
                 ("plate.3mf!Metadata/model_settings.config", "machine_paths"), ("icon.svg", "project_names"), ("broken.gz", "undecodable")]:
        assert want in got, (want, sorted(got))
    assert sum(1 for a, _, g, _ in h if a == "README.md" and g == "people_names") == 2, ("a soft hyphen and a zero-width space are seen", h)
    assert ("README.md", "project_names") in got, ("a phrase wrapped over a line break is seen", h)
    assert sum(1 for a, _, g, _ in h if a == "src/a.py" and g == "record_ids_as_citations") == 2, "every match on a line is reported"
    assert used["github.com/zzpublic/pub"] == 1, used
    for bad in ["qwyzzle", "url: qwyzzle", "url: abc", "key: the_qwyzzle_field_name", "url: not a url at all", "binary: logo.png"]:
        assert parse_allow([bad], T)[2], bad
    sha = hashlib.sha256(open(f"{e}/logo.png", "rb").read()).hexdigest()
    s2, r2, _ = parse_allow([f"binary: logo.png {sha}", "binary: gone.png " + "0" * 64], T)
    h2, _, used2 = lint_export(e, T, s2, r2)
    assert ("logo.png", "binary-review") not in {(a, g) for a, _, g, _ in h2} and used2["binary: logo.png"] == 1 and used2["binary: gone.png"] == 0
    open(f"{e}/logo.png", "ab").write(b"x")
    h3, _, _ = lint_export(e, T, s2, r2); assert ("logo.png", "binary-changed") in {(a, g) for a, _, g, _ in h3}, "a changed binary fails its hash"
    with q, q2:
        empty = f"{d}/empty.yaml"; open(empty, "w").write("{}\n")
        assert export_main(e, generic, empty, allow) == 2, "an empty private file is refused"
        part = f"{d}/part.yaml"; open(part, "w").write("people_names: ['(?i)qwyzzle']\n")
        assert export_main(e, generic, part, allow) == 2, "a private file without every promised group is refused"
        bad = f"{d}/bad.yaml"; open(bad, "w").write("people_names: qwyzzle\n")
        assert export_main(e, generic, bad, allow) == 2, "a group written as a string is refused"
        assert export_main(e, generic, priv, allow, terms_given=True) == 2, "--terms is refused in export mode"
        assert export_main(f"{d}/nope", generic, priv, allow) == 2
        os.makedirs(f"{d}/emptydir"); assert export_main(f"{d}/emptydir", generic, priv, None) == 2, "an empty export folder is refused"
        os.makedirs(f"{e}/sub"); open(f"{e}/sub/.git", "w").write("gitdir: x\n")
        assert export_main(e, generic, priv, allow) == 2, "a .git file anywhere is refused"
    os.remove(f"{e}/sub/.git")


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
        blocks = 0; inside = False; prev = None
        for n, line in enumerate(open(f, encoding="utf-8", errors="replace"), 1):
            if line.lstrip().startswith(BEGIN):                                # a marker opens a line; code or prose that quotes it is not a block
                blocks += 1; inside = True
                if blocks > 1:
                    hits.append((rel, n, "worked-example", "a second worked-example block (one per file)"))
            elif line.lstrip().startswith(END):
                inside = False
            if "generic: ok" in line:
                prev = None; continue
            if prev is not None:                                                # a name split over a line break ("source" / "project")
                j = prev + " " + line.strip()
                for g, rx in terms:
                    if g.endswith("_names"):
                        hits.extend((rel, n, g, m.group(0)) for m in rx.finditer(j) if m.start() < len(prev) < m.end())
            prev = line.rstrip()
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
    priv = f"{d}/private.yaml"; open(priv, "w").write("people_names:\n  - '(?i)qwyzzle'\nproject_names:\n  - '\\bZYXPROJ\\b'\nproject_ids:\n  - '\\b99887766\\b'\nparts_and_refdes:\n  - '\\bZQX-9\\b'\n")   # a synthetic private term
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
    print("selftest OK (term groups, whole-repo file set, worked-example block keeps numbers not names, one block per file, history keeps numbers, generic: ok marker, private terms merged from outside the repo, a missing explicit path fails, export mode fail-closed: empty or patternless private file, missing or empty folder, .git refused; every match per line; seed ids; zip / 3MF / gzip / svgz members and PDF Flate streams decoded, an undecodable part a hit; Unicode-normalised and cross-line matches; typed allow entries with no term inside; binaries allowed by sha256, a changed or unused entry fails)")
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
        return export_main(os.path.abspath(a.export), os.path.join(skill_default, "scripts", "generic_lint_terms.yaml"), pp, a.allow, terms_given=bool(a.terms))
    if not pp:
        print("generic_lint: note: no private term file; generic patterns only (set HWFS_PRIVATE_TERMS)", file=sys.stderr)
    files = [os.path.abspath(f) for f in a.files] or default_files(a.skill)
    try:
        terms = load_terms(tp, *([pp] if pp else []))
    except ValueError as e:
        print(f"generic_lint: {e}", file=sys.stderr); return 2
    hits = lint(files, terms, a.skill)
    for rel, n, g, m in hits:
        print(f"{rel}:{n}: {g} `{m}`" if g != "MISSING" else f"{rel}: MISSING")
    print(f"generic_lint: {len(hits)} hit(s) in {len(files)} file(s)")
    return 2 if any(g == "MISSING" for _, _, g, _ in hits) else (1 if hits else 0)


if __name__ == "__main__":
    sys.exit(main(sys.argv))
