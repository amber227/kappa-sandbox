"""
Contact map → Kappa model.

Agents and sites interpreted from the contact map image:
  B(b, a)      -- b: B-B self-binding (self-loop), a: binds A.z
  A(z, d, s)   -- z: binds B.a, d: binds Alpha.x, s: binds Alpha.y
  Alpha(x,y,c) -- x: binds A.d, y: binds A.s, c: Alpha self-binding (contact-map loop on y)

Note: Alpha's self-binding (y-y loop in the contact map) is modeled with a
separate site 'c' in simulation to avoid a PyKappa parity bug: when site y is
shared between A-binding and self-binding, A-Alpha-y events shift Alpha(y[.])
count by ±1, causing n_embeddings % n_symmetries ≠ 0 for the symmetric
Alpha-Alpha rule. Using site 'c' isolates the homodimer count parity.
"""

import random
import subprocess
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Arc
from pykappa.system import System

# Reproducibility
SEED = 42
random.seed(SEED)

result = subprocess.run(
    ["git", "rev-parse", "--short", "HEAD"],
    capture_output=True, text=True, cwd="/home/ec2-user/kappa-sandbox"
)
git_hash = result.stdout.strip()

# ============================================================
# Kappa Model
# ============================================================
kappa_model = """
%init: 100 B(b[.], a[.])
%init: 100 A(z[.], d[.], s[.])
%init: 100 Alpha(x[.], y[.], c[.])

B(b[.]), B(b[.]) <-> B(b[1]), B(b[1]) @ 0.002, 0.1
B(a[.]), A(z[.]) <-> B(a[1]), A(z[1]) @ 0.005, 0.1
A(d[.]), Alpha(x[.]) <-> A(d[1]), Alpha(x[1]) @ 0.005, 0.1
A(s[.]), Alpha(y[.]) <-> A(s[1]), Alpha(y[1]) @ 0.003, 0.1
Alpha(c[.]), Alpha(c[.]) <-> Alpha(c[1]), Alpha(c[1]) @ 0.002, 0.1

%obs: 'B_BB' |B(b[1]), B(b[1])|
%obs: 'BA' |B(a[1]), A(z[1])|
%obs: 'A_Alpha_x' |A(d[1]), Alpha(x[1])|
%obs: 'A_Alpha_y' |A(s[1]), Alpha(y[1])|
%obs: 'Alpha_AA' |Alpha(c[1]), Alpha(c[1])|
"""

system = System.from_ka(kappa_model, seed=SEED)

print("Simulating...")
max_time = 300.0
while system.time < max_time:
    system.update()

df = system.monitor.dataframe
# Homodimer observables double-count (two ordered embeddings per dimer)
df["B_dimers"] = df["B_BB"] / 2
df["Alpha_dimers"] = df["Alpha_AA"] / 2

print(f"Simulation complete. Steps: {len(df)}, Final time: {df['time'].iloc[-1]:.1f}")

# ============================================================
# Figure 1: Contact Map
# ============================================================
fig_cm, ax = plt.subplots(figsize=(6, 9))
ax.set_xlim(-2.2, 2.2)
ax.set_ylim(-2.8, 3.2)
ax.set_aspect("equal")
ax.axis("off")
ax.set_title("Contact Map", fontsize=16, fontweight="bold", pad=10)

pos = {"B": (0.0, 2.1), "A": (0.0, 0.5), "Alpha": (0.0, -1.3)}
radii = {"B": 0.55, "A": 0.65, "Alpha": 0.90}
colors = {"B": "#aed6f1", "A": "#a9dfbf", "Alpha": "#f9e79f"}

for name, (cx, cy) in pos.items():
    r = radii[name]
    circle = plt.Circle((cx, cy), r, color=colors[name], ec="black", lw=2, zorder=2)
    ax.add_patch(circle)
    label = "α" if name == "Alpha" else name
    ax.text(cx, cy, label, ha="center", va="center", fontsize=15,
            fontweight="bold", zorder=3)

