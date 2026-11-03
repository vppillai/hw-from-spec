# High-speed trace design and SI analysis

Read this before you draw or judge any multi-gigabit lane: a host channel, a loopback, a connector launch or a test coupon. The general
impedance rules of the board (when a pair needs control, how to record the calculation) live in `references/pcb-layout-dfm.md` §3. This page
covers the rest, from the stack-up and the launch to the solvers, the coupon, the bench and the blind review. The rules are tagged **[physics]**, **[fab capability]**, **[method]** or **[owner choice]**. A worked number is
labelled *(worked example)*; the mechanism generalises, the value does not.

## 0. The SI convergence playbook: what to run on day 1

One SI loop ran eight iterations against its mode-conversion limit *(worked example)*. Most of them fixed a fault that a day-1 check
catches in minutes. Run the steps of §0.2 in order, before the first performance number. Plan three iterations: build and
screen, bounds and fixes, sign-off and review. The sections after this one hold the detail of each step.

### 0.1 What cost the iterations

| Fault | Symptom | Cost *(worked example)* | The check that catches it first |
|---|---|---|---|
| The model lacks features of the layout of record | A requirement closes, then a review reopens it. A twin with a solid plane and no contact posts read 9 dB better than the launch of record. | 2 iterations and a reversed owner decision | A feature census of the model against the layout source (step 3) |
| A simplified contact stands in for the real one | The result moves by more than its uncertainty when the contact changes. A vertical port overstated the launch reflection by 3 dB. Contact posts and the real contact tails differed by up to 2 ps of measured p/n delay. On posts the p trace led. On the real tails it lagged, and a retune sized on the posts made the conversion worse. | 1 to 2 iterations | One solve of the real contact from the vendor STEP at nominal (step 4) |
| The voxel or dropped-cell artefact | A step of several dB for a micron of width, or a cliff at one corner that only one solver shows | 3 iterations; a two-day redesign sized and then dropped | The edge-snapped mesh and the whole-model voxel screen before any solver time (step 5) |
| The bounds come late | A fix tuned at nominal fails at a window edge, a fab corner or a module corner. The pair gap fell under the fab minimum at the worst etch after the launch was tuned. | 2 iterations | Exact window edges, fab corners and module corners in the first sweep (step 8) |
| Corrupt lines in a vendor Touchstone file | A crosstalk figure several times the measured report: 17.5 mV of connector ICN against 2.0 to 3.1 mV measured | A false conclusion carried for six iterations | Point-by-point passivity on every vendor file before use (step 6) |
| Skew inferred, never measured | A skew retune moves the null but not the worst value, so the retune repeats. SCD21 implied 1.4 ps of p/n delay; the step crossings measured 0.7 ps. | 3 retune rounds | The p/n delay from the step response and the p and n TDR overlay (step 9) |
| Judging only up to Nyquist | A pair clean at Nyquist converts at −10 to −14 dB just above it | Found in the last iteration | Every metric plotted to twice Nyquist from the first run (step 8) |
| One lane solved for all | A fix that helps one loop hurts its neighbour. A loss pad helped the short loop and cost the long loop its return-loss margin. | Every fix ran twice | Each distinct lane geometry solved on its own (step 7) |
| A skew target copied by symmetry | The contact tails rise on one side of their pads, so opposite loops are not mirrors. A loop read −16.1 dB on a template that read −38.8 dB on its own group. | 1 retune round | One solve per direction group, each with its own skew target (step 7) |
| An uncalibrated evaluator | A home-made COM-like eye read 1.4 to 3.1 dB high with a bias that changed per channel. Its false finding drove a two-iteration fix study. | 2 iterations | The official code from the first eye (step 6) |
| Bench limits found late | A limit that no fixture can resolve. The test plan was rewritten after the review. | 1 review round | The verification method written beside each limit before the runs (step 1) |
| A coupon that cannot check the launch | A replica fed from its far end predicts −15 dB of conversion that the board does not have | 1 coupon redesign | Each coupon structure predicted with the same model, in the same iteration as the launch (step 10) |
| A fix part that does not fit | A resistor pad solved in 3D, then found taller than the gap under the connector body | Most of an iteration | The housing height from the STEP read before you solve a fix (step 2) |

### 0.2 Day 1, in order

1. **Write the limit table with its basis and its verification method** (§9.1, §13). Give each limit its standard clause or its design
   basis. Say how the bench or the coupon checks it. A limit that no fixture can resolve is an analysis requirement from the start.
2. **Read the fab stack-up, the fab tolerances and the mechanical envelope live** (§2, §3). Compute the exact widths at both edges of the
   impedance window. Check the pair gap at the worst etch. Read the housing heights over the routing from the STEP. Fix the pair geometry
   before any 3D work.
3. **Generate the field model from the layout source** (§1). The layout and the model read the same yaml. Run a feature census: every void,
   plane, pad, post and stitch of the layout appears in the model, and every via. A twin may screen a variant. It never closes a requirement.
4. **Model the real contact, and build ports that see every quantity** (§8). Solve the vendor contact geometry once at nominal. Compare it
   with the post or port stand-in. Keep the stand-in only inside the difference you measured. Use single-ended ports to a ground bar, so the
   common mode shows. Validate the setup on a mirror-symmetric pair: SCD21 below −100 dB.
5. **Screen the mesh before you spend solver time** (§7). Make every copper edge a mesh line. Run the whole-model voxel screen: 0 cuts over
   half a cell. Run three mesh levels on the first geometry. Use a DC-free excitation and judge the port tail. Close a plane cavity with a
   solid wall.
6. **Clean the inputs and fix the evaluator** (§9.3, §14). Check every vendor file for passivity, point by point. Drop isolated spikes too: a passive point
   10 dB off its neighbours is still corrupt. Agree every reference
   plane, so no pad counts twice. Run the official COM code from the first eye. Calibrate any fast evaluator against it on your own channels.
7. **List every distinct lane geometry and solve each one** (§6.1). Group lanes only by a symmetry you can state. Solve nested partner loops
   and their neighbours together. Solve every lane group, or prove with numbers that it matches a solved one. Extra room near a group
   is no reason to skip it. Read the contact tails in the STEP. One-sided tails break the mirror: solve one loop per direction group.
8. **Put the bounds in the first sweep** (§10). Solve both window edges exactly. Add the registration and p/n etch corners. Add the module
   corners: the return-loss mask at one end and at both ends, and the slowest transmitter edge. Turn crosstalk on. Plot every metric to twice
   Nyquist.
