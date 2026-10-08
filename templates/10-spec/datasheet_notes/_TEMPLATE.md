# <MPN> — datasheet notes (rule 3: read before the part is drawn)

Datasheet: <live URL of the fitted code> · revision / date on the document: <…> · read on <date> by <agent>.

| VERIFY item (spec value or claim) | Where in the datasheet (page, section, table, figure) | Value read | Matches the spec? | Note |
|---|---|---|---|---|
| e.g. "Iq 55 µA" | p. 7 §6.5 Electrical characteristics, row IQ | 55 µA typ, 80 µA max | yes | "not in datasheet text" if read from a curve — name the reader |

Pinout / package checks: pin numbers vs the symbol; package drawing vs the footprint (the drawing governs; the vendor STEP is the only source for heights).
Open questions → a `90-log/BLOCKERS.md` row when the vendor page cannot be fetched, a `90-log/DECISIONS.md` CC row when the spec value must change.
