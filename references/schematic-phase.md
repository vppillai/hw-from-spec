# schematic-phase.md — G0 → G1: what the design yaml holds, the ERC gate, map checks, the G1 review pack, the studies before a next revision

The schematic generator is project code (`gen/build_sch.py`); this page fixes what it must consume and produce so the gates in `90-log/GATES.md`
mean the same thing in every project. One generator of record (KiCad 10, sheet fragments instantiated per port) is the worked example; the
shapes below are the generic contract.

## 1. Design yaml — the minimum a schematic needs (`20-design/<board>.yaml`, `20-design/parts.yaml`, `20-design/sheets/*.yaml`)

```yaml
# 20-design/<board>.yaml — the root: identity, libraries, sheets, root-level nets
board:
  name: <board>                     # file stem of the generated CAD project (<cad>/<board>/<board>.*)
  title: <one line>  rev: "0"  date: YYYY-MM-DD  paper: A3
  parts: [20-design/parts.yaml]        # part rows looked up by refdes (MPN, fab code, package, tag, DNP) — never typed on the symbol
  lib_map: 20-design/lib_map.yaml      # MPN or refdes prefix -> symbol / footprint
  libs: {sym: [lib/<fab>/<fab>.kicad_sym], fp: [lib/<fab>/<fab>.pretty]}
  power_rails: [GND, +3V3, VBUS]    # names that get power symbols / PWR_FLAG handling
  notes: |                          # the root NOTES block (intent, key values, rework links, test points, checklist) — a review reads it
sheets:                             # one entry per sheet; refdes = sheet × 100 + n; a fragment may be instantiated more than once ({P} prefix)
  - {no: 1, name: power,  file: 20-design/sheets/power.yaml}
  - {no: 2, name: channel_a, file: 20-design/sheets/channel.yaml, prefix: CA_}   # one fragment instantiated twice = two generated sheet files
  - {no: 3, name: channel_b, file: 20-design/sheets/channel.yaml, prefix: CB_}
nets: {}                            # root-level connections between sheets (hierarchical labels), by REF.PIN: NET

# 20-design/sheets/<sheet>.yaml — one sheet or a reusable fragment
title: "{P}channel"                 # {P} = instance prefix; nets without {P} are shared between instances
groups: [ic, passives, connectors]  # placement groups for the drawer
components:
  - {ref: U1, group: ic, part: <MPN>}                           # part row supplies symbol/footprint/fields
  - {ref: R1, group: passives, symbol: Device:R, value: 4.7k, footprint: Resistor_SMD:R_0603_1608Metric,
     fields: {MPN: …, Manufacturer: …, <FAB_CODE>: …, Datasheet: <live URL>, Confidence: V, Alt_MPN: "", Alt_<FAB_CODE>: ""}}
  - {ref: R2, dnp: true, …, fields: {Confidence: S}}           # [S] rows have no MPN yet; DNP is explicit on symbol AND footprint
nets:                               # REF.PIN: NET — every pin either has a net, is in `no_connect`, or the generator refuses
  U1.1: "{P}VCC"
  U1.2: GND
no_connect: [U1.7]
labels: {…}  notes: |               # sheet NOTES block (same five items as the root)
```

Rules the generator enforces (each a `--selftest` case): every fitted part has a `Confidence` of V or N/A (`[K]` refuses — `references/part-verification.md`).
Value ↔ MPN ↔ fab code agree. Every pin is connected or explicitly no-connect. Refdes are unique across sheets after the prefix. The symbol fields
are copied to the footprint as hidden properties (schematic ↔ board parity). UUIDs are rewritten deterministically so `--check` is byte-stable. A
sheet instantiated twice is two generated sheet FILES (some CAD CLIs mishandle one file instantiated twice). Never rewrite a project file
another generator owns without re-reading and merging its part (`references/pitfalls.md` tooling/gates).

## 2. ERC gate (rule 7)

Run after every generation, with every severity on, machine-readable, zero errors:

```sh
<cad-cli> sch erc --severity-all --format json -o 30-board/layout/erc.json <cad>/<board>/<board>.kicad_sch     # KiCad 10 form; other CADs: the equivalent
```

