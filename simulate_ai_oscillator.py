"""
Activator-Inhibitor oscillator from Cao et al. 2015 (Nature Physics).
Direct Gillespie SSA implementation (PyKappa does not support agent creation/deletion).

Species tracked:
  n_Mu   - free M (unphosphorylated)
  n_MR   - MR complex (M bound to R, M in state u)
  n_Mp   - free M (phosphorylated)
  n_MpK  - MpK complex (M bound to K, M in state p)
  n_R    - total R molecules (free + in MR)
  n_X    - X (inhibitor)

Conserved: n_Mu + n_MR + n_Mp + n_MpK = M_T * V = 500
           free K = K_T * V - n_MpK = 50 - n_MpK
"""

import random
import math
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Parameters (V=50, γ=1e-5) ────────────────────────────────────────────────
SEED   = 42
V      = 50
GAMMA  = 1e-5

k0 = 1.0          # Mp-driven R synthesis rate (per Mp molecule)
k1 = 1.0          # constitutive synthesis prefactor
S  = 0.4          # constitutive synthesis input concentration
k2 = 1.0          # X-mediated R degradation (ODE units c⁻¹t⁻¹)
k3 = 1.0          # Mp-driven X synthesis rate (per Mp molecule)
k4 = 0.5          # X degradation rate

a1 = 100.0        # M + R → MR   (ODE bimolecular rate)
d1 = 15.0         # MR → M + R
f1 = 15.0         # MR → Mp + R  (phosphorylation)
a2 = 100.0        # Mp + K → MpK
d2 = 15.0         # MpK → Mp + K
f2 = 15.0         # MpK → M + K  (dephosphorylation)

fm1 = math.sqrt(GAMMA) * a1 * f1 / d1   # ≈ 0.3162 (ODE units)
fm2 = fm1

M_T = 10.0        # total kinase concentration
K_T = 1.0         # total phosphatase concentration

# Stochastic rates (bimolecular → divide by V; zeroth-order → multiply by V)
R_CONST_SYNTH = k1 * S * V            # = 20.0  (zeroth-order propensity)
K0 = k0                                # per free Mp molecule
K2 = k2 / V                           # per (X, free-R) pair
K3 = k3                                # per free Mp molecule
K4 = k4                                # per X molecule

A1 = a1 / V                           # per (Mu, free-R) pair
D1 = d1                                # per MR
F1 = f1                                # per MR
A2 = a2 / V                           # per (Mp, free-K) pair
D2 = d2                                # per MpK
F2 = f2                                # per MpK
FM1 = fm1 / V                          # per (Mp, free-R) pair  ≈ 0.006325
FM2 = fm2 / V                          # per (Mu, free-K) pair  ≈ 0.006325

N_M_TOTAL = int(M_T * V)              # 500
N_K_TOTAL = int(K_T * V)              # 50

# ── Initial conditions ────────────────────────────────────────────────────────
np.random.seed(SEED)
random.seed(SEED)

n_Mu  = N_M_TOTAL   # all kinase starts free and unphosphorylated
n_MR  = 0
n_Mp  = 0
n_MpK = 0
n_R   = 20
n_X   = 0

# ── Gillespie SSA ─────────────────────────────────────────────────────────────
MAX_TIME = 500.0

times  = [0.0]
R_traj = [n_R]
X_traj = [n_X]
Mp_traj = [n_Mp]

t = 0.0

print("Running Gillespie SSA...")
step = 0
while t < MAX_TIME:
    n_K_free  = N_K_TOTAL - n_MpK
    n_R_free  = n_R - n_MR

    # Propensities for all 13 reactions
    a = [
        R_CONST_SYNTH,                        # R1:  ∅ → R
        K0 * n_Mp,                             # R2:  Mp → Mp + R
        K2 * n_X * n_R,                        # R3:  X + R → X  (total R, matching ODE)
        K3 * n_Mp,                             # R4:  Mp → Mp + X
        K4 * n_X,                              # R5:  X → ∅
        A1 * n_Mu * max(n_R_free, 0),          # R6:  Mu + R → MR
        D1 * n_MR,                             # R7:  MR → Mu + R
        F1 * n_MR,                             # R8:  MR → Mp + R
        A2 * n_Mp * max(n_K_free, 0),          # R9:  Mp + K → MpK
        D2 * n_MpK,                            # R10: MpK → Mp + K
        F2 * n_MpK,                            # R11: MpK → Mu + K
        FM1 * n_Mp * max(n_R_free, 0),         # R12: Mp + R → MR (reverse)
        FM2 * n_Mu * max(n_K_free, 0),         # R13: Mu + K → MpK (reverse)
    ]

    a_total = sum(a)
    if a_total == 0:
        break

    # Time to next event
    dt = np.random.exponential(1.0 / a_total)
    t += dt

    # Choose reaction
    r = np.random.uniform(0, a_total)
    cumsum = 0.0
    chosen = -1
    for i, ai in enumerate(a):
        cumsum += ai
        if r < cumsum:
            chosen = i
            break

    # Apply state change
    if   chosen == 0:  n_R   += 1                          # R1
    elif chosen == 1:  n_R   += 1                          # R2
    elif chosen == 2:                                       # R3: degrade free or bound R
        n_R -= 1
        if n_R > 0 and np.random.random() < n_MR / (n_R + 1):
            n_MR -= 1; n_Mu += 1  # was a bound R; release M
    elif chosen == 3:  n_X   += 1                          # R4
    elif chosen == 4:  n_X   -= 1                          # R5
    elif chosen == 5:  n_Mu  -= 1; n_MR  += 1             # R6
    elif chosen == 6:  n_Mu  += 1; n_MR  -= 1             # R7
    elif chosen == 7:  n_MR  -= 1; n_Mp  += 1             # R8
    elif chosen == 8:  n_Mp  -= 1; n_MpK += 1             # R9
    elif chosen == 9:  n_MpK -= 1; n_Mp  += 1             # R10
    elif chosen == 10: n_MpK -= 1; n_Mu  += 1             # R11
    elif chosen == 11: n_Mp  -= 1; n_MR  += 1             # R12
    elif chosen == 12: n_Mu  -= 1; n_MpK += 1             # R13

    step += 1
    if step % 500_000 == 0:
        print(f"  t={t:.1f}  R={n_R}  X={n_X}  Mp={n_Mp}")

    times.append(t)
    R_traj.append(n_R)
    X_traj.append(n_X)
    Mp_traj.append(n_Mp)

print(f"Done: {step:,} steps, final t={t:.2f}")

# ── Plot ──────────────────────────────────────────────────────────────────────
times  = np.array(times)
R_traj = np.array(R_traj)
X_traj = np.array(X_traj)

git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode().strip()

fig, axes = plt.subplots(2, 1, figsize=(13, 6), sharex=True)

axes[0].plot(times, R_traj, color='steelblue', linewidth=0.6)
axes[0].set_ylabel('R (molecules)', fontsize=12)
axes[0].set_title(
    f'Activator-Inhibitor Oscillator — Cao et al. 2015  '
    f'(V={V}, γ={GAMMA}, seed={SEED}, git:{git_hash})',
    fontsize=12)

axes[1].plot(times, X_traj, color='tomato', linewidth=0.6)
axes[1].set_ylabel('X (molecules)', fontsize=12)
axes[1].set_xlabel('Time', fontsize=12)

plt.tight_layout()
fname = f'ai_oscillator_single_run_{git_hash}.png'
fig.savefig(fname, dpi=150)
print(f"Saved: {fname}")
