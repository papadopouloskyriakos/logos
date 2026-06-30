#!/usr/bin/env python3
"""logos verdict — the SOLE writer of `verdicts` (invariant 2/3).

For every committed hypothesis whose held-out implication is registered but ungraded, this job
mechanically grades it against the held-out corpus and writes the verdict. The LLM is NOWHERE on
the verdict path (design §C.5) — it proposes hypotheses; it never grades them.

Grading (docs/design/comparison-layer.md §A/§B/§E):
  * primary statistic is deflated S_lex (lexstat.s_lex — the Gordon failure mode hammered head-on;
    maintainer refinement F.1 makes S_lex the pragmatic primary because Linear A is short &
    formulaic, so S_morph may have no power regardless of truth).
  * the L_fake fabricated-language canary (scripts/comparison/lfake) is the HEADLINE falsifier
    (F.1): a candidate passes only if its held-out score beats the L_fake score distribution by
    the corrected margin. L_fake cannot be regurgitated, so any signal it shows is spurious.
  * DSR (logos_stats.deflated_sharpe) is the SECONDARY, mechanical-search-scoped statistic — it
    deflates against the instrumented N_eff (the exact trial count the retrieval logged). The L_fake
    canary is the N_eff-INDEPENDENT backstop for the human/LLM mental search (garden of forking paths).

§E acceptance gate — a hypothesis is EVIDENCE only if ALL hold:
  registered before test; DSR>=0.95; free_params k<=U_floor; beats L_fake margin;
  generalizes to L_virgin signs; not (llm_proposed AND lit_index_hit); survives LLM ablation.
  Fail any -> result != match, gate verdict REJECT / NULL_PUBLISHED. Never GRADUATE on internal fit.

CLI:
  python3 scripts/verdict.py                 # grade all due hypotheses
  python3 scripts/verdict.py <plan_hash>     # grade one (re-grade: deletes prior verdict first)
"""
import argparse
import datetime
import hashlib
import json
import os
import sys

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts import logos_db, logos_stats  # noqa: E402
from scripts.comparison import lexstat, lfake, run_canary  # noqa: E402

METRIC_VERSION = "verdict-v1"          # bump when grade semantics / gate clauses change
DSR_GATE = 0.95                        # §E DSR threshold
N_FAKE_DEFAULT = 16                    # L_fake canary instances for the headline null distribution
EPS_DEFAULT = 0.25                     # normalized-edit-distance epsilon for S_lex


