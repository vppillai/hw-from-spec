#!/usr/bin/env python3
"""scripts/print_dfm.py — vendor-independent manufacturability check for printed bodies (MJF / SLA / FDM), run on the MESH before every upload.

Rules come from physics and the published process minimums, parameterised per process row in `20-design/dfm_processes.yaml` (every number cited
[V] fetched / [K] known); a vendor's DFM verdicts (`60-orders/quotes/dfm_verdicts.yaml`) are a VALIDATION set, never a fitting target. Nothing in
here is tuned to one vendor. `references/print-dfm.md` carries the loop; this docstring carries the mechanism.

Measures (per surface sample, area-weighted, fixed seed):
  t_ray  material thickness along the inverse normal (the census ray, origin nudged 1e-3 INTO the material — nudged the other way it hit its own
         face and read inf on every sample while the ball hid the defect — assert the measure, not only the verdict); the hit face's angle classifies wall (< 30 deg) / wedge
  t_med  tangent-ball thickness limited by OPPOSING faces only (normals within ~45 deg of the inverse normal) = the largest inscribed ball tangent
         at the sample: reads a NECK / ROOT that no ray sees (a rim ring set inboard of its wall over a lap step stands on a root the width of
         the overlap while every ray through it reads the full rim) and does not read a convex 90 deg edge thin (a perpendicular face is not
         opposing)
  t_k    the same ball against ANY face that faces back at all (included angle < ~87 deg) = the knife-edge field: a ridge of included angle a reads
         2 s tan(a/2) at distance s from its tip, so its sub-feature_min tip band is feature_min / (2 tan(a/2)) long — that band is what the tip loses
  t = min(t_ray, t_med);  g = both measures cast OUTWARD = void / slot / hole width
Samples below a threshold are linked on the surface (pairs within max(3 spacings, 2.5 mm)) into REGIONS (area, extent, min / median, class).
Rules (each a row: process parameter + physical reason + fix; verdict FLAG / PASS / INFO):
  M  manifold / bodies: non-manifold or open edges (located; those inside legend boxes listed), inconsistent winding, or a solid count other than
     --bodies N (default 1) — two solids that touch at a vertex / edge / face without a union arrive as pieces; an open mesh has no inside
  C  closed cavity: an inward-facing closed shell = a sealed void; FLAG where it traps media (powder / resin), INFO on FDM (the slicer hollows it)
  W  wall: wall-class region with median t < wall_min and extent >= slender x t — [K] slenderness heuristic: a strip ~10 x longer than it is thick
     bends / cracks under depowdering, cleaning and handling; shorter = a feature (rule F)
  R  root: the W regions whose RAY thickness is >= wall_min = a rim / ledge standing on a root narrower than its own wall; its own row
  Z  skin (layer processes): a wall-class region whose normals are within 30 deg of the print Z is a horizontal skin = a LAYER count, not a perimeter
     count; its floor is skin_min_layers x layer, not wall_min (a 0.6 sheet printed flat is three layers, printable; stood up it is a 0.6 wall)
  F  feature: short wall-class region with median t < feature_min that is not a sliver — below the smallest formable feature it does not form /
     breaks off; sliver = area < sliver_area AND extent <= 2 x its thickness (a tangency / boolean patch); a pin Ø0.4 x 3.5 is a feature
  K  knife edge: a t_k region (wedge, tip below feature_min) whose tip band feature_min / (2 tan(a/2)) is longer than feature_min (included angle
     below 2 atan(1/2) = 53 deg) over >= slender x feature_min — the tip loses more than one feature cell of its height [K]; a 60 deg ridge loses
     0.43, a 90 deg edge 0.25 (rounds), a 30 deg rail tip 0.93 (frays); a chamfer / ramp whose thin end stays >= feature_min has no band
  P  point contact: t <= neck_max on 15 section planes — two surfaces touching along a line / parted by a hairline arrive as pieces
  V  void: g < detail_min anywhere (an engraved stroke / slit narrower than the smallest detail closes — MJF / SLA: fuses; FDM: one line width, the
     line squish / gap fill closes it); media processes only: detail_min <= g < void_min over >= slender x void_min (a long slot does not clear its
     powder / resin). FDM has no long-slot rule: a slot wider than one line is two walls with air between, nothing to clear (void_min null)
  H  hole: a round void (normals in two directions) with g < hole_min
  O  overhang (layer processes): down-facing faces steeper than overhang_max_deg (+1 deg tolerance) from vertical, not the bed, not a ceiling, whose
     footprint reaches further than bridge_max across (a shorter one is bridged from its edges: the round top of a slot, a shallow recess roof);
  B  bridge (layer processes): a horizontal ceiling above the bed whose SPAN exceeds bridge_max — the span is measured by rays from the ceiling sample
     nearest its inscribed-circle centre: both in-plane axes supported -> min(inscribed circle, chord_x, chord_y); exactly one axis -> that chord (a
     pi roof open at the ends reads its width, a tunnel its width, a rebate split by full-height lands one strip); no axis -> the inscribed circle (a
     relief ring reads its width). Never a bbox extent, never a raster run through the footprint mask.
  S  size: bbox against part_min / build_max
  L  INFO: regions inside legend boxes (the coupon rule owns them) and slivers
  Y  INFO: wall-class surface between wall_min and wall_reco (the vendor's grey line = the design margin; the census gate owns it)
Legend boxes: (x0, y0, z0, x1, y1, z1) in the print frame (a 4-tuple x0 y0 x1 y1 spans every Z), written by the generators beside the record
(`<piece>.boxes.json`) and loaded by the CLI with --boxes, so a CLI run reproduces the gated record byte for byte (no run time inside the record);
inside a box the wall limit is legend_land_min, the void limit legend_void_min, and every rule's findings are listed (row L) instead of flagged —
a region is 'inside' when >= 50 % of its samples are.
Heat map (--render, needs matplotlib): faces coloured by the MIN thickness of their samples — grey >= wall_reco, yellow, red < feature_min,
voids narrower than void_min (detail_min on FDM) dark red — six orthographic faces + two isos, the same convention the vendors' viewers use.

CLI (paths default to the project root = the nearest parent holding project.yaml, else the cwd; the process table falls back to the skill's
`templates/20-design/dfm_processes.yaml` when the project has none yet):
  scripts/print_dfm.py --process <row> <mesh.stl>... [--out DIR] [--piece NAME] [--render] [--samples N] [--boxes boxes.json] [--land x0 y0 x1 y1 ...]
                       [--supports none|interior|any] [--bodies N]
      one record per body (DIR/<piece>.json [+ DIR/<piece>.boxes.json] [+ DIR/<piece>_<view>.png]); prints one line per rule; exit 1 when any body FLAGs
  scripts/print_dfm.py --list                                 the process rows and their thresholds
  scripts/print_dfm.py --gate <dfm_dir>... [--target <print target>] [--open <tag>/<piece>=<decision id> ...] [--expect <tag>/<piece>=<reason> ...]
      PURE adopt gate (recomputes nothing). FAILs on: an STL of the record set without a same-md5 record (the sibling `stl/` of each DIR and the
      `paths.mech_record` glob under DIR's parent); a record whose `sig` does not verify (hand-edited, or written by another rule set); a record
      `version` != this VERSION or `thresholds` != the current table row; a record `process` != `print_targets.<t>.dfm_process` (t = --target or
      DIR's parent name); a sibling census/<piece>.json with another md5; a census piece without a dfm record; a verdict FLAG — unless --open
      <tag>/<piece>=<id> names a row of paths.decisions whose status is OPEN (printed with its topic; any other id = FAIL) or --expect
      <tag>/<piece>=<reason> says the body FLAGs BY DESIGN (a coupon that tests the limit; printed with its reason on every run). Neither is a
      waiver: the record still says FLAG. A DIR without a sibling census/ is a record-only dir (coupons, dummies, colour bodies): its records are
      checked the same way.
  scripts/print_dfm.py --validate [--verdicts Y] [--val-dir D] [--val-doc M] [--render-validation substr ...]
      run every labelled STL (records cached by md5 + rule-set version), group the files by GEOMETRY (equal faces, volume within 0.05 mm3, area
      within 0.5 mm2, bbox within 0.01 — four uploads of one tray are one data point), write the validation doc (vendor vs ours per geometry,
      confusion matrix, rules fired, coverage per mechanism, thresholds with their [V] / [K] tags); a geometry the vendor FLAGGED that we PASS is a
      RULE DEFECT -> printed, exit 1
  scripts/print_dfm.py --selftest                             a positive AND a negative construct per rule (a dead measure passes a verdict-only test)
Exit codes: 0 PASS, 1 FLAG (or a gate / validation problem), 2 usage / configuration (missing file, unknown row, missing table or dependency).
Dependencies: numpy trimesh scipy shapely rtree networkx mapbox-earcut pyyaml (`--render`: matplotlib).
ponytail: random area-weighted samples + KD-tree geometry, per-face MIN colouring; finds and sizes a defect, not a CAD thickness analysis.
"""
import sys, os, json, hashlib, time, glob, argparse, re
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
VERSION = "0.10.3"        # rule-set version stamped into every record (the validation cache is keyed on it); bump when a rule or a measure changes
WALL_DEG = 30.0          # limiting face within 30 deg of parallel = wall / neck / root; otherwise wedge (census convention)
COS_OPP = 0.7            # main field: a face 'opposes' the sample when its normal is within ~45 deg of the inverse normal (a 45 deg ramp under a skin counts, a 90 deg side face does not)
COS_K = 0.05             # knife field: any face that faces back at all (included angle < ~87 deg); a 90 deg side face still does not
KNIFE_BAND = 1.0         # [K] K flags when the tip band is longer than KNIFE_BAND x feature_min (= included angle < 2 atan(1 / (2 KNIFE_BAND)) = 53 deg)
NOISE_N = 5              # a region of fewer samples is sampling noise (a tessellation sliver), not a feature
RAY_SKIP = 0.02          # a ray hit closer than this is the origin face (numerical); the ball owns necks below it (rule P)
OVERHANG_TOL = 1.0       # deg: a 45 deg lead-in drawn at exactly overhang_max_deg is not an overhang
VIEWS = {"top": ((0, 0, -1), (1, 0, 0)), "sole": ((0, 0, 1), (1, 0, 0)), "left": ((1, 0, 0), (0, 1, 0)), "right": ((-1, 0, 0), (0, -1, 0)),
         "front": ((0, 1, 0), (1, 0, 0)), "rear": ((0, -1, 0), (-1, 0, 0)), "iso": ((-1, -1, -1), (1, -1, 0)), "iso_rear": ((1, 1, -1), (-1, 1, 0))}   # (direction the camera looks along, screen-right)
THRESHOLD_KEYS = ("wall_min", "wall_reco", "feature_min", "detail_min", "void_min", "hole_min", "neck_max", "slender", "sliver_area", "layer", "skin_min_layers", "media",
                  "overhang_max_deg", "bridge_max", "supports", "legend_land_min", "legend_void_min")


def project_root(start=None):
    d = os.path.abspath(start or os.environ.get("HWFS_PROJECT") or os.getcwd())
    while True:
        if os.path.exists(os.path.join(d, "project.yaml")):
            return d
        if os.path.dirname(d) == d:
            return os.path.abspath(start or os.getcwd())
        d = os.path.dirname(d)


ROOT = project_root()
DEFAULTS = dict(processes=os.path.join(ROOT, "20-design", "dfm_processes.yaml"), verdicts=os.path.join(ROOT, "60-orders", "quotes", "dfm_verdicts.yaml"),
                val_dir=os.path.join(ROOT, "40-case", "dfm_validation"), val_doc=os.path.join(ROOT, "80-reviews", "PRINT_DFM_VALIDATION.md"))
TEMPLATE_TABLE = os.path.join(os.path.dirname(HERE), "templates", "20-design", "dfm_processes.yaml")
PATHS = dict(DEFAULTS)


def md5(path):
    return hashlib.md5(open(path, "rb").read()).hexdigest()


