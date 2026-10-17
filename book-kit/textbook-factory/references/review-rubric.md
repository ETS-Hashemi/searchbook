# Review rubric, review file format and verdict rules

Reviewers act as a demanding but constructive professional textbook reviewer and a domain
expert. They review one chapter against the style guide, the chapter's spec and the
requirements, and they **verify**, not just read: build the chapter, read the whole PDF
text, run the code, recompute the worked example, check each theorem against the canonical
source.

## Categories

* **A. Technical accuracy.** Definitions, pseudocode, formulas, complexity and optimality
  claims, theorem statements and proofs, numbers in worked examples, code correctness.
* **B. Completeness** against the spec's must-cover list and the requirements for the topic.
* **C. Pedagogy and clarity.** Intuition before formalism, worked-example quality, no
  undefined symbol, prerequisites honoured, progression, readability for the target reader
  reading alone; sentence length (flag chapters whose mean sentence exceeds ~28 words).
* **D. Figures and tables.** At least 4 figures, all referenced, captions say what to
  notice, consistent styles, legible, generated figures reproducible.
* **E. Exercises.** 6–10, graded, includes the brief's coding exercise for the topic,
  solvable from the chapter, a range of difficulty, solutions file present.
* **F. Consistency.** Notation table and macros, terminology and cross-references, index
  entries (≥15 per chapter), glossary terms.
* **G. LaTeX quality and length.** Compiles cleanly, warnings, overfull boxes, float
  placement, listing length, unique labels and macro names, length within the band (cuts
  only where there is padding).
* **H. Citations.** Original sources cited, every key exists, no fabricated reference,
  further-reading paragraph.

## Review file: `reviews/<id>-round<k>.md`

```
# Review of <Chapter title> - round <k>
<what was reviewed, build result, code result, what was recomputed>
## Verdict
**Accept** | **Minor revision** | **Major revision** (one paragraph of justification)
## Required changes
1. **<location: section / label / lines>: <problem in one sentence>.** <evidence> Concrete
   fix: <replacement text or exact instruction>. *Category <A-H>.*
...
## Suggestions
## What must be kept
```

Verdict rules: Accept only if there are no required changes in A–E and at most cosmetic
items in F–H. Minor revision if every required change is local. Major revision otherwise.
A wrong formula, an invalid proof, a claim stated as a theorem without proof or citation, a
number the code does not reproduce, or a missing must-cover item is always a required
change. In round k>1 the reviewer verifies that each earlier required change was resolved
and does not re-raise items that were resolved correctly.

## Reviser's response (appended to the same file)

```
## Response to review (round <k>)
1. <done | not done, because ...> — <what exactly changed, where>
...
```

A reviser may refuse a required change only when certain it is technically wrong, and says
why; the next reviewer adjudicates.

## Structured outputs for the loop script

Reviewer: `{verdict, required_changes:[{location, problem, fix, category}], suggestions:[], keep}`.
Author / reviser: `{status: done|partial|failed, pages, notes}`.
