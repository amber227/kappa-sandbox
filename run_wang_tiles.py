#!/usr/bin/env python3
"""
Simulate Wang tiles self-assembly into alternating striped lattices
Based on Winfree 2000, Figure 1
"""

import random
import subprocess
from pykappa.system import System
import matplotlib.pyplot as plt

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)

# Get git commit hash
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
except:
    git_hash = 'no_git'

print("Building Wang tiles stripe model...")

# Define the system using Kappa notation
# Binding rules encode the stripe pattern:
# - Horizontal: A binds to B (alternation)
# - Vertical: like binds to like (A-A, B-B)

kappa_model = """
%init: 100 TileA(n[.], s[.], e[.], w[.])
%init: 100 TileB(n[.], s[.], e[.], w[.])

TileA(e[.]), TileB(w[.]) <-> TileA(e[1]), TileB(w[1]) @ 0.001, 0.1
TileB(e[.]), TileA(w[.]) <-> TileB(e[1]), TileA(w[1]) @ 0.001, 0.1

TileA(n[.]), TileA(s[.]) <-> TileA(n[1]), TileA(s[1]) @ 0.001, 0.1
TileB(n[.]), TileB(s[.]) <-> TileB(n[1]), TileB(s[1]) @ 0.001, 0.1

%obs: 'total_A' |TileA()|
%obs: 'total_B' |TileB()|
%obs: 'free_A' |TileA(n[.], s[.], e[.], w[.])|
%obs: 'free_B' |TileB(n[.], s[.], e[.], w[.])|
%obs: 'AB_horiz' |TileA(e[1]), TileB(w[1])|
%obs: 'BA_horiz' |TileB(e[1]), TileA(w[1])|
%obs: 'AA_vert' |TileA(n[1]), TileA(s[1])|
%obs: 'BB_vert' |TileB(n[1]), TileB(s[1])|
"""

system = System.from_ka(kappa_model, seed=SEED)

# Run simulation
max_time = 500.0
print(f"Running simulation until t={max_time}...")

while system.time < max_time:
    system.update()

print(f"Simulation complete at t={system.time:.2f}")

# Get results from monitor
monitor = system.monitor
df = monitor.dataframe

# Calculate derived observables (apply symmetry correction to vertical bonds)
df['total_h_bonds'] = df['AB_horiz'] + df['BA_horiz']
df['total_v_bonds'] = df['AA_vert']/2 + df['BB_vert']/2
df['total_bonds'] = df['total_h_bonds'] + df['total_v_bonds']

# Print summary statistics
print("\n" + "="*60)
print("SIMULATION SUMMARY")
print("="*60)
print(f"Final time: {df['time'].iloc[-1]:.2f}")
print(f"\nFinal observable values:")
print(f"  Total tiles A: {df['total_A'].iloc[-1]:.0f}")
print(f"  Total tiles B: {df['total_B'].iloc[-1]:.0f}")
print(f"  Free tiles A: {df['free_A'].iloc[-1]:.0f}")
print(f"  Free tiles B: {df['free_B'].iloc[-1]:.0f}")
print(f"\n  Horizontal bonds (A-B): {df['total_h_bonds'].iloc[-1]:.0f}")
print(f"  Vertical bonds (same-type): {df['total_v_bonds'].iloc[-1]:.0f}")
print(f"  Total bonds: {df['total_bonds'].iloc[-1]:.0f}")

# Create visualization
print("\nGenerating plots...")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# Plot 1: Tile counts
ax = axes[0, 0]
ax.plot(df['time'], df['total_A'], label='Total A', linewidth=2)
ax.plot(df['time'], df['total_B'], label='Total B', linewidth=2)
ax.plot(df['time'], df['free_A'], label='Free A', linestyle='--', alpha=0.7)
ax.plot(df['time'], df['free_B'], label='Free B', linestyle='--', alpha=0.7)
ax.set_xlabel('Time')
ax.set_ylabel('Count')
ax.set_title('Tile Populations')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 2: Bond formation
ax = axes[0, 1]
ax.plot(df['time'], df['total_h_bonds'], label='Horizontal (A-B)', linewidth=2)
ax.plot(df['time'], df['total_v_bonds'], label='Vertical (A-A, B-B)', linewidth=2)
ax.plot(df['time'], df['total_bonds'], label='Total bonds', linewidth=2, linestyle='--', color='black')
ax.set_xlabel('Time')
ax.set_ylabel('Bond Count')
ax.set_title('Bond Formation Dynamics')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 3: Individual bond types
ax = axes[1, 0]
ax.plot(df['time'], df['AB_horiz'], label='A-B (east-west)', linewidth=2)
ax.plot(df['time'], df['BA_horiz'], label='B-A (east-west)', linewidth=2)
ax.plot(df['time'], df['AA_vert']/2, label='A-A (north-south)', linestyle='--', linewidth=2)
ax.plot(df['time'], df['BB_vert']/2, label='B-B (north-south)', linestyle='--', linewidth=2)
ax.set_xlabel('Time')
ax.set_ylabel('Bond Count')
ax.set_title('Individual Bond Types')
ax.legend()
ax.grid(True, alpha=0.3)

# Plot 4: Assembly fraction
ax = axes[1, 1]
ax.plot(df['time'], (df['total_A'] - df['free_A']) / df['total_A'], label='A in assemblies', linewidth=2)
ax.plot(df['time'], (df['total_B'] - df['free_B']) / df['total_B'], label='B in assemblies', linewidth=2)
ax.set_xlabel('Time')
ax.set_ylabel('Fraction')
ax.set_title('Fraction of Tiles in Assemblies')
ax.set_ylim([0, 1])
ax.legend()
ax.grid(True, alpha=0.3)

plt.tight_layout()

# Save figure
output_filename = f"file_outbox/wang_tiles_stripes_{git_hash}.png"
plt.savefig(output_filename, dpi=300, bbox_inches='tight')
print(f"\nPlot saved to: {output_filename}")

plt.show()

print("\nSimulation complete!")
