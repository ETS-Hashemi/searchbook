#!/usr/bin/env python3
"""Scaffold a new textbook project from a book.json description (textbook-factory kit).

Usage:  python3 new_book.py book.json TARGET_DIR [--force]

Creates in TARGET_DIR: the Overleaf/ LaTeX project (root document, style file, build and
package scripts, placeholders for every chapter and appendix, front matter, tools), docs/
(chapter template, style test, author briefs with the book map, spec stubs, the chapter-loop
workflow and an example batch), STYLE_GUIDE.md, TODO.md, tools/ (autosave, QA, spelling, index
and static-check scripts), .claude/agents/ (the five agents) and .gitignore.  See
assets/book.example.json for every field.  Placeholders in templates are written {{KEY}}.
"""
import datetime, json, os, shutil, stat, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.dirname(HERE)
ASSETS = os.path.join(KIT, 'assets')
LATEX = os.path.join(ASSETS, 'latex')

def die(msg): print('new_book:', msg, file=sys.stderr); sys.exit(1)
def read(path): return open(path, encoding='utf-8').read()
def write(path, text, mode=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)
    if mode: os.chmod(path, mode)
def fill(text, m):
    for k, v in m.items(): text = text.replace('{{' + k + '}}', str(v))
    return text
def copy(src, dst, m=None, mode=None):
    if m is None: shutil.copy(src, dst)
    else: write(dst, fill(read(src), m))
    if mode: os.chmod(dst, mode)

args = [a for a in sys.argv[1:] if not a.startswith('--')]
if len(args) != 2: die(__doc__)
cfg = json.load(open(args[0], encoding='utf-8')); target = os.path.abspath(args[1])
if os.path.isdir(target) and os.listdir(target) and '--force' not in sys.argv:
    die(f'{target} exists and is not empty (use --force to write into it anyway)')
for k in ('short', 'title', 'author', 'parts'):
    if k not in cfg: die(f'book.json lacks "{k}"')

chapters = [dict(c, part=p['title']) for p in cfg['parts'] for c in p['chapters']]
appendices = cfg.get('appendices', [])
units = chapters + appendices
ids = [u['id'] for u in units]
if len(set(ids)) != len(ids): die('duplicate chapter/appendix ids')
for u in units:
    for k in ('id', 'stem', 'title'):
        if k not in u: die(f'unit {u} lacks "{k}"')

def md(key, default=''): return cfg.get(key, default)
m = {
    'TITLE': cfg['title'], 'SUBTITLE': md('subtitle', ''), 'SHORT': cfg['short'],
    'SHORT_TITLE': md('short_title', cfg['title']), 'AUTHOR': cfg['author'],
    'AFFILIATION': md('affiliation', ''), 'YEAR': md('year', str(datetime.date.today().year)),
    'EMAIL_LINE': ('\\href{mailto:%s}{\\nolinkurl{%s}}' % (cfg['email'], cfg['email'])) if md('email') else '',
    'SUBJECT': md('subject', cfg['title']), 'KEYWORDS': md('keywords', ''),
    'DOMAIN': md('domain', 'the subject of this book'),
    'APPLICATION_CONTEXT': md('application_context', 'the applications the book builds toward'),
    'APPLICATION_BOX_LINE': '\\renewcommand{\\ApplicationBoxTitle}{%s}' % md('application_box_title', 'In practice'),
    'PURPOSE': md('purpose', 'Teach, from first principles, every method of the requirements (docs/requirements.md).'),
    'READER': md('reader', 'A graduate student or engineer entering the field; reads the book alone.'),
    'SPELLING': md('spelling', 'American'), 'CODE_LANGUAGE': md('code_language', 'Python'),
    'CODE_POLICY': md('code_policy', 'Python 3.10+ and NumPy only; PEP 8, short docstrings, no unicode in source.'),
    'LENGTH_RULE': md('length_rule', '16-22 pages for the Essential chapters (up to 24 when the material needs it), 12-20 pages for the others.'),
    'SOURCE_BRIEF': md('source_brief', 'the source brief'),
    'DATE': datetime.date.today().isoformat(),
    'PLACE_DATE': md('place_date', datetime.date.today().strftime('%B %Y')),
    'ABOUT_TEXT': md('about_text', '% (to be written from the facts the author supplies)'),
    'FIRST_STEM': chapters[0]['stem'],
    'TITLE_LINES': cfg['title'].replace(' and ', '\\\\[0.35em] and\\\\[0.35em] ', 1) if ' and ' in cfg['title'] else cfg['title'],
}
m['CANONICAL_SOURCES'] = '\n'.join('| %s | %s |' % (a, b) for a, b in md('canonical_sources', [['(topic)', '(source of truth)']]))

