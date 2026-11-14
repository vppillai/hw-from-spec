# pcb-layout-dfm.md — kickoff → G1: layout-forward design (§0); G1 → G2: the PCB build rules, the layout chain, the power-path proof (§1.5) and the adopt gate

Every quantitative rule below carries one of four tags, so a reader knows what moves it:

| Tag | Meaning | What changes it |
|---|---|---|
| **[checker]** | what the fab's DFM viewer or the CAD DRC grades (a number the mirror reproduces) | the fab changes its viewer → re-copy `20-design/dfm_thresholds.json` |
| **[fab capability: URL, date]** | a published limit of the fab, fetched live and dated | the fab's capability page → re-fetch before every quote |
| **[physics]** | a material or process fact independent of the vendor | never silently; a decision row with a source |
| **[owner choice]** | a bar the owner set (recorded as a D row from the kickoff questionnaire) | the owner |
| **[convention]** | a shape the scripts and templates rely on | a decision row + the generator |

The worked example throughout is JLCPCB, numbers fetched **2026-09-13** from `jlcpcb.com/capabilities/pcb-capabilities` and the PCBA
capability page; they are the values that were live then — **fetch the current page before using any of them** (`references/fab-dfm.md` §7).
The design margin rule for every fab number: **design strictly greater than the published minimum** (the viewer grades a value EQUAL to its
warning threshold as Warning) — limit + 0.01 mm for copper rules, one full step for drills.

## 0. Layout-forward design: kickoff → G0 → G1

Part choice, pin maps and the schematic set most of a board's routability. A router cannot undo them. So plan the layout from
kickoff, and gate it at G1 with numbers. SKILL §1.3 holds the step. This section holds the method.

**Never cut a feature for layout** **[owner choice]**. Change the placement, a pin map, a package, the stack-up or the board
size instead. A feature cut is a spec change: an OPEN decision row for the owner (SKILL §3, rule 2). It is never a layout fix.

*Worked example.* One dense 6-layer board stalled near 71 % routed after four scripted router tries. Five causes were set
before layout. A buck controller had its gate pins on the side away from its FET pair. Only 5 of its 16 gate pins had a
legal via site. Two common-mode filter capacitors sat on stubs of 15 and 26 mm against a 3 mm limit. Damper copper of tens of
mΩ broke a power model with a budget near 10 mΩ. Scripted supply feeds closed lines in. A protection array was not between
the connector and the protected part. A late pin re-assignment gained nothing. Each subsection below catches one of these causes
before G1.

### 0.1 Budgets at kickoff (kickoff B9 to B11) **[owner choice]**
- **Board size and layers.** Record a base outline and layer count. Record the cost of each fallback step.
- **The fallback order.** This is the one list; other sections point here. Step 1 is placement. Step 2 is the pin map, inside
  the B11 swap policy. Step 3 is the package. Step 4 is more layers. Step 5 is a larger outline by a stated step.
  Steps 1 to 3 leave the B9 budget unchanged. B9 sets the order of steps 4 and 5; the recommended order is layers first.
  A fixed envelope in kickoff I1 removes step 5. A B9 answer that fixes the layers removes step 4. A feature cut is never a fallback.
- **The routability gate thresholds.** Kickoff B10 sets them. The defaults are in the table of §0.8.
- **The swap policy.** Kickoff B11 says if pin swaps and part swaps are allowed for routability. Each swap is a CC row.
  A swap inside one function group (two GPIOs, two lanes of one bus) or to a pin-compatible part is the recommended scope.
  A swap that changes a spec value still follows rule 2.
- **The trigger.** A row that still fails on two placement variants takes the next fallback step. More router passes do not fix a
  cause that the floorplan set.

### 0.2 The floorplan, before the G0 ask **[method]**
- Generate the floorplan from a yaml (`20-design/<board>_floorplan.yaml`). Never draw it by hand in the CAD.
- It holds the outline and the fixed parts: connectors, holes, a cage, anything the case or the spec pins.
- It holds the keep-outs on each side and on each layer they cover: the case, the mounting hardware, the connector drawings,
  isolation and creepage.
- It holds one region per function block. Give each region an area and the parts it holds, with their courtyard sizes.
- The fill of a region per side is the sum of its courtyard areas over its area. The recommended limit is 60 %. Use 45 %
  for a region with a part of 0.5 mm pitch or less.
- Place each region so that the pin rows of its dense parts face the regions they connect to.

### 0.3 Channel count per region and per layer **[method]**
- A *cut* is a line across the floorplan between two regions, or across the narrowest neck of a region.
- List the nets that must cross each cut. Take them from the block diagram before the schematic and from the netlist after it.
- Channels on one layer of a cut = the usable cut length divided by the routing pitch, rounded down.
- The pitch is the track width plus the clearance of the net class. A differential pair takes 2 w + s plus one clearance
  on each side.
- The usable length leaves out the rows of vias, power necks and keep-outs on that layer. A reference-plane layer carries 0 signal
  channels.
- Draw each scripted supply feed and each power neck before the count (§1.4).
- Channel use = the nets that cross over the channels available. Gate it per cut, over the layers the nets may use, and
  per layer.

### 0.4 Escape count per dense part **[method]**
- A dense part has a pitch of 0.65 mm or less. A part whose pins must change layer next to the body is dense too.
  Power-stage controllers and multi-row connectors are the usual cases. The fill limit of §0.2 uses a tighter pitch, 0.5 mm.
- For each pin row, count the pins that need a via inside the escape distance. These are the pins whose nets leave on
  another layer. The escape distance is 3 pitches of the row from the pad edge, unless the floorplan yaml gives a value.
- Count the legal via sites inside the escape distance on the side of that row. A legal site is a free circle (§2), clear of
  pads, rule areas and silk text.
- The escape ratio of the row = legal sites over pins that need a via. In the worked example, the gate row had 5 sites for
  16 pins, a ratio of 0.31.
- Fix a low ratio with the fallback order of §0.1. Rotating the part is part of step 1. Via-in-pad is a decision row (§5).

