#!/usr/bin/env python3
"""scripts/dfm_check.py — the fab-DFM mirror: grading engine, threshold file, acceptance list, report (references/fab-dfm.md).

  python scripts/dfm_check.py --items out/dfm_items.json [--thresholds design/dfm_thresholds.json] [--accept design/board.yaml] [--json out/dfm.json]
  python scripts/dfm_check.py --selftest

Split of work: MEASURING is CAD-specific (a KiCad SWIG measurer lives in the project and emits items); GRADING is generic and lives here,
so the grading rule is written once and tested once. Items JSON: [{"check": "Trace spacing", "value": 0.15, "refs": ["R1", "C2"],
"layer": "F.Cu", "xy": [12.3, 45.6]}]; `value` null = a presence-only check (graded Warning when the fab lists it without a threshold).

Thresholds JSON (design/dfm_thresholds.json — copy the fab's numbers, cite the source and date):
  {"source": "...", "checks": {"Trace spacing": {"danger": 0.10, "warning": 0.15, "fab_counts": [d, w, g]}, "Fiducial": {"danger": null, "warning": null}},
   "project_min": {"Trace width": 0.16}}
Grading (the rule every fab's viewer was observed to use): value <= danger -> Danger; danger < value <= warning -> Warning (EQUAL to the warning
threshold is STILL Warning — design to strictly greater); value > warning -> Good. Values are rounded to 2 decimals before grading (viewers work at
2 decimals); the project rule (`project_min`, applied when the fab lists no threshold or to checks the fab does not run) uses full precision.

Exit 1 when any Danger / Warning / project failure remains that the --accept file does not cover (yaml key `dfm_accepted`, or a standalone list):
entries {check, refs: [REF, ...] | {REF: max_count}, reason}; an item is accepted only when EVERY refdes it involves is listed (a pair needs both)
and, in the dict form, the per-ref count is not exceeded. Items without a refdes (bare tracks, vias) cannot be accepted — fix them.
"""
import argparse, collections, json, os, sys, tempfile
from decimal import Decimal, ROUND_HALF_UP

import yaml

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from project import Project  # noqa: E402

TOL = 5e-4


def r2(v):
    return float(Decimal(str(v)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP))


def grade(check, value, thresholds):
    """('Danger'|'Warning'|'Good'|'project-FAIL'|'INFO', limit_used)"""
    th = (thresholds.get("checks") or {}).get(check)
    pmin = (thresholds.get("project_min") or {}).get(check)
    if th is not None and (th.get("danger") is not None or th.get("warning") is not None):
        if value is None:
            return "Warning", None
        v = r2(value)
        if th.get("danger") is not None and v <= th["danger"]:
            return "Danger", th["danger"]
        if th.get("warning") is not None and v <= th["warning"]:
            return "Warning", th["warning"]
        return "Good", th.get("warning")
    if th is not None and value is None:          # the fab lists the check without a threshold: every found item is Warning (as the viewers do)
        return "Warning", None
    if pmin is not None and value is not None:
        return ("project-FAIL" if value + TOL < pmin else "Good"), pmin
    return "INFO", None


def accepted(item, acc):
    refs = item.get("refs") or []
    if not refs:
        return False
    for a in acc:
        if a.get("check") != item["check"]:
            continue
        lst = a.get("refs") or {}
        names = set(lst) if isinstance(lst, (list, dict)) else set()
        if all(r in names for r in refs):
            return True
    return False


def run(items, thresholds, acc, top=10):
    graded, counts = [], collections.Counter()
    by_ref_used = collections.Counter()
    for it in items:
        g, lim = grade(it["check"], it.get("value"), thresholds)
        ok = g in ("Good", "INFO")
        acc_hit = (not ok) and accepted(it, acc)
        if acc_hit:   # dict form: per-ref budget
            for a in acc:
                if a.get("check") == it["check"] and isinstance(a.get("refs"), dict):
                    for r in it.get("refs") or []:
                        by_ref_used[(it["check"], r)] += 1
                        if by_ref_used[(it["check"], r)] > a["refs"].get(r, 0):
                            acc_hit = False
        graded.append({**it, "grade": g, "limit": lim, "accepted": acc_hit})
        counts[g] += 1
        if acc_hit:
            counts["accepted"] += 1
    open_bad = [g for g in graded if g["grade"] in ("Danger", "Warning", "project-FAIL") and not g["accepted"]]
    L = ["| Check | Danger | Warning | project-FAIL | Good | accepted |", "|---|---|---|---|---|---|"]
    for chk in sorted({g["check"] for g in graded}):
        c = collections.Counter(g["grade"] for g in graded if g["check"] == chk)
        a = sum(1 for g in graded if g["check"] == chk and g["accepted"])
        L.append(f"| {chk} | {c['Danger']} | {c['Warning']} | {c['project-FAIL']} | {c['Good']} | {a} |")
    L += ["", f"Open (not accepted) Danger/Warning/project failures: **{len(open_bad)}**"]
    for g in sorted(open_bad, key=lambda g: (g["grade"] != "Danger", g.get("value") if g.get("value") is not None else 0))[:top]:
        L.append(f"- {g['grade']} {g['check']} value {g.get('value')} (limit {g['limit']}) refs {g.get('refs')} layer {g.get('layer')} at {g.get('xy')}")
    return graded, open_bad, "\n".join(L)


