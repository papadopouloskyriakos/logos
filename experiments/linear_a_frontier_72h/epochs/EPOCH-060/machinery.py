"""
EPOCH-060 machinery: Metrological / logographic ledger entry template (L2).

Token CLASS + POSITION only. No sign values, no readings, no phonetics/meaning,
no metrological arithmetic.

Classes:
  WORD, NUM, DIV, NL  -- from token 't'
  LOGOGRAM  -- 'other' with raw starting with '*'
  FRACTION  -- 'other' with raw containing '⁄' or a char in U+2150..U+215F
  OTHERSIGN -- 'other' otherwise (ignored for H1/H2)

Metrics:
  H1 LOGO->NUM     = frac(logogram tokens whose next token is NUM)
  H2 FRAC-TERMINAL = frac(fraction tokens whose next token is NL or END)

Null: within each line (segment of non-NL tokens between NLs), permute the order
of the non-NL tokens (preserving multiset + NL/line structure). >=500 perms.
perm p = frac(null stat >= observed), one-sided enrichment.
"""
import json, random
from collections import Counter

VULGAR_LO, VULGAR_HI = 0x2150, 0x215F

def is_vulgar_frac_char(ch):
    return VULGAR_LO <= ord(ch) <= VULGAR_HI

def is_logogram_raw(raw):
    return raw.startswith('*')

def is_fraction_raw(raw):
    return ('⁄' in raw) or any(is_vulgar_frac_char(c) for c in raw)

def token_class(tok):
    t = tok.get('t')
    if t == 'word': return 'WORD'
    if t == 'num':  return 'NUM'
    if t == 'div':  return 'DIV'
    if t == 'nl':   return 'NL'
    if t == 'other':
        raw = tok.get('raw', '')
        if is_logogram_raw(raw): return 'LOGOGRAM'
        if is_fraction_raw(raw): return 'FRACTION'
        return 'OTHERSIGN'
    return 'OTHERSIGN'

def split_into_lines(stream):
    """Return list of lines; each line is a list of (non-NL) tokens.
    NL tokens are line delimiters and are NOT part of any line's permutable content."""
    lines = []
    cur = []
    for tok in stream:
        if tok.get('t') == 'nl':
            lines.append(cur)
            cur = []
        else:
            cur.append(tok)
    lines.append(cur)  # trailing segment after last nl (may be empty)
    return lines

def reassemble(lines):
    """Rebuild a flat stream from lines, inserting NL between consecutive lines."""
    out = []
    for i, ln in enumerate(lines):
        out.extend(ln)
        if i < len(lines) - 1:
            out.append({'t': 'nl'})
    return out

def permute_stream(stream, rng):
    """Within-line permutation null: permute non-NL tokens within each line."""
    lines = split_into_lines(stream)
    new_lines = []
    for ln in lines:
        if len(ln) > 1:
            cp = ln[:]
            rng.shuffle(cp)
            new_lines.append(cp)
        else:
            new_lines.append(ln)
    return reassemble(new_lines)

# ---- metrics ----

def h1_logo_num(stream):
    """Fraction of LOGOGRAM tokens immediately followed by NUM."""
    n_logo = 0
    n_logo_then_num = 0
    L = len(stream)
    for i, tok in enumerate(stream):
        if token_class(tok) == 'LOGOGRAM':
            n_logo += 1
            if i + 1 < L:
                if token_class(stream[i+1]) == 'NUM':
                    n_logo_then_num += 1
            # END is not NUM -> no increment
    if n_logo == 0:
        return 0.0, 0
    return n_logo_then_num / n_logo, n_logo

def h2_frac_terminal(stream):
    """Fraction of FRACTION tokens immediately followed by NL or END."""
    n_frac = 0
    n_frac_term = 0
    L = len(stream)
    for i, tok in enumerate(stream):
        if token_class(tok) == 'FRACTION':
            n_frac += 1
            if i + 1 < L:
                if token_class(stream[i+1]) == 'NL':
                    n_frac_term += 1
            else:
                n_frac_term += 1  # END
    if n_frac == 0:
        return 0.0, 0
    return n_frac_term / n_frac, n_frac

def permutation_test(stream, n_perm=500, seed=12345, stat_choice='both'):
    """Run the within-line permutation null for H1 and/or H2."""
    rng = random.Random(seed)
    h1_obs, n_logo = h1_logo_num(stream)
    h2_obs, n_frac = h2_frac_terminal(stream)
    h1_null = []
    h2_null = []
    for _ in range(n_perm):
        ps = permute_stream(stream, rng)
        if stat_choice in ('both', 'h1'):
            v, _ = h1_logo_num(ps)
            h1_null.append(v)
        if stat_choice in ('both', 'h2'):
            v, _ = h2_frac_terminal(ps)
            h2_null.append(v)
    out = {}
    if stat_choice in ('both', 'h1'):
        h1_p = sum(1 for v in h1_null if v >= h1_obs) / len(h1_null)
        out['h1'] = {'obs': h1_obs, 'null_mean': sum(h1_null)/len(h1_null),
                     'perm_p': h1_p, 'n_logograms': n_logo}
    if stat_choice in ('both', 'h2'):
        h2_p = sum(1 for v in h2_null if v >= h2_obs) / len(h2_null)
        out['h2'] = {'obs': h2_obs, 'null_mean': sum(h2_null)/len(h2_null),
                     'perm_p': h2_p, 'n_fractions': n_frac}
    return out

