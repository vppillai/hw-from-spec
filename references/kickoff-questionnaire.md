# kickoff-questionnaire.md — every owner decision a board and / or enclosure project needs, asked UP FRONT with a recommended answer

Owner's words (2026-09-28): *"the skill should ask all questions upfront … the questions must come with required recommendations that the user
can select."* The decision classes below are mined from one complete project's owner rows (85 D rows, 200+ agent rows); each question carries a
**RECOMMENDED** answer (marked) and two or three alternatives with their one-line consequence. The agent asks them in the batches of §0 with the
`AskUserQuestion` tool (≤ 4 questions per call, ≤ 4 options per question; the recommended answer listed first and labelled; **"accept every
recommended answer of this batch" is the FIRST option of the batch's FIRST question** — so that question carries at most two alternatives, the
others at most three; a question with more alternatives folds the rare ones into one "other (named in the reason)" option), records every answer in `docs/governance/KICKOFF_ANSWERS.md` (`templates/KICKOFF_ANSWERS.md`), writes
one owner row per answer into `docs/governance/DECISIONS.md` (D rows, the owner's words quoted; a recommended default the owner accepted reads
`accepted recommended`), copies the machine-readable values into `project.yaml` (`kickoff`, `board`, `fab_dfm.bar`, `print_targets`) and a
traceability entry per row — **all before any CAD**. A question the owner defers is a D row `OPEN` and blocks the phase that needs it, never a
silent assumption (rule 2). Re-asking an answered question is a defect; changing an answer is a new D row that supersedes the old one.

**Scope first (A0).** Every question below carries the scopes it applies to — `[ee, both]`, `[mech, both]` or none (= every scope). A0 is
asked alone before batch 1; from then on a question outside the scope is **not asked** (its KICKOFF_ANSWERS row reads `n/a (scope)`) and a
batch with no applicable question is skipped — a mech-only owner never sees via-in-pad, an ee-only owner never sees retention or brand marks.

## 0. Batches (ask in this order; one AskUserQuestion call per batch)
| Batch | Questions | Scopes | Needed before |
|---|---|---|---|
| 0 scope | A0 | all | anything else — it decides which batches follow |
| 1 product & process | A1–A4 | all (A3 ee/both, A4 mech/both) | the spec is read |
| 2 PCB build | B1–B4 | ee, both | SPEC §4 (R-M01) |
| 3 PCB build (cont.) | B5–B8 | ee, both | SPEC §5, layout rules |
| 4 enclosure architecture | C1–C4 | mech, both | the case concept in SPEC §8 |
| 5 enclosure architecture (cont.) | C5–C8 | mech, both | case.yaml |
| 6 print process rows, brand marks, kit, margin | C8a, C9, C10, D3 | mech, both | `print_targets.<t>.dfm_process`, the mark option before the first FDM plate, START_HERE recipient |
| 7 the manufacturability bar + review rounds | D1, D2, E1, E2 | all | day-1 `fab_dfm.bar` / `print_targets.*.accepted`; the G0 review round |
| 8 verification (cont.) + bought parts | E3, E4, F1, F2 | all (E3 mech/both) | the G0 review round, parts.yaml |
| 9 software + reports | G1, G2, H1, H2 | all (G1–G2 ee/both) | the bring-up tool, the first release report |
| 10 CI, retro, envelope, branding | H3, H4, I1, I2 | all | the spec is read |
| 11 debug access, delegation, slicer optimisation | I3, I4, C11 | all (I3 ee/both, C11 mech/both) | the spec is read (I1–I4: found by the first retro — the owner rows the source project needed that no batch asked; C11 by the fifth) |

Twelve batches (0–11), none above four questions; a batch whose questions are all out of scope is skipped.