### 0.5 Power-stage templates at G0 **[physics]**
- Draw a placement template for each switching stage before the G0 ask. Take its numbers from the controller's layout guide.
- The template holds the input capacitor, the switch pair, the inductor, the output capacitor, the controller or driver and
  the sense parts.
- Mark three loops on it. The *hot loop* runs from the input capacitor through both switches and back. The *gate loop* of
  each switch runs from the driver pin to the gate and back from the source to the driver return. The *sense loop* runs
  from the sense element to the amplifier pins as a Kelvin pair.
- Write a length or area budget for each loop. Copy the number from the layout guide, or derive it in a calculation row.
- Turn the controller so that its gate pins face their switch pair. Count the escape of the gate pins (§0.4).
- When a template does not fit its region, change the region, the part or the stack-up before G0.

### 0.6 Placement budgets that feed the models **[physics]**
- Give a budget row to each part whose distance or copper changes a model result. Decoupling at power pins, damper branches,
  filter parts, protection arrays, terminations, coupling capacitors and crystals are the usual parts.
- A row holds the part, its node, the maximum distance in mm, and the maximum copper R in mΩ and L in nH. State R and L at the
  hot and the cold corner. Name the model that reads the row and the source of each number.
- The power model and the SI model take the budget values as their parasitics. A model pass at the budget values is the rule
  that placement and routing then hold (§1.1, the damper bullet).
- A shunt part on a fast line has a stub budget from the SI model (`high-speed-si.md` §5). In the worked example, the filter
  stubs were 15 and 26 mm against 3 mm.
- Put a flow-through protection array next to the connector, between the connector and the protected part (§1.1).

### 0.7 Pinouts for escape and pair order **[method]**
- Choose the connector pinouts and the dense-part pin maps with the floorplan open, between G0 and G1.
- Order each pin row to match the order of the pins it faces. Each pair crossing needs a pair of vias in the budget.
- Check the pin order around each package (§4) and count a connector map by position per row (§2.1).
- Make the swaps that kickoff B11 allows before G1. After placement, a swap frees one window at best. In the worked example,
  a late re-assignment gained nothing.

### 0.8 The routability gate at G1 **[owner choice]**
The schematic does not freeze until this gate passes. Do not ask for the G1 cell before it passes. Generate
`80-reviews/G1/routability.md` from the floorplan yaml and the netlist. Kickoff B10 sets the limits. The defaults:

| Row | Default limit |
|---|---|
| region fill per side | ≤ 60 %; ≤ 45 % with a part of 0.5 mm pitch or less |
| channel use per cut, over the allowed layers | ≤ 70 % |
| channel use per layer on a cut | ≤ 85 % |
| escape ratio per pin row of a dense part | ≥ 1.2 |
| power-stage templates | one per stage; each loop inside its budget |
| placement budget rows | each inside its budget; each model passes at the budget values |
| protection and filter order | connector, protection array, protected part; the array next to the connector; each stub inside its budget |
| supply feeds and power necks | drawn before the channel count |

- Fix a failed row with the fallback order of §0.1. Never fix it with a feature cut.
- When a row still fails after the last fallback, stop. Ask the owner with the numbers of each row.
- At G2, a router that stalls after its plateau (§1.2) sends the work back to this table. A cause that was set before layout
  needs a floorplan change, not more router passes.

### 0.9 G1 review checklist: layout-forward
1. Does the floorplan yaml hold every fixed part, every keep-out and every region with its fill per side?
2. Does each cut list its crossing nets, with the channel count per layer and the feeds drawn?
3. Does each pin row of each dense part show its escape ratio from legal sites?
4. Does each switching stage have a template with its three loops and their budgets?
5. Does each placement-critical part have a budget row, and does each model pass at the budget values?
6. Is each protection array next to the connector, between the connector and the protected part?
7. Were the allowed swaps made before G1, each with its CC row?
8. Does each failed row name its fix, and is no fix a feature cut?

## 1. The G1 → G2 chain (inputs, outputs, gate, decider)

| | |
|---|---|
| **Inputs** | the G1 schematic of record (yaml + generated CAD), `20-design/<board>_board.yaml` (outline, stack-up, design rules, net classes, keep-outs, `dfm_accepted`), `20-design/placement.csv`, `20-design/dfm_thresholds.json`, the fab's rotation table (`20-design/<fab>_rotation.yaml`) |
| **Generators (project `gen/`)** | `place_pcb` (placement CSV → footprints, rule areas, canary) → router (`route_*`, the router session file is the record) → post-pass (stub snap, staircase merge — scripted, never hand edits) → `silk_pass` → `export` (Gerbers/drill/pos, DRC json, parity, route quality, DFM items) → `panelize` → `fab_package` |
| **Outputs** | `30-board/kicad/<board>/<board>.kicad_pcb` (board of record, md5 keys everything), the router session (`*.ses`/`*.dsn`), `80-reviews/G2/` review pack (§1.3), `30-board/layout/dfm_items.json` + `30-board/layout/dfm.json`, `30-board/fab/<rev>/` package (board_id.txt carries the md5) |
| **Gate** | SKILL §6 adopt rule: DRC 0 errors / 0 unconnected, **0 warnings unless a dated waiver row** (§9), schematic parity 0, canary fires exactly once, route quality 0 unjustified HIGH, fab DFM mirror 0 open, silk check 0, every `--selftest` / `--check` green, clone gate on `git archive HEAD`, visual inspection round merged |
| **Decider** | the owner writes the G2 cell after one review round (`board` role set + `routing-inspection.js`) is merged; the agent asks (SKILL §1.1) |