9. **Cross-check every run in the time domain** (§4, §9.5). Measure the p/n delay at the 50 % crossings of the step response. Compare it
   with the delay that SCD21 implies. Agreement means a pure skew, and a length retune fixes it. Disagreement points at an impedance
   asymmetry first. Overlay the p and n TDR. Tune the skew on the measured delay.
10. **Design the coupon in the same iteration as the launch** (§12). Feed each replica pad where the real driver touches it. Predict every
    structure with the model of record.
11. **Run the second solver on the worst corner in the same iteration** (§6, §7.4). Size its memory first. Pick the isolated cutout that
    fits. A single-solver corner value never closes a requirement.
12. **Close with the verdict table** (§16). Each row says converged, cross-checked, and the margin against its uncertainty. A blind
    reviewer recomputes the headline numbers from the yaml and the scripts before the owner sees a closure (§15).

### 0.3 Stop rules

- A result that moves by more than its stated uncertainty between iterations stops the loop. Find the step of §0.2 that missed it
  before the next run.
- A fix that holds at nominal only is half a fix. Rerun it at the bounds of step 8 before you report it.
- A closure that rests on a twin, a stand-in contact or one solver goes to the owner with that note. It never reads MEETS.
- Keep the inner loop cheap. Screen a variant on the medium mesh. Judge a margin on the fine mesh only (§7.1).
- A screening setting (a looser FDTD end criterion, a narrower excitation) is for main-path screens only. Never use it for mode
  conversion or crosstalk (§7.1).
- A number from a new host or a new tool image counts only after that host reproduces a result of record (§6.2).

## 1. The rule of record

- A number counts only when three things hold **[method]**. Its mesh has converged. A second solver agrees in band on the same geometry. The
  evaluator behind any eye or COM figure is calibrated against the official code.
- The model is the layout of record **[method]**. It holds every void, post, plane and pad, and every via. A simplified twin may screen a
  variant. It never closes a requirement. One study read SCD21 −33.5 dB on a twin with a solid plane and no contact posts. The launch of record
  read −24 dB *(worked example)*. Generate the model from the layout source and census its features (§0 step 3).
- Build the port that sees the quantity before you simplify the geometry **[method]**. A differential port cannot see common mode, so it
  cannot measure SCD21.
- Every number in a record comes from a script that reads the design yaml. A study table is regenerated, never typed.

## 2. Stack-up and impedance at the fab's tolerance

- Read the fab's stack-up live: layer thicknesses, Dk per dielectric, copper finish thickness and mask thickness **[fab capability]**. Cite the
  URL and date. A prepreg and a core of the same family differ in Dk; enter each.
- Pick the prepreg for the launch pad, not only for the trace **[physics]**. A wide pad over a thin prepreg is a low-impedance section. It needs a
  plane void under it, or a thicker dielectric.
- Name the impedance tolerance in writing on the order **[fab capability]**. Many fabs give ±10 % by default and ±5 % on request. A symmetric
  window is the usual offer. Ask for the impedance test report with the shipment.
- Run the open-loop corners before you trust the window **[method]**. Vary the etch by ±20 % of each pair's own width and the prepreg by
  ±10 %. Sweep the Dk span, the copper and the mask thickness. The open-loop span is wide. Only the fab's impedance control holds the pair inside the window.
- Check the pair gap at the worst etch **[fab capability]**. A wider track narrows the gap. Keep the gap above the fab's minimum space with
  margin at +20 % etch, or widen the pair.
- Judge the window on every loop and every metric **[method]**. A lower window can help one structure's mode conversion and cost another its
  return loss or COM.
- Audit the stack-up as the solver sees it, layer by layer **[method]**. Check the thickness, Dk and Df per dielectric. Check the conductor
  material, the etch shape and the roughness model. Check the conductor's material type, not only its conductivity value. In some tools a material typed as a
  perfect conductor ignores the conductivity field.
- Model the etch as a trapezoid (etch factor, which face is etched) in a cross-section solver. Model roughness with a physical nodule model,
  set per surface: top, bottom and side **[physics]**.
- Give the cross-section solver the copper thickness **[method]**. Zero-thickness sheet copper raised a narrow unmasked pair by about 15 ohm.
  That alone made a 6.5 dB gap between two solvers *(worked example)*.
- A Df that no primary source gives stays [K]. Sweep it. Close it with a coupon fit (§12).
- Add a dielectric anisotropy corner **[physics]**. A glass-reinforced laminate has a different Dk in plane and through the
  thickness. A single isotropic Dk hides that term.
- Treat the glass weave as a skew term, not as noise **[physics]**. One leg can run over glass and its partner over resin. For a pair
  with a tight skew budget, write a routing angle or an artwork rotation rule. Read the conversion on a coupon from each lot.
- Set the impedance target per interface, with its window **[owner choice]**. Two interfaces on one board can need different targets. A target
  without a window cannot fail.
- Model each dielectric wideband (Djordjevic-Sarkar), with Dk and Df quoted at a stated frequency **[physics]**. Resin content moves Dk: a
  high-resin prepreg sits lower than its core.
- A screening window may be tighter than the sign-off window, on purpose **[method]**. Say which is which. The reserve absorbs a later stack-up
  or material change.
- The same shift in ohms is a larger percentage at a lower target **[physics]**. Rank the risk of a material change per interface.
- Any stack-up change invalidates every via and launch result **[physics]**. Re-optimise them all and mark the old results superseded. A barrel
  that balanced a capacitive pad stops balancing when the dielectric thickness moves.
- Screen a material swap with an old-to-new table per structure **[method]**. Give Z max, Z min, SDD21 and SDD11 at Nyquist, the delta and the
  margin. Keep the geometry fixed for the screen, then retune the structures it flags.

## 3. Launch, pad, void and via design

- The launch sets the return loss of a short channel **[physics]**. Loss is rarely the risk on a short host loop; the reflection is.
- Size a discontinuity with a rule of thumb before you spend solver time on it **[physics]**. Excess capacitance matters when
  its value in fF exceeds about 10 times the rise time in ps. A corner matters when its width in mils exceeds about 5 times the
  rise time in ps. Solve only the features above the threshold.
- Two ground planes form a cavity **[physics]**. Stitch them near every discontinuity and around each connector. Write the stitch
  pitch as a layout rule. A perfect-conductor wall in the model is a convenience: run one case with the real stitching vias too.
- A connector pad longer than the contact foot acts as a stub **[physics]**. Cutting the pad to the foot is the strongest cure. It changes the
  vendor footprint, so it needs the vendor's word on solder-joint reliability.
