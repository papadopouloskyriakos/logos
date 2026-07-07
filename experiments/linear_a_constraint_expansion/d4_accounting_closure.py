import json, random, unicodedata
from collections import Counter, defaultdict

d = json.load(open('/home/claude-runner/gitlab/n8n/logos/corpus/silver/inscriptions_structured.json'))

sup = {'⁰':'0','¹':'1','²':'2','³':'3','⁴':'4','⁵':'5','⁶':'6','⁷':'7','⁸':'8','⁹':'9'}
sub = {'₀':'0','₁':'1','₂':'2','₃':'3','₄':'4','₅':'5','₆':'6','₇':'7','₈':'8','₉':'9'}

def subscript_frac(raw):
    s = raw.replace('≈','').strip()
    if '⁄' in s:
        a,b = s.split('⁄')
        n = ''.join(sup.get(c,'') for c in a); m = ''.join(sub.get(c,'') for c in b)
        if n and m: return int(n)/int(m)
    return None

# FLAGGED metrological hypothesis: Bennett/GORILA Linear A fraction signs.
# Unicode names give letter labels A701..A709. Value set used here follows the
# widely-cited tentative reconstruction (Palmer 1963/Schoep 2002/Montecchi;
# summarized in the Unicode L2/07 proposal & Consani-Negri): the "half/quarter"
# family. Values are DISPUTED -> flagged. Codepoint -> value:
GLYPH_FRAC = {
    0x10746: 0.5,     # A707 J  ~ 1/2  (JE/half family)
    0x10743: 0.25,    # A704 E  ~ 1/4
    0x10744: 0.2,     # A705 F  ~ 1/5
    0x10747: 1/6,     # A708 K  ~ 1/6
    0x10748: 1/8,     # A709 L  ~ 1/8  (L-family, small)
    0x10749: 1/8,     # A709-2 L2
    0x1074b: 1/8,     # A709-4 L4
    0x1074c: 1/8,     # A709-6 L6
    0x10755: 0.5,     # A732 JE ~ 1/2
}
# NOTE: U+1076B (451x, unassigned Unicode cp, most common 'other') and the *NNN
# starred signs / 𐝓 etc. are treated as OPAQUE commodity/logogram tokens, value 0.

def other_value(raw, mode):
    """mode: 'none' | 'safe' | 'hypo'. Returns fractional value contributed."""
    if mode == 'none':
        return 0.0
    v = subscript_frac(raw)
    if v is not None:
        return v  # editor-resolved explicit fraction (SAFE)
    if mode == 'hypo':
        tot = 0.0
        for ch in raw:
            tot += GLYPH_FRAC.get(ord(ch), 0.0)
        return tot
    return 0.0

KURO=['KU','RO']; PTKURO=['PO','TO','KU','RO']; KIRO=['KI','RO']

def lines_of(ins):
    """Split stream into lines; each line -> dict(words, num, others)."""
    lines=[]; cur={'words':[],'num':None,'others':[]}
    for tok in ins['stream']:
        t=tok['t']
        if t=='nl':
            lines.append(cur); cur={'words':[],'num':None,'others':[]}
        elif t=='word': cur['words'].append(tok['signs'])
        elif t=='num': cur['num']=tok['v']
        elif t=='other': cur['others'].append(tok['raw'])
        # div ignored
    lines.append(cur)
    return lines

def line_value(ln, mode):
    if ln['num'] is None: return None
    return ln['num'] + sum(other_value(r,mode) for r in ln['others'])

def total_lines(lines):
    out=[]
    for i,ln in enumerate(lines):
        for w in ln['words']:
            if w==KURO or w==PTKURO:
                kind='PTKURO' if w==PTKURO else 'KURO'
                out.append((i,kind))
    return out

