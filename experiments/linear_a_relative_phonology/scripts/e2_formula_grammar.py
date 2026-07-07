#!/usr/bin/env python3
"""E2 - FORMULA GRAMMAR (LOGOS Constitution v2.2)

Induce finite-state / probabilistic formula structures from Linear A, split by
site, support, document type, chronology, inscription length. Two grammars:

  (A) the ADMINISTRATIVE LEDGER grammar  -> KU-RO / KI-RO / PO-TO-KU-RO
  (B) the VOTIVE / LIBATION formula family -> *SA-SA-RA(-ME) + A-TA-I-*301-WA-JA

NON-CIRCULAR discipline: sign-sequences (KU-RO, JA-SA-SA-RA-ME, ...) are treated
as ANONYMOUS RECURRING ANCHORS - conventional GORILA sign-names, NOT phonetic or
semantic values. No phonetic value is assigned. The only 'meaning' test used is
the ARITHMETIC one (a numeral after a total-anchor vs the cumulative sum of the
entry numerals that precede it) - a relative-structure property that is
independent of any reading. Highest claim layer: L2/L3 (structure/role); no
transfer licence claimed.

Seed 20260708.
"""
import json, collections, re, os

SEED = 20260708
ROOT = "/home/claude-runner/gitlab/n8n/logos-linear-a-relative-phonology-seals"
SRC = os.path.join(ROOT, "corpus/silver/inscriptions_structured.json")
OUTD = os.path.join(ROOT, "experiments/linear_a_relative_phonology/data")
REPD = os.path.join(ROOT, "experiments/linear_a_relative_phonology/reports")

TOTAL_ANCHORS = {"KU-RO", "PO-TO-KU-RO"}
DEFICIT_ANCHORS = {"KI-RO"}

# ---- commodity-logogram lexicon (pattern based, ledger scope) ------------
COM_ABBR = {"GRA","VIN","CYP","OLE","OLIV","VIR","HIDE","CAP","OVIS","SUS",
            "BOS","FIC","TELA","AROM","GRA+PA","MI"}
def wjoin(w): return "-".join(w)

def is_commodity(tok):
    """token = list of GORILA signs. True if it reads as a commodity logogram."""
    s = wjoin(tok)
    if s in TOTAL_ANCHORS or s in DEFICIT_ANCHORS:
        return False
    if "*301" in s or "*321" in s or "*325" in s:   # libation signs, not commodity
        return False
    if "+" in s:                                     # ligatured commodity sign
        return True
    if re.fullmatch(r"\*?\d+[A-Z]*", s):             # starred numeric logogram *304 etc
        return True
    for seg in tok:
        seg2 = re.sub(r"[\d₀-₉\[\]?+].*", "", seg)
        if seg2 in COM_ABBR and len(seg2) >= 3:
            return True
    if re.search(r"[A-Z]{3,}", s):                   # long all-caps run
        return True
    return False

# ---- token-class abstraction for the ledger FSA --------------------------
def classify_stream(r):
    """Return list of (class, raw) over the reading stream of one inscription."""
    out = []
    for t in r["stream"]:
        tt = t["t"]
        if tt == "word":
            s = wjoin(t["signs"])
            if s in TOTAL_ANCHORS:      cls = "TOT"
            elif s in DEFICIT_ANCHORS:  cls = "DEF"
            elif is_commodity(t["signs"]): cls = "LOG"
            else:                       cls = "W"
            out.append((cls, s))
        elif tt == "num":
            out.append(("N", t["v"]))
        elif tt == "other":
            raw = t.get("raw", "")
            if any(c in raw for c in "½¼⁄") or "1" in raw and "/" in raw:
                out.append(("FR", raw))
            else:
                out.append(("LOG", raw))   # bare logogram glyph
        # div / nl are layout, dropped from the token grammar
    return out

def load():
    with open(SRC) as f:
        return json.load(f)

