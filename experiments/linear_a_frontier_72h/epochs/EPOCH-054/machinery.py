#!/usr/bin/env python3
"""
EPOCH-054 machinery: Benford's Law fitter for Linear A numeral magnitudes.

L2/L3 structural statistics. Magnitudes only. No sign values / readings.

Benford first-digit: P(d) = log10(1 + 1/d), d in 1..9.
Nigrini MAD conformity bands:
    MAD < 0.006        -> close
    0.006 <= MAD < 0.012 -> acceptable
    0.012 <= MAD < 0.015 -> marginal
    MAD >= 0.015       -> nonconformant
"""
import json
import math
from collections import Counter

BENFORD = {d: math.log10(1 + 1.0 / d) for d in range(1, 10)}


def first_digits(magnitudes):
    """Return list of first digits for positive integer magnitudes."""
    out = []
    for v in magnitudes:
        if v < 1:
            continue
        out.append(int(str(abs(int(v)))[0]))
    return out


def first_digit_hist(magnitudes):
    fd = first_digits(magnitudes)
    c = Counter(fd)
    return {str(d): c.get(d, 0) for d in range(1, 10)}


def benford_mad(magnitudes):
    """Mean absolute deviation of observed vs Benford first-digit proportions."""
    fd = first_digits(magnitudes)
    n = len(fd)
    if n == 0:
        return float("nan")
    c = Counter(fd)
    mad = 0.0
    for d in range(1, 10):
        obs = c.get(d, 0) / n
        mad += abs(obs - BENFORD[d])
    return mad / 9.0


def nigrini_band(mad):
    if mad < 0.006:
        return "close"
    if mad < 0.012:
        return "acceptable"
    if mad < 0.015:
        return "marginal"
    return "nonconformant"


def chi_square_benford(magnitudes):
    """Chi-square GoF vs Benford, df=8. Returns (chi2, p)."""
    fd = first_digits(magnitudes)
    n = len(fd)
    if n == 0:
        return (float("nan"), float("nan"))
    c = Counter(fd)
    chi2 = 0.0
    for d in range(1, 10):
        exp = BENFORD[d] * n
        obs = c.get(d, 0)
        chi2 += (obs - exp) ** 2 / exp
    # p-value via survival of chi2 with df=8 using regularized upper incomplete gamma
    p = chi2_sf(chi2, 8)
    return (chi2, p)


def _lgamma(x):
    return math.lgamma(x)


def _gammainc_series(a, x):
    """Lower regularized gamma P(a,x) via series (x < a+1)."""
    if x <= 0:
        return 0.0
    ap = a
    s = 1.0 / a
    term = s
    for _ in range(1000):
        ap += 1
        term *= x / ap
        s += term
        if abs(term) < abs(s) * 1e-14:
            break
    return s * math.exp(-x + a * math.log(x) - _lgamma(a))


def _gammainc_cf(a, x):
    """Upper regularized gamma Q(a,x) via continued fraction (x >= a+1)."""
    # Lentz's algorithm
    tiny = 1e-300
    b = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b
    h = d
    for i in range(1, 1000):
        an = -i * (i - a)
        b += 2.0
        d = an * d + b
        if abs(d) < tiny:
            d = tiny
        c = b + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    return h * math.exp(-x + a * math.log(x) - _lgamma(a))


def chi2_sf(chi2, df):
    """Survival function P(X > chi2) for chi-square with df degrees of freedom."""
    if chi2 <= 0:
        return 1.0
    a = df / 2.0
    x = chi2 / 2.0
    if x < a + 1.0:
        return 1.0 - _gammainc_series(a, x)
    else:
        return _gammainc_cf(a, x)


def classify(magnitudes):
    """Frozen LA classification thresholds."""
    mad = benford_mad(magnitudes)
    chi2, p = chi_square_benford(magnitudes)
    if mad <= 0.012 or p > 0.05:
        cls = "CONSISTENT"
    elif mad > 0.015 and p < 0.01:
        cls = "DEVIANT"
    else:
        cls = "INCONCLUSIVE"
    return {
        "mad": mad,
        "nigrini_band": nigrini_band(mad),
        "chi2": chi2,
        "chi2_p": p,
        "classification": cls,
    }


# ---------- Positive controls ----------

def _synth_benford(n, rng, lo=1, hi=3000):
    """Sample n magnitudes whose first digits are Benford-distributed.
    Mantissa method: 10^U where U ~ Uniform[0,3) gives Benford first digits over a wide range."""
    import random
    out = []
    while len(out) < n:
        u = rng.random() * 3.0  # log10 span ~ 3 decades -> up to 1000; extend to 3000
        val = int(10 ** u)
        if 1 <= val <= hi:
            out.append(val)
    return out


def _synth_uniform(n, rng, lo=1, hi=3000):
    return [rng.randint(lo, hi) for _ in range(n)]


def positive_control(n_la=1276, draws=20, seed=20240517):
    """Returns dict with pc_verdict, benford_synth_conformant, uniform_synth_nonconformant, false_deviant_rate."""
    import random
    rng = random.Random(seed)

    # (a) DETECT both directions
    ben_synth = _synth_benford(n_la, rng)
    uni_synth = _synth_uniform(n_la, rng)
    ben_cls = classify(ben_synth)
    uni_cls = classify(uni_synth)
    ben_conformant = ben_cls["classification"] == "CONSISTENT"
    uni_nonconformant = uni_cls["classification"] == "DEVIANT"

    # (b) FP: false 'deviant' rate on true-Benford samples
    false_dev = 0
    for _ in range(draws):
        s = _synth_benford(n_la, rng)
        c = classify(s)
        if c["classification"] == "DEVIANT":
            false_dev += 1
    fdr = false_dev / draws

    detect_ok = ben_conformant and uni_nonconformant
    fp_ok = fdr <= 0.10
    pc_verdict = "PASSED" if (detect_ok and fp_ok) else "FAILED"
    return {
        "pc_verdict": pc_verdict,
        "benford_synth_conformant": ben_conformant,
        "uniform_synth_nonconformant": uni_nonconformant,
        "false_deviant_rate": fdr,
        "ben_synth_detail": ben_cls,
        "uni_synth_detail": uni_cls,
        "n_draws": draws,
    }


def self_check():
    """__main__ self-check: fitter must classify synthetic Benford as conformant and uniform as nonconformant."""
    pc = positive_control()
    print("=== EPOCH-054 machinery self-check ===")
    print("Benford synthetic ->", pc["ben_synth_detail"]["classification"],
          "MAD=%.5f" % pc["ben_synth_detail"]["mad"], "band=", pc["ben_synth_detail"]["nigrini_band"])
    print("Uniform synthetic ->", pc["uni_synth_detail"]["classification"],
          "MAD=%.5f" % pc["uni_synth_detail"]["mad"], "band=", pc["uni_synth_detail"]["nigrini_band"])
    print("False-deviant rate on true-Benford:", pc["false_deviant_rate"])
    print("PC verdict:", pc["pc_verdict"])
    ok = pc["benford_synth_conformant"] and pc["uniform_synth_nonconformant"] and pc["false_deviant_rate"] <= 0.10
    print("SELF-CHECK:", "PASS" if ok else "FAIL")
    return ok


if __name__ == "__main__":
    self_check()
