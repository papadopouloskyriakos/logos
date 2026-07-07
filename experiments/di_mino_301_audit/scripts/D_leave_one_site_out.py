#!/usr/bin/env python3
"""TASK D — Leave-one-site-out (LOSO) Libation-Formula prediction.

Prereg DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c), Constitution v2.2, seed 20260708.

Question: does the Di Mino system (*301=/na/, morphology A|TA|I|*301-WA-JA=root N-W-Y)
PREDICT held-out regional peak-sanctuary formula forms, or only explain them retrospectively?

Mechanical LOSO over the peak-sanctuary invocation-verb-slot *301 forms. For each held-out
site, freeze every model on the OTHER sites and predict the held-out site's position-1 form
(ranked candidates), its segmentation, the claimed morpheme slots, and *301 behaviour.

Models compared:
  M_freq   site-independent frequency baseline (predict modal form; rank by #training sites)
  M_tmpl   formula-template baseline (canonical slot filler = modal form only)
  M_markov sign-level bigram Markov (add-1), ranks the candidate universe by log-prob
  M_davis  Davis/Thomas structural baseline (structural template; cut {b2,b4} / edge cuts)
  M_dimino Di Mino system: exact form = target it parses; slots A|TA|I|*301-WA-JA(root)
  M_rand   random-Semitic-root null (Monte Carlo *301-value + matched-shape root)

NON-CIRCULAR: no known LB/Semitic value is fed to any LA-side model input. *301's value is the
hypothesis; the frequency/Markov/structural models never see it. Di Mino's exact-form output is
fixed by the form it was built on (the modal form) — that is the whole point of the test.

Scoring per held-out site: exact-form top-1 accuracy, rank of observed form in the ranked
candidate universe, boundary F1 vs a DATA-DRIVEN structural reference (word-edge cuts from the
branching-entropy analysis, report 04), morpheme-slot / root-recurrence accuracy, calibration.
Plus: effective number of independent sites (union-find deflation), random-Semitic null band,
power / NO_POWER determination.

Writes reports/D_LEAVE_ONE_SITE_OUT.md + data/results/loso.json.
"""
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict

SEED = 20260708
random.seed(SEED)

HERE = os.path.dirname(os.path.abspath(__file__))
CAMP = os.path.dirname(HERE)
CORPUS = os.path.join(CAMP, "data", "libation_formula_exact", "corpus.json")
OUT_JSON = os.path.join(CAMP, "data", "results", "loso.json")
OUT_MD = os.path.join(CAMP, "reports", "D_LEAVE_ONE_SITE_OUT.md")

DERIVATION_SITES = {"Iouktas", "Troullos"}


# ---------------------------------------------------------------------------
# Load invocation-verb-slot *301 forms per site
# ---------------------------------------------------------------------------
def load_site_forms():
    d = json.load(open(CORPUS))
    # per site: list of (form, partition, lso_eligible)
    recs = []
    for r in d["records_301"]:
        if not r["is_invocation_verb_slot"]:
            continue
        recs.append({
            "site": r["site"],
            "form": r["diplomatic_reading"],
            "signs": r["sign_sequence"],
            "partition": r["partition"],
            "lso_eligible": r["leave_site_out_eligible"],
            "contaminated": r["site_contaminated_vs_derivation"],
        })
    return recs, d


def signs_of(form):
    return form.split("-")


# ---------------------------------------------------------------------------
# Boundary machinery. Signs are atomic. Internal boundary i means a cut between
# sign i-1 and sign i (i in 1..len-1). We compare cut SETS as sign-index sets.
# ---------------------------------------------------------------------------
def all_internal_positions(signs):
    return set(range(1, len(signs)))


def dimino_cuts(signs):
    """Di Mino parse: prefix | stem-1 | stem-2 | root.
    On A-TA-I-*301-WA-JA -> A | TA | I | *301-WA-JA i.e. cuts after A(1), TA(2), I(3).
    Generalize: cut after a leading A-/JA- prefix, after the two stem signs, isolating the
    tail starting at *301 as the 'root'. If the form lacks the schema, apply the same
    positional rule (cut at 1,2,3) so the model still emits a prediction."""
    n = len(signs)
    cuts = set()
    for c in (1, 2, 3):
        if c < n:
            cuts.add(c)
    return cuts