def processes(path=None):
    p = path or PATHS["processes"]
    if not os.path.exists(p) and not path and os.path.exists(TEMPLATE_TABLE):
        p = TEMPLATE_TABLE
    if not os.path.exists(p):
        print(f"print_dfm: no process table at {p} (copy templates/20-design/dfm_processes.yaml to 20-design/ or pass --processes)", file=sys.stderr); sys.exit(2)
    return yaml.safe_load(open(p))["processes"], p


def geom_sig(m):
    """Geometry signature independent of the STL writer (triangle order, ASCII / binary): face count, volume, area, bbox -> md5-8 (the validation groups by it)."""
    return hashlib.md5(json.dumps([int(len(m.faces)), round(float(m.volume), 1), round(float(m.area), 0), np.round(m.bounds, 1).tolist()]).encode()).hexdigest()[:8]


def norm_boxes(boxes):
    """Legend boxes -> list of (x0, y0, z0, x1, y1, z1); a legacy 4-tuple (x0, y0, x1, y1) spans every Z."""
    out = []
    for b in boxes or []:
        b = [float(v) for v in b]
        if len(b) == 4:
            b = [b[0], b[1], -1e9, b[2], b[3], 1e9]
        assert len(b) == 6, b
        out.append((min(b[0], b[3]), min(b[1], b[4]), min(b[2], b[5]), max(b[0], b[3]), max(b[1], b[4]), max(b[2], b[5])))
    return out


def load_boxes(path):
    return norm_boxes(json.load(open(path))) if path else []


def _tangent_ball(pts, nrm, sign, r0, cos_opps=(COS_OPP,), query=None):
    """Largest ball tangent at every sample on the material side (sign -1) or the air side (+1) that no sample with an opposing normal enters, once per
    opposing-cone cosine in cos_opps. Returns [(2 r, angle of the limiting face in deg)]; inf / nan where nothing opposes within 2 r0. One KD query
    per sample: a smaller tangent ball is inside the r0 ball, so the limiting point is always among the r0 ball's members."""
    tree = cKDTree(pts)
    qp, qn = query if query is not None else (pts, nrm)
    c0 = qp + sign * qn * r0
    nb = tree.query_ball_point(c0, r0 * 1.0001)
    T = [np.full(len(qp), np.inf) for _ in cos_opps]; A = [np.full(len(qp), np.nan) for _ in cos_opps]
    for i, idx in enumerate(nb):
        if len(idx) < (2 if query is None else 1):
            continue
        idx = np.asarray(idx); dq = pts[idx] - qp[i]; h = sign * (dq @ qn[i])
        dots = nrm[idx] @ qn[i]
        r_all = (dq ** 2).sum(1) / (2 * np.where(h > 1e-6, h, np.inf))
        for j, co_ in enumerate(cos_opps):
            sel = (dots < -co_) & (h > 1e-6)
            if not sel.any():
                continue
            k = int(np.argmin(np.where(sel, r_all, np.inf)))
            T[j][i] = 2 * r_all[k]; A[j][i] = np.degrees(np.arccos(np.clip(-dots[k], -1, 1)))
    return list(zip(T, A))


def _rays(m, pts, nrm, sign):
    """census ray from the sample nudged 1e-3 INTO the side it travels (sign -1 = into the material, +1 = into the air) along sign * normal, so the
    first hit is the far face and not the origin face: (distance, hit face angle; 0 = parallel). Nudged the other way
    every ray hit its own face at 0.001, was discarded as a self-hit and read inf — R then fired on every thin wall."""
    orig = pts + sign * nrm * 1e-3
    loc, ir, it = m.ray.intersects_location(orig, sign * nrm, multiple_hits=False)
    d = np.full(len(pts), np.inf); a = np.full(len(pts), np.nan)
    if len(ir):
        dd = np.linalg.norm(loc - orig[ir], axis=1); ok = dd > RAY_SKIP          # the intersector returns the origin face itself as a 0.000 hit
        d[ir[ok]] = dd[ok]
        a[ir[ok]] = np.degrees(np.arccos(np.clip(-np.einsum("ij,ij->i", nrm[ir[ok]], m.face_normals[it[ok]]), -1, 1)))
    return d, a


def field(m, n_s, seed=0, r0=1.0, r0_void=0.75):
    pts, fid = trimesh.sample.sample_surface(m, n_s, seed=seed); nrm = m.face_normals[fid]
    t_ray, a_ray = _rays(m, pts, nrm, -1)
    (t_med, a_med), (t_k, a_k) = _tangent_ball(pts, nrm, -1, r0, (COS_OPP, COS_K))
    g_ray, ga_ray = _rays(m, pts, nrm, +1)
    g_ray[ga_ray >= WALL_DEG] = np.inf                                       # a re-entrant corner is not a slot (census convention)
    (g_med, _), = _tangent_ball(pts, nrm, +1, r0_void)
    use_med = t_med < t_ray
    return dict(pts=pts, fid=fid, nrm=nrm, t=np.where(use_med, t_med, t_ray), ang=np.where(use_med, a_med, a_ray), t_ray=t_ray, t_med=t_med, t_k=t_k, a_k=a_k,
                g=np.minimum(g_ray, g_med), g_ray=g_ray, g_med=g_med)


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


def _footprint_mask(P, spacing, cell=0.25):
    """Rasterised sample footprint: (mask, k, cell, lo) — the sampling gaps closed by a dilation of k cells (k = ceil(spacing / cell) + 1)."""
    from scipy.ndimage import binary_dilation
    cell = max(cell, spacing); k = int(np.ceil(spacing / cell)) + 1
    xy = np.asarray(P)[:, :2]; lo = xy.min(0) - (k + 2) * cell
    ij = np.floor((xy - lo) / cell).astype(int); shape = tuple(ij.max(0) + k + 3)
    mask = np.zeros(shape, bool); mask[ij[:, 0], ij[:, 1]] = True
    return binary_dilation(mask, iterations=k), k, cell, lo


def span_edt(P, spacing, cell=0.25):
    """Shortest crossing of a footprint bounded all round = the largest inscribed circle: Euclidean distance transform of the closed footprint,
    2 x (max - k) x cell. A 2 x 40 tunnel roof reads ~2, not 40."""
    from scipy.ndimage import distance_transform_edt
    mask, k, cell, _ = _footprint_mask(P, spacing, cell)
    return round(float(max(0.0, distance_transform_edt(mask).max() - k) * 2 * cell), 1)


def span_rays(m, P, spacing, cell=0.25):
    """Bridge span of a ceiling and how many of its ends rest on material, measured with RAYS from the inscribed-circle centre: the origin is the
    ceiling SAMPLE nearest the EDT maximum (a real point of the face, 0.05 below it); along each in-plane axis a ray each way counts a hit only within
    the footprint extent + 1 -> ends[a] in 0..2, chord[a] = the two hit distances summed. ends [2, 2] -> min(inscribed circle, chord_x, chord_y) (a
    merged word reads its stroke width, a rectangle its inscribed circle); exactly one axis with both ends on material -> that chord (a pi roof open
    at the ends, a tunnel, a rebate split by full-height lands); otherwise the inscribed circle (a relief ring reads its width). Not a bbox extreme and
    not a raster run: a run through a MERGED cluster reads any row of it and the mask dilation erases lands thinner than two cells."""
    from scipy.ndimage import distance_transform_edt
    from scipy.spatial import cKDTree
    mask, k, cell, lo = _footprint_mask(P, spacing, cell)
    edt = distance_transform_edt(mask); c = np.unravel_index(int(np.argmax(edt)), edt.shape)
    edt_span = round(float(max(0.0, edt[c] - k) * 2 * cell), 1)
    centre = np.array([lo[0] + (c[0] + 0.5) * cell, lo[1] + (c[1] + 0.5) * cell])
    o = P[cKDTree(P[:, :2]).query(centre)[1]].copy(); o[2] -= 0.05
    reach = float(np.ptp(P[:, :2], axis=0).max()) + 1.0
    ends, chord = [0, 0], [0.0, 0.0]
    for a in (0, 1):
        for sgn in (1.0, -1.0):
            d = np.zeros(3); d[a] = sgn
            loc, ir, _ = m.ray.intersects_location(o[None], d[None], multiple_hits=False)
            if len(ir):
                dist = float(np.linalg.norm(loc[0] - o))
                if dist <= reach:
                    ends[a] += 1; chord[a] += dist
    two = [a for a in (0, 1) if ends[a] == 2]
    if len(two) == 2:
        span = round(min(edt_span, chord[0], chord[1]), 1)
    elif len(two) == 1:
        span = round(chord[two[0]], 1)
    else:
        span = edt_span
    return span, ends


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
                seg = np.linalg.norm(np.roll(R, -1, axis=0) - R, axis=1); cum = np.concatenate([[0.0], np.cumsum(seg)])   # arc length along the ring
                for a, b in cKDTree(R).query_pairs(neck_max, output_type="ndarray"):
                    if min((a - b) % n, (b - a) % n) <= 1 or N[a] @ N[b] >= 0:
                        continue
                    i0, i1 = sorted((a, b)); path = cum[i1] - cum[i0]; path = min(path, cum[-1] - path)   # the shorter way round the ring between the two points
                    if path < 10 * neck_max:
                        continue                                           # a two-vertex detour of the tessellation (a bottom edge crossed at a slant), not two surfaces: a neck has material on both sides of it
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
    """sample (x, y, z) inside any legend box (6-tuples, print frame)"""
    pts = np.asarray(pts, float).reshape(-1, 3)
    if not boxes or not len(pts):
        return np.zeros(len(pts), bool)
    B = np.array(boxes, float).reshape(-1, 6)
    return ((pts[:, None, :] >= B[None, :, :3]) & (pts[:, None, :] <= B[None, :, 3:])).all(2).any(1)


def _where(rs, k="vmin", n=5):
    return "; ".join(f"{r.get('cls', '')} {r['area']} mm2 x {r['extent']} mm" + (f" (span {r['span']})" if "span" in r else "") + (f" (angle {r['a_med']:.0f} deg, tip band {r['band']})" if "band" in r else "")
                     + f", min {r[k]} med {r['vmed']}, box {r['bbox']}" for r in rs[:n])


