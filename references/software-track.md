# software-track.md — bring-up tool, architecture, criteria, codes, selftests

The software exists before the hardware does, so it is built to be testable without it and to generate the documents that describe it.

## Order
1. **Bring-up tool** (`tools/<board>_bringup.py`): every hardware access behind one adapter (bus, GPIO, identity reads). Flags: `--list`, `--dry-run <cmd>`
   (prints the transactions it would do), `--selftest`. The selftest uses a fake device from an iterator hooked on the exact read shape the poll uses.
   Time-driven paths are testable by swapping `time.sleep` for a no-op in `try/finally`. Driver notes (which OS binds a serial driver, what `Access denied` means)
   in `90-log/ENV.md` with the hardware step OPEN until a unit exists.
2. **Architecture note** (`20-design/SOFTWARE_ARCHITECTURE.md`): states, safety guards S1…Sn with their record trail, override flags, what each guard
   protects (a fixed cap vs warn/throttle levels — print both at release, or the operator never sees a WARN).
3. **Criteria as YAML** (`20-design/test_criteria.yaml`): every test T-nn with limits, the tool reads them; the test plan and the technician manual
   quote them from the same file (one source). **Who decides**: the agent drafts every limit from the spec with its source in a CC row. The owner
   approves the set (a D row the yaml header cites) before the software refuses or throttles on it. The refuse-vs-warn posture per guard is an
   owner answer at kickoff (`references/kickoff-questionnaire.md` §software).
4. **Result verdicts**: PASS / FAIL / **INCONCLUSIVE** with a reason code from one code list (`tools/codes.py` or a yaml). The technician manual's
   code table is GENERATED from that list. A generator check asserts set equality (every code the software can emit is documented).
5. **Records**: identity fields (serial, firmware, board md5) copied into the record FIRST, gates second — a refusal must still be attributable.
6. **Rule-2 posture**: a gate the owner has not nodded yet ships as an optional flag that warns when omitted; the nod is a one-line
   `required=True`.
7. **udev / driver rules** shipped with the tool; the first-plug hazard (default UART mode driving pins for ms) documented and mitigated.

## Selftest pattern
- Fake sensor/EEPROM from a list of (offset, length) → bytes; assert the identity and page reads keep their real values while the ramp advances per
  health sample.
- One `--selftest` run in the adopt gates; it needs no hardware and no network.

## Documents generated from the software
Reason-code table, guard list (S1…Sn + override flags), supported-class table (from the criteria + FEA/thermal records), quick card (pinout +
codes). Hand prose sits outside `gen:BEGIN/END` blocks.
