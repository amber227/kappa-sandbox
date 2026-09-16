"""Simulation driver for the kinetic-proofreading Kappa model."""
import random, time, os, sys
import numpy as np
import pandas as pd
from pykappa.system import System

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from model import Params, kappa

OBS = ["free_R", "free_W", "prod_R", "prod_W"]


def simulate(p: Params, n_events: int, seed: int = 0, n_samples: int = 500):
    """Run `n_events` Gillespie events; return (samples DataFrame, named tallies)."""
    random.seed(seed)            # pykappa's Rule.select uses the module-level RNG
    names = []
    sys_ = System.from_ka(kappa(p, names), seed=seed)
    sys_.monitor = None          # per-event monitoring would dominate the runtime
    name_of = {str(r): n for n, r in zip(names, sys_.rules.values())}
    every = max(1, n_events // n_samples)
    rows = []
    for i in range(n_events):
        sys_.update()
        if i % every == 0 or i == n_events - 1:
            rows.append([sys_.time] + [sys_[o] for o in OBS])
    df = pd.DataFrame(rows, columns=["time"] + OBS)
    tallies = {name_of.get(k, k): v["applied"] for k, v in sys_.tallies.items()}
    return df, tallies


def summarise(df: pd.DataFrame, p: Params, tally: dict, tail: float = 0.6) -> dict:
    """Error fraction, growth velocity and proofreading cost over the last
    `tail` of the run (the beginning is transient: chains start one residue long)."""
    n = len(df)
    a, b = df.iloc[int((1 - tail) * n)], df.iloc[-1]
    dR, dW = b.prod_R - a.prod_R, b.prod_W - a.prod_W
    dt, n_eff = b.time - a.time, dR + dW
    eta = dW / n_eff if n_eff > 0 else np.nan
    n_exc = tally.get("proofread_R", 0) + tally.get("proofread_W", 0)
    n_com = tally.get("commit_R", 0) + tally.get("commit_W", 0)
    n_inc = b.prod_R + b.prod_W
    return dict(
        eta=eta,
        eta_lo=_ci(dW, n_eff)[0], eta_hi=_ci(dW, n_eff)[1],
        n_incorp=float(n_eff),
        velocity=n_eff / dt / p.n_chains if dt > 0 else np.nan,
        cost=n_exc / n_inc if n_inc > 0 else np.nan,       # excisions per residue kept
        futility=(n_com + n_exc) / n_inc if n_inc > 0 else np.nan,
        free_R=float(b.free_R), free_W=float(b.free_W),
        mean_len=float(n_inc) / p.n_chains, sim_time=float(b.time),
    )


def _ci(k, n, z=1.0):
    """Wilson score interval (1 sigma) for a binomial proportion."""
    if n <= 0:
        return (np.nan, np.nan)
    ph = k / n
    d = 1 + z**2 / n
    c = (ph + z**2 / (2 * n)) / d
    h = z * np.sqrt(ph * (1 - ph) / n + z**2 / (4 * n**2)) / d
    return (max(c - h, 0.0), min(c + h, 1.0))
