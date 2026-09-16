"""
Independent references for the Kappa model, used to validate it.

`self_consistent_eta`  exact steady state of the tip process under the paper's
                       uncorrelated-error ansatz (Pigolotti & Sartori Eq. 3):
                       when the terminal residue is removed, the residue it
                       exposes is W with probability eta, independently.
                       State = (active-site occupancy, species of terminal
                       committed residue) -> 6 states; eta solved by fixed point.

`stack_gillespie`      direct stochastic simulation of the same process on an
                       explicit stack of committed residues.  Makes no ansatz,
                       so it also tests whether the ansatz itself is good.

Neither uses Kappa; agreement with the Kappa simulation is a genuine check.
"""
import numpy as np


def _rate_table(p):
    r = p.rates()
    return dict(
        alpha=p.assoc,
        k_off={"R": r["k_off_R"], "W": r["k_off_W"]},
        k_cat={"R": r["k_cat_R"], "W": r["k_cat_W"]},
        k_un={"R": r["k_un_R"], "W": r["k_un_W"]},
        k_pf=({"R": r["k_pf_R"], "W": r["k_pf_W"]} if p.proofread else {"R": 0.0, "W": 0.0}),
        lam=({"R": r["k_lig_R"] * p.c, "W": r["k_lig_W"] * p.c} if p.proofread
             else {"R": 0.0, "W": 0.0}),
    )


def _fluxes(p, eta, R=None):
    """Net incorporation fluxes J_R, J_W of the tip process, given an assumed
    error fraction eta for the residue exposed by a removal."""
    R = R or _rate_table(p)
    SP = ["R", "W"]
    idx = {("_", "R"): 0, ("_", "W"): 1, ("R", "R"): 2, ("R", "W"): 3,
           ("W", "R"): 4, ("W", "W"): 5}
    q = {"R": 1 - eta, "W": eta}
    Q = np.zeros((6, 6))
    for tau in SP:
        i = idx[("_", tau)]
        for nu in SP:
            Q[i, idx[(nu, tau)]] += R["alpha"]                  # add
            Q[i, idx[("_", nu)]] += R["lam"][nu]                # ligate (push nu)
        for tau2 in SP:
            Q[i, idx[("_", tau2)]] += R["k_pf"][tau] * q[tau2]  # excise (pop tau)
            Q[i, idx[(tau, tau2)]] += R["k_un"][tau] * q[tau2]  # uncommit (pop tau)
        for nu in SP:
            j = idx[(nu, tau)]
            Q[j, idx[("_", tau)]] += R["k_off"][nu]             # reject
            Q[j, idx[("_", nu)]] += R["k_cat"][nu]              # commit (push nu)
    np.fill_diagonal(Q, 0.0)
    np.fill_diagonal(Q, -Q.sum(axis=1))
    A = np.vstack([Q.T[:-1], np.ones(6)])
    b = np.zeros(6); b[-1] = 1.0
    pi = np.linalg.solve(A, b)
    J = {}
    for nu in SP:
        push = R["k_cat"][nu] * sum(pi[idx[(nu, t)]] for t in SP) \
             + R["lam"][nu] * sum(pi[idx[("_", t)]] for t in SP)
        pop = (R["k_pf"][nu] + R["k_un"][nu]) * pi[idx[("_", nu)]]
        J[nu] = push - pop
    return J["R"], J["W"]


