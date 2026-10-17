#!/usr/bin/env python3
"""British -> American spelling for a LaTeX/Python book project.

Usage: american.py [Overleaf-dir] [--apply] [--exclude 16,17,20] [--only 03,04] [--report FILE]
Dry run (default) prints per-substitution counts and per-file counts.  Rules: word-level and
substring substitutions, case-preserving, never inside a control-sequence name (\\macro), never
inside protected macro arguments (labels, refs, citations, file paths, urls).  AFTER APPLYING, run
check_book.py --since=HEAD: names inside \\SetKwFunction{...} and similar definitions are converted
while their \\uses are not, and must be renamed by hand; citation keys inside unusual cite commands
may need restoring."""
import re, sys, glob, argparse, collections, os

ap = argparse.ArgumentParser()
ap.add_argument('root', nargs='?', default='Overleaf')
ap.add_argument('--apply', action='store_true')
ap.add_argument('--exclude', default='')
ap.add_argument('--only', default='')
ap.add_argument('--report', default='')
args = ap.parse_args()
R = args.root

def default_files():
    fs = []
    for pat in ('chapters/*.tex', 'appendices/**/*.tex', 'frontmatter/*.tex', 'figures/**/*.tex',
                'figures/data/*.dat', 'code/*.py', 'code/figures/*.py', 'main.tex', 'textbook.sty'):
        fs += glob.glob(os.path.join(R, pat), recursive=True)
    return sorted(set(fs))

files = default_files()
excl = [x.strip() for x in args.exclude.split(',') if x.strip()]
only = [x.strip() for x in args.only.split(',') if x.strip()]
def chap_of(f):
    m = re.search(r'ch(\d\d)', os.path.basename(f)) or re.search(r'/ch(\d\d)/', f)
    return m.group(1) if m else None
files = [f for f in files if chap_of(f) not in excl]
if only: files = [f for f in files if chap_of(f) in only]

STEMS = ("minim linear initial normal summar recogn factor optim vector maxim penal discret central random "
         "general amort local organ marginal raster special visual symmetr regular priorit stabil decentral "
         "parametr parameter real equal character parallel standard diagonal formal serial refactor parenthes "
         "emphas util categor quant synchron hypothes memor custom final ideal critic author digit token "
         "trivial capital internal external modern theor item magnet canon sympath energ immun atom alphabet neutral "
         "polar popular scrutin steril subsid urban vocal civil legal liberal mechan mobil human harmon jeopard "
         "fertil oxid pressur sanit public national monopol").split()
ISE = re.compile(r'(?<![\\A-Za-z])((?:re|un|de|pre|non|over|under|mis)?(?:' + '|'.join(STEMS) + r'))(is)(e|es|ed|ing|er|ers|ation|ations|able|ability)\b', re.IGNORECASE)
def ise_sub(m):
    z = 'IZ' if m.group(2) == 'IS' else ('Iz' if m.group(2) == 'Is' else 'iz')
    return m.group(1) + z + m.group(3)
SUBSTR = [("neighbour","neighbor"),("behaviour","behavior"),("colour","color"),("favour","favor"),("labour","labor"),
    ("flavour","flavor"),("honour","honor"),("humour","humor"),("harbour","harbor"),("rumour","rumor"),("vapour","vapor"),
    ("vigour","vigor"),("rigour","rigor"),("endeavour","endeavor"),("armour","armor"),("odour","odor"),("savour","savor"),
    ("tumour","tumor"),("candour","candor"),("clamour","clamor"),("splendour","splendor"),("fervour","fervor"),
    ("valour","valor"),("parlour","parlor"),("saviour","savior"),
    ("centred","centered"),("centre","center"),("centring","centering"),("metre","meter"),("litre","liter"),("fibre","fiber"),
    ("calibre","caliber"),("theatre","theater"),("sombre","somber"),("spectre","specter"),("lustre","luster"),("meagre","meager"),
    ("sabre","saber"),("manoeuvred","maneuvered"),("manoeuvre","maneuver"),("manoeuvr","maneuver"),("modell","model"),
    ("labell","label"),("travell","travel"),("artefact","artifact"),("counter-clockwise","counterclockwise"),("anticlockwise","counterclockwise")]
