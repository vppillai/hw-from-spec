// workflows/delta-audit.js — TEMPLATE: a DELTA audit after a bounded change (a copper hop, a tooling round, a document set): only the specialties
// the change can touch, briefed with the round's CLAIMS list, verifying claims against the frozen worktree rather than re-reviewing everything.
// Same machinery as blind-deep-review.js (roles × in-session + external × verifier → merge); the differences are the role filter, the claims
// paragraph and the merge instruction to compare with the previous merged report item by item.
export const meta = {
  name: '{{PROJECT}}-delta-audit-{{ROUND}}',
  description: '{{PROJECT}} {{ROUND}} delta audit: the specialties the change can affect, each reviewed blind by one in-session reviewer and two external models against the round claims; BLOCKER/MAJOR verified; merged against the previous audit',
  phases: [{ title: 'Review' }, { title: 'Verify' }, { title: 'Merge' }],
}
const FINDINGS = { type: 'object', properties: { report_path: { type: 'string' }, model: { type: 'string' }, findings: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, area: { type: 'string' }, severity: { type: 'string', enum: ['BLOCKER', 'MAJOR', 'MINOR', 'NOTE'] }, finding: { type: 'string' }, evidence: { type: 'string' }, proposed_change: { type: 'string' } }, required: ['id', 'area', 'severity', 'finding', 'evidence', 'proposed_change'] } }, files_read: { type: 'integer' }, summary: { type: 'string' } }, required: ['report_path', 'model', 'findings', 'files_read', 'summary'] }
const VERDICT = { type: 'object', properties: { verdicts: { type: 'array', items: { type: 'object', properties: { id: { type: 'string' }, verdict: { type: 'string', enum: ['CONFIRMED', 'REFUTED', 'PARTLY', 'UNVERIFIABLE'] }, evidence: { type: 'string' }, corrected_finding: { type: 'string' }, severity: { type: 'string', enum: ['BLOCKER', 'MAJOR', 'MINOR', 'NOTE'] } }, required: ['id', 'verdict', 'evidence', 'corrected_finding', 'severity'] } }, report_path: { type: 'string' } }, required: ['verdicts', 'report_path'] }
const MERGE = { type: 'object', properties: { report_path: { type: 'string' }, blockers: { type: 'integer' }, majors: { type: 'integer' }, minors: { type: 'integer' }, notes: { type: 'integer' }, claims_confirmed: { type: 'integer' }, claims_not_confirmed: { type: 'integer' }, owner_decisions: { type: 'array', items: { type: 'string' } }, required_changes: { type: 'array', items: { type: 'string' } }, verdict: { type: 'string' }, summary: { type: 'string' } }, required: ['report_path', 'blockers', 'majors', 'minors', 'notes', 'claims_confirmed', 'claims_not_confirmed', 'owner_decisions', 'required_changes', 'verdict', 'summary'] }

const WT = '{{FROZEN_WORKTREE}}', MAIN = '{{REPO_ROOT}}', HANDOFF = '{{HANDOFF_DOC}}', TAG = '{{REVIEW_TAG}}', MERGED = '{{MERGED_REPORT}}', TODAY = '{{DATE}}', KPY = '{{CAD_PYTHON}}'
const PREVIOUS = '{{PREVIOUS_MERGED_REPORT}}'   // the audit this delta is measured against (its REQUIRED list = the claims verified now)

// What changed since PREVIOUS, one numbered claim each with the commit that made it — the hand-off carries the same list with evidence paths.
const CLAIMS = `{{CLAIMS}}`   // e.g. "(1) the DRC now enforces net classes via explicit assignments + a canary rule (commit …); (2) copper re-laid in place at …; (3) release tooling: …"

const ALL_ROLES = [
  { key: 'power', title: 'Power & analog', brief: '{{BRIEF_POWER}}' },
  { key: 'layout', title: 'Layout, signal integrity and fab DFM', brief: '{{BRIEF_LAYOUT}}' },
  { key: 'fab', title: 'Fab package, BOM/CPL and the order', brief: '{{BRIEF_FAB}}' },
  { key: 'gates', title: 'Gates, generators and release tooling', brief: '{{BRIEF_GATES}}' },
  { key: 'mech', title: 'Mechanical, thermal and the case', brief: '{{BRIEF_MECH}}' },
  { key: 'docs', title: 'Document set: manuals, SOPs, compliance statements', brief: '{{BRIEF_DOCS}}' },
]
const ROLES = ALL_ROLES.filter(r => [{{DELTA_ROLE_KEYS}}].includes(r.key))   // e.g. 'layout', 'fab', 'gates'
const MODELS = [{{EXTERNAL_MODELS}}], FALLBACK = '{{FALLBACK_MODEL}}'   // at least two distinct models; role i gets MODELS[i], MODELS[i+1] (cyclic)
if (new Set(MODELS).size < 2) throw new Error(`EXTERNAL_MODELS needs at least two distinct models (got ${JSON.stringify(MODELS)}) — two vendors per role`)
const pair = (i) => { const n = MODELS.length, m1 = MODELS[i % n], m2 = MODELS[(i + 1) % n]; if (m1 === m2) throw new Error(`role ${i}: both models are ${m1}`); return { m1, m2 } }