### 1.1 Placement CSV **[convention]**
`20-design/placement.csv` has the columns `ref, x, y, rot, side, locked, group, note`. Positions are mm in the board frame, with the drill/place
origin as origin and Y up. Rotation is in CCW degrees. `side` = top/bottom, `locked` = the part is fixed for the router, `group` = the placement
cluster (connectors, power, mcu, …). The
generator refuses a refdes missing from the schematic or a part outside the outline; a part the spec pins (connector positions, mounting holes,
the cage) is `locked: true` with the spec section in `note`. Placement is regenerated from the CSV — the CAD GUI is never the source.
**A packer that places by outline area or wire length does not leave routing channels** **[method]**. A packer here is a script
that proposes placement CSV rows. Such a packer leaves no rows of via sites through a dense fan-out. It does not hold the
decoupling at the power pins either. Track three placement predictors per variant: the via-site count (§2), the unrouted count
after one fixed router pass, and the total wire length. Stop the variants when three in a row change each predictor by less
than its run-to-run spread. Then place the dense bands by hand-guided rows. A dense band is a strip of fine-pitch parts and
their fan-out. A hand-guided row is a CSV row whose position the designer chooses, with `locked: true`. Place the rows of
via sites first, then the decoupling at the pins. Then run the router again.

**Put a flow-through protection array next to the connector, between the connector and the protected part** **[method]**.
In a flow-through array, each line passes straight over its pad, with no stub. With the
connector and the protected part on one side of the array, each line goes out and comes back. That band then needs about twice
the width. The out-and-back stub also adds inductance and weakens the clamp.

**Put the routed copper of each damper branch into the power model at placement** **[physics]**. A damper branch is a
series resistor and capacitor that damps a rail resonance. The power model is the rail's impedance or transient
simulation. The branch node is the point where the branch joins the rail. The tap is the track from that node to the
damper. With a 0 Ω link, the capacitor ESR is the only designed damping resistance. The tap copper, the vias and the
link then add to it in series. Model their resistance at the hot and the cold corner before you fix the tap width. Add the
tap inductance too, because it narrows the band where the damper works. Size the damper site and its distance from the
branch node at placement, not at routing. In one model, tens of mΩ of copper met a budget near 10 mΩ per branch. A pass
became a fail *(worked example)*.

**Give each long exit track a row with a free exit** **[method]**. An *exit track* must leave a column of parts to reach
its branch. Place the parts with long exit tracks in rows whose exit side is free on that layer. Turn a two-pad link so
that its exit pad faces its branch. Then the track does not run round the part. Choose the row order for each board from
its exit-track lengths.

### 1.2 Router session **[convention]**
The routed board + the router's session file (Freerouting `.ses` with its `.dsn`, or the equivalent) are the artefacts of record; routing is
never re-run to reproduce them. Re-import (`--import-ses`) is the replay. Keep-outs and
net classes must be exported into the router input — grep the DSN for them after any flag change (`references/pitfalls.md` kicad).
Judge a stack-up by its routed percentage only after the router has plateaued. Run it until the unrouted count stops falling
over several passes, and read the pass log, not the clock. A 40-minute limit on one dense board tested one pass, not the
rip-up *(worked example)*. Skip the optimiser pass, which adds no connections. A low routed percentage is a screen: confirm
the bottleneck by hand before you change the stack-up.

**Check that the router repeats before you compare two runs** **[method]**. A multi-threaded pass or a time limit can give a
different result for the same board. First run one thread with a pass limit, not a time limit (`agent-ops.md` §5). Run the
same input twice. Compare the session-file hashes, not only the unrouted counts. If the hashes differ, run a scripted change
three times or more on each side. The change counts only if the medians differ by more than the run-to-run spread. The
session of record stays the record.

### 1.3 The G2 review pack (`80-reviews/G2/`, generated, committed)
| File | Produced by | Why the reviewer needs it |
|---|---|---|
| `<board>.kicad_pcb` md5 + `board_id.txt` | export | identity: the board of record |
| `drc.json` + `drc_summary.md` | `<cad-cli> pcb drc --severity-all --format json` | 0 errors / 0 unconnected / 0 warnings-or-waived, with the canary line |
| `parity.md` | export (schematic ↔ board field + net diff) | 0 differences |
| `route_quality.md` | `gen/route_quality.py` | per-net table, HIGH list with justification rows |
| `dfm.json` / `dfm_items.json` | measurer + `scripts/dfm_check.py` | fab DFM mirror 0 open; accepted items by refdes with reason |
| `silk_check.md` + silk PNGs | silk pass | geometry + a READ legibility pass |
| `gerbers/`, `<board>.drl`, `pos.csv`, `bom_jlc.csv`, `cpl_jlc.csv`, `rotation_log.csv` | export | what the fab receives; rotation offsets applied per footprint listed for the reviewer |
| `renders/` (top, bottom, iso, opaque background) + `tiles/` (≥ 40 px/mm) | render + tiler | the visual gates read images |
| `EVIDENCE.md`, `REVIEW_NOTES.md` | generator / hand-written | md5 of every file above; what changed since the last round |

### 1.4 Check reach before you count channels **[method]**
A free channel helps only if the lines can get into it. Check reach before you count channels or change a line order.
Terms: a *window* is a gap in copper or parts that a group of lines must pass. A *strip* is a free band you plan to use for
new lines. The *source* is the part where the lines start. A *free region* is the copper-free area on one layer. Shrink it
by the clearance plus half the track width. A *power neck* is a narrow part of a power pour. A *supply feed* is a scripted
power track.
- **Before a line-order change at a window, trace each pad's free region on its layer.** Other lines, a power neck and a
  ring of vias can block a pad on all sides but one. Then no reorder frees that pad. Three changes can free it. One is a
  move of the copper that blocks it. The others are a new via site and a moved part.
- **Before you free a strip for new lines, test reach from the source.** Find the free regions on each layer. Join two
  regions only at a via site (§2) that is free on every layer the via crosses. Then check that the source pads and the
  strip are in one joined region. A strip that joins only the target side adds no path.
- **Draw each scripted supply feed before a channel count.** A feed can turn round a column of parts. On that layer, it
  then blocks every line inside the turn. Count the channels with the feed drawn.
- **Draw a supply feed to each closed-in part.** Scripted lines can close in a part. It is closed in when no free
  region joins its supply pads to the supply. The router can leave those pads open on repeated runs. Draw the feed with
  the lines that close the part in. Then trace each supply pad's free region again (first bullet).
- A flow-through protection array is a placement rule (§1.1). It also sets the width of the band through it.