# ==========================================================================
# (A) ADMINISTRATIVE LEDGER GRAMMAR
# ==========================================================================
def ledger_grammar(d):
    ledger = [r for r in d if any(t["t"] == "num" for t in r["stream"])]
    res = {"n_inscriptions": len(ledger)}

    # --- bigram transition FSA over token classes ---
    classes = ["W","LOG","N","FR","TOT","DEF"]
    START, END = "^", "$"
    trans = collections.Counter()
    unigram = collections.Counter()
    for r in ledger:
        seq = [c for c,_ in classify_stream(r) if c in classes]
        prev = START
        for c in seq:
            trans[(prev,c)] += 1; unigram[c] += 1; prev = c
        trans[(prev,END)] += 1
    # normalise
    rowtot = collections.Counter()
    for (a,b),n in trans.items(): rowtot[a] += n
    fsa = {}
    for (a,b),n in sorted(trans.items()):
        fsa.setdefault(a, {})[b] = round(n/rowtot[a], 4)
    res["unigram_counts"] = dict(unigram)
    res["fsa_transition_prob"] = fsa
    res["fsa_transition_counts"] = {f"{a}->{b}": n for (a,b),n in sorted(trans.items())}

    # --- entry regularity: is a value-token (LOG or W) followed by N? ---
    ent_pairs = collections.Counter()  # (carrier_class, next_is_num)
    for r in ledger:
        seq = [c for c,_ in classify_stream(r)]
        for i,c in enumerate(seq):
            if c in ("LOG","W"):
                nxt = seq[i+1] if i+1 < len(seq) else "$"
                ent_pairs[(c, nxt in ("N","FR"))] += 1
    res["entry_carrier_followed_by_number"] = {
        "LOG_yes": ent_pairs[("LOG",True)], "LOG_no": ent_pairs[("LOG",False)],
        "W_yes": ent_pairs[("W",True)],   "W_no": ent_pairs[("W",False)],
        "LOG_rate": round(ent_pairs[("LOG",True)]/max(1,ent_pairs[("LOG",True)]+ent_pairs[("LOG",False)]),4),
        "W_rate": round(ent_pairs[("W",True)]/max(1,ent_pairs[("W",True)]+ent_pairs[("W",False)]),4),
    }

    # --- TOTAL/DEFICIT slot: normalised position + follow-by-number ---
    def slot_stats(anchor_set):
        positions=[]; follow_num=0; occ=0; carriers=0
        for r in ledger:
            seq = classify_stream(r)
            L = len(seq)
            for i,(c,v) in enumerate(seq):
                if v in anchor_set:
                    occ += 1
                    positions.append(round(i/max(1,L-1),4) if L>1 else 1.0)
                    # next non-layout token
                    if i+1 < L and seq[i+1][0] in ("N","FR"): follow_num += 1
            if any(v in anchor_set for _,v in seq): carriers += 1
        return {
            "occurrences": occ, "carrier_inscriptions": carriers,
            "mean_norm_position": round(sum(positions)/len(positions),4) if positions else None,
            "frac_in_last_third": round(sum(p>=2/3 for p in positions)/len(positions),4) if positions else None,
            "followed_by_number": follow_num,
            "followed_by_number_rate": round(follow_num/occ,4) if occ else None,
        }
    res["TOTAL_slot"] = slot_stats(TOTAL_ANCHORS)
    res["DEFICIT_slot"] = slot_stats(DEFICIT_ANCHORS)

    # --- arithmetic sum-consistency of the TOTAL anchor (relative-structure test) ---
    exact=near=nofollow=occ=segfrac=0; examples=[]
    for r in ledger:
        seq = classify_stream(r)
        idx = [i for i,(c,v) in enumerate(seq) if v in TOTAL_ANCHORS]
        prev = 0
        for i in idx:
            occ += 1
            seg = seq[prev:i]
            psum = sum(v for c,v in seg if c=="N")
            nfrac = sum(1 for c,v in seg if c=="FR")
            nxt = None
            for j in range(i+1, min(i+3, len(seq))):
                if seq[j][0]=="N": nxt=seq[j][1]; break
                if seq[j][0] in ("W","LOG","TOT","DEF"): break
            prev = i+1
            if nxt is None: nofollow += 1; continue
            if psum==nxt and nxt>0:
                exact += 1
                if len(examples)<12: examples.append({"id":r["id"],"total":nxt,"cumsum":psum,"match":"exact"})
            elif abs(psum-nxt)<=2:
                near += 1
                if len(examples)<12: examples.append({"id":r["id"],"total":nxt,"cumsum":psum,"match":"near","nfrac":nfrac})
            if nfrac>0: segfrac += 1
    with_follow = occ - nofollow
    res["TOTAL_sum_consistency"] = {
        "occurrences": occ, "with_following_number": with_follow,
        "no_following_number": nofollow,
        "exact_match": exact, "near_match_within_2": near,
        "exact_rate_of_testable": round(exact/with_follow,4) if with_follow else None,
        "exact_or_near_rate_of_testable": round((exact+near)/with_follow,4) if with_follow else None,
        "testable_segments_with_fractions": segfrac,
        "note": "silver corpus stores only integer numerals; fraction glyphs (½ ¼ ...) are uncounted, which deflates exact matches on segments that carry them.",
        "examples": examples,
    }

    # --- coverage: fraction of ledger tokens / inscriptions parsed by the
    #     entry grammar  HEADING?  ( (W|LOG)+ (N FR?)?  )*  (TOT N)?  (DEF ...)? ---
    #     operationalised: token is 'covered' if it is W/LOG/N/FR/TOT/DEF (i.e. in
    #     the accounting alphabet). Report token- and inscription-level coverage.
    tok_cov=tok_all=0; full=0
    num_tot=num_wellformed=0        # meaningful: numeral immediately preceded by a value-carrier
    ins_parse=0                     # inscription is a clean [carrier (N|FR)?]+ [TOT N]? [DEF ...]? run
    for r in ledger:
        seq=[c for c,_ in classify_stream(r)]
        acct={"W","LOG","N","FR","TOT","DEF"}
        c=sum(1 for x in seq if x in acct)
        tok_cov+=c; tok_all+=len(seq)
        if seq and c==len(seq): full+=1
        for i,x in enumerate(seq):
            if x=="N":
                num_tot+=1
                if i>0 and seq[i-1] in ("W","LOG","TOT","DEF","FR"): num_wellformed+=1
        # clean-parse test: no two carriers with no number between is fine;
        # inscription parses if every numeral is well-formed (carrier-anchored)
        ok=all(not(x=="N" and (i==0 or seq[i-1] not in ("W","LOG","TOT","DEF","FR")))
               for i,x in enumerate(seq))
        if seq and ok: ins_parse+=1
    res["coverage"] = {
        "token_level_in_accounting_alphabet": round(tok_cov/tok_all,4) if tok_all else None,
        "token_level_note": "1.0 by construction (all non-layout tokens map to the accounting alphabet); reported only for completeness.",
        "numerals_total": num_tot,
        "numerals_anchored_to_carrier": num_wellformed,
        "numeral_wellformed_rate": round(num_wellformed/num_tot,4) if num_tot else None,
        "numeral_wellformed_note": "fraction of numerals immediately preceded by a value-carrier (W/LOG/TOT/DEF/FR) = a well-formed (carrier VALUE) accounting entry.",
        "inscriptions_all_numerals_wellformed": ins_parse,
        "inscriptions_all_numerals_wellformed_rate": round(ins_parse/len(ledger),4) if ledger else None,
    }

    # --- breakdowns by facet (carrier presence of TOT/DEF + entry density) ---
    def facet(keyfn):
        agg=collections.defaultdict(lambda: {"n":0,"with_TOT":0,"with_DEF":0,"numerals":0,"entries_WN":0})
        for r in ledger:
            k=keyfn(r); seq=classify_stream(r); a=agg[k]
            a["n"]+=1
            vals={v for _,v in seq}
            if vals & TOTAL_ANCHORS: a["with_TOT"]+=1
            if vals & DEFICIT_ANCHORS: a["with_DEF"]+=1
            a["numerals"]+=sum(1 for c,_ in seq if c=="N")
            cl=[c for c,_ in seq]
            a["entries_WN"]+=sum(1 for i in range(len(cl)-1) if cl[i] in ("W","LOG") and cl[i+1] in ("N","FR"))
        return {str(k):v for k,v in sorted(agg.items(), key=lambda kv:-kv[1]["n"])}
    res["by_support"] = facet(lambda r: r["support"])
    res["by_site"] = {k:v for k,v in list(facet(lambda r: r["site"]).items())[:10]}
    def periodkey(r):
        p=r.get("context") or "UNDATED"; return p
    res["by_period"] = facet(periodkey)
    def lenbin(r):
        n=sum(1 for c,_ in classify_stream(r) if c in ("W","LOG"))
        return "1carrier" if n<=1 else ("2-4carriers" if n<=4 else "5+carriers")
    res["by_length"] = facet(lenbin)
    return res

