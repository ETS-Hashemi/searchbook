export const meta = {
  name: 'searchbook-chapter-loop',
  description: 'Write or complete textbook chapters (session model), peer-review and revise on the review model until accepted',
  phases: [
    { title: 'Write', detail: 'author writes or completes the chapter; compile-checked; code self-test passing; 12-16 pages' },
    { title: 'Review', detail: 'independent reviewer applies the STYLE_GUIDE.md rubric; report saved to reviews/' },
    { title: 'Revise', detail: 'reviser applies every required change, rebuilds, re-runs code, responds in the review file' },
  ],
}

const ROOT = '/home/user/searchbook'
const ITEMS = args.items
// Authors keep the session model (Fable) unless args.writeModel says otherwise; reviewers and
// revisers run on args.reviewModel (default Opus) so the accuracy-critical writing stays on the
// strongest model while the review loop spends the cheaper quota.
const WRITE_OPTS = args.writeModel ? { model: args.writeModel } : {}
const REVIEW_MODEL = args.reviewModel || 'opus'
const MAX_ROUNDS = args.maxRounds || 3   // round 3 only if round 2 is still "Major revision"

const REPORT = {
  type: 'object',
  properties: {
    status: { type: 'string', enum: ['done', 'partial', 'failed'] },
    pages: { type: 'number' },
    notes: { type: 'string' },
  },
  required: ['status', 'notes'],
}
const REVIEW = {
  type: 'object',
  properties: {
    verdict: { type: 'string', enum: ['Accept', 'Minor revision', 'Major revision'] },
    required_changes: {
      type: 'array',
      items: {
        type: 'object',
        properties: {
          location: { type: 'string' },
          problem: { type: 'string' },
          fix: { type: 'string' },
          category: { type: 'string' },
        },
        required: ['location', 'problem', 'fix', 'category'],
      },
    },
    suggestions: { type: 'array', items: { type: 'string' } },
    keep: { type: 'string' },
  },
  required: ['verdict', 'required_changes', 'keep'],
}

async function tryAgent(prompt, opts, attempts) {
  const n = attempts || 2
  for (let i = 0; i < n; i++) {
    const r = await agent(prompt, { ...opts, label: opts.label + (i ? ':retry' + i : '') })
    if (r) return r
    log(opts.label + ': no result on attempt ' + (i + 1) + (i + 1 < n ? ', retrying' : ', giving up'))
  }
  return null
}

function file(it) { return 'Overleaf/' + it.dir + '/' + it.stem + '.tex' }

function writePrompt(it) {
  const assets = it.assets ? ` Existing assets you must reuse where they fit: ${it.assets}.` : ''
  const appendix = it.id === 'appB'
    ? ' This item is an appendix: no code file and no solutions file; it does need Overleaf/appendices/glossary/appB-terms.tex and figures in Overleaf/figures/appB/.'
    : ''
  return `You are the author of ${it.title} of the textbook in ${ROOT}. Read ${ROOT}/docs/writer-brief.md and follow it exactly (it points to STYLE_GUIDE.md, docs/chapter-template.tex, docs/core-idea.txt, Overleaf/searchbook.sty and docs/style-test.tex). Your detailed specification is ${ROOT}/docs/specs/${it.id}.md: every "must cover" item in it is mandatory.${appendix}
FIRST check the target file ${file(it)}: if it already contains a draft (anything beyond the 4-line placeholder), read it and COMPLETE or FIX it - keep what is good, do not start over; also check for existing figures in Overleaf/figures/${it.id}/, code Overleaf/code/${it.id}_*.py, and solutions/glossary files under Overleaf/appendices/, and reuse them.${assets} Chapters 1-5 and 10 are complete; read Overleaf/chapters/ch04-astar.tex once for the house style and reuse its notation. Other chapters are being written in parallel: refer to them only by chapter labels (ch:chNN, ch:appX) as listed in the brief, never by section labels.
LENGTH IS A HARD CONSTRAINT: the chapter must be 12-16 pages of chapter text (at most about 1100 lines of LaTeX in the chapter file, excluding figure files). A longer draft must be condensed: shorter prose, no repetition, one worked example, and no more than 10 exercises. The reviewer rejects chapters over 18 pages.
Method: write or complete the chapter text FIRST, in at most three large writes; compile with \`cd ${ROOT}/Overleaf && ./build.sh ${it.stem}\` and read build/only-${it.stem}.log; fix every error (undefined references to OTHER chapters are expected in a single-chapter build and are not errors). Then write and run the code file the spec names (its self-test must pass in under 60 s; every number quoted in the worked example must come from it), the figure files (one tikzpicture per file in Overleaf/figures/${it.id}/, included with \\inputfigure), the generated .dat files, the solutions file and the glossary file (both listed in the brief). Proofread once with \`pdftotext build/only-${it.stem}.pdf - | head -500\`. Finish only when the build status is 0 with no errors and no undefined labels of your own, and the self-test passes.
Rules: do not run git (the repository autosaves); do not edit main.tex, searchbook.sty, references.bib, the front matter or other chapters (put new references in Overleaf/bib/${it.id}-extra.bib and only if you are certain of them); macro and \\SetKwFunction names must be unique (prefix with the chapter topic); ASCII only in code and .dat files; be economical: no repeated re-reads of large files, no page-image rendering unless the log suggests a figure problem, no more than about 60 tool calls.
Your final output is the structured report: status (done/partial/failed), pages (of the chapter itself, i.e. the single-chapter PDF page count minus the front matter), and notes (files written, counts of figures/tables/algorithms/listings/exercises, what the self-test checks, anything the editor must know).`
}

