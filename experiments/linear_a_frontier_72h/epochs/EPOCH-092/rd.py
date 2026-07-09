"""Graph reaction-diffusion (Turing morphogenesis) core.

Two-field activator-inhibitor on a symmetric-normalized graph Laplacian L (eigenvalues in [0,2]):
    du/dt = f(u,v) - Du * L u
    dv/dt = g(u,v) - Dv * L v
Turing instability is VERIFIED mechanically per run (else TURING_MODEL_INVALID):
  (1) homogeneous equilibrium (u*,v*) exists (f=g=0);
  (2) ODE-stable without diffusion: trace(J)<0 AND det(J)>0;
  (3) diffusion-driven instability: some graph eigenvalue lambda_k>0 has det(J - lambda_k*diag(Du,Dv))<0
      (equivalently max Re eig(M_k)>0), with Du<Dv;
  (4) the unstable pattern is NOT explained by degree or connected components
      (n_components==1 enforced; |corr(pattern, degree)| reported and gated).
The emergent pattern is the nonlinear steady-state activator field u(inf) from (u*,v*)+noise.
"""
import numpy as np

# ---- reaction families: f,g, analytic equilibrium, analytic Jacobian at equilibrium ----

def schnakenberg(a=0.1, b=0.9):
    def f(u, v): return a - u + u * u * v
    def g(u, v): return b - u * u * v
    us = a + b; vs = b / (us * us)
    J = np.array([[-1 + 2 * us * vs, us * us],
                  [-2 * us * vs,     -us * us]], float)
    return dict(name="Schnakenberg", f=f, g=g, us=us, vs=vs, J=J, params=dict(a=a, b=b))

def gierer_meinhardt(a=0.1, b=1.0):
    def f(u, v): return a - b * u + (u * u) / v
    def g(u, v): return u * u - v
    us = (a + 1.0) / b; vs = us * us
    J = np.array([[-b + 2.0 / us, -1.0 / (us * us)],
                  [2.0 * us,       -1.0]], float)
    return dict(name="GiererMeinhardt", f=f, g=g, us=us, vs=vs, J=J, params=dict(a=a, b=b))

def gray_scott(F=0.037, k=0.06):
    # nontrivial steady state of u'=-uv^2+F(1-u), v'=uv^2-(F+k)v ; solve numerically
    def f(u, v): return -u * v * v + F * (1 - u)
    def g(u, v): return u * v * v - (F + k) * v
    disc = 1 - 4 * (F + k) ** 2 / F
    if disc <= 0:
        return None  # no nontrivial Turing state for these (F,k)
    vs = (F * (1 + np.sqrt(disc))) / (2 * (F + k))
    us = (F) / (F + vs * vs)
    # numeric Jacobian
    eps = 1e-6
    J = np.zeros((2, 2))
    J[0, 0] = (f(us + eps, vs) - f(us - eps, vs)) / (2 * eps)
    J[0, 1] = (f(us, vs + eps) - f(us, vs - eps)) / (2 * eps)
    J[1, 0] = (g(us + eps, vs) - g(us - eps, vs)) / (2 * eps)
    J[1, 1] = (g(us, vs + eps) - g(us, vs - eps)) / (2 * eps)
    return dict(name="GrayScott", f=f, g=g, us=us, vs=vs, J=J, params=dict(F=F, k=k))


def _mode_growth(J, evals, Du, Dv):
    """Max real part of eig(J - lambda_k*diag(Du,Dv)) over each graph eigenvalue. Returns array over modes."""
    out = np.empty(len(evals))
    for i, lam in enumerate(evals):
        M = J - lam * np.diag([Du, Dv])
        out[i] = np.max(np.real(np.linalg.eigvals(M)))
    return out


def verify_turing(reaction, evals, Du, Dv, eq_tol=1e-6):
    """Return dict with conditions 1-3 and the unstable-mode growth spectrum."""
    us, vs, J = reaction["us"], reaction["vs"], reaction["J"]
    cond1 = (abs(reaction["f"](us, vs)) < eq_tol and abs(reaction["g"](us, vs)) < eq_tol
             and us > 0 and vs > 0 and np.isfinite(us) and np.isfinite(vs))
    tr, det = np.trace(J), np.linalg.det(J)
    cond2 = (tr < 0) and (det > 0)                       # ODE stable at lambda=0
    growth = _mode_growth(J, evals, Du, Dv)
    # exclude the homogeneous mode lambda_0=0 from "diffusion-driven"
    nonzero = evals > 1e-9
    cond3 = bool(np.any((growth > 1e-9) & nonzero)) and (Du < Dv)
    unstable_modes = np.where((growth > 1e-9) & nonzero)[0]
    return dict(cond1_equilibrium=bool(cond1), cond2_ode_stable=bool(cond2),
                cond3_diffusion_instability=bool(cond3), trace=float(tr), det=float(det),
                growth=growth, unstable_modes=unstable_modes.tolist(),
                max_growth=float(growth[nonzero].max()) if nonzero.any() else float("nan"))


