// workflows/blind-deep-review.js — TEMPLATE: extensive double-blind review, N specialties × (1 in-session + 2 external models) → adversarial
// verifiers → merge. Replace every double-brace placeholder (workflows/README.md lists them); delete roles you do not need. ROLE_SET 'spec'
// is the G0 round (the briefing is SPEC.md; header rows for board/package/case read MISSING by design), 'board' every later round in ee / both,
// 'mech' the M1 / M2 / case-order rounds of a mech-scope project (case_dfm + mechanical intent + hardware sourcing + gates; no electrical role).
// Generalised from the source project's final deep review (five audits, 8 roles × 3 reviewers).
export const meta = {
  name: '{{PROJECT}}-deep-review-{{ROUND}}',
  description: '{{PROJECT}} {{ROUND}} double-blind review: each specialty reviewed by one in-session reviewer and two external models, briefed only with the hand-off in a frozen worktree; every BLOCKER/MAJOR adversarially verified; merged disposition with owner rows and a generator fix list',
  phases: [{ title: 'Review' }, { title: 'Verify' }, { title: 'Merge' }],
}
const FINDINGS = { type: 'object', properties: { report_path: { type: 'string' }, model: { type: 'string' }, findings: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, area: { type: 'string' }, severity: { type: 'string', enum: ['BLOCKER', 'MAJOR', 'MINOR', 'NOTE'] }, finding: { type: 'string' }, evidence: { type: 'string' }, proposed_change: { type: 'string' } }, required: ['id', 'area', 'severity', 'finding', 'evidence', 'proposed_change'] } }, files_read: { type: 'integer' }, summary: { type: 'string' } }, required: ['report_path', 'model', 'findings', 'files_read', 'summary'] }
const VERDICT = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, verdict: { type: 'string', enum: ['CONFIRMED', 'ALREADY DECIDED', 'REFUTED', 'PARTLY', 'UNVERIFIABLE'] }, evidence: { type: 'string' }, corrected_finding: { type: 'string' }, severity: { type: 'string', enum: ['BLOCKER', 'MAJOR', 'MINOR', 'NOTE'] }, decided_by: { type: 'string' }, rev_impact: { type: 'string', enum: ['ordered revision', 'arrival bench check', 'next revision', 'record only'] } }, required: ['id', 'verdict', 'evidence', 'corrected_finding', 'severity', 'rev_impact'] } }, report_path: { type: 'string' } }, required: ['verdicts', 'report_path'] }
const MERGE = { type: 'object', properties: { report_path: { type: 'string' }, blockers: { type: 'integer' }, majors: { type: 'integer' }, minors: { type: 'integer' }, notes: { type: 'integer' }, corroborated: { type: 'integer' }, owner_decisions: { type: 'array', items: { type: 'string' } }, required_changes: { type: 'array', items: { type: 'string' } }, verdict: { type: 'string' }, summary: { type: 'string' } }, required: ['report_path', 'blockers', 'majors', 'minors', 'notes', 'corroborated', 'owner_decisions', 'required_changes', 'verdict', 'summary'] }

const WT = '{{FROZEN_WORKTREE}}'        // detached `git worktree add` at the reviewed commit; read-only for reviewers
const MAIN = '{{REPO_ROOT}}'            // live repo: reports are written to docs/reviews/ here
const HANDOFF = '{{HANDOFF_DOC}}'       // e.g. docs/reviews/REVIEW_HANDOFF.md — the ONLY briefing (header from scripts/handoff_header.py)
const TAG = '{{REVIEW_TAG}}'            // report file prefix, e.g. R7REVIEW
const MERGED = '{{MERGED_REPORT}}'      // e.g. docs/reviews/final_review_r7_merged.md
const PREVIOUS = '{{PREVIOUS_MERGED_REPORTS}}'   // comma-separated earlier merged reports to compare against ('' for the first round)
const TODAY = '{{DATE}}'
const KPY = '{{CAD_PYTHON}}'            // the CAD's Python for parsing board/schematic files (or 'grep')

