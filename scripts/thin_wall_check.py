#!/usr/bin/env python3
"""scripts/thin_wall_check.py — two mesh checks a print-service DFM will run on you (references/case-pipeline.md §Census / §Point contacts).

  scripts/thin_wall_check.py --census PIECE.stl [--samples 40000] [--thin 1.0] [--red 0.5] [--self-hit 0.02] [--cell 3.0] [--json OUT]
      inward ray-cast wall-thickness census: histogram (mm bins) + clusters of thin samples (n, min, median, n_red, bbox) so a heat-map colour
      becomes a number and a named feature. Needs trimesh + numpy at run time. The GATE form (wall / wedge classification, outward void rays,
      --json record + a pure --gate-dir for the adopt list) is `scripts/thin_wall_census.py` — use that to gate a body; this mode stays a quick look.
  scripts/thin_wall_check.py --pinch PIECE.stl [--z Z] [--close 0.05] [--path-frac 0.05] [--merge 3.0] [--web D] [--clip R]
      POINT CONTACTS of a mark-shaped body: section the piece at Z, take the outline, report non-adjacent boundary vertices closer than --close
      (a potrace path of touching shapes pinches to 0.003–0.03 mm; a ridge / distance-transform "thinnest arm" census cannot see it). With --web,
      also the neck each contact would have after a web disc of diameter D clipped to the outline's closing (offset +R then -R; needs shapely).
  scripts/thin_wall_check.py --pinch-polygon OUTLINE.json [same options]      the outline as [[x, y], ...] (no mesh libraries needed)
  scripts/thin_wall_check.py --selftest                                       pure python: no trimesh / numpy / shapely required

Rules baked in (references/case-pipeline.md §Point contacts): (1) a ray from a point nudged 1e-3 inside a face hits THAT face at 0.000 for a fraction of samples —
discard hits closer than --self-hit and take the first beyond it (`multiple_hits=True`), or solid 2 mm chamfers read "0.00 mm walls";
(2) trimesh `section().to_2D()` RE-ORIGINS the plane — map the outline back through the returned to-3D transform before you place anything;
(3) bridge a contact with a disc INTERSECTED with the outline's closing, never a bare disc (it bulges into the silhouette); (4) add a census row
for the neck and keep the `connected components = 1` row — that row caught the mis-placed disc, the neck row measured the wrong frame.
Exit 1 when --pinch finds a contact or --census finds a red cluster (so it can sit in a gate list).
"""
import argparse, json, math, os, sys


# the ray / histogram / clustering core is shared with scripts/thin_wall_census.py (the GATE); this file keeps the quick look and the pinch test
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from thin_wall_census import first_hit_beyond, histogram, grid_groups, need  # noqa: E402