# ---- synthetic corpora for positive control ----

def make_detect_corpus(rng, n_lines=60):
    """Plant: each line = [LOGOGRAM, NUM, FRACTION] -> logo always before num,
    fraction always line-final."""
    stream = []
    for _ in range(n_lines):
        stream.append({'t': 'other', 'raw': '*304'})
        stream.append({'t': 'num', 'v': rng.randint(1, 99)})
        stream.append({'t': 'other', 'raw': '¹⁄₂'})
        stream.append({'t': 'nl'})
    return stream

def make_uniform_corpus(rng, n_lines=60):
    """Plant: each line has [LOGOGRAM, NUM, FRACTION] plus a variable number (2-5)
    of filler WORD tokens, ALL in RANDOM order (uniform placement within line).
    Variable line length gives a smooth permutation null distribution."""
    stream = []
    for _ in range(n_lines):
        k = rng.randint(2, 5)
        toks = [
            {'t': 'other', 'raw': '*304'},
            {'t': 'num', 'v': rng.randint(1, 99)},
            {'t': 'other', 'raw': '¹⁄₂'},
        ]
        for _ in range(k):
            toks.append({'t': 'word', 'signs': ['A', 'RA']})
        rng.shuffle(toks)
        stream.extend(toks)
        stream.append({'t': 'nl'})
    return stream

def positive_control(n_perm=500, n_fp_draws=30, seed=2024):
    """Returns dict: pc_verdict, detect_p_h1, detect_p_h2, false_pos_rate, pc_is_synthetic."""
    rng = random.Random(seed)
    # (a) DETECT
    det = make_detect_corpus(rng)
    det_res = permutation_test(det, n_perm=n_perm, seed=seed, stat_choice='both')
    detect_p_h1 = det_res['h1']['perm_p']
    detect_p_h2 = det_res['h2']['perm_p']
    detect_ok = (detect_p_h1 <= 0.05) and (detect_p_h2 <= 0.05)
    # (b) FALSE POSITIVE
    fp_count = 0
    for k in range(n_fp_draws):
        corp = make_uniform_corpus(random.Random(seed + 1000 + k))
        res = permutation_test(corp, n_perm=n_perm, seed=seed + 5000 + k, stat_choice='both')
        flagged = (res['h1']['perm_p'] <= 0.05) or (res['h2']['perm_p'] <= 0.05)
        if flagged:
            fp_count += 1
    fp_rate = fp_count / n_fp_draws
    fp_ok = (fp_rate <= 0.10)
    pc_pass = detect_ok and fp_ok
    return {
        'pc_verdict': 'PASSED' if pc_pass else 'FAILED',
        'detect_p_h1': detect_p_h1,
        'detect_p_h2': detect_p_h2,
        'false_pos_rate': fp_rate,
        'pc_is_synthetic': True,
        'detect_ok': detect_ok,
        'fp_ok': fp_ok,
    }

# ---- self-check ----

def _selfcheck():
    """Validate the within-line permutation null on a synthetic."""
    rng = random.Random(7)
    s = make_detect_corpus(rng, n_lines=10)
    h1, n1 = h1_logo_num(s)
    h2, n2 = h2_frac_terminal(s)
    assert abs(h1 - 1.0) < 1e-9, ('h1 detect', h1)
    assert abs(h2 - 1.0) < 1e-9, ('h2 detect', h2)
    assert n1 == 10 and n2 == 10, (n1, n2)
    fp_pvals = []
    for k in range(15):
        corp = make_uniform_corpus(random.Random(900+k))
        res = permutation_test(corp, n_perm=200, seed=7000+k, stat_choice='both')
        fp_pvals.append(res['h1']['perm_p'])
        fp_pvals.append(res['h2']['perm_p'])
    mean_p = sum(fp_pvals)/len(fp_pvals)
    assert mean_p > 0.2, ('uniform mean p too low', mean_p)
    s2 = [{'t':'other','raw':'*304'},{'t':'num','v':5},{'t':'other','raw':'¹⁄₂'},{'t':'nl'}]*3
    ps = permute_stream(s2, random.Random(1))
    assert Counter(json.dumps(t,sort_keys=True) for t in s2) == Counter(json.dumps(t,sort_keys=True) for t in ps), 'multiset broken'
    assert [t.get('t') for t in ps].count('nl') == [t.get('t') for t in s2].count('nl'), 'nl count broken'
    print('SELF-CHECK OK: detect h1=h2=1.0; uniform mean p=%.3f; permutation preserves multiset+nl' % mean_p)

if __name__ == '__main__':
    _selfcheck()
    print('Running positive control...')
    pc = positive_control(n_perm=500, n_fp_draws=30, seed=2024)
    print('PC:', pc)
