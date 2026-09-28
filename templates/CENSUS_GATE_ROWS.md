# census_gate — check-table rows every printed body carries (`references/dfm-printed-enclosure.md` §2; measurer `scripts/thin_wall_census.py`)

One block per exported body per print preset, emitted by the case generator's check function from the census JSON (`--json`), never typed. Columns
are the project's check table (`# | group | item | value | limit | status | note`); `status` is **OK / FAIL only** — a row with no threshold goes to
the INFO table (§6 of the reference). Fill `{{…}}` from the JSON; `{{GATE}}` = the preset's wall minimum (MJF 1.2 → designed 1.3; FDM 1.6),
`{{VGATE}}` = the void minimum (MJF 1.2; FDM 1.0), `{{THR}}` = `{{GATE}} − 0.05`.

| # | group | item | value | limit | status | note |
|---|---|---|---|---|---|---|
| n | census | {{PIECE}}: ray-cast thin-wall census of `{{STL_REL}}` (md5 {{MD5_8}}, {{SAMPLES}} samples; surface below 0.8 / 1.0 / 1.2 = {{F08}} / {{F10}} / {{F12}} %); WALL clusters below {{THR}}: {{N_WALL}} ({{N_FAIL}} FAIL); VOID clusters below {{VGATE}}: {{N_VOID}}; wedge clusters (listed): {{N_WEDGE}} | {{N_FAIL}} FAIL | 0 FAIL | OK/FAIL | inward rays = wall thickness, outward rays = void width; clusters classified by the opposite-face angle (< 30° wall, else wedge) |
| n | census | {{PIECE}}: WALL cluster below the {{GATE}} gate — span {{SPAN}} at bbox {{BBOX}} ({{WHERE}}: yaml key `{{KEY}}`) | {{TMED_WALL}} (min {{TMIN}}) | >= {{GATE}} | FAIL | a parallel-faced skin / wall / land thinner than the print gate: fix the geometry (never "listed"); one row per cluster |
| n | census | {{PIECE}}: VOID narrower than {{VGATE}} (slot / hole / groove / engraving width) — span {{SPAN}} at bbox {{BBOX}} ({{WHERE}}) | {{GMED}} (min {{GMIN}}) | >= {{VGATE}} | OK/FAIL | the vendor colours a narrow void like a thin wall (every engraved glyph red) |
| n | census | {{PIECE}}: wedge cluster (chamfer / ramp / rail flank) — span {{SPAN}} at bbox {{BBOX}} | {{TMED}} at the edge | backed by a >= {{GATE}} wall | OK/FAIL | grey at the vendor only when cut INTO a wall; a free-standing wedge (rail tip, lip, added cove / fillet) is RED — remove it or give it a >= {{GATE}} flat land |
| n | census | {{PIECE}}: SANITY = the vendor's colouring reproduced — fraction of WALL-class surface below {{THR}} / of void-facing surface below {{THR}} (noise floor on a {{GATE}}+0.1 plate + boss + hole primitive: {{NF_W}} / {{NF_V}} %) | {{WF}} / {{VF}} % | <= {{NF_W}} / <= {{NF_V}} % | OK/FAIL | no yellow, no red; wedge samples are not counted |
| n | census | {{PIECE}}: WALL-class surface in the band {{GATE}}..{{GATE}}+0.3 (walls designed at {{GATE}}+0.1) | {{WB}} % of the surface | PASS by design: every gated wall drawn {{GATE}}+0.1 = 0.1 over the vendor's line | OK | process tolerance ±0.1 keeps it above the grey threshold; a first-article pull test stays in KNOWN_ISSUES §1 |
| n | census | {{PIECE}}: bodies (connected components) | {{BODIES}} | = 1 | OK/FAIL | a mark-shaped body split by a pinch arrives as lobes (`scripts/thin_wall_check.py --pinch`) |
| n | mesh | {{PIECE}}: concentricity of every bore family from mesh sections (Kasa circle fit, {{N_SECTIONS}} sections) — max centre spread | {{SPREAD}} | <= 0.20 | OK/FAIL | measured on the exported STL, not the yaml |
| n | mesh | {{PIECE}}: designed offsets that look like defects ({{FEATURE}} at {{OFFSET}}) | {{MEASURED_OFFSET}} | = designed {{OFFSET}} | OK/FAIL | rendered in `faces/` and printed in the order sheet + KNOWN_ISSUES §1 — or removed with its reason |
| n | faces | {{PIECE}}: six orthographic face renders (top, sole, front, back, left, right) written to `{{FACES_DIR}}` | {{N_FACES}} | 6 | OK/FAIL | the visual review reads every face a technician or the vendor will photograph |

Adopt-list line (PURE gate, recomputes nothing): `"$PY scripts/thin_wall_census.py --gate out/<board>/mechanical/case/<preset>/census"` — every
`<piece>.json` must carry `stl_md5` = md5 of the committed `stl/<piece>_body.stl` beside it and an empty `fails` list.
