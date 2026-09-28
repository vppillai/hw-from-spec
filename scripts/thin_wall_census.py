#!/usr/bin/env python3
"""scripts/thin_wall_census.py — the thin-wall census that gates a printed body (references/dfm-printed-enclosure.md §2; rows: templates/CENSUS_GATE_ROWS.md).

  scripts/thin_wall_census.py PIECE.stl [--gate 1.2] [--void-gate 1.2] [--samples 60000] [--cell 3.0] [--self-hit 0.02] [--red 0.5]
                              [--boxes BOXES.json] [--box-min 1.0] [--json OUT.json]
      Every surface sample casts a ray INWARD (hit distance = wall thickness) and OUTWARD (hit within the void gate = a slot / slit / groove /
      engraved stroke narrower than the gate). Samples below `gate - 0.05` are grid-clustered (26-neighbour cells) and each cluster is CLASSIFIED
      by the angle between the sample face and the hit face: < 30 deg = WALL (a skin whose thickness IS the hit distance), else WEDGE (chamfer,
      ramp, rail flank — thickness grows away from the edge). WALL clusters below the gate and VOID clusters below the void gate are FAIL;
      wedges are listed (each must be a chamfer cut INTO a wall — a free-standing wedge is red at the vendor). A cluster mostly inside a --boxes
      rectangle (legend lands, [[x0, y0, x1, y1], ...]) gates at --box-min instead. Prints the rows, writes --json, exit 1 on any FAIL.
      Needs trimesh + numpy at run time.
  scripts/thin_wall_census.py --gate-dir DIR [DIR ...]
      PURE gate for the adopt list: every DIR/*.json (written by --json) must name an STL whose md5 equals `stl_md5` and carry an empty `fails`
      list. Recomputes nothing; proves the record matches the mesh of record. Exit 1 on any problem.
  scripts/thin_wall_census.py --selftest
      pure python core (classification, clustering, gating, the pure gate on a temp dir); with trimesh installed also a 1.0 mm plate (one WALL
      cluster, FAIL at 1.2), a 45 deg prism (wedges only) and a 2.0 mm plate (0 FAIL).

Rules baked in (measured on the source project, references/dfm-printed-enclosure.md): cluster below `gate - 0.05` (at the gate itself the nominal
walls sampled 0.01 under join every region into one cluster); a ray nudged inside a face hits that face at ~0.000 — discard hits closer than
--self-hit; a WALL cluster is a wall whatever the yaml calls it (lip, land, skin, floor, ring); an outward hit whose faces are >= 30 deg apart is a
re-entrant corner, not a slot. The 141 mm x 0.88 mm lip that cracked on five parts was a WALL cluster filed under "knife edges".
"""
import argparse, hashlib, json, math, os, sys

WALL_DEG = 30.0
BINS = (0, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, math.inf)


# ---------------------------------------------------------------- pure-python core (selftested) -----------------------------------------------
def first_hit_beyond(dists, self_hit):
    for x in dists:
        if x > self_hit:
            return x
    return math.inf


def histogram(values, bins=BINS):
    h = {f"{a}-{b}": 0 for a, b in zip(bins[:-1], bins[1:])}
    for v in values:
        for a, b in zip(bins[:-1], bins[1:]):
            if a <= v < b or (v == b == math.inf):
                h[f"{a}-{b}"] += 1; break
    return h


def grid_groups(points, cell):
    """26-neighbour union-find over grid cells -> list of index lists."""
    keys = [tuple(math.floor(c / cell) for c in p) for p in points]
    uniq = {k: i for i, k in enumerate(sorted(set(keys)))}
    par = list(range(len(uniq)))

    def f(x):
        while par[x] != x:
            par[x] = par[par[x]]; x = par[x]
        return x
    for k, i in uniq.items():
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for dz in (-1, 0, 1):
                    j = uniq.get((k[0] + dx, k[1] + dy, k[2] + dz))
                    if j is not None:
                        par[f(i)] = f(j)
    groups = {}
    for i, k in enumerate(keys):
        groups.setdefault(f(uniq[k]), []).append(i)
    return list(groups.values())


