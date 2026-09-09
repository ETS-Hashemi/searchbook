# Review of Chapter 16 (Rapidly-Exploring Random Trees) - round 1

Reviewed artefacts: `Overleaf/chapters/ch16-rrt.tex` (1337 lines), figures
`Overleaf/figures/ch16/{voronoi,primitives,tree-snapshots,jagged,connect,iterations,shortcut,scene3d}.tex`,
code `Overleaf/code/ch16_rrt.py` and `Overleaf/code/figures/gen_ch16_tree.py`,
`Overleaf/appendices/solutions/ch16-solutions.tex`, `Overleaf/appendices/glossary/ch16-terms.tex`,
`Overleaf/bib/ch16-extra.bib`, against `STYLE_GUIDE.md` §9, `docs/specs/ch16.md` and
`docs/core-idea.txt` (Week 8).

Build: `./build.sh ch16-rrt` exits 0, no `!` errors, **no overfull boxes above 15 pt**, no
undefined labels or citations belonging to this chapter (only the expected `??` for
`ch:ch11`, `ch:ch20`, `ch:ch21` from other chapters). Chapter body = printed pages
158-177, i.e. **exactly 20 pages** (front matter excluded) - at the review limit, above the
spec target of 13-15 pages, but every page carries required content, so no cuts are
*required*; see the suggestions.

Code: `python3 code/ch16_rrt.py` passes in 3.6 s; `python3 code/figures/gen_ch16_tree.py`
regenerates all eight figures in 19 s. I re-ran both and re-derived the worked example,
the 100-seed statistics, the Voronoi percentages, the 3D and kinodynamic runs, the
shortest-path reference (16.72 with zero clearance, 17.198 with clearance 0.075 - both
confirmed analytically) and both proofs. Everything checks out except the items below.

## Verdict

**Minor revision.** The mathematics is correct (I verified both proofs line by line and the
sharper margin of Exercise 16.3(b) is genuinely the tight one), completeness against the
spec and the Week-8 plan is total, and almost every number in the text is reproduced by the
committed code. The required changes are seven local fixes: one wrong count, two claims the
code does not support, two pseudocode/statement precision defects, one missing reference
number in the code output, and float drift in §16.7.

## Required changes

1. **Location:** §16.5 (`sec:ch16-example`), lines 396-398, "the first panel of
   \cref{fig:ch16-snapshots} shows only $17$ vertices after $50$ iterations: $33$
   extensions were rejected."
   **Problem:** the code does not reproduce 33. The tree holds 17 vertices after 50
   iterations, but one of them is the root, so only 16 were added and **34** extensions were
   rejected. (Verified: instrumenting `rrt(world,(1,1),(9,9),eta=0.5,p_goal=0.05,
   r_goal=0.5,seed=1)` gives 16 accepted / 34 rejected in the first 50 iterations, and
   `gen_ch16_tree.py` prints `{50: 17}` vertices.)
   **Fix:** write "$34$ extensions were rejected" (or "$16$ of $50$ extensions succeeded").
   **Category:** A.

