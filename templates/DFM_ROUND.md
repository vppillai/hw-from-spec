# {{VENDOR}} DFM round {{ROUND}} — case {{CASE_VERSION}} — {{DATE}} (record; `references/dfm-printed-enclosure.md` §7)

Quote page only: nothing saved to an account, carted, agreed or paid (`references/vendor-review.md` §1). Owner signed in: {{YES/NO}} (the DFM read
needs no login); uploads by {{AGENT}}. Files here: `<piece>_<version><round>_<md5-8>.stl` (the exact bytes uploaded, canonical STL),
`<piece>_<round>_<md5-8>_<material>_heatmap_<face>.png`, `quote_page_<round>_flags.png`, `probe/` (if §5 was needed). One STL per page session, page
reloaded between uploads (a page with several lines opens the wrong file's analysis). **Verdict = the analysis API response (`getFileAnalyzeResult`)
at `parseStatus == 2`, `modelAnalysisVO.thinWall`; a DOM reading before parseStatus 2 is not a verdict.** The flag is computed at upload and does not
depend on the material chosen on the line.

## 1. Bodies uploaded (one row per session)
| Body | STL of record (md5-8, canonical) | Uploaded file | Process / material SET on the line before reading (price + legend; not the flag) | API `parseStatus` / `thinWall` (how read) | Vendor volume = ours | Page flag ("Thin walls detected" / risk popover) | Heat-map screenshots (every face, via `previewUrl`) | Verdict |
|---|---|---|---|---|---|---|---|---|
| {{PIECE}} | `{{MD5_8}}` | `{{PIECE}}_{{VERSION}}{{ROUND}}_{{MD5_8}}.stl` | {{PROCESS}} / {{MATERIAL}} (default was {{DEFAULT_MATERIAL}} — changed, Edit dialog saved) | 2 / {{true/false}} ({{network log / re-request}}, {{HH:MM}}) | {{VOL_VENDOR}} / {{VOL_OURS}} cm³ | {{NONE / TEXT}} (agrees with the API: {{YES}}) | `…_heatmap_iso_top.png`, `…_inside.png`, `…_sole.png`, `…_front.png` | PASS (API false, all grey) / FLAGGED |

A row whose API cell is empty or `parseStatus` ≠ 2 has no verdict. The coordinator re-requests the API for every md5 a worker reports as PASS before the
decision row is written (`references/agent-ops.md` §6).

## 2. Every coloured area mapped to a feature (FLAGGED bodies only)
| Body | Colour + where on the map (face, extent) | Feature (yaml key) | Class (wall / void / free wedge) | Census number (`scripts/thin_wall_census.py`, cluster span + bbox) | Fix in the yaml + generator | Re-upload round |
|---|---|---|---|---|---|---|
| {{PIECE}} | {{RED/YELLOW}} {{FACE}} {{EXTENT}} | `{{KEY}}` | {{CLASS}} | {{MM}} × {{SPAN}} at {{BBOX}} | {{CHANGE}} | {{ROUND+1}} |

A colour that maps to no feature is a finding (a 0.01 mm overshoot slab, a stale export). A verdict that differs from the previous round on the
same body: confirm both reads were API reads at parseStatus 2, then diff the meshes (facets, vertices, volume, winding, container ASCII/binary)
before changing geometry. **A flagged body whose census is clean → §5 probes** (the metric is length-dependent; `dfm-printed-enclosure.md` §7.1).

## 3. Our own numbers for the same files (check tables + census, mode stated)
| Body | Check table (rows / FAIL / WARN / INFO) | Census: walls below gate / voids below gate / wedges listed | SANITY (wall-class / void-facing surface below gate−0.05) | Concentricity spread | Faces rendered |
|---|---|---|---|---|---|
| {{PIECE}} | {{N}} / 0 / 0 / {{INFO}} | 0 / 0 / {{WEDGES}} | {{WF}} / {{VF}} % (floor {{NF}}) | {{SPREAD}} | 6 |

## 4. Verdict of the round
**{{PASS / NOT YET}}** — acceptance bar: every body no flag + no yellow / red under the material of the order, 0 FAIL / 0 WARN in the tables and census,
zero slicer warnings (home build), every face looked at. Bodies of record after this round: {{PIECE}} `{{MD5_8}}`, … Owner items: {{NONE / LIST}}.
Decision row: {{CC-nnn}} (APPLIED / OPEN). Not done: {{LIST}}.

## 5. Probes (only when a body is flagged and the census finds nothing — `probe/PROBES.md` carries the full table; summary here)
| Probe | What (slab of the body of record Y a..b / plain profile, length, knob = value) | Uploaded alone | API `thinWall` | Reading |
|---|---|---|---|---|
| {{S1}} | slab {{Y0}}..{{Y1}} ({{LEN}} mm), capped | yes | {{true/false}} | localises {{FEATURE}} / length threshold {{L}} mm |
| {{K0}} | plain profile as-is, {{FULL_LEN}} mm | yes | true | reproduces the body's flag without bosses / holes |
| {{K1}} | plain profile, knob `{{KNOB}}` = {{VALUE}}, {{FULL_LEN}} mm | yes | false | **rule adopted**: {{RULE}} |
| {{K1s}} | the same knob at 40 mm | yes | false | proves nothing about the full length — recorded for the length rule only |

Rule into the census as a named row: {{RULE}} (e.g. "rim over a lap step ≥ 2.0 OR undercut filled"). Yaml change: `{{KEY}}` on the vendor preset AND the
home preset (own version keys). Re-verification of every body of record by the API after the change: {{PIECE}} `{{MD5_8}}` false, …
