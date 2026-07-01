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
  registered before test; search multiplicity INSTRUMENTED (N_eff COUNTED — else fail closed to
  INCOMPLETE, never n_trials=1); L_fake null present; beats the ORDER-STATISTIC E[max] bar over
  N_eff (the operative deflation); beats the L_fake corrected margin; generalizes to L_virgin signs
  above a pre-registered threshold; not (llm_proposed AND lit_index_hit); S_morph gold-standard when
  the corpus has power. DSR and the MDL check (k<=U_floor) are REPORTED diagnostics, REMOVED from the
  gate after review. Fail any -> gate verdict REJECT / NULL_PUBLISHED / INCOMPLETE. Never GRADUATE on
  internal fit.

CLI:
  python3 scripts/verdict.py                 # grade all due hypotheses
  python3 scripts/verdict.py <plan_hash>     # grade one (re-grade: deletes prior verdict first)
"""
import argparse
import datetime
import hashlib
import json
import math
import os
import sys
from statistics import NormalDist

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from scripts import logos_db, logos_stats  # noqa: E402
from scripts.comparison import lexstat, lfake, run_canary  # noqa: E402
# Additive comparison-layer diagnostics + §E gate inputs (design §A.2/§B.2/§B.3/§C.2). All pure,
# arithmetic, deterministic — never on the verdict's decision: S_phono/S_morph are REPORTED, the
# searchlog supplies the instrumented N_eff, litindex supplies the L_virgin generalization share.
from scripts.comparison import phonostat, morphostat, searchlog, litindex  # noqa: E402

METRIC_VERSION = "verdict-v2"          # bump when grade semantics / gate clauses change (P0.3-0.5: fail-
                                       # closed on un-instrumented multiplicity; eps-grid comparison count)
GATE_VERSION = "gate-e2"               # §E gate semantics version (persisted per verdict)
DSR_GATE = 0.95                        # §E DSR threshold — REPORTED/diagnostic only, off every gate
N_FAKE_DEFAULT = 300                   # P1.4: L_fake canary instances for the headline null distribution
                                       # (the corrected-margin/Cornish-Fisher bar is estimated from these)
EPS_DEFAULT = 0.25                     # normalized-edit-distance epsilon for S_lex
_NORM = NormalDist()                   # Φ for the §B.3 order-stat DSR (reported/secondary per F.1)


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
          null_recalls=None, fake_recalls=None, eps=EPS_DEFAULT, n_fake=N_FAKE_DEFAULT, seed=0,
          heldout_by_inscription=None, search_log=None, per_sign_support=None, sign_partition=None,
          phono_order=3, virgin_threshold=None, virgin_min_signs=2, eps_grid=None):
    """Mechanically grade one hypothesis against its held-out implication.

    Returns a dict with: result (match|partial|deviation), accuracy (S*), brier, dsr, the L_fake
    bar + diagnostics, n_eff, the per-clause §E gate, and the gate_verdict
    (GRADUATE | REJECT | NULL_PUBLISHED). Pure: no DB, no network, no LLM.

    PRIMARY/HEADLINE are unchanged (refinement F.1): deflated S_lex is the pragmatic primary and the
    L_fake corrected-margin canary is the headline falsifier. The parameters below are ADDITIVE — they
    feed REPORTED diagnostics and the already-wired §E clauses, never weaken an existing clause:

      heldout_by_inscription : held-out forms grouped per INDEPENDENT inscription (list of lists) so
          S_morph (the STRONG/Kober test, §A.2) can test cross-inscription recurrence. When None, the
          flat ``heldout_forms`` is used, which forces S_morph's F.1 no-power escape (single group).
      search_log             : a :class:`searchlog.SearchLog` (or any object exposing ``.n_eff``); when
          given, its COUNTED N_eff (design §B.2, invariant 12) overrides the hand-passed ``n_eff``.
      per_sign_support, sign_partition : a per-sign held-out support map + an {L_known, L_virgin}
          partition; when both given, the §E ``generalizes_to_virgin`` clause uses
          ``litindex.virgin_support`` over them instead of the pre-passed ``virgin_sign_support`` float.
      phono_order            : n-gram order for the REPORTED S_phono surface-plausibility diagnostic.
    """
    heldout_forms = list(heldout_forms or [])
    candidate_lexicon = list(candidate_lexicon or [])

    # Instrumented N_eff (design §B.2, invariant 12 — counts are GENERATED, not hand-written): a
    # SearchLog's COUNTED distinct-candidate total is authoritative over the hand-passed int when the
    # retrieval was instrumented. Duck-typed so tests/fakes exposing `.n_eff` also work; falls back
    # cleanly to the passed n_eff otherwise (a missing instrument never crashes the grade).
    n_eff_source = "passed"
    if isinstance(search_log, searchlog.SearchLog) or (search_log is not None and hasattr(search_log, "n_eff")):
        n_eff = int(search_log.n_eff)
        n_eff_source = "searchlog"

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
        # P0.4: the L_fake margin's multiplicity count must be the FULL searched epsilon grid, taken
        # from the persisted search log (or passed explicitly), NEVER inferred from the single
        # SELECTED eps (which is always 1 and silently undercounts the comparisons made).
        _grid = None
        if search_log is not None and getattr(search_log, "eps_grid", None):
            _grid = list(search_log.eps_grid)
        _grid = _grid or list(eps_grid or []) or [eps]
        n_cmp = max(1, len(set(_grid)))
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

    # §B.3 order-statistic bar (ADDITIVE / SECONDARY per F.1; the L_fake corrected bar stays HEADLINE).
    # The deflated threshold is E[max over N_eff draws from the null] (μ0 + σ0·z-multiplier); then
    # DSR_order = Φ((S* − bar) / σ̂(S*)), with σ̂ = the standard error of the held-out recall S* so a
    # THIN held-out set T widens σ̂ and pulls DSR_order toward 0.5 (design §B.3: penalize thin T).
    # A missing/degenerate n_eff or σ falls back cleanly (expected_max_order_stat → μ0; DSR_order None).
    sigma0 = math.sqrt(sr_variance)
    order_stat_bar = logos_stats.expected_max_order_stat(mu0, sigma0, n_trials)
    T = len(per_form)
    sigma_hat = None
    dsr_order = None
    if T >= 2:
        var_h = sum((float(h) - observed) ** 2 for h in per_form) / (T - 1)   # sample var of per-form hits
        se = math.sqrt(var_h / T)                                             # σ̂(S*) = SE of the mean
        if se > 1e-12:
            sigma_hat = se
            dsr_order = _NORM.cdf((observed - order_stat_bar) / se)

    # S_phono (phonostat §A.2) — the WEAK surface-plausibility diagnostic, REPORTED beneath S_lex (F.1).
    # NaN (degenerate: empty held-out OR empty lexicon) is surfaced as None + the explicit flag, never a
    # misleading finite 0 (honesty: a no-power read is visibly distinct from a real likelihood).
    phono_rep = phonostat.s_phono_report(heldout_forms, candidate_lexicon, order=phono_order)
    _sp = phono_rep["s_phono"]
    s_phono_val = round(float(_sp), 4) if isinstance(_sp, float) and _sp == _sp else None
    s_phono_degenerate = bool(phono_rep["is_degenerate"])

    # S_morph (morphostat §A.2) — the STRONG/Kober gold-standard test, used WHEN POWERED (F.1). Grouped
    # held-out (heldout_by_inscription) lets it test cross-inscription recurrence; a flat list forces the
    # no-power escape. A no-power result is REPORTED but neutral to the gate (it must not block/fake-pass).
    morph_input = heldout_by_inscription if heldout_by_inscription is not None else heldout_forms
    s_morph_res = morphostat.s_morph(morph_input, candidate_lexicon, seed=seed)
    morph_powered = bool(s_morph_res.get("is_powered", False))

    k = int(free_params)
    # P0.1: u_floor is now REPORTED-ONLY. The k<=u_floor MDL clause was dimensionally incoherent (a
    # free-parameter COUNT compared against a sign-occurrence unicity figure) and, worse, u_floor
    # defaulted to free_params, so k<=u_floor passed by construction. The clause is deleted from the §E
    # gate; unicity survives only as the withdrawn toy-model precondition diagnostic. Real bit-level MDL
    # is stated future work. No free_params fallback: if a prereg omits u_floor it is reported as NaN,
    # never silently satisfied.
    u_floor = float(u_floor) if u_floor is not None else float("nan")
    # §E generalizes_to_virgin: prefer litindex.virgin_support over a per-sign support map + the
    # {L_known, L_virgin} partition WHEN both are supplied (the instrumented §C.2 path); otherwise fall
    # back to the pre-passed float (existing behaviour — callers without the partition are unchanged).
    if per_sign_support is not None and sign_partition is not None:
        virgin = float(litindex.virgin_support(per_sign_support, sign_partition))
    else:
        virgin = float(virgin_sign_support) if virgin_sign_support is not None else 0.0
    # P0.2: discovery must clear a PRE-REGISTERED L_virgin threshold, never a single hit. Fail closed —
    # absent a committed virgin_threshold the clause does NOT pass. When the per-sign partition is
    # available, ALSO require >= virgin_min_signs DISTINCT L_virgin signs to carry held-out support.
    n_virgin_supported = None
    if per_sign_support is not None and sign_partition is not None:
        _lv = set(sign_partition.get("L_virgin", []))
        n_virgin_supported = sum(1 for s in _lv if float(per_sign_support.get(s, 0.0)) > 0.0)
    virgin_ok = (virgin_threshold is not None) and (virgin >= float(virgin_threshold))
    if n_virgin_supported is not None:
        virgin_ok = virgin_ok and (n_virgin_supported >= int(virgin_min_signs))
    # P0.3: the operative deflation clause is the §B.3 order-statistic bar (E[max over n_trials draws
    # from the null]); S* must EXCEED it. Fail closed on a degenerate null (no variance, or <1 trial —
    # the bar collapses to mu0 and is meaningless, so the clause must not pass). Finance-DSR is DEMOTED
    # to reported-only (kept in the output, off the decision path).
    beats_order_stat = (sigma0 > 1e-12) and (n_trials >= 1) and (observed > float(order_stat_bar))
    # §E gate — ALL must hold for the hypothesis to count as evidence / graduate.
    clauses = {
        "registered_before_test": True,                       # by construction (it's in the DB)
        "search_multiplicity_instrumented": (n_eff_source == "searchlog"),  # P0.3: fail closed unless
                                                              # N_eff was COUNTED (never the fail-open n=1 default)
        "lfake_null_present": has_lfake,                      # the headline falsifier must exist
        "beats_order_stat_bar": beats_order_stat,             # P0.3: E[max over n_trials] deflation (operative)
        "beats_lfake_margin": (observed > bar),               # the headline L_fake falsifier
        "generalizes_to_virgin": virgin_ok,                   # P0.2: pre-registered L_virgin threshold
        "not_llm_lit_contamination": not (provenance == "llm_proposed" and bool(lit_index_hit)),
        # S_morph is the gold-standard test WHEN THE CORPUS CAN SUPPORT IT (F.1). The clause keys off
        # has_power (the corpus has enough independent inscriptions/affixes/null-variance to test
        # morphology) vs is_significant (given power, the affixes productively recur above the null):
        #   has_power & significant     -> True   (corroborated)
        #   has_power & NOT significant -> False  (the strong test was AVAILABLE and the candidate
        #                                          FAILED it -> blocks graduation; a REAL clause)
        #   NOT has_power               -> True   (neutral: a short/formulaic corpus's honest no-power
        #                                          must never block or fake-pass the gate)
        # This is NOT the old tautology (is_powered already implied deflated>0): a powered-but-
        # insignificant S_morph can now make this clause False. AND-ing it is still monotone — it only
        # makes the gate STRICTER, so no existing §E clause is weakened.
        "morph_gold_standard_when_powered": (bool(s_morph_res.get("is_significant", False))
                                             if s_morph_res.get("has_power") else True),
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
    _substantive_hold = all(v for k, v in clauses.items()
                            if k != "search_multiplicity_instrumented")
    if all_hold and result == "match":
        gate_verdict = "GRADUATE"
    elif result == "match" and _substantive_hold and n_eff_source != "searchlog":
        # P0.3: clears every substantive clause but the multiplicity N_eff was NOT counted (fail-open
        # n_trials=1 default) — fail closed. Never a silent win on an un-instrumented search.
        gate_verdict = "INCOMPLETE"
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
        # §B.3 order-stat bar + DSR (reported/secondary per F.1 — NOT a gate input; the gate's DSR
        # clause stays bound to the primary `dsr` above).
        "order_stat_bar": round(float(order_stat_bar), 4),
        "dsr_order": None if dsr_order is None else round(float(dsr_order), 4),
        "sigma_hat": None if sigma_hat is None else round(float(sigma_hat), 6),
        "n_trials": n_trials,                    # P0.3: distinct candidates tried (SearchLog), NOT independent tests
        "n_trials_source": n_eff_source,
        "n_virgin_supported": n_virgin_supported,   # distinct L_virgin signs with held-out support (None if unpartitioned)
        # additive comparison-layer diagnostics (REPORTED, never on the verdict's decision path).
        "s_phono": s_phono_val,                  # None when degenerate (NaN) — honest no-power, not a 0
        "s_phono_degenerate": s_phono_degenerate,
        "s_morph": s_morph_res,                  # full no-power-aware result (is_powered + reason + z…)
        "s_morph_powered": morph_powered,
        "free_params": k,
        "u_floor": u_floor,
        "gate_verdict": gate_verdict,
        "gate_version": GATE_VERSION,
        "clauses": clauses,
        "failing_clauses": failing,
        "version": METRIC_VERSION,
    }


def _notes(g):
    """Compact (<=255 char) audit string for verdicts.notes."""
    dsr = "NA" if g["dsr"] is None else f"{g['dsr']:.3f}"
    dsro = "NA" if g.get("dsr_order") is None else f"{g['dsr_order']:.3f}"
    mph = "Y" if g.get("s_morph_powered") else "np"   # np = no power (the F.1 escape), distinct from a fail
    uf = "NA" if g["u_floor"] != g["u_floor"] else f"{g['u_floor']:.0f}"   # NaN-safe (u_floor reported-only)
    s = (f"gate={g['gate_verdict']} result={g['result']} dsr={dsr} dsrO={dsro} k={g['free_params']}/"
         f"U{uf} osbar={g['order_stat_bar']:.3f} S*={g['accuracy']:.3f} lfake_bar={g['lfake_bar']:.3f} "
         f"virgin={'Y' if g['clauses']['generalizes_to_virgin'] else 'N'} morph={mph} "
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
    # Additive §A.2/§C.2 inputs, consumed only WHEN the prediction carries them (else None ⇒ the
    # pre-existing flat/float fallbacks): per-inscription grouping powers S_morph's cross-inscription
    # test; a per-sign support map + {L_known,L_virgin} partition lets the gate use litindex.virgin_support.
    heldout_by_inscription = pred.get("heldout_by_inscription")
    per_sign_support = pred.get("per_sign_support")
    sp = pred.get("sign_partition")
    sign_partition = None
    if isinstance(sp, dict):                                # JSON arrays -> sets for litindex.virgin_support
        sign_partition = {key: set(sp.get(key, []) or []) for key in ("L_known", "L_virgin")}
    return grade(
        heldout_forms=heldout_forms, candidate_lexicon=candidate_lexicon,
        confidence=confidence, free_params=free_params,
        provenance=body.get("provenance", "human"),
        lit_index_hit=bool(pred.get("lit_index_hit", False)),
        virgin_sign_support=pred.get("virgin_sign_support"),
        # P0.1: u_floor is REPORTED-ONLY (the k<=u_floor clause is removed). No free_params fallback —
        # an omitted u_floor is reported as NaN, never silently satisfied. Real bit-level MDL is future work.
        u_floor=pred.get("u_floor"),
        n_eff=n_eff, null_recalls=pred.get("null_recalls"),
        eps=eps, n_fake=n_fake, seed=seed,
        heldout_by_inscription=heldout_by_inscription,
        per_sign_support=per_sign_support, sign_partition=sign_partition,
        # P0.2: the pre-registered L_virgin discovery threshold + min distinct virgin signs (fail closed
        # if the prereg commits no threshold).
        virgin_threshold=pred.get("virgin_threshold"),
        virgin_min_signs=int(pred.get("virgin_min_signs", 2)))


def write_verdict(cur, plan_hash, family, g):
    """INSERT the verdict (idempotent via UNIQUE uq_verdicts_plan).

    P0.1/P0.5: gate_verdict, gate_version and the per-clause gate_clauses_json are persisted as
    STRUCTURED columns (not left to survive only inside the free-text `notes`), so downstream
    roll-ups (family_scores) read the §E outcome directly and a win is provably a GRADUATE."""
    heldout_site = ""
    g2 = dict(g)
    clauses_json = json.dumps(g.get("clauses", {}), sort_keys=True)
    cur.execute(
        """INSERT INTO verdicts (plan_hash, result, gate_verdict, gate_version, gate_clauses_json,
                                 held_out_site, accuracy, brier, notes, provenance)
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
           ON DUPLICATE KEY UPDATE result=VALUES(result), gate_verdict=VALUES(gate_verdict),
              gate_version=VALUES(gate_version), gate_clauses_json=VALUES(gate_clauses_json),
              accuracy=VALUES(accuracy), brier=VALUES(brier), notes=VALUES(notes),
              provenance=VALUES(provenance)""",
        (plan_hash, g["result"], g.get("gate_verdict"), g.get("gate_version", GATE_VERSION),
         clauses_json, heldout_site, g["accuracy"], g["brier"], _notes(g), code_sha()))
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
