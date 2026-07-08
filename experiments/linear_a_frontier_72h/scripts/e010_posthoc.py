#!/usr/bin/env python3
"""EPOCH-010 POST-HOC (declared, descriptive, NON-claim-bearing).

Characterizes the single closure-blocking quantity from the frozen run: the CAP_ORACLE_PICK3
union ceiling at the LA operating point (KNOWN, b=5, f=0.75), whose median margin over the
mechanical required rate was exactly 0.000. Recomputes the identical deterministic replicates
(same RNG streams as e010_channel_capacity.py) and reports per-replicate margins, the
rep-level exceed fraction, per-expert unique contributions, and whether union hits concentrate
on particular signs. No new endpoints, no verdict change. Seed 20260708.
"""
from __future__ import annotations
import json, os, sys
from collections import Counter

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import e003_seed_poverty as E3
import e010_channel_capacity as E10

OUT = os.path.join(E10.OUTDIR, "E010_posthoc.json")


def run():
    probs = E10.build_problems()
    out = {}
    for f in (0.75, 1.0):
        rows, hit_signs = [], Counter()
        uniq = Counter()
        for d, rep in E10.draw_reps_for(f):
            prob = probs[("KNOWN", f, d)]
            srng, _ = E3.rng_for("KNOWN", "seeds", f, d, E10.B, rep)
            seed_idx, anchor = E10.uniform_anchor(prob, srng)
            held = [i for i in range(len(prob["s_signs"])) if i not in set(seed_idx)]
            truths = [prob["gt_idx"][i] for i in held]
            costs = E10.base_cost_matrices(prob, anchor)
            per = [[int(np.argmin(c[i])) for i in held] for c in costs]
            names = ["M1", "EST_GW", "EST_OT"]
            ok = {m: [per[k][hi] == truths[hi] for hi in range(len(held))]
                  for k, m in enumerate(names)}
            union = [any(ok[m][hi] for m in names) for hi in range(len(held))]
            for hi in range(len(held)):
                if union[hi]:
                    hit_signs[prob["s_signs"][held[hi]]] += 1
                    contributors = [m for m in names if ok[m][hi]]
                    if len(contributors) == 1:
                        uniq[contributors[0]] += 1
            # required count, identical stream to the frozen run
            accs = [float(np.mean(ok[m])) for m in names]
            best = int(np.argmax(accs))
            _, nrng = E3.rng_for("cap_null", "CAP_ORACLE_PICK3", f, d, rep)
            _, _, c_req = E10.exact_p_full(per[best], truths, nrng)
            H = len(held)
            rows.append({"d": d, "rep": rep, "H": H, "c_req": c_req,
                         "union_count": int(np.sum(union)),
                         "union_acc": float(np.mean(union)),
                         "required": c_req / H,
                         "margin": float(np.mean(union)) - c_req / H,
                         "per_expert_acc": dict(zip(names, accs)),
                         "best_single_acc": max(accs)})
        margins = [r["margin"] for r in rows]
        out[str(f)] = {
            "reps": rows,
            "margin_median": float(np.median(margins)),
            "margin_mean": float(np.mean(margins)),
            "frac_reps_margin_gt0": float(np.mean([m > 0 for m in margins])),
            "frac_reps_margin_ge0": float(np.mean([m >= 0 for m in margins])),
            "frac_reps_union_ge_creq": float(np.mean([r["union_count"] >= r["c_req"]
                                                      for r in rows])),
            "mean_union_minus_best_single": float(np.mean([r["union_acc"] -
                                                           r["best_single_acc"]
                                                           for r in rows])),
            "unique_contributions": dict(uniq),
            "top_union_hit_signs": hit_signs.most_common(12),
            "n_distinct_hit_signs": len(hit_signs)}
        print(f"f={f}: margin med {out[str(f)]['margin_median']:+.4f} "
              f"mean {out[str(f)]['margin_mean']:+.4f} "
              f"reps>0 {out[str(f)]['frac_reps_margin_gt0']:.2f} "
              f"reps>=0 {out[str(f)]['frac_reps_margin_ge0']:.2f} "
              f"union-best {out[str(f)]['mean_union_minus_best_single']:+.3f} "
              f"uniq {dict(uniq)} distinct_signs {len(hit_signs)}")
        print("  top hit signs:", hit_signs.most_common(8))
    json.dump(out, open(OUT, "w"), indent=1, default=float)
    print("wrote", OUT)
    return out


if __name__ == "__main__":
    run()