def clusters(points, thick, cell=3.0, red=0.5):
    """Grid-cluster (26-neighbour union-find) thin samples -> rows sorted by red count then min thickness; each row names a bbox = a feature."""
    rows = []
    for idx in grid_groups(points, cell):
        ts = sorted(thick[i] for i in idx); ps = [points[i] for i in idx]
        rows.append({"n": len(idx), "tmin": round(ts[0], 3), "tmed": round(ts[len(ts) // 2], 2), "n_red": sum(t < red for t in ts),
                     "bbox": [round(min(p[i] for p in ps), 1) for i in range(3)] + [round(max(p[i] for p in ps), 1) for i in range(3)]})
    rows.sort(key=lambda r: (-r["n_red"], r["tmin"]))
    return rows


def pinch_points(coords, close=0.05, path_frac=0.05, merge=3.0):   # ponytail: O(n²) over the vertices; grid-bucket by `close` if outlines exceed ~5 k vertices
    """Point contacts of a closed outline (list of [x, y], last != first): pairs of vertices closer than `close` whose distance ALONG the boundary
    exceeds `path_frac` of the perimeter (a smoothed tip has close vertices too, but adjacent ones); contacts within `merge` are one.
    Returns [(x, y, gap)] sorted."""
    n = len(coords)
    if n < 4:
        return []
    seg = [math.dist(coords[i], coords[(i + 1) % n]) for i in range(n)]
    cum = [0.0]
    for s in seg:
        cum.append(cum[-1] + s)
    per = cum[-1]
    found = []
    for i in range(n):
        for j in range(i + 1, n):
            d = math.dist(coords[i], coords[j])
            if d < close:
                along = cum[j] - cum[i]; along = min(along, per - along)
                if along > path_frac * per:
                    found.append(((coords[i][0] + coords[j][0]) / 2, (coords[i][1] + coords[j][1]) / 2, d))
    out = []
    for q in sorted(found, key=lambda q: q[2]):
        if not any(math.dist(q[:2], r[:2]) < merge for r in out):
            out.append(q)
    return sorted(out, key=lambda q: (round(q[0], 3), round(q[1], 3)))


# ---------------------------------------------------------------- mesh-bound wrappers (trimesh / numpy / shapely at run time) -----------------
def section_outline(stl, z=None):
    """Outline polygon(s) of the piece at height z (default: mid-height), in MODEL coordinates (to_2D's re-origin mapped back through the full
    2-D affine part of its to-3D matrix, rotation included)."""
    trimesh, = need("trimesh"); need("shapely")
    from shapely.ops import unary_union
    from shapely import affinity
    m = trimesh.load(stl, force="mesh")
    z = (m.bounds[0][2] + m.bounds[1][2]) / 2 if z is None else z
    sec = m.section(plane_origin=[0, 0, z], plane_normal=[0, 0, 1])
    if sec is None:
        sys.exit(f"{stl}: the plane z={z} misses the mesh (z range {m.bounds[0][2]:.2f}..{m.bounds[1][2]:.2f})")
    path2d, M = sec.to_2D()
    poly = affinity.affine_transform(unary_union(path2d.polygons_full), [float(M[0, 0]), float(M[0, 1]), float(M[1, 0]), float(M[1, 1]), float(M[0, 3]), float(M[1, 3])])
    return poly, m


def necks_after_webs(poly, contacts, web, clip):
    """Narrowest chord through each contact once a disc of diameter `web` (clipped to the outline's closing, radius `clip`) is added — the neck the fab measures."""
    need("shapely")
    from shapely.geometry import Point, LineString
    from shapely.ops import unary_union
    q = poly
    if web > 0:
        discs = unary_union([Point(c[0], c[1]).buffer(web / 2, quad_segs=24) for c in contacts])
        if clip > 0:
            discs = discs.intersection(q.buffer(clip, join_style=1, quad_segs=32).buffer(-clip, join_style=1, quad_segs=32))
        q = unary_union([q, discs])
    necks = []
    for c in contacts:
        best = math.inf
        for k in range(90):
            a = math.pi * k / 90; dx, dy = 3 * math.cos(a), 3 * math.sin(a)
            seg = q.intersection(LineString([(c[0] - dx, c[1] - dy), (c[0] + dx, c[1] + dy)]))
            for g in getattr(seg, "geoms", [seg]):
                if g.length > 0 and g.distance(Point(c[0], c[1])) < 1e-6:
                    best = min(best, g.length)
        necks.append(round(best, 3) if best < math.inf else 0.0)
    return necks


def census(stl, samples, thin, red, self_hit, cell, out_json):
    np, trimesh = need("numpy", "trimesh")
    np.random.seed(0)
    m = trimesh.load(stl, force="mesh")
    print(f"{stl}: faces {len(m.faces)} watertight {m.is_watertight} bbox {np.round(m.bounds, 2).tolist()} volume {m.volume / 1000:.2f} cm3 "
          f"bodies {len(m.split(only_watertight=False))}")
    pts, fid = trimesh.sample.sample_surface(m, samples); nrm = m.face_normals[fid]; orig = pts - nrm * 1e-3
    loc, idx_ray, _ = m.ray.intersects_location(orig, -nrm, multiple_hits=True)
    d = np.linalg.norm(loc - orig[idx_ray], axis=1)
    per_ray = {}
    for r, x in zip(idx_ray.tolist(), d.tolist()):
        per_ray.setdefault(r, []).append(x)
    th = [first_hit_beyond(sorted(per_ray.get(i, [])), self_hit) for i in range(samples)]
    h = histogram(th); print("thickness histogram (mm bins):", h)
    sel = [(pts[i].tolist(), th[i]) for i in range(samples) if th[i] < thin]
    rows = clusters([p for p, _ in sel], [t for _, t in sel], cell, red)
    print(f"clusters of samples < {thin} mm (n, min, median, n<{red}, bbox):"); [print("  ", r) for r in rows[:25]]
    if out_json:
        json.dump({"stl": stl, "samples": samples, "self_hit": self_hit, "histogram": h, "clusters": rows}, open(out_json, "w"), indent=1)
    return 1 if any(r["n_red"] for r in rows) else 0


def cross_ring_contacts(rings, close, merge):
    """Near-touches BETWEEN rings (two lobes 0.003 mm apart are two polygons, a hole touching the outer boundary is a ring pair): nearest vertex pairs < close."""
    found = []
    for i in range(len(rings)):
        for j in range(i + 1, len(rings)):
            for a in rings[i]:
                for b in rings[j]:
                    d = math.dist(a, b)
                    if d < close:
                        found.append(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, d))
    out = []
    for q in sorted(found, key=lambda q: q[2]):
        if not any(math.dist(q[:2], r[:2]) < merge for r in out):
            out.append(q)
    return out


def pinch(poly, close, path_frac, merge, web, clip):
    geoms = list(getattr(poly, "geoms", [poly]))
    rings = [[list(c) for c in list(g.exterior.coords)[:-1]] for g in geoms] + [[list(c) for c in list(i.coords)[:-1]] for g in geoms for i in g.interiors]
    found = [c for r in rings for c in pinch_points(r, close, path_frac, merge)] + cross_ring_contacts(rings, close, merge)
    print(f"outline polygons at the section: {len(geoms)} (a mark-shaped body must be 1); point contacts (< {close} mm, non-adjacent, within and between rings): {len(found)}")
    for x, y, gap in found:
        print(f"   at ({x:.3f}, {y:.3f}) gap {gap:.4f} mm")
    if found and web:
        print(f"necks after web discs d={web} clipped to the closing r={clip}: {necks_after_webs(poly, [(x, y) for x, y, _ in found], web, clip)} mm")
    return 1 if found or len(geoms) > 1 else 0


def selftest():
    assert first_hit_beyond([0.0, 0.0004, 1.98, 3.1], 0.02) == 1.98 and first_hit_beyond([0.001], 0.02) == math.inf, "self-hit discard"
    h = histogram([0.1, 0.45, 0.9, 1.2, 5.0, math.inf]); assert h["0-0.3"] == 1 and h["0.3-0.5"] == 1 and h["0.8-1.0"] == 1 and h["1.2-1.5"] == 1 and h["2.0-inf"] == 2, h
    pts = [(0, 0, 0), (1, 0, 0), (0.5, 1, 0), (20, 20, 20), (21, 20, 20)]; th = [0.3, 0.4, 0.9, 0.45, 0.9]
    rows = clusters(pts, th, cell=3.0, red=0.5)
    assert len(rows) == 2 and rows[0]["n"] == 3 and rows[0]["n_red"] == 2 and rows[0]["tmin"] == 0.3 and rows[1]["n_red"] == 1, rows
    # two 10 x 10 squares touching corner to corner through a 0.01 mm neck (a traced mark of touching shapes): one contact; a plain square none
    a = [[0, 0], [10, 0], [10, 10], [0, 10]]
    eight = [[0, 0], [10, 0], [10, 9.99], [10.01, 10.01], [20, 10.01], [20, 20], [10.01, 20], [10.01, 10.02], [9.99, 10], [0, 10]]
    assert pinch_points(a) == [], "a square has no contact"
    c = pinch_points(eight, close=0.05)
    assert len(c) == 1 and abs(c[0][0] - 10) < 0.02 and abs(c[0][1] - 10) < 0.02 and c[0][2] < 0.02, c
    assert len(pinch_points(eight, close=0.05, merge=0.001)) == 4 and len(pinch_points(eight, close=0.001)) == 0, "without merge every vertex pair of the neck is listed; the close threshold is honoured"
    two = [[[0, 0], [10, 0], [10, 10], [0, 10]], [[10.004, 0], [20, 0], [20, 10], [10.004, 10]]]
    assert len(cross_ring_contacts(two, 0.05, 3.0)) == 2 and len(cross_ring_contacts(two, 0.05, 20.0)) == 1 and cross_ring_contacts(two, 0.001, 3.0) == [], "two lobes 0.004 mm apart along an edge: both ends listed, merged within the merge radius"
    # adjacent close vertices (a smoothed tip) are not a contact
    tip = [[0, 0], [10, 0], [10, 5], [5.001, 5.0], [5.0, 5.001], [0, 5]]
    assert pinch_points(tip, close=0.05) == [], "adjacent vertices are a tip, not a contact"
    print("selftest OK (pure core: self-hit discard, histogram, clusters, point contacts on a figure-eight / square / tip, cross-ring contacts — the mesh wrappers need trimesh/numpy/shapely and are not covered here)")
    return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--census", metavar="STL"); ap.add_argument("--pinch", metavar="STL"); ap.add_argument("--pinch-polygon", metavar="JSON")
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--json")
    ap.add_argument("--samples", type=int, default=40000); ap.add_argument("--thin", type=float, default=1.0); ap.add_argument("--red", type=float, default=0.5)
    ap.add_argument("--self-hit", type=float, default=0.02); ap.add_argument("--cell", type=float, default=3.0)
    ap.add_argument("--z", type=float); ap.add_argument("--close", type=float, default=0.05); ap.add_argument("--path-frac", type=float, default=0.05)
    ap.add_argument("--merge", type=float, default=3.0); ap.add_argument("--web", type=float, default=0.0); ap.add_argument("--clip", type=float, default=0.0)
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.census:
        return census(a.census, a.samples, a.thin, a.red, a.self_hit, a.cell, a.json)
    if a.pinch:
        poly, m = section_outline(a.pinch, a.z)
        print(f"{a.pinch}: bodies {len(m.split(only_watertight=False))} (a mark-shaped body must be 1)")
        return pinch(poly, a.close, a.path_frac, a.merge, a.web, a.clip)
    if a.pinch_polygon:
        coords = json.load(open(a.pinch_polygon))
        found = pinch_points(coords, a.close, a.path_frac, a.merge)
        print(f"point contacts: {len(found)}"); [print(f"   at ({x:.3f}, {y:.3f}) gap {g:.4f} mm") for x, y, g in found]
        if found and a.web:
            need("shapely"); from shapely.geometry import Polygon
            print("necks after webs:", necks_after_webs(Polygon(coords), [(x, y) for x, y, _ in found], a.web, a.clip))
        return 1 if found else 0
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
