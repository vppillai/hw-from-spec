#!/usr/bin/env python3
"""evals/run_evals.py — run the mechanically checkable part of every eval in evals.json; report the rest as manual.

  evals/run_evals.py [--only ID,ID] [--python PY]
      Each eval may carry `checks: [{name, run, expect_rc?}]`: `run` is a shell snippet executed in a fresh temp dir with $SKILL (this repo),
      $PY and $PYTHON (the interpreter: --python made absolute, else the interpreter running this file) and $T (the temp dir) set.
  evals/run_evals.py --selftest      # evals.json schema: unique ids, prompt / expected_output / assertions / checks (name + run) on every eval A check whose `run` starts with
      `needs-mesh:` is SKIPPED (not failed) when $PY lacks numpy / trimesh. Evals without checks are listed as manual with their assertion count
      (they need an agent run against the prompt and a human reading the assertions). Exit 1 on any failed check.
"""
import argparse, json, os, subprocess, sys, tempfile

HERE = os.path.dirname(os.path.realpath(__file__)); SKILL = os.path.dirname(HERE)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0]); ap.add_argument("--only"); ap.add_argument("--python"); ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    py = os.path.abspath(a.python) if a.python else sys.executable   # checks run with cwd = a temp dir, so a relative --python must be absolutised; default = the interpreter running this file
    mesh = subprocess.run([py, "-c", "import numpy, trimesh, scipy, shapely"], capture_output=True).returncode == 0
    evals = json.load(open(os.path.join(HERE, "evals.json")))["evals"]
    only = set(a.only.split(",")) if a.only else None
    fails = 0; n_mech = n_manual = n_skip = 0
    for e in evals:
        if only and str(e["id"]) not in only:
            continue
        checks = e.get("checks") or []
        if not checks:
            n_manual += 1; print(f"[manual] {e['id']:>2} {e['name']}: {len(e['assertions'])} assertion(s) need an agent run + a reader"); continue
        n_mech += 1
        with tempfile.TemporaryDirectory(prefix="hwfs_eval_") as T:
            for c in checks:
                run = c["run"]
                if run.startswith("needs-mesh:"):
                    run = run[len("needs-mesh:"):].strip()
                    if not mesh:
                        n_skip += 1; print(f"[skip ] {e['id']:>2} {c.get('name', run[:60])}: mesh libraries absent in {py}"); continue
                r = subprocess.run(["bash", "-e", "-o", "pipefail", "-c", run], cwd=T, env=dict(os.environ, SKILL=SKILL, PY=py, PYTHON=py, T=T), capture_output=True, text=True)
                ok = r.returncode == c.get("expect_rc", 0)
                fails += not ok
                print(f"[{'PASS' if ok else 'FAIL'} ] {e['id']:>2} {c.get('name', run[:60])}" + ("" if ok else f"\n        rc {r.returncode}: {(r.stdout + r.stderr).strip()[-600:]}"))
    print(f"\nevals: {n_mech} with mechanical checks ({fails} failed check(s), {n_skip} skipped), {n_manual} manual — the manual ones are graded by a human after an agent run")
    return 1 if fails else 0


def selftest():
    E = json.load(open(os.path.join(HERE, "evals.json")))["evals"]
    ids = [e["id"] for e in E]; assert len(ids) == len(set(ids)) and ids == sorted(ids), "ids unique and ordered"
    for e in E:
        assert e.get("prompt") and e.get("expected_output") and e.get("assertions") and e.get("checks"), f"eval {e.get('id')} incomplete"
        assert all(c.get("name") and c.get("run") for c in e["checks"]), f"eval {e['id']}: a check without name / run"
    print(f"selftest OK ({len(E)} evals, every one with prompt / expected_output / assertions / checks)"); return 0


if __name__ == "__main__":
    sys.exit(main())
