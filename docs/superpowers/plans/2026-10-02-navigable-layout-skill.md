# Navigable Layout — Skill Release (0.11.0) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the numbered lifecycle tree of the spec the skill's default project layout, with revision-named folders, a kit-of-record shape, the five `00-now/` pages and a generalised path mover, released as hw-from-spec 0.11.0 with the smoke, evals and both lints green.

**Architecture:** Every path the skill names is a `paths:` key whose default lives in one dict (`scripts/project.py` `DEFAULTS["paths"]`); the templates, references, SKILL.md and the smoke spell the same defaults. Folder identity moves from hashes to `project.revision` (`rev0`), the hash stays inside each folder as a record. A new generator `scripts/now_pages.py` derives the five answer pages from the logs and the kits and is gated like every other generated document. The migration of an existing project is the existing `scripts/reorg_paths.py` fed by a `reorg:` block, documented with the originating project's move table as the worked example.

**Tech Stack:** Python 3.11+ (pyyaml only for the generic scripts), bash ≥ 3.2 for the smoke, git. No new dependencies.

**Spec:** `docs/superpowers/specs/2026-10-02-navigable-layout-design.md`

## Global Constraints

- Top-level folders and numbers exactly: `00-now 10-spec 20-design 30-board 40-case 50-kits 60-orders 70-release 80-reviews 90-log`; `gen/ scripts/ tools/ lib/ Makefile CLAUDE.md` unchanged.
- No hash and no date as a folder name at the top of any tree; revisions are `rev0`, kits are their print target; `40-case/dfm_validation/` is the one place a hash is a name.
- Scope tags: `30-board/` is `{{ee,both}}`; `40-case/`, `50-kits/` are `{{mech,both}}`.
- Records are relocated, never re-written: no record md5, engine or rule-set version changes in this release.
- The skill text is generic: `scripts/generic_lint.py` and `scripts/doc_voice_lint.py` at 0 hits; the originating project's names appear only in CHANGELOG, `docs/retro/`, `docs/reviews/`, `docs/superpowers/`.
- Every new script: executable, shebang, `--selftest` (temp dir only), `--check` where it writes, exit 0 / 1 / 2, in `smoke/run_smoke.sh` and in the template's `gates.adopt`.
- Version 0.11.0 in `SKILL.md`, `README.md`, CHANGELOG current state and a `## 0.11.0` entry; tag `v0.11.0` after the double-blind review.
- Heavy work only through `scripts/jobs.sh`; at most 3 writing agents at once; commit after every task.

## Review Focus

1. A project whose `project.yaml` sets no `paths:` at all must scaffold and run the whole smoke chain on the new defaults — Task 1's selftest asserts every default key resolves under the numbered tree, Task 7 runs the chain.
2. A project that KEEPS the old layout (an override of every `paths:` key to the old `docs/...` values) must still pass `--check` everywhere — Task 1's selftest sets the old values and asserts `P.path()` returns them unchanged (no hard-coded new path survives in a script).
3. `now_pages.py` on an ee-only project (no kits, no case) must write `WHAT_TO_PRINT.md` with a "nothing to print in this scope" line, not crash — Task 4 selftest.
4. `now_pages.py` with an empty GATES table, no OPEN rows and no arrival yaml must write all five pages (each reading "nothing") — Task 4 selftest.
5. `reorg_paths.py` moving a whole frozen directory (`docs/quotes/<date>/…` → `60-orders/quotes/<date>/…`) must move the files without rewriting their content and `--map` must answer the old path — Task 6 selftest.

---

### Task 1: One place for the layout — `DEFAULTS["paths"]`, `project.revision`, `Project.rev()`

**Files:**
- Modify: `scripts/project.py:33-47` (DEFAULTS), `:95-110` (`path()`, `record_md5()`), the `selftest()` body
- Modify: `templates/project.yaml` (`project:` block gains `revision`; a commented `paths:` block listing every default)

