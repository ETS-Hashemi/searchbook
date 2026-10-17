#!/usr/bin/env python3
"""Static checks over the LaTeX sources.  Usage: check_book.py [Overleaf-dir] [--since GITREF]
  * float labels (fig/tab/alg/lst) that are never referenced
  * citation keys used in the text that no .bib file defines
  * duplicate labels and duplicate \\SetKwFunction / \\SetKwData names across files
  * \\index{} arguments that span lines
  * with --since REF: definition names (SetKw*, environments, colors, styles) that changed
    between REF and the working tree (a spelling script can rename a definition but not its uses)
Exit status 1 when a problem is found."""
import glob, os, re, subprocess, sys
root = next((a for a in sys.argv[1:] if not a.startswith('--')), 'Overleaf')
since = next((a.split('=', 1)[1] for a in sys.argv[1:] if a.startswith('--since=')), None)
files = [f for f in glob.glob(root + '/**/*.tex', recursive=True) if '/build' not in f and '/figcache/' not in f]
alltext = ''.join(open(f, encoding='utf-8').read() + '\n' for f in files)
problems = 0
labels = re.findall(r'\\label\{((?:fig|tab|alg|lst):[^}]*)\}', alltext)
refs = set()
for m in re.finditer(r'\\(?:cref|Cref|ref|autoref|pageref|hyperref\[)\{?([^}\]]*)', alltext):
    refs.update(p.strip() for p in m.group(1).split(','))
unref = sorted(l for l in set(labels) if l not in refs and l.count(':') < 2)   # algorithm line labels (alg:x:y) are exempt
if unref: problems += 1; print(f"{len(unref)} float labels never referenced:", ', '.join(unref))
dups = sorted({l for l in labels if labels.count(l) > 1})
alllabels = re.findall(r'\\label\{([^}]*)\}', alltext)
dups = sorted({l for l in alllabels if alllabels.count(l) > 1})
if dups: problems += 1; print(f"{len(dups)} duplicate labels:", ', '.join(dups))
used = set()
for m in re.finditer(r'\\[A-Za-z]*cite[A-Za-z]*\*?(?:\[[^\]]*\]){0,2}\{([^}]*)\}', alltext):
    used.update(k.strip() for k in m.group(1).split(','))
defined = set()
for b in glob.glob(root + '/**/*.bib', recursive=True):
    defined |= set(re.findall(r'^@\w+\{([^,]+),', open(b, encoding='utf-8').read(), re.M))
undef = sorted(used - defined)
if undef: problems += 1; print(f"{len(undef)} citation keys not defined in any .bib:", ', '.join(undef))
kw = {}
for f in files:
    for name in re.findall(r'\\SetKw(?:Function|Data|Array|Prog|Input|InOut|Block)?\{([^}]*)\}', open(f, encoding='utf-8').read()):
        kw.setdefault(name, set()).add(os.path.basename(f))
multi = {k: v for k, v in kw.items() if len(v) > 1}
if multi: problems += 1; print(f"{len(multi)} SetKw names defined in several files:", '; '.join(f"{k} ({', '.join(sorted(v))})" for k, v in multi.items()))
split = 0
for f in files:
    s = open(f, encoding='utf-8').read(); i = 0
    while True:
        j = s.find('\\index{', i)
        if j < 0: break
        k = j + 7; depth = 1
        while k < len(s) and depth: depth += (s[k] == '{') - (s[k] == '}'); k += 1
        if '\n' in s[j:k]: split += 1
        i = k
if split: problems += 1; print(f"{split} \\index{{}} arguments span a line break (run joinindex.py)")
if since:
    pat = re.compile(r'\\(?:SetKwFunction|SetKwData|SetKwArray|SetKw|SetKwProg|SetKwInput|SetKwInOut|SetKwBlock|newenvironment|newtcolorbox|definecolor|colorlet|lstdefinestyle|newtheorem|hypertarget|hyperlink)\*?\{([^}]*)\}')
    sty = re.compile(r'([A-Za-z][A-Za-z0-9 ]*)/\.style')
    changed = 0
    for f in files + glob.glob(root + '/*.sty'):
        before = subprocess.run(['git', 'show', f'{since}:{f}'], capture_output=True, text=True).stdout
        if not before: continue
        after = open(f, encoding='utf-8').read()
        nb = set(pat.findall(before)) | set(sty.findall(before)); na = set(pat.findall(after)) | set(sty.findall(after))
        if nb != na: changed += 1; print(f"{f}: definition names removed {sorted(nb - na)} added {sorted(na - nb)}")
    if changed: problems += 1
print('check_book:', 'OK' if not problems else f'{problems} problem class(es) found')
sys.exit(1 if problems else 0)
