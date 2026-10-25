# Merged review — hw-from-spec 0.11.25 (A, B, C, D)

Inputs: four blind reviews of the frozen 0.11.25 tree and the 0.11.24 → 0.11.25 diff. Each reviewer saw only the artefact and the brief.
- A: Agent tool, Claude Opus. 31 findings: MAJOR 5, MINOR 19, NOTE 7.
- B: Agent tool, Claude Opus. 32 findings: MAJOR 7, MINOR 20, NOTE 5. B ran a mutation test of eval 19 (8 of 9 rule deletions stayed green).
- C: GPT. 61 findings: BLOCKER 19, MAJOR 29, MINOR 11, NOTE 2.
- D: Grok. 27 findings: BLOCKER 4, MAJOR 11, MINOR 7, NOTE 5.

151 findings merge into the 85 rows below. A row's severity is the highest that any source gave it. Ids: A-nn, B-nn, C = HWFS-nnn, D = Rnn.

Dispositions:
- FIXED: the text or the code changed in this branch.
- PARTLY: the core is fixed; the rest is rejected with the reason in the row.
- REJECTED: no change, with the reason.
- ACCEPTED: the NOTE confirms the text; no change is needed.

## Counts

| severity | rows | FIXED | PARTLY | REJECTED | ACCEPTED |
|---|---|---|---|---|---|
| BLOCKER | 17 | 13 | 4 | 0 | 0 |
| MAJOR | 36 | 31 | 5 | 0 | 0 |
| MINOR | 25 | 23 | 2 | 0 | 0 |
| NOTE | 7 | 4 | 0 | 1 | 2 |
| total | 85 | 71 | 11 | 1 | 2 |

Each PARTLY row names what it fixed and what it rejected, with the reason. Round 2 below reopened some round-1 rows.

## What the rule check proves

Round 1 guarded one phrase per bullet. Round 2 showed that 47 of 86 §23 sentences could then go unseen. The round-2 state is below.
`scripts/rule_check.py evals/core_rules.yaml --mutate` runs in eval 19 and the smoke. Four sections are guarded sentence by sentence,
intro included: software-track §23, schematic-phase §6, release-and-cut §15 and dfm §8.7. Phrase guards cover parts of §18, §20,
the pitfalls and the SKILL links. Result on this branch: 393 of 393 mutations went red. They are 295 sentence deletions, 58 verdict
flips, 28 banned-phrase insertions and 12 block deletions for phrase guards. The proof covers the guarded text only. A rule
outside these sections, and a meaning kept in new words outside an every_sentence section, are not seen.

## Merged list

