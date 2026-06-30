#!/usr/bin/env python3
"""run_canary.py — the L_fake canary SELF-VALIDATION (logos comparison-layer §C.3 + F.2).

This is the proof the canary works, run on a REAL cognate pair (Ugaritic <-> Hebrew) so the
statistic is exercised on a known truth before it is ever pointed at Linear A.

  CALIBRATION  — L_fake is calibrated to the HEBREW side of corpus/bronze/ugaritic/uga-heb.gold.cog
                 (Hebrew phoneme frequencies + trilateral root-template structure + lexicon size).
  POSITIVE     — real Ugaritic->Hebrew cognate pairs SHOULD produce non-trivial S_lex (a real
                 correspondence registers). Ugaritic is the "held-out inscription" set; the Hebrew
                 lexicon is the candidate.
  NEGATIVE     — L_fake (invented, no real correspondence with Ugaritic) MUST score at the
                 false-positive FLOOR. Many L_fake instances give the floor DISTRIBUTION; a real
                 candidate must clear it by the corrected margin or the match is spurious.

Headline diagnostic (refinement F.2): because L_fake is structurally matched to Hebrew, an elevated
S_lex(Ugaritic, L_fake) would mean the statistic is reading CONSONANT SIMILARITY (search
attractiveness), not cognacy — i.e. the layer has NO POWER and the null is published. If
S_lex(Ugaritic, Hebrew) >> S_lex(Ugaritic, L_fake), the statistic carries real cognate signal above
the structural floor, and the canary is fit for purpose.

Honesty notes (Nair 2026, arXiv:2604.17828): the calibration divergence is PUBLISHED, never hidden;
L_fake is a FLOOR, never ground truth; and even a 'pass' on a real candidate is an Etruscan-grade
result (sound-value imputations, uncertainty-quantified) — explicitly NOT a meaning decipherment.

    python3 scripts/comparison/run_canary.py
    python3 scripts/comparison/run_canary.py --n-fake 32 --eps 0.20 --json
"""
from __future__ import annotations

import json
import os
import sys
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np

# make `scripts.comparison` importable when run as a plain script (cron-style)
_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.dirname(os.path.dirname(_HERE))
if _ROOT not in sys.path:
    sys.path.insert(0, _ROOT)

from scripts.comparison import lfake, nulls, lexstat  # noqa: E402

GOLD_COG = os.path.abspath(os.path.join(
    _HERE, "..", "..", "corpus", "bronze", "ugaritic", "uga-heb.gold.cog"))


# --------------------------------------------------------------------------- #
# Data loading
# --------------------------------------------------------------------------- #
def load_gold(path: str = GOLD_COG) -> Tuple[List[str], List[str], List[Tuple[str, str]]]:
    """Return (ugaritic_forms, hebrew_forms_flat, paired) from a uga-heb gold cognate file.

    Hebrew cells may carry several pipe-separated cognates; each is flattened into the lexicon.
    """
    uga: List[str] = []
    heb: List[str] = []
    pairs: List[Tuple[str, str]] = []
    with open(path, encoding="utf-8") as f:
        for i, line in enumerate(f):
            line = line.rstrip("\n")
            if i == 0 or not line.strip():
                continue
            parts = line.split("\t")
            if len(parts) < 2:
                continue
            u = parts[0].strip()
            if not u:
                continue
            uga.append(u)
            hebs = [h.strip() for h in parts[1].split("|") if h.strip()]
            heb.extend(hebs)
            for h in hebs:
                pairs.append((u, h))
    return uga, heb, pairs


