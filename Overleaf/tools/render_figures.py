#!/usr/bin/env python3
"""Render every \\inputfigure picture into figcache/ (TikZ externalization).

For each \\include unit of main.tex (chapters and appendices) a temporary root
figgen-<unit>.tex is written that (a) restricts the document to that unit with
\\includeonly and (b) switches the TikZ external library to "list and make".
One pdfLaTeX run writes figgen-<unit>.makefile; make -j then renders the unit's
figures in parallel, each as figcache/<chNN-name>.pdf (plus a .dpth file).
The book itself uses external/mode "graphics if exists" (see searchbook.sty), so
a present PDF is included as a graphic and a missing one is compiled from source.

Usage (from Overleaf/ or anywhere):
    python3 tools/render_figures.py                  # everything, about 10 minutes on 4 cores
    python3 tools/render_figures.py ch03-dijkstra    # one or more units
"""
import glob, os, re, subprocess, sys, time

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
os.chdir(root)
main = open('main.tex', encoding='utf-8').read()
units = [u for u in re.findall(r'^\\include\{([^}]*)\}', main, re.M) if 'glossary' not in u]
want = sys.argv[1:]
if want:
    units = [u for u in units if os.path.basename(u) in want]
os.makedirs('figcache', exist_ok=True)
jobs = os.cpu_count() or 2
t0 = time.time(); rendered = 0; expected = 0
for u in units:
    stem = os.path.basename(u); rootname = 'figgen-' + stem
    src = main.replace('% \\includeonly{chapters/ch04-astar}', '\\includeonly{%s}' % u, 1)
    assert '\\includeonly{%s}' % u in src, 'the commented \\includeonly line of main.tex was not found'
    src = src.replace('\\usepackage{searchbook}',
                      '\\usepackage{searchbook}\n\\tikzset{external/mode=list and make,external/force remake}', 1)
    open(rootname + '.tex', 'w', encoding='utf-8').write(src)
    r = subprocess.run(['pdflatex', '-interaction=batchmode', rootname + '.tex'], capture_output=True)
    mk = rootname + '.makefile'
    if os.path.exists(mk):
        targets = list(dict.fromkeys(re.findall(r'^(figcache/\S+\.pdf):', open(mk).read(), re.M)))  # each target is listed twice
        subprocess.run(['make', '-s', '-k', '-j', str(jobs), '-f', mk], capture_output=True)
        made = [t for t in targets if os.path.exists(t)]
        expected += len(targets); rendered += len(made)
        print(f'{stem}: {len(made)}/{len(targets)} figures rendered', flush=True)
        for t in targets:
            if t not in made: print('   MISSING', t, flush=True)
    else:
        print(f'{stem}: no makefile written (pdflatex status {r.returncode})', flush=True)
    for f in glob.glob(rootname + '.*'): os.remove(f)
# keep only the graphics and their depth files; drop aux files written next to the sources
for f in glob.glob('figcache/*'):
    if not (f.endswith('.pdf') or f.endswith('.dpth')): os.remove(f)
for pat in ('chapters/*.aux', 'appendices/*.aux', 'appendices/*/*.aux', 'frontmatter/*.aux'):
    for f in glob.glob(pat): os.remove(f)
print(f'figcache: {len(glob.glob("figcache/*.pdf"))} pdf files ({rendered}/{expected} rendered in this run, {time.time()-t0:.0f} s)')
