# Multi-Agent Path Planning and Drone Collision Avoidance — Overleaf project

This folder is a complete, self-contained **Overleaf project** for the textbook.

## Open it in Overleaf

Either of the following works:

1. **Upload the zip.** In Overleaf choose *New Project → Upload Project* and select
   `searchbook-overleaf.zip` (a zip of this folder). `main.tex` is the root document.
2. **Import from GitHub.** In Overleaf choose *New Project → Import from GitHub*, pick this
   repository, and set `Overleaf/main.tex` as the main document
   (Menu → Settings → Main document).

Overleaf settings: compiler **pdfLaTeX**, TeX Live 2023 or newer. Overleaf runs
Biber and MakeIndex automatically; nothing else is required.

### The figure cache (this is what makes Overleaf compiles possible)

`figcache/` holds every TikZ/pgfplots figure pre-rendered as a small PDF (`figcache/ch04-idea.pdf`
for `figures/ch04/idea.tex`). The style file loads the TikZ `external` library in its
"graphics if exists" mode: when the PDF is present the figure is included as a graphic, when it is
absent the figure is compiled from its TikZ source. No shell escape is needed. Measured on a
4-core machine: one pdfLaTeX pass over the whole book 51 s with the cache (117 s without), a
complete latexmk run 115 s (8-12 min without); one chapter via `\includeonly` 5 s per pass and
13 s for the complete run (41 s without).

* Overleaf premium (4-minute limit): the whole book compiles; a "Recompile from scratch" needs four
  passes plus Biber and is close to the limit on a slow server, a normal recompile is well inside it.
* Overleaf free (20-second limit): compile one chapter at a time with `\includeonly` (below).
* After editing a figure, delete its `figcache/chNN-name.pdf` so the edited source is used
  (or delete the whole `figcache/` folder to compile everything from source).
* Regenerate the cache locally with `python3 tools/render_figures.py` (about 10 minutes on 4 cores);
  `package.sh` does this before every build. A figure file that starts with `\tikzexternaldisable`
  is never cached (needed when the picture contains a `\cref` or `\label`).

### Compiling only one chapter (fast compiles / free plan timeouts)

The full book (about 740 pages, roughly 170 TikZ/pgfplots figures) takes 8-12 minutes to compile with pdfLaTeX.
If your compile times out, open `main.tex` and uncomment the line

```latex
% \includeonly{chapters/ch04-astar}
```

with the chapter you are working on. Cross-references to other chapters then show as
`??` until you compile the whole book again.

## Local build

```bash
./build.sh              # full book  -> build-full/main.pdf
./build.sh ch04-astar   # one chapter -> build/only-ch04-astar.pdf
```

Requires a TeX Live installation with `pdflatex`, `biber`, `makeindex` and `latexmk`.

## Layout

| Path | Contents |
|------|----------|
| `main.tex` | Root document (parts, chapter includes) |
| `searchbook.sty` | Packages, colours, boxes, TikZ styles, notation macros |
| `frontmatter/` | Title page, copyright, preface, notation table |
| `chapters/chNN-*.tex` | One file per chapter |
| `appendices/` | Study plan, maths refresher, solutions, glossary |
| `figures/chNN/*.tex` | TikZ/pgfplots figures, one file each, `\input` by chapters |
| `figures/data/*.dat` | Data tables plotted by pgfplots |
| `code/*.py` | Runnable Python reference implementations used in the book |
| `code/figures/*.py` | Scripts that regenerate the data/figure files |
| `references.bib` | Bibliography (Biber) |
| `latexmkrc` | Build configuration (used by Overleaf and `build.sh`) |
| `tools/assemble_glossary.py` | Rebuilds `appendices/glossary.tex` from `appendices/glossary/*-terms.tex` |
| `tools/thin_dat.py` | Thins oversized `.dat` files so pdfLaTeX does not run out of memory |
| `package.sh` | Assembles the glossary, builds the book, writes `searchbook.pdf` and `searchbook-overleaf.zip` |

## Memory

pdfLaTeX's default main memory (5,000,000 words, the same on Overleaf) is enough for the whole
book. If you add a figure with thousands of plotted points and see `TeX capacity exceeded`,
thin its data file with `python3 tools/thin_dat.py 1500 figures/data/<file>.dat`.