### 1.5 Power-path proof against the routed copper **[method]**
A rail must stay inside its window at the load. The power model reads the copper resistance of each path from a record row.
Terms: a *path row* gives the copper resistance from the source to one model node. The *static window* is the allowed band at
a fixed load. The *transient window* is the allowed band during a load step. The *release top* is the overshoot above the
set point after a load release. A *grant* is the power level that the source allows a load.
- **Count path resistance with a resistor network, not with squares.** Parallel vias, stubs and vias in pads make a squares
  count wrong in both directions. Grid the copper of the supply net and its return net into resistors. Include each via
  barrel. Solve the node voltages with a small linear solve. Read the resistance between the two ends of the path. Halve the
  grid once. The value must hold.
- **End each path proof where the circuit model puts its node.** A proof to the pour edge leaves out the copper to the pin or
  the capacitor. Include the return path and the copper temperature of the hot corner. One tap read 10 mΩ to the pour edge.
  To the capacitor, with the return and the hot corner, it read 13 mΩ, and the model failed *(worked example)*.
- **Check each path row against the routed copper as soon as copper exists.** A row that assumes a plane can hide the real
  track. One rail row assumed a pour on an inner layer. The routed rail was five times that value, and the branch copper came on
  top. The static window failed *(worked example)*.
- **Build a what-if copper plan through the generator before you trust it.** Hand-drawn boxes hide necks and junctions. One
  built plan lost about 1 mΩ on one branch to a narrow junction. The boxes did not show it *(worked example)*.
- **Split a branch resistor at the capacitor node before you judge a load-step edge.** Copper before the node slows the dip. Copper
  after the node adds to the pad drop. Read the split from the routed board, not from an estimate.
- **Sweep the shape of a per-branch budget before you quote it.** A budget vector scaled as one unit can mislead. One model
  failed with one heavy branch and two light branches. It passed with a uniform value of a similar total. The heavy branch set
  the limit *(worked example)*.
- **Give the transient model the same routed copper as the static window.** A transient run that keeps an old path row says
  nothing about the board. One run passed with the old row. With the routed copper, it failed by tens of mV *(worked example)*.
- **Hold the operating point constant in an RSS judgement.** Fix the load, the temperature and the set point. Combine by RSS only
  the tolerance limits that are independent. Add the correlated and the one-sided terms linearly on top. A carried budget
  can itself be a linear sum of terms. Split it into those terms before the RSS.
- **A trimmed set point has a ceiling.** The ceiling is the window top, less the reading error, less the release top. Check the
  release top before you raise the set point for the static window. Check that the regulator's trim range reaches the new
  point from its low raw corner.
- **Make each gate around a trim target at its ceiling one-sided.** Accept readings from the target down to the lower limit
  only. Aim the trim one reading error below the target. A two-sided gate lets a unit sit above the target. That spends the
  top margin.
- **A set point per load grant must hold the release top of every lower grant.** A load with a high grant can still draw at a
  lower grant and release from there. A low-resistance path can give a higher release top than the nominal path. Run a
  low-resistance path row before you trust a zero top margin.

G2 review rows for the power path:
1. Does each path row come from a resistor-network solve of the routed copper, with the return net?
2. Does each path row end at the node that the circuit model uses?
3. Do the static and the transient model read the same path rows of record?
4. Is each branch resistor split at its capacitor node?
5. Does each RSS hold the operating point fixed, and stack the one-sided terms linearly?
6. Does each set point hold the release top of every lower grant, on a low-resistance path row too?
7. Is each gate around a trim target at its ceiling one-sided?

## 2. Stack-up and copper weight
- **Stack-up = the fab's named template, copied into the CAD's physical stack-up** **[fab capability]**. The fab publishes templates per
  layer count / thickness / outer / inner copper. JLC 2026-09-13: `JLC04162H-7628` = 4 layers, 1.6 mm, 2 oz outer, 0.5 oz inner, 7628 prepreg
  0.2104 mm, core 1.065 mm, Dk 4.4 / 4.6; total 1.656 mm. Record the template name in `20-design/<board>_board.yaml` and on the order sheet;
  the same template is selected on the quote form.
- **Copper weight is an owner choice with consequences** **[owner choice]**. Heavier outer copper (2 oz) buys current capacity. It costs
  minimum trace/space: JLC 0.15/0.15 at 2 oz vs 0.09/0.09 at 1 oz. It costs mask dam width: 0.20 vs 0.10. It also costs the fab's impedance
  calculator support: JLC's supports 1 oz only (2026-09-13). Inner copper default 0.5 oz **[fab capability]**; 1 oz inner changes prepreg/core
  thickness and therefore impedance geometry — pin one value in the spec before layout.
- **Check the via sites against the copper weight before placement** **[method]**. A via site is a spot where a via fits with
  its clearance to all other copper. Its free circle is the via pad plus twice the copper-to-copper clearance at that copper
  weight, plus any annular-ring growth the fab asks. Read the clearance from the fab's live table (§4). Count the vias the
  netlist needs under each dense part's fan-out, and compare with the free circles that fit between its pads. Do it before the
  copper weight is fixed. One dense four-layer logic board on 2 oz outer copper ran out of via sites under its dense parts, and
  a larger outline did not help *(worked example)*. §0.4 gates this count per pin row at G1.