# ---------------- Overleaf/ ----------------
O = os.path.join(target, 'Overleaf')
for d in ('chapters', 'appendices/glossary', 'appendices/solutions', 'figures/data', 'figcache', 'code/figures', 'bib', 'frontmatter', 'tools'):
    os.makedirs(os.path.join(O, d), exist_ok=True)
for c in chapters: os.makedirs(os.path.join(O, 'figures', c['id']), exist_ok=True)
for a in appendices: os.makedirs(os.path.join(O, 'figures', a['id']), exist_ok=True)
body = []
for p in cfg['parts']:
    body.append('\\part{%s}' % p['title'])
    body += ['\\include{chapters/%s}' % c['stem'] for c in p['chapters']]
    body.append('')
m['BODY'] = '\n'.join(body).rstrip()
m['APPENDICES'] = '\n'.join('\\include{appendices/%s}' % a['stem'] for a in appendices)
m['BIBRESOURCES'] = '\n'.join(['\\addbibresource{references.bib}'] + ['\\addbibresource{bib/%s-extra.bib}' % c['id'] for c in chapters])
copy(os.path.join(LATEX, 'main.tex.template'), os.path.join(O, 'main.tex'), m)
copy(os.path.join(LATEX, 'textbook.sty'), os.path.join(O, 'textbook.sty'), m)
copy(os.path.join(LATEX, 'latexmkrc'), os.path.join(O, 'latexmkrc'))
copy(os.path.join(LATEX, 'build.sh'), os.path.join(O, 'build.sh'), mode=0o755)
copy(os.path.join(LATEX, 'package.sh.template'), os.path.join(O, 'package.sh'), m, mode=0o755)
copy(os.path.join(LATEX, 'README.md.template'), os.path.join(O, 'README.md'), m)
for t in ('assemble_glossary.py', 'render_figures.py', 'thin_dat.py'):
    copy(os.path.join(LATEX, 'tools', t), os.path.join(O, 'tools', t), mode=0o755)
copy(os.path.join(LATEX, 'run_all.py'), os.path.join(O, 'code', 'run_all.py'), mode=0o755)
for f in os.listdir(os.path.join(LATEX, 'frontmatter')):
    copy(os.path.join(LATEX, 'frontmatter', f), os.path.join(O, 'frontmatter', f.replace('.template', '')), m)
write(os.path.join(O, 'references.bib'), '%% %s -- bibliography.  Add only entries you have verified (authors, title, venue, year).\n%% Per-chapter additions go to bib/chNN-extra.bib and are audited before the final build.\n' % cfg['title'])
for c in chapters:
    write(os.path.join(O, 'bib', '%s-extra.bib' % c['id']), '%% Extra references of %s (%s). Only entries the author is certain of.\n' % (c['id'], c['title']))
    copy(os.path.join(LATEX, 'placeholder-chapter.tex.template'), os.path.join(O, 'chapters', c['stem'] + '.tex'), dict(m, TITLE=c['title'], ID=c['id']))
for a in appendices:
    if a.get('kind') == 'solutions':
        inputs = '\n'.join('\\InputIfFileExists{appendices/solutions/%s-solutions}{}{}' % c['id'] for c in chapters)
        copy(os.path.join(LATEX, 'placeholder-solutions.tex.template'), os.path.join(O, 'appendices', a['stem'] + '.tex'), dict(m, TITLE=a['title'], ID=a['id'], SOLUTION_INPUTS=inputs))
    else:
        copy(os.path.join(LATEX, 'placeholder-chapter.tex.template'), os.path.join(O, 'appendices', a['stem'] + '.tex'), dict(m, TITLE=a['title'], ID=a['id']))
