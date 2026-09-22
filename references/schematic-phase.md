# schematic-phase.md — G0 → G1: what the design yaml holds, the ERC gate, map checks, the G1 review pack

The schematic generator is project code (`gen/build_sch.py`); this page fixes what it must consume and produce so the gates in `docs/GATES.md`
mean the same thing in every project. The source project's generator (KiCad 10, sheet fragments instantiated per port) is the worked example; the
shapes below are the generic contract.

## 1. Design yaml — the minimum a schematic needs (`design/<board>.yaml`, `design/parts.yaml`, `design/sheets/*.yaml`)

```yaml
# design/<board>.yaml — the root: identity, libraries, sheets, root-level nets
board:
  name: <board>                     # file stem of the generated CAD project (<cad>/<board>/<board>.*)
  title: <one line>  rev: "0"  date: YYYY-MM-DD  paper: A3
  parts: [design/parts.yaml]        # part rows looked up by refdes (MPN, fab code, package, tag, DNP) — never typed on the symbol
  lib_map: design/lib_map.yaml      # MPN or refdes prefix -> symbol / footprint
  libs: {sym: [lib/<fab>/<fab>.kicad_sym], fp: [lib/<fab>/<fab>.pretty]}
  power_rails: [GND, +3V3, VBUS]    # names that get power symbols / PWR_FLAG handling
  notes: |                          # the root NOTES block (intent, key values, rework links, test points, checklist) — a review reads it
sheets:                             # one entry per sheet; refdes = sheet × 100 + n; a fragment may be instantiated more than once ({P} prefix)
  - {no: 1, name: power,  file: design/sheets/power.yaml}
  - {no: 2, name: port_a, file: design/sheets/port.yaml, prefix: PA_}
  - {no: 3, name: port_b, file: design/sheets/port.yaml, prefix: PB_}
nets: {}                            # root-level connections between sheets (hierarchical labels), by REF.PIN: NET

# design/sheets/<sheet>.yaml — one sheet or a reusable fragment
title: "{P}port"                    # {P} = instance prefix; nets without {P} are shared between instances
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

Rules the generator enforces (each a `--selftest` case): every fitted part has a `Confidence` of V or N/A (`[K]` refuses — `references/part-verification.md`);
value ↔ MPN ↔ fab code agree; every pin is connected or explicitly no-connect; refdes unique across sheets after the prefix; the symbol fields
are copied to the footprint as hidden properties (schematic ↔ board parity); UUIDs rewritten deterministically so `--check` is byte-stable; a
sheet instantiated twice is two generated sheet FILES (some CAD CLIs mishandle one file instantiated twice). Never rewrite a project file
another generator owns without re-reading and merging its part (`references/pitfalls.md` tooling/gates).

## 2. ERC gate (rule 7)

Run after every generation, with every severity on, machine-readable, zero errors:

```sh
<cad-cli> sch erc --severity-all --format json -o out/<board>/erc.json <cad>/<board>/<board>.kicad_sch     # KiCad 10 form; other CADs: the equivalent
```

Errors → fix the yaml or the generator. Warnings → fix, or one row in `docs/ERC_WAIVERS.md` (sheet, item, type, justification, decision row,
date). Add the ERC run to `gates.adopt` at G1 (`templates/project.yaml` has the commented block) so it is repeated on every adopt run and in
`git archive HEAD`. Export the netlist in the same step (`<cad-cli> sch export netlist --format kicadxml -o out/<board>.xml …`): `paths.netlist`
feeds the `netlist_net` checks of `scripts/traceability.py`.

## 3. Map checks

A "map" is any table in the spec or in `design/` that says which pin, address or connector position carries what: an MCU / bridge GPIO map, an
I²C address map, a connector pinout, a switch/strap table, a test-point map. **Map checks** = a project script (`gen/check_maps.py --check`) that
reads every map and the exported netlist and asserts both directions: every map row is present in the netlist as written (net name on that pin;
address on that device), and every relevant netlist net appears in exactly one map. Output `out/<board>/check_maps.md` (one table per map: row,
netlist evidence, OK/FAIL) — a G1 prerequisite in `docs/GATES.md` and a `gates.adopt` line. A map row the spec names but the design does not
implement is a CC row (rule 2), not a silent omission.

## 4. The G1 review pack (`out/G1/`, generated, committed)

| File | Produced by | Why the reviewer needs it |
|---|---|---|
| `<board>.pdf` | `<cad-cli> sch export pdf` | the schematic as drawn, every sheet |
| `<board>.xml` | `<cad-cli> sch export netlist --format kicadxml` | machine-checkable connectivity |
| `bom.csv`, `procurement.csv` | the project's BOM exporter | every fitted part with MPN / fab code / tag; DNP excluded |
| `erc.json` + `docs/ERC_WAIVERS.md` | §2 | zero errors, justified warnings |
| `check_maps.md` | §3 | maps vs netlist |
| `EVIDENCE.md` | the generator | which yaml revision / commit produced the pack; md5 of every file above |
| `REVIEW_NOTES.md` | hand-written, short | what changed since the last round, what the reviewers should weigh |

The hand-off for the G1 round (`templates/REVIEW_HANDOFF.md`) lists these files with md5 in §2; `scripts/handoff_header.py` still reports the
board as MISSING at G1 (no routed board yet) — that is expected and said in the hand-off. Blind review roles at G1: the `board` role set of
`workflows/blind-deep-review.js` minus layout/silk/fab-package (no copper yet), or the same nine roles with briefs scoped to the schematic.

## 5. G0 → G1 in order

1. G0 cell written by the owner → 2. `design/*.yaml` from SPEC (every spec value that must change → CC row OPEN first) → 3. `gen/build_sch.py`
(`--check` green, ERC zero errors, netlist) → 4. map checks → 5. G1 pack → 6. `scripts/traceability.py` entries for every spec requirement now
landing in the yaml (stage `schematic`) → 7. freeze, hand-off, blind round (SKILL §5), merged report `docs/reviews/G1_merged.md` → 8. REQUIRED
items applied, regenerate, re-run 3-6 → 9. ask for the G1 cell (SKILL §1.1). Layout CAD starts only after the cell exists.
