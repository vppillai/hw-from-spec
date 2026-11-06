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

- A symbol that the CLI cannot load drops its whole child sheet from ERC, the netlist and the BOM. The only sign can be a hierarchical-label
  mismatch on the root sheet. Load each child sheet alone with the netlist export, then remove one symbol type at a time to find it.
- Read each library symbol's pin types against the datasheet, not only the pin numbers. Stock symbols have typed an open-drain reset as an
  output and an exposed pad as unspecified *(worked example)*.
- Two output pads of one part on one net read as a power-out conflict. Type the second pad passive in the pin-type yaml. Never put a power
  flag on a net that a power-output pin drives.

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
- **A window comparator with an RC gate.** An RC filter on a start-up window comparator delays its output. Count that lag against
  the threshold spread of the gate FET. Otherwise the comparator clears the latch on a normal start. Run the check at both FET corners.
- **A divider into a pin.** Check a divider into a pin's absolute maximum at the TVS clamp voltage, not at the nominal input.
  A surge holds the input at the clamp voltage, and the divider passes its share to the pin.
- **Back-power.** A rail part does not stop back-power through signal lines. List every path that can feed the rail. Check each
  path for isolation, voltage, direction and reset behaviour. A bus buffer with a rated Ioff isolates only the paths it covers.
  A tristate state in the tool helps only while the tool runs; it is not fail-safe at reset.
- **USB power sink.** Pick the sink controller by its fallback on a source with no PD. One kind reports the Type-C current there;
  another reports nothing. A PD source that offers only a 5 V PDO is a different case; test both. A sink controller may keep the source
  capabilities only until the next message overwrites its buffer. Read that behaviour in the chosen controller's datasheet. The firmware
  copies the capabilities on the alert. To read them again, it sends Get_Source_Cap. A soft reset is protocol recovery, not a
  query. Send a soft reset only when the PD policy engine and the controller's datasheet call for recovery.
- **The sink request current.** A sink PDO current above a common charger's rating can drop the contract to a lower voltage. Read the
  sink chip's matching rule, and its "request source current" option. Test the request against the chargers the product names.
- **The PD under-voltage alert.** Put the alert threshold below the legal load-step dip plus the cable drop. Otherwise a normal load step
  trips the alert.
- **Fan start-up.** A fan controller's duty after a power cycle is undefined until you verify it. A volatile curve can leave the fan
  at 0 % with no host. Use a part with an EEPROM, or a controller with the curve in flash. Verify a safe reset default duty.
- **Over-temperature.** Give the load an over-temperature path that needs no host.
- **Airflow.** The airflow sits where the fan curve meets the impedance curve of the whole enclosure: grille, filters and path.
  Model or measure them together. This skill carries no flow solver; a bench measurement decides. Worked example: a 1-D
  estimate gave 20 to 27 % of free flow behind 212 mm² of slots. A 30 mm fan's gross disc is about 700 mm², and a 40 mm fan's
  about 1250 mm².
- **Fan sizing.** Size the fan against the hottest part's case limit, through the real flow path. A bulk-air rise rule asked for
  about twice the flow and hid the pressure *(worked example)*. Read the heat-sink fin pressure drop at the operating point. A 1.0 mm
  fin gap needed about 129 Pa at the needed flow. A small fan stalled near 50 Pa *(worked example)*. Small fans are pressure-limited.
  Pick the fan by its pressure at the need, never by its free flow.
- **A side path beside the sink.** A bare-board bench read with no air gives the heat path beside the sink. Put it in the model.
  One sink-only model read 4 W low, because the side path carried about a third of the heat *(worked example)*.
- **The fan in its duct.** Check that the fan fits the duct in its real orientation, with every chamfer and rib of the hood. One hood
  chamfer took 4.5 mm of roof at the fan wall, and a 40 mm fan missed its hood by 8 mm *(worked example)*. Read the fan's PWM frequency
  window against the drive. One fan took 80 to 120 Hz only, and another took 20 to 30 kHz *(worked example)*.
- **Heat capacity.** Measure the load's heat capacity on the bench before you set the fan's response. On one bench, 8 W raised a
  module 11 K in 60 s, with the losses neglected. That reading, about 44 J/K, overstates C. Sensor lag flattens the measured
  slope and overstates C again. Fit the sensor lag with the net heat flow. Otherwise use an independent conservative C, from
  the masses and their specific heats. Use the worst-case net heat. The time from detection to full airflow is at
  most ΔT_margin × C_low / P_worst. That time holds the sensor lag, the command and the spin-up.
- **Sizing.** Size the electronics for the top load power. Size the heat sink for every load and ambient the product supports.
  Otherwise enforce a lower power limit, with an independent thermal shutdown.
- **Units.** Write GBd for a symbol rate and Gb/s for a bit rate, never one number for both. A PAM4 lane carries two bits per symbol.
- **Loops on a connector.** Loop a transmit pair to a neighbour lane's receive pair. Pair placement alone does not prove one-layer
  routing. Check the drawing and the whole launch and routing geometry. A checker that locks on the same pattern from any lane cannot
  prove the lane map. Challenge every physical lane on its own: a lane-unique pattern or seed, or an error injected on that lane.
  Verify the whole map: the lane order, the polarity and the direction. Match the polarity and the
  precoding per lane on the loop. Check the crosstalk between neighbouring loops against the SI budget. Take the number, value and
  placement of the coupling stages from the interface specification and the schematics of both ends. State where each path is
  coupled.