function reviewPrompt(it, round) {
  const prev = round > 1
    ? ` This is round ${round}: the previous review is ${ROOT}/reviews/${it.id}-round${round - 1}.md with the reviser's response appended; verify that each earlier required change was actually resolved and do not re-raise items that were resolved correctly.`
    : ''
  return `You are an independent, demanding but constructive professional textbook reviewer and a domain expert in robot motion planning, multi-agent path finding, estimation and control. Review ${it.title} (${file(it)}) of the textbook in ${ROOT} against the rubric in ${ROOT}/STYLE_GUIDE.md section 9 (categories A-H), the chapter's specification ${ROOT}/docs/specs/${it.id}.md (if that file does not exist, review against the chapter's own objectives box and the training plan), and the training plan ${ROOT}/docs/core-idea.txt.${prev}
Procedure: (1) read STYLE_GUIDE.md, the spec and the chapter file completely, plus its figure files in Overleaf/figures/${it.id}/, its code Overleaf/code/${it.id}_*.py (if any), and its solutions and glossary files under Overleaf/appendices/; (2) build it with \`cd ${ROOT}/Overleaf && ./build.sh ${it.stem}\`, read the log for errors, undefined labels of this chapter and overfull boxes, then read the WHOLE PDF text with \`pdftotext build/only-${it.stem}.pdf -\`; (3) run the code once (\`python3 code/${it.id}_*.py\`) and check that the numbers quoted in the text match its output; (4) verify the technical content against your expert knowledge of the canonical sources: every definition, theorem statement, proof, formula, pseudocode line and complexity claim - recompute the worked example with a short script if needed; (5) check completeness against every "must cover" item of the spec and the week's items in the training plan; (6) check pedagogy and clarity for a graduate student reading alone, figures (at least 4, all referenced, captions that say what to notice, consistent styles), tables, exercises (6-10, difficulty spread, the week's coding exercise present, solvable), consistency with the notation of the earlier chapters (Overleaf/frontmatter/notation.tex; skim Overleaf/chapters/ch02-toolbox.tex and ch04-astar.tex where relevant), index entries (at least 15), citations (every key exists in Overleaf/references.bib or Overleaf/bib/${it.id}-extra.bib; flag any reference whose existence or details you cannot vouch for), and LENGTH: the chapter itself (single-chapter PDF minus the front matter) must be at most 18 pages - if it is longer, a required change (category G) must name concrete cuts.
Write the full review to ${ROOT}/reviews/${it.id}-round${round}.md with the sections: "# Review of ${it.title} - round ${round}", "## Verdict", "## Required changes" (numbered; each with location such as section/label/line, the problem, a concrete fix, and the rubric category A-H), "## Suggestions", "## What must be kept". Verdict rules: Accept only if there are NO required changes in categories A-E and at most cosmetic items in F-H; Minor revision if every required change is local; Major revision otherwise. A wrong formula, an incorrect proof, a claim stated as a theorem without proof or citation, a number in the text that the code does not reproduce, or a missing "must cover" item is always a required change. Be specific enough that a reviser can act without asking questions, and economical: at most about 40 tool calls. Do NOT edit the chapter or any other file except the review file.
Your final output is the structured verdict: verdict, required_changes (the same list as in the file), suggestions, keep.`
}

