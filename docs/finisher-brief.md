# Brief for finishing authors

You are completing a chapter of the textbook in /home/user/searchbook whose first draft was written by a previous author who was interrupted. Read, in this order: docs/writer-brief.md (rules, deliverables, book map), STYLE_GUIDE.md, and your chapter's specification in docs/specs/. Then read the existing draft and its figure/code files.

Your job, in order:
1. Make the chapter compile: `cd Overleaf && ./build.sh <chapter-file-stem>`; read the log; fix every error (missing figure files must be created, not removed). Undefined references to *other* chapters (ch:chNN, ch:appX) are expected in a single-chapter build and are not errors.
2. Complete every mandatory element of the specification and of docs/chapter-template.tex that the draft lacks (sections, ≥4 figures, worked example with trace table whose numbers come from the code, pseudocode, properties with proofs, listing, ≥2 pitfall boxes, drone box, summary, further reading, exercises, solutions file, glossary file). Do not rewrite text that is already good.
3. Run the chapter's Python file; its self-test must pass; regenerate any .dat files its figures need.
4. Compile again until the build status is 0 with no errors, then proofread the PDF text once (`pdftotext build/only-<stem>.pdf - | head -400`).
Rules: work only on your chapter's files (chapter .tex, figures/chNN/, figures/data/chNN-*, code/chNN_*.py, code/figures/gen_chNN_*.py, appendices/solutions/chNN-solutions.tex, appendices/glossary/chNN-terms.tex, bib/chNN-extra.bib). Never edit main.tex, searchbook.sty, references.bib or other chapters. Do not run git (the repository autosaves). Be economical: few large edits, no page-image rendering unless a figure looks wrong. Finish with the final report described in docs/writer-brief.md.
