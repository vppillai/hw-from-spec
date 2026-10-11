#!/usr/bin/env python3
"""scripts/vendor_gate.py — the vendor checker's verdict, read by a script: every STL of record has a clean API reply and six clean captures (stdlib only).

  scripts/vendor_gate.py <checks dir | file>... --stl <stl>...
  scripts/vendor_gate.py --newest '<glob>' --stl <stl>...        # `--newest` is the first argument and takes exactly one glob
      `--newest` picks the newest round folder among the glob's directories by version sort (`_r2` < `_r10`, a later date dir later),
      so a gate line survives a round folder that moves to `_r<n>`; no match exits 2 (a pin that silently passes an empty folder is no gate).
      A round folder name ends in a digit (`<round>`, `<round>_r<n>`). A suffixed sibling (`<round>_r10_corner`, `<round>_bisect`) is
      skipped, so a probe, bisect or corner folder never outranks the round; slabs and probes never get their own `_r<n>` folder.
  scripts/vendor_gate.py --help                                   # this text, exit 0
      For every STL (md5 of record, first 8 hex = md5-8) the files given (directories are listed, not walked) must hold:
      - the analysis reply: `<md5-8>_analyze.json` or the saved `*<md5-8>*getFileAnalyzeResult*` network response (JLC3DP format).
        It passes when `success` is true, every `parseStatus` reads 2 (analysis complete), every `thinWall` reads false (at least one),
        `modelBrokenFace` reads 0, `errorMsg` is empty, and a `fileMd5` (base64 of the md5 bytes) equals the STL's md5.
      - six captures `*<md5-8>*_<view>.png`, views az000 az090 az180 az270 poleA poleB, each 0 yellow / 0 red by
        `heatmap_count.py` (same classify, same legend / tool-bar strips).
      Prints one line per missing or failing item; exit 1 when any, 0 when every STL passes, 2 on usage or a missing STL.
  scripts/vendor_gate.py --selftest

A DOM read of the quote page is not a verdict; only the reply after parseStatus 2 is (references/dfm-printed-enclosure.md §13).
"""
import base64, contextlib, hashlib, io, json, os, sys, tempfile, zlib

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from heatmap_count import count, write_png  # noqa: E402

VIEWS = ("az000", "az090", "az180", "az270", "poleA", "poleB")


def newest(pattern):
    """The newest directory among the glob matches by version sort over the whole path (digits compare as numbers); None when nothing matches."""
    import glob, re
    key = lambda p: [int(s) if s.isdigit() else s for s in re.split(r"(\d+)", p)]
    dirs = sorted((m for m in glob.glob(pattern) if os.path.isdir(m) and os.path.basename(m)[-1:].isdigit()), key=key)   # a round folder ends in a digit
    return dirs[-1] if dirs else None


def walk(o, key):
    """Every value of `key` anywhere in the JSON tree."""
    if isinstance(o, dict):
        for k, v in o.items():
            if k == key:
                yield v
            yield from walk(v, key)
    elif isinstance(o, list):
        for v in o:
            yield from walk(v, key)