def _fastest_mode(J, evals, Du, Dv):
    """Return (lambda* of the max-growth non-zero mode, its growth rate)."""
    g = _mode_growth(J, evals, Du, Dv)
    nz = evals > 1e-9
    if not nz.any() or not np.any((g > 1e-9) & nz):
        return None, None
    idx = np.where(nz)[0]
    gi = idx[np.argmax(g[idx])]
    return float(evals[gi]), float(g[gi])


def find_Du(reaction, evals, ratio, Du_grid=None):
    """Frozen UNSUPERVISED selection rule (no truth labels): scan Du (Dv=ratio*Du) and choose the diffusion
    scale that destabilizes the COARSEST structure — i.e. minimizes the smallest nonzero unstable eigenvalue
    (long-wavelength = community/class scale), tie-broken toward the NARROWEST band (fewest unstable modes).
    Coarse patterns need LARGER Du (lambda* ~ f_u/(2 Du)); a band that falls in the low spectral gap
    destabilizes nothing and is rejected by the Turing conditions. Returns dict or None."""
    if Du_grid is None:
        Du_grid = np.geomspace(1e-3, 50.0, 80)
    best = None
    for Du in Du_grid:
        Dv = ratio * Du
        v = verify_turing(reaction, evals, Du, Dv)
        if not (v["cond1_equilibrium"] and v["cond2_ode_stable"] and v["cond3_diffusion_instability"]):
            continue
        um = [m for m in v["unstable_modes"] if evals[m] > 1e-9]
        if not um:
            continue
        lo = float(min(evals[m] for m in um))
        key = (lo, len(um))            # minimize coarsest unstable lambda, then narrowest band
        if best is None or key < best[0]:
            best = (key, Du, Dv, v, lo)
    if best is None:
        return None
    _, Du, Dv, v, lo = best
    return dict(Du=float(Du), Dv=float(Dv), verify=v, min_unstable_lam=lo,
                n_unstable=len(v["unstable_modes"]))


def integrate(reaction, L, Du, Dv, seed=0, t_max=400.0, dt=0.05, noise=1e-2):
    """Explicit-Euler nonlinear RD to steady state. Returns u(inf) node field (n,)."""
    rng = np.random.default_rng(seed)
    n = L.shape[0]
    us, vs, f, g = reaction["us"], reaction["vs"], reaction["f"], reaction["g"]
    u = us + noise * rng.standard_normal(n)
    v = vs + noise * rng.standard_normal(n)
    steps = int(t_max / dt)
    for _ in range(steps):
        Lu = L @ u; Lv = L @ v
        du = f(u, v) - Du * Lu
        dv = g(u, v) - Dv * Lv
        u = u + dt * du; v = v + dt * dv
        u = np.clip(u, -1e3, 1e3); v = np.clip(v, 1e-6, 1e3)
        if not np.all(np.isfinite(u)):
            break
    return u


def pattern_degree_corr(pattern, degree):
    """Condition-4 diagnostic: |Pearson corr| of the emergent pattern with node degree."""
    p = pattern - pattern.mean(); d = degree - degree.mean()
    denom = (np.linalg.norm(p) * np.linalg.norm(d))
    return float(abs(p @ d) / denom) if denom > 0 else 0.0


REACTIONS = {"Schnakenberg": schnakenberg, "GiererMeinhardt": gierer_meinhardt, "GrayScott": gray_scott}


if __name__ == "__main__":
    # self-test the Turing math on a ring graph (classic Turing substrate) + report conditions
    import numpy as np
    n = 60
    W = np.zeros((n, n))
    for i in range(n):
        W[i, (i + 1) % n] = W[(i + 1) % n, i] = 1.0
    d = W.sum(1); dinv = 1 / np.sqrt(d)
    L = np.eye(n) - (W * dinv[:, None]) * dinv[None, :]
    evals = np.clip(np.linalg.eigvalsh(0.5 * (L + L.T)), 0, None)
    for name, ctor in REACTIONS.items():
        r = ctor()
        if r is None:
            print(f"{name}: no nontrivial state"); continue
        res = find_Du(r, evals, ratio=20)
        if res is None:
            print(f"{name}: NO Turing regime found on ring spectrum"); continue
        v = res["verify"]
        u = integrate(r, L, res["Du"], res["Dv"], seed=1)
        print(f"{name}: eq({r['us']:.3f},{r['vs']:.3f}) cond1={v['cond1_equilibrium']} cond2={v['cond2_ode_stable']} "
              f"cond3={v['cond3_diffusion_instability']} Du={res['Du']:.4f} Dv={res['Dv']:.3f} "
              f"n_unstable={len(v['unstable_modes'])} u_range=[{u.min():.2f},{u.max():.2f}] std={u.std():.3f}")
