#!/usr/bin/env bash
# Build the book and produce the deliverables:
#   Overleaf/searchbook.pdf            compiled book
#   Overleaf/searchbook-overleaf.zip   Overleaf project package (main.tex at the zip root)
set -uo pipefail
cd "$(dirname "$0")"
python3 tools/assemble_glossary.py
./build.sh | tail -8
if [ -f build-full/main.pdf ]; then
  cp build-full/main.pdf searchbook.pdf
  rm -f searchbook-overleaf.zip
  zip -qr searchbook-overleaf.zip main.tex searchbook.sty latexmkrc references.bib README.md build.sh package.sh \
      frontmatter chapters appendices figures code bib tools -x "*/__pycache__/*" -x "*.pyc"
  echo "packaged: $(pdfinfo searchbook.pdf 2>/dev/null | grep Pages) ; $(unzip -l searchbook-overleaf.zip | tail -1)"
else
  echo "no PDF produced" >&2; exit 1
fi
