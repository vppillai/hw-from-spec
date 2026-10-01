# vendor-review.md — a fab's engineering review mail arrives after the order: map → decide → replace files → re-DFM → replace on the order

The order is placed (the owner's click). Hours later the print service / CNC / PCB vendor mails "please confirm the risks" with marked-up
pictures and per-line file ids, and an order-page **Replace File** button that exists only after a reply. This is a review round like any
other — evidence first, findings mapped to design features, decisions logged, changes through the generator — with one extra wall: the order is
the owner's account. Record template: `templates/VENDOR_REVIEW_RECORD.md` (one file per mail under `docs/quotes/<date>/`).

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
   ids, often fetchable without login; the mail itself carries no attachments) under `docs/quotes/<date>/`, named by order and line id. A
   vendor picture may use a piece-local frame (e.g. a lid's Z = body Z − the split plane): write the conversion next to the picture.
2. **Map every flag to a design feature** on the STLs of record (`scripts/thin_wall_check.py --census` per piece, `--pinch` on mark-shaped
   bodies): each red area is either designed geometry listed before ordering (knife edges, slits, legend webs — quote the order sheet line that
   listed it) or a real defect. Write the mapping table into §2 of the record (`templates/VENDOR_REVIEW_RECORD.md`, under `docs/quotes/<date>/`); a flag you cannot map is a finding.
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
