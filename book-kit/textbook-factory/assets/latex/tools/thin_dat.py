#!/usr/bin/env python3
"""Thin whitespace-separated .dat files that have more than MAX rows (keeping the header row and
comment lines), so that pgfplots does not exhaust pdflatex's main memory in the full book.
Usage: python3 tools/thin_dat.py [MAX] file.dat ...   (default MAX = 1500)."""
import sys
args = sys.argv[1:]
MAX = int(args.pop(0)) if args and args[0].isdigit() else 1500
for path in args:
    lines = open(path).read().splitlines()
    head = [l for l in lines if l.startswith('#') or l.startswith('%')]
    body = [l for l in lines if l and not (l.startswith('#') or l.startswith('%'))]
    if not body: continue
    header, rows = body[0], body[1:]
    if len(rows) <= MAX:
        print(f"{path}: {len(rows)} rows, kept"); continue
    step = len(rows) / MAX
    kept = [rows[int(i * step)] for i in range(MAX)]
    if kept[-1] != rows[-1]: kept[-1] = rows[-1]
    open(path, 'w').write('\n'.join(head + [header] + kept) + '\n')
    print(f"{path}: {len(rows)} -> {len(kept)} rows")