# --------------------------------------------------------------------------- #
# The self-validation
# --------------------------------------------------------------------------- #
def run(n_fake: int = 16, eps_grid: Sequence[float] = (0.20, 0.25, 0.30),
        base_seed: int = 0, gold_path: str = GOLD_COG,
        heldout_frac: float = 0.5, max_heldout: int = 800) -> dict:
    """Run the canary self-validation and return a structured report dict.

    ``max_heldout`` caps the held-out Ugaritic set via a DETERMINISTIC subsample (seeded). S_lex is
    a proportion; on 800 forms the recall stderr is ~0.012, ample for a floor comparison. The full
    set is used when it is already smaller than the cap. The expensive reference baselines
    (null distribution + Monte-Carlo chance) are run only at the *primary* epsilon (middle of the
    grid); the headline pair (positive vs L_fake distribution) is computed at every epsilon.
    """
    uga, heb, pairs = load_gold(gold_path)
    heb_unique = sorted(set(heb))
    uga_unique = sorted(set(uga))

    # deterministic held-out subsample (keeps the comparison fair and the run tractable)
    rng0 = np.random.default_rng(base_seed)
    if len(uga_unique) > max_heldout:
        sel = sorted(int(i) for i in rng0.choice(len(uga_unique),
                                                 size=max_heldout, replace=False))
        uga_eval = [uga_unique[i] for i in sel]
        report_note = (f"held-out Ugaritic set subsampled to {max_heldout} of {len(uga_unique)} "
                       f"deterministically (seed={base_seed}); S_lex is a proportion so the recall "
                       f"estimate is unbiased, stderr ~0.012.")
    else:
        uga_eval = list(uga_unique)
        report_note = "full held-out Ugaritic set used."

    # --- 1. CALIBRATE L_fake to Hebrew (F.2: freq + root-template + lexicon size) ---
    cfg = lfake.calibrate_to(heb_unique, mode="semitic", root_len=3)
    cal_div = lfake.aggregate_divergence(heb_unique, cfg, n_instances=n_fake,
                                         base_seed=base_seed)["aggregate"]

    report: Dict[str, object] = {
        "citation": [lfake.CITATION_NAIR, lfake.CITATION_DESIGN,
                     nulls.CITATION_PACKARD, nulls.CITATION_NAIR, lexstat.CITATION_DESIGN],
        "gold_file": os.path.basename(gold_path),
        "calibration": {
            "candidate": "Hebrew (from uga-heb.gold.cog)",
            "mode": cfg.mode,
            "phoneme_inventory_size": len(cfg.inventory),
            "lexicon_size_target": cfg.lexicon_size,
            "root_len": cfg.root_len,
            "n_ugaritic_forms": len(uga_unique),
            "n_hebrew_forms": len(heb_unique),
        },
        "calibration_divergence": cal_div,
        "heldout_note": report_note,
        "ceiling_statement": (
            "Even a 'pass' of a real candidate against this canary is an Etruscan-grade result: "
            "sound-value imputations with quantified uncertainty, NOT a meaning decipherment. "
            "L_fake is a false-positive FLOOR, never ground truth."
        ),
    }

    # --- 2. generate the L_fake instances (the false-positive floor) ---
    fake_lexicons: List[List[str]] = []
    for i in range(n_fake):
        g = lfake.LFakeGenerator(cfg, seed=base_seed + i)
        g.generate_lexicon()
        fake_lexicons.append(g.generated)

    # held-out split (computed once; small sets so cheap at every eps)
    rng = np.random.default_rng(base_seed)
    idx = np.arange(len(pairs))
    rng.shuffle(idx)
    cut = int(len(idx) * heldout_frac)
    derive_idx = set(idx[:cut].tolist())
    heldout_idx = set(idx[cut:].tolist())
    derive_heb = sorted({pairs[k][1] for k in derive_idx})
    heldout_uga = sorted({pairs[k][0] for k in heldout_idx})

    # precompute the Hebrew length distribution for the chance baseline
    len_dist = {L: c / max(sum(lfake.length_distribution(heb_unique).values()), 1)
                for L, c in lfake.length_distribution(heb_unique).items()}

    primary_pos = len(eps_grid) // 2
    primary_eps = eps_grid[primary_pos]

    # --- 3. score across the epsilon grid ---
    eps_results: List[dict] = []
    for ei, eps in enumerate(eps_grid):
        # POSITIVE: real cognates (Ugaritic held-out inscription set vs the Hebrew lexicon)
        pos_recall = lexstat.s_lex(uga_eval, heb_unique, eps)

        # NEGATIVE / CANARY: same Ugaritic forms vs each L_fake instance
        fake_recalls = np.array([lexstat.s_lex(uga_eval, fk, eps) for fk in fake_lexicons])

        heldout_recall = (lexstat.s_lex(heldout_uga, derive_heb, eps)
                          if heldout_uga and derive_heb else None)

        row = {
            "eps": eps,
            "positive_s_lex_real_cognates": pos_recall,
            "heldout_split_s_lex": heldout_recall,
            "lfake_distribution": {
                "mean": float(fake_recalls.mean()),
                "std": float(fake_recalls.std()),
                "p5": float(np.percentile(fake_recalls, 5)),
                "p50": float(np.percentile(fake_recalls, 50)),
                "p95": float(np.percentile(fake_recalls, 95)),
                "p99": float(np.percentile(fake_recalls, 99)),
                "min": float(fake_recalls.min()),
                "max": float(fake_recalls.max()),
                "n_instances": int(len(fake_recalls)),
            },
            "margin_over_lfake_mean": pos_recall - float(fake_recalls.mean()),
            "power_ratio_positive_over_lfake": pos_recall / max(fake_recalls.mean(), 1e-9),
        }

        # expensive reference baselines only at the primary epsilon
        if ei == primary_pos:
            chance = lexstat.expected_chance_recall(
                uga_eval, cfg.inventory, eps=eps, n_mc=30, seed=base_seed, length_dist=len_dist)

            def _stat(h, L, _e=eps):
                return lexstat.s_lex(h, L, _e)
            null_scores = nulls.null_distribution(
                _stat, uga_eval, heb_unique, seed=base_seed,
                n_packard=8, n_random=8, n_within=8)
            null_all = np.concatenate([null_scores["packard"], null_scores["random_lexeme"],
                                       null_scores["within_form"]])
            row.update({
                "independent_chance_baseline": chance,
                "null_mean_positive": float(null_all.mean()),
                "null_breakdown": {k: {"mean": float(np.mean(v)), "std": float(np.std(v))}
                                   for k, v in null_scores.items()},
                "deflated_positive_s_lex": max(0.0, pos_recall - float(null_all.mean())),
            })

        fake_p95 = row["lfake_distribution"]["p95"]
        clears_p95 = pos_recall > fake_p95
        no_power = bool(pos_recall <= fake_p95)        # F.2: within the L_fake band => no power
        row["clears_lfake_p95"] = bool(clears_p95)
        row["no_power_diagnostic"] = no_power
        row["verdict"] = ("NO_POWER_REPORT_NULL" if no_power
                          else ("CANARY_HOLDS_REAL_CLEARS_FLOOR" if clears_p95 else "AMBIGUOUS"))
        eps_results.append(row)

    report["epsilon_grid"] = eps_results
    report["primary_eps"] = primary_eps

    # headline (at the primary eps, the middle of the grid)
    primary = eps_results[primary_pos]
    report["headline"] = {
        "eps": primary["eps"],
        "real_cognate_s_lex": primary["positive_s_lex_real_cognates"],
        "lfake_floor_mean": primary["lfake_distribution"]["mean"],
        "lfake_floor_p95": primary["lfake_distribution"]["p95"],
        "verdict": primary["verdict"],
        "interpretation": (
            "L_fake (fabricated, no real Ugaritic correspondence) sits at the false-positive "
            "floor; real Ugaritic<->Hebrew cognates clear it. The canary catches spurious matches."
            if primary["verdict"] == "CANARY_HOLDS_REAL_CLEARS_FLOOR" else
            "Real cognate recall is within the L_fake band -> the statistic is reading consonant "
            "similarity, not cognacy (no power); publish the null."
        ),
    }
    return report