| id | sources | severity | finding | disposition |
|---|---|---|---|---|
| M-01 | C HWFS-051 (BLOCKER), A-24, B-28, D R17 | BLOCKER | `scripts/generic_lint_terms.yaml` publishes the project, company, person, order and part names it guards against. The repo is public. | FIXED. The repo file keeps generic shapes only. The names moved to a private file outside the repo (`--private-terms`, `$HWFS_PRIVATE_TERMS`, `~/.config/hw-from-spec/private_terms.yaml`). Without it the lint runs the generic patterns and prints a note. The selftest uses synthetic terms. The smoke's own project-name grep is gone. Git history is not rewritten: the owner decides. D R17 ("keep") is overruled by the owner rule. |
| M-02 | C HWFS-052 | MINOR | A private scratch path in `docs/reviews/blind_review_0.9.0.md:92`. | FIXED: `<worktree>/.venv/bin/python`. `machine_paths` gains the macOS temp root, `/home/<user>` and a Windows user path. |
| M-03 | C HWFS-054 | MAJOR | The lint skips binaries and whole `generic: ok` lines, and misses Windows paths and `R-C12` ids. | PARTLY. Added: Windows and `/home/` paths, the macOS temp root, `R-C` ids. Rejected: archive and binary scanning, and token-scoped suppressions. The skill repo carries no archives, and `generic: ok` marks lint fixtures only. |
| M-04 | D R15 | MAJOR | The CHANGELOG source line names the source product type, against the skill's own generic rule. | FIXED in the 0.11.25 and 0.11.24 source lines. The phrase is a private lint term. |
| M-05 | A (leaks note) | NOTE | `BER-LANE-3` in release-and-cut §15 looks like a project data key. | FIXED: `X-LANE-3`. |
| M-06 | B-32, D R24, D R27, C (closing line), A (runs) | NOTE | Versions agree, cross-references resolve, counts hold, no decision ids leaked. | ACCEPTED. |
| M-07 | C HWFS-001, D R01, D R02 (BLOCKER), A-02, B-02 (MAJOR), A-06, B-10, B-11 (MINOR) | BLOCKER | The "bits law" accepts rate × T² / 2 as a model. It is not physical, it can inflate the bit count and hide a bad BER, and it sets a 5 s window minimum. Eval 19 teaches it. Two window minimums disagree. | FIXED. §23: the bit counter grows at the lane rate × T; any other law is a counter fault and the window is INCONCLUSIVE. T² / 2 stays only as a dated example. The 5 s and 10 s minimums are gone; the window is bounded by the wrap rule. Eval 19 rewritten. |
| M-08 | C HWFS-007 (BLOCKER), A-01, D R05 (MAJOR), B-12, B-24 (MINOR) | BLOCKER | The lane rate as "host interface rate over media lane count" is wrong for unequal lane counts, gearboxes, PAM4 and FEC overhead. | FIXED: the lane rate of the checker's side, from the standard's table, with the encoding and FEC overhead; a rate the tool cannot look up gives INCONCLUSIVE. |
| M-09 | C HWFS-002, HWFS-003 (BLOCKER), D R14 (part) | BLOCKER | No counter deltas, no verified reset epoch, no read-back after a reset, reads too soon after a reset. | FIXED in §23 (one verified reset epoch, read-back near zero, the first update interval skipped, a reset inside a window invalidates it) and §20 (reset verified before the gate). |
| M-10 | C HWFS-004 (BLOCKER), B-05 (MAJOR), C HWFS-018 (MINOR) | BLOCKER | "A count that goes down" misses multiple wraps, saturation and unknown widths. The bit counter's wrap is not covered. A wrapped count proves at least 2^32 errors, yet the run is only INCONCLUSIVE. | PARTLY. Fixed: know the width and the wrap or saturate behaviour; a short first window; each window bounded by the previous BER; a step of half the modulus or more invalidates the window; a proven wrap is a lower bound, and a lower-bound BER over the limit is a FAIL. HWFS-018 (unwrap one proven wrap and keep the window) rejected: the count after a wrap is a lower bound, so the window stays invalid for the BER. |
| M-11 | C HWFS-005 (BLOCKER), B-01, D R11 (MAJOR), A-08 (MINOR) | BLOCKER | Computed against reported BER has no tolerance and no consequence. The text does not say which rate is judged. An unfrozen read is not coherent. | PARTLY. Fixed: a tolerance stated before the run; a mismatch makes the window INCONCLUSIVE; compare on a frozen read; an unfrozen read adds one update interval to the slack; the verdict uses run totals of checked counters. Rejected: a mandatory latch. Some modules have none, and the slack bound keeps such a read honest. |
| M-12 | C HWFS-008, HWFS-012, D R03 (BLOCKER), B-04 (MAJOR), D R14 (part) | BLOCKER | The verdict aggregation is undefined (average, last, sum). There is no per-lane or per-direction rule. | FIXED: run totals per lane and per direction over the counted windows; never average window rates; never judge the last window alone; at least two counted windows; any invalid window makes the run INCONCLUSIVE. |
| M-13 | C HWFS-013 (BLOCKER), A-05 (MAJOR), B-04, D R14 | BLOCKER | A zero-error result carries no confidence bound and no minimum bit count. | FIXED: BER below −ln(1 − CL) / N, about 3 / N at 95 %; a minimum bit count of about 3 / limit; fewer bits give INCONCLUSIVE. |
| M-14 | C HWFS-014 (BLOCKER), A-05, D R14 | BLOCKER | No pre-FEC or post-FEC distinction, no counter unit. | FIXED: record what each counter counts and its FEC point; key each limit to it. |
| M-15 | C HWFS-015, D R04 (BLOCKER) | BLOCKER | A deaf checker (stuck at zero) passes every arithmetic check. | FIXED: known errors or a known-bad path, per lane and direction where the hardware allows, before a release record. |
| M-16 | C HWFS-011 (BLOCKER), D R12 (part), B-05 (part) | BLOCKER | Lock loss after the settling is never verdict-bearing; an OR suits latched flags, not live lock. | FIXED: the live lock and the latched loss kept apart; a lock loss after the settling bears on the verdict through the criteria. |
| M-17 | B-03, C HWFS-017, D R12 (MAJOR) | MAJOR | The settling time is undefined and can move after the data is seen. | FIXED: a rule fixed before the run, with a maximum time; excluded and reported; never moved; every later window counts; past the maximum the run is INCONCLUSIVE. |
| M-18 | A-03 | MAJOR | "Judge warm" blames heat for what the data shows is the checker lock-in. | FIXED: separate the lock-in from a temperature effect; claim a warm-up effect only when the rate tracks the temperature after the settling. The cold-start reading and its pitfall wording are gone. |
| M-19 | C HWFS-010 (BLOCKER), D R08 (MAJOR), A-26 (NOTE) | BLOCKER | "A disabled lane stops at one bit, an odd count" is one module's behaviour stated as law. | FIXED (§20): judge each lane against the expected enable map; a disabled lane stays near zero, an enabled lane counts at the lane rate. |
| M-20 | C HWFS-016 (BLOCKER), B-14 (MINOR) | BLOCKER | "Any invalid window" is undefined. Eval 19 only greps prose, has no negative fixtures, and 8 of 9 rule deletions stay green. | PARTLY. Fixed: §23 names each invalid state; `scripts/rule_check.py` + `evals/core_rules.yaml` guard every §23 bullet; `--mutate` proves each deletion goes red; eval 19 has two negative fixtures. Rejected: executable counter-model tests (reset, wrap, lane swap) in the skill. The skill ships the rules, not a measurement tool; the project's tool carries those selftests. |
| M-21 | C HWFS-006 | BLOCKER | "Gating timers for an exact window" ignores the actual gate times and an incomplete gate. | FIXED (§20): record the actual gate start and end; an incomplete gate makes the window INCONCLUSIVE. |
| M-22 | D R13 | MAJOR | A host-side loop can stand in for a media-link result. | FIXED (§20): the record names the topology; a host-loop result is not a media-link result. |
| M-23 | D R14 (rest) | MAJOR | No pattern configuration check, no thermal soak gate, no full lane matrix. | PARTLY. Fixed: read back the pattern, polarity and enable at both ends before the gate; per lane and per direction. Rejected: a soak as a skill gate. The criteria file sets the soak; §18 sizes the soak limits from a fit under traffic. |
| M-24 | A-07 | MINOR | "The read at the end covers only the last second" assumes a 1 s poll. | FIXED: the flag is ORed over every read of the window; the sentence is gone. |
| M-25 | B-13 | MINOR | The record-name check does not prove the record can be written. | FIXED: refuse an existing name; open for exclusive create and write the identity first. |
| M-26 | B-09 | MINOR | §20 "arm (setup, settle, …)" still hides the settling. | FIXED: arm is setup and flag clearing; the settling is judged inside the run. |
| M-27 | C HWFS-022, D R06 (MAJOR), A-10, B-25, D R20 (MINOR) | MAJOR | The CC voltages omit the Default level, read as acceptance values, apply only before PD, and no high-impedance read is required. | FIXED: the three bands over 5.1 kΩ (0.25–0.61 V Default, 0.70–1.16 V 1.5 A, 1.31–2.04 V 3 A); the plain DC range; read before a PD contract; under a contract read the accepted PDO; PD 3.0 Rp toggling. |
| M-28 | C HWFS-019 (BLOCKER), A-20 (MINOR) | BLOCKER | A connector cage as the ground point may be chassis, RC-coupled or floating. | FIXED: a designated circuit-ground test point; the cage only after its tie to signal ground is confirmed. |
| M-29 | C HWFS-021 | MAJOR | "The fix is on the signal lines, not the rail" is one board's answer stated as general. | FIXED: trace every feed path and fix each one; the signal lines are the worked example. |
| M-30 | C HWFS-024 | MAJOR | The health poll has no maximum latency and no sensor-failure rule. | FIXED: poll period well under the thermal time constant; a failed sensor read stops the run. |
| M-31 | C HWFS-025 | MAJOR | "Only the rail switch is an absolute stop" contradicts the back-power path. | FIXED: a rail switch with verified isolation, and no signal-line back-power. |
| M-32 | C HWFS-026 | MAJOR | "The read-back of the active set is the only proof" is overstated. | FIXED: read back the active set, then the configuration status and the data path state. |
| M-33 | C HWFS-027 (MAJOR), A-09 (MINOR) | MAJOR | "Leaving low power does not bring the data path up" is not universal. | FIXED: the result depends on the data path controls and the state machine; read the state, never assume it. |
| M-34 | C HWFS-028 | MAJOR | An application selected by its interface name is not a unique identity. | FIXED: select by the whole descriptor (host and media codes, lane counts); key the criteria on the firmware version. |
| M-35 | C HWFS-029 | MINOR | "One browser now…" names no browser or version. | FIXED: name the browser, the version and the test date; the rule also depends on the page's origin. |
| M-36 | C HWFS-030 | MAJOR | A wired serial link offered as an alternative to encryption. | FIXED: an authenticated, encrypted session; a wire reduces exposure but does not replace encryption. |
| M-37 | A-19 | MINOR | §18 is titled "without instruments" but holds a meter session. | FIXED: "Bring-up with few instruments, …". |
| M-38 | A-25 (NOTE), D R16 (MINOR) | MINOR | Hard-to-read sentences: the two gates, "13 degrees and 1.6 degrees per watt", "0.43 mm over the springs". | FIXED: the gates named; 13 K above the idle fit and a 1.6 K/W steeper slope; "the spring height". |
| M-39 | B-17 | MINOR | The software-track intro says "Sections 3 to 17". | FIXED: "Sections 3 to 23"; guarded in `core_rules.yaml`. |
| M-40 | C HWFS-009 (BLOCKER), D R09 (MAJOR), A-14 (MINOR) | BLOCKER | "A pattern checker does not care which generator lane feeds it" means PRBS cannot prove the lane map; one-layer loops depend on the pinout; coupling caps and crosstalk. | FIXED: a pattern checker cannot prove the lane map; prove it with a per-lane marker or error injection; one layer only when each row pairs a transmit and a receive pair; polarity and precoding per lane; crosstalk against the SI budget; coupling from the interface specification and both ends. |
| M-41 | C HWFS-023, D R07 (MAJOR), A-11 (MINOR) | MAJOR | The PD sink rule conflates a no-PD fallback with a 5 V-only PDO, states one controller's buffer as general, and uses a soft reset as the query. | FIXED: test both cases; read the buffer behaviour in the chosen datasheet; Get_Source_Cap first; a soft reset only when that fails. |
| M-42 | C HWFS-032 (MAJOR), A-12 (MINOR) | MAJOR | The grille rule does not support its example, and airflow needs the fan and system curves together. | FIXED: the fan curve meets the enclosure impedance curve; model or measure together; the example gives the swept areas. |
| M-43 | C HWFS-033, D R10 (MAJOR), A-13 (MINOR), A-28 (NOTE) | MAJOR | "Must reach full speed inside 30 s" does not follow from 44 J/K; losses neglected; the taller-sink outcome is project-specific. | FIXED: t ≤ ΔT_margin × C / P (5 K, 44 J/K, 8 W → about 27 s); fit a model with losses; the taller-sink sentence is gone. |
| M-44 | C HWFS-020 | MAJOR | Switch sizing by drop omits SOA, inrush, current limit, reverse current and fault energy; a tool tristate is not fail-safe. | FIXED: the extra checks named; powered-off isolation in hardware; the tool state helps only while the tool runs. |
| M-45 | C HWFS-031 | MINOR | A stored fan curve alone is not a fail-safe start. | FIXED: a fail-safe start-up duty and an over-temperature path that needs no host. |
| M-46 | C HWFS-034 | MAJOR | "Pick by the ambient" may use the wrong rating. | FIXED: the quantity the datasheet rates (ambient, case or junction) at the worst local temperature, with self-heating and margin. |
| M-47 | C HWFS-037 | MINOR | The single-reflow rule omits the assembler's order and the profile. | FIXED in pcb-layout-dfm §9 and schematic-phase §6. |
| M-48 | B-26 | MINOR | "Size the electronics … and the heat sink for the first build" reads two ways. | FIXED: two sentences. |
| M-49 | B-23, B-24 | MINOR | The study rules and §18–§20 use one product class's words. | PARTLY. Fixed: the study rules restated generally; the examples marked as one two-ended test product. Rejected: removing module terms such as "data path" and "application" where the rule is about them. |
| M-50 | B-18 | MINOR | schematic-phase is titled G0 → G1 only; the routing row omits the studies. | FIXED: title and routing row. |
| M-51 | B-07, C HWFS-042 | MAJOR | "Make the cell wall the gate wall" contradicts `wall_gate + design_margin`. | FIXED: the cell wall is the design wall; the old phrase is banned in `core_rules.yaml`. |
| M-52 | A-04 (MAJOR), B-08 (MINOR) | MAJOR | The pitfall "Design 0.1 over the gate" contradicts `design_margin` ≥ 0.3. | FIXED: "Draw at `wall_gate + design_margin` (≥ 0.3)"; the old phrase is banned. |
| M-53 | C HWFS-040 (MAJOR), A-15 (MINOR) | MAJOR | "Cannot end round or in a V; run the boss to the bed" overstates; a blunted V within the overhang limit prints. | FIXED: a V or teardrop within the overhang limit with a blunted tip, else the slab; check the sliced toolpath. Pitfall aligned. |
| M-54 | C HWFS-045 (MAJOR), A-16 (MINOR) | MAJOR | "Holds lift and twist, never a sideways pull" uses frame words and misstates the key. | FIXED: resists sliding and rotation in the joint plane, not separation normal to the faces. |
| M-55 | C HWFS-039 | MAJOR | "Derive any proud height from the pocket depth" reverses the functional stack. | PARTLY. Fixed: the two sum to the disc thickness; set the proud height from the mating need, then check the depth fits the wall. Rejected: dropping the wall check, which is what the rule protects. |
| M-56 | C HWFS-043 | MAJOR | "Bridge it in two layers" is not portable. | FIXED: check the span against the process bridge limit and read the G-code. |
| M-57 | C HWFS-038 | MINOR | The magnet budget omits adhesive, clearance and tolerance. | FIXED. |
| M-58 | C HWFS-041 | MINOR | "Hull the pad" and "run to the outline" are prescribed from one census artefact. | FIXED: where the clearance or function allows; re-run the census. |
| M-59 | C HWFS-044 | MINOR | "Put a foot beside its screw" is not universal. | FIXED: a removable plug is the other way. |
| M-60 | B-22 | MINOR | "Room above the vents" conflicts with the slab and the vent drop. | FIXED: drop the slots under the boss after the vent register is chosen. |
| M-61 | A-22, B-19 | MINOR | Two pitfall lines on the same plain-bar case. | FIXED: merged into one line with a pointer. |
| M-62 | B-20 | MINOR | New pitfall lines carry no home pointer. | FIXED: 28 lines gained `(file §n)`. |
| M-63 | C HWFS-046 | MAJOR | The cable-on moment ratio omits the cable force, direction and height. | FIXED: the row states the force, direction, height and the minimum moment ratio. |
| M-64 | C HWFS-047 | MAJOR | One finish block for every plate overgeneralises; a config cannot prove a dry spool. | FIXED: a justified geometry exception is named; the spool is a separate process row. |
| M-65 | C HWFS-048 | MINOR | "One of the two is enough" for hole compensation; three bores prove little. | PARTLY. Fixed: never compensate one hole in both places without tracking each. Rejected: a size and orientation matrix. The three-bore coupon is a worked example for one insert fit. |
| M-66 | C HWFS-061 | NOTE | The finish-block cell packs many settings. | REJECTED: a table cell lists the block's keys; it is data, not instructions. |
| M-67 | D R23 (MAJOR), D R21 (MINOR) | MAJOR | New bullets join several instructions, against the writing standard. | PARTLY. Fixed: every new or changed sentence linted at 20 words and split. Rejected for this branch: older lines outside the diff. |
| M-68 | C HWFS-035 (MAJOR), D R19 (MINOR) | MAJOR | The pad impedance example lacks its parameters; "void the plane" can hurt the return path. | FIXED: a field-solver estimate for one stack; a void changes the return path; model the whole launch with the live stack and the connector model. |
| M-69 | C HWFS-036, D R18 (MINOR), A-27, B-29 (NOTE) | MINOR | The back-drill and layer-count facts read as general. | FIXED: "that fab's table, that day; verify it live". Rejected: a source URL in the skill; the reference already says to read the live page. |
| M-70 | C HWFS-049 | MAJOR | The search body `{"keyword", "currentPage", "pageSize"}` is not valid JSON; the endpoint is undocumented. | FIXED: a valid key/value body; verify live before use. |
| M-71 | C HWFS-050 (MAJOR), A-17 (MINOR) | MAJOR | "A distributor API … never a drawing" contradicts the `pdfUrl` path. | FIXED: distributor metadata is not authoritative; the linked manufacturer PDF is the primary source. |
| M-72 | C HWFS-053 (BLOCKER), D R22 (MINOR) | BLOCKER | §15 promises a leak gate, but the skill ships no exporter, scanner or CI gate. | PARTLY. Fixed: the gate reads the final exported tree and the push depends on it; the generator is project code, like the cut generator; `generic_lint.py --skill <export tree> --private-terms …` is named as a usable scanner. Rejected for this branch: a skill-side exporter. The skill ships contracts, not project generators (SKILL §10). |
| M-73 | C HWFS-055 (MAJOR), A-18, B-27 (MINOR) | MAJOR | Allowing a key by a regex on its line hides a second leak on that line; screenshots have no provenance and pixels are not scanned. | PARTLY. Fixed: strip the exact allowed string before the match, never skip the line; record each screenshot's capture command, date and page state; each blind review reads every screenshot. Rejected: OCR in the gate; the skill has no OCR tool, and the human read covers it. |
| M-74 | B-06 | MAJOR | §15 is an orphan: SKILL.md and the routing row never name the public export. | FIXED: SKILL §10 and the routing row link §15; guarded in `core_rules.yaml`. |
| M-75 | B-16 | MINOR | §8.7 is not linked from SKILL.md. | FIXED: §8 step 5 and the routing row; guarded. |
| M-76 | C HWFS-059 (MINOR), A-30 (NOTE) | MINOR | The Pages rule is provider-specific and the configure step can enable Pages. | FIXED: "On GitHub Pages, …"; the configure step named. |
| M-77 | C HWFS-060 | NOTE | §15 bullets combine two gates and three operations. | FIXED: one rule per sentence. |
| M-78 | C HWFS-057 | MAJOR | `release_archive.sh` stages several packages of record; `workflow_dispatch` bypasses the tag gate. | FIXED: the script refuses several packages with the same md5; the release job runs only on a tag ref. |
| M-79 | C HWFS-058 | MAJOR | "A tag set on the old main needs a forced re-point" is unsafe for a published tag. | FIXED: re-point only an unpublished tag; a published tag stays, and a new tag follows. |
| M-80 | C HWFS-056 (MAJOR), A-21, B-21 (MINOR) | MAJOR | "One blind pass per discipline before each gate" conflicts with one round per gate, fixes one product's list, asks for inapplicable passes, and the reason reads backwards. The workflow is not wired. | FIXED: one pass per discipline that a gate freezes; the list comes from the scope; passes are roles inside the gate's one round; the reason rewritten; the workflow split is manual and says so. |
| M-81 | B-15 (MINOR), A-31 (NOTE) | MINOR | The smoke greps only the §6 and §8.7 headings. | FIXED: the smoke runs `rule_check.py --mutate` over all five groups. |
| M-82 | A-23 | MINOR | `smoke/README.md` says a smoke check takes `needs-mesh:`; only eval checks read it. | FIXED. |
| M-83 | B-30 | NOTE | A relative `--python` fails every eval check. | FIXED: `run_evals.py` makes the resolved path absolute. |
| M-84 | A-29, B-31 | NOTE | A 49-word CHANGELOG sentence; the ten coordinator items sit outside the class count without saying so. | FIXED: split, and the count stated. |
| M-85 | D R25, D R26 | NOTE | The GBd / Gb/s rule and the switch drop arithmetic are correct. | ACCEPTED. |

