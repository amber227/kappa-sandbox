# KaiABC Circadian Oscillator - Kappa Modeling Summary

**Paper**: van Zon et al. (2007) "An allosteric model of circadian KaiC phosphorylation"
**System**: In vitro reconstitution of cyanobacterial circadian clock with KaiA, KaiB, and KaiC proteins

---

## AGENTS

### 1. KaiC Hexamer (C)
- **Oligomeric state**: Hexamer of 6 identical monomers (does not dissociate in this model)
- **Phosphorylation sites**: Each monomer can be phosphorylated or unphosphorylated
  - Paper simplifies to binary states (p/u) though multiple phosphorylation sites exist in reality
  - Hexamer phosphorylation level: i = 0 to 6 (number of phosphorylated monomers)
- **Conformational states**:
  - **Active (A)**: Favors phosphorylation, can bind KaiA
  - **Inactive (I)**: Favors dephosphorylation, can bind KaiB
- **Nucleotide binding**:
  - ATP binds preferentially to unphosphorylated monomers
  - ADP binds preferentially to phosphorylated monomers
  - Nucleotide binding favors active conformation
  - Phosphorylation favors inactive conformation
- **States notation**:
  - C_i = active hexamer with i phosphorylated monomers
  - C̃_i = inactive hexamer with i phosphorylated monomers
- **Key property**: The model assumes MWC-like allostery - all 6 monomers in a hexamer must be in the same conformational state (all active or all inactive)

**Initial state**: Fully unphosphorylated active state C_0

### 2. KaiA Dimer (A)
- **Oligomeric state**: Dimer (does not dissociate)
- **Function**: Stimulates KaiC phosphorylation
- **Binding**:
  - Binds to CII domain of active KaiC hexamers
  - Maximum 1 KaiA dimer per KaiC hexamer (in absence of KaiB)
  - Binding affinity decreases as KaiC phosphorylation level increases (differential affinity)
  - Can be sequestered by KaiB-KaiC complexes
- **States**: Free or bound to KaiC (active state) or bound to KaiB-KaiC complex (inactive state)

**Concentration**: ~3× less abundant than KaiC hexamers in experiments ([A]_T ≈ 1.75 μM, [C]_T ≈ 0.58 μM, so [A]_T/[C]_T ≈ 3)

### 3. KaiB Dimer (B)
- **Oligomeric state**: Dimer or tetramer (paper mentions both; model uses dimer)
- **Function**:
  - Stabilizes inactive KaiC conformation
  - Sequesters KaiA away from active KaiC
- **Binding**:
  - Binds only to inactive KaiC hexamers
  - Maximum 2 KaiB dimers per inactive KaiC hexamer
  - KaiB-bound inactive KaiC can bind up to 2 KaiA dimers (specifically B₂C̃_4, B₂C̃_3, B₂C̃_2, B₂C̃_1 states)

**Concentration**: Equal to KaiC hexamer concentration ([B]_T ≈ 0.58 μM, [B]_T/[C]_T ≈ 1)

### 4. Complex States
- **AC_i**: KaiA dimer bound to active KaiC with i phosphorylated monomers
- **B₂C̃_i**: 2 KaiB dimers bound to inactive KaiC with i phosphorylated monomers
- **A₂B₂C̃_i**: 2 KaiA + 2 KaiB dimers bound to inactive KaiC with i phosphorylated monomers

---

## INTERACTIONS

### 1. Conformational Transitions (Allosteric Flips)

**Active ↔ Inactive state switching**

```
C_i ⟷ C̃_i  (for i = 0, 1, 2, 3, 4, 5, 6)
     f_i (forward: active → inactive)
     b_i (backward: inactive → active)
```

**Mechanism**: Cooperative conformational change of entire hexamer

**Rate dependence on phosphorylation level**:
- Forward rate: f_i = k₀ exp[ΔG(i)/2] = c^i
- Backward rate: b_i = k₀ exp[-ΔG(i)/2] = c^(-i)
- Where: ΔG(i) = i·ΔG_p + (6-i)·ΔG_u
  - ΔG_p: free energy difference (I vs A) for phosphorylated monomer
  - ΔG_u: free energy difference (I vs A) for unphosphorylated monomer
  - c = exp[(ΔG_p - ΔG_u)/2]