write(os.path.join(O, 'appendices', 'glossary', 'README.md'), 'One file per chapter, `chNN-terms.tex`, with lines `\\item[Term] One-sentence definition.`; `tools/assemble_glossary.py` builds `appendices/glossary.tex` from them.\n')
write(os.path.join(O, 'appendices', 'solutions', 'README.md'), 'One file per chapter, `chNN-solutions.tex`, with `\\begin{solution}{exr:chNN-slug} ... \\end{solution}` blocks; the solutions appendix inputs them.\n')
write(os.path.join(O, 'figcache', '.gitkeep'), '')
write(os.path.join(O, 'figures', 'data', '.gitkeep'), '')
# initial glossary
import subprocess
subprocess.run([sys.executable, os.path.join(O, 'tools', 'assemble_glossary.py')], cwd=O, capture_output=True)

# ---------------- docs/ ----------------
D = os.path.join(target, 'docs')
os.makedirs(os.path.join(D, 'specs'), exist_ok=True); os.makedirs(os.path.join(D, 'workflows', 'batches'), exist_ok=True)
copy(os.path.join(LATEX, 'chapter-template.tex'), os.path.join(D, 'chapter-template.tex'))
copy(os.path.join(LATEX, 'style-test.tex'), os.path.join(D, 'style-test.tex'))
bookmap = []
for p in cfg['parts']:
    bookmap.append('Part — %s' % p['title'])
    for c in p['chapters']:
        bookmap.append('* `ch:%s` **%s.** %s' % (c['id'], c['title'], c.get('scope', '')))
    bookmap.append('')
if appendices:
    bookmap.append('Appendices')
    bookmap += ['* `ch:%s` **%s.** %s' % (a['id'], a['title'], a.get('scope', '')) for a in appendices]
m['BOOK_MAP'] = '\n'.join(bookmap)
copy(os.path.join(ASSETS, 'writer-brief.md.template'), os.path.join(D, 'writer-brief.md'), m)
copy(os.path.join(ASSETS, 'finisher-brief.md.template'), os.path.join(D, 'finisher-brief.md'), m)
req = md('requirements_file')
if req and os.path.exists(req): shutil.copy(req, os.path.join(D, 'requirements.md'))
else:
    write(os.path.join(D, 'requirements.md'), '# Requirements\n\nExtracted from %s. Replace this stub with: the topics in order, their priority, prerequisites, the schedule, the exercises and milestones per topic, the capstone, the completion checklist.\n' % m['SOURCE_BRIEF'])
for i, u in enumerate(units):
    kind = u.get('kind', 'algorithm' if u in chapters else 'appendix')
    n = chapters.index(u) + 1 if u in chapters else None
    head = ('# Chapter %d — %s' % (n, u['title'])) if n else ('# Appendix %s — %s' % (u['id'][-1], u['title']))
    pri = 'Essential' if u.get('essential') else 'Important'
    write(os.path.join(D, 'specs', u['id'] + '.md'),
          '%s (priority %s; <schedule slot>)\nFile Overleaf/%s/%s.tex, label ch:%s. %s template. Target <pages> pages.\n'
          'Must cover: %s <expand into the full must-cover list; see the skill reference spec-template.md>.\n'
          'Code: Overleaf/code/%s_<slug>.py: <functions; what the self-test checks; reproduces the worked-example numbers>.\n'
          'Cite: <keys that exist in references.bib, or the exact references to add>.\nDo not cover: <what belongs to other chapters>.\n'
          % (head, pri, 'chapters' if n else 'appendices', u['stem'], u['id'], kind.capitalize(), u.get('scope', ''), u['id']))
copy(os.path.join(HERE, 'chapter-loop.js'), os.path.join(D, 'workflows', 'chapter-loop.js'))
batch = {'root': target, 'domain': m['DOMAIN'], 'reviewModel': 'opus', 'maxRounds': 3,
         'items': [{'id': c['id'], 'stem': c['stem'], 'dir': 'chapters', 'title': 'Chapter %d (%s)' % (i + 1, c['title']), **({'essential': True} if c.get('essential') else {})} for i, c in enumerate(chapters[:6])]}
