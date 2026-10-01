# Blind review — hw-from-spec 0.8.0, print DFM (cold-user lens), 2026-09-30

**Setup.** One reviewer sub-agent, persona *"I have a bracket STL and want to know if Xometry MJF will print it — can I run this from the README
alone?"* It received the repo path, the checklist and the skill venv as its interpreter; nothing of the author's reasoning, no git history, no
`docs/retro/`. It built its own bodies (an L-bracket with a 0.6 mm rib, a plate with two Ø4 holes, a free 0.6 × 6 × 60 plate, an inboard rib) and ran
the tool as written. Verdict as received: *"Partly … took about 25 minutes, ~10 working around F4 and ~10 convincing myself F1 was the tool and not
my part."*

## Findings and dispositions

| # | Sev | Finding (reviewer's words, shortened) | Disposition |
|---|---|---|---|
| F1 | BLOCKER | **R fires on every thin wall** incl. a free 0.6 × 6 × 60 plate; `ray_med: Infinity` on every region — the ray origin is nudged OUTSIDE, the first hit is the origin face, discarded as a self-hit → `t_ray = inf` → every W is an R. The selftest never asserted R absent. | **FIXED** — `_rays` nudges INTO the side the ray travels (`pts + sign·n·1e-3`); verified: 0.8 plate ray median 0.799, finite fraction 1.0 (was 0.0). Selftest now asserts R absent + ray ≈ 0.8 on the plate and `flagged == ["W wall"]` on a free 0.6 × 60 rib; the 0.5-root body still flags W + R, root 1.3 still passes. **The same defect is in the source project's `gen/print_dfm.py`** (validated with the ball measure alone; its "FLAG (W, R)" rows are W-only in truth) — reported to the project as an OPEN decision row, not patched silently (CLAUDE.md rule 2). |
| F2 | SHOULD-FIX | The limit column reads `none` for W/R/F/K/P/V/H. | **FIXED** — numeric limits per row (`wall_min 1.0 over >= 10 x t`, `feature_min 0.5 (area >= 5 mm2)`, `neck_max 0.05`, `detail_min 0.8; void_min 0.8 over any 8 mm`, `hole_min 1.5`, …). |
| F3 | SHOULD-FIX | No rule says what to DO; the only remedy presumes a generated body. | **FIXED** — every rule carries a `fix:` (thicken / widen the overlap / stop the taper with a flat / web or part / open the hole / re-orient / resize), printed on FLAG rows and stored in the record; the reference says "CAD or generator". |
| F4 | SHOULD-FIX | The README's literal command fails (`permission denied`, no interpreter, no install path without a project); Quick start begins with `git submodule add`. | **FIXED** — `chmod +x` on both new scripts; a no-project block under Quick start: clone, one venv + install line, `--list`, `--process xometry_mjf_pa12 ~/bracket.stl`, exit codes. |
| F5 | SHOULD-FIX | 29 value lines without a `[V]`/`[K]` tag; `hp_mjf_guide` is untagged copies; `neck_max` header untagged. | **FIXED (by rule)** — header: an untagged value line repeats the first tagged occurrence of the key above it; `neck_max` tagged in the header; `hp_mjf_guide` says it copies the JLC row and cannot gate. Tagging all 29 lines individually was rejected: it would repeat the same citation 29 times. |
| F6 | SHOULD-FIX | Xometry `build_max [380, 284, 380]` matches neither the machine (381 × 279 × 381) nor the usable (356 × 279 × 330) volume; `wall_min` tagged `[V]` while the line says the figure is inferred. | **FIXED** — `[356, 279, 330]` (usable gates), `wall_min` retagged `[K]` with the `[V]` feature citation behind it. |
| F7 | SHOULD-FIX | README says 17 generic tools; 16 exist. | **FIXED** — 16. |
| F8 | NIT | Three different rule lists. | **FIXED** — "W R F K P V H O B S + INFO L Y" in both SKILL.md places; the reference table already carried L / Y as INFO. |
| F9 | NIT | Exit codes indistinguishable; a missing STL is a trimesh traceback. | **FIXED** — missing file → one line, exit 2; docstring and reference: 0 PASS, 1 FLAG / gate / validation problem, 2 usage / configuration. |
| F10 | NIT | `scad_lint.py --help` tracebacks. | **FIXED**. |
| F11 | NIT | H never says it saw the two Ø4 holes; `t_min None`. | **PARTLY** — H's value states that voids wider than max(void_min, hole_min) are not measured (they clear); `t_min None` was a consequence of F1 and is gone. Listing every hole with its diameter is not done (a different measurement; add when a user needs a hole table). |
| F12 | NIT | Project jargon (coupon rule, print_targets) and an unexplained `box` order. | **FIXED** — L row only when there is something to list; the result header names the column order and `box = xmin ymin zmin xmax ymax zmax`; Y row says "design margin (the census gate's wall gate)". |
| F13 | NIT | "no waiver field" vs `--open`. | **FIXED** — one sentence in the reference's `--gate` row: the record still says FLAG, the gate prints OPEN, the decision row owns the fix. |
| F14 | NIT | Link radius stated two ways. | **FIXED** — `max(3 sample spacings, 2.5 mm)`. |
| F15 | NIT | The bracket paragraph sat at the end of the project steps. | **FIXED** (with F4) — moved under Quick start. |

Checklist answers worth keeping: the after-verdict procedure and the RULE DEFECT definition were found identical in SKILL.md §8.1 (b), the
reference §3 (b) and the verdict yaml header (no circularity); no hard-coded path; the template table resolved through the symlinked `scripts`
(`realpath`, found by the smoke before this review); all linked paths exist; no fenced README line over 90 characters.

## After the fixes
`scripts/print_dfm.py --selftest`, `scripts/scad_lint.py --selftest`, every other `--selftest`, `smoke/run_smoke.sh` green (step 0d: template rows parse
with `validated_on: []`, the eval-14 pair FLAGs W + R / PASSes through the CLI, `--list` outside a project). The reviewer's own 0.6 mm rib case is now
the selftest's second body. Not re-reviewed by a second lens this version (one-topic release); the next full retro reviews 0.8.x with both lenses.