const COMMON = `Today is ${TODAY}. DELTA AUDIT {{ROUND}}: since the previous audit (${PREVIOUS}) the following changed — ${CLAIMS}. Concentrate on VERIFYING these claims against the frozen worktree (the hand-off lists each claim with its commit and evidence path), on the items applied ahead of the owner's nod (hand-off nod section), and on the rebuilt package/order chain; do not re-litigate earlier findings that are unchanged unless the change made them worse. BLINDNESS: your ONLY briefing is ${WT}/${HANDOFF} plus read access to ${WT} (detached checkout; never write there). Do NOT read docs/reviews/${TAG}_* or any merged review newer than ${PREVIOUS}; do not read the live repo ${MAIN} except to WRITE your report. Every finding cites file + line/coordinate/refdes/net and how you checked it. Severity: BLOCKER / MAJOR / MINOR / NOTE as in the hand-off. Finish with 'files_read' and a 10-line summary that states per claim CONFIRMED / NOT CONFIRMED / PARTLY.`

const inSession = (r) => agent(`${COMMON}
You are the IN-SESSION blind reviewer for **${r.title}**. Scope: ${r.brief}
Read the hand-off first, then the files it points to in ${WT} (parse CAD files with ${KPY} or grep; images with Read). Write ${MAIN}/docs/reviews/${TAG}_${r.key}_claude.md (header + one table row per finding: id ${r.key.toUpperCase()}-Cnn | severity | finding | evidence | proposed change). Return the schema (model = 'claude-in-session').`, { label: `review:${r.key}:claude`, phase: 'Review', schema: FINDINGS, effort: 'high' })

const external = (r, model, n) => agent(`${COMMON}
You are the WRAPPER for an EXTERNAL blind reviewer: model **${model}** via the Cursor agent CLI, run from the frozen worktree:
  cd ${WT} && agent -p --mode ask --model ${model} --output-format text "<PROMPT>" > ${MAIN}/docs/reviews/${TAG}_${r.key}_${n}_${model}.md 2> ${MAIN}/docs/reviews/${TAG}_${r.key}_${n}_${model}.stderr.log
<PROMPT> (under 30 kB, do not paste the hand-off): 'You are a senior hardware reviewer doing a BLIND DELTA audit of {{PROJECT_ONE_LINE}}. Read ${HANDOFF} completely first — it is your only briefing and lists the claims of this round — then verify each claim and review the specialty "${r.title}": ${r.brief} You may read any file here; you may not write. Report ONLY a markdown table ID | Severity | Area | Finding | Evidence (file + line/coordinate/refdes/net and how you checked) | Proposed change, ids ${r.key.toUpperCase()}-E${n}-nn, then "Files read: N" and a 10-line summary with CONFIRMED / NOT CONFIRMED per claim.'
No timeout on macOS: background + PID + until-loops (≤ 8 min per call, ≤ 75 min). Empty report = failure: retry once with --model ${FALLBACK} (note it), else write the failure into the report and return zero findings. Never judge the design yourself. Parse the table into the schema.`, { label: `review:${r.key}:${model}`, phase: 'Review', schema: FINDINGS, effort: 'medium' })

const verify = (r, reviews) => {
  const all = reviews.filter(Boolean).flatMap(v => v.findings.map(f => ({ ...f, model: v.model })))
  const toVerify = all.filter(f => f.severity === 'BLOCKER' || f.severity === 'MAJOR')
  if (!toVerify.length) return Promise.resolve({ role: r.key, all, verdicts: [] })
  return agent(`Today is ${TODAY}. Adversarial VERIFIER for **${r.title}** (delta audit {{ROUND}}). Default REFUTED unless ${WT} supports the claim; open the cited files, compute the number, read the image; CONFIRMED / REFUTED / PARTLY / UNVERIFIABLE with corrected text and severity; mark duplicates by identical corrected_finding. Write ${MAIN}/docs/reviews/${TAG}_${r.key}_verify.md. Findings: ${JSON.stringify(toVerify).slice(0, 60000)}`, { label: `verify:${r.key}`, phase: 'Verify', schema: VERDICT, effort: 'high' }).then(v => ({ role: r.key, all, verdicts: v ? v.verdicts : [] }))
}

const results = await pipeline(
  ROLES.map((r, i) => ({ r, ...pair(i) })),
  ({ r, m1, m2 }) => parallel([() => inSession(r), () => external(r, m1, 1), () => external(r, m2, 2)]).then(rs => ({ r, rs })),
  ({ r, rs }) => verify(r, rs),
)

phase('Merge')
const merged = await agent(`Today is ${TODAY}. MERGE delta audit {{ROUND}} into ${MAIN}/${MERGED}. Compare FIRST with ${PREVIOUS}: for each of its REQUIRED items and owner rows state CONFIRMED / NOT CONFIRMED / PARTLY with the verifier evidence; for each claim of this round (${CLAIMS}) the same. Inputs: every ${MAIN}/docs/reviews/${TAG}_*.md and ${JSON.stringify(results.filter(Boolean).map(x => ({ role: x.role, n: x.all.length, verdicts: x.verdicts }))).slice(0, 80000)}. Method as in the deep review: verifier verdicts applied (REFUTED → rejected table), dedupe by defect with a corroboration matrix, classify REQUIRED / OWNER (proposed row text, next free agent ID) / DOCUMENT / ACCEPT, explicit VERDICT ('{{VERDICT_OPTIONS}}') with three reasons, reviewer quality, counts. No design file changes. Commit the review files with explicit paths. Return the schema.`, { label: 'merge', phase: 'Merge', schema: MERGE, effort: 'high' })
return { results: results.filter(Boolean).map(x => ({ role: x.role, findings: x.all.length, verified: x.verdicts.length })), merged }