**Interfaces:**
- Produces: `DEFAULTS["paths"]` keys (used by every later task): `now_dir=00-now`, `spec_dir=10-spec`, `design_dir=20-design`, `board_dir=30-board`, `layout_dir=30-board/layout`, `fab_dir=30-board/fab`, `case_dir=40-case`, `kits_dir=50-kits`, `orders_dir=60-orders`, `quotes_dir=60-orders/quotes`, `release_dir=70-release`, `reports_dir=70-release/reports`, `collateral_dir=70-release/collateral`, `marketing_dir=70-release/marketing`, `production_dir=70-release`, `reviews_dir=80-reviews`, `log_dir=90-log`, `decisions=90-log/DECISIONS.md`, `status=90-log/STATUS.md`, `gates=90-log/GATES.md`, `blockers=90-log/BLOCKERS.md`, `known_issues=90-log/KNOWN_ISSUES.md`, `learnings=90-log/LEARNINGS_LOG.md`, `env=90-log/ENV.md`, `traceability_out=90-log/TRACEABILITY.md`, `traceability_yaml=20-design/traceability.yaml`, `erc_accept=20-design/erc_accept.yaml`, `test_plan=20-design/TEST_PLAN.md`, `kickoff_answers=10-spec/KICKOFF_ANSWERS.md`, `spec=10-spec/SPEC.md`, `datasheet_notes=10-spec/datasheet_notes`, `parts_verification=60-orders/PARTS_VERIFICATION.md`, `procurement=60-orders/PROCUREMENT.md`, `mech_record=40-case/*/parts/*.stl`, `reorg_rewrites=80-reviews/REORG_REWRITES.txt`.
- Produces: `Project.rev()` → `str` (`project.revision`, default `"rev0"`); `Project.path(key)` unchanged signature.

- [ ] **Step 1: Write the failing selftest assertions** (append inside `selftest()` after the existing `P.get("ids.agent_prefix")` assertion):

```python
    # 0.11.0 layout: every default path sits under the numbered tree; an explicit old-layout override wins unchanged; rev defaults to rev0
    P = Project.__new__(Project); P.cfg = {"project": {"name": "t"}}; P.root = "/tmp"
    top = {"00-now", "10-spec", "20-design", "30-board", "40-case", "50-kits", "60-orders", "70-release", "80-reviews", "90-log"}
    for k, v in DEFAULTS["paths"].items():
        assert v.split("/")[0] in top, (k, v)
    assert P.path("decisions") == "90-log/DECISIONS.md" and P.path("mech_record") == "40-case/*/parts/*.stl" and P.rev() == "rev0"
    P.cfg["paths"] = {"decisions": "docs/governance/DECISIONS.md"}; P.cfg["project"]["revision"] = "rev1"
    assert P.path("decisions") == "docs/governance/DECISIONS.md" and P.rev() == "rev1", "an explicit path / revision wins"
```

- [ ] **Step 2: Run the selftest, expect FAIL** — `Run: .venv/bin/python scripts/project.py --selftest` — Expected: `AssertionError` on the first `top` check (defaults still `docs/...`) or `AttributeError: rev`.

- [ ] **Step 3: Implement** — replace the `"paths"` dict in `DEFAULTS` with the keys listed under Interfaces (exact values), and add after `path()`:

```python
    def rev(self):
        """The project revision that names folders (`project.revision`, default rev0); the record hash lives INSIDE the folder."""
        return str(self.get("project.revision", "rev0"))
```

- [ ] **Step 4: Run the selftest, expect PASS** — `Run: .venv/bin/python scripts/project.py --selftest` — Expected: `selftest OK (...)`.

- [ ] **Step 5: Template** — in `templates/project.yaml` add `  revision: rev0                              # names the fab package, cut, collateral and marketing folders (the hash is inside each: board_id.txt, RENDERS.md, MANIFEST)` after `scope:`; add a commented `paths:` block listing every default from Interfaces with one comment per line, headed `# paths:  # the layout of record (references/project-yaml.md §Layout); every key below is a DEFAULT — set a key only to deviate`.

- [ ] **Step 6: Commit** — `git add scripts/project.py templates/project.yaml && git commit -m "layout: DEFAULTS paths under the numbered tree, project.revision + Project.rev()"`.

### Task 2: Revision-named folders — collateral, fab package, production cut

**Files:**
- Modify: `scripts/collect_renders.py:30-40`, `scripts/release_report.py:101-130,180-190` + its selftest fixtures (`out/fab/2026-01-01_x` → `30-board/fab/rev0`), `scripts/production_cut.py` (`{rev}` placeholder, `package_root` default), `templates/production_cut.yaml:2-12,26`
- Test: each script's `--selftest`

**Interfaces:**
- Consumes: `Project.rev()`, `P.path("collateral_dir")`, `P.path("fab_dir")`, `P.path("production_dir")`.
- Produces: collateral at `<collateral_dir>/<rev>/renders/RENDERS.md` whose first table row carries `record md5`; fab package at `<fab_dir>/<rev>/board_id.txt` (selection stays BY MD5 inside `board_id.txt`, folder name is only a name); cut at `<production_dir>/<rev>/` with `{rev}` and `{md5}` both expandable in `production_cut.yaml`.

