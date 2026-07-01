#!/usr/bin/env python3
"""logos family_scores — per-family scorecard (mirrors agora strategy_scores).

Aggregates the mechanical verdicts into `family_scores` (win_rate, held_out_acc, calibration_gap,
dsr, n_trials) via logos_stats, and updates `graduation_state` from the §E gate. verdict.py is the
sole writer of verdicts; THIS is the sole writer of family_scores + graduation_state. Separation
matches agora: the grader writes outcomes, the scorecard rolls them up.

A family graduates (§E) only on the honest primitives: a real held-out GRADUATE win-rate (invariant:
a win is a §E-gate GRADUATE, not the intermediate result=="match") AND enough verdicts to be worth
scoring (MIN_VERDICTS). DSR (§B.3 via logos_stats.deflated_sharpe) is computed and REPORTED as a
diagnostic column but is NOT a graduation clause: deflating held-out accuracies as if they were
financial returns is the invalid domain transfer the manuscript removed from every operative gate
(P0.2). The multiple-testing pool it reports over is every hypothesis tried across all families (the
"English is a Semitic language" failure mode is the enemy, invariant 8).

CLI:
  python3 scripts/family_scores.py            # re-score every family
  python3 scripts/family_scores.py semitic    # re-score one family
"""
import argparse
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts import logos_db, logos_stats  # noqa: E402

DSR_GATE = 0.95            # §E / §B.3 family-level DSR threshold
MIN_VERDICTS = 5           # below this, a family is too thin to graduate (honest cold start)
WIN_RATE_GATE = 0.5        # majority of held-out verdicts must clear the L_fake bar
OUTCOME = {"match": 1.0, "partial": 0.5, "deviation": 0.0}


def _load_family_rows(cur, family=None):
    """Per-family (result, gate_verdict, accuracy, confidence). Mirrors agora's verdict aggregation.

    P0.1: gate_verdict is loaded EXPLICITLY so a family win is defined by the §E gate outcome
    (``gate_verdict == 'GRADUATE'``), never by the intermediate ``result == 'match'`` signal — which
    only means "cleared the local L_fake bar," NOT a validated, gate-passing win. A REJECT/INCOMPLETE
    row therefore contributes 0 to win_rate even when its ``result`` is 'match'."""
    sql = ("SELECT h.family, v.result, v.gate_verdict, v.accuracy, h.confidence "
           "FROM verdicts v JOIN hypotheses h ON h.plan_hash = v.plan_hash "
           "WHERE v.result IN ('match','partial','deviation')")
    args = ()
    if family:
        sql += " AND h.family=%s"
        args = (family,)
    cur.execute(sql, args)
    rows = cur.fetchall()
    by = {}
    for fam, result, gate_verdict, acc, conf in rows:
        by.setdefault(fam, []).append((result, gate_verdict, float(acc or 0.0), float(conf or 0.0)))
    return by


def scorecard(family, rows, n_trials_pool, sr_variance):
    """Pure aggregation of one family's verdict rows -> scorecard dict (no DB)."""
    n = len(rows)
    if n == 0:
        return None
    results = [r[0] for r in rows]
    gate_verdicts = [r[1] for r in rows]
    accuracies = [r[2] for r in rows]
    confs = [r[3] for r in rows]
    outcomes = [OUTCOME.get(r, 0.0) for r in results]

    # P0.1: a family WIN is a §E-gate GRADUATE, never the intermediate result=="match" (which only
    # means the local L_fake bar was cleared). A REJECT/INCOMPLETE with result=="match" contributes 0.
    wins = sum(1 for gv in gate_verdicts if gv == "GRADUATE")
    win_rate = wins / n
    held_out_acc = sum(accuracies) / n
    cal_gap = logos_stats.calibration_in_the_large(confs, outcomes) or 0.0

    # DSR is a REPORTED diagnostic only (P0.2) — computed and stored, but NOT a graduation clause.
    # Applying the Deflated-Sharpe Ratio to held-out accuracies treats them as financial returns, the
    # invalid domain transfer the manuscript removed; the operative family gate is the honest
    # primitives below (GRADUATE win-rate + minimum verdict count).
    sr = logos_stats.sharpe(accuracies)
    dsr = None
    if sr is not None and len(accuracies) >= 2:
        skew, kurt = logos_stats.moments(accuracies)
        dsr = logos_stats.deflated_sharpe(sr, len(accuracies), skew, kurt,
                                          n_trials=max(1, n_trials_pool), sr_variance=sr_variance)

    # §E family graduation gate — honest primitives only (DSR excluded per P0.2).
    clauses = {
        "win_rate_gt_0_5": (win_rate > WIN_RATE_GATE),
        "n_verdicts_ge_min": (n >= MIN_VERDICTS),
    }
    graduated = all(clauses.values())
    failing = [c for c, ok in clauses.items() if not ok]
    reason = ("GRADUATED G2" if graduated
              else f"frozen: {', '.join(failing) or 'unspecified'} (n={n} dsr="
                   f"{'NA' if dsr is None else round(dsr,3)} win={round(win_rate,3)})")
    return {
        "family": family,
        "n_predictions": n,
        "win_rate": round(win_rate, 3),
        "held_out_acc": round(held_out_acc, 4),
        "calibration_gap": round(cal_gap, 4),
        "dsr": None if dsr is None else round(dsr, 4),
        "n_trials": int(n_trials_pool),
        "graduated": graduated,
        "gate": "G2" if graduated else "G0",
        "reason": reason[:255],
    }