// One entry per specialty: key (file-name safe), title, brief (what to look at — files, nets, decisions; numbers come from the hand-off, not from here).
const ROLE_SET = '{{ROLE_SET}}'          // 'spec' at G0 (SPEC.md is the artefact), 'board' at G1 / G2 / order, 'mech' at M1 / M2 / case order (mech scope)
const SPEC_ROLES = [
  { key: 'spec', title: 'Spec coherence: requirements, interfaces, numbers that must agree, VERIFY items', brief: '{{BRIEF_SPEC}}' },
  { key: 'parts', title: 'Parts and sourcing: every named part fetchable, tags, alternates, stock for the run', brief: '{{BRIEF_PARTS}}' },
  { key: 'mech', title: 'Mechanical intent: envelope, connectors, case concept, thermal', brief: '{{BRIEF_MECH}}' },
  { key: 'test', title: 'Test plan and bring-up: every requirement has a check, criteria measurable', brief: '{{BRIEF_TEST}}' },
]
const BOARD_ROLES = [
  { key: 'power', title: 'Power & analog', brief: '{{BRIEF_POWER}}' },
  { key: 'digital', title: 'Digital, interfaces, firmware-facing pins', brief: '{{BRIEF_DIGITAL}}' },
  { key: 'layout', title: 'Layout, signal integrity and fab DFM', brief: '{{BRIEF_LAYOUT}}' },
  { key: 'fab', title: 'Fab package, BOM/CPL and the order', brief: '{{BRIEF_FAB}}' },
  { key: 'mech', title: 'Mechanical, thermal and the case', brief: '{{BRIEF_MECH}}' },
  { key: 'case_dfm', title: 'Printed-enclosure DFM: walls / voids / wedges / opposing faces vs print_targets, inserts and retention present in the mesh, tolerance stack, closed rims, orientation (checklist = templates/CENSUS_GATE_ROWS.md + references/dfm-printed-enclosure.md §1; verifier re-runs scripts/thin_wall_census.py --target on the frozen STLs)', brief: '{{BRIEF_CASE_DFM}}' },
  { key: 'silk', title: 'Silkscreen, UX and operator documentation', brief: '{{BRIEF_SILK}}' },
  { key: 'software', title: 'Software, bring-up and test plan', brief: '{{BRIEF_SOFTWARE}}' },
  { key: 'coherence', title: 'Requirements, decisions and traceability coherence', brief: '{{BRIEF_COHERENCE}}' },
  { key: 'gates', title: 'Gates, generators and release tooling', brief: '{{BRIEF_GATES}}' },
]
const MECH_ROLES = [
  BOARD_ROLES.find(r => r.key === 'case_dfm'),
  { key: 'mech', title: 'Mechanical intent: envelope, fit input of record (STEP / envelope md5 + tag), clearances, retention, assembly', brief: '{{BRIEF_MECH}}' },
  { key: 'parts', title: 'Bought hardware: inserts, magnets, feet, screws, adhesives — every line [V] on the manufacturer page + TDS', brief: '{{BRIEF_PARTS}}' },
  { key: 'gates', title: 'Gates, generators, census + print-DFM records and the kit', brief: '{{BRIEF_GATES}}' },
]
const ROLES = ROLE_SET === 'spec' ? SPEC_ROLES : ROLE_SET === 'mech' ? MECH_ROLES : BOARD_ROLES

// external models available to the Cursor agent CLI (`agent --list-models`): AT LEAST TWO distinct entries; role i gets MODELS[i] and MODELS[i+1]
// (cyclic), so every role sees two different models whatever the list length
const MODELS = [{{EXTERNAL_MODELS}}]           // e.g. 'gpt-5.3-codex-xhigh', 'claude-opus-5-thinking-high', 'gemini-3.7-flash-high'
const FALLBACK = '{{FALLBACK_MODEL}}'
if (new Set(MODELS).size < 2) throw new Error(`EXTERNAL_MODELS needs at least two distinct models (got ${JSON.stringify(MODELS)}) — two vendors per role`)
const pair = (i) => { const n = MODELS.length, m1 = MODELS[i % n], m2 = MODELS[(i + 1) % n]; if (m1 === m2) throw new Error(`role ${i}: both models are ${m1}`); return { m1, m2 } }

