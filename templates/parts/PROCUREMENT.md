# PROCUREMENT.md — owner-bought and non-fab lines a buyer can execute (references/part-verification.md "Bought hardware")

Every line here is a [V] row in `docs/parts/PARTS_VERIFICATION.md` (manufacturer page + TDS) or a BLOCKERS row with the exact URL the owner opens
logged in. Quantities are per unit × units × (1 + spares); prices carry currency and date; a count that disagrees with another record (yaml,
assembly guide, order sheet) is flagged in a decision row, never resolved here.

| Line | Class | MPN | Manufacturer | Spec (thread × length / Ø × h / grade / size) | Drive / head / coating / colour | Material / finish | Qty per unit | Spares % | Order qty | MOQ | Unit price (currency, date) | Supplier URL (verified how) | Equivalent MPNs | RoHS / REACH source | Fit numbers (pocket, bore, torque) | Tag |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | screw | {{MPN}} | {{mfr}} | M3 × 8 | pan, Torx T10 | zinc-plated steel | 4 | 10 | {{n}} | 100 | {{0.02 USD, DATE}} | {{URL}} (plain-HTML dealer) | {{alt}} | {{TDS URL}} | torque `[OWNER: … Nm]` | [V] |
| 2 | insert | | | M3 heat-set, OD {{mm}}, L {{mm}} | | brass | 4 | 10 | | | | | | | bore Ø{{}} × {{}} deep (TDS p.{{n}}) | [S] |
| 3 | magnet | | | Ø6 × 3 N45 | Ni-Cu-Ni | NdFeB, max 80 °C | 2 pairs | 20 | | | | | | | pocket Ø{{}} (+0.4 MJF glued / +0.1 PLA press); pull {{N}} at {{gap}} | [S] |
| 4 | foot | | | Ø8 × 2 flat-top | PSA | polyurethane; **PSA primer for PA12** (TDS substrate table) | 4 | 20 | | | | | | | pocket Ø{{}}, annulus area {{mm²}} | [S] |
| 5 | label / badge | | | {{W × L}} | | | 1 | 10 | | | | | | | recess {{W+1 × L+1}}, flat land | [S] |
