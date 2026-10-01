#!/usr/bin/env python3
"""scripts/print_dfm.py — vendor-independent manufacturability check for printed bodies (MJF / SLA / FDM), run on the MESH before every upload.

Rules come from physics and the published process minimums, parameterised per process row in `design/dfm_processes.yaml` (every number cited
[V] fetched / [K] known); a vendor's DFM verdicts (`docs/quotes/dfm_verdicts.yaml`) are a VALIDATION set, never a fitting target. Nothing in
here is tuned to one vendor. `references/print-dfm.md` carries the loop; this docstring carries the mechanism.

Measures (per surface sample, area-weighted, fixed seed):
  t_ray  material thickness along the inverse normal (the census ray); the hit face's angle classifies wall (< 30 deg) / wedge
  t_med  tangent-ball thickness limited by OPPOSING faces only (normals within 45 deg of the inverse normal) = the largest inscribed ball tangent
         at the sample: reads a NECK / ROOT that no ray sees (a rim ring set inboard of its wall over a lap step stands on a root the width of
         the overlap while every ray through it reads the full rim) and does not read a convex 90 deg edge thin (a perpendicular face is not
         opposing)
  t = min(t_ray, t_med);  g = both measures cast OUTWARD = void / slot / hole width
Samples below a threshold are linked on the surface (pairs within max(3 spacings, 2.5 mm)) into REGIONS (area, extent, min / median, class).
Rules (each a row: process parameter + physical reason; verdict FLAG / PASS / INFO):
  W  wall: wall-class region with median t < wall_min and extent >= slender x t — a thin plate strip (Kirchhoff, L/t >= 10) bends / cracks
     under depowdering, cleaning and handling loads; shorter = a feature (rule F)
  R  root: the W regions whose RAY thickness is >= wall_min = a rim / ledge standing on a root narrower than its own wall; its own row
  F  feature: short wall-class region with median t < feature_min — below the smallest formable feature it does not form / breaks off
  K  knife edge: wedge-class region whose thin end runs below feature_min over >= slender x feature_min — a taper the process cannot form; a
     chamfer / ramp whose thin end stays >= feature_min is a listed INFO wedge
  P  point contact: t <= neck_max on 15 section planes — two bodies touching along a line (or parted by a hairline) arrive as pieces
  V  void: g < detail_min anywhere (an engraved stroke / slit narrower than the smallest detail closes); detail_min <= g < void_min over
     >= slender x void_min (a long narrow slot: powder / resin does not clear)
  H  hole: a closed void (normals all round) with g < hole_min
  M  manifold: the mesh is watertight with consistent winding and holds exactly the expected number of bodies (--bodies N, default 1) — an open
     mesh (a STEP->STL export with gaps, two un-unioned solids) has no inside; a stray shell or a split part prints as pieces
  O  overhang (FDM): down-facing faces steeper than overhang_max_deg from vertical, not the bed, not a ceiling; PLUS every horizontal ceiling with
     fewer than two supported ends (a CANTILEVER is a 90 deg overhang, not a bridge) longer than two line widths
  B  bridge (FDM): a horizontal ceiling above the bed with BOTH ends on material, longer than bridge_max
  S  size: bbox against part_min / build_max
  L  INFO: regions inside legend land boxes (the coupon rule owns them) and slivers under sliver_area (a tangency / boolean remnant)
  Y  INFO: wall-class surface between wall_min and wall_reco (the vendor's grey line = the design margin; the census gate owns it)
Heat map (--render, needs matplotlib): faces coloured by the MIN thickness of their samples — grey >= wall_reco, yellow, red < feature_min,
voids narrower than void_min dark red — six orthographic faces + two isos, the same convention the vendors' viewers use.

CLI (paths default to the project root = the nearest parent holding project.yaml, else the cwd; the process table falls back to the skill's
`templates/design/dfm_processes.yaml` when the project has none yet):
  scripts/print_dfm.py --process <row> <mesh.stl>... [--out DIR] [--piece NAME] [--render] [--samples N] [--land x0 y0 x1 y1 ...] [--bodies N]
      one record per body (DIR/<piece>.json [+ DIR/<piece>_<view>.png]); prints one line per rule; exit 1 when any body FLAGs
  scripts/print_dfm.py --list                                 the process rows and their thresholds
  scripts/print_dfm.py --gate <dfm_dir>... [--target <print target>] [--open <tag>/<piece>=<decision id> ...]
      PURE adopt gate (recomputes nothing). FAILs on: an STL of the record set without a same-md5 record (the sibling `stl/` of each DIR and the
      `paths.mech_record` glob under DIR's parent); a record whose `sig` does not verify (hand-edited, or written by another rule set); a record
      `version` != this VERSION or `thresholds` != the current table row; a record `process` != `print_targets.<t>.dfm_process` (t = --target or
      DIR's parent name); a sibling census/<piece>.json with another md5; a census piece without a dfm record; a verdict FLAG — unless --open
      <tag>/<piece>=<id> names a row of paths.decisions whose status is OPEN (printed with its topic; any other id = FAIL). Not a waiver: the
      record still says FLAG and the OPEN row owns the fix.
  scripts/print_dfm.py --validate [--verdicts Y] [--val-dir D] [--val-doc M] [--render-validation substr ...]
      run every labelled STL (records cached by md5 + rule-set version), write the validation doc (vendor vs ours, confusion matrix, rules fired);
      a body the vendor FLAGGED that we PASS is a RULE DEFECT -> printed, exit 1
  scripts/print_dfm.py --selftest
Exit codes: 0 PASS, 1 FLAG (or a gate / validation problem), 2 usage / configuration (missing file, unknown row, missing table or dependency).
Dependencies: numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml (`--render`: matplotlib).
ponytail: random area-weighted samples + KD-tree geometry, per-face MIN colouring; finds and sizes a defect, not a CAD thickness analysis.
"""
import sys, os, json, hashlib, time, glob, argparse
from collections import defaultdict

try:
    import numpy as np, trimesh, yaml
    from scipy.spatial import cKDTree
    from scipy.sparse import coo_matrix
    from scipy.sparse.csgraph import connected_components
    import shapely, rtree, networkx, mapbox_earcut  # noqa: F401 — trimesh needs them for extrusions, ray queries and sections; fail here with the hint, not deep in trimesh
except ImportError as e:  # the generic scripts need pyyaml only; this one needs the mesh stack
    print(f"print_dfm: missing {e.name} — install into the project venv: pip install numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml", file=sys.stderr)
    sys.exit(2)

HERE = os.path.dirname(os.path.realpath(__file__))   # realpath: in a project `scripts` is a symlink into vendor/hw-from-spec — the template table must resolve through it
sys.path.insert(0, HERE)
from project import record_sig, verify_sig, open_decisions  # noqa: E402
VERSION = "0.9.0"        # rule-set version stamped into every record (the validation cache is keyed on it); bump when a rule or a measure changes
WALL_DEG = 30.0          # limiting face within 30 deg of parallel = wall / neck / root; otherwise wedge (census convention)
COS_OPP = 0.7            # a face 'opposes' the sample when its normal is within ~45 deg of the inverse normal (a 45 deg ramp under a skin counts, a 90 deg side face does not)
NOISE_N = 5              # a region of fewer samples is sampling noise (a tessellation sliver), not a feature
VIEWS = {"top": ((0, 0, -1), (1, 0, 0)), "sole": ((0, 0, 1), (1, 0, 0)), "left": ((1, 0, 0), (0, 1, 0)), "right": ((-1, 0, 0), (0, -1, 0)),
         "front": ((0, 1, 0), (1, 0, 0)), "rear": ((0, -1, 0), (-1, 0, 0)), "iso": ((-1, -1, -1), (1, -1, 0)), "iso_rear": ((1, 1, -1), (-1, 1, 0))}   # (direction the camera looks along, screen-right)


def project_root(start=None):
    d = os.path.abspath(start or os.environ.get("HWFS_PROJECT") or os.getcwd())
    while True:
        if os.path.exists(os.path.join(d, "project.yaml")):
            return d
        if os.path.dirname(d) == d:
            return os.path.abspath(start or os.getcwd())
        d = os.path.dirname(d)


