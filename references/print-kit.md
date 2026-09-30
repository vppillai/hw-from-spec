# print-kit.md — the home-FDM print kit as a deliverable a technician can run without the repo

Added 0.7.1 from a blind technician review of a kit as received (worked example: the source project's P2S kit, 2026-09-30 — two BLOCKERs, both in
the one irreversible step). The rules are FAIL-gated where a generator can check them; the numbers are the worked example's.

## 1. One entry point: a generated `START_HERE.md` at the top of the kit
Written by the slicer wrapper (it owns the minutes and grams) from a `kit_facts.json` the geometry generator writes — **numbers from the
sidecars, prose from the knobs, nothing typed**. Four blocks, in this order:
1. **Header**: what every project file embeds (printer, nozzle, layer, material, plate), the one hand step (AMS: *the project defines filaments
   1 / 2; the send dialog maps them to slots* — never "load slot 2"), how to print a subset (delete objects / the `_1x` project), what the
   `.3mf.json` sidecar is for (`print_time_s`, `filament_g`, `objects_in_3mf`; the rest is the engineer's check data).
2. **Print order table**: `step | project file (.3mf, in this folder) | objects | time + mass (sliced) | check before the next step`. Coupons →
   board dummy → tray → body → hood (option A plates / option B AMS: *choose ONE*, one line) → legend plate → fixture → caps (bracket → coupon →
   plate). Each check is a pass/fail sentence and says what to do on FAIL ("stop and report"); the coupon row states the gate explicitly
   (*print on, the answers only tune the legend plate* or *stop until the regenerated kit arrives*). Total printer time per option.
3. **Assembly sequence**, numbered, with the order-critical facts (§2): supports out → drill the bores → inserts from the pillar ENDS (body upside
   down) → dry-fit body on tray → screws → **magnets dry, then CA** → legend plate (CA) → hood plate (CA on the lands only) → fixture = real
   board only → **feet LAST** over the screw counterbores (a foot fitted early is peeled and wasted).
4. **Report-back table** with **numeric pass criteria per interface** (body-on-tray play ≤ 0.3 at the seam; plates ≈ 1.2 proud, LED holes
   concentric; hood pulls itself down at both magnet pairs and holds upside down; cap mouth 18.55..18.65 × 8.7..8.8 by calliper; coupon: which
   cap / stroke reads) **and a recipient** ("reply in the project chat" / a name). A kit without a recipient gets no answer.

Rules the entry point makes checkable:
- **Print-sheet names = project-file names** (`PRINT_SHEET_<piece>.md` names its `.3mf`; sheets called `shell` / `plate_ui` for projects called
  `case_body` / `case_legend_plate` cost the reviewer four READMEs). Every sheet's Profile line is generated from the SAME dict the 3MF is
  written from (a sheet said "elephant foot 0" beside a 3MF carrying 0.15).
- **Hardware list derived from the fastener knobs** (`hood_hold`, `magnet_rule`, `write_kit_facts` or equivalents), read by every emitter —
  README, sheets, coupon README, START_HERE, the clearance-count rows. A typed "6 inserts, 2 in the hood bosses" survived two fastener changes and
  would have put a heat-set insert into a Ø6.1 magnet pocket.
- Technician-facing remedies are "report X to the engineer", never a yaml edit or a D-/CC- id. Both board-dummy variants shipped → say which to
  print ("one-piece; two-piece is the fallback"); a check the dummy cannot do (rigid nose vs bezel) is listed as EXCLUDED, not implied.
- Ship what the texts cite: a `faces/` render cited → `faces/` in the kit; census artefacts and `.scad` out of the print folder; duplicate copies
  (caps inside the case kit) byte-identical or absent.

## 2. Magnet assembly (the one irreversible step)
- **Stack-and-mark polarity rule**, generated from the yaml positions: stack the discs, mark the top face of the stack, slide one off, mark the
  next — marked face UP in the body pockets, marked face DOWN in the (upside-down) hood pockets. **Asymmetric boss keying** (Ø10 one side / Ø11
  the other, `dfm-printed-enclosure.md` §1.1) so the hood cannot go on rotated.
- **Dry attract check before any CA**: seat all discs dry, lower the hood — it must pull itself down at both pairs; only then one CA dot per disc.
- Magnets before glue (plates), feet last (they cover the screw heads). A position printed as `None` here is the failure the text gate (§3) exists for.

## 3. Kit text gate (a FAIL row over every emitted kit text and the ASSEMBLY / QA record)
| Token class | Example | Why FAIL |
|---|---|---|
| template residue | `None`, `nan`, a `{name}` brace | a bullet read the screw dict while the fastener was magnets: "pockets at Y None" |
| repo paths | `out/…/stl/`, `design/*.yaml`, `gen/` | the technician has the folder, not the repo |
| dead file references | a backticked name the `--copy` does not deliver; `faces/` cited, folder absent | four dead pointers in one kit |
| features the preset disables | `snap tab` / `screws for the hood` when `fastener: magnets`; `PETG` when `material: PLA`; `insert` counts ≠ the knob | "0 magnets, PETG, the two snap tabs click" three fastener changes later |
| governance jargon | `D-xx`, `CC-xxx`, `VERIFY_`, owner quotes | not actionable without the repo |

The gate reads the forbidden tokens from the preset (fastener, material, marks option), so a knob change updates the gate with it. Run it over
START_HERE, every README and print sheet, and the generated ASSEMBLY.md; the run FAILS on a hit; the row is in the census record.

## 4. Coupon, ONE part, then the plate
- A mark coupon proves GEOMETRY and first-layer behaviour, not the thermal state of a 99-minute print (warp, sag on a long span, colour
  opacity at depth): after the coupon, print **one part** (one cap, one plate) before the multi-object plate; START_HERE says so per step.
- **Snug-fit features ship as a bracket plate** (`dfm-printed-enclosure.md` §8.5): e.g. crush ribs at 0.20 / 0.25 / 0.30, one object each, NAMED
  by its value in the 3MF (no digit deboss — the object name carries it). The technician keeps the one that seats under thumb pressure and
  survives the hang test and reports the value; **the owner picks the knob after that print** (default stays the middle value).

## 5. Records that travel with the kit
- **Watertight row per exported STL** (a slicer fills or drops a non-manifold feature silently and reports "clean"); a `watertight: false` was
  recorded for a day without gating it. Raised legend items keep a `legend_edge` margin (0.3) from the plate outline and the fit filter LISTS
  what it dropped (three 1 × 1.2 triangles 0.05 inside the edge became 0.66 mm open stubs).
- **Sidecars carry every slicer key a rule depends on** — `top_one_wall_type`, `xy_hole_compensation`, `elefant_foot_compensation`, the ironing
  keys (`ironing_type`, `top_shell_layers`), `wall_loops`, seam, support flags — and a drift check compares the sidecar with the embedded
  `project_settings.config` of the 3MF it names (md5). A reviewer reads the config, not the sidecar; the two must agree.
- Sidecars in the kit carry no local temp paths (`cli` block stripped or the paths made relative); `.DS_Store` and census artefacts removed by the
  mirror step; the mirror is byte-identical to the sources (md5 list in `kit_facts.json`).
