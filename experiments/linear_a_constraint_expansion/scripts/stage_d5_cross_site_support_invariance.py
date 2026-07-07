import json, collections, random, math
random.seed(42)
CORP="/home/claude-runner/gitlab/n8n/logos/corpus/silver/inscriptions_structured.json"
d=json.load(open(CORP))

def issyll(s): return '+' not in s and not s.isdigit()

# Build records: word (list of syllabic signs), site, support
recs=[]
for x in d:
    site=x['site']; sup=x['support']
    for w in x.get('words',[]):
        ws=[s for s in w if issyll(s)]
        if len(ws)>=2:
            recs.append((ws,site,sup))
print("total multi-sign syllabic words:",len(recs))

def cellsel(recs, sites=None, sups=None, notsites=None, notsups=None):
    out=[]
    for ws,site,sup in recs:
        if sites and site not in sites: continue
        if sups and sup not in sups: continue
        if notsites and site in notsites: continue
        if notsups and sup in notsups: continue
        out.append(ws)
    return out

# ---- Structural statistic: positional specialization ----
# For a set of words, measure mutual information I(sign; position-class) where
# position-class in {initial, medial, final}. Null = shuffle sign order within each word
# (preserves each word's multiset AND set overall sign freq => degree/metadata preserving).
def posMI(words):
    # counts
    joint=collections.Counter(); psign=collections.Counter(); ppos=collections.Counter()
    N=0
    for w in words:
        L=len(w)
        for i,s in enumerate(w):
            pos='I' if i==0 else ('F' if i==L-1 else 'M')
            joint[(s,pos)]+=1; psign[s]+=1; ppos[pos]+=1; N+=1
    if N==0: return 0.0
    mi=0.0
    for (s,pos),c in joint.items():
        pxy=c/N; px=psign[s]/N; py=ppos[pos]/N
        mi+=pxy*math.log2(pxy/(px*py))
    return mi

def null_posMI(words, B=1000):
    obs=posMI(words)
    ge=0; vals=[]
    for _ in range(B):
        sh=[random.sample(w,len(w)) for w in words]
        v=posMI(sh); vals.append(v)
        if v>=obs: ge+=1
    mean=sum(vals)/len(vals)
    sd=(sum((v-mean)**2 for v in vals)/len(vals))**0.5
    z=(obs-mean)/sd if sd>0 else float('nan')
    p=(ge+1)/(B+1)
    return obs,mean,z,p

# ---- Final-sign concentration: top-signs coverage of final position vs null ----
def final_conc(words,k=5):
    fin=collections.Counter(w[-1] for w in words)
    tot=sum(fin.values())
    top=sum(c for _,c in fin.most_common(k))
    return top/tot if tot else 0.0

# Define contexts
contexts={
 "ALL": cellsel(recs),
 "Tablet(admin)": cellsel(recs,sups={'Tablet'}),
 "StoneVessel(libation)": cellsel(recs,sups={'Stone vessel'}),
 "HT_Tablet": cellsel(recs,sites={'Haghia Triada'},sups={'Tablet'}),
 "nonHT_Tablet": cellsel(recs,sups={'Tablet'},notsites={'Haghia Triada'}),
 "nonHT_nonTablet": cellsel(recs,notsites={'Haghia Triada'},notsups={'Tablet','Nodule'}),
 "StoneVessel_multisite": cellsel(recs,sups={'Stone vessel'}),
}
print("\n=== POSITIONAL MI (sign x position-class), within-word-shuffle null, B=1000 ===")
for name,ws in contexts.items():
    if len(ws)<15:
        print(f"  {name:28s} n={len(ws):4d}  [too few]"); continue
    obs,mean,z,p=null_posMI(ws,B=1000)
    fc=final_conc(ws)
    print(f"  {name:28s} n={len(ws):4d}  MI={obs:.4f} null={mean:.4f} z={z:6.1f} p={p:.4f}  finalTop5={fc:.2f}")

print("\n=== CROSS-GENRE POSITIONAL-GRAMMAR AGREEMENT ===")
# per-sign final-preference = P(sign in final pos | sign occurs), using only words len>=2
def finalpref(words, minc=6):
    tot=collections.Counter(); fin=collections.Counter(); ini=collections.Counter()
    for w in words:
        L=len(w)
        for i,s in enumerate(w):
            tot[s]+=1
            if i==L-1: fin[s]+=1
            if i==0: ini[s]+=1
    fp={s:fin[s]/tot[s] for s in tot if tot[s]>=minc}
    ip={s:ini[s]/tot[s] for s in tot if tot[s]>=minc}
    return fp,ip,tot

import statistics
def pearson(xs,ys):
    n=len(xs); mx=sum(xs)/n; my=sum(ys)/n
    cov=sum((a-mx)*(b-my) for a,b in zip(xs,ys))
    sx=(sum((a-mx)**2 for a in xs))**.5; sy=(sum((b-my)**2 for b in ys))**.5
    return cov/(sx*sy) if sx*sy>0 else float('nan')

TA=cellsel(recs,sups={'Tablet'})
SV=cellsel(recs,sups={'Stone vessel'})
fpA,ipA,totA=finalpref(TA); fpB,ipB,totB=finalpref(SV)
common=sorted(set(fpA)&set(fpB))
print(f"signs w/ >=6 occ in BOTH admin-tablet & stone-vessel: {len(common)}")
xf=[fpA[s] for s in common]; yf=[fpB[s] for s in common]
xi=[ipA[s] for s in common]; yi=[ipB[s] for s in common]
rf=pearson(xf,yf); ri=pearson(xi,yi)
print(f"  final-preference cross-genre Pearson r = {rf:.3f}")
print(f"  initial-preference cross-genre Pearson r = {ri:.3f}")

