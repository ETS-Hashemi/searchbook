# Book-level review — *Multi-Agent Path Planning and Drone Collision Avoidance*

Reviewer: book-level (whole manuscript, not chapter internals).
Object reviewed: `Overleaf/` at the state of the 2026-09-09 interim build
(`Overleaf/searchbook.pdf`, 710 pages, 25 chapters + 3 appendices + glossary,
bibliography and index). Chapter internals were reviewed separately
(`reviews/chNN-round*.md`) and are not re-litigated here.

Source state: commit `78d9370` plus the uncommitted edits in the working tree.
Part 2 of the cross-chapter consistency pass
(`docs/consistency-issues.md`) is **in flight** — `frontmatter/notation.tex` and
`chapters/ch22-milp.tex` changed during this review. Required item 7 below is
written against the post-pass state and credits what has already landed; every
other item was re-verified against the tree after that change. The typeset page
and algorithm numbers cited throughout come from the 9 September PDF and will
shift once the pass and these revisions are applied.

---

## Verdict

**Minor revision.**

The manuscript is architecturally sound and, for a 700-page multi-author book,
unusually coherent. Three things earn that verdict and should be said before the
complaints:

* **Prerequisites hold.** A mechanical scan of every cross-chapter reference to a
  *numbered* result (theorem, definition, equation, algorithm, example, figure,
  table) found exactly **one** forward reference in the entire book: `ch01` →
  `def:ch12-ttc`, in the preview chapter, explicitly flagged. Everything else
  that points forward is a signposted pointer of the "you will meet this in
  \cref{ch:chNN}" kind. Chapter 1's claim that "each one uses only what came
  before it" is true.
* **The spine is carried all the way through.** All 25 chapters have exactly one
  `objectives`, one `keyidea`, one `dronebox` and one `summary` box; 24 of 25
  droneboxes name their study-plan week and `\cref{ch:appA}`; every dronebox
  places its algorithm inside the four-layer architecture of `ch01`/`ch24`; the
  three architecture figures (`ch01/architecture`, `ch24/architecture`,
  `appA/architecture`) agree; `ch24` §24.13 answers all seven research
  directions opened in `ch01` §1.5, in the same order.
* **Production hygiene is good.** 0 undefined references (`??`) in the build;
  188 bibliography entries, no duplicate titles, exactly one uncited entry;
  337 glossary terms with duplicates merged; 7–10 graded exercises per chapter,
  every one with the study plan's coding exercise; 5–10 figures per chapter;
  the shared definition/example/theorem counter works exactly as the preface
  promises.

Nothing on the required list below asks for a chapter to be rewritten or the
book to be reordered. But there are enough items, and items 1, 2, 6 and 7 touch
enough files, that this is a real revision round rather than a copyedit. Items
**1** and **6** are the two that a demanding external reviewer would refuse to
let pass.

---

## Required book-level changes

### 1. Space-time A\* is printed three times as a numbered algorithm

