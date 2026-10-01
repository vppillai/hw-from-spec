#!/usr/bin/env python3
"""scripts/step2stl.py — bring an EXISTING CAD body (a STEP the owner already has) into the mech chain of record as a canonical STL + provenance.

  scripts/step2stl.py <part.step> --out out/mechanical/case/<target>/stl/<piece>.stl [--tag V|K] [--source-note TEXT] [--tolerance 0.01]
      Converts with the first available route: (1) `cadquery` in the venv (`pip install cadquery`), (2) FreeCAD's CLI (`FreeCADCmd` /
      `freecadcmd` / `freecad.cmd` on PATH), (3) an existing STL given instead of a STEP is only canonicalised. OpenSCAD cannot read STEP.
      Writes the CANONICAL binary STL (triangles sorted, normals from the float32 vertices — the md5 IS the geometry, SKILL.md §8.1 item 3) and
      the sidecar `<piece>.stl.provenance.json` {source, source_md5, tag, converter, tolerance, stl_md5, signature, date}; prints the decision row
      the imported body needs (SKILL.md §8 "imported body": a generated-only exception with its chain of record) and the two commands that give
      it a census and a print_dfm record like a generated body. Exit 2 when no converter is available (the routes are printed).
  scripts/step2stl.py --canonical <in.stl> --out <out.stl>      re-export any STL canonically (ascii or binary in)
  scripts/step2stl.py --selftest                                 pure python: canonical writer determinism, reader, provenance, decision row text
"""
import argparse, datetime, hashlib, json, math, os, re, shutil, struct, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, HERE)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def read_stl(path):
    """-> list of triangles [((x,y,z),(x,y,z),(x,y,z))] from a binary or ascii STL."""
    data = open(path, "rb").read()
    if len(data) >= 84 and not data[:5].lower() == b"solid" or (len(data) >= 84 and len(data) == 84 + 50 * struct.unpack("<I", data[80:84])[0]):
        n = struct.unpack("<I", data[80:84])[0]; tris = []
        for i in range(n):
            o = 84 + 50 * i; v = struct.unpack("<12f", data[o:o + 48])
            tris.append((tuple(v[3:6]), tuple(v[6:9]), tuple(v[9:12])))
        return tris
    verts = [tuple(float(x) for x in m.groups()) for m in re.finditer(rb"vertex\s+(\S+)\s+(\S+)\s+(\S+)", data)]
    return [tuple(verts[i:i + 3]) for i in range(0, len(verts) - len(verts) % 3, 3)]


def _f32(x):
    return struct.unpack("<f", struct.pack("<f", x))[0]


def canonical_stl(tris):
    """Binary STL bytes: vertices rounded to float32, each triangle rotated so its lexicographically smallest vertex comes first (winding kept),
    triangles sorted, normal from the float32 vertices. Two exports of the same geometry give the same bytes."""
    rows = []
    for t in tris:
        t = [tuple(_f32(c) for c in v) for v in t]
        k = min(range(3), key=lambda i: t[i]); t = t[k:] + t[:k]
        rows.append(tuple(t))
    rows.sort()
    out = [struct.pack("<80sI", b"hw-from-spec canonical STL", len(rows))]
    for a, b, c in rows:
        u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]; L = math.sqrt(sum(x * x for x in n)) or 1.0
        out.append(struct.pack("<12fH", *(x / L for x in n), *a, *b, *c, 0))
    return b"".join(out)


def signature(tris):
    """volume / area / bbox / facets rounded 1e-3 — the geometry signature beside the md5 (a moved md5 with an unchanged signature is not geometry)."""
    vol = area = 0.0; lo = [math.inf] * 3; hi = [-math.inf] * 3
    for a, b, c in tris:
        u = [b[i] - a[i] for i in range(3)]; v = [c[i] - a[i] for i in range(3)]
        n = [u[1] * v[2] - u[2] * v[1], u[2] * v[0] - u[0] * v[2], u[0] * v[1] - u[1] * v[0]]
        area += 0.5 * math.sqrt(sum(x * x for x in n)); vol += sum(a[i] * n[i] for i in range(3)) / 6.0
        for p in (a, b, c):
            for i in range(3):
                lo[i] = min(lo[i], p[i]); hi[i] = max(hi[i], p[i])
    return dict(vol=round(abs(vol), 3), area=round(area, 3), bbox=[round(x, 3) for x in lo + hi], facets=len(tris))