# Build closure problems: for each KU-RO/PO-TO-KU-RO total line with a number,
# entries = value-bearing lines since the previous total (or start), excluding
# the total line itself and excluding pure-heading lines (no number).
def problems(ins):
    lines=lines_of(ins)
    tls=total_lines(lines)
    probs=[]
    prev=-1
    tls_sorted=sorted(tls)
    for idx,(li,kind) in enumerate(tls_sorted):
        tl=lines[li]
        # entries between prev total line and this one
        entries=[]
        for j in range(prev+1, li):
            v=line_value(lines[j],'none')  # existence check
            ln=lines[j]
            # skip lines that are themselves totals
            if any(w==KURO or w==PTKURO for w in ln['words']): continue
            if ln['num'] is not None:
                entries.append(j)
        prev=li
        if not entries: continue
        probs.append({'total_line':li,'kind':kind,'entry_lines':entries})
    return lines,probs

def evaluate(mode, tol):
    n=0; exact=0; within=0; details=[]
    per_site=defaultdict(lambda:[0,0,0])  # n, exact, within
    problem_bank=[]
    for ins in d:
        lines,probs=problems(ins)
        for p in probs:
            tl=lines[p['total_line']]
            tval=line_value(tl,mode)
            if tval is None: continue
            esum=sum(line_value(lines[j],mode) for j in p['entry_lines'])
            n+=1
            diff=abs(esum-tval)
            ex = diff < 1e-9
            wi = diff <= tol+1e-9
            if ex: exact+=1
            if wi: within+=1
            s=ins['site']
            per_site[s][0]+=1; per_site[s][1]+=ex; per_site[s][2]+=wi
            details.append((ins['id'],p['kind'],round(esum,4),round(tval,4),round(diff,4),ex,wi))
            problem_bank.append((esum,tval))
    return dict(n=n,exact=exact,within=within,per_site=dict(per_site),details=details,bank=problem_bank)

TOL=0.5
res={}
for mode in ['none','safe','hypo']:
    res[mode]=evaluate(mode,TOL)
    r=res[mode]
    print('=== MODE %s (tol +-%.2f) ==='%(mode,TOL))
    print('  problems n=%d  exact=%d (%.1f%%)  within=%d (%.1f%%)'%(
        r['n'],r['exact'],100*r['exact']/r['n'],r['within'],100*r['within']/r['n']))
    for site,(sn,se,sw) in r['per_site'].items():
        print('    %-16s n=%2d exact=%d within=%d'%(site,sn,se,sw))

# permutation null on SAFE mode: shuffle totals across problems, recompute exact-match
def perm_null(mode, tol, iters=20000, seed=1):
    r=res[mode]
    esums=[a for a,b in r['bank']]
    tvals=[b for a,b in r['bank']]
    rng=random.Random(seed)
    obs_exact=sum(1 for a,b in r['bank'] if abs(a-b)<1e-9)
    obs_within=sum(1 for a,b in r['bank'] if abs(a-b)<=tol+1e-9)
    ge_exact=0; ge_within=0
    n=len(tvals)
    for _ in range(iters):
        perm=tvals[:]; rng.shuffle(perm)
        ex=sum(1 for i in range(n) if abs(esums[i]-perm[i])<1e-9)
        wi=sum(1 for i in range(n) if abs(esums[i]-perm[i])<=tol+1e-9)
        if ex>=obs_exact: ge_exact+=1
        if wi>=obs_within: ge_within+=1
    return dict(obs_exact=obs_exact,obs_within=obs_within,
                p_exact=(ge_exact+1)/(iters+1),p_within=(ge_within+1)/(iters+1),
                null_exact_mean=None)

print()
for mode in ['none','safe','hypo']:
    pn=perm_null(mode,TOL,iters=20000)
    print('PERM NULL %s: obs_exact=%d p=%.4f | obs_within=%d p=%.4f'%(
        mode,pn['obs_exact'],pn['p_exact'],pn['obs_within'],pn['p_within']))

print()
print('--- SAFE mode per-problem detail ---')
for row in res['safe']['details']:
    print('  ',row)
