"""Pure research-integrity statistics (AGORA-21): Sharpe, the Probabilistic Sharpe Ratio, and
the Deflated Sharpe Ratio (Bailey & López de Prado 2014) — the multiple-testing guard.

The DSR answers the one question agora's mission demands: with N strategies tried, what is the
probability that THIS one's Sharpe reflects real skill rather than the luckiest draw of N? No DB,
no network — unit-tested in tests/test_agora.py.
"""
import math
import random
from statistics import NormalDist

_N = NormalDist()
EULER_GAMMA = 0.5772156649015329


def sharpe(returns):
    """Per-period Sharpe of a return series (mean / sample-stdev). None if <2 pts or zero vol."""
    n = len(returns)
    if n < 2:
        return None
    m = sum(returns) / n
    sd = (sum((r - m) ** 2 for r in returns) / (n - 1)) ** 0.5
    return m / sd if sd > 1e-12 else None


def moments(returns):
    """(skew, kurtosis) — kurtosis is NON-excess (3.0 for a normal distribution)."""
    n = len(returns)
    m = sum(returns) / n
    sd = (sum((r - m) ** 2 for r in returns) / n) ** 0.5 or 1e-12
    skew = sum(((r - m) / sd) ** 3 for r in returns) / n
    kurt = sum(((r - m) / sd) ** 4 for r in returns) / n
    return skew, kurt


def psr(sr, n, skew, kurt, sr_benchmark=0.0):
    """Probabilistic Sharpe Ratio: P(true Sharpe > sr_benchmark) given n obs + higher moments.
    kurt = non-excess kurtosis (3 = normal). Returns a probability in [0,1] or None."""
    if sr is None or n < 2:
        return None
    denom = 1.0 - skew * sr + (kurt - 1.0) / 4.0 * sr * sr
    if denom <= 1e-12:
        return None
    z = (sr - sr_benchmark) * math.sqrt(n - 1) / math.sqrt(denom)
    return _N.cdf(z)


def expected_max_sharpe(n_trials, sr_variance):
    """Expected maximum Sharpe under the null across n_trials independent strategies
    (Bailey–López de Prado). sr_variance = variance of the trials' Sharpe estimates."""
    if n_trials < 2 or sr_variance <= 0:
        return 0.0
    sd = math.sqrt(sr_variance)
    z1 = _N.inv_cdf(1.0 - 1.0 / n_trials)
    z2 = _N.inv_cdf(1.0 - 1.0 / (n_trials * math.e))
    return sd * ((1.0 - EULER_GAMMA) * z1 + EULER_GAMMA * z2)


def deflated_sharpe(sr, n, skew, kurt, n_trials, sr_variance):
    """Deflated Sharpe Ratio: probability the observed Sharpe reflects skill, *deflated* for the
    selection bias of having tried n_trials strategies. The G2 gate's honesty test."""
    sr0 = expected_max_sharpe(n_trials, sr_variance)
    return psr(sr, n, skew, kurt, sr_benchmark=sr0)


def dsr_trial_count(n_scored, n_declared):
    """Selection-bias multiplicity fed to the Deflated Sharpe Ratio — the number of strategies
    'tried'. Deflate by EVERY declared family (not only those that produced a Sharpe yet) and never
    below 1, so the DSR can never be silently un-deflated to a single-trial (decorative) value. This
    extracts the most load-bearing attestation in the honesty stack into one tested place: a
    regression that set the count to 1 fails its unit test (audit V6)."""
    return max(int(n_scored), int(n_declared), 1)


def _var_min_n(alpha):
    # below ~1/(1−alpha) observations the (1−alpha) tail has <1 point, so the quantile degenerates to the
    # single WORST day and grossly overstates risk — at alpha=0.95 that falsely armed the circuit breaker
    # on ~6 days of history. Require the floor; the consumer (portfolio_risk) treats None as 'don't arm'.
    return max(5, int(round(1.0 / (1.0 - alpha))))


def historical_var(returns, alpha=0.95):
    """Historical Value-at-Risk: the loss (positive %) the book exceeds only (1−alpha) of the time.
    Returns None below ~1/(1−alpha) observations (the tail quantile is meaningless there)."""
    if len(returns) < _var_min_n(alpha):
        return None
    s = sorted(returns)
    idx = max(0, min(len(s) - 1, int((1.0 - alpha) * len(s) + 1e-9)))   # +eps: 0.1*10 floats to 0.999…
    return -s[idx]


def expected_shortfall(returns, alpha=0.95):
    """Expected Shortfall (CVaR): the average loss in the worst (1−alpha) tail — what VaR ignores."""
    if len(returns) < _var_min_n(alpha):
        return None
    s = sorted(returns)
    idx = max(1, int((1.0 - alpha) * len(s) + 1e-9))
    tail = s[:idx]
    return -(sum(tail) / len(tail))


def rolling_sharpe_trend(returns, min_n=10):
    """Sharpe(recent half) − Sharpe(older half). Negative ⇒ the edge is fading. None if too short."""
    n = len(returns)
    if n < min_n:
        return None
    h = n // 2
    a, b = sharpe(returns[:h]), sharpe(returns[h:])
    if a is None or b is None:
        return None
    return round(b - a, 4)


def edge_decaying(returns, min_n=12, trend_drop=0.3, mean_drop_sd=0.5):
    """A structural-decay flag for a family's verdict-return series: True if the rolling Sharpe is
    trending down hard OR the recent half's mean return has dropped ≥ mean_drop_sd stdevs below the
    older half. Catches an edge dying *before* the drawdown does."""
    n = len(returns)
    if n < min_n:
        return False
    h = n // 2
    a, b = returns[:h], returns[h:]
    ma, mb = sum(a) / len(a), sum(b) / len(b)
    sda = (sum((r - ma) ** 2 for r in a) / len(a)) ** 0.5 or 1e-9
    trend = rolling_sharpe_trend(returns)
    return (trend is not None and trend < -trend_drop) or ((ma - mb) > mean_drop_sd * sda)