write(os.path.join(D, 'workflows', 'batches', 'batch1.json'), json.dumps(batch, indent=1))

# ---------------- root files ----------------
copy(os.path.join(ASSETS, 'STYLE_GUIDE.md.template'), os.path.join(target, 'STYLE_GUIDE.md'), m)
m['PHASE2_LINES'] = '\n'.join('- [ ] 2.%02d Ch %d %s — spec `docs/specs/%s.md`' % (i + 1, i + 1, c['title'], c['id']) for i, c in enumerate(chapters))
m['PHASE4_LINES'] = '\n'.join('- [ ] 4.%d Appendix %s: %s' % (i + 1, a['id'][-1], a['title']) for i, a in enumerate(appendices)) or '- [ ] 4.1 (no appendices configured)'
m['PHASE5_LINES'] = '\n'.join('- [ ] 5.%02d Ch %d — review/revise until Accept' % (i + 1, i + 1) for i, c in enumerate(chapters))
m['REVIEW_LOG_LINES'] = '\n'.join('| Ch %d | | | | |' % (i + 1) for i, c in enumerate(chapters))
copy(os.path.join(ASSETS, 'TODO.md.template'), os.path.join(target, 'TODO.md'), m)
T = os.path.join(target, 'tools'); os.makedirs(T, exist_ok=True)
for s in ('autosave.sh', 'qa.sh', 'american.py', 'joinindex.py', 'check_book.py'):
    copy(os.path.join(HERE, s), os.path.join(T, s), mode=0o755)
A = os.path.join(target, '.claude', 'agents'); os.makedirs(A, exist_ok=True)
for f in os.listdir(os.path.join(ASSETS, 'agents')): copy(os.path.join(ASSETS, 'agents', f), os.path.join(A, f))
write(os.path.join(target, '.gitignore'), '\n'.join(['# LaTeX build outputs', 'Overleaf/build/', 'Overleaf/build-full/', 'Overleaf/*.aux', 'Overleaf/*.log', 'Overleaf/*.out', 'Overleaf/*.toc', 'Overleaf/*.bbl', 'Overleaf/*.bcf', 'Overleaf/*.blg', 'Overleaf/*.idx', 'Overleaf/*.ilg', 'Overleaf/*.ind', 'Overleaf/*.loa', 'Overleaf/*.lof', 'Overleaf/*.lot', 'Overleaf/*.run.xml', 'Overleaf/*.synctex.gz', 'Overleaf/*.fls', 'Overleaf/*.fdb_latexmk', 'Overleaf/only-*.tex', 'Overleaf/figgen-*', 'Overleaf/chapters/*.aux', 'Overleaf/appendices/*.aux', 'Overleaf/appendices/*/*.aux', 'Overleaf/frontmatter/*.aux', '__pycache__/', '*.pyc', '!Overleaf/%s.pdf' % cfg['short'], '!Overleaf/%s-overleaf.zip' % cfg['short'], '']))
shutil.copy(args[0], os.path.join(target, 'book.json'))

# ---------------- report ----------------
left = []
for dp, _, fns in os.walk(target):
    for fn in fns:
        if fn.endswith(('.tex', '.md', '.sty', '.sh', '.py')):
            t = read(os.path.join(dp, fn))
            import re
            for k in re.findall(r'\{\{([A-Z_]+)\}\}', t):
                left.append((os.path.relpath(os.path.join(dp, fn), target), k))
print('scaffolded %s: %d chapters in %d parts, %d appendices -> %s' % (cfg['title'], len(chapters), len(cfg['parts']), len(appendices), target))
if left: print('WARNING: unfilled placeholders:', sorted(set(left)))
print('next: fill STYLE_GUIDE.md sections 1 and 8, the DOMAIN NOTATION block of Overleaf/textbook.sty, docs/requirements.md and docs/specs/*.md;'
      ' then  cd Overleaf && ./build.sh  and  ./build.sh --standalone ../docs/style-test.tex')