- Thickness tolerance ±10 % at ≥ 1.0 mm **[fab capability]** (1.6 → 1.44…1.76): a press-fit connector or a card-edge must accept the range.
- Material grade / Tg is selected at order **[owner choice]** (JLC impedance profiles assume a TG155 laminate).
- **Fab capabilities move** **[fab capability]**. Read the live capability page before a study recommends a stack. Worked example, JLC
  2026-10-24 (that fab's table, that day; verify it live). That fab back-drilled boards of 4 to 32 layers, from 0.8 mm thick.
  For its back-drilled boards on that date, 2.5 mm and thicker needed 12 layers or more, at ±10 %.

### 2.1 Fab tolerances against vendor limits **[fab capability]**
- Read the fab's extremes against every vendor minimum before the stack-up is fixed. A 1.6 mm board at −10 % is 1.44 mm, exactly one
  press-fit connector's minimum *(worked example)*. A ±0.075 mm hole position is wider than a fine connector's true-position tolerance.
- The fab's page may not state the finished copper tolerance, the dielectric thickness tolerance or the layer registration. Ask for them at
  the quote. Assume −20 % copper until the answer arrives.
- Heavier inner copper changes the prepreg. One fab's 2 oz inner templates grew the outer prepreg from 0.20 to 0.29 mm, and a 90 Ω pair
  widened from 0.28 to 0.38 mm *(worked example)*. Read the plies before you trade inner copper for current.
- Start a board-to-board alignment budget at the contacts, not at the drilled holes. A peg that floats in its hole moves the connector
  off its own holes. A REF dimension on the print caps how far the budget can tighten; ask the vendor for its tolerance.
- Drill the tooling holes in the same program as the connector peg holes. Gate the in-program hole position at first article. A budget that
  rests on a written fab statement stays open until the statement arrives (`references/vendor-review.md` §7).
- Put each term of an angular budget on its own lever: peg play over the peg span, pin play over the tooling-pin span.
- Count a pin map by position per row, not by pins. One map held the right pin count and still left a power block short of pairs.
- A connector on the bottom face mirrors x in the top view. Check in the generator that pin 1 lands on the side of its nets.

## 3. Controlled impedance and differential pairs
- **When it is required** **[physics]**: any pair whose length exceeds ~1/10 of the signal's rise-time wavelength on FR-4. Examples are USB 2.0
  90 Ω pairs longer than a few cm, any multi-Gb/s lane, and RF. Short pairs (a few cm) care more about skew and stubs than about ±10 %
  impedance. Write the requirement per net class in the spec (`R-Exx: 90 Ω ±10 % differential`), or the row "no controlled impedance — every pair < N cm"
  as a D row.
- **Recording the calculation** **[convention]**: use the CAD's calculator on the fab's stack-up (coupled microstrip / stripline with the mask
  layer). Cross-check it with the fab's own calculator where that calculator supports the copper weight. The result (w / s / layer / reference
  plane / Z / tool) is a row in `20-design/<board>_board.yaml net_classes` with the source, and the pack quotes it. Keep w ≥ 0.20 mm so the
  fab's ±20 % width tolerance **[fab capability]** stays inside ±10 % Z.
- Differential rules the CAD enforces: pair gap, uncoupled length ≤ N mm, skew ≤ N mm, no via stubs on the pair, reference plane continuous
  (an In2 signal over an In1 antipad edge is a route-quality HIGH, §10). Impedance control is an order option **[fab capability]**: ask for it
  on the quote form; if the form refuses it for the copper weight, that is a decision row, not a silent drop.
- **Connector pads** **[physics]**: a wide pad over thin prepreg can drop below the target impedance. A thinner prepreg lowers
  the pad impedance further. Pick the prepreg for the pad as well as the trace. A void under the pad changes the return path.
  Model the whole launch with the live stack-up and the connector model: εr, copper, mask, reference and pour gap.
- Multi-gigabit lanes take a tier first (`references/high-speed-si.md` §0.0). A short lane that follows its layout guide closes
  on the calculator row, the length and skew rules and the vendor checklist. A long, marginal or fast lane needs a field solve or the full chain.
- **Gaps in a via fence or ground ring** **[physics]**: a gap acts as a waveguide. Keep its width well below
  c / (2 f sqrt(εr)) at the highest frequency of interest (`references/high-speed-si.md` §3).

## 4. Trace / space / via / annular / drill minimums vs the fab table
Copy the fab's table into `20-design/dfm_thresholds.json` (source URL + date) and design strictly greater **[checker]**. Worked example
(JLCPCB, 2 oz outer, multilayer, 2026-09-13) **[fab capability]**:

| Rule | Fab limit | Design value (limit + margin) |
|---|---|---|
| track width / spacing | 0.15 / 0.15 | DRC min 0.16 / 0.16; net-class default 0.20 |
| via drill / pad | 0.15 possible, 0.20 preferred, < 0.30 surcharge; ring ≥ +0.10 | default 0.30 / 0.62 (ring 0.16); constrained 0.25 / 0.50 only where a fan-out needs it, ordered with the matching min-via option |
| PTH annular ring | 0.254 (2 oz) | ≥ 0.30 |
| hole-to-hole | 0.20 via / 0.45 PTH | 0.50 |
| hole to copper (inner) | 0.20 via / 0.30 PTH | 0.30 |
| PTH hole to track | 0.28 min, 0.35 recommended | 0.35 |
| copper to routed edge / to V-cut | 0.20 / 0.40 | 0.30 / 0.50 |
| PTH hole tolerance | +0.13 / −0.08; press-fit option ±0.05 (multilayer ENIG, circular, listed in the remark) | press-fit holes per the connector drawing, named in the order remark |
| same-net spacing | 0.25 | 0.25 (no CAD rule — avoid parallel same-net slivers) |
| min SMD pad | 0.25 × 0.25 | never below the datasheet pad |

- **Judge a space rule with nets** **[checker]**. Assign the net to every pad first. Then judge spacing between unlike nets only. A
  net-blind check fails a pad for the wrong reason. When the check gains nets, re-read every verdict and exemption that rested on it.
- **A pad-size trial checks the neighbours, not only its ring** **[checker]**. A larger peg or tooling pad can come within the space rule
  of the next contact row. Joining the pad to that contact's net removes the rule; prove the net from the pinout first.
- **Rate a via's current on the plating inside the drilled hole** **[physics]**. The copper area is π (r² − (r − t)²). Plating drawn
  outside the hole overstates the current by about 10 % for a small drill.
- **A study board goes stale silently** **[convention]**. A generator with no `--check` tied to a changed key keeps the old copper. Give
  every study board a `--check` on each key it draws. Regenerate each board when a value moves.
- **Test a net-class clearance against the connector land before you set it** **[checker]**. A maker's land pattern can put two
  pads closer than the class. The class can never hold there, so keep the clearance the land allows.