def code_sha():
    """SHA-8 of this file's source — stamped into verdicts.provenance (audit trail, agora pattern)."""
    with open(__file__, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()[:12]


# --------------------------------------------------------------------------- #
# The L_fake headline null (design §B.1/§C.3, maintainer refinement F.1/F.2)
# --------------------------------------------------------------------------- #
def lfake_distribution(heldout_forms, candidate_lexicon, n_fake=N_FAKE_DEFAULT, seed=0, eps=EPS_DEFAULT):
    """Build the L_fake canary score distribution: the empirical false-positive floor.

    Calibrates a fabricated-language generator to the candidate lexicon's own stats (frequency /
    root-template / lexicon-size-matched — F.2, so a trilateral-root-rich Semitic does not beat a
    sparse L_fake by search-attractiveness), generates `n_fake` invented matchable lexicons, and
    scores each with the SAME s_lex the real candidate is scored with. L_fake is never published
    and never in any training set, so any "signal" here is definitionally spurious.

    FAILS OPEN: a degenerate candidate (too few / too-short forms to calibrate trilateral roots) is
    a property of the data, not a crash — returns ``[]`` and the grade records ``no_lfake_null``
    (and REFUSES to graduate, since the headline falsifier is absent). The verdict batch survives.
    """
    forms = [w for w in candidate_lexicon if w]
    if not forms or not heldout_forms:
        return []
    # the semitic trilateral-root sampler needs consonantal skeletons (>=3 consonants). cv/markov
    # are always available as a fallback for vowel-rich or too-short candidates.
    mode = "semitic" if sum(len(set(c for c in w if c not in "aeiou")) >= 3 for w in forms) >= max(2, len(forms) // 2) \
        else "cv"
    recalls = []
    for i in range(int(n_fake)):
        try:
            cfg = lfake.calibrate_to(forms, mode=mode, root_len=3)
            gen = lfake.LFakeGenerator(cfg, seed=seed + i)
            gen.generate_lexicon()
            recalls.append(lexstat.s_lex(heldout_forms, gen.generated, eps))
        except Exception:
            continue                       # one bad draw is fine; n_fake is generous on purpose
    return recalls


# --------------------------------------------------------------------------- #
# The pure grade (no DB, no LLM) — unit-testable
# --------------------------------------------------------------------------- #
def grade(heldout_forms, candidate_lexicon, confidence, free_params, provenance,
          lit_index_hit, virgin_sign_support, u_floor, n_eff,
          null_recalls=None, fake_recalls=None, eps=EPS_DEFAULT, n_fake=N_FAKE_DEFAULT, seed=0):
    """Mechanically grade one hypothesis against its held-out implication.

    Returns a dict with: result (match|partial|deviation), accuracy (S*), brier, dsr, the L_fake
    bar + diagnostics, n_eff, the per-clause §E gate, and the gate_verdict
    (GRADUATE | REJECT | NULL_PUBLISHED). Pure: no DB, no network, no LLM.
    """
    heldout_forms = list(heldout_forms or [])
    candidate_lexicon = list(candidate_lexicon or [])
    per_form = lexstat.s_lex_per_form(heldout_forms, candidate_lexicon, eps)
    observed = (sum(per_form) / len(per_form)) if per_form else 0.0      # S* — raw held-out recall

    # the L_fake headline null (compute if not supplied — keeps grade() self-contained for tests)
    if fake_recalls is None:
        fake_recalls = lfake_distribution(heldout_forms, candidate_lexicon, n_fake, seed, eps)
    fake_recalls = list(fake_recalls or [])
    # the Packard/random-lexeme null (deflation of the statistic itself); fall back to L_fake mean
    null_recalls = list(null_recalls or fake_recalls or [])
    mu0 = (sum(null_recalls) / len(null_recalls)) if null_recalls else 0.0
    s_def = max(0.0, observed - mu0)                                      # deflated S_lex (§B.3 at stat level)

    # the corrected L_fake margin bar (Cornish-Fisher + Bonferroni/DSR, run_canary.corrected_margin_bar)
    has_lfake = bool(fake_recalls)
    if has_lfake:
        n_cmp = max(1, len({eps}))   # one epsilon in the scaffold; ablation grid would widen this
        bar, bar_diag = run_canary.corrected_margin_bar(fake_recalls, n_comparisons=n_cmp)
    else:
        # no L_fake canary -> the headline falsifier is absent. Refuse to graduate; the bar is set
        # at the observed score so beats_lfake_margin is mechanically False (no free pass).
        bar, bar_diag = observed, {"method": "no_lfake_null", "raw_p95": mu0}

    # DSR — the secondary, mechanical-search-scoped statistic (§B.3 via logos_stats.deflated_sharpe).
    # the "return" series is the per-form held-out hit indicator (how consistently the committed map
    # recovers L-lexemes blind); n_trials = the instrumented N_eff; sr_variance = cross-draw null var.
    sr = logos_stats.sharpe([float(h) for h in per_form]) if len(per_form) >= 2 else None
    skew = kurt = 0.0
    if len(per_form) >= 2:
        skew, kurt = logos_stats.moments([float(h) for h in per_form])
    n_trials = max(1, int(n_eff or 1))
    sr_variance = float(sum((r - mu0) ** 2 for r in null_recalls) / max(1, len(null_recalls)))
    dsr = logos_stats.deflated_sharpe(sr, len(per_form), skew, kurt, n_trials, sr_variance) \
        if sr is not None else None

    k = int(free_params)
    u_floor = float(u_floor)
    virgin = float(virgin_sign_support) if virgin_sign_support is not None else 0.0
    # §E gate — ALL must hold for the hypothesis to count as evidence / graduate.
    clauses = {
        "registered_before_test": True,                       # by construction (it's in the DB)
        "lfake_null_present": has_lfake,                      # the headline falsifier must exist
        "dsr_ge_0_95": (dsr is not None and dsr >= DSR_GATE),
        "k_le_u_floor": (k <= u_floor),
        "beats_lfake_margin": (observed > bar),               # the headline L_fake falsifier
        "generalizes_to_virgin": (virgin > 0.0),              # discovery rests only on L_virgin signs
        "not_llm_lit_contamination": not (provenance == "llm_proposed" and bool(lit_index_hit)),
    }
    all_hold = all(clauses.values())

    # result — purely mechanical, held-out only.
    if observed > bar and observed > mu0:
        result = "match"        # clears the corrected L_fake bar -> held-out evidence
    elif observed > mu0:
        result = "partial"      # above the chance null but not clearing the corrected bar
    else:
        result = "deviation"    # no signal above chance (the layer has no power for this candidate)

    # §E graduation verdict.
    if all_hold and result == "match":
        gate_verdict = "GRADUATE"
    elif observed <= mu0:
        gate_verdict = "NULL_PUBLISHED"   # S* ~= L_fake -> calibrated null, the publishable non-result
    else:
        gate_verdict = "REJECT"           # some clause failed / below the corrected bar

    outcome = {"match": 1.0, "partial": 0.5, "deviation": 0.0}[result]
    brier = (float(confidence) - outcome) ** 2
    failing = [c for c, ok in clauses.items() if not ok]

    return {
        "result": result,
        "accuracy": round(observed, 4),
        "s_deflated": round(s_def, 4),
        "null_mean": round(mu0, 4),
        "lfake_bar": round(float(bar), 4),
        "lfake_bar_diag": bar_diag,
        "brier": round(brier, 4),
        "dsr": None if dsr is None else round(dsr, 4),
        "n_eff": n_trials,
        "free_params": k,
        "u_floor": u_floor,
        "gate_verdict": gate_verdict,
        "clauses": clauses,
        "failing_clauses": failing,
        "version": METRIC_VERSION,
    }


def _notes(g):
    """Compact (<=255 char) audit string for verdicts.notes."""
    dsr = "NA" if g["dsr"] is None else f"{g['dsr']:.3f}"
    s = (f"gate={g['gate_verdict']} result={g['result']} dsr={dsr} k={g['free_params']}/"
         f"U{g['u_floor']:.0f} S*={g['accuracy']:.3f} lfake_bar={g['lfake_bar']:.3f} "
         f"virgin={'Y' if g['clauses']['generalizes_to_virgin'] else 'N'} "
         f"fail={','.join(g['failing_clauses']) or 'none'} code={code_sha()} v={METRIC_VERSION}")
    return s[:255]


# --------------------------------------------------------------------------- #
# DB orchestration (the ONLY writer of verdicts)
# --------------------------------------------------------------------------- #
def _load_due(cur, plan_hash=None):
    """Hypotheses with no verdict yet (LEFT JOIN ... IS NULL). Optionally one plan_hash."""
    sql = ("SELECT h.plan_hash, h.family, h.body, h.prediction, h.confidence "
           "FROM hypotheses h LEFT JOIN verdicts v ON v.plan_hash = h.plan_hash "
           "WHERE v.plan_hash IS NULL")
    args = ()
    if plan_hash:
        sql += " AND h.plan_hash=%s"
        args = (plan_hash,)
    cur.execute(sql, args)
    return cur.fetchall()


def grade_row(plan_hash, family, body_json, prediction_json, confidence, n_fake=N_FAKE_DEFAULT,
              eps=EPS_DEFAULT, seed=0):
    """Unpack a hypothesis row into grade() inputs and grade it. `prediction` carries the
    frozen held-out evaluation set (heldout_forms, candidate_lexicon, n_eff, ...)."""
    body = json.loads(body_json) if isinstance(body_json, str) else (body_json or {})
    pred = json.loads(prediction_json) if isinstance(prediction_json, str) else (prediction_json or {})
    heldout_forms = pred.get("heldout_forms") or []
    candidate_lexicon = pred.get("candidate_lexicon") or []
    # N_eff is the INSTRUMENTED trial count the retrieval logged (design §B.2) — COUNT it, don't
    # estimate it. If absent, default 1 (single-trial; the L_fake canary is the N_eff-independent
    # backstop, so an un-instrumented search is still falsified, just not DSR-deflated).
    n_eff = int(pred.get("n_eff", 1))
    free_params = int(body.get("free_params", 0) or 0)
    return grade(
        heldout_forms=heldout_forms, candidate_lexicon=candidate_lexicon,
        confidence=confidence, free_params=free_params,
        provenance=body.get("provenance", "human"),
        lit_index_hit=bool(pred.get("lit_index_hit", False)),
        virgin_sign_support=pred.get("virgin_sign_support"),
        # U_floor default = k (no MDL slack): a hypothesis that asserts more free params than the
        # corpus can pin fails k<=U_floor by default; the predictor must commit a real budget.
        u_floor=float(pred.get("u_floor", free_params)),
        n_eff=n_eff, null_recalls=pred.get("null_recalls"),
        eps=eps, n_fake=n_fake, seed=seed)


def write_verdict(cur, plan_hash, family, g):
    """INSERT the verdict (idempotent via UNIQUE uq_verdicts_plan)."""
    heldout_site = ""
    g2 = dict(g)
    cur.execute(
        """INSERT INTO verdicts (plan_hash, result, held_out_site, accuracy, brier, notes, provenance)
           VALUES (%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE result=VALUES(result), accuracy=VALUES(accuracy),
              brier=VALUES(brier), notes=VALUES(notes), provenance=VALUES(provenance)""",
        (plan_hash, g["result"], heldout_site, g["accuracy"], g["brier"], _notes(g), code_sha()))
    return g2


def run(plan_hash=None, n_fake=N_FAKE_DEFAULT, eps=EPS_DEFAULT, seed=0, conn=None):
    """Grade every due hypothesis (or one) and write its verdict. Returns [(plan_hash, grade), ...]."""
    owns = conn is None
    conn = conn or logos_db.db()
    out = []
    try:
        with conn.cursor() as cur:
            for ph, family, body, pred, conf in _load_due(cur, plan_hash):
                try:
                    g = grade_row(ph, family, body, pred, float(conf), n_fake=n_fake, eps=eps, seed=seed)
                    write_verdict(cur, ph, family, g)
                    out.append((ph, g))
                    dsr_s = "NA" if g["dsr"] is None else f"{g['dsr']:.3f}"
                    print(f"  {g['result']:9} {ph[:12]} gate={g['gate_verdict']:14} "
                          f"S*={g['accuracy']:.3f} lfake_bar={g['lfake_bar']:.3f} dsr={dsr_s}")
                except Exception as e:  # a single bad row must not abort the batch
                    print(f"  SKIP {ph[:12]}: {type(e).__name__}: {e}")
    finally:
        if owns:
            conn.close()
    if not out:
        print("no due hypotheses (everything graded or none committed).")
    return out


def main():
    ap = argparse.ArgumentParser(description="the SOLE writer of logos.verdicts (mechanical, held-out)")
    ap.add_argument("plan_hash", nargs="?", help="grade one hypothesis; omit for all due")
    ap.add_argument("--n-fake", type=int, default=N_FAKE_DEFAULT, help="L_fake canary instances")
    ap.add_argument("--eps", type=float, default=EPS_DEFAULT, help="S_lex normalized-edit epsilon")
    args = ap.parse_args()
    run(plan_hash=args.plan_hash, n_fake=args.n_fake, eps=args.eps)


if __name__ == "__main__":
    main()
