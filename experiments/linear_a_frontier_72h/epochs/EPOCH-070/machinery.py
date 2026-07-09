"""
EPOCH-070 machinery: fraction attachment (num->frac vs word->frac).
L2 token-class adjacency only. Within-line shuffle null. Site contrast.

Frozen metric:
  R_num  = frac of fractions immediately preceded by 'num'
  R_word = frac of fractions immediately preceded by 'word'

NULL: within each line (segment between 'nl'), permute order of non-nl tokens
(preserving line token multiset + nl structure); recompute rates; >=1000 perms;
perm p = frac(null rate >= observed) one-sided (enrichment).

SITE-CONTRAST: site-label permutation over pooled HT+Khania fractions;
  stat = |R_num(A) - R_num(B)|; perm p = frac(null >= observed).
"""
import json, random, hashlib, sys
from collections import Counter

VULGAR = set('½¼¾⅓⅕⅙⅛⅔⅗')

def is_frac(tok):
    if not isinstance(tok, dict): return False
    if tok.get('t') != 'other': return False
    raw = tok.get('raw', '') or ''
    return ('⁄' in raw) or any(c in VULGAR for c in raw)

def load_corpus(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

# ---------- line segmentation ----------
def split_lines(stream):
    """Split a stream into lines. A line = list of non-nl tokens terminated by nl.
    Trailing tokens without nl form a final line. nl tokens themselves are NOT
    part of the line content (they are structural). div tokens are kept as
    content tokens (they are non-nl). Returns list of lines (each a list of tokens)."""
    lines = []
    cur = []
    for tok in stream:
        if isinstance(tok, dict) and tok.get('t') == 'nl':
            lines.append(cur)
            cur = []
        else:
            cur.append(tok)
    if cur:
        lines.append(cur)
    return lines

# ---------- rate computation ----------
def rates_from_stream(stream):
    """Compute (R_num, R_word, n_frac, before_hist) over a stream."""
    n_frac = 0
    n_num = 0
    n_word = 0
    before = Counter()
    for i, tok in enumerate(stream):
        if is_frac(tok):
            n_frac += 1
            if i > 0:
                pc = stream[i-1].get('t', '?') if isinstance(stream[i-1], dict) else '?'
                before[pc] += 1
                if pc == 'num': n_num += 1
                elif pc == 'word': n_word += 1
            else:
                before['START'] += 1
    if n_frac == 0:
        return 0.0, 0.0, 0, dict(before)
    return n_num/n_frac, n_word/n_frac, n_frac, dict(before)

def rates_from_inscriptions(inscriptions):
    """Aggregate rates over all fraction tokens across inscriptions."""
    n_frac = 0; n_num = 0; n_word = 0
    before = Counter()
    for ins in inscriptions:
        st = ins.get('stream', [])
        for i, tok in enumerate(st):
            if is_frac(tok):
                n_frac += 1
                if i > 0:
                    pc = st[i-1].get('t','?') if isinstance(st[i-1], dict) else '?'
                    before[pc] += 1
                    if pc == 'num': n_num += 1
                    elif pc == 'word': n_word += 1
                else:
                    before['START'] += 1
    if n_frac == 0:
        return 0.0, 0.0, 0, dict(before)
    return n_num/n_frac, n_word/n_frac, n_frac, dict(before)

# ---------- within-line shuffle null ----------
def permute_inscriptions(inscriptions, rng):
    """Return a NEW list of inscriptions with each line's non-nl tokens permuted.
    nl structure preserved; token multiset per line preserved."""
    out = []
    for ins in inscriptions:
        new_ins = dict(ins)
        st = ins.get('stream', [])
        lines = split_lines(st)
        new_stream = []
        for li, line in enumerate(lines):
            perm = list(line)
            rng.shuffle(perm)
            new_stream.extend(perm)
            # add nl terminator if original line had one (i.e., not the last trailing line OR
            # there was an nl). We reconstruct: original stream had nl after each complete line.
            # A line is "complete" (nl-terminated) if it is not the final trailing segment.
            # But the final segment may also have been nl-terminated if stream ended with nl.
            # Detect by counting nl in original.
            pass
        # The above naive approach loses nl placement. Rebuild properly:
        new_stream = []
        # Walk original stream; collect tokens until nl, shuffle that block, emit, then emit nl.
        block = []
        for tok in st:
            if isinstance(tok, dict) and tok.get('t') == 'nl':
                rng.shuffle(block)
                new_stream.extend(block)
                new_stream.append(tok)
                block = []
            else:
                block.append(tok)
        if block:
            rng.shuffle(block)
            new_stream.extend(block)
        new_ins['stream'] = new_stream
        out.append(new_ins)
    return out

def null_distribution(inscriptions, n_perm, target='num', seed=0):
    """Compute null distribution of R_<target> via within-line shuffle.
    Returns list of null rates."""
    rng = random.Random(seed)
    nulls = []
    for _ in range(n_perm):
        perm = permute_inscriptions(inscriptions, rng)
        if target == 'num':
            r, _, _, _ = rates_from_inscriptions(perm)
        else:
            _, r, _, _ = rates_from_inscriptions(perm)
        nulls.append(r)
    return nulls

def perm_p_enrichment(observed, nulls):
    """One-sided enrichment: frac(null >= observed)."""
    if len(nulls) == 0: return 1.0
    ge = sum(1 for x in nulls if x >= observed)
    # add-1 to avoid p=0
    return (ge + 1) / (len(nulls) + 1)

# ---------- site contrast ----------
def site_R_num(inscriptions, site):
    sub = [ins for ins in inscriptions if ins.get('site') == site]
    r, _, n, _ = rates_from_inscriptions(sub)
    return r, n

def site_contrast_perm(inscriptions, siteA, siteB, n_perm=2000, seed=0):
    """Site-label permutation over pooled fractions from siteA and siteB.
    stat = |R_num(A) - R_num(B)|. Returns observed stat, perm p."""
    # Collect per-fraction preceding-class for the two sites.
    # Each fraction token contributes (site, preceded_by_num_bool).
    fracs = []  # list of (site, is_num_preceded)
    for ins in inscriptions:
        if ins.get('site') not in (siteA, siteB): continue
        st = ins.get('stream', [])
        for i, tok in enumerate(st):
            if is_frac(tok):
                pc = st[i-1].get('t','?') if i>0 and isinstance(st[i-1],dict) else '?'
                fracs.append((ins.get('site'), 1 if pc=='num' else 0))
    nA = sum(1 for s,_ in fracs if s==siteA)
    nB = sum(1 for s,_ in fracs if s==siteB)
    if nA == 0 or nB == 0:
        return 0.0, 1.0, 0.0, 0.0, nA, nB
    def rA(labels):
        a = [v for s,v in zip(labels, [v for _,v in fracs]) if s==siteA]
        return sum(a)/len(a) if a else 0.0
    # observed
    labels_obs = [s for s,_ in fracs]
    vals = [v for _,v in fracs]
    rA_obs = sum(v for s,v in fracs if s==siteA)/nA
    rB_obs = sum(v for s,v in fracs if s==siteB)/nB
    obs = abs(rA_obs - rB_obs)
    rng = random.Random(seed)
    cnt = 0
    for _ in range(n_perm):
        shuf = list(labels_obs)
        rng.shuffle(shuf)
        # recompute R per site using shuffled labels
        a = [v for s,v in zip(shuf, vals) if s==siteA]
        b = [v for s,v in zip(shuf, vals) if s==siteB]
        ra = sum(a)/len(a) if a else 0.0
        rb = sum(b)/len(b) if b else 0.0
        if abs(ra-rb) >= obs:
            cnt += 1
    p = (cnt+1)/(n_perm+1)
    return obs, p, rA_obs, rB_obs, nA, nB

# ---------- positive controls (synthetic) ----------
def make_synthetic_detect(n_lines=200, seed=0):
    """Fractions ALWAYS follow a numeral. Lines like: word num frac nl."""
    rng = random.Random(seed)
    ins = []
    for li in range(n_lines):
        st = []
        st.append({'t':'word','signs':['W']})
        st.append({'t':'num','v':rng.randint(1,99)})
        st.append({'t':'other','raw':'¹⁄₂'})
        st.append({'t':'nl'})
        ins.append({'id':f'S{li}','site':'Haghia Triada','stream':st})
    return ins

def make_synthetic_random(n_lines=200, seed=0):
    """Fractions placed at a random non-nl position within each line.
    Line content: [word, num, word, frac] shuffled (frac position uniform random
    among the 4 slots, but frac is just one of the permutable tokens)."""
    rng = random.Random(seed)
    ins = []
    for li in range(n_lines):
        toks = [
            {'t':'word','signs':['W']},
            {'t':'num','v':rng.randint(1,99)},
            {'t':'word','signs':['X']},
            {'t':'other','raw':'¹⁄₂'},
        ]
        rng.shuffle(toks)
        st = toks + [{'t':'nl'}]
        ins.append({'id':f'R{li}','site':'Haghia Triada','stream':st})
    return ins

def pc_detect(n_perm=1000, seed=0):
    ins = make_synthetic_detect(seed=seed)
    r_num, r_word, n, _ = rates_from_inscriptions(ins)
    nulls = null_distribution(ins, n_perm, target='num', seed=seed+1)
    p = perm_p_enrichment(r_num, nulls)
    null_mean = sum(nulls)/len(nulls)
    return r_num, null_mean, p, n

def pc_false_positive(n_draws=20, n_perm=1000, alpha=0.05):
    """Across n_draws random corpora, fraction flagged at p<=alpha."""
    flags = 0
    ps = []
    for d in range(n_draws):
        ins = make_synthetic_random(seed=100+d)
        r_num, _, n, _ = rates_from_inscriptions(ins)
        nulls = null_distribution(ins, n_perm, target='num', seed=200+d)
        p = perm_p_enrichment(r_num, nulls)
        ps.append(p)
        if p <= alpha:
            flags += 1
    return flags/n_draws, ps

# ---------- self-check ----------
def self_check():
    """Validate within-line permutation null on a synthetic where we know the answer."""
    # Build a corpus of 10 lines, each [word, num, frac, nl]. Observed R_num=1.0 (20 fracs).
    # Null: frac position uniform among 3 non-nl slots -> P(after num)=1/3, so null mean ~0.33,
    # and the chance all 20 land after num is negligible -> enrichment p must be tiny.
    stream=[]
    for li in range(10):
        stream.append({'t':'word','signs':[f'W{li}']})
        stream.append({'t':'num','v':5+li})
        stream.append({'t':'other','raw':'¹⁄₂'})
        stream.append({'t':'nl'})
    ins = [{'id':'T1','site':'Haghia Triada','stream':stream}]
    r_num, r_word, n, _ = rates_from_inscriptions(ins)
    assert n == 10, f"expected 10 frac, got {n}"
    assert abs(r_num - 1.0) < 1e-9, f"observed R_num should be 1.0, got {r_num}"
    # permute and check nl structure preserved + multiset preserved
    rng = random.Random(0)
    perm = permute_inscriptions(ins, rng)
    pst = perm[0]['stream']
    # count nl
    nl_orig = sum(1 for t in ins[0]['stream'] if isinstance(t,dict) and t.get('t')=='nl')
    nl_perm = sum(1 for t in pst if isinstance(t,dict) and t.get('t')=='nl')
    assert nl_orig == nl_perm, f"nl count changed {nl_orig}->{nl_perm}"
    # multiset of t's preserved
    c_orig = Counter(t.get('t') for t in ins[0]['stream'] if isinstance(t,dict))
    c_perm = Counter(t.get('t') for t in pst if isinstance(t,dict))
    assert c_orig == c_perm, f"multiset changed {c_orig} vs {c_perm}"
    # null distribution: R_num should be < 1.0 on average (frac not always after num)
    nulls = null_distribution(ins, 1000, target='num', seed=1)
    null_mean = sum(nulls)/len(nulls)
    assert null_mean < 1.0, f"null mean should be <1.0, got {null_mean}"
    # perm p should be small (enrichment)
    p = perm_p_enrichment(r_num, nulls)
    assert p <= 0.05, f"self-check enrichment p should be <=0.05, got {p}"
    print(f"SELF-CHECK PASSED: obs R_num={r_num}, null_mean={null_mean:.3f}, p={p:.4f}")
    print(f"  nl structure preserved, token multiset preserved, enrichment detected.")
    return True

if __name__ == '__main__':
    self_check()
    print("--- PC DETECT (synthetic, fractions always follow num) ---")
    r, nm, p, n = pc_detect(n_perm=1000, seed=0)
    print(f"  R_num={r:.3f} null_mean={nm:.3f} p={p:.4f} n={n}  -> {'DETECT' if p<=0.05 else 'NO-DETECT'}")
    print("--- PC FALSE-POSITIVE (synthetic, fractions uniform random) ---")
    fpr, ps = pc_false_positive(n_draws=20, n_perm=1000, alpha=0.05)
    print(f"  false-positive rate={fpr:.3f} (threshold <=0.10)  ps={[round(x,3) for x in ps]}")
    print(f"  -> {'CALIBRATED' if fpr<=0.10 else 'MISCALIBRATED'}")