2. **Location:** §16.3, lines 267-269 ("the self-test ... checks exactly this case, a wall
   of thickness $0.02$ with $\delta=0.05$, at forty segment angles") and the pitfall
   *Testing the vertices but not the segments*, lines 1073-1075 ("the inflated test catches
   it at every angle").
   **Problem:** the self-test (`code/ch16_rrt.py` line 495, `for y in np.linspace(0.3, 9.7,
   40): assert not w.segment_free([1.0, y], [7.0, y + 0.3])`) sweeps 40 *offsets* of one and
   the same direction $(6,0.3)$; it tests a single angle. The text claims something the code
   does not check.
   **Fix:** either (a) reword both places to "at forty crossings of the wall" / "the inflated
   test catches it at every offset tested", or (b) better, make the code match the text by
   replacing the loop with a sweep of angles through a point inside the wall, e.g.
   `for th in np.linspace(0.0, np.pi, 40, endpoint=False):`
   `    e = 2.0*np.array([np.cos(th), np.sin(th)]); c = np.array([4.01, 5.0])`
   `    assert not w.segment_free(c - e, c + e)`
   and re-run the self-test.
   **Category:** A.

3. **Location:** §16.5, lines 422-425, "the shortest path in $\Xfree$ ... has length $16.72$
   (in the limit of zero clearance; with a clearance of $0.075$ it has length $17.20$), so
   the \rrt path is $43\,\%$ longer."
   **Problem:** the self-test prints only the clearance-0.075 reference (17.198); 16.72 is a
   hand-computed number that no committed code produces, and it is the baseline of the
   "43 %" claim, while §16.6.2 measures "65 %" against 17.20. Both values are correct (I
   confirmed $\sqrt{29}+2+\sqrt5+2+\sqrt{26}=16.7203$), but the guide requires quoted
   numbers to come from the code.
   **Fix:** add two lines to `_self_test()` (or to `gen_ch16_tree.py`) that print the
   zero-clearance reference and assert it, e.g.
   `w0 = World([0,0],[10,10], boxes=[([3,0],[5,6]),([6,4],[8,10])], radius=0.0, delta=1e-6)`
   `_, ref0 = visibility_shortest_path(w0, start, goal, offset=1e-6)   # 16.720`
   (verified here: 16.7203, via the corners $(3,6),(5,6),(6,4),(8,4)$ as the text says), and
   state in the text which baseline each percentage uses ("$43\,\%$ longer than the
   zero-clearance optimum, $39\,\%$ longer than the $17.20$ reference").
   **Category:** A.

4. **Location:** §16.8.2, lines 968-971 ("about $0.02$~ms for $n=10^{3}$ vertices,
   $0.2$~ms for $10^{4}$ and $2.3$~ms for $10^{5}$") and §16.8.3, line 1018 ("The self-test
   runs in about two seconds").
   **Problem:** no code in the repository measures the nearest-neighbour timings, and the
   self-test takes 3.6 s on this machine, not "about two". Numbers in the text must be
   produced by running the code (§3 and §6 of the guide).
   **Fix:** add a tiny benchmark to `ch16_rrt.py` that is run by the self-test, e.g.
   `for n in (10**3, 10**4, 10**5): t = Tree(np.zeros(3), n); t.V = rng.random((n,3)); t.n = n;`
   time 1000 `t.nearest(q)` calls and print the mean in ms; quote its output. Change
   "about two seconds" to "a few seconds" (or print and quote the measured value, which the
   test already computes at line 604).
   **Category:** A.

5. **Location:** `alg:ch16-kino` (\cref{alg:ch16-kino}), lines 754, 762, 766 and 771.
   **Problem:** three precision defects in the pseudocode. (i) Line 766 evaluates
   $\rho(\mathrm{best},\state_{\mathrm{rand}})$ while $\mathrm{best}=\KwNil$ on the first
   pass; the convention $\rho(\KwNil,\cdot)=+\infty$ is never stated. (ii) Line 771 labels
   the new edge $\acc_j$, the loop variable of the *finished* inner loop, so a literal
   implementation stores the control of the last candidate instead of the best one - the
   code (`best_a`) does it correctly. (iii) The input list on line 754 omits
   $p_{\mathrm{goal}}$ and the metric weight $w_{\mathrm{v}}$, both used in the body.
   **Fix:** add "with $\rho(\KwNil,\cdot)=\infty$" to line 762 or as a `\tcp*`; write
   "edge label $\acc_{\mathrm{best}}$" on line 771 and store the control together with the
   state on line 767; add $p_{\mathrm{goal}}$ and $w_{\mathrm{v}}$ to `\KwIn`.
   **Category:** A.

6. **Location:** \cref{thm:ch16-complete} (Theorem, probabilistic completeness), hypothesis
   on lines 448-450.
   **Problem:** the theorem only assumes "a path $\tau$ ... with clearance $\delta_c>0$",
   but the proof chooses $m\le\lceil \mathrm{length}(\tau)/\nu\rceil+1$ waypoints along
   $\tau$, which needs $\tau$ to be rectifiable; a continuous path in a bounded box may have
   infinite length, and then $m$ is not finite and the bound $m/(np)$ is vacuous.
   **Fix:** state "Suppose there is a path $\tau$ **of finite length** from
   $x_{\mathrm{init}}$ to $x_{\mathrm{goal}}$ with clearance $\delta_c>0$", and optionally
   add one clause in the proof noting that any path with clearance $\delta_c$ can be replaced
   by a polygonal one of finite length inside the same tube.
   **Category:** A.

7. **Location:** floats of §16.7: `\begin{algorithm}` at line 751 (kinodynamic \rrt),
   `\begin{algorithm}` at line 805 (post-processing) and `\begin{figure}` at line 875
   (3D scene).
   **Problem:** all three drift about three pages past the text that discusses them.
   In the built PDF, Algorithm 16.3 is referenced on printed page 167 and typeset on 170,
   Algorithm 16.4 is referenced on 168 and typeset on 171, and Figure 16.8 is referenced on
   169 and typeset on 172 - i.e. the kinodynamic algorithm and the shortcutting algorithm
   appear inside §16.8 "Implementation notes", far from their walkthroughs. A reader working
   alone has to page back and forth.
   **Fix:** move each float block a page earlier in the source (put the `algorithm`
   environment immediately *before* the paragraph that first cites it) and use `[!t]`
   instead of `[htb]` for `alg:ch16-kino`, `alg:ch16-shortcut` and `fig:ch16-scene3d`;
   rebuild and check that each now sits on the page of, or the page after, its first
   reference.
   **Category:** G.

## Suggestions

* **Length (20 pages, spec target 13-15).** Nothing must be cut, but about 1.5 pages of
  duplication could go if the editor wants the chapter shorter: (i) §16.8.3, lines
  1018-1026, recites eight things the self-test checks, each of which is already stated
  where it matters (§16.3 for the thin wall, §16.6.1 for the median ordering, §16.7.3 for
  smoothing) - one sentence plus a pointer would do; (ii) the opening paragraph of §16.9
  (lines 1104-1114) restates the "Prefer when" row of \cref{tab:ch16-comparison} almost word
  for word; (iii) the caption of \cref{tab:ch16-trace} (lines 361-366) explains the stuck
  regime that the following paragraph explains again; (iv) §16.6.2 repeats the mean, standard
  deviation, minimum and maximum that \cref{tab:ch16-connect} already gives.
* §16.1, line 43: "the grid has $10^{14}$ cells" while \cref{tab:ch16-gridsizes} says
  $5.0\times10^{14}$ for that row; write $5\times10^{14}$.
* §16.2, lines 114-116, and the `keyidea` box: "the probability that $v$ is extended equals
  the area of its region" - it is the probability that $v$ is *selected*; the extension may
  still be rejected by the collision check (the worked example makes exactly this point ten
  lines later). One clause ("selected for extension") removes the tension.
* \cref{thm:ch16-suboptimal}: name the "mild regularity assumptions" of Karaman and Frazzoli
  (goal region with non-empty interior, an optimal path with weak clearance, fixed $\eta$) so
  the reader can check them against a map.
* `World.point_checks` already counts the point tests but is never printed; printing it in
  the self-test would make the "$3\,965$ points" of §16.5 (which I confirmed) directly
  visible, at the cost of one line.
* Notation: $\rho$ is used in \cref{eq:ch16-metric} for the weighted state metric, while
  `frontmatter/notation.tex` line 136 assigns $\rho$, $\rho_0$ to clearance and influence
  distance in \cref{ch:ch15}. Ask the editor to add a ch16 row with $\eta$, $\delta$,
  $p_{\mathrm{goal}}$, $r_{\mathrm{goal}}$ and $\rho$ (state-space metric), or rename the
  metric $d_{w}$.
* Exercises: the spread is 1,1,2,2,2,2,2,3. Promoting \cref{exr:ch16-shortcut} (part (c) is a
  genuine topological argument) or \cref{exr:ch16-completeness} to `\difficulty{3}` would
  widen it. The solutions appendix covers 4 of 8; \cref{exr:ch16-gridsizes} and
  \cref{exr:ch16-trace} are pure arithmetic and cheap to add.
* §16.7.3 is titled "shortcutting and smoothing" but smoothing proper (fitting a bounded-
  velocity curve and re-checking it) gets one sentence. Two more sentences - corner rounding
  radius, re-collision-check, pointer to \cref{ch:ch21} - would honour the title.

## What must be kept

The completeness proof is the best thing in the chapter and must survive revision unchanged
apart from item 6: the ball chain with $\nu=\min(\eta/3,\delta_c/4,r_{\mathrm{goal}})$, the
three-term triangle inequality that forces \textsc{Steer} to return the sample exactly, the
convexity argument that puts the whole segment inside the clearance tube, and the
domination by a sum of geometrics are all correct, and the three bullets afterwards (role of
$\eta$, role of the goal bias, narrow passages with the $(1/w)^{d}$ law) are exactly what a
lone reader needs. Keep \cref{thm:ch16-resolution} and the $r+\delta/2$ inflation: it is
correct, it is carried consistently into `segment_free`, into \cref{fig:ch16-primitives} and
into the pitfalls, and Exercise 16.3(b) sharpens it to $\sqrt{r^{2}+\delta^{2}/4}$, which is
indeed the tight margin. Keep the worked example and its reproducibility: the trace table
matches the code line for line, and the snapshots, the jagged-path figure, the 100-seed
table, the 3D scene and the kinodynamic run are all regenerated by committed scripts.
Keep the honest goal-bias result ($p_{\mathrm{goal}}=0.5$ is worse than no bias at all) with
its matching pitfall box, \cref{tab:ch16-gridsizes} and \cref{tab:ch16-comparison}, which
between them answer the Week-8 milestone, the "only the bounds change" 3D section, and the
`dronebox` on splicing a local \rrt into a global grid plan.

## Response to review (round 1)

All seven required changes are applied; the chapter builds with status 0, no
errors and no overfull boxes above 15 pt, and `python3 code/ch16_rrt.py`
passes (4.5 s). Every number quoted below is printed by the self-test.

**Required 1 (wrong count, 33 vs 34).** Fixed. Section 16.5 now reads "shows
only $17$ vertices after $50$ iterations: $16$ of the $50$ extensions
succeeded and $34$ were rejected."

**Required 2 (forty angles).** Fixed in the code, option (b) of the review.
`_self_test()` now sweeps forty *directions* through the point $(4.01,5.0)$
inside the thin wall (`for th in np.linspace(0.0, np.pi, 40, endpoint=False)`)
*and* keeps the forty parallel crossings. Section 16.3 now says "at forty
segment angles through a point inside the wall and at forty parallel
crossings of it"; the pitfall box says the inflated test "rejects every one
of the forty directions and forty crossings it tries".

**Required 3 (16.72 not produced by the code; two baselines).** Fixed both
ways. The self-test now computes the zero-clearance reference itself: it
solves the visibility graph of a world with a small corner offset, snaps the
interior waypoints back onto the exact box corners and measures the
polyline, printing `zero-clearance shortest path length 16.720 via (3,6)
(5,6) (6,4) (8,4)` next to the clearance-0.075 value 17.198. Section 16.5
now names both baselines: "$16.72$ in the limit of zero clearance, and
$17.20$ when the corners are rounded off by the clearance $0.075$ of the
collision checker; the self-test prints both. The RRT path is $43\,\%$
longer than the zero-clearance optimum and $39\,\%$ longer than the $17.20$
reference." Section 16.6.2 likewise names its baseline ($65\,\%$ above
17.20, $70\,\%$ above 16.72).

**Required 4 (unmeasured timings; "two seconds").** Fixed. The self-test now
times 200 `nearest()` queries on trees of $10^3$, $10^4$ and $10^5$ random
3D vertices and prints the means (one run prints `n=1000 0.046 ms, n=10000 0.325 ms,
n=100000 2.932 ms`; repeated runs vary by up to a factor of two). Section
16.8.2 quotes "about $0.04$~ms ... $0.3$~ms ... $3$~ms ... means of $200$
queries, timed and printed by the self-test ... reproducible to within a
factor of two on any other [machine]". Section 16.8.3 now says the self-test
"runs in a few seconds (it prints its own runtime, $4.5$~s here)" and the
eight-item recitation of the checks is compressed to one sentence
(suggestion (i)).

**Required 5 (kinodynamic pseudocode).** All three defects fixed in
`alg:ch16-kino`: the `\KwIn` list gains the goal bias $p_{\mathrm{goal}}$ and
the velocity weight $w_{\mathrm{v}}$; the initialisation line now reads
"$\mathrm{best}\gets\mathrm{Nil}$; $\acc_{\mathrm{best}}\gets\mathrm{Nil}$"
with the comment "convention $\rho(\mathrm{Nil},\cdot)=+\infty$"; the winning
control is stored as $\acc_{\mathrm{best}}$ and the new edge is labelled
$\acc_{\mathrm{best}}$, not $\acc_j$.

**Required 6 (rectifiability).** Fixed. The hypothesis of
`thm:ch16-complete` now reads "Suppose there is a path $\tau$ of finite
length from $x_{\mathrm{init}}$ to $x_{\mathrm{goal}}$ with clearance
$\delta_c>0$", and the proof adds the note that finite length costs nothing:
the image of a path with clearance $\delta_c$ is compact, finitely many
balls of radius $\delta_c/2$ centred on it cover it, and joining the centres
of consecutive overlapping balls gives a polygonal path of finite length in
the same tube with clearance at least $\delta_c/2$. Nothing else in the
proof changed.

**Required 7 (float drift in Section 16.7).** Improved but not perfect. The
three floats were moved next to the paragraphs that cite them and given
aggressive placement options (`[!htb]` for `alg:ch16-kino` and
`alg:ch16-shortcut`, `[!t]` for `fig:ch16-scene3d`). All three now stay
inside Section 16.7 instead of drifting into Section 16.8: Algorithm 16.3 is
referenced on the printed page 168 and typeset on 170, Algorithm 16.4
referenced on 169 and typeset on 171, Figure 16.8 referenced on 171 and
typeset on 172 (the figure now meets the "page of, or page after" rule; the
two algorithms are one page short of it). The residual two-page lag is
physical, not a placement-option problem: Section 16.7 carries eight floats
(Algorithm 16.2, Figures 16.5-16.6, Table 16.3, Algorithms 16.3-16.4,
Figures 16.7-16.8) over about four pages of text, and pages 169-170 are
already full of floats, so with `!` placement LaTeX still cannot fit a
25-line algorithm earlier. Removing the lag entirely would require merging
Figures 16.5 and 16.6 into one float, which loses a figure the specification
asks for; I preferred to keep the content.

### Suggestions

Applied: the grid size in Section 16.1 is now $5\times10^{14}$ (matching
`tab:ch16-gridsizes`); Section 16.2 and the key-idea box now say a vertex is
*selected* with probability equal to its Voronoi area and extended only if
the step is collision-free; `thm:ch16-suboptimal` now names the
Karaman-Frazzoli assumptions (goal region with non-empty interior, an
optimal path with weak clearance, fixed $\eta$); `World.point_checks` is
printed and the text says so ("a counter the self-test prints"); Section
16.7.3 gains two sentences on corner rounding, re-checking the rounded arc
and the pointer to `ch:ch21`; `exr:ch16-shortcut` is promoted to difficulty
3; solutions were added for `exr:ch16-gridsizes` and `exr:ch16-trace` (both
verified against the code: $1.536\times10^{8}$ cells, $153.6$~MB,
$5.5\times10^{12}$ velocity-augmented states, $0.56$~MB for a
20 000-vertex tree; iterations 11 and 12 both select vertex 6 and are
rejected by the wall, $x_{\mathrm{new}}=(3.335,3.076)$ and $(3.145,3.331)$),
so 6 of 8 exercises now have solutions. Duplication trims (i)-(iv) were
applied: the self-test recitation, the opening of Section 16.9, the caption
of `tab:ch16-trace` and the repeated mean/sd in Section 16.6.2.

Not applied: the notation row for $\eta,\delta,p_{\mathrm{goal}},
r_{\mathrm{goal}},\rho$ in `frontmatter/notation.tex` - that file belongs to
the editor and is outside this chapter's file set; the request is passed on
unchanged. Length: the chapter is now 21 printed pages. The required
additions (both baselines, the finite-length note, the named regularity
assumptions, two `\KwIn` entries, the smoothing sentences) add about a page
and the trims give back about a third of it; nothing required was removed to
save space.
