# cnc-enclosure.md — a machined (aluminium) enclosure piece: the rules a quote-page DFM will hold you to

Short by design: the source project quoted CNC hoods (JLCCNC, 6061, 2026-09-20) and did not order one, so every number below is either the
vendor's published capability **[fab capability: verify live, cite the date]** or machining practice **[physics]**; nothing here is measured on a
received part. The chain (yaml → generator → STEP → quote → drawing) is `references/case-pipeline.md`; the quote-form mechanics are
`references/fab-dfm.md` §6.

## 1. Geometry rules
- **Internal corner radius ≥ tool radius** **[physics]**: a pocket corner cannot be sharper than the cutter; design inside corners at
  R ≥ 1.0 (Ø2 tool) for pockets ≤ 10 mm deep, R ≥ 1.5–2.0 deeper; sharp inside corners = manual quote or an EDM surcharge. Outside corners any.
- **Pocket depth ≤ 4 × tool diameter** at the pocket's corner radius **[physics]** (a deep narrow pocket needs a long tool: chatter, cost); a
  slot narrower than 1.5 mm or deeper than 5 × width goes to manual quote at most services.
- **Minimum wall ≥ 0.8–1.0 mm aluminium** **[fab capability]**, 1.5 for a wall that is machined on both sides (holding force, vibration);
  1.2 for thin floors under a pocket.
- **Threads**: tapped holes M2 … M8; thread depth ≤ 3 × diameter (tap length); ≥ 2 × diameter of solid material around the hole; specify the
  thread on the drawing (STEP carries a plain hole); helicoil / insert if the boss is thin **[physics]**.
- **Tolerances**: general ±0.1 mm (ISO 2768-m) is the free default; a fit (lid lap, connector window) is called out on the drawing with its
  tolerance; do not tolerance what nothing mates with **[fab capability]**.
- **Text**: engraved ≥ 0.5 mm stroke / 0.2–0.3 deep (single-line font for a small tool); raised text is a pocketed field and costs machining
  time everywhere but the letters.
- **Deburr / edge break** 0.2–0.5 × 45° on every external edge (a drawing note "break all edges 0.3 max") **[convention]**.

## 2. Finish
- **Anodising** adds 5–25 µm per surface (type II) and grows a thread / shrinks a bore by that much: **mask threads** or size the bore for
  the build-up; bead-blast before anodising rounds edges ~0.05–0.1 mm **[physics]**. Colour anodising is not colour-stable in UV for reds /
  purples; black and clear are. State finish, colour, gloss and masked features on the drawing and the order sheet.
- Powder coat adds 60–120 µm — clearances at every mating face and window.

## 3. Quote page (worked example: JLCCNC, 2026-09-20 — verify live)
- A **true B-rep STEP** (cadquery / OCP export) quotes instantly; a faceted STL-sewn STEP goes to manual quote.
- A finish change **drops the mandatory drawing upload** — re-upload the PDF before Save.
- The drawing PDF carries: material + temper, finish + masked features, thread callouts, the two or three fitted dimensions with tolerances,
  the general tolerance class, edge-break note, quantity. Generated from the same yaml as the STEP (dimension lines = yaml numbers).
- Nothing saved / carted / agreed / paid (`references/vendor-review.md` §1); the quote figure + screenshot go to `60-orders/quotes/<date>/`.

## 4. Gate before the order (the "Case order" row in `templates/GATES.md`)
The vendor's DFM clean (no manual-quote fallback, no flagged feature), every inside radius ≥ the rule, every wall ≥ the rule as MEASURED on
the STEP/mesh (the census script works on an STL export of the B-rep), the interference check against the board mesh of record 0 mm³ with
the worst-case clearance row (case ±0.1, board ±0.2, anodising build-up), the drawing's dimensions equal to the yaml, material rating on the
order sheet (6061-T6 UL 94 n/a — metal; thermal path noted if the case is a heat sink).
