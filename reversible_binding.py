"""
Reversible binding simulation using PyKappa.

This script reproduces the example from https://pykappa.org/examples/reversible_binding.html
It models a simple reversible binding interaction between molecules A and B.
"""

import random
import subprocess
from pykappa.system import System
import matplotlib.pyplot as plt

# Set random seed for reproducibility
random.seed(42)

# Get git commit hash for figure filename
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
except:
    git_hash = 'no-git'

# Define the system using Kappa notation
system = System.from_ka(
    """
    %init: 100 A(x[.])
    %init: 100 B(x[.])

    %obs: 'AB' |A(x[1]), B(x[1])|

    A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ 1, 1
    """
)

# Simulate until time 1
times = []
while system.time < 1:
    system.update()
times.append(system.time)

# Add 50 new molecules and track free A
system.mixture.instantiate("A(x[.]), B(x[.])", 50)
system["A"] = "|A(x[.])|"
while system["A"] > 10:
    system.update()
times.append(system.time)

# Continue simulation to time 2
while system.time < 2:
    system.update()
times.append(2)

# Plot results
system.monitor.plot(combined=True)
for time in times:
    plt.axvline(time, color="black", linestyle="dotted")

# Save figure with git hash
output_filename = f"reversible_binding_{git_hash}.png"
plt.savefig(output_filename, dpi=150, bbox_inches='tight')
print(f"Plot saved to {output_filename}")

# Display plot
plt.show()
