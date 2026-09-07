# Review of Chapter 3 (Dijkstra's Algorithm) - round 2

## Verdict

**Minor revision.**

The four required changes of round 1 were all applied, and applied correctly; I re-verified each
one against the file and against the code, and I re-verified the whole chapter from scratch. Two
new items remain, both strictly local: one clause missing from the *newly added* half of the proof
of Corollary 3.8 (category A), and one dangling cross-reference introduced by the round-1 repair of
the Chapter 2 pointer (category F/G). Nothing else in A-E is open.

What I checked this round.

* **Round-1 items.** (1) `cor:ch03-ucs` now proves its second claim in the body of the proof and
  Exercise 3.3 is reduced to the tie case, the upper bound and zero-cost termination, with a hint -
  correct, except for the gap in Required change 1. (2) `thm:ch03-true-distance` item 1 now carries
  the hypothesis `\delta(s,t)<\infty`, the converse says both summands are finite because their sum
  is, and the counterexample that makes the hypothesis necessary is recorded - correct and complete.
  (3) The "best-first skeleton of Chapter 2" is gone; Section 3.3 now names what is actually reused,
  and Section 3.4 cites `alg:ch02-lazypq` - but see Required change 2. (4) The `dronebox` no longer
  restates Section 3.1: it now points back to `sec:ch03-motivation`, names the consumers, states
  what the algorithm does not do, and links `\dstarlite` and Week 1. The applied suggestions
  (fourth `pitfall` box on float equality, multi-source wave started from free cells that touch an
  obstacle, two-case bidirectional argument, empty `\Open` as `\min=\infty`, the "for this example
  only" clause in Example 3.9, the hint in Exercise 3.3) are all in place and all correct.
* **Build.** `./build.sh ch03-dijkstra` -> status 0, `build/only-ch03-dijkstra.pdf`, 40 pages.
  No `!` errors. No undefined reference or citation belonging to Chapter 3 (only the expected
  cross-chapter `??`). One overfull box, 6.91 pt at line 396, below the 15 pt threshold.
* **Length.** Chapter body = pp. 13-31 of the single-chapter PDF = **19 pages**, inside the 20-page
  ceiling, above the spec's 12-14. I could not find a second block of genuine padding after the
  round-1 cut; the residual overlap is named in Suggestion 2 as optional, and **no cut is required**.
* **Code.** `python3 code/ch03_dijkstra.py` -> `all self-tests passed (0.04 s)`. I recomputed
  independently, not by re-reading the self-test: the 4-connected grid run (19 pops, **0 stale**,
  `g(T)=8`, settling order and costs exactly as printed in Section 3.5, open cells `(2,3)`/`(3,2)`/
  `(3,3)` at 9/9/10, `(3,4)` undiscovered), all three panels of `fig:ch03-backward-heuristic`
  (forward table, `h*` table, and the nine cells with `g+h*=8`, which are exactly the path cells),
  `h*(3,3)=2` against 4 for a plain forward run from `T`, the eight cells where the forward and
  backward tables differ (exactly the eight slow cells - the list in the solution to Exercise 3.6(b)
  is right, value by value), the 8-connected instance of Exercise 3.5 (`\delta(S,T)=6+\sqrt2`,
  24 pops, 19 expansions, **5 stale** - the exercise's premise holds), the Exercise 3.1 variant with
  `c(B,E)=4` (11 pops, 4 stale, `\delta(A,G)=8` along `A,B,E,G`, `\delta(A,F)=9` - the appendix
  solution matches exactly), and the multi-source obstacle-distance table (`(0,0)` gets 3, cells
  touching an obstacle get 0, so "one less than the distance to the nearest blocked cell" is right).
  Every number in `figures/data/ch03-expansions.dat` still matches the text: 7498.5 -> "7,499",
  7437.7 -> "7,438", 7436.6 -> "7,437", 165.489 -> "165.5", 85.252 -> "85.3", 3020.4 -> "3,020"
  and 3020.4/7437.7 = 41 %, 1856.9 -> 7498.5 = "four times as many".
* **Mathematics.** Lemma 3.6, Theorem 3.7, Theorem 3.10 and Theorem 3.11 are correct as stated and
  proved; the `|E|+1` push/pop count, the `O((|V|+|E|)\log|V|)` bound, the Fibonacci-heap
  `O(|E|+|V|\log|V|)`, the dense-graph `O(|V|^2)` array version, the `2(d/2)^2=d^2/2` area argument
  (and the quarter in 3D), the BFS two-level argument and the "at least two slow cells, 12 or more"
  bound (which is tight: `(2,0)->(2,1)->(3,1)->(4,1)->(4,2)->(4,3)->T` costs exactly 12) all check
  out. `\pi`-level detail: the negative-edge trace of Example 3.9 and the `2\le0` failure of
  step (iii) are exactly right.
* **Counts.** 6 figures (all `\cref`-referenced, generated ones committed with their generators),
  2 tables, 2 algorithms, 2 listings (verbatim from the source file, 30 and 27 lines), 4 `pitfall`
  boxes, 40 distinct `\index` entries, 8 exercises graded 1,1,2,2,2,2,3,3 with the Week-1 coding
  exercise and the backward-heuristic exercise both present, 15 glossary terms, 4 solutions.
  `\SetKwFunction{DijkstraSearch}`/`{DijkstraBackward}` are unique in the book; no duplicate
  `ch03-` label anywhere.
* **Citations.** All seven keys resolve and I vouch for all seven: `dijkstra1959note` (Numer. Math.
  1:269-271, 1959), `cormen2009clrs`, `russell2020aima`, `hart1968formal` (IEEE TSSC 4(2):100-107,
  1968), `pearl1984heuristics`, `fredman1987fibonacci` (JACM 34(3):596-615, 1987),
  `felner2011position` (SoCS 2011). No fabricated reference; the further-reading paragraph is intact.
* **Spec.** Every "must cover" item of `docs/specs/ch03.md` is present, including the two required
  examples, the negative-edge counterexample, the four variants, the generated expansions figure,
  the drone box and the eight exercises. Week 1 of the training plan is covered for the Dijkstra
  half (graph search, exact/consistent/admissible heuristics via Theorem 3.11, space-time
  admissibility, open/closed visualisation in Exercise 3.7(a)).

## Required changes

1. **Proof of Corollary 3.8 (`cor:ch03-ucs`), `chapters/ch03-dijkstra.tex` lines 502-508** - the
   second half of the proof added in round 1.
   *Problem (category A).* The step "As in step (ii) of the proof of `\cref{thm:ch03-invariant}`,
   the predecessor of `y` on that path is settled and has relaxed the edge into `y`" does not
   follow as written. In the early-exit algorithm one settled vertex is **never expanded**: the
   target `t` itself, because line~`\ref{alg:ch03-dijkstra:exit}` breaks immediately after
   line~`\ref{alg:ch03-dijkstra:settle}`. If the predecessor of `y` were `t`, it would be settled
   without having relaxed the edge into `y`, and the entry `(\delta(s,y),y)` need not be in the
   heap. (The same objection applies to `y=t`, if "the moment `t` is popped" is read as the moment
   before `t` joins `\Closed`.) The chapter makes this exception conspicuous three pages earlier -
   "`T`, which is popped but, because of the early exit, never expanded" (Section 3.5) - so an
   attentive reader will stop here.
   *Fix.* Insert one clause ruling `t` out before the appeal to step (ii): "Note first that `t`
   does not lie on this path: a prefix of it ending at `t` would give
   `\delta(s,t)\le\delta(s,v)`, contradicting `\delta(s,v)<\delta(s,t)` (here `c\ge0` is used
   again). Hence `y\neq t` and the predecessor of `y` is a vertex settled *and expanded* strictly
   before `t` was popped, so, as in step (ii) of the proof of `\cref{thm:ch03-invariant}`, ...".
   Nothing else in the proof changes.

2. **Section 3.3 (`sec:ch03-problem`), line 178:** "`...from \cref{ch:ch02} we reuse only the
   implicit successor interface $\Succ$ and the lazy-deletion queue \code{LazyPQ}
   (\cref{alg:ch02-lazypq,lst:ch02-lazypq})`".
   *Problem (categories F and G).* The label `lst:ch02-lazypq` **does not exist**: the only
   occurrence of that string in the whole project is this reference
   (`grep -rn "lst:ch02-lazypq" --include=*.tex .`). Chapter 2 defines only
   `lst:ch02-grid-neighbors` (line 704) and `lst:ch02-geometry` (line 724); `LazyPQ` appears there
   in `alg:ch02-lazypq` and in prose, never in a listing. In the full-book build this renders as
   `??` and raises an undefined-reference warning - a defect the single-chapter build hides,
   because every `ch02` label is undefined there anyway. The sentence is also an overclaim in its
   own right: Chapter 3 does not reuse `LazyPQ`; `\cref{alg:ch03-dijkstra}` and
   `\cref{lst:ch03-core}` use a bare `heapq` plus a closed set, which Chapter 2 (line 666) is at
   pains to distinguish from `LazyPQ`'s best-key form.
   *Fix.* Drop the non-existent label and say what is true, e.g.: "Both are new here; from
   `\cref{ch:ch02}` we reuse the implicit successor interface `$\Succ$` and the lazy-deletion idiom
   of its priority queue `\code{LazyPQ}` (`\cref{alg:ch02-lazypq}`), in the closed-set form: since
   `\hcost=0` here, the two forms settle exactly the same vertices." Leave the correct
   `\cref{alg:ch02-lazypq}` in Section 3.4 (line 191) as it is.

## Suggestions

1. *Bidirectional sketch, Section 3.7.3 (lines 771-790).* The two-case argument added in round 1 is
   the right shape, and two half-clauses would make it airtight. (a) In case 1, "then `c(\pi)` is at
   least the sum of the two smallest keys" needs the reason that the smallest key bounds an *open*
   vertex from below: the open forward vertex `u` on `\pi` carries the key
   `\gcost_f(u)=\delta(s,u)` by step (ii) of `\cref{thm:ch03-invariant}`, so
   `\min_{\Open_f}\le\delta(s,u)`, and symmetrically on the backward side. (b) In case 2, say
   *which* end scanned the edge: "whichever of `x` and `y` was settled later scanned `(x,y)` when
   both `\gcost_f(x)` and `\gcost_b(y)` were already final".
2. *Optional trim, about two thirds of a page (category G, not required at 19 pages).* The
   "tentative costs of open vertices are upper bounds" point is made six times: Section 3.2 ("Two
   consequences follow"), the "The result" paragraph (lines 261-275), "The early exit" paragraph of
   Section 3.5, `cor:ch03-ucs` and its proof, the "The closed set" paragraph of Section 3.8, and
   summary bullet 3. If the chapter must come closer to the spec's 12-14 pages, cut the two
   sentences "Without a target every reachable vertex is settled. With a target, only the vertices
   with `\delta(s,v)\le\delta(s,t)` have been settled, and the tentative costs of the vertices left
   in the queue are upper bounds, not answers." from lines 263-265 and replace them with
   "`\Cref{cor:ch03-ucs}` says exactly which vertices a run with a target settles." Keep everything
   else in that paragraph (path reconstruction, the unreachable-target case) - it is not repeated
   anywhere.
3. *Line 39, "It is the oldest of the shortest-path algorithms in this book."* Bellman-Ford
   (Ford 1956, Bellman 1958) is older, and it appears in this book: it is named on the same page as
   "the algorithm of choice" for negative costs and it is implemented in `ch03_dijkstra.py`. Either
   say "the oldest algorithm this book studies in detail" or drop the superlative.
4. *Solution to Exercise 3.6(c) (`appendices/solutions/ch03-solutions.tex`).* "the true constrained
   cost from `S` is 9" is right, but only because a wait costs 1; Chapter 2 (line 193) fixes only
   `c_{\text{wait}}>0`. Add "with a wait action of cost 1, as in the unit-cost setting of
   `\cref{ch:ch02}`".
5. *Hint for `exr:ch03-bidirectional`(b).* Section 3.7.3 now says "this second case is the crux",
   which is a good pointer, but the exercise still has no solution while the text leans on it.
   Two lines in the solutions file mirroring Suggestion 1 would close the loop, as was done for
   `exr:ch03-monotone` in round 1.
6. *Book-level, not chapter defects (carried over from round 1, still open, and outside this
   chapter's file set).* `frontmatter/notation.tex` is still the two-row placeholder, although
   Chapter 3 is the book's first heavy user of `\delta(u,v)`, `c(u,v)`, `\Succ`, `\Open`, `\Closed`
   and `\hcost^*`; and `appendices/glossary.tex` is still a placeholder that does not `\input`
   `appendices/glossary/ch03-terms.tex`, so the chapter's fifteen well-written glossary entries do
   not reach the book. Both belong to the editor's Phase 1/7 pass.

## What must be kept

Everything round 1 asked to keep survived, and the repairs improved the chapter rather than
scarring it. Keep the wave metaphor and the way it is carried through the whole chapter - the stone
in the pond, the bands `\lfloor\gcost\rfloor` of `\cref{fig:ch03-wavefront}` bending around the
block and re-centring on the gap, the settling order, the early exit, the area argument for
bidirectional search, and the expansions plot. Keep all six figures: they are stylistically uniform,
generated by the committed `gen_ch03_*.py` scripts, and their captions really do say what to notice.

Keep the proof architecture - Lemma 3.6 -> Theorem 3.7 -> Corollary 3.8 -> Theorem 3.10 - and above
all the sentence "*This is the only place where `c\ge0` is used*" in step (iii), followed by
Example 3.9 walking the reader through that exact step failing (`2\le0`) on a concrete negative
edge. The round-1 additions are keepers in their own right: the second half of the Corollary 3.8
proof (with the one clause of Required change 1 added), the `\delta(s,t)<\infty` hypothesis of
Theorem 3.11 together with the recorded counterexample, and the honest two-case bidirectional
argument that names its own crux.

Keep Section 3.7.2 in full. Theorem 3.11 - exactness, consistency, and admissibility in space-time
under arbitrary constraints - is the hinge to Chapters 4, 8 and 9, and the right-hand panel of
`\cref{fig:ch03-backward-heuristic}` (the green `g+h^*=8` cells being exactly the optimal path) is
the clearest possible preparation for A*. The directed-grid subtlety - entering a slow cell costs 3,
leaving it costs 1, so a forward run from `T` gives 4 where `h^*(3,3)=2` - is instructive and, I
confirmed cell by cell, correct.

Finally, keep the discipline of the worked examples and the code: the trace table with the heap
after every pop and stale entries as first-class citizens, the settling order printed cell by cell,
the `.dat`-backed expansions figure, the verbatim listings, the four pitfall boxes (the goal-test
timing bug with its 13 -> 12 -> 11 evidence, the constant-shift trap, the missing stale check and
the float-equality box promoted in round 1), and a self-test that checks the chapter's numbers
against brute force and against a Bellman-Ford reference. This chapter's numbers are trustworthy:
everything I recomputed independently matched the text to the last digit.

## Response to review (round 2)

All required changes applied; the cheap suggestions applied as well. Build:
`./build.sh ch03-dijkstra` -> **status 0**, no `!` errors, no undefined reference or citation
belonging to Chapter 3, no overfull box above 15 pt, `build/only-ch03-dijkstra.pdf`.
Chapter body still **19 pages** (pp. 14-32 of the single-chapter PDF).
`python3 code/ch03_dijkstra.py` -> `all self-tests passed (0.04 s)`. No code and no `.dat` file
needed to change: none of the edits touches a quoted number.

**Required change 1 (category A) - the early-exit gap in the proof of `cor:ch03-ucs`.**
Applied exactly as prescribed, in the proof of Corollary 3.8. Before the appeal to step~(ii) the
proof now rules `t` out of the path:

> Note first that `t` does not lie on this path: the prefix of the path ending at `t` would cost at
> least `\delta(s,t)` and the rest of the path at least 0, so `\delta(s,t)\le\delta(s,v)`,
> contradicting `\delta(s,v)<\delta(s,t)` (here `c\ge0` is used again). This step is needed because
> `t` is the one vertex that the early exit on line~\ref{alg:ch03-dijkstra:exit} settles without
> expanding. Hence `y\neq t`, and the predecessor of `y` on the path is a vertex settled *and*
> expanded strictly before `t` was popped, so, as in step~(ii) of the proof of
> `thm:ch03-invariant`, it has relaxed the edge into `y` and the heap holds the entry
> `(\delta(s,y),y)` with ...

One sentence was added beyond the suggested wording - the reminder that `t` is the only settled
vertex that is never expanded - so that the reader sees *why* the clause is there and the point
connects to the Section 3.5 observation the review quotes. Nothing else in the proof changed.

**Required change 2 (category F) - the non-existent label `lst:ch02-lazypq` and the overclaim.**
Applied. Section 3.3 (now around line 176) reads: "Both are new here; from \cref{ch:ch02} we reuse
the implicit successor interface `\Succ` and the lazy-deletion idiom of its priority queue
`LazyPQ` (`\cref{alg:ch02-lazypq}`), in the closed-set form: since `\hcost=0` here, the two forms
settle exactly the same vertices." The dangling label is gone (`grep -rn lst:ch02-lazypq` over the
project now returns nothing), the claim matches what Chapter 3 actually does, and the closed-set /
best-key equivalence is exactly the one Chapter 2 states at its line 666 for a consistent
heuristic. The correct `\cref{alg:ch02-lazypq}` in Section 3.4 was left untouched.

**Suggestion 1 (bidirectional sketch) - applied, both half-clauses.**
(a) Case 1 now names the witnesses: `u` is the first vertex of `\pi` the forward side has not
settled and `w` the last one the backward side has not settled, `u` comes no later than `w`, step
(ii) of `thm:ch03-invariant` gives `\gcost_f(u)=\delta(s,u)` in `\Open_f` and
`\gcost_b(w)=\delta(w,t)` in `\Open_b`, so the two minima are bounded by the prefix and the suffix
of `\pi` and the piece between them costs at least 0. (b) Case 2 now names the end that scanned
the edge: "Whichever of `x` and `y` was settled later scanned that edge during its own expansion -
`x` scans `(x,y)` forward, `y` scans it backward on `G^R` ... - and by then both `\gcost_f(x)` and
`\gcost_b(y)` were already final".

**Suggestion 2 (optional trim) - applied.** The two sentences at the old lines 263-265 became
"Without a target every reachable vertex is settled; \cref{cor:ch03-ucs} says exactly which
vertices a run with a target settles." The rest of the paragraph (path reconstruction, the
unreachable target) is unchanged. This removes the sixth statement of the upper-bound point and
offsets the lines added above; the body stayed at 19 pages.

**Suggestion 3 (the "oldest" superlative) - applied.** Line 39 now reads "It is the oldest
algorithm this book studies in detail", which leaves Bellman-Ford (Ford 1956) alone.

**Suggestion 4 (Exercise 3.6(c) solution) - applied.** The sentence now reads "... the drone must
wait one step or take a detour and, with a wait action of cost 1 as in the unit-cost setting of
`\cref{ch:ch02}`, the true constrained cost from `S` is 9".

**Suggestion 5 (solution for `exr:ch03-bidirectional`) - applied.** A fifth solution was added to
`appendices/solutions/ch03-solutions.tex`. Part (a) gives a counterexample to the naive meeting
rule that I verified with a throwaway alternating bidirectional Dijkstra rather than by eye:
undirected `S-a=1`, `a-b=28`, `b-T=1`, `S-u=16`, `u-T=16`. The settle order is `S` (f), `T` (b),
`a` (f), `b` (b); `\mu=30` is recorded when the forward expansion of `a` scans `(a,b)` with
`\gcost_b(b)=1` already finite; `\cref{eq:ch03-bidir-stop}` then fires at `16+16\ge30` and returns
`S,a,b,T`, while the first vertex settled by both sides is `u` with
`\gcost_f(u)+\gcost_b(u)=32>30`. Part (b) mirrors Suggestion 1 in full; part (c) says what to
report and why obstacles erode the factor of one half. `./build.sh appC-solutions` produces the
appendix PDF with no `!` error and no undefined `ch03-` reference (its non-zero latexmk status is
the 160 chapter labels that are undefined in any appendix-only build, none of them from Chapter 3;
the one overfull box near the file's start belongs to the Chapter 14 solutions, not to this file).

**Suggestion 6 (book-level: `frontmatter/notation.tex`, `appendices/glossary.tex`) - not actioned,
by the rules of the finisher brief.** Both files are outside this chapter's file set and belong to
the editor's Phase 1/7 pass; `appendices/glossary/ch03-terms.tex` and its fifteen entries are in
place and ready to be `\input`.

**Kept, as required.** The wave metaphor and its `\lfloor \gcost \rfloor` bands, all six figures
and their generators, the proof architecture Lemma 3.6 -> Theorem 3.7 -> Corollary 3.8 ->
Theorem 3.10, the sentence "This is the only place where `c\ge0` is used" with Example 3.9 walking
through `2\le0`, the second half of the Corollary 3.8 proof (now with the missing clause), the
`\delta(s,t)<\infty` hypothesis of Theorem 3.11 and its counterexample, the honest two-case
bidirectional argument (strengthened, not replaced), Section 3.7.2 in full including the green
`\gcost+\hcost^*=8` cells and the directed-grid subtlety, the trace table with the heap after every
pop, the settling order, the `.dat`-backed expansions figure, the verbatim listings, the four
pitfall boxes and the self-test.