def reply_problems(path, md5):
    """-> problem list of one saved analysis reply against the STL md5 (hex)."""
    try:
        d = json.load(open(path, encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"cannot read ({e})"]
    bad = []
    if d.get("success") is not True:
        bad.append(f"success {d.get('success')!r}")
    ps = list(walk(d, "parseStatus"))
    if not ps or any(p != 2 for p in ps):
        bad.append(f"parseStatus {ps} (2 = analysis complete; a read before 2 is no verdict)")
    tw = list(walk(d, "thinWall"))
    if not tw or any(t is not False for t in tw):
        bad.append(f"thinWall {tw}")
    if any(v not in (0, None) for v in walk(d, "modelBrokenFace")):
        bad.append(f"modelBrokenFace {list(walk(d, 'modelBrokenFace'))}")
    if any(v for v in walk(d, "errorMsg")):
        bad.append(f"errorMsg {list(walk(d, 'errorMsg'))}")
    fm = []
    for v in walk(d, "fileMd5"):
        try:
            fm.append(base64.b64decode(v).hex())
        except (ValueError, TypeError):
            fm.append(str(v))
    if md5 not in fm:
        bad.append(f"fileMd5 {fm} is not the STL md5 {md5[:8]} (the reply belongs to another file)")
    return bad


def gate(paths, stls):
    """-> problem lines over every STL."""
    files = []
    for p in paths:
        files += [os.path.join(p, f) for f in sorted(os.listdir(p))] if os.path.isdir(p) else [p]
    bad = []
    for stl in stls:
        md5 = hashlib.md5(open(stl, "rb").read()).hexdigest(); m8 = md5[:8]; tag = f"{os.path.basename(stl)} ({m8})"
        mine = [f for f in files if m8 in os.path.basename(f)]
        replies = [f for f in mine if os.path.basename(f) == f"{m8}_analyze.json" or "getFileAnalyzeResult" in os.path.basename(f)]
        if not replies:
            bad.append(f"{tag}: no analysis reply ({m8}_analyze.json or *{m8}*getFileAnalyzeResult*)")
        for r in replies:
            bad += [f"{tag}: {os.path.basename(r)}: {b}" for b in reply_problems(r, md5)]
        for v in VIEWS:
            caps = [f for f in mine if f.endswith(f"_{v}.png")]
            if not caps:
                bad.append(f"{tag}: no capture *{m8}*_{v}.png")
            for c in caps:
                try:
                    y, r = count(c)
                except (OSError, ValueError, zlib.error) as e:
                    bad.append(f"{tag}: {os.path.basename(c)}: cannot read ({e})"); continue
                if y or r:
                    bad.append(f"{tag}: {os.path.basename(c)}: yellow {y} red {r}")
    return bad


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_vg_")
    stl = os.path.join(d, "body.stl"); open(stl, "wb").write(b"solid b\nendsolid b\n")
    md5 = hashlib.md5(open(stl, "rb").read()).hexdigest(); m8 = md5[:8]; b64 = base64.b64encode(bytes.fromhex(md5)).decode()
    def reply(**kw):
        vo = dict(parseStatus=2, thinWall=False, errorMsg=None, drawFileVOS=[dict(fileMd5=b64)]); vo.update(kw)
        json.dump(dict(success=True, data=dict(parseStatus=2, modelBrokenFace=0, modelAnalysisVO=vo)), open(os.path.join(d, f"{m8}_analyze.json"), "w"))
    grey = lambda x, y: (160, 160, 160)
    reply()
    assert any("no capture" in b for b in gate([d], [stl])), "captures missing"
    for v in VIEWS:
        write_png(os.path.join(d, f"body_{m8}_heatmap_{v}.png"), 40, 30, grey)
    assert gate([d], [stl]) == [], gate([d], [stl])
    write_png(os.path.join(d, f"body_{m8}_heatmap_poleB.png"), 40, 30, lambda x, y: (255, 0, 0) if x < 5 and y < 5 else (160, 160, 160))
    bad = gate([d], [stl]); assert len(bad) == 1 and "poleB.png: yellow 0 red 25" in bad[0], bad
    write_png(os.path.join(d, f"body_{m8}_heatmap_poleB.png"), 40, 30, grey)
    for kw, word in ((dict(thinWall=True), "thinWall"), (dict(parseStatus=1), "parseStatus"), (dict(errorMsg="bad mesh"), "errorMsg"),
                     (dict(drawFileVOS=[dict(fileMd5=base64.b64encode(b"\0" * 16).decode())]), "fileMd5")):
        reply(**kw); bad = gate([d], [stl]); assert len(bad) == 1 and word in bad[0], (kw, bad)
    os.remove(os.path.join(d, f"{m8}_analyze.json")); assert any("no analysis reply" in b for b in gate([d], [stl]))
    reply(); assert gate([os.path.join(d, f) for f in os.listdir(d)], [stl]) == [], "files given one by one"
    q = os.path.join(d, "quotes")
    for sub in ("2026-10-09/jlc_dfm_v4.0", "2026-10-10/jlc_dfm_v4.0_r2", "2026-10-10/jlc_dfm_v4.0_r10", "2026-10-10/jlc_dfm_v4.0_r3",
                "2026-10-10/jlc_dfm_v4.0_r10_corner", "2026-10-10/jlc_dfm_bisect", "2026-10-09/jlc_dfm_v4.0_r12"):
        os.makedirs(os.path.join(q, sub))
    open(os.path.join(q, "2026-10-10/jlc_dfm_v4.0_r11"), "w").write("a file, not a round")
    assert newest(os.path.join(q, "*/jlc_dfm_*")).endswith("2026-10-10/jlc_dfm_v4.0_r10"), newest(os.path.join(q, "*/jlc_dfm_*"))
    assert newest(os.path.join(q, "*/nothing_*")) is None
    with contextlib.redirect_stderr(io.StringIO()):
        assert main(["vendor_gate.py", "--newest", os.path.join(q, "*/nothing_*"), "--stl", stl]) == 2, "no round folder = 2"
    for f in os.listdir(d):
        if m8 in f:
            os.rename(os.path.join(d, f), os.path.join(q, "2026-10-10/jlc_dfm_v4.0_r10", f))
    with contextlib.redirect_stdout(io.StringIO()):
        assert main(["vendor_gate.py", "--newest", os.path.join(q, "*/jlc_dfm_*"), "--stl", stl]) == 0, "the newest round folder passes"
        assert main(["vendor_gate.py", "--help"]) == 0, "--help exits 0"
        with contextlib.redirect_stderr(io.StringIO()):
            assert main(["vendor_gate.py", "--newest", "a", "b", "--stl", stl]) == 2, "two globs = 2"
    os.makedirs(os.path.join(q, "2026-10-11/jlc_dfm_v4.0_r1"))
    assert newest(os.path.join(q, "*/jlc_dfm_*")).endswith("2026-10-11/jlc_dfm_v4.0_r1"), "a later date dir wins over a higher _r"
    with contextlib.redirect_stderr(io.StringIO()):
        assert main(["vendor_gate.py", d]) == 2 and main(["vendor_gate.py", d, "--stl", os.path.join(d, "nope.stl")]) == 2, "usage / missing STL = 2"
    print("vendor_gate selftest OK: clean reply + six grey captures pass; a red capture, a missing capture, thinWall true, parseStatus not 2, an errorMsg, a foreign fileMd5 and a missing reply fail; usage exits 2; --newest picks _r10 over _r3 by version sort, skips a suffixed sibling and a bisect folder, prefers a later date dir, and exits 2 on no match; --help exits 0")
    return 0


def main(argv):
    if argv[1:] == ["--selftest"]:
        return selftest()
    if "--help" in argv[1:] or "-h" in argv[1:]:
        print(__doc__); return 0
    if "--stl" not in argv:
        print(__doc__, file=sys.stderr); return 2
    i = argv.index("--stl"); paths, stls = argv[1:i], argv[i + 1:]
    if paths[:1] == ["--newest"]:
        if len(paths) != 2:
            print("vendor_gate: --newest takes one glob", file=sys.stderr); return 2
        folder = newest(paths[1])
        if folder is None:
            print(f"vendor_gate: no round folder matches {paths[1]}", file=sys.stderr); return 2
        print(f"vendor gate: newest round folder {folder}"); paths = [folder]
    if not paths or not stls or any(not os.path.exists(p) for p in paths + stls):
        print("vendor_gate: give existing checks dirs / files and --stl files" + "".join(f"\n  missing: {p}" for p in paths + stls if not os.path.exists(p)), file=sys.stderr)
        return 2
    bad = gate(paths, stls)
    for b in bad:
        print("VENDOR GATE:", b)
    print(f"vendor gate: {len(stls)} STL(s), {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
