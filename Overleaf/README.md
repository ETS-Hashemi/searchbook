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

### Compiling only one chapter (fast compiles / free plan timeouts)

The full book contains hundreds of TikZ figures and takes a few minutes to compile.
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