Errors → fix the yaml or the generator. Warnings → fix, or one entry in `20-design/erc_accept.yaml` (`{type, ref, reason, decision, date}`; the decision
row must exist and not be REJECTED) — `scripts/erc_gate.py 30-board/layout/erc.json` is the gate: 0 errors, 0 unaccepted warnings, no stale entry, no
GUI exclusion (a hidden waiver). There is no prose waiver table. Add `erc_gate.py` to `gates.adopt` at G1 (`templates/project.yaml` has the commented block) so it is repeated on every adopt run and in
`git archive HEAD`. Export the netlist in the same step (`<cad-cli> sch export netlist --format kicadxml -o 30-board/layout/<board>.xml …`): `paths.netlist`
feeds the `netlist_net` checks of `scripts/traceability.py`.

## 3. Map checks

A "map" is any table in the spec or in `20-design/` that says which pin, address or connector position carries what: an MCU / bridge GPIO map, an
I²C address map, a connector pinout, a switch/strap table, a test-point map. **Map checks** = a project script (`gen/check_maps.py --check`) that
reads every map and the exported netlist. It asserts both directions. Every map row is present in the netlist as written (net name on that pin;
address on that device). Every relevant netlist net appears in exactly one map. Output `30-board/layout/check_maps.md` (one table per map: row,
netlist evidence, OK/FAIL) — a G1 prerequisite in `90-log/GATES.md` and a `gates.adopt` line. A map row the spec names but the design does not
implement is a CC row (rule 2), not a silent omission.

## 4. The G1 review pack (`80-reviews/G1/`, generated, committed)

| File | Produced by | Why the reviewer needs it |
|---|---|---|
| `<board>.pdf` | `<cad-cli> sch export pdf` | the schematic as drawn, every sheet |
| `<board>.xml` | `<cad-cli> sch export netlist --format kicadxml` | machine-checkable connectivity |
| `bom.csv`, `procurement.csv` | the project's BOM exporter | every fitted part with MPN / fab code / tag; DNP excluded |
| `erc.json` + `20-design/erc_accept.yaml` | §2 | `scripts/erc_gate.py` green: zero errors, every warning accepted by a decision row |
| `check_maps.md` | §3 | maps vs netlist |
| `EVIDENCE.md` | the generator | which yaml revision / commit produced the pack; md5 of every file above |
| `REVIEW_NOTES.md` | hand-written, short | what changed since the last round, what the reviewers should weigh |

The hand-off for the G1 round (`templates/REVIEW_HANDOFF.md`) lists these files with md5 in §2; `scripts/handoff_header.py` still reports the
board as MISSING at G1 (no routed board yet) — that is expected and said in the hand-off. Blind review roles at G1: the `board` role set of
`workflows/blind-deep-review.js` minus layout/silk/fab-package (no copper yet), or the same nine roles with briefs scoped to the schematic.

## 5. G0 → G1 in order

1. G0 cell written by the owner → 2. `20-design/*.yaml` from SPEC (every spec value that must change → CC row OPEN first) → 3. `gen/build_sch.py`
(`--check` green, ERC zero errors, netlist) → 4. map checks → 5. G1 pack → 6. `scripts/traceability.py` entries for every spec requirement now
landing in the yaml (stage `schematic`) → 7. freeze, hand-off, blind round (SKILL §5), merged report `80-reviews/G1_merged.md` → 8. REQUIRED
items applied, regenerate, re-run 3-6 → 9. ask for the G1 cell (SKILL §1.1). Layout CAD starts only after the cell exists.

## 6. Studies before the next revision's spec
A next revision opens with one study per open area: power, thermal and mechanics, signal integrity, the controller. Studies that share no
file run in parallel. Each one answers the owner's questions and ends in a recommendation.
- **The shape.** The short answer comes first. Then the inputs from the bench records, the options, the recommendation and the owner
  questions, each with a recommended answer. Then what the note does not know, the learnings for the log and the sources. The owner's
  answers go at the end of the same file, and the decisions they make become decision rows.
- **Live parts.** Every part a study names is read live that day and tagged (`references/part-verification.md`). The rows go into the parts
  table. A part that could not be read live sits in its own section, never in the recommendation.
- **The bench first.** A study starts from what the last revision measured: its power, its heat, its faults.