WORDS = [(r'grey(s|ed|ing|ish|scale)?', r'gray\1'),(r'whilst','while'),(r'amongst','among'),(r'amidst','amid'),
    (r'towards','toward'),(r'afterwards','afterward'),(r'backwards','backward'),(r'forwards','forward'),(r'upwards','upward'),
    (r'downwards','downward'),(r'outwards','outward'),(r'inwards','inward'),(r'onwards','onward'),
    (r'learnt','learned'),(r'spelt','spelled'),(r'spoilt','spoiled'),(r'dreamt','dreamed'),(r'burnt','burned'),(r'leant','leaned'),
    (r'programme(s)?', r'program\1'),(r'analogue(s)?', r'analog\1'),(r'catalogue(s)?', r'catalog\1'),(r'catalogued','cataloged'),(r'cataloguing','cataloging'),
    (r'defence(s)?', r'defense\1'),(r'offence(s)?', r'offense\1'),(r'licence(s)?', r'license\1'),(r'pretence','pretense'),
    (r'practise(s|d)?', r'practice\1'),(r'practising','practicing'),(r'sceptic(al|ally|ism|s)?', r'skeptic\1'),
    (r'judgement(s)?', r'judgment\1'),(r'acknowledgement(s)?', r'acknowledgment\1'),(r'disc(s)?', r'disk\1'),
    (r'focussed','focused'),(r'focussing','focusing'),(r'analys(e|ed|ing|er|ers)', r'analyz\1'),
    (r'cancelled','canceled'),(r'cancelling','canceling'),(r'signalled','signaled'),(r'signalling','signaling'),
    (r'totalled','totaled'),(r'totalling','totaling'),(r'levelled','leveled'),(r'levelling','leveling'),
    (r'channelled','channeled'),(r'channelling','channeling'),(r'fuelled','fueled'),(r'fuelling','fueling'),
    (r'marshalled','marshaled'),(r'marshalling','marshaling'),(r'tunnelled','tunneled'),(r'tunnelling','tunneling'),
    (r'spiralled','spiraled'),(r'spiralling','spiraling'),(r'dialled','dialed'),(r'dialling','dialing'),
    (r'equalled','equaled'),(r'equalling','equaling'),(r'parallelled','paralleled'),(r'unparallelled','unparalleled'),
    (r'initialled','initialed'),(r'pencilled','penciled'),(r'counselled','counseled'),(r'quarrelled','quarreled'),(r'rivalled','rivaled'),
    (r'fulfil','fulfill'),(r'fulfils','fulfills'),(r'fulfilment','fulfillment'),(r'enrol','enroll'),(r'enrols','enrolls'),
    (r'enrolment','enrollment'),(r'instalment','installment'),(r'skilful','skillful'),(r'wilful','willful'),(r'distil','distill'),(r'instil','instill'),
    (r'aluminium','aluminum'),(r'maths','math'),(r'tyre(s)?', r'tire\1'),(r'kerb(s)?', r'curb\1'),(r'mould(s|ed|ing)?', r'mold\1'),
    (r'plough','plow'),(r'draught','draft'),(r'cosy','cozy'),(r'encyclopaedia','encyclopedia'),(r'mediaeval','medieval'),
    (r'enquire(s|d)?', r'inquire\1'),(r'enquiry','inquiry'),(r'enquiries','inquiries'),(r'orientated','oriented'),(r'speciality','specialty'),
    (r'co-ordinate(s|d)?', r'coordinate\1'),(r'co-ordination','coordination'),(r'co-operate(s|d)?', r'cooperate\1'),
    (r'co-operation','cooperation'),(r'co-operative','cooperative'),(r'sizeable','sizable'),(r'likeable','likable'),
    (r'moveable','movable'),(r'ageing','aging'),(r'queueing','queuing'),(r'aeroplane(s)?', r'airplane\1'),(r'sulphur','sulfur'),
    (r'anaesthe','anesthe'),(r'paediatric','pediatric')]
