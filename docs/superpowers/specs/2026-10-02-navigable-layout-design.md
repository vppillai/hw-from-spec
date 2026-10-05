# Navigable project layout — design spec (2026-10-02)

Owner request: "a better organization of the output from the skill that is intuitive to navigate … without a README". Approved in five
sections in conversation on 2026-10-02; this file is the written form. Scope: the layout the skill lays down in a PROJECT (its tree, the
kits it hands over, the production cut and release documents) and the skill changes that make that layout the default. The skill repo's
own layout is out of scope.

## 1. Goals and non-goals

Goals — a reader who has never seen the project finds, from the tree alone:
1. where things stand and what is blocked on the owner;
2. what to print or order next, and what to check when it arrives;
3. the hand-over for a technician, a reviewer or a future maintainer.

Rules the tree must satisfy without a README:
- **Names are nouns a technician knows.** No hash and no date as a folder name at the top of any tree; a revision is `rev0`, a kit is its
  print target, the hash lives inside the folder (`board_id.txt`, record sidecars).
- **One current thing per path.** Superseded kits, cuts and case versions are not kept beside the current one; git history holds them.
- **Records sit next to what they describe.** A part's census and DFM verdict live in `checks/` beside its STL, not in a parallel tree.
- **Order follows the life of the project.** Numbered top-level folders read top to bottom: now → spec → design → board → case → kits →
  orders → release → reviews → log.

Non-goals: moving the machinery (`gen/`, `scripts/`, `tools/`, `lib/`, `Makefile`, `CLAUDE.md` stay where they are); changing any record's
content, md5 or rule-set version (records are relocated, never re-written); a web dashboard.

## 2. The tree (skill default layout; every path a `paths:` key in project.yaml)

```
00-now/          WHERE_THINGS_STAND.md  BLOCKED_ON_OWNER.md  WHAT_TO_PRINT.md  WHAT_TO_ORDER.md  WHAT_TO_CHECK_ON_ARRIVAL.md
                 generated every record round from 90-log/ and the kits; never edited; a stale page fails the gates
10-spec/         SPEC.md  FINDINGS.md  KICKOFF_ANSWERS.md  spec_sections/  datasheet_notes/
20-design/       the yaml sources of truth, briefs, design notes, test plan, software architecture, drawings index
30-board/        kicad/   layout/ (gerbers, drc, dxf, renders, inspection)   fab/<rev>/ (the uploaded package; board_id.txt = md5 + commit)   [ee, both]
40-case/         <set>/ per print target — e.g. vendor_case/ home_case/ caps_set/ coupons/ board_dummy/ dfm_validation/ fea/                     [mech, both]
                 each set: parts/ (STL of record, tracked)  checks/ (census + DFM records, clearance, interference = what the gates read)
                           pictures/ (previews, faces, assembly renders)  build/ (SCAD, logs, slicer scratch, caches — gitignored)
50-kits/         <kit>/ per print target — START_HERE.md  plates/ (.3mf + .3mf.json sidecar)  parts/ (STL copies, md5-checked)  sheets/     [mech, both]
                 the one kit of record; mirrored byte-identical to ~/Downloads/<project>_kits/<kit>/
60-orders/       PROCUREMENT.md  PARTS_VERIFICATION.md  ORDER_<rev>.md  ARRIVAL_CHECKLIST_<rev>.md  quotes/<date>/ (fab evidence, frozen)
70-release/      <rev>/ (manuals, SOPs, PDFs, records/, MANIFEST)   reports/   collateral/<rev>/   marketing/<rev>/
80-reviews/      <round>/ — one folder per review round, the merged file at its root
90-log/          DECISIONS.md  STATUS.md (append log)  LEARNINGS_LOG.md  GATES.md  BLOCKERS.md  KNOWN_ISSUES.md  TRACEABILITY.md  ENV.md
gen/  scripts/  tools/  lib/  Makefile  CLAUDE.md        the machinery, unchanged
```

Scope tags: an ee-only project has no `40-case/` or `50-kits/`; a mech-only project has no `30-board/`. The folder numbers are fixed so the
order reads the same in every project; a project that lacks a stage simply has no folder at that number.

Where today's folders go (the originating project's current layout at the time):

| today | new |
|---|---|
| `docs/governance/*` | `90-log/*` (KICKOFF_ANSWERS → `10-spec/`) |
| `docs/design/*`, `design/*.yaml` | `20-design/` (yaml stays the source of truth; the briefs and notes beside it) |
| `SPEC.md FINDINGS.md docs/spec_sections docs/datasheet_notes` | `10-spec/` |
| `docs/parts/*`, `docs/production/MINI_ORDER.md`, `…/REV0_ARRIVAL_CHECKLIST.md`, `docs/quotes/` | `60-orders/` (`ORDER_rev0.md`, `ARRIVAL_CHECKLIST_rev0.md`, `quotes/<date>/` frozen) |
| `docs/production/<md5-8>/` | `70-release/rev0/` |
| `docs/release/*_DESIGN_REPORT.md`, `RELEASE_NOTES_*`, `collateral/<md5>`, `marketing/<md5>_<ver>` | `70-release/reports/`, `70-release/collateral/rev0/`, `70-release/marketing/rev0/` |
| `docs/reviews/<ROUND>_*.md` | `80-reviews/<round>/…` |
| `kicad/`, `out/<board>/layout/`, `out/<board>/fab/<date>_<md5>/` | `30-board/kicad/`, `30-board/layout/`, `30-board/fab/rev0/` |
| `out/<board>/mechanical/case/<ver>/`, `…/v3-home/`, `…/caps/`, `…/home_coupons/`, `…/board_dummy/`, `…/dfm_validation/`, `…/pcb_fea/` | `40-case/vendor_case/`, `home_case/`, `caps_set/`, `coupons/`, `board_dummy/`, `dfm_validation/`, `fea/` — each split into parts/ checks/ pictures/ build/ |
| the four Downloads kit folders | `50-kits/home_case/`, `50-kits/caps_set/` + the mirror `~/Downloads/<project>_kits/`; old folders → one-line `SUPERSEDED.md` |