def purged_kfold(n, k=5, embargo=0):
    """Purged K-fold splits (López de Prado): each test fold is a contiguous block; the train set
    drops that block AND an `embargo` of points on each side, so overlapping-horizon labels can't
    leak from test into train. Returns [(train_idx, test_idx), ...]. The within-family overfitting
    control that complements the DSR's across-family selection control."""
    folds = []
    size = max(1, n // k)
    for i in range(k):
        lo = i * size
        hi = n if i == k - 1 else (i + 1) * size
        if lo >= n:
            break
        test = list(range(lo, min(hi, n)))
        plo, phi = max(0, lo - embargo), min(n, hi + embargo)
        train = [j for j in range(n) if j < plo or j >= phi]
        folds.append((train, test))
    return folds


def softmax(values, temp=1.0):
    """Normalised exp weights (sum to 1). Higher value → higher weight; temp controls sharpness.
    The meta-allocator's capital split across families."""
    if not values:
        return []
    mx = max(values)
    exps = [math.exp((v - mx) / temp) for v in values]
    s = sum(exps) or 1.0
    return [e / s for e in exps]


# ─────────────────────────────────────────────────────────────────────────────
# AGORA-30 — López de Prado compliance layer (see docs/lopez-de-prado-audit.md).
# All pure, all unit-tested. These close the gaps the audit found in agora's honesty stack.
# ─────────────────────────────────────────────────────────────────────────────

def average_uniqueness(spans):
    """Average uniqueness of overlapping labels (López de Prado ch4). spans = [(t0, t1), …] as
    integer day-indices, t1 inclusive. Two labels are *concurrent* when their intervals overlap —
    they share a return, so they are NOT IID. Each label's uniqueness is the mean of 1/concurrency
    over its lifespan; returns one ū_i ∈ (0, 1] per span (1 = no overlap, →0 = heavily overlapped).
    The fix for agora's #1 integrity bug: PSR/DSR must scale by the SUM of these, not the raw count."""
    if not spans:
        return []
    lo = min(s[0] for s in spans)
    hi = max(s[1] for s in spans)
    width = hi - lo + 1
    # sweep-line concurrency: +1 at t0, −1 after t1, then prefix-sum
    delta = [0] * (width + 1)
    for (a, b) in spans:
        delta[a - lo] += 1
        delta[b - lo + 1] -= 1
    conc = [0] * width
    run = 0
    for t in range(width):
        run += delta[t]
        conc[t] = run
    out = []
    for (a, b) in spans:
        span = b - a + 1
        u = sum(1.0 / conc[t - lo] for t in range(a, b + 1) if conc[t - lo] > 0) / span
        out.append(u)
    return out


def effective_n(spans):
    """Effective number of (near-)independent observations for a set of overlapping labels =
    Σ average_uniqueness. ≤ len(spans). This is the honest `n` to feed PSR/DSR — feeding the raw
    count overstates the track record and makes the honesty gate too generous (audit §A1)."""
    us = average_uniqueness(spans)
    return sum(us) if us else 0.0


def hhi(values):
    """Herfindahl–Hirschman concentration of a series, normalised to [0, 1]. 0 = perfectly uniform
    (every observation contributes equally — healthy), 1 = a single observation dominates (fragile).
    Run on positive returns and on negative returns separately (López de Prado ch14 §14.5.1): a high
    h+ means the 'edge' is really one or two lucky bets — a fragility the Sharpe alone won't show."""
    w = [abs(v) for v in values]
    s = sum(w)
    n = len(w)
    if s <= 0 or n < 2:
        return None
    p = [x / s for x in w]
    raw = sum(x * x for x in p)
    return max(0.0, (raw - 1.0 / n) / (1.0 - 1.0 / n))


def implied_precision(target_sharpe, n_per_year, pi_pos, pi_neg):
    """Precision p a strategy needs to hit `target_sharpe`, given its bet frequency and payouts
    (López de Prado ch15 §15.3, asymmetric payouts). pi_pos>0, pi_neg<0 are the average win/loss.
    Solves a p² + b p + c = 0 and returns the upper root in [0, 1] (None if infeasible)."""
    D = pi_pos - pi_neg
    if D <= 0 or n_per_year <= 0:
        return None
    a = (n_per_year + target_sharpe ** 2) * D * D
    b = D * (2 * n_per_year * pi_neg - target_sharpe ** 2 * D)
    c = n_per_year * pi_neg * pi_neg
    disc = b * b - 4 * a * c
    if disc < 0 or a == 0:
        return None
    p = (-b + math.sqrt(disc)) / (2 * a)
    return min(1.0, max(0.0, p))


def prob_strategy_failure(returns, n_per_year, target_sharpe=1.0):
    """Probability a strategy FAILS to reach `target_sharpe` — *strategy* risk, not portfolio risk
    (López de Prado ch15 §15.4). Estimates win/loss payouts and observed precision p̂ from the bet
    outcomes, derives the precision p* required for the target, and returns P(p < p*) under a normal
    approx of p̂. High = fragile: one small drop in hit-rate wipes the edge, even at low volatility."""
    pos = [r for r in returns if r > 0]
    neg = [r for r in returns if r <= 0]
    m = len(returns)
    if m < 10 or not pos or not neg:
        return None
    pi_pos = sum(pos) / len(pos)
    pi_neg = sum(neg) / len(neg)
    p_hat = len(pos) / m
    p_req = implied_precision(target_sharpe, n_per_year, pi_pos, pi_neg)
    if p_req is None:
        return None
    se = (p_hat * (1.0 - p_hat) / m) ** 0.5 or 1e-9
    return _N.cdf((p_req - p_hat) / se)


def pbo(pnl_matrix, s=8):
    """Probability of Backtest Overfitting via CSCV (Bailey/López de Prado ch11 §11.6). pnl_matrix =
    list of columns, each a per-period return series for ONE config (same length). Splits the rows
    into s blocks, forms every C(s, s/2) train/test combination, picks the in-sample-best config and
    measures how often its OUT-of-sample rank lands below the median (logit ≤ 0). PBO = that fraction.
    Complements DSR: DSR = selection bias *across* families, PBO = overfitting *within* the search."""
    import itertools
    cols = [c for c in pnl_matrix if c]
    N = len(cols)
    if N < 2:
        return None
    T = min(len(c) for c in cols)
    if T < s or s % 2 != 0:
        return None
    cols = [c[:T] for c in cols]
    bsize = T // s
    blocks = [list(range(i * bsize, (i + 1) * bsize if i < s - 1 else T)) for i in range(s)]
    logits = []
    for combo in itertools.combinations(range(s), s // 2):
        tr = [i for b in combo for i in blocks[b]]
        te = [i for b in range(s) if b not in combo for i in blocks[b]]
        is_perf = [sharpe([col[i] for i in tr]) for col in cols]
        oos_perf = [sharpe([col[i] for i in te]) for col in cols]
        best = max(range(N), key=lambda j: (is_perf[j] if is_perf[j] is not None else -9.0))
        ob = oos_perf[best]
        valid = [x for x in oos_perf if x is not None]
        if ob is None or not valid:
            continue
        rank = sum(1 for x in valid if x <= ob) / len(valid)
        rank = min(max(rank, 1e-6), 1 - 1e-6)
        logits.append(math.log(rank / (1.0 - rank)))
    if not logits:
        return None
    return sum(1 for x in logits if x <= 0) / len(logits)


def time_under_water(returns):
    """Longest run (in number of bets) the cumulative-PnL curve spends below a prior high-watermark
    (López de Prado ch14 §14.5.2). The metric that actually predicts operator abandonment — directly
    relevant to agora's 'survive abandonment' constraint. Returns the max TuW in observations."""
    cum = peak = 0.0
    since = worst = 0
    for r in returns:
        cum += r
        if cum >= peak:
            peak = cum
            since = 0
        else:
            since += 1
            worst = max(worst, since)
    return worst


def cusum_break(returns, threshold=5.0):
    """One-sided (downward) CUSUM structural-break detector on standardized returns (López de Prado
    ch17 flavour). Accumulates negative deviations of returns from their running mean, resetting at
    zero; fires when the cumulative excursion exceeds `threshold` σ — a sustained regime break, not a
    one-day dip. Returns (broke: bool, max_excursion_sigma: float). Hardens edge_decay's heuristic."""
    n = len(returns)
    if n < 12:
        return (False, 0.0)
    m = sum(returns) / n
    sd = (sum((r - m) ** 2 for r in returns) / n) ** 0.5 or 1e-9
    s_neg = 0.0
    worst = 0.0
    for r in returns:
        s_neg = min(0.0, s_neg + (r - m) / sd)
        worst = min(worst, s_neg)
    return (worst <= -threshold, round(-worst, 3))


def bet_size_from_prob(prob, n_classes=2):
    """Translate a calibrated probability into a signed bet size in [−1, 1] (López de Prado ch10
    §10.3): z = (p − 1/k) / √(p(1−p)); size = 2·Φ(z) − 1. Lets size respond to THIS signal's
    strength rather than only the family's average win-rate. Feeds sizing once meta-labels give P(act)."""
    if prob is None or prob <= 0.0 or prob >= 1.0:
        return 0.0
    z = (prob - 1.0 / n_classes) / (prob * (1.0 - prob)) ** 0.5
    return 2.0 * _N.cdf(z) - 1.0


# ── Hierarchical Risk Parity (López de Prado ch16) — capital allocation across correlated families ──

def _covariance(mat):
    n, T = len(mat), len(mat[0])
    means = [sum(c) / T for c in mat]
    cov = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i, n):
            c = sum((mat[i][t] - means[i]) * (mat[j][t] - means[j]) for t in range(T)) / max(1, T - 1)
            cov[i][j] = cov[j][i] = c
    return cov


def _correlation(cov):
    n = len(cov)
    sd = [cov[i][i] ** 0.5 or 1e-12 for i in range(n)]
    return [[cov[i][j] / (sd[i] * sd[j]) for j in range(n)] for i in range(n)]


def _quasi_diag(dist):
    """Single-linkage agglomerative clustering on a distance matrix → seriated leaf order (the
    quasi-diagonalization of ch16: similar assets adjacent, dissimilar far apart)."""
    n = len(dist)
    members = {i: [i] for i in range(n)}
    active = list(range(n))
    nxt = n
    while len(active) > 1:
        best = None
        bp = None
        for ii in range(len(active)):
            for jj in range(ii + 1, len(active)):
                a, b = active[ii], active[jj]
                d = min(dist[x][y] for x in members[a] for y in members[b])  # nearest-point linkage
                if best is None or d < best:
                    best, bp = d, (a, b)
        a, b = bp
        members[nxt] = members[a] + members[b]   # order preserved → seriation
        active.remove(a)
        active.remove(b)
        active.append(nxt)
        nxt += 1
    return members[active[0]]


def _cluster_var(cov, items):
    iv = [1.0 / cov[i][i] if cov[i][i] > 0 else 0.0 for i in items]
    s = sum(iv) or 1.0
    w = [x / s for x in iv]
    var = 0.0
    for a in range(len(items)):
        for b in range(len(items)):
            var += w[a] * w[b] * cov[items[a]][items[b]]
    return var


def hrp_weights(returns_by_asset, mp_q=None, metric="corr"):
    """Hierarchical Risk Parity (López de Prado ch16): allocate capital across families by
    tree-clustering the correlation matrix → quasi-diagonalizing → recursive bisection with
    inverse-variance splits. Delivers lower OUT-of-sample variance than inverse-variance or softmax
    when the families are correlated (agora's are), and is robust on a near-singular covariance.
    returns_by_asset = {name: [returns…]}. Returns {name: weight}, weights sum to 1.

    AGORA-38 C11 — `mp_q` (= T/N): if set, Marcenko-Pastur DENOISE the correlation before clustering (LdP-ML §2),
    so the tree isn't built on a mostly-noise matrix. Default None = the original behaviour, unchanged.

    AGORA-38 C11b — `metric` (LdP-ML §3): 'corr' (default, unchanged) clusters on linear correlation; 'nmi'/'vi'
    cluster on nonlinear codependence (`codependence_matrix`) so families that co-move non-monotonically aren't
    mis-seriated as independent. The codependence drives only the TREE TOPOLOGY; the inverse-variance splits
    still use the real return covariance, so sizing is unaffected by the metric choice."""
    names = [k for k, v in returns_by_asset.items() if v and len(v) >= 2]
    if len(names) < 2:
        if not returns_by_asset:
            return {}
        eq = 1.0 / len(returns_by_asset)
        return {k: eq for k in returns_by_asset}
    T = min(len(returns_by_asset[n]) for n in names)
    mat = [list(returns_by_asset[n][-T:]) for n in names]
    cov = _covariance(mat)
    corr = _correlation(cov) if metric == "corr" else codependence_matrix(mat, metric)
    N = len(names)
    if mp_q:
        corr = mp_denoise(corr, mp_q)
    dist = [[(0.5 * max(0.0, 1.0 - corr[i][j])) ** 0.5 for j in range(N)] for i in range(N)]
    order = _quasi_diag(dist)
    w = {i: 1.0 for i in range(N)}
    stack = [order]
    while stack:
        nxt = []
        for c in stack:
            if len(c) <= 1:
                continue
            half = len(c) // 2
            c1, c2 = c[:half], c[half:]
            v1, v2 = _cluster_var(cov, c1), _cluster_var(cov, c2)
            denom = (v1 + v2) or 1.0
            alpha = 1.0 - v1 / denom
            for i in c1:
                w[i] *= alpha
            for i in c2:
                w[i] *= (1.0 - alpha)
            nxt += [c1, c2]
        stack = nxt
    tot = sum(w.values()) or 1.0
    return {names[i]: w[i] / tot for i in range(N)}


# ── Meta-labeling secondary model (López de Prado ch3 §3.6) — pure logistic regression ──

def logistic_fit(X, y, l2=1.0, iters=400, lr=0.3):
    """Tiny L2-regularized logistic regression by batch gradient descent (pure python, no sklearn).
    The meta-label SECONDARY model: it never picks the side (the family does that) — it learns
    P(act | features) on the primary model's realized outcomes, filtering false positives. X = list
    of feature rows (pre-scaled), y = 0/1 labels. Returns weights with w[0] = bias."""
    if not X:
        return []
    d = len(X[0])
    w = [0.0] * (d + 1)
    m = len(X)
    for _ in range(iters):
        g = [0.0] * (d + 1)
        for xi, yi in zip(X, y):
            z = w[0] + sum(w[k + 1] * xi[k] for k in range(d))
            p = 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))
            err = p - yi
            g[0] += err
            for k in range(d):
                g[k + 1] += err * xi[k]
        w[0] -= lr * g[0] / m
        for k in range(d):
            w[k + 1] -= lr * (g[k + 1] / m + l2 * w[k + 1] / m)
    return w