def self_loop(ax, cx, cy, r, site_label, angle_deg=90, color="black", loop_r=0.28):
    """Decorative self-loop at angle_deg on the agent circle."""
    rad = np.radians(angle_deg)
    # Attach point on circle edge
    ax_pt = cx + r * np.cos(rad)
    ay_pt = cy + r * np.sin(rad)
    # Loop center slightly outside
    lx = cx + (r + loop_r) * np.cos(rad)
    ly = cy + (r + loop_r) * np.sin(rad)
    loop = plt.Circle((lx, ly), loop_r, fill=False, ec=color, lw=2, zorder=4)
    ax.add_patch(loop)
    # Site label
    label_x = cx + (r + 2 * loop_r + 0.1) * np.cos(rad)
    label_y = cy + (r + 2 * loop_r + 0.1) * np.sin(rad)
    ax.text(label_x, label_y, site_label, fontsize=9, color=color,
            ha="center", va="center", fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.15", fc="white", ec=color, lw=0.8), zorder=5)

def edge(ax, p1, p2, r1, r2, lbl1, lbl2, offset=0.0, color="black"):
    """Draw labeled edge between two agent circles."""
    x1, y1 = p1
    x2, y2 = p2
    dx, dy = x2 - x1, y2 - y1
    dist = np.hypot(dx, dy)
    ux, uy = dx / dist, dy / dist
    px, py = -uy * offset, ux * offset

    sx = x1 + ux * r1 + px
    sy = y1 + uy * r1 + py
    ex = x2 - ux * r2 + px
    ey = y2 - uy * r2 + py

    ax.annotate("", xy=(ex, ey), xytext=(sx, sy),
                arrowprops=dict(arrowstyle="-", color=color, lw=2), zorder=1)

    # Site labels near each endpoint
    frac = 0.18
    lx1 = sx + (ex - sx) * frac + px * 0.3
    ly1 = sy + (ey - sy) * frac + py * 0.3
    lx2 = sx + (ex - sx) * (1 - frac) + px * 0.3
    ly2 = sy + (ey - sy) * (1 - frac) + py * 0.3

    for lx, ly, lbl in [(lx1, ly1, lbl1), (lx2, ly2, lbl2)]:
        ax.text(lx, ly, lbl, fontsize=8, color=color, ha="center", va="center",
                fontweight="bold",
                bbox=dict(boxstyle="round,pad=0.12", fc="white", ec=color, lw=0.7), zorder=5)

# Self-loops
self_loop(ax, *pos["B"], radii["B"], "b", angle_deg=90, color="#1a5276")
self_loop(ax, *pos["Alpha"], radii["Alpha"], "y", angle_deg=270, color="#7d6608")

# B—A edge
edge(ax, pos["B"], pos["A"], radii["B"], radii["A"], "a", "z", offset=0.0, color="#5d6d7e")

# A—Alpha via x  (left)
edge(ax, pos["A"], pos["Alpha"], radii["A"], radii["Alpha"], "d", "x", offset=-0.32, color="#1e8449")

# A—Alpha via y  (right)
edge(ax, pos["A"], pos["Alpha"], radii["A"], radii["Alpha"], "s", "y", offset=+0.32, color="#7d6608")

legend_items = [
    mpatches.Patch(color=colors["B"],     label="B"),
    mpatches.Patch(color=colors["A"],     label="A"),
    mpatches.Patch(color=colors["Alpha"], label="α"),
]
ax.legend(handles=legend_items, loc="lower right", fontsize=10)

fig_cm.tight_layout()
cm_path = f"file_outbox/contact_map_{git_hash}.png"
fig_cm.savefig(cm_path, dpi=150, bbox_inches="tight")
print(f"Saved: {cm_path}")

# ============================================================
# Figure 2: Simulation Dynamics
# ============================================================
fig_sim, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

ax1.plot(df["time"], df["B_dimers"],    label="B–B dimers (b|b)",    color="#1a5276", lw=1.5)
ax1.plot(df["time"], df["BA"],           label="B–A complex (a|z)",   color="#5d6d7e", lw=1.5)
ax1.plot(df["time"], df["Alpha_dimers"],label="α–α dimers (c|c)",    color="#7d6608", lw=1.5)
ax1.set_ylabel("Complex count")
ax1.set_title(f"Dynamics — Contact Map Model  [seed={SEED}, commit={git_hash}]")
ax1.legend(fontsize=9)
ax1.grid(True, alpha=0.3)

ax2.plot(df["time"], df["A_Alpha_x"],   label="A–α complex (d|x)",  color="#1e8449", lw=1.5)
ax2.plot(df["time"], df["A_Alpha_y"],   label="A–α complex (s|y)",  color="#922b21", lw=1.5)
ax2.set_xlabel("Time (a.u.)")
ax2.set_ylabel("Complex count")
ax2.legend(fontsize=9)
ax2.grid(True, alpha=0.3)

fig_sim.tight_layout()
sim_path = f"file_outbox/dynamics_{git_hash}.png"
fig_sim.savefig(sim_path, dpi=150, bbox_inches="tight")
print(f"Saved: {sim_path}")

print("\n--- Steady-state (last time point) ---")
last = df.iloc[-1]
for col, lbl in [("B_dimers","B-B dimers"), ("BA","B-A"), ("A_Alpha_x","A-α(x)"),
                  ("A_Alpha_y","A-α(y)"), ("Alpha_dimers","α-α dimers")]:
    print(f"  {lbl:15s}: {last[col]:.1f}")
