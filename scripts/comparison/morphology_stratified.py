#!/usr/bin/env python3
"""morphology_stratified.py — Direction-A STRATIFIED morphology re-run (TASK #20).

Executes the two dated pre-registration addenda (both 2026-06-30):
  - prereg-morphology-stratification-addendum: induce the FROZEN pre-registered affix panel PER GENRE
    STRATUM (admin / libation / other), test CROSS-STRATUM STABILITY of every candidate affix, EXCLUDE
    the abbreviation channel (seal-type supports + short list-headers), DEFLATE effective-n for
    within-SITE non-independence (hands are unavailable for Linear A — TASK #19), and DECLINE
    chronological CV (the corpus is ~74% single-horizon LM IB; `context` field).
  - prereg-morphology-salgarella-addendum H7: the benchmark typology is agglutinative + VSO.

WHY stratify: the pooled run (morphology.py) reported a null, but the within-form permutation null
PRESERVES the pooling, so it cannot catch a "morphology" that is really a mix of registers. An affix
that confirms in ONLY ONE genre stratum is a REGISTER feature, not validated language morphology; only
an affix that is CROSS-STRATUM STABLE (confirms in >=2 strata) AND SITE-ROBUST (borne across >=2
distinct sites, the within-site-independence control) may be called morphology.

Grades from the persisted artifact (runtime/morphology-stratified.json), never from narration. Reuses
morphology.null_falsification per stratum. NO phonetic claim; imports no verdict.
"""
from __future__ import annotations

import argparse
import json
import os
from collections import Counter, defaultdict
from typing import Dict, List, Optional, Sequence, Set, Tuple

from . import morphology  # type: ignore
from .morphology import (Inscription, PREREG_AFFIXES, Affix, affix_residual, null_falsification,
                         run_affix_panel, build_lfake_corpus, SignCodec)

_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_SILVER = os.path.join(_ROOT, "corpus", "silver", "inscriptions_structured.json")

# --------------------------------------------------------------------------- #
# Genre stratification from the GORILA `support` field (Salgarella 2025 §6).
#   SEAL supports = the abbreviation channel (single-/short-sign administrative markings) — EXCLUDED.
#   LIBATION = stone vessels bearing the libation formula (the cultic/votive register).
#   ADMIN    = tablets + bars/lames: the multi-sign accounting words.
#   OTHER    = clay vessels, metal votives, architecture, graffiti, ... (heterogeneous).
# --------------------------------------------------------------------------- #
SEAL_SUPPORTS = {"Nodule", "Roundel", "Sealing", "Label"}
LIBATION_SUPPORTS = {"Stone vessel", "Stone object", "Inked inscription"}
ADMIN_SUPPORTS = {"Tablet", "Lames (short thin tablet)", "3-sided bar", "4-sided bar"}
INDUCTION_STRATA = ("admin", "libation", "other")    # seal is excluded from induction


def genre_of(support: str) -> str:
    s = (support or "").strip()
    if s in SEAL_SUPPORTS:
        return "seal"
    if s in LIBATION_SUPPORTS:
        return "libation"
    if s in ADMIN_SUPPORTS:
        return "admin"
    return "other"


