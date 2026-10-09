#!/usr/bin/env python3
"""scripts/thin_wall_census.py — the thin-wall census that gates a printed body (references/dfm-printed-enclosure.md §2; rows: templates/CENSUS_GATE_ROWS.md).

  scripts/thin_wall_census.py PIECE.stl --target NAME [--project project.yaml] [--json OUT.json]
                              [--gate G] [--void-gate V] [--red R] [--wedge-band B] [--design-margin M] [--samples N | --samples-per-mm2 D]
                              [--cell 3.0] [--self-hit 0.02] [--boxes BOXES.json] [--box-min 1.0] [--accepted ACC.json]
      Every number comes from `project.yaml print_targets.<NAME>` (wall_gate, void_gate, red_line, wedge_band, design_margin, samples_per_mm2, accepted);
      a flag given on the command line overrides that one value; with no --target every gate must be given (no constant lives here).
      Every surface sample casts a ray INWARD (hit distance = wall thickness) and OUTWARD (hit within the void gate = a slot / slit / groove /
      engraved stroke narrower than the gate). Samples below `gate - 0.05` are grid-clustered (26-neighbour cells) and each cluster is CLASSIFIED
      by the angle between the sample face and the hit face: < 30 deg = WALL (a skin whose thickness IS the hit distance), else WEDGE (chamfer,
      ramp, rail flank — thickness grows away from the edge); the two classes are clustered SEPARATELY (a mixed cluster chained through chamfer
      flanks once swallowed a sub-gate lip under the "wedge" label). Gated: WALL clusters below the gate, VOID clusters below the void gate, WEDGE
      clusters whose band of sub-gate surface is wider than --wedge-band (a chamfer cut into a wall has a narrow band; a free-standing 35 deg
      rail flank a wide one), and OPPOSING faces — the nearest face with an opposing normal in ANY direction (a ledge underside beside a step top,
      the root of a rim ring set inboard of its wall: invisible to normal rays, coloured by the vendor). A FAIL cluster passes only when an
      `accepted` entry {class, bbox, reason, date, evidence} covers it (bbox ± 1 mm, same class, all three text fields present).
      MARGIN row (class `margin`): wall-class samples under `wall_gate + design_margin - 0.05` are clustered on their own. A WALL cluster
      outside the boxes whose median sits at or over the gate and under that line FAILs. 0.05 is the census sampling noise (CLUSTER_MARGIN).
      design_margin comes from the target (--design-margin overrides it); 0 or absent adds no row.
      A cluster mostly inside a --boxes box gates at --box-min instead — wall, void AND opposing-face rows. An in-box wall / void
      cluster gates on its 10th-percentile sample (BOX_PCT), not its median; opposing rows gate on their minimum. A box is the print_dfm
      3-D tuple [x0, y0, z0, x1, y1, z1] or [x0, y0, z0, x1, y1, z1, land_min, void_min]: a sample outside its Z band is not in the box,
      and the trailing pair gates walls / voids at the box's own values (a debossed label's 0.45 beside raised 0.9 strokes on one part).
      The legacy 2-D [x0, y0, x1, y1] and [x0, y0, x1, y1, gate] span every Z and print a WARNING; any other length exits 2.
      Samples default to --samples-per-mm2 x surface area (a fixed count under-samples a large part). Prints the rows, writes --json, exit 1 on
      any unaccepted FAIL. Needs numpy + trimesh + scipy at run time.
  scripts/thin_wall_census.py --gate-dir DIR [DIR ...]
      PURE gate for the adopt list (recomputes nothing; exit 1 on any problem): every DIR/*.json (written by --json) must verify its `sig`
      (hand-edited = FAIL), carry this VERSION, name an STL whose md5 equals `stl_md5`, carry an empty `fails` list, and every `accepted_fails`
      entry must still carry reason / date / evidence AND match an entry of `print_targets.<record.target>.accepted` in the current
      project.yaml by the same reason / date / evidence, the same class and a bbox that still covers the record's cluster bbox (± ACC_TOL)
      (an acceptance deleted, re-classed or narrowed in the yaml un-passes the body — "re-asserted every run"). Every STL of the record set under DIR's
      parent (`<set>/parts/*.stl` when DIR is `<set>/checks/census`, else the sibling `stl/`, and the `paths.mech_record` glob) needs a same-md5
      census record (blind review 0.8.0 F5).
  scripts/thin_wall_census.py --selftest
      pure python core (classification, clustering, wedge band, accepted matching, gating, the pure gate on a temp dir); with numpy + trimesh +
      scipy + shapely installed also the RECALL primitives: a 1.0 plate (WALL FAIL), a 45 deg prism (wedges, band under 1.5, 0 FAIL), a 2.0 plate
      (0 FAIL), a 3.0 plate with a 0.8 rib and a 0.6 slit (exactly one WALL FAIL and one VOID FAIL), a wall with a rim ring on a 0.4 root (one
      OPPOSING FAIL while every normal ray reads >= 1.3).

Conventions baked in (references/dfm-printed-enclosure.md §2): cluster below `gate - 0.05` (at the gate itself the nominal walls sampled 0.01
under join every region into one cluster); a ray nudged inside a face hits that face at ~0.000 — discard hits closer than --self-hit; the 30 deg
wall / wedge split is a convention, not a calibration; a WALL cluster is a wall whatever the yaml calls it (lip, land, skin, floor, ring).
"""
import argparse, glob, hashlib, json, math, os, sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import record_sig, verify_sig  # noqa: E402 — pure python, no yaml until a project is read

VERSION = "0.10.0"       # census record version: stamped + signed into every record; the pure gate refuses another version
WALL_DEG = 30.0          # convention: opposite face within 30 deg of parallel = a wall
CLUSTER_MARGIN = 0.05    # convention: cluster below gate - 0.05; also the census sampling noise the margin row allows (a nominal wall reads up to 0.05 under)
BOX_PCT = 0.10           # an in-box (legend) cluster gates on its 10th-percentile sample, not its median (a thin stroke edge hides under a median)
BINS = (0, 0.3, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, math.inf)
ACC_TOL = 1.0            # mm: an accepted entry's bbox covers a cluster bbox within this


# ---------------------------------------------------------------- pure-python core (selftested) -----------------------------------------------
def first_hit_beyond(dists, self_hit):
    """The thickness a ray reports: the first hit farther than self_hit (the nudged origin's own face returns ~0.000); shared with thin_wall_check."""
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


def norm_boxes(boxes, warn=True):
    """--boxes entries -> (x0, y0, z0, x1, y1, z1, wall_gate, void_gate) tuples (gates None when the box carries none).
    6 / 8 values = the print_dfm 3-D box (+ land_min, void_min); 4 / 5 values = the legacy 2-D box (+ one gate for both), spanning every Z.
    Any other length exits 2: an 8-tuple read as a 5-tuple once took z0 for x1 and y1 for the gate (review 0.11.13 B-5)."""
    out = []
    for b in boxes or []:
        b = [float(v) for v in b]
        if len(b) in (4, 5):
            if warn:
                print(f"WARNING thin_wall_census: legacy 2-D box {b} spans every Z (it exempts the wall under the legend); write the print_dfm 3-D box", file=sys.stderr)
            g = b[4] if len(b) == 5 else None; b = [b[0], b[1], -math.inf, b[2], b[3], math.inf, g, g]
        elif len(b) == 6:
            b = b + [None, None]
        elif len(b) != 8:
            print(f"thin_wall_census: box {b} has {len(b)} values; expected [x0, y0, z0, x1, y1, z1] or [x0, y0, z0, x1, y1, z1, land_min, void_min] (legacy [x0, y0, x1, y1(, gate)])", file=sys.stderr); sys.exit(2)
        out.append(tuple(min(b[i], b[i + 3]) for i in range(3)) + tuple(max(b[i], b[i + 3]) for i in range(3)) + tuple(b[6:]))
    return out


