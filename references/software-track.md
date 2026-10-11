# software-track.md — bring-up tool, package, criteria, codes, selftests

The software exists before the hardware does. So you build it to run without hardware, and it generates the documents that describe it.
Sections 1 and 2 give the order and the selftest pattern. Sections 3 to 13 hold the rules a package round proved. Each rule carries its
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
9. **Spec revision**: after the review round, revise the architecture note to the code as a dated revision (§10).
10. **Hardware phase**: the first physical phase waits for boards. Name what the first boards will hit in the record before they arrive (§13).

## 2. Selftest pattern
- Fake sensor or EEPROM from a list of (offset, length) → bytes. Assert the identity and page reads keep their real values while the ramp
  advances per health sample.
- One `--selftest` run in the adopt gates. It needs no hardware and no network.
- The selftest patches `time.sleep` on module and instance attributes, never on a module global of the tool. A global of the tool is not
  visible from a package.

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

## Documents generated from the software
Reason-code table, guard list (S1…Sn + override flags), supported-class table (from the criteria + FEA/thermal records), quick card (pinout +
codes). Hand prose sits outside `gen:BEGIN/END` blocks.
