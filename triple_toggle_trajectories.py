import random
import matplotlib.pyplot as plt
from pykappa.system import System

COMMIT = "334c299"
N_RUNS = 10
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

colors = {
    "A_on": "#4C72B0", "B_on": "#DD8452",
    "C_on": "#55A868", "D_on": "#C44E52",
    "E_on": "#8172B2", "F_on": "#937860",
}
labels = {"A_on": "A", "B_on": "B", "C_on": "C",
          "D_on": "D", "E_on": "E", "F_on": "F"}

fig, axes = plt.subplots(2, 5, figsize=(18, 7), sharey=True, sharex=True)
axes = axes.flatten()

for i in range(N_RUNS):
    seed = i
    random.seed(seed)
    system = System.from_ka(ka_template, seed=seed)
    while system.time < MAX_TIME:
        system.update()
        if system.reactivity == 0:
            break

    df = system.monitor.dataframe
    ax = axes[i]

    for obs, color in colors.items():
        ax.plot(df["time"], df[obs], color=color, lw=0.9, label=labels[obs])

    # Annotate winner of each pair
    ab = "A" if df["A_on"].iloc[-1] > df["B_on"].iloc[-1] else "B"
    cd = "C" if df["C_on"].iloc[-1] > df["D_on"].iloc[-1] else "D"
    ef = "E" if df["E_on"].iloc[-1] > df["F_on"].iloc[-1] else "F"
    ax.set_title(f"Run {i+1}: {ab}↑ {cd}↑ {ef}↑", fontsize=9)
    ax.set_ylim(0, 220)
    if i >= 5:
        ax.set_xlabel("Time", fontsize=8)
    if i % 5 == 0:
        ax.set_ylabel("# active", fontsize=8)

# Shared legend
handles = [plt.Line2D([0], [0], color=c, lw=1.5, label=l)
           for l, c in zip("ABCDEF", colors.values())]
fig.legend(handles=handles, loc="upper right", fontsize=9,
           title="Agent", ncol=1)

fig.suptitle("Triple toggle switch — 10 individual trajectories (all 6 agents, no basal/deact)", fontsize=12)
fig.tight_layout()

fname = f"triple_toggle_trajectories_no_basal_{COMMIT}.png"
fig.savefig(fname, dpi=150)
print(f"Saved {fname}")