def analyse(path, process, n_s=None, seed=0, boxes=None, out_dir=None, piece=None, render=False, supports=None, bodies_expected=1, lands=None):
    """One body -> the record (dict; written to out_dir/<piece>.json [+ <piece>.boxes.json] and, with render, out_dir/<piece>_<view>.png).
    boxes: legend boxes (print frame, 6-tuples; `lands` = the legacy 4-tuple spelling); supports: none | interior | any overrides the process row
    (the body's own slicer setting); bodies_expected: the number of solids the file intentionally holds."""
    t0 = time.time()
    table, table_path = processes()
    if process not in table:
        print(f"print_dfm: process '{process}' is not a row of {table_path}; rows: {', '.join(table)}", file=sys.stderr); sys.exit(2)
    pr = table[process]
    if pr.get("wall_min") is None:
        print(f"print_dfm: row '{process}' has wall_min null (BLOCKED source) — fill the row before gating on it", file=sys.stderr); sys.exit(2)
    boxes = norm_boxes(boxes if boxes is not None else lands)
    m = trimesh.load(path, force="mesh")
    area = float(m.area); ext = (m.bounds[1] - m.bounds[0])
    n_s = n_s or int(min(300000, max(60000, area * 8)))
    wall_min, reco, fmin, dmin, vmin_, hmin, S, SLV = pr["wall_min"], pr["wall_reco"], pr["feature_min"], pr["detail_min"], pr.get("void_min"), pr["hole_min"], pr["slender"], pr.get("sliver_area", 5.0)
    layer = pr.get("layer"); skin_layers = pr.get("skin_min_layers", 3); skin_min = round(skin_layers * layer, 3) if layer else None     # layer processes judge horizontal skins by layers
    media = pr.get("media", "powder"); sup = supports or pr.get("supports")
    F = field(m, n_s, seed=seed, r0=max(1.0, reco / 2 + 0.4), r0_void=max(0.75, max(vmin_ or 0.0, hmin) / 2 + 0.3))
    pts, nrm, t, ang, g = F["pts"], F["nrm"], F["t"], F["ang"], F["g"]
    a_per = area / n_s; spacing = a_per ** 0.5; link = max(3.0 * spacing, 2.5)      # a 0.4 mm band holds ~3 samples / mm along its length: a density-scaled 1 mm link broke a long root band into pieces; 2.5 keeps it whole
    land = _in_boxes(pts, boxes) if (boxes and pr.get("legend_land_min") is not None) else np.zeros(n_s, bool)
    thr_w = np.where(land, pr.get("legend_land_min", wall_min), wall_min)
    thr_d = np.where(land, pr.get("legend_void_min", dmin), dmin)
    wall = ang < WALL_DEG
    def cls_of(s):
        wf = float(wall[s].mean()); nz = float(np.median(np.abs(nrm[s, 2])))
        cls = "wall" if wf >= 0.5 else "wedge"
        if cls == "wall" and layer and nz >= np.cos(np.radians(WALL_DEG)):
            cls = "skin"                                                       # normals along the print Z = a horizontal skin, judged by layers (rule Z)
        return dict(wall_frac=round(wf, 2), cls=cls, nz=round(nz, 2), red_frac=round(float((t[s] < fmin).mean()), 2), ray_med=round(float(np.median(F["t_ray"][s])), 2), in_land=round(float(land[s].mean()), 2))
    thin = regions(pts, t, t < thr_w, link, a_per, cls_of)                     # below the process minimum (inside legend boxes: the legend minimum)
    rows = []
    def row(rule, value, limit, verdict, where, why, fix=""):
        rows.append(dict(rule=rule, value=value, limit=limit, verdict=verdict, where=where, why=why, fix=fix))
    inland = lambda r: r.get("in_land", 0) >= 0.5
    sliver = lambda r: r["area"] < SLV and r["extent"] <= 2 * max(r["vmed"], 0.1)       # a patch no longer than twice its thickness; anything longer is a feature however small
    # --- M manifold / bodies, C closed cavity ---
    parts = m.split(only_watertight=False)
    cav = [p for p in parts if p.is_watertight and float(p.volume) < -1e-6]            # an inward-facing closed shell = a sealed void
    n_solid = len(parts) - len(cav)
    ue, cnt = np.unique(m.edges_sorted, axis=0, return_counts=True); bad_e = ue[cnt != 2]
    mid = m.vertices[bad_e].mean(1) if len(bad_e) else np.zeros((0, 3))
    e_out = mid[~_in_boxes(mid, boxes)] if len(mid) else mid
    mp = []
    if len(e_out):
        mp.append(f"{len(e_out)} non-manifold / open edge(s) outside legend boxes, e.g. at {np.round(e_out[:3], 2).tolist()}")
    if not m.is_winding_consistent:
        mp.append("inconsistent winding (flipped faces)")
    if n_solid != bodies_expected:
        mp.append(f"{n_solid} solid body/bodies, expected {bodies_expected}" + (f" (bboxes {[np.round(p.bounds, 1).tolist() for p in parts[:3]]})" if n_solid > 1 else ""))
    row("M manifold / bodies", f"{n_solid} solid(s), {len(cav)} sealed cavity/cavities, {len(bad_e)} edge(s) not shared by exactly two faces ({len(bad_e) - len(e_out)} inside legend boxes), winding consistent {bool(m.is_winding_consistent)}",
        f"{bodies_expected} solid, every edge on two faces outside legend boxes", "FLAG" if mp else "PASS", "; ".join(mp),
        "a slicer or vendor cannot tell inside from outside on an open mesh (every thickness below is unreliable); two solids that touch at a vertex / edge / face without a union, or a stray shell, print as pieces; legend arms that touch by design are listed (row L)",
        "union the solids and close the open edges in the CAD, re-export; pass --bodies N only when the file intentionally holds N parts")
    row("C closed cavity", f"{len(cav)} sealed internal void(s)" + (f": volumes {[round(-float(p.volume), 1) for p in cav[:4]]} mm3" if cav else ""),
        ("none on a powder / resin process (escape hole >= " + str(pr.get("published", {}).get("escape_hole", "the row's published escape_hole")) + ")") if media in ("powder", "resin") else "listed (FDM hollows it)",
        ("FLAG" if media in ("powder", "resin") else "INFO") if cav else "PASS", "; ".join(f"{-float(p.volume):.1f} mm3 at {np.round(p.bounds, 1).tolist()}" for p in cav[:4]),
        f"a sealed cavity traps un-fused {media} that cannot be removed (weight, leak, no clean-out)" if media != "none" else "a sealed cavity on FDM is printed hollow / with infill — no media to trap",
        "open an escape hole into the cavity, or fill it in the CAD")
    # --- W / R / Z / F ---
    walls = [r for r in thin if r["cls"] == "wall"]; skins = [r for r in thin if r["cls"] == "skin"]
    W = [r for r in walls if r["extent"] >= S * max(r["vmed"], 0.1) and not inland(r)]            # inside a legend box the coupon rule owns the land (row L) — like every other rule
    Rt = [r for r in W if r["ray_med"] >= wall_min]
    Zs = [r for r in skins if skin_min is not None and r["vmed"] < skin_min and not inland(r) and not sliver(r)]
    Fe = [r for r in walls if r not in W and r["vmed"] < fmin and not inland(r) and not sliver(r)]
    row("W wall", f"{len(W)} wall-class region(s) with median < {wall_min} and extent >= {S} x thickness", f"wall_min {wall_min} over >= {S} x t", "FLAG" if W else "PASS", _where(W),
        f"[K] slenderness heuristic: a strip thinner than the process minimum over >= {S} x its thickness bends / cracks under depowdering, cleaning and handling; shorter = a feature (rule F)",
        f"thicken the strip to >= {wall_min} (or shorten it below {S} x t) in the CAD / generator, re-export, rerun")
    row("R root under a rim / ledge", f"{len(Rt)} of them read >= {wall_min} along the normal", f"no W region with ray >= wall_min {wall_min} (= a root)", "FLAG" if Rt else "PASS", _where(Rt),
        "a rim set inboard of its wall over a step stands on a root the width of the overlap: the ball from the wall face is stopped by the rim's outer face while every ray reads the full rim — the construction behind a cracked long lip",
        f"widen the overlap to >= {wall_min} (move the rim over the wall), fill the undercut or chamfer the step")
    if layer:
        row("Z skin (layers)", f"{len(Zs)} horizontal skin(s) (normals within {WALL_DEG:g} deg of the print Z) thinner than {skin_min} = {skin_layers} x {layer}; {len(skins)} skin region(s) below wall_min listed, not walls",
            f"skin_min {skin_min} ({skin_layers} layers [K])", "FLAG" if Zs else "PASS", _where(Zs) or ("skins between skin_min and wall_min: " + _where([r for r in skins if r not in Zs], n=4)),
            "a horizontal skin is a LAYER count, not a perimeter count: a 0.6 sheet printed flat is three layers and prints; the same sheet stood up is a 0.6 wall (rule W). Fewer than skin_min_layers = pinholes / sag [K]",
            f"thicken the skin to >= {skin_min} ({skin_layers} layers) or re-orient the part so it prints as a wall")
    row("F feature", f"{len(Fe)} short wall-class region(s) below feature_min {fmin} that are not slivers (area >= {SLV} mm2 or extent > 2 x thickness)", f"feature_min {fmin}", "FLAG" if Fe else "PASS", _where(Fe),
        "below the smallest feature the process forms it does not print or breaks off in post-processing (a Ø0.4 x 3.5 pin); a sliver = a patch under sliver_area no longer than twice its thickness = a tangency / boolean remnant that fills or vanishes without loss (row L)",
        f"thicken the feature to >= {fmin} or remove it")
    # --- K knife edge (own field: any face that faces back) ---
    a_k = F["a_k"]
    def k_of(s):
        am = float(np.median(a_k[s])); return dict(cls="wedge", a_med=round(am, 0), band=round(fmin / (2 * np.tan(np.radians(max(am, 1.0)) / 2)), 2), red_frac=1.0, in_land=round(float(land[s].mean()), 2))
    kreg = regions(pts, F["t_k"], (F["t_k"] < fmin) & (a_k >= WALL_DEG), link, a_per, k_of)
    K = [r for r in kreg if r["band"] > KNIFE_BAND * fmin and r["extent"] >= S * fmin and not inland(r) and not sliver(r)]
    Ki = [r for r in kreg if r not in K and r["band"] > fmin / 2 + 1e-9]
    row("K knife edge", f"{len(K)} wedge region(s) whose sub-{fmin} tip band is longer than {KNIFE_BAND * fmin:g} (included angle < {np.degrees(2 * np.arctan(1 / (2 * KNIFE_BAND))):.0f} deg) over >= {S * fmin} mm; {len(kreg)} tapering region(s) read in all",
        f"tip band <= {KNIFE_BAND:g} x feature_min [K]", "FLAG" if K else "PASS", _where(K) or ("listed wedges (band <= feature_min or short): " + _where(Ki, n=4)),
        f"a ridge of included angle a reads 2 s tan(a/2) at distance s from its tip: the band below feature_min is {fmin} / (2 tan(a/2)) long and that is what the tip loses — 30 deg {fmin / (2 * np.tan(np.radians(15))):.2f} (frays: rail tips, cove lips), 50 deg {fmin / (2 * np.tan(np.radians(25))):.2f}, 60 deg {fmin / (2 * np.tan(np.radians(30))):.2f}, 90 deg {fmin / 2:.2f} (rounds); a chamfer whose thin end stays >= feature_min has no band",
        f"stop the taper with a flat >= {fmin} at its thin end, open the included angle to >= 53 deg, or cut it as a chamfer into a full wall")
    # --- P point contact ---
    allnecks = pinches(m, pr["neck_max"])
    if boxes and pr.get("legend_land_min") is not None:                        # a raised / debossed mark's arms may touch at points BY DESIGN inside legend boxes (the print fuses them over one line width) -> row L
        inl = _in_boxes(np.array([[r["x"], r["y"], r["z"]] for r in allnecks]).reshape(-1, 3), boxes) if allnecks else np.zeros(0, bool)
        necks = [r for r, q in zip(allnecks, inl) if not q]; land_necks = [r for r, q in zip(allnecks, inl) if q]
    else:
        necks, land_necks = allnecks, []
    row("P point contact", f"{len(necks)} contact line(s) / hairline(s) <= {pr['neck_max']} wide on 15 section planes" + (f" (+ {len(land_necks)} inside legend boxes, row L)" if land_necks else ""), f"no two surfaces within neck_max {pr['neck_max']}", "FLAG" if necks else "PASS",
        "; ".join(f"{r['kind']} {r['width']} at ({r['x']}, {r['y']}, {r['z']}) x{r['n']}" for r in necks[:8]), "two bodies touching along a line (or parted by a hairline) arrive as two parts or crack there — a vendor's ENGINEER flags this where its automatic check passes",
        f"bridge the contact with a web >= {wall_min} wide, or part the bodies by >= {vmin_ or dmin}")
    # --- V void / slot, H hole ---
    def roundness(s):                                                            # normals of a slit are +/-n (one principal direction); of a hole they cover a plane (two)
        e = np.sort(np.linalg.eigvalsh(np.cov(nrm[s].T)))[::-1]
        return round(float(e[1] / e[0]), 2) if e[0] > 1e-9 else 0.0
    vlim = max(dmin, vmin_) if vmin_ else dmin
    voids = regions(pts, g, g < np.where(land, thr_d, vlim), link, a_per, lambda s: dict(cls="void", red_frac=round(float((g[s] < dmin).mean()), 2), roundness=roundness(s), in_land=round(float(land[s].mean()), 2)))
    Vd = [r for r in voids if r["vmed"] < dmin and not inland(r) and not sliver(r)]
    Vs = [r for r in voids if vmin_ and r not in Vd and not inland(r) and r["extent"] >= S * vmin_]
    row("V void / slot", f"{len(voids)} void region(s) narrower than {vlim}: {len(Vd)} below detail_min {dmin}" + (f", {len(Vs)} long slots (>= {S * vmin_} mm)" if vmin_ else " (no long-slot rule: FDM has no media to clear)"),
        f"detail_min {dmin}" + (f"; void_min {vmin_} over any {S * vmin_} mm" if vmin_ else ""), "FLAG" if (Vd or Vs) else "PASS", _where(Vd + Vs),
        ("a void narrower than the smallest detail closes (the walls fuse); a long slot narrower than void_min does not clear its powder / resin" if vmin_ else
         "FDM: a void narrower than one line width (detail_min) is closed by the line's squish / the slicer's gap fill — it must be printed as a GAP between two extrusions, and a gap under one line is not; a slot wider than one line is two walls with air between, nothing to clear"),
        f"widen the stroke / slit to >= {dmin}" + (f" (a long slot to >= {vmin_})" if vmin_ else "") + " or drop it")
    H = [r for r in voids if r["roundness"] >= 0.5 and r["vmed"] < hmin and not inland(r) and r not in Vd and not sliver(r)]
    row("H hole", f"{len(H)} round void(s) (normals in two directions) narrower than hole_min {hmin}; voids wider than {max(vlim, hmin)} are not measured (they clear)", f"hole_min {hmin}", "FLAG" if H else "PASS", _where(H),
        "a hole below the process minimum closes or does not clear; debossed glyph counters inside legend boxes are legends, not holes (row L)", f"open the hole to >= {hmin} or drop it (drill after printing)")
    Lg = [r for r in thin + voids + kreg if inland(r)]; Sl = [r for r in thin + voids + kreg if not inland(r) and sliver(r) and r not in W]
    row("L legend boxes / slivers (INFO)", f"{len(Lg)} sub-minimum region(s), {len(land_necks)} point contact(s) and {len(bad_e) - len(e_out)} non-manifold edge(s) inside legend boxes; {len(Sl)} sliver(s) (< {SLV} mm2 and <= 2 x thickness) outside them",
        "listed — the coupon rule / census legend rows own the boxes; a sliver fills or vanishes without loss", "INFO",
        _where(Lg, n=6) + (" || contacts: " + "; ".join(f"{r['kind']} {r['width']} at ({r['x']}, {r['y']})" for r in land_necks[:4]) if land_necks else "") + (" || slivers: " + _where(Sl, n=6) if Sl else ""),
        "raised / debossed legend glyphs are wedges and sub-line gaps by construction (the coupon decides); a tangency or boolean remnant below the process' detail cell has nothing to lose")
    # --- O overhang / B bridge (layer processes) ---
    O = Os = C = B = Ct = []
    if pr.get("overhang_max_deg") is not None:
        zmin = m.bounds[0][2]; down = nrm[:, 2] < -np.sin(np.radians(pr["overhang_max_deg"] + OVERHANG_TOL)); ceiling = nrm[:, 2] < -0.985; bed = pts[:, 2] < zmin + 0.2
        Oall = regions(pts, -nrm[:, 2], down & ~ceiling & ~bed, link, a_per, lambda s: dict(cls="overhang", deg=round(float(np.degrees(np.arcsin(np.clip(-nrm[s, 2].mean(), -1, 1)))), 0), span=span_edt(pts[s], spacing)))
        O = [r for r in Oall if r["span"] > pr["bridge_max"]]; Os = [r for r in Oall if r not in O]
        C = regions(pts, pts[:, 2], ceiling & ~bed, link, a_per, lambda s: dict(cls="ceiling", z=round(float(np.median(pts[s, 2])), 2), _s=s))
        for r in C:                                                              # span + supported ends by rays from the inscribed-circle centre (span_rays); every ceiling is judged as a bridge, rule O owns overhangs
            P = pts[r.pop("_s")]; r["span"], r["supported_ends"] = span_rays(m, P, spacing); r["cls"] = "bridge"
        B = [r for r in C if r["cls"] == "bridge" and r["span"] > pr["bridge_max"]]
        hard = sup == "none"
        row("O overhang (layers)", f"{len(O)} down-facing region(s) steeper than {pr['overhang_max_deg']} deg from vertical (+{OVERHANG_TOL:g} deg tolerance; not the bed, not a ceiling) reaching further than bridge_max {pr['bridge_max']} across ({len(Os)} shorter one(s) listed: the slicer bridges them); supports = {sup}",
            "none when supports = none; listed otherwise", ("FLAG" if O else "PASS") if hard else "INFO", _where(O, k="deg") or ("short overhangs (reach <= bridge_max): " + _where(Os, k="deg", n=4)),
            "an FDM layer needs the layer below it: beyond ~45..60 deg from vertical it sags or needs support (Prusa: 45..60 deg); a steep region whose footprint spans less than bridge_max is bridged from its supported edges [K]; the body's own support setting decides whether the rest is a defect",
            "re-orient the part, add a 45 deg lead-in, or allow supports there")
        row("B bridge (layers)", f"{len(B)} horizontal ceiling(s) above the bed whose span (the shortest crossing between supported edges, by rays from the inscribed-circle centre) exceeds bridge_max {pr['bridge_max']}; {len(C)} ceiling(s) read; supports = {sup}", "none when supports = none; listed otherwise", ("FLAG" if B else "PASS") if hard else "INFO",
            _where(B, k="span") or ("ceilings (span / long side): " + "; ".join(f"{r['cls']} span {r['span']} x {r['extent']} mm, {r['area']} mm2 at Z {r['z']}" for r in C[:5])),
            "bridge lines run the SHORTEST way between two supported edges: the span is that crossing, not the long side (a 2 x 40 tunnel roof bridges 2 mm); longer than bridge_max it droops", f"split the span below {pr['bridge_max']} with a rib, or allow interior supports")
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
    fin = np.isfinite(t); finr = np.isfinite(F["t_ray"])
    flagged = [r["rule"] for r in rows if r["verdict"] == "FLAG"]
    rec = dict(tool="scripts/print_dfm.py (hw-from-spec, vendor-independent)", version=VERSION, stl=os.path.relpath(os.path.abspath(path), ROOT), stl_md5=md5(path), geom=geom_sig(m), process=process, piece=piece or os.path.splitext(os.path.basename(path))[0],
               faces=int(len(m.faces)), watertight=bool(m.is_watertight), bodies=int(n_solid), bodies_expected=bodies_expected, cavities=len(cav), supports=sup, area_mm2=round(area, 1), bbox=np.round(ext, 2).tolist(), samples=int(n_s), spacing=round(spacing, 3), link=round(link, 3),
               thresholds={k: pr.get(k) for k in THRESHOLD_KEYS},
               frac_below={str(b): round(float((t < b).mean()), 5) for b in (fmin, wall_min, reco)}, area_below={str(b): round(float((t < b).sum() * a_per), 1) for b in (fmin, wall_min, reco)},
               t_min=round(float(t[fin].min()), 3) if fin.any() else None, ray_finite_frac=round(float(finr.mean()), 3), ray_med=round(float(np.median(F["t_ray"][finr])), 3) if finr.any() else None,
               thin=thin[:40], knife=kreg[:20], voids=voids[:40], necks=necks[:40], overhangs=O[:20], short_overhangs=Os[:10], ceilings=C[:20],
               verdict="FLAG" if flagged else "PASS", flagged=flagged, rows=rows, boxes=[list(b) for b in boxes])
    rec["sig"] = record_sig(rec, VERSION)                                         # the gate refuses a record whose body changed after it was written; no run time inside: a rerun reproduces the record byte for byte
    rec["_seconds"] = round(time.time() - t0, 1)                                  # not written, not signed
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
        json.dump({k: v for k, v in rec.items() if not k.startswith("_")}, open(os.path.join(out_dir, rec["piece"] + ".json"), "w"), indent=1)
        bp = os.path.join(out_dir, rec["piece"] + ".boxes.json")
        if boxes:
            json.dump([list(b) for b in boxes], open(bp, "w"))
        elif os.path.exists(bp):
            os.remove(bp)
        if render:
            heatmap(m, F, pr, os.path.join(out_dir, rec["piece"]))
    return rec