def logistic_predict(w, x):
    """P(act) for one feature row from logistic_fit weights. 0.5 if the model is untrained."""
    if not w:
        return 0.5
    z = w[0] + sum(w[k + 1] * x[k] for k in range(len(x)))
    return 1.0 / (1.0 + math.exp(-max(-30.0, min(30.0, z))))


def safe_factor_eval(expr, features, whitelist=None):
    """Safely evaluate an LLM-proposed cross-sectional factor expression over a feature dict.
    SECURITY-CRITICAL — this is the read-only sandbox between an untrusted model output and the data
    (the factor-research loop, AGORA-33). A whitelisted-AST evaluator: only numeric literals, the named
    features (∈ whitelist), + − × ÷, unary ±, comparisons, and/or, the ternary, and abs/min/max are
    allowed. Attributes, subscripts, ** (pow), calls to anything else, imports, lambdas, comprehensions,
    and non-whitelisted names are REJECTED. Globals carry no builtins. Returns a float, or None on any
    rejection / non-finite / numeric error. Never executes arbitrary code."""
    import ast as A
    funcs = {"abs": abs, "min": min, "max": max}
    names_ok = (set(whitelist) if whitelist is not None else set(features)) | set(funcs)
    try:
        tree = A.parse(expr, mode="eval")
    except Exception:
        return None
    allowed = (A.Expression, A.BinOp, A.UnaryOp, A.Add, A.Sub, A.Mult, A.Div,
               A.USub, A.UAdd, A.Load, A.Call, A.Compare, A.Lt, A.Gt, A.LtE, A.GtE,
               A.Eq, A.NotEq, A.IfExp, A.BoolOp, A.And, A.Or, A.Name, A.Constant)
    for node in A.walk(tree):
        if not isinstance(node, allowed):
            return None
        if isinstance(node, A.Name) and node.id not in names_ok:
            return None
        if isinstance(node, A.Call) and not (isinstance(node.func, A.Name)
                                             and node.func.id in funcs and not node.keywords):
            return None
        if isinstance(node, A.Constant) and not isinstance(node.value, (int, float)):
            return None
    try:
        val = eval(compile(tree, "<factor>", "eval"), {"__builtins__": {}}, {**features, **funcs})
        val = float(val)
        return val if val == val and abs(val) != float("inf") else None
    except Exception:
        return None


def accrual_status(last_seen_ord, today_ord, grace_days=21):
    """Forward-accrual delisting heuristic for the survivorship universe (AGORA-34). A name whose data
    has not been seen for `grace_days` is flagged 'delisted' — the grace window tolerates transient
    feed gaps / holidays so a one-off Yahoo miss doesn't wrongly retire a live name. Returns
    'listed' or 'delisted'. Pure (ordinal-day ints) so it's deterministic and testable."""
    return "delisted" if (today_ord - last_seen_ord) > grace_days else "listed"


def vol_scaled_barriers(sigma_horizon, target_sigmas=1.5, adverse_sigmas=1.0, floor_pct=0.5):
    """Translate a position's horizon volatility σ into triple-barrier thresholds in σ-units (López de
    Prado ch3): a 1.5σ target and 1.0σ stop mean the SAME number of sigmas in calm and storm, so the
    verdict's match/partial/deviation is regime-fair instead of a fixed % that's trivial in a storm and
    unreachable in a calm. sigma_horizon is a fraction (0.04 = 4%). Returns (target_pct, adverse_pct),
    floored so they're never absurdly tight. None if vol is unknown."""
    if sigma_horizon is None or sigma_horizon <= 0:
        return None
    tp = max(floor_pct, round(target_sigmas * sigma_horizon * 100.0, 2))
    ap = max(floor_pct, round(adverse_sigmas * sigma_horizon * 100.0, 2))
    return (tp, ap)


