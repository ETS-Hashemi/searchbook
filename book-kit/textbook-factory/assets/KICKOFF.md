# Kickoff prompt for a new book (paste into a fresh Claude Code session)

Replace the bracketed parts. Keep the structure: the skill needs these facts to start.

```
Use the textbook-factory skill (installed in .claude/skills/textbook-factory) to write a
complete textbook from scratch in this repository, in the Overleaf/ folder as an Overleaf
package (zip with main.tex at the root) plus a compiled PDF.

Source brief: [path to the Word/markdown/PDF file, or paste the outline here]. The book must
teach every topic in it, in that order, with the priorities and the exercises it lists.

Author: [name], [affiliation], [email]. Audience: [who reads it and what they know].
Spelling: [American|British]. Code: [Python 3 with NumPy | other]. Length: about [N] pages,
[M] chapters.

Work like this: keep TODO.md with every task of writing, reviewing and revising a textbook
and tick tasks as you complete them; commit and push to main after every step so I can
follow progress in the repository; review every chapter as a demanding professional reviewer
and revise it until the reviewer is satisfied; wait 30 seconds between loop iterations.
Use the strongest model for chapter authors and the accuracy check; use [model] for
reviewers and revisers. Do everything automatically; do not stop to ask unless a decision
would change the book's scope. Tell me what you are doing in short status messages.
```

Then, when it asks nothing and starts: watch `TODO.md` and the loop log in the repository.
Useful follow-ups: "continue", "check that the agents are not stalled", "how long is left",
"what did you do today", "push everything done so far", "build the Overleaf package".
