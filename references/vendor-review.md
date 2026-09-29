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

## 3. Point contacts — the defect class a wall census cannot see (worked example: an SLA inlay plate)
A traced (potrace) outline of shapes that touch comes out as ONE path pinched to 0.003–0.03 mm at the contacts; extruded, the plate is several
lobes held by hairlines, every DFM flags it ("B 0.01") and the part arrives in pieces. A ridge / distance-transform "thinnest arm" row read 3 mm
and saw nothing. Before any mark-shaped body or pocket (inlay, badge, deboss): `scripts/thin_wall_check.py --pinch <stl>` (non-adjacent
boundary vertices closer than ~0.05 mm), bridge each contact with a web disc **intersected with the outline's closing** (`offset(r=+R) offset(r=-R)`,
R ≈ 3 × web — concave fills only; a bare disc left a 0.4 mm nub on the silhouette), add a census row for the neck (≥ the process minimum) and
keep the `connected components = 1` row (it caught the mis-placed disc when the neck row measured the wrong frame). trimesh `section().to_2D()`
re-origins the plane: map the outline back through the returned to-3D transform before placing anything. Detail: `references/case-pipeline.md`.

## 4. Quote-page DFM mechanics (worked example: JLC3DP, 2026-09-23 / 09-28 — verify live, they change)
- **One STL per page session (reload between uploads), verdict read from the analysis API at `parseStatus == 2`, screenshots named with the STL md5** —
  the full procedure and the record template are `references/dfm-printed-enclosure.md` §7 + `templates/DFM_ROUND.md`. With several lines present the
  page opened the wrong file's analysis twice. The thin-wall flag is computed at UPLOAD and does not depend on the material chosen on the line (the
  line defaults to **9600 Resin**; set the order's material anyway for the price and the map legend). A DOM "no flag" read before `parseStatus 2` is
  invalid — two such reads passed a tray the API later flagged. Uploads and the analysis work signed out; the hidden `input[type=file]` can be unhidden
  by script for a chooser-less upload.
- **The metric is length-dependent** (`dfm-printed-enclosure.md` §7.1): the same wall profile passed at 48 mm and failed at 88 / 147 mm — calibrate with
  full-length probes cut from the failing body (`slice_mesh_plane`, capped) and plain-profile extrusions with one knob each, uploaded alone.
- Upload on the quote page, no account state: per-line **Edit** dialog must be *saved* for the material to stick on the quote line (that is form
  state, not a cart); the risk checkbox stays unticked; "I agree" stays as the site pre-checks it; the tab is closed afterwards.
- A clean part has NO "Printing risk" popover but its thin-wall heat map still exists: the page polls
  `GET …/tdpFile/getFileAnalyzeResult?fileAccessId=…` (read it in the network log or re-request it) whose `modelAnalysisVO` carries `thinWall` (bool),
  volume, surface, bbox and `previewUrl` (a `forface3dPreview?params=<base64 {thicknessModelUrl, modelUrl}>` viewer link = the Analysis Results tab)
  — that response at `parseStatus 2` is the verdict of record; open `previewUrl` to read the map of a part the vendor calls clean.
- The viewer legend is a colour scale (JLC3DP 2026-09-28: grey ≥ 1.2, yellow 0.5–1.2, red < 0.5 mm) — the CHECKER's line, not the vendor's
  published printable minimum (its mail: nylon ≥ 1.0) and not the owner's bar (`dfm-printed-enclosure.md` §1); its only numbers are volume / area /
  bbox — the census turns a colour into a number. The vendor's volume must equal yours (same geometry parsed). The map colours walls, VOIDS (slots, engraved strokes) and
  FREE-STANDING wedges (rail tips, added coves); chamfers cut into a ≥ 1.2 wall stay grey (`references/dfm-printed-enclosure.md` §1).
- A yellow band "full length" along a feature is a strength finding: an owner decision row with the number, or a fix — never "kept (design geometry)".
- A verdict that flips between two uploads of one body: diff the meshes (facets, vertices, winding, volume) and check that BOTH reads were API reads
  at `parseStatus 2` before touching the generator — the r3 tray that read red was the r2 tray that "passed" on a premature DOM read.
- Order page: the Replace Files dialog shows old name, upload, Confirm; no terms / payment wording; the site re-weighs the order and the
  shipping *display* moves — a quote figure while unpaid, say so in the record.
- Remark caps (PCB 200 / assembly 500 chars) and a mandatory customs description cascader exist on the quote form; a placed order has no
  free-text box — the full remark goes as an attachment and into the production-file confirmation reply.