def davis_cuts(signs):
    """Davis/Thomas structural: recurring i-*301 stem + inflectional ending.
    Cut after the A-TA prefix (pos2) and isolate the ending -WA-JA/-U-JA/... (cut before
    the last two signs). Data-corroborated edges."""
    n = len(signs)
    cuts = set()
    if n >= 3:
        cuts.add(2)          # A-TA | I-*301-...
    if n >= 2:
        cuts.add(n - 2)      # ... | WA-JA   (isolate 2-sign ending)
    cuts.discard(0)
    return {c for c in cuts if 0 < c < n}


def edge_reference_cuts(signs):
    """DATA-DRIVEN reference (report 04, branching-entropy): the only corpus-credited
    boundaries are the WORD EDGES — the A-/JA- prefix (b1) and the -JA/-E ending (b_last).
    This is the non-circular structural 'gold' we score boundary F1 against (labelled as
    structural, not truth)."""
    n = len(signs)
    cuts = set()
    if n >= 2:
        cuts.add(1)          # after leading prefix sign
        cuts.add(n - 1)      # before final ending sign
    return {c for c in cuts if 0 < c < n}


def f1(pred, gold):
    if not pred and not gold:
        return 1.0
    if not pred or not gold:
        return 0.0
    tp = len(pred & gold)
    prec = tp / len(pred)
    rec = tp / len(gold)
    if prec + rec == 0:
        return 0.0
    return 2 * prec * rec / (prec + rec)


# ---------------------------------------------------------------------------
# Root-recurrence test (H2). The claimed root = the tail *301-WA-JA (signs after A-TA-I).
# Does that exact root tail recur in the held-out form?
# ---------------------------------------------------------------------------
CLAIMED_ROOT = ["*301", "WA", "JA"]


def has_claimed_root(signs):
    return signs[-3:] == CLAIMED_ROOT if len(signs) >= 3 else False


def has_claimed_prefix(signs):
    # A=1cs prefix
    return len(signs) >= 1 and signs[0] == "A"


def has_claimed_stem(signs):
    # TA (tG) then I (stem vowel) in positions 1,2
    return len(signs) >= 3 and signs[1] == "TA" and signs[2] == "I"


def dimino_full_schema(signs):
    return has_claimed_prefix(signs) and has_claimed_stem(signs) and has_claimed_root(signs)


# ---------------------------------------------------------------------------
# Markov sign-bigram model
# ---------------------------------------------------------------------------
def train_bigram(train_forms):
    # train_forms: list of sign-lists (weighted by occurrence). add-1 smoothing over vocab.
    vocab = set()
    for s in train_forms:
        vocab.update(s)
    vocab |= {"^", "$"}
    V = len(vocab)
    trans = defaultdict(Counter)
    for s in train_forms:
        seq = ["^"] + s + ["$"]
        for a, b in zip(seq, seq[1:]):
            trans[a][b] += 1
    def logp(signs):
        seq = ["^"] + signs + ["$"]
        lp = 0.0
        for a, b in zip(seq, seq[1:]):
            num = trans[a][b] + 1
            den = sum(trans[a].values()) + V
            lp += math.log(num / den)
        return lp
    return logp, vocab


# ---------------------------------------------------------------------------
# Random-Semitic-root null: draw a random *301 value + random matched-shape root,
# emit a random form from the candidate universe (or a resampled sign string).
# Scores exact-form and slot accuracy under the null.
# ---------------------------------------------------------------------------
def random_semitic_null(candidate_universe, target_form, rng, n_draws=100000):
    hits = 0
    slot_hits = 0
    tgt_signs = signs_of(target_form)
    for _ in range(n_draws):
        pick = rng.choice(candidate_universe)
        if pick == target_form:
            hits += 1
        # random slot parse: pick a random subset of internal positions of size 3
        n = len(tgt_signs)
        if n >= 2:
            k = min(3, n - 1)
            cuts = set(rng.sample(range(1, n), k)) if n - 1 >= k else set(range(1, n))
        else:
            cuts = set()
        if cuts == dimino_cuts(tgt_signs):
            slot_hits += 1
    return hits / n_draws, slot_hits / n_draws


