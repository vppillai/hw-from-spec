# {{VENDOR}} DFM round {{ROUND}} — case {{CASE_VERSION}} — {{DATE}} (record; `references/dfm-printed-enclosure.md` §7)

Quote page only: nothing saved to an account, carted, agreed or paid (`references/vendor-review.md` §1). **Owner consent to upload the design
to {{VENDOR}}: decision row {{D-nn}} (quoted: "{{OWNER_WORDS}}"); vendor terms read {{DATE}} at {{TERMS_URL}}.** Owner signed in: {{YES/NO}}
(the DFM read needs no login); uploads by {{AGENT}}; browser / UA: {{BROWSER}}. Files here: `<piece>_<version><round>_<md5-8>.stl` (the exact bytes
uploaded, canonical STL) and `<md5-8>_analyze.json` (the RAW API response with URL, timestamp, headers). The folder also holds `<piece>_<round>_<md5-8>_<material>_heatmap_<face>.png`,
`quote_page_<round>_flags.png`, `capability_page_{{DATE}}.pdf` (the vendor's published design rules as they read today), and `probe/` (if §5 was needed).
One STL per page session, page reloaded between uploads. **Verdict = the vendor's analysis API response, read when its parse is complete —
`{{VERDICT_API}}` (JLC3DP: `getFileAnalyzeResult` at `parseStatus == 2`, `modelAnalysisVO.thinWall`); a page reading before that is not a verdict.**
The flag is computed at upload and does not depend on the material chosen on the line. **Site-changed branch**: endpoint or field missing today → BLOCKERS row {{B-nn}}, verdict class = "page popover +
screenshot", round NOT YET. Legend thresholds as displayed today: grey ≥ {{LEGEND_GREY}}, yellow {{LEGEND_YELLOW}}, red < {{LEGEND_RED}}
(compare with `print_targets.{{TARGET}}`; a difference is a decision row).

## 1. Bodies uploaded (one row per session)
| Body | STL of record (md5-8, canonical) + signature (vol / area / bbox / facets) | Uploaded file | Process / material SET on the line (price + legend; not the flag) | Quote price per body | API `parseStatus` / `thinWall` (how read; raw JSON file) | Vendor volume / area / bbox = ours (scale sanity) | Page flag | Heat-map screenshots (every face, via `previewUrl`) | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| {{PIECE}} | `{{MD5_8}}` {{SIG}} | `{{PIECE}}_{{VERSION}}{{ROUND}}_{{MD5_8}}.stl` | {{PROCESS}} / {{MATERIAL}} (default was {{DEFAULT_MATERIAL}} — changed, Edit dialog saved) | {{PRICE}} {{CURRENCY}} at qty {{QTY}} | 2 / {{true/false}} ({{network log / re-request}}, {{HH:MM}}; `{{MD5_8}}_analyze.json`) | {{VOL_VENDOR}} / {{VOL_OURS}} cm³; bbox {{BBOX_VENDOR}} = {{BBOX_OURS}} | {{NONE / TEXT}} (agrees with the API: {{YES}}) | `…_heatmap_iso_top.png`, `…_inside.png`, `…_sole.png`, `…_front.png` | PASS (API false, all grey) / FLAGGED |

A row whose API cell is empty or `parseStatus` ≠ 2 has no verdict. The coordinator re-requests the API for every md5 a worker reports as PASS before the
decision row is written (`references/agent-ops.md` §6). A vendor bbox or volume that differs from ours = a different file or a unit / scale error — no verdict.

## 2. Every coloured area mapped to a feature (FLAGGED bodies only)
| Body | Colour + where on the map (face, extent) | Feature (yaml key) | Class (wall / void / free wedge / opposing) | Census number (`scripts/thin_wall_census.py`, cluster span + bbox) | Fix in the yaml + generator | Re-upload round |
|---|---|---|---|---|---|---|
| {{PIECE}} | {{RED/YELLOW}} {{FACE}} {{EXTENT}} | `{{KEY}}` | {{CLASS}} | {{MM}} × {{SPAN}} at {{BBOX}} | {{CHANGE}} | {{ROUND+1}} |

A colour that maps to no feature is a finding (a 0.01 mm overshoot slab, a stale export). A verdict that differs from the previous round on the
same body: confirm both reads were API reads at parseStatus 2, then compare the geometry signatures and diff the meshes before changing geometry.
**A flagged body whose census is clean → §5 probes** (the metric is length-dependent; `dfm-printed-enclosure.md` §7.1).

## 3. Our own numbers for the same files (check tables + census, mode stated)
| Body | Target | Check table (rows / FAIL / INFO; INFO rows new in the round) | `print_dfm.py --process <row>` verdict (record md5) | Census: walls / voids / wedges over band / opposing below gate (unaccepted FAIL) | Accepted entries matched | Noise floor (wall-class / void-facing below gate−0.05) | Worst-case clearance rows | Concentricity spread | Faces rendered |
|---|---|---|---|---|---|---|---|---|---|
| {{PIECE}} | `{{TARGET}}` | {{N}} / 0 / {{INFO}} (+{{NEW_INFO}}: {{WHY}}) | PASS ({{MD5_8}}) | 0 / 0 / 0 / 0 | {{N_ACC}} ({{IDS}}) | {{WF}} / {{VF}} % (floor {{NF}}) | {{N_PAIRS}} ≥ 0 | {{SPREAD}} | 6 |

## 4. Verdict of the round
**{{PASS / NOT YET}}** — acceptance bar: every body no flag (API read) + no yellow / red under the material of the order. The bar also needs 0 unaccepted FAIL in the
tables and census, zero slicer warnings (home build), every face looked at, and no waivers. Bodies of record after the round: {{PIECE}} `{{MD5_8}}`, …
**Material rating per target on the order sheet**: {{TARGET}} = {{MATERIAL}}, UL 94 {{RATING}}, HDT (0.45 MPa) {{HDT}} °C (TDS {{URL}}, {{DATE}}).
Owner's "engineering sample, not a rated enclosure" row: {{D-nn}}. **Build orientation** (asked / answered / n.a.): {{ORIENTATION}}.
**Post-process** named: {{POST}}. Owner items: {{NONE / LIST}}. Decision row: {{CC-nnn}} (APPLIED / OPEN). Not done: {{LIST}}.

## 5. Probes (only when a body is flagged and the census finds nothing — `probe/PROBES.md` carries the full table; summary here)
| Probe | What (slab of the body of record Y a..b / plain profile, length, knob = value) | Uploaded alone | API `thinWall` | Reading |
|---|---|---|---|---|
| {{S1}} | slab {{Y0}}..{{Y1}} ({{LEN}} mm), capped | yes | {{true/false}} | localises {{FEATURE}} / length threshold {{L}} mm |
| {{K0}} | plain profile as-is, {{FULL_LEN}} mm | yes | true | reproduces the body's flag without bosses / holes |
| {{K1}} | plain profile, knob `{{KNOB}}` = {{VALUE}}, {{FULL_LEN}} mm | yes | false | **rule adopted**: {{RULE}} |
| {{K1s}} | the same knob at 40 mm | yes | false | proves nothing about the full length — recorded for the length rule only |
| {{K1t}} | the same profile and length in a taller / wider box (bbox hypothesis test, §7.1) | yes | {{true/false}} | margin ∝ max bbox dimension: {{YES/NO}} → `max_bbox_for_rule` |

Rule into the census as a named row: {{RULE}} (for example "rim over a lap step ≥ 2.0 OR undercut filled"). Yaml change: `{{KEY}}` on the vendor preset AND the
home preset (own version keys). Re-verification of every body of record by the API after the change: {{PIECE}} `{{MD5_8}}` false, …
