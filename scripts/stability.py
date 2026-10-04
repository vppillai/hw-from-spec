#!/usr/bin/env python3
"""scripts/stability.py — static stability of a free-standing piece: centre of gravity vs the support polygon, at every pose.

A piece that stands, rocks, walks or is set down on a desk has a support polygon (the convex hull of what touches the ground) and a centre of
gravity (CoG). It stays up only while the CoG's ground projection lies INSIDE that polygon, by a margin the geometry's errors cannot eat
(SKILL §8, `references/case-pipeline.md` "Stability"). This is a GEOMETRY check: it is computed from the STL set of record (volume centroids),
the assembly transforms, a density per body (infill-aware) and the ground-contact footprints per pose — never from a render or a guess.
The source project's walker had its CoG 21 mm behind the hip because the drive sat at the back; at a third of the crank angles only one foot per
side was down and the margin was −17 mm: it would have tipped onto its gear. One row found it before the first plate.

Use from a generator (the poses are the project's; this module does the arithmetic):
    from stability import cog_of_assembly, support_margin
    cog, mass = cog_of_assembly([(stl_path, M4x4, density_g_mm3), ...])      # M maps the STL's print frame into the machine frame
    margin, hull = support_margin((cog[0], cog[1]), contact_polygons)         # contacts: shapely polygons on the ground plane (footprints)
    -> margin > 0 inside (distance to the nearest edge), < 0 outside (a single foot still has a footprint), None with no contact at all
A CHECKS row: min margin over the poses >= a stated limit (the source project used 2 mm on a 165 g piece with 14 mm shoes).
    improper_placements([(label, M4x4), ...])                                 # -> [(label, det)] for every placement that is a mirror or not rigid
A placement matrix with determinant -1 is a MIRROR, and a mirror cannot be printed: the same transforms this module weighs the CoG through must
every one be a proper rotation (det +1) — one CHECKS row, `len(improper_placements(...)) == 0`. The walker project drew one whole side of the
machine as a mirror image for three days of renders and a GIF; the printed part did not match the guide and nothing but the owner's hands caught it.
Density: PLA 1.24e-3 g/mm3 solid; parts printed with sparse infill weigh less — pass a per-body factor (walls + top/bottom shells dominate small
parts, so 0.5–0.7 of solid for large flat plates, ~1.0 for pins and bars). The CoG moves only if the factors differ between front and back.
"""
import json, os, sys


def _trimesh():
    try:
        import trimesh  # noqa: F401
        return trimesh
    except ImportError:
        sys.exit("stability.py needs trimesh (uv pip install trimesh)")


def cog_of_assembly(items):
    """items: [(stl_path, M (4x4 nested list), density_g_mm3)] -> (cog xyz in the machine frame, total mass g)."""
    import numpy as np
    tm = _trimesh()
    acc = np.zeros(3); tot = 0.0; cache = {}
    for stl, M, rho in items:
        if stl not in cache:
            m = tm.load(stl, force="mesh")
            if not m.is_watertight:
                raise ValueError(f"{stl}: not watertight — its volume and mass centre are undefined (canonicalise / fix the body first)")
            # center_mass is the VOLUME centroid; trimesh's `centroid` is the area-weighted average of the triangle centroids and sits
            # elsewhere on any body that is not symmetric (a bar with a boss at one end) — never use it for a mass model
            cache[stl] = (np.append(m.center_mass, 1.0), float(abs(m.volume)))
        c, v = cache[stl]
        p = np.array(M, dtype=float) @ c
        w = v * rho
        acc += p[:3] * w; tot += w
    if tot <= 0:
        raise ValueError("no mass")
    return (acc / tot).tolist(), tot