## History, not rewritten

Past versions of `scripts/generic_lint_terms.yaml` in the public history hold the private terms. Their hashes and term classes are in the
branch's pull-request report to the owner. A history rewrite is the owner's decision.

## Round 2: three confirmation reviews

Inputs: three blind reviews of the round-1 tree and diff, the lint-terms hunk left out. Claude (29 findings: BLOCKER 1, MAJOR 6,
MINOR 16, NOTE 6), GPT (38: BLOCKER 6, MAJOR 20, MINOR 10, NOTE 2) and Grok (21: BLOCKER 2, MAJOR 7, MINOR 7, NOTE 5). Ids: Claude
F-nn, GPT by its own prefixes, Grok Rnn. 88 findings merge into 49 rows. Round 2 reopened round-1 rows M-07, M-10, M-11, M-12, M-13,
M-15, M-20, M-40, M-41, M-43, M-55, M-56, M-72 and M-04: their round-1 fix was incomplete.

| severity | rows | FIXED | PARTLY | REJECTED | ACCEPTED |
|---|---|---|---|---|---|
| BLOCKER | 6 | 4 | 2 | 0 | 0 |
| MAJOR | 24 | 21 | 2 | 1 | 0 |
| MINOR | 18 | 16 | 2 | 0 | 0 |
| NOTE | 1 | 0 | 0 | 0 | 1 |
| total | 49 | 41 | 6 | 1 | 1 |