ROOT = project_root()
DEFAULTS = dict(processes=os.path.join(ROOT, "design", "dfm_processes.yaml"), verdicts=os.path.join(ROOT, "docs", "quotes", "dfm_verdicts.yaml"),
                val_dir=os.path.join(ROOT, "out", "dfm_validation"), val_doc=os.path.join(ROOT, "docs", "reviews", "PRINT_DFM_VALIDATION.md"))
TEMPLATE_TABLE = os.path.join(os.path.dirname(HERE), "templates", "design", "dfm_processes.yaml")
PATHS = dict(DEFAULTS)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def processes(path=None):
    p = path or PATHS["processes"]
    if not os.path.exists(p) and not path and os.path.exists(TEMPLATE_TABLE):
        p = TEMPLATE_TABLE
    if not os.path.exists(p):
        sys.exit(f"print_dfm: no process table at {p} (copy templates/design/dfm_processes.yaml to design/ or pass --processes)")
    return yaml.safe_load(open(p))["processes"], p


def _tangent_ball(pts, nrm, sign, r0, cos_opp=COS_OPP, query=None):
    """Largest ball tangent at every sample on the material side (sign -1) or the air side (+1) that no sample with an opposing normal enters.
    Returns (2 r, angle of the limiting face in deg); inf / nan where nothing opposes within 2 r0. One KD query per sample: a smaller tangent ball is
    inside the r0 ball, so the limiting point is always among the r0 ball's members."""
    tree = cKDTree(pts)
    qp, qn = query if query is not None else (pts, nrm)
    c0 = qp + sign * qn * r0
    nb = tree.query_ball_point(c0, r0 * 1.0001)
    t = np.full(len(qp), np.inf); ang = np.full(len(qp), np.nan)
    for i, idx in enumerate(nb):
        if len(idx) < (2 if query is None else 1):
            continue
        idx = np.asarray(idx); dq = pts[idx] - qp[i]; h = sign * (dq @ qn[i])
        dots = nrm[idx] @ qn[i]
        sel = (dots < -cos_opp) & (h > 1e-6)
        if not sel.any():
            continue
        r = (dq[sel] ** 2).sum(1) / (2 * h[sel]); k = int(np.argmin(r))
        t[i] = 2 * r[k]; ang[i] = np.degrees(np.arccos(np.clip(-dots[sel][k], -1, 1)))
    return t, ang


def _rays(m, pts, nrm, sign):
    """census ray from the sample nudged 1e-3 INTO the side it travels (sign -1 = into the material, +1 = into the air) along sign * normal, so the
    first hit is the far face and not the origin face: (distance, hit face angle; 0 = parallel). Blind review 0.8.0 F1: nudged the other way every
    ray hit its own face at 0.001, was discarded as a self-hit and read inf — R then fired on every thin wall."""
    orig = pts + sign * nrm * 1e-3
    loc, ir, it = m.ray.intersects_location(orig, sign * nrm, multiple_hits=False)
    d = np.full(len(pts), np.inf); a = np.full(len(pts), np.nan)
    if len(ir):
        dd = np.linalg.norm(loc - orig[ir], axis=1); ok = dd > 0.02          # the intersector returns the origin face itself as a 0.000 hit
        d[ir[ok]] = dd[ok]
        a[ir[ok]] = np.degrees(np.arccos(np.clip(-np.einsum("ij,ij->i", nrm[ir[ok]], m.face_normals[it[ok]]), -1, 1)))
    return d, a


def field(m, n_s, seed=0, r0=1.0, r0_void=0.75):
    pts, fid = trimesh.sample.sample_surface(m, n_s, seed=seed); nrm = m.face_normals[fid]
    t_ray, a_ray = _rays(m, pts, nrm, -1)
    t_med, a_med = _tangent_ball(pts, nrm, -1, r0)
    g_ray, ga_ray = _rays(m, pts, nrm, +1)
    g_ray[ga_ray >= WALL_DEG] = np.inf                                       # a re-entrant corner is not a slot (census convention)
    g_med, _ = _tangent_ball(pts, nrm, +1, r0_void)
    use_med = t_med < t_ray
    return dict(pts=pts, fid=fid, nrm=nrm, t=np.where(use_med, t_med, t_ray), ang=np.where(use_med, a_med, a_ray), t_ray=t_ray, t_med=t_med, g=np.minimum(g_ray, g_med), g_ray=g_ray, g_med=g_med)


def regions(pts, vals, mask, link, a_per, extra=None, min_n=NOISE_N):
    """connected regions of the masked samples (pairs within `link` on the surface) -> rows sorted by area"""
    idx = np.flatnonzero(mask)
    if len(idx) < min_n:
        return []
    P = pts[idx]; pairs = cKDTree(P).query_pairs(link, output_type="ndarray"); n = len(idx)
    lab = connected_components(coo_matrix((np.ones(len(pairs)), (pairs[:, 0], pairs[:, 1])), shape=(n, n)), directed=False)[1] if len(pairs) else np.arange(n)
    rows = []
    for L in np.unique(lab):
        s = idx[lab == L]
        if len(s) < min_n:
            continue
        pp = pts[s]; v = vals[s]; bb = np.r_[pp.min(0), pp.max(0)]
        row = dict(n=int(len(s)), area=round(float(len(s) * a_per), 2), extent=round(float((bb[3:] - bb[:3]).max()), 1), vmin=round(float(v.min()), 3), vmed=round(float(np.median(v)), 2), bbox=np.round(bb, 1).tolist())
        if extra is not None:
            row.update(extra(s))
        rows.append(row)
    rows.sort(key=lambda r: -r["area"])
    return rows


def pinches(m, neck_max, levels=(0.1, 0.3, 0.5, 0.7, 0.9)):
    """Point contacts / hairlines from SECTIONS (random samples never land on a 0.01 mm neck; a traced outline's pinch is a vertex pair): on 5 section
    planes along each axis, pairs of ring vertices within neck_max that are not neighbours on the ring and whose outward normals are not parallel
    (dot < 0: two surfaces facing AWAY from each other = a neck of material between them, facing each other = a hairline slit; dot > 0 = the same
    finely tessellated curve, skipped). Returns rows {x, y, z, width, kind}."""
    out = []; lo, hi = m.bounds
    for ax in range(3):
        for f in levels:
            o = np.zeros(3); o[ax] = lo[ax] + f * (hi[ax] - lo[ax]); nrm = np.zeros(3); nrm[ax] = 1.0
            try:
                sec = m.section(plane_origin=o, plane_normal=nrm)
            except Exception:  # noqa: BLE001 — a plane through a degenerate spot yields no section; the other 14 planes stand
                sec = None
            if sec is None:
                continue
            keep = [i for i in range(3) if i != ax]
            for loop in sec.discrete:
                R3 = np.asarray(loop); R = R3[:, keep]
                if len(R) > 1 and np.allclose(R[0], R[-1]):
                    R = R[:-1]; R3 = R3[:-1]
                n = len(R)
                if n < 4:
                    continue
                ccw = 0.5 * np.sum(R[:, 0] * np.roll(R[:, 1], -1) - np.roll(R[:, 0], -1) * R[:, 1]) > 0
                def outn(e):
                    v = np.c_[e[:, 1], -e[:, 0]] * (1 if ccw else -1); return v / (np.linalg.norm(v, axis=1)[:, None] + 1e-12)
                N = outn(R - np.roll(R, 1, axis=0)) + outn(np.roll(R, -1, axis=0) - R); N /= (np.linalg.norm(N, axis=1)[:, None] + 1e-12)
                for a, b in cKDTree(R).query_pairs(neck_max, output_type="ndarray"):
                    if min((a - b) % n, (b - a) % n) <= 1 or N[a] @ N[b] >= 0:
                        continue
                    d = R[b] - R[a]; kind = "neck" if (N[a] @ d < 0 and N[b] @ (-d) < 0) else "hairline slit"
                    pt = (R3[a] + R3[b]) / 2
                    out.append(dict(x=round(float(pt[0]), 3), y=round(float(pt[1]), 3), z=round(float(pt[2]), 3), width=round(float(np.linalg.norm(d)), 4), kind=kind, axis="xyz"[ax]))
    rows = []                                                                 # one row per contact line: merge points within 0.5 mm in the section-plane coordinates
    for r in sorted(out, key=lambda r: r["width"]):
        for q in rows:
            if abs(q["x"] - r["x"]) < 0.5 and abs(q["y"] - r["y"]) < 0.5 and abs(q["z"] - r["z"]) < 3.0 and q["kind"] == r["kind"]:
                q["n"] += 1; q["z_max"] = max(q["z_max"], r["z"]); q["z_min"] = min(q["z_min"], r["z"]); break
        else:
            rows.append(dict(r, n=1, z_min=r["z"], z_max=r["z"]))
    return rows