# ─────────────────────────────────────────────────────────────────────────────
# AGORA-31 — synthetic-data backtesting & optimal trading rules (book ch12–13).
# Test a rule across MANY simulated paths instead of the one history that happened, and DERIVE the
# profit-take/stop-loss from the fitted process instead of curve-fitting them. All seeded-deterministic.
# ─────────────────────────────────────────────────────────────────────────────

def ou_fit(prices):
    """Fit a discrete Ornstein–Uhlenbeck (mean-reverting AR(1)) process by OLS (López de Prado ch13):
    P_t = (1−φ)·θ + φ·P_{t−1} + σ·ε. Returns (phi, theta, sigma, r2). 0<φ<1 ⇒ mean-reverting (OTR
    eligible); φ≥1 ⇒ trending / random-walk (ineligible). None if too short or degenerate."""
    n = len(prices)
    if n < 20:
        return None
    x, y = prices[:-1], prices[1:]
    m = len(x)
    mx, my = sum(x) / m, sum(y) / m
    sxx = sum((xi - mx) ** 2 for xi in x)
    if sxx <= 1e-12:
        return None
    phi = sum((x[i] - mx) * (y[i] - my) for i in range(m)) / sxx
    intercept = my - phi * mx
    theta = intercept / (1.0 - phi) if abs(1.0 - phi) > 1e-9 else None
    resid = [y[i] - (intercept + phi * x[i]) for i in range(m)]
    sigma = (sum(r * r for r in resid) / max(1, m - 2)) ** 0.5
    syy = sum((yi - my) ** 2 for yi in y)
    r2 = 1.0 - sum(r * r for r in resid) / syy if syy > 1e-12 else 0.0
    return (round(phi, 6), round(theta, 6) if theta is not None else None, round(sigma, 6), round(r2, 6))


def half_life(phi):
    """Half-life of mean reversion (in periods) from the O-U/AR(1) coefficient: −ln(2)/ln(φ), valid for
    φ ∈ (0,1). None otherwise (no reversion — the name is trending or a random walk)."""
    if phi is None or phi <= 0.0 or phi >= 1.0:
        return None
    return -math.log(2.0) / math.log(phi)


def ou_path(p0, phi, theta, sigma, n, seed=0):
    """Simulate one O-U price path of length n from a seed value (parametric synthetic data)."""
    rng = random.Random(seed)
    out = [p0]
    p = p0
    for _ in range(n - 1):
        p = (1.0 - phi) * theta + phi * p + sigma * rng.gauss(0.0, 1.0)
        out.append(p)
    return out


def optimal_trading_rule(forecast, half_life_, sigma=1.0, max_hp=100, mesh_max=10.0,
                         mesh_steps=8, n_paths=1500, seed=0):
    """Optimal Trading Rule WITHOUT backtesting (López de Prado / Carr ch13). Given an O-U process
    (long-run `forecast`, `half_life_`, σ), Monte-Carlo a mesh of (profit-take, stop-loss) pairs in
    σ-units and return the pair that MAXIMISES the Sharpe of exit P&L — deriving the barriers from the
    process, not curve-fitting them on one history. Common random innovations across cells (variance
    reduction); deterministic for a given seed. Returns dict {best_pt, best_sl, best_sharpe, pct_pt,
    pct_sl, pct_timeout} or None. Defaults trade fidelity for speed (8×8 mesh, 1500 paths, vs the
    book's 21×21 / 1e5) — fine for a weekly cron over a handful of names."""
    if half_life_ is None or half_life_ <= 0:
        return None
    rng = random.Random(seed)
    phi = 2.0 ** (-1.0 / half_life_)
    grid = [mesh_max * i / (mesh_steps - 1) for i in range(1, mesh_steps)]   # exclude 0
    innov = [[rng.gauss(0.0, 1.0) for _ in range(max_hp)] for _ in range(n_paths)]
    best = None
    for pt in grid:
        for sl in grid:
            exits = []
            npt = nsl = nto = 0
            for seq in innov:
                p = 0.0
                hit = None
                for hp in range(max_hp):
                    p = (1.0 - phi) * forecast + phi * p + sigma * seq[hp]
                    if p >= pt:
                        hit = p
                        npt += 1
                        break
                    if p <= -sl:
                        hit = p
                        nsl += 1
                        break
                if hit is None:
                    hit = p
                    nto += 1
                exits.append(hit)
            sr = sharpe(exits)
            if sr is not None and (best is None or sr > best["best_sharpe"]):
                tot = len(exits) or 1
                best = {"best_pt": round(pt, 3), "best_sl": round(sl, 3), "best_sharpe": round(sr, 4),
                        "pct_pt": round(npt / tot, 3), "pct_sl": round(nsl / tot, 3),
                        "pct_timeout": round(nto / tot, 3)}
    return best


def cpcv_path_count(n_groups, k):
    """Number of backtest PATHS from Combinatorial Purged CV (López de Prado ch12): φ = k·C(N,k)/N.
    Each of N groups belongs to exactly φ test sets, so φ full-timeline OOS paths can be stitched —
    a DISTRIBUTION of Sharpe instead of the single path WF/CV give."""
    if n_groups < 2 or k < 1 or k >= n_groups:
        return 0
    return k * math.comb(n_groups, k) // n_groups


def cpcv_splits(n_groups, k):
    """All C(N,k) test-group combinations for CPCV (training set = the complement of each)."""
    import itertools
    if n_groups < 2 or k < 1 or k >= n_groups:
        return []
    return list(itertools.combinations(range(n_groups), k))


def cpcv_paths(n_groups, k):
    """Assign CPCV test groups to the φ reconstructed backtest paths (López de Prado ch12, Fig 12.2).
    Returns φ paths, each a list of (group, split_index) covering all N groups in order — every
    (group, split) test prediction consumed exactly once. The caller computes one Sharpe per path."""
    combos = cpcv_splits(n_groups, k)
    phi = cpcv_path_count(n_groups, k)
    if phi == 0:
        return []
    by_group = {g: [s for s, c in enumerate(combos) if g in c] for g in range(n_groups)}
    return [[(g, by_group[g][p]) for g in range(n_groups)] for p in range(phi)]


def block_bootstrap(returns, n_out=None, mean_block=None, seed=0):
    """Stationary block bootstrap (Politis–Romano 1994): resample a return series in CIRCULAR blocks of
    random GEOMETRIC length (mean = mean_block) to preserve autocorrelation while staying stationary.
    Generates one synthetic 'what-if' series of length n_out from the empirical distribution — no
    parametric assumption, keeps the real fat tails. Default mean block ≈ N^(1/3). Seeded-deterministic."""
    n = len(returns)
    if n < 4:
        return list(returns)
    if n_out is None:
        n_out = n
    if mean_block is None:
        mean_block = max(2.0, n ** (1.0 / 3.0))
    p = 1.0 / mean_block
    rng = random.Random(seed)
    out = []
    while len(out) < n_out:
        i = rng.randrange(n)
        while len(out) < n_out:
            out.append(returns[i])
            if rng.random() < p:
                break
            i = (i + 1) % n
    return out[:n_out]


def consolidate_concurrent(sizes, cap_usd):
    """Cap concurrent bets on the SAME instrument (López de Prado ch10.4 — averaging active bets).
    When several families bet the same name at once, their independently-computed sizes would STACK
    into one oversized position. Scale them proportionally so their TOTAL never exceeds cap_usd (the
    per-name exposure budget), preserving each family's relative conviction. Returns adjusted sizes
    (sum ≤ cap_usd); unchanged when already under budget. The families stay independent experiments —
    only the aggregate exposure to one name is bounded."""
    clean = [s if (s and s > 0) else 0.0 for s in sizes]
    tot = sum(clean)
    if tot <= cap_usd or tot <= 0:
        return clean
    scale = cap_usd / tot
    return [round(s * scale, 2) for s in clean]


def discretize_size(usd, step=50.0):
    """Round a position size to the nearest `step` to stop jitter-trading on trivial rebalances
    (López de Prado ch10.5). Anything below half a step rounds to 0 — not worth a trade."""
    if usd is None or usd <= 0:
        return 0.0
    return round(usd / step) * step