- [ ] **Step 1: Failing tests** — in `collect_renders.py` selftest assert the output path is `.../70-release/collateral/rev0/renders/RENDERS.md` and that the file contains `md5 \`<8 hex>\``; in `release_report.py` selftest rename the fixture package dir to `30-board/fab/rev0` and assert `pkg_for_board` still finds it by md5 and that a second dir `30-board/fab/rev1` with another md5 is NOT chosen; in `production_cut.py` selftest assert `{rev}` expands and the package root is `70-release/rev0`.
- [ ] **Step 2: Run the three selftests, expect FAIL** on the new paths.
- [ ] **Step 3: Implement** — `collect_renders.py`: `out_dir = os.path.join(P.path("collateral_dir"), P.rev(), "renders")`; write `| record | md5 \`{md5[:8]}\` |` as the first row of RENDERS.md. `release_report.py`: `rel = f"{P.path('collateral_dir')}/{P.rev()}/renders/RENDERS.md"`; `pkg_for_board` unchanged logic (glob `fab_dir/*/board_id.txt`, pick the md5 match). `production_cut.py`: `self.vars["rev"] = P.rev()`; default `package_root` from `P.path("production_dir")`; folder `f"{package_root}/{rev}"`. `templates/production_cut.yaml`: header line 2 names `{rev}`; `package_root: 70-release  # -> 70-release/{rev}/`; collateral path `70-release/collateral/{rev}/…`.
- [ ] **Step 4: Run the three selftests, expect PASS.**
- [ ] **Step 5: Commit** — `git commit -am "layout: revision-named collateral / fab package / cut folders; the hash stays inside"`.

### Task 3: The literal sweep — every path the skill spells

**Files:**
- Modify: every file under `SKILL.md README.md references/ templates/ scripts/ smoke/ evals/ workflows/` that carries an old literal (61 files today); NOT `CHANGELOG.md`, `docs/retro/`, `docs/reviews/`, `docs/superpowers/`.
- Create: `scripts/layout_sweep.py` (one-off, deleted at the end of the task; kept out of the tree)

**Interfaces:**
- Consumes: the mapping below.
- Produces: zero occurrences of the old literals in the swept set (checked by the grep in Step 4).

Mapping (longest first; applied to word-bounded literals as `reorg_paths.py` does):

| old | new |
|---|---|
| `docs/governance/KICKOFF_ANSWERS.md` | `10-spec/KICKOFF_ANSWERS.md` |
| `docs/governance/` | `90-log/` |
| `docs/design/` | `20-design/` |
| `design/` (yaml sources: `design/erc_accept.yaml`, `design/traceability.yaml`, `design/arrival_checklist.yaml`, `design/dfm_processes.yaml`, `design/case.yaml`, `design/board.yaml`, `design/parts.yaml`) | `20-design/` |
| `docs/parts/` | `60-orders/` |
| `docs/production/ARRIVAL_CHECKLIST.md` | `60-orders/ARRIVAL_CHECKLIST_rev0.md` (template default; the yaml `arrival_checklist.out` key carries it) |
| `docs/production/<md5-8>/` and `docs/production/{md5}/` | `70-release/{rev}/` |
| `docs/production/` (order sheets, quotes index, fab rules) | `60-orders/` |
| `docs/quotes/` | `60-orders/quotes/` |
| `docs/release/collateral/` | `70-release/collateral/` ; `/{md5}` or `/<md5-8>` after it → `/{rev}` |
| `docs/release/marketing/` | `70-release/marketing/` |
| `docs/release/` (the two design reports, RELEASE_NOTES) | `70-release/reports/` |
| `docs/reviews/` | `80-reviews/` |
| `docs/datasheet_notes/` | `10-spec/datasheet_notes/` |
| `docs/spec_sections/` | `10-spec/spec_sections/` |
| `SPEC.md` (root), `FINDINGS.md` (root) | `10-spec/SPEC.md`, `10-spec/FINDINGS.md` |
| `out/mechanical/case/*/stl/*.stl` | `40-case/*/parts/*.stl` |
| `out/mechanical/case/<ver>/stl/` , `out/mechanical/case/{CASE_VERSION}/` | `40-case/<set>/parts/` , `40-case/<set>/` |
| `out/mechanical/case/<ver>/census` , `/dfm` | `40-case/<set>/checks/census` , `40-case/<set>/checks/dfm` |
| `out/mechanical/` (board mesh, provenance) | `40-case/board_mesh/` |
| `out/fab/` | `30-board/fab/` |
| `out/<board>/` , `out/layout/` , `out/drawings/` | `30-board/layout/` , `30-board/layout/` , `30-board/layout/drawings/` |
| `kicad/` | `30-board/kicad/` |