def improper_placements(items, tol=1e-6):
    """items: [(label, M (4x4 nested list))] -> [(label, det)] for every placement whose 3x3 is not a proper rotation: det < 0 is a mirror
    (unprintable — a part that only fits as its mirror image needs a mirrored BODY, never a mirrored transform), |det| != 1 is a scale or a
    shear. Empty list = every placement is physically realisable."""
    import numpy as np
    bad = []
    for label, M in items:
        d = float(np.linalg.det(np.array(M, dtype=float)[:3, :3]))
        if d < 0 or abs(abs(d) - 1.0) > tol:
            bad.append((label, round(d, 6)))
    return bad


def support_margin(cog_xy, contacts):
    """contacts: shapely polygons (ground footprints). -> (signed margin mm, hull polygon or None)."""
    from shapely.geometry import Point
    from shapely.ops import unary_union
    polys = [c for c in contacts if c is not None and not c.is_empty]
    if not polys:
        return None, None
    hull = unary_union(polys).convex_hull
    if hull.area <= 0:
        return None, hull
    p = Point(cog_xy)
    d = hull.exterior.distance(p)
    return (d if hull.contains(p) else -d), hull


def sweep(poses):
    """poses: iterable of (label, cog_xy, contacts) -> (worst margin, label of the worst pose, rows [(label, margin, n_contacts)])."""
    rows = []; worst = (float("inf"), None)
    for label, cxy, contacts in poses:
        m, hull = support_margin(cxy, contacts)
        mm = -999.0 if m is None else m
        rows.append((label, round(mm, 2), len([c for c in contacts if c is not None and not c.is_empty])))
        if mm < worst[0]:
            worst = (mm, label)
    return worst[0], worst[1], rows