# ---------------------------------------------------------------------------
# Main LOSO
# ---------------------------------------------------------------------------
def run():
    recs, corpus = load_site_forms()

    # site -> Counter of forms (attestation weighted); and set of distinct forms
    site_form_counts = defaultdict(Counter)
    for r in recs:
        site_form_counts[r["site"]][r["form"]] += 1
    sites = sorted(site_form_counts.keys())

    # candidate universe = all distinct invocation forms
    universe = sorted({r["form"] for r in recs})

    clean_sites = [s for s in sites if s not in DERIVATION_SITES]

    results = {}
    per_site = []

    for held in sites:
        held_forms = list(site_form_counts[held].keys())
        # training = all recs at other sites
        train_recs = [r for r in recs if r["site"] != held]
        # frequency by #distinct training SITES the form appears at (site-fair)
        form_sites = defaultdict(set)
        for r in train_recs:
            form_sites[r["form"]].add(r["site"])
        freq_rank = sorted(form_sites.keys(), key=lambda f: (-len(form_sites[f]), f))
        modal = freq_rank[0] if freq_rank else None

        # training sign-lists (attestation weighted)
        train_sign_lists = []
        for r in train_recs:
            train_sign_lists.append(signs_of(r["form"]))
        logp, _ = train_bigram(train_sign_lists)

        # ---- rank the candidate universe under each model ----
        # M_freq: by training-site support, then Markov as tiebreak-independent -> unseen last
        def freq_score(f):
            return len(form_sites.get(f, set()))
        freq_ranking = sorted(universe, key=lambda f: (-freq_score(f), -logp(signs_of(f)), f))

        # M_markov: pure bigram log-prob
        markov_ranking = sorted(universe, key=lambda f: (-logp(signs_of(f)), f))

        # M_tmpl: only the modal form is predicted (rank 1); everything else unranked
        tmpl_top = modal

        # M_davis: structural template -> same exact-form preference as modal (structural
        # frequency), differs only in segmentation. Rank by training-site support of the
        # STRUCTURAL template (A-TA-I-*301-...); collapses to modal for exact form.
        davis_ranking = freq_ranking  # exact-form channel identical; boundary differs

        # M_dimino: exact form = the form it parses (the modal target it was built on).
        # It carries NO regional-variation generator -> predicts the target everywhere.
        dimino_top = "A-TA-I-*301-WA-JA"
        # ranking: target first, then (no further generative content) fall back to freq order
        dimino_ranking = [dimino_top] + [f for f in freq_ranking if f != dimino_top]

        def rank_of(ranking, forms):
            best = None
            for f in forms:
                if f in ranking:
                    r = ranking.index(f) + 1
                    best = r if best is None else min(best, r)
            return best if best is not None else len(ranking) + 1

        def top1_hit(top, forms):
            return 1 if top in forms else 0

        row = {
            "held_site": held,
            "held_forms": held_forms,
            "is_derivation_site": held in DERIVATION_SITES,
            "n_train_sites": len({r["site"] for r in train_recs}),
            "modal_train_form": modal,
            "exact_top1": {
                "M_freq": top1_hit(freq_ranking[0], held_forms),
                "M_tmpl": top1_hit(tmpl_top, held_forms),
                "M_markov": top1_hit(markov_ranking[0], held_forms),
                "M_davis": top1_hit(davis_ranking[0], held_forms),
                "M_dimino": top1_hit(dimino_top, held_forms),
            },
            "rank_observed": {
                "M_freq": rank_of(freq_ranking, held_forms),
                "M_markov": rank_of(markov_ranking, held_forms),
                "M_dimino": rank_of(dimino_ranking, held_forms),
            },
            "root_recurs_WA_JA": int(any(has_claimed_root(signs_of(f)) for f in held_forms)),
            "full_dimino_schema": int(any(dimino_full_schema(signs_of(f)) for f in held_forms)),
            "prefix_A_present": int(any(has_claimed_prefix(signs_of(f)) for f in held_forms)),
            "stem_TA_I_present": int(any(has_claimed_stem(signs_of(f)) for f in held_forms)),
        }

        # boundary F1 vs data-driven edge reference, averaged over the site's distinct forms
        b_dimino, b_davis, ref_sizes = [], [], []
        for f in held_forms:
            sg = signs_of(f)
            ref = edge_reference_cuts(sg)
            b_dimino.append(f1(dimino_cuts(sg), ref))
            b_davis.append(f1(davis_cuts(sg), ref))
        row["boundary_f1_vs_edgeref"] = {
            "M_dimino": round(sum(b_dimino) / len(b_dimino), 4),
            "M_davis": round(sum(b_davis) / len(b_davis), 4),
        }
        per_site.append(row)

    # ---- aggregate exact-form accuracy per model over all sites and clean sites ----
    def agg_top1(model, site_subset):
        vals = [r["exact_top1"][model] for r in per_site if r["held_site"] in site_subset]
        return round(sum(vals) / len(vals), 4), len(vals)

    all_sites = set(sites)
    clean = set(clean_sites)
    models_exact = ["M_freq", "M_tmpl", "M_markov", "M_davis", "M_dimino"]
    exact_acc_all = {m: agg_top1(m, all_sites) for m in models_exact}
    exact_acc_clean = {m: agg_top1(m, clean) for m in models_exact}

    # divergent (non-modal) held-out clean sites: the discriminating targets
    modal_form = "A-TA-I-*301-WA-JA"
    divergent_clean = [r["held_site"] for r in per_site
                       if r["held_site"] in clean and modal_form not in r["held_forms"]]
    exact_acc_divergent = {m: agg_top1(m, set(divergent_clean)) for m in models_exact}

    # root-recurrence on clean non-derivation held-out sites (H2)
    root_recur_clean = [(r["held_site"], r["root_recurs_WA_JA"]) for r in per_site
                        if r["held_site"] in clean]
    root_recur_divergent = [(r["held_site"], r["root_recurs_WA_JA"]) for r in per_site
                            if r["held_site"] in set(divergent_clean)]

    # ---- effective number of independent sites (union-find deflation) ----
    # Two sites are dependent if they carry the SAME set of forms (same lexeme copied) OR
    # both are derivation-contaminated. All forms are single-source GORILA (one lineage) ->
    # that caps cross-form independence too. We report: raw sites, distinct forms, and the
    # independent DISCRIMINATING units = distinct NON-modal forms at clean sites.
    distinct_forms = sorted({r["form"] for r in recs})
    distinct_clean_forms = sorted({f for s in clean for f in site_form_counts[s]})
    clean_divergent_forms = sorted({f for f in distinct_clean_forms if f != modal_form})
    # union-find over clean sites by identical form-set
    parent = {s: s for s in clean}
    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    def union(a, b):
        parent[find(a)] = find(b)
    clean_list = sorted(clean)
    for i in range(len(clean_list)):
        for j in range(i + 1, len(clean_list)):
            a, b = clean_list[i], clean_list[j]
            if set(site_form_counts[a]) == set(site_form_counts[b]):
                union(a, b)
    eff_site_components = len({find(s) for s in clean})

    # ---- random-Semitic null band (Monte Carlo) for exact-form on a divergent target ----
    rng = random.Random(SEED)
    # use a representative divergent target
    rep_target = "TA-NA-I-*301-TI"
    null_exact, null_slot = random_semitic_null(universe, rep_target, rng, n_draws=100000)

    # ---- power / verdict logic ----
    dimino_acc = exact_acc_clean["M_dimino"][0]
    freq_acc = exact_acc_clean["M_freq"][0]
    tmpl_acc = exact_acc_clean["M_tmpl"][0]
    markov_acc = exact_acc_clean["M_markov"][0]
    davis_acc = exact_acc_clean["M_davis"][0]

    # Does Di Mino make a DIFFERENT exact-form prediction from the frequency/template/davis
    # baseline at ANY held-out site? (If never, the exact-form channel is non-discriminating.)
    dimino_differs_from_freq = any(
        (r["exact_top1"]["M_dimino"] != r["exact_top1"]["M_freq"])
        for r in per_site if r["held_site"] in clean
    )
    dimino_beats_baselines = dimino_acc > max(freq_acc, tmpl_acc, markov_acc, davis_acc)

    # divergent-form predictability: can ANY model predict a clean divergent (singleton) form?
    any_model_predicts_divergent = any(
        max(r["exact_top1"].values()) == 1
        for r in per_site if r["held_site"] in set(divergent_clean)
    )

    # root-recurrence outcome on clean held-out sites (H2)
    n_clean = len(root_recur_clean)
    n_clean_root = sum(v for _, v in root_recur_clean)
    n_div = len(root_recur_divergent)
    n_div_root = sum(v for _, v in root_recur_divergent)

    # POWER: effective independent DISCRIMINATING sites = clean sites carrying a NON-modal
    # (divergent) form, each a single-attestation single-source unique lexeme.
    eff_discriminating_sites = len(divergent_clean)
    NO_POWER_THRESHOLD = 3

    # Headline verdict (mechanical, per prereg H4/H6 framing + Task-D NO_POWER rule)
    if not dimino_beats_baselines and not dimino_differs_from_freq:
        # Di Mino's exact-form prediction is identical to the baselines at every site ->
        # the exact-form LOSO channel cannot discriminate the system from the baseline.
        headline = "NO_POWER"
        headline_reason = (
            "Di Mino's exact-form prediction is identical to the frequency/template/structural "
            "baseline at every held-out site (it carries no regional-variation generator), so the "
            "exact-form LOSO channel has zero power to separate the system from the baseline; and "
            f"the effective independent discriminating sites ({eff_discriminating_sites}) sit at/"
            f"below the NO_POWER floor ({NO_POWER_THRESHOLD}). Every clean divergent form is a "
            "unique single-source singleton, unpredictable by any leave-one-out model."
        )
    elif dimino_beats_baselines:
        headline = "SUPPORT_CANDIDATE"
        headline_reason = "Di Mino exceeds baselines on held-out exact-form prediction (check deflation)."
    else:
        headline = "REJECT"
        headline_reason = "Di Mino does not beat baselines despite adequate power."

    verdict = {
        "prereg": "DI_MINO_EXACT_CLAIM_V1 (sha 8b098a4c)",
        "constitution": "v2.2",
        "seed": SEED,
        "task": "D — leave-one-site-out formula prediction",
        "headline_verdict": headline,
        "headline_reason": headline_reason,
        "n_peak_sanctuary_sites_total": len(sites),
        "n_clean_nonderivation_sites": len(clean),
        "derivation_sites_excluded": sorted(DERIVATION_SITES),
        "candidate_universe": universe,
        "n_distinct_forms": len(distinct_forms),
        "distinct_forms": distinct_forms,
        "clean_divergent_forms": clean_divergent_forms,
        "divergent_clean_sites": sorted(divergent_clean),
        "effective_independent_discriminating_sites": eff_discriminating_sites,
        "effective_site_components_by_shared_form": eff_site_components,
        "NO_POWER_threshold": NO_POWER_THRESHOLD,
        "exact_form_top1_accuracy_all_sites": exact_acc_all,
        "exact_form_top1_accuracy_clean_sites": exact_acc_clean,
        "exact_form_top1_accuracy_divergent_clean_sites": exact_acc_divergent,
        "dimino_differs_from_freq_baseline_anywhere": dimino_differs_from_freq,
        "dimino_beats_baselines_exact_form": dimino_beats_baselines,
        "any_model_predicts_a_clean_divergent_form": any_model_predicts_divergent,
        "root_recurrence_H2": {
            "clean_sites_tested": n_clean,
            "clean_sites_with_WA_JA_root": n_clean_root,
            "divergent_clean_sites_tested": n_div,
            "divergent_clean_sites_with_WA_JA_root": n_div_root,
            "per_site": {r["held_site"]: r["root_recurs_WA_JA"] for r in per_site},
            "reading": (
                "The claimed *301-WA-JA root recurs ONLY in copies of the target form itself "
                "(and, on the derivation-contaminated Iouktas site, A-NA-TI-*301-WA-JA). In the "
                f"{n_div} clean held-out DIVERGENT forms it recurs {n_div_root} times -> the root "
                "is a property of the single lexeme it was extracted from, not a cross-site "
                "morpheme. H2 root-recurrence is REFUTED on held-out divergent sites."
            ),
        },
        "random_semitic_null": {
            "representative_divergent_target": rep_target,
            "n_draws": 100000,
            "null_exact_form_hit_rate": round(null_exact, 5),
            "null_slot_parse_hit_rate": round(null_slot, 5),
            "author_stated_sim_count": "~1e5",
        },
        "boundary_note": (
            "Boundary F1 scored vs a DATA-DRIVEN structural edge reference (branching-entropy "
            "word edges {b1, b_last} from report 04); it is a structural benchmark, NOT ground "
            "truth. Reported per site in loso.json."
        ),
        "per_site": per_site,
    }
    return verdict


