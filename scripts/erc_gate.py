#!/usr/bin/env python3
"""scripts/erc_gate.py — the ERC gate with a MACHINE-CHECKED accept file instead of a prose waiver table (CLAUDE.md rule 7, SKILL.md §1.2).

  scripts/erc_gate.py out/<board>/erc.json... [--accept design/erc_accept.yaml]
      Reads the CAD's ERC JSON (KiCad: `kicad-cli sch erc --severity-all --format json`; `sheets[].violations[]` with `severity`, `type`,
      `items[].description`). Exit 1 on: any error; any warning no accept entry covers; an accept entry missing a field (type, ref, reason,
      decision, date); a `decision` that is not a row of paths.decisions or is REJECTED / SUPERSEDED; an accept entry that covers nothing (stale);
      a violation `excluded` in the CAD GUI (a hidden waiver — the yaml is the only path). An entry covers a violation when `type` equals the
      violation type and `ref` (a refdes, net or pin text) occurs in one of its item descriptions.
  scripts/erc_gate.py --selftest
Accept file (templates/design/erc_accept.yaml; paths.erc_accept): `accepted: [{type, ref, reason, decision, date}]`.
"""
import argparse, json, os, re, sys

sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project, split_row, decision_status as _decision_status  # noqa: E402

FIELDS = ("type", "ref", "reason", "decision", "date")


def violations(erc):
    for sh in erc.get("sheets", []):
        for v in sh.get("violations", []):
            yield dict(sheet=sh.get("path", "/"), type=v.get("type", "?"), severity=str(v.get("severity", "")).lower(), excluded=bool(v.get("excluded")),
                       items=[str(i.get("description", "")) for i in v.get("items", [])], description=v.get("description", ""))


def decision_status(path):
    """{id: STATUS} of the decision log (project.decision_status, upper-cased)."""
    return {k: v.upper() for k, v in _decision_status(path).items()}


def grade(ercs, accepted, decisions):
    """-> (problems, counts). Pure: no file is read here."""
    bad = []; n_err = n_warn = n_acc = 0; used = [False] * len(accepted)
    for i, a in enumerate(accepted):
        missing = [k for k in FIELDS if not str(a.get(k, "")).strip()]
        if missing:
            bad.append(f"accept entry {i + 1} lacks {', '.join(missing)}: {a}"); used[i] = True; continue
        st = decisions.get(str(a["decision"]))
        if st is None:
            bad.append(f"accept entry {i + 1}: decision {a['decision']} is not a row of the decision log")
        elif st.startswith(("REJECTED", "SUPERSEDED")):
            bad.append(f"accept entry {i + 1}: decision {a['decision']} is {st} — the acceptance fell with it")
    for src, erc in ercs:
        for v in violations(erc):
            where = f"{src} {v['sheet']} {v['type']}: " + " | ".join(v["items"])[:200]
            if v["excluded"]:
                bad.append(f"{where} — excluded in the CAD GUI: a hidden waiver; accept it in the yaml or fix it"); continue
            if v["severity"] == "error":
                n_err += 1; bad.append(f"ERROR {where}"); continue
            if v["severity"] != "warning":
                continue
            n_warn += 1
            hit = [i for i, a in enumerate(accepted) if str(a.get("type")) == v["type"] and any(str(a.get("ref", "")) in it for it in v["items"])]
            if hit:
                n_acc += 1
                for i in hit:
                    used[i] = True
            else:
                bad.append(f"WARNING not accepted: {where}")
    for i, u in enumerate(used):
        if not u:
            bad.append(f"accept entry {i + 1} ({accepted[i].get('type')} {accepted[i].get('ref')}) covers no violation — stale, remove it")
    return bad, dict(errors=n_err, warnings=n_warn, accepted=n_acc)


def selftest():
    erc = {"sheets": [{"path": "/", "violations": [
        {"type": "pin_not_connected", "severity": "warning", "excluded": False, "items": [{"description": "Symbol U1 [LDO] Pin 3 [NC]"}]},
        {"type": "unconnected_wire_endpoint", "severity": "warning", "excluded": False, "items": [{"description": "Wire end at (10, 20)"}]},
        {"type": "pin_to_pin", "severity": "error", "excluded": False, "items": [{"description": "Pins of type Output and Power Out"}]},
        {"type": "label_dangling", "severity": "warning", "excluded": True, "items": [{"description": "Label 'X'"}]}]}]}
    dec = {"CC-012": "APPLIED", "CC-013": "REJECTED"}
    acc = [dict(type="pin_not_connected", ref="U1", reason="NC per datasheet p.4", decision="CC-012", date="2026-01-01")]
    bad, c = grade([("erc.json", erc)], acc, dec)
    assert c == dict(errors=1, warnings=2, accepted=1), c
    kinds = sorted(b.split(" ")[0] for b in bad); assert kinds == ["ERROR", "WARNING", "erc.json"], bad   # error, unaccepted wire end, GUI exclusion
    assert grade([("e", erc)], acc + [dict(type="pin_not_connected", ref="U9", reason="r", decision="CC-012", date="d")], dec)[0][-1].startswith("accept entry 2") and "stale" in grade([("e", erc)], acc + [dict(type="pin_not_connected", ref="U9", reason="r", decision="CC-012", date="d")], dec)[0][-1]
    assert any("lacks reason, date" in b for b in grade([("e", erc)], [dict(type="pin_not_connected", ref="U1", decision="CC-012")], dec)[0])
    assert any("is REJECTED" in b for b in grade([("e", erc)], [dict(acc[0], decision="CC-013")], dec)[0])
    assert any("not a row" in b for b in grade([("e", erc)], [dict(acc[0], decision="CC-099")], dec)[0])
    clean = {"sheets": [{"path": "/", "violations": []}]}
    assert grade([("e", clean)], [], dec) == ([], dict(errors=0, warnings=0, accepted=0))
    import tempfile
    d = tempfile.mkdtemp(prefix="hwfs_erc_"); open(f"{d}/D.md", "w").write("| ID | Date | Status | Topic | P | R |\n|---|---|---|---|---|---|\n| CC-012 | d | **APPLIED (!)** (was: OPEN) | nc pin | p | r |\n")
    assert decision_status(f"{d}/D.md") == {"CC-012": "APPLIED (!)"}
    print("selftest OK (error, unaccepted warning, GUI exclusion, accepted warning, stale entry, missing fields, rejected / unknown decision, clean)")
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("erc", nargs="*"); ap.add_argument("--accept"); ap.add_argument("--project"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if not a.erc:
        ap.error("give one or more ERC JSON files")
    P = Project.find(arg=a.project)
    acc_path = a.accept or P.path("erc_accept")
    accepted = []
    if acc_path and os.path.exists(acc_path):
        import yaml
        accepted = (yaml.safe_load(open(acc_path)) or {}).get("accepted") or []
    ercs = []
    for p in a.erc:
        if not os.path.exists(p):
            print(f"erc_gate: missing {p} — run the CAD's ERC first", file=sys.stderr); return 2
        ercs.append((os.path.relpath(p, P.root), json.load(open(p))))
    bad, c = grade(ercs, accepted, decision_status(P.path("decisions")))
    for b in bad:
        print("ERC GATE:", b)
    print(f"erc gate: {len(ercs)} file(s), {c['errors']} error(s), {c['warnings']} warning(s) of which {c['accepted']} accepted by {os.path.relpath(acc_path, P.root) if acc_path else 'nothing'}, {len(bad)} problem(s)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