**Location.** `alg:ch04-spacetime` (Algorithm 4.2, §4.8 "Space-time A\*",
p. 79), `alg:ch08-ca` (Algorithm 8.2 "Cooperative A\*: space-time A\* against a
reservation table", §8.4, p. 155), `alg:ch09-lowlevel` (Algorithm 9.2 "The low
level: space-time A\* for one agent under its constraints", §9.4, p. 176).
Supporting duplicates: the reservation table is described informally in
`ch04` §4.8.2 and defined formally in `def:ch08-reservation`; the goal-stay time
is `def:ch04-goalstay` and is bolded again with its own index entry at
`alg:ch08-ca:tg`.

**Problem.** These are the same search line for line — same key
`(f, −t)`, same wait-first successor order, same `t > t_gamma` goal test, same
`T_max` cut-off — differing only in whether the filter is called a constraint
set, a reservation table or `C_i`, and in the static-obstacle set `B`. The
triplication is visible to the reader in the front matter: the List of
Algorithms shows 4.2, 8.2, 9.2 and 10.1 all naming "space-time A\*". The
glossary assembler independently flags it: *goal-stay time* → ch04 + ch08,
*reservation table* → ch04 + ch08. A reader who has met the search three times
cannot tell which is the canonical one, and a reader who implements from
Algorithm 8.2 will not have the `Gen` duplicate-detection argument that only
`ch04` gives.

**Fix.**
* Make `alg:ch04-spacetime` canonical. Keep in `ch04` §4.8: the space-time state
  (`def:ch04-spacetime`), the vertex/edge constraint definition
  (`def:ch04-constraints`), the goal-stay time (`def:ch04-goalstay`), the horizon
  `T_max = H + 1 + D`, and the pseudocode.
* Move the reservation table entirely to `ch08` §8.3 (`def:ch08-reservation`
  already exists and is the better version). In `ch04` §4.8.2 cut the
  "Constraints and reservation tables" bullet list down to two sentences:
  constraints come either from a CBS node (`ch09`) or from the earlier agents'
  paths, "collected in a *reservation table*, defined in
  \cref{def:ch08-reservation}". Note that `tab:appA-checklist` already routes
  the reader to ch08 for reservation tables, so this makes the appendix true.
* In `ch08`, delete the `algorithm` float `alg:ch08-ca` and replace it with a
  six-line delta: "Cooperative A\* is \cref{alg:ch04-spacetime} with three
  changes: (i) …, (ii) …, (iii) …". Keep the walkthrough paragraph, retargeted at
  those three lines. `alg:ch08-pp` and `alg:ch08-whca` stay.
* In `ch09`, delete `alg:ch09-lowlevel` and replace it with a five-line delta
  against `alg:ch04-spacetime` (constraints carry an agent index; `t_gamma` is
  read from `C_i`). `alg:ch09-cbs` stays.
* `alg:ch10-lowlevel` (Algorithm 10.1) legitimately survives — it adds FOCAL and
  the returned lower bound — but present it too as a delta on
  `alg:ch04-spacetime` rather than as a fresh listing.
* Delete the duplicated glossary entries in `appendices/glossary/ch08-terms.tex`
  (*goal-stay time*) and `ch04-terms.tex` (*reservation table*), keeping one of
  each.

**Size.** Roughly −3 to −4 printed pages. Edits in 3 chapter files, 2 glossary
term files; the List of Algorithms fixes itself.

---

### 2. Chapter 2 §2.8–§2.9 duplicates Appendix B §B.3 and §B.5

**Location.** `ch02` §2.8 "Uncertainty: random vectors, Gaussians and Bayes'
rule" (`def:ch02-mean-covariance`, `def:ch02-gaussian`,
`def:ch02-covariance-ellipse`, `eq:ch02-bayes`) and §2.9 "Computation:
complexity, priority queues and hashing" (`def:ch02-big-o`,
`def:ch02-priority-queue`, the lazy-deletion idiom, the "Hashing states"
paragraph, the "Floats and arrays as dictionary keys" pitfall), against
`appB` §B.3.1–B.3.3 and §B.3.5, and §B.5.1–B.5.3 (`def:appB-bigO`, the binary
heap, the `heapq`/`dict` idiom, the "Heap entries must be comparable" pitfall).

**Problem.** Big-O is defined twice (`def:ch02-big-o`, `def:appB-bigO`), the
binary heap twice, lazy deletion twice (with two glossary entries and two index
headings), hashable-state advice twice with near-identical pitfalls, and the
multivariate Gaussian, the affine-transformation rule and Bayes' rule twice.
Neither section points at the other; `ch02` contains **no** reference to
`\cref{ch:appB}` at all. The reader who follows the preface ("\cref{ch:appB}
collects the mathematical facts that the book relies on") finds the same
material in the chapter they just read, with different notation for the same
heap.

**Fix.** Decide the split explicitly and state it in the first paragraph of
`ch02` §2.8 and §2.9:
* Appendix B owns the *mathematics*: the Gaussian density, affine maps,
  marginal/conditional, Bayes' rule, Mahalanobis and chi-square, big-O/Omega/
  Theta, heap mechanics, hash tables.
* Chapter 2 owns the *drone-specific use*: the covariance ellipse as a picture
  of an intruder's uncertainty (`def:ch02-covariance-ellipse`,
  `thm:ch02-ellipse-axes`, `ex:ch02-ellipse`, `fig:ch02-gaussian`, the
  "68–95 rule is one-dimensional" pitfall — all of which appB does not have and
  should not get), `alg:ch02-lazypq` (the actual `LazyPQ` the searches call),
  and the state-encoding convention.
* Replace `def:ch02-mean-covariance`, `def:ch02-gaussian`, `def:ch02-big-o`,
  `def:ch02-priority-queue` and the "Bayes' rule" / "Hashing states" paragraphs
  with two-sentence recalls plus `\cref{ch:appB}`.

**Size.** −2.5 to −3 pages in `ch02`; about 12 pointer sentences; delete the
duplicate glossary entry for *lazy deletion*.

---

### 3. Appendix B is unreachable from 21 of the 25 chapters

**Location.** `appB` opening ("Read a section when a chapter sends you here")
versus the fact that only `ch01`, `ch18`, `ch22` and `ch23` ever cite
`\cref{ch:appB}` (5 references in total, plus one in the preface).

