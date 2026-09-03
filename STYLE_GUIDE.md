# Searchbook — Writing, Figure, Code and Review Guide

This guide governs every chapter of *Multi-Agent Path Planning and Drone Collision
Avoidance: A Textbook of Algorithms*. Chapter authors, revisers and reviewers all work
from it. The LaTeX project lives in `Overleaf/`; the chapter template is
`docs/chapter-template.tex`; the shared style file is `Overleaf/searchbook.sty`.

## 1. The book and its reader

* **Purpose.** Teach, from first principles, every algorithm in the training plan
  (`core idea/core.docx`, extracted in `docs/core-idea.txt`): single-agent graph search,
  multi-agent path finding (MAPF), local/reactive collision avoidance, sampling-based
  planning, tracking and prediction, optimization and control, and how they combine into a
  hybrid swarm planner.
* **Reader.** A graduate student or engineer starting research on drone swarms. Comfortable
  with Python, basic linear algebra, calculus and probability. No prior knowledge of
  robotics planning is assumed. Reads the book alone, without a lecturer.
* **Voice.** A patient tutor. Plain American English, short sentences, active voice,
  second person is welcome ("you can now..."). Intuition first, formalism second, code third.
  Never write "obviously", "clearly", "trivially" or "it is easy to see".
* **Promise to the reader.** Every algorithm gets: a motivation, a plain-words idea, exact
  definitions, pseudocode, a fully worked example with a figure and a trace table, its
  properties with proofs or proof sketches, Python that runs, pitfalls, its place in the
  drone system, a summary, and exercises.

## 2. Chapter structure (mandatory)

Follow `docs/chapter-template.tex` in this order:

1. `\chapter{...}\label{ch:chNN}` (label is the file prefix, e.g. `ch:ch04`).
2. `objectives` box with 4–6 outcomes.
3. *Why this matters for a drone swarm* (½–1 page, concrete scenario, roadmap).
4. *The idea in plain words* with a `keyidea` box and at least one concept figure.
5. *Problem statement and notation* (`definition` environments).
6. *The algorithm*: `algorithm2e` pseudocode + line-by-line walkthrough.
7. *A worked example*: small instance, figure, trace table, numbers verified by code.
8. *Properties*: completeness, optimality, complexity as `theorem`/`proposition` with
   proof or proof sketch; state assumptions exactly.
9. *Variants and extensions* (short; point to later chapters where relevant).
10. *Implementation notes* + Python listing + at least two `pitfall` boxes in the chapter.
11. *Where this fits in the drone system* (`dronebox`, referencing `\cref{ch:ch24}` and the
    study-plan week in `\cref{ch:appA}`).
12. `summary` box (bullets) and a *Further reading* paragraph with citations.
13. *Exercises*: 6–10, graded `\difficulty{1..3}`; conceptual, pen-and-paper and coding;
    the coding exercise of the corresponding study-plan week must appear.

**Length.** 12–18 pages per chapter (about 900–1500 lines of LaTeX in the chapter file
plus figure files). "Essential" topics at the upper end, "Awareness" topics shorter.
Chapters 1, 2, 24 and 25 may deviate from the algorithm template but keep boxes, figures,
tables, summary and exercises.

## 3. Writing rules

* Define every symbol before it is used; use the macros of `searchbook.sty` and the
  notation table (`Overleaf/frontmatter/notation.tex`). Do not invent competing notation.
* Define each acronym at first use in every chapter (MAPF, CBS, ...).
* One idea per paragraph. Use lists for enumerations; use tables for comparisons.
* Bold a term when it is defined and add an `\index{}` entry. At least 15 index entries
  per chapter (use subentries: `\index{A*!consistency}`).
* Reference every figure, table, algorithm and listing from the text with `\cref`.
* Captions say what to notice ("The dashed path is longer but avoids the corridor.").
* Labels: `ch:chNN`, `sec:chNN-slug`, `fig:chNN-slug`, `tab:chNN-slug`, `alg:chNN-slug`,
  `eq:chNN-slug`, `def:chNN-slug`, `thm:chNN-slug`, `ex:chNN-slug` (examples),
  `exr:chNN-slug` (exercises), `lst:chNN-slug`. Cross-chapter references: `\cref{ch:ch09}`.