## A0. Scope (asked first, alone)
**A0 Project scope.** **RECOMMENDED: what the brief implies — `both` when a board is being designed AND will be housed** (today's full flow:
G0 → G1 → G2 → board order, the case gates hanging off G2). *Alt:* `ee` — PCB / PCBA only: schematic, layout, fab DFM, parts, software track
optional; skips batches 4–5, C9, D3, E3, every case gate and the print DFM; no `print_targets`, no `case_yaml`. *Alt:* `mech` — enclosure /
printed / CNC parts only, from a mechanical brief or an imported board envelope / STEP: case pipeline, print DFM, vendor quotes, kits; gates
G0 (mechanical spec) → M1 geometry → M2 first article → case order; skips batches 2–3, G1–G2, I3, KiCad / ERC / DRC / fab DFM, the
electronics parts seed (hardware — inserts, magnets, feet, screws — is still verified [V]); the record id is the STL set's md5
(`scripts/project.py record`), not a board md5. Written to `project.scope`; the templates are resolved with `scripts/project.py scaffold --scope`.

## A. Product, process, material, quantity
**A1 Product class.** **RECOMMENDED: engineering sample / internal tool** — no regulatory claim, compliance = a RoHS table fetched at cut time,
an owner row "engineering sample, not a rated enclosure"; the smallest document set. *Alt:* product for external users — adds UL 94-rated
materials, a CE / FCC / WEEE path, label placement, packaging spec, two more gates. *Alt:* one-off lab jig — home FDM only, no vendor DFM round,
no production cut.
**A2 Quantity and horizon.** **RECOMMENDED: 5 boards / 5 cases first article, design for 50** — stock gate run-relative at 5 × attrition, owner
floors on jellybeans, assembly ≤ 10 min hands-on, ≤ 3 glued pieces. *Alt:* 1–2 units — skip the panel and the assembly SOP. *Alt:* 100+ — panel
by the fab, hand assembly out, a fixture per press-fit step, a second DFM round for the case tooling.
**A3 Board fab and assembly vendor** [ee, both]. **RECOMMENDED: one contract fab with its own DFM viewer and parts library (JLCPCB-class)** — the DFM mirror
copies its viewer, every part [V] on its library, two-sided assembly available. *Alt:* fab + separate assembler — two DFM sets, a stencil / paste
spec you own, consigned parts. *Alt:* prototype fab only, hand assembly — no CPL / rotation work, no basic-part policy.
**A4 Enclosure process and material (per target)** [mech, both]. **RECOMMENDED: two targets — a print service MJF PA12 build of record + a home FDM (PLA /
PETG, 0.4 nozzle) mirror** — the vendor part is premium and rated HB, the home part is the fit / assembly mock-up and every vendor DFM decision is
mirrored the same day. *Alt:* MJF only — no coupons before the first quote, every fit answered by the vendor round. *Alt:* FDM only — an engineering
sample; every legend raised; ≥ 1.6 walls. *Alt:* another process, named in the reason — SLA resin (smoother, brittle, walls ≥ 0.8 / parts ≥ 2 mm,
drain holes, post-cure warp, no snap or press fits; `references/dfm-printed-enclosure.md` §11) or CNC aluminium (corner radii, threads, anodising
build-up, 5–10× the price; `references/cnc-enclosure.md`). Four options: the AskUserQuestion limit.