- A plane void under each signal pad raises the pad impedance **[physics]**. Reference the pad to the next plane down. Sweep the void margin.
  The best margin is a value, not "as large as possible".
- A void changes the reference of every trace that crosses it **[physics]**. A trace that runs over a void sees a different delay and impedance
  from its partner that does not. That difference is a p/n delay and it converts modes (§4).
- Keep the trace edge away from the edge of a plane void **[physics]**. Keep a wide, solid reference under every high-speed pair outside the
  pad region.
- A void edge near the trace makes the registration sensitivity one-sided **[physics]**. One registration corner reads several dB
  worse than the other. Pull the void back on that side until the two corners balance. One launch moved a void edge by 0.05 mm.
  The two corners then balanced with no length change *(worked example)*.
- Let the pair converge to its coupled pitch right below the pad **[physics]**. Long uncoupled legs reflect and convert.
- Put one ground via in every ground pad of the launch, plated through every plane it passes **[physics]**. A via that stops at the first plane
  leaves the plane pair floating.
- A via transition reflects on its own **[physics]**. A two-via dive to the far side and back can set most of a section's reflection. Size the
  antipad and the plane cut-out under any pad in a 3D sweep.
- Tune the anti-pad per layer along the via, not one size for the whole barrel **[physics]**. The via sees a different reference on every
  layer. The per-layer clearance is the main knob for a flat TDR.
- Use the anti-pad shape as a tool **[physics]**. One oval round both barrels lowers the capacitance. Two separate circles keep copper between
  the barrels and pull down a via that reads high.
- A small drill and a small anti-pad protect the power planes but push the via impedance high **[physics]**. Record that SI against PI trade as
  a decision.
- The landing-pad size is the strongest knob near the landing layer **[physics]**. It does little for a high region deep in the barrel.
- Expect the result of a via to get worse steadily with its depth **[physics]**. A trend that is not monotonic points at the model or the mesh.
- A ground void next to a signal pad lowers the pad capacitance and adds an inductive peak beside it **[physics]**. Balance the two in the TDR.
- A large fixed pad (a ball pad or a connector pad) can set a dip that board geometry cannot remove **[physics]**. Confirm the limit with the part
  vendor. Record the mechanism, then carry the cure to the equaliser or the next part choice.
- Simulate a back-drill at its longest allowed stub, not the nominal **[fab capability]**. The stub resonance comes from the longest stub
  the fab can ship.
- State the ground-via cage of every launch: count and pitch **[physics]**. The cage sets the via's impedance and its crosstalk.
- Quote via sizes as the drill diameter, not the finished hole **[method]**. The field sees the barrel surface.
- Where the pair spacing opens near a ball field, each leg runs nearly single-ended **[physics]**. Size each leg near half of Zdiff there.
- Model a series AC-coupling capacitor, its pads and its vias as one block **[method]**. Judge it on S-parameters only: a step TDR sees an open
  at DC. That block is often the worst reflector on the path.
- Write down the direction convention of every lane **[method]**. A lane named from the host side can sit on the other physical path from one
  named from the chip side.
- A part cannot sit under a connector body unless its height clears the housing **[physics]**. Read the housing height from the STEP.

### 3.1 Post-layout reality against the isolated optimisation

- An isolated single-pair optimisation is not the routed structure **[method]**. The routed board adds neighbouring anti-pads, pours that pull
  back or relieve, layers that reference a power plane, longer lead-ins and fab width trims. Re-extract from the real layout before sign-off.
- A long lead-in lifts the TDR baseline **[physics]**. De-embed the lead-in before you read a via's impedance, or take it from a short cutout.
- State the TDR rise time and the de-embedded length with every TDR number **[method]**. A number without its rise time cannot be compared.
- Show a TDR profile for every net from its driving end. Mark the far port on the time axis, or stop the window there. Past the far port
  the trace shows the port impedance, not the line.

### 3.2 From the solved geometry to the layout

- Give the solved geometry a fab check that fails **[fab capability]**. Check every clearance after the etch tolerance, against
  the fab minimum. Check each plane void against the vias, and against the neck width it leaves. A printed table that a person
  must read is not a check.
- Draw the solved region from the same yaml the solver reads **[method]**. The layout and the field model then cannot drift apart.
- Re-extract the launch from the routed board and solve it again before the layout sign-off (§3.1).
- Keep the corners the solver solved on a skew-compensation jog **[physics]**. A mitre changes the jog length, and so the skew it
  nulls. Solve the mitred variant and compare it before you change the corners.
- Solve and compare a variant before you change any solved feature. An unsolved edit voids the result of record.

## 4. Differential skew and its compensation

- Compensate skew at the pin where it is created **[physics]**. A back-jog does this: the short-path trace takes its detour at its own pin.
  On a U-shaped loop the inner trace can leave its pad from the side that faces its partner. It then runs down the gap between the two pads.
- Tight length-tuning bumps buy little delay **[physics]**. The two legs of a bump couple and cancel most of the added path. Six bumps added
  1.56 mm of path and 0.28 mm of electrical length *(worked example)*.
- Avoid serpentines next to the device edge **[physics]**. They degrade return loss most there. If matching is still needed, use few segments
  with a small amplitude.
- Neck down inside a pin field and return to the full pair geometry outside it. Keep the neck short.
- Tune skew on the electrical delay, not the geometric length **[method]**. A void, a contact post or a pad section changes the delay of one
  trace more than the other. The geometric target then differs from zero.
- Sweep the skew target and read the whole band **[method]**. The conversion is not one skew. A 0.04 mm move can shift the null and change the
  worst value by several dB *(worked example)*.
- Read the shape of SCD21 **[physics]**. A rise of 20 dB per decade is a pure p/n delay, and a skew retune can null it. A flat or resonant
  shape is a geometry or reference asymmetry; a retune does not fix it.
- A p/n delay dt gives a conversion of about sin(π f dt) **[physics]**. A fraction of a picosecond already reads near −33 dB at 13 GHz. Use it
  to size the fix and the bench limit (§13).
- A length retune that compensates a reference asymmetry holds at one corner **[physics]**. Run it at the registration and dielectric corners
  (§10) before you close it.
- Measure the p/n delay in the time domain before a retune (§9.5). SCD21 holds the magnitude only, and part of it may not be delay. One
  launch implied 1.4 ps from SCD21 and measured 0.7 ps at the step crossings *(worked example)*.
- Compare the measured p/n delay with the delay that SCD21 infers **[method]**. When they agree, the conversion is a pure skew and
  a length retune works. When they disagree, overlay the p and n TDR and look for an impedance asymmetry first.