* Citations: `\cite{key}` from `Overleaf/references.bib`. Cite the original paper and one
  textbook treatment. **Never fabricate a reference.** Add an entry only if you are certain
  of authors, title, venue and year; append it at the end of the file under a comment naming
  your chapter. Omit page numbers rather than guess.
* Accuracy: pseudocode and formulas must match the canonical sources (Section 8). Check edge
  cases (D* Lite key modifier, ORCA half-plane orientation, Kalman update, ECBS focal bound).
  Numbers in worked examples must be produced or checked by the Python code.

## 4. Figures

* TikZ / pgfplots only; no bitmap or external PDF images.
* One figure per file: `Overleaf/figures/chNN/<slug>.tex` containing only the
  `tikzpicture` (no `figure` environment, no `\label`). Include it with
  `\begin{figure}[tb]\centering\inputfigure{chNN/slug}\caption{...}\label{fig:chNN-slug}\end{figure}`.
* Use the shared styles: `sbobstacle`, `sbopen`, `sbclosed`, `sbpath`, `sbpathalt`,
  `sbstart`, `sbgoal`, `sbnode`, `sbedge`, `sbagentA..D`, `sbintruder`, `sbvec`, `sbannot`,
  `sbbox`, `sbflow`, `sbregion`, `\drawgrid{c}{r}`, `\gridobstacle{x}{y}`, colours `sbBlue`,
  `sbOrange`, `sbGreen`, `sbPurple`, `sbRed`, `sbGray`.
* At least 4 figures per chapter: a concept figure, a worked-example figure, an
  algorithm-output or comparison figure, and one more where useful.
* Algorithm-output figures are generated: write `Overleaf/code/figures/gen_chNN_<slug>.py`
  (NumPy only, fixed seeds) that writes `Overleaf/figures/data/chNN-<slug>.dat`
  (whitespace-separated, header row) for `\addplot table[x=..., y=...]`, or writes a
  complete TikZ file into `Overleaf/figures/chNN/`. Run it and commit its output.
* Keep plots below ~1500 points; width at most `\textwidth`; text `\small` or `\footnotesize`.
* Test every figure by compiling the chapter (Section 7).

## 5. Tables and pseudocode

* Tables use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), `\small`, caption above.
  Typical tables: algorithm comparison, trace of the worked example (step, expanded node,
  Open/Closed, g/h/f), parameters and their effect, metrics.
* Pseudocode uses `algorithm2e` (already configured): `\begin{algorithm}[htb]`,
  `\caption`, `\label{alg:...}`, `\KwIn`, `\KwOut`, `\Fn{\Name{args}}{...}`, `\KwRet`,
  `\ForEach`, `\While`, `\If`/`\ElseIf`/`\Else`, `\Comment{...}` (use `\tcp*{...}` for
  end-of-line comments). Declare function names with `\SetKwFunction{Uniq}{Name}` at the
  top of the chapter; **macro names must be unique across the book** (prefix with the
  chapter topic). Label lines with `\label{alg:chNN-name:step}` and refer to them with
  `line~\ref{alg:chNN-name:step}`.

## 6. Code

* Python 3.10+, NumPy (SciPy only where unavoidable: `scipy.optimize` for MILP/QP). PEP 8,
  short docstrings, no unicode in source.
* Full implementation: `Overleaf/code/chNN_<slug>.py`, with `if __name__ == "__main__":`
  running a self-test with `assert`s in under 10 seconds. Run it; it must pass.
* In the chapter: `\begin{lstlisting}[caption={...},label={lst:...}] ... \end{lstlisting}`
  excerpts of at most 45 lines, copied verbatim from the file. When the text quotes
  numbers or output, they must come from actually running the code.

## 7. Compile check (required before a chapter is handed in)

```bash
cd Overleaf && ./build.sh chNN-slug      # builds build/only-chNN-slug.pdf
python3 code/chNN_slug.py                # self-test must pass
```

