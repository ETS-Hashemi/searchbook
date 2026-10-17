# The production process, phase by phase

This is the playbook behind the skill. Each phase ends with a verified, committed state.
Tick tasks in `TODO.md` as you go (the scaffolder generates it with one line per chapter);
the loop log at its end is the user's window on progress.

## Phase 0 — Requirements, planning, infrastructure (orchestrator only)

1. **Extract the brief.** Whatever the user gives (Word file, syllabus, outline, training
   plan, list of topics) becomes `docs/requirements.md`: the topics in order, their
   priority (Essential / Important / Optional), prerequisites, any schedule (weeks,
   lectures), the exercises or milestones the reader must reach, the capstone or system the
   book builds toward, and a completion checklist if the brief has one. Everything the book
   must cover is in this file; reviewers check chapters against it. Keep the original file
   in the repository too.
2. **Decide the editorial frame** and write it into `STYLE_GUIDE.md` §1: audience, what the
   reader can do before and after, voice, spelling (American or British, final), code
   language and library policy, chapter length bands (Essential 16–22 pages, others 12–20
   worked for an algorithms book; a conceptual book may need less), the "promise to the
   reader" (what every chapter contains).
3. **Table of contents.** Parts → chapters → appendices. One chapter per method or per
   tightly related pair; an introduction chapter that maps the whole book; a toolbox
   chapter for shared prerequisites; a closing chapter that assembles everything; an
   appendix for the course/study plan, one for mathematical prerequisites, one for
   solutions. Twenty to thirty chapters of 15–25 pages is a 600–750 page book.
4. **Scaffold** with `scripts/new_book.py book.json <dir>`; then fill the domain-specific
   parts: notation macros in `Overleaf/textbook.sty` (one macro per recurring symbol, used
   everywhere), the canonical-sources table in `STYLE_GUIDE.md` §8 (for each topic, the
   paper or book that is the source of truth), seed `Overleaf/references.bib` with 30–60
   references you have verified (web search; DOI or venue and year), colour and figure
   styles if the subject has its own visual language.
5. **Build the skeleton** (`cd Overleaf && ./build.sh`): placeholders only, zero errors.
   Build the style test (`./build.sh --standalone ../docs/style-test.tex`) so every
   environment is known to work. Commit, push.

## Phase 1 — Specifications

One `docs/specs/<id>.md` per chapter and appendix, 150–400 words each, in the format of
`references/spec-template.md`. Write them from the requirements and your own knowledge of
the subject; where the brief lists a coding exercise or milestone for a topic, the spec
names it. Read all specs together once: do they overlap? Is every requirement covered
exactly once? Do the cross-references between chapters go in one direction (later chapters
assume earlier ones)? Fix before launching authors; a spec change after drafting costs a
revision round.

## Phase 2 — Chapter drafts (parallel authors)

* Batches of 6–8 chapters per workflow run, foundations first so that later authors can
  read a finished chapter for the house style (tell them which one).
* Each author gets: the brief (`docs/writer-brief.md`), the style guide, the chapter
  template, its spec, the style file, and a budget. The deliverables are fixed: chapter
  file, ≥4 figures (one TikZ picture per file), code file with a self-test, generated data
  files, solutions file, glossary term file, optional extra bib file.
* Authors never edit `main.tex`, the style file, `references.bib`, front matter, or other
  chapters; they report needed macros instead. This is what keeps parallel authors from
  colliding.
* When an author dies mid-chapter, launch a *finisher* (`docs/finisher-brief.md`) that
  completes the draft rather than a new author that starts over.
* After each batch: build each chapter, run its code, commit, update TODO (phase 2 lines
  and the loop log).

## Phase 3 — Reference code and figure generators

Usually done inside Phase 2 by the authors. The orchestrator verifies: `code/run_all.py`
passes; every `.dat` file has a generator script with a fixed seed; every listing in a
chapter is an excerpt of a file that runs (reviewers check this per chapter).

## Phase 4 — Back matter

* Notation table (`frontmatter/notation.tex`): every macro of the style file with meaning
  and the chapter that introduces it; grouped by area; a "warnings" paragraph for symbols
  that mean different things in different chapters.
* Glossary: `tools/assemble_glossary.py` merges the per-chapter term files; remove
  duplicates by deleting the later chapter's term.
* Solutions appendix: per-chapter solution files are `\input` into it; add hint blocks for
  every coding exercise that has no full solution.
* Study plan / course map appendix: the brief's schedule mapped to chapters, with a
  traceability table (requirement → chapter → exercise).
* Bibliography audit: an agent with web search verifies every entry (authors, title, venue,
  year); fix or delete; run `biber --validate-datamodel` or at least a clean build.
* Index audit: list the top-level terms, merge variants, make sure every `\index{}`
  argument is on one source line (`scripts/joinindex.py`).

## Phase 5 — Peer review and revision (per chapter, until Accept)

The loop script does this: review → revise → re-review, saving
`reviews/<id>-round<k>.md` with the reviser's response appended. Verdict rules and the
file format are in `references/review-rubric.md`. Budget rule: two rounds per chapter, a
third only if round 2 is still Major revision; whatever is left after the last round is
applied by a reviser without a further review and logged as "changes applied, unreviewed".
Record every round in the review log table of `TODO.md`.

## Phase 6 — Book-level passes

See `references/book-level-passes.md`: coverage audit, consistency pass, book-level
review, accuracy spot-check, fix passes on disjoint file sets, mechanical pass. Each pass
is one or a few agents with precisely scoped files, so that they can run in parallel and
their work can be committed separately.

## Phase 7 — Copyediting and front matter

Preface (why the book exists, who it is for, how to read it, conventions, the code,
sources, errata, acknowledgments, a production note: how the book was produced, including
the use of AI tools, which publishers require), title page, copyright page (name, year,
license), about-the-author page, short captions where list entries overflow, last overfull
boxes, TOC depth, list of algorithms.

## Phase 8 — Final build, QA, packaging, delivery

`Overleaf/package.sh` (glossary → figure cache → full build → PDF + zip), then
`scripts/qa.sh`; unzip the package into an empty directory and compile one chapter from it;
commit and push; send the PDF and the zip; final TODO ticks and loop-log row; tell the user
what remains theirs to do.

## The 30-second rule and the loop log

Between TODO iterations wait 30 seconds (a `sleep 30` in the orchestrator is fine; agents
run in the background meanwhile). Every iteration appends a row to the loop log:
`| n | date time | what was done, with numbers | what comes next |`. When the user asks
"what did you do today", the log answers.