def _in_boxes(pts, boxes):
    if not boxes:
        return np.zeros(len(pts), bool)
    B = np.array(boxes, float).reshape(-1, 4)
    return ((pts[:, None, 0] >= B[None, :, 0]) & (pts[:, None, 0] <= B[None, :, 2]) & (pts[:, None, 1] >= B[None, :, 1]) & (pts[:, None, 1] <= B[None, :, 3])).any(1)


def _where(rs, k="vmin", n=5):
    return "; ".join(f"{r.get('cls', '')} {r['area']} mm2 x {r['extent']} mm, min {r[k]} med {r['vmed']}, box {r['bbox']}" for r in rs[:n])


def analyse(path, process, n_s=None, seed=0, lands=None, out_dir=None, piece=None, render=False, bodies_expected=1):
    """One body -> the record (dict; written to out_dir/<piece>.json and, with render, out_dir/<piece>_<view>.png)."""
    t0 = time.time()
    table, table_path = processes()
    if process not in table:
        sys.exit(f"print_dfm: process '{process}' is not a row of {table_path}; rows: {', '.join(table)}")
    pr = table[process]
    if pr.get("wall_min") is None:
        sys.exit(f"print_dfm: row '{process}' has wall_min null (BLOCKED source) — fill the row before gating on it")
    m = trimesh.load(path, force="mesh")
    area = float(m.area); ext = (m.bounds[1] - m.bounds[0])
    n_s = n_s or int(min(300000, max(60000, area * 8)))
    wall_min, reco, fmin, dmin, vmin_, hmin, S, SLV = pr["wall_min"], pr["wall_reco"], pr["feature_min"], pr["detail_min"], pr["void_min"], pr["hole_min"], pr["slender"], pr.get("sliver_area", 5.0)
    F = field(m, n_s, seed=seed, r0=max(1.0, reco / 2 + 0.4), r0_void=max(0.75, max(vmin_, hmin) / 2 + 0.3))
    pts, nrm, t, ang, g = F["pts"], F["nrm"], F["t"], F["ang"], F["g"]
    a_per = area / n_s; spacing = a_per ** 0.5; link = max(3.0 * spacing, 2.5)      # a 0.4 mm band holds ~3 samples / mm along its length: a density-scaled 1 mm link broke a 147 mm root band into 25 pieces; 2.5 keeps it whole
    land = _in_boxes(pts, lands) if (lands and pr.get("legend_land_min") is not None) else np.zeros(n_s, bool)
    thr_w = np.where(land, pr.get("legend_land_min", wall_min), wall_min)
    thr_d = np.where(land, pr.get("legend_void_min", dmin), dmin)
    wall = ang < WALL_DEG
    cls_of = lambda s: dict(wall_frac=round(float(wall[s].mean()), 2), cls="wall" if wall[s].mean() >= 0.5 else "wedge", red_frac=round(float((t[s] < fmin).mean()), 2),
                            ray_med=round(float(np.median(F["t_ray"][s])), 2), in_land=round(float(land[s].mean()), 2))
    thin = regions(pts, t, t < thr_w, link, a_per, cls_of)                     # below the process minimum (inside legend lands: the legend minimum)
    rows = []
    def row(rule, value, limit, verdict, where, why, fix=""):
        rows.append(dict(rule=rule, value=value, limit=limit, verdict=verdict, where=where, why=why, fix=fix))
    n_bodies = len(m.split(only_watertight=False)); mp = []
    if not m.is_watertight:
        mp.append("not watertight (open edges: a STEP->STL export with gaps, or two un-unioned solids)")
    if not m.is_winding_consistent:
        mp.append("inconsistent winding (flipped faces)")
    if n_bodies != bodies_expected:
        mp.append(f"{n_bodies} bodies, expected {bodies_expected}")
    row("M manifold", f"watertight {bool(m.is_watertight)}, winding consistent {bool(m.is_winding_consistent)}, {n_bodies} body/bodies", f"watertight, consistent, bodies = {bodies_expected}", "FLAG" if mp else "PASS", "; ".join(mp),
        "a slicer or vendor cannot tell inside from outside on an open mesh (every thickness below is unreliable); an unexpected body count is a split part or a stray shell that prints as pieces",
        "union the solids and close the open edges in the CAD, re-export; pass --bodies N only when the file intentionally holds N parts")
    walls = [r for r in thin if r["cls"] == "wall"]
    W = [r for r in walls if r["extent"] >= S * max(r["vmed"], 0.1)]
    Rt = [r for r in W if r["ray_med"] >= wall_min]
    inland = lambda r: r.get("in_land", 0) >= 0.5
    Fe = [r for r in walls if r not in W and r["vmed"] < fmin and not inland(r) and r["area"] >= SLV]
    row("W wall", f"{len(W)} wall-class region(s) with median < {wall_min} and extent >= {S} x thickness", f"wall_min {wall_min} over >= {S} x t", "FLAG" if W else "PASS", _where(W),
        "a plate strip thinner than the process minimum over >= 10 x its thickness is a thin plate (Kirchhoff L/t >= 10): it bends / cracks under depowdering, cleaning and handling",
        f"thicken the strip to >= {wall_min} (or shorten it below {S} x t) in the CAD / generator, re-export, rerun")
    row("R root under a rim / ledge", f"{len(Rt)} of them read >= {wall_min} along the normal", f"no W region with ray >= wall_min {wall_min} (= a root)", "FLAG" if Rt else "PASS", _where(Rt),
        "a rim set inboard of its wall over a step stands on a root the width of the overlap: the ball from the wall face is stopped by the rim's outer face while every ray reads the full rim — the construction that cracked on a 141 mm lip",
        f"widen the overlap to >= {wall_min} (move the rim over the wall), fill the undercut or chamfer the step")
    row("F feature", f"{len(Fe)} short wall-class region(s) below feature_min {fmin} and >= sliver_area {SLV} mm2", f"feature_min {fmin} (area >= {SLV} mm2)", "FLAG" if Fe else "PASS", _where(Fe), "below the smallest feature the process forms it does not print or breaks off in post-processing; a patch under sliver_area is a tangency / boolean sliver that fills or vanishes without loss (listed in row L)",
        f"thicken the feature to >= {fmin} or remove it")
    wedges = [r for r in thin if r["cls"] == "wedge"]
    K = [r for r in wedges if r["vmin"] < fmin and r["extent"] >= S * fmin and not inland(r) and r["area"] >= SLV]
    Ki = [r for r in wedges if r not in K]
    row("K knife edge", f"{len(K)} wedge-class region(s) tapering below {fmin} over >= {S * fmin} mm", f"thin end >= feature_min {fmin} over any {S * fmin} mm", "FLAG" if K else "PASS", _where(K) or ("listed wedges (thin end >= feature_min or short): " + _where(Ki, n=4)),
        "a free taper thinner than the smallest formable feature crumbles / never forms (rail tips, cove lips at slot ends); a chamfer or ramp whose thin end stays above it is fine",
        f"stop the taper with a flat >= {fmin} at its thin end, or cut it as a chamfer into a full wall")
    allnecks = pinches(m, pr["neck_max"])
    if lands and pr.get("legend_land_min") is not None:                        # a raised / debossed mark's arms may touch at points BY DESIGN inside legend lands (the print fuses them over one line width) -> row L
        inl = _in_boxes(np.array([[r["x"], r["y"], 0.0] for r in allnecks]).reshape(-1, 3), lands) if allnecks else np.zeros(0, bool)
        necks = [r for r, q in zip(allnecks, inl) if not q]; land_necks = [r for r, q in zip(allnecks, inl) if q]
    else:
        necks, land_necks = allnecks, []
    row("P point contact", f"{len(necks)} contact line(s) / hairline(s) <= {pr['neck_max']} wide on 15 section planes" + (f" (+ {len(land_necks)} inside legend lands, row L)" if land_necks else ""), f"no two surfaces within neck_max {pr['neck_max']}", "FLAG" if necks else "PASS",
        "; ".join(f"{r['kind']} {r['width']} at ({r['x']}, {r['y']}, {r['z']}) x{r['n']}" for r in necks[:8]), "two bodies touching along a line (or parted by a hairline) arrive as two parts or crack there — a vendor's ENGINEER flags this where its automatic check passes",
        f"bridge the contact with a web >= {wall_min} wide, or part the bodies by >= {vmin_}")
    def roundness(s):                                                            # normals of a slit are +/-n (one principal direction); of a hole they cover a plane (two)
        e = np.sort(np.linalg.eigvalsh(np.cov(nrm[s].T)))[::-1]
        return round(float(e[1] / e[0]), 2) if e[0] > 1e-9 else 0.0
    voids = regions(pts, g, g < np.maximum(thr_d, vmin_ * (~land)), link, a_per, lambda s: dict(cls="void", red_frac=round(float((g[s] < dmin).mean()), 2), roundness=roundness(s), in_land=round(float(land[s].mean()), 2)))
    Vd = [r for r in voids if r["vmed"] < dmin and not inland(r) and r["area"] >= SLV]
    Vs = [r for r in voids if r not in Vd and not inland(r) and r["extent"] >= S * vmin_]
    row("V void / slot", f"{len(voids)} void region(s) narrower than {vmin_}: {len(Vd)} below detail_min {dmin}, {len(Vs)} long slots (>= {S * vmin_} mm)", f"detail_min {dmin}; void_min {vmin_} over any {S * vmin_} mm", "FLAG" if (Vd or Vs) else "PASS", _where(Vd + Vs),
        "a void narrower than the smallest detail closes (MJF / SLA) or cannot be extruded (FDM); a long slot narrower than void_min does not clear its powder / resin",
        f"widen the stroke / slit to >= {dmin} (a long slot to >= {vmin_}) or drop it")
    H = [r for r in voids if r["roundness"] >= 0.5 and r["vmed"] < hmin and not inland(r) and r not in Vd and r["area"] >= SLV]
    row("H hole", f"{len(H)} round void(s) (normals in two directions) narrower than hole_min {hmin}; voids wider than {max(vmin_, hmin)} are not measured (they clear)", f"hole_min {hmin}", "FLAG" if H else "PASS", _where(H), "a hole below the process minimum closes or does not clear",
        f"open the hole to >= {hmin} or drop it (drill after printing)")
    Lg = [r for r in thin + voids if inland(r)]; Sl = [r for r in walls + wedges + voids if not inland(r) and r["area"] < SLV and r not in W]
    if Lg or Sl or land_necks:
        row("L legend lands / slivers (INFO)", f"{len(Lg)} sub-minimum region(s) and {len(land_necks)} point contact(s) inside legend land boxes; {len(Sl)} sliver(s) under {SLV} mm2 outside them", "listed - the coupon rule / census legend rows own the lands; a sliver fills or vanishes without loss", "INFO", _where(Lg, n=6) + (" || contacts: " + "; ".join(f"{r['kind']} {r['width']} at ({r['x']}, {r['y']})" for r in land_necks[:4]) if land_necks else "") + (" || slivers: " + _where(Sl, n=6) if Sl else ""), "raised / debossed legend glyphs are wedges and sub-line gaps by construction (the coupon decides); a tangency or boolean remnant below the process' detail cell has nothing to lose")
    O = B = C = []
    if pr.get("overhang_max_deg") is not None:
        zmin = m.bounds[0][2]; down = nrm[:, 2] < -np.sin(np.radians(pr["overhang_max_deg"])); ceiling = nrm[:, 2] < -0.985; bed = pts[:, 2] < zmin + 0.2
        O = regions(pts, -nrm[:, 2], down & ~ceiling & ~bed, link, a_per, lambda s: dict(cls="overhang", deg=round(float(np.degrees(np.arcsin(-nrm[s, 2].mean()))), 0)))
        def supported_ends(r):                                                   # a horizontal ray from just under each end of the ceiling, outward along its long axis, must hit material within reach: 2 hits = bridge, fewer = cantilever
            s = r["_s"]; P = pts[s]; a = int(np.argmax(np.ptp(np.asarray(P)[:, :2], axis=0))); n = 0
            for end, sign in ((P[np.argmin(P[:, a])], -1.0), (P[np.argmax(P[:, a])], 1.0)):
                d = np.zeros(3); d[a] = sign; o = end.copy(); o[2] -= 0.3; o[a] -= sign * 0.5
                loc, ir, _ = m.ray.intersects_location(o[None], d[None], multiple_hits=False)
                n += bool(len(ir)) and float(np.linalg.norm(loc[0] - o)) <= max(3.0, 2 * link)
            return n
        C = regions(pts, pts[:, 2], ceiling & ~bed, link, a_per, lambda s: dict(cls="ceiling", _s=s))
        for r in C:
            r["supports_n"] = supported_ends(r); r["cls"] = "bridge" if r["supports_n"] >= 2 else "cantilever"; del r["_s"]
        B = [r for r in C if r["cls"] == "bridge" and r["extent"] > pr["bridge_max"]]
        Ct = [r for r in C if r["cls"] == "cantilever" and r["extent"] > 2 * fmin]
        hard = pr.get("supports") == "none"
        row("O overhang (FDM)", f"{len(O)} down-facing region(s) steeper than {pr['overhang_max_deg']} deg from vertical (not the bed, not a ceiling); {len(Ct)} horizontal cantilever(s) (a ceiling with < 2 supported ends) longer than two line widths ({2 * fmin} mm)", "none when supports = none; listed otherwise", ("FLAG" if (O or Ct) else "PASS") if hard else "INFO", _where(O, k="deg") + (" || cantilevers: " + _where(Ct, k="extent") if Ct else ""),
            "an FDM layer needs the layer below it: beyond ~45..60 deg from vertical it sags or needs support (Prusa: 45..60 deg); a horizontal face with one supported edge is a 90 deg overhang — only a span with material at BOTH ends is a bridge", "re-orient the part, add a 45 deg lead-in, or allow supports there")
        row("B bridge (FDM)", f"{len(B)} horizontal ceiling(s) above the bed with both ends supported, longer than bridge_max {pr['bridge_max']}", "none when supports = none; listed otherwise", ("FLAG" if B else "PASS") if hard else "INFO", _where(B, k="extent"),
            "an unsupported horizontal span between two supports longer than the process' bridge limit droops", f"split the span below {pr['bridge_max']} with a rib, or allow interior supports")
    sz = []
    if pr.get("part_min"):
        srt = sorted(ext); pm = sorted(pr["part_min"])
        if any(srt[i] < pm[i] - 1e-6 for i in range(3)):
            sz.append(f"part {np.round(ext, 1).tolist()} below the process minimum {pr['part_min']}")
    if pr.get("build_max") and any(sorted(ext)[i] > sorted(pr["build_max"])[i] for i in range(3)):
        sz.append(f"part {np.round(ext, 1).tolist()} exceeds the build volume {pr['build_max']}")
    row("S size", f"bbox {np.round(ext, 1).tolist()} mm", f"part_min {pr.get('part_min')} .. build_max {pr.get('build_max')}", "FLAG" if sz else "PASS", "; ".join(sz), "the vendor refuses the file below its minimum part size or above its build volume", "resize, split the part, or pick a process row whose build fits")
    yb = float(((t >= wall_min) & (t < reco) & wall).sum() * a_per)
    row("Y below the recommended line", f"{yb:.1f} mm2 of wall-class surface between {wall_min} and {reco}", "INFO (design margin, not a manufacturability limit)", "INFO", "", "the vendor's map colours it yellow; the design margin (the census gate's wall gate) owns it")
    fin = np.isfinite(t)
    flagged = [r["rule"] for r in rows if r["verdict"] == "FLAG"]
    rec = dict(tool="scripts/print_dfm.py (hw-from-spec, vendor-independent)", version=VERSION, stl=os.path.relpath(os.path.abspath(path), ROOT), stl_md5=md5(path), process=process, piece=piece or os.path.splitext(os.path.basename(path))[0],
               faces=int(len(m.faces)), watertight=bool(m.is_watertight), bodies=n_bodies, bodies_expected=bodies_expected, area_mm2=round(area, 1), bbox=np.round(ext, 2).tolist(), samples=int(n_s), spacing=round(spacing, 3), link=round(link, 3),
               thresholds={k: pr.get(k) for k in ("wall_min", "wall_reco", "feature_min", "detail_min", "void_min", "hole_min", "neck_max", "slender", "overhang_max_deg", "bridge_max", "supports", "legend_land_min", "legend_void_min")},
               frac_below={str(b): round(float((t < b).mean()), 5) for b in (fmin, wall_min, reco)}, area_below={str(b): round(float((t < b).sum() * a_per), 1) for b in (fmin, wall_min, reco)},
               t_min=round(float(t[fin].min()), 3) if fin.any() else None, thin=thin[:40], voids=voids[:40], necks=necks[:40], overhangs=O[:20], ceilings=C[:20],
               verdict="FLAG" if flagged else "PASS", flagged=flagged, rows=rows, seconds=round(time.time() - t0, 1), lands=[list(map(float, b)) for b in (lands or [])])
    rec["sig"] = record_sig(rec, VERSION)                                         # the gate refuses a record whose body changed after it was written
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        json.dump(rec, open(os.path.join(out_dir, rec["piece"] + ".json"), "w"), indent=1)
        if render:
            heatmap(m, F, pr, os.path.join(out_dir, rec["piece"]))
    return rec


