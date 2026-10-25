# software-track.md — bring-up tool, package, criteria, codes, selftests

The software exists before the hardware does. So you build it to run without hardware, and it generates the documents that describe it.
Sections 1 and 2 give the order and the selftest pattern. Sections 3 to 23 hold the rules the package, bench-preparation and bring-up rounds proved. Each rule carries its
reason and one worked example.

## 1. Order
1. **Bring-up tool** (`tools/<board>_bringup.py`): every hardware access sits behind one adapter (bus, GPIO, identity reads). Flags: `--list`,
   `--dry-run <cmd>` (prints the transactions it would do), `--selftest`. The selftest uses a fake device from an iterator. The iterator hooks
   on the exact read shape the poll uses. A time-driven path is testable: swap `time.sleep` for a no-op in `try/finally`. Driver notes go in
   `90-log/ENV.md` (which OS binds a serial driver, what `Access denied` means). The hardware step stays OPEN until a unit exists.
2. **Architecture note** (`20-design/SOFTWARE_ARCHITECTURE.md`): states, safety guards S1…Sn with their record trail, override flags, and what
   each guard protects. A fixed cap and a warn or throttle level are both printed at release. Otherwise the operator never sees a WARN.
3. **Criteria as YAML** (`20-design/test_criteria.yaml`): every test T-nn with limits. The tool reads them. The test plan and the technician manual
   quote them from the same file (one source). **Who decides**: the agent drafts every limit from the spec with its source in a CC row. The owner
   approves the set (a D row the yaml header cites) before the software refuses or throttles on it. The refuse-vs-warn posture per guard is an
   owner answer at kickoff (`references/kickoff-questionnaire.md` §G). The owner also names who owns each number (G2).
4. **Result verdicts**: PASS / FAIL / **INCONCLUSIVE** with a reason code from one code list (`tools/codes.py` or a yaml). The technician manual's
   code table is GENERATED from that list. A generator check asserts set equality (every code the software can emit is documented).
5. **Records**: identity fields (serial, firmware, board md5) copied into the record FIRST, gates second. A refusal must still be attributable.
6. **Rule-2 posture**: a gate the owner has not nodded yet ships as an optional flag that warns when omitted. The nod is a one-line
   `required=True`.
7. **udev / driver rules** ship with the tool. The first-plug hazard (default UART mode driving pins for ms) is documented and mitigated.
8. **Package** (`tools/<pkg>/`): carve it out of the working tool once the tool's selftest passes (§3). The tool becomes a shim over the package.
9. **Spec revision**: after the review round, revise the architecture note to the code as a dated revision (§10). After several
   code rounds the revision is a checklist from the decision rows (§17).
10. **Hardware phase**: the first physical phase waits for boards. Name what the first boards will hit in the record before they arrive (§13).
    Write the hardware runbook from the code of record before they arrive (§14). Build the calibration tool on cloned records (§15).

## 2. Selftest pattern
- Fake sensor or EEPROM from a list of (offset, length) → bytes. Assert the identity and page reads keep their real values while the ramp
  advances per health sample.
- One `--selftest` run in the adopt gates. It needs no hardware and no network.
- The selftest patches `time.sleep` on module and instance attributes, never on a module global of the tool. A global of the tool is not
  visible from a package.
- Under the patched `time.sleep` two samples share one timestamp, so a slope reads None. Assert the temperature, not the slope.

## 3. Carve a package out of the working tool
- Move code verbatim. Keep the tool's selftest byte-identical as the fidelity proof. A moved line that changes is a decision, not a move.
  *Reason*: the selftest is the only proof that the package does what the tool did. *Example*: a 1700-line package moved with four edits to
  the selftest. Three edits renamed an entry call. The fourth was one `__file__`-relative path.
- **A module loaded twice has two copies of every class**. Load the legacy module by path once. Then rebind every shared class in it (one
  `setattr` per class). *Reason*: `except Nack` in the legacy copy never matches the `Nack` the package raises. *Example*: the package port
  raised the shared error. The legacy command caught its own copy and missed it. Five `setattr` lines fixed it.
- A `__file__`-relative data path inside the package keeps the script-mode selftests alive. `importlib.resources` does not. A path that climbs
  out of the package (`../../criteria`) breaks in a wheel (§11).
- A package module named like a stdlib module (`inspect.py`) shadows it in script mode. `dataclasses` imports `inspect`. So a sibling selftest
  fails while a cached check still reads PASS. Name project modules so no stdlib name collides.
- A module that imports nothing from the package can run as a file (`safety.py --selftest`). One that does cannot. Decide per module which
  mode its selftest uses.
- The parity check: run every command on the fake through the tool and through the package. Diff the two outputs.

