"""TASK H — shared model builder over the dependency-aware anchor lattice.

Builds a value-inference model (variables, domains, factors) from a sign-universe
inventory (conservative/split/merged) + the lattice's dependency audit, honoring
Art. XI/XII dependency-collapse.

Variables  = syllabic signs (A-only + AB-shared); domain = 65-slot LB CV grid.
Factors:
  * ANCHOR (unary, value-bearing).  Every catalogued anchor descends from the single
    META_CONTINUITY_LA_eq_LB meta-lineage (lattice: DEPENDENCY_COLLAPSED_independent
    _anchor_count = 0).  Three modes:
      'on'        : pin each anchored sign to its graded LB value  (INVENTORY-side /
                    positive-control view — treats stacked citations as if independent).
      'collapsed' : dependency-distinct value-bearing lineages ONLY -> 0 pins (the
                    honest Art. XII view; Egyptian LIN_EG has SEED_A=0).
      'null'      : random-anchor null — the SAME NUMBER of pins reassigned to random
                    signs with random grid values.
  * RELATIVE (value-free): substitution_neighbors + rel_class -> members share ONE
    coordinate (C or V axis).  Survives phoneme relabeling => ZERO absolute value
    information on its own (Art. XV).  Used for equivalence-class structure only.
  * MORPHOLOGICAL / FORMULA / STROKE: value-free structural / circular -> excluded from
    absolute value inference (recorded for the audit; never pin a label).

No subjective semantic plausibility anywhere.  Seed 20260708.
"""
import json, math, random
from collections import defaultdict

SEED = 20260708

VOWELS = ['a', 'e', 'i', 'o', 'u']
CONS = ['', 'd', 'j', 'k', 'm', 'n', 'p', 'q', 'r', 's', 't', 'w', 'z']  # '' = pure vowel
VGRID = [(c, v) for c in CONS for v in VOWELS]           # 65 slots
VIDX = {cv: i for i, cv in enumerate(VGRID)}
NV = len(VGRID)                                           # 65
H_MAX = math.log2(NV)                                     # 6.0224 bits


def parse_label(lab):
    if not lab or lab.startswith('*') or ':' in lab:
        return None
    s = ''.join(ch for ch in str(lab) if ch.isalpha()).lower()
    if not s:
        return None
    v = s[-1]
    if v not in VOWELS:
        return None
    c = s[:-1]
    if c == '':
        return ('', v)
    if c in CONS:
        return (c, v)
    return ('', v)   # diphthong / off-grid allograph -> pure-vowel bucket


def entropy_bits(counts):
    it = list(counts.values()) if isinstance(counts, dict) else list(counts)
    tot = sum(it)
    if tot == 0:
        return 0.0
    h = 0.0
    for c in it:
        if c > 0:
            p = c / tot
            h -= p * math.log2(p)
    return h


class Model:
    def __init__(self, inv_signs, continuity_mode='collapsed', rng=None):
        self.mode = continuity_mode
        self.rng = rng or random.Random(SEED)
        # syllabic variables only
        self.meta = {k: v for k, v in inv_signs.items()
                     if v.get('class') in ('A-only', 'AB-shared')}
        self.skey = list(self.meta.keys())
        self.sset = set(self.skey)
        self.cls = {k: self.meta[k]['class'] for k in self.skey}
        self.a_only = [k for k in self.skey if self.cls[k] == 'A-only']
        self.ab = [k for k in self.skey if self.cls[k] == 'AB-shared']

        # ---- anchor pins ----
        real = {}   # sign -> grid idx (graded LB value)
        for k in self.skey:
            ac = self.meta[k].get('anchor_coverage') or {}
            if self.meta[k].get('has_anchor_coverage'):
                lab = ac.get('conventional_value_LB_graded')
                coord = parse_label(lab)
                if coord is not None:
                    real[k] = VIDX[coord]
        self.n_anchored_signs = sum(1 for k in self.skey if self.meta[k].get('has_anchor_coverage'))
        self.n_real_pins = len(real)
        if self.mode == 'on':
            self.pin = dict(real)
        elif self.mode == 'collapsed':
            self.pin = {}                     # 0 dependency-distinct value-bearing pins
        elif self.mode == 'null':
            n = self.n_real_pins
            tgt = self.rng.sample(self.skey, min(n, len(self.skey)))
            self.pin = {s: self.rng.randrange(NV) for s in tgt}
        else:
            raise ValueError(self.mode)

        # ---- relative (value-free) edges: pairwise share-one-coordinate ----
        self.rel_edges = []
        seen = set()
        for k in self.skey:
            for nb in self.meta[k].get('substitution_neighbors') or []:
                if nb in self.sset:
                    e = tuple(sorted((k, nb)))
                    if e not in seen:
                        seen.add(e); self.rel_edges.append((e[0], e[1]))
        # rel_class cliques
        cls_members = defaultdict(list)
        for k in self.skey:
            rc = self.meta[k].get('rel_class')
            if rc:
                cls_members[rc].append(k)
        self.rel_classes = dict(cls_members)
        for rc, mem in cls_members.items():
            for i in range(len(mem)):
                for j in range(i + 1, len(mem)):
                    e = tuple(sorted((mem[i], mem[j])))
                    if e not in seen:
                        seen.add(e); self.rel_edges.append((e[0], e[1]))

        self.adj = defaultdict(set)
        for a, b in self.rel_edges:
            self.adj[a].add(b); self.adj[b].add(a)

    def components(self):
        seen = set(); comps = []
        for k in self.skey:
            if k in seen:
                continue
            stack = [k]; comp = set()
            while stack:
                x = stack.pop()
                if x in seen:
                    continue
                seen.add(x); comp.add(x)
                stack.extend(self.adj[x] - seen)
            comps.append(comp)
        return comps


def load_inventory(path):
    return json.load(open(path))['signs']