def heatmap(m, F, pr, prefix, views=None, size=1600):
    """Map renders: every face takes the MIN thickness of its samples (a face without a sample inherits the nearest sample), banded grey >= wall_reco,
    yellow [feature_min, wall_reco), red < feature_min; faces of a void narrower than void_min dark red. Six orthographic faces + two isos."""
    try:
        import matplotlib
    except ImportError:
        print("print_dfm: --render needs matplotlib (pip install matplotlib); records written, no PNGs", file=sys.stderr); return {}
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    nf = len(m.faces); ft = np.full(nf, np.inf); fg = np.full(nf, np.inf)
    np.minimum.at(ft, F["fid"], F["t"]); np.minimum.at(fg, F["fid"], F["g"])
    miss = np.bincount(F["fid"], minlength=nf) == 0
    if miss.any():
        _, j = cKDTree(F["pts"]).query(m.triangles_center[miss]); ft[miss] = F["t"][j]; fg[miss] = F["g"][j]
    col = np.tile([0.62, 0.62, 0.62], (nf, 1))
    col[ft < pr["wall_reco"]] = [1.0, 0.88, 0.0]; col[ft < pr["feature_min"]] = [1.0, 0.16, 0.0]; col[(fg < pr["void_min"]) & (ft >= pr["wall_reco"])] = [0.75, 0.25, 0.25]
    out = {}
    for name, (view, right) in (views or VIEWS).items():
        v = np.array(view, float); v /= np.linalg.norm(v); r = np.array(right, float); r -= r @ v * v; r /= np.linalg.norm(r); u = np.cross(r, v)
        shade = 0.75 + 0.25 * np.abs(m.face_normals @ v)
        tri = m.triangles; x = tri @ r; y = tri @ u; order = np.argsort(-(tri.mean(1) @ v))       # far first (painter)
        fig = plt.figure(figsize=(size / 200, size / 200 * 0.75), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_aspect("equal"); ax.axis("off")
        ax.add_collection(PolyCollection(np.stack([x, y], -1)[order], facecolors=np.clip((col * shade[:, None])[order], 0, 1), edgecolors="none", antialiased=False))
        ax.set_xlim(x.min() - 2, x.max() + 2); ax.set_ylim(y.min() - 2, y.max() + 2)
        ax.text(0.01, 0.99, f"{os.path.basename(prefix)} {name}  grey >= {pr['wall_reco']}  yellow {pr['feature_min']}..{pr['wall_reco']}  red < {pr['feature_min']}  (void < {pr['void_min']} dark red)  min {np.nanmin(ft[np.isfinite(ft)]):.2f}",
                transform=ax.transAxes, va="top", fontsize=6, family="monospace")
        p = f"{prefix}_{name}.png"; fig.savefig(p, facecolor="white"); plt.close(fig); out[name] = p
    return out


def _project():
    """The project (None outside one): print_targets, paths.decisions, paths.mech_record."""
    if not os.path.exists(os.path.join(ROOT, "project.yaml")):
        return None
    from project import Project
    return Project(os.path.join(ROOT, "project.yaml"))


def gate(dfm_dirs, open_findings=(), target=None):
    """PURE adopt gate (recomputes nothing) — see the docstring's --gate entry. Returns 1 on any problem."""
    bad = []; n = 0; P = _project(); table, _ = processes()
    opn = {}
    if open_findings:
        dec = P.path("decisions") if P else None; rows = open_decisions(dec) if dec else {}
        for e in open_findings:
            k, _, did = e.partition("=")
            if did in rows:
                opn[k] = f"{did} ({rows[did][:60]})"
            else:
                bad.append(f"--open {e}: {did!r} is not an OPEN row of {P.get('paths.decisions') if P else 'the decision log (no project.yaml found)'} — a finding stays open only under an OPEN decision")
    targets = (P.cfg.get("print_targets") or {}) if P else {}
    for d in dfm_dirs:
        d = d.rstrip("/"); parent = os.path.dirname(os.path.abspath(d)); tag = target or os.path.basename(parent); census = os.path.join(parent, "census")
        want = None
        if targets:
            if tag not in targets:
                bad.append(f"{d}: '{tag}' is not a print target (print_targets: {', '.join(targets)}) — lay the records out under <target>/dfm or pass --target"); continue
            want = targets[tag].get("dfm_process")
            if not want:
                bad.append(f"{d}: print_targets.{tag}.dfm_process is not set (kickoff C8a) — the gate cannot tell which process row the bodies must pass")
        recs = {}
        for ej in sorted(glob.glob(os.path.join(d, "*.json"))):
            try:
                e = json.load(open(ej))
            except Exception as ex:  # noqa: BLE001 — a corrupt record is a gate failure, not a traceback
                bad.append(f"{ej}: unreadable ({ex})"); continue
            n += 1; piece = os.path.basename(ej)[:-5]; recs[piece] = e
            if not verify_sig(e, VERSION):
                bad.append(f"{ej}: signature does not verify — the record was edited after it was written, or written by another rule set (rerun print_dfm {VERSION})"); continue
            if e.get("version") != VERSION:
                bad.append(f"{ej}: rule set {e.get('version')} != {VERSION} — rerun"); continue
            if want and e.get("process") != want:
                bad.append(f"{ej}: checked against process row '{e.get('process')}' but print_targets.{tag}.dfm_process = '{want}' — rerun with --process {want}"); continue
            if e.get("process") in table:
                cur = {k: table[e["process"]].get(k) for k in e.get("thresholds", {})}
                if cur != e.get("thresholds"):
                    bad.append(f"{ej}: thresholds differ from the current row '{e.get('process')}' ({', '.join(k for k in cur if cur[k] != e['thresholds'].get(k))}) — the table moved, rerun"); continue
            cj = os.path.join(census, piece + ".json")
            if os.path.exists(cj) and json.load(open(cj)).get("stl_md5") != e.get("stl_md5"):
                bad.append(f"{ej}: record of {str(e.get('stl_md5'))[:8]} but the census / STL of record is {str(json.load(open(cj)).get('stl_md5'))[:8]} — rerun"); continue
            stl = e["stl"] if os.path.isabs(e["stl"]) else os.path.join(ROOT, e["stl"])
            if not os.path.exists(stl) or md5(stl) != e["stl_md5"]:
                bad.append(f"{ej}: STL {e['stl']} missing or changed — rerun"); continue
            if e.get("verdict") != "PASS":
                msg = f"{ej}: verdict {e.get('verdict')}: " + "; ".join(f"{r['rule']} -> {r['where'][:160]}" for r in e["rows"] if r["verdict"] == "FLAG")
                if f"{tag}/{piece}" in opn:
                    print(f"PRINT-DFM GATE: OPEN {opn[f'{tag}/{piece}']} - {msg}")
                else:
                    bad.append(msg)
        for cj in glob.glob(os.path.join(census, "*.json")):
            if os.path.basename(cj)[:-5] not in recs:
                bad.append(f"{d}/{os.path.basename(cj)}: census record without a print_dfm record (run scripts/print_dfm.py on the body)")
        # the STL set of record: every body under this tag (sibling stl/ + the paths.mech_record glob under the parent) needs a same-md5 record
        have = {e.get("stl_md5") for e in recs.values()}
        stls = set(glob.glob(os.path.join(parent, "stl", "*.stl")))
        if P and P.get("paths.mech_record"):
            stls |= {f for f in glob.glob(os.path.join(ROOT, P.get("paths.mech_record"))) if os.path.abspath(f).startswith(parent + os.sep)}
        for f in sorted(stls):
            if md5(f) not in have:
                bad.append(f"{os.path.relpath(f, ROOT)}: body of the record set without a print_dfm record of its md5 (run scripts/print_dfm.py --process {want or '<row>'} --out {d} on it)")
    if not n:
        bad.append("no print_dfm records in " + ", ".join(dfm_dirs) + " (a green gate that checked nothing is a failing check)")
    for b in bad:
        print("PRINT-DFM GATE:", b)
    print(f"print_dfm gate: {n} bodies, {len(bad)} problem(s)")
    return 1 if bad else 0


def _label_verdict(lb):
    """verdict schema: `verdict: FLAG | PASS | n/a` (template) or `vendor: true | false | null` (older labels) -> 'FLAG' / 'PASS' / None."""
    if "verdict" in lb:
        v = str(lb["verdict"]).upper(); return v if v in ("FLAG", "PASS") else None
    return {True: "FLAG", False: "PASS"}.get(lb.get("vendor"))


def validate(write_doc=True, renders=()):
    """Run every labelled STL (cached by md5 + VERSION in val_dir), write the validation doc: vendor verdict vs ours per body, confusion matrix, rules
    fired. Returns the summary; `looser` lists the RULE DEFECTS (vendor FLAG, ours PASS)."""
    if not os.path.exists(PATHS["verdicts"]):
        sys.exit(f"print_dfm: no verdict record at {PATHS['verdicts']} (copy templates/docs/quotes/dfm_verdicts.yaml, append every vendor verdict)")
    labels = yaml.safe_load(open(PATHS["verdicts"]))["verdicts"] or []
    table, table_path = processes(); VAL_DIR = PATHS["val_dir"]
    os.makedirs(VAL_DIR, exist_ok=True); recs = []
    for lb in labels:
        path = lb["stl"] if os.path.isabs(lb["stl"]) else os.path.join(ROOT, lb["stl"])
        if not os.path.exists(path):
            sys.exit(f"print_dfm: labelled STL missing: {lb['stl']} (every verdict row needs its STL in the tree)")
        h = md5(path)
        assert h.startswith(str(lb["md5"])), f"{lb['stl']}: md5 {h[:8]} != label {lb['md5']} — the file changed after the verdict; relabel"
        cj = os.path.join(VAL_DIR, f"{h[:8]}.json"); rec = json.load(open(cj)) if os.path.exists(cj) else None
        thr = {k: table[lb["process"]].get(k) for k in (rec or {}).get("thresholds", {})}
        if not rec or rec.get("version") != VERSION or rec.get("stl_md5") != h or rec.get("process") != lb["process"] or rec.get("thresholds") != thr:
            rec = analyse(path, lb["process"], out_dir=VAL_DIR, piece=h[:8], render=any(k in lb["stl"] for k in renders)); print(f"[val] {os.path.basename(lb['stl'])} {rec['verdict']} {rec['seconds']} s", flush=True)
        recs.append((lb, rec))
    cm = defaultdict(int); per_rule = defaultdict(lambda: defaultdict(int)); looser = []; stricter = []
    rel = lambda p: os.path.relpath(p, ROOT)
    lines = ["# PRINT_DFM_VALIDATION.md — scripts/print_dfm.py against every vendor verdict on record", "",
             f"Generated by `scripts/print_dfm.py --validate` on {time.strftime('%Y-%m-%d')} (rule set {VERSION}); labels `{rel(PATHS['verdicts'])}`; process table `{rel(table_path)}`; per-body records and heat maps `{rel(VAL_DIR)}/<md5-8>*`.",
             "The rules are physics + published process minimums (every number cited in the table); nothing is fitted to a vendor. Where the vendor is LOOSER than the rule the rule stands (listed with its reason); a LOOSER verdict of OURS is a RULE DEFECT — fix the rule (physics, not a vendor fudge), re-validate.", "",
             "## 1. Body table", "", "| STL | md5 | process | vendor verdict (evidence) | our verdict (rules fired) | largest sub-minimum region: area mm2 x extent, min (class) | agreement | note |", "|---|---|---|---|---|---|---|---|"]
    for l, r in recs:
        vs = _label_verdict(l); ours = r["verdict"]; big = r["thin"][0] if r["thin"] else None
        ag = "unlabelled" if vs is None else ("agree" if ours == vs else ("STRICTER (ours flags)" if ours == "FLAG" else "**LOOSER — RULE DEFECT**"))
        if vs is not None:
            cm[(vs, ours)] += 1
            (looser if (vs == "FLAG" and ours == "PASS") else stricter if (vs == "PASS" and ours == "FLAG") else []).append(l["stl"])
            for ru in r["flagged"]:
                per_rule[ru.split()[0]]["vendor FLAG" if vs == "FLAG" else "vendor PASS"] += 1
        bigs = f"{big['area']} x {big['extent']}, {big['vmin']} ({big['cls']})" if big else "none"
        lines.append(f"| `{os.path.basename(l['stl'])}` | {l['md5']} | {l['process']} | {vs or 'n/a'} ({l.get('evidence', l.get('source', ''))}) | {ours} ({', '.join(x.split()[0] for x in r['flagged']) or '-'}) | {bigs} | {ag} | {l.get('note', '')} |")
    lines += ["", "## 2. Confusion matrix (labelled bodies)", "", "| | ours PASS | ours FLAG |", "|---|---|---|",
              f"| vendor PASS | {cm[('PASS', 'PASS')]} | {cm[('PASS', 'FLAG')]} (stricter — list each with its reason below the marker) |", f"| vendor FLAG | {cm[('FLAG', 'PASS')]} (**looser = rule defect**) | {cm[('FLAG', 'FLAG')]} |", "",
              "## 3. Rules fired, by vendor verdict", "", "| rule | fired on vendor-FLAG bodies | fired on vendor-PASS bodies (stricter) |", "|---|---|---|"]
    for ru in sorted(per_rule):
        lines.append(f"| {ru} | {per_rule[ru]['vendor FLAG']} | {per_rule[ru]['vendor PASS']} |")
    if write_doc:                                                                 # the generated sections are rewritten; the hand-written reading after the marker is kept
        VAL_DOC = PATHS["val_doc"]; old = open(VAL_DOC).read() if os.path.exists(VAL_DOC) else ""
        hand = old[old.index("<!-- hand: begin -->"):] if "<!-- hand: begin -->" in old else "<!-- hand: begin -->\n## 4. Reading (hand-written, kept across regenerations)\n\nFor every STRICTER row: the physical reason the rule stands. For every rule: which labelled bodies validate it, which it cannot be decided from.\n"
        os.makedirs(os.path.dirname(VAL_DOC), exist_ok=True); open(VAL_DOC, "w").write("\n".join(lines) + "\n\n" + hand)
    return dict(cm=dict((f"{k[0]}->{k[1]}", v) for k, v in cm.items() if v), per_rule={k: dict(v) for k, v in per_rule.items()}, looser=looser, stricter=stricter, recs=recs, lines=lines)


def rim_profile(root, rim=2.0, wall=2.0, lap_h=4.6, top=7.1):
    """Half profile of a wall of `wall` with a rim ring `rim` wide standing `root` mm on top of it over a lap step (the ring-root construction):
    wall x in [-wall-0.5, -0.5], rim x in [-0.5-root, -0.5-root+rim]."""
    from shapely.geometry import Polygon
    r0 = -0.5 - root; r1 = r0 + rim
    return Polygon([(-wall - 0.5, 0), (12, 0), (12, 2), (-0.5, 2), (-0.5, lap_h), (r1, lap_h), (r1, top), (r0, top), (r0, lap_h), (-wall - 0.5, lap_h)])


def selftest():
    import tempfile
    global PATHS
    PATHS = dict(PATHS, processes=TEMPLATE_TABLE if os.path.exists(TEMPLATE_TABLE) else PATHS["processes"])
    global ROOT
    ROOT0 = ROOT
    with tempfile.TemporaryDirectory() as d:
        ROOT = d                                                                      # records store the STL path relative to the project root
        p1 = os.path.join(d, "plate08.stl"); trimesh.creation.box((30.0, 30.0, 0.8)).export(p1)
        r = analyse(p1, "jlc_mjf_pa12", n_s=20000)
        assert "W wall" in r["flagged"] and abs(r["thin"][0]["vmed"] - 0.8) < 0.05 and r["thin"][0]["cls"] == "wall", r["rows"][0]
        assert "R root under a rim / ledge" not in r["flagged"] and abs(r["thin"][0]["ray_med"] - 0.8) < 0.05, ("a free plate has no root; the ray must read it", r["thin"][0])
        p0 = os.path.join(d, "rib06.stl"); trimesh.creation.box((60.0, 6.0, 0.6)).export(p0)                     # review 0.8.0 F1: a free 0.6 rib = W only
        r = analyse(p0, "xometry_mjf_pa12", n_s=20000)
        assert r["flagged"] == ["W wall"] and r["t_min"] is not None and all(x["verdict"] != "FLAG" or x["fix"] for x in r["rows"]), r["flagged"]
        p2 = os.path.join(d, "plate20.stl"); trimesh.creation.box((30.0, 30.0, 2.0)).export(p2)
        r = analyse(p2, "jlc_mjf_pa12", n_s=20000)
        assert r["verdict"] == "PASS" and not r["thin"], r["rows"]                                   # convex 90 deg edges everywhere: none may read thin
        # eval 14: a 0.5 root under a 2.0 rim over 90 mm — rays read >= 2.0 everywhere, the root reads 0.5 on the inner face -> W + R FLAG
        p3 = os.path.join(d, "root05.stl"); trimesh.creation.extrude_polygon(rim_profile(0.5), 90.0).export(p3)
        r = analyse(p3, "jlc_mjf_pa12", n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root05")
        big = r["thin"][0]
        assert r["verdict"] == "FLAG" and 0.45 <= big["vmin"] <= 0.6 and big["extent"] >= 89 and big["cls"] == "wall" and "R root under a rim / ledge" in r["flagged"], (big, r["flagged"])
        p4 = os.path.join(d, "root13.stl"); trimesh.creation.extrude_polygon(rim_profile(1.3), 90.0).export(p4)   # the same geometry at root 1.3 -> PASS
        r = analyse(p4, "jlc_mjf_pa12", n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root13")
        assert r["verdict"] == "PASS", r["flagged"]
        r = analyse(p3, "jlc_sla_9600", n_s=20000)
        assert "S size" not in r["flagged"], r["rows"]
        p5 = os.path.join(d, "tiny.stl"); trimesh.creation.box((1.0, 5.0, 12.0)).export(p5)
        assert "S size" in analyse(p5, "jlc_sla_9600", n_s=5000)["flagged"]
        # review 0.8.0 F8: rule M — an open mesh and a two-body file FLAG; --bodies 2 accepts the pair
        bx = trimesh.creation.box((20.0, 20.0, 5.0)); bx.faces = bx.faces[2:]; p6 = os.path.join(d, "open.stl"); bx.export(p6)
        assert "M manifold" in analyse(p6, "jlc_mjf_pa12", n_s=5000)["flagged"], "an open mesh must FLAG M"
        a2 = trimesh.creation.box((20.0, 20.0, 2.0)); b2 = trimesh.creation.box((20.0, 20.0, 2.0)); b2.apply_translation((40.0, 0, 0)); p7 = os.path.join(d, "two.stl"); trimesh.util.concatenate([a2, b2]).export(p7)
        assert "M manifold" in analyse(p7, "jlc_mjf_pa12", n_s=5000)["flagged"] and "M manifold" not in analyse(p7, "jlc_mjf_pa12", n_s=5000, bodies_expected=2)["flagged"], "two bodies FLAG unless expected"
        # review 0.8.0 F25: a T-section's 18 mm free arms are cantilevers (O), an upside-down U's 32 mm roof is a bridge (B)
        from shapely.geometry import Polygon
        rotx = trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0])
        tee = trimesh.creation.extrude_polygon(Polygon([(-2, 0), (2, 0), (2, 15), (20, 15), (20, 18), (-20, 18), (-20, 15), (-2, 15)]), 10.0); tee.apply_transform(rotx); p8 = os.path.join(d, "tee.stl"); tee.export(p8)
        r = analyse(p8, "home_fdm_04", n_s=20000); ro = next(x for x in r["rows"] if x["rule"].startswith("O")); rb = next(x for x in r["rows"] if x["rule"].startswith("B"))
        assert "2 horizontal cantilever(s)" in ro["value"] and rb["value"].startswith("0 horizontal"), (ro["value"], rb["value"])
        pi_ = trimesh.creation.extrude_polygon(Polygon([(-20, 0), (-16, 0), (-16, 15), (16, 15), (16, 0), (20, 0), (20, 18), (-20, 18)]), 10.0); pi_.apply_transform(rotx); p9 = os.path.join(d, "pi.stl"); pi_.export(p9)
        r = analyse(p9, "home_fdm_04", n_s=20000); ro = next(x for x in r["rows"] if x["rule"].startswith("O")); rb = next(x for x in r["rows"] if x["rule"].startswith("B"))
        assert "0 horizontal cantilever(s)" in ro["value"] and rb["value"].startswith("1 horizontal"), (ro["value"], rb["value"])
        # the gate (review 0.8.0 F5 / F6 / F7 / F28): FLAG fails; --open needs an OPEN decision row; a tampered record, a changed STL, an uncensused
        # STL of the record set, a laxer process row than the target's and a census record without a dfm record all fail
        import contextlib, io
        def quiet(*a, **k):
            with contextlib.redirect_stdout(io.StringIO()):
                return gate(*a, **k)
        tag = os.path.basename(d); G = [os.path.join(d, "dfm")]
        assert quiet(G) == 1, "FLAG must fail"
        assert quiet(G, [f"{tag}/root05=D-00"]) == 1, "--open without a project / decision log must fail"
        os.makedirs(os.path.join(d, "docs", "governance")); open(os.path.join(d, "docs", "governance", "DECISIONS.md"), "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-07** | d | **OPEN** | widen the root | p | r |\n| CC-010 | d | APPLIED | x | p | r |\n")
        open(os.path.join(d, "project.yaml"), "w").write(f"project: {{name: t, scope: mech}}\npaths: {{mech_record: 'stl/*.stl'}}\nprint_targets: {{{tag}: {{dfm_process: jlc_mjf_pa12}}}}\n")
        assert quiet(G, [f"{tag}/root05=WHATEVER"]) == 1 and quiet(G, [f"{tag}/root05=CC-010"]) == 1, "a free string or an APPLIED row is not an OPEN decision"
        assert quiet(G, [f"{tag}/root05=D-07"]) == 0, "an OPEN row names the finding"
        rj = os.path.join(d, "dfm", "root13.json"); e = json.load(open(rj)); e["verdict"] = "FLAG"; json.dump(e, open(rj, "w")); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a hand-edited record fails the signature"
        e["verdict"] = "PASS"; json.dump(e, open(rj, "w")); assert quiet(G, [f"{tag}/root05=D-07"]) == 0, "restored body verifies again"
        os.makedirs(os.path.join(d, "stl")); import shutil; shutil.copy(p1, os.path.join(d, "stl", "plate08.stl")); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a body of the record set without a record fails"
        os.remove(os.path.join(d, "stl", "plate08.stl"))
        analyse(p4, "protolabs_mjf_pa12", n_s=20000, out_dir=os.path.join(d, "dfm"), piece="root13"); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a laxer process row than print_targets.<t>.dfm_process fails"
        analyse(p4, "jlc_mjf_pa12", n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root13"); assert quiet(G, [f"{tag}/root05=D-07"]) == 0
        assert quiet(G, [f"{tag}/root05=D-07"], target="nope") == 1, "an unknown print target fails"
        os.makedirs(os.path.join(d, "census")); json.dump(dict(stl=p4, stl_md5="0" * 32), open(os.path.join(d, "census", "root13.json"), "w"))
        assert quiet(G, [f"{tag}/root05=D-07"]) == 1
        json.dump(dict(stl=p4, stl_md5=md5(p4)), open(os.path.join(d, "census", "root13.json"), "w")); json.dump({}, open(os.path.join(d, "census", "orphan.json"), "w"))
        assert quiet(G, [f"{tag}/root05=D-07"]) == 1
        os.remove(os.path.join(d, "census", "orphan.json")); assert quiet(G, [f"{tag}/root05=D-07"]) == 0
        # the validation loop on the verdict schema: a labelled FLAG we pass is a RULE DEFECT
        PATHS.update(verdicts=os.path.join(d, "v.yaml"), val_dir=os.path.join(d, "val"), val_doc=os.path.join(d, "VAL.md"))
        yaml.safe_dump(dict(verdicts=[dict(stl=p3, md5=md5(p3)[:8], process="jlc_mjf_pa12", vendor="x", date="2026-01-01", verdict="FLAG", evidence="e1"),
                                      dict(stl=p4, md5=md5(p4)[:8], process="jlc_mjf_pa12", vendor="x", date="2026-01-01", verdict="FLAG", evidence="e2"),
                                      dict(stl=p2, md5=md5(p2)[:8], process="jlc_mjf_pa12", vendor=False, source="old schema")]), open(PATHS["verdicts"], "w"))
        with contextlib.redirect_stdout(io.StringIO()):
            v = validate()
        assert v["looser"] == [p4] and v["cm"] == {"FLAG->FLAG": 1, "FLAG->PASS": 1, "PASS->PASS": 1}, v["cm"]
        doc = open(PATHS["val_doc"]).read(); assert "RULE DEFECT" in doc and "<!-- hand: begin -->" in doc
        assert _label_verdict(dict(vendor=None)) is None and _label_verdict(dict(verdict="n/a")) is None
    ROOT = ROOT0
    print("selftest OK: 0.8 plate -> W FLAG only (ray reads 0.8), 0.6 x 60 rib -> W only, 2.0 plate -> PASS (no convex-edge artefact), 0.5 root under a 2.0 rim x 90 -> W + R FLAG, root 1.3 -> PASS, SLA size rule, M (open mesh / two bodies / --bodies 2), O cantilever vs B bridge, gate (FLAG / --open only an OPEN row / tampered record / uncensused STL / laxer row / md5 / orphan census), validate (RULE DEFECT, both label schemas)")


def main():
    ap = argparse.ArgumentParser(description="vendor-independent print manufacturability check (hw-from-spec); see references/print-dfm.md")
    ap.add_argument("stl", nargs="*"); ap.add_argument("--process", help="row of the process table (--list shows them)"); ap.add_argument("--out", help="record dir (DIR/<piece>.json)"); ap.add_argument("--piece"); ap.add_argument("--render", action="store_true", help="heat maps beside the record (matplotlib)")
    ap.add_argument("--samples", type=int); ap.add_argument("--bodies", type=int, default=1, help="expected body count (rule M; default 1)"); ap.add_argument("--land", nargs=4, type=float, action="append", metavar=("X0", "Y0", "X1", "Y1"), help="legend land box (repeatable)")
    ap.add_argument("--processes", help=f"process table (default {os.path.relpath(DEFAULTS['processes'])}, else the skill template)"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--gate", nargs="+", metavar="DFM_DIR"); ap.add_argument("--open", nargs="*", default=[], metavar="TAG/PIECE=ID"); ap.add_argument("--target", help="--gate: the print target the DIRs belong to (default: DIR's parent name)")
    ap.add_argument("--validate", action="store_true"); ap.add_argument("--verdicts", help=f"default {os.path.relpath(DEFAULTS['verdicts'])}"); ap.add_argument("--val-dir"); ap.add_argument("--val-doc"); ap.add_argument("--render-validation", nargs="*", default=[], metavar="SUBSTR")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    for k in ("processes", "verdicts", "val_dir", "val_doc"):
        if getattr(a, k):
            PATHS[k] = os.path.abspath(getattr(a, k))
    if a.selftest:
        selftest(); return 0
    if a.list:
        table, p = processes(); print(f"process rows of {p}:")
        for k, v in table.items():
            print(f"  {k:22s} {v.get('vendor', '')} / {v.get('process', '')}: wall_min {v.get('wall_min')} feature_min {v.get('feature_min')} detail_min {v.get('detail_min')} void_min {v.get('void_min')} hole_min {v.get('hole_min')}" + ("  (BLOCKED: wall_min null)" if v.get("wall_min") is None else ""))
        return 0
    if a.gate:
        return gate(a.gate, a.open, a.target)
    if a.validate:
        c = validate(renders=a.render_validation); print(json.dumps(dict(cm=c["cm"], per_rule=c["per_rule"], stricter=c["stricter"]), indent=1))
        for s in c["looser"]:
            print(f"RULE DEFECT: vendor FLAG, ours PASS: {s} — fix the rule (physics), re-validate, run skill_retro.py")
        return 1 if c["looser"] else 0
    if not a.stl:
        ap.error("give one or more STL files (or --list / --gate / --validate / --selftest)")
    if not a.process:
        table, p = processes(); ap.error(f"--process <row> is required; rows of {p}: {', '.join(table)}")
    missing = [p for p in a.stl if not os.path.isfile(p)]
    if missing:
        print(f"print_dfm: no such file: {', '.join(missing)}", file=sys.stderr); return 2
    rc = 0
    for p in a.stl:
        r = analyse(p, a.process, n_s=a.samples, lands=a.land, out_dir=a.out, piece=a.piece, render=a.render, bodies_expected=a.bodies)
        print(f"{p}: {r['verdict']} ({a.process}) faces {r['faces']} watertight {r['watertight']} area {r['area_mm2']} mm2 samples {r['samples']} t_min {r['t_min']} {r['seconds']} s  [rows: verdict rule: measured | limit | where (box = xmin ymin zmin xmax ymax zmax) | fix]")
        for row in r["rows"]:
            print(f"  {row['verdict']:5s} {row['rule']}: {row['value']} | {row['limit']} | {row['where'][:300]}" + (f" | fix: {row['fix']}" if row["verdict"] == "FLAG" and row.get("fix") else ""))
        rc |= r["verdict"] == "FLAG"
    return rc


if __name__ == "__main__":
    sys.exit(main())
