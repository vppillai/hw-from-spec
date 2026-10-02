// workflows/routing-inspection.js — TEMPLATE: blind trace-by-trace inspection of a routed board. Two independent inspectors (in-session + an
// external model that sees ONLY the tiles) read every copper tile at ≥ 40 px/mm; merge into a fix list for the board agent.
export const meta = {
  name: '{{PROJECT}}-routing-inspection-{{ROUND}}',
  description: 'Blind re-inspection of the routed {{PROJECT}} board: tile every copper layer at >= 40 px/mm with a mm legend, two independent inspectors read every tile and report autorouter/hand-routing artefacts; merge into a fix list',
  phases: [{ title: 'Tile' }, { title: 'Inspect' }, { title: 'Merge' }],
}
const TILES = { type: 'object', properties: { ok: { type: 'boolean' }, tile_dir: { type: 'string' }, tiles: { type: 'integer' }, layers: { type: 'array', items: { type: 'string' } }, index_path: { type: 'string' } }, required: ['ok', 'tile_dir', 'tiles', 'layers', 'index_path'] }
const FIND = { type: 'object', properties: { report_path: { type: 'string' }, issues: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, layer: { type: 'string' }, net: { type: 'string' }, xy: { type: 'string' }, kind: { type: 'string' }, severity: { type: 'string', enum: ['MAJOR', 'MINOR', 'NOTE'] }, description: { type: 'string' }, fix: { type: 'string' } }, required: ['id', 'layer', 'net', 'xy', 'kind', 'severity', 'description', 'fix'] } }, tiles_read: { type: 'integer' } }, required: ['report_path', 'issues', 'tiles_read'] }
const MERGE = { type: 'object', properties: { report_path: { type: 'string' }, majors: { type: 'integer' }, minors: { type: 'integer' }, fix_list: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' } }, required: ['report_path', 'majors', 'minors', 'fix_list', 'summary'] }

const MAIN = '{{REPO_ROOT}}', BOARD = '{{BOARD_FILE}}', TODAY = '{{DATE}}', RUN = '{{RUN_TAG}}'
const KCLI = '{{CAD_CLI}}'                       // e.g. kicad-cli: 'pcb export svg --layers <L> --exclude-drawing-sheet --page-size-mode 2' then rsvg-convert
const OUT = '{{INSPECTION_DIR}}'                 // e.g. 30-board/layout/layout/inspection
const LAYERS = '{{COPPER_LAYERS}}'               // e.g. F.Cu,In1.Cu,In2.Cu,B.Cu
const CHECKLIST = '{{CHECKLIST_SOURCE}}'         // the decision-log row / doc that lists the artefact classes to look for
const HIGHLIGHTS = '{{NET_CLASS_HIGHLIGHTS}}'    // e.g. "USB pair, I2C, control lines, power branches (corridor cross-section)"
const EXT_MODEL = '{{EXTERNAL_MODEL}}', FALLBACK = '{{FALLBACK_MODEL}}'

const COMMON = `Today is ${TODAY}. Board = {{BOARD_STATE}} (md5, counts and the rules of record are in the hand-off / package board_id.txt — treat those as authoritative). Project root: ${MAIN}. Board file ${BOARD} (read-only for you; work on copies). {{RULES_OF_RECORD}} The board agent has done its own inspection — do NOT read it (blind): never open ${OUT}/*.md from earlier runs or 80-reviews/ROUTING_*.`

phase('Tile')
const tiles = await agent(`${COMMON} TASK — produce the tile set: for each copper layer (${LAYERS}) an SVG with that copper + pads/vias (outer layers with the mask for pad visibility, inner layers with the through-hole/via drills) + the board outline, rendered at >= 40 px/mm via ${KCLI}, cut into ~12 x 12 mm tiles with 1 mm overlap named <layer>_r<row>_c<col>.png with the mm coordinates burned into each tile's corner (PIL text), plus per-net-class highlight renders (${HIGHLIGHTS}) — tracks/vias/pads of the class in colour over the faded layer (classes from the project's netclass assignments/patterns). Write ${OUT}/tiles/ and an INDEX.md (tile -> mm rectangle). Return counts.`, { label: 'tile', phase: 'Tile', schema: TILES, effort: 'medium' })

const ROLE = `Read ${CHECKLIST} for the checklist of artefacts. Then read EVERY tile listed in ${tiles.index_path} (Read tool, all of them — report tiles_read) and the net-highlight renders. For each issue: layer, net (from the highlight renders or by tracing to a pad), mm coordinates from the tile legend, kind (meander/detour, needless via or layer change, jog/acute angle, stub, squeezed between fine-pitch pads, odd pad entry, under a crystal or beside a switching node, return-path break (inner signal over a non-solid reference), long control detour, pair asymmetry, thin power branch, pour neck/island, thermal-relief oddity), severity, one-line fix. Coordinates: say which frame you use (tile legend = board frame).`

phase('Inspect')
const [a, b] = await parallel([
  () => agent(`${COMMON} You are BLIND inspector A (in-session). ${ROLE} Write ${MAIN}/80-reviews/ROUTING_INSPECT_A_${RUN}.md. Return the issues.`, { label: 'inspect:A', phase: 'Inspect', schema: FIND, effort: 'high' }),
  () => agent(`${COMMON} You are the WRAPPER for BLIND inspector B, an external model. BLINDNESS: the model must see ONLY the tiles — copy ${OUT}/ (tiles, highlight renders, INDEX.md) and a copy of the checklist text into a fresh scratch directory and run the CLI with that directory as cwd so it cannot read 80-reviews/ or any notes. Rewrite the prompt paths relative to that directory. Run, capturing stdout to ${MAIN}/80-reviews/ROUTING_INSPECT_B_${RUN}.md (absolute path): agent -p --mode ask --model ${EXT_MODEL} --output-format text "<PROMPT>" where <PROMPT> is: 'You are a PCB layout reviewer. Read the checklist file for the artefact classes. Then open and inspect EVERY image listed in INDEX.md (copper-layer tiles of a routed board with mm legends) and the net-highlight renders in the same folder. Report ONLY a markdown table ID | Layer | Net | X,Y mm | Kind | Severity (MAJOR/MINOR/NOTE) | Description | Fix, followed by a line Tiles read: N. Be exhaustive and concrete.' No timeout on macOS: background + PID + until-loop (≤ 10 min per call, ≤ 60 min). AFTER it exits, 'test -s' the report — EMPTY = failure: retry once with --model ${FALLBACK} (note the substitution); if empty again, write the failure (exit codes, stderr tail) into the report and return zero issues — NEVER judge the board yourself. Parse the table into the schema.`, { label: 'inspect:B', phase: 'Inspect', schema: FIND, effort: 'medium' }),
])

phase('Merge')
const m = await agent(`${COMMON} Merge the two blind inspections (A: ${JSON.stringify(a).slice(0, 20000)}; B: ${JSON.stringify(b).slice(0, 20000)}) into ${MAIN}/80-reviews/ROUTING_INSPECT_merged_${RUN}.md: dedupe by layer+net+xy (within 1 mm, convert frames first), mark corroborated items, order by severity, verify each MAJOR yourself on the tile (Read) and drop false positives with a reason, and produce a fix list for the board agent (net, layer, coordinates, what to do) plus counts. Earlier merged inspections describe OTHER copper — re-derive everything from A and B. Commit the three review files with explicit paths. Return.`, { label: 'merge', phase: 'Merge', schema: MERGE, effort: 'high' })
return { tiles, a, b, m }
