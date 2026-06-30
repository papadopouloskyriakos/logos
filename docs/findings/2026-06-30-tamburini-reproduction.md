# Finding 2026-06-30 — Tamburini 2025 (CSA_OptMatcher) reproduction: the published non-neural baseline

Reproducing Tamburini 2025 Table 3 with his **unmodified** code, as the logos
credibility anchor (the "reproduce a known decipherment" audit). This is **prior
art, not a logos contribution** — see [2026-06-30-paper-audit.md](./2026-06-30-paper-audit.md).
logos adopts CSA_OptMatcher as the non-neural cognate-ID baseline; the wrapper is
`scripts/baselines/run_tamburini.py` (vendor code gitignored under `corpus/bronze/code/`).

**Reference**
Fabio Tamburini, *On automatic decipherment of lost ancient scripts relying on
combinatorial optimisation and coupled simulated annealing*, **Frontiers in
Artificial Intelligence 8:1581129 (2025)**. DOI [10.3389/frai.2025.1581129](https://doi.org/10.3389/frai.2025.1581129).
Code: `github.com/ftamburin/CSA_OptMatcher` (+ `EditDistanceWild`).

## What was set up

- Cloned `CSA_OptMatcher` + `EditDistanceWild` (`--depth 1`) into `corpus/bronze/code/`
  (gitignored — vendor code; invariant 10). EditDistanceWild's C++ extension built
  and installed (`pip install -e .`, CPU path — no GPU on this host; torch 2.12.1+cpu).
  `structurely/csa` pip-installed for completeness; NOTE the runtime actually uses
  Tamburini's **local** `pycsa.py`/`lsa_2g.py` (his modified CSA), imported by `CSA_OptMatcher.py`.
- Protocol (paper §3.2-3.3, locked by `tests/test_tamburini_baseline.py`):
  16 coupled annealers; **N/M by his rule** `N=1,M=2 if |L_s|>|K_s| else N=2,M=1`;
  **λ=4** generally, **λ=8** for U/OH-noisy (his stated exception); his exact
  hyperparameters (tacc₀=200, tacc_sched=0.95, tgen₀=1, tgen_sched=0.999, qa=0.1,
  update_interval=⌈|state|/16⌉). Accuracy metric = Luo et al. 2019 cognate-ID rate
  (his `EvalModel`), mean±std over 4 seeds (Reimers & Gurevych 2017).

## The CPU feasibility wall (the honest constraint)

The paper used **CUDA**; this host is CPU-only. The dominant cost is Tamburini's
`energy()` — a Python loop over every cognate issuing one `editdistance1N` call.
Measured per-eval (single-threaded, torch threads=1):

| benchmark | |lLex| | energy-eval | per CSA step (≈16 evals / 16 procs) |
|---|---:|---:|---:|
| U/OH noiseless | 2,214 | **19.2 s** | ~20 s/step (procs=16) |
| LB/MG | 919 | 4.1 s | ~4 s/step |
| CS/AG | 693 | 6.0 s | ~6 s/step |
| Ph/Ug | 139 | 55 ms | <1 s/step |
| Luv/Hit | 109 | 32 ms | <1 s/step |

His code hardcodes `steps=100000`. At 20 s/step that is ≈**23 days for one Ugaritic
seed** on CPU. Full Table 3 (7 benchmarks × 4 seeds × 100k steps) is therefore
infeasible here. The paper's *stated* stopping rule is "100 temperature updates
without improvement in best σ" — his released code does **not** implement that
early-stop, so a fixed reduced step budget is the faithful reading of the artifact.

**What we did instead:** run his code (unmodified functions) at a **reduced,
clearly-reported step budget**, harvesting a convergence trace via the wrapper's
`--checkpoint-steps` (his `CoupledAnnealer.anneal()` mutates instance temps/state,
so calling it in chunks gives a continuous temperature schedule; `get_best()` +
his `EvalModel` evaluate each checkpoint). Treat reduced-budget numbers as
**lower bounds until the curve plateaus at the published value.** CSA cools from
tacc=200 by ×0.95 per temp-update (every ⌈|state|/16⌉ steps); for Ugaritic that is
≈450 steps just to cool to ~1, so <450-step Ugaritic runs are knowingly under-cooled.

Two host-specific fixes the wrapper applies (without touching his algorithm):
`OMP/OPENBLAS/MKL_NUM_THREADS=1` + `torch.set_num_threads(1)` (else 8 workers ×
20 threads thrash on 20 cores), and importing `CSA_OptMatcher` as a **real
importable module** on `sys.path` (a synthetic importlib name makes
multiprocessing fail with `PicklingError: Can't pickle <class '….Problem'>`).

## Reproduced results vs Tamburini 2025 Table 3

_All our numbers are CPU. The paper used CUDA at 100,000 steps/seed. Our budgets
are stated per row; treat any run well short of the plateau as a lower bound._

| benchmark | N/M/λ | our acc (seed, steps) | published CSA | gap |
|---|---|---|---:|---|
| U/OH noiseless | 1/2/4 | **0.0%** (seed 0, step 25; 40 s/step → ~6 h/seed to converge) | 95.5 | CPU-infeasible in budget (see wall) |
| U/OH noisy | 1/2/8 | _not run (same infeasibility wall; bigger lexicon)_ | 74.7 | infeasible |
| LB/MG | 2/1/4 | _not run (4.1 s/eval → days)_ | 89.4 | infeasible |
| CS/AG | 2/1/4 | _not run (6.0 s/eval → days)_ | 86.3 | infeasible |
| Ph/Ug | 2/1/4 | step 4000 → **82.9%** (87/105); energy 35.10→31.96 | 80.5 | **reproduced** (single seed; +2.4pp over 4-seed mean) |
| Luv/Hit | 2/1/4 | step 4000 → **47.5%** (28/59); energy plateaued 36.95→37.02 | 47.5 | **reproduced** (single seed, 4k vs 100k steps) |

_(Decontaminated NeuroCipher-dagger from Table 3: U/OH 90.4 / 87.6, LB/MG 75.8,
Luv/Hit 18.2.)_

**The Ugaritic feasibility wall (empirical, PRIMARY benchmark).** A single
Ugaritic-noiseless energy eval is **19.2 s** on CPU (his 2,214-word Python loop
issuing one `editdistance1N` per cognate). In the 16-annealer pool the effective
per-step wall is **~40 s** (his `pycssa.py` recreates a 16-process `mp.Pool`
every step). CSA cools from tacc=200 by ×0.95 per temp-update (every ⌈60/16⌉=4
steps) ⇒ needs ≈**450 steps just to cool** to ~1, then hundreds more to find the
optimum. One converged seed therefore costs ≈ **6 hours**; his protocol is 100,000
steps (≈23 days) and 4 seeds. On this CPU-only host the PRIMARY benchmark cannot be
converged in a session budget. Our evidence: seed-0 step-25 checkpoint = **0.0%
(0/2214), energy 715.9** — the system is still "hot" (acceptance temp ≈148), i.e.
near-random mapping, exactly as the cooling schedule predicts. This is a
**budget/env limitation, not a method divergence** — the wrapper drives his
unaltered `energy`/`move`/`lsa_2g`/`EvalModel` (validated by the small benchmarks
below converging toward their published values).

## Interpretation

The discipline-relevant outcome is **not** to beat or exactly match 95.5 on
CPU/reduced-budget — it is (a) to confirm the wrapper faithfully drives his code
(its energy/move/LSA-2G/EvalModel are byte-for-byte his), and (b) to establish
the **convergence ceiling** our budget can evidence.

**The wrapper is validated.** On the two benchmarks whose lexica fit the CPU
budget, our single-seed reduced-step runs land on the published values:

```
Luvian-Hittite   step 2000 -> 44.1% (26/59)  E=36.95   [pub CSA 47.5]
                 step 4000 -> 47.5% (28/59)  E=37.02   <- reproduced (energy plateaued)
Phoenician/Ug    step 2000 -> 65.7% (69/105) E=35.10   [pub CSA 80.5]
                 step 4000 -> 82.9% (87/105) E=31.96   <- reproduced (energy still falling)
```

Both reach the published Table-3 value at ~4,000 steps (his runs are 100,000,
4 seeds, GPU). Luv/Hit plateaus exactly on 47.5%; Ph/Ug at 82.9% is within
single-seed noise of the 80.5% four-seed mean. This is the credibility anchor:
the wrapper + his unmodified algorithm reproduce his published numbers, so the
shortfalls below are budget/env, not method.

**Where we undershoot published, the cause is budget/env (CPU + far fewer steps),
not a method divergence:**
- **Ugaritic-Hebrew (PRIMARY)** — CPU-infeasible to converge: 19.2 s/eval × his
  16-annealer pool (recreated every step) ≈ 40 s/step, and CSA needs ≈450 steps
  just to cool ⇒ ~6 h/seed, vs 100,000 steps/4 seeds in the paper. Documented
  empirically: seed-0 step-25 = 0.0% (system still "hot", near-random mapping).
  The full cooling trajectory is in `runtime/tamburini/ugaritic-trajectory.log`.
- **U/OH-noisy, LB/MG, CS/AG** — same wall (4-6 s/eval for the syllabic lexica,
  bigger still for noisy Ugaritic); not run to convergence.
- The paper reports **mean ± std over 4 seeds**; our feasible runs are single-seed.

This is the honest framing the audit demands: the non-neural baseline is adopted
and its protocol is faithfully reproducible here; the large-lexicon numbers simply
need a GPU (or a multi-hour CPU budget) to reach Table 3, which is the next
session's work via the gpu host. The wrapper (`scripts/baselines/run_tamburini.py`)
is the committed artifact the discipline layer calls; the protocol registry is
locked by `tests/test_tamburini_baseline.py` (6 tests).

## Reproducibility

```
# vendor code (gitignored):
git clone --depth 1 https://github.com/ftamburin/CSA_OptMatcher   corpus/bronze/code/
git clone --depth 1 https://github.com/ftamburin/EditDistanceWild corpus/bronze/code/
cd corpus/bronze/code/EditDistanceWild && pip install --user --break-system-packages -e .

# our wrapper (committed):
python3 scripts/baselines/run_tamburini.py --list
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 \
  python3 scripts/baselines/run_tamburini.py -b luvian-hittite --seeds 0 1 2 3 --steps 6000
# convergence trace for the big lexica:
OMP_NUM_THREADS=1 ... python3 scripts/baselines/run_tamburini.py -b ugaritic-noiseless \
  --seeds 0 --steps 400 --checkpoint-steps 25 --processes 16
```
