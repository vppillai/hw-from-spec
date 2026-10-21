# solidcraft-pipeline.md — a parametric B-rep CAD back end beside OpenSCAD

The case chain (`references/case-pipeline.md`) says "yaml → generated CAD source → STL". The CAD source is OpenSCAD or a SolidCraft command
script. Pick SolidCraft when the part needs fillets, shells, a true STEP, hole features or a parameter table that rebuilds a timeline. Pick
OpenSCAD when the part is a CSG tree and the project already runs it. Both are generated only (SKILL §2), both export the STL of record through
the same gates, and the owner decides per project at kickoff (`references/kickoff-questionnaire.md` C-batch). Every rule below was measured on
the SolidCraft release of 2026-10-21 (the version is in the project's `90-log/ENV.md`); the vendor's own agent skills carry the full command shapes
(`https://github.com/tangency-labs/solidcraft/tree/main/skills`, read `solidcraft-modeling/reference.md` once per project).

## 1. Wire it up

- The CLI and the MCP server are one binary. The desktop app ships it (`SolidCraft.app/Contents/MacOS/solidcraft-cli` on macOS). Record
  the path and version in `90-log/ENV.md` beside OpenSCAD, never in the skill.
- The project's `.mcp.json` registers the server headless: `{"mcpServers": {"solidcraft": {"command": "<path>/solidcraft-cli", "args":
  ["mcp", "--allow-path", "<repo>"]}}}`. Without `--allow-path` the server reads and writes only the open design's folder and its own
  scratch folder. A font file path outside those folders is refused too, so name installed fonts by family.
- Bridged mode (`solidcraft --control 7878`, then `mcp --connect 127.0.0.1:7878`) shows the agent's work in the app. Use it for a review
  session, never for the chain: the headless run is the geometry of record.
- The MCP server has 16 tools. `batch` runs steps all-or-nothing and reports `failed.index` and `failed.error`. `measure` costs about
  1 KB. `inspect_design {"measure": false, "sketches": false}` lists every feature's `error` and `warning`. The unfiltered `list_commands`
  is over 100 KB: filter it, or read the vendor reference instead.

## 2. The script is the generated source

- A script is `{"commands": [{"command": id, "params": {...}}, ...]}`. `solidcraft-cli run script.json --save part.solidcraft --out
  part.stl --out part.3mf --out part.step` builds, saves the design and exports in one call. A failing step fails the run and writes nothing.
- The generator emits the script from `20-design/case.yaml` the way it emits SCAD today. Start every script with `parameters.add` for every
  yaml value (`{"name": "wall", "expression": "2 mm"}`; a count takes `"unit": ""`). Derived values are parameters too (`"W": "bw + 2 *
  (clear + wall)"`). After that, every dimension, offset, base point, height and spacing is an expression over those names. A plain number
  never follows a parameter.
- Sketch dimensions bind through `sketch.draw.dimensioned` (`dimensions: {"width": "W", "height": "D"}`) and `sketch.dimension`
  (`entities: ["origin", "p5"], type: "horizontal", value: "port_x"`). Primitive features take expressions directly: `solid.cylinder
  base: ["hx/2", "hy/2", "wall"]`, `solid.box center: ["vent_pitch * (n_vent - 1) / 2", 0, "wall/2"]`, `solid.pattern.rectangular
  spacing1: "hx", count1: "n_vent"`.
- Edge and face picks (`solid.fillet edges`, `solid.shell faces`) are plain numbers. The pick snaps to the nearest edge with no distance
  limit, so compute it from the parameters at emit time (the vertical corner edge of a centred box is `[W/2, D/2, h/2]`). A pick is
  resolved once and then follows its edge when a parameter changes.
- Presets run on top of the saved design: `solidcraft-cli run preset.json --in part.solidcraft --out part_<target>.stl`. A preset script
  is a list of `parameters.change` steps (or one `changes: {name: expr, ...}` step, all or nothing) and `timeline.suppress` steps for
  features one target does not get (a raised legend on a powder process). The base design stays the single source.
- `run` does not check parameter keys. A misspelt optional key (`operaton` for `operation`) is ignored and the step reports success
  with the wrong geometry. The MCP server checks two commands (`solid.box`, `solid.extrude`) under `--param-check warn|strict`; nothing
  else is checked anywhere. So the generator validates its own key names against the command's `params` text (`solidcraft-cli commands`),
  and every feature is proven by `measure`, never by its `ok`.

## 3. Build order (the vendor skill, confirmed)

1. Parameters, the outline sketch, `solid.extrude`.
2. `solid.fillet` on the outside, then `solid.shell` (the shell follows the fillets). Round the rim after the shell.
3. Joined bosses with their cut pilot holes, patterned together (`features: ["Standoff", "Pilot"]`).
4. Cuts through walls from a sketch on an offset plane: `sketch.create {"plane": "XZ", "offset": "-D/2"}` is the front wall. On XZ,
   sketch y is **-Z**, so a feature at height z is drawn at sketch y = -z. A positive cut distance goes into the wall; give it `wall + 1`.
5. Vents as `solid.box` cuts where the tool meets planar faces only. A primitive boolean that touches a curved face can fail with
   `takes planar faces only`: use a sketch and an extrude cut there.
6. Text last, in its own batch (the risky step). `sketch.text` takes `height` and `at` as expressions.

The tray of §8 (38 steps) builds in 0.9 s, a block in 18 ms, so a parameter sweep is a loop over `run`, not a job for the pool.

## 4. Verify