def heatmap(m, F, pr, prefix, views=None, size=1600):
    """Map renders: every face takes the MIN thickness of its samples (a face without a sample inherits the nearest sample), banded grey >= wall_reco,
    yellow [feature_min, wall_reco), red < feature_min; faces of a void narrower than void_min (detail_min on FDM) dark red. Six orthographic faces + two isos."""
    try:
        import matplotlib
    except ImportError:
        print("print_dfm: --render needs matplotlib (pip install matplotlib); records written, no PNGs", file=sys.stderr); return {}
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.collections import PolyCollection
    vband = pr.get("void_min") or pr["detail_min"]
    nf = len(m.faces); ft = np.full(nf, np.inf); fg = np.full(nf, np.inf)
    np.minimum.at(ft, F["fid"], F["t"]); np.minimum.at(fg, F["fid"], F["g"])
    miss = np.bincount(F["fid"], minlength=nf) == 0
    if miss.any():
        _, j = cKDTree(F["pts"]).query(m.triangles_center[miss]); ft[miss] = F["t"][j]; fg[miss] = F["g"][j]
    col = np.tile([0.62, 0.62, 0.62], (nf, 1))
    col[ft < pr["wall_reco"]] = [1.0, 0.88, 0.0]; col[ft < pr["feature_min"]] = [1.0, 0.16, 0.0]; col[(fg < vband) & (ft >= pr["wall_reco"])] = [0.75, 0.25, 0.25]
    out = {}
    for name, (view, right) in (views or VIEWS).items():
        v = np.array(view, float); v /= np.linalg.norm(v); r = np.array(right, float); r -= r @ v * v; r /= np.linalg.norm(r); u = np.cross(r, v)
        shade = 0.75 + 0.25 * np.abs(m.face_normals @ v)
        tri = m.triangles; x = tri @ r; y = tri @ u; order = np.argsort(-(tri.mean(1) @ v))       # far first (painter)
        fig = plt.figure(figsize=(size / 200, size / 200 * 0.75), dpi=200); ax = fig.add_axes([0, 0, 1, 1]); ax.set_aspect("equal"); ax.axis("off")
        ax.add_collection(PolyCollection(np.stack([x, y], -1)[order], facecolors=np.clip((col * shade[:, None])[order], 0, 1), edgecolors="none", antialiased=False))
        ax.set_xlim(x.min() - 2, x.max() + 2); ax.set_ylim(y.min() - 2, y.max() + 2)
        ax.text(0.01, 0.99, f"{os.path.basename(prefix)} {name}  grey >= {pr['wall_reco']}  yellow {pr['feature_min']}..{pr['wall_reco']}  red < {pr['feature_min']}  (void < {vband} dark red)  min {np.nanmin(ft[np.isfinite(ft)]):.2f}",
                transform=ax.transAxes, va="top", fontsize=6, family="monospace")
        p = f"{prefix}_{name}.png"; fig.savefig(p, facecolor="white"); plt.close(fig); out[name] = p
    return out


def _project():
    """The project (None outside one): print_targets, paths.decisions, paths.mech_record."""
    if not os.path.exists(os.path.join(ROOT, "project.yaml")):
        return None
    from project import Project
    return Project(os.path.join(ROOT, "project.yaml"))



def parts_dir(records_dir):
    """The STL set a records dir belongs to: `<set>/parts/` when the records sit in `<set>/checks/<kind>/` (the layout of record), else the
    sibling `stl/` of the records dir's parent (an older project shape). One rule for every pure gate."""
    parent = os.path.dirname(os.path.abspath(records_dir.rstrip("/")))
    if os.path.basename(parent) == "checks":
        return os.path.join(os.path.dirname(parent), "parts")
    return os.path.join(parent, "stl")