## 4. Print and return: one `say` callback
- Separate print from return with one callback, not with a captured log. Every primitive takes `say=None`. The first line is
  `say = say or _quiet`. The CLI passes `cli.say`. *Reason*: the primitives print progress while they wait (a state change, one health line per
  second). A list of lines returned at the end hides a 60 s hold from the operator.
- The selftest keeps its stdout checks with `functools.partial(f, say=say)`.
- A console library wraps at 80 columns when stdout is a pipe. Set soft wrap on the console, or the health lines break into tails.
- A yaml reader reads `off` as `false`. Quote a state word: `hood: "off"`.

## 5. The judge and the runner
- **Decide what a missing value means before you write the rule kinds**. A judged key without a value is `INCONCLUSIVE NOT-MEASURED`. It is
  never 0 and never skipped. FAIL still wins over INCONCLUSIVE. *Reason*: a rule that skips an absent key lets a run that stopped early read
  PASS on identity alone.
- A judged key that is absent for a known reason carries its own marker (`edge_seen: false`). Otherwise every record reads NOT-MEASURED.
- A safety gate reads an absent key as unsafe (`not straps_intact`). So the fixture record must carry the key.
- **Test the judge on what the runner writes, never on a hand-made record**. The first check: run the fake through the runner, round-trip the
  record through JSON, then judge it. Write that check before the hand-made probes. *Reason*: the author types the record the author expects.
  *Example*: 31 hand-made probes passed. One real record failed four ways from one root. The runner wrote `MEASURED (layout assumed)`, a table
  label instead of `raw`, and `ABORTED: x` with a space. Every good cable read INCONCLUSIVE, and a bit-error rate of 1.0 read PASS. The fix
  was one adapter in one place.
- Keep one selftest case per judge path. The paths: the missing section, the missing module threshold, and a FAIL with the block removed.
- A slope needs two samples. A one-second soak is NOT-MEASURED. So the shortest judged soak asks for two seconds.

## 6. Fakes
- **Write the fake's default as the field default**. A fake that inserts itself after the open hides the normal case. *Reason*: every real
  lot cable is in the cage before the scan. *Example*: the fake inserted at 0.3 s. The watch step refused a present module. The first board
  would have read NOT-PRESENT on every cable.
- Test the pre-inserted path and the never-present path, not only the edge.
- A dead fake end must ACK once (the insert watch reads one byte) and NACK after. Otherwise the flow reads NOT-PRESENT, not NO-ACK.
- A scripted `read` callback is the cheapest place to reshape a persistent fake between the cables of one open.
- A primitive that tags every sample at or above WARN prints once. A check that expects one tag reads the primitive wrong. Read the
  primitive, then write the check.
- A fake with one serial makes every lot scan one label. A dry run with a label check then fails the cable before the check you wanted.
  Give the fake a serial per cable, or skip the label check in the dry run.

## 7. Wire a flow on the primitives
- Build the flow on the primitives as they are. Then read what each one does at its edges before you wire it. *Example*: the test command
  released both ends in its `finally` and returned them to low power. The flow's own release was an idempotent repeat, not a conflict. A watch
  on a present module waited for a removal first, so the fake staggered the ends.
- A report page written before `close()` lists only the hashes that are final at that moment. The event log grows until close. Say in the
  page which it is.
- A session per process needs an `attach` that counts the event lines to continue the sequence number.
- Two sessions of one name in one second collide on the manifest. Name them in the selftest, or sleep one real second between them.

## 8. Read the standard before you name a register
- **Read the standard's table before you name a register**. A brief can ask for a register that does not exist. *Example*: the brief asked for
  a management-init duration byte. The standard holds that value as a timing parameter in a table, with no register. The durations sit two
  bytes lower, and the asked bytes are module characteristics.
- Grep the table index of the text extract first, then the body. The index line gives the printed page. The body line gives the bytes.
- Every decoder cites its table in a notes file (`10-spec/datasheet_notes/<standard>.md`): table, page, bytes, and the decoded meaning.
- A decoder is faithful to the primary text: no offset, no default, no guess. A field the text does not define is `unknown`, recorded only.
- The kickoff names the standard tables the tool decodes (G2). A table outside that list is a decision row before a decoder exists.

## 9. Process boundaries: one process, one open
- A lot loop over separate processes cannot hold a USB handle. So "open once" means the checklist and the safety line once, not one handle.
  Run the lot in one process with one open.
- `next` re-opens without a prompt. The port constructor re-latches SAFE before it drives.
- A verdict the lot changes after the session closed must not rewrite the closed manifest. Put it in `lot.json` and apply it to the row in
  the summary. *Example*: a missing ACK at the end of a swapped run.
- A session id carries the UTC second. Two runs of one label in one second refuse by name.

## 10. Revise the spec after the review round
- Revise the architecture note to the code after the review round, never during it. The revision is a dated row, OPEN for the owner, with a
  veto hash. *Reason*: eight rows each carried a list for the next revision. The lists disagreed with each other and with the code.