- Tune against the real contact, not a post stand-in **[physics]**. The contact tail adds its own p/n path. On one loop the real tails moved
  the measured p/n delay by about 2 ps against straight posts *(worked example)*.
- A port construct can flip the sign of a skew **[method]**. On box posts with a ground bar, one launch read the p trace early.
  With the real tails cut from the STEP, it read the p trace late. The retune sized on the posts made the conversion worse
  *(worked example)*. A fused STEP still gives the tails: cut the slab below the housing underside, one mesh per tail.
- One-sided contact tails break the mirror argument **[physics]**. When every tail rises on one side of its pad, loops that run in
  opposite directions see different p/n paths. Group the loops by direction. Solve one loop per direction group. Set each loop's
  skew target from its own solve. Never copy a target to another loop by symmetry. One loop read −16.1 dB on the template of
  the other direction, which read −38.8 dB there *(worked example)*.
- Record the variants that failed beside the one adopted. They are the reason for the adopted form.

## 5. Breakout and routing patterns

- Split the layout review into regions: device breakout, layer transition, open routing, connector. Give each region its own rule.
- Route one pair per pin channel where the pitch allows. Keep the breakout short.
- Single-ended routing inside a short breakout can give better loss than a forced coupled pair there **[physics]**.
- The preferred breakout form changes with the data rate. Write the rate threshold into the rule, with its source.
- Use 45 degree mitres or arcs at bends. The outer trace at a bend is longer; count it in the skew budget. A solved
  compensation jog keeps its solved corners (§3.2).

## 6. The solver chain

| Step | Tool kind | What it gives |
|---|---|---|
| Cross-section | 2D quasi-TEM field solver (finite elements) with roughness and wideband dielectric models | Zdiff, loss per length, the pair geometry |
| Launch and local structure | 3D FDTD (openEMS) of the region with every pad, void, via and post | S-parameters of the launch and the loop |
| Cross-check | 3D FEM (Palace) on the same isolated geometry | agreement in band; a second opinion on any corner |
| Cascade | network tool (scikit-rf): P370 split, cascades, mixed-mode conversion | channel S-parameters, de-embedded parts |
| Eye or COM | the official IEEE COM code (it runs under GNU Octave) | COM against a reference channel |

- Validate each solver on a known case first **[method]**. Check the 2D solver against a closed-form microstrip. Check a 3D mixed-mode setup on
  a mirror-symmetric pair: SCD21 must sit below −100 dB. Then a large SCD21 on the real geometry is physics, not a port bug.
- Check reciprocity and the Tx and Rx drives of the same model **[method]**. They must agree.
- Every script has `--selftest`. Heavy runs go through the host's job pool. Cache each finished sweep keyed on its inputs before the next step
  starts; a crash in the last step then loses nothing.
- Size the FEM memory before a run **[method]**. Second-order FEM needs tens of kB per tetrahedron. A full pad-row model can need far more
  memory than one isolated loop. Record the size limit, then pick the cross-check case that fits.
- Under a container cpuset, the MPI launcher can refuse a FEM job for lack of slots. Allow oversubscription (Open MPI:
  `OMPI_MCA_rmaps_base_oversubscribe=1`), and let the job's slot count bound the ranks.
- Test each suspect of a solver disagreement on its own, on a cheap case. Compare a closed box with absorbing faces. Compare direct
  solves with an adaptive sweep. Sweep the copper thickness in 2D.

### 6.1 Partition the channel

- Segment the channel; do not extract it in one 3D run **[method]**. Split it into the package, the near breakout, the routed line, the far breakout
  and the measured connector model. Cascade the blocks in a circuit tool. A full multi-pair channel in one run can take days and never converge.
- Keep the line a segment of its own **[method]**. Then fab corners rerun the line only. Cut it at the via edges when the breakout has no
  width change.
- List every via on the path with its segment **[method]**. No via may be counted twice or left out. Added blocks bring their own vias.
- Agree the reference plane at every handoff with the owner of the next model: ball top, ball centre or board pad **[method]**. A package model
  that holds the ball and the via of the board must not meet a board model that holds them again.
- Draw the model chain in one figure: driver, package, board, package, receiver **[method]**. State the reference impedance at each joint. A
  joint with two reference impedances adds a false reflection.
- Cut each board block from pad to pad and keep every via, meander and neighbour of the group in it **[method]**.
- Model a package with its S-parameters or a coupled RLGC model, never as a lossless delay **[physics]**. A delay line drops the package loss,
  its impedance steps and its crosstalk.
- Keep single-ended multi-port files and assign the pairs in the cascade **[method]**. Set the differential reference to the target and the
  common-mode reference to a quarter of it. The files then keep every conversion and coupling term.
- Terminate unused ports of a multi-port block in the reference impedance **[method]**. An open port reflects into the victim. State the
  far-end termination of every run, and run each condition that occurs in service.
- Keep a port table: net, then the port number at each end **[method]**. Name every port by reference designator, pin and net. Most mixed-up
  results come from a wrong port order.
- Report the solver convergence with every result: the adaptive passes, the final delta-S and the sweep type **[method]**.
- Feed the same extracted file to the frequency-domain review and the time-domain run **[method]**. Two different models cannot check each
  other.
- Run a set-up pass before any performance run **[method]**. It proves the ports, the pair map, the segments and the lane direction. Mark its
  numbers "preliminary, set-up check".
- Sweep each block far enough: vias to about 2 to 2.5 times Nyquist, lines to about 3 times **[method]**. A line must roll off smoothly over
  the span. A resonance there is a model fault.

### 6.2 Choose and prove a simulation host

- Route each job by the bottleneck of its solver, not by core count or memory size **[physics]**. FDTD is memory-bandwidth bound. FEM
  is memory-capacity bound. SPICE and small numeric scripts are single-thread bound, so a fast core wins.
- Count the physical cores and the memory channels before you size a pool **[method]**. A many-core workstation with two memory channels
  ran one FDTD job at about half the speed of a laptop-class SoC with wide unified memory. One, two or four jobs shared the same total
  *(worked example)*. Run one bandwidth-bound job per such host, and give its other slots single-thread work.
- Read the memory slots too. One module gives one channel. One module ran FDTD at two thirds of the speed of two, on
  the same CPU *(worked example)*. Most Linux hosts list the modules without root (`udevadm info -e`,
  `MEMORY_DEVICE_*_SIZE`).
