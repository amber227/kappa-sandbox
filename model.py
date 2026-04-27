"""
Simple binding and phosphorylation model.

Agent specification:
- A(bind): Agent A with a binding site
- B(bind, res~u~p): Agent B with a binding site and a residue that can be unphosphorylated (u) or phosphorylated (p)

Rules:
1. Reversible binding between A and B
2. Phosphorylation of B when bound to A (irreversible)
"""

import random
from pykappa import KappaModel

# Set random seed for reproducibility
random.seed(42)

# Create model
model = KappaModel()

# Define agents
model.add_agent("A(bind)")
model.add_agent("B(bind, res~u~p)")

# Rule 1: Reversible binding between A and B
model.add_rule(
    "bind",
    lhs="A(bind[.]), B(bind[.])",
    rhs="A(bind[1]), B(bind[1])",
    rate_fwd=1.0,  # Forward binding rate
    rate_bck=0.1   # Backward unbinding rate
)

# Rule 2: Phosphorylation of B when bound to A (irreversible)
model.add_rule(
    "phosphorylate",
    lhs="A(bind[1]), B(bind[1], res~u)",
    rhs="A(bind[1]), B(bind[1], res~p)",
    rate_fwd=0.5   # Phosphorylation rate
)

# Define initial mixture
model.add_init("A(bind[.])", 100)
model.add_init("B(bind[.], res~u)", 100)

# Define observables
model.add_obs("A_free", "A(bind[.])")
model.add_obs("B_free", "B(bind[.])")
model.add_obs("AB_complex", "A(bind[1]), B(bind[1])")
model.add_obs("B_u", "B(res~u)")
model.add_obs("B_p", "B(res~p)")

print("Model scaffold created successfully")
print(f"\nAgents: {len(model.agents)}")
print(f"Rules: {len(model.rules)}")
print(f"Observables: {len(model.observables)}")