- **Check the pin order around each package before you write a one-layer rule for a pair** **[physics]**. Two chips on the same
  face that both number their pins counter-clockwise cannot join a D+/D- pair on one layer: the pair must cross once.
- **Neck a wide line on fine-pitch pins along the pad axis** **[checker]**. When two pairs leave adjacent pins of one package,
  keep both necked until they part.
- **Count packages, not symbol units** **[convention]**. A multi-unit symbol lists one row per unit. Key a height, area or part
  count on the reference designator.

## 5. Via-in-pad and tenting
- Tented (mask-covered) vias by default, ≤ 0.5 mm, none inside SMD pads **[fab capability + convention]**; via-in-pad needs the fab's filled-and-
  capped process (an order option and a surcharge) — a decision row, never an accident of a fan-out. Mask-plugged vias: no opening either side,
  ≥ 0.35 mm from other mask openings (JLC).
- A via under a silk text cell is a silk defect (§11); a via in a fiducial's clearance ring is a placement defect.
- A via inside an SMD pad joins the pad on the outer layer only **[checker]**. The DRC then reports each one as dangling, a warning.
  End a track segment at each via centre to give it a joint of its own. Make the dangling-via class a gate failure.

## 6. Thermal reliefs and teardrops
- **Thermal reliefs** **[physics + owner choice]**: always on PTH pads into pours. A solid connection wicks heat from the joint and tombstones
  a hand-soldered pin. On SMD pads into pours, the default is solid for power/GND pads under ICs (thermal path) and relief spokes on small
  passives (reflow balance). Record the choice per zone in `20-design/<board>_board.yaml zones`, with spoke width ≥ the track minimum + margin.
  A class clearance larger than the fill's zone clearance is unenforceable — write the as-built geometry into scoped rules
  (`references/pitfalls.md` kicad).
- **Teardrops** **[owner choice]**: on at the track/pad and track/via junctions of the fine-pitch escape when the ring is at the fab minimum.
  They buy annular-ring margin against drill wander. Record them as a generator flag so the replay reproduces them. The DRC and the fab mirror
  run on the board WITH teardrops, because teardrops change spacing.

## 7. Solder mask, paste and stencil
- **Mask expansion 0 (pad-defined openings)** **[fab capability, LDI]**; keep ≥ 0.09 mm between an opening and a neighbouring trace (JLC).
- **Mask dam (bridge) minimum** **[fab capability]**: 0.20 mm at 2 oz any colour; 0.10 mm at 1 oz for standard colours, 0.13 black/white
  (JLC 2026-09-13). Below the dam minimum the fab gangs the openings — a 0.4 mm pitch QFN with 0.2 mm pads at 2 oz has exactly 0.20 → zero
  margin: state "gang opening accepted" or move to 1 oz as a decision row. **Pin mask = copper on fine-pitch parts**; a +0.05 expansion cuts
  the webs below the minimum (`references/pitfalls.md` silk).
- **Paste** **[convention]**: paste = pad by default. Reduce paste (−10…−30 %) on large thermal pads. On QFN centre pads, windowpane the paste
  into 4–9 apertures at ≤ 50–70 % coverage **[physics]**, or the part floats / voids. No paste on NPTH annuli or test pads. Export the paste
  layer on both sides for a two-sided assembly.
- **Stencil thickness** is the fab's choice for its own assembly (JLC prices one stencil per side). State it only when the design needs it
  (0.10 mm for 0.4 mm pitch, 0.12–0.15 mm general) **[physics]**, as a remark, and only when the fab lets the customer choose.
- Exposed copper area above the fab's percentage (JLC: 30 % for ENIG) is a surcharge **[fab capability]** — keep pours under the mask, expose
  pads, test points and designed artwork only.

## 8. Component size and link-part policy **[owner choice]**
Defaults the questionnaire proposes:
- **No 0201** (Economic PCBA minimum is 0402 at JLC; 0201 is Standard-only and hand-rework-hostile); **0402 minimum**, 0603 where the value is
  likely to be reworked (pull-up options, series terminations near an edge).
- **Signal 0 Ω links: 0603; power-path links: 1206** (a named basic-library code of the fab). The size is the current rating and the
  rework handle. A link that may be cut later is a **bridged solder-jumper net-tie footprint** (allowed, DFM-clean), never a 0 Ω resistor
  drawn as a wire.
- Every fitted part is rated for the fab's reflow profile **[fab capability]** (JLC Economic 255 ± 5 °C not adjustable; Standard 240 ± 5 °C).
  The parts-vetting checklist carries "≥ 260 °C peak per J-STD-020". A part at zero margin gets a bake / profile remark.
- Basic vs extended library: each unique extended part costs a feeder fee **[fab capability]** — the BOM report counts them; prefer basic /
  preferred parts for jellybeans (a stock floor per code is an owner choice, `references/part-verification.md`).

## 9. Two-sided SMT assembly
- The **owner chooses** single / two-sided **[owner choice]** (two-sided buys 30–40 % board area). Two-sided implies the
  fab's Standard tier (setup + second stencil fees) and requires edge rails / fiducials. A press-fit or THT step then needs a **fixture band**
  on the bottom: no bottom part within ±2 mm of a press-fit row over its length, and boss / screw-head keep-outs drawn on BOTH sides.
- **Part height per side** **[physics + convention]**: the side that reflows first (usually the lighter, smaller-part side) reflows a second
  time upside down. Parts heavier than ~30 g per square inch of pad area or tall parts (electrolytics, inductors > 4.5 mm) go on the second
  side or get glue. Glue is a remark, and the fab decides. Record per-side max height in the board yaml, because the case reads it.
- THT: unused PTH stay solder-free (say so in the remark); hand-installed parts are DNP in the BOM and marked on the fab drawing.
- A part whose datasheet allows a single reflow goes on the side reflowed last. A radio module is the usual case. Confirm the order
  with the assembler, and check its profile against the part's peak temperature and time above liquidus.

