# Book-level passes (after every chapter is accepted)

Each pass is an agent or a script with a precise file scope. Run passes that touch
disjoint files in parallel; commit each pass separately so a bad one can be reverted.

## 1. Coverage audit (one reviewer agent, read-only)

Input: `docs/requirements.md`, the TOC, every chapter's objectives box and exercises.
Output: `docs/coverage-audit.md` listing gaps (requirement items with no home or a thin
treatment), inconsistencies between the course-plan appendix and the chapters (exercise
numbers, week assignments, counts), and which chapter should fix each. Gaps become fix
items with a chapter owner.

## 2. Consistency pass (one agent per half of the book, or a script where mechanical)

Notation: the same symbol for the same thing everywhere (make a list of clashes:
`h` as horizon index vs consensus step, `tau` vs `sigma` for paths, bold vs plain states).
Terminology: one canonical name per concept (the drone book had five names for one
architecture layer; fix with a grep list and a judgment call per site). Cross-references:
every "see Chapter N" points where it says. Duplicated material: the same algorithm or
definition presented twice gets one canonical presentation and a "delta" (what changes)
elsewhere, with labels preserved. Output: `docs/consistency-issues.md` with "applied" and
"queued for the mechanical pass" sections.

## 3. Book-level review (one reviewer agent, read-only)

A reviewer reads the whole PDF text (`pdftotext`) plus the sources, as a demanding
textbook reviewer would read the manuscript: structure, front matter promises vs content,
reading paths, duplicated or contradictory statements across chapters, spelling and style
uniformity, index and glossary quality, list-of-algorithms entries, chapter lengths vs the
guide, the weakest chapters. Output: `docs/book-review.md` with a verdict and numbered
required items, each with location and fix. Expect 10–20 items.

## 4. Accuracy spot-check (one strong reviewer agent, read-only)

Extract every theorem, lemma, proposition and corollary with its proof, and every
comparison/complexity table, into one file (a 40-line script does it); the agent checks
statement truth, hypotheses, proof validity, constants, complexity claims, and named
classical results against their correct hypotheses, opening the chapter for definitions
when needed. Output: `docs/accuracy-spot-check.md` (findings table with severity and
exact replacement text). Apply the fixes yourself; rebuild the touched chapters. In the
drone book this found one false proposition (a bound stated for weighted graphs that holds
only for unit weights) and one missing hypothesis that two review rounds had missed.

## 5. Fix passes (agents on disjoint chapter sets)

Group the items from passes 1–4 by chapter, give each agent a set of chapters nobody else
touches, a list of items with locations, and the instruction to keep edits minimal and to
rebuild each chapter. Commit per agent.

## 6. Mechanical pass (scripts first, one copyeditor agent for the judgment items)

* Spelling convention: `scripts/american.py` converts British to American spelling across
  `.tex`, `.py`, `.dat` and the style file (word-level and substring rules,
  case-preserving, protected macro names, labels, citation keys, file paths). Run it in
  dry-run mode, read the report, apply, then run `scripts/check_book.py`: any
  `\SetKwFunction{Name}` or defined name that changed must be renamed consistently
  (the script protects `\macro` uses but not names inside braces), and every citation key
  must still exist. Record the convention in the style guide and the preface.
* `scripts/joinindex.py`: every `\index{}` argument on one line (a line break inside the
  argument splits the index entry in two).
* `\paragraph*` → `\paragraph` where the book uses numbered-free run-in headings
  consistently; short captions (`\caption[short]{long}`) for list-of-figures/algorithms
  entries that overflow; glossary duplicates; `tools/assemble_glossary.py` again.
* Copyeditor agent: canonical names book-wide from a grep list, pointers to the math
  appendix at the first use of its material in each chapter, notation rows for symbols that
  the table lacks, overfull boxes (`align*` for long inline chains, `sloppypar` for lines
  with long identifiers, narrower group plots), Appendix B/C cross-links.

## 7. Front matter and production note

Preface sections: why the book exists, who should read it, what you will be able to do,
how it is organized, how to read it (reading paths that agree with Chapter 1), conventions
(boxes, numbering, difficulty stars, spelling), the code, sources, errata and a production
note (AI-assisted drafting under the author's direction; the author is responsible for the
content), acknowledgments. Title page and copyright page carry the real author; an
about-the-author page follows the copyright page if the user wants one.

## 8. Overleaf compile limits and the figure cache

Overleaf's compile timeout is 20 s on the free plan and 240 s on premium. A book with
~180 TikZ/pgfplots figures needs ~120 s per pdfLaTeX pass, so it cannot compile on
Overleaf without help. The style file externalizes every `\inputfigure` picture in
"graphics if exists" mode: `tools/render_figures.py` renders all figures once into
`figcache/` (shipped in the zip); with the cache, one pass takes ~50 s for the whole book
and ~5 s for one chapter via `\includeonly` (premium: whole book; free: one chapter at a
time). The index must be guarded with `\tikzifexternalizing{}{...}` in `main.tex` so that
export sub-jobs do not clobber it. pdfLaTeX main memory (5 million words) is the other
limit: keep `.dat` files under ~1500 rows (`tools/thin_dat.py`).

## 9. Final QA list

0 errors, 0 undefined references or citations, 0 overfull boxes > 15 pt, 0 `??` in the PDF
text, TOC complete (every chapter has its Summary section), every chapter has figures,
tables, examples and exercises (per-chapter counts from `scripts/qa.sh`), index and
bibliography present, PDF metadata (title, author, subject, keywords), the zip has
`main.tex` at its root and compiles after unzipping.