# ==========================================================================
# (B) VOTIVE / LIBATION FORMULA GRAMMAR
# ==========================================================================
# anchor families detected on the joined inscription sign-string (robust to
# GORILA word-division artefacts, e.g. 'JA-SA-SA-RA ME' or 'A SA-SA-RA-ME').
# opener family: X-TA-I-*301-... / TA-NA-I-*301-... / A-NA-TI-*301-... / bare *301-WA.
# excludes commodity ligatures (TE-*301, I+*301, MI+*301, DA+*301, ...).
OP_PAT = r"TA-I-\*301|TA-NA-I-\*301|A-NA-TI-\*301|\*301-WA"
ANCHOR_PATTERNS = [
    ("OP",  OP_PAT),            # A-TA-I-*301-WA-JA / TA-NA-I-*301-... opener family
    ("SSR", r"SA-SA-RA"),       # *SA-SA-RA(-ME) core anchor
    ("UNK", r"NA-KA-NA"),       # U-NA-KA-NA-SI / U-NA-RU-KA-NA-SI/TI/JA-SI
    ("IPN", r"PI-NA-M"),        # I-PI-NA-MA / I-PI-NA-MI-NA
    ("SIR", r"SI-RU"),          # SI-RU-TE / SI-RU
]

def votive_grammar(d):
    # votive carriers = any inscription whose joined sign string hits SSR or OP
    def joined(r): return "-".join(r["signs"])
    carriers=[r for r in d if re.search("SA-SA-RA", joined(r)) or re.search(OP_PAT, joined(r))]
    res={"n_carriers":len(carriers)}
    res["by_support"]=dict(collections.Counter(r["support"] for r in carriers))
    res["by_site"]=dict(collections.Counter(r["site"] for r in carriers))
    res["by_period"]=dict(collections.Counter((r.get("context") or "UNDATED") for r in carriers))

    # per inscription: ordered anchor labels (by first sign index) + fills
    fam_count=collections.Counter()
    seqs=[]
    for r in carriers:
        js=joined(r)
        hits=[]
        for lab,pat in ANCHOR_PATTERNS:
            m=re.search(pat, js)
            if m:
                # sign index = number of '-' before match start
                idx=js.count("-",0,m.start())
                hits.append((idx,lab)); fam_count[lab]+=1
        hits.sort()
        seqs.append({"id":r["id"],"support":r["support"],"order":[l for _,l in hits],
                     "words":[wjoin(w) for w in r["words"]]})
    res["anchor_family_carrier_counts"]=dict(fam_count)

    # pairwise order consistency: among inscriptions containing both A and B,
    # fraction where A precedes B (defines the canonical linear template)
    labs=[l for l,_ in ANCHOR_PATTERNS]
    order=collections.Counter(); both=collections.Counter()
    for s in seqs:
        pos={l:i for i,l in enumerate(s["order"])}
        for a in labs:
            for b in labs:
                if a!=b and a in pos and b in pos:
                    both[(a,b)]+=1
                    if pos[a]<pos[b]: order[(a,b)]+=1
    pair=[]
    for a in labs:
        for b in labs:
            if a<b and both[(a,b)]:
                fwd=order[(a,b)]; n=both[(a,b)]
                pair.append({"pair":f"{a}<{b}","n_both":n,"a_before_b":fwd,
                             "consistency":round(max(fwd,n-fwd)/n,4),
                             "dominant":f"{a}<{b}" if fwd>=n-fwd else f"{b}<{a}"})
    res["pairwise_order"]=pair

    # canonical template = topological order by 'a precedes b in majority'
    score=collections.Counter()
    for a in labs:
        for b in labs:
            if a!=b and both[(a,b)]:
                if order[(a,b)]>both[(a,b)]-order[(a,b)]: score[a]+=1
    canon=sorted([l for l in labs if fam_count[l]], key=lambda l:-score[l])
    res["canonical_template"]=canon
    res["template_gloss"]={"OP":"opener *301-WA family","SSR":"*SA-SA-RA(-ME) core",
        "UNK":"U-NA-(RU-)KA-NA-SI/TI","IPN":"I-PI-NA-M(A/INA)","SIR":"SI-RU(-TE)"}

    # coverage: how many carriers' observed anchor order is NON-INVERTING wrt the
    # canonical template, i.e. the observed sequence embeds as a subsequence of the
    # canonical template (missing slots allowed; order must not invert).
    def obs_embeds_in_template(order, templ):
        it=iter(templ)
        return all(any(t==o for t in it) for o in order)
    full=sum(1 for s in seqs if obs_embeds_in_template(s["order"], canon))
    # slot-fill matrix
    res["slot_fill_rate"]={l:round(fam_count[l]/len(carriers),4) for l in labs}
    # --- permutation null: is the ZERO-inversion global order significant? ---
    # observed statistic = # ordered co-occurring pairs that are perfectly
    # consistent (all same direction). Null = shuffle each carrier's anchor order.
    import random
    multi=[s["order"] for s in seqs if len(s["order"])>=2]
    def max_consistency_pairs(orders):
        o2=collections.Counter(); b2=collections.Counter()
        for od in orders:
            pos={l:i for i,l in enumerate(od)}
            for a in labs:
                for b in labs:
                    if a!=b and a in pos and b in pos:
                        b2[(a,b)]+=1
                        if pos[a]<pos[b]: o2[(a,b)]+=1
        perfect=0; tested=0
        for a in labs:
            for b in labs:
                if a<b and b2[(a,b)]:
                    tested+=1
                    if o2[(a,b)] in (0,b2[(a,b)]): perfect+=1
        return perfect, tested
    obs_perfect, obs_tested = max_consistency_pairs(multi)
    rng=random.Random(SEED); N=20000; ge=0
    for _ in range(N):
        shuf=[]
        for od in multi:
            od2=od[:]; rng.shuffle(od2); shuf.append(od2)
        p,_t=max_consistency_pairs(shuf)
        if p>=obs_perfect: ge+=1
    res["order_permutation_null"]={
        "n_multi_anchor_carriers":len(multi),
        "observed_perfectly_consistent_pairs":obs_perfect,
        "co_occurring_pairs_tested":obs_tested,
        "n_permutations":N,
        "p_value_ge_observed":round((ge+1)/(N+1),6),
        "note":"null shuffles each carrier's realised anchor order uniformly; statistic = number of co-occurring anchor pairs that are 100% consistent in direction. Small n per pair -> treat as suggestive.",
    }
    res["template_order_coverage"]={
        "carriers_matching_canonical_subsequence":full,
        "rate":round(full/len(carriers),4) if carriers else None,
        "note":"carriers whose observed anchor order is a subsequence of the canonical template (extra/missing slots allowed, order must not invert).",
    }
    # length structure of the formula: n anchors realised per carrier
    res["anchors_realised_hist"]=dict(collections.Counter(len(s["order"]) for s in seqs))
    res["carrier_sequences"]=seqs
    return res