def self_consistent_eta(p):
    """Steady-state error fraction and per-chain growth velocity, solved exactly
    (within the uncorrelated-error ansatz) by bracketing eta = J_W/(J_R+J_W)."""
    from scipy.optimize import brentq
    R = _rate_table(p)

    def g(eta):
        JR, JW = _fluxes(p, eta, R)
        tot = JR + JW
        if tot <= 0:
            return np.nan
        return JW / tot - eta

    grid = np.concatenate([[1e-10], np.logspace(-9, np.log10(0.499), 400)])
    vals = np.array([g(x) for x in grid])
    ok = np.isfinite(vals)
    lo = hi = None
    for i in range(len(grid) - 1):
        if ok[i] and ok[i + 1] and vals[i] * vals[i + 1] < 0:
            lo, hi = grid[i], grid[i + 1]
            break
    try:
        if lo is None:
            return dict(eta=np.nan, velocity=np.nan, J_R=np.nan, J_W=np.nan)
        eta = brentq(g, lo, hi, xtol=1e-15, rtol=1e-15)
    except (ValueError, np.linalg.LinAlgError):
        return dict(eta=np.nan, velocity=np.nan, J_R=np.nan, J_W=np.nan)
    JR, JW = _fluxes(p, eta, R)
    return dict(eta=eta, velocity=JR + JW, J_R=JR, J_W=JW)


def stack_gillespie(p, n_events=2_000_000, seed=0, burn=0.3):
    """Direct SSA on an explicit stack of committed residues (no ansatz)."""
    rng = np.random.default_rng(seed)
    R = _rate_table(p)
    SP = ("R", "W")
    stack = ["S"]          # seed residue, never removable
    site = None            # None, "R" or "W"
    t = 0.0
    pushes = {"R": 0, "W": 0}
    pops = {"R": 0, "W": 0}
    rec = []
    burn_n = int(burn * n_events)
    for step in range(n_events):
        tip = stack[-1]
        removable = len(stack) > 1 and tip != "S"
        ev, rates = [], []
        if site is None:
            for nu in SP:
                ev.append(("add", nu)); rates.append(R["alpha"])
                if R["lam"][nu] > 0:
                    ev.append(("lig", nu)); rates.append(R["lam"][nu])
            if removable:
                if R["k_pf"][tip] > 0:
                    ev.append(("exc", tip)); rates.append(R["k_pf"][tip])
                ev.append(("unc", tip)); rates.append(R["k_un"][tip])
        else:
            ev.append(("rej", site)); rates.append(R["k_off"][site])
            ev.append(("com", site)); rates.append(R["k_cat"][site])
        rates = np.asarray(rates)
        tot = rates.sum()
        t += rng.exponential(1.0 / tot)
        kind, nu = ev[rng.choice(len(ev), p=rates / tot)]
        if kind == "add":
            site = nu
        elif kind == "rej":
            site = None
        elif kind == "com":
            stack.append(nu); site = None; pushes[nu] += 1
        elif kind == "lig":
            stack.append(nu); pushes[nu] += 1
        elif kind == "exc":
            stack.pop(); pops[nu] += 1
        elif kind == "unc":
            stack.pop(); pops[nu] += 1; site = nu
        if step == burn_n:
            t0, p0 = t, dict(pushes=dict(pushes), pops=dict(pops))
    nR = (pushes["R"] - p0["pushes"]["R"]) - (pops["R"] - p0["pops"]["R"])
    nW = (pushes["W"] - p0["pushes"]["W"]) - (pops["W"] - p0["pops"]["W"])
    return dict(eta=nW / (nR + nW), velocity=(nR + nW) / (t - t0),
                n_incorp=nR + nW, final_len=len(stack),
                eta_seq=np.mean([s == "W" for s in stack[1:]]))


if __name__ == "__main__":
    import sys
    sys.path.insert(0, "/home/ec2-user/kappa-sandbox-2/kpr")
    from model import Params
    for pf in (False, True):
        p = Params(proofread=pf)
        th = self_consistent_eta(p)
        sg = stack_gillespie(p, 400_000, seed=3)
        print(f"proofread={pf}")
        print(f"   theory : eta={th['eta']:.5f}  v={th['velocity']:.4f}")
        print(f"   stack  : eta={sg['eta']:.5f}  v={sg['velocity']:.4f}  "
              f"n={sg['n_incorp']}  seq_eta={sg['eta_seq']:.5f}  len={sg['final_len']}")