**Problem.** Appendix B states that "each result names the chapters that depend
on it", and it does — but the dependency is one-way. `ch03` uses heaps and big-O,
`ch10` complexity, `ch13` a two-dimensional linear program, `ch16`/`ch17`
measure and probability, `ch19` Gaussians and Monte Carlo, `ch21` convexity, KKT
and QPs, `ch25` confidence intervals — and none of them tells the reader that
appB has the prerequisite. Twenty pages of carefully written appendix are
effectively invisible.

**Fix.** One `\cref{ch:appB}` pointer at the first use of appB material in each
of `ch02` (§2.7 vectors, §2.8 Gaussians, §2.9 heaps), `ch03` (§3.8), `ch10`
(§10.6), `ch13` (§13.5 linear program), `ch16` and `ch17` (§.4 problem
statement), `ch19` (§19.3), `ch20` (§20.3), `ch21` (§21.3 and §21.4), `ch25`
(§25.6 statistics).

**Size.** ~12 one-line insertions.

---

### 4. The preface's reading paths contradict Chapter 1 §1.6

**Location.** `frontmatter/preface.tex`, section "How to read it", against
`ch01` §1.6 and `fig:ch01-reading-paths`.

**Problem.** Three discrepancies.
(a) The preface offers the fast path "…\cref{ch:ch09} (\cbs), \cref{ch:ch07}
(the MAPF problem)…" without the caveat that `ch01` §1.6 gives one page later:
"The plan lists CBS before the MAPF overview; if you have never seen a
multi-agent path finding instance, read \cref{ch:ch07} first, it is short and
\cref{ch:ch09} assumes it." The preface therefore sends a first-time reader into
CBS unprepared, and the two front-matter statements disagree.
(b) The preface's list omits `ch02`, which `fig:ch01-reading-paths` includes as
the book's substitute for the plan's "planning reference" item.
(c) Neither the preface nor `ch01` warns that the fast path reaches `ch20`
without `ch18`, although `ch20` §20.5 ("Kalman extrapolation") and its dronebox
("Receives … from the tracker of \cref{ch:ch18}") depend on it.

**Fix.** Rewrite the "How to read it" paragraph to mirror `ch01` §1.6, carrying
both remarks over and adding a third: "the plan's order reaches trajectory
prediction without the Kalman filter; read \cref{ch:ch18} first, or at least its
§18.10 on predicting ahead."

**Size.** One paragraph.

---

### 5. The preface over-promises two conventions the chapters do not deliver

**Location.** `frontmatter/preface.tex`, section "Conventions".

**Problem.** (a) "Inside a chapter you will meet five kinds of coloured boxes:
key idea (green); in the drone system (purple); pitfall (orange); *historical
note (grey)*; and *plain notes carry their own titles*." The `historynote`
environment is used in **2** of 25 chapters (`ch01`, `ch23`); the `notebox`
environment in **1** chapter (`ch18`) plus `appA`. Two of the five box kinds are
effectively not part of the book. (b) "Where the training plan assigns a
priority to an algorithm it is shown as a tag such as `\priority{Essential}`."
The tag appears 31 times in `ch01` and 27 times in `appA`, and **three** times in
all other chapters combined (`ch05`, `ch11`, `ch13`); 20 chapters never show
their own priority.

**Fix.** Either keep the promises — add one `historynote` per part (seven boxes,
material already exists in the further-reading paragraphs) and one
`\priority{}` tag to the opening sentence of each algorithm chapter's §.1 — or,
cheaper and equally honest, reword: "key idea, in the drone system and pitfall
boxes appear in every chapter; a historical note (grey) and a plain titled note
appear occasionally", and "the priority the training plan assigns to each
algorithm is collected in \cref{tab:ch01-map} and \cref{tab:appA-traceability}".

**Size.** One sentence each (cheap route), or 7 boxes + 22 one-line tags.

---

### 6. The book is written in British English; the style guide and preface say American

**Location.** `STYLE_GUIDE.md` §1 ("Plain American English"), the whole
manuscript.

**Problem.** Counts over `chapters/`, `appendices/` and `frontmatter/`:
`centre` 206 / `center` 9; `neighbour` 286 / `neighbor` 15; `behaviour` 17 /
`behavior` 4; `modelling` 9 / `modeling` 0; `minimise` 91 / `minimize` 1;
`linearise` 66 / `linearize` 2; `normalise` 36 / `normalize` 13; `initialise`
35 / `initialize` 2. The book is British in `-our`/`-re` and predominantly
British in `-ise`, so the style guide is simply wrong about what was written.
Worse, the `-ise`/`-ize` split is genuinely mixed (391 vs 481 tokens book-wide)
and splits by chapter: `ch19` 49/11 and `ch21` 50/15 are almost purely `-ise`,
while `ch08` 0/48, `appA` 0/26, `ch16` 8/32 and `ch23` 5/24 are almost purely
`-ize`. Appendix A is written in full American English throughout (`neighbor`,
`labeled`, `maneuver`, `visualization`, `behavior`) next to chapters that are
not. A demanding reviewer opens the book at two random chapters and sees two
different Englishes.