- Read the code of record for every fact: the code list, the event calls, the parsers, the schemas. Cite the row that caused each change.
- Keep an old sentence only when it carries a decision. One OPEN row with a veto hash is cheaper than a spec the next writer cannot trust.
- List the deltas in the row: event types, codes, verbs and flags, record schemas, rule kinds, signatures.
- After several code rounds the delta lines of the rows are the checklist of the next revision (§17).

## 11. Packaging: the wheel
- A data file whose source of record lives elsewhere can be a symlink inside the package. The build tool copies the target into the wheel.
  The tree keeps one file.
- The paths that break in a wheel climb out of the package. So the selftest takes `--criteria FILE` and resolves a SKU name beside that
  file. Every tree-only check says `skipped`, never FAIL.
- Prove the wheel in a throwaway venv, never the shared one. Install it, run `--selftest`, read the last line.
- The build leaves `build/` and `*.egg-info/` behind. Remove them in the script, or the clean-tree check fails.
- A `--help` prints to stdout before the probe's own line. Read the probe's last line, not `startswith`.

## 12. Entry-point isolation
- A technician entry point imports no register-access module and exposes no safety override flag.
- Prove it with `sys.modules` in a fresh interpreter. The check: `python -c "import sys, <pkg>.cli_tech; assert '<pkg>.rd' not in sys.modules"`.
  Inside the selftest process the engineering module is already loaded, so a check there proves nothing.
- The technician `--help` lists no override flag. A grep over its parser is the second check.

## 13. Before the first boards: the hardware list
- A physical-hardware phase waits for boards. Name the things the first boards will hit in the record before they arrive. The blind
  reviewer's list of untested paths is that list. *Example*: five items. The pre-inserted cable. A switch mode that makes every read NACK. The real open
  path and its OS driver. A signal inside a real sleep. The real numbers of the first SKU.
- Each item gets a selftest where a fake can reach it, and an arrival row where only hardware can.

## 14. The hardware runbook, written before the boards
- Write the hardware runbook from the code of record, never from the spec. *Reason*: the code holds facts no document names.
  *Example*: no document named the insertion window of the run verb (a 15 s constant). One unit-state field had no writer verb. Both
  came out of a grep over the callers while the author filled the expected-lines column.
- A runbook row has four cells. They are the command, the lines to expect, the record file and the pass rule by test id. A row
  without one of them is a note, not a step.
- Put the printed strings of the primitives (`say(...)`) into the expected column verbatim. The technician then diffs the screen
  against the page.
- The reviewer's list of what the first boards hit (§13) is the runbook's closing checklist. One row per item, with the observation
  and where it shows.
- Ship a fix-list template beside the runbook: id, observation, command, record file, severity, decision row. Pre-fill the rows the
  writing found. A gap the runbook finds closes where it found it (one verb, one selftest line, one row).
- The open questions of the spec become decide-after lines: the question and the measurement that decides it.
- The runbook describes the tool as built. Rule 2 holds: no code change comes out of writing it, only fix-list rows.

## 15. Re-judging records and calibration
- A tool that re-judges old sessions must rebuild every input the live judge saw, not only the measured keys. *Reason*: the files
  are not the live record. *Example*: the engine read the runner's interrupt passthrough list. The rebuild lacked it. A thermal
  session that ran INCONCLUSIVE live re-judged FAIL, and the check called the cable "caught".
- Diff the live observed dict against the rebuilt one key by key before the first statistic.
- The report rows in the manifest carry no identity. Take the identity from the identity events. The events round the time axis,
  so two soak samples inside one hundredth give no slope. Read the live source for each key.
- Write the rebuild first. Judge one real session under the file of record and demand PASS with no NOT-MEASURED. Then compute a
  statistic.
- Clone one real session for the fixture (new serial, new error rate, new temperature, hashes recomputed), never typed manifests.
  The shapes stay the runner's. Add one clone per live status the engine can emit, not only PASS clones. *Reason*: a selftest with
  PASS clones of one shape stayed green through three review findings.
- A calibration candidate never loosens a limit of record. Cap every candidate at the record's own limit and say "the lower wins" in
  the method string.
- A candidate skips rehearsal sessions. The runner marks a dry run in the manifest (`hardware.dry_run`), and the selection reads the
  mark.
- The candidate tool refuses the file of record as its output path, and opens every output with `'x'`.
- Keep the candidates out of the keys the engine reads (`tightened`, a `calibration` block). Apply them only inside `--check`. The
  file of record then changes only through a decision row the owner approves. The run verbs refuse a file with a `calibration` block.
- A per-run writer collides with a selftest that runs the verb twice on one day. Remove both outputs, or use a second directory.

