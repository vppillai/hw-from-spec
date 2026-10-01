# {{VENDOR}} review of order {{ORDER_ID}} — {{DATE}} (record; `references/vendor-review.md`)

Files here: `{{MAIL}}.eml`, `{{ORDER_ID}}_<line>_*.png` (the vendor's marked-up pictures, fetched from the mail's image links), screenshots below.
Agent: {{AGENT}}; owner delegation quoted verbatim in §4/§5; nothing here was paid, agreed, carted or changed except what §5 lists.

## 1. What the vendor asked (verbatim, per line)
| Line id | File | Material / process | Vendor's flag | Picture |
|---|---|---|---|---|
| {{LINE_ID}} | {{FILE}} | {{MATERIAL}} | {{FLAG_TEXT}} | `{{PNG}}` |

## 2. Mapping to design features (STLs of record, `scripts/thin_wall_check.py --census / --pinch`)
| Line | Red area (vendor frame → model frame) | Feature (yaml key / order-sheet line that listed it) | Class | Number |
|---|---|---|---|---|
| {{LINE_ID}} | {{WHERE}} | {{FEATURE}} | designed knife edge · legend web · slit · **defect** | {{MM}} |

## 3. Decision per line (DECISIONS rows)
| Line | Options offered (CC-{{nnn}}) | Owner decision (D-{{nn}}) | Reply wording |
|---|---|---|---|
| {{LINE_ID}} | accept risk / fix + replace / redesign | {{DECISION}} | {{TEXT}} |

Reply template (the owner sends it; `references/dfm-printed-enclosure.md` §10): **Facts** — order {{ORDER_ID}}, line {{LINE_ID}}, file
`{{FILE}}` md5 `{{MD5}}`. **What we measured** — {{NUMBERS}} on the received part / the ordered STL (photos `{{PNG}}`). **What we changed** — new file
`{{FILE_vX}}` md5 `{{MD5_NEW}}`, {{WHAT_MOVED}}. **What we ask** — ship as is / reprint at our cost / reprint at your cost (dimension outside your
published tolerance {{TOL}}) / credit. **What we do not accept** — {{E.G. a part not matching the file}}. Vendor-fault decision table: §10 step 3.

## 4. Replacement files (generated chain, version {{CASE_VERSION}}, tag {{TAG}})
| Order line | Replace with | md5 | What changed (facets / volume / bbox vs the uploaded file) | Vendor DFM re-check (quote page, nothing saved) |
|---|---|---|---|---|
| {{LINE_ID}} | `{{FILE_vX_md5.stl}}` | `{{MD5}}` | {{DELTA}} | {{RESULT}} — `{{RECHECK_PNG}}` |
Not replaced: {{LINES_UNCHANGED}} (geometry identical: facets / volume / area equal; md5 differs by export order only).

## 5. Actions on the order (owner's explicit word: "{{OWNER_QUOTE}}", {{TIME}})
| Time | Action | Line | Result / screenshot |
|---|---|---|---|
| {{HH:MM}} | {{VENDOR_REPLACE_ACTION}} (e.g. "Replace File") → upload `{{FILE}}` (md5 re-checked locally) → Confirm | {{LINE_ID}} | line shows the new file, qty / price unchanged; `{{PNG}}` |
| {{HH:MM}} | Chat: "{{EXACT_MESSAGE}}" | — | reply: "{{VENDOR_REPLY}}" |

**Explicitly NOT touched:** payment / checkout / cart; any terms, risk or "I agree" box; quantities, materials, colours, finishes, remarks,
address, shipping; Cancel; the other lines ({{LIST}}); other orders; account settings. Observed side effects not clicked: {{E.G. shipping display recomputed}}.

## 6. Follow-up (read-only status checks, one line per check)
- {{DATE TIME}}: order history / detail / message centre read; the vendor's "please replace files" mail = the replace action activated, not a
  rejection; lines approved {{TIMES}}; pending on our side: {{NOTHING / ITEM}}; owner next: {{PAY / NOTHING}}; watch: {{FACTORY CLOSURES}}.