def main():
    d=load()
    out={"task":"E2_formula_grammar","seed":SEED,
         "constitution":"v2.2","claim_layer":"L2/L3 structure-role; no phonetic value; no transfer licence",
         "corpus":{"n_inscriptions":len(d)}}
    out["ledger_grammar"]=ledger_grammar(d)
    out["votive_libation_grammar"]=votive_grammar(d)
    os.makedirs(OUTD, exist_ok=True)
    p=os.path.join(OUTD,"E2_formula.json")
    with open(p,"w") as f: json.dump(out,f,ensure_ascii=False,indent=1)
    print("wrote",p)
    # brief stdout
    lg=out["ledger_grammar"]; vg=out["votive_libation_grammar"]
    print("LEDGER n=",lg["n_inscriptions"],"TOTAL slot=",lg["TOTAL_slot"])
    print("TOTAL sum-consistency=",lg["TOTAL_sum_consistency"]["exact_match"],
          "/",lg["TOTAL_sum_consistency"]["with_following_number"],
          "exact_or_near=",lg["TOTAL_sum_consistency"]["exact_or_near_rate_of_testable"])
    print("entry carrier->num:",lg["entry_carrier_followed_by_number"])
    print("VOTIVE carriers=",vg["n_carriers"],"canon=",vg["canonical_template"],
          "coverage=",vg["template_order_coverage"])
    return out

if __name__=="__main__":
    main()