def convert_cadquery(step, tol):
    import cadquery as cq  # noqa: F401 — optional
    shape = cq.importers.importStep(step).val()
    verts, faces = shape.tessellate(tol, 0.1)
    return [tuple(tuple(verts[i].toTuple()) for i in f) for f in faces], f"cadquery {cq.__version__}"


def convert_freecad(step, tol):
    exe = next((e for e in ("FreeCADCmd", "freecadcmd", "freecad.cmd") if shutil.which(e)), None)
    if not exe:
        raise FileNotFoundError("no FreeCAD CLI on PATH")
    with tempfile.TemporaryDirectory() as d:
        tmp = os.path.join(d, "fc.stl"); scr = os.path.join(d, "conv.py")
        open(scr, "w").write(f"import Part, Mesh\ns = Part.read({step!r})\nMesh.Mesh(s.tessellate({tol})).write({tmp!r})\n")
        subprocess.run([exe, scr], check=True, capture_output=True)
        return read_stl(tmp), f"{exe} (Part.tessellate {tol})"


ROUTES = """step2stl: no converter available. Routes (pick one, record it in the decision row):
  1. pip install cadquery          into the project venv (.venv/bin/python -m pip install cadquery), rerun
  2. FreeCAD CLI on PATH           (FreeCADCmd / freecadcmd / freecad.cmd), rerun — the script calls Part.read + Mesh.write for you
  3. export an STL from your CAD   (fine tessellation, mm), then: scripts/step2stl.py --canonical <export.stl> --out <piece>.stl --source <part.step>
OpenSCAD cannot read STEP."""


def decision_row(piece, prov, out_rel):
    return (f"| CC-nnn | {prov['date']} | OPEN | imported body `{piece}` (generated-only exception, SKILL §2 / §8) | "
            f"Body of record `{out_rel}` is NOT generated from design/case.yaml: imported from `{prov['source']}` (md5 {prov['source_md5'][:8]}, tag [{prov['tag']}]) "
            f"via {prov['converter']}, tolerance {prov['tolerance']}; canonical STL md5 {prov['stl_md5'][:8]}, signature vol {prov['signature']['vol']} / area {prov['signature']['area']} / "
            f"facets {prov['signature']['facets']}; provenance `{out_rel}.provenance.json`. Chain of record: a changed source md5 or signature = a new row. | "
            f"the owner's CAD is the geometry of record; the census + print_dfm records gate it like a generated body |")


def run(src, out, tag, note, tol, canonical_only=False, source=None):
    tris = conv = None
    if canonical_only or src.lower().endswith(".stl"):
        tris, conv = read_stl(src), "canonicalised from an STL export"
    else:
        for fn in (convert_cadquery, convert_freecad):
            try:
                tris, conv = fn(src, tol); break
            except Exception as e:  # noqa: BLE001 — try the next route; the last failure is reported
                last = e
        if tris is None:
            print(ROUTES + f"\n  (last error: {last})", file=sys.stderr); return 2
    if not tris:
        print(f"step2stl: {src} yielded no triangles", file=sys.stderr); return 1
    os.makedirs(os.path.dirname(os.path.abspath(out)) or ".", exist_ok=True)
    data = canonical_stl(tris); open(out, "wb").write(data)
    origin = source or src
    prov = dict(source=origin, source_md5=md5(origin), tag=tag, note=note or "", converter=conv, tolerance=tol, stl=out, stl_md5=hashlib.md5(data).hexdigest(),
                signature=signature(tris), date=datetime.date.today().isoformat())
    json.dump(prov, open(out + ".provenance.json", "w"), indent=1)
    rel = lambda q: q if os.path.relpath(q).startswith("..") else os.path.relpath(q)
    out, tgt_dir = rel(out), rel(os.path.dirname(os.path.dirname(os.path.abspath(out)))); prov["source"] = rel(prov["source"]); prov["stl"] = out
    piece = os.path.splitext(os.path.basename(out))[0]
    print(f"{out}: {len(tris)} facets, md5 {prov['stl_md5'][:8]}, signature {prov['signature']}; provenance {out}.provenance.json ({conv})")
    print("\nDecision row to append (OPEN until the owner confirms the import; CC-nnn = next free id):\n" + decision_row(piece, prov, out))
    print(f"\nRecords like a generated body:\n  scripts/thin_wall_census.py {out} --target <t> --json {tgt_dir}/census/{piece}.json\n  scripts/print_dfm.py --process <print_targets.<t>.dfm_process> --out {tgt_dir}/dfm {out}")
    return 0


