#!/usr/bin/env python3
"""
KaiABC Circadian Oscillator Model

Based on van Zon et al. (2007) "An allosteric model of circadian KaiC phosphorylation"
Implements the full model with:
- KaiC hexamers with Active/Inactive conformational states
- 7 phosphorylation levels (0-6 monomers phosphorylated)
- KaiA-stimulated phosphorylation with differential affinity
- KaiB stabilization and KaiA sequestration
"""

import random
import numpy as np
import matplotlib.pyplot as plt
from pykappa.system import System
import pandas as pd

# Set random seed for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

def generate_kai_model():
    """
    Generate the complete KaiABC Kappa model as a string.

    Agent structure:
    - C(state{active inactive}, phos{p0 p1 p2 p3 p4 p5 p6}, kaiA, kaiB1, kaiB2)
    - A(x) - KaiA dimer with binding site
    - B(c, a) - KaiB dimer: c binds KaiC, a binds KaiA when sequestering
    """

    # Parameters (estimated based on paper constraints)
    # Time units: arbitrary (not calibrated to 24h without fitted parameters)
    params = {
        # Conformational flip parameters
        'k0_flip': 0.5,      # base flip rate
        'c_param': 1.8,      # exp dependence on phosphorylation (c>1 favors inactive when phosphorylated)

        # KaiA binding to active KaiC
        'k_Af': 5.0,         # forward binding rate (fast)
        'k_Ab_base': 1.0,    # backward binding base rate
        'alpha': 1.5,        # differential affinity (k_Ab increases with phos level)

        # Phosphorylation rates
        'k_pf': 2.0,         # KaiA-stimulated phosphorylation (fast)
        'k_ps_a': 0.05,      # spontaneous phosphorylation, active state (slow)
        'k_dps_a': 0.2,      # spontaneous dephosphorylation, active state
        'k_ps_i': 0.02,      # spontaneous phosphorylation, inactive state (very slow)
        'k_dps_i': 0.2,      # spontaneous dephosphorylation, inactive state

        # KaiB binding to inactive KaiC
        'k_Bf': 5.0,         # forward binding (fast)
        'k_Bb': 0.5,         # backward unbinding

        # KaiA sequestration by B2C complex
        'k_Aseq_f': 10.0,    # forward (high affinity)
        'k_Aseq_b': 0.01,    # backward (very slow unbinding)
    }

    # Initial concentrations (following experiment ratios)
    # [C]:[A]:[B] = 1:3:1
    n_KaiC = 100
    n_KaiA = 300
    n_KaiB = 100

    # Build Kappa model string
    lines = []
    lines.append("// KaiABC Circadian Oscillator Model")
    lines.append("// Based on van Zon et al. (2007)")
    lines.append("")

    # Parameters
    lines.append("// === PARAMETERS ===")
    for pname, pval in params.items():
        lines.append(f"%var: '{pname}' {pval}")
    lines.append("")

    # Initial conditions
    lines.append("// === INITIAL CONDITIONS ===")
    lines.append(f"%init: {n_KaiC} C(state{{active}}, phos{{p0}}, kaiA[.], kaiB1[.], kaiB2[.])")
    lines.append(f"%init: {n_KaiA} A(x[.])")
    lines.append(f"%init: {n_KaiB} B(c[.], a[.])")
    lines.append("")

    # === RULES ===
    lines.append("// === RULES ===")
    lines.append("")

    # 1. Conformational transitions (Active <-> Inactive)
    lines.append("// 1. Conformational transitions (phosphorylation-dependent)")
    for i in range(7):
        # Forward rate: f_i = k0 * c^i
        # Backward rate: b_i = k0 * c^(-i) = k0 / c^i
        f_rate = f"'k0_flip' * ('c_param' ^ {i})"
        b_rate = f"'k0_flip' / ('c_param' ^ {i})" if i > 0 else "'k0_flip'"

        lines.append(f"C(state{{active}}, phos{{p{i}}}, kaiA[.]) -> C(state{{inactive}}, phos{{p{i}}}, kaiA[.]) @ {f_rate}")
        lines.append(f"C(state{{inactive}}, phos{{p{i}}}, kaiB1[.], kaiB2[.]) -> C(state{{active}}, phos{{p{i}}}, kaiB1[.], kaiB2[.]) @ {b_rate}")
    lines.append("")

    # 2. KaiA binding to active KaiC (differential affinity)
    lines.append("// 2. KaiA binding to active KaiC (differential affinity)")
    for i in range(7):
        # Backward rate increases with phosphorylation: k_Ab * alpha^i
        k_ab = f"'k_Ab_base' * ('alpha' ^ {i})" if i > 0 else "'k_Ab_base'"
        lines.append(f"C(state{{active}}, phos{{p{i}}}, kaiA[.]), A(x[.]) <-> C(state{{active}}, phos{{p{i}}}, kaiA[1]), A(x[1]) @ 'k_Af', {k_ab}")
    lines.append("")

    # 3. KaiA-stimulated phosphorylation (releases KaiA)
    lines.append("// 3. KaiA-stimulated phosphorylation")
    for i in range(6):  # p0 to p5
        lines.append(f"C(state{{active}}, phos{{p{i}}}, kaiA[1]), A(x[1]) -> C(state{{active}}, phos{{p{i+1}}}, kaiA[.]), A(x[.]) @ 'k_pf'")
    lines.append("")

    # 4. Spontaneous phosphorylation (active state)
    lines.append("// 4. Spontaneous phosphorylation (active, slow)")
    for i in range(6):
        lines.append(f"C(state{{active}}, phos{{p{i}}}) -> C(state{{active}}, phos{{p{i+1}}}) @ 'k_ps_a'")
    lines.append("")

    # 5. Spontaneous dephosphorylation (active state)
    lines.append("// 5. Spontaneous dephosphorylation (active)")
    for i in range(1, 7):  # p1 to p6
        lines.append(f"C(state{{active}}, phos{{p{i}}}) -> C(state{{active}}, phos{{p{i-1}}}) @ 'k_dps_a'")
    lines.append("")

    # 6. KaiB binding to inactive KaiC (sequential: 2 binding sites)
    lines.append("// 6. KaiB binding to inactive KaiC (2 sites)")
    # First KaiB
    for i in range(7):
        lines.append(f"C(state{{inactive}}, phos{{p{i}}}, kaiB1[.]), B(c[.]) <-> C(state{{inactive}}, phos{{p{i}}}, kaiB1[1]), B(c[1], a[.]) @ 'k_Bf', 'k_Bb'")
    # Second KaiB
    for i in range(7):
        lines.append(f"C(state{{inactive}}, phos{{p{i}}}, kaiB1[_], kaiB2[.]), B(c[.]) <-> C(state{{inactive}}, phos{{p{i}}}, kaiB1[_], kaiB2[2]), B(c[2], a[.]) @ 'k_Bf', 'k_Bb'")
    lines.append("")

    # 7. Spontaneous dephosphorylation (inactive state, with or without KaiB)
    lines.append("// 7. Spontaneous dephosphorylation (inactive)")
    for i in range(1, 7):
        lines.append(f"C(state{{inactive}}, phos{{p{i}}}) -> C(state{{inactive}}, phos{{p{i-1}}}) @ 'k_dps_i'")
    lines.append("")

    # 8. Weak phosphorylation (inactive state)
    lines.append("// 8. Spontaneous phosphorylation (inactive, very slow)")
    for i in range(6):
        lines.append(f"C(state{{inactive}}, phos{{p{i}}}) -> C(state{{inactive}}, phos{{p{i+1}}}) @ 'k_ps_i'")
    lines.append("")

    # 9. KaiA sequestration by B2C complex
    # Only for p1, p2, p3, p4 (as stated in paper)
    # B bound to C can bind A at its a site
    lines.append("// 9. KaiA sequestration by KaiB-KaiC complexes (p1-p4 only)")
    for i in [1, 2, 3, 4]:
        # First KaiA binds to first KaiB
        lines.append(f"B(c[1], a[.]), C(state{{inactive}}, phos{{p{i}}}, kaiB1[1]), A(x[.]) <-> B(c[1], a[2]), C(state{{inactive}}, phos{{p{i}}}, kaiB1[1]), A(x[2]) @ 'k_Aseq_f', 'k_Aseq_b'")
        # Second KaiA binds to second KaiB
        lines.append(f"B(c[1], a[.]), C(state{{inactive}}, phos{{p{i}}}, kaiB2[1]), A(x[.]) <-> B(c[1], a[2]), C(state{{inactive}}, phos{{p{i}}}, kaiB2[1]), A(x[2]) @ 'k_Aseq_f', 'k_Aseq_b'")
    lines.append("")

    # === OBSERVABLES ===
    lines.append("// === OBSERVABLES ===")
    lines.append("")

    # Individual phosphorylation levels
    for i in range(7):
        lines.append(f"%obs: 'C_p{i}' |C(phos{{p{i}}})|")
    lines.append("")

    # Conformational states
    lines.append("%obs: 'C_active' |C(state{active})|")
    lines.append("%obs: 'C_inactive' |C(state{inactive})|")
    lines.append("")

    # Complexes
    lines.append("%obs: 'AC_complex' |C(kaiA[1]), A(x[1])|")
    lines.append("%obs: 'BC_complex' |C(kaiB1[_])|")  # At least one KaiB bound
    lines.append("%obs: 'B2C_complex' |C(kaiB1[_], kaiB2[_])|")  # Both KaiB bound
    lines.append("%obs: 'A_sequestered' |B(c[_], a[1]), A(x[1])|")  # KaiA bound to KaiB
    lines.append("")

    # Free proteins
    lines.append("%obs: 'A_free' |A(x[.])|")
    lines.append("%obs: 'B_free' |B(c[.], a[.])|")

    return "\n".join(lines), params, n_KaiC

# Generate model
kappa_model, parameters, n_KaiC = generate_kai_model()

# Save model to file
with open("kai_abc_model.ka", "w") as f:
    f.write(kappa_model)

print("KaiABC model generated and saved to kai_abc_model.ka")
print(f"Model contains {len(kappa_model.splitlines())} lines")
print(f"\nAgent counts: {n_KaiC} KaiC, {n_KaiC*3} KaiA, {n_KaiC} KaiB")
print("\nParameters:")
for k, v in parameters.items():
    print(f"  {k}: {v}")