## B. PCB build (`references/pcb-layout-dfm.md`)
**B1 Layers and thickness** [ee, both]. **RECOMMENDED: 4 layers, 1.6 mm, the fab's default stack-up template named in the yaml** — a solid GND plane under
every signal, a power plane, the template's numbers in the CAD physical stack-up. *Alt:* 2 layers — cheaper; no reference plane, no controlled
impedance, more via work. *Alt:* 6 layers — for dense high-speed; cost ×1.6, longer lead time.
**B2 Copper weights** [ee, both]. **RECOMMENDED: 1 oz outer / 0.5 oz inner** — 0.09 / 0.09 trace-space at the worked-example fab, 0.10 mask dams, the fab's
impedance calculator supports it. *Alt:* 2 oz outer — current capacity and heat spreading; minimum trace / space 0.15 / 0.15, mask dam 0.20 (a 0.4
pitch QFN gets gang openings), no calculator support at the worked-example fab. *Alt:* 2 oz inner — only for a plane carrying > 6 A.
**B3 Controlled impedance** [ee, both]. **RECOMMENDED: no controlled impedance, every differential pair < N cm with skew / uncoupled-length rules** — for
USB 2.0 and short buses; state N in the spec. *Alt:* 90 / 100 Ω pairs on the fab's calculator, impedance option on the order — required for any
multi-Gb/s lane or a pair longer than ~1/10 wavelength; w ≥ 0.20 mm for the ±20 % width tolerance. *Alt:* RF section — a named laminate and a
separate design review role.
**B4 Finish, mask colour, silk** [ee, both]. **RECOMMENDED: ENIG, green mask, white silk** — flat pads for fine pitch, every tier of the fab, cheapest
mask dam rule. *Alt:* black (or another) mask — premium look; mask dam 0.13 at 1 oz, forces the fab's Standard assembly tier at some vendors,
colour-silk options vanish. *Alt:* HASL — cheaper; not flat for 0.4 mm pitch. *Alt:* multi-colour silk — vendor-specific EDA path and 1 oz / white
mask only at the worked-example fab (checked live 2026-09-13); a decision row with the live check.
**B5 Component size and link policy** [ee, both]. **RECOMMENDED: no 0201; 0402 minimum; 0603 where rework is likely; signal 0 Ω links 0603; power-path links
1206 (a basic-library code); cuttable straps as bridged solder-jumper net ties** — the Economic tier's 0402 minimum, hand rework possible, link
size = current rating. *Alt:* 0201 allowed — density; Standard tier only, no hand rework, X-ray per QFN anyway. *Alt:* 0603 minimum — easiest
rework, 20–30 % more area.
**B6 Assembly sides** [ee, both]. **RECOMMENDED: SMT on both sides, THT and press-fit hand-installed** — 30–40 % smaller board; the fab's Standard tier,
fixture bands for press-fit rows, per-side height limits in the yaml. *Alt:* top-only — Economic tier, flat bottom for press-fit backing, a larger
board and case. *Alt:* fab installs THT too — +1 day and a per-joint fee, unused PTH stay solder-free.
**B7 Test points and self-documenting silk** [ee, both]. **RECOMMENDED: one test point per rail and per bus line the bring-up tool reads, ≥ 1.0 mm pads in a
labelled field; every switch, jumper, header and test point carries a silk label with its meaning; pin-1 / polarity marks on every polarised part**
— the technician needs no drawing. *Alt:* probe on component pads — no TP area; no repeatable fixture. *Alt:* edge connector for a bed-of-nails —
for 100+ units.
**B8 Panel and fiducials** [ee, both]. **RECOMMENDED: single boards ≥ 70 mm per side, or a customer panel with rails on the long edges + mouse bites when a
side is narrower; 3 fiducials per assembled side** — the fab's Standard tier needs rails and fiducials; V-cut only when copper is ≥ 0.40 mm from
the line. *Alt:* panel by the fab — its rails land on the short edges (connector ends). *Alt:* no panel, Economic tier — only for top-only boards
≥ the tier's minimum size.