**Fix.** Pick one and record it in `STYLE_GUIDE.md` §1 and in the preface's
Conventions paragraph. The cheapest route consistent with what is on the page is
**Oxford British**: keep `-our`/`-re` (206 `centre`, 286 `neighbour` stay), and
normalise every verb to `-ize`; then fix the 9 `center`, 15 `neighbor`, 4
`behavior` strays and rewrite `appA`'s `maneuver`/`labeled`/`visualization`.
The alternative (full American) is roughly the same amount of work in the other
direction. Either way the front matter must stop claiming a variety the book
does not use.

**Size.** ~700–900 scripted substitutions plus one proofreading pass; two
sentences in `STYLE_GUIDE.md` and the preface.

---

### 7. Notation table: missing rows, one live sign clash, and one clash newly introduced

**Location.** `frontmatter/notation.tex`.

*Assessed against the working tree at commit `78d9370`, "WIP: consistency pass
part 2 in progress". That pass has already landed the goal symbol `\gamma`,
`\dist`, `\mathcal{T}` for the RRT tree, `\mat{W}` for the `ch23` adjacency
matrix, `\mat{P}_f` for the terminal weight, `\omega^{(i)}` for particle
weights, `\vect{u}_{\max}` for the QP bound, and `\eps → h` for the consensus
step size, together with the matching table rows and an extended warnings
paragraph. Items (a)–(e) below are what is left, plus one problem the pass
created.*

**Problem.** The table's stated scope is "every symbol used in more than one
place", and its introduction promises "Where a letter really does carry two
meanings … the table says so rather than pretend otherwise". Five gaps remain
against that promise:

(a) **`\tau_h`, the safety horizon, still has no row of its own.** It is used in
`ch01` (4×), `ch24` (27×) and `ch25` (4×) — the book's spine quantity, the
threshold in `def:ch24-inside` and the trigger of the whole decision logic. The
`\ttc` row now mentions it, but attributes it to `ch01` only; its home is `ch24`.
Add a `\tau_h` row naming `ch24`, plus `R_{\mathrm{safe}}` and `\kappa_p` (the
prediction inflation factor), and a small **Evaluation** block for `ch25`'s
recurring metric symbols (`d_{\min}^{dd}/d_{\min}^{di}`, `\rho_L`,
`n_{\mathrm{rp}}`, `n_{\mathrm{cv}}`, `e_F^{\max}`, `c_{99}`), none of which
appears in any table although `ch25` uses them throughout and `appA`
§A.5.3 lists them as the plan's ten metrics.

(b) **"Relative velocity" has opposite signs in Part I and Part IV — and the
updated table now mis-describes `ch02`.** `def:ch02-closest-approach` (line 487)
writes `p = p_B − p_A`, `v = v_B − v_A`; `def:ch12-relative` and
`eq:ch13-relative` write `v_rel = v_A − v_B`. Both are bolded as *the*
definition of the term and both carry `\index{relative velocity}`. The new
`$t^*$, $t_c$` row reads "time of closest approach and time to collision of
`\pos_rel`, `\vel_rel` … \cref{ch:ch02}", but `ch02` uses neither subscript and
defines the velocity with the opposite sign, so the table now points the reader
at a chapter that contradicts it. Fix: convert `ch02` §2.7 to the Part IV
convention (`\pos_{\mathrm{rel}} = \pos_B − \pos_A`,
`\vel_{\mathrm{rel}} = \vel_A − \vel_B`,
`D(t) = ‖p_rel − t·v_rel‖`) and update `eq:ch02-tca`, `eq:ch02-ttc`,
`ex:ch02-closest-approach`, `fig:ch02-closest-approach` and the docstrings of
`time_of_closest_approach` / `time_to_collision` in `code/ch02_toolbox.py`.

