# fab-dfm.md — mirror the fab's DFM checker in-repo

## 1. Why
CAD DRC at the fab's published capability limit passes and the fab's own DFM viewer still lights up: the viewer grades a value EQUAL to its warning
threshold as Warning, applies checks the CAD has no rule for (THT-to-SMD spacing, mask bridge, silk-to-hole, unconnected via = copper on one layer
only, sharp corner) and counts by its own definitions. Two quote rounds were lost to this before the mirror existed. Build the mirror before the
first quote and make it part of the adopt rule.

## 2. The generic recipe
1. **Thresholds file** `20-design/dfm_thresholds.json`: copy every check name and its danger/warning numbers from the fab's viewer (cite the viewer URL +
   date in `source`); checks the fab lists without numbers get `null` (every found item grades Warning, as the viewer does); `project_min` holds the
   project's own rule for checks the fab reported clean.
2. **Measurer** (project-specific, CAD-bound): re-measure each check from the board file — tracks, vias, pads as effective polygons, STORED zone fills
   (no refill), silk as glyph/stroke polygons, the true outline polygon — and emit `30-board/layout/dfm_items.json` items `{check, value, refs, layer, xy}`.
   Keep it in the project's `gen/`; the source project's measurer (26 checks, pure-python capsule/polygon distances on a 1 mm grid over
   KiCad SWIG shapes) is the worked example. The items contract:

   | Field | Type | Rule |
   |---|---|---|
   | `check` | string | **byte-equal to a key of `thresholds.checks` or `project_min`** (the fab's spelling); an unknown name grades INFO and the grader prints a WARNING listing it |
   | `value` | number or null | the measured quantity in the fab's unit (mm unless the check is a count/percentage); `null` = presence-only item (graded Warning when the fab lists the check without numbers) |
   | `refs` | list of refdes | every part involved (a pair item names both); empty = bare track/via/zone item that cannot be accepted, only fixed |
   | `layer` | string, optional | CAD layer name, for the report line |
   | `xy` | [x, y] mm, optional | where, in the board frame, for the report line |

   One item = one violation site (the viewer counts sites, not nets). An acceptance (`dfm_accepted`) matches an item only when its `check` is equal
   and every refdes of the item is listed; the dict form `{REF: n}` is a per-ref budget applied to that acceptance entry only.
3. **Grader** `scripts/dfm_check.py`: value ≤ danger → Danger; danger < value ≤ warning → Warning; else Good; 2-decimal half-up rounding before
   grading (viewers work at 2 decimals); project rule at full precision with a 5e-4 tolerance. Exit 1 on any open item.
4. **Acceptances** by refdes with reason, **date and vendor evidence** (`dfm_accepted` in the board yaml; the fields `fab_dfm.bar.accepted_requires`
   names — an entry missing one is ignored and listed): a pair item needs BOTH refs listed; dict form `{REF: n}` is a budget; bare tracks/vias
   cannot be accepted — fix them. The bar is 0 Danger / 0 Warning open (SKILL §1.2).
5. **Design strictly greater**: rules at limit + 0.01 (0.16 where the fab says 0.15), annular ring > the minimum, silk line ≥ the minimum + 0.01.
6. **Fixture disagreements**: when the selftest fixture and the checker disagree, print the checker's REASON before touching either — the "extra"
   unconnected-via hits were correct (copper on one layer only); the fix was in the fixture.
7. Run the fab's viewer on every upload (board AND panel) and diff its counts against the mirror; keep the exported PDF under `60-orders/quotes/<date>/`.

## 3. Silk rules that the mirror needs
- No via/PTH hole under a silk TEXT cell (via keep-out from the text bbox at route time); clipping silk at holes is for hairlines only — it mutilated
  26 words once.
- Silk-to-edge against the TRUE outline polygon (notches), silk-to-mask incl. the fab's expansion, glyph stroke ≥ the fab minimum by a morphological
  opening (the CAD's TrueType thickness warning is an estimate).
- A legibility gate READS the rendered silk (an agent looks at the PNG) in addition to geometry.

## 4. Panel
- Standard PCBA at the worked-example fab needs every side ≥ 70 mm; its automatic rails land on the SHORT edges (where connectors often are). A
  narrow board needs a **customer panel**: 1-up + rails on the LONG edges, mouse bites (V-cut needs ≥ 0.40 copper-to-edge), 3 fiducials, tooling
  holes, break-line pour keep-outs, drill/place origin unchanged. Own minimal SWIG implementation (move every object +rail, redraw the outline
  tab-interrupted) beat installing a panel plugin into the CAD's Python.
- Gate the panel on its STORED fills (`BuildConnectivity()` before every fill, or pours starve silently), per-zone area within 1 % of the source,
  Gerber regions bbox-matched, segment/via counts equal, DRC 0/0.
- Run the fab DFM on the PANEL zip: a merged drill file cannot mark mouse-bite holes NPTH (30 cosmetic "unconnected via"), rail fiducials add
  warnings — a remark sentence or a separate NPTH drill settles it.

## 5. Quote form traps (worked example: JLCPCB, 2026-09-20/22)
- Options easy to miss: press-fit holes (+35 on a 5-panel order), "Edge Rails/Fiducials = Added by Customer" (the form's wording) <!-- voice: ok -->, "Panel by Customer" REQUIRES the panel
  format column × row, precision outline, "confirm production file". The first two PCBA quotes were both wrong.
- The order remark is GENERATED from the rule file + board (copper minimums, solder-free holes, THT neighbours); only the vendor-drawing paragraph is
  static. Typed remarks rotted twice.
- The remark has TWO readers. The generated technical block (refdes, hole sizes, distances) is for the engineer; the fab's customer-service desk
  reads it first and cannot parse it ("we cannot understand it very well" cost a three-mail loop, 2026-09-29). Put a PLAIN-WORDS paragraph ahead of
  the table, one sentence per item, verbs and functions instead of refdes and numbers: "the connector is placed and reflowed normally; the two
  larger unplated holes under it are for its own locating pegs, the twelve small plated holes are for a cage we press on after delivery - leave all
  fourteen without paste or solder"; "the one through-hole header is hand-soldered after reflow - do NOT wave solder, the other side is fully SMT";
  "the USB shell legs reflow with the SMT side, partial slot fill accepted". Pre-empt the questions the desk always asks: which PART a hole belongs
  to (say "holes in the PCB"), wave soldering for any THT part on a two-sided SMT board (say no, explicitly), and the fallback ("ship that part loose
  in the bag"). Expect one to three clarification mails; answer each with the vendor drawing's picture of the feature. Their screenshots arrive as
  links to the fab's message-file API, not attachments - download and file them the same day, the links are session-bound.
- Holes in a remark are cited by drill tool / finished diameter / count with coordinates in the drill-file frame (origin = the aux origin),
  never by CAD pad names: pad names are not exported to Gerbers or Excellon, so a remark that says "S1-S12" names nothing the fab's
  engineer can see. Attach a marked picture generated from the drill file (the same data the fab has).
- Driven browser: session expires within hours; a fresh tab on the orders URL is the decisive signed-in check (redirect = out); reload the quote tab
  after re-sign-in. Vue tiles ignore `element.click()` from a script — use real input events; the hidden file input needs its `hide` class defeated;
  material lists re-order after finish changes — click by text, never by position (a positional click bought the wrong laminate at 2× the price).
- DFM viewer: rows read "Unanalyzed" until its own button is pressed (~60 s); the export is an icon-only toolbar item; the PDF lands in Downloads.
- PCBA: a part with a stock shortfall is auto-deselected; a catalogue part without a fab footprint shows nothing until the paid confirm step.
- Prices are read from the live form and written next to the generated parameters; `newest_quote()` accepts only a row whose price cell starts
  with a figure.

## 6. Print-service / CNC DFM (worked example: JLC3DP / JLCCNC)
- Print DFM = a thin-wall heat map + one yes/no risk gate (API `thinWall`). The legend (JLC3DP 2026-09-28: grey ≥ 1.2, yellow 0.5–1.2, red < 0.5)
  is the **checker's** colouring; the vendor's **published printable minimum** is a different number (its review mail: nylon ≥ 1.0, resin ≥ 0.8);
  the **owner's bar** (no yellow) is a third — keep the three apart (`references/dfm-printed-enclosure.md` §1) and put them in `print_targets`.
  Compare process rule sets, not colours. Its only numbers are volume / area / bbox — turn a colour into a number with your own ray-cast.
- FDM refuses parts < 30 × 30 × 10 mm per file; **SLA: the Edit dialog refuses a PART thinner than 2 mm overall, the wall minimum is 0.8** (two
  different numbers — `dfm-printed-enclosure.md` §11); a mandatory customs cascader makes Save a silent no-op; dyeing / post-processing is an
  add-on that changes dimensions (§1.2 there); pricing linear in quantity.
- CNC: a faceted STL-sewn STEP goes to manual quote; a true B-rep STEP (cadquery) quotes instantly; a finish change drops the mandatory drawing
  upload — re-upload before Save. The machining rules (corner radii, walls, threads, anodising build-up) are `references/cnc-enclosure.md`.

- After the order: the print service's engineer review arrives by mail with per-line file ids; the flow, the boundaries and the quote-page
  mechanics (`getFileAnalyzeResult` → `previewUrl` heat map for a "clean" part; Edit dialog saved = form state; "audit failed" mail = Replace
  File enabled) are in `references/vendor-review.md`.

## 7. Worked-example numbers (JLCPCB, 2026-09) — the full build-rule set with tags is `references/pcb-layout-dfm.md`
2 oz outer: track/space 0.16/0.16 (published), via 0.30 drill / 0.62 ring (annular > 0.15 to escape Warning), pad-to-edge warning 0.20, PTH-to-trace
0.23 (project 0.24), silk line 0.16, silk-to-hole 0.22, mask bridge 0.20, hole-to-hole 0.50, PCBA min side 70 mm, V-cut copper-to-edge 0.40.
These are the values that were live then; fetch the current capability page before using them.

## 8. Fab package gate: the placed-order stock freeze (project-side generator; contract here)
The morning after an order is placed the live stock gate turns against its own package: the fab's shelf shows what the order consumed (a part at
4 → 0), `fab_package --check` re-derives a different PCBA verdict and fails, and its selftest (built on the live records) fails with it.
- **Rule:** a package whose order is PLACED — an owner row in the decision log matching `markers.placed_regex` AND naming the package folder — is
  judged on `stock_snapshot.json` inside the package: the stock records of its BOM codes as at the build commit, frozen once by
  `--freeze-stock` and hashed in the package MANIFEST. `--check` on a placed package without the snapshot says so (run `--freeze-stock`) instead
  of grading on live data. Live re-checks after the order are still recorded in `PARTS_VERIFICATION.md`; they do not grade a frozen package.
- **Selftest fixture:** the selftest never reads the live stock file — it builds a fixture (every record in stock, dated today) and points the
  checker at it; the package logic is under test, not the market.
- The frozen package: fab files, panel/, board_id.txt byte-identical forever (a rebuild re-exports the panel and re-stamps the commit — never on
  a placed order); generator-owned prose (ORDER_PARAMETERS, PACKAGE.md) may be re-derived with a `--refresh-notes` that re-hashes the manifest.
- Look for a moved records file under both its old and new path when reading the build commit after a re-layout (`scripts/reorg_paths.py --map`).
