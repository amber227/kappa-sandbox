import random
import matplotlib.pyplot as plt
from pykappa.system import System

COMMIT = "22f4afd"
N_RUNS = 10
MAX_TIME = 500.0

ka_template = """
%var: 'k_self'  0.003
%var: 'k_inh'   0.005
%var: 'k_deact' 0.05
%var: 'k_basal' 0.002

A(s{on}), A(s{of}) -> A(s{on}), A(s{on}) @ 'k_self'
B(s{on}), B(s{of}) -> B(s{on}), B(s{on}) @ 'k_self'

A(s{on}), B(s{on}) -> A(s{on}), B(s{of}) @ 'k_inh'
B(s{on}), A(s{on}) -> B(s{on}), A(s{of}) @ 'k_inh'

A(s{on}) -> A(s{of}) @ 'k_deact'
B(s{on}) -> B(s{of}) @ 'k_deact'

A(s{of}) -> A(s{on}) @ 'k_basal'
B(s{of}) -> B(s{on}) @ 'k_basal'

%init: 100 A(s{on})
%init: 100 A(s{of})
%init: 100 B(s{on})
%init: 100 B(s{of})

%obs: 'A_on' |A(s{on})|
%obs: 'B_on' |B(s{on})|
"""

fig, axes = plt.subplots(2, 5, figsize=(16, 6), sharey=True, sharex=True)
axes = axes.flatten()

outcomes = []
for i in range(N_RUNS):
    seed = i
    random.seed(seed)
    system = System.from_ka(ka_template, seed=seed)
    while system.time < MAX_TIME:
        system.update()

    df = system.monitor.dataframe
    a_final = df["A_on"].iloc[-1]
    b_final = df["B_on"].iloc[-1]
    winner = "A" if a_final > b_final else "B"
    outcomes.append(winner)

    ax = axes[i]
    ax.plot(df["time"], df["A_on"], color="steelblue", lw=0.8, label="A")
    ax.plot(df["time"], df["B_on"], color="tomato", lw=0.8, label="B")
    ax.set_title(f"Run {i+1}: {winner} wins", fontsize=9)
    ax.set_ylim(0, 220)
    if i >= 5:
        ax.set_xlabel("Time", fontsize=8)
    if i % 5 == 0:
        ax.set_ylabel("# active", fontsize=8)

handles = [
    plt.Line2D([0], [0], color="steelblue", label="A (active)"),
    plt.Line2D([0], [0], color="tomato",    label="B (active)"),
]
fig.legend(handles=handles, loc="upper right", fontsize=9)
fig.suptitle(
    f"Toggle switch — 10 replicates (symmetric init, 100 each)\n"
    f"A wins: {outcomes.count('A')}/10  |  B wins: {outcomes.count('B')}/10",
    fontsize=11,
)
fig.tight_layout()

fname = f"toggle_switch_10runs_{COMMIT}.png"
fig.savefig(fname, dpi=150)
print(f"Saved {fname}")
print(f"Outcomes: {outcomes}")
print(f"A wins: {outcomes.count('A')}/10, B wins: {outcomes.count('B')}/10")