# Null: shuffle within words in each genre separately, recompute cross-genre r. metadata-preserving.
def shuf(words): return [random.sample(w,len(w)) for w in words]
B=2000; ge_f=0; ge_i=0; rf_null=[]; ri_null=[]
for _ in range(B):
    a=shuf(TA); b=shuf(SV)
    fa,ia,_=finalpref(a); fb,ib,_=finalpref(b)
    cm=sorted(set(fa)&set(fb))
    rfn=pearson([fa[s] for s in cm],[fb[s] for s in cm])
    rin=pearson([ia[s] for s in cm],[ib[s] for s in cm])
    rf_null.append(rfn); ri_null.append(rin)
    if rfn>=rf: ge_f+=1
    if rin>=ri: ge_i+=1
print(f"  final r null mean={sum(rf_null)/B:.3f}  p(r>=obs)={(ge_f+1)/(B+1):.4f}")
print(f"  initial r null mean={sum(ri_null)/B:.3f}  p(r>=obs)={(ge_i+1)/(B+1):.4f}")

print("\n  Top FINAL-preferring signs shared (fp>0.5 in both):")
for s in common:
    if fpA[s]>0.5 and fpB[s]>0.5:
        print(f"    {s:6s} tablet={fpA[s]:.2f}(n{totA[s]})  stonevessel={fpB[s]:.2f}(n{totB[s]})")
print("  Top INITIAL-preferring signs shared (ip>0.5 in both):")
for s in common:
    if ipA[s]>0.5 and ipB[s]>0.5:
        print(f"    {s:6s} tablet={ipA[s]:.2f}(n{totA[s]})  stonevessel={ipB[s]:.2f}(n{totB[s]})")

print("\n=== SITE-vs-SUPPORT DECOMPOSITION of positional grammar ===")
def cross_r(A,B,which,B_null=2000):
    fA,iA,_=finalpref(A); fB,iB,_=finalpref(B)
    src=(fA,fB) if which=='final' else (iA,iB)
    cm=sorted(set(src[0])&set(src[1]))
    if len(cm)<8: return None
    robs=pearson([src[0][s] for s in cm],[src[1][s] for s in cm])
    ge=0
    for _ in range(B_null):
        a=shuf(A); b=shuf(B)
        fa,ia,_=finalpref(a); fb,ib,_=finalpref(b)
        s2=(fa,fb) if which=='final' else (ia,ib)
        c2=sorted(set(s2[0])&set(s2[1]))
        rn=pearson([s2[0][s] for s in c2],[s2[1][s] for s in c2])
        if rn>=robs: ge+=1
    return len(cm),robs,(ge+1)/(B_null+1)

HTt=cellsel(recs,sites={'Haghia Triada'},sups={'Tablet'})
nHTt=cellsel(recs,sups={'Tablet'},notsites={'Haghia Triada'})
NN=cellsel(recs,notsites={'Haghia Triada'},notsups={'Tablet','Nodule'})  # 3rd genre, held-out

tests=[
 ("FINAL  site-only (HTtab vs nonHTtab)", HTt,nHTt,'final'),
 ("FINAL  support (Tablet vs StoneVessel)", TA,SV,'final'),
 ("INIT   site-only (HTtab vs nonHTtab)", HTt,nHTt,'initial'),
 ("INIT   support (Tablet vs StoneVessel)", TA,SV,'initial'),
 ("INIT   HELDOUT 3rd genre (Tablet vs nonHT-nonTab)", TA,NN,'initial'),
 ("INIT   HELDOUT (StoneVessel vs nonHT-nonTab)", SV,NN,'initial'),
 ("FINAL  HELDOUT 3rd genre (Tablet vs nonHT-nonTab)", TA,NN,'final'),
]
for name,A,B,which in tests:
    r=cross_r(A,B,which)
    if r is None: print(f"  {name:48s} [too few common signs]"); continue
    n,ro,p=r
    flag="INVARIANT" if p<0.05 else "confounded/ns"
    print(f"  {name:48s} nsign={n:3d} r={ro:+.3f} p={p:.4f}  {flag}")

print("\n=== Is INITIAL invariance just the vowel-initial rule? (drop A,I,U,E,O) ===")
def cross_r_excl(A,B,which,excl,B_null=2000):
    fA,iA,_=finalpref(A); fB,iB,_=finalpref(B)
    src=(fA,fB) if which=='final' else (iA,iB)
    cm=sorted((set(src[0])&set(src[1]))-set(excl))
    robs=pearson([src[0][s] for s in cm],[src[1][s] for s in cm])
    ge=0
    for _ in range(B_null):
        a=shuf(A); b=shuf(B)
        fa,ia,_=finalpref(a); fb,ib,_=finalpref(b)
        s2=(fa,fb) if which=='final' else (ia,ib)
        c2=sorted((set(s2[0])&set(s2[1]))-set(excl))
        rn=pearson([s2[0][s] for s in c2],[s2[1][s] for s in c2])
        if rn>=robs: ge+=1
    return len(cm),robs,(ge+1)/(B_null+1)
V={'A','I','U','E','O'}
for name,A,B in [("Tablet vs StoneVessel",TA,SV),("Tablet vs nonHT-nonTab",TA,NN),("StoneVessel vs nonHT-nonTab",SV,NN)]:
    n,r,p=cross_r_excl(A,B,'initial',V)
    print(f"  INIT no-vowels {name:30s} nsign={n} r={r:+.3f} p={p:.4f}")