function revisePrompt(it, review, round) {
  return `You are the reviser of ${it.title} (${file(it)}) of the textbook in ${ROOT}. A peer reviewer returned the verdict "${review.verdict}" with these required changes (JSON):
${JSON.stringify(review.required_changes, null, 1)}
Suggestions: ${JSON.stringify(review.suggestions || [])}
What must be kept: ${review.keep}
The full review is ${ROOT}/reviews/${it.id}-round${round}.md. Read ${ROOT}/docs/finisher-brief.md for the rules (your chapter's files only; no git; never edit main.tex, searchbook.sty, references.bib or other chapters), ${ROOT}/STYLE_GUIDE.md, and the specification ${ROOT}/docs/specs/${it.id}.md if it exists.
Apply EVERY required change, and the suggestions where they are cheap, while keeping what the reviewer said must be kept and keeping the chapter within 18 pages. If you are certain a required change is technically wrong, do not apply it and explain why in your response. Rebuild with \`cd ${ROOT}/Overleaf && ./build.sh ${it.stem}\` until the status is 0 with no errors; re-run the chapter's code self-test; make sure every number quoted in the text still matches the code; regenerate .dat files if the code changed. Append a section "## Response to review (round ${round})" to ${ROOT}/reviews/${it.id}-round${round}.md listing each required change and exactly what you did about it. Be economical: at most about 50 tool calls.
Your final output is the structured report: status, pages, notes.`
}

async function reviewLoop(it) {
  const history = []
  let verdict = 'unknown'
  for (let round = 1; round <= MAX_ROUNDS; round++) {
    const review = await tryAgent(reviewPrompt(it, round),
      { label: 'review:' + it.id + ':r' + round, phase: 'Review', agentType: 'general-purpose', schema: REVIEW, model: REVIEW_MODEL })
    if (!review) { verdict = 'review-failed'; break }
    verdict = review.verdict
    history.push({ round, verdict: review.verdict, required: review.required_changes.length })
    log(it.id + ' round ' + round + ': ' + review.verdict + ' (' + review.required_changes.length + ' required changes)')
    if (review.verdict === 'Accept') break
    // Budget rule: a third round only if the second verdict is still a major revision.
    if (round === MAX_ROUNDS || (round === 2 && review.verdict !== 'Major revision')) {
      log(it.id + ': stopping after round ' + round + ' with verdict "' + review.verdict + '"; applying the remaining changes without a further review')
      const rev = await tryAgent(revisePrompt(it, review, round),
        { label: 'revise:' + it.id + ':r' + round, phase: 'Revise', agentType: 'general-purpose', schema: REPORT, model: REVIEW_MODEL })
      history.push({ round, revised: rev ? rev.status : 'failed', final: true })
      if (rev) verdict = review.verdict + ' (changes applied, unreviewed)'
      break
    }
    const rev = await tryAgent(revisePrompt(it, review, round),
      { label: 'revise:' + it.id + ':r' + round, phase: 'Revise', agentType: 'general-purpose', schema: REPORT, model: REVIEW_MODEL })
    if (!rev) { verdict = 'revise-failed'; break }
    history.push({ round, revised: rev.status, notes: (rev.notes || '').slice(0, 300) })
  }
  return { verdict, history }
}

const results = await pipeline(ITEMS,
  async (it) => {
    if (it.mode === 'review-only') return { status: 'done', pages: 0, notes: 'pre-existing draft; review only' }
    return await tryAgent(writePrompt(it),
      { label: 'write:' + it.id, phase: 'Write', agentType: 'general-purpose', schema: REPORT, ...WRITE_OPTS })
  },
  async (report, it) => {
    if (!report || report.status === 'failed') { log(it.id + ': author failed'); return { id: it.id, verdict: 'author-failed' } }
    if (report.status === 'partial') log(it.id + ': author reports partial - reviewer will catch the gaps')
    const r = await reviewLoop(it)
    return { id: it.id, pages: report.pages, authorNotes: (report.notes || '').slice(0, 400), verdict: r.verdict, history: r.history }
  })

const out = results.filter(Boolean)
log('finished: ' + out.map(r => r.id + '=' + r.verdict).join(', '))
return out