## 16. A live screen for the technician
- A live terminal page cannot take typed input while it runs. The prompt prints above the page and the echo lands under a hidden
  cursor. Stop the page. Print one static copy, bounded to the terminal height, with the prompt as its bottom line. Read the answer.
  Erase the answer line, move the cursor up by the copy's height, then restart. The live render overwrites the copy, so the page
  does not scroll.
- Feed the page from the session events, not from the `say` lines. One `on_event` hook on the session is one attribute and one
  `if`. The verdict and close events of `close()` arrive through the same hook.
- A screen hook never raises into the flow. Wrap the hook body in `try/except` and log the fault on the page. *Reason*: a screen
  fault that reaches the flow closes the cable's record as ABORTED, and ends a lot.
- A hook attribute set in `__init__` is absent on an `attach` that uses `cls.__new__`. Make it a class attribute.
- Both user interfaces run on the same functions (`say`, `ask`, `read`). Without the console library or a TTY, one line says so and
  the plain path runs.
- Every screen check runs on a string console. So the real terminal (a short height, a resize, Ctrl-C at the prompt) goes on the
  hardware list (§13).
- A console control call takes `(code, param)` tuples, not positional codes. A record's direction names (`A_to_B`) can differ from
  the verdict's (`AB`); map once.

## 17. The spec revision as a checklist
- A spec revision after several code rounds is a checklist, not a rewrite. The items are the "deltas for the next revision" lines
  of the decision rows since the last revision. *Reason*: one row alone named nine sections.
- Grep the code for every name before you write the sentence. The sources are the parser (`add_argument`), the docstring, the
  manifest writer and the selftest print line. *Example*: three facts in the delta lists had drifted from the code. A rules file was
  a symlink, not a copy. A named module never existed.
- Keep the open questions table and every PROPOSED tag. Count the tags before and after.
- Write the open questions the revision finds as new rows of that table, each with a recommended answer. Never as prose.
- The revision is a dated row, OPEN for the owner, with a veto hash (§10).
- Lint the added lines alone at the 20-word cap (`git diff | grep '^+'`). The whole-file gate at 40 hides a long new sentence.
  Code-fence lines merge into false hits, so read the hit text before you fix it.

## 18. Bring-up with few instruments, and the identity in the bridge chip
- With no meter, the first power still has an order that limits the loss. Charger on the power-only port for five
  seconds. Read the LEDs, touch the parts, smell. Then one minute. The host port comes last. *Reason*: a short on the
  host port can take the computer's port with it.
- A rail that is off still lights the LEDs on its pull-ups. Write that into the plan, so the first reading is not a fault.
- A tester whose module rail is a buck converter hums at no load. The light-load mode makes the ceramic capacitors sing. Note it
  for the next revision; it is not a fault.
- The USB bridge chip's EEPROM carries the unit identity. Build the image from an all-zero base and set every field. A tool that
  writes only the bytes you name leaves the rest at 0xFF on a blank chip, the vendor and product ids included. Print the image
  before any write, and check a read-back of record in the selftest.
- The bytes the bridge chip never reads hold a board-info area with its own checksum: the board revision, the order, the case preset.
  Lay the whole chip out in one function. The tool reads that area at open, with the product string, before any revision check.
  *Pitfall*: a merge moved the read out of the open path, and every run stopped at the revision check with no product.
- After an EEPROM write the chip resets and leaves the USB stack. A re-plug of the host cable is part of the procedure, not a fault.
- Read a module's EEPROM before you search for its part. A label can carry a typo; the EEPROM carries the catalogue number.
- A passive loopback plug and a passive copper cable are EEPROM-only tests on a management tester. Check the length and attenuation
  fields against the label: vendors leave them wrong or empty. A passive plug reads a flat memory, a zero temperature and a
  reserved state; that is the plug, not the bus.
- Run the thermal throttle path once on every tester build before you trust a long hold. A bare board with a cage sink and no air
  sheds about 5 to 6 degrees per watt, with a time constant near five minutes. A posture table written from a model can be six
  times too low; the module's own sensor and the throttle are the control.
- A dead bridge chip with its USB power LED on points at a latched input, current forced into a pin at cable attachment. The recovery
  is a full power removal: host cable, charger and module out for thirty seconds. A USB re-plug alone does not clear it. Isolate
  every bridge I/O that leaves the chip in the next revision: series resistors, a clamp array, powered-off isolation, a
  current-limited rail.
- A tester that cannot see its own power source relies on an operator flag. Put a charger-present sense and a rail current monitor
  on the next revision, and make the release step refuse itself when the budget is not there.
- The first meter session has its own traps. A meter's low-impedance mode loads the node with a few kΩ. It pulls a bled
  rail or a pull-up line down. Use the plain DC volts range.