def sharpe_dist_summary(sharpes):
    """Summarise a distribution of per-path Sharpe ratios (CPCV / bootstrap / MC): median, fraction of
    paths profitable (Sharpe>0), and the 5th–95th percentile band. The honest robustness read that one
    historical Sharpe cannot give. None if empty."""
    xs = sorted(s for s in sharpes if s is not None)
    if not xs:
        return None

    def pct(q):
        if len(xs) == 1:
            return xs[0]
        idx = q * (len(xs) - 1)
        lo = int(idx)
        return xs[lo] + (idx - lo) * (xs[min(lo + 1, len(xs) - 1)] - xs[lo])

    return {"median": round(pct(0.5), 4), "pct_profitable": round(sum(1 for s in xs if s > 0) / len(xs), 4),
            "p5": round(pct(0.05), 4), "p95": round(pct(0.95), 4), "n_paths": len(xs)}


# ── AGORA-37 P11 — forecast CALIBRATION (does a stated confidence mean what it says?) ────────────────
def brier_score(probs, outcomes):
    """Mean squared error of probabilistic forecasts; `outcomes` in [0,1] (1=right, 0=wrong, 0.5=partial).
    0 = perfect, 0.25 = always-say-0.5, → worse as forecasts miss. None if empty."""
    p, o = list(probs), list(outcomes)
    if not p:
        return None
    return sum((pi - oi) ** 2 for pi, oi in zip(p, o)) / len(p)


def reliability_curve(probs, outcomes, n_bins=10):
    """Per confidence bin: (bin_lo, bin_hi, mean_predicted, mean_observed, count) for NON-empty bins. A
    calibrated forecaster sits on the diagonal: mean_observed ≈ mean_predicted in every bin."""
    bins = [[] for _ in range(n_bins)]
    for pi, oi in zip(probs, outcomes):
        b = min(n_bins - 1, max(0, int(pi * n_bins)))
        bins[b].append((pi, oi))
    out = []
    for i, b in enumerate(bins):
        if b:
            out.append((i / n_bins, (i + 1) / n_bins,
                        sum(x[0] for x in b) / len(b), sum(x[1] for x in b) / len(b), len(b)))
    return out


def expected_calibration_error(probs, outcomes, n_bins=10):
    """Count-weighted mean |mean_predicted − mean_observed| across confidence bins (ECE). 0 = calibrated."""
    n = len(probs)
    if not n:
        return None
    return sum(cnt * abs(mp - mo) for _, _, mp, mo, cnt in reliability_curve(probs, outcomes, n_bins)) / n


def calibration_in_the_large(probs, outcomes):
    """Overall over/under-confidence: mean(predicted) − mean(observed). >0 ⇒ systematically OVERCONFIDENT
    (shrink the model's stated confidence); <0 ⇒ underconfident. None if empty."""
    if not probs or not outcomes:
        return None
    return sum(probs) / len(probs) - sum(outcomes) / len(outcomes)


