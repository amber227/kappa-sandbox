"""
A(x, y, z) contact map model.
  Bond B: A(z) -- A(z)   symmetric homodimerization
  Bond α: A(x) -- A(y)   head-to-tail, linear chains only (rings forbidden)

Ring closure is prevented via ambiguous-molecularity syntax {0}, which
requires component tracking to be enabled on the mixture.

Chain length distribution sampled at discrete snapshots via bond-graph BFS.
"""

import random
import subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from collections import Counter
from pykappa.system import System

# ── Config ────────────────────────────────────────────────────────────────────
DRY_RUN = False
SEED = 42
N_AGENTS = 500
MAX_TIME = 200.0
SNAPSHOT_TIMES = [10.0, 50.0, 200.0]

random.seed(SEED)

git_hash = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True,
    cwd="/home/ec2-user/kappa-sandbox"
).stdout.strip()

# ── Kappa model ───────────────────────────────────────────────────────────────
kappa_model = f"""
%init: {N_AGENTS} A(x[.], y[.], z[.])

A(z[.]), A(z[.]) <-> A(z[1]), A(z[1]) @ 0.01, 0.02
A(x[.]), A(y[.]) <-> A(x[1]), A(y[1]) @ 0.01 {{0}}, 0.02

%obs: 'free_monomer' |A(x[.], y[.], z[.])|
%obs: 'z_bonds'      |A(z[1]), A(z[1])|
%obs: 'alpha_bonds'  |A(x[1]), A(y[1])|
"""

# ── Chain length distribution ─────────────────────────────────────────────────
def chain_length_distribution(mixture):
    """
    Count α-bond (x-y) chain lengths by traversing the bond graph directly.
    z-bond state is ignored — z-z bonds form independent dimers orthogonal
    to chain topology.

    Works for both linear chains and rings (which arise when a chain closes
    on itself via two x-y bonds in opposite directions).
    Returns a Counter: {chain_length: count}.
    """
    # Map each agent id to the id of the agent it connects to via x→y and y←x
    x_to = {}   # a.id -> id of agent whose y is bound to a's x (or None)
    y_from = {}  # a.id -> id of agent whose x is bound to a's y (or None)

    for a in mixture.agents:
        sites = {s.label: s for s in a.sites}
        x_site = sites.get('x')
        y_site = sites.get('y')

        if x_site and x_site.bound and x_site.partner.label == 'y':
            x_to[a.id] = x_site.partner.agent.id
        else:
            x_to[a.id] = None

        if y_site and y_site.bound and y_site.partner.label == 'x':
            y_from[a.id] = y_site.partner.agent.id
        else:
            y_from[a.id] = None

    # BFS over undirected x-y bond graph to find connected components
    all_ids = set(a.id for a in mixture.agents)
    visited = set()
    lengths = []

    for start in all_ids:
        if start in visited:
            continue
        component = set()
        queue = [start]
        while queue:
            curr = queue.pop()
            if curr in component:
                continue
            component.add(curr)
            if x_to[curr] is not None:
                queue.append(x_to[curr])
            if y_from[curr] is not None:
                queue.append(y_from[curr])
        visited |= component
        lengths.append(len(component))

    return Counter(lengths)


# ── Simulation ────────────────────────────────────────────────────────────────
system = System.from_ka(kappa_model, seed=SEED)
system.mixture.enable_component_tracking()

snapshots = {}
t_idx = 0

while system.time < MAX_TIME:
    system.update()
    if t_idx < len(SNAPSHOT_TIMES) and system.time >= SNAPSHOT_TIMES[t_idx]:
        t = SNAPSHOT_TIMES[t_idx]
        dist = chain_length_distribution(system.mixture)
        snapshots[t] = dist
        total_in_chains = sum(L * n for L, n in dist.items())
        print(f"t={system.time:.2f}  dist={dict(dist)}  "
              f"(total A accounted for: {total_in_chains}/{N_AGENTS})")
        t_idx += 1

df = system.monitor.dataframe
print(f"\nDone. Steps: {len(df)}, final t={df['time'].iloc[-1]:.2f}")
print("Final observables:", df.iloc[-1][['free_monomer', 'z_bonds', 'alpha_bonds']].to_dict())

# ── Figure 1: dynamics ────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(df['time'], df['free_monomer'], label='free monomer (x,y,z all free)', lw=1.5)
ax.plot(df['time'], df['z_bonds'],      label='z-z bonds (B)',                 lw=1.5)
ax.plot(df['time'], df['alpha_bonds'],  label='α x-y bonds',                   lw=1.5)
ax.set_xlabel('Time')
ax.set_ylabel('Count')
ax.set_title(f'A(x,y,z) dynamics  [N={N_AGENTS}, seed={SEED}, commit={git_hash}]')
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)
fig.tight_layout()
dyn_path = f'file_outbox/dynamics_v2_{git_hash}.png'
fig.savefig(dyn_path, dpi=150, bbox_inches='tight')
print(f'Saved: {dyn_path}')

# ── Figure 2: chain length distributions at each snapshot ────────────────────
fig2, axes = plt.subplots(1, len(snapshots), figsize=(5 * len(snapshots), 4), sharey=False)
if len(snapshots) == 1:
    axes = [axes]
for ax, (t, dist) in zip(axes, sorted(snapshots.items())):
    lengths = sorted(dist.keys())
    counts  = [dist[L] for L in lengths]
    ax.bar(lengths, counts, color='steelblue', edgecolor='white', lw=0.5)
    ax.set_xlabel('Chain length (# A in α-bond component)')
    ax.set_ylabel('Count')
    ax.set_title(f't = {t}')
    ax.grid(True, axis='y', alpha=0.3)
fig2.suptitle(f'α-bond chain length distribution  [N={N_AGENTS}, seed={SEED}, commit={git_hash}]',
              fontsize=11)
fig2.tight_layout()
chain_path = f'file_outbox/chain_dist_v2_{git_hash}.png'
fig2.savefig(chain_path, dpi=150, bbox_inches='tight')
print(f'Saved: {chain_path}')