- Use a designated circuit-ground test point as the ground point. A press-fit connector cage holds a probe tip without
  slipping. Use the cage only after you confirm that it ties to signal ground. Many cages go to chassis through an RC.
- A switched-off rail is not at 0 V while the host is plugged. Idle-high bus lines feed it through their pull-ups into the
  bleeder; one board read 0.57 V. Check a rail "off" with every source connected. Trace every path that feeds the rail, and
  fix each one. On that board the feed was the signal lines, not the rail.
- A laptop USB-C port may offer 1.5 A only. Read the source's current advertisement before you budget host power.
  Read CC with the plain DC range, never the low-impedance mode. Read it before a PD contract exists.
  Over the sink's 5.1 kΩ pull-down, 0.25 to 0.61 V means Default USB power.
  A reading of 0.70 to 1.16 V means 1.5 A. A reading of 1.31 to 2.04 V means 3 A.
  A reading between two bands is INCONCLUSIVE: measure again, never round it to a tier.
- Default USB power is 500, 900 or 1500 mA by the USB version and the configuration state. Battery Charging can raise it.
  Budget only what the port has granted.
- Under a PD contract, the contract sets the current. Read it from the accepted request (RDO), not from the CC voltage.
  A PD 3.0 source also moves its Rp between the 3 A and 1.5 A levels to signal collision avoidance.
- A fan that is off reads like a bad module. Three throttles in a row came from a fan with no power. Look at the fan before
  you blame the module, and give the next revision a tachometer read.
- A high-power window without a health poll is a hazard. One run polled nothing between its windows. The module crossed its
  warning limit and shut two lanes down. Poll both ends between windows, with the throttle limit. Set the poll period well
  under the thermal time constant. A failed sensor read stops the run.
- Two gates can let a high-power run through: the posture table and the power budget flag. The record names the gate that
  let the run through.
- Pattern traffic adds heat over the idle hold at the same budget. One fit under traffic read 13 K above the idle fit, with a slope 1.6 K/W steeper.
  Size the cooling and the soak limits from a fit under traffic.

## 19. The register map as data
- A tester that reads only the bytes its tests need grows a pile of constants with holes. An audit read 7 of 18 page families
  and the page showed about 25 fields of 300. Write one data table per page: byte, bits, kind, unit, the revision that defines
  it, the advertisement bit that gates it. One decode loop then covers every page, and an unread block says "not advertised".
- Gate a decode on the revision byte AND the advertisement bit. A module of an older revision advertises a page in that older
  layout. Say "not in this revision" and keep the raw bytes, so a reader sees why the page is empty.
- The lower page is its own buffer. An index of `byte - 128` into the upper page reads garbage without an error.
- Page checksums are plain sums modulo 256 over the standard's byte ranges. A fake module needs them set, or every audit fails.
- The flag bytes latch at power-up and clear on read. A pin sense before any register read shows the interrupt line low on every
  fresh insert. Read the flag bytes first, name the bits, then sense the pins. "Interrupt pending" is true only when the line
  stays low after that read. The page says "interrupt latched since insert, read the cable to clear it".
- A module does not power up in its first application, and the staged application is not the active one. Read the active
  application before you trust a lane count. A narrow application needs one data path per lane group, with the data path id as
  the lowest lane of its group; one id on all lanes is rejected.
- An active cable waits in its init state until a host-side signal arrives. On a tester with no host lanes the media flags read
  zero and prove nothing. Read the data path state before you trust a media flag. The lever is the host signal: a cross-connect
  between two cages on one board gives one end the other end's generator output, and the module leaves its init state.
- An advertisement bit says a register exists, not that it works. A feature matrix finds the hollow ones in low power: a write, a
  read-back and a restore per advertised row, or a read per monitor. The hollow ones seen: a user page that ignores writes,
  monitors that read a constant, descriptor pages that read zero. The passport flags a hollow feature; it never lists the bit as a feature.
- An advertised duration is a ceiling the host waits for, not a measurement. One module answered ten times faster than its bound.
- A module may answer a feature query with "command unknown" and still run the commands of that family. "Unknown" reads as
  "not advertised", never as a failure, and the exercise decides.
- A latched flag latches again while its condition holds. A loss-of-signal flag pulled the interrupt line low right after the
  read, because the far transmitter was still off. Read the line a second time after the undo.
- A success status on a write is not proof that the setting applied. One module answered "success" for every staged setting
  and kept its active set unchanged. Read back the active set. Then read the configuration status and the data path state.
- A low-power pin is not a hardware guard when a register can override it. Any bus master can write the override. Only the
  rail switch with verified isolation is an absolute stop. Check that no signal line back-powers the rail (§18).
- Leaving low power does not always bring the data path up. The result depends on the data path controls and the
  standard's state machine. Read the data path state; never assume it. A deactivated data path leaves the receive monitors
  blank. Read those monitors inside a pattern run or a trend run.
