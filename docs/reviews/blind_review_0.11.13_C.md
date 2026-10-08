<!-- blind reviewer C: GPT-5.6 Terra (GitHub Copilot CLI); artefact + checklist only; 2026-10-08 -->
# Blind review C — hw-from-spec 0.11.13 (cold user, both scopes)
## Setup (what you ran, where)
MEASURED: Read only `/private/tmp/claude-502/-Users-vpillai-temp-aec-tester/d3f10fc6-10e5-4769-b4fd-2330e8da1aae/scratchpad/review_0113/skill` (excluding `docs/reviews`); working project is `/private/tmp/claude-502/-Users-vpillai-temp-aec-tester/d3f10fc6-10e5-4769-b4fd-2330e8da1aae/scratchpad/review_0113/work_C`; Python is `/Users/vpillai/temp/hw-from-spec/.venv/bin/python` (3.13.12). No OpenSCAD, slicer, KiCad, internet, or git mutation will be used.

MEASURED: Ran README step-4 copy/scaffold blocks for `both`, `ee`, and `mech`; every `scripts/*.{py,sh} --selftest` from a fresh project and from the skill directory; project smoke; documented evals; default/project/relative-file/marker/report style-lint cases; and negative unapproved-gate/kickoff cases.

## Findings
| id | sev | where | what | evidence | suggested fix |
|---|---|---|---|---|---|
| C-1 | BLOCKER | `templates/90-log/GATES.md:29-30` | The `both` scaffold drops M1 and M2, although `both` requires the case pipeline and its M1/M2 approvals. The gate checker therefore refuses M1 permanently. | **MEASURED:** the prescribed `both` scaffold reported 27 lines dropped; its output `scripts/gate_check.py M1` says `NOT approved ... no row`. **JUDGMENT:** no owner approval can satisfy a missing row. | Tag M1 and M2 rows `{{mech,both}}`; add a both-scope scaffold/gate-check regression. |
| C-2 | MAJOR | `evals/run_evals.py:31`; `scripts/clone_gate.sh:19` | README’s documented eval command fails: eval 3 starts `clone_gate.sh --selftest` in a temp directory without `PYTHON`, so it cannot find the caller venv. | **MEASURED:** `.venv/bin/python vendor/hw-from-spec/evals/run_evals.py` exits 1: `[FAIL] 3 ... rc 1: selftest FAILED: regen copy-back`; the same clone selftest exits 1 in `mktemp` and 0 from the project root. | Export `PYTHON=$PY` in eval checks, or have clone selftest use its script-relative interpreter. Add the eval as a release test. |
| C-3 | MAJOR | `references/kickoff-questionnaire.md:70-73`; `templates/10-spec/KICKOFF_ANSWERS.md:19` | B3’s recommended answer leaves `N` undefined while the required answer template repeats it. The text only says to state N in the spec; it gives no value or selection method. | **MEASURED:** B3 says `pairs < N cm`; template answer is `{{none, pairs < N cm}}`; `project.py kickoff --check` reports that exact unfilled B3 slot. **JUDGMENT:** a cold user cannot accept this recommended answer literally. | Specify a recommended maximum length or add a bounded calculation/selection question with a landing key. |
| C-4 | MINOR | `README.md:46` | The promise that every generic script has read-only `--check` is inaccurate. `print_dfm.py` and `gate_check.py` reject that flag. | **MEASURED:** both `python scripts/print_dfm.py --check` and `.../gate_check.py --check` exit 2; gate_check says `unrecognized arguments: --check`. **JUDGMENT:** users cannot use the advertised uniform command contract. | Qualify the claim, or implement documented read-only check modes where appropriate. |

## Checked and correct
- MEASURED: README's template copy/scaffold block creates the scope folders and files for all three scopes. `ee` keeps G0/G1/G2/board-order/Release; `mech` keeps G0/M1/M2/case-order/Release.
- MEASURED: All 28 Python and shell script selftests pass from both required locations when shell scripts receive the documented project interpreter (`PYTHON=/Users/vpillai/temp/hw-from-spec/.venv/bin/python`).
- MEASURED: `vendor/hw-from-spec/smoke/run_smoke.sh` exits 0 from the fresh project and exercises positive and negative gate enforcement.
- MEASURED: `scripts/gate_check.py G0` exits 1 with an empty owner cell. The template and SKILL clearly assign approval-cell and release-line authorship to the owner.
- MEASURED: `scripts/style_lint.py` on default skill files exits 0 (46 files). `--project ROOT` flags a prohibited word, `<!-- style: ok -->` suppresses it, a relative argument resolves from cwd, and `--report` exits 0.
- MEASURED: The questionnaire has ordered scope-tagged batches 0–11, no more than four questions per batch, and inspected questions provide marked recommendations plus alternatives.

## Coverage limits (what you could not run or read)
MEASURED: Not reading `SKILL_DIR/docs/reviews/*` as required. Hardware application checks requiring OpenSCAD, a slicer, or KiCad are out of scope by instruction.

MEASURED: No actual product specification, owner identity/decisions, vendor data, or tool paths were supplied. Therefore the copied templates intentionally retain 243 (`both`), 177 (`ee`), and 175 (`mech`) slots and a genuine day-one project cannot reach the green gate list. `style_lint --report` reports 548 sentences over 25 words, although its current enforced cap is 40 and its default lint passes.

MEASURED: Counts — BLOCKER: 1; MAJOR: 2; MINOR: 1; NOTE: 0.