## C. Enclosure architecture (`references/dfm-printed-enclosure.md`, `references/case-pipeline.md`)
**C1 Pieces** [mech, both]. **RECOMMENDED: two pieces — tray + shell, one print orientation each, no supports on visible faces; a removable hood only if a
serviced part sits under it** — the fewest laps, one census per body per target. *Alt:* three (tray + body + hood) — tool-free access to a module;
one more lap, collar rims that need the opposing-face metric. *Alt:* clamshell + lid + bezel — colour accents by piece; ≤ 3 glued pieces, ~3× the
assembly time.
**C2 Retention (hood / lid)** [mech, both]. **RECOMMENDED: screws into inserts (thread-forming screws or heat-set inserts per the material table §1.1)** —
serviceable, coupon-measurable torque, works in PA12 and PLA. *Alt:* magnets — tool-free, Ø6 × 3 N42/N45 pairs, pocket + 0.4 glued (MJF) /
+ 0.1 press (PLA), polarity keyed by an asymmetric boss, ≤ 80 °C; pull force vs gap on the row. *Alt:* none (friction lap) — fit mock-up only.
*Alt:* snap fits — possible in PA12 with a slit ≥ the void gate and an engineered arm; rarely fits a no-yellow bar's space budget; never in PLA.
**C3 Coupling / stacking between units** [mech, both]. **RECOMMENDED: none** — closed rims, no open grooves. *Alt:* enclosed pocket rail in a wider part —
allowed under the closed-rim bar; +2.4 mm width. *Alt:* external clip / bracket — a separate part, no change to the case walls.
**C4 Feet and mounting** [mech, both]. **RECOMMENDED: 4 adhesive flat-top feet in shallow concentric pockets (no counterbore through the pocket floor), PSA
with a primer on PA12 / porous MJF** — the bond area is the whole pocket. *Alt:* moulded-in feet — a wedge / thin skin risk at the checker. *Alt:*
DIN-rail / wall-mount lugs — a strength case in FEA.
**C5 Labelling and identity marks** [mech, both]. **RECOMMENDED: a label carrier (UV-printed plate or adhesive label in a recess label + 1 mm, flat land)
for text; raised legends on the home FDM plate; one engraved mark only where its stroke ≥ the void gate** — legible on every process. *Alt:*
engraved text everywhere — cap ≥ ~6 mm at a 1.2 void gate, else yellow / red. *Alt:* inlay / badge plate — premium, a pinch check on the outline,
a second material. *Alt:* two-tone print (MJF dyed + resin plate, FDM colour bands) — colour on top faces in one Z band per part.
**C6 Fan, vents, thermal** [mech, both]. **RECOMMENDED: passive vents sized from the thermal case; a fan only when the FEA / thermal case says so, bosses =
fan-hole count, recess dropped when the hood prints roof-down** — fewer parts. *Alt:* fan fitted — a 5 V rail, a connector, a fan header row on
the board, an acoustic note. *Alt:* sealed — a heat path through a metal plate; the FEA thermal case is mandatory.
**C7 Light pipes / windows / switch access** [mech, both]. **RECOMMENDED: through holes for LEDs and switches (Ø LED + 0.2), no light pipe on rev 0** — a
backlog row for the pipe. *Alt:* light pipes — hole + 0.1, LED-to-pipe gap verified on the mesh of record. *Alt:* clear window insert — a glued
piece or a clear resin part.
**C8 Two print targets and their fits** [mech, both]. **RECOMMENDED: one yaml, presets `base + overrides`, every fit clearance a per-preset knob decided by a
coupon, every vendor DFM decision mirrored into `home_fdm` the same day** — two versions, one geometry of record. *Alt:* vendor target only — no
mock-up before the order. *Alt:* separate generators — divergence nobody diffs.
**C8a — which `design/dfm_processes.yaml` row each target gates on** (`print_targets.<t>.dfm_process`; `references/print-dfm.md`). Selectable rows of
the shipped table: `jlc_mjf_pa12` · `jlc_sla_9600` · `jlc_fdm` · `xometry_mjf_pa12` · `protolabs_mjf_pa12` · `home_fdm_04` (`hp_mjf_guide` is BLOCKED
until its page is fetched). **RECOMMENDED: the vendor's own row for the vendor target + `home_fdm_04` for `home_fdm`.** *Alt:* a vendor not in the
table — ONE new row with its published minimums `[V]` (URL + date) and `validated_on: []` before the first upload; the retro carries it to the skill.

**C9 Brand marks / logos on FDM parts** [mech, both] (`references/dfm-printed-enclosure.md` §8.1). **RECOMMENDED: a TOP-face feature (deboss or raised
0.6 = 3 layers) under `ironing_type: top` (never `topmost`), top shell ≥ recess + 1.0, the part oriented so the marked face is a top face, one
mark coupon first on the plate** — one filament, one ironing pass builds face and mark alike. *Alt:* a flush AMS colour body in the bed layers —
marked face on the bed, mark mirrored in the model, 2 layers (0.4) for a dark mark / 3 for a light one on a dark body; the crispest boundary and a
second colour, at 2 filament changes per 2 layers + purge; needs an AMS. *Alt:* both, as two plates in the kit — the owner picks by eye on the
first print. *Alt:* a face-up printed plate glued into a keyed rebate (spans > 10 mm split by glue lands) when the mark must sit on a bed face
without an AMS. *Never:* a bed-face deboss (bridge-ceiling "webbing"), a vertical-wall deboss (stair-steps), webs / discs that alter the artwork.