Rules the studies found, for any next revision. The worked examples come from one two-ended test product.
- **Power budget.** An end-to-end test of a two-ended product loads both ports at once. Budget the sum of both ends.
- **Protection switch.** Size a protection switch by its drop at the rail current. One 28 mΩ switch at 5 A on a 3.3 V rail drops
  0.14 V and burns 0.7 W. Also check its safe operating area, inrush, current limit, reverse current and fault energy.
- **Overvoltage.** A high input voltage makes a failed regulator a load killer. Put an overvoltage cut-off between the regulator and
  the load.
- **Back-power.** A rail part does not stop back-power through signal lines. List every path that can feed the rail. Check each
  path for isolation, voltage, direction and reset behaviour. A bus buffer with a rated Ioff isolates only the paths it covers.
  A tristate state in the tool helps only while the tool runs; it is not fail-safe at reset.
- **USB power sink.** Pick the sink controller by its fallback on a source with no PD. One kind reports the Type-C current there;
  another reports nothing. A PD source that offers only a 5 V PDO is a different case; test both. A sink controller may keep the source
  capabilities only until the next message overwrites its buffer. Read that behaviour in the chosen controller's datasheet. The firmware
  copies the capabilities on the alert. To read them again, it sends Get_Source_Cap. A soft reset is protocol recovery, not a
  query. Use it only as the PD policy engine and the controller's datasheet direct.
- **Fan start-up.** A fan controller's duty after a power cycle is undefined until you verify it. A volatile curve can leave the fan
  at 0 % with no host. Use a part with an EEPROM, or a controller with the curve in flash. Verify a safe reset default duty.
- **Over-temperature.** Give the load an over-temperature path that needs no host.
- **Airflow.** The airflow sits where the fan curve meets the impedance curve of the whole enclosure: grille, filters and path.
  Model or measure them together. This skill carries no flow solver; a bench measurement decides. Worked example: a 1-D
  estimate gave 20 to 27 % of free flow behind 212 mm² of slots. A 30 mm fan's gross disc is about 700 mm², and a 40 mm fan's
  about 1250 mm².
- **Heat capacity.** Measure the load's heat capacity on the bench before you set the fan's response. On one bench, 8 W raised a
  module 11 K in 60 s, with the losses neglected. That reading, about 44 J/K, overstates C. Use a conservative lower bound on C:
  the initial slope, or a fit of the net heat flow. Use the worst-case net heat. The time from detection to full airflow is at
  most ΔT_margin × C_low / P_worst. That time holds the sensor lag, the command and the spin-up.
- **Sizing.** Size the electronics for the top load power. Size the heat sink for every load and ambient the product supports.
  Otherwise enforce a lower power limit, with an independent thermal shutdown.
- **Units.** Write GBd for a symbol rate and Gb/s for a bit rate, never one number for both. A PAM4 lane carries two bits per symbol.
- **Loops on a connector.** Loop a transmit pair to a neighbour lane's receive pair. Pair placement alone does not prove one-layer
  routing. Check the drawing and the whole launch and routing geometry. A checker that locks on the same pattern from any lane cannot
  prove the lane map. Challenge every physical lane on its own: a lane-unique pattern or seed, or an error injected on that lane.
  Verify the whole map: the lane order, the polarity and the direction. Match the polarity and the
  precoding per lane on the loop. Check the crosstalk between neighbouring loops against the SI budget. Follow the interface
  specification and the schematics of both ends for AC coupling. State where each path is coupled. Give each path exactly one
  compliant coupling stage.
- **Pads and the stack.** A wide pad over thin prepreg can drop below the target impedance (`references/pcb-layout-dfm.md` §3).
  Connectors mirrored on both board faces set the board thickness and the termination. Read the fab's live thickness table by layer count
  before a study recommends them.
- **The controller.** A module family can carry other temperature ratings per memory option. Pick by the quantity the datasheet rates
  (ambient, case or junction) at the worst local temperature, with self-heating and margin. Never pick by the deepest stock. A part rated
  for a single reflow goes on the side reflowed last. Confirm the order with the assembler (`references/pcb-layout-dfm.md` §9). Read the
  controller's errata for its USB download path, and keep the ROM recovery path and its pins free.
