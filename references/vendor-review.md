# vendor-review.md — a fab's engineering mail arrives after the order: map → decide → replace files → re-DFM → replace on the order; PCBA engineer questions and the production-file package (§5–§7)

The order is placed (the owner's click). Hours later the print service / CNC / PCB vendor mails "please confirm the risks" with marked-up
pictures and per-line file ids, and an order-page **Replace File** button that exists only after a reply. This is a review round like any
other — evidence first, findings mapped to design features, decisions logged, changes through the generator — with one extra wall: the order is
the owner's account. Record template: `templates/VENDOR_REVIEW_RECORD.md` (one file per mail under `60-orders/quotes/<date>/`).

## 1. Boundaries (hard)
- **Agents never pay, never tick a terms / risk / "I agree" box, never cart, never change quantity, material, colour, finish, address or remarks,
  never cancel.** Reading the order pages is fine; a signed-in check that touches nothing is a fresh tab on the orders URL (its title says
  signed-in or redirects).
- **Replace File and a chat message only on the owner's explicit word** for that action ("do it" after the file list was shown), and only the
  actions named: the record quotes the delegation, lists every click made and every button NOT clicked (`templates/VENDOR_REVIEW_RECORD.md` §5).
- The reply mail to the vendor is the owner's; the agent drafts the text into the decision row (option wording per line) from the template in
  `templates/VENDOR_REVIEW_RECORD.md` §3 (facts, measured, changed, asked, not accepted) and decides fault with the table in
  `references/dfm-printed-enclosure.md` §10 — the vendor is at fault when a dimension is outside its published tolerance or the part is not the file.
- Uploading a design to a vendor's quote page is a disclosure: the owner's consent is quoted in the decision row that opens the round, the vendor's
  terms page read once and cited (`dfm-printed-enclosure.md` §7 step 0).
- A hand-over that stops one click before the cart is the right split: the agent puts every field, upload, dialog and price on record with
  screenshots; the owner spends two minutes reading deviations; the account never sees an agent-side purchase.

## 2. The round
1. **File the evidence.** Save the mail as `.eml` and every linked image (the vendor's marked-up heat maps are `<img>` links to its message-file
   ids, often fetchable without login; the mail itself carries no attachments) under `60-orders/quotes/<date>/`, named by order and line id. A
   vendor picture may use a piece-local frame (e.g. a lid's Z = body Z − the split plane): write the conversion next to the picture.
2. **Map every flag to a design feature** on the STLs of record (`scripts/thin_wall_check.py --census` per piece, `--pinch` on mark-shaped
   bodies): each red area is either designed geometry listed before ordering (knife edges, slits, legend webs — quote the order sheet line that
   listed it) or a real defect. Write the mapping table into §2 of the record (`templates/VENDOR_REVIEW_RECORD.md`, under `60-orders/quotes/<date>/`); a flag you cannot map is a finding.
3. **Decide per line** — a CC row with options and a recommendation, OPEN for the owner: accept the risk (bodies whose thin parts are designed),
   fix and replace (a real defect), redesign (rare). The owner's row (D-nn) decides; the reply wording per line goes into the CC row.
4. **Fix through the yaml + generator** (never the STL): version bump, full generated chain, new census row for the defect class (§3 point
   contacts), `--check`s green, tag. Compare facet count / volume / area / bbox per piece to know which files actually changed (an STL md5 is
   not a geometry signature — CGAL export order moves every md5).
5. **Re-run the vendor's own DFM on the replacements** before uploading them, on the quote page, nothing saved (§4 mechanics): the record says
   "no new flag" or names the new one. List the replacement files with md5s and which order line each replaces (record §4).
6. **Replace on the order** — owner's word (§1): Replace File per activated line; a line without the button → one chat message asking to
   activate it (the vendor tip: ask Live Chat right away instead of waiting for a mail); upload; screenshot before / each line / after; record
   quantities and prices unchanged. Then the vendor re-reviews; the owner pays.
7. **Read the follow-up mails right.** An automated "order … audit failed — please replace files" mail (JLC3DP wording, worked example) means
   *Replace File enabled*, not a rejection; the approvals arrive per line minutes after the upload. A status check is read-only: order history + detail + message centre,
   screenshots, a table "pending on our side?" per order, watch items (factory closures) listed, buttons not clicked listed.

## 3. Point contacts — the defect class a wall census cannot see
A traced outline of touching shapes is lobes held by hairlines; the vendor's engineer flags it ("B 0.01") where the automatic check passed it. Before
any mark-shaped body or pocket: `scripts/thin_wall_check.py --pinch <stl>`, web discs clipped to the outline's closing, the neck row and the
`connected components = 1` row — the mechanism is `references/case-pipeline.md` §Point contacts.

## 4. Quote-page and order-page mechanics (JLC3DP is the example — verify live, they change)
- The quote-page DFM procedure (one STL per session, the API response as the verdict, the flag independent of the material on the line, the heat
  map via `previewUrl`, the legend vs the published minimum vs the owner's bar, the length-dependent metric and the probe method) is
  `references/dfm-printed-enclosure.md` §7 / §7.1 with the record template `templates/DFM_ROUND.md` — not repeated here.
- Quote-page state is not account state: a per-line **Edit** dialog must be *saved* for the material to stick on the quote line (form state, not a
  cart); the risk checkbox stays unticked; "I agree" stays as the site pre-checks it; the tab is closed afterwards.
- Order page: the replace-file dialog shows old name, upload, Confirm; no terms / payment wording; the site re-weighs the order and the shipping
  *display* moves — a quote figure while unpaid, say so in the record.
- Remark caps (PCB 200 / assembly 500 chars) and a mandatory customs description cascader exist on the quote form; a placed order has no free-text
  box — the full remark goes as an attachment and into the production-file confirmation reply.
- **Signing in empties the signed-out quote**: expect to reload every line (upload all files in one call, Batch Edit the same-material lines,
  the colour / special lines one by one); a refusal (a full-colour line below its minimum bounding box) appears only as a notice at Save. The
  moment the owner reports the order id, read the order-detail page and record every line id with its file and md5 — the user-center pages
  may not screenshot through the browser bridge; capture their text instead.
- **A print-orientation PICTURE goes with every print order**, not a remark ("top face up" drew "please provide the picture to show how to place
  the part for printing" at file review): one tile per line — the body exactly as its uploaded file is framed (print frame: Z = build direction,
  a grey plate at Z 0, a red Z arrow), captioned with the order line id, the file name and how it sits (sole down, skirt down, colour face up),
  all tiles on one sheet. Render the body ALONE (a `colour = all` preview of a shell draws the fitted insert inside it, which the vendor does not
  print with the shell); the sheet is re-cut whenever a line's file changes. The colour-file rule the same review enforces (one shell per file)
  is `dfm-printed-enclosure.md` §12 Files.

## 5. PCBA fab after the order: the engineer's questions (polarity, placement, "is it okay to proceed?")
The assembly fab's engineer mails a numbered question with its own "corrected part placement" snapshots (top and bottom renders of the board as the
fab will place it) and asks for a yes within a day; production waits on the answer. Same boundaries as §1: the reply is the owner's, the agent
drafts it into the record.
- **Read the fab's marks on the board's pad-1 positions, never on the CPL rotation.** The snapshot convention (verify on the first picture; it
  is stable per fab): a red `+` at the anode, a red `−` at the cathode, a red dot at pin 1, a two-letter flag (e.g. `FL`) on a part the engineer
  could not resolve; the bottom view is mirrored in X. For every queried part read pad 1's position, the footprint's pin-1 meaning (cathode on the
  CAD library's SOD / chip-LED footprints, anode on some vendor-library SMA footprints — check the silk bar) and its nets from the board file,
  map the board frame into the snapshot (board-colour bounding box → px/mm; mirror the bottom), and compare crops side by side with the renders
  of record. A table per part: side, what the fab shows, what the board says, OK / REVERSED (rotate 180°). The electrical intent (anodes on the
  sources, cathodes on the shared bus; LED cathodes on the sink nets) is the cross-check that the footprint pin numbering itself is right.
- Expect the fab's picture to be wrong on a part class, not at random (worked example: one SOD-123 family on the bottom at 90° drawn 180° off
  while every LED, SMA diode and SOT part at the same CPL rotations matched). Answer the class, not only the listed refdes.
- **A connector on a custom footprint gets no body in their picture.** Send a picture back: the fab's own snapshot with the body outline (from
  the STEP's footprint-frame bbox) drawn over the pad rows, pin 1 circled, the mating direction arrowed, and beside it a render of the board with
  the cage / shield model removed so the body is visible. Name the holes that stay empty (press-fit for a cage pressed later) and the unplated
  peg holes.
- **Reply format** (owner sends; attach the picture): per question a numbered answer; per part "CORRECT, place as shown" or "REVERSED: the
  cathode (your `−`, the band end) goes toward <board landmark>; rotate 180°, position unchanged"; the sentence "with <parts> rotated it is okay
  to proceed". Then: arrival checklist §A row for the rotated parts (cathode band toward <landmark>), order-sheet row marked SENT.
- **Round 2 — "we updated them on the attached DFM, is that correct?"** can arrive as the SAME render under a new title (the first said
  "Corrected Part Place", the second "Original Part Placement"). Pixel-diff the new picture against the previous one (title row excluded) and
  crop the queried parts at 6×: in the worked example only the refdes labels on the two bodies had turned 180° while the `+` / `−` pad marks
  were identical — an AMBIGUOUS picture (the mark may follow the placed part or the pad data). Do not infer: the reply states what the picture
  shows, asks the fab to **state the cathode position in words**, attaches THEIR picture marked (red = as drawn, green = required), and
  re-asks every confirmation the fab skipped (hole tolerances). Production is released only on a picture or a sentence that shows the change;
  the arrival checklist checks those parts first either way.
- **Round 3 — the fab answers with pictures, not words.** After "please confirm in words … and send a picture that shows it" the third render
  came with the marks moved (and the refdes labels turned back) and still no sentence; three rounds for one rotation is the normal cost. Each
  round: crop the queried parts from every round so far at 4×, side by side with their titles, and read the pad marks against the board file;
  release production on the picture that shows the change. The inline images in a reply thread are often YOUR OWN pictures quoted back —
  compare their md5 against your attachments before analysing anything; the fab's new content is in the attachments of the latest mail. Once
  the blocking item is settled, re-ask the skipped confirmations (hole tolerances) "for our records — production does not need to wait".
- **Round 4 — the order-history "Confirm Parts Placement" step.** After the mails the fab adds an *Action Required* item on the order with a
  silent timer ("confirm within 2d23h, or your order will be produced directly") — no mail announces it, so check Order History after every
  engineer reply. Its viewer (`/smt/dfm-result?...&confirmFile=1`) shows the engineer-adjusted placement, a designator table with the polarity
  flag and a DFM column, and the form ("Yes, please proceed" / "No, modification needed" + Submit). The data behind it is the fab's engineering
  file (`downloadHandleWeldFile?fileType=Smt_Hw_Bom_Merge` → `designator_info[].top/bottom[]`, `oc` = your CPL row, `ec` = the engineer's row).
  Do this before any picture: assert `oc` == your CPL and the fab codes == your BOM for every designator, then diff `ec` against `oc` — it names
  every change (worked example: 56 passives turned 180°, package-origin shifts on two connectors and five switches, library-zero 90° deltas on a
  SOT-23-6 and an LQFP). A polarity fix can land in the fab's package mapping with `ec == oc`, so the picture stays the proof: calibrate the
  fab's snapshot on the mounting holes (five Ø3.2 holes fitted → 0.1 px residual; the board-colour bounding box sat half a pad off), draw your
  pad 1 over their marks for every polarity-flagged part, and read pad-1 meaning from the footprint (vendor SMA diode footprints: pad 1 = anode,
  bar at pad 2; KiCad SOD / LED footprints: pad 1 = cathode). The agent opens the viewer read-only and files the record; the owner selects and
  submits. Afterwards the deltas go into the rotation table (`pcb-layout-dfm.md` §10) so the next order of these packages needs no round at all.

## 6. The fab's production-file package ("please review the production file")
The package the fab sends back is its CAM output, not your upload: production Gerbers (often inch 2.6, one file per layer plus drill map, rout
profile, via-plug layer, code-mark layers), an ODB++ job (`steps/<step>/layers/<layer>/features`, `drl/tools` with FINISH_SIZE vs DRILL_SIZE),
your own upload for reference, and an order-parameter file (layers, copper weights, finish, mask / silk colours, via treatment, press-fit flag,
the order remark the quote generated). Approve it the same day; it is the last look before copper.
1. **Rasterise both sets on one frame** (a Gerber library → SVG with forced bounds → PNG at ~16 px/mm, white background) and XOR per layer:
   both / fab-only / yours-only. Connected components of each difference, mapped to the drill table by position, name the cause of every
   square millimetre; a component that maps to no hole and is not a thin edge sliver is a finding.
2. **Read the compensation from the aperture headers**, not the raster: every fab aperture = yours + one constant (etch compensation for the
   copper weight; +0.065 mm on 2 oz outer layers in the worked example, i.e. half that per edge). The artwork spacing at your minimum shrinks by
   that constant and etches back; ask the fab to confirm the finished minimum, do not "fix" the files.
3. **Expected, harmless CAM differences** — list them in the record so the review is a diff against expectations:
   - a uniform ring around every outer feature (compensation);
   - discs at via / component-hole sites on the inner layers that only you have (non-functional pad removal — no press-fit hole may lose its pad);
   - mask windows over the rail / tab rout slots and the rail tooling holes; the outline band on every layer;
   - one flash per via on a separate layer (via plugging / tenting as ordered); code placeholders on the rails; small NPTH relief holes in the tab slots only;
   - drill oversize for plating — read yours from the ODB `drl/tools` FINISH_SIZE vs DRILL_SIZE (worked-example numbers: via 0, PTH +0.15,
     press-fit +0.11 with the finished size unchanged, NPTH +0.05);
   - silk and paste identical (paste is often absent from the CAM Gerber set — compare it from the ODB feature counts).
4. **Compare the order-parameter file with your order sheet** line by line (copper, finish, colours, via treatment, panel, press-fit, customer
   code, the remark text) — a wrong option here is cheaper to catch than on the board.
5. **Reply** (owner sends, §1): APPROVED with the list of what was checked and at most two confirmations (press-fit finished-hole tolerance against the connector
   drawing; an NPTH peg hole drilled +0.05 — hold the design size if they can). Record: the per-layer table + the evidence crops under
   `60-orders/quotes/<date>/`, the zip filed beside it, the reply text in the same record as §5 when both arrive together.

## 7. Upfront: pre-answer the engineer before the order (the cheap half of §5–§6)
Every question in §5 and every confirmation in §6 can be in the package before the fab asks — then the mail is a yes instead of a day's
exchange. At G2 / package build (`references/fab-dfm.md` §9, `references/pcb-layout-dfm.md` §10):
- **Assembly notes in the fab package** (`ASSEMBLY_NOTES`, a cut deliverable; the contract is `references/fab-dfm.md` §9). The order remark
  points at it ("see ASSEMBLY_NOTES in the package").
- **A fab's-eye pass on the silk at G2** (`references/pcb-layout-dfm.md` §10; a G2 prerequisite beside the silk check): fix the footprint, not the mail.
- **The order remark carries the fab-side decisions** the CAM would otherwise take silently — press-fit and peg hole finished sizes and
  tolerances, which holes are NPTH, via treatment, "mask openings as designed", minimum trace/space finished — within the remark cap (§4); what
  does not fit is in `ASSEMBLY_NOTES`, which the remark names. §6 step 4 checks the same list back.
- **The arrival checklist** gets its §A rows at the order (template rows A-0 and A-5): the production-file diff on file before the fab's approval
  reply, the engineer-question answers seen in the fab's final photos; B-2 checks the rotated parts first on the bench.
