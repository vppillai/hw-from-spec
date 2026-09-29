# SOFTWARE_ARCHITECTURE.md — {{PROJECT}} bring-up / test software (references/software-track.md)

## 1. Modes and states
{{operator mode / engineering mode}}; state machine: {{IDLE → IDENTIFY → TEST → REPORT}}; every state names its exit conditions.

## 2. Hardware access layer
One adapter (`{{tools/<board>_hal.py}}`): bus, GPIO, identity reads; every call replayable in `--dry-run`; the fake device for `--selftest`
feeds bytes from an iterator hooked on the exact read shape.

## 3. Safety guards (record trail)
| Guard | Protects | Level(s) printed | Override flag | Decision row | Default until the owner's nod |
|---|---|---|---|---|---|
| S1 | {{over-temperature}} | warn {{°C}} / throttle {{°C}} / cap {{°C}} — both printed | `--no-s1` | {{CC-nnn}} | optional flag that warns when omitted (rule-2 posture) |

## 4. Criteria and codes (one source each)
- Criteria: `design/test_criteria.yaml` (T-nn ↔ limits; the test plan and the technician manual quote it).
- Reason codes: `{{tools/codes.py}}`; the technician manual's table is generated from it and set-equality asserted.

## 5. Records
Identity fields (serial, firmware, board md5) into the record FIRST, gate verdicts second; PASS / FAIL / INCONCLUSIVE + code.

## 6. Owner decisions this document depends on
{{D rows: modes, refusal vs warn/throttle, criteria limits approved}}