**C10 Print kit hand-over and snug fits** [mech, both] (`references/print-kit.md`). **RECOMMENDED: a generated `START_HERE.md` (print order with the
project-file names, assembly sequence, numeric report-back) with the report-back recipient named here; every kit text from the knobs through the
kit text gate; snug-fit features (crush ribs, press lips) ship as a bracket plate at three values and the owner picks the knob after the first
print** — the technician needs no repo, the irreversible steps (magnets, CA) are instructed. *Alt:* READMEs only — the technician reconstructs the
order from the sheets. *Alt:* the engineer picks the fit value from the tolerance row alone — no bracket, one reprint if it binds.
**Owner inputs:** the recipient for the report-back (a chat, a name); who decides the fit knob after the bracket print (RECOMMENDED: the owner).
The picked value has a landing key, `kickoff.enclosure.fit_result` ("pending: bracket print" until the print; the arrival checklist row E-FIT closes
it, SKILL §10.1) — an answer that is "the owner picks after a print" is still an answer with a home, not a loose end.

**C11 Slicer optimisation target** [mech, both] (`references/fdm-print-optimisation.md` §4). **RECOMMENDED: minimal waste** — colour changes grouped
low in one Z band, `flush_into_infill` / `flush_into_support` on bodies whose changes sit above the first infill layer (a 2-layer bed-face mark
gains nothing — stated per plate), flush volumes calibrated per filament pair, prime tower off on single-filament plates, purge grams reported
per plate against the chute-only slice. *Alt:* strength — 4–5 walls, gyroid / cubic 20–25 %, modifier meshes at 100 % around inserts / bosses /
magnet pockets, orientation by load. *Alt:* surface — inner/outer/inner walls, seam at the back, `ironing_type: top` on marked faces, Arachne,
precise outer wall. *Alt:* speed — 3 walls, 10 % gyroid, no ironing. Every knob set is in the plate yaml and proven from the g-code (`purge_g`,
`tower_g`, `wall_loops` read back); written to `kickoff.enclosure.optimise`.

## D. The manufacturability bar (SKILL §1.2) — the owner confirms the default explicitly
**D1 The bar.** **RECOMMENDED: zero errors, zero warnings, no waivers** — board: DRC 0 / 0 / 0 warnings, fab DFM 0 Danger / 0 Warning; printed
enclosure: census 0 unaccepted FAIL, slicer log clean, vendor checker no flag by API read, no yellow / red; CNC: vendor DFM clean; recorded as
`fab_dfm.bar` and the print targets' `accepted: []`. *Alt:* warnings allowed with a dated acceptance carrying vendor evidence — the checker
re-asserts each one every run; the merge lists every acceptance added per round. *Alt:* vendor-clean only (no own mirror) — one lost quote round
per surprise; not recommended.
**D2 What may be waived (default: nothing).** **RECOMMENDED: nothing — an item is fixed through the generator, or a dated `accepted` / `dfm_accepted`
entry with the vendor's written acceptance is the only exception, per refdes / per cluster, listed in the merge.** *Alt:* a named class waived
(e.g. the fab's "sharp trace corner" presence check) — one decision row per class with the vendor's statement. *Alt:* prose waivers — forbidden
(the waived 0.88 × 141 mm lip cracked on five parts).
**D3 Design margin and tolerance source per target** [mech, both]. **RECOMMENDED: walls at the checker's line + 0.1 (MJF), first-article caliper table
replaces the vendor's published tolerance after the first order, INFO until then** — no "PASS by design". *Alt:* design at the line — the mesh
samples 0.01 under and the argument is lost. *Alt:* + 0.3 everywhere — heavy, slow, unnecessary on a 2 mm shell.

## E. Verification (SKILL §5, `references/pcb-layout-dfm.md`, `references/dfm-printed-enclosure.md`)
**E1 Review rounds per gate.** **RECOMMENDED: one review round (in-session + two external models per role, adversarial verifiers, merge) before
G0, G1, G2, the board order and the case order; a delta audit after a bounded change** — external models via a read-only CLI. *Alt:* in-session
only — same model family, weaker; say so in the merged report. *Alt:* owner review only — no blind pass; the owner reads every heat map.
**E2 Visual inspections.** **RECOMMENDED: routing inspection on ≥ 40 px/mm tiles, silk legibility read from renders, six face renders per printed
body incl. the sole, every designed asymmetry rendered and listed** — geometry-only checks passed blank bars and mutilated words. *Alt:* renders
only at release — the sole with the off-centre pockets HAD been rendered and nobody asked.
**E3 Coupons, dummies, first article** [mech, both]. **RECOMMENDED: FDM coupons (text, walls, fits, insert + torque) and a board dummy (two-piece AND one-piece)
before the first case print; a first-article caliper table on every received part** — the fit numbers become yaml knobs. *Alt:* order the case
and measure — one vendor round per surprise. *Alt:* coupons at the vendor too — 1 week and a quote per coupon; the probe method is cheaper.
**E4 Vendor DFM before the order and FEA.** **RECOMMENDED: the fab's own DFM viewer on board AND panel, the print service's checker read from its
analysis API per body, both filed with raw evidence before any order; FEA on the case (torsion, drop, boss load, thermal) and the board (press-fit,
side load) with the owner accepting any WARN by row** — the gates in `templates/GATES.md`. *Alt:* vendor DFM only after ordering — the vendor's
review mail becomes the review. *Alt:* no FEA — for a lab jig only.

## F. Bought parts (`references/part-verification.md`)
**F1 Acceptable verification sources.** **RECOMMENDED: the fab's parts library API + page for electronics ([V] only after a live fetch this
session); the manufacturer's product page + PDF TDS for hardware; plain-HTML dealers for price / stock; snippet-only numbers stay [K]** — never an
invented number. *Alt:* distributor pages the owner opens logged in (McMaster, Digi-Key, Mouser are login- or bot-walled) — a BLOCKERS row per part
with the exact URL for the owner. *Alt:* owner-supplied part list taken as [V] — only with the owner's fetch date and URL on each row.
**F2 Stock policy and alternates.** **RECOMMENDED: stock ≥ qty × boards × 1.2 for every code, ≥ 1 000 for jellybeans, an `Alt_MPN` verified for
every extended part, frozen `stock_snapshot.json` once the order is PLACED** — the morning-after shelf never grades a placed order. *Alt:* "> 0"
gate — a stock of 4 passed a 5-board run once. *Alt:* global sourcing / consignment for a named part — +2–3 weeks, inspection fees, a row per part.