const COMMON = `Today is ${TODAY}. {{ROUND_CONTEXT}} ${ROLE_SET === 'spec' ? 'This is the G0 SPEC review: the artefact is SPEC.md (plus docs/parts/PARTS_VERIFICATION.md, the test plan, the case concept); there is no board, no package and no case yet — the identity header says MISSING for those by design. Judge whether the spec is complete, coherent and buildable, and list every VERIFY item (a value or claim resting on a datasheet or standard not yet read).' : ''} BLINDNESS: your ONLY briefing is ${WT}/${HANDOFF} (self-contained) plus read access to the frozen worktree ${WT} (a detached checkout; never write there). Do NOT read any file named docs/reviews/${TAG}_* or any earlier merged review (other reviewers' output), and do not read the live repo ${MAIN} except to WRITE your report. Every finding must cite file + line/coordinate/refdes/net from the worktree and say how you checked it (grep, a number you computed, an image you read). Severity: BLOCKER = would make the board not work or not build; MAJOR = a real functional/robustness/DFM risk to fix before ordering; MINOR = worth fixing, not blocking; NOTE = observation. Be exhaustive within your specialty; prefer many concrete findings over prose; do not repeat what the hand-off lists as known/open unless you disagree with its disposition (say so and why). Finish with a 'files_read' count and a 10-line summary.`

const inSession = (r) => agent(`${COMMON}
You are the IN-SESSION blind reviewer for the specialty **${r.title}**. Scope: ${r.brief}
Read the hand-off first (all of it), then the files it points to for your specialty in ${WT} (CAD files can be parsed with ${KPY} or grep; images with the Read tool). Write your report to ${MAIN}/docs/reviews/${TAG}_${r.key}_claude.md (markdown: header with role/model/date/files read, then one table row per finding: id ${r.key.toUpperCase()}-Cnn | severity | finding | evidence | proposed change). Return the findings in the schema (model = 'claude-in-session').`, { label: `review:${r.key}:claude`, phase: 'Review', schema: FINDINGS, effort: 'high' })

const external = (r, model, n) => agent(`${COMMON}
You are the WRAPPER for an EXTERNAL blind reviewer: model **${model}** via the Cursor agent CLI. Run from the frozen worktree so the model can only see the snapshot:
  cd ${WT} && agent -p --mode ask --model ${model} --output-format text "<PROMPT>" > ${MAIN}/docs/reviews/${TAG}_${r.key}_${n}_${model}.md 2> ${MAIN}/docs/reviews/${TAG}_${r.key}_${n}_${model}.stderr.log
where <PROMPT> (under 30 kB; do NOT paste the hand-off, the model reads it) is: 'You are a senior hardware reviewer doing a BLIND review of {{PROJECT_ONE_LINE}}. Read ${HANDOFF} in this directory completely first — it is your only briefing — then open the files it points to for the specialty "${r.title}": ${r.brief} You may read any file in this directory; you may not write anything. Report ONLY a markdown table with columns ID | Severity (BLOCKER/MAJOR/MINOR/NOTE) | Area | Finding | Evidence (file + line/coordinate/refdes/net and how you checked) | Proposed change, ids ${r.key.toUpperCase()}-E${n}-nn, at least 15 rows if you can find them and as many as are real, followed by "Files read: N" and a 10-line summary. Do not invent facts; if you cannot open a file say so.'
macOS has no timeout command: launch the CLI in the background with an ampersand, record the PID, poll with until-loops (≤ 8 min per Bash call, up to 75 minutes total). When it exits: 'test -s' the report — an EMPTY or error-only report is a failure: retry once with --model ${FALLBACK} (note the substitution in the report header); if that is empty too, write the failure (exit code, stderr tail) into the report and return zero findings. Do NOT judge the design yourself and do not add findings of your own. Parse the model's table into the schema (model = the model that actually produced the report; files_read from its text or 0).`, { label: `review:${r.key}:${model}`, phase: 'Review', schema: FINDINGS, effort: 'medium' })