**Key parameters** (from model):
- c > 1 (phosphorylation favors inactive; unphosphorylated favors active)
- Active state has lower free energy overall (in absence of KaiB)
- f₆ and b₀ are critical for period determination
- Most flips occur at high (C_6 → C̃_6) or low (C̃_0 → C_0) phosphorylation

**Directionality**:
- Highly phosphorylated hexamers (i ≈ 6) prefer to flip A → I
- Weakly phosphorylated hexamers (i ≈ 0) prefer to flip I → A
- Intermediate phosphorylation states flip rarely (high energy barrier)

### 2. KaiA Binding to Active KaiC

**Binding/unbinding** (reversible):
```
C_i + A ⟷ AC_i  (for i = 0, 1, 2, 3, 4, 5, 6)
       k^i_Af (forward)
       k^i_Ab (backward)
```

**Mechanism**: Single KaiA dimer binds CII domain of active KaiC hexamer

**Differential affinity** (key for synchronization):
- Dissociation constant increases with phosphorylation level
- k^i_Ab = k^0_Ab · α^i, where α > 1
- Less phosphorylated KaiC hexamers bind KaiA more tightly
- This creates competition favoring "laggard" hexamers

**Stoichiometry**: Maximum 1 KaiA per active KaiC hexamer (without KaiB)

**Rate magnitudes**: Binding/unbinding much faster than phosphorylation (for temperature compensation)

### 3. Phosphorylation of Active KaiC (KaiA-stimulated)

**Phosphorylation**:
```
AC_i → C_(i+1) + A  (for i = 0, 1, 2, 3, 4, 5)
      k_pf
```

**Mechanism**:
- KaiA-bound active KaiC undergoes phosphorylation
- ATP hydrolysis transfers phosphate to KaiC monomer
- KaiA is released after phosphorylation event
- Paper suggests this is catalytic activity of KaiA

**Dependencies**:
- Requires KaiA to be bound
- Requires ATP binding (assumed fast equilibrium)
- Only occurs in active conformation

**Reversibility**: Effectively irreversible in this direction (ATP hydrolysis provides driving force)

### 4. Spontaneous Phosphorylation (Active KaiC)

**Weak autophosphorylation**:
```
C_i → C_(i+1)  (for i = 0, 1, 2, 3, 4, 5)
     k_ps
```

**Mechanism**: ATP-dependent autophosphorylation activity of KaiC (without KaiA)

**Rate**: Much slower than KaiA-stimulated phosphorylation

**Key constraint**: k_ps < k̃_dps (spontaneous phosphorylation slower than spontaneous dephosphorylation, ensuring KaiC alone reaches low phosphorylation level)

### 5. Spontaneous Dephosphorylation (Active KaiC)

**Autodephosphorylation**:
```
C_i → C_(i-1)  (for i = 1, 2, 3, 4, 5, 6)
     k_dps
```

**Mechanism**: Intrinsic phosphatase activity of KaiC

**Rate**: Faster than spontaneous phosphorylation (k_dps > k_ps)

### 6. KaiB Binding to Inactive KaiC

**Binding/unbinding** (reversible):
```
C̃_i + 2B ⟷ B₂C̃_i  (for i = 0, 1, 2, 3, 4, 5, 6)
        k̃^i_Bf (forward)
        k̃^i_Bb (backward)
```

**Mechanism**:
- Two KaiB dimers bind to inactive KaiC hexamer
- Stabilizes inactive conformation (shifts equilibrium toward I state)
- Does not directly affect phosphorylation/dephosphorylation rates

**Stoichiometry**: Maximum 2 KaiB dimers per inactive KaiC

**Function**: Restores capacity for phosphorylation cycling by stabilizing inactive state

**Rate magnitudes**: Fast binding/unbinding (for temperature compensation)