def in_box_frac(points, boxes):
    if not boxes or not points:
        return 0.0
    return sum(any(b[0] <= p[0] <= b[2] and b[1] <= p[1] <= b[3] for b in boxes) for p in points) / len(points)


def cluster_rows(points, values, angles, cell=3.0, red=0.5, boxes=None):
    """Thin samples -> rows {n, tmin, tmed, tmed_wall, n_red, wall_frac, cls, span, bbox, in_box_frac}; WALL rows first, biggest first."""
    rows = []
    for idx in grid_groups(points, cell):
        pp = [points[i] for i in idx]; tt = sorted(values[i] for i in idx); aa = [angles[i] for i in idx]
        wall = [values[i] for i in idx if angles[i] < WALL_DEG]
        wf = len(wall) / len(idx); tw = sorted(wall) if wall else tt
        lo = [min(p[i] for p in pp) for i in range(3)]; hi = [max(p[i] for p in pp) for i in range(3)]
        rows.append(dict(n=len(idx), tmin=round(tt[0], 3), tmed=round(tt[len(tt) // 2], 2), tmed_wall=round(tw[len(tw) // 2], 2),
                         n_red=sum(t < red for t in tt), wall_frac=round(wf, 2), cls="wall" if wf >= 0.5 else "wedge",
                         span=round(max(h - l for l, h in zip(lo, hi)), 1), bbox=[round(x, 1) for x in lo + hi],
                         in_box_frac=round(in_box_frac(pp, boxes), 2)))
    rows.sort(key=lambda r: (r["cls"] != "wall", -r["n"]))
    return rows


def void_rows(points, gaps, cell=3.0, boxes=None):
    rows = []
    for idx in grid_groups(points, cell):
        pp = [points[i] for i in idx]; gg = sorted(gaps[i] for i in idx)
        lo = [min(p[i] for p in pp) for i in range(3)]; hi = [max(p[i] for p in pp) for i in range(3)]
        rows.append(dict(n=len(idx), gmin=round(gg[0], 3), gmed=round(gg[len(gg) // 2], 2), span=round(max(h - l for l, h in zip(lo, hi)), 1),
                         bbox=[round(x, 1) for x in lo + hi], in_box_frac=round(in_box_frac(pp, boxes), 2)))
    rows.sort(key=lambda r: -r["n"])
    return rows


def gate_rows(clusters, voids, gate, void_gate, box_min=None):
    """FAIL strings: every WALL cluster below its gate, every VOID cluster below the void gate. Wedges never fail (they are listed)."""
    fails = []
    for c in clusters:
        if c["cls"] != "wall":
            continue
        g = box_min if (box_min is not None and c["in_box_frac"] >= 0.5) else gate
        if c["tmed_wall"] < g - 1e-9:
            fails.append(f"WALL {c['tmed_wall']:.2f} (min {c['tmin']:.2f}) < {g} span {c['span']} bbox {c['bbox']}")
    for v in voids:
        g = box_min if (box_min is not None and v["in_box_frac"] >= 0.5) else void_gate
        if v["gmed"] < g - 1e-9:
            fails.append(f"VOID {v['gmed']:.2f} (min {v['gmin']:.2f}) < {g} span {v['span']} bbox {v['bbox']}")
    return fails


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def pure_gate(dirs):
    """Every DIR/*.json: its `stl` (relative to cwd, else to the json's dir) exists, md5 == stl_md5, fails == []. Returns the problem list."""
    bad = []; n = 0
    for d in dirs:
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not name.endswith(".json"):
                continue
            jp = os.path.join(d, name); n += 1
            try:
                r = json.load(open(jp))
            except Exception as e:  # noqa: BLE001 — a corrupt record is a gate failure, not a traceback
                bad.append(f"{jp}: unreadable ({e})"); continue
            stl = r.get("stl", "")
            cand = [stl, os.path.join(os.path.dirname(jp), stl)]
            path = next((p for p in cand if p and os.path.exists(p)), None)
            if path is None:
                bad.append(f"{jp}: STL {stl!r} not found"); continue
            if md5_of(path) != r.get("stl_md5"):
                bad.append(f"{jp}: census of {str(r.get('stl_md5', '?'))[:8]} but the STL of record is {md5_of(path)[:8]} — rerun the census")
            if r.get("fails"):
                bad.append(f"{jp}: {len(r['fails'])} FAIL cluster(s): " + "; ".join(r["fails"])[:300])
    if n == 0:
        bad.append("no census JSON found in " + ", ".join(dirs))
    return bad


# ---------------------------------------------------------------- mesh wrapper (trimesh + numpy) ------------------------------------------------
def need(*mods):
    import importlib
    out = []
    for name in mods:
        try:
            out.append(importlib.import_module(name))
        except ImportError:
            sys.exit(f"thin_wall_census: this mode needs {', '.join(mods)} ({name} is not installed): pip install {' '.join(mods)}")
    return out


def first_hits(m, origins, dirs, nrm, self_hit, np):
    """Per ray: (distance, angle between the SAMPLE face and the hit face) of the first hit beyond self_hit; inf/nan when the ray leaves the piece.
    0 deg = the hit face is parallel and facing the sample face (a wall for inward rays, a slot for outward rays)."""
    loc, idx_ray, idx_tri = m.ray.intersects_location(origins, dirs, multiple_hits=True)
    loc = np.asarray(loc, dtype=float).reshape(-1, 3)                                    # no hit at all (a convex plate, outward) -> shape (0,)
    d = np.linalg.norm(loc - origins[idx_ray], axis=1)
    per = {}
    for r, x, t in zip(idx_ray.tolist(), d.tolist(), idx_tri.tolist()):
        per.setdefault(r, []).append((x, t))
    n = len(origins); dist = np.full(n, np.inf); ang = np.full(n, np.nan)
    for r, hits in per.items():
        for x, t in sorted(hits):
            if x > self_hit:
                dist[r] = x
                ang[r] = math.degrees(math.acos(float(np.clip(-np.dot(nrm[r], m.face_normals[t]), -1.0, 1.0))))
                break
    return dist, ang


def census(stl, samples, gate, void_gate, cell, self_hit, red, boxes, box_min, out_json, seed=0):
    np, trimesh = need("numpy", "trimesh")
    np.random.seed(seed)
    m = trimesh.load(stl, force="mesh")
    thr = round(gate - 0.05, 3)
    pts, fid = trimesh.sample.sample_surface(m, samples); nrm = m.face_normals[fid]
    th, ang = first_hits(m, pts - nrm * 1e-3, -nrm, nrm, self_hit, np)                  # inward: wall thickness; hit face vs sample face
    gap, oang = first_hits(m, pts + nrm * 1e-3, nrm, nrm, self_hit, np)                 # outward: void width; a re-entrant corner is not a slot
    gap = np.where(np.isnan(oang) | (oang >= WALL_DEG), np.inf, gap)
    ang = np.where(np.isnan(ang), 180.0, ang)
    P = pts.tolist(); T = th.tolist(); A = ang.tolist(); G = gap.tolist()
    thin = [i for i in range(samples) if T[i] < thr]
    clusters = cluster_rows([P[i] for i in thin], [T[i] for i in thin], [A[i] for i in thin], cell, red, boxes)
    vt = [i for i in range(samples) if G[i] < void_gate]
    voids = void_rows([P[i] for i in vt], [G[i] for i in vt], cell, boxes)
    fails = gate_rows(clusters, voids, gate, void_gate, box_min if boxes else None)
    wall = ang < WALL_DEG
    r = dict(stl=stl, stl_md5=md5_of(stl), faces=int(len(m.faces)), watertight=bool(m.is_watertight), bodies=int(len(m.split(only_watertight=False))),
             bbox=np.round(m.bounds, 2).tolist(), vol_cm3=round(float(m.volume) / 1000, 3), samples=samples, gate=gate, void_gate=void_gate, thr=thr,
             hist=histogram(T), frac_below={str(b): round(float((th < b).mean()), 4) for b in (0.8, 1.0, 1.2)},
             wall_frac_below={str(thr): round(float(((th < thr) & wall).mean()), 5)}, void_frac_below={str(thr): round(float((gap < thr).mean()), 5)},
             clusters=clusters, voids=voids, fails=fails)
    print(f"{stl} md5 {r['stl_md5'][:8]} faces {r['faces']} watertight {r['watertight']} bodies {r['bodies']} bbox {r['bbox']} vol {r['vol_cm3']} cm3")
    print(f"histogram {r['hist']}  below 0.8 / 1.0 / 1.2: {r['frac_below']}  SANITY wall-class / void-facing below {thr}: {r['wall_frac_below'][str(thr)]:.2%} / {r['void_frac_below'][str(thr)]:.2%}")
    print(f"clusters < {thr} (cls n tmed_wall tmin span bbox in_box):")
    for c in clusters[:30]:
        print(f"  {c['cls']:5s} n {c['n']:5d} wall-med {c['tmed_wall']:.2f} min {c['tmin']:.2f} span {c['span']:6.1f} bbox {c['bbox']} box {c['in_box_frac']:.2f}")
    print(f"voids < {void_gate} (n gmed gmin span bbox):")
    for v in voids[:30]:
        print(f"  n {v['n']:5d} med {v['gmed']:.2f} min {v['gmin']:.2f} span {v['span']:6.1f} bbox {v['bbox']}")
    print(f"FAIL {len(fails)}" + ("".join("\n  " + f for f in fails) if fails else " — 0 walls below the gate, 0 voids below the void gate; wedges listed: "
                                                                       f"{sum(c['cls'] == 'wedge' for c in clusters)} (each must be a chamfer backed by a wall)"))
    if out_json:
        json.dump(r, open(out_json, "w"), indent=1)
    return 1 if fails else 0


# ---------------------------------------------------------------- selftest -----------------------------------------------------------------------
def selftest():
    import tempfile
    # pure core: a 1.0 plate = parallel-face samples -> ONE wall cluster, FAIL at 1.2; a 45 deg wedge -> wedge, never FAIL; a 0.5 void -> FAIL
    plate = [(x * 1.0, y * 1.0, 0.0) for x in range(30) for y in range(30)]
    rows = cluster_rows(plate, [1.0] * 900, [0.0] * 900, cell=3.0)
    assert len(rows) == 1 and rows[0]["cls"] == "wall" and rows[0]["tmed_wall"] == 1.0 and rows[0]["span"] == 29.0, rows
    assert gate_rows(rows, [], 1.2, 1.2) and gate_rows(rows, [], 1.0, 1.2) == [], "a 1.0 wall fails 1.2 and passes 1.0"
    wedge = cluster_rows([(x * 0.5, 0.0, 0.0) for x in range(40)], [0.3 + 0.02 * x for x in range(40)], [45.0] * 40)
    assert wedge[0]["cls"] == "wedge" and gate_rows(wedge, [], 1.2, 1.2) == [], "a 45 deg edge is listed, not gated"
    mixed = cluster_rows(plate[:100] + [(50.0, 50.0, 0.0)], [1.0] * 100 + [0.4], [0.0] * 100 + [60.0])
    assert [c["cls"] for c in mixed] == ["wall", "wedge"] and mixed[0]["n"] == 100, mixed
    voids = void_rows([(0.0, 0.0, 0.0), (0.5, 0.0, 0.0)], [0.5, 0.45])
    assert gate_rows([], voids, 1.2, 1.2) and gate_rows([], voids, 1.2, 0.4) == [], "a 0.5 slot fails a 1.2 void gate"
    # legend boxes: a 1.0 raised stroke inside a box gates at box_min
    boxed = cluster_rows(plate, [1.0] * 900, [0.0] * 900, boxes=[[-1, -1, 31, 31]])
    assert boxed[0]["in_box_frac"] == 1.0 and gate_rows(boxed, [], 1.6, 1.0, box_min=1.0) == [] and gate_rows(boxed, [], 1.6, 1.0) , "legend land rule"
    assert histogram([0.1, 1.19, 5.0, math.inf])["1.0-1.2"] == 1 and histogram([math.inf])["2.0-inf"] == 1
    # the pure gate: matching md5 + no fails passes; a wrong md5 and a FAIL list are named
    with tempfile.TemporaryDirectory() as d:
        stl = os.path.join(d, "p_body.stl"); open(stl, "wb").write(b"solid p\nendsolid p\n")
        good = dict(stl=stl, stl_md5=md5_of(stl), fails=[]); json.dump(good, open(os.path.join(d, "p.json"), "w"))
        assert pure_gate([d]) == [], pure_gate([d])
        json.dump(dict(good, stl_md5="0" * 32), open(os.path.join(d, "p.json"), "w")); assert any("STL of record" in b for b in pure_gate([d]))
        json.dump(dict(good, fails=["WALL 0.88 < 1.2 span 141"]), open(os.path.join(d, "p.json"), "w")); assert any("FAIL cluster" in b for b in pure_gate([d]))
        assert pure_gate([os.path.join(d, "none")]) and "no census JSON" in pure_gate([os.path.join(d, "none")])[0]
    msg = "selftest OK (pure core: wall / wedge classification, clustering, span, void + legend-box gating, pure --gate-dir on a temp record"
    try:
        import numpy, trimesh  # noqa: F401
    except ImportError:
        print(msg + "; trimesh/numpy absent — the mesh primitives were not run)"); return 0
    with tempfile.TemporaryDirectory() as d:
        p = os.path.join(d, "plate10.stl"); trimesh.creation.box((30.0, 30.0, 1.0)).export(p)
        j = os.path.join(d, "plate10.json")
        assert census(p, 6000, 1.2, 1.2, 3.0, 0.02, 0.5, None, None, j) == 1, "a 1.0 plate must FAIL the 1.2 gate"
        r = json.load(open(j)); w = [c for c in r["clusters"] if c["cls"] == "wall"]
        assert w and abs(w[0]["tmed_wall"] - 1.0) < 0.05 and w[0]["span"] >= 29 and r["fails"], r["clusters"][:2]
        assert any("STL of record" not in b for b in pure_gate([d])) and any("FAIL" in b for b in pure_gate([d]))
        q = os.path.join(d, "wedge.stl"); trimesh.creation.extrude_triangulation(numpy.array([[0, 0], [20, 0], [0, 20.0]]), numpy.array([[0, 1, 2]]), 30.0).export(q)
        assert census(q, 6000, 1.2, 1.2, 3.0, 0.02, 0.5, None, None, None) == 0, "a 45 deg prism has wedges only"
        p2 = os.path.join(d, "plate20.stl"); trimesh.creation.box((30.0, 30.0, 2.0)).export(p2)
        assert census(p2, 6000, 1.2, 1.2, 3.0, 0.02, 0.5, None, None, None) == 0, "a 2.0 plate passes"
    print(msg + "; primitives: 1.0 plate FAIL, 45 deg prism wedges only, 2.0 plate 0 FAIL)"); return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stl", nargs="?"); ap.add_argument("--gate-dir", nargs="+", metavar="DIR"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--gate", type=float, default=1.2); ap.add_argument("--void-gate", type=float, default=1.2); ap.add_argument("--samples", type=int, default=60000)
    ap.add_argument("--cell", type=float, default=3.0); ap.add_argument("--self-hit", type=float, default=0.02); ap.add_argument("--red", type=float, default=0.5)
    ap.add_argument("--boxes", metavar="JSON"); ap.add_argument("--box-min", type=float, default=1.0); ap.add_argument("--json", metavar="OUT")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.gate_dir:
        bad = pure_gate(a.gate_dir)
        for b in bad:
            print("CENSUS GATE:", b)
        print(f"census gate: {len(bad)} problem(s)"); return 1 if bad else 0
    if a.stl:
        boxes = json.load(open(a.boxes)) if a.boxes else None
        return census(a.stl, a.samples, a.gate, a.void_gate, a.cell, a.self_hit, a.red, boxes, a.box_min, a.json)
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
