"""
Activator-Inhibitor oscillator — Cao et al. 2015 (Nature Physics)
Single-run simulation via KaSim, plotting R, X, and free Mp.
"""

import subprocess
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

SEED     = 42
MAX_TIME = 500.0
PLOT_DT  = 0.2

KASIM   = os.path.expanduser('~/.opam/kappa/bin/KaSim')
KA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'ai_oscillator.ka')
OUT_CSV = '/tmp/ai_oscillator_out.csv'

# ── Run KaSim ─────────────────────────────────────────────────────────────────
print("Running KaSim...")
result = subprocess.run(
    [KASIM, '-i', KA_FILE, '-l', str(MAX_TIME), '-p', str(PLOT_DT),
     '-o', OUT_CSV, '-seed', str(SEED), '--no-log', '-mode', 'batch'],
    capture_output=True, text=True
)
if result.returncode != 0:
    print("STDERR:", result.stderr)
    raise RuntimeError("KaSim failed")
print("Done.")

# ── Parse output ──────────────────────────────────────────────────────────────
with open(OUT_CSV) as f:
    lines = f.readlines()

# KaSim output: two comment lines (#), then quoted CSV header, then data
lines  = [l for l in lines if not l.startswith('#')]
header = [h.strip().strip('"') for h in lines[0].split(',')]
data   = np.array([[float(v) for v in line.split(',')] for line in lines[1:] if line.strip()])

col = {name: i for i, name in enumerate(header)}
print("Columns:", header)

time = data[:, col['[T]']]
R    = data[:, col['R']]
X    = data[:, col['X']]
Mp   = data[:, col['Mp']]

# ── Plot ──────────────────────────────────────────────────────────────────────
git_hash = subprocess.check_output(
    ['git', 'rev-parse', '--short', 'HEAD'],
    cwd=os.path.dirname(os.path.abspath(__file__))
).decode().strip()

fig, axes = plt.subplots(3, 1, figsize=(13, 8), sharex=True)

axes[0].plot(time, R,  color='steelblue',   linewidth=0.7)
axes[0].set_ylabel('R (molecules)', fontsize=11)
axes[0].set_title(
    f'AI Oscillator — Cao et al. 2015  (V=50, γ=10⁻⁵, seed={SEED}, git:{git_hash})',
    fontsize=12)

axes[1].plot(time, X,  color='tomato',      linewidth=0.7)
axes[1].set_ylabel('X (molecules)', fontsize=11)

axes[2].plot(time, Mp, color='forestgreen', linewidth=0.7)
axes[2].set_ylabel('Mp (molecules)', fontsize=11)
axes[2].set_xlabel('Time', fontsize=11)

plt.tight_layout()
fname = f'ai_oscillator_single_run_{git_hash}.png'
fig.savefig(fname, dpi=150)
print(f"Saved: {fname}")