- A firmware update can rotate the application table. One update moved the one-lane application to the first slot and made the
  eight-lane one the second. Select an application by its whole descriptor: the host and media interface codes and the lane
  counts. Never select it by its number. Key the criteria on the firmware version.
- A firmware update on a two-ended cable is two updates. Each end carries its own image banks, and the serial is shared. The
  tool updates one end per insertion; the kit text says "swap the ends and repeat".

## 20. Pattern tests between two ends
- The checker's lock-loss flag latches from the moment the checker is enabled. Read it once after the far generator is up.
  Then reset the counters, verify the reset by a read-back, and open the gate (§23).
- A long pattern function hides three reusable steps: arm, end-of-gate statistics, disable. Arm is the setup and the clearing
  of the latched flags; the settling is judged inside the run (§23). Read back the pattern, the polarity and the enable at both
  ends before the gate. Pull them out, and a per-second trend and a far-end
  loopback cost one loop each.
- A module's bit counter may not grow at the lane rate. Check its growth law in every window before you trust a rate from it (§23).
- A far-end loopback carries the pattern while the checker reports lock loss for the whole gate and still counts. Judge a loopback
  run on a per-second lock view, never on the end flag alone.
- A link reads worse in its first seconds. One per-second rate fell tenfold inside a minute. Most of that is
  the checker lock-in. Apply the predeclared settling rule and report the settling (§23). Say which fibre or cable set the
  floor; the wrong fibre type still links.
- Judge each lane against the expected enable map. A disabled lane's bit total stays near zero. An enabled lane counts at
  the lane rate (§23). Judge on the counters: the latched lock-loss byte flickers on a marginal fibre in any short window.
- A host-side loop also acts as a far-end loopback. A module in mission mode returns its media input through the loop to
  its media output. The record names the topology. A host-loop result is not a media-link result.
- A host-side generator points at the host, not at the cable. On a two-cage board with the host lanes cross-connected it drives
  the other end's host input, and the far media-side checker measures the whole path with no host present.
- Use the module's gating timers for the window. Record the actual gate start and end. A gate that does not complete makes
  the window INCONCLUSIVE. Read the error counters beside the derived rate.

## 21. The command block and a firmware download
- A command-block command is one write of the header and payload, then one write of the command id. The check code is the one's
  complement of the sum of the header bytes and the payload; the standard's own example values confirm the formula. The status
  query fails with a range error unless its delay payload is sent. One module folds the two reply-header bytes into its check
  although the standard excludes them: write them as zero and every vendor agrees.
- A firmware download lists the host password as step 0. The entry area is in the standard, so is the status code for a
  password error, and the value is vendor-defined and clears at reset. A design note with every download step and no password step
  fails on the first real module.
- The download has two halves the standard splits on purpose: the command sequence, which a fake proves, and the vendor header,
  which only the vendor can vouch for. Every guard is a refusal: no download unless the features command advertises it, a version
  check, a header check, Run and Commit behind their own flags, a confirmation string for Commit, abort before Run on any failure,
  verify after. The first hardware run is a written gate: serial, file hash, block count.
- The download is bound by the module, not the bus. The same block count took the same time at 100 and 400 kHz: the module spends
  about a second per block after the write. A faster clock buys nothing there; it buys reads.
- Earn the faster clock with a ramp gate: open at the slow clock, read the identity there, then re-clock and run a short stress read
  with page read-back. Keep the fast clock on zero misses, fall back with the reason, and put the clock into every record header.
  Ramp after the identity read, so the first page shows before the clock steps up.
- The module features bitmap stops at the first command family. The firmware family is advertised by the firmware-features reply,
  the monitoring family by its own. A decoder that reads the bitmap alone shows no firmware command.
- The management clock at a module's 400 kHz is a functional pass when checksummed blocks, the stress read and the identity reads
  all pass. It is not a scope measurement; the instrument rows stay open.

## 22. The browser page over the bench tool
- A browser page is cheap when the tool has quiet functions with a `say` callback. Run the function in a thread, push every
  line to a queue, stream the queue as server-sent events. The live chart parses the same line the terminal prints, so the
  records stay one truth. The technician's `ask` becomes a blocking question the browser answers.
- The server carries an instance id on its heartbeat. The page treats a changed id as a restart and reloads every cached
  value. Without it an old tab shows yesterday's readings with today's clock.
- Design the screens from the questions a user brings: which cable is this, is it healthy, run the test. A first page built
  from the command line's shape shows raw JSON under empty panels. Name the tabs by task, never by skill level. Keep the raw
  record behind a toggle, and every table goes through one label module with formatters, checked by a script run in the selftest.
- A technician page never asks for a switch the product ships preset. The first real run read the engineering checklist as
  instructions, and the operator moved switches the design hides on purpose. Read the state from the pins, show a pre-check
  card, and ask only for the one fix. The strap and forced-air lines stay in the engineering path.