## 3. `00-now/` — the five pages

One generator (`scripts/now_pages.py` in the skill; a project may wrap it) writes all five with `--check`; it reads only files the layout
names, so a page cannot disagree with a record. A stale page fails `gates.adopt` like a stale release report.

- **WHERE_THINGS_STAND.md** — one line per gate (from GATES: reached / open / prerequisites), the last three landed items (STATUS, newest
  first), the current revision and case version with their identities, one line per open blocker. Under 60 lines.
- **BLOCKED_ON_OWNER.md** — every OPEN decision row that names the owner, every owner row of the arrival checklist, every kit fit result still
  pending: row id, the one-line question, the file to answer in. An empty section reads "nothing".
- **WHAT_TO_PRINT.md** — one row per plate in `50-kits/*/plates/`: kit, plate, minutes, grams, filament changes, what it proves, in print order
  (coupon → one part → plate), from the sidecars; links the kit's START_HERE.
- **WHAT_TO_ORDER.md** — procurement rows without an order (distributor part number, quantity), printed sets ready to reorder with their verdict
  of record, fab orders in flight with their status date.
- **WHAT_TO_CHECK_ON_ARRIVAL.md** — arrival-checklist rows not DONE, grouped by what has arrived or will.

STATUS.md remains the append log in `90-log/`; the "read this first" paragraphs stop being written there because `00-now/` is where they go.

## 4. Kits (`50-kits/`)

- **The repo folder is the kit.** Generators write into `50-kits/<kit>/` directly (today they copy from four `out/` folders into Downloads).
  `~/Downloads/<project>_kits/<kit>/` is a plain byte-identical mirror; the collateral gate checks it as now.
- **One current kit per target**, named for the printer and what it prints (`home_case`, `caps_set`), no version in the name; the version is a
  line in START_HERE and in every sheet. Old Downloads folders receive a one-line `SUPERSEDED.md` pointing at the mirror, written once.
- **Plates carry their identity**: every `.3mf.json` names the STL md5s and the case version it was sliced from; the kit text gate keeps every
  sheet consistent with the sidecars. `WHAT_TO_PRINT.md` is derived from these folders only.

## 5. `30-board/` and `40-case/`

- A set is named for its print target, never its version; superseded versions are not sibling folders.
- `checks/` is the only place the census, print-DFM and interference gates look; the gate lines in `project.yaml` name one folder per set.
- `build/` holds everything a regenerate recreates and is gitignored; the determinism check compares the regenerated part with its recorded
  md5 in `checks/`.
- `dfm_validation/` keeps the labelled STLs under their hashes (the vendor verdicts are keyed on them): the one place a hash is a name, inside
  the set, not at the top.

## 6. Migration

**Skill (0.11.0)** — `references/project-yaml.md` §Layout and `templates/project.yaml` carry the tree with every path as a `paths:` key (the
defaults above; a project may override any). `scripts/reorg_paths.py` becomes the general mover: it reads a `reorg:` block (moves, frozen
folders, allow-listed historical literals) instead of a hard-coded table, keeps `--plan / --apply / --check / --map / --proof`, rewrites
literals in every non-frozen tracked text file and the join forms the generators use. `scripts/now_pages.py` is new, with `--check` and
`--selftest`, in the smoke and `gates.adopt`. The kit writers, the kit text gate and the collateral gate learn the `50-kits/` shape. The smoke
scaffolds a project on the new layout and runs the chain on it; generic and voice lints stay at zero; SKILL.md, README, CLAUDE.md template and
every reference spell the new paths.

**Project, phase 1** (docs, kits, release, now-pages): a decision row names the move; `design/reorg.yaml` lists it; `--plan → --apply →
regenerate → --check → --proof` with the zero-loss proof on two `git ls-files -s` dumps. `quotes/<date>/` and the cut's `records/` are frozen:
moved as whole folders, content untouched, `--map` explains the old paths quoted in dated rows. The generators write kits into `50-kits/`; the
Downloads mirror and the tombstones are written once; the five pages are generated and gated. One record round, one tag.

**Project, phase 2** (`out/` → `30-board/`, `40-case/`): the same mechanics after phase 1 has run clean for a day. Census, print-DFM,
traceability and collateral gate paths move with the records; engines and record md5s do not change, so nothing is re-written.

## 7. Acceptance

Each phase ends with: adopt gates green serially and in parallel; the clone gate green on the committed HEAD; the smoke green in both repos;
`reorg_paths.py --proof` zero-loss; both lints at zero in the skill; and a fresh clone from GitHub into an empty folder in which a cold reader
opens `00-now/` and answers the three questions of §1 without being told where to look.

## 8. Decisions taken in the design conversation

- Numbered prefixes on the ten top-level folders (owner: ok, 2026-10-02).
- Move files, not only a navigation layer (owner: "Move files too").
- The tree is the navigation; no README is required to use it (owner: "intuitive to navigate without a readme").
- Two project phases, skill first; `out/` split is phase 2.