def gate(dfm_dirs, open_findings=(), target=None, expected=()):
    """PURE adopt gate (recomputes nothing) — see the docstring's --gate entry. Returns 1 on any problem."""
    bad = []; n = 0; P = _project(); table, _ = processes()
    opn = {}
    if open_findings:
        dec = P.path("decisions") if P else None; rows = open_decisions(dec) if dec else {}
        for e in open_findings:
            k, _, did = e.partition("=")
            piece = k.rsplit("/", 1)[-1]
            if did not in rows:
                bad.append(f"--open {e}: {did!r} is not an OPEN row of {P.get('paths.decisions') if P else 'the decision log (no project.yaml found)'} — a finding stays open only under an OPEN decision")
            elif piece.lower() not in rows[did].lower():
                bad.append(f"--open {e}: OPEN row {did} does not name the piece '{piece}' in its topic / proposal — one row per body, not a blanket")
            else:
                opn[k] = f"{did} ({rows[did][:60]})"
    exp = {}
    for e in expected:
        k, _, why = e.partition("=")
        if not why.strip():
            bad.append(f"--expect {e}: a body that FLAGs by design needs its reason after '=' (what the coupon tests)")
        else:
            exp[k] = why.strip()
    used = set()
    targets = (P.cfg.get("print_targets") or {}) if P else {}
    for d in dfm_dirs:
        d = d.rstrip("/"); parent = os.path.dirname(os.path.abspath(d)); tag = target or os.path.basename(os.path.dirname(parts_dir(d))); census = os.path.join(parent, "census")
        want = None
        if targets:
            if tag not in targets:
                bad.append(f"{d}: '{tag}' is not a print target (print_targets: {', '.join(targets)}) — lay the records out under <target>/dfm or pass --target"); continue
            want = targets[tag].get("dfm_process")
            if not want:
                bad.append(f"{d}: print_targets.{tag}.dfm_process is not set (kickoff C8a) — the gate cannot tell which process row the bodies must pass")
        recs = {}
        for ej in sorted(glob.glob(os.path.join(d, "*.json"))):
            if ej.endswith(".boxes.json"):                                        # the legend-box sidecar, not a record
                continue
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
                key = f"{tag}/{piece}"
                if key in opn:
                    used.add(key); print(f"PRINT-DFM GATE: OPEN {opn[key]} - {msg}")
                elif key in exp:
                    used.add(key); print(f"PRINT-DFM GATE: EXPECTED FLAG ({exp[key]}) - {msg}")
                else:
                    bad.append(msg)
        for cj in glob.glob(os.path.join(census, "*.json")):
            if os.path.basename(cj)[:-5] not in recs:
                bad.append(f"{d}/{os.path.basename(cj)}: census record without a print_dfm record (run scripts/print_dfm.py on the body)")
        # the STL set of record: every body under this tag (sibling stl/ + the paths.mech_record glob under the parent) needs a same-md5 record
        have = {e.get("stl_md5") for e in recs.values()}
        set_root = os.path.dirname(parts_dir(d))
        stls = set(glob.glob(os.path.join(parts_dir(d), "*.stl")))
        if P and P.get("paths.mech_record"):
            stls |= {f for f in glob.glob(os.path.join(ROOT, P.get("paths.mech_record"))) if os.path.abspath(f).startswith(set_root + os.sep)}
        for f in sorted(stls):
            if md5(f) not in have:
                bad.append(f"{os.path.relpath(f, ROOT)}: body of the record set without a print_dfm record of its md5 (run scripts/print_dfm.py --process {want or '<row>'} --out {d} on it)")
    for k in sorted(set(opn) | set(exp)):
        if k not in used:
            print(f"PRINT-DFM GATE: note: --open / --expect {k} unused (the body passes or has no record here) — drop the stale entry")
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


def threshold_table(table_path, keys):
    """process-table rows -> [(process, key, value, tag, comment)] from the line comments: every threshold shows its [V] / [K] tag (or 'untagged')."""
    out = []; proc = None
    for line in open(table_path):
        if re.match(r"^  (\w+):\s*$", line):
            proc = line.strip()[:-1]; continue
        mt = re.match(r"^    (\w+):\s*([^#]*?)\s*(?:#\s*(.*))?$", line.rstrip("\n"))
        if proc in keys and mt and mt.group(1) in THRESHOLD_KEYS + ("part_min", "build_max"):
            c = mt.group(3) or ""; tag = "[V]" if c.startswith("[V]") else ("[K]" if "[K" in c[:40] or c.startswith("BLOCKED") else "untagged")
            out.append((proc, mt.group(1), mt.group(2), tag, c[:110].replace("|", "/")))
    return out


def validate(write_doc=True, renders=()):
    """Run every labelled STL (cached by md5 + VERSION in val_dir), group the files by GEOMETRY (tolerances: equal faces, |dV| < 0.05 mm3, |dA| < 0.5 mm2,
    bbox within 0.01 — a hash splits twins at a rounding boundary), write the validation doc: vendor verdict vs ours per geometry, confusion matrix,
    rules fired, coverage per mechanism, thresholds with their tags. Returns the summary; `looser` lists the RULE DEFECTS (vendor FLAG, ours PASS)."""
    if not os.path.exists(PATHS["verdicts"]):
        print(f"print_dfm: no verdict record at {PATHS['verdicts']} (copy templates/60-orders/quotes/dfm_verdicts.yaml, append every vendor verdict)", file=sys.stderr); sys.exit(2)
    labels = yaml.safe_load(open(PATHS["verdicts"]))["verdicts"] or []
    table, table_path = processes(); VAL_DIR = PATHS["val_dir"]
    os.makedirs(VAL_DIR, exist_ok=True); recs = []; sig = []
    for lb in labels:
        path = lb["stl"] if os.path.isabs(lb["stl"]) else os.path.join(ROOT, lb["stl"])
        if not os.path.exists(path):
            print(f"print_dfm: labelled STL missing: {lb['stl']} (every verdict row needs its STL in the tree)", file=sys.stderr); sys.exit(2)
        h = md5(path)
        assert h.startswith(str(lb["md5"])), f"{lb['stl']}: md5 {h[:8]} != label {lb['md5']} — the file changed after the verdict; relabel"
        cj = os.path.join(VAL_DIR, f"{h[:8]}.json"); rec = json.load(open(cj)) if os.path.exists(cj) else None
        thr = {k: table[lb["process"]].get(k) for k in (rec or {}).get("thresholds", {})}
        if not rec or rec.get("version") != VERSION or rec.get("stl_md5") != h or rec.get("process") != lb["process"] or rec.get("thresholds") != thr:
            rec = analyse(path, lb["process"], out_dir=VAL_DIR, piece=h[:8], render=any(k in lb["stl"] for k in renders)); print(f"[val] {os.path.basename(lb['stl'])} {rec['verdict']} {rec['_seconds']} s", flush=True)
        recs.append((lb, rec))
        m_ = trimesh.load(path, force="mesh"); sig.append((len(m_.faces), float(m_.volume), float(m_.area), m_.bounds.ravel()))
    parent = list(range(len(recs)))                                               # union-find on the geometry tolerance
    def root(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]; i = parent[i]
        return i
    for i in range(len(recs)):
        for j in range(i):
            a, b = sig[i], sig[j]
            if a[0] == b[0] and abs(a[1] - b[1]) < 0.05 and abs(a[2] - b[2]) < 0.5 and np.abs(a[3] - b[3]).max() < 0.01:
                parent[root(i)] = root(j)
    groups = {}                                                                   # group key = the first member's geometry signature -> the labels of that geometry
    for i, (lb, rec) in enumerate(recs):
        groups.setdefault(recs[root(i)][1]["geom"], []).append((lb, rec))
    cm = defaultdict(int); per_rule = defaultdict(lambda: defaultdict(int)); looser = []; stricter = []; fam = defaultdict(list); uniq_rows = []
    rel = lambda p: os.path.relpath(p, ROOT)
    for gkey, items in groups.items():
        vs_ = {_label_verdict(lb) for lb, _ in items} - {None}
        vs = None if not vs_ else (vs_.pop() if len(vs_) == 1 else "CONFLICT")
        rec = items[0][1]; ours = rec["verdict"]; fired = sorted({x.split()[0] for _, r in items for x in r["flagged"]})
        ag = "unlabelled" if vs is None else ("conflicting labels" if vs == "CONFLICT" else ("agree" if ours == vs else ("STRICTER (ours flags)" if ours == "FLAG" else "**LOOSER — RULE DEFECT**")))
        if vs in ("FLAG", "PASS"):
            cm[(vs, ours)] += 1
            (looser if (vs == "FLAG" and ours == "PASS") else stricter if (vs == "PASS" and ours == "FLAG") else []).append(items[0][0]["stl"])
            for ru in fired:
                per_rule[ru]["vendor FLAG" if vs == "FLAG" else "vendor PASS"] += 1
            if vs == "FLAG":
                fam["W/R rim-on-root / thin wall" if set(fired) <= {"W", "R"} else ("K knife edge" if set(fired) <= {"K", "V", "W", "R"} and "K" in fired else "+".join(fired) or "none")].append(str(items[0][0]["md5"]))
        big = rec["thin"][0] if rec["thin"] else None
        bigs = f"{big['area']} x {big['extent']}, {big['vmin']} ({big['cls']})" if big else "none"
        names = "<br>".join(f"`{os.path.basename(lb['stl'])}` {lb['md5']} ({str(lb.get('evidence', lb.get('source', '')))[:60]})" for lb, _ in items)
        uniq_rows.append(f"| {gkey} | {names} | {items[0][0]['process']} | {vs or 'n/a'} | {ours} ({', '.join(fired) or '-'}) | {bigs} | {ag} | {items[0][0].get('note', '')} |")
    n_lab = sum(1 for lb, _ in recs if _label_verdict(lb) is not None); n_uni = sum(cm.values())
    lines = ["# PRINT_DFM_VALIDATION.md — scripts/print_dfm.py against every vendor verdict on record", "",
             f"Generated by `scripts/print_dfm.py --validate` on {time.strftime('%Y-%m-%d')} (rule set {VERSION}); labels `{rel(PATHS['verdicts'])}`; process table `{rel(table_path)}`; per-body records and heat maps `{rel(VAL_DIR)}/<md5-8>*`.",
             "The rules are physics + published process minimums (every number cited in the table); nothing is fitted to a vendor. Where the vendor is LOOSER than the rule the rule stands (listed with its reason); a LOOSER verdict of OURS is a RULE DEFECT — fix the rule (physics, not a vendor fudge), re-validate.",
             f"**Unique geometries:** {len(groups)} from {len(recs)} labelled files ({n_lab} with a vendor verdict -> {n_uni} unique labelled geometries); files of one geometry (triangle order / ASCII twins) share a row: grouped by tolerance (equal face count, volume within 0.05 mm3, area within 0.5 mm2, bbox within 0.01 mm); the key shown is the first member's `geom` signature.", "",
             "## 1. Body table (one row per geometry)", "", "| geometry | files (md5, evidence) | process | vendor verdict | our verdict (rules fired) | largest sub-minimum region: area mm2 x extent, min (class) | agreement | note |", "|---|---|---|---|---|---|---|---|"] + uniq_rows
    lines += ["", "## 2. Confusion matrix (unique labelled geometries)", "", "| | ours PASS | ours FLAG |", "|---|---|---|",
              f"| vendor PASS | {cm[('PASS', 'PASS')]} | {cm[('PASS', 'FLAG')]} (stricter — list each with its reason below the marker) |", f"| vendor FLAG | {cm[('FLAG', 'PASS')]} (**looser = rule defect**) | {cm[('FLAG', 'FLAG')]} |", "",
              "## 3. Rules fired, by vendor verdict (unique geometries)", "", "| rule | fired on vendor-FLAG geometries | fired on vendor-PASS geometries (stricter) |", "|---|---|---|"]
    for ru in sorted(per_rule):
        lines.append(f"| {ru} | {per_rule[ru]['vendor FLAG']} | {per_rule[ru]['vendor PASS']} |")
    lines += ["", "## 3a. Coverage of the vendor-FLAG geometries by mechanism (the agreement is only as broad as this table)", "", "| mechanism (rules we fire) | vendor-FLAG geometries |", "|---|---|"]
    for k, v in sorted(fam.items(), key=lambda kv: -len(kv[1])):
        lines.append(f"| {k} | {len(v)}: {', '.join(v)} |")
    exercised = set(per_rule); allrules = ["M", "C", "W", "R", "Z", "F", "K", "P", "V", "H", "O", "B", "S"]
    lines += ["", f"Rules exercised by a vendor verdict: {', '.join(sorted(exercised)) or 'none'}. Not exercised by any labelled geometry: {', '.join(r for r in allrules if r not in exercised)} — their positive / negative constructs live in `--selftest` only; a process row with `validated_on: []` has no verdict at all.", "",
              "## 3b. Thresholds and their source tags", "", "| process | key | value | tag | source (yaml comment) |", "|---|---|---|---|---|"]
    for p_, k_, v_, tg, c_ in threshold_table(table_path, {lb["process"] for lb, _ in recs}):
        lines.append(f"| {p_} | {k_} | {v_} | {tg} | {c_} |")
    lines += ["", f"Judgment constants in the tool itself [K]: `WALL_DEG` {WALL_DEG:g} (wall / wedge class), `COS_OPP` {COS_OPP} (~45 deg opposing cone of the thickness ball), `COS_K` {COS_K} (the knife field reads any face that faces back), `KNIFE_BAND` {KNIFE_BAND:g} (a tip may lose one feature cell), `NOISE_N` {NOISE_N} samples, `RAY_SKIP` {RAY_SKIP}, `OVERHANG_TOL` {OVERHANG_TOL:g} deg, link radius max(3 spacings, 2.5 mm), legend-box membership >= 50 % of a region's samples, `sliver_area` with the 2 x thickness aspect test."]
    if looser:
        lines += ["", f"**LOOSER than the vendor on {len(looser)} geometry/geometries — RULE DEFECT:** " + ", ".join(looser)]
    if write_doc:                                                                 # the generated sections are rewritten; the hand-written reading after the marker is kept
        VAL_DOC = PATHS["val_doc"]; old = open(VAL_DOC).read() if os.path.exists(VAL_DOC) else ""
        hand = old[old.index("<!-- hand: begin -->"):] if "<!-- hand: begin -->" in old else "<!-- hand: begin -->\n## 4. Reading (hand-written, kept across regenerations)\n\nFor every STRICTER row: the physical reason the rule stands. For every rule: which labelled geometries validate it, which it cannot be decided from.\n"
        os.makedirs(os.path.dirname(VAL_DOC), exist_ok=True); open(VAL_DOC, "w").write("\n".join(lines) + "\n\n" + hand)
    return dict(cm=dict((f"{k[0]}->{k[1]}", v) for k, v in cm.items() if v), per_rule={k: dict(v) for k, v in per_rule.items()}, looser=looser, stricter=stricter, recs=recs, lines=lines, groups=len(groups))