- [ ] **Step 1: Write the sweep script** in the scratchpad (not the repo): a Python script that walks the swept set, applies the table with the `reorg_paths.py` rewrite rule (`(?<![\w/-])old(?!\w)`), and prints per-file counts; run with `--plan` first.
- [ ] **Step 2: Run `--plan`**, read the per-file counts, then apply.
- [ ] **Step 3: Hand-fix the semantic splits** the table cannot decide: `docs/production/` lines that meant the CUT (`{md5}`, `MANIFEST`, `records/`, `pdf/`) → `70-release/{rev}/`; lines that meant ORDER SHEETS / QUOTES INDEX / FAB RULES → `60-orders/`. Grep: `grep -rn '60-orders/' SKILL.md references templates | grep -i 'manifest\|records/\|pdf/\|manual\|sop'` must return nothing.
- [ ] **Step 4: Verify no old literal remains** — `grep -rnE '\b(docs/(governance|design|parts|production|quotes|release|reviews|datasheet_notes|spec_sections)|out/(mechanical|fab)|^kicad/)' SKILL.md README.md references templates scripts smoke evals workflows` — Expected: no output. Run every `scripts/*.py --selftest` (fixtures were swept too) — Expected: all OK. Run both lints — Expected: 0 hits.
- [ ] **Step 5: Commit** — `git add -A && git commit -m "layout: every path the skill spells moves to the numbered tree (sweep table in the plan)"`.

### Task 4: `scripts/now_pages.py` — the five answer pages

**Files:**
- Create: `scripts/now_pages.py`
- Modify: `templates/project.yaml` (`gates.adopt` gains `"$PY scripts/now_pages.py --check"`), `references/print-kit.md` (sidecar keys the pages read), `smoke/run_smoke.sh` (step 5e), `evals/evals.json` (eval 18)

**Interfaces:**
- Consumes: `P.path("gates"|"decisions"|"status"|"blockers"|"kits_dir"|"procurement"|"now_dir")`, `P.get("arrival_checklist.yaml")`, `P.rev()`, `P.record_md5()`; kit sidecars `<kits_dir>/<kit>/plates/<plate>.3mf.json` with keys `print_time_s` (int), `filament_g` (float), `objects` (list), optional `filament_changes` (int), `proves` (str), `order` (int).
- Produces: `00-now/WHERE_THINGS_STAND.md`, `BLOCKED_ON_OWNER.md`, `WHAT_TO_PRINT.md`, `WHAT_TO_ORDER.md`, `WHAT_TO_CHECK_ON_ARRIVAL.md`; `--check` exit 1 when any differs from a regenerate (the `Generated` line excluded, as `release_report.py` VOLATILE does); `--selftest`.

- [ ] **Step 1: Write the selftest first** (temp project): GATES with one reached and one open gate; DECISIONS with one `**OPEN** (owner)` row and one APPLIED row; STATUS with three dated lines; BLOCKERS with one row; an arrival yaml with one TODO row and one DONE; a kit `50-kits/k/plates/p.3mf.json` `{"print_time_s": 3600, "filament_g": 12.5, "objects": ["a"], "filament_changes": 2, "proves": "fit", "order": 1}` and a `START_HERE.md`; `60-orders/PROCUREMENT.md` with one row whose order column is empty. Assert: five files exist; WHERE_THINGS_STAND has the open gate and the three STATUS lines in newest-first order and is under 60 lines; BLOCKED_ON_OWNER names the OPEN row id and the TODO arrival row and not the APPLIED row; WHAT_TO_PRINT has one row `k | p | 60 min | 12.5 g | 2 changes | fit`; WHAT_TO_ORDER has the unordered procurement row; WHAT_TO_CHECK_ON_ARRIVAL has the TODO row and not the DONE row; `--check` exits 0, then after appending a line to BLOCKED_ON_OWNER exits 1; an ee-only project with no kits writes `WHAT_TO_PRINT.md` containing `nothing to print in this scope`; an empty project (empty GATES table, no rows, no yaml) writes all five with `nothing`.
- [ ] **Step 2: Run, expect FAIL** (`FileNotFoundError` / missing script).
- [ ] **Step 3: Implement** `scripts/now_pages.py`:

```python
#!/usr/bin/env python3
"""scripts/now_pages.py — the five pages of 00-now/: each answers its own file name, from the logs and the kits only; `--check` compares a
regenerate (the Generated line excluded) with the files on disk; `--selftest` in a temp dir. Never hand-edited (a stale page fails gates.adopt)."""
import glob, json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.realpath(__file__)))
from project import Project  # noqa: E402

VOLATILE = re.compile(r"^Generated .*$", re.M)
PAGES = ["WHERE_THINGS_STAND.md", "BLOCKED_ON_OWNER.md", "WHAT_TO_PRINT.md", "WHAT_TO_ORDER.md", "WHAT_TO_CHECK_ON_ARRIVAL.md"]

def rows(path):
    """markdown table rows -> list of cell lists (header and rule rows skipped)"""
    if not os.path.exists(path): return []
    out = []
    for l in open(path, encoding="utf-8"):
        if l.startswith("|") and not re.match(r"^\|\s*-", l):
            out.append([c.strip() for c in l.strip().strip("|").split("|")])
    return out[1:] if out else []

def head(title, p):
    return [f"# {title}", "", "GENERATED by `scripts/now_pages.py` from the records — do not edit; regenerate.", "Generated " + time.strftime("%Y-%m-%d %H:%M"), ""]

def where(P):
    L = head("Where things stand", P)
    lab, md5 = P.record_md5(); L += [f"- Revision **{P.rev()}**; {lab} md5 `{(md5 or 'MISSING')[:8]}`", ""]
    g = [r for r in rows(P.path("gates")) if len(r) >= 4]
    L += ["## Gates", ""] + ([f"- {r[0].strip('*')}: {'approved — ' + r[3] if r[3] and 'not yet' not in r[3] else 'open'}" for r in g] or ["- nothing"]) + [""]
    st = [l.rstrip() for l in open(P.path("status"), encoding="utf-8") if re.match(r"^- \*?\*?\d{4}-\d\d-\d\d", l)] if os.path.exists(P.path("status")) else []
    L += ["## Landed (newest first)", ""] + (sorted(st, reverse=True)[:3] or ["- nothing"]) + [""]
    b = [r for r in rows(P.path("blockers")) if r and r[0]]
    L += ["## Blockers", ""] + ([f"- {r[0]}: {r[1] if len(r) > 1 else ''}" for r in b] or ["- nothing"])
    return "\n".join(L) + "\n"

def blocked(P):
    L = head("Blocked on the owner", P)
    dec = [r for r in rows(P.path("decisions")) if len(r) > 2 and "OPEN" in r[2] and "owner" in r[2].lower()]
    L += ["## Decisions waiting for the owner", ""] + ([f"- {r[0].strip('*')}: {r[3] if len(r) > 3 else ''} — answer in `{P.path('decisions')}`" for r in dec] or ["- nothing"]) + [""]
    ac = arrival_rows(P); own = [r for r in ac if r.get("status", "").upper().startswith("TODO") and "owner" in (r.get("item", "") + r.get("id", "")).lower()]
    L += ["## Arrival rows the owner closes", ""] + ([f"- {r['id']}: {r['item']}" for r in own] or ["- nothing"])
    return "\n".join(L) + "\n"

def arrival_rows(P):
    y = P.get("arrival_checklist.yaml")
    if not y or not os.path.exists(y): return []
    import yaml
    d = yaml.safe_load(open(y)) or {}; out = []
    def walk(x):
        if isinstance(x, dict):
            if "id" in x and "item" in x: out.append(x)
            for v in x.values(): walk(v)
        elif isinstance(x, list):
            for v in x: walk(v)
    walk(d); return out

def to_print(P):
    L = head("What to print", P)
    kd = P.path("kits_dir"); plates = sorted(glob.glob(f"{kd}/*/plates/*.3mf.json"))
    if P.get("project.scope") == "ee" or not plates:
        return "\n".join(L + ["- nothing to print in this scope" if P.get("project.scope") == "ee" else f"- nothing: no plate sidecar under `{kd}/*/plates/`"]) + "\n"
    L += ["| kit | plate | time | filament | changes | proves | start |", "|---|---|---|---|---|---|---|"]
    items = []
    for p in plates:
        s = json.load(open(p)); kit = p.split(os.sep)[-3]; plate = os.path.basename(p)[:-9]
        items.append((s.get("order", 99), kit, plate, s))
    for _, kit, plate, s in sorted(items):
        L.append(f"| {kit} | {plate} | {int(s.get('print_time_s', 0)) // 60} min | {s.get('filament_g', 0)} g | {s.get('filament_changes', 0)} changes | {s.get('proves', '')} | `{kd}/{kit}/START_HERE.md` |")
    return "\n".join(L) + "\n"

def to_order(P):
    L = head("What to order", P)
    pr = rows(P.path("procurement")); hdr = rows_header(P.path("procurement"))
    oi = next((i for i, h in enumerate(hdr) if "order" in h.lower()), None)
    todo = [r for r in pr if oi is not None and len(r) > oi and not r[oi]] if oi is not None else []
    L += ["## Not yet ordered", ""] + ([f"- {' | '.join(r[:3])}" for r in todo] or ["- nothing"])
    return "\n".join(L) + "\n"

def rows_header(path):
    if not os.path.exists(path): return []
    for l in open(path, encoding="utf-8"):
        if l.startswith("|"): return [c.strip() for c in l.strip().strip("|").split("|")]
    return []

def to_check(P):
    L = head("What to check on arrival", P)
    ac = [r for r in arrival_rows(P) if not str(r.get("status", "")).upper().startswith(("DONE", "N/A", "APPLIED"))]
    L += ([f"- {r['id']}: {r['item']} — {r.get('how', '')}" for r in ac] or ["- nothing"])
    return "\n".join(L) + "\n"

def render(P):
    return dict(zip(PAGES, [where(P), blocked(P), to_print(P), to_order(P), to_check(P)]))

def main(argv):
    if "--selftest" in argv: return selftest()
    P = Project.find(); os.chdir(P.root); out = P.path("now_dir"); pages = render(P)
    if "--check" in argv:
        bad = [n for n, t in pages.items() if not os.path.exists(f"{out}/{n}") or VOLATILE.sub("", open(f"{out}/{n}").read()) != VOLATILE.sub("", t)]
        for n in bad: print(f"STALE: {out}/{n} differs from scripts/now_pages.py output — run scripts/now_pages.py")
        return 1 if bad else (print(f"OK: {out}/ up to date") or 0)
    os.makedirs(out, exist_ok=True)
    for n, t in pages.items(): open(f"{out}/{n}", "w", encoding="utf-8").write(t)
    print(f"{out}/ written ({len(pages)} pages)"); return 0
```

  plus the `selftest()` from Step 1 (temp dir, `Project` built from a written `project.yaml`, `os.chdir`), and `if __name__ == "__main__": sys.exit(main(sys.argv))`.

- [ ] **Step 4: Run the selftest, expect PASS.** `chmod +x scripts/now_pages.py`.
- [ ] **Step 5: Wire it** — `templates/project.yaml` `gates.adopt`: add `- "$PY scripts/now_pages.py --check"` after the arrival checklist line; `smoke/run_smoke.sh`: after step 5d add `say "5e now pages (the five answers of 00-now/; --check in gates)"; $PY scripts/now_pages.py; $PY scripts/now_pages.py --check; grep -q '^# Blocked on the owner' 00-now/BLOCKED_ON_OWNER.md || { echo "FAIL: now pages"; exit 1; }` and add `$PY scripts/now_pages.py --check` to step 7; `references/print-kit.md` §4: the sidecar keys (`print_time_s`, `filament_g`, `objects`, optional `filament_changes`, `proves`, `order`) and that `WHAT_TO_PRINT.md` is derived from them; `evals/evals.json` eval 18 "a cold reader opens 00-now/" with checks `test -x "$SKILL"/scripts/now_pages.py && "$PY" "$SKILL"/scripts/now_pages.py --selftest >/dev/null` and `grep -q '^00-now/' "$SKILL"/references/project-yaml.md`.
- [ ] **Step 6: Commit** — `git add -A && git commit -m "now_pages: the five answers of 00-now/ generated from the logs and kits, gated"`.

### Task 5: The kit of record and the `40-case/` set shape in the references

**Files:**
- Modify: `references/print-kit.md` (§1 the kit folder; §4 sidecars), `references/case-pipeline.md` (Chain: parts/ checks/ pictures/ build/; the set is named for its print target), `references/dfm-printed-enclosure.md` §7 (census / DFM records under `checks/`), `references/release-and-cut.md` (cut at `70-release/<rev>/`, collateral `<rev>`), `references/project-yaml.md` §Layout (the tree of the spec, verbatim, with scope tags and the rules), `templates/CLAUDE.md` (the layout paragraph + rule 11 path), `templates/ci/Makefile` (targets `case`, `slice`, `renders` paths), `SKILL.md` §2 / §8 / §10 (kit hand-over at `50-kits/<kit>/START_HERE.md`; the mirror `~/Downloads/<project>_kits/<kit>/`; `SUPERSEDED.md`), `templates/.gitignore` (create: `40-case/*/build/`)

**Interfaces:**
- Consumes: the tree of Task 1; the sidecar keys of Task 4.
- Produces: the written layout of record every later project scaffolds from.

- [ ] **Step 1: Failing check** — a grep the smoke will carry (add to `smoke/run_smoke.sh` section 0): `grep -q '^00-now/' "$SKILL/references/project-yaml.md" && grep -q '50-kits/<kit>/START_HERE.md' "$SKILL/SKILL.md" && grep -q '40-case/\*/build/' "$SKILL/templates/.gitignore" || { echo "FAIL: the layout of record is not written where the spec puts it"; exit 1; }` — run the smoke's section 0 alone (`bash -n` then the grep by hand) — Expected: FAIL.
- [ ] **Step 2: Write the texts** — §Layout = the spec §2 tree plus the four rules of spec §1 as four bullets; print-kit §1 = the `50-kits/<kit>/` shape (START_HERE at the root, `plates/ parts/ sheets/`), the mirror path, the tombstone rule, "one current kit per target, no version in the name"; case-pipeline Chain = `40-case/<set>/{parts,checks,pictures,build}` and "a set is named for its print target"; the CLAUDE.md template paragraph reads: "The tree is the navigation: `00-now/` answers where things stand, what is blocked on you, what to print, what to order, what to check on arrival; `10-spec` → `90-log` follow the life of the project (references/project-yaml.md §Layout)."
- [ ] **Step 3: Run the grep, expect PASS**; both lints 0.
- [ ] **Step 4: Commit** — `git add -A && git commit -m "layout: the kit of record, the case set shape and the tree of record written where the spec puts them"`.

### Task 6: `reorg_paths.py` — whole-directory moves, frozen folders, the worked example

**Files:**
- Modify: `scripts/reorg_paths.py` (selftest + any gap found), `references/project-yaml.md` `reorg:` section (the worked example = the originating project's move table of spec §2, generic names), `templates/project.yaml` (`reorg:` commented block with `moves:`, `frozen:`, `allow_missing:`, `gitignore:` keys)

**Interfaces:**
- Consumes: `reorg.moves {old: new}` (file or directory), `reorg.frozen [dir, …]`, `reorg.allow_missing [regex, …]`, `reorg.rewrites_record`.
- Produces: `--apply` moves a directory key as a whole (`git mv dir newdir`), rewrites literals under it in non-frozen text, leaves frozen content byte-identical; `--map` answers `old/sub/file` → `new/sub/file`.

- [ ] **Step 1: Failing selftest cases** — in `selftest()`: a fixture with `docs/quotes/2026-01-01/mail.txt` (content `see docs/quotes/2026-01-01/mail.txt`) and `reorg: {moves: {docs/quotes: 60-orders/quotes, docs/governance/DECISIONS.md: 90-log/DECISIONS.md}, frozen: [docs/quotes]}`; after `--apply` assert the file is at `60-orders/quotes/2026-01-01/mail.txt` with content UNCHANGED, DECISIONS moved and a reference in another file rewritten, `--map docs/quotes/2026-01-01/mail.txt` prints the new path, `--proof` passes.
- [ ] **Step 2: Run, expect FAIL** wherever the implementation does not yet move directories or map sub-paths (if it already passes, keep the cases and go to Step 4).
- [ ] **Step 3: Implement the gap** (directory `git mv`, frozen exclusion by prefix after the move, `--map` longest-prefix match).
- [ ] **Step 4: Run, expect PASS.**
- [ ] **Step 5: Reference + template** — the `reorg:` section carries the spec §2 mapping as the worked example (generic names: `docs/governance → 90-log`, …); the template's commented block shows `moves`, `frozen: [60-orders/quotes, 70-release/*/records]`, `allow_missing`, `gitignore: [40-case/*/build/]`.
- [ ] **Step 6: Commit** — `git add -A && git commit -m "reorg_paths: whole-directory moves with frozen content, --map for sub-paths, the migration worked example"`.

### Task 7: Smoke, evals, version, changelog

**Files:**
- Modify: `smoke/run_smoke.sh` (every fixture path: `docs/governance/GATES.md` → `90-log/GATES.md`, `out/mechanical/case/v1/stl` → `40-case/vendor_case/parts`, `out/fab/2026-01-03_<md5>` → `30-board/fab/rev0`, `docs/release/PCB_DESIGN_REPORT.md` → `70-release/reports/PCB_DESIGN_REPORT.md`, `docs/production/ARRIVAL_CHECKLIST.md` → `60-orders/ARRIVAL_CHECKLIST_rev0.md`, the mech scope block, step 10), `evals/evals.json` (paths in checks), `SKILL.md` (`version: 0.11.0`), `README.md` (version line; Quick start paths), `CHANGELOG.md` (current state 0.11.0: the layout; `## 0.11.0` entry: tree, revision names, now pages, kit of record, set shape, reorg worked example, the sweep)

