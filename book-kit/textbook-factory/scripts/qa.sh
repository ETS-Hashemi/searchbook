#!/bin/bash
# Final QA of the full build.  Usage: tools/qa.sh [path/to/Overleaf]   (after ./build.sh there)
cd "${1:-Overleaf}" || exit 1
L=build-full/main.log
[ -f "$L" ] || { echo "no full build log at $L; run ./build.sh first"; exit 1; }
echo "errors:            $(grep -c -E '^(! |\./.*:[0-9]+: )' $L)"
echo "undefined refs:    $(grep -c -E 'Reference .* undefined|Citation .* undefined' $L)"
echo "multiply defined:  $(grep -c -i 'multiply' $L)"
echo "overfull > 15pt:"; grep -o 'Overfull \\hbox ([0-9.]*pt' $L | awk -F'[( ]' '{v=$3+0; if (v>15) print "  "v"pt"}' | sort -rn | head -12
echo "pages:             $(grep -o 'Output written on build-full/main.pdf ([0-9]* pages' $L | grep -o '[0-9]* pages')"
echo "chapters in TOC:   $(grep -c 'contentsline {chapter}{\\numberline {[0-9]' build-full/main.toc)"
echo "Summary sections:  $(grep -c 'Summary' build-full/main.toc)"
echo "algorithms (LoA): $(grep -c 'contentsline' build-full/main.loa 2>/dev/null)   figures (aux): $(cat build-full/chapters/*.aux build-full/appendices/*.aux 2>/dev/null | grep -c 'newlabel{fig:')   tables (aux): $(cat build-full/chapters/*.aux build-full/appendices/*.aux 2>/dev/null | grep -c 'newlabel{tab:')"
echo "index entries:     $(grep -c -E '^\s*\\item' build-full/main.ind 2>/dev/null)   subentries: $(grep -c -E '^\s*\\subitem' build-full/main.ind 2>/dev/null)"
echo "bib entries:       $(grep -c -E '^\s*\\entry\{' build-full/main.bbl 2>/dev/null)"
if command -v pdftotext >/dev/null; then pdftotext -layout build-full/main.pdf /tmp/qa-main.txt 2>/dev/null && echo "'??' in PDF text:  $(grep -c '??' /tmp/qa-main.txt)"; fi
echo "per-chapter figures (labels):"; for f in build-full/chapters/ch*.aux; do [ -f "$f" ] || continue; n=$(basename $f .aux | cut -c3-4); printf "%s:%s " $n $(grep -c "newlabel{fig:" $f); done; echo
echo "per-chapter tables (labels):"; for f in build-full/chapters/ch*.aux; do [ -f "$f" ] || continue; n=$(basename $f .aux | cut -c3-4); printf "%s:%s " $n $(grep -c "newlabel{tab:" $f); done; echo
echo "examples / exercises per chapter (source):"; for f in chapters/ch*.tex; do n=$(basename $f | cut -c3-4); printf "%s:%s/%s " $n $(grep -c 'begin{example}' $f) $(grep -c 'begin{exercise}' $f); done; echo