(c) **The `\eps → h` fix in `ch23` traded one collision for a worse one.** `h` is
the prediction-horizon step index across the book's spine — `\hat{\pos}_{T+h}`,
`\mat{\Sigma}_h`, `\mathcal{E}_h`, `\mathcal{B}_h` — 31 occurrences in `ch20`,
25 in `ch24`, and it is what `ch18`'s dronebox hands to the local layer. `ch23`
now uses `h` for the consensus step size in `(\mat{I} − h\mat{L})` (9
occurrences), and the two meanings are listed in two different tables ("$h$ is a
horizon step", `ch20` row; "$h$ & step size of discrete consensus", `ch23` row)
with no cross-warning — and `ch23`'s dronebox feeds `ch24` directly. Use
`\alpha_c`, the alternative `docs/consistency-issues.md` item 8 already offers,
which collides with nothing.

(d) **`\eps` still carries two meanings and the warnings paragraph does not
mention it**: ARA\* inflation (`ch06`, `\astar_\eps` in `ch10`) and numerical
tolerance (`ch13`, `ch21`, `ch22`). Both are listed, in two different tables. The
paragraph is still headed "Two warnings about letters" although it now covers
three (`Q`/`R`, `F`/`H` vs `A`/`C`, and `\mat{W}` vs `\mat{A}`). Retitle it
"Warnings about letters" and add `\eps` — and `h`, if (c) is not taken.

(e) **Three raw `\epsilon` where the book macro is `\eps` (`\varepsilon`)
survive the pass**: `ch06` ×2 (§6.9.2 and §6.12), `ch14` ×1 (`exr:ch14-…`,
line 1339). These print a visibly different glyph from the ε of the surrounding
text. `ch12`, `ch19` and `ch23` have already been fixed.

**Size.** ~7 new table rows, one retitled and extended warning paragraph, ~20
substitutions in `ch02` (plus one figure and one code file), ~9 in `ch23`, 3
one-character fixes.

---

### 8. Chapter 17 breaks the book's own font convention and disagrees with Chapter 16

**Location.** `ch17` throughout (§17.4 onward), against `ch16` and
`frontmatter/notation.tex` ("vectors are bold lower case").

**Problem.** `ch16` writes sampling states as `\state_{\mathrm{init}}`,
`\state_{\mathrm{rand}}`, `\state_{\mathrm{new}}` — bold, 120 occurrences, 0
plain. `ch17` writes the same objects as italic `x_{\mathrm{init}}`,
`x_{\mathrm{new}}`, `x_{\mathrm{rand}}` — 157 occurrences in the chapter, 4 in
`appendices/solutions/ch17-solutions.tex`, and in four figure files
(`figures/ch17/{near,choose-parent,ball-covering,ellipse-transform}.tex`). Two
consecutive chapters on the same algorithm family print the same vector in two
fonts, and `ch17` contradicts the notation table. `docs/consistency-issues.md`
item 4 decided bold states; the in-flight consistency pass (commit `78d9370`)
applied it to `ch16` and to the `\Xfree` row of the notation table — which now
reads "its points are states `\state`" — but not to `ch17`, so the mismatch is
currently *worse* than before the pass and the table is wrong about Part V.
This is the one item of `docs/consistency-issues.md` part 2 still fully open.

**Fix.** Convert `ch17`, its solutions file and its four figures to `\state`.
Keep `c_best`, `c_min`, `\zeta_d`, `\mu(\cdot)` as they are.

**Size.** ~165 scripted substitutions plus a compile and a visual check of four
figures.

---

### 9. The third layer of the architecture has six names

**Location.** Book-wide; canonical names in `ch01` §1.3.1,
`fig:ch01-architecture` and `tab:ch24-layers`.

**Problem.** Counts across `chapters/`, `appendices/` and `frontmatter/`:
"local layer" 76, "safety layer" 43, "local safety layer" 27, "reactive layer"
17, "avoidance layer" 14, "local avoidance layer" 6 — six names for one layer,
183 mentions. Layer 1 has three: "global planner" 66, "global layer" 15, "global
swarm planner" 10. Since the four-layer architecture is the thread that holds
the book together (item D of the brief), and since `ch04`'s dronebox says
"reactive layer" where `ch12`'s says "local safety layer" for the same box in
the same diagram, this is the one terminology slip that actually costs the
reader.

**Fix.** Fix the four canonical names in `ch01` §1.3.1 exactly as
`fig:ch01-architecture` and `tab:ch24-layers` label them — *global swarm
planner*, *prediction layer*, *local safety layer*, *replanning layer* — add one
sentence there permitting the short forms *global planner* and *local layer*
after first use, and normalise: replace "reactive layer", "avoidance layer",
"local avoidance layer" and bare "safety layer" with one of the two sanctioned
forms, except where the text is deliberately contrasting *reactive* with
*deliberative* (`ch01` §1.2, `ch15` §15.1).

**Size.** ~80 substitutions plus one sentence.

---

### 10. Forty-one `\index{}` arguments contain a line break, splitting index headings

**Location.** 41 occurrences in 13 files: `ch03` ×1, `ch05` ×4, `ch07` ×1,
`ch08` ×1, `ch09` ×1, `ch10` ×4, `ch12` ×2, `ch15` ×7, `ch19` ×5, `ch21` ×1,
`ch22` ×7, `ch24` ×5, `appB` ×1. Already documented in `docs/index-audit.md`;
still present in the 9 September build.

**Problem.** The break survives into the `.idx` file, so MakeIndex sorts the two
spellings as different terms. In the printed index (pp. 701–710) this produces
duplicated headings:

```
lazy deletion, 37, 47, 596
lazy deletion, 37, 47, 67, 104, 208
safety horizon, 516
safety horizon, 10, 516
velocity obstacle, 242
velocity obstacle, 238, 240, 261
lower bound            (with sub-entries)
lower bound, 141
```

and files sub-entries such as `artificial potential\nfield!repulsive potential`
under a parent that appears nowhere else. A split index entry is the kind of
defect a reviewer notices in thirty seconds.

**Fix.** Put every `\index{...}` argument on a single source line. Purely
mechanical; `docs/index-audit.md` already lists the exact pairs.

**Size.** 41 one-line edits.

---

### 11. All three appendices have running heads reading "Chapter A/B/C"

**Location.** `Overleaf/searchbook.sty` line 204:
`\renewcommand{\chaptermark}[1]{\markboth{\chaptername\ \thechapter.\ #1}{}}`.
Affects ~55 pages (pp. 582–597 App. A, 598–617 App. B, 618–660 App. C).

**Problem.** `\appendix` in the `book` class redefines `\@chapapp`, not
`\chaptername`, so the header keeps saying "Chapter". Pages read
"Chapter A. The Twelve-Week Study Plan", "Chapter B. Mathematical Refresher",
"Chapter C. Hints and Solutions to Selected Exercises". This survived all 27
chapter reviews because `searchbook.sty` is off-limits to chapter authors
(`docs/finisher-brief.md`), which is exactly why it belongs in a book-level pass.

**Fix.**
```latex
\makeatletter
\renewcommand{\chaptermark}[1]{\markboth{\@chapapp\ \thechapter.\ #1}{}}
\makeatother
```

**Size.** One line.

---

### 12. Chapter 25's running head is too long and collides with the section mark

**Location.** `ch25-experiments.tex` line 1; visible on pp. 560–561 of the
interim build, where `pdftotext` extracts the head as

```
Chapter 25. Evaluating a Hybrid Planner: Experiments, Metrics
25.4and
TheBenchmarks
```

i.e. the left mark overprints the right one.

**Problem.** The layout is `oneside`, so both marks share one line; a
62-character chapter title plus a long section title does not fit. `ch02`,
`ch20` and `ch22` already solve this with `\chaptermark`; `ch11` and `ch17` with
a short `\chapter[...]` title; `ch19`, `ch24` and `ch25` do neither, and `ch25`
is over the limit.

**Fix.** `\chapter[Evaluating a Hybrid Planner]{Evaluating a Hybrid Planner:
Experiments, Metrics and Benchmarks}`, and add short marks defensively to `ch19`
("Nonlinear Filtering") and `ch24` ("The Hybrid Architecture").

**Size.** 3 lines.

---

### 13. Chapter 4 has no `\section{Summary}`; six chapters star the further-reading paragraph

**Location.** `ch04-astar.tex` between the dronebox (§4.9) and
`\paragraph*{Further reading.}`; and `\paragraph*{Further reading.}` in `ch04`,
`ch06`, `ch15`, `ch16`, `ch18`, `ch25` against `\paragraph{Further reading.}` in
the other 19 chapters.

**Problem.** `ch04` is the only chapter whose `summary` box floats without a
section heading, so Chapter 4 is missing a Summary entry in the table of
contents and breaks the "same fixed sequence of sections" that `ch01` §1.6.1
promises the reader will be able to rely on for finding things. The starred
`\paragraph*` is cosmetic but gratuitous.

**Fix.** Insert `\section{Summary}\label{sec:ch04-summary}` before
`\begin{summary}` in `ch04`; unstar the six paragraphs.

**Size.** 7 lines.

---

### 14. Two droneboxes break the pattern the other twenty-three keep

**Location.** `ch11` dronebox (§11.11) and `ch24` dronebox (§24.14).

**Problem.** (a) `ch11` is the only chapter whose dronebox names neither its
study-plan week nor `\cref{ch:appA}`, although `appA` §A.4.5 assigns it to
Week 5 ("Read \cref{ch:ch11} to know how M\* and Push-and-Swap differ from
CBS"). Every other dronebox does. (b) `ch24`'s dronebox says it is "the executive
that the droneboxes of ch03, ch04, ch05, ch07, ch09, ch10, ch13, ch14, ch18,
ch20, ch21, ch23 have been pointing to" — omitting eleven chapters whose
droneboxes do point at `ch24` (ch02, ch06, ch08, ch11, ch12, ch15, ch16, ch17,
ch19, ch22, ch25). The reader of, say, `ch16` finds their chapter written out of
the payoff.

**Fix.** Add one closing sentence to `ch11`'s dronebox ("This is the optional
second half of Week 5 of the study plan (\cref{ch:appA}); its coding exercise is
\cref{exr:ch11-coding}."). Change `ch24`'s list to "the droneboxes of every
earlier chapter".

**Size.** 2 sentences.

---

### 15. The style guide's length rule no longer describes the book

**Location.** `STYLE_GUIDE.md` §2, "Length. 12–18 pages per chapter".

**Problem.** Measured from the build, every chapter is **18–24** pages (mean 21;
`ch13`, `ch18`, `ch20`, `ch24` at 24), for 526 pages of chapters and 710 pages
total. Twenty of 25 chapters exceed the stated ceiling. The production log
records that the target was relaxed during drafting ("Essential chapters get
more space, 16–22 pp, up to 24") but the style guide was never updated, so every
future reviewer will re-raise length as a defect and every author will be
measured against a rule nobody follows.

**Fix.** Update §2 to the length that was actually agreed, and say which chapters
are allowed the upper end. The cuts in items 1 and 2 recover ~6 pages, which
brings `ch02`, `ch04`, `ch08` and `ch09` back inside it.

**Size.** One paragraph in `STYLE_GUIDE.md`.

---

## Optional suggestions

1. **`ch13` §13.2 retells `ch12` §12.7.** The corridor dance in `ch13` and the
   oscillation experiment in `ch12` make the same point. `ch13` is the better
   prose and `ch12` has the numbers (51 sign changes in 100 steps). Open `ch13`
   §13.2 with one sentence citing `\cref{sec:ch12-oscillation}` and drop the
   re-narration of why plain VO oscillates; keep both figures, which show
   different things.
2. **`thm:ch12-cone` re-proves `thm:ch02-tangents`.** The half-angle
   `arcsin(R/d)` is proved from scratch in `ch12` although `ch02` proved it and
   `ch12` cites it two lines later. Replace the proof with three lines that apply
   `thm:ch02-tangents` in the relative frame.
3. **The intruder and the goal are the same colour.** `searchbook.sty` line 50
   sets `sbGoal = sbRed` and line 55 sets `sbIntruder = sbRed`. In
   `fig:ch01-scenario`, `fig:ch05-drone-replanning` and `fig:ch24-scenario` the
   two appear together and cannot be told apart by colour. Give `sbIntruder` its
   own hue (or a consistent marker shape, e.g. a triangle) and say so in
   `STYLE_GUIDE.md` §4.
4. **Part openers.** The eight `\part{}` pages carry nothing but a title. Half a
   page each — what the part assumes, what it delivers, which layer it builds —
   would make the book navigable by part as well as by chapter, and would give
   the seven historical notes of required item 5 a natural home.
5. **Label the roadmap.** All 25 chapters end §.1 with a roadmap paragraph, but
   only `ch03`, `ch08`, `ch10` and `ch11` label it `\paragraph{Roadmap.}`. Label
   the other 21.
6. **Mention `code/run_all.py`** in the preface's "The code" section and in
   `appA`'s "How the book's code files support the exercises" note; it is the
   one command that verifies the whole book's code and it is named nowhere in
   the book.
7. **Point the exercises at Appendix C.** `\cref{ch:appC}` is referenced only
   from the preface. One line at the head of each `\section{Exercises}` ("hints
   and solutions for a selection of these are in \cref{ch:appC}") costs 25 lines
   and makes 60 pages of solutions discoverable.
8. **Part V is a cul-de-sac.** `ch16`/`ch17` are referenced downstream only by
   `ch24`. Two pointers would connect them: from `ch21` (MPC as the smoother that
   turns an RRT\* polyline into a flyable trajectory) and from `ch25` (a
   sampling-based row in the baseline table).
9. **`ch15` §15.9 and `ch23` overlap** on flocking, velocity consensus and
   formation springs. It is well signposted and no cut is required, but the
   Reynolds paragraph would sit more naturally in `ch23` §23.9 with a pointer
   back from `ch15`.
10. **`appA` reuses `\difficulty{}` for weekly load**, which the preface defines
    as exercise difficulty. It is explained locally, but a separate macro
    (`\load{}`) would remove the collision.
11. **Delete or cite `ren2007distributed`**, the only uncited entry among 188
    bibliography keys; `ch23`'s further reading is the obvious home.

---

## Readability

Measured on the LaTeX source with math, floats, listings and pseudocode stripped
(≈290 sentences per chapter). Book mean: **27.7** words per sentence.

**Markedly harder than the rest** — and worth one sentence-splitting pass each:

| Chapter | mean | 90th pct | sentences > 40 words | semicolons/sentence |
|---|---|---|---|---|
| `ch24` Hybrid architecture | 30.9 | 54 | 24.7 % | 0.36 |
| `ch13` RVO and ORCA | 30.1 | 50 | 23.7 % | 0.17 |
| `ch15` Potential fields | 30.0 | 53 | 23.0 % | 0.26 |
| `ch22` MILP | 29.6 | 52 | 20.8 % | 0.23 |
| `ch25` Experiments | 29.4 | 50 | 23.5 % | 0.28 |
| `ch19` Nonlinear filters | 29.2 | 48 | 21.9 % | 0.33 |

`ch24` is the worst offender and matters most: it is the chapter the whole book
walks towards, and a quarter of its sentences run past forty words. §24.4
(decision logic), §24.5 (safety horizon) and §24.8 (formation and communication
constraints) are where the semicolon chains concentrate. `ch18` and `ch20` do not
top the sentence-length table but carry the heaviest jargon load in the book
(4.3 % and 3.8 % of words are eleven letters or longer, against a 2.5 % book
median); both would benefit from spelling out a few nominalisations.

**Easiest and clearest**, for calibration: `ch01` 23.4, `ch04` 24.1, `ch08` 24.6,
`ch03` 25.3, `ch02` 25.4. These five are the register the rest of the book should
be edited towards; the target is not "shorter" in the abstract but "as short as
Chapter 4".

---

## What must be kept

Five sections to protect from any revision, plus two runners-up.

1. **`ch01` §1.1, "The problem: many drones, one airspace, and a stranger"**
   (pp. 23–27). The factory-roof scenario, `def:ch01-planned-conflict` and
   `def:ch01-unexpected-obstacle`, `ex:ch01-scenario` with `tab:ch01-trace`, and
   the "An intruder is not a wall" pitfall. This is the best opening section in
   the manuscript: it states the whole book's problem in two pages, in numbers, and
   the distinction it draws — a conflict is a *fact*, an encounter is a
   *prediction* — is the one idea the reader carries through 700 pages.
2. **`ch10` §10.2, "The idea in plain words"** (the band instead of a point; two
   levels, one bound; the low level returning its own lower bound so that the
   high-level ruler stays honest). The clearest explanation of bounded-suboptimal
   search I have read anywhere, and its `keyidea` box is exemplary.
3. **`ch13` §13.2, "The idea in plain words"**, with `fig:ch13-idea`. The
   corridor dance → "each steps half as far and keeps that step" → the ORCA
   half-plane, in one page, ending in a `keyidea` that actually states the
   theorem. If any cutting is done in Chapter 13, cut elsewhere.
4. **`ch02` §2.7, "A geometry toolkit"**. Every primitive stated, proved,
   evaluated on real numbers, implemented in the chapter's code file, and
   explicitly linked forward to the chapter that consumes it
   ("this cone is the velocity obstacle of \cref{ch:ch12}"). This is how a
   toolbox chapter should be written, and it is the model that required items 2
   and 3 should be applied *around*, not to.
5. **`ch24` §24.11, "What guarantees survive"**, especially
   `thm:ch24-separation` — the `ℓ/√2` physical-separation bound with its full
   proof. It is the one result in the book that belongs to the integration rather
   than to a cited paper, it is correctly scoped, and the honest ledger that
   follows it (what survives, what does not: deadlock-freedom, optimality after
   deviation, safety against an adversary) is exactly the intellectual honesty the
   preface promises.

Runners-up, also to be preserved: **`ch25` §25.3 "Metrics"** with its two
pitfalls (collision rate without minimum separation; comparing computation times
across machines) — the section that turns the training plan's ten metrics into
something a thesis committee would accept; and **`appA` §A.4, the week notes**,
whose *Focus / Build / Done when / Traps / Exercises* rhythm is a genuinely
unusual and useful piece of instructional design that no chapter review would
have produced.

Two structural properties must also be preserved through the revision: the
**dronebox in every chapter naming its layer and its study-plan week** (item 14
exists only to restore it in `ch11`), and the **`ch01` → `ch24` → `ch25` research
thread**, in which all seven open directions named in `ch01` §1.5 come back in
`ch24` §24.13 with a formulation and an evaluation, and are measured by the
experiment matrix of `ch25`. That thread is the reason this manuscript reads as a
book and not as twenty-five surveys.