- `solidcraft-cli eval part.solidcraft` (or the `measure` tool) gives volume, area, bbox, centre of mass and face counts from the B-rep
  kernel. Compare them with values the generator computes from the same yaml: the kernel and the analytic volume agree to about 0.001 %.
  A cut that misses still reports success; only the volume shows it.
- A parameter change through `set_parameter` returns `recomputed` and `errors: []`. A non-empty `errors` list names the feature that broke.
  Then `measure` again, and check the bbox and the centre-of-mass shift you computed.
- Check the timeline after every build with `inspect_design` (headless `eval` has no timeline field). A `Boolean retry` warning with a
  matching volume is harmless; with a volume gap it is a defect.
- The exported mesh is tessellated, 0.03 % under the kernel volume on a part with round bosses and fillets. There is no tolerance knob on
  export. The gates read the mesh, so the census and the print DFM run on the STL, never on the kernel numbers.

## 5. Exports and determinism

| Format | Same script, two runs | Use |
|---|---|---|
| `.3mf` | byte-identical | the order file; carries body names and colours (`appearance.assign`) |
| `.stl` | same triangle set, different order | the chain's STL of record **after** `scripts/step2stl.py --canonical` (sorted triangles, so the md5 is the geometry) |
| `.step` | identical when the file name is the same (the name is in the header) | a true B-rep for CNC quotes and for `step2stl.py` |
| `.solidcraft` | the design with its timeline and parameters | the design of record beside the script; `--save` also writes a `.bak` next to it, which the build cleans |

- A text sketch extruded as `operation: "new"` makes one body per closed glyph outline. For a colour body, join them (`solid.combine
  {"target": "Legend", "tools": ["Legend (2)", ...]}`), name it and assign its colour. Then the 3MF holds the host and one legend body, which
  the slicer maps to a second filament. The STL for DFM is the fused host with the legend joined (`operation: "join"`), from a sibling script.
  The slicer's CLI accepted the file assembled with one filament id per part and sliced it with no warning, but its G-code carried one
  filament and no tool change. Assign the filaments in the slicer project and count the tool changes in the G-code before the plate goes
  into the kit (`references/fdm-print-optimisation.md` §5).
- `file.export bodies: [...]` writes one body alone (the legend's own STL for the colour-body DFM row).

## 6. Pictures

`solidcraft-cli snapshot --in part.solidcraft --out top.png --view top --width 800 --height 500 --no-grid --no-axes` renders on the GPU in
under a second; `--view iso|front|...` and `--section z=<mm>` cover the review set. The MCP `screenshot {"source": "model", "view": "top",
"grid": false, "axes": false}` gives the same picture as an image block. Use the top view to check pattern positions: a full pattern keeps
the centre of mass on the axis, so `measure` cannot see a wrong spacing.

## 7. Traps measured (2026-10-21)

| Trap | What happens | Do instead |
|---|---|---|
| A dimension value goes negative when a parameter changes sign | `invalid value: dimension value -20`; the sketch fails and every feature on it is lost | Distances are unsigned. Dimension from the wall or edge the feature belongs to (`"W/2 - port_from_edge"`), or mirror. Keep the yaml value positive and name its side. |
| `sketch.text bold: true` with no `font` | `the built-in font has no bold face` | Name an installed family (`"font": "Arial", "bold": true`), never a file path (refused outside the allowed folders). |
| Regular text engraved at cap 4 mm | strokes 0.39–0.44 mm; the FDM detail floor (0.45) FLAGs it | Raised legends only, bold, cap ≥ 5.1 (`references/case-pipeline.md` §Presets, FDM); a glyph's inner notch (W, V) is a sub-gate void by nature, so it is a declared legend box (`print_dfm.py --boxes`), and on a powder process the legend is suppressed in that preset. |
| `rectangle.center` | its centre point is `p5`, and each corner joins three lines (two construction diagonals) | dimension `origin` to `p5`; fillet the solid's edges, not the sketch corners |
| `solid.cylinder` with no `operation` | a new body where a join or a cut was meant | always pass `operation` |
| `run --param-check` | has no effect; only the MCP server checks, and only two commands | §2 last bullet |
| `--save` beside an existing design | writes `<name>.solidcraft.bak` | `rm -f *.bak` in the build, keep `build/` ignored |

## 8. Worked example: a parametric board tray, one script, every gate green

<!-- worked example: begin (2026-10-21) -->
A board of 65 × 30 with an M2.5 hole pattern of 58 × 23, 1 mm clearance, 2 mm walls and floor, 12 mm cavity, 3 mm corner radius, four
Ø6 standoffs 4 mm high with Ø2.2 pilots, one 8 × 5 port through the front wall at x = 12, four 2 × 20 vents at 10 mm pitch. 21 parameters,
38 steps, 0.86 s. The kernel reports 9949.65 mm³. The analytic sum (block − cavity + standoffs − port − vents) is 9949.71, a gap of 0.0006 %.
The bbox is 71 × 36 × 14 with 55 faces. The centre of mass sits at −0.096 in x and +0.137 in y, which is the port's 80 mm³ at (12, −17). A `set_parameter`
of the board width to 85 and the hole pitch to 78 recomputes 11 features with no error; the volume becomes 12349.65 against 12349.71 analytic
and the standoffs stay in the corners of the top view. The STL is watertight, one solid, and passes `print_dfm.py` on the 0.4-nozzle FDM row
and the MJF row, and the census at a 1.2 gate with 0.3 margin reads FAIL 0. The raised bold legend at cap 6 passes the FDM row with one
declared legend box, and the MJF preset suppresses it. The check script asserts the volume to 0.01 % on every build.
<!-- worked example: end -->