### 7. Dephosphorylation of Inactive KaiC

**Spontaneous dephosphorylation**:
```
C̃_i → C̃_(i-1)  (for i = 1, 2, 3, 4, 5, 6)
     k̃_dps

B₂C̃_i → B₂C̃_(i-1)  (for i = 1, 2, 3, 4, 5, 6)
       k̃_dps
```

**Mechanism**: Intrinsic phosphatase activity in inactive state

**Key property**: Same rate whether or not KaiB is bound (KaiB doesn't directly affect dephosphorylation)

**Comparison**: k̃_dps rate similar to k_dps (both autodephosphorylation)

### 8. Weak Phosphorylation of Inactive KaiC

**Spontaneous phosphorylation**:
```
C̃_i → C̃_(i+1)  (for i = 0, 1, 2, 3, 4, 5)
     k̃_ps

B₂C̃_i → B₂C̃_(i+1)  (for i = 0, 1, 2, 3, 4, 5)
       k̃_ps
```

**Mechanism**: Weak autophosphorylation in inactive state

**Rate**: Very slow; k̃_ps < k̃_dps (net flux favors dephosphorylation in inactive state)

### 9. KaiA Sequestration by KaiB-KaiC Complex

**KaiA binding to B₂C̃** (high affinity):
```
B₂C̃_i + 2A ⟷ A₂B₂C̃_i  (for i = 1, 2, 3, 4)
          k̃^i_Af (forward)
          k̃^i_Ab (backward)
```

**Mechanism**:
- KaiB-bound inactive KaiC can bind up to 2 KaiA dimers
- Specifically states i = 1, 2, 3, 4 (not i = 0, 5, 6)
- This sequesters KaiA away from active KaiC

**Function (critical for synchronization)**:
- Reduces free KaiA concentration
- Creates competition for limited KaiA
- Inactive "laggard" hexamers sequester KaiA from active "front-runner" hexamers
- This is the differential affinity mechanism at the bottom of the cycle

**Affinity**: Very high (K_d much smaller than protein concentrations)

**Stoichiometry**: Maximum 2 KaiA per B₂C̃_i complex

### 10. Dephosphorylation of Sequestered Complex

**Dephosphorylation while KaiA is sequestered**:
```
A₂B₂C̃_i → A₂B₂C̃_(i-1)  (for i = 1, 2, 3, 4, 5, 6)
         k̃_dps
```

**Mechanism**: Dephosphorylation continues even with KaiA and KaiB bound

**Rate**: Same k̃_dps as free inactive KaiC (KaiA/KaiB don't affect dephosphorylation rate)

**Phosphorylation**:
```
A₂B₂C̃_i → A₂B₂C̃_(i+1)  (for i = 0, 1, 2, 3, 4, 5)
         k̃_ps
```

**Rate**: Same k̃_ps as free inactive KaiC

---

## DEPENDENCIES AND LOGIC

### Causal Chain (Oscillation Cycle)

The oscillation proceeds through a specific sequence:

1. **Phosphorylation Phase** (Active state, low i → high i):
   - Start: C_0 (unphosphorylated, active)
   - KaiA binds: C_i + A ⟷ AC_i
   - Phosphorylation: AC_i → C_(i+1) + A
   - Continues until i ≈ 6
   - Free KaiA concentration drops near zero (competition)

2. **Transition to Inactive** (i ≈ 6):
   - Conformational flip: C_6 → C̃_6 (favored when highly phosphorylated)
   - KaiA is released from active KaiC

3. **Dephosphorylation Phase** (Inactive state, high i → low i):
   - KaiB binds: C̃_i + 2B ⟷ B₂C̃_i
   - KaiA sequestered: B₂C̃_i + 2A ⟷ A₂B₂C̃_i (for i = 1-4)
   - Dephosphorylation: C̃_i → C̃_(i-1) (or B₂C̃_i → B₂C̃_(i-1))
   - Continues until i ≈ 0

4. **Transition to Active** (i ≈ 0):
   - Conformational flip: C̃_0 → C_0 (favored when unphosphorylated)
   - KaiB is released
   - Cycle repeats

**Period**: ~24 hours in experiments

### Conditional Dependencies

1. **KaiA binding requires active state**:
   - Single KaiA binding: Requires C_i (active), not C̃_i (inactive)
   - KaiA sequestration: Requires B₂C̃_i (inactive with KaiB)

2. **KaiB binding requires inactive state**:
   - Can only bind to C̃_i, not C_i

3. **Conformational flip probability depends on phosphorylation**:
   - A → I flip (f_i) increases exponentially with i
   - I → A flip (b_i) increases exponentially with (6-i)
   - Flips primarily occur at extremes (i ≈ 0 or i ≈ 6)

4. **Phosphorylation stimulation**:
   - Active state: Fast when KaiA bound, slow spontaneous rate
   - Inactive state: Only slow spontaneous rate (net flux toward dephosphorylation)

5. **KaiA sequestration is phosphorylation-level specific**:
   - Only B₂C̃_1, B₂C̃_2, B₂C̃_3, B₂C̃_4 bind KaiA strongly
   - B₂C̃_0, B₂C̃_5, B₂C̃_6 do not sequester KaiA

### Synchronization Mechanism (Differential Affinity)

**During phosphorylation phase**:
- All hexamers compete for limited KaiA
- Less phosphorylated hexamers have higher affinity (k^i_Ab ∝ α^i, α > 1)
- "Laggards" (low i) outcompete "front-runners" (high i) for KaiA
- Laggards phosphorylate faster, front-runners slow down
- Population synchronizes

**During dephosphorylation phase**:
- Hexamers that remain inactive (laggards) sequester KaiA into A₂B₂C̃_i
- Hexamers that flip back to active (front-runners) cannot access KaiA
- Front-runners' phosphorylation slows (only spontaneous k_ps)
- Laggards catch up by completing dephosphorylation
- Population synchronizes at bottom of cycle

**Critical requirement**: Limited KaiA ([A]_T much less than [C]_T in model; experiments show [A]_T ≈ 3[C]_T but minimum [A]_T/[C]_T ≈ 0.25 needed)

### Feedback Structures

**Positive feedback** (self-amplifying):
- Phosphorylation favors inactive state → conformational flip → dephosphorylation
- Dephosphorylation favors active state → conformational flip → phosphorylation

**Negative feedback** (oscillation-generating):
- Phosphorylation reduces KaiA affinity → slows phosphorylation
- High phosphorylation triggers flip to inactive → dephosphorylation begins
- Dephosphorylation eventually triggers flip to active → phosphorylation begins

**Competition** (synchronization):
- Hexamers compete for limited KaiA
- Differential affinity favors laggards
- Maintains synchrony across population

### Allosteric Coupling

**Within a hexamer** (MWC model assumption):
- All 6 monomers must be in same conformational state
- Energetic cost of mixed states is prohibitively high
- This creates cooperative switching

**Between phosphorylation and conformation**:
- Phosphorylation stabilizes inactive state
- Nucleotide (ATP/ADP) binding stabilizes active state
- Creates thermodynamic cycle driving oscillations

---

## GAPS AND UNCERTAINTIES

### Missing Mechanistic Details

1. **Exact phosphorylation sites**:
   - Paper simplifies to binary (p/u) per monomer
   - Reality: Multiple phosphorylation sites per KaiC monomer (Ser431, Thr432 mentioned in references)
   - **Ambiguity**: Which sites are modified in which order?
   - **Quote**: "Although there is strong evidence that KaiC monomers can be phosphorylated at multiple sites, most published data do not distinguish between different phosphorylated forms. We thus assume that KaiC monomers have only two phosphorylation states..."

2. **Structural details of conformational states**:
   - Active vs Inactive states not structurally characterized in this paper
   - **Uncertainty**: What are the atomic-level differences?
   - **Quote**: "We postulate that an individual KaiC monomer can be in either an active (A) or an inactive (I) conformation."
   - Paper references RecA/DnaB superfamily, but specific structural changes unclear

3. **KaiA binding site and stoichiometry details**:
   - CII domain mentioned as binding site
   - **Ambiguity**: Exact binding interface not specified
   - In presence of KaiB, complex stoichiometry changes
   - **Quote**: "Recent experiments suggest that, in the absence of KaiB, KaiA binds as a single dimer to the CII domain of the KaiC hexamer"

4. **KaiB oligomeric state**:
   - **Ambiguity**: "KaiB is present in the cell as a dimer or a tetramer"
   - Model uses dimer; unclear if this is critical
   - **Quote**: "KaiB as a dimer (6, 7) or a tetramer (8)"

5. **ATP/ADP exchange kinetics**:
   - Assumed fast equilibrium
   - **Uncertainty**: Explicit rates not provided
   - **Quote**: "If we assume that ATP and ADP exchange are fast, so that the free energy of each state is well defined..."

6. **Monomer exchange between hexamers**:
   - Mentioned as potentially contributing (ref 19, 7)
   - **Not included in this model**
   - **Quote**: "Emberly and Wingreen (19) introduced the elegant hypothesis that exchange of monomers among KaiC hexamers might contribute to oscillations... their own work, however, shows that such exchange by itself is insufficient"

### Ambiguities in Model Assumptions

1. **Why only B₂C̃_1 through B₂C̃_4 bind KaiA?**:
   - Model assumes B₂C̃_0, B₂C̃_5, B₂C̃_6 don't bind KaiA
   - **Unclear biological basis** for this restriction
   - **Quote**: "Based on the measured size of the heteromultimeric complexes (6, 7), we assume that the inactive form of KaiC can bind two KaiB dimers, and that B₂C̃₄, B₂C̃₃, B₂C̃₂, and B₂C̃₁ can each bind two KaiA dimers with high affinity."

2. **Active state more stable than inactive (without KaiB)**:
   - Required to match KaiA-only experiments
   - **Uncertainty**: What is the structural/energetic basis?
   - **Quote**: "In the absence of KaiB, KaiC should thus have no tendency to cyclically phosphorylate and dephosphorylate. This requires that the active state of KaiC has a lower free energy than the inactive one"

3. **MWC-type allostery assumption**:
   - All-or-none switching assumption
   - **Potential simplification**: Could monomers switch independently?
   - **Quote**: "In the spirit of the MWC model, we assume that the energetic cost of having two different monomer conformations in the same hexamer is prohibitively large"

4. **KaiB effect on conformational stability**:
   - Model assumes KaiB stabilizes inactive state
   - **Mechanism unclear**: Direct binding energy? Allosteric effect?
   - Doesn't affect (de)phosphorylation rates directly

### Parameter Uncertainties

1. **All rate constants are fitted, not measured**:
   - (De)phosphorylation rates: "strongly constrained by... experiments on the subsets of Kai proteins"
   - Other 39 parameters: "we have simply chosen plausible values"
   - **Major uncertainty**: Many parameters not independently measurable

2. **Differential affinity parameter α**:
   - Critical for synchronization
   - **Not measured experimentally**
   - Assumed α > 1, but specific value fitted
   - **Quote**: "We implement differential affinity by setting k^i_Ab = k^0_Ab α^i, with α > 1"

3. **Energy differences ΔG_p and ΔG_u**:
   - Determine conformational flip rates
   - **Not measured**
   - Encoded in parameter c = exp[(ΔG_p - ΔG_u)/2]

4. **Temperature compensation parameters**:
   - Model assumes certain rates are temperature-compensated
   - **Quote**: "(de)phosphorylation reactions are each individually temperature-compensated (3)"
   - But specific temperature dependencies of binding constants unknown

### Experimental Gaps

1. **In vivo vs in vitro discrepancies**:
   - In vivo: [A]_T ≈ 0.1[C]_T → model predicts no oscillations
   - **Quote**: "In S. elongatus, the concentration of KaiA dimers is ~10% of that of KaiC hexamers (12). Our model predicts that in this regime, the in vitro oscillations of ref. 4 disappear."
   - Authors speculate other processes (localization, SasA, etc.) resolve this
   - **Major gap**: Model incomplete for in vivo system

2. **Direct measurement of conformational states**:
   - No experimental evidence for distinct A/I states in this paper
   - Needed: Structural studies, FRET, etc.

3. **Direct measurement of differential affinity**:
   - K_d values as function of phosphorylation level not measured
   - Needed: Binding assays with differentially phosphorylated KaiC

4. **Time-resolved complex composition**:
   - Figure 3B shows model predictions
   - Corresponding experimental data not shown in this paper
   - **Quote**: Reference to experiments in ref 7 (Kageyama 2006)

---

## MODELING CONSIDERATIONS

### Simplifications for Initial Kappa Model

1. **Binary phosphorylation per monomer**:
   - Already simplified in this paper
   - Each KaiC monomer: {u, p} states
   - Hexamer: 0-6 phosphorylated monomers

2. **Deterministic vs stochastic**:
   - Paper uses both: deterministic rate equations (mean-field) and stochastic simulations (Gillespie)
   - For initial model: Deterministic (ODE) approach simpler
   - Stochastic may be needed to capture variability (Figure 1C shows single hexamer noise)

3. **Explicit nucleotide states**:
   - Could include ATP/ADP binding explicitly in Kappa
   - Or assume fast equilibrium (as paper does) and encode in effective rates
   - **Recommendation**: Start without explicit nucleotides; add if needed

4. **Individual monomers vs hexamer-level**:
   - **Option 1**: Model individual monomers with binding sites, assemble into hexamers
   - **Option 2**: Treat hexamer as single agent with phosphorylation level 0-6
   - **Recommendation**: Option 2 (hexamer-level) matches paper's approach and avoids combinatorial explosion

5. **Simplified complex formation**:
   - Start with 1:1 KaiA:KaiC in active state
   - Add 2:1 KaiB:KaiC in inactive state
   - Then add A₂B₂C̃ ternary complexes
   - Build complexity incrementally

6. **Reduced number of phosphorylation levels**:
   - Could start with just 3 levels (low/medium/high) instead of 0-6
   - Test mechanism before full complexity
   - **Trade-off**: Loses detail but easier to debug

### Key Parameters Requiring Estimation

**From experiments**:
1. Total concentrations: [C]_T, [A]_T, [B]_T
   - Experiments: [C]_T = 0.58 μM, [A]_T = 1.75 μM, [B]_T = 0.58 μM
   - Ratios: [A]_T/[C]_T = 3, [B]_T/[C]_T = 1

**From fitting** (see SI Appendix of paper):
2. Conformational flip rates: f_i, b_i (exponential in i)
   - Only f₆ and b₀ critical for period
3. (De)phosphorylation rates: k_ps, k_dps, k̃_ps, k̃_dps, k_pf
   - Constrained by experiments without KaiA/KaiB
4. Binding rates: k_Af, k_Ab (and i-dependence via α), k̃_Bf, k̃_Bb, k̃_Af, k̃_Ab
5. Differential affinity parameter: α > 1

**Units**: Concentrations in μM, time in hours, rates in h⁻¹ or μM⁻¹h⁻¹

### Observables to Track

1. **Mean phosphorylation level**:
   ```
   p = Σ_i i·([C_i] + [C̃_i] + [AC_i] + [B₂C̃_i] + [A₂B₂C̃_i]) / (6·[C]_T)
   ```
   - Should oscillate with ~24h period, amplitude 0.2-0.8

2. **Fraction in active vs inactive state**:
   ```
   f_active = Σ_i ([C_i] + [AC_i]) / [C]_T
   f_inactive = Σ_i ([C̃_i] + [B₂C̃_i] + [A₂B₂C̃_i]) / [C]_T
   ```

3. **Complex abundances**:
   ```
   [AC] = Σ_i [AC_i]  (KaiA-KaiC complex)
   [BC] = Σ_i [B₂C̃_i]  (KaiB-KaiC complex)
   [ABC] = Σ_i [A₂B₂C̃_i]  (Ternary complex)
   ```
   - Should show phase relationships (Figure 3B)

4. **Free KaiA concentration**:
   ```
   [A]_free = [A]_T - Σ_i [AC_i] - 2·Σ_i [A₂B₂C̃_i]
   ```
   - Should drop near zero during phosphorylation phase

5. **Distribution of phosphorylation levels** (optional):
   ```
   [C_i] + [C̃_i] for each i
   ```
   - Check synchronization (narrow distribution means good sync)

### Validation Experiments Mentioned

1. **KaiC alone** (Figure 4):
   - Initial: Fully phosphorylated
   - Final: Low phosphorylation (~10-20%)
   - Time scale: Reaches equilibrium in ~8-12 hours

2. **KaiC + KaiA** (Figure 4):
   - Initial: Fully unphosphorylated
   - Final: High phosphorylation (~90-95%)
   - Time scale: Reaches steady state in ~6-8 hours

3. **KaiC + KaiB** (Figure 4):
   - Should match KaiC alone behavior

4. **KaiA + KaiB + KaiC** (Figures 3, 4):
   - Oscillations with period ~24h
   - Amplitude: p oscillates between ~0.2 and ~0.8
   - Complex formation: AC rises during phosphorylation, BC rises at peak, ABC rises during dephosphorylation

5. **Concentration dependence** (Figure 6):
   - Oscillations disappear below [A]_T ≈ 0.5[C]_T (Hopf bifurcation)
   - Oscillations disappear above [A]_T ≈ 1.25[C]_T
   - Period decreases with increasing [A]_T
   - Amplitude peaks at [A]_T ≈ 0.85[C]_T
   - Oscillations robust to [B]_T variation (above minimum [B]_T ≈ [C]_T)

6. **Temperature compensation** (Figure 5):
   - Period varies by only ~10% when dissociation constants change 25-fold
   - Period varies by ~10% when flip rates change 25-fold

### Implementation Strategy

**Phase 1**: Build core cycling mechanism (no synchronization)
- Single KaiC hexamer with 7 phosphorylation levels (0-6)
- Active/inactive conformational states
- Spontaneous (de)phosphorylation in both states
- Conformational flips with i-dependent rates
- **Expected outcome**: Noisy oscillations of single hexamer (Figure 1C)

**Phase 2**: Add KaiA stimulation
- KaiA binding to active KaiC (without differential affinity yet)
- KaiA-stimulated phosphorylation
- Multiple KaiC hexamers
- **Expected outcome**: High phosphorylation steady state (like Figure 4, C+A)

**Phase 3**: Add differential affinity
- Implement i-dependent KaiA binding (k^i_Ab ∝ α^i)
- Tune [A]_T to limiting value
- **Expected outcome**: Synchronized oscillations in simple model (Figure 2)

**Phase 4**: Add KaiB
- KaiB binding to inactive KaiC
- KaiA sequestration by B₂C̃_i complexes
- Stabilization of inactive state
- **Expected outcome**: Full oscillations matching Figure 3

**Phase 5**: Validation and parameter fitting
- Match all experimental conditions (C alone, C+A, C+B, C+A+B)
- Tune parameters for 24h period
- Check temperature compensation
- Test concentration dependencies

### Kappa-Specific Considerations

1. **Agent representation**:
   ```
   %agent: C(state{active inactive}, phos{0 1 2 3 4 5 6}, kaiA, kaiB1, kaiB2)
   %agent: A(c, b)
   %agent: B(c)
   ```
   - C has conformational state, phosphorylation level, binding sites for KaiA and 2 KaiBs
   - A can bind C or B
   - B binds C

2. **Differential affinity implementation**:
   - Need 7 separate binding rules for each phosphorylation level
   - Each with different off-rate
   - Or: Use rate function (if PyKappa supports it)

3. **Conformational flip rules**:
   - Need 7 rules for A→I flip (one per phosphorylation level)
   - Need 7 rules for I→A flip
   - Each with different rate (exponential in i)

4. **Phosphorylation rules**:
   - Active state: free or KaiA-bound, slow or fast rate
   - Inactive state: slow rate only
   - Complex states: same rates

5. **Symmetry considerations**:
   - Two KaiB binding sites are symmetric
   - Two KaiA binding sites on B₂C̃ are symmetric
   - PyKappa should handle symmetry correction automatically

6. **Observable calculations**:
   - Mean phosphorylation requires weighted sum over all phosphorylation levels
   - Pattern matching for each [C_i] state
   - Post-process to calculate p = Σ i·count(C_i) / (6·count(C_total))

---

## SUMMARY OF KEY MECHANISTIC PRINCIPLES

1. **Individual hexamers have intrinsic cycling tendency**:
   - Allosteric conformational states (Active/Inactive)
   - Phosphorylation favors Inactive → triggers flip → dephosphorylation occurs
   - Dephosphorylation favors Active → triggers flip → phosphorylation occurs
   - Creates noisy, unsynchronized cycles

2. **KaiA stimulates phosphorylation of Active state**:
   - Binds to Active KaiC with phosphorylation-dependent affinity
   - Accelerates phosphorylation rate

3. **Differential affinity synchronizes the population**:
   - Less phosphorylated hexamers bind KaiA more tightly (k_off ∝ α^i, α > 1)
   - Limited KaiA creates competition
   - "Laggards" outcompete "front-runners"
   - Population synchronizes

4. **KaiB enables oscillations and synchronization in dephosphorylation phase**:
   - Stabilizes Inactive state (balances Active state bias)
   - Sequesters KaiA away from Active hexamers
   - Creates differential affinity effect at bottom of cycle

5. **Temperature compensation via rate hierarchy**:
   - (De)phosphorylation rates are temperature-compensated (experimental fact)
   - Binding rates and flip rates are fast (saturated kinetics)
   - Period determined by slow (de)phosphorylation, not by fast binding
   - Makes period robust to temperature changes

6. **ATP hydrolysis only during phosphorylation**:
   - Non-equilibrium system driven by ATP → ADP
   - All other reactions (binding, conformational flips) obey detailed balance
   - Unusual feature for biological oscillator

---

## CRITICAL QUOTES RELEVANT TO MODELING

### On the core mechanism:
> "At its heart is the assumption that KaiC can exist in two conformational states, one favoring phosphorylation and the other dephosphorylation."

> "To generate macroscopic oscillations, however, the phosphorylation cycles of the different hexamers must be synchronized."

### On differential affinity:
> "We propose a novel synchronization mechanism based on differential affinity: KaiA stimulates KaiC phosphorylation, but the limited supply of KaiA dimers binds preferentially to those KaiC hexamers that are falling behind in the oscillation."

> "The natural phenomenological assumption is then that the flip rates depend exponentially on the free-energy difference: f_i = k₀exp[ΔG(i)/2] = c^i"

### On KaiB function:
> "KaiB sequesters KaiA and stabilizes the dephosphorylating KaiC state."

> "One critical role of KaiB is thus to allow the KaiC hexamers to enter the dephosphorylation phase of the cycle."

### On rate hierarchy for temperature compensation:
> "All (un)binding rates and the flip rates f₆ and b₀ are much faster than the (de)phosphorylation rates."

> "The affinities among the Kai proteins are high. KaiA, the least abundant of the three proteins, will then be almost entirely bound up in complexes with KaiB and KaiC."

### On parameter constraints:
> "We found that the experiments on the various subsets of the three Kai proteins strongly constrain the model's design."

---

## REFERENCES FOR FURTHER DETAILS

- **Supporting Information (SI Appendix)**: Contains all parameter values, detailed rate equations, bifurcation analysis
- **Structural studies**: Refs 22-23 (RecA/DnaB superfamily conformations)
- **Experimental validation**: Refs 4, 7 (Nakajima 2005, Kageyama 2006)
- **Phosphorylation sites**: Refs 10, 24, 25
- **Temperature compensation**: Ref 3 (Tomita 2005)
