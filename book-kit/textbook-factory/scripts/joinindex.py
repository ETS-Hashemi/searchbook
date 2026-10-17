#!/usr/bin/env python3
"""Put every \\index{...} argument on one source line (a line break inside the argument makes
MakeIndex create two different entries).  Usage: joinindex.py [Overleaf-dir] [--exclude ch16,ch17]"""
import glob, os, re, sys
root = next((a for a in sys.argv[1:] if not a.startswith('--')), 'Overleaf')
excl = []
for a in sys.argv[1:]:
    if a.startswith('--exclude='): excl = a.split('=', 1)[1].split(',')
files = glob.glob(root + '/chapters/*.tex') + glob.glob(root + '/appendices/**/*.tex', recursive=True) + glob.glob(root + '/frontmatter/*.tex')
total = 0; nfiles = 0
for f in sorted(files):
    if any(e and e in os.path.basename(f) for e in excl): continue
    s = open(f, encoding='utf-8').read(); out = []; i = 0; n = 0
    while True:
        j = s.find('\\index{', i)
        if j < 0: out.append(s[i:]); break
        out.append(s[i:j]); k = j + 7; depth = 1
        while k < len(s) and depth:
            depth += (s[k] == '{') - (s[k] == '}'); k += 1
        arg = s[j + 7:k - 1]; new = re.sub(r'\s*\n\s*', ' ', arg)
        if new != arg: n += 1
        out.append('\\index{' + new + '}'); i = k
    if n:
        open(f, 'w', encoding='utf-8').write(''.join(out)); total += n; nfiles += 1; print(f"{n:3d} {f}")
print(f"joined {total} index entries in {nfiles} files")