- Size the FEM memory per case before you pick the host (§6). A small VM ran out on a cutout that a large-memory host fits several times.
- Measure a short run of each solver class on each host before you route work **[method]**. Record the speed and the peak memory per
  class, and route by that table.
- Prove a new host against results of record before it produces one **[method]**. Rerun each solver class on a past case. A
  deterministic tool must give byte-identical output. Any other tool must agree within a stated tolerance, with the cause named.
- Name the cause of each cross-host difference **[method]**. The usual causes are:
  - The FDTD end criterion meets floating-point noise, so two hosts stop at different steps. Cut both time records to the common
    length and compare again. The cut records agreed far inside the tolerance *(worked example)*.
    Two hosts with the same CPU and thread count gave bit-identical results. The stop step is a property of the platform.
  - The FEM mesher gives a different mesh on another CPU architecture from the same geometry. Judge the difference against the mesh
    tolerance of §7, not against zero.
  - A CAD netlist export writes stacked pins of one unit in another order, because the sort is not stable across C++ libraries.
    Compare netlists with the pin lists sorted and the date lines dropped.
- Match the interpreter version of the reference host, not only the code **[method]**. The official COM code ran over an order of
  magnitude slower under an older numeric interpreter, with identical numbers *(worked example)*.
- Run every solver in a container image, and pin the image by its digest **[method]**. Pin the distro package snapshot in the image
  too. Then two hosts run the same binaries, and a rebuild a month later does as well.
- Install the CA certificates before you point the package sources at an https snapshot. A bare base image has none, and the package
  tool falls back to the live archive without an error. Read the package policy output to confirm the snapshot.
- Keep one host of record per output kind. A second host checks parity. It does not replace the files of record.

## 7. Convergence and meshing artefacts

### 7.1 Mesh and time

- Run three mesh levels at the copper (coarse, medium, fine) **[method]**. State the spread as the uncertainty. If the order is not monotonic,
  keep the pessimistic level of record.
- Judge mode conversion on the fine mesh only **[method]**. At nominal the medium mesh agreed with the fine one. At the impedance corners it was
  10 dB off *(worked example)*.
- Judge FDTD time convergence on the port tail, not only on the energy **[method]**. A Gaussian excitation carries DC, and an absorbing face
  cannot remove a static field. The energy then stalls while every port voltage has died. A DC-free excitation (the derivative of a Gaussian)
  converges fast and gives the same S-parameters.
- A looser FDTD end criterion and a narrower excitation are screening settings **[method]**. On one loop model, −50 dB saved
  17 % of the steps. It moved S by 0.23 dB above −30 dB, and by up to 3.1 dB on low-level ports. A 30 GHz excitation saved 32 %
  and cost up to 0.66 dB in band *(worked example)*. Use them for main-path screens only, never for mode conversion or crosstalk.
  Plot the error per frequency before you say where its maximum sits.
- A frequency-dependent (Debye) dielectric can run about 100 times slower in an FDTD solver than a fitted conductivity
  **[method]**. One 6-pole model ran at 1 % of the cell rate *(worked example)*. When the de-embed already restores the correct
  line, only the short launch keeps the model material. Bound that error by analysis over the launch length instead of a full run.
  State the sign too. Extra loss damps each reflection on its round trip, so a model with a higher loss tangent reads RL optimistic.
- Close an FDTD plane-pair cavity with a solid conducting wall, never a via fence near an absorbing face **[method]**. Field leaks between the
  fence vias into a thin strip that ends on the absorbing face, and the run diverges.
- A 2x-thru for de-embedding reuses the DUT's mesh at its ports **[method]**. With its own mesh the thru reads a flat loss that the de-embedded
  part then shows as gain.

### 7.2 Mesh starvation in an adaptive FEM model

- An adaptive mesher in a large multi-pair model spends its budget on long traces and coupling regions **[method]**. A narrow anti-pad gap then
  gets one element across. Its capacitance is low, so the via reads high. L is not mesh-sensitive; C is.
- Fix it with a local length rule on the signal nets only **[method]**. Set the largest element to a third or a quarter of the smallest radial
  gap, per gap group. Do not mesh inside conductors.
- The isolated single-structure cutout is the golden reference **[method]**. Refine the multi-structure model until its feature matches the
  cutout.
- Accept a mesh on a convergence test, not on its smallest edge **[method]**. Tighten one more step. If the impedance barely moves, stop.
- A refined feature can lower the total element count. A coarser far plane is fine while the copper ring next to the gap stays fine.
- Runtime is a free warning. A run heading for a day on a model that should take hours is probably starved or ill-posed.
- A change that fixes an impedance after an unrelated edit may only be the re-mesh it triggered **[method]**. Undo the edit and rerun. A
  result that does not come back has a numerical cause.
- Inspect every curve for features no physics makes: a vertical step, a one-point spike, a jagged band **[method]**. Confirm them with a
  discrete sweep or a finer mesh before you judge the curve. Interpolation and meshing can invent resonances.
- Below the numerical floor, report "negligible", not a number. A crosstalk value deep under the floor is solver noise.

### 7.3 The voxel and dropped-cell artefact

- An FDTD solver decides per cell whether copper is there **[method]**. When two drawn edges lie closer than the merge gap, the mesher merges
  their lines. The merged line can land just outside a copper edge. Then a whole row of cells along that trace is dropped.
- The symptom is a step: a result that jumps several dB for a micron of width. One SCD21 moved by 9 dB between two widths 0.001 mm apart
  *(worked example)*. Mesh-line and polygon checks show nothing; the lines agree and the topology is the same.
- Dump what the solver meshes when a result jumps with a tiny geometry change (openEMS: `debug_PEC` with a setup-only run). Measure the metal
  width across the trace. Compare it with the drawn width.
- A copper grow sized to half the merge gap is not enough **[method]**. A chain of close edges moves the running mean further. Coarser meshes
  have larger gaps.

### 7.4 The edge-snapped mesh and the whole-model voxel screen

- Make every axis-parallel copper edge a mesh line of its own **[method]**. Drop other lines inside the merge gap of a hard edge. Then grow
  the copper by about 1 µm so each such line falls inside the metal.
- Screen the whole model, not one cut **[method]**. Cut every axis-parallel trace segment at a fixed step and every contact foot, on the
  solver's own copper dump. Compare the meshed edge with the drawn edge. The gate is 0 cuts over half a cell.
- Run the screen before any solver time on a new geometry, and on every model of record.
- Never take a single-solver corner value as a pass or a fail **[method]**. A cliff with no physical cause is an artefact until a second
  solver or the voxel screen says otherwise.