def _cross_family_sr_variance(by):
    """Variance of the per-family Sharpe estimates (the DSR's sr_variance input). 0 if <2 families."""
    srs = []
    for fam, rows in by.items():
        acc = [r[1] for r in rows]
        sr = logos_stats.sharpe(acc)
        if sr is not None:
            srs.append(sr)
    if len(srs) < 2:
        return 0.0
    m = sum(srs) / len(srs)
    return sum((s - m) ** 2 for s in srs) / (len(srs) - 1)


def run(family=None, conn=None):
    """Re-score every family (or one) and write family_scores + graduation_state."""
    owns = conn is None
    conn = conn or logos_db.db()
    out = []
    try:
        with conn.cursor() as cur:
            by = _load_family_rows(cur, family)
            # the multiple-testing pool: EVERY hypothesis ever committed (graded or not), all families.
            cur.execute("SELECT COUNT(DISTINCT family) FROM hypotheses")
            n_families = int(cur.fetchone()[0] or 0)
            cur.execute("SELECT COUNT(*) FROM hypotheses")
            n_trials_pool = int(cur.fetchone()[0] or 1)
            sr_variance = _cross_family_sr_variance(by)
            for fam, rows in sorted(by.items()):
                sc = scorecard(fam, rows, n_trials_pool, sr_variance)
                if not sc:
                    continue
                cur.execute(
                    """INSERT INTO family_scores (family, n_predictions, win_rate, held_out_acc,
                                                  calibration_gap, dsr, n_trials)
                       VALUES (%s,%s,%s,%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE n_predictions=VALUES(n_predictions),
                          win_rate=VALUES(win_rate), held_out_acc=VALUES(held_out_acc),
                          calibration_gap=VALUES(calibration_gap), dsr=VALUES(dsr),
                          n_trials=VALUES(n_trials)""",
                    (fam, sc["n_predictions"], sc["win_rate"], sc["held_out_acc"],
                     sc["calibration_gap"], sc["dsr"], sc["n_trials"]))
                cur.execute(
                    """INSERT INTO graduation_state (family, gate, frozen, reason)
                       VALUES (%s,%s,%s,%s)
                       ON DUPLICATE KEY UPDATE gate=VALUES(gate), frozen=VALUES(frozen),
                          reason=VALUES(reason)""",
                    (fam, sc["gate"], 0 if sc["graduated"] else 1, sc["reason"]))
                out.append(sc)
                dsr_s = "NA" if sc["dsr"] is None else f"{sc['dsr']:.3f}"
                state = "GRADUATE" if sc["graduated"] else "frozen"
                print(f"  {fam:16} n={sc['n_predictions']:2} win={sc['win_rate']:.3f} "
                      f"acc={sc['held_out_acc']:.3f} dsr={dsr_s} -> {state}")
    finally:
        if owns:
            conn.close()
    if not out:
        print("no graded families yet (cold start — verdicts land as hypotheses mature).")
    return out


def main():
    ap = argparse.ArgumentParser(description="per-family scorecard + graduation gate (§E)")
    ap.add_argument("family", nargs="?", help="score one family; omit for all")
    args = ap.parse_args()
    run(family=args.family)


if __name__ == "__main__":
    main()