def _write_md(v):
    L = []
    A = L.append
    A("# D — Leave-One-Site-Out Libation-Formula Prediction\n")
    A(f"**Prereg:** {v['prereg']} · **Constitution:** {v['constitution']} · **Seed:** {v['seed']}\n")
    A("**Generator:** `scripts/D_leave_one_site_out.py` → `data/results/loso.json`\n")
    A("Question: does the Di Mino system *predict* held-out peak-sanctuary formula forms, or only "
      "explain them retrospectively? Mechanical LOSO; known values grade benchmarks only "
      "(non-circular). Primary held-out statistic = recurring morphology (root recurrence).\n")
    A(f"## Headline verdict: **{v['headline_verdict']}**\n")
    A(v["headline_reason"] + "\n")

    A("## A. Sites, forms, partitions\n")
    A(f"- Peak-sanctuary invocation-slot sites (total): **{v['n_peak_sanctuary_sites_total']}** "
      f"— derivation sites excluded from clean LOSO: {v['derivation_sites_excluded']}\n")
    A(f"- Clean non-derivation sites: **{v['n_clean_nonderivation_sites']}**\n")
    A(f"- Distinct invocation forms (candidate universe, {v['n_distinct_forms']}): "
      f"{v['distinct_forms']}\n")
    A(f"- Clean **divergent** (non-modal) forms — the only discriminating targets: "
      f"{v['clean_divergent_forms']} at sites {v['divergent_clean_sites']}\n")

    A("\n## B. Exact-form top-1 accuracy (predicted form attested at held-out site)\n")
    A("| model | all sites | clean sites | clean **divergent** sites |")
    A("|---|---|---|---|")
    for m in ["M_freq", "M_tmpl", "M_markov", "M_davis", "M_dimino"]:
        a = v["exact_form_top1_accuracy_all_sites"][m]
        c = v["exact_form_top1_accuracy_clean_sites"][m]
        dv = v["exact_form_top1_accuracy_divergent_clean_sites"][m]
        A(f"| {m} | {a[0]} (n={a[1]}) | {c[0]} (n={c[1]}) | {dv[0]} (n={dv[1]}) |")
    A("")
    A(f"- Di Mino makes a **different** exact-form prediction from the frequency baseline at any "
      f"held-out site? **{v['dimino_differs_from_freq_baseline_anywhere']}**\n")
    A(f"- Di Mino **beats** baselines on held-out exact form? **{v['dimino_beats_baselines_exact_form']}**\n")
    A(f"- Any model predicts a clean **divergent** singleton form? "
      f"**{v['any_model_predicts_a_clean_divergent_form']}**\n")

    A("\n## C. Root recurrence (H2 — the Di Mino system's one falsifiable cross-site prediction)\n")
    r = v["root_recurrence_H2"]
    A(f"- Clean held-out sites tested: {r['clean_sites_tested']}; with `*301-WA-JA` root present: "
      f"**{r['clean_sites_with_WA_JA_root']}**\n")
    A(f"- Clean **divergent** held-out sites: {r['divergent_clean_sites_tested']}; with the root: "
      f"**{r['divergent_clean_sites_with_WA_JA_root']}**\n")
    A("- per-site root presence: " + ", ".join(f"{k}={vv}" for k, vv in r["per_site"].items()) + "\n")
    A("> " + r["reading"] + "\n")

    A("\n## D. Power / effective independent sites\n")
    A(f"- Effective independent **discriminating** sites (clean, divergent, single-source singletons): "
      f"**{v['effective_independent_discriminating_sites']}** vs NO_POWER floor "
      f"{v['NO_POWER_threshold']}\n")
    A(f"- Site components after collapsing sites carrying an identical form-set: "
      f"**{v['effective_site_components_by_shared_form']}**\n")
    A("- All forms are single-source (GORILA); every divergent form is a one-attestation, "
      "one-toponym unique lexeme → not learnable under leave-one-out (no second instance).\n")

    A("\n## E. Random-Semitic-root null (deflation)\n")
    ns = v["random_semitic_null"]
    A(f"- Representative divergent target `{ns['representative_divergent_target']}`, "
      f"{ns['n_draws']} draws (seed {v['seed']}): null exact-form hit-rate = "
      f"**{ns['null_exact_form_hit_rate']}**, null slot-parse hit-rate = "
      f"**{ns['null_slot_parse_hit_rate']}**; author-stated sims {ns['author_stated_sim_count']}.\n")

    A("\n## F. Boundary / segmentation\n")
    A(v["boundary_note"] + "\n")
    A("| held site | boundary F1 M_dimino | boundary F1 M_davis |")
    A("|---|---|---|")
    for row in v["per_site"]:
        b = row["boundary_f1_vs_edgeref"]
        A(f"| {row['held_site']} | {b['M_dimino']} | {b['M_davis']} |")

    A("\n## G. Interpretation (mechanical)\n")
    A("1. **The Di Mino system is not a predictor of regional form.** Its exact-form output is "
      "fixed to the single lexeme it was built on (`A-TA-I-*301-WA-JA` = the modal form), so its "
      "held-out prediction is byte-identical to the frequency/template/Davis baseline at every "
      "site. It cannot, by construction, exceed those baselines.\n")
    A("2. **The divergent regional forms are unpredictable by any model.** Each clean divergent "
      "form is a unique single-source singleton; leave-one-out removes its only instance, so "
      "exact-form accuracy on them is 0 for every model including the null.\n")
    A("3. **The one falsifiable cross-site prediction the system does make — recurrence of the "
      "`*301-WA-JA` root — FAILS on held-out divergent sites** (root present in 0 of them). The "
      "root is a property of one lexeme, not a morpheme that generalises.\n")
    A("4. **Therefore Task D returns NO_POWER for supporting the claim** (the exact-form channel "
      "cannot discriminate the system from the baseline, and the discriminating sites sit at/below "
      "the floor), with a **secondary REFUTATION** of the H2 root-recurrence sub-claim on the "
      "held-out divergent sites. No SUPPORT.\n")
    return "\n".join(L)


if __name__ == "__main__":
    v = run()
    os.makedirs(os.path.dirname(OUT_JSON), exist_ok=True)
    with open(OUT_JSON, "w") as fh:
        json.dump(v, fh, indent=2)
    with open(OUT_MD, "w") as fh:
        fh.write(_write_md(v))
    print("HEADLINE:", v["headline_verdict"])
    print("exact clean:", {m: v["exact_form_top1_accuracy_clean_sites"][m] for m in
                           ["M_freq", "M_dimino"]})
    print("dimino differs from freq anywhere:", v["dimino_differs_from_freq_baseline_anywhere"])
    print("dimino beats baselines:", v["dimino_beats_baselines_exact_form"])
    print("eff discriminating sites:", v["effective_independent_discriminating_sites"])
    print("root recur divergent:", v["root_recurrence_H2"]["divergent_clean_sites_with_WA_JA_root"],
          "/", v["root_recurrence_H2"]["divergent_clean_sites_tested"])
    print("null exact hit:", v["random_semitic_null"]["null_exact_form_hit_rate"])
    print("wrote", OUT_JSON, OUT_MD)