def rim_profile(root, rim=2.0, wall=2.0, lap_h=4.6, top=7.1):
    """Half profile of a wall of `wall` with a rim ring `rim` wide standing `root` mm on top of it over a lap step (the ring-root construction):
    wall x in [-wall-0.5, -0.5], rim x in [-0.5-root, -0.5-root+rim]."""
    from shapely.geometry import Polygon
    r0 = -0.5 - root; r1 = r0 + rim
    return Polygon([(-wall - 0.5, 0), (12, 0), (12, 2), (-0.5, 2), (-0.5, lap_h), (r1, lap_h), (r1, top), (r0, top), (r0, lap_h), (-wall - 0.5, lap_h)])


def _extrude(poly, h, path, up=False):
    """extrude the (x, y) profile by h along Z; up=True rotates so the profile's y becomes the print Z (a tunnel's roof faces down)"""
    m = trimesh.creation.extrude_polygon(poly, h)
    if up:
        m.apply_transform(trimesh.transformations.rotation_matrix(np.pi / 2, [1, 0, 0]))
    m.export(path); return path


def selftest():
    """One positive AND one negative construct per rule: a verdict-only selftest passes with a dead measure (the ray read inf on every sample for a
    day while the ball covered every wall; R fired on every W region and nothing noticed)."""
    import tempfile, contextlib, io, shutil
    from shapely.geometry import Polygon
    global PATHS, ROOT
    PATHS = dict(PATHS, processes=TEMPLATE_TABLE if os.path.exists(TEMPLATE_TABLE) else PATHS["processes"])
    ROOT0 = ROOT; MJF, FDM = "jlc_mjf_pa12", "home_fdm_04"
    fired = lambda r: {x.split()[0] for x in r["flagged"]}
    # P must not read a tessellation detour as a neck: a slab turned 7 deg has section rings whose bottom-edge crossing leaves two vertices
    # 0.02 mm apart two steps along the ring (facing away from each other); the arc-length test keeps them out
    slab = trimesh.creation.box((40.0, 12.0, 3.5)); slab.apply_translation((0.0, 0.0, 1.75))
    slab.apply_transform(trimesh.transformations.rotation_matrix(np.radians(7.0), (0, 0, 1))); slab = slab.subdivide().subdivide()
    assert not pinches(slab, 0.05), "a slanted plate edge is not a point contact"
    with tempfile.TemporaryDirectory() as d:
        ROOT = d                                                                      # records store the STL path relative to the project root
        # the ray reads the plate; W on a 0.8 plate, R SILENT (a free plate is not a root); every FLAG row carries a fix
        p1 = os.path.join(d, "plate08.stl"); trimesh.creation.box((30.0, 30.0, 0.8)).export(p1)
        r = analyse(p1, MJF, n_s=20000)
        assert r["ray_finite_frac"] > 0.9 and abs(r["ray_med"] - 0.8) < 0.02, (r["ray_finite_frac"], r["ray_med"])
        assert fired(r) == {"W"} and abs(r["thin"][0]["vmed"] - 0.8) < 0.05 and r["thin"][0]["cls"] == "wall" and abs(r["thin"][0]["ray_med"] - 0.8) < 0.05, (fired(r), r["thin"][:1])
        assert all(x["verdict"] != "FLAG" or x["fix"] for x in r["rows"])
        p2 = os.path.join(d, "plate20.stl"); trimesh.creation.box((30.0, 30.0, 2.0)).export(p2)
        r = analyse(p2, MJF, n_s=20000)
        assert r["verdict"] == "PASS" and not r["thin"] and not r["knife"], (r["flagged"], r["thin"][:2], r["knife"][:2])     # convex 90 deg edges everywhere: none may read thin, no knife band
        # free rib 0.6 x 15 x 8 on a 20 x 3 base (inverted T): W (0.6 < 1.0 over 15), R silent (the ray reads 0.6, not a rim); a free 0.6 x 60 rib likewise
        rib = Polygon([(-10, 0), (10, 0), (10, 3), (0.3, 3), (0.3, 11), (-0.3, 11), (-0.3, 3), (-10, 3)]); p3 = _extrude(rib, 15.0, os.path.join(d, "rib.stl"))
        r = analyse(p3, MJF, n_s=30000); assert fired(r) == {"W"}, r["flagged"]
        p0 = os.path.join(d, "rib06.stl"); trimesh.creation.box((60.0, 6.0, 0.6)).export(p0)
        assert fired(analyse(p0, "xometry_mjf_pa12", n_s=20000)) == {"W"}
        # eval 14: a 0.5 root under a 2.0 rim over 90 mm — rays read >= 2.0 everywhere, the root reads 0.5 on the inner face -> W + R FLAG; root 1.3 -> PASS
        p4 = os.path.join(d, "root05.stl"); trimesh.creation.extrude_polygon(rim_profile(0.5), 90.0).export(p4)
        r = analyse(p4, MJF, n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root05"); big = r["thin"][0]
        assert fired(r) == {"W", "R"} and 0.45 <= big["vmin"] <= 0.6 and big["extent"] >= 89 and big["cls"] == "wall", (big, r["flagged"])
        p5 = os.path.join(d, "root13.stl"); trimesh.creation.extrude_polygon(rim_profile(1.3), 90.0).export(p5)
        r = analyse(p5, MJF, n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root13"); assert r["verdict"] == "PASS", r["flagged"]
        assert "S size" not in analyse(p4, "jlc_sla_9600", n_s=20000)["flagged"]
        p6 = os.path.join(d, "tiny.stl"); trimesh.creation.box((1.0, 5.0, 12.0)).export(p6)
        assert "S size" in analyse(p6, "jlc_sla_9600", n_s=5000)["flagged"]
        # 3-D legend boxes: a box limited to the rib's foot band does not exempt the rib; a full-height box does (the generator must not draw one); records reproduce byte for byte, the sidecar is written and removed
        r = analyse(p3, FDM, n_s=30000, boxes=[(-0.9, 2.4, -0.6, 0.9, 3.6, 15.6)]); assert "W wall" in r["flagged"], r["flagged"]
        r2 = analyse(p3, FDM, n_s=30000, boxes=[(-0.9, 2.4, -0.6, 0.9, 11.6, 15.6)]); assert "W wall" not in r2["flagged"], r2["flagged"]
        bx = os.path.join(d, "b.json"); json.dump([[-0.9, 2.4, -0.6, 0.9, 3.6, 15.6]], open(bx, "w"))
        ra = analyse(p3, FDM, n_s=30000, boxes=load_boxes(bx), out_dir=os.path.join(d, "bx"), piece="rib"); rb = analyse(p3, FDM, n_s=30000, boxes=[(-0.9, 2.4, -0.6, 0.9, 3.6, 15.6)])
        assert json.dumps({k: v for k, v in ra.items() if not k.startswith("_")}) == json.dumps({k: v for k, v in rb.items() if not k.startswith("_")}), "record not reproducible"
        assert json.load(open(os.path.join(d, "bx", "rib.boxes.json"))) == [[-0.9, 2.4, -0.6, 0.9, 3.6, 15.6]] and "_seconds" not in json.load(open(os.path.join(d, "bx", "rib.json")))
        analyse(p3, FDM, n_s=30000, out_dir=os.path.join(d, "bx"), piece="rib"); assert not os.path.exists(os.path.join(d, "bx", "rib.boxes.json")), "a rerun without boxes removes the stale sidecar"
        assert norm_boxes([(0, 0, 1, 1)])[0][2] < -1e8, "a 4-tuple --land box spans every Z"
        # legend boxes own their lands: a 0.3 rib fully inside a box is listed (row L), not W; outside it is W
        rib3 = Polygon([(-10, 0), (10, 0), (10, 3), (0.15, 3), (0.15, 11), (-0.15, 11), (-0.15, 3), (-10, 3)]); p3b = _extrude(rib3, 15.0, os.path.join(d, "rib03.stl"))
        assert "W wall" in analyse(p3b, FDM, n_s=30000)["flagged"]
        r = analyse(p3b, FDM, n_s=30000, boxes=[(-0.9, 2.4, -0.6, 0.9, 11.6, 15.6)]); assert "W wall" not in r["flagged"] and r["thin"] and r["thin"][0]["in_land"] >= 0.5, (r["flagged"], r["thin"][:1])
        # sliver aspect test: pins are features, not slivers (Ø0.4 x 3.5 and Ø0.3 x 2.9 on a Ø20 x 3 base -> F on MJF); a Ø1.2 pin passes
        for dia, h, want in ((0.4, 3.5, True), (0.3, 2.9, True), (1.2, 3.5, False)):
            pp = os.path.join(d, f"pin{dia}.stl"); trimesh.creation.revolve(np.array([(0, 0), (10, 0), (10, 3), (dia / 2, 3), (dia / 2, 3 + h), (0, 3 + h)]), sections=48).export(pp)
            r = analyse(pp, MJF, n_s=40000); assert ("F feature" in r["flagged"]) == want and "W wall" not in r["flagged"], (dia, r["flagged"], [x for x in r["thin"] if x["cls"] == "wall"][:2])
        # knife edge by tip band: ridges 30 / 40 / 50 / 60 / 90 deg on a 3 mm base, 30 mm long — every one READ (finite), K: 30 / 40 / 50 FLAG, 60 / 90 pass
        for deg, want in ((30, True), (40, True), (50, True), (60, False), (90, False)):
            w = 4.0 * np.tan(np.radians(deg / 2)); rp = _extrude(Polygon([(-6, 0), (6, 0), (6, 3), (w, 3), (0, 7), (-w, 3), (-6, 3)]), 30.0, os.path.join(d, f"ridge{deg}.stl"))
            r = analyse(rp, MJF, n_s=40000); kr = [k for k in r["knife"] if k["extent"] >= 25]
            band = 0.5 / (2 * np.tan(np.radians(deg / 2)))
            if deg < 87:                                                                                     # the knife field reads any ridge sharper than a square edge
                assert kr and abs(kr[0]["band"] - band) < 0.08 and abs(kr[0]["a_med"] - deg) <= 6, (deg, kr[:1], band)
            else:
                assert not kr and not r["thin"], (deg, kr[:1], r["thin"][:1])                                # a 90 deg ridge IS a plain convex edge (band feature_min / 2): nothing to read
            assert ("K knife edge" in r["flagged"]) == want, (deg, r["flagged"])
            assert deg == 30 or "W wall" not in r["flagged"], (deg, r["flagged"])                            # a 30 deg ridge sits on the wall / wedge class boundary (WALL_DEG) and may read as a thin wall too
            assert ("K knife edge" in analyse(rp, FDM, n_s=40000)["flagged"]) == (band > 0.45), deg
        # layer process: a 0.6 sheet flat on the bed = 3 layers (Z skin, PASS); 0.4 = 2 layers (Z FLAG); the same 0.6 sheet stood up = W; a 0.6 slot is V on MJF (0.8 detail), not on FDM
        trimesh.creation.box((30.0, 30.0, 0.6)).export(os.path.join(d, "sheet06.stl")); r = analyse(os.path.join(d, "sheet06.stl"), FDM, n_s=20000)
        assert r["verdict"] == "PASS" and r["thin"] and r["thin"][0]["cls"] == "skin", (r["flagged"], r["thin"][:1])
        trimesh.creation.box((30.0, 30.0, 0.4)).export(os.path.join(d, "sheet04.stl")); r = analyse(os.path.join(d, "sheet04.stl"), FDM, n_s=20000); assert fired(r) == {"Z"}, r["flagged"]
        trimesh.creation.box((0.6, 30.0, 30.0)).export(os.path.join(d, "wall06.stl")); r = analyse(os.path.join(d, "wall06.stl"), FDM, n_s=20000); assert fired(r) == {"W"}, r["flagged"]
        slot = _extrude(Polygon([(-2.3, 0), (2.3, 0), (2.3, 10), (0.3, 10), (0.3, 2), (-0.3, 2), (-0.3, 10), (-2.3, 10)]), 20.0, os.path.join(d, "slot.stl"))
        assert "V void / slot" in analyse(slot, MJF, n_s=30000)["flagged"] and "V void / slot" not in analyse(slot, FDM, n_s=30000)["flagged"]
        # bridge span: a 2 x 40 tunnel roof bridges 2 (not 40): B silent even with supports none; a 15 mm tunnel -> B FLAG with supports none, INFO with interior
        for wid, want in ((2.0, False), (15.0, True)):
            tp = _extrude(Polygon([(-12, 0), (12, 0), (12, 8), (-12, 8)], holes=[[(-wid / 2, 2), (wid / 2, 2), (wid / 2, 4), (-wid / 2, 4)]]), 40.0, os.path.join(d, f"tunnel{wid}.stl"), up=True)
            r = analyse(tp, FDM, n_s=40000, supports="none"); c = [x for x in r["ceilings"] if x["extent"] > 30]
            assert c and c[0]["cls"] == "bridge" and abs(c[0]["span"] - wid) <= 0.6, (wid, c[:1])
            assert ("B bridge (layers)" in r["flagged"]) == want and "B bridge (layers)" not in analyse(tp, FDM, n_s=40000, supports="interior")["flagged"], (wid, r["flagged"])
        # a T-section's 18 mm free arms have no axis with both ends on material: their span is the inscribed circle of the arm (10) -> silent; an upside-down U's
        # 32 mm roof open at the ends has one supported axis -> a 32 mm bridge (B), not the 10 mm inscribed circle
        tee = _extrude(Polygon([(-2, 0), (2, 0), (2, 15), (20, 15), (20, 18), (-20, 18), (-20, 15), (-2, 15)]), 10.0, os.path.join(d, "tee.stl"), up=True)
        r = analyse(tee, FDM, n_s=20000, supports="none"); c = [x for x in r["ceilings"] if x["extent"] > 15]
        assert c and all(max(x["supported_ends"]) < 2 and x["span"] <= 10.5 for x in c) and not ({"B", "O"} & fired(r)), ("tee arms: no supported axis, inscribed circle, silent", c[:2], r["flagged"])
        pi_ = _extrude(Polygon([(-20, 0), (-16, 0), (-16, 15), (16, 15), (16, 0), (20, 0), (20, 18), (-20, 18)]), 10.0, os.path.join(d, "pi.stl"), up=True)
        r = analyse(pi_, FDM, n_s=20000, supports="none"); rb = next(x for x in r["rows"] if x["rule"].startswith("B"))
        assert rb["value"].startswith("1 horizontal") and fired(r) == {"B"} and abs(r["ceilings"][0]["span"] - 32) < 1, (rb["value"], r["ceilings"][:1])
        pi6 = _extrude(Polygon([(-7, 0), (-3, 0), (-3, 15), (3, 15), (3, 0), (7, 0), (7, 18), (-7, 18)]), 40.0, os.path.join(d, "pi6.stl"), up=True)
        r = analyse(pi6, FDM, n_s=40000, supports="none"); c = [x for x in r["ceilings"] if x["extent"] > 30]
        assert c and c[0]["cls"] == "bridge" and abs(c[0]["span"] - 6) <= 0.6 and "B bridge (layers)" not in r["flagged"], ("pi 6 x 40 must read 6 and stay silent", c[:1], r["flagged"])
        # 0.10.0: a rebate split by two full-height 2.0 lands into three 6.1 strips, open at both ends, links into ONE ceiling region (gap < link): the span
        # is the longest in-footprint chord 6.1 along the supported axis — the bbox extent (22.3) flipped three verdicts of record in the source project
        w, land, wall = 6.1, 2.0, 4.0; x0 = -(1.5 * w + land + wall); pts2 = [(x0, 0)]
        for i in range(3):
            a = x0 + wall + i * (w + land) if i == 0 else pts2[-1][0]
            if i == 0:
                pts2 += [(a, 0), (a, 15), (a + w, 15), (a + w, 0)]
            else:
                pts2 += [(a + land, 0), (a + land, 15), (a + land + w, 15), (a + land + w, 0)]
        pts2 += [(-x0, 0), (-x0, 18), (x0, 18)]
        reb = _extrude(Polygon(pts2), 40.0, os.path.join(d, "rebate_lands.stl"), up=True)
        r = analyse(reb, FDM, n_s=60000, supports="none"); c = [x for x in r["ceilings"] if x["extent"] > 30]
        assert c and all(x["cls"] == "bridge" for x in c) and max(x["span"] for x in c) <= w + 0.7 and "B bridge (layers)" not in r["flagged"], ("lands-split rebate must read ~6.1 per strip, never the whole-rebate bbox", c[:3], r["flagged"])
        # a 1.4 mm relief ring around a sole (an annular groove on the bottom face, by revolution — no boolean backend needed) and a 1.4 mm straight groove
        # open at both ends: each ceiling reads its WIDTH (~1.4), never the ring's circumference / the groove's 46 mm length
        ring = trimesh.creation.revolve(np.array([(0, 0), (10, 0), (10, 2), (11.4, 2), (11.4, 0), (22, 0), (22, 8), (0, 8)], float), sections=96); ring.export(os.path.join(d, "ring.stl"))
        r = analyse(os.path.join(d, "ring.stl"), FDM, n_s=60000, supports="none"); c = [x for x in r["ceilings"] if x["cls"] == "bridge"]
        assert c and max(x["span"] for x in c) <= 2.0 and "B bridge (layers)" not in r["flagged"], ("a relief ring must read its 1.4 width", [(x["span"], x["extent"]) for x in c], r["flagged"])
        gr = _extrude(Polygon([(-23, 0), (-0.7, 0), (-0.7, 2), (0.7, 2), (0.7, 0), (23, 0), (23, 8), (-23, 8)]), 46.0, os.path.join(d, "groove.stl"), up=True)
        r = analyse(gr, FDM, n_s=60000, supports="none"); c = [x for x in r["ceilings"] if x["cls"] == "bridge"]
        assert c and max(x["span"] for x in c) <= 2.0 and "B bridge (layers)" not in r["flagged"], ("an open groove must read its 1.4 width, not 46", [(x["span"], x["extent"]) for x in c], r["flagged"])
        # a debossed word on the bottom face: five 1.0 mm strokes at 1.0 mm gaps link into ONE cluster whose dilated mask merges them — the span is one
        # STROKE (1.0, the chord from a real sample), never the 9 mm word
        prof = [(-15, 0)]
        for x0 in (-4.5, -2.5, -0.5, 1.5, 3.5):
            prof += [(x0, 0), (x0, 1.0), (x0 + 1, 1.0), (x0 + 1, 0)]
        prof += [(15, 0), (15, 3), (-15, 3)]
        word = _extrude(Polygon(prof), 6.0, os.path.join(d, "word.stl"), up=True)
        r = analyse(word, FDM, n_s=40000, supports="none"); c = [x for x in r["ceilings"] if x["cls"] == "bridge"]
        assert c and max(x["span"] for x in c) <= 1.6 and "B bridge (layers)" not in r["flagged"], ("debossed strokes must read their 1.0 width", [(x["span"], x["extent"]) for x in c], r["flagged"])
        # overhang by reach: a 60 deg pitched slot roof 2 mm across is bridged (listed), a 24 mm one is an overhang defect with supports none (INFO with interior)
        for wid, want in ((2.0, False), (24.0, True)):
            apex = 2 + (wid / 2) * np.tan(np.radians(30))
            op = _extrude(Polygon([(-16, 0), (16, 0), (16, 12), (-16, 12)], holes=[[(-wid / 2, 2), (wid / 2, 2), (0, apex)]]), 40.0, os.path.join(d, f"pitch{wid}.stl"), up=True)
            r = analyse(op, FDM, n_s=40000, supports="none"); oh = r["overhangs"] + r["short_overhangs"]
            assert oh and abs(oh[0]["deg"] - 60) <= 6, (wid, oh[:1])
            assert ("O overhang (layers)" in r["flagged"]) == want and "B bridge (layers)" not in r["flagged"], (wid, r["flagged"])
            assert "O overhang (layers)" not in analyse(op, FDM, n_s=40000, supports="interior")["flagged"]
        # sealed cavity: a 16 mm void in a 20 mm cube: C FLAG on MJF, INFO on FDM; manifold: an open mesh, two cubes touching at a vertex / an edge -> M (bodies / edges); --bodies 2 accepts the clean pair
        o = trimesh.creation.box((20.0, 20.0, 20.0)); i = trimesh.creation.box((16.0, 16.0, 16.0)); i.invert(); cv = os.path.join(d, "cavity.stl"); trimesh.util.concatenate([o, i]).export(cv)
        assert fired(analyse(cv, MJF, n_s=20000)) == {"C"} and analyse(cv, FDM, n_s=20000)["verdict"] == "PASS"
        bx2 = trimesh.creation.box((20.0, 20.0, 5.0)); bx2.faces = bx2.faces[2:]; p7 = os.path.join(d, "open.stl"); bx2.export(p7)
        assert "M manifold / bodies" in analyse(p7, MJF, n_s=5000)["flagged"], "an open mesh must FLAG M"
        for shift, two_ok in (((10, 10, 10), True), ((10, 10, 0), False)):                                   # vertex contact = two clean solids; edge contact = a non-manifold edge as well
            a = trimesh.creation.box((10.0, 10.0, 10.0)); b = trimesh.creation.box((10.0, 10.0, 10.0)); b.apply_translation(shift); tc = os.path.join(d, f"touch{shift[2]}.stl"); trimesh.util.concatenate([a, b]).export(tc)
            r = analyse(tc, MJF, n_s=20000); assert "M manifold / bodies" in r["flagged"], (shift, r["flagged"])
            assert ("M manifold / bodies" not in analyse(tc, MJF, n_s=20000, bodies_expected=2)["flagged"]) == two_ok, shift
        # the gate: FLAG fails; --open needs an OPEN decision row naming the piece; --expect needs a reason; a tampered
        # record, a changed STL, an uncensused STL of the record set, a laxer process row than the target's and a census record without a dfm record all fail
        def quiet(*a, **k):
            with contextlib.redirect_stdout(io.StringIO()):
                return gate(*a, **k)
        tag = os.path.basename(d); G = [os.path.join(d, "dfm")]
        assert quiet(G) == 1, "FLAG must fail"
        assert quiet(G, [f"{tag}/root05=D-00"]) == 1, "--open without a project / decision log must fail"
        assert quiet(G, expected=[f"{tag}/root05="]) == 1 and quiet(G, expected=[f"{tag}/root05=tests the 0.5 root limit"]) == 0, "--expect needs a reason; with one the by-design FLAG is printed, not failed"
        os.makedirs(os.path.join(d, "90-log")); open(os.path.join(d, "90-log", "DECISIONS.md"), "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| **D-07** | d | **OPEN** | widen the root of root05 | p | r |\n| CC-010 | d | APPLIED | x | p | r |\n")
        open(os.path.join(d, "project.yaml"), "w").write(f"project: {{name: t, scope: mech}}\npaths: {{mech_record: 'stl/*.stl'}}\nprint_targets: {{{tag}: {{dfm_process: jlc_mjf_pa12}}}}\n")
        assert quiet(G, [f"{tag}/root05=WHATEVER"]) == 1 and quiet(G, [f"{tag}/root05=CC-010"]) == 1, "a free string or an APPLIED row is not an OPEN decision"
        assert quiet(G, [f"{tag}/root13=D-07"]) == 1, "an OPEN row that does not name the piece is not its licence (blind review 0.9.0 N2)"
        assert quiet(G, [f"{tag}/root05=D-07"]) == 0, "an OPEN row names the finding"
        rj = os.path.join(d, "dfm", "root13.json"); e = json.load(open(rj)); e["verdict"] = "FLAG"; json.dump(e, open(rj, "w")); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a hand-edited record fails the signature"
        e["verdict"] = "PASS"; json.dump(e, open(rj, "w")); assert quiet(G, [f"{tag}/root05=D-07"]) == 0, "restored body verifies again"
        json.dump([[0, 0, 0, 1, 1, 1]], open(os.path.join(d, "dfm", "root13.boxes.json"), "w")); assert quiet(G, [f"{tag}/root05=D-07"]) == 0, "a boxes sidecar is not a record"
        os.makedirs(os.path.join(d, "stl")); shutil.copy(p1, os.path.join(d, "stl", "plate08.stl")); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a body of the record set without a record fails"
        os.remove(os.path.join(d, "stl", "plate08.stl"))
        analyse(p5, "protolabs_mjf_pa12", n_s=20000, out_dir=os.path.join(d, "dfm"), piece="root13"); assert quiet(G, [f"{tag}/root05=D-07"]) == 1, "a laxer process row than print_targets.<t>.dfm_process fails"
        analyse(p5, MJF, n_s=60000, out_dir=os.path.join(d, "dfm"), piece="root13"); assert quiet(G, [f"{tag}/root05=D-07"]) == 0
        assert quiet(G, [f"{tag}/root05=D-07"], target="nope") == 1, "an unknown print target fails"
        os.makedirs(os.path.join(d, "census")); json.dump(dict(stl=p5, stl_md5="0" * 32), open(os.path.join(d, "census", "root13.json"), "w"))
        assert quiet(G, [f"{tag}/root05=D-07"]) == 1
        json.dump(dict(stl=p5, stl_md5=md5(p5)), open(os.path.join(d, "census", "root13.json"), "w")); json.dump({}, open(os.path.join(d, "census", "orphan.json"), "w"))
        assert quiet(G, [f"{tag}/root05=D-07"]) == 1
        os.remove(os.path.join(d, "census", "orphan.json")); assert quiet(G, [f"{tag}/root05=D-07"]) == 0
        # the validation loop on the verdict schema: a labelled FLAG we pass is a RULE DEFECT; twins of one geometry are one row
        shutil.copy(p4, os.path.join(d, "root05_twin.stl"))
        PATHS.update(verdicts=os.path.join(d, "v.yaml"), val_dir=os.path.join(d, "val"), val_doc=os.path.join(d, "VAL.md"))
        yaml.safe_dump(dict(verdicts=[dict(stl=p4, md5=md5(p4)[:8], process=MJF, vendor="x", date="2026-01-01", verdict="FLAG", evidence="e1"),
                                      dict(stl=os.path.join(d, "root05_twin.stl"), md5=md5(p4)[:8], process=MJF, vendor="x", date="2026-01-01", verdict="FLAG", evidence="e1 twin"),
                                      dict(stl=p5, md5=md5(p5)[:8], process=MJF, vendor="x", date="2026-01-01", verdict="FLAG", evidence="e2"),
                                      dict(stl=p2, md5=md5(p2)[:8], process=MJF, vendor=False, source="old schema")]), open(PATHS["verdicts"], "w"))
        with contextlib.redirect_stdout(io.StringIO()):
            v = validate()
        assert v["groups"] == 3 and v["looser"] == [p5] and v["cm"] == {"FLAG->FLAG": 1, "FLAG->PASS": 1, "PASS->PASS": 1}, (v["groups"], v["cm"])
        doc = open(PATHS["val_doc"]).read(); assert "RULE DEFECT" in doc and "<!-- hand: begin -->" in doc and "root05_twin.stl" in doc and "## 3b." in doc
        assert _label_verdict(dict(vendor=None)) is None and _label_verdict(dict(verdict="n/a")) is None
    ROOT = ROOT0
    print("selftest OK: ray reads 0.8 on the 0.8 plate (W, no R) / 2.0 plate PASS / free ribs W no R / 0.5 root under a 2.0 rim x 90 -> W + R, root 1.3 PASS / SLA size / "
          "Z-limited legend box keeps W, full box lists it, records byte-identical, sidecar written + removed / 0.3 rib in a box listed not W / pins Ø0.4 Ø0.3 -> F, Ø1.2 PASS / "
          "ridges 30-40-50 K, 60-90 read but pass / 0.6 sheet flat = skin PASS, 0.4 -> Z, stood up -> W / 0.6 slot V on MJF not FDM / 2 mm tunnel span 2, 15 mm -> B / tee arms read their inscribed width (silent), pi roof 32 mm bridge B, pi 6 x 40 silent, lands-split rebate 3 x 6.1 silent, 1.4 relief ring + open groove read 1.4, debossed 1.0 strokes read 1.0 (span by rays from the ceiling sample nearest the inscribed-circle centre) / "
          "60 deg slot roof 2 mm bridged, 24 mm -> O / cavity C (MJF) INFO (FDM) / open mesh + touching cubes M, --bodies 2 / gate (FLAG, --open only an OPEN row naming the piece, --expect with a reason, tampered record, sidecar ignored, uncensused STL, laxer row, md5, orphan census) / validate (RULE DEFECT, geometry twins grouped, both label schemas)")


def main():
    ap = argparse.ArgumentParser(description="vendor-independent print manufacturability check (hw-from-spec); see references/print-dfm.md")
    ap.add_argument("stl", nargs="*"); ap.add_argument("--process", help="row of the process table (--list shows them)"); ap.add_argument("--out", help="record dir (DIR/<piece>.json [+ <piece>.boxes.json])"); ap.add_argument("--piece"); ap.add_argument("--render", action="store_true", help="heat maps beside the record (matplotlib)")
    ap.add_argument("--samples", type=int); ap.add_argument("--bodies", type=int, default=1, help="solids the file intentionally holds (rule M; default 1)")
    ap.add_argument("--boxes", help="legend boxes JSON [[x0,y0,z0,x1,y1,z1],...] in the print frame (the generators write <piece>.boxes.json beside the record)")
    ap.add_argument("--land", nargs=4, type=float, action="append", metavar=("X0", "Y0", "X1", "Y1"), help="legend box spanning every Z (repeatable; legacy spelling of --boxes)")
    ap.add_argument("--supports", choices=["none", "interior", "any"], help="the body's own support setting (overrides the process row): none makes O / B gates")
    ap.add_argument("--processes", help=f"process table (default {os.path.relpath(DEFAULTS['processes'])}, else the skill template)"); ap.add_argument("--list", action="store_true")
    ap.add_argument("--gate", nargs="+", metavar="DFM_DIR"); ap.add_argument("--open", nargs="*", default=[], metavar="TAG/PIECE=ID"); ap.add_argument("--expect", nargs="*", default=[], metavar="TAG/PIECE=REASON", help="--gate: a body that FLAGs BY DESIGN (a coupon that tests the limit), printed with its reason")
    ap.add_argument("--target", help="--gate: the print target the DIRs belong to (default: DIR's parent name)")
    ap.add_argument("--validate", action="store_true"); ap.add_argument("--verdicts", help=f"default {os.path.relpath(DEFAULTS['verdicts'])}"); ap.add_argument("--val-dir"); ap.add_argument("--val-doc"); ap.add_argument("--render-validation", nargs="*", default=[], metavar="SUBSTR")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    for k in ("processes", "verdicts", "val_dir", "val_doc"):
        if getattr(a, k):
            PATHS[k] = os.path.abspath(getattr(a, k))
    if a.processes and not os.path.exists(PATHS["processes"]):
        print(f"print_dfm: --processes {a.processes} does not exist (the template fallback applies only when no table is named)", file=sys.stderr); return 2
    if a.selftest:
        selftest(); return 0
    if a.list:
        table, p = processes(); print(f"process rows of {p}:")
        for k, v in table.items():
            print(f"  {k:22s} {v.get('vendor', '')} / {v.get('process', '')}: wall_min {v.get('wall_min')} feature_min {v.get('feature_min')} detail_min {v.get('detail_min')} void_min {v.get('void_min')} hole_min {v.get('hole_min')} media {v.get('media', 'powder')}" + (f" layer {v['layer']} x {v.get('skin_min_layers', 3)}" if v.get("layer") else "") + ("  (BLOCKED: wall_min null)" if v.get("wall_min") is None else ""))
        return 0
    if a.gate:
        return gate(a.gate, a.open, a.target, a.expect)
    if a.validate:
        c = validate(renders=a.render_validation); print(json.dumps(dict(geometries=c["groups"], cm=c["cm"], per_rule=c["per_rule"], stricter=c["stricter"]), indent=1))
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
    if a.boxes and not os.path.isfile(a.boxes):
        print(f"print_dfm: no such boxes file: {a.boxes}", file=sys.stderr); return 2
    boxes = load_boxes(a.boxes) + norm_boxes(a.land)
    rc = 0
    for p in a.stl:
        r = analyse(p, a.process, n_s=a.samples, boxes=boxes, out_dir=a.out, piece=a.piece, render=a.render, supports=a.supports, bodies_expected=a.bodies)
        print(f"{p}: {r['verdict']} ({a.process}) faces {r['faces']} watertight {r['watertight']} area {r['area_mm2']} mm2 samples {r['samples']} t_min {r['t_min']} ray median {r['ray_med']} {r['_seconds']} s" + (f" boxes {len(r['boxes'])}" if r["boxes"] else "") + "  [rows: verdict rule: measured | limit | where (box = xmin ymin zmin xmax ymax zmax) | fix]")
        for row in r["rows"]:
            print(f"  {row['verdict']:5s} {row['rule']}: {row['value']} | {row['limit']} | {row['where'][:300]}" + (f" | fix: {row['fix']}" if row["verdict"] == "FLAG" and row.get("fix") else ""))
        rc |= r["verdict"] == "FLAG"
    return rc


if __name__ == "__main__":
    sys.exit(main())