def selftest():
    d = tempfile.mkdtemp(prefix="hwfs_s2s_")
    tris = [((0, 0, 0), (1, 0, 0), (0, 1, 0)), ((0, 0, 1), (0, 1, 1), (1, 0, 1)), ((1, 0, 0), (1, 1, 0), (0, 1, 0))]
    a = canonical_stl(tris); b = canonical_stl([tris[2], tris[0], tris[1]]); c = canonical_stl([(t[1], t[2], t[0]) for t in tris])
    assert a == b == c, "order and vertex rotation must not change the bytes"
    assert canonical_stl([tris[0], tris[1], ((1, 0, 0), (0, 1, 0), (1, 1, 0))]) != a, "flipped winding is another geometry"
    p = os.path.join(d, "t.stl"); open(p, "wb").write(a)
    back = read_stl(p); assert len(back) == 3 and canonical_stl(back) == a, "binary round trip"
    asc = os.path.join(d, "a.stl"); open(asc, "w").write("solid a\n" + "".join(f"facet normal 0 0 1\nouter loop\nvertex {v[0]} {v[1]} {v[2]}\nvertex {w[0]} {w[1]} {w[2]}\nvertex {x[0]} {x[1]} {x[2]}\nendloop\nendfacet\n" for v, w, x in tris) + "endsolid a\n")
    assert canonical_stl(read_stl(asc)) == a, "ascii round trip"
    sig = signature(tris); assert sig["facets"] == 3 and sig["bbox"] == [0, 0, 0, 1, 1, 1] and abs(sig["area"] - 1.5) < 1e-6, sig
    out = os.path.join(d, "o", "piece.stl")
    import contextlib, io
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        ok = run(asc, out, "K", "owner's export", 0.01) == 0 and os.path.exists(out + ".provenance.json")
        no_conv = run(os.path.join(d, "none.step"), out, "V", "", 0.01)
    assert ok
    prov = json.load(open(out + ".provenance.json")); assert prov["source_md5"] == md5(asc) and prov["tag"] == "K" and prov["stl_md5"] == hashlib.md5(a).hexdigest()
    row = decision_row("piece", prov, "o/piece.stl"); assert row.count("|") == 7 and "generated-only exception" in row and prov["stl_md5"][:8] in row
    assert _has_converter() or no_conv == 2, "no converter -> exit 2 with the routes"
    print("selftest OK (canonical writer determinism, winding, binary + ascii readers, signature, provenance sidecar, decision row, exit 2 without a converter)")
    return 0


def _has_converter():
    try:
        import cadquery  # noqa: F401
        return True
    except ImportError:
        return any(shutil.which(e) for e in ("FreeCADCmd", "freecadcmd", "freecad.cmd"))


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("src", nargs="?"); ap.add_argument("--out"); ap.add_argument("--tag", default="K", choices=["V", "K"], help="V = measured / vendor drawing, K = owner-stated")
    ap.add_argument("--source-note", default=""); ap.add_argument("--tolerance", type=float, default=0.01); ap.add_argument("--canonical", metavar="STL"); ap.add_argument("--source", help="with --canonical: the CAD file the STL was exported from")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    if a.canonical:
        sys.exit(run(a.canonical, a.out or a.canonical, a.tag, a.source_note, a.tolerance, canonical_only=True, source=a.source))
    if not (a.src and a.out):
        ap.error("give <part.step> --out <piece.stl> (or --canonical <in.stl> --out <out.stl>)")
    if not os.path.exists(a.src):
        print(f"step2stl: no such file: {a.src}", file=sys.stderr); sys.exit(2)
    sys.exit(run(a.src, a.out, a.tag, a.source_note, a.tolerance))
