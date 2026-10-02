# part-verification.md — live parts only

## The rule
A fab/distributor part number enters the BOM only after a fetch of its live page **in this session** confirms MPN, package, stock and library
class (basic/extended or the fab's equivalent). Cached numbers, hand-off numbers and memory are not evidence: the first hand-off of the source
project carried wrong numbers and a stock of 4 passed a "> 0" gate for a 5-board run.

## Tags
| Tag | Meaning | Allowed on a fitted part? |
|---|---|---|
| **[V]** | verified live this session: URL + date + stock + class recorded | yes |
| **[K]** | known-unverified (number from memory / an old note / a datasheet) | no — the schematic generator refuses `Confidence K` on a fitted part |
| **[K owner-read]** | the OWNER read the distributor page (date, who, which page) and our tools could not fetch it (login / bot wall) | as a sourced hardware line in PROCUREMENT with the owner's read quoted and an `ARRIVAL_CHECKLIST` row; promoted to [V] only by a fetch of ours — never on the owner's word alone (rule 1 is about evidence we can re-check) |
| **[S]** | select-by-parameter (value, package, tolerance known; MPN not chosen yet) | no — becomes [V] when chosen and fetched |
| **N/A** | global-sourcing / owner-supplied line (no fab code by design) | yes, with an MPN and a procurement row |

## PARTS_VERIFICATION.md table
One row per check, append-only:

| Date | Refdes / value | MPN | Fab code | Package | Stock | Class | URL fetched | Result | Tag |
|---|---|---|---|---|---|---|---|---|---|

Re-verify before every package build (`verify_parts` style script: machine endpoint first, human page as evidence) — stock moves daily.

## Machine endpoints (worked example: JLCPCB / LCSC, verified 2026-09-13)
- `https://wmsc.lcsc.com/ftps/wm/product/detail?productCode=Cxxxx` — JSON (`productModel`, `encapStandard`, `brandNameEn`, stock, prices).
- `https://cart.jlcpcb.com/shoppingCart/smtGood/getComponentDetail?componentCode=Cxxxx` — JSON (`componentModelEn`, `componentLibraryType`, stock, datasheet URL): the basic/extended + fab-stock check.
- `https://www.lcsc.com/product-detail/Cxxxx.html`, `https://jlcpcb.com/partdetail/Cxxxx` — server-rendered evidence pages.
- EasyEDA component API needs a browser UA (403 with a bare one); `easyeda2kicad` fetches symbol/footprint/3D. Post-process converted footprints: zero-ring pegs → NPTH, `attr smd` when every numbered pad is SMD, real pin electrical types (ERC depends on them), duplicate-numbered pegs renumbered `MP<n>`.
Record every endpoint that answered in `90-log/ENV.md`; a fab that changes its API is a BLOCKER row, not a guess.

## Gates that catch the usual mistakes
- **value ↔ MPN ↔ code**: the BOM groups by fab code; a value edited on the symbol does not change the ordered part. Decode the MPN (chip codes) and refuse a group with > 1 value or a Value ≠ decoded MPN.
- **symbol MPN ↔ live MPN**: the fetched record's MPN must equal the symbol field.
- **stock gate run-relative**: `min = ceil(qty_per_board × boards × 1.2)` for EVERY code; below it the package says "PCBA-complete: no — <code> stock N < min" under a STOCK SHORT banner. Owner-preferred absolute floors (e.g. ≥ 5000 for jellybeans) on top.
- **DNP**: DNP parts excluded from BOM and CPL, marked on the symbol and the footprint; DNP does not imply exclude-from-BOM in the schematic tool — set both attributes explicitly.
- **BOM ⊂ CPL** (fiducials, owner-supplied parts are CPL-only), every CPL row inside the outline, drill via count = board vias.
- **CPL rotation**: offsets per footprint family from two independent rotation databases; only agreeing rows are `review: false`; a `+90` for 1×N headers is confirmed only by the fab's 3-D preview. The REVIEW worklist follows the rule (unverified offset), not the side.
- **Alternates**: `Alt_MPN` / `Alt_LCSC` fields on every symbol; alternates are verified the same way.

## Datasheets (rule 3)
Every VERIFY item in the findings is closed by reading the primary datasheet, page/section cited in `10-spec/datasheet_notes/<part>.md`, before the
part is drawn. If the vendor site blocks the fetch: `90-log/BLOCKERS.md` row (what was tried, result, workaround — e.g. an older revision read via
an archive with the deltas marked unknown). Vendor library footprint vs vendor drawing: the drawing governs; the vendor STEP is the only source
for heights. Values read from curves are marked "not in datasheet text" with the reader named.

## Bought hardware (feet, screws, inserts, labels) — where a live read is possible
Rule 1 applies to every purchased item, not only fab codes — and for hardware the usual pages are closed to an agent: **McMaster-Carr answers every
product URL with a login wall for automated / new sessions** (HTTP 200 JS shell; rendered "To continue browsing, please log in"), **Digi-Key sits behind
Cloudflare, Mouser / Newark / Farnell / RS / Keystone / Essentra return 403**. What does read: the **manufacturer's own product pages in a real browser**
(3M Bumpon pages rendered), the **manufacturer's PDF TDS by curl** (dimension tables, tolerances — ±0.5 mm on moulded shapes), and **small plain-HTML
dealers** (price, stock). So: verify on the manufacturer's site + TDS → [V]; a price or number seen only in a search snippet → [K]; a login-walled
source → `90-log/BLOCKERS.md` row per rule 10 with the exact URL and filter set for the owner to open logged in (2 minutes) — never invent a
number, never promote a snippet to [V]. Fit numbers belong beside the part (pocket Ø − foot Ø margin at the tolerance limit; height above the sole;
adhesive area on an annulus when the pocket floor is opened by a counterbore), and a count that disagrees between records (yaml five, guide four) is
flagged in the decision row, not resolved silently.

## Fields on every symbol
`MPN, Manufacturer, LCSC (or the fab's code field), Datasheet (the live URL of the fitted code), Confidence (V/K/S/N/A), Alt_MPN, Alt_LCSC`.
The generator copies them to the footprint as hidden properties so schematic parity holds.

## Hardware line schema (what a buyer needs to execute the line — `templates/parts/PROCUREMENT.md`)
`Line | Class | MPN | Manufacturer | Spec (thread × length, Ø × h, grade, size) | Drive / head / coating / colour | Material / finish | Qty per unit |
Spares % | Order qty | MOQ | Unit price (currency, date) | Supplier URL (how verified) | Equivalent MPNs | RoHS / REACH source | Fit numbers | Tag`.
The `PARTS_VERIFICATION.md` columns (fab code, package, class) do not fit a screw or a magnet: hardware rows put the spec in "Refdes / value" and
"Package", the supplier in "URL fetched", and the class in "Class" (screw / insert / magnet / foot / label / O-ring / light pipe).

## Hardware classes and what to verify per class
| Class | Verify on the manufacturer page / TDS | Fit numbers beside the part | Notes |
|---|---|---|---|
| screws (machine, thread-forming for plastics) | thread, length, head Ø / height, drive, material, finish, tensile class | counterbore Ø / depth, pilot Ø for thread-forming (TDS), engagement length | thread-forming (Delta PT / Remform class) is the normal MJF fastener; torque `[OWNER]` until the coupon |
| heat-set / press-fit inserts | OD, length, bore Ø + depth from the TDS, install temperature per material | boss OD ≥ 2 × insert OD; 0.1–0.2 below flush | PA12 needs a higher iron temperature (Tm ≈ 178 °C); PLA creeps above ~45 °C under preload |
| magnets | grade (N35 … N52; hobby sizes Ø6 × 3 / Ø4 × 2 exist only at 80 °C grades on login-free vendor pages — H / SH grades start at 2 × 2 / 4 × 4 via distributors), coating (Ni-Cu-Ni), max operating temperature (N35 ≈ 80 °C, H grades 120 °C), pull force vs gap curve, tolerance | pocket Ø = magnet Ø + 0.4 glued (MJF) / + 0.1 light press (PLA), depth = h + recess, pocket wall ≥ the wall gate | polarity keyed by geometry (asymmetric boss), never by a mark cut into the face; imperial 6.35 vs metric 6.0 stated |
| adhesive feet / pads | shape (flat-top vs hemisphere), Ø × h, adhesive family, **substrate compatibility table** | pocket Ø − foot Ø at the tolerance limit (moulded ±0.5), adhesive annulus area | **PA12 is a low-surface-energy plastic and MJF surfaces are porous: most PSA feet (incl. acrylic Bumpon) need a primer or fail — the TDS substrate table (or a named primer) is part of the [V] check for anything bonded to nylon** |
| labels / badges / inlay plates | material, thickness, print process, adhesive, temperature rating | recess = label + 1 mm each side, flat land, orientation | regulatory / serial marks go here (release-and-cut §7) |
| O-rings / gaskets | ID, cross-section, material (NBR / silicone), hardness, compression set | groove width / depth for 15–25 % compression | only if the enclosure claims any ingress rating |
| light pipes | Ø, length, material, bend radius, mounting (press / snap) | hole Ø + 0.1, LED-to-pipe gap | VERIFY the LED position against the mesh of record |
| fans | frame size, hole count and pattern (4 even when one SKU drawing shows 3), thickness, connector, airflow at the working point | boss count = hole count, screw type | |