WORDRX = [(re.compile(r'(?<![\\A-Za-z\-])' + p + r'(?![A-Za-z])', re.IGNORECASE), r) for p, r in WORDS]
ABBR = re.compile(r'\b(i\.e\.|e\.g\.)\\ ')
PROTECT = re.compile(r'\\(?:label|ref|cref|Cref|eqref|pageref|nameref|autoref|[a-zA-Z]*cite[a-zA-Z]*|crefrange|Crefrange|input|include|includeonly|'
                     r'lstinputlisting|includegraphics|addbibresource|bibliography|url|begin|end|usepackage|documentclass|'
                     r'RequirePackage)\*?(?:\[[^\]]*\])?\{[^}]*\}|\\hyperref\[[^\]]*\]|\\href\{[^}]*\}')

def preserve(src, rep):
    if src.isupper() and len(src) > 1: return rep.upper()
    if src[0].isupper(): return rep[0].upper() + rep[1:]
    return rep
def in_control_sequence(text, start):
    i = start
    while i > 0 and text[i - 1].isalpha(): i -= 1
    return i > 0 and text[i - 1] == '\\'

counts = collections.Counter(); percounts = collections.Counter(); changed = {}
def convert(text, fname):
    holes = []
    def hole(m):
        holes.append(m.group(0)); return '\x00%d\x00' % (len(holes) - 1)
    t = PROTECT.sub(hole, text); cur = [t]
    def sub_ise(m):
        if in_control_sequence(cur[0], m.start()): return m.group(0)
        out = ise_sub(m); counts[(m.group(0).lower(), out.lower())] += 1; percounts[fname] += 1; return out
    t = ISE.sub(sub_ise, t); cur[0] = t
    for src, rep in SUBSTR:
        rx = re.compile(re.escape(src), re.IGNORECASE)
        def f(m, src=src, rep=rep):
            if in_control_sequence(cur[0], m.start()): return m.group(0)
            out = preserve(m.group(0), rep); counts[(src, rep)] += 1; percounts[fname] += 1; return out
        t = rx.sub(f, t); cur[0] = t
    for rx, rep in WORDRX:
        def g(m, rx=rx, rep=rep):
            if in_control_sequence(cur[0], m.start()): return m.group(0)
            out = preserve(m.group(0), m.expand(rep)); counts[(m.group(0).lower(), out.lower())] += 1; percounts[fname] += 1; return out
        t = rx.sub(g, t); cur[0] = t
    if fname.endswith('.tex'):
        n = len(ABBR.findall(t))
        if n: counts[('i.e.\\ ', 'i.e., ')] += n; percounts[fname] += n
        t = ABBR.sub(r'\1, ', t)
    return re.sub('\x00(\\d+)\x00', lambda m: holes[int(m.group(1))], t)

for f in files:
    try: src = open(f, encoding='utf-8').read()
    except UnicodeDecodeError: continue
    out = convert(src, f)
    if out != src:
        changed[f] = out
        if args.apply: open(f, 'w', encoding='utf-8').write(out)
lines = [f"files scanned: {len(files)}, files changed: {len(changed)}, substitutions: {sum(counts.values())}" + ('' if args.apply else '  (dry run; add --apply)')]
lines.append("--- per substitution ---")
for (a, b), n in sorted(counts.items(), key=lambda x: -x[1]): lines.append(f"{n:5d}  {a} -> {b}")
lines.append("--- per file ---")
for f, n in sorted(percounts.items(), key=lambda x: -x[1]): lines.append(f"{n:5d}  {f}")
rep = '\n'.join(lines)
if args.report: open(args.report, 'w').write(rep); print(lines[0])
else: print(rep)