- A form that sends an empty string for an unscanned field turns a missing value into a mismatch. Normalise at the engine
  boundary, never in the judge. One early stop leaves one line, not one per unmeasured key.
- A long step with no visible motion reads as a hung tool. Show the step name, what it does, a timer against the expected
  duration and the last lines the engine printed, from the first event of the step.
- The run streams every event; keep them by step from the first line. Every step is then a door to its results, live and on a
  saved record. Each tab owns its result area, so a query result never follows the user to the next tab.
- A pin badge must know what a read does to the pin (§19). A clock chip shows the clock in use; the ramp detail goes to a bubble.
- Every string the page shows follows the writing standard, with a lint over the page's text sources in the selftest and the
  record round. Help bubbles come from one glossary source, and the help page is task-first: a short how-to per tab, the long
  text behind a toggle, a troubleshooting table.
- Check a page round on the real units from its worktree before the merge. The real pair exposed a pins-low badge, a reset budget
  field, a stacked chart and an undefined stop reason that the fake never showed. Measure overflow in the browser, element edge
  against card edge, never by eye. A header cell styled `nowrap` with a 1% width is right for a key column and wrong for a
  six-column table.
- A second front end on the same server costs one handler subclass and a static fallback directory. The unit lock, the job
  stream, the heartbeat and the record index stay in one module.
- A criteria file derived from one dump guesses two things a run contradicts: the data path state with no host (§19) and the
  thermal slope in the first minute, which is the step response. Derive the no-host expectation and a slope limit from the
  thermal fit, judged after the first minute. A proposed file gives inconclusive, never a fail bin; the owner confirms it by
  writing a name into it. Key the match on the firmware version.
- A record index keyed on identity needs a kind rule decided by the records that carry the evidence: a record that states the
  media technology sets the kind, a record without one never does. A flow written for two ends hides literal end names in
  prompts, loops and the judge; grep for them before the first one-end run.
- A browser's private-network rule changes by version and by the page's origin. Name the browser, its version and the test
  date with each claim. Test each browser the users run.
- A provisioning protocol over a radio link can send the network password in clear. Protect it by an authenticated,
  encrypted session. A wired serial link reduces the exposure; it does not replace the encryption.

## 23. A measurement checks its own counters: the norm, never a mode
A pattern test gives a verdict only from counters it has checked. The rules below hold for any error counter on any link.
- Counter checks are part of every measurement. No flag or mode turns them off. No name such as "high fidelity" sets them
  apart. The knobs are the window length and the gate mode.
- Keep the raw reads of every window. A read holds the monotonic time, the error and opportunity counters, the reported ratio
  and the lock flags. It also holds the temperature of both ends.
- Record the event unit of each error counter: bit, symbol, block or codeword. Record its opportunity count in the same unit.
  A bit counter gives a BER: bit errors over bits. A symbol, block or codeword counter gives an error ratio over symbols,
  blocks or codewords. Compare a ratio only with a limit in the same unit. Convert between units only by a stated model.
- Record the counting point of each counter: before or after the FEC, and before or after a gearbox. Key each limit to that
  point. A post-FEC count of zero does not prove the pre-FEC margin.
- Take the lane rate at the counting point. Read it from the standard's table for the active configuration. Include the
  encoding and FEC overhead that the counting point sees. For example, one 100G PAM4 lane runs at 53.125 GBd, which is
  106.25 Gb/s. A lane rate the tool cannot look up makes the window INCONCLUSIVE. Never divide an aggregate rate by the other
  side's lane count.
- T is the time the counters were enabled, from the verified reset to the read.
- The opportunity counter grows at the lane rate in its own unit × T. Allow the clock tolerance and the read timing slack over T.
  Any other growth law is a counter fault, and the window is INCONCLUSIVE with that reason. Test the expected linear law,
  not one named alternative. Dated example (2026-10): one module's bit counter grew as rate × T² / 2.
- Use counter deltas within one verified reset epoch. Reset the counters. Read them back near zero. Record the reset time.
  Skip the reads of the first update interval after a reset: they can hold the count from before it.
- Treat each counter on its own. A fall of either counter that no wrap explains invalidates the window.
- Know each counter's width, and whether it wraps or saturates.
- Cap every window, whatever the ratio of the window before. The cap is (modulus / 2) / (lane rate × BER_max). BER_max is the
  worst error ratio at which the checker still holds lock; take 0.5 when it is unknown. Also cap the window so that the
  opportunity counter cannot pass half its own modulus.
- Example: a 32-bit error counter on a 106.25 Gb/s lane. Its cap is about 40 ms at BER_max 0.5 and about 20 s at 1e-3. The
  first window uses the cap at BER_max. A dated tool used a first window of 0.25 s, which holds up to a BER_max of about 0.08.