## 10. Polarity, rotation and the CPL **[convention + fab capability]**
- CPL file: `Designator, Mid X, Mid Y, Rotation, Layer`, mm, 4 decimals. Position = pad-bounding-box centre relative to the drill/place origin,
  Y up. Rotation is **CCW positive viewed from the top**; bottom rows use `(180 − rotation) mod 360`. BOM: `Comment, Designator, Footprint, <fab part
  field>`. DNP is excluded from both. **The generator hard-fails on an empty fab-code field on a fitted part. It never falls back to the MPN.**
- **The fab has no per-package zero-rotation table**: "zero = tape/reel orientation, corrected per the silkscreen" (JLC). Two community
  rotation databases disagree by 180° on SOT-23 and QFN. So the project keeps a **project-owned rotation table** (`20-design/<fab>_rotation.yaml`,
  footprint-name regex → offset, seeded from two databases, only agreeing rows `review: false`). The pack carries `rotation_log.csv`, which
  lists every applied offset. **The fab's 3-D placement preview is the only authoritative check** before paying. It is a G2 checklist item; a
  +90 for 1×N headers was confirmed only there.
- **The table grows from the fab's own rows, with a selftest** **[measured]**. After every assembled order, diff the fab's engineering file
  (`vendor-review.md` §5 round 4: `ec` vs `oc` per designator). Group the deltas by footprint. Write them into the rotation table as rules, with
  the order id as the source. The CPL generator's selftest regenerates the file and asserts every polarized part against the engineer rows.
  The next order of these packages then ships right the first time. One order taught four facts. A vendor-made (EasyEDA) footprint does not
  sit at the fab's zero just because the fab drew it. LQFP-64 needed +270, as the community tables said for the stock footprint. The `-BL` /
  `-BR` suffix of a vendor footprint is a different pin-1 corner and needs its own offset (SOT-23-6: `-BL` 0, `-BR` +90). The fab's package
  ORIGIN is not the pad-bbox centre (a USB-C receptacle +2.345 mm, slide switches +0.127 mm toward the board edge). A rule key `shift: [dx, dy]`
  covers it, in the footprint frame, rotated with the part and mirrored on the bottom. Two-pin passives come back normalised by 180° either
  way; ignore them. The
  board file needs no change for any of this — the table is the design file that was missing, and the ordered package stays frozen as evidence.
- Polarity mark on the silk of **every** polarised footprint. The fab places per silkscreen when it conflicts with the CPL. The marks: pin-1
  dot on every IC, cathode band / triangle on diodes, + on electrolytics, pin 1 on headers. The F.Fab layer carries the same marks for the
  assembly drawing.
- **Pre-answer the fab's engineer** **[convention]**: at G2, run a fab's-eye pass beside the silk check. Look for a polarised footprint whose
  only mark is on the bottom at an odd rotation, a mark under mask or a pad, or a custom footprint with no body outline on the fab layer. Each
  is a production-hold question waiting to happen; fix the footprint. The package ships `ASSEMBLY_NOTES` (`references/fab-dfm.md` §9). It
  holds renders with the cathode end / pin-1 corner per part class, body + pin 1 + mating direction of every custom-footprint connector, and
  the empty / unplated holes with finished sizes and tolerances. The order remark points at it. When the fab's engineer questions still come,
  answer them on the board's pad-1 positions, never on the CPL rotation (`references/vendor-review.md` §5–§7).

## 11. Fiducials, test points, silk, courtyards
- **Fiducials** **[fab capability]**: 3 per side that carries parts (1 mm copper, 3 mm mask opening, ≥ 5 mm from the edge, not on a symmetry
  axis), on the panel rails when panelised; Standard PCBA requires them, Economic does not.
- **Test points** **[owner choice + convention]**: one per rail and per bus line the bring-up tool reads (the criteria yaml names them). Pad
  ≥ 1.0 mm, ≥ 2.54 mm pitch where a probe clip is expected. Label each with the net name and purpose on the silk (self-documenting labels).
  Group them in a field with a legend grid. The test plan lists the coverage (T-nn ↔ TP). Put each name on the silk, never on the
  fabrication layer only: that layer is invisible at the bench. Check the test point card against a real board, not the layout file.
- **Silk** **[fab capability + checker]**: line ≥ 0.15 (design 0.16+), text height ≥ 1.0 mm (labels 1.1–1.2), width:height 1:6, silk-to-pad /
  mask ≥ 0.15 (design 0.20). **No silk over pads, no via or PTH under a text cell.** Keep vias out of the text bbox at route time; clipping is
  for hairlines only. Check silk-to-edge against the TRUE outline polygon (notches). Check glyph stroke ≥ the minimum by a morphological
  opening. The font is either shipped with the repo or count-aware in CI, because a proprietary system font cannot run on the runner. A
  legibility gate READS the rendered PNG. Order number: "specify location" on a silk box or removed **[owner choice]**.
- **Placed artwork inside the outline** **[convention]**: an unsigned distance-to-outline test lets an off-board point pass. A "free space" test
  for placed copper or silk art combines point-in-polygon with the distance. The generator asserts every placed item lies inside the
  outline by the edge clearance. DRC did not flag copper outside the edge: marks across two tapered corners sat 1.68 mm outside the outline on
  a shipped board **[K]**. Gate row per layer: the Gerber copper bounding box lies inside the Edge.Cuts bounding box by the edge clearance.
- **Courtyards and tombstoning** **[fab capability + physics]**: body-to-body spacing per the fab's SMD spacing table (JLC: 0402↔0402 0.18,
  0603↔0603 0.25, chip↔QFN 1.0, QFN↔QFN 1.0, BGA↔BGA 2.0). In practice: ≥ 0.30 passives body-to-body, 0.50 where hand rework is expected,
  ≥ 1.5 mm around tall parts. Use symmetric pads and equal thermal mass on both ends of a chip part. One pad into a pour without relief
  tombstones the part. Courtyard overlap = DRC error, no exceptions.
- **Copper under a cage or shell** **[convention]**: read the connector drawing before you advise on copper under its body. A drawing can mark a
  component keep-out that still allows traces. The drawing reversed advice to keep tracks clear of the cage walls *(worked example)*.