## 8. Ports, reference planes and de-embedding

- Put the port where the real driver is **[physics]**. A vertical port under a pad adds inductance at the launch. It overstated the launch
  reflection by about 3 dB against contact posts with a port between their tops *(worked example)*. A lumped port on a ball or connector pad
  forces a step that does not exist. One breakout read its return loss far worse until the full connector model replaced the port.
- To see common mode at a contact, model the contact posts and a conducting bar joined to the ground posts. Run a single-ended port from each
  signal post to the bar **[method]**. Single-ended ports to a bare ground post close the differential current through the pads and vias.
  The insertion loss is then wrong. Check it against the differential-port model.
- State the reference plane of every part in the cascade **[method]**. The 3D model ends at one plane. The connector model starts at another.
  A gap or an overlap between them is a bias. Keep the overlap inside the span the de-embedding was tested over.
- A vendor connector model can carry its own host pad **[method]**. A board model that holds the real pad then counts it twice.
  Fit a shunt C to the host-end TDR dip and de-embed it. Check the result stays passive. Report the result over the fit span and with no
  de-embedding; the sign of the margin must hold.
- De-embed a differential fixture with the mixed-mode P370 class **[method]**. The single-ended split cannot remove the fixture's own p/n
  terms.
- Every fixture on a coupon is a copy of one 2x-thru half. Then one split removes all of them.
- State the reference impedance of the mixed-mode conversion on every plot.

## 9. Figures of merit and how to read them

### 9.1 What to plot

- One page per link group. Four panels: SDD21, SDD11, SCD21 and SDC21. Every lane of the group is overlaid, one colour per lane.
- Add SCD11 when a module input has a common-mode limit. Plot SCD21 and SDC21 both: they differ when the structure is not symmetric end to end.
- Put one marker at the Nyquist frequency of the target rate. Put the worst lane value at that marker in the panel title.
- Name the two ends of the link on each page.
- The overlay shows an outlier lane at once. Investigate the outlier, not the average.
- Break the link into segments (each via, each trace, the connector) and give each its share of the loss at Nyquist.
- Group links by type (chip to chip, connector to chip, long reach). Each group gets its own expectation.
- Write the limit table before the runs: IL, RL, NEXT, FEXT and impedance at Nyquist **[method]**. A limit fixed first cannot move to fit the
  result. Add a softer aim up to twice Nyquist; edges carry energy there.
- Draw the limit line on every plot. A PASS word in a text box hides a curve 1 dB from the limit.
- Give a table of the worst value and its frequency per net. Name and highlight a failing net, so the layout fix stays local.
- Plot the return loss from both ends. The ends differ when the launches differ.
- Plot every NEXT and FEXT pair at one end, then the power sum or ICN per victim. Several aggressors that each pass a pair limit can fail
  together.
- Bound every exception ("except at transitions") by its length and depth. An open exception lets a real discontinuity through.

### 9.2 What the curves say

- IL ripple on the insertion loss is a reflection between two discontinuities **[physics]**. Its period gives their distance. A standing wave
  between two launches makes a length sweep non-monotonic.
- A notch or roll-off above Nyquist marks a resonance: a stub, a long via or a plane-pair cavity. Keep it clear of the band you claim.
- Narrow features in the return loss can be plane-pair resonances seen through voids. Their frequency moves with the model's plane size.
  Until one is identified, the worst value with the feature is the number of record.
- A resonance cluster in one band on every net usually belongs to the model. Look for a plane cavity, an open boundary or a gap in the
  stitching. It can also be a real plane resonance that the board must fix. Explain it either way.
- A deep, narrow IL notch whose frequency follows a stub length is a quarter-wave stub **[physics]**. Far above the band it is harmless. Near
  Nyquist, remove it by back-drill, a shorter via or a layer change.
- Meanders raise FEXT and shorten the delay less than their drawn length **[physics]**. Coupled parallel lines show a crosstalk ripple whose
  period follows the coupled length; that ripple is expected.
- Pick the crosstalk group as the worst arrangement on each layer, not a fixed lane set. Reduce a heavy run to the group that holds the
  dominant aggressors.
- A model that holds one via pair carries no coupling between vias **[physics]**. In a dense ball field the breakout vias and the package often dominate.
  Extract the vias of several pairs together when crosstalk matters.
- Return loss: compare the board alone with its own target, and the channel with the standard's mask. A short channel between two reflective
  ends is echo-limited. Loss can help it.
- Crosstalk: report the integrated crosstalk noise (ICN) with one parameter set for every source. Compare the connector model's ICN with any
  measured report on the same set. Then give the COM cost of all crosstalk together.
- A design limit that no standard clause sets is a design margin. Derive its basis (for example the common-mode voltage it puts at the module
  input) and write it beside the limit.

### 9.3 COM against the standard's reference

- Judge a short channel by the difference to a reference **[method]**. The reference is the same channel padded with line to the standard's
  loss budget, through the same transmitter, receiver and packages.
- Run the official COM code **[method]**. A home-made evaluator read 1.4 to 3.1 dB high, and its bias depended on the channel. That bias
  produced a finding the official code did not repeat *(worked example)*. A second open-source port also swung by several dB between
  near-identical channels.
- If no public calibration case exists at your rate, run the official code itself. Check your Touchstone writer against an original file
  through it.
- Run the module corners: typical packages, one end on the return-loss mask, both ends on it, and the slowest allowed transmitter edge. Report
  the corners that fail; do not require them when no channel passes there, the reference included.

### 9.4 Active sign-off in the time domain

- Sign off in two stages: the passive channel (S-parameters per block) and the active link (transmitter and receiver models end to end)
  **[method]**. The passive report proves the structures; the active report proves the link.
- Run first-order compliance (COM, ERL) on the cascade before any bit-by-bit run. It finds a gross fault cheaply.
- Draw the eye mask at its stated BER and give the margin as a number in mV and ps **[method]**. A margin nobody can read becomes "adequate".
- Reach the target BER with a statistical eye or the receiver model's SNR, not a counted BER **[physics]**. Zero errors in N bits means a BER
  under about 1/N only.
- State the basis of the BER target and the alternatives: an internal target, the standard's pre-FEC limit, the silicon vendor's figure.
- Use a long PRBS with a different seed per lane. Equal seeds make the lanes switch together. Add a worst-case pattern from the pulse response.
- Drop the start-up transient and the equaliser training bits before you count. Use at least 32 samples per UI.
- Probe at the die pad, after the package and the termination. The receiver decides there.
- Enter jitter and noise as separate random and deterministic terms, from the silicon data or the model **[method]**. Cite the source. Tool
  defaults make the eye look better than the part.