- [ ] **Step 1: Run the smoke, expect FAIL** on the first old fixture path (`Run: scripts/jobs.sh -- smoke/run_smoke.sh`).
- [ ] **Step 2: Fix every fixture path** per the table in Task 3; re-run until `SMOKE OK` with the mesh libraries; then on a pyyaml-only venv (`uv venv .venv_nomesh && uv pip install pyyaml`, symlink as `.venv` in a copy of the tree) — Expected: `SMOKE OK` twice.
- [ ] **Step 3: Evals** — `.venv/bin/python evals/run_evals.py --python .venv/bin/python` — Expected: 18 with mechanical checks, 0 failed.
- [ ] **Step 4: Version + CHANGELOG** as listed; both lints 0.
- [ ] **Step 5: Commit** — `git add -A && git commit -m "0.11.0: the navigable layout is the default (numbered tree, revision names, 00-now pages, kit of record, set shape, reorg worked example)"`.

### Task 8: Double-blind review, fixes, tag

**Files:**
- Create: `docs/reviews/blind_review_0.11.0_A.md`, `docs/reviews/blind_review_0.11.0_B.md`, `docs/reviews/blind_review_0.11.0_verified.md`; `docs/reviews/INDEX.md` rows

**Interfaces:**
- Consumes: the committed HEAD of Task 7 (`git archive HEAD` → a scratch tree each reviewer gets), the checklist below; reviewers never see each other or this plan.
- Produces: a verifier table (CONFIRMED / ALREADY DECIDED / REFUTED / PARTLY) and the fixes; tag `v0.11.0`.

