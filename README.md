# Multi-Agent Path Planning and Drone Collision Avoidance — a textbook

A complete, self-contained textbook (LaTeX/Overleaf project, runnable Python code, figures
generated from that code) teaching every algorithm in the research training plan
`core idea/core.docx`: single-agent graph search (Dijkstra, A\*, LPA\*/D\* Lite, ARA\*),
multi-agent path finding (prioritized planning, CBS, ECBS, M\*, Push-and-Swap/Rotate),
local collision avoidance (VO, RVO, ORCA, DWA, potential fields), sampling-based planning
(RRT, RRT\*, Informed RRT\*), tracking and prediction (Kalman filter, EKF, UKF, particle
filter, LSTM and Transformer trajectory prediction), optimization and control (MPC, MILP,
consensus and formation control), and the hybrid collision-avoidance architecture that
combines them, with a chapter on how to evaluate it.

| Where | What |
|---|---|
| `Overleaf/` | the Overleaf project (open `Overleaf/README.md` for upload/compile instructions) |
| `Overleaf/searchbook.pdf` | the compiled book |
| `Overleaf/searchbook-overleaf.zip` | the project as a zip for *New Project → Upload* on Overleaf |
| `Overleaf/code/` | reference implementation of every algorithm, each file with a self-test |
| `reviews/` | the peer-review reports (one per chapter and round) with the revisers' responses |
| `docs/specs/` | the per-chapter specifications the authors and reviewers worked from |
| `docs/workflows/` | the write → review → revise loop used to produce the book |
| `docs/bib-audit.md` | the bibliography audit (every reference checked against the literature) |
| `STYLE_GUIDE.md` | writing, figure, code and review rules |
| `TODO.md` | the task list, loop log and review log |

## How the book was produced

1. The training plan was extracted from `core idea/core.docx` (`docs/core-idea.txt`).
2. A style guide, chapter template and per-chapter specification were written first.
3. Each chapter was written by an author agent (Claude Fable 5.1) that had to make the chapter
   compile and its code self-test pass, then reviewed by an independent reviewer agent
   (Claude Opus 5) against the rubric in `STYLE_GUIDE.md` §9, revised, and re-reviewed until
   accepted or until only cosmetic items remained (`docs/workflows/chapter-loop.js`).
4. Every bibliography entry was verified by web search; the glossary is assembled from the
   chapters' term files; the index has at least 23 entries per chapter.

## Running the code

```bash
cd Overleaf
python3 code/ch04_astar.py        # every chapter file runs a self-test
python3 code/figures/gen_ch04_expansions.py   # regenerates the data behind a figure
```

Requires Python 3.10+, NumPy, and SciPy for Chapters 21–22.