- Add the package delay of every pin to the board delay before you judge skew **[physics]**.
- State the aggressor alignment and run the worst one. Give the crosstalk penalty as the delta with aggressors on and off, same victim, same
  extraction.
- Read the equaliser state as a health check: gain stages not saturated, main tap near unity, the transmitter preset named. An equaliser at
  its limit leaves no margin even when the eye opens.
- Run the driver and receiver corners and every termination option, not typical only **[method]**. The slow corner sets the eye height; the
  fast corner sets ringing and crosstalk.
- Simulate each topology state of a shared net separately. An inactive load is an open stub.
- Run at least one corner with the real power network when many lanes switch together **[physics]**. Ideal rails hide simultaneous switching
  noise.
- Close each marginal frequency-domain item with a named time-domain number. "To be confirmed in the time domain" is an open item until then.
- A link that is symmetric by direction can be signed in one direction. Say so, so the reader can check the claim.

### 9.5 Time-domain cross-checks

- **Step response.** Compute the step response of each extracted file. It settles to the DC point and shows no response before the edge
  arrives. A response before the edge is a causality fault.
- **Measured skew against inferred skew.** Take the p/n delay from the single-ended transmission 50 % crossings or the phase delay. Infer the
  delay from SCD21 with sin(π f dt). Compare both with the skew in the eye. A disagreement points at the ports or the model chain.
- **Single-ended TDR overlay.** Overlay the p and n TDR profiles from the same end. Where the two traces part, the pair is asymmetric. That
  place is where the conversion comes from.
- **TDR on a short loop.** A window between the pads of a short loop stays inside the launch reflection. The level there tracks the
  edge rate and the contact model, not the line impedance. One loop read about 88 ohm there on a 100 ohm pair *(worked example)*.
  Read the line impedance from the 2D cross-section. Quote a TDR level only where the line is long enough to settle.
- **Conversion above Nyquist.** Read SCD21 and SCD11 to twice Nyquist. A pair clean at Nyquist that converts just above it still feeds common
  mode to the receiver.

## 10. Corners and Monte Carlo

- Run the window edges exactly **[method]**. Compute the widths that give the two edges of the ordered impedance window, and solve both.
- Monte Carlo over the fab spread: etch, prepreg, Dk, Df, roughness, mask, copper **[method]**. Use 1000 samples or more for a 99th percentile,
  and state the 95 % bound on that percentile.
- Save every sample set with its run, not only the summary **[method]**. A later figure or check may need the samples. Check the
  file on disk, not the code that writes it: one run predated the save line and left no samples.
- Vary the launch too: layer registration of the plane void against the pad, and a p/n etch difference **[method]**. A Monte Carlo that holds
  the launch at nominal misses the term that sets the launch.
- Know which route reaches a window edge **[physics]**. The dielectric spread alone may not reach it; a lot at the edge also has a different
  track width. Model the edge the way it happens.
- Choose the impedance window with the mode conversion, not only with the return loss **[physics]**. A side-entry launch converts more as the
  pair narrows.

### 10.1 Ranking layout options

- Compare options on the same stack-up, solver settings, ports, limits and plots **[method]**. Show the layouts side by side, then overlay
  their curves.
- Rank by the margin number, the worst value against the limit, not by PASS or FAIL. Two passing options can differ by 10 dB.
- Run the fab corners on the winning option before you adopt it. A winner at nominal can lose at a corner.

## 11. Margin rules

- Set a margin in reflection magnitude, not only in dB **[owner choice]**. For example, a target of 15 dB return loss with 20 % of |Γ| to spare.
  Report the margin at the 99th percentile of the fab spread.
- A margin smaller than the stated uncertainty (mesh, solver, fab) is MARGINAL, not MEETS.
- A margin whose last term rests on one solver says so in the record.
- A per-block return-loss figure is an aim, not a sign-off limit **[physics]**. In the assembled channel a reflection makes a round trip
  through the line and drops by about twice the line loss. Judge a block that misses its aim at channel level.
- Per-block loss is informational. Check the total against the budget in the cascade.
- A waiver needs independent support: the channel-level result, an active margin on the same structure and a documented precedent. Confirm it
  again after any design change.
- Give every known model bias its sign. A receiver model that terminates twice is pessimistic; a pass with it stands, with the note.
- Hold the loss of the channel under a margin rule well inside the standard's budget **[owner choice]**.
- Margins are owner decisions. An agent proposes the row with the number; the owner accepts it.

## 12. Coupon design that checks the model

- Put the coupon on a breakaway rail of the same panel: same lot, same stack-up **[fab capability]**.
- Draw four kinds of structure. A 2x-thru removes the fixtures. Two line lengths give a delta-L fit of Dk, Df and roughness. A TDR line gives
  Zdiff. A replica holds the launch of record.
- Feed each replica pad at the point where the real driver touches it **[physics]**. A far-end feed adds a p/n path that the board does not
  have. Such a replica cannot check the board's conversion, even in principle.
- Predict every coupon structure with the same model before the order. The pass mark is the prediction plus an allowance. Three remounts of the
  2x-thru set that allowance.
- The edge launch must be rated for the board thickness. Read its drawing first.
- Put one coupon on each panel, and use reusable clamp-on edge launches **[method]**. A soldered SMA varies from one fixture to the
  next, and the 2x-thru de-embed needs identical fixture halves. It also limits the bandwidth. Probe pads need a probe station.
- Put the delta-L pair in both weave directions **[physics]**. The glass weave differs along x and along y.
- Run each loop replica in the same direction as its board loop. A loop with one-sided contact tails is not its own mirror (§4).
- Key the coupon data of each board by the board's unique ID. Use this when the identity EEPROM has no room for the data.
- Fit the material from the delta-L lines. Put the fitted values into the design yaml and rerun the study.
- A TDR reading within its own uncertainty of a window edge is re-measured, never a lot hold by itself.

## 13. What a bench can and cannot resolve

- A bench reading through compliance fixtures includes the fixtures' own mode conversion **[physics]**. A mated fixture set may convert more
  than the board limit. A fraction of a picosecond of fixture p/n delay alone reads near −33 dB.
- Keep a limit that the bench cannot resolve as an analysis requirement. Let the coupon check the model against its prediction. Record the bench
  reading as a diagnostic with no mark.