Checklist handed to both reviewers (and nothing else): (1) scaffold a `both` project from the templates and, without reading any README, find where things stand, what to print, what to order and the hand-over for a technician — report each path you opened and every dead end; (2) every path spelled in SKILL.md, the references and the templates exists in the scaffolded tree or is a documented key; (3) no hash or date names a folder at the top of any tree; (4) ee-only and mech-only scaffolds carry only their stages; (5) the smoke and selftests pass on a fresh clone with a pyyaml-only venv; (6) list any rule that now lives in two places.

- [ ] **Step 1: Dispatch two reviewers** (Opus 5.5, `Agent` tool, each with its own worktree of HEAD, the checklist, a `--no-mesh` venv recipe; "artefact + checklist only") in parallel; a third agent as verifier reads both reports plus the spec and the records and classifies every finding.
- [ ] **Step 2: Apply CONFIRMED findings** as tasks in this plan's style (test, fail, fix, pass, commit); REFUTED ones get one line each in the verifier file.
- [ ] **Step 3: Re-run** smoke (both venvs), evals, lints — Expected: all green.
- [ ] **Step 4: Tag and push** — `git tag -a v0.11.0 -m "0.11.0: navigable project layout" && git push origin main v0.11.0`.

---

## Self-review (run before handing off)

- Spec coverage: §1 rules → Task 5 (written) and Task 1 (defaults); §2 tree → Tasks 1, 3, 5, 7; §3 pages → Task 4; §4 kits → Tasks 4, 5; §5 sets → Tasks 3, 5; §6 skill part → Tasks 1–7, project phases → separate plans; §7 acceptance → Tasks 7, 8; §8 decisions → carried in Global Constraints.
- Placeholders: none; every code step carries its code or exact text; the sweep table is explicit.
- Type consistency: `Project.rev()` (Task 1) is what Tasks 2 and 4 call; `P.path("kits_dir")`, `("now_dir")`, `("procurement")` exist in Task 1's key list; sidecar keys in Task 4 and `print-kit.md` match.
- Review Focus: items 1 and 2 → Task 1 selftest + Task 7 chain; 3 and 4 → Task 4 selftest; 5 → Task 6 selftest.