## G. Software and test (`references/software-track.md`)
**G1 Modes and refusal posture** [ee, both]. **RECOMMENDED: an operator mode and an engineering mode; guards WARN and THROTTLE, never refuse, until the owner
approves the criteria set; both levels printed** — a fixed cap with a hidden WARN was unreachable once. *Alt:* refuse on any limit — safer for an
external user; blocks bring-up. *Alt:* engineering mode only — no technician manual.
**G2 Criteria and codes** [ee, both]. **RECOMMENDED: criteria as YAML the tool reads (T-nn ↔ limits, owner-approved in a D row), PASS / FAIL / INCONCLUSIVE
with reason codes from one list, the technician table generated from it** — one source. *Alt:* limits in code — three copies drift by the second
revision.

## H. Release, production cut, feedback loop (`references/release-and-cut.md`, SKILL §13)
**H1 Report set.** **RECOMMENDED: PCB + case design reports generated (DRAFT until the owner's line), release notes with a source per number, the
renders / FEA composites as collateral, an annotated tag** — nothing hand-typed. *Alt:* release notes only — no traceability matrix.
**H2 Production cut.** **RECOMMENDED: the full document set (manuals, manufacturing spec incl. material rating and label placement, SOPs with
`[OWNER]` records, analysis index, compliance table) built by one generator into `docs/production/<md5-8>/`, records filed as they happen** —
`templates/production_cut.yaml`. *Alt:* manufacturing spec + SOP only — for an internal tool with one builder.
**H3 CI and repository hygiene.** **RECOMMENDED: PR check = the adopt gates, nightly = the case chain selftests, release = the fresh-checkout gate;
a re-layout + deletion pass at the order through `reorg_paths.py`** — the developer runs the same commands. *Alt:* no CI — the clone gate by hand
before every tag.
**H4 The feedback loop into the skill.** **RECOMMENDED: every agent appends to `LEARNINGS_LOG.md`; at the production cut `scripts/skill_retro.py`
drafts the skill's next changes and a retro report goes to the skill repo as a PR** — the skill gets better with each project (SKILL §13). *Alt:*
no retro — the next project repeats this one's rounds.

## I. Identity, envelope, delegation (added by the first retro — the owner rows that recurred and no question asked)
**I1 Envelope: fixed or grows.** **RECOMMENDED: the board grows as routing needs, the case follows; connector positions and the form-factor
class are fixed** — clean routing beats a millimetre. *Alt:* envelope fixed by a mating part (a cage, a rail, a pocket) — a routing budget
per iteration and a decision row when it is missed. *Alt:* smallest possible — expect two placement iterations per connector.
**I2 Branding, look and identity.** **RECOMMENDED: product name + logo lock-up as one designed block on the silk and on the case (label
carrier or gold copper artwork), a consistent legend grid, no exposed copper except designed artwork, the order number hidden** — a product, not a
coupon. *Alt:* engineering look — refdes everywhere, no logo, cheapest. *Alt:* premium finish (black mask, anodised, two-tone) — the B4 / A4
consequences apply.
**I3 Debug and service access** [ee, both]. **RECOMMENDED: a simple wire header + cuttable straps for the debug path, reachable with the hood off; no
vendor-specific pod connector exposed by the case** — one keyed header, one manual page. *Alt:* a dedicated debug connector in the wall — a
window, a tolerance stack row, a light-pipe-class part. *Alt:* none — the board is programmed in the fixture only.
**I4 Delegation while the owner is offline.** **RECOMMENDED: "go with the recommended option" applies to every OPEN agent proposal below a
named class (parts alternates, copper rules, case fits); spec values, gate cells, orders and payments never** — quoted in a D row, checked at
every pause point. *Alt:* nothing delegated — the agent stops at every OPEN row. *Alt:* full delegation for a bounded window — the record quotes the
window and lists every action taken.

## What the answers write
| Answer | `project.yaml` | Other records |
|---|---|---|
| A0 | `project.scope` | CLAUDE.md scope line, GATES.md rows (scaffold), KICKOFF_ANSWERS `n/a (scope)` rows |
| A1–A4 | `kickoff.product_class`, `kickoff.quantity`, `kickoff.fab`, `print_targets.<t>` (vendor, process, material, rating) | SPEC §1, §8; D rows |
| B1–B8 | `board.layers / thickness / copper / stackup_template / impedance / finish / mask / silk / min_package / link_parts / sides / test_points / panel` | SPEC §4–§6 (R-M01…), `design/<board>_board.yaml`, `design/dfm_thresholds.json` (source + date) |
| C1–C11 | `kickoff.enclosure` (pieces, retention, coupling, feet, labelling, fan, light_pipe, targets, marks, kit_recipient, fit_decider, fit_result, optimise); C8a `print_targets.<t>.dfm_process` | SPEC §8, `design/case.yaml` presets + `fits` knobs; START_HERE report-back recipient; the plate yaml `optimise:` block; ARRIVAL_CHECKLIST E-FIT |
| D1–D3 | `fab_dfm.bar`, `print_targets.<t>.design_margin / tolerance / accepted` | GATES.md `{{D-BAR}}` row id, CLAUDE.md rule 9 |
| E1–E4 | `kickoff.verification` (rounds, visual, fea), `kickoff.coupons` (E3) | GATES prerequisites, `workflows/` model list |
| F1–F2 | `kickoff.sourcing` (sources, stock_floor, attrition) | PARTS_VERIFICATION header, BLOCKERS |
| G1–G2 | `kickoff.software` (modes, posture) | SOFTWARE_ARCHITECTURE.md §1/§3, test_criteria.yaml header |
| H1–H4 | `kickoff.release` (reports, cut, ci, retro) | production_cut.yaml, ci templates, SKILL §13 |
| I1–I4 | `kickoff.identity` (envelope, branding, delegation), `kickoff.debug_access` (I3) | SPEC §1, §4; CLAUDE.md conventions; the pause-point owner list |

The template `templates/project.yaml` carries every key above as a slot (`kickoff:` mapping, `board:` block); `scripts/project.py kickoff --check`
reads KICKOFF_ANSWERS.md and fails on an answered row whose `Written to` key is still missing from project.yaml.