def load_stratified(path: str = DEFAULT_SILVER) -> List[Tuple[Inscription, str, str, str]]:
    """[(Inscription, support, genre, period), ...] — carries the support/context the core loader drops."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out: List[Tuple[Inscription, str, str, str]] = []
    for d in data:
        words = [[str(s) for s in w] for w in d.get("words", []) if w]
        if not words:
            continue
        ins = Inscription(iid=str(d.get("id", "")), site=str(d.get("site", "")), words=words)
        support = str(d.get("support", ""))
        out.append((ins, support, genre_of(support), str(d.get("context", ""))))
    return out


# --------------------------------------------------------------------------- #
# Abbreviation channel (field intel 2026-06-30): short list-headers + seal-signs masquerade as affix
# variants. Seal-support inscriptions are dropped wholesale; the leading <=max_len-sign word of an
# admin/other/libation inscription (the list-header) is dropped. Everything dropped is REPORTED.
# --------------------------------------------------------------------------- #
def strip_abbreviation(ins: Inscription, genre: str, max_len: int = 3) -> Tuple[Optional[Inscription], int]:
    """Seal inscriptions are dropped wholesale. For ADMIN tablets only, the leading <=max_len-sign word
    (the list-header) is dropped — libation/votive first words are dedicatory text, NOT list-headers, so
    they are kept. Everything dropped is reported by the caller."""
    if genre == "seal":
        return None, len(ins.words)                       # whole seal inscription excluded
    words = list(ins.words)
    removed = 0
    if genre == "admin" and words and len(words[0]) <= max_len:   # admin list-header only
        words = words[1:]
        removed = 1
    if not words:
        return None, removed
    return Inscription(ins.iid, ins.site, words), removed


def build_strata(recs: Sequence[Tuple[Inscription, str, str, str]],
                 exclude_abbrev: bool = True) -> Tuple[Dict[str, List[Inscription]], Dict[str, object]]:
    strata: Dict[str, List[Inscription]] = {k: [] for k in INDUCTION_STRATA}
    stats = {"seal_inscriptions_excluded": 0, "seal_words_excluded": 0,
             "heading_words_excluded": 0, "inscriptions_emptied_by_strip": 0,
             "period_distribution": dict(Counter(p or "(none)" for _, _, _, p in recs))}
    for ins, _support, genre, _period in recs:
        if genre == "seal":
            stats["seal_inscriptions_excluded"] += 1
            stats["seal_words_excluded"] += len(ins.words)
            continue
        if exclude_abbrev:
            stripped, removed = strip_abbreviation(ins, genre)
            stats["heading_words_excluded"] += removed
            if stripped is None:
                stats["inscriptions_emptied_by_strip"] += 1
                continue
            strata[genre].append(stripped)
        else:
            strata[genre].append(ins)
    return strata, stats


# --------------------------------------------------------------------------- #
# Within-SITE non-independence control (#19/#20): hands are unavailable for Linear A, so the strongest
# available independence unit is the SITE. An affix borne by 10 inscriptions all at Haghia Triada is ~1
# independent site-sample, not 10. site_robust requires recurrence across >=2 distinct sites.
# --------------------------------------------------------------------------- #
def sites_bearing(corpus: Sequence[Inscription], affix: Affix) -> Set[str]:
    sites: Set[str] = set()
    for ins in corpus:
        for w in ins.words:
            if affix_residual(w, affix) is not None:
                sites.add(ins.site)
                break
    return sites


def lfake_confirmed_affixes(corpus: Sequence[Inscription], codec: SignCodec, *,
                            n_null: int = 200, seed: int = 0, n_lfake: int = 3) -> Set[str]:
    """The PER-AFFIX bigram floor: the set of affixes that confirm in ANY of n_lfake fabricated
    (markov, sign-bigram-calibrated) corpora. Conservative (union) -> an affix the bigram model can
    manufacture is excluded from 'morphology'. This is the affix-level analogue of the pooled finding's
    L_fake floor, which null_falsification only reports in aggregate (rate), not per-affix."""
    confirmed: Set[str] = set()
    for i in range(max(1, n_lfake)):
        lf = build_lfake_corpus(corpus, codec, seed=seed + 29 + i)
        if not lf:
            continue
        r = run_affix_panel(lf, codec, n_null=n_null, seed=seed + 29 + i)
        confirmed.update(r["confirmed_affixes"])
    return confirmed


def cross_stratum_stability(per_stratum: Dict[str, Dict[str, object]],
                            strata: Dict[str, List[Inscription]],
                            affixes: Sequence[Affix] = PREREG_AFFIXES,
                            min_sites: int = 2) -> Dict[str, object]:
    """Which CONFIRMED affixes are cross-stratum stable (>=2 strata) AND site-robust (>=2 sites)."""
    by_label = {a.affix: a for a in affixes}
    confirmed_in: Dict[str, List[str]] = defaultdict(list)
    site_robust_in: Dict[str, List[str]] = defaultdict(list)
    for name in INDUCTION_STRATA:
        r = per_stratum.get(name, {})
        # credit only affixes that PASS THE PER-AFFIX L_fake bigram floor (confirm on real, NOT on L_fake)
        for label in (r.get("morphology_affixes") or []):
            confirmed_in[label].append(name)
            ns = len(sites_bearing(strata.get(name, []), by_label[label])) if label in by_label else 0
            if ns >= min_sites:
                site_robust_in[label].append(name)
    cross_stable = {a: sorted(s) for a, s in confirmed_in.items() if len(s) >= 2}
    register_features = {a: s[0] for a, s in confirmed_in.items() if len(s) == 1}
    # a candidate is validated MORPHOLOGY only if it is cross-stratum stable AND site-robust in >=2 strata
    morphology_validated = {a: sorted(site_robust_in[a]) for a in cross_stable
                            if len(site_robust_in.get(a, [])) >= 2}
    return {
        "confirmed_in": {a: sorted(s) for a, s in confirmed_in.items()},
        "site_robust_in": {a: sorted(s) for a, s in site_robust_in.items()},
        "cross_stratum_stable": cross_stable,
        "single_stratum_register_features": register_features,
        "morphology_validated": morphology_validated,
    }


def run_stratified(path: str = DEFAULT_SILVER, *, n_null: int = 200, seed: int = 0,
                   exclude_abbrev: bool = True, min_inscriptions: int = 12) -> Dict[str, object]:
    """The full stratified panel + cross-stratum/site stability + the honest grade (from the artifact)."""
    recs = load_stratified(path)
    strata, abbrev_stats = build_strata(recs, exclude_abbrev=exclude_abbrev)

    per_stratum: Dict[str, Dict[str, object]] = {}
    for name in INDUCTION_STRATA:
        corpus = strata[name]
        n_words = sum(len(ins.words) for ins in corpus)
        n_sites = len({ins.site for ins in corpus})
        if len(corpus) < min_inscriptions:
            per_stratum[name] = {"n_inscriptions": len(corpus), "n_words": n_words, "n_sites": n_sites,
                                 "no_power": True, "real_confirmed_affixes": [], "morphology_affixes": [],
                                 "reason": f"stratum too thin (<{min_inscriptions} inscriptions) -> NO POWER"}
            continue
        codec = SignCodec.from_corpus(corpus)
        nf = null_falsification(corpus, codec=codec, n_null=n_null, seed=seed)
        # PER-AFFIX bigram floor: an affix is morphology only if it confirms on real but NOT on L_fake.
        lfake_aff = sorted(lfake_confirmed_affixes(corpus, codec, n_null=n_null, seed=seed))
        real_aff = list(nf.get("real_confirmed_affixes") or [])
        morphology_aff = [a for a in real_aff if a not in set(lfake_aff)]
        nf.update({"n_inscriptions": len(corpus), "n_words": n_words, "n_sites": n_sites,
                   "lfake_confirmed_affixes": lfake_aff, "morphology_affixes": morphology_aff})
        per_stratum[name] = nf

    cross = cross_stratum_stability(per_stratum, strata)

    # HEADLINE grade (mechanical, from the per-stratum artifacts): validated morphology requires an affix
    # that confirms in >=2 strata AND is site-robust (>=2 sites) in >=2 strata. Expected: NULL.
    has_validated = bool(cross["morphology_validated"])
    if has_validated:
        verdict = (f"VALIDATED cross-stratum morphology: {sorted(cross['morphology_validated'])} confirm "
                   f"in >=2 genre strata AND are site-robust. " + morphology.NO_PHONETIC_CLAIM)
    elif cross["cross_stratum_stable"]:
        verdict = (f"Cross-stratum-stable affixes {sorted(cross['cross_stratum_stable'])} exist but are "
                   f"NOT site-robust across strata (within-site non-independence not cleared) -> NO "
                   f"validated morphology; report the null.")
    elif cross["single_stratum_register_features"]:
        verdict = (f"Affixes confirm in only ONE stratum each "
                   f"({cross['single_stratum_register_features']}) -> REGISTER features, not validated "
                   f"language morphology; report the null.")
    else:
        verdict = ("No pre-registered affix confirms above its L_fake floor in any genre stratum -> the "
                   "pooled null holds under stratification; report the null. DO NOT claim morphology.")

    return {
        "task": "#20 stratified morphology re-run",
        "exclude_abbrev": exclude_abbrev,
        "n_inscriptions_total": len(recs),
        "abbreviation_channel": abbrev_stats,
        "strata_sizes": {n: {"n_inscriptions": len(strata[n]),
                             "n_words": sum(len(i.words) for i in strata[n]),
                             "n_sites": len({i.site for i in strata[n]})} for n in INDUCTION_STRATA},
        "per_stratum": per_stratum,
        "cross_stratum": cross,
        "has_validated_morphology": has_validated,
        "verdict": verdict,
        "chronological_cv": "DECLINED — corpus is ~74% single-horizon LM IB (see abbreviation_channel."
                            "period_distribution); per the stratification addendum, site-held-out only.",
    }


def main(argv: Optional[Sequence[str]] = None) -> int:
    p = argparse.ArgumentParser(description="Direction-A stratified morphology re-run (#20)")
    p.add_argument("--corpus", default=DEFAULT_SILVER)
    p.add_argument("--n-null", type=int, default=200)
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--no-exclude-abbrev", action="store_true", help="sensitivity: keep the abbreviation channel")
    p.add_argument("--json", default=None, help="write the full result JSON here")
    args = p.parse_args(list(argv) if argv is not None else None)

    res = run_stratified(args.corpus, n_null=args.n_null, seed=args.seed,
                         exclude_abbrev=not args.no_exclude_abbrev)
    print("== Direction-A stratified morphology (#20) ==")
    ab = res["abbreviation_channel"]
    print(f"abbreviation channel excluded: {ab['seal_inscriptions_excluded']} seal inscriptions "
          f"({ab['seal_words_excluded']} words) + {ab['heading_words_excluded']} list-headers")
    for n in INDUCTION_STRATA:
        s = res["strata_sizes"][n]
        r = res["per_stratum"][n]
        tag = ("NO POWER" if r.get("no_power") else
               f"real {r.get('real_confirm_rate', 0):.3f} vs L_fake {r.get('lfake_confirm_rate', 0):.3f}; "
               f"real-confirm {r.get('real_confirmed_affixes', [])}; "
               f"L_fake also-confirms {r.get('lfake_confirmed_affixes', [])}; "
               f"PASS-floor {r.get('morphology_affixes', [])}")
        print(f"  [{n:8s}] {s['n_inscriptions']:4d} insc / {s['n_words']:5d} words / {s['n_sites']:2d} sites  {tag}")
    print(f"cross-stratum stable: {res['cross_stratum']['cross_stratum_stable']}")
    print(f"register features:    {res['cross_stratum']['single_stratum_register_features']}")
    print(f"VALIDATED morphology: {res['has_validated_morphology']}")
    print(f"VERDICT: {res['verdict']}")
    if args.json:
        os.makedirs(os.path.dirname(os.path.abspath(args.json)), exist_ok=True)
        with open(args.json, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2, ensure_ascii=False)
        print(f"wrote {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