def load_accept(path):
    if not path or not os.path.exists(path):
        return []
    doc = yaml.safe_load(open(path)) or []
    return doc if isinstance(doc, list) else (doc.get("dfm_accepted") or [])


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--items"); ap.add_argument("--thresholds"); ap.add_argument("--accept"); ap.add_argument("--json"); ap.add_argument("--top", type=int, default=10)
    ap.add_argument("--project"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    P = Project.find(arg=a.project)
    th_path = a.thresholds or P.path("dfm_thresholds") or os.path.join(P.root, P.get("dfm.thresholds", "design/dfm_thresholds.json"))
    items_path = a.items or os.path.join(P.root, P.get("dfm.items", "out/dfm_items.json"))
    acc_path = a.accept or (os.path.join(P.root, P.get("dfm.accept")) if P.get("dfm.accept") else None)
    if not os.path.exists(items_path):
        print(f"MISSING: {items_path} — run the project's measurer first (references/fab-dfm.md §3)"); return 1
    thresholds = json.load(open(th_path)) if os.path.exists(th_path) else {"checks": {}}
    graded, open_bad, report = run(json.load(open(items_path)), thresholds, load_accept(acc_path), a.top)
    print(report)
    if a.json:
        json.dump({"items": graded, "open": len(open_bad), "thresholds": os.path.relpath(th_path, P.root)}, open(a.json, "w"), indent=1)
    return 1 if open_bad else 0


def selftest():
    th = {"checks": {"Trace spacing": {"danger": 0.10, "warning": 0.15}, "Fiducial": {"danger": None, "warning": None}}, "project_min": {"Trace width": 0.16}}
    assert grade("Trace spacing", 0.15, th) == ("Warning", 0.15), "EQUAL to the warning threshold is still Warning"
    assert grade("Trace spacing", 0.1549, th)[0] == "Warning", "2-decimal rounding: 0.1549 -> 0.15 -> Warning"
    assert grade("Trace spacing", 0.155, th)[0] == "Good", "0.155 rounds half-up to 0.16 -> Good"
    assert grade("Trace spacing", 0.10, th)[0] == "Danger" and grade("Trace spacing", 0.16, th)[0] == "Good"
    assert grade("Fiducial", None, th)[0] == "Warning", "a listed check without thresholds grades every item Warning"
    assert grade("Trace width", 0.15999, th)[0] == "Good", "project rule tolerance 5e-4"
    assert grade("Trace width", 0.15, th)[0] == "project-FAIL" and grade("Unknown", 1, th)[0] == "INFO"
    items = [{"check": "Trace spacing", "value": 0.15, "refs": ["R1", "C1"]}, {"check": "Trace spacing", "value": 0.12, "refs": []},
             {"check": "Trace spacing", "value": 0.15, "refs": ["R2"]}, {"check": "Trace spacing", "value": 0.15, "refs": ["R2"]}]
    acc = [{"check": "Trace spacing", "refs": ["R1"], "reason": "one of the pair only"}, {"check": "Trace spacing", "refs": {"R2": 1}, "reason": "budget 1"}]
    graded, open_bad, rep = run(items, th, acc)
    assert not graded[0]["accepted"], "a pair item needs BOTH refs listed"
    assert not graded[1]["accepted"], "an item without refs cannot be accepted"
    assert graded[2]["accepted"] and not graded[3]["accepted"], "dict form: the per-ref count is a budget"
    assert len(open_bad) == 3 and "Open (not accepted) Danger/Warning/project failures: **3**" in rep, rep
    d = tempfile.mkdtemp()
    json.dump(items, open(f"{d}/i.json", "w")); json.dump(th, open(f"{d}/t.json", "w"))
    open(f"{d}/project.yaml", "w").write("dfm: {thresholds: t.json, items: i.json}\n")
    sys.argv = ["x", "--project", f"{d}/project.yaml"]
    assert main() == 1
    print("selftest OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