- Inside the cap, shorten the next window when the ratio before calls for it. Keep a margin for a rise.
- An error count that falls while the opportunity count rises is a wrap. A step of half the modulus or more between two reads
  invalidates the window.
- A read at the saturation value makes that window and every later window INCONCLUSIVE. The saturated count is a lower bound
  on the errors.
- A proven wrap or a saturation gives a lower bound on the errors. A lower-bound ratio over the limit is a FAIL. That FAIL wins
  over the INCONCLUSIVE of the invalid window.
- Compute the ratio two ways: errors over the rate × T, and errors over the opportunity counter. Compare both with the reported
  ratio. With no reported ratio, compare the two computed values with each other. The criteria state the tolerance before the
  run. A dated tool used a factor of 1.5; use a tighter factor when the reported ratio has the resolution. A mismatch beyond
  the tolerance makes the window INCONCLUSIVE.
- Compare on a frozen read or an atomic latch. Without one, timestamp each field read. Bound the total skew of all the fields,
  and add it to the slack. A module that reports a ratio only cannot pass this check.
- A deaf checker reads zero errors on any link. Challenge the checker on every judged lane and direction before a result
  enters a release record. Known-bad paths: a pattern mismatch (PRBS31 at one end, PRBS15 at the other), an inverted polarity
  at one end, an error-injection command, a known-bad cable. Record the challenge with the run. A lane with no challenge reads
  "checker unproven". An unproven lane cannot enter a release record.
- Keep the live lock state and the latched lock loss apart. OR a clear-on-read flag over every read of the window. A lock loss
  after the settling is verdict-bearing. The criteria say whether it fails the lane or makes it INCONCLUSIVE; it is never
  dropped. The errors and opportunities of a window with a lock loss stay out of the run totals.
- The start-up settling is a rule fixed before the run, with a maximum time from the criteria. Base the rule on observable
  lock and state signals where the checker gives them. Dated example rule (2026-10): a settling window reads 10 errors or more,
  and its ratio exceeds 3 times the later median. Exclude the settling windows from the
  verdict. Report them, with the time to a stable ratio per direction. Never move the settling point after you see the data.
  Every window after the settling counts, a later burst too. Settling past the maximum makes the run INCONCLUSIVE.
- The first window after a release can hold the checker lock-in. The settling rule decides; never drop a window by default.
  Call the cause lock-in only when a control proves it.
- A window is invalid when the lane rate is unknown, the growth law fails, a counter falls unexplained, or a wrap cannot be
  excluded. It is also invalid when a counter saturates, the ratios disagree, the gate does not complete or the settling
  passes its maximum. An invalid window makes the run INCONCLUSIVE, unless a lower bound proves a FAIL.
- The verdict uses run totals per lane and per direction. A run total is the errors over the opportunities, each summed over
  the counted windows. Never average window ratios. Never judge the last window alone. Keep enough counted windows to apply
  the settling rule; the dated tool needed two.
- Judge each run total by its Poisson confidence bounds at a stated level CL. For k errors in N opportunities, the upper bound
  is χ²(CL; 2k + 2) / (2N). The lower bound is χ²(1 − CL; 2k) / (2N). PASS needs the upper bound under the limit. FAIL needs
  the lower bound over the limit. Otherwise the lane is INCONCLUSIVE. With zero errors the upper bound is −ln(1 − CL) / N,
  about 3 / N at 95 %. The bounds assume independent errors; a burst makes them optimistic, so report the window spread too.
  Set the minimum opportunity count from the limit, about 3 / limit at 95 %.
- Separate the lock-in from a temperature effect. Log the temperature per window. Claim a warm-up effect only when the ratio
  tracks the temperature after the settling windows are excluded.
- Test each unit as a sender and as a receiver. One module sent clean and received at 1e-4 on all lanes. Only a swap of the far
  unit showed which side failed.
- Rule out one cause per run. Write each one down: temperature, supply, tool, method, unit, cable direction. The list keeps
  the hunt short and a vendor question factual.
- Number every unit before a multi-unit session, on the unit and in the record. Four modules moved between three unmarked cases
  in one evening, and only the identity read told them apart.
- Check the record name before the power goes up. Refuse a record name that exists. Open the record for exclusive create.
  Write the identity first. Check the record path and every permission flag of the run before the power goes up. A run that
  fails at its record after the power-up leaves a hot unit and no record.
- A command that writes its record and then re-raises needs one handler at the command dispatch. A handler per command misses
  the next command.

## Documents generated from the software
Reason-code table, guard list (S1…Sn + override flags), supported-class table (from the criteria + FEA/thermal records), quick card (pinout +
codes). Hand prose sits outside `gen:BEGIN/END` blocks.