## 12. Creepage and clearance for the voltage class **[physics + owner choice]**
Below 60 V DC / 30 V AC (SELV) the fab minimum spacing governs. Above it, the spec names the standard (IEC 60664-1 / IPC-2221 tables: pollution
degree, material group, working voltage). The layout then carries the creepage / clearance as a **generated rule** (a net-class-to-net-class
clearance), plus a slot where creepage needs it. State the class in the spec even when it is "SELV only — no creepage rule" (a decision row the
reviewer can read); an isolated section (USB isolator, mains) gets a keep-out zone on every layer and a drawn isolation barrier.

## 13. Panelization **[fab capability]**
- Standard PCBA needs every side ≥ 70 mm (JLC 2026-09-13), and the fab's automatic rails land on the SHORT edges. A narrow board needs a
  **customer panel**: 1-up + rails on the LONG edges (5 mm rails, Ø2 tooling holes, 1 mm fiducials on the rails). Use **mouse bites** (5 × Ø0.5
  tabs) where copper is < 0.40 mm from the break line (V-cut needs ≥ 0.40), with routed 2 mm slots between. Keep the drill/place origin
  unchanged so the panel CPL = board CPL + rail offset.
- Gate the panel on its STORED fills (`BuildConnectivity()` before every fill or pours starve). The gate: per-zone area within 1 % of the
  source, Gerber region count equal, DRC 0/0. Run the fab DFM on the PANEL zip too. A merged drill cannot mark mouse-bite holes NPTH; a remark
  settles the "unconnected via" warnings. Panel by customer REQUIRES the panel format field on the quote form.

## 14. DRC census: 0 errors / 0 warnings unless a dated waiver row
- Run `<cad-cli> pcb drc --severity-all --format json` on the committed board with **classes enforced**. KiCad honours only explicit
  `netclass_assignments`, never patterns, and no DRC exclusions: emit per-net assignments and rules from the generator. The census counts
  every severity per rule name (`gen/drc_count.py` style, cross-host: silk-text items dropped only when the font is absent, with a NOTE).
- **Zero errors, zero unconnected, zero warnings.** A warning that stays is a **dated waiver row** in `90-log/DECISIONS.md` (rule,
  item, reason, owner). A generated accept rule mirrors the row (`enclosedByArea` marker rule area per accepted item, not `insideArea`). DRC
  and the route-quality gate then accept exactly the same copper. A prose waiver the matrix cannot read does not count. The G2 cell and the board order
  require this bar (`templates/90-log/GATES.md`).
- **The canary rule** **[convention]**: one deliberately violated generated rule (a `CANARY` text or a marker area) must fire **exactly
  once** in every DRC run. It proves the rule file was parsed and the classes are enforced. A malformed `.kicad_dru` is silently ignored. A
  stricter rule than the class is invisible to the router and appears afterwards.
- **One canary per custom rule** **[convention]**. Copy the board without zones, add one deliberate miss per rule, and assert that the
  DRC flags each one. A rule with a wrong layer keyword or a wrong condition otherwise fails silently.

## 15. Route-quality classes **[convention + owner choice]**
Per net: routed / direct (MST over pads) meander ratio, segments, vias, layer changes, min/max width vs class, stubs, acute corners, layers used.
Board level: via total, copper per layer, inner-layer signal length not over solid reference copper, sensitive-net proximity (I²C / control /
sense / USB) to switching nodes and the crystal, and power corridor cross-section. The corridor needs ≥ N mm² per rail and ≥ 2 vias per
transition. Flags are graded
HIGH / MED / LOW; **0 unjustified HIGH** at G2, each HIGH either fixed through
the generator or a dated waiver row + accept rule (§14). The report is `route_quality.md` in the pack.

## 16. Schematic ↔ layout parity **[convention]**
Every symbol field is copied to the footprint as a hidden property (MPN, fab code, Confidence, DNP, Alt_*). Footprint attributes mirror the
symbol: DNP does not imply exclude-from-BOM, so set both. Net names and pin nets match between the exported netlist and the board. The parity
check lists every difference and G2 requires 0. A schematic regeneration must not rewrite the board-side project file (rules, classes) —
restore it from HEAD or merge (`references/pitfalls.md` tooling/gates).

## 17. Fab DFM mirror before the order, and the order-time stock freeze
- **Before the first quote and at every adopt**: mirror the fab's checker in-repo (`references/fab-dfm.md`). The mirror holds a thresholds
  JSON with source + date, a project measurer → items, the `scripts/dfm_check.py` grader, and acceptances by refdes with **date + reason +
  evidence**. Bare tracks / vias are never accepted. The mirror shows **0 open**: every item of either fab grade is fixed or accepted with
  vendor evidence. Then the fab's
  own viewer on the board AND the panel upload, counts diffed against the mirror, PDF export filed under `60-orders/quotes/<date>/`.
- **Stock**: every fitted code verified live with the run-relative minimum (`qty × boards × attrition`), owner floors on jellybeans; **once the
  order is PLACED the package is judged on the frozen `stock_snapshot.json`**, never on the live shelf (`references/fab-dfm.md` §8).

## 18. Where the numbers come from (worked example, JLCPCB 2026-09-13)
The PCB numbers come from `jlcpcb.com/capabilities/pcb-capabilities` (copper, drill, mask, silk, outline, tolerances). The PCBA numbers come
from `…/capabilities/pcb-assembly-capabilities` (Economic vs Standard: sides, min package 0402 / 0201, min pitch 0.4 / 0.35, reflow 255 / 240 °C,
rails + fiducials). The rest come from the help articles `pick-place-file-for-pcb-assembly`, `pcb-assembly-faqs-part-2` (rotation = tape
orientation, silkscreen governs polarity), `minimum-spacing-for-smd-components`, `Panelizing-your-PCB-for-Assembly`,
`in-what-cases-will-there-be-charged-extra`, and the stack-up template API (`getImpedanceTemplateSettings`). Fetch again, cite the date, and
keep the raw responses under `60-orders/quotes/<date>/`.