| id | sources | severity | finding | disposition |
|---|---|---|---|---|
| N-01 | F-01, R01 (BLOCKER) | BLOCKER | A saturating error counter reads zero deltas and can PASS a bad link. | FIXED: a read at the saturation value makes that window and every later one INCONCLUSIVE; the count is a lower bound; a lower bound over the limit is a FAIL. Eval 19 fixture. |
| N-02 | BER-02, R02 (BLOCKER), F-02 | BLOCKER | The window bound follows the previous BER only; after a clean window a rise can wrap the counter several times. No first-window number. | FIXED: every window capped at (modulus / 2) / (lane rate × BER_max), and by the opportunity counter's width, whatever the window before. Numbers: about 40 ms at 0.5 and 20 s at 1e-3 for 32 bits at 106.25 Gb/s; the first window uses the cap. |
| N-03 | F-03, BER-07 | MAJOR | Only a zero-error claim has a bound; k > 0 can PASS on the point estimate. The bound is stated as fact, its assumptions unstated. | FIXED: Poisson bounds at a stated CL for any k; PASS only when the upper bound is under the limit, FAIL when the lower bound is over it, else INCONCLUSIVE; independence stated, window spread reported; opportunities, not bits, for other units. |
| N-04 | BER-05 (BLOCKER), F-04, R04 | BLOCKER | "Where the hardware allows" lets an unchallenged deaf checker pass. | FIXED: challenge every judged lane and direction; known-bad paths named (PRBS31 against PRBS15, inverted polarity, error injection, a known-bad cable); an unchallenged lane reads "checker unproven" and cannot enter a release record. Eval 19 fixture. |
| N-05 | BER-01 (BLOCKER), R03, F-08 | BLOCKER | Symbol, block and codeword counts divided by the bit rate give a wrong ratio. | FIXED: event unit and opportunity count in the same unit; BER only for bit errors; compare a ratio only with a limit in its unit; the growth law in the counter's own unit. |
| N-06 | BER-04, R16 | MAJOR | A proven-wrap FAIL and "any invalid window is INCONCLUSIVE" contradict; invalid states are scattered. | FIXED: one list of invalid states; the lower-bound FAIL wins over INCONCLUSIVE. |
| N-07 | BER-03 | MAJOR | "Both counters falling" misses a reset of one counter and confuses wraps with resets. | FIXED: each counter on its own; a fall no wrap explains invalidates the window. |
| N-08 | BER-06, F-10, F-09 | MAJOR | "The first window measures the lock-in" is vendor-specific; the example rule reads AND or OR. | FIXED: the first window can hold the lock-in; the rule decides; never drop a window by default; call the cause lock-in only when a control proves it; the rule uses observable lock signals where they exist; the example says AND. |
| N-09 | BER-08 | MAJOR | The counting point and the counted interval T are not defined. | FIXED: the counting point (FEC, gearbox) recorded; the lane rate taken there; T is the enabled time from the verified reset. |
| N-10 | BER-09 | MAJOR | One update interval of slack is not a bound on field skew. | FIXED: a frozen read or an atomic latch, else a timestamp per field and the total skew bounded and added. |
| N-11 | BER-10 | MINOR | "At least two counted windows" is arbitrary. | FIXED: enough counted windows to apply the settling rule; two is the dated tool's need. |
| N-12 | F-11 | MINOR | No rule for counts during lock loss, or without a reported ratio. | FIXED: a window with a lock loss stays out of the run totals; without a reported ratio the two computed ratios are compared. |
| N-13 | R13 | MINOR | The 1.5 tolerance example is loose. | FIXED: the criteria state the tolerance; 1.5 is a dated tool value; tighter where the resolution allows. |
| N-14 | R12 | MINOR | CC voltages between the bands are undefined. | FIXED: a reading between two bands is INCONCLUSIVE; measure again. |
| N-15 | USB-01, F-25 | MAJOR | The Default current omits the USB version, configuration state and Battery Charging; the contract current is the RDO. | FIXED. |
| N-16 | USB-02 | MAJOR | A soft reset is not a fallback query. | FIXED: Get_Source_Cap is the query; a soft reset is protocol recovery, used only as the policy engine and the datasheet direct. |
| N-17 | THM-01, F-18 | MAJOR | Neglected losses overstate C and the safe time; the time omits sensing, command and spin-up. | FIXED: C from the initial slope or a net-flow fit; t covers detection to full airflow; "at most about 27 s". |
| N-18 | THM-02, F-26 | MINOR | The 20–27 % figure is unsupported; the fan areas are gross discs. | PARTLY: labelled as a 1-D estimate that a curve model overrides; gross disc areas stated. Rejected: deleting the example; it shows the size of the error. |
| N-19 | SI-01 | MAJOR | "A checker cannot prove the lane map" is overstated; pair placement does not prove one-layer routing. | FIXED: an identical-pattern lock cannot prove it; a lane-unique pattern or seed, or one injected error, can; the whole launch geometry is checked. |
| N-20 | SI-02, F-20 | MINOR | "Drops far below" is not universal; the pad example omits single-ended and target. | FIXED: "can drop"; single-ended against a 50 Ω line; split. |
| N-21 | PWR-01, R15 | MAJOR | A buffer with powered-off isolation covers only its own paths; the power bullet packs four rules. | FIXED: rated Ioff covers only its paths; list and check every feed path; the bullet split into four. |
| N-22 | DFM-01 | MAJOR | "Sum to the disc thickness" contradicts the adhesive. | FIXED: depth + proud = disc + bondline, plus clearance and worst-case tolerances. |
| N-23 | DFM-02 | MAJOR | "Blunt its tip to the wall gate" contradicts the design wall. | FIXED: blunt to `wall_gate + design_margin`; check the sliced minimum and the census margin. |
| N-24 | DFM-03, R14 | MAJOR | The two-layer bridge is still a recipe. | FIXED: layers from the validated process, span and seat strength; the two layers are a worked FDM example. |
| N-25 | DFM-04 | MINOR | The foot and shear-key rules are categorical. | FIXED: the screw-access need first, the foot beside its screw as one layout; the key only as tight as its fit. |
| N-26 | DFM-05 | MINOR | The three-bore coupon is stated as proof. | FIXED: a worked example; test the part's sizes, orientation, material and process. |
| N-27 | LEAK-01, LEAK-02 (BLOCKER), F-06, LEAK-03 | BLOCKER | The named scanner does not meet §15: `generic: ok` skips, no exact-string allow, ids only in `.md`, history skipped, binaries skipped, no names without the private file. | PARTLY. Fixed: `generic_lint.py --export` needs the private terms, reads every file, name and symlink target, skips nothing, strips exact allowed strings, scans the strings of binaries and flags each unreviewed binary; selftest per case. Rejected: OCR and archive extraction; an archive or image is a binary that a human must review before it is allowed. |
| N-28 | F-07, F-12 | MAJOR | Without the private file nothing checks names; a typo in the env var skips silently. | PARTLY. Fixed: a named but missing term file exits 2; every run prints which terms it used; the export mode refuses to run without them; CI writes them from a secret (§15, README). Rejected: hashed terms; the terms are regexes, and a hash cannot match a pattern. |
| N-29 | LEAK-05 | MAJOR | The README bans every company name while the skill names public vendors and tools. | FIXED: private names (project, person, customer, employer, order, private part) against public dependencies (fab, distributor, tool, model vendor). |
| N-30 | F-05, TEST-01, R07 | MAJOR | One phrase per bullet leaves 47 of 86 §23 sentences unguarded; inversions and paraphrases stay green; the intro is unguarded. | FIXED: `every_sentence` mode; four sections guarded sentence by sentence, intro included; `--mutate` deletes each sentence and flips one verdict word per sentence; banned patterns (`never_re`) catch rewordings. Stable rule ids rejected: the sentence is its own id. |
| N-31 | TEST-02, F-17 | MAJOR | Many changed rules have no guard (case-pipeline, part-verification, fdm, pcb rules). | PARTLY. Fixed: §6, §15 and §8.7 are now sentence-guarded too. Open: the other changed files have no guard; a guard there is the next step. |
| N-32 | TEST-03 (BLOCKER), F-24 | BLOCKER | Eval 19 never grades an agent; its checks prove only the text. | PARTLY. Fixed: the runner counts the assertions of an eval with checks as needing an agent run and a human grade, and says the checks prove the text only. Rejected: an automatic agent grader and executable counter models; the runner has no agent, and the skill ships rules, not a measurement tool. |
| N-33 | R06 | MAJOR | Eval 19 ran `--only measurement,navigation`. | FIXED: the whole rule file, and the mutation proof over every group. |
| N-34 | TEST-04 | MINOR | The "run totals" fixture deleted another sentence. | FIXED: it deletes "The verdict uses run totals per lane and per direction." and asserts that exact rule. |
| N-35 | R05 | MAJOR | "`E-[0-9]+` does not match `X-LANE-3`." | REJECTED: the reviewer is wrong. `re.search(r'E-[0-9]+', 'X-LANE-3')` returns `E-3`. The sentence now names the matched text. |
| N-36 | R09 (MAJOR), LEAK-04 | MAJOR | The review record's first line named the agent workstream. | FIXED: the comment is gone. |
| N-37 | F-13 | MINOR | One generator's yaml key stayed in a pitfall line. | FIXED in the pitfall, the CHANGELOG and an old review; the key is a private term. |
| N-38 | F-14, R10 | MINOR | The 0.11.24 heading still named the product type. | FIXED. |
| N-39 | R11 | MINOR | The 0.11.24 entry named a branch and its pull request. | FIXED: "an earlier open branch (0.11.17)". |
| N-40 | F-15 | MINOR | "Five greps" overstated the smoke. | FIXED: one rule check over every group and one grep. |
| N-41 | F-16, R08 (MAJOR) | MAJOR | The pitfall said "per discipline before each gate", against SKILL §5. | FIXED: "that a gate freezes, as roles inside its one round"; the old phrase is banned. |
| N-42 | CLAIM-01 | MAJOR | "Every BLOCKER and MAJOR is fixed" and "each guarded rule" were not true. | FIXED: the CHANGELOG, this record and the rule_check docstring state what the guards cover and what stays open. |
| N-43 | SRC-01 | MAJOR | "The API never gives a drawing the PDF lacks" is a universal claim. | FIXED: verify every technical artifact against its manufacturer-controlled source. |
| N-44 | OPS-01 | MINOR | The `gh pr checkout` claim has no version. | FIXED: dated, with "read `--help` of the installed version". |
| N-45 | NAV-01 | MINOR | The §8.7 link lacked the `references/` path. | FIXED in SKILL.md and the guard. |
| N-46 | F-21, F-22, WRITE-01 | MINOR | Several sentences hold more than one instruction. | PARTLY. Fixed: §23, §6 power, §8.7 and §15 split, the flags named. Rejected for this branch: older CHANGELOG and pitfall lines outside the change. |
| N-47 | F-19 | MINOR | The configure step can enable Pages only with an admin token. | FIXED. |
| N-48 | F-23 | MINOR | "Size the heat sink for the first build" reads two ways. | FIXED: for the load of the first build, with room for the top load. |
| N-49 | F-26, F-27, F-28, F-29, META-01, META-02, R17, R18, R19, R20, R21 | NOTE | Arithmetic, versions, navigation and the public terms file checked correct. | ACCEPTED. R19 is carried by "Key each limit to that point". |