def _inside(p, b):
    return all(b[i] <= p[i] <= b[i + 3] for i in range(3))


def in_box_frac(points, boxes):
    if not boxes or not points:
        return 0.0
    return sum(any(_inside(p, b) for b in boxes) for p in points) / len(points)


def box_gate(points, boxes, k=6):
    """the own gate of the box holding most of the cluster (k = 6 wall, 7 void); None when it carries none. Boxes come from norm_boxes."""
    best, n_best = None, 0
    for b in boxes or []:
        n = sum(_inside(p, b) for p in points)
        if n > n_best:
            best, n_best = b, n
    return float(best[k]) if best is not None and best[k] is not None else None


def _own(pp, boxes, k=6):
    g = box_gate(pp, boxes, k)
    return {"box_gate": g} if g is not None else {}        # absent unless a box carries a gate: records of plain boxes stay byte-identical


def _extent(pp):
    lo = [min(p[i] for p in pp) for i in range(3)]; hi = [max(p[i] for p in pp) for i in range(3)]
    ext = sorted((h - l for l, h in zip(lo, hi)), reverse=True)
    return lo, hi, ext


def cluster_rows(points, values, angles, cell=3.0, red=0.5, boxes=None):
    """Thin samples -> rows {n, tmin, tmed, tmed_wall, n_red, wall_frac, cls, span, band, bbox, in_box_frac}; WALL rows first, biggest first.
    band = the second-largest bbox extent: how far the sub-gate surface reaches from the thin edge (a free wedge's band is wide, a chamfer's narrow)."""
    rows = []
    for idx in grid_groups(points, cell):
        pp = [points[i] for i in idx]; tt = sorted(values[i] for i in idx)
        wall = [values[i] for i in idx if angles[i] < WALL_DEG]
        wf = len(wall) / len(idx); tw = sorted(wall) if wall else tt
        lo, hi, ext = _extent(pp)
        rows.append(dict(n=len(idx), tmin=round(tt[0], 3), tmed=round(tt[len(tt) // 2], 2), tmed_wall=round(tw[len(tw) // 2], 2),
                         tp10_wall=round(tw[int(len(tw) * BOX_PCT)], 2), n_red=sum(t < red for t in tt), wall_frac=round(wf, 2), cls="wall" if wf >= 0.5 else "wedge",
                         span=round(ext[0], 1), band=round(ext[1], 2), bbox=[round(x, 1) for x in lo + hi],
                         in_box_frac=round(in_box_frac(pp, boxes), 2), **_own(pp, boxes)))
    rows.sort(key=lambda r: (r["cls"] != "wall", -r["n"]))
    return rows


def void_rows(points, gaps, cell=3.0, boxes=None):
    rows = []
    for idx in grid_groups(points, cell):
        pp = [points[i] for i in idx]; gg = sorted(gaps[i] for i in idx)
        lo, hi, ext = _extent(pp)
        rows.append(dict(n=len(idx), gmin=round(gg[0], 3), gmed=round(gg[len(gg) // 2], 2), gp10=round(gg[int(len(gg) * BOX_PCT)], 2), span=round(ext[0], 1),
                         bbox=[round(x, 1) for x in lo + hi], in_box_frac=round(in_box_frac(pp, boxes), 2), **_own(pp, boxes, 7)))
    rows.sort(key=lambda r: -r["n"])
    return rows


def opp_rows(points, dists, kinds, cell=3.0, boxes=None):
    """Opposing-face samples (normal rays clean, nearest opposing face below its gate) -> rows {n, dmin, dmed, kind, span, bbox, in_box_frac}."""
    rows = []
    for idx in grid_groups(points, cell):
        pp = [points[i] for i in idx]; dd = sorted(dists[i] for i in idx)
        kind = "void" if sum(kinds[i] for i in idx) * 2 > len(idx) else "wall"
        lo, hi, ext = _extent(pp)
        rows.append(dict(n=len(idx), dmin=round(dd[0], 3), dmed=round(dd[len(dd) // 2], 2), kind=kind, span=round(ext[0], 1),
                         bbox=[round(x, 1) for x in lo + hi], in_box_frac=round(in_box_frac(pp, boxes), 2), **_own(pp, boxes, 7 if kind == "void" else 6)))
    rows.sort(key=lambda r: -r["n"])
    return rows


def accepted_entry(cls, bbox, accepted):
    """The first accepted entry with the same class whose bbox covers the cluster (± ACC_TOL) and that carries reason, date and evidence."""
    for a in accepted or []:
        if a.get("class") != cls or not all(str(a.get(k, "")).strip() for k in ("reason", "date", "evidence")):
            continue
        ab = a.get("bbox") or []
        if len(ab) == 6 and all(ab[i] - ACC_TOL <= bbox[i] and bbox[i + 3] <= ab[i + 3] + ACC_TOL for i in range(3)):
            return a
    return None


def gate_rows(clusters, voids, gate, void_gate, box_min=None, wedge_band=None, opps=None, accepted=None, margin_clusters=None, design_margin=None):
    """-> (fails, accepted_fails): WALL clusters below the gate, VOID clusters below the void gate, WEDGE clusters with a band wider than
    wedge_band (None = wedges are listed only), OPPOSING rows below their gate; a covered FAIL moves to accepted_fails with its entry.
    In-box clusters gate on their 10th percentile (tp10_wall / gp10). MARGIN: a WALL cluster of margin_clusters (wall-class samples under
    gate + design_margin - noise) outside the boxes whose median sits in [gate, gate + design_margin - noise) — nominal walls drawn under the margin."""
    fails, acc = [], []

    def emit(cls, bbox, text):
        a = accepted_entry(cls, bbox, accepted)
        (acc if a else fails).append(text if not a else dict(fail=text, reason=a["reason"], date=a["date"], evidence=a["evidence"], **{"class": cls}, bbox=bbox))
    for c in clusters:
        inb = box_min is not None and c["in_box_frac"] >= 0.5
        g = (c.get("box_gate") or box_min) if inb else gate
        t, lbl = (c.get("tp10_wall", c["tmed_wall"]), "p10 ") if inb else (c["tmed_wall"], "")
        if c["cls"] == "wall":
            if t < g - 1e-9:
                emit("wall", c["bbox"], f"WALL {lbl}{t:.2f} (min {c['tmin']:.2f}) < {g} span {c['span']} bbox {c['bbox']}")
        elif wedge_band is not None and c.get("band", 0) > wedge_band + 1e-9:
            emit("wedge", c["bbox"], f"WEDGE band {c['band']:.2f} > {wedge_band} (edge {c['tmed']:.2f}, min {c['tmin']:.2f}) span {c['span']} bbox {c['bbox']} — free-standing unless an accepted entry names the backing wall")
    for v in voids:
        inb = box_min is not None and v["in_box_frac"] >= 0.5
        g = (v.get("box_gate") or box_min) if inb else void_gate
        t, lbl = (v.get("gp10", v["gmed"]), "p10 ") if inb else (v["gmed"], "")
        if t < g - 1e-9:
            emit("void", v["bbox"], f"VOID {lbl}{t:.2f} (min {v['gmin']:.2f}) < {g} span {v['span']} bbox {v['bbox']}")
    for o in opps or []:
        g = void_gate if o["kind"] == "void" else gate
        if box_min is not None and o.get("in_box_frac", 0) >= 0.5:    # a legend stroke IS two opposing faces box_min apart: the land rule owns it
            g = o.get("box_gate") or box_min
        if o["dmin"] < g - 1e-9:                 # the root WIDTH is the minimum (exact point-to-face distance, no sampling noise); the median grows with the band
            emit("opp", o["bbox"], f"OPP {o['dmin']:.2f} (med {o['dmed']:.2f}) < {g} ({o['kind']}, opposing faces in any direction) span {o['span']} bbox {o['bbox']}")
    line = round(gate + (design_margin or 0) - CLUSTER_MARGIN, 3)
    for c in margin_clusters or []:
        if c["cls"] == "wall" and not (box_min is not None and c["in_box_frac"] >= 0.5) and gate - 1e-9 <= c["tmed_wall"] < line - 1e-9:
            emit("margin", c["bbox"], f"MARGIN {c['tmed_wall']:.2f} (min {c['tmin']:.2f}) < {line} = wall_gate {gate} + design_margin {design_margin} - noise {CLUSTER_MARGIN} span {c['span']} bbox {c['bbox']}")
    return fails, acc


def md5_of(path):
    h = hashlib.md5()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def _project_targets(start):
    """print_targets of the nearest project.yaml above `start` (and its root), or ({}, None) outside a project."""
    d = os.path.abspath(start)
    while True:
        p = os.path.join(d, "project.yaml")
        if os.path.exists(p):
            from project import Project
            P = Project(p); return (P.cfg.get("print_targets") or {}), P
        if os.path.dirname(d) == d:
            return {}, None
        d = os.path.dirname(d)



def parts_dir(records_dir):
    """The STL set a records dir belongs to: `<set>/parts/` when the records sit in `<set>/checks/<kind>/` (the layout of record), else the
    sibling `stl/` of the records dir's parent (an older project shape). One rule for every pure gate."""
    parent = os.path.dirname(os.path.abspath(records_dir.rstrip("/")))
    if os.path.basename(parent) == "checks":
        return os.path.join(os.path.dirname(parent), "parts")
    return os.path.join(parent, "stl")


def pure_gate(dirs):
    """See the docstring's --gate-dir entry. -> problem list."""
    bad = []; n = 0
    for d in dirs:
        parent = os.path.dirname(os.path.abspath(d.rstrip("/"))); targets, P = _project_targets(parent); have = set()
        for name in sorted(os.listdir(d)) if os.path.isdir(d) else []:
            if not name.endswith(".json"):
                continue
            jp = os.path.join(d, name); n += 1
            try:
                r = json.load(open(jp))
            except Exception as e:  # noqa: BLE001 — a corrupt record is a gate failure, not a traceback
                bad.append(f"{jp}: unreadable ({e})"); continue
            if r.get("version") != VERSION:
                bad.append(f"{jp}: census version {r.get('version')} != {VERSION} — written by another census version, rerun thin_wall_census {VERSION}"); continue
            if not verify_sig(r, VERSION):
                bad.append(f"{jp}: signature does not verify — edited after it was written, or written by another census version (rerun thin_wall_census {VERSION})"); continue
            stl = r.get("stl", "")
            # the STL of record is the sibling stl/<basename> of THIS tree, then a project-relative path; an absolute path stored by an older
            # census is honoured only inside this project's root (a gate run from another checkout must never read another tree's STLs)
            root = os.path.abspath(P.root) if P else None
            cand = [os.path.join(parts_dir(d), os.path.basename(stl)),
                    os.path.join(root, stl) if root and not os.path.isabs(stl) else "",
                    os.path.join(os.path.dirname(jp), stl) if not os.path.isabs(stl) else "",
                    stl if os.path.isabs(stl) and (root is None or os.path.abspath(stl).startswith(root + os.sep)) else ""]
            path = next((p for p in cand if p and os.path.exists(p)), None)
            if path is None:
                bad.append(f"{jp}: STL {stl!r} not found — expected at {os.path.join(parts_dir(d), os.path.basename(stl))} (the records sit in {d.rstrip('/')}/)"); continue
            have.add(r.get("stl_md5"))
            if md5_of(path) != r.get("stl_md5"):
                bad.append(f"{jp}: census of {str(r.get('stl_md5', '?'))[:8]} but the STL of record is {md5_of(path)[:8]} — rerun the census")
            if r.get("fails"):
                bad.append(f"{jp}: {len(r['fails'])} FAIL cluster(s): " + "; ".join(r["fails"])[:300])
            cur = (targets.get(r.get("target")) or {}).get("accepted") if r.get("target") in targets else None
            for a in r.get("accepted_fails") or []:
                if not all(str(a.get(k, "")).strip() for k in ("reason", "date", "evidence")):
                    bad.append(f"{jp}: accepted entry without reason / date / evidence: {a.get('fail', '?')[:80]}")
                elif cur is not None and not (a.get("class") and len(a.get("bbox") or []) == 6):
                    bad.append(f"{jp}: accepted entry without class / bbox ({a.get('fail', '?')[:60]}) — written before 0.11.14, rerun the census")
                elif cur is not None and not accepted_entry(a["class"], a["bbox"], [x for x in cur if all(str(x.get(k)) == str(a.get(k)) for k in ("reason", "date", "evidence"))]):
                    bad.append(f"{jp}: accepted entry no longer in print_targets.{r['target']}.accepted with its class and a bbox covering {a['bbox']} ({a.get('fail', '?')[:60]}) — the acceptance was withdrawn or moved; the FAIL stands, rerun")
        set_root = os.path.dirname(parts_dir(d))
        stls = set(glob.glob(os.path.join(parts_dir(d), "*.stl")))
        if P and P.get("paths.mech_record"):
            stls |= {f for f in glob.glob(os.path.join(P.root, P.get("paths.mech_record"))) if os.path.abspath(f).startswith(set_root + os.sep)}
        for f in sorted(stls):
            if md5_of(f) not in have:
                bad.append(f"{f}: body of the record set without a census record of its md5 (run thin_wall_census.py --target <t> --json {d}/<piece>.json on it)")
    if n == 0:
        bad.append("no census JSON found in " + ", ".join(dirs))
    return bad


def target_settings(name, project_arg=None):
    """print_targets.<name> from project.yaml -> dict of the census knobs (None where the target does not say)."""
    sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
    from project import Project  # noqa: E402 — pyyaml only when a target is named
    P = Project.find(arg=project_arg)
    t = (P.cfg.get("print_targets") or {}).get(name)
    if not t:
        print(f"thin_wall_census: print_targets.{name} not found in {P.file} (references/project-yaml.md)", file=sys.stderr); sys.exit(2)
    return dict(gate=t.get("wall_gate"), void_gate=t.get("void_gate"), red=t.get("red_line"), wedge_band=t.get("wedge_band"),
                density=t.get("samples_per_mm2"), accepted=t.get("accepted") or [], design_margin=t.get("design_margin"))


# ---------------------------------------------------------------- mesh wrapper (numpy + trimesh + scipy) --------------------------------------
def need(*mods):
    import importlib
    out = []
    for name in mods:
        try:
            out.append(importlib.import_module(name))
        except ImportError:
            print(f"thin_wall_census: this mode needs {', '.join(mods)} ({name} is not installed): pip install {' '.join(mods)}", file=sys.stderr); sys.exit(2)
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


def opposing_faces(m, pts, nrm, fid, radius, np):
    """Per sample: (exact distance to the nearest face whose normal opposes the sample's within WALL_DEG, in ANY direction; kind 0 = material
    between (wall / root), 1 = air between (void)). Candidate faces come from sample pairs within `radius` (scipy KD-tree); the distance is the
    exact point-to-triangle distance, so it does not depend on the sampling density."""
    from scipy.spatial import cKDTree
    from trimesh.triangles import closest_point
    d = np.full(len(pts), np.inf); kind = np.zeros(len(pts), dtype=int)
    pairs = cKDTree(pts).query_pairs(r=radius, output_type="ndarray")
    if len(pairs) == 0:
        return d, kind
    i, j = pairs[:, 0], pairs[:, 1]
    opp = np.einsum("ij,ij->i", nrm[i], nrm[j]) < -math.cos(math.radians(WALL_DEG))
    i, j = i[opp], j[opp]
    tri = m.triangles
    for a, b in ((i, j), (j, i)):                     # a = the sample, b = the opposing partner whose FACE we measure to
        if len(a) == 0:
            continue
        cp = closest_point(tri[fid[b]], pts[a]); dist = np.linalg.norm(cp - pts[a], axis=1)
        side = np.einsum("ij,ij->i", cp - pts[a], nrm[a])          # > 0: the opposing face lies in front (air between); <= 0: behind / beside (material)
        np.minimum.at(d, a, dist)
        best = dist <= d[a] + 1e-9
        kind[a[best]] = (side[best] > 0.1 * dist[best]).astype(int)
    return d, kind


def census(stl, samples, gate, void_gate, cell, self_hit, red, boxes, box_min, out_json, wedge_band=None, density=None, accepted=None,
           target=None, seed=0, design_margin=None):
    np, trimesh = need("numpy", "trimesh", "scipy")[:2]
    boxes = norm_boxes(boxes)
    np.random.seed(seed)                                                                  # trimesh < 4 reads the global seed
    m = trimesh.load(stl, force="mesh")
    area = float(m.area)
    if samples is None:
        samples = max(2000, int(math.ceil(area * (density or 10.0))))
    thr = round(gate - CLUSTER_MARGIN, 3)
    pts, fid = trimesh.sample.sample_surface(m, samples, seed=seed); nrm = m.face_normals[fid]   # trimesh >= 4 ignores np.random.seed: seed the sampler itself
    th, ang = first_hits(m, pts - nrm * 1e-3, -nrm, nrm, self_hit, np)                  # inward: wall thickness; hit face vs sample face
    gap, oang = first_hits(m, pts + nrm * 1e-3, nrm, nrm, self_hit, np)                 # outward: void width; a re-entrant corner is not a slot
    gap = np.where(np.isnan(oang) | (oang >= WALL_DEG), np.inf, gap)
    ang = np.where(np.isnan(ang), 180.0, ang)
    dopp, kind = opposing_faces(m, pts, nrm, fid, max(gate, void_gate), np)
    P = pts.tolist(); T = th.tolist(); A = ang.tolist(); G = gap.tolist(); D = dopp.tolist(); K = kind.tolist()
    # cluster WALL-class and WEDGE-class samples SEPARATELY: one mixed cluster that chained across a body through chamfer flanks was labelled
    # "wedge" and swallowed a 1.0..1.2 lip and 1.3 slot lands (a vendor-MJF retro, 2026-09-28)
    clusters = []
    for pick in (lambda i: A[i] < WALL_DEG, lambda i: A[i] >= WALL_DEG):
        thin = [i for i in range(samples) if T[i] < thr and pick(i)]
        clusters += cluster_rows([P[i] for i in thin], [T[i] for i in thin], [A[i] for i in thin], cell, red, boxes)
    clusters.sort(key=lambda r: (r["cls"] != "wall", -r["n"]))
    vt = [i for i in range(samples) if G[i] < void_gate]
    voids = void_rows([P[i] for i in vt], [G[i] for i in vt], cell, boxes)
    # opposing faces: only where the normal rays are clean (otherwise the wall / void row already carries the finding)
    ot = [i for i in range(samples) if T[i] >= thr and G[i] >= void_gate and D[i] < ((void_gate if K[i] else gate) - CLUSTER_MARGIN)]   # normal rays clean, opposing face not
    opps = opp_rows([P[i] for i in ot], [D[i] for i in ot], [K[i] for i in ot], cell, boxes)
    # MARGIN row: wall-class samples under gate + design_margin - noise, clustered on their own (merging them into the gate pass would let a
    # nominal 1.3 wall carry a sub-gate lip's median over the gate)
    mthr = round(gate + (design_margin or 0) - CLUSTER_MARGIN, 3)
    mi = [i for i in range(samples) if T[i] < mthr and A[i] < WALL_DEG] if (design_margin or 0) > 0 else []
    mclusters = cluster_rows([P[i] for i in mi], [T[i] for i in mi], [A[i] for i in mi], cell, red, boxes)
    fails, acc = gate_rows(clusters, voids, gate, void_gate, box_min if boxes else None, wedge_band, opps, accepted, mclusters, design_margin)
    wall = ang < WALL_DEG
    _, Pr = _project_targets(os.path.dirname(os.path.abspath(stl)))
    stl_rec = os.path.relpath(os.path.abspath(stl), os.path.abspath(Pr.root)) if Pr else stl   # project-relative in the record: the gate resolves it in ITS tree
    r = dict(version=VERSION, stl=stl_rec, stl_md5=md5_of(stl), target=target, faces=int(len(m.faces)), watertight=bool(m.is_watertight),
             bodies=int(len(m.split(only_watertight=False))), bbox=np.round(m.bounds, 2).tolist(), vol_cm3=round(float(m.volume) / 1000, 3),
             area_mm2=round(area, 1), signature=dict(vol=round(float(m.volume), 3), area=round(area, 3), bbox=np.round(m.bounds, 3).tolist(), faces=int(len(m.faces))),
             samples=samples, density_per_mm2=round(samples / area, 2), gate=gate, void_gate=void_gate, red=red, wedge_band=wedge_band, thr=thr,
             design_margin=design_margin, margin_line=mthr if (design_margin or 0) > 0 else None,
             hist=histogram(T), frac_below={str(b): round(float((th < b).mean()), 4) for b in (0.8, 1.0, gate)},
             wall_frac_below={str(thr): round(float(((th < thr) & wall).mean()), 5)}, void_frac_below={str(thr): round(float((gap < thr).mean()), 5)},
             clusters=clusters, voids=voids, opposing=opps, fails=fails, accepted_fails=acc)
    print(f"{stl} md5 {r['stl_md5'][:8]} target {target} faces {r['faces']} watertight {r['watertight']} bodies {r['bodies']} bbox {r['bbox']} vol {r['vol_cm3']} cm3 area {r['area_mm2']} mm2 samples {samples} ({r['density_per_mm2']}/mm2)")
    print(f"histogram {r['hist']}  below 0.8 / 1.0 / {gate}: {r['frac_below']}  NOISE FLOOR wall-class / void-facing below {thr}: {r['wall_frac_below'][str(thr)]:.2%} / {r['void_frac_below'][str(thr)]:.2%}")
    print(f"clusters < {thr} (cls n tmed_wall tmin band span bbox in_box):")
    for c in clusters[:30]:
        print(f"  {c['cls']:5s} n {c['n']:5d} wall-med {c['tmed_wall']:.2f} min {c['tmin']:.2f} band {c['band']:5.2f} span {c['span']:6.1f} bbox {c['bbox']} box {c['in_box_frac']:.2f}")
    print(f"voids < {void_gate} (n gmed gmin span bbox):")
    for v in voids[:30]:
        print(f"  n {v['n']:5d} med {v['gmed']:.2f} min {v['gmin']:.2f} span {v['span']:6.1f} bbox {v['bbox']}")
    print(f"opposing faces below the gate where the normal rays were clean (n dmed dmin kind span bbox):")
    for o in opps[:30]:
        print(f"  n {o['n']:5d} med {o['dmed']:.2f} min {o['dmin']:.2f} {o['kind']:4s} span {o['span']:6.1f} bbox {o['bbox']}")
    print(f"FAIL {len(fails)}" + ("".join("\n  " + f for f in fails) if fails else
                                   f" — 0 walls below the gate, 0 voids below the void gate, 0 wedges over band {wedge_band}, 0 opposing faces, 0 walls under the margin line; wedges listed: "
                                   f"{sum(c['cls'] == 'wedge' for c in clusters)}") + (f"; ACCEPTED {len(acc)} (dated, evidence): " + "; ".join(a['fail'][:60] for a in acc) if acc else ""))
    r["sig"] = record_sig(r, VERSION)                                          # the pure gate refuses a record whose body changed after it was written
    if out_json:
        json.dump(r, open(out_json, "w"), indent=1)
    return 1 if fails else 0


# ---------------------------------------------------------------- selftest -----------------------------------------------------------------------
def selftest():
    import tempfile
    # pure core: a 1.0 plate = parallel-face samples -> ONE wall cluster, FAIL at 1.2; a 45 deg wedge -> wedge, never FAIL under the band; a 0.5 void -> FAIL
    plate = [(x * 1.0, y * 1.0, 0.0) for x in range(30) for y in range(30)]
    rows = cluster_rows(plate, [1.0] * 900, [0.0] * 900, cell=3.0)
    assert len(rows) == 1 and rows[0]["cls"] == "wall" and rows[0]["tmed_wall"] == 1.0 and rows[0]["span"] == 29.0, rows
    assert gate_rows(rows, [], 1.2, 1.2)[0] and gate_rows(rows, [], 1.0, 1.2)[0] == [], "a 1.0 wall fails 1.2 and passes 1.0"
    wedge = cluster_rows([(x * 0.5, 0.0, z * 1.0) for x in range(3) for z in range(40)], [0.3 + 0.2 * x for x in range(3) for z in range(40)], [45.0] * 120)
    assert wedge[0]["cls"] == "wedge" and abs(wedge[0]["band"] - 1.0) < 1e-6 and gate_rows(wedge, [], 1.2, 1.2, wedge_band=1.5)[0] == [], "a 1.0-wide chamfer band is listed, not gated"
    wide = cluster_rows([(x * 0.5, 0.0, z * 1.0) for x in range(5) for z in range(40)], [0.3 + 0.2 * x for x in range(5) for z in range(40)], [45.0] * 200)
    assert wide[0]["band"] == 2.0 and any(f.startswith("WEDGE band 2.00") for f in gate_rows(wide, [], 1.2, 1.2, wedge_band=1.5)[0]), "a 2.0-wide free flank FAILs the band rule"
    assert gate_rows(wide, [], 1.2, 1.2)[0] == [], "without a band the wedge is listed only"
    mixed = cluster_rows(plate[:100] + [(50.0, 50.0, 0.0)], [1.0] * 100 + [0.4], [0.0] * 100 + [60.0])
    assert [c["cls"] for c in mixed] == ["wall", "wedge"] and mixed[0]["n"] == 100, mixed
    voids = void_rows([(0.0, 0.0, 0.0), (0.5, 0.0, 0.0)], [0.5, 0.45])
    assert gate_rows([], voids, 1.2, 1.2)[0] and gate_rows([], voids, 1.2, 0.4)[0] == [], "a 0.5 slot fails a 1.2 void gate"
    opps = opp_rows([(0.0, 0.0, 10.0), (0.4, 0.0, 10.0)], [0.4, 0.42], [0, 0])
    assert opps[0]["kind"] == "wall" and any(f.startswith("OPP 0.4") for f in gate_rows([], [], 1.2, 1.2, opps=opps)[0]), "a 0.4 root between opposing faces FAILs"
    assert gate_rows([], [], 1.2, 1.2, opps=opp_rows([(0, 0, 0)], [1.1], [1]))[0] and gate_rows([], [], 1.6, 1.0, opps=opp_rows([(0, 0, 0)], [1.1], [1]))[0] == [], "a void-kind opposing pair gates at the void gate"
    # accepted list: same class + covering bbox + reason / date / evidence moves the FAIL; a bare entry does not
    acc = [dict(**{"class": "wall"}, bbox=[-1, -1, -1, 30, 30, 1], reason="vendor accepted in writing", date="2026-09-28", evidence="60-orders/quotes/2026-09-28/mail.eml")]
    f, a = gate_rows(rows, [], 1.2, 1.2, accepted=acc)
    assert f == [] and len(a) == 1 and a[0]["evidence"].endswith(".eml"), (f, a)
    assert gate_rows(rows, [], 1.2, 1.2, accepted=[dict(acc[0], evidence="")])[0], "an entry without evidence does not count"
    assert gate_rows(rows, [], 1.2, 1.2, accepted=[dict(acc[0], **{"class": "void"})])[0], "class must match"
    assert gate_rows(rows, [], 1.2, 1.2, accepted=[dict(acc[0], bbox=[0, 0, 0, 10, 10, 1])])[0], "the entry bbox must cover the cluster"
    # legend boxes: a 1.0 raised stroke inside a box gates at box_min
    boxed = cluster_rows(plate, [1.0] * 900, [0.0] * 900, boxes=norm_boxes([[-1, -1, 31, 31]], warn=False))
    assert boxed[0]["in_box_frac"] == 1.0 and gate_rows(boxed, [], 1.6, 1.0, box_min=1.0)[0] == [] and gate_rows(boxed, [], 1.6, 1.0)[0], "legend land rule"
    assert "box_gate" not in boxed[0], "a plain box adds no key (records stay byte-identical)"
    # a box's own gate (fifth value) wins over --box-min: a 1.0 stroke in a 0.45 box passes under box-min 1.6, the plain box fails
    own = cluster_rows(plate, [1.0] * 900, [0.0] * 900, boxes=norm_boxes([[-1, -1, 31, 31, 0.45]], warn=False))
    assert own[0]["box_gate"] == 0.45 and gate_rows(own, [], 1.6, 1.0, box_min=1.6)[0] == [] and gate_rows(boxed, [], 1.6, 1.0, box_min=1.6)[0], "a box's own gate"
    vown = void_rows([(10.0, 10.0, 6.3)], [0.5], boxes=norm_boxes([[0, 0, 30, 30, 0.45]], warn=False))
    assert gate_rows([], vown, 1.6, 1.0, box_min=0.9)[0] == [] and gate_rows([], void_rows([(10.0, 10.0, 6.3)], [0.5], boxes=norm_boxes([[0, 0, 30, 30]], warn=False)), 1.6, 1.0, box_min=0.9)[0], "void rows honour the box's own gate"
    # B-7: an in-box cluster gates on its 10th percentile: 20 % of the samples at 0.6 and 80 % at 1.0 under a 0.9 land FAIL (the median reads 1.0)
    mix = cluster_rows(plate, [0.6] * 180 + [1.0] * 720, [0.0] * 900, boxes=norm_boxes([[-1, -1, -1, 31, 31, 1, 0.9, 0.9]]))
    assert mix[0]["tmed_wall"] == 1.0 and mix[0]["tp10_wall"] == 0.6 and any(f.startswith("WALL p10 0.60") for f in gate_rows(mix, [], 1.6, 1.0, box_min=0.9)[0]), mix
    vmix = void_rows(plate, [0.3] * 180 + [1.0] * 720, boxes=norm_boxes([[-1, -1, -1, 31, 31, 1, 0.9, 0.9]]))
    assert any(f.startswith("VOID p10 0.30") for f in gate_rows([], vmix, 1.6, 1.0, box_min=0.9)[0]), "in-box voids gate on p10 too"
    assert gate_rows(cluster_rows(plate, [0.6] * 180 + [1.0] * 720, [0.0] * 900), [], 0.9, 1.0)[0] == [], "outside a box the median rule stands"
    # B-1: the MARGIN row — a 1.3 wall under wall_gate 1.2 + design_margin 0.3 - noise 0.05 = 1.45 FAILs; margin 0.0 or a 1.5 wall adds no row
    w13 = cluster_rows(plate, [1.3] * 900, [0.0] * 900)
    f = gate_rows([], [], 1.2, 1.2, margin_clusters=w13, design_margin=0.3)[0]
    assert len(f) == 1 and f[0].startswith("MARGIN 1.30") and "< 1.45" in f[0], f
    assert gate_rows([], [], 1.2, 1.2, margin_clusters=w13, design_margin=0.0)[0] == [], "margin 0.0: no row"
    assert gate_rows([], [], 1.2, 1.2, margin_clusters=cluster_rows(plate, [1.46] * 900, [0.0] * 900), design_margin=0.3)[0] == [], "a 1.46 wall clears 1.45"
    assert gate_rows([], [], 1.2, 1.2, margin_clusters=cluster_rows(plate, [1.0] * 900, [0.0] * 900), design_margin=0.3)[0] == [], "below the gate: the WALL row owns it"
    assert gate_rows([], [], 1.2, 1.2, accepted=[dict(acc[0], **{"class": "margin"})], margin_clusters=w13, design_margin=0.3)[1], "a margin entry accepts it"
    # an opposing-face pair inside a legend land gates at box_min too (a 1.3 raised stroke is two faces 1.3 apart, not a thin wall)
    lopp = opp_rows([(10.0, 10.0, 6.3), (10.0, 11.3, 6.3)], [1.3, 1.3], [0, 0], boxes=norm_boxes([[0, 0, 30, 30]], warn=False))
    assert gate_rows([], [], 1.6, 1.0, box_min=1.0, opps=lopp)[0] == [] and gate_rows([], [], 1.6, 1.0, opps=lopp)[0], "legend land rule applies to opposing-face rows"
    # 3-D boxes (review 0.11.13 B-4 / B-5): a 1.0 host wall (30 x 30, XZ plane) under an 18 mm debossed label box in the top 5 mm FAILs the 1.6 wall
    # gate (the box's Z band holds 1/6 of the wall); the legacy 2-D box of the same footprint spans every Z and exempts it (the defect, kept as legacy)
    hw = [(x * 1.0, 0.0, z * 1.0) for x in range(30) for z in range(30)]
    lab = cluster_rows(hw, [1.0] * 900, [0.0] * 900, boxes=norm_boxes([[0, -1, 25, 18, 1, 30, 0.45, 0.45]]))
    assert lab[0]["in_box_frac"] < 0.5 and any(f.startswith("WALL 1.00") for f in gate_rows(lab, [], 1.6, 1.0, box_min=0.9)[0]), ("host wall under a label box FAILs", lab[0])
    leg = cluster_rows(hw, [1.0] * 900, [0.0] * 900, boxes=norm_boxes([[0, -1, 18, 1, 0.45]], warn=False))
    assert leg[0]["in_box_frac"] >= 0.5 and gate_rows(leg, [], 1.6, 1.0, box_min=0.9)[0] == [], "a legacy 2-D box spans every Z"
    b8 = norm_boxes([[0, -1, 0, 30, 1, 30, 0.9, 0.45]])
    assert cluster_rows(hw, [1.0] * 900, [0.0] * 900, boxes=b8)[0]["box_gate"] == 0.9 and void_rows(hw[:2], [0.5, 0.5], boxes=b8)[0]["box_gate"] == 0.45, "an 8-tuple: land_min gates walls, void_min voids"
    import contextlib, io
    try:
        with contextlib.redirect_stderr(io.StringIO()) as err:
            norm_boxes([[0, 0, 0, 1, 1, 1, 0.9]])
        raise AssertionError("a 7-tuple must exit 2")
    except SystemExit as e:
        assert e.code == 2 and "has 7 values; expected [x0, y0, z0, x1, y1, z1]" in err.getvalue(), err.getvalue()
    assert histogram([0.1, 1.19, 5.0, math.inf])["1.0-1.2"] == 1 and histogram([math.inf])["2.0-inf"] == 1
    # the pure gate: matching md5 + no fails passes; a wrong md5, a FAIL list, an undated acceptance, a tampered record, a withdrawn acceptance
    # and an uncensused STL of the record set are named (review 0.8.0 F5 / F28)
    with tempfile.TemporaryDirectory() as d:
        os.makedirs(os.path.join(d, "stl")); os.makedirs(os.path.join(d, "census"))
        stl = os.path.join(d, "stl", "p_body.stl"); open(stl, "wb").write(b"solid p\nendsolid p\n"); C = os.path.join(d, "census")
        def put(rec, name="p.json"):
            rec = dict(rec); rec["sig"] = record_sig(rec, VERSION); json.dump(rec, open(os.path.join(C, name), "w"))
        acc = dict(fail="WALL 0.9", reason="r", date="2026-01-01", evidence="e", bbox=[0.2, 0.2, 0.2, 0.8, 0.8, 0.8], **{"class": "wall"})
        good = dict(version=VERSION, stl=stl, stl_md5=md5_of(stl), target="t", fails=[], accepted_fails=[acc]); put(good)
        assert pure_gate([C]) == [], pure_gate([C])
        put(dict(good, stl_md5="0" * 32)); assert any("STL of record" in b for b in pure_gate([C]))
        put(dict(good, fails=["WALL 0.88 < 1.2 span 141"])); assert any("FAIL cluster" in b for b in pure_gate([C]))
        put(dict(good, accepted_fails=[dict(acc, date="")])); assert any("without reason / date / evidence" in b for b in pure_gate([C]))
        json.dump(dict(good, fails=[], sig="00"), open(os.path.join(C, "p.json"), "w")); assert any("signature" in b for b in pure_gate([C])), "a hand-edited record fails"
        old = dict(good, version="0.0.1"); old["sig"] = record_sig(old, "0.0.1"); json.dump(old, open(os.path.join(C, "p.json"), "w"))
        assert any("another census version" in b for b in pure_gate([C])), "another version fails"
        put(good); open(os.path.join(d, "stl", "q_body.stl"), "wb").write(b"solid q\nendsolid q\n")
        assert any("without a census record" in b for b in pure_gate([C])), "an uncensused STL beside the records fails"
        os.remove(os.path.join(d, "stl", "q_body.stl"))
        # the record's stl path is resolved in THIS tree: an absolute path into another checkout (same name, other content) must not be read
        with tempfile.TemporaryDirectory() as other:
            os.makedirs(os.path.join(other, "stl")); open(os.path.join(other, "stl", "p_body.stl"), "wb").write(b"solid other\nendsolid other\n")
            put(dict(good, stl=os.path.join(other, "stl", "p_body.stl"))); assert pure_gate([C]) == [], "the sibling stl/ of the record set wins over a stored absolute path"
            put(dict(good, stl=os.path.join(other, "stl", "p_body.stl"), stl_md5=md5_of(os.path.join(other, "stl", "p_body.stl"))))
            assert any("STL of record" in b for b in pure_gate([C])), "a record of another tree's body fails against this tree's STL"
            put(dict(good, stl=os.path.join(other, "stl", "zz_body.stl")))
            nf = [b for b in pure_gate([C]) if "not found" in b]; assert nf and f"expected at {os.path.join(d, 'stl', 'zz_body.stl')} (the records sit in {C}/)" in nf[0], ("a missing STL names its expected path", nf)
        put(dict(good, stl="stl/p_body.stl")); assert pure_gate([C]) == [], "a project-relative path resolves from the record set's parent"
        put(good)
        assert any("no census JSON" in b for b in pure_gate([os.path.join(d, "none")]))
        # with a project (needs pyyaml): the acceptance must still be in print_targets.<t>.accepted; the mech_record glob widens the STL set
        try:
            import yaml  # noqa: F401
        except ImportError:
            print("selftest: pyyaml absent — the project-dependent gate cases were skipped"); yaml = None
        if yaml:
            open(os.path.join(d, "project.yaml"), "w").write("paths: {mech_record: 'stl/*.stl'}\nprint_targets: {t: {wall_gate: 1.2, void_gate: 1.2, red_line: 0.5, wedge_band: 1.5, samples_per_mm2: 10, accepted: [{class: wall, bbox: [0,0,0,1,1,1], reason: r, date: 2026-01-01, evidence: e}]}}\n")
            assert pure_gate([C]) == [], pure_gate([C])
            open(os.path.join(d, "project.yaml"), "w").write("paths: {mech_record: 'stl/*.stl'}\nprint_targets: {t: {wall_gate: 1.2, void_gate: 1.2, red_line: 0.5, wedge_band: 1.5, samples_per_mm2: 10, accepted: []}}\n")
            assert any("withdrawn" in b for b in pure_gate([C])), "an acceptance deleted from the yaml un-passes the body"
            t = target_settings("t", os.path.join(d, "project.yaml"))
            assert t["gate"] == 1.2 and t["wedge_band"] == 1.5 and t["density"] == 10 and t["accepted"] == [], t
            # D-1: the same reason / date / evidence with a moved bbox or another class does not cover the record's cluster
            for e in ("{class: wall, bbox: [5,5,5,6,6,6]", "{class: void, bbox: [0,0,0,1,1,1]"):
                open(os.path.join(d, "project.yaml"), "w").write("paths: {mech_record: 'stl/*.stl'}\nprint_targets: {t: {wall_gate: 1.2, void_gate: 1.2, red_line: 0.5, wedge_band: 1.5, samples_per_mm2: 10, accepted: [" + e + ", reason: r, date: 2026-01-01, evidence: e}]}}\n")
                assert any("withdrawn or moved" in b for b in pure_gate([C])), ("a moved bbox / another class is a gate problem", e, pure_gate([C]))
            put(dict(good, accepted_fails=[dict(fail="WALL 0.9", reason="r", date="2026-01-01", evidence="e")]))
            assert any("without class / bbox" in b for b in pure_gate([C])), "a pre-0.11.14 accepted entry asks for a rerun"
            put(good)
    msg = "selftest OK (pure core: wall / wedge classification, wedge band, opposing rows, accepted matching, void + legend-box gating (in-box p10), MARGIN row, 3-D boxes (host wall under a label box FAILs, legacy 2-D spans Z, 8-tuple gates, bad length exits 2), pure --gate-dir incl. signature / withdrawn or moved acceptance / uncensused STL / foreign-tree path, target settings"
    try:
        import numpy, trimesh, scipy, shapely  # noqa: F401
    except ImportError:
        print(msg + "; numpy / trimesh / scipy / shapely absent — the mesh recall primitives were not run)"); return 0
    from shapely.geometry import Polygon
    with tempfile.TemporaryDirectory() as d:
        run = lambda m, name, **kw: (m.export(os.path.join(d, name)), census(os.path.join(d, name), None, 1.2, 1.2, 3.0, 0.02, 0.5, None, None, os.path.join(d, name + ".json"), wedge_band=1.5, density=10, **kw))[1]
        assert run(trimesh.creation.box((30.0, 30.0, 1.0)), "plate10.stl") == 1, "a 1.0 plate must FAIL the 1.2 gate"
        r = json.load(open(os.path.join(d, "plate10.stl.json"))); w = [c for c in r["clusters"] if c["cls"] == "wall"]
        j1 = open(os.path.join(d, "plate10.stl.json")).read(); run(trimesh.creation.box((30.0, 30.0, 1.0)), "plate10.stl")
        assert open(os.path.join(d, "plate10.stl.json")).read() == j1, "two census runs of one STL must be byte-identical (the sampler is seeded, not only np.random)"
        assert w and abs(w[0]["tmed_wall"] - 1.0) < 0.05 and w[0]["span"] >= 29 and r["fails"] and r["samples"] >= 10 * 1900, r["clusters"][:2]
        assert any("STL of record" not in b for b in pure_gate([d])) and any("FAIL" in b for b in pure_gate([d]))
        prism = trimesh.creation.extrude_triangulation(numpy.array([[0, 0], [20, 0], [0, 20.0]]), numpy.array([[0, 1, 2]]), 30.0)
        assert run(prism, "wedge.stl") == 0, "a 45 deg prism has wedges only, every band under 1.5"
        assert run(trimesh.creation.box((30.0, 30.0, 2.0)), "plate20.stl") == 0, "a 2.0 plate passes"
        # RECALL (proper watertight extrusions, no internal faces): a 3.0 plate carrying a 0.8 rib -> exactly one WALL FAIL at 0.8;
        # a 3.0 plate with a 0.6-wide slit -> exactly one VOID FAIL at 0.6
        ribbed = Polygon([(0, 0), (30, 0), (30, 3), (7.4, 3), (7.4, 6), (6.6, 6), (6.6, 3), (0, 3)])
        assert run(trimesh.creation.extrude_polygon(ribbed, 30.0), "rib.stl") == 1
        r = json.load(open(os.path.join(d, "rib.stl.json")))
        assert [f.split()[0] for f in r["fails"]] == ["WALL"] and abs(float(r["fails"][0].split()[1]) - 0.8) < 0.1, ("recall: one 0.8 rib WALL FAIL", r["fails"])
        slit = Polygon([(0, 0), (30, 0), (30, 30), (15.3, 30), (15.3, 10), (14.7, 10), (14.7, 30), (0, 30)])
        assert run(trimesh.creation.extrude_polygon(slit, 3.0), "slit.stl") == 1
        r = json.load(open(os.path.join(d, "slit.stl.json")))
        assert [f.split()[0] for f in r["fails"]] == ["VOID"] and abs(float(r["fails"][0].split()[1]) - 0.6) < 0.1, ("recall: one 0.6 slit VOID FAIL", r["fails"])
        # OPPOSING: a 2.0 wall carrying a 1.3 rim ring whose root is 0.4 wide — every normal ray >= 1.3, the root FAILs through the opposing metric
        prof = Polygon([(0, 0), (2, 0), (2, 10), (2.9, 10), (2.9, 12.5), (1.6, 12.5), (1.6, 10), (0, 10)])
        assert run(trimesh.creation.extrude_polygon(prof, 40.0), "root.stl") == 1
        r = json.load(open(os.path.join(d, "root.stl.json")))
        assert r["fails"] and all(f.startswith("OPP") for f in r["fails"]) and abs(float(r["fails"][0].split()[1]) - 0.4) < 0.15, ("the 0.4 root", r["fails"], r["clusters"][:3])
        assert r["frac_below"]["1.0"] < 0.01, "normal rays read the wall (2.0) and the ring (1.3) — the root is invisible to them"
        # the same root accepted with evidence passes and is carried in accepted_fails; the pure gate re-asserts the fields
        acc = [dict(**{"class": "opp"}, bbox=[0, 8, -1, 3, 12, 41], reason="root widened next round; vendor accepted this batch", date="2026-09-28", evidence="60-orders/quotes/2026-09-28/DFM_ROUND.md")]
        assert census(os.path.join(d, "root.stl"), None, 1.2, 1.2, 3.0, 0.02, 0.5, None, None, os.path.join(d, "root.stl.json"), wedge_band=1.5, density=10, accepted=acc) == 0
        r = json.load(open(os.path.join(d, "root.stl.json"))); assert r["fails"] == [] and len(r["accepted_fails"]) >= 1
        # B-1 on a mesh: a 1.3 plate passes the 1.2 gate, FAILs the MARGIN row at design_margin 0.3, and adds no row at 0.0
        assert run(trimesh.creation.box((30.0, 30.0, 1.3)), "plate13.stl", design_margin=0.3) == 1
        r = json.load(open(os.path.join(d, "plate13.stl.json"))); assert [x.split()[0] for x in r["fails"]] == ["MARGIN"] and r["margin_line"] == 1.45, r["fails"]
        assert run(trimesh.creation.box((30.0, 30.0, 1.3)), "plate13.stl", design_margin=0.0) == 0
        for n in ("plate10", "rib", "slit"):
            os.remove(os.path.join(d, n + ".stl.json"))
        assert pure_gate([d]) == [], pure_gate([d])
    print(msg + "; recall primitives: 1.0 plate FAIL, 45 deg prism 0 FAIL, 2.0 plate 0 FAIL, 0.8 rib + 0.6 slit = 1 WALL + 1 VOID FAIL, 0.4 rim-ring root = 1 OPP FAIL, accepted root passes, 1.3 plate = 1 MARGIN FAIL at margin 0.3 and 0 at 0.0)"); return 0


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("stl", nargs="?"); ap.add_argument("--gate-dir", nargs="+", metavar="DIR"); ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--target", metavar="NAME", help="print_targets.<NAME> in project.yaml"); ap.add_argument("--project")
    ap.add_argument("--gate", type=float); ap.add_argument("--void-gate", type=float); ap.add_argument("--red", type=float); ap.add_argument("--wedge-band", type=float); ap.add_argument("--design-margin", type=float)
    ap.add_argument("--samples", type=int); ap.add_argument("--samples-per-mm2", type=float)
    ap.add_argument("--cell", type=float, default=3.0); ap.add_argument("--self-hit", type=float, default=0.02)
    ap.add_argument("--boxes", metavar="JSON"); ap.add_argument("--box-min", type=float, default=1.0); ap.add_argument("--accepted", metavar="JSON"); ap.add_argument("--json", metavar="OUT")
    a = ap.parse_args(argv[1:])
    if a.selftest:
        return selftest()
    if a.gate_dir:
        bad = pure_gate(a.gate_dir)
        for b in bad:
            print("CENSUS GATE:", b)
        print(f"census gate: {len(bad)} problem(s)"); return 1 if bad else 0
    if a.stl:
        t = target_settings(a.target, a.project) if a.target else dict(gate=None, void_gate=None, red=None, wedge_band=None, density=None, accepted=[], design_margin=None)
        gate = a.gate if a.gate is not None else t["gate"]; void_gate = a.void_gate if a.void_gate is not None else t["void_gate"]
        if gate is None or void_gate is None:
            print("thin_wall_census: name a print target (--target NAME, project.yaml print_targets) or give --gate and --void-gate — no gate value lives in this script", file=sys.stderr); sys.exit(2)
        red = a.red if a.red is not None else (t["red"] if t["red"] is not None else 0.5)
        wedge_band = a.wedge_band if a.wedge_band is not None else t["wedge_band"]
        density = a.samples_per_mm2 if a.samples_per_mm2 is not None else t["density"]
        accepted = json.load(open(a.accepted)) if a.accepted else t["accepted"]
        boxes = json.load(open(a.boxes)) if a.boxes else None
        margin = a.design_margin if a.design_margin is not None else t["design_margin"]
        return census(a.stl, a.samples, gate, void_gate, a.cell, a.self_hit, red, boxes, a.box_min, a.json, wedge_band, density, accepted, a.target, design_margin=margin)
    ap.print_help(); return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