# --------------------------------------------------------------------------- #
# Pretty printer
# --------------------------------------------------------------------------- #
def _fmt(report: dict) -> str:
    lines: List[str] = []
    lines.append("=" * 78)
    lines.append("L_fake CANARY SELF-VALIDATION  (logos comparison-layer §C.3 + F.2; Nair 2026)")
    lines.append("=" * 78)
    c = report["calibration"]
    lines.append(f"candidate calibration : {c['candidate']}")
    lines.append(f"  mode={c['mode']}  inventory={c['phoneme_inventory_size']} chars  "
                 f"lexicon_size_target={c['lexicon_size_target']}  root_len={c['root_len']}")
    lines.append(f"  Ugaritic forms={c['n_ugaritic_forms']}  Hebrew forms={c['n_hebrew_forms']}")
    lines.append("")
    lines.append("CALIBRATION DIVERGENCE (generator output vs Hebrew targets; reported, NOT ground truth):")
    for k, v in report["calibration_divergence"].items():
        lines.append(f"  {k:<24} mean={v['mean']:.4f}  std={v['std']:.4f}")
    lines.append("")
    for r in report["epsilon_grid"]:
        d = r["lfake_distribution"]
        lines.append(f"eps={r['eps']:.2f}  "
                     f"REAL cognates S_lex={r['positive_s_lex_real_cognates']:.3f}  "
                     f"(held-out split={r['heldout_split_s_lex']:.3f})")
        lines.append(f"         L_fake floor: mean={d['mean']:.3f} std={d['std']:.3f}  "
                     f"[p5 {d['p5']:.3f}, p50 {d['p50']:.3f}, p95 {d['p95']:.3f}, p99 {d['p99']:.3f}]  "
                     f"(n={d['n_instances']})")
        ref = []
        if "independent_chance_baseline" in r:
            ref.append(f"chance={r['independent_chance_baseline']:.3f}")
        if "null_mean_positive" in r:
            ref.append(f"null_mean={r['null_mean_positive']:.3f}")
            ref.append(f"deflated_pos={r['deflated_positive_s_lex']:.3f}")
        lines.append("         " + ("  ".join(ref) if ref else "(reference baselines at primary eps only)"))
        lines.append(f"         margin_over_lfake={r['margin_over_lfake_mean']:+.3f}  "
                     f"power_ratio={r['power_ratio_positive_over_lfake']:.2f}x  "
                     f"clears_p95={r['clears_lfake_p95']}  -> {r['verdict']}")
        lines.append("")
    h = report["headline"]
    lines.append("-" * 78)
    lines.append(f"HEADLINE @ eps={h['eps']:.2f}: real={h['real_cognate_s_lex']:.3f}  "
                 f"L_fake floor mean={h['lfake_floor_mean']:.3f} (p95 {h['lfake_floor_p95']:.3f})")
    lines.append(f"VERDICT: {h['verdict']}")
    lines.append(f"  {h['interpretation']}")
    lines.append("")
    lines.append("CEILING: " + report["ceiling_statement"])
    return "\n".join(lines)


def main(argv: Optional[Sequence[str]] = None) -> int:
    import argparse
    p = argparse.ArgumentParser(description="L_fake canary self-validation")
    p.add_argument("--n-fake", type=int, default=16, help="number of L_fake instances")
    p.add_argument("--eps", nargs="+", type=float, default=[0.15, 0.20, 0.25, 0.30])
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--gold", default=GOLD_COG)
    p.add_argument("--json", action="store_true")
    args = p.parse_args(argv)
    report = run(n_fake=args.n_fake, eps_grid=tuple(args.eps), base_seed=args.seed,
                 gold_path=args.gold)
    if args.json:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(_fmt(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