- Give the bench a gross-fault screen only: a reading far over its prediction holds the lot for analysis. Nothing close to the floor holds a lot.
- Compare lane groups on the same module pair to read an echo penalty directly. A margin the simulation cannot close moves to that bench
  comparison. Until it holds, a fail in that group reads INCONCLUSIVE, never a fail bin.

## 14. Vendor models and data hygiene

- Check every vendor Touchstone file for passivity point by point before use **[method]**. Single corrupt lines can hide in a crosstalk file. One
  file set made a connector ICN several times its measured value *(worked example)*. Drop the non-passive points and record how many.
- Despike every vendor file as well **[method]**. A point can be passive and still corrupt. One SDD11 point at −15 dB between
  −34 dB neighbours moved the official COM by 0.25 dB *(worked example)*. Drop isolated spikes of about 10 dB, and record how many.
- A vendor model of a similar part from another maker is a stand-in. Say so in the record. Compare it with any measured report for that part.
- A measured report of a mated fixture set includes fixture traces. Do not compare its IL with a bare connector model.
- Licensed vendor models and drawings stay local. Never commit them; record their path and licence.
- Use the vendor's measurement-correlated model of a connector, not an approximation. If a vendor's 3D model is wrong, say so and ask for a
  correct one.

### 14.1 Model-export checks

Run these on every Touchstone file before a cascade, a plot of record or any time-domain use.

- **Passivity.** The largest singular value stays at or below 1 at every point. Record any point that is not.
- **Causality.** No response before the edge arrives in the impulse or step response. Use causality- and passivity-fitted files, and label
  them as fitted.
- **DC point.** The file starts at or extrapolates cleanly to DC, with the right DC loss. A wrong DC point shifts the baseline of the eye.
- **Reciprocity.** Sij equals Sji for a passive board structure. A large difference points at a port or an export fault.
- **Round trip.** Overlay the solver's native result with the exported and re-imported file. The two curves lie on top of each other.

## 15. Blind review checklist for SI

Give each reviewer the frozen study, the yaml, the scripts and this list. Give no other reviewer's output.

1. Does the model of record hold every void, post, plane, pad and every via of the layout of record? Is any requirement closed on a twin?
2. Can the ports see the quantity each requirement names? Which port sees common mode?
3. Three mesh levels: what spread, which level is of record, and is the conversion judged on the fine mesh?
4. Does a voxel screen of the whole model show 0 cuts over half a cell? Is every copper edge a mesh line?
5. Does a second solver agree in band on the same geometry? Which terms rest on one solver?
6. Is the time convergence judged on the port tail?
7. Are the stack-up values read live and cited? Are the impedance tolerance and the report named on the order?
8. Are both window edges solved exactly? Does the Monte Carlo vary the launch (registration, p/n etch)?
9. Is the skew tuned on electrical delay? Does the retune hold at the corners? Is the SCD21 shape a pure delay?
10. Are SDD21, SDD11, SCD21, SDC21 and the crosstalk plotted for every lane, with the reference impedance stated?
11. Is COM run with the official code, against a padded reference, at the module corners?
12. Are the vendor files checked for passivity? Is any pad or fixture counted twice? Where is each reference plane?
13. Is each margin larger than its uncertainty? Is each design limit's basis written beside it?
14. Can the coupon check the model? Is each replica fed where the real driver touches it? Is there a prediction for each structure?
15. What does the bench claim to resolve, and can it?
16. Do the variants that failed stay in the record beside the one adopted?
17. Does every extracted file pass the export checks of §14.1? Do the time-domain cross-checks of §9.5 agree?
18. Is the limit line on every plot, with a worst-value table per net? Is every exception bounded?
19. Is the channel partitioned, with every via listed once and every handoff plane agreed?
20. Does a result for a via come from a starved FEM mesh? Does the multi-structure model match the isolated cutout?
21. Do the active runs cover the corners, the real jitter values, the aggressor alignment and the power network?
22. Which steps of the §0 playbook ran, and in what order? Which step did the study skip, and what does the skip cost?
23. Is every distinct lane geometry solved, or does one lane stand for others? What symmetry argument covers the rest?
24. Is the p/n delay measured in the time domain, and does the skew tuning use it? Is every metric read to twice Nyquist?
25. Does every fix part fit the mechanical envelope (housing height, keep-outs) before its 3D run?
26. Recompute three headline numbers from the yaml and the scripts. Do they match the record?
27. Did each host and image that produced a number first reproduce a result of record? Is each cross-host difference explained?
28. Was each skew compensation sized on the real contact? Do the measured and the inferred p/n delays agree?
29. Is every vendor file despiked as well as checked for passivity?
30. Did any screening setting (a looser end criterion, a narrower excitation) produce a conversion or crosstalk number?
31. Does the solved geometry carry a fab check that fails after the etch tolerance? Does the layout draw it from the solver's yaml?
32. Was the launch re-extracted from the routed board and solved again before the layout sign-off?
33. Are the contact tails one-sided? Does each direction group have its own solve and its own skew target?
34. Does any line impedance come from a TDR window inside a launch reflection, not from the 2D cross-section?
35. Is the effect of a dispersive dielectric bounded, with the sign of the RL error stated?
36. Is every Monte Carlo sample set on disk beside its run?
37. Does the coupon put the delta-L pair in both weave directions? Does each replica run in its board loop's direction?
38. Is every figure and number labelled simulated, calculated or measured?

## 16. Records

- One study file per board revision, with an iteration section per pass. A later iteration states which earlier sections it supersedes.
  Superseded numbers stay in the history, marked at the top; they never sit beside the numbers of record.
- Give each result section the same layout. Start with the date, stack-up, target and window, materials and via size. Then give the
  per-layer anti-pads, the TDR markers with delta and margin, the S-parameters at Nyquist and a status table.
- Keep the Touchstone files of record beside the sign-off, named by structure, layers and date. The cascade uses exactly those files.
- Mark a set-up check "preliminary" in its first line.
- Label every figure and every number for a reader as simulated, calculated or measured. COM, ICN and ILD are software outputs.
  Say so, and name what the bench measures instead: BER, a VNA sweep or a TDR. Give each gallery short notes for a beginner.
- Results borrowed from a sister board are a placeholder. Say so, and sign off again with the board's own models.
- Each iteration ends with a verdict table (converged / cross-checked / verdict), a risk register, proposed decision rows and learnings.
- Results of record live beside the study. Figures are generated. The solver export (Gerber, drill, stack-up and port table of exactly the
  solved copper) lets a commercial tool repeat a run.
- When a predecessor's runs are reused, read the diff of its last commit first. One slip in an indentation left every ground pad floating
  *(worked example)*.
