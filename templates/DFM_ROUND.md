# {{VENDOR}} DFM round {{ROUND}} — case {{CASE_VERSION}} — {{DATE}} (record; `references/dfm-printed-enclosure.md` §7)

Quote page only: nothing saved to an account, carted, agreed or paid (`references/vendor-review.md` §1). Owner signed in: {{YES/NO}}; uploads by {{AGENT}}.
Files here: `<piece>_<version><round>_<md5-8>.stl` (the exact bytes uploaded, canonical STL), `<piece>_<round>_<md5-8>_<material>_heatmap_<face>.png`,
`quote_page_<round>_flags.png`. One STL per page session (a page with several lines opens the wrong file's analysis).

## 1. Bodies uploaded (one row per session)
| Body | STL of record (md5-8, canonical) | Uploaded file | Process / material SET on the line before reading | Vendor volume = ours | Flag ("Thin walls detected" / risk popover) | Heat-map screenshots (every face) | Verdict |
|---|---|---|---|---|---|---|---|
| {{PIECE}} | `{{MD5_8}}` | `{{PIECE}}_{{VERSION}}{{ROUND}}_{{MD5_8}}.stl` | {{PROCESS}} / {{MATERIAL}} (default was {{DEFAULT_MATERIAL}} — changed, Edit dialog saved) | {{VOL_VENDOR}} / {{VOL_OURS}} cm³ | {{NONE / TEXT}} | `…_heatmap_iso_top.png`, `…_inside.png`, `…_sole.png`, `…_front.png` | PASS (no flag, all grey) / FLAGGED |

## 2. Every coloured area mapped to a feature (FLAGGED bodies only)
| Body | Colour + where on the map (face, extent) | Feature (yaml key) | Class (wall / void / free wedge) | Census number (`scripts/thin_wall_census.py`, cluster span + bbox) | Fix in the yaml + generator | Re-upload round |
|---|---|---|---|---|---|---|
| {{PIECE}} | {{RED/YELLOW}} {{FACE}} {{EXTENT}} | `{{KEY}}` | {{CLASS}} | {{MM}} × {{SPAN}} at {{BBOX}} | {{CHANGE}} | {{ROUND+1}} |

A colour that maps to no feature is a finding (a 0.01 mm overshoot slab, a stale export). A verdict that differs from the previous round on the
same body: diff the meshes first (facets, vertices, volume, winding, container ASCII/binary) and check both lines' material before changing geometry.

## 3. Our own numbers for the same files (check tables + census, mode stated)
| Body | Check table (rows / FAIL / WARN / INFO) | Census: walls below gate / voids below gate / wedges listed | SANITY (wall-class / void-facing surface below gate−0.05) | Concentricity spread | Faces rendered |
|---|---|---|---|---|---|
| {{PIECE}} | {{N}} / 0 / 0 / {{INFO}} | 0 / 0 / {{WEDGES}} | {{WF}} / {{VF}} % (floor {{NF}}) | {{SPREAD}} | 6 |

## 4. Verdict of the round
**{{PASS / NOT YET}}** — acceptance bar: every body no flag + no yellow / red under the material of the order, 0 FAIL / 0 WARN in the tables and census,
zero slicer warnings (home build), every face looked at. Bodies of record after this round: {{PIECE}} `{{MD5_8}}`, … Owner items: {{NONE / LIST}}.
Decision row: {{CC-nnn}} (APPLIED / OPEN). Not done: {{LIST}}.
