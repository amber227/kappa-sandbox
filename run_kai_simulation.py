#!/usr/bin/env python3
"""
Run KaiABC oscillator simulation and analyze results
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from pykappa.system import System
import pandas as pd
import subprocess
import os

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Get git commit hash for reproducibility
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
except:
    git_hash = "unknown"

print("=" * 70)
print("KaiABC Circadian Oscillator Simulation")
print("=" * 70)
print(f"Random seed: {SEED}")
print(f"Git commit: {git_hash}")
print()

# Load the Kappa model
print("Loading Kappa model...")
with open("kai_abc_model.ka", "r") as f:
    kappa_model = f.read()

# Create system
print("Creating system...")
system = System.from_ka(kappa_model, seed=SEED)
print(f"System initialized with {len(system.observables)} observables")
print()

# Simulation parameters
max_time = 200.0  # Simulation time (arbitrary units)
print(f"Running simulation until t = {max_time}...")
print()

# Run simulation
update_count = 0
last_percent = -1
while system.time < max_time:
    system.update()
    update_count += 1

    # Progress indicator
    percent = int(100 * system.time / max_time)
    if percent > last_percent and percent % 10 == 0:
        print(f"  Progress: {percent}% (t = {system.time:.2f}, {update_count} updates)")
        last_percent = percent

print(f"\nSimulation complete!")
print(f"  Total updates: {update_count}")
print(f"  Final time: {system.time:.2f}")
print()

# Get results
monitor = system.monitor
df = monitor.dataframe

# Calculate derived observables
print("Calculating derived observables...")

# Mean phosphorylation level (weighted average)
df['mean_phos'] = (
    0 * df['C_p0'] +
    1 * df['C_p1'] +
    2 * df['C_p2'] +
    3 * df['C_p3'] +
    4 * df['C_p4'] +
    5 * df['C_p5'] +
    6 * df['C_p6']
) / (6 * 100)  # Total KaiC = 100, max phos per hexamer = 6

# Fraction in each conformational state
df['frac_active'] = df['C_active'] / 100
df['frac_inactive'] = df['C_inactive'] / 100

# Save data
print("Saving data...")
df.to_csv(f"kai_simulation_data_{git_hash}.csv", index=False)
print(f"  Saved: kai_simulation_data_{git_hash}.csv")
print()

# Print final statistics
print("Final state statistics:")
print(f"  Mean phosphorylation: {df['mean_phos'].iloc[-1]:.3f}")
print(f"  Active hexamers: {df['C_active'].iloc[-1]:.0f} ({df['frac_active'].iloc[-1]*100:.1f}%)")
print(f"  Inactive hexamers: {df['C_inactive'].iloc[-1]:.0f} ({df['frac_inactive'].iloc[-1]*100:.1f}%)")
print(f"  AC complexes: {df['AC_complex'].iloc[-1]:.0f}")
print(f"  BC complexes: {df['BC_complex'].iloc[-1]:.0f}")
print(f"  B2C complexes: {df['B2C_complex'].iloc[-1]:.0f}")
print(f"  Sequestered KaiA: {df['A_sequestered'].iloc[-1]:.0f}")
print(f"  Free KaiA: {df['A_free'].iloc[-1]:.0f}")
print()

# Check for oscillations
print("Checking for oscillatory behavior...")
mean_phos = df['mean_phos'].values
time = df['time'].values

# Simple peak detection (look for local maxima)
from scipy.signal import find_peaks
peaks, _ = find_peaks(mean_phos, prominence=0.05)
troughs, _ = find_peaks(-mean_phos, prominence=0.05)

print(f"  Detected {len(peaks)} peaks and {len(troughs)} troughs")
if len(peaks) >= 2:
    periods = np.diff(time[peaks])
    print(f"  Average period between peaks: {np.mean(periods):.2f} ± {np.std(periods):.2f}")
    print(f"  Oscillation amplitude: {mean_phos.max() - mean_phos.min():.3f}")
elif len(peaks) == 1:
    print(f"  Single peak detected - may be approaching first oscillation")
else:
    print(f"  No clear oscillations detected - system may be equilibrating")
print()

# Create visualizations
print("Creating visualizations...")
fig, axes = plt.subplots(3, 2, figsize=(14, 12))

# 1. Mean phosphorylation over time
ax = axes[0, 0]
ax.plot(df['time'], df['mean_phos'], 'b-', linewidth=2)
if len(peaks) > 0:
    ax.plot(time[peaks], mean_phos[peaks], 'ro', markersize=8, label='Peaks')
if len(troughs) > 0:
    ax.plot(time[troughs], mean_phos[troughs], 'go', markersize=8, label='Troughs')
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Mean Phosphorylation Level', fontsize=12)
ax.set_title('KaiC Phosphorylation Dynamics', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
if len(peaks) > 0 or len(troughs) > 0:
    ax.legend()

# 2. Phosphorylation distribution
ax = axes[0, 1]
for i in range(7):
    ax.plot(df['time'], df[f'C_p{i}'], label=f'p{i}', linewidth=1.5)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Phosphorylation Level Distribution', fontsize=14, fontweight='bold')
ax.legend(loc='best', ncol=2, fontsize=9)
ax.grid(True, alpha=0.3)

# 3. Conformational states
ax = axes[1, 0]
ax.plot(df['time'], df['C_active'], 'r-', label='Active', linewidth=2)
ax.plot(df['time'], df['C_inactive'], 'b-', label='Inactive', linewidth=2)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Conformational States', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# 4. Complex formation
ax = axes[1, 1]
ax.plot(df['time'], df['AC_complex'], label='AC (KaiA-KaiC)', linewidth=2)
ax.plot(df['time'], df['BC_complex'], label='BC (KaiB-KaiC)', linewidth=2)
ax.plot(df['time'], df['B2C_complex'], label='B₂C (2 KaiB)', linewidth=2, linestyle='--')
ax.plot(df['time'], df['A_sequestered'], label='Sequestered KaiA', linewidth=2)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Complex Formation', fontsize=14, fontweight='bold')
ax.legend(loc='best', fontsize=9)
ax.grid(True, alpha=0.3)

# 5. Free protein concentrations
ax = axes[2, 0]
ax.plot(df['time'], df['A_free'], label='Free KaiA', linewidth=2)
ax.plot(df['time'], df['B_free'], label='Free KaiB', linewidth=2)
ax.set_xlabel('Time', fontsize=12)
ax.set_ylabel('Count', fontsize=12)
ax.set_title('Free Protein Dynamics', fontsize=14, fontweight='bold')
ax.legend()
ax.grid(True, alpha=0.3)

# 6. Phase plot: mean phosphorylation vs conformational state
ax = axes[2, 1]
scatter = ax.scatter(df['mean_phos'], df['frac_active'],
                     c=df['time'], cmap='viridis', s=10, alpha=0.6)
ax.set_xlabel('Mean Phosphorylation Level', fontsize=12)
ax.set_ylabel('Fraction Active', fontsize=12)
ax.set_title('Phase Portrait (colored by time)', fontsize=14, fontweight='bold')
ax.grid(True, alpha=0.3)
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('Time', fontsize=10)

plt.tight_layout()
fig_name = f"kai_simulation_results_{git_hash}.png"
plt.savefig(fig_name, dpi=300, bbox_inches='tight')
print(f"  Saved: {fig_name}")

plt.savefig(fig_name.replace('.png', '.pdf'), bbox_inches='tight')
print(f"  Saved: {fig_name.replace('.png', '.pdf')}")

print()
print("=" * 70)
print("Simulation complete!")
print("=" * 70)