# ── AGORA-38 C1 — compliance primitives: HAC inference, cointegration, info-theory, optimal-f ────────
# (pure stdlib; the eigendecomposition cluster — mp_denoise/detone/onc_clusters/mda — ships with C11)
def _matinv(A):
    """Inverse of a small square matrix via Gauss-Jordan with partial pivoting. None if singular."""
    n = len(A)
    M = [list(A[i]) + [1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-13:
            return None
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]; M[c] = [v / piv for v in M[c]]
        for r in range(n):
            if r != c:
                f = M[r][c]
                M[r] = [M[r][j] - f * M[c][j] for j in range(2 * n)]
    return [row[n:] for row in M]


def _ols_full(X, y):
    """OLS with t-stats. X = rows of regressors (include your own intercept column). Returns
    (coefs, tstats, ssr) or None. SE_j from σ²·(XᵀX)⁻¹; t_j = coef_j/SE_j."""
    n = len(X)
    if n == 0 or n <= len(X[0]):
        return None
    k = len(X[0])
    XtX = [[sum(X[i][a] * X[i][b] for i in range(n)) for b in range(k)] for a in range(k)]
    Xty = [sum(X[i][a] * y[i] for i in range(n)) for a in range(k)]
    inv = _matinv(XtX)
    if inv is None:
        return None
    coef = [sum(inv[a][b] * Xty[b] for b in range(k)) for a in range(k)]
    ssr = sum((y[i] - sum(coef[a] * X[i][a] for a in range(k))) ** 2 for i in range(n))
    sigma2 = ssr / (n - k)
    tstats = [(coef[j] / math.sqrt(sigma2 * inv[j][j]) if (inv[j][j] > 0 and sigma2 > 1e-300) else 0.0)
              for j in range(k)]
    return coef, tstats, ssr


def newey_west_tstat(series, lags=None):
    """HAC (Newey-West, Bartlett-kernel) t-stat that the per-period MEAN of `series` is zero — the standard
    cross-section-literature inference, robust to autocorrelation + heteroskedasticity (BEM Ch.1 §1.3).
    `lags` default = floor(4·(T/100)^(2/9)). Returns (mean, tstat)."""
    x = [float(v) for v in series]
    T = len(x)
    if T < 3:
        return (sum(x) / T if T else 0.0), 0.0
    mu = sum(x) / T
    e = [v - mu for v in x]
    if lags is None:
        lags = int(4 * (T / 100.0) ** (2.0 / 9.0))
    s = sum(v * v for v in e) / T
    for L in range(1, max(0, lags) + 1):
        w = 1.0 - L / (lags + 1.0)
        s += 2.0 * w * sum(e[t] * e[t - L] for t in range(L, T)) / T
    var_mean = s / T
    return mu, (mu / math.sqrt(var_mean) if var_mean > 1e-18 else 0.0)


def _chi2_crit(dof, p=0.95):
    """Upper-(1-p) chi-square critical value via Wilson-Hilferty (pure-stdlib, accurate for dof≥1)."""
    if dof <= 0:
        return 0.0
    z = _N.inv_cdf(p)
    return dof * (1.0 - 2.0 / (9.0 * dof) + z * math.sqrt(2.0 / (9.0 * dof))) ** 3


def ljung_box(residuals, lags=10):
    """Ljung-Box portmanteau Q-stat for residual autocorrelation up to `lags` (Hyndman §2.9/§5.4).
    Returns (Q, dof, white_ok) — white_ok = Q below the 5% chi²(dof) crit (no significant autocorrelation)."""
    x = [float(v) for v in residuals]
    T = len(x)
    lags = min(lags, T - 1)
    if T < 4 or lags < 1:
        return 0.0, 0, True
    mu = sum(x) / T
    d = sum((v - mu) ** 2 for v in x)
    Q = 0.0
    for k in range(1, lags + 1):
        rk = (sum((x[t] - mu) * (x[t - k] - mu) for t in range(k, T)) / d) if d > 0 else 0.0
        Q += rk * rk / (T - k)
    Q *= T * (T + 2)
    return Q, lags, Q < _chi2_crit(lags)


def fama_macbeth(daily, nw_lags=None):
    """Fama-MacBeth two-pass (BEM Ch.6): `daily` = list of (X_rows, y) per period — X_rows are the regressors
    WITHOUT an intercept (one is added). Per period OLS y~[1,X]; average each slope across periods; HAC t-stat
    on the per-period slope series. Returns [(mean_slope, nw_tstat), …] per regressor (intercept excluded)."""
    slopes = []
    for X, y in daily:
        if not X or len(X) <= len(X[0]) + 1:
            continue
        res = _ols_full([[1.0] + list(r) for r in X], list(y))
        if res:
            slopes.append(res[0])
    if not slopes:
        return []
    return [newey_west_tstat([s[j] for s in slopes], nw_lags) for j in range(1, len(slopes[0]))]


def adf(series, lags=1):
    """Augmented Dickey-Fuller t-stat on the lagged-level coefficient (H0: unit root = non-stationary).
    Regress Δyₜ on [1, yₜ, Δyₜ₋₁…Δyₜ₋ₗ]; (stat, is_stationary) with stat < −2.86 (≈5% MacKinnon, constant)."""
    y = [float(v) for v in series]
    T = len(y)
    if T < lags + 6:
        return 0.0, False
    dy = [y[t] - y[t - 1] for t in range(1, T)]
    rows, tgt = [], []
    for t in range(lags, len(dy)):
        rows.append([1.0, y[t]] + [dy[t - j] for j in range(1, lags + 1)])
        tgt.append(dy[t])
    res = _ols_full(rows, tgt)
    if not res:
        return 0.0, False
    stat = res[1][1]
    return stat, stat < -2.86


def cadf(y, x, lags=1):
    """Engle-Granger cointegration: OLS y~[1,x], then ADF the residual (Chan Ch.2). (stat, is_cointegrated)
    with the residual-based 5% crit ≈ −3.34 (more negative than plain ADF because the spread was estimated)."""
    y = [float(v) for v in y]; x = [float(v) for v in x]
    n = min(len(y), len(x))
    if n < lags + 8:
        return 0.0, False
    res = _ols_full([[1.0, x[i]] for i in range(n)], y[:n])
    if not res:
        return 0.0, False
    a, b = res[0][0], res[0][1]
    stat, _ = adf([y[i] - a - b * x[i] for i in range(n)], lags)
    return stat, stat < -3.34


def variance_ratio(series, k=2):
    """Lo-MacKinlay variance ratio: Var(k-period diff)/(k·Var(1-period diff)) of `series`. ≈1 random walk,
    <1 mean-reverting, >1 trending. Returns (vr, z) with the homoskedastic z-stat. (Chan Ch.2)"""
    p = [float(v) for v in series]
    T = len(p)
    if T < 2 * k + 2 or k < 2:
        return 1.0, 0.0
    r = [p[t] - p[t - 1] for t in range(1, T)]
    n = len(r)
    mu = sum(r) / n
    var1 = sum((v - mu) ** 2 for v in r) / (n - 1)
    kr = [sum(r[t - j] for j in range(k)) for t in range(k - 1, n)]
    m = k * (n - k + 1) * (1.0 - k / n)                              # Lo-MacKinlay overlapping-estimator correction
    vark = (sum((v - k * mu) ** 2 for v in kr) / m) if m > 0 else 0.0   # σ²_c: the per-period k-variance
    vr = (vark / var1) if var1 > 0 else 1.0                          # VR = σ²_c / σ²_a (≈1 under a random walk)
    phi = 2.0 * (2 * k - 1) * (k - 1) / (3.0 * k * n)
    return vr, ((vr - 1.0) / math.sqrt(phi) if phi > 0 else 0.0)


def hurst(series, max_lag=20):
    """Hurst exponent via the slope of log(std of L-lag differences) vs log(L). ≈0.5 random walk, <0.5
    mean-reverting, >0.5 persistent/trending. (Chan Ch.2)"""
    x = [float(v) for v in series]
    T = len(x)
    max_lag = min(max_lag, T // 2)
    if max_lag < 4:
        return 0.5
    tau, ll = [], []
    for L in range(2, max_lag):
        d = [x[t] - x[t - L] for t in range(L, T)]
        if len(d) < 2:
            continue
        mu = sum(d) / len(d)
        sd = math.sqrt(sum((v - mu) ** 2 for v in d) / len(d))
        if sd > 0:
            tau.append(math.log(sd)); ll.append(math.log(L))
    if len(tau) < 3:
        return 0.5
    res = _ols_full([[1.0, l] for l in ll], tau)
    return res[0][1] if res else 0.5


def monte_carlo_optimal_f(returns, n_paths=1000, horizon=None, seed=0, f_grid=None):
    """Chan Ch.8: growth-optimal leverage f by Monte-Carlo over the EMPIRICAL return distribution (keeps
    fat tails/skew a Gaussian Kelly ignores). Picks f maximising median terminal log-growth Σlog(1+f·R);
    a path that would be ruined (1+f·R≤0) scores −inf. Returns (best_f, median_log_growth)."""
    r = [float(v) for v in returns if v is not None]
    if len(r) < 10:
        return 0.0, 0.0
    horizon = min(horizon or len(r), 504)
    f_grid = f_grid or [i / 20.0 for i in range(1, 21)]
    rng = random.Random(seed)
    best = (0.0, -1e18)
    for f in f_grid:
        growths = []
        for _ in range(n_paths):
            g, ruined = 0.0, False
            for _ in range(horizon):
                m = 1.0 + f * r[rng.randrange(len(r))]
                if m <= 0:
                    ruined = True; break
                g += math.log(m)
            growths.append(-1e18 if ruined else g)
        growths.sort()
        med = growths[len(growths) // 2]
        if med > best[1]:
            best = (f, med)
    return best


def trend_scanning_labels(prices, spans=(5, 10, 21)):
    """López de Prado trend-scanning labels (LdP-ML §5): for each t pick the look-forward span whose
    price~time slope is most significant (max |t-stat|), label = sign(slope) ∈ {−1,0,+1}. A LABELING tool
    (uses the future) for research — never a live feature."""
    p = [float(v) for v in prices]
    T = len(p)
    labels = [0] * T
    for t in range(T):
        best_abs, lab = 0.0, 0
        for L in spans:
            if t + L >= T:
                continue
            seg = p[t:t + L + 1]
            res = _ols_full([[1.0, float(i)] for i in range(len(seg))], seg)
            if res and abs(res[1][1]) > best_abs:
                best_abs = abs(res[1][1]); lab = 1 if res[0][1] > 0 else -1
        labels[t] = lab
    return labels


def _eqfreq_bins(v, b):
    """Equal-frequency (quantile) bin labels 0..b-1 for a list of values."""
    order = sorted(range(len(v)), key=lambda i: v[i])
    lab = [0] * len(v)
    for rank, i in enumerate(order):
        lab[i] = min(b - 1, rank * b // len(v))
    return lab


def _entropy(counts, n):
    return -sum((c / n) * math.log(c / n) for c in counts if c > 0)


def _mi_terms(x, y, bins):
    from collections import Counter
    n = min(len(x), len(y))
    b = bins or max(2, int(round(n ** (1.0 / 3.0))))
    bx = _eqfreq_bins([float(v) for v in x[:n]], b); by = _eqfreq_bins([float(v) for v in y[:n]], b)
    hx = _entropy(Counter(bx).values(), n); hy = _entropy(Counter(by).values(), n)
    hxy = _entropy(Counter(zip(bx, by)).values(), n)
    return hx, hy, hxy, (hx + hy - hxy)


def normalized_mutual_info(x, y, bins=None):
    """NMI ∈ [0,1] via equal-frequency binning — a NONLINEAR codependence measure (LdP-ML §3) linear
    correlation misses. 0 = independent, 1 = identical information."""
    if min(len(x), len(y)) < 4:
        return 0.0
    hx, hy, _, mi = _mi_terms(x, y, bins)
    denom = math.sqrt(hx * hy)
    return max(0.0, min(1.0, mi / denom)) if denom > 1e-12 else 0.0


def variation_of_information(x, y, bins=None):
    """Variation of information VI = H(X,Y) − I(X;Y), a true METRIC distance (LdP-ML §3), normalized by
    H(X,Y) into [0,1]: 0 = identical, 1 = independent. Usable as a nonlinear clustering distance."""
    if min(len(x), len(y)) < 4:
        return 1.0
    _, _, hxy, mi = _mi_terms(x, y, bins)
    return max(0.0, min(1.0, (hxy - mi) / hxy)) if hxy > 1e-12 else 0.0


def codependence_matrix(mat, metric="corr", bins=None):
    """Build an N×N codependence matrix from `mat` (mat[i] = the series of variable i) expressed on the
    SAME [−1,1] correlation scale that `_quasi_diag`/`hrp_weights`/`onc_clusters` already consume — so a
    NONLINEAR codependence (López de Prado, ML for Asset Managers §3) is a drop-in replacement for linear
    correlation wherever a correlation matrix feeds clustering / seriation.

      metric='corr' : Pearson correlation (linear; the default — identical to `_correlation(_covariance(·))`).
      metric='nmi'  : normalized mutual information, mapped 2·NMI−1 → [−1,1] (identical info → +1, independent
                      → −1). Chosen so the downstream distance √(½(1−c)) reduces to √(1−NMI): 0 when identical.
      metric='vi'   : variation of information, mapped 1−2·VI → [−1,1] (VI=0 identical → +1, VI=1 independent
                      → −1); downstream distance √(½(1−c)) = √VI, monotone in the true VI metric.

    NMI/VI capture monotone AND non-monotone dependence that Pearson misses (the φ-audit's CCA is also linear),
    at the cost of binning resolution. Symmetric, unit diagonal. Pure-stdlib; reuses the C1 MI primitives."""
    if metric == "corr":
        return _correlation(_covariance(mat))
    if metric not in ("nmi", "vi"):
        raise ValueError(f"codependence_matrix: unknown metric {metric!r}")
    n = len(mat)
    out = [[1.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            if metric == "nmi":
                c = 2.0 * normalized_mutual_info(mat[i], mat[j], bins) - 1.0
            else:  # vi
                c = 1.0 - 2.0 * variation_of_information(mat[i], mat[j], bins)
            out[i][j] = out[j][i] = c
    return out


# ── AGORA-38 C9 — forecast evaluation (Hyndman §5.2/§5.8/§5.9): skill, MASE, interval scoring ─────────
def rw_skill_score(actual, predicted):
    """Skill vs the random-walk (persistence) benchmark: 1 − MSE(model)/MSE(naive), naive = previous actual.
    >0 beats persistence, ≤0 doesn't (Hyndman §5.2 — naive is usually best for stock prices). None if short."""
    a = [float(v) for v in actual]; p = [float(v) for v in predicted]
    n = min(len(a), len(p))
    if n < 2:
        return None
    mse_m = sum((a[i] - p[i]) ** 2 for i in range(n)) / n
    mse_n = sum((a[i] - a[i - 1]) ** 2 for i in range(1, n)) / (n - 1)
    return (1.0 - mse_m / mse_n) if mse_n > 0 else None


def mase(actual, predicted, train_actual=None, m=1):
    """Mean Absolute Scaled Error (Hyndman §5.8): MAE / naive-MAE on the training series (or the actuals).
    MASE ≥ 1 ⇒ no skill over the naive m-step forecast — a cheap, scale-free 'is there any skill?' pre-gate
    that avoids MAPE's div-by-zero. None if degenerate."""
    a = [float(v) for v in actual]; p = [float(v) for v in predicted]
    base = [float(v) for v in (train_actual if train_actual is not None else a)]
    n = min(len(a), len(p))
    if n < 1 or len(base) <= m:
        return None
    scale = sum(abs(base[t] - base[t - m]) for t in range(m, len(base))) / (len(base) - m)
    return (sum(abs(a[i] - p[i]) for i in range(n)) / n) / scale if scale > 1e-18 else None


def winkler_score(actual, lo, hi, alpha=0.2):
    """Winkler interval score for a (1−α) prediction interval (Hyndman §5.9): the width + a 2/α penalty per
    actual outside the interval. Lower is better; rewards SHARP intervals that still cover. None if empty."""
    a, l, h = [float(v) for v in actual], [float(v) for v in lo], [float(v) for v in hi]
    n = min(len(a), len(l), len(h))
    if n < 1:
        return None
    s = 0.0
    for i in range(n):
        w = h[i] - l[i]
        s += w + (2.0 / alpha) * (l[i] - a[i] if a[i] < l[i] else (a[i] - h[i] if a[i] > h[i] else 0.0))
    return s / n


def interval_coverage(actual, lo, hi):
    """Empirical coverage: fraction of actuals inside [lo,hi]. A calibrated (1−α) interval covers ≈(1−α)
    (Hyndman §5.9) — the shape-calibration DUAL of the scalar-confidence calibration (C11/P11). None if empty."""
    a, l, h = [float(v) for v in actual], [float(v) for v in lo], [float(v) for v in hi]
    n = min(len(a), len(l), len(h))
    return (sum(1 for i in range(n) if l[i] <= a[i] <= h[i]) / n) if n else None


def pinball_loss(actual, q_pred, q):
    """Pinball (quantile) loss at quantile q (Hyndman §5.9): the asymmetric penalty minimized by the true
    q-quantile. Lower is better. None if empty."""
    a, p = [float(v) for v in actual], [float(v) for v in q_pred]
    n = min(len(a), len(p))
    if n < 1:
        return None
    return sum((q * (a[i] - p[i]) if a[i] >= p[i] else (1.0 - q) * (p[i] - a[i])) for i in range(n)) / n


# ── AGORA-61 R4 — proper scoring for the RAG forward lane (CRPS + Murphy/isotonic) ───────────────────
def crps_sample(samples, y):
    """Continuous Ranked Probability Score of an ENSEMBLE/sample forecast {x_i} vs observation y (Gneiting &
    Raftery): CRPS = mean|x_i − y| − ½·mean|x_i − x_j|. A strictly proper score that generalises MAE to a full
    predictive distribution (lower = better). Pure O(n²). None if empty."""
    x = [float(v) for v in samples]
    n = len(x)
    if n < 1:
        return None
    y = float(y)
    term1 = sum(abs(xi - y) for xi in x) / n
    term2 = sum(abs(x[i] - x[j]) for i in range(n) for j in range(n)) / (2.0 * n * n)
    return term1 - term2


def murphy_brier_decomposition(probs, outcomes, bins=10):
    """Murphy (1973) decomposition of the Brier score into Reliability − Resolution + Uncertainty over `bins`
    forecast-probability bins. Reliability (calibration; lower better), Resolution (discrimination; higher
    better), Uncertainty (base-rate variance, irreducible). Returns a dict; the three reconstruct Brier
    (rel − res + unc) up to binning. None if too few points."""
    p = [min(1.0, max(0.0, float(v))) for v in probs]
    o = [1.0 if v else 0.0 for v in outcomes]
    n = min(len(p), len(o))
    if n < 2:
        return None
    obar = sum(o[:n]) / n
    rel = res = 0.0
    for b in range(bins):
        lo, hi = b / bins, (b + 1) / bins
        idx = [i for i in range(n) if (lo <= p[i] < hi) or (b == bins - 1 and p[i] == 1.0)]
        if not idx:
            continue
        nk = len(idx)
        fk = sum(p[i] for i in idx) / nk
        ok = sum(o[i] for i in idx) / nk
        rel += nk * (fk - ok) ** 2
        res += nk * (ok - obar) ** 2
    return {"reliability": round(rel / n, 6), "resolution": round(res / n, 6),
            "uncertainty": round(obar * (1.0 - obar), 6),
            "brier_reconstructed": round(rel / n - res / n + obar * (1.0 - obar), 6)}


def isotonic_fit(x, y):
    """Isotonic (monotone non-decreasing) regression via Pool-Adjacent-Violators (PAVA) — recalibrates raw
    scores `x` to outcomes `y` for a reliability curve / calibration map. Returns the fitted values aligned to
    x sorted ascending: [(x_sorted, y_fitted)], non-decreasing in y_fitted. Pure stdlib."""
    pairs = sorted(zip([float(v) for v in x], [float(v) for v in y]))
    if not pairs:
        return []
    xs = [a for a, _ in pairs]
    # PAVA: blocks of (sum, weight, value)
    blocks = [[b, 1.0, b] for _, b in pairs]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][2] > blocks[i + 1][2]:                    # violation → pool with the next block
            s = blocks[i][0] + blocks[i + 1][0]
            w = blocks[i][1] + blocks[i + 1][1]
            blocks[i:i + 2] = [[s, w, s / w]]
            if i > 0:
                i -= 1                                         # back up — pooling may have created a new violation
        else:
            i += 1
    fitted = []
    for blk in blocks:
        fitted.extend([blk[2]] * int(blk[1]))
    return list(zip(xs, fitted))


def residual_car(asset_ret, bench_ret, event_ix, est_window=120, gap=5, horizons=(1, 3, 5, 21)):
    """Market-model cumulative ABNORMAL return for the RAG forward lane (AGORA-61 R4; event-study upgrade to the
    raw realized-vs-benchmark verdict). OLS-estimate (alpha, beta) of the asset on the benchmark over an
    ESTIMATION window ending `gap` days BEFORE `event_ix` (the gap avoids pre-event contamination), then
    CAR_h = Σ_{t=event..event+h−1} (r_asset,t − (alpha + beta·r_bench,t)). Returns {h: CAR} or None
    (FAIL-CLOSED) when the clean pre-event window is too short / degenerate. Additive — the locked verdict
    contract is unchanged; this is the abnormal-return scorer it can call. Pure."""
    n = min(len(asset_ret), len(bench_ret))
    est_end = event_ix - gap
    est_start = est_end - est_window
    if est_start < 0 or (est_end - est_start) < 20 or event_ix >= n:
        return None                                            # fail-closed: insufficient clean estimation window
    xs = bench_ret[est_start:est_end]
    ys = asset_ret[est_start:est_end]
    m = len(xs)
    mx = sum(xs) / m
    my = sum(ys) / m
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx < 1e-12:
        return None                                            # benchmark has no variance → β undefined
    beta = sum((xs[i] - mx) * (ys[i] - my) for i in range(m)) / sxx
    alpha = my - beta * mx
    out = {}
    for h in horizons:
        if event_ix + h > n:
            continue
        out[h] = round(sum(asset_ret[event_ix + t] - (alpha + beta * bench_ret[event_ix + t]) for t in range(h)), 6)
    return out or None


# ── AGORA-38 C11 — LdP-ML matrix layer (§2/§6): MP denoising, detoning, MDA importance (pure, Jacobi) ──
def _jacobi_eigen(A, max_sweeps=100, tol=1e-12):
    """Eigenvalues + eigenvectors of a small SYMMETRIC matrix via cyclic Jacobi rotations (pure stdlib).
    Returns (eigvals, eigvecs) with eigvecs[i][k] = i-th component of the k-th eigenvector. For N ≲ 60."""
    n = len(A)
    M = [list(r) for r in A]
    V = [[1.0 if i == j else 0.0 for j in range(n)] for i in range(n)]
    for _ in range(max_sweeps):
        off = math.sqrt(sum(M[p][q] ** 2 for p in range(n) for q in range(p + 1, n)))
        if off < tol:
            break
        for p in range(n):
            for q in range(p + 1, n):
                if abs(M[p][q]) < 1e-300:
                    continue
                theta = (M[q][q] - M[p][p]) / (2.0 * M[p][q])
                t = (1.0 if theta >= 0 else -1.0) / (abs(theta) + math.sqrt(theta * theta + 1.0))
                c = 1.0 / math.sqrt(t * t + 1.0); s = t * c
                for k in range(n):                          # rotate rows p,q
                    a, b = M[p][k], M[q][k]
                    M[p][k] = c * a - s * b; M[q][k] = s * a + c * b
                for k in range(n):                          # rotate cols p,q
                    a, b = M[k][p], M[k][q]
                    M[k][p] = c * a - s * b; M[k][q] = s * a + c * b
                for k in range(n):                          # accumulate eigenvectors
                    a, b = V[k][p], V[k][q]
                    V[k][p] = c * a - s * b; V[k][q] = s * a + c * b
    return [M[i][i] for i in range(n)], V


def _reconstruct_corr(vals, vecs, use):
    n = len(vals)
    C = [[sum(vecs[i][k] * vals[k] * vecs[j][k] for k in use) for j in range(n)] for i in range(n)]
    d = [math.sqrt(C[i][i]) if C[i][i] > 1e-12 else 1.0 for i in range(n)]
    return [[C[i][j] / (d[i] * d[j]) for j in range(n)] for i in range(n)]


def mp_denoise(corr, q):
    """Marcenko-Pastur denoising (LdP-ML §2): eigenvalues below λ₊=(1+√(1/q))² are NOISE — replace them all
    with their average (preserving the trace), keep the signal eigenvalues, re-normalise to unit diagonal.
    q = T/N (observations / variables); higher q ⇒ less noise. The highest-leverage cleanup before HRP /
    distance / optimisation (a raw sample correlation is mostly noise). Pure (Jacobi)."""
    n = len(corr)
    if n < 2 or q <= 0:
        return [list(r) for r in corr]
    vals, vecs = _jacobi_eigen(corr)
    lam_plus = (1.0 + math.sqrt(1.0 / q)) ** 2
    keep = [i for i in range(n) if vals[i] > lam_plus] or [max(range(n), key=lambda i: vals[i])]
    noise = [i for i in range(n) if i not in keep]
    nv = list(vals)
    if noise:
        avg = sum(vals[i] for i in noise) / len(noise)
        for i in noise:
            nv[i] = avg
    return _reconstruct_corr(nv, vecs, range(n))


def detone(corr, n_market=1):
    """Remove the top `n_market` (market) eigenvector(s) from a correlation matrix (LdP-ML §2), so clustering/
    distance isn't dominated by the single market factor. Re-normalised to unit diagonal. Pure."""
    n = len(corr)
    if n < 2 or n_market < 1:
        return [list(r) for r in corr]
    vals, vecs = _jacobi_eigen(corr)
    top = set(sorted(range(n), key=lambda i: vals[i], reverse=True)[:n_market])
    return _reconstruct_corr(vals, vecs, [i for i in range(n) if i not in top])


def mda_importance(X, y, score_fn, n_shuffle=5, seed=0):
    """Mean-Decrease-Accuracy feature importance (LdP-ML §6): for each feature, shuffle its column and measure
    the DROP in `score_fn(X, y)` (an IC/accuracy/etc.). Substitution-robust vs the in-sample MDI. Returns the
    mean score-drop per feature (higher = more important). `X` = list of rows. Pure given score_fn."""
    base = score_fn(X, y)
    n = len(X)
    p = len(X[0]) if n else 0
    rng = random.Random(seed)
    out = []
    for f in range(p):
        col = [X[i][f] for i in range(n)]
        drops = []
        for _ in range(n_shuffle):
            perm = col[:]; rng.shuffle(perm)
            Xs = [list(X[i]) for i in range(n)]
            for i in range(n):
                Xs[i][f] = perm[i]
            drops.append(base - score_fn(Xs, y))
        out.append(sum(drops) / len(drops))
    return out


def _mean_silhouette(dist, labels):
    """Mean silhouette of a clustering over a distance matrix: per point, (b−a)/max(a,b) with a = mean intra-
    cluster distance, b = min mean distance to any OTHER cluster. In [−1,1]; higher = better-separated clusters."""
    n = len(dist)
    members = {}
    for i, lab in enumerate(labels):
        members.setdefault(lab, []).append(i)
    sils = []
    for i in range(n):
        own = members[labels[i]]
        if len(own) <= 1:
            sils.append(0.0); continue
        a = sum(dist[i][j] for j in own if j != i) / (len(own) - 1)
        others = [sum(dist[i][j] for j in members[l]) / len(members[l]) for l in members if l != labels[i]]
        b = min(others) if others else 0.0
        sils.append(((b - a) / max(a, b)) if max(a, b) > 1e-12 else 0.0)
    return sum(sils) / n if sils else 0.0


def onc_clusters(corr, k_max=None):
    """Optimal Number of Clusters (López de Prado, ML for Asset Managers §4): seriate the correlation-distance
    matrix via single-linkage (the ch16 quasi-diagonalisation), cut the order into k contiguous blocks for
    k=2..k_max, and pick the k with the best MEAN SILHOUETTE (cluster quality). Returns (labels, k, silhouette).
    Pure — reuses `_quasi_diag`. Denoise the correlation first (`mp_denoise`) for a cleaner partition."""
    n = len(corr)
    if n < 3:
        return [0] * n, 1, 0.0
    dist = [[math.sqrt(max(0.0, 0.5 * (1.0 - corr[i][j]))) for j in range(n)] for i in range(n)]
    order = _quasi_diag(dist)
    k_max = max(2, min(k_max or n // 2, n - 1))
    best = (list(range(n)), 1, -1.0)
    for k in range(2, k_max + 1):
        labels = [0] * n
        bnd = [round(b * n / k) for b in range(k + 1)]
        for ci in range(k):
            for pos in range(bnd[ci], bnd[ci + 1]):
                labels[order[pos]] = ci
        sil = _mean_silhouette(dist, labels)
        if sil > best[2]:
            best = (labels, k, sil)
    return best[0], best[1], round(best[2], 4)