- **Pads and the stack.** A wide pad over thin prepreg can drop below the target impedance (`references/pcb-layout-dfm.md` §3).
  Connectors mirrored on both board faces set the board thickness and the termination. Read the fab's live thickness table by layer count
  before a study recommends them.
- **The controller.** A module family can carry other temperature ratings per memory option. Pick by the quantity the datasheet rates
  (ambient, case or junction) at the worst local temperature, with self-heating and margin. Never pick by the deepest stock. A part rated
  for a single reflow goes on the side reflowed last. Confirm the order with the assembler (`references/pcb-layout-dfm.md` §9). Read the
  controller's errata for its USB download path, and keep the ROM recovery path and its pins free.

## 7. Architecture and sizing rules for a next revision
Run these before the spec fixes a target or a board split. A study of §6 cites them.
- **First-time and reproducible success.** Ask the owner whether the revision may have a prototype. Without one, the study plan holds:
  a simulation of every analog risk, at least 20 % derating at the fab extremes, an isolation link on the supply and control of every new
  block, and test points on every rail. Reviews add three blind reviewers on the high-risk disciplines, a red team before each gate, and a
  fresh fix-check until no MAJOR remains. Prefer the option that builds the same on every unit: a factory cable over a hand-crimped harness.
  Size for realistic worst cases, not for stacked extreme corners. Ask the owner which disciplines keep the full rigour.
- **The connector contact limit first.** Read the mating connector's rated current per power contact and its count of power contacts
  before you set a current target. Six contacts at 1.5 A cap a port at 9 A *(worked example)*; a 12 A target died in a study after the
  target was set. Derate each part at the current it sees. A power class can carry several currents (a 50 µs peak, a sustained peak and
  the steady draw). Write the target as the class, then derive each current.
- **A board exists for a reason.** Name the reason before a study splits or removes a board. One display board existed for the display
  height under a tall section, not for its haptics. A stepped case, low where the user interface sits, removed the board and its cable.
- **The user-interface height stack.** Compute the stack before you split boards: the display, its tail and its connector, the window,
  and the tall parts beside it. A tall section in front of a low deck hides the deck from a seated user. The hidden depth is the step
  height divided by the tangent of the viewing elevation. A haptic actuator on the main board shakes the whole unit, so the tap is lost.
- **A removed switch removes a stop.** List each hard stop the switch held. Name its logic or firmware replacement, and say what the
  replacement does not cover.
- **A part change leaves old numbers behind.** Rewrite the clauses the decision names. Mark every other number derived from the old part
  as superseded, with the re-run that replaces it.
- **A decision leaves old copies behind.** When a decision lands, search every document and every yaml for each copy of the old value.
  Update them all in the same pass. One blind review found stale copies of a power ceiling, a grant rule, a switch part and a buffer
  part *(worked example)*.
- **A live lift needs sequenced pins.** A test that lifts a mezzanine connector under load is unsafe when its presence pins have the same
  contact length as its power pins. Equal pins cannot break the power before the presence signal. Remove power first, or use a connector
  with a short presence pin. Put this item in the safety review of the test plan.
- **An error budget carries every term.** A divider's temperature coefficient and a converter's offset widen a monitor's reading error.
  Every band set from that error then narrows. Search every copy of the old figure before you edit one.
- **A monitor before a protection part reads that part's loss as load**. Subtract I² × (on-resistance max + shunt) from the draw it
  reports, or move the monitor after the part.
- **A threshold band has two corners.** The earliest turn-on sits at the lowest threshold. Size a delay at the input-low minimum, the
  shortest time constant and the highest supply.
- **A one-shot fed by a hold signal fires at power-up when the button is held**. A power-on clear cannot stop it, because the hold
  edge comes later. Add an arm latch that sets only on a release.
- **Chain a reset sequence from supervisors with a stated minimum and maximum delay**. Start each stage from the one before, so the
  order holds at every corner without a race.
- **A fan sheet with no start current gives no start budget**. Stagger the starts on one switch, or read the current on the bench.
- **Keep a field that changes in use outside the checksum span of an identity block**. One torn write then cannot invalidate the
  identity.
- **A single-ended sense across a high-current return reads high by the return drop**. A monitor whose bus pin is referred to
  ground counts the return path in its voltage. Subtract I × R_return in firmware, with R_return measured per unit by a Kelvin
  read. Store it with the unit, and widen the guard by the residual.
- **An RC delay needs a discharge path that resets on supply loss**. A large RC can hold an enable high for many seconds after
  the supply drops. A quick replug then skips the delay. Use a supervisor with a stated minimum delay and an output that drops
  at once on supply loss.
- **Check an eFuse's reverse-current block against a converter in forced PWM**. Forced PWM can sink current and boost its input
  back above the source on a load release. The eFuse sees reverse current and trips. Filter its fault longer than the episode,
  or change the converter mode. Size the filter with a circuit simulation of the release.
- **State the life of every wear part in units tested**. A connector rated for a few hundred mating cycles serves that many units
  per port. Write the spare count and the swap steps into the spec. Do the same for a reference part that each test consumes.
