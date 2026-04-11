import random
import itertools
from collections import Counter
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from pykappa.system import System

COMMIT = "791d04c"
N_RUNS = 200
MAX_TIME = 300.0

ka_template = """
%var: 'k_self'  0.003
%var: 'k_inh'   0.005
%var: 'k_deact' 0.05
%var: 'k_basal' 0.002

A(s{on}), A(s{of}) -> A(s{on}), A(s{on}) @ 'k_self'
B(s{on}), B(s{of}) -> B(s{on}), B(s{on}) @ 'k_self'
C(s{on}), C(s{of}) -> C(s{on}), C(s{on}) @ 'k_self'
D(s{on}), D(s{of}) -> D(s{on}), D(s{on}) @ 'k_self'
E(s{on}), E(s{of}) -> E(s{on}), E(s{on}) @ 'k_self'
F(s{on}), F(s{of}) -> F(s{on}), F(s{on}) @ 'k_self'

A(s{on}), B(s{on}) -> A(s{on}), B(s{of}) @ 'k_inh'
B(s{on}), A(s{on}) -> B(s{on}), A(s{of}) @ 'k_inh'

C(s{on}), D(s{on}) -> C(s{on}), D(s{of}) @ 'k_inh'
D(s{on}), C(s{on}) -> D(s{on}), C(s{of}) @ 'k_inh'

E(s{on}), F(s{on}) -> E(s{on}), F(s{of}) @ 'k_inh'
F(s{on}), E(s{on}) -> F(s{on}), E(s{of}) @ 'k_inh'

A(s{on}) -> A(s{of}) @ 'k_deact'
B(s{on}) -> B(s{of}) @ 'k_deact'
C(s{on}) -> C(s{of}) @ 'k_deact'
D(s{on}) -> D(s{of}) @ 'k_deact'
E(s{on}) -> E(s{of}) @ 'k_deact'
F(s{on}) -> F(s{of}) @ 'k_deact'

A(s{of}) -> A(s{on}) @ 'k_basal'
B(s{of}) -> B(s{on}) @ 'k_basal'
C(s{of}) -> C(s{on}) @ 'k_basal'
D(s{of}) -> D(s{on}) @ 'k_basal'
E(s{of}) -> E(s{on}) @ 'k_basal'
F(s{of}) -> F(s{on}) @ 'k_basal'

%init: 100 A(s{on})
%init: 100 A(s{of})
%init: 100 B(s{on})
%init: 100 B(s{of})
%init: 100 C(s{on})
%init: 100 C(s{of})
%init: 100 D(s{on})
%init: 100 D(s{of})
%init: 100 E(s{on})
%init: 100 E(s{of})
%init: 100 F(s{on})
%init: 100 F(s{of})

%obs: 'A_on' |A(s{on})|
%obs: 'B_on' |B(s{on})|
%obs: 'C_on' |C(s{on})|
%obs: 'D_on' |D(s{on})|
%obs: 'E_on' |E(s{on})|
%obs: 'F_on' |F(s{on})|
"""

outcomes = []  # list of (AB_winner, CD_winner, EF_winner)
print(f"Running {N_RUNS} simulations...")
for i in range(N_RUNS):
    seed = i
    random.seed(seed)
    system = System.from_ka(ka_template, seed=seed)
    while system.time < MAX_TIME:
        system.update()
    df = system.monitor.dataframe
    ab = "A" if df["A_on"].iloc[-1] > df["B_on"].iloc[-1] else "B"
    cd = "C" if df["C_on"].iloc[-1] > df["D_on"].iloc[-1] else "D"
    ef = "E" if df["E_on"].iloc[-1] > df["F_on"].iloc[-1] else "F"
    outcomes.append((ab, cd, ef))
    if (i + 1) % 20 == 0:
        print(f"  {i+1}/{N_RUNS} done")

# ── Summary stats ────────────────────────────────────────────────────────────
a_wins = sum(1 for o in outcomes if o[0] == "A")
c_wins = sum(1 for o in outcomes if o[1] == "C")
e_wins = sum(1 for o in outcomes if o[2] == "E")

combo_counts = Counter(outcomes)

all_combos = list(itertools.product(["A","B"], ["C","D"], ["E","F"]))
labels = [f"{a}/{c}/{e}" for a,c,e in all_combos]
counts = [combo_counts.get(combo, 0) for combo in all_combos]

print(f"\nPair win rates (out of {N_RUNS}):")
print(f"  A/B: A={a_wins}, B={N_RUNS-a_wins}")
print(f"  C/D: C={c_wins}, D={N_RUNS-c_wins}")
print(f"  E/F: E={e_wins}, F={N_RUNS-e_wins}")
print(f"\nAttractor distribution:")
for combo, cnt in sorted(combo_counts.items(), key=lambda x: -x[1]):
    print(f"  {combo[0]}/{combo[1]}/{combo[2]}: {cnt}")

# ── Figure ───────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(13, 5))

# Left: per-pair win rates
pairs = ["A vs B", "C vs D", "E vs F"]
first_wins = [a_wins, c_wins, e_wins]
second_wins = [N_RUNS - w for w in first_wins]
x = np.arange(3)
w = 0.35
axes[0].bar(x - w/2, first_wins,  w, label="A / C / E", color="steelblue")
axes[0].bar(x + w/2, second_wins, w, label="B / D / F", color="tomato")
axes[0].axhline(N_RUNS / 2, color="grey", lw=1, ls="--", label="Expected (50%)")
axes[0].set_xticks(x)
axes[0].set_xticklabels(pairs)
axes[0].set_ylabel("# wins")
axes[0].set_ylim(0, N_RUNS)
axes[0].set_title("Per-pair win counts")
axes[0].legend()

# Right: combined attractor distribution
bar_colors = ["steelblue" if (a=="A" and c=="C" and e=="E") else
              "mediumpurple" for a,c,e in all_combos]
axes[1].bar(labels, counts, color=bar_colors)
axes[1].axhline(N_RUNS / 8, color="grey", lw=1, ls="--", label="Expected (12.5%)")
axes[1].set_xlabel("Attractor (winner per pair: AB/CD/EF)")
axes[1].set_ylabel("# simulations")
axes[1].set_title("Combined attractor distribution")
axes[1].tick_params(axis="x", rotation=45)
axes[1].legend()

fig.suptitle(
    f"Triple toggle switch — {N_RUNS} replicates\n"
    f"A/B: A={a_wins}  B={N_RUNS-a_wins}  |  "
    f"C/D: C={c_wins}  D={N_RUNS-c_wins}  |  "
    f"E/F: E={e_wins}  F={N_RUNS-e_wins}",
    fontsize=11,
)
fig.tight_layout()

fname = f"triple_toggle_{COMMIT}.png"
fig.savefig(fname, dpi=150)
print(f"\nSaved {fname}")