Requirements: build status 0; no `!` errors; no undefined references or citations that
belong to *your* chapter (references to other chapters may show `??` in single-chapter
builds); fix overfull boxes wider than 15 pt when the fix is easy. Do not edit
`searchbook.sty`, `main.tex`, or other chapters; list needed macro additions in your final
report instead. `pdftotext build/only-chNN-slug.pdf - | head -200` is a good way to read
your own output.

## 8. Canonical sources (accuracy anchors)

| Topic | Source of truth |
|---|---|
| Dijkstra, A*, admissibility/consistency | Hart, Nilsson & Raphael 1968; Pearl 1984; Russell & Norvig 2020; CLRS |
| LPA*, D* Lite | Koenig & Likhachev 2002 (AAAI), Koenig, Likhachev & Furcy 2004 (AIJ), Koenig & Likhachev 2005 (T-RO) |
| ARA* | Likhachev, Gordon & Thrun 2003 |
| MAPF definitions | Stern et al. 2019 |
| Prioritized planning, space-time A* | Silver 2005; Erdmann & Lozano-Pérez 1987; Čáp et al. 2015; Ma et al. 2019 |
| CBS / ICBS | Sharon et al. 2015; Boyarski et al. 2015 |
| ECBS, focal search | Barer et al. 2014; Pearl & Kim 1982; Li, Ruml & Koenig 2021 |
| M* | Wagner & Choset 2011, 2015 |
| Push-and-Swap / Push-and-Rotate | Luna & Bekris 2011; de Wilde et al. 2014 |
| VO / RVO / ORCA | Fiorini & Shiller 1998; van den Berg et al. 2008, 2011 |
| DWA | Fox, Burgard & Thrun 1997 |
| APF | Khatib 1986; Koren & Borenstein 1991 |
| RRT / RRT* / Informed RRT* | LaValle 1998; Karaman & Frazzoli 2011; Gammell et al. 2014 |
| KF / EKF / UKF / PF | Kalman 1960; Thrun et al. 2005; Julier & Uhlmann 1997/2004; Wan & van der Merwe 2000; Gordon et al. 1993; Arulampalam et al. 2002 |
| LSTM / Transformer prediction | Hochreiter & Schmidhuber 1997; Alahi et al. 2016; Vaswani et al. 2017; Giuliari et al. 2021; Rudenko et al. 2020 |
| MPC | Rawlings, Mayne & Diehl 2017; Mayne et al. 2000 |
| MILP for planning | Schouwenaars et al. 2001; Richards & How 2002; Yu & LaValle 2016 |
| Consensus / formation | Olfati-Saber, Fax & Murray 2007; Ren & Beard 2005/2008; Oh, Park & Ahn 2015 |

## 9. Review rubric (used by reviewers; verdicts drive the revision loop)

Reviewers act as a demanding but constructive professional textbook reviewer and domain
expert. Review each chapter against:

* **A. Technical accuracy.** Definitions, pseudocode, formulas, complexity and optimality
  claims, theorem statements and proofs, numbers in worked examples, code correctness.
* **B. Completeness against the training plan.** Everything the plan lists for the topic and
  its week (e.g. Week 1: admissible/consistent heuristics, space-time representation).
* **C. Pedagogy and clarity.** Intuition before formalism, worked example quality, no
  undefined symbols, prerequisites honoured, progression, readability for the target reader.
* **D. Figures and tables.** Present (≥4 figures), correct, referenced, informative
  captions, consistent style, legible.
* **E. Exercises.** 6–10, graded, includes the plan's coding exercise, solvable from the
  chapter, appropriate range.
* **F. Consistency.** Notation table and macros, terminology and cross-references consistent
  with the other chapters, index entries present.
* **G. LaTeX quality.** Compiles cleanly, warnings, overfull boxes, float placement,
  listing length, unique labels/macros.
* **H. Citations.** Original sources cited, entries exist in `references.bib`, no
  fabricated references, further-reading paragraph.

Output of a review: a markdown file `reviews/chNN-round<k>.md` with (1) verdict
**Accept** / **Minor revision** / **Major revision**, (2) a numbered list of *required*
changes, each with location (section/label/line), the problem, and a concrete fix,
(3) optional suggestions, (4) a short praise paragraph naming what must be kept.
A chapter is *Accepted* only when there are no required changes left in A–E and at most
cosmetic items in F–H.