const verify = (r, reviews) => {
  const all = reviews.filter(Boolean).flatMap(v => v.findings.map(f => ({ ...f, model: v.model })))
  const toVerify = all                                                        // 0.10.0: EVERY finding passes the verifier (the record pass marks ALREADY DECIDED items; nothing is applied without its row)
  log(`${r.key}: ${all.length} findings from ${reviews.filter(Boolean).length} reviewers; verifying all of them`)
  if (!toVerify.length) return Promise.resolve({ role: r.key, all, verdicts: [] })
  return agent(`Today is ${TODAY}. Adversarial VERIFIER for the specialty **${r.title}** — the one reader WITH record access: ${WT}/docs/governance/DECISIONS.md, KNOWN_ISSUES.md, BLOCKERS.md, SPEC.md and docs/spec_sections/SPEC_ERRATA.md, the test plan, the netlist / mesh of record (the reviewers saw none of these). Default to REFUTED unless the evidence in the frozen worktree ${WT} supports the claim: for each finding below, open the cited files (parse CAD files with ${KPY} or grep, read images with Read, compute the number — a number about copper carries the script that produced it; a netlist claim is re-exported and parsed by you, a mesh claim re-measured with trimesh; convert coordinate frames before calling a site missing), state exactly what you found, and return CONFIRMED / ALREADY DECIDED (name the row in decided_by and say whether its number still holds) / REFUTED / PARTLY / UNVERIFIABLE with a corrected finding text, your severity (downgrade freely; upgrade only with evidence) and rev_impact: 'ordered revision' (changes what is being built), 'arrival bench check' (a row for ARRIVAL_CHECKLIST.md), 'next revision', or 'record only'. Mark duplicates across reviewers (same defect) by giving them the same corrected_finding text. Write ${MAIN}/docs/reviews/${TAG}_${r.key}_verify.md with one row per finding. Findings: ${JSON.stringify(toVerify).slice(0, 60000)}`, { label: `verify:${r.key}`, phase: 'Verify', schema: VERDICT, effort: 'high' }).then(v => ({ role: r.key, all, verdicts: v ? v.verdicts : [] }))
}

const results = await pipeline(
  ROLES.map((r, i) => ({ r, ...pair(i) })),
  ({ r, m1, m2 }) => parallel([() => inSession(r), () => external(r, m1, 1), () => external(r, m2, 2)]).then(rs => ({ r, rs })),
  ({ r, rs }) => verify(r, rs),
)

phase('Merge')
const merged = await agent(`Today is ${TODAY}. MERGE the {{PROJECT}} {{ROUND}} double-blind review into ${MAIN}/${MERGED}. ${PREVIOUS ? `Compare FIRST with the earlier merged reports (${PREVIOUS}): state per earlier REQUIRED / OWNER item CLOSED / STILL OPEN / NEW with the verifier evidence.` : ''} Inputs: the per-role reviews and verifier verdicts (read every ${MAIN}/docs/reviews/${TAG}_*.md; structured data: ${JSON.stringify(results.filter(Boolean).map(x => ({ role: x.role, n: x.all.length, verdicts: x.verdicts }))).slice(0, 80000)}). Method: (1) apply the verifier verdicts — REFUTED findings go to a 'rejected' table with the reason, ALREADY DECIDED ones to a 'decided' table citing decided_by (no new row), PARTLY/CONFIRMED keep the corrected text, severity and rev_impact; every item with rev_impact 'arrival bench check' is listed as a proposed design/arrival_checklist.yaml row; (2) dedupe across roles and models by defect (same file/net/refdes/mechanism) and record the corroboration count and which models found it — a corroboration matrix (finding × model); (3) classify each surviving item: REQUIRED generator/YAML change before ordering (file + exact change), OWNER decision (write the proposed decision-log row text, numbered from the next free agent ID — grep the log first — one bundle row if many), DOCUMENT (test plan / docs), ACCEPT (with reason); (4) an explicit VERDICT: '{{VERDICT_OPTIONS}}' — with the three strongest reasons; (5) reviewer quality: findings per model, refuted rate and already-decided rate per model, empty/failed runs; (6) counts. Do not change any design file. Commit with 'cd ${MAIN} && git add -- docs/reviews/${TAG}_*.md docs/reviews/${TAG}_*.stderr.log ${MERGED} && git commit -m "{{ROUND}} double-blind review: ${ROLES.length} specialties x 3 reviewers, verified and merged" -- docs/reviews/${TAG}_*.md docs/reviews/${TAG}_*.stderr.log ${MERGED}' (explicit paths only). Return the schema.`, { label: 'merge', phase: 'Merge', schema: MERGE, effort: 'high' })
return { results: results.filter(Boolean).map(x => ({ role: x.role, findings: x.all.length, verified: x.verdicts.length })), merged }