def selftest():
    try:
        import numpy as np, tempfile, trimesh as tm, scipy  # noqa: F401
        from shapely.geometry import box
    except ImportError:   # as print_dfm.py: exit 2 = skipped, not failed (the smoke's 0a loop skips it when the mesh stack is absent)
        print("SKIP: mesh libraries absent (numpy trimesh scipy shapely)"); return 2
    with tempfile.TemporaryDirectory() as d:
        body = tm.creation.box((20.0, 20.0, 10.0)); body.apply_translation((0, 0, 5)); p1 = os.path.join(d, "body.stl"); body.export(p1)
        knob = tm.creation.box((10.0, 10.0, 10.0)); knob.apply_translation((0, 0, 5)); p2 = os.path.join(d, "knob.stl"); knob.export(p2)
        I = np.eye(4).tolist()
        c, mass = cog_of_assembly([(p1, I, 1.0)])
        assert abs(c[0]) < 1e-6 and abs(c[2] - 5.0) < 1e-6 and abs(mass - 4000.0) < 1e-6, (c, mass)
        T = np.eye(4); T[0, 3] = 30.0                                     # a knob 30 mm to the side moves the CoG by 1000/5000 * 30 = 6
        c2, mass2 = cog_of_assembly([(p1, I, 1.0), (p2, T.tolist(), 1.0)])
        assert abs(c2[0] - 6.0) < 1e-6 and abs(mass2 - 5000.0) < 1e-6, c2
        c3, _ = cog_of_assembly([(p1, I, 1.0), (p2, T.tolist(), 0.5)])    # half density halves the pull
        assert abs(c3[0] - 1000 * 0.5 * 30 / 4500) < 1e-6, c3
        # ONE asymmetric mesh (body + knob at x = 30 as one STL): the volume centroid is x = 6.0; the area-weighted centroid reads ~8.2
        both = tm.util.concatenate([body, knob.copy().apply_transform(T)]); p3 = os.path.join(d, "both.stl"); both.export(p3)
        c4, m4 = cog_of_assembly([(p3, I, 1.0)]); assert abs(c4[0] - 6.0) < 1e-6 and abs(m4 - 5000.0) < 1e-6, (c4, m4)
        assert abs(tm.load(p3, force="mesh").centroid[0] - 6.0) > 1.0, "the test body must separate the two centroids"
        open_body = body.copy(); open_body.update_faces([i for i in range(len(open_body.faces)) if i != 0]); p4 = os.path.join(d, "open.stl"); open_body.export(p4)
        try:
            cog_of_assembly([(p4, I, 1.0)]); raise AssertionError("an open mesh must be refused")
        except ValueError as e:
            assert "watertight" in str(e), e
        feet = [box(-10, -10, -6, -6), box(6, -10, 10, -6), box(-10, 6, -6, 10), box(6, 6, 10, 10)]
        m, hull = support_margin((0.0, 0.0), feet); assert abs(m - 10.0) < 1e-6, m                  # centred: 10 to the hull edge
        m, _ = support_margin((0.0, 0.0), feet[:2]); assert m is not None and m < 0, m             # two feet on one side: outside
        m, _ = support_margin((14.0, 0.0), feet); assert abs(m + 4.0) < 1e-6, m                      # 4 mm outside the back edge
        m, _ = support_margin((0.0, 0.0), []); assert m is None
        worst, lab, rows = sweep([("a", (0.0, 0.0), feet), ("b", (14.0, 0.0), feet), ("c", (0.0, 0.0), feet[:1])])
        assert lab == "c" and worst < -8.0 and rows[1][1] == -4.0, (worst, lab, rows)                  # one foot: the CoG is outside its footprint
        # handedness: a flat part laid print-XY -> machine-XZ with print +z -> +y is a mirror (det -1) however plausible the render; the same
        # part turned over (print +z -> -y) is a proper rotation; a 90° turn is proper; a scale is not rigid; a mirrored body may NOT be rescued by
        # a second mirror in the transform (two mirrors = proper, but then the BODY is the mirror body, which is the point)
        flat_mirror = [[1, 0, 0, 0], [0, 0, 1, 0], [0, 1, 0, 0], [0, 0, 0, 1]]
        flat_turned = [[1, 0, 0, 0], [0, 0, -1, 3.0], [0, 1, 0, 0], [0, 0, 0, 1]]
        turn90 = [[0, -1, 0, 5], [1, 0, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
        scaled = [[2, 0, 0, 0], [0, 2, 0, 0], [0, 0, 2, 0], [0, 0, 0, 1]]
        bad = improper_placements([("ok_I", I), ("mirror", flat_mirror), ("turned", flat_turned), ("turn90", turn90), ("scaled", scaled)])
        assert [b[0] for b in bad] == ["mirror", "scaled"] and bad[0][1] == -1.0 and bad[1][1] == 8.0, bad
        assert improper_placements([]) == []
    print("selftest OK (volume centroid of transformed bodies with densities — not the area centroid, open mesh refused; support margin inside / outside / degenerate; sweep worst pose; improper placements: mirror and scale flagged, turn-over and 90° pass)")
    return 0


def main(argv):
    if "--selftest" in argv:
        return selftest()
    if len(argv) == 2 and argv[1].endswith(".json"):
        # {"items": [[stl, M, rho], ...], "poses": [[label, [x, y], [[x0,y0,x1,y1], ...]], ...]} -> margins
        from shapely.geometry import box
        spec = json.load(open(argv[1]))
        bad = improper_placements([(i[0], i[1]) for i in spec["items"]])
        if bad:
            print("FAIL: placements that are not proper rotations (a mirror cannot be printed): " + ", ".join(f"{l} det {d}" for l, d in bad)); return 1
        c, mass = cog_of_assembly([tuple(i) for i in spec["items"]])
        worst, lab, rows = sweep([(l, tuple(cxy) if cxy else (c[0], c[1]), [box(*b) for b in bxs]) for l, cxy, bxs in spec["poses"]])
        print(f"cog {['%.2f' % v for v in c]} mass {mass:.1f} g; worst margin {worst:.2f} mm at pose {lab}")
        for r in rows:
            print(" ", *r)
        return 0 if worst >= float(spec.get("limit", 0.0)) else 1
    print(__doc__); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
