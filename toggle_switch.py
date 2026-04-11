import random
import matplotlib.pyplot as plt
from pykappa.system import System

SEED = 42
random.seed(SEED)

ka_model = """
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

%init: 99  A(s{on})
%init: 101 A(s{of})
%init: 101 B(s{on})
%init: 99  B(s{of})

%obs: 'A_on' |A(s{on})|
%obs: 'B_on' |B(s{on})|
"""

system = System.from_ka(ka_model, seed=SEED)

max_time = 500.0
while system.time < max_time:
    system.update()

df = system.monitor.dataframe

COMMIT = "7e82c21"
fig, ax = plt.subplots(figsize=(10, 4))
ax.plot(df["time"], df["A_on"], label="A (active)", color="steelblue")
ax.plot(df["time"], df["B_on"], label="B (active)", color="tomato")
ax.set_xlabel("Time")
ax.set_ylabel("# active molecules")
ax.set_title("Toggle switch — mutual inhibition + self-activation")
ax.legend()
ax.set_ylim(0, 220)
fig.tight_layout()

fname = f"toggle_switch_{COMMIT}.png"
fig.savefig(fname, dpi=150)
print(f"Saved {fname}")
print(f"Final A_on={df['A_on'].iloc[-1]:.0f}, B_on={df['B_on'].iloc[-1]:.0f}")
