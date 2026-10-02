# census_gate — check-table rows every printed body carries (`references/dfm-printed-enclosure.md` §2; measurer `scripts/thin_wall_census.py`)

One block per exported body per print preset, emitted by the case generator's check function from the census JSON (`--json`), never typed. Columns
are the project's check table (`# | group | item | value | limit | status | note`); `status` is **OK / FAIL only** — a row with no threshold goes to
the INFO table (§6 of the reference) **and states why it has no threshold**. Every number comes from `project.yaml print_targets.<target>`
(`references/project-yaml.md`): `{{GATE}}` = `wall_gate` (worked example: JLC3DP checker 1.2, home FDM 0.4 nozzle 1.6), `{{MARGIN}}` =
`design_margin` (owner bar, 0.1), `{{VGATE}}` = `void_gate` (1.2 / 1.0), `{{RED}}` = `red_line` (0.5), `{{BAND}}` = `wedge_band` (1.5, convention),
`{{THR}}` = `{{GATE}} − 0.05` (clustering convention), `{{TOL}}` = `tolerance` (the vendor's published figure until first-article measured).

| # | group | item | value | limit | status | note |
|---|---|---|---|---|---|---|
| n | census | {{PIECE}}: ray-cast thin-wall census of `{{STL_REL}}` (md5 {{MD5_8}}, target `{{TARGET}}`, {{SAMPLES}} samples = {{DENSITY}} /mm²; surface below 0.8 / 1.0 / {{GATE}} = {{F08}} / {{F10}} / {{FG}} %); WALL clusters below {{THR}}: {{N_WALL}}; VOID clusters below {{VGATE}}: {{N_VOID}}; WEDGE clusters: {{N_WEDGE}} ({{N_WEDGE_FAIL}} over band {{BAND}}); OPPOSING-face clusters below {{GATE}}: {{N_OPP}}; accepted (dated, evidence): {{N_ACC}} | {{N_FAIL}} unaccepted FAIL | 0 | OK/FAIL | inward rays = wall, outward rays = void, opposing = nearest face with an opposing normal in ANY direction; classes by the opposite-face angle (< 30° wall, else wedge — convention) |
| n | census | {{PIECE}}: WALL cluster below the {{GATE}} gate — span {{SPAN}} at bbox {{BBOX}} ({{WHERE}}: yaml key `{{KEY}}`) | {{TMED_WALL}} (min {{TMIN}}) | >= {{GATE}} | FAIL | a parallel-faced skin / wall / land thinner than the target's gate: fix the geometry (never "listed"); one row per cluster; the value is measured on the MESH, never read from the yaml |
| n | census | {{PIECE}}: VOID narrower than {{VGATE}} (slot / hole / groove / engraving width) — span {{SPAN}} at bbox {{BBOX}} ({{WHERE}}) | {{GMED}} (min {{GMIN}}) | >= {{VGATE}} | OK/FAIL | the checker colours a narrow void like a thin wall (every sub-gate engraved glyph red); engraved text is allowed when its stroke ≥ {{VGATE}} |
| n | census | {{PIECE}}: WEDGE cluster (chamfer / ramp / rail flank) — band below the gate {{WBAND}} wide, span {{SPAN}} at bbox {{BBOX}} | {{TMED}} at the edge, band {{WBAND}} | band <= {{BAND}} or backed by a >= {{GATE}} wall named in `accepted` | OK/FAIL | grey at the checker only when cut INTO a wall (tangent fillets and chamfers into ≥ gate walls are fine); a free-standing wedge (rail tip, lip, non-tangent cove, knife edge) is RED — remove it or give it a >= {{GATE}} flat land |
| n | census | {{PIECE}}: OPPOSING faces closer than {{GATE}} in any direction (ledge underside vs step top, ring face vs wall plane, a rim ring's root) — span {{SPAN}} at bbox {{BBOX}} | {{DOPP}} (min {{DOPP_MIN}}) | >= {{GATE}} (wall) / >= {{VGATE}} (void) | OK/FAIL | the class every normal-ray census missed and the vendor found (reference §7.1); a root narrower than the gate cracks however thick the ring and the wall are |
| n | census | {{PIECE}}: NOISE FLOOR — fraction of WALL-class surface below {{THR}} / of void-facing surface below {{THR}} (floor on a {{GATE}}+{{MARGIN}} plate + boss + hole primitive: {{NF_W}} / {{NF_V}} %) | {{WF}} / {{VF}} % | <= {{NF_W}} / <= {{NF_V}} % | OK/FAIL | false-positive floor, NOT proof of recall (recall is the selftest's 0.8 rib + 0.6 slit); wedge samples are not counted |
| n | census | {{PIECE}}: accepted cluster `{{ACC_CLASS}}` at bbox {{ACC_BBOX}} — `{{ACC_REASON}}` ({{ACC_DATE}}, evidence `{{ACC_EVIDENCE}}`) | {{TMED}} | matched by `print_targets.{{TARGET}}.accepted` | OK | re-asserted every run by bbox + class; an entry without date / reason / evidence does not count; listed in the gate merge with the round it was added |
| n | census | {{PIECE}}: bodies (connected components) | {{BODIES}} | = 1 | OK/FAIL | a mark-shaped body split by a pinch arrives as lobes (`scripts/thin_wall_check.py --pinch`) |
| n | census | {{PIECE}}: geometry signature (volume / area / bbox / facets, 1e-3) beside md5 {{MD5_8}} | {{SIG}} | = the signature of the previous export unless a yaml change names the piece | OK/FAIL | an md5 that moved with an unchanged signature is a container / export-order change, not geometry (reference §7.2) |
| n | mesh | {{PIECE}}: concentricity of every bore family from mesh sections (circle fit, {{N_SECTIONS}} sections) — max centre spread | {{SPREAD}} | <= {{CONC}} (convention, one part family) | OK/FAIL | measured on the exported STL, not the yaml |
| n | mesh | {{PIECE}}: retention feature present in the mesh ({{RETENTION}}: bosses / bores / pockets at {{XY}}) | {{FOUND}} | = designed | OK/FAIL | a check row that read the yaml passed a hood whose STL carried no bosses — every retention row measures the mesh |
| n | mesh | {{PIECE}}: designed offsets that look like defects ({{FEATURE}} at {{OFFSET}}) | {{MEASURED_OFFSET}} | = designed {{OFFSET}} | OK/FAIL | rendered in `faces/` and printed in the order sheet + KNOWN_ISSUES §1 — or removed with its reason |
| n | fit | {{PIECE}} ↔ {{PARTNER}}: worst-case clearance = nominal {{NOM}} − (case ±{{TOL}} + board ±0.2 + {{OTHER}}) | {{WORST}} | >= 0 | OK/FAIL | nominal-only interference (0 mm³) passes designs that bind at worst case; tolerances from `print_targets` + the board outline; fits are per-preset knobs |
| n | faces | {{PIECE}}: six orthographic face renders (top, sole, front, back, left, right) written to `{{FACES_DIR}}` | {{N_FACES}} | 6 | OK/FAIL | the visual review reads every face a technician or the vendor will photograph |

INFO table (no threshold — each row says why): `WALL-class surface in the band {{GATE}}..{{GATE}}+0.3` (no threshold until the first-article
caliper table gives the process spread; the vendor's published tolerance is ±{{TOL}}, so a {{GATE}}+{{MARGIN}} wall may print below the gate —
this row is INFO, not "PASS by design"); `build orientation` (vendor's choice, recorded when answered); `post-process` (`{{POST}}`, subtracted in
the margin); `material rating` (UL 94 / Tg from the TDS, printed on the order sheet).

Adopt-list lines (PURE gates, recompute nothing): `"$PY scripts/thin_wall_census.py --gate-dir 40-case/<set>/checks/census"` — every
`<piece>.json` must carry `stl_md5` = md5 of the committed `stl/<piece>.stl` beside it and an empty `fails` list (accepted clusters live in
`accepted_fails` with their entry) — AND `"$PY scripts/print_dfm.py --gate 40-case/<set>/checks/dfm"` (the printability floor, `references/print-dfm.md`);
`scripts/project.py gates-required` demands both once the STL set exists.
