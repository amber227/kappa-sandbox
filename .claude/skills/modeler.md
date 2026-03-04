# Kappa Modeler Skill

## Purpose
This skill enables creating, running, and analyzing rule-based models of dynamical systems using PyKappa. Focus on iterative exploration: build models, simulate, observe results, refine hypotheses.

## Core Concepts

### What is Kappa?
- **Rule-based modeling language** for systems of interacting structured entities
- **Graph rewriting**: Molecules are site graphs; rules specify transformations
- **Handles combinatorial complexity**: Rules avoid enumerating all possible species
- **Mechanism vs reaction**: A rule represents a mechanism; reactions are instances when rules match specific entities

### Site Graphs
- **Agents**: Typed nodes (e.g., proteins) with interfaces
- **Sites**: Binding locations and state holders on agents
- **Internal states**: Modifications (e.g., phosphorylation: `{u}` unphosphorylated, `{p}` phosphorylated)
- **Bonds**: Connections between sites, labeled with integers
- **Rigidity**: All sites have distinct names; embedding defined by matching single node

### PyKappa Hierarchy
Four levels from specific to general:
1. **Patterns**: Subsets of mixtures on which rules operate
   - `Agent`: Single typed entity with sites
   - `Component`: Connected set of agents
2. **Mixtures**: Collections of agents tracking embeddings
3. **Rules**: Transform patterns (left → right) with stochastic rates
4. **Systems**: Bundle mixtures, rules, observables for simulation

## PyKappa Syntax & API

### Creating Patterns
```python
from pykappa.pattern import Agent, Component

# From Kappa string
agent = Agent.from_kappa("A(x[.], y{u})")
complex = Component.from_kappa("A(x[1]), B(x[1])")

# Check embeddings
embeddings = pattern.embeddings(target_component)
```

**Kappa notation**:
- `A(x[.])` - Agent A with site x free
- `A(x[1]), B(x[1])` - A and B bound at sites x
- `A(x{u})` - Site x in internal state u
- `A(x[_])` - Site x bound to something unspecified
- `A(x[y.B])` - Binding type: bound to site y of some B

### Building Mixtures
```python
from pykappa.mixture import Mixture

mixture = Mixture()
mixture.instantiate("A(x[.])", n_copies=100)
mixture.track_component(complex)  # For advanced tracking

# Query
n_embeddings = len(mixture.embeddings(pattern))
```

### Defining Rules
```python
from pykappa.rule import KappaRule

# From Kappa string
rule = KappaRule.from_kappa("'bind' A(x[.]), B(x[.]) -> A(x[1]), B(x[1]) @ 0.001")

# Apply to mixture
if rule.n_embeddings(mixture) > 0:
    embedding = rule.select(mixture)
    mixture.apply_update(embedding)
```

**Rule syntax**:
- `->` one-way reaction
- `<->` reversible (requires two rates: `@ k_on, k_off`)
- `.` empty slot (agent creation/deletion)
- `@` precedes rate constant

### Systems and Simulation
```python
from pykappa.system import System, Monitor

# From .ka file
system = System.read_ka("model.ka", seed=42)

# Or from Kappa string
ka_str = """
%agent: A(x)
%agent: B(x)
'bind' A(x[.]), B(x[.]) -> A(x[1]), B(x[1]) @ 0.001
%init: 100 A(), B()
%obs: 'AB' |A(x[1]), B(x[1])|
"""
system = System.from_ka(ka_str, seed=42)

# Simulate
monitor = Monitor(system)
system.update_until(max_time=100.0)

# Analyze
monitor.update()
df = monitor.dataframe
monitor.plot()
```

### Observables
Algebraic expressions counting pattern occurrences:
```python
system.observables['AB'] = |A(x[1]), B(x[1])|  # Count AB complexes
```

## Key Modeling Considerations

### Pattern Matching (Embedding)
- **Subgraph isomorphism**: Every agent/site in pattern must match mixture
- **Less specific matches more specific**:
  - Wildcard `{#}` or `[#]` matches any state
  - `[_]` matches any bound state
  - `[.]` matches only free
  - Binding type `[y.B]` matches type without requiring stoichiometry

### Symmetry (Important!)
- **Automorphisms**: Embeddings related by symmetry
- **Affects observable counting**: Must divide by symmetry factor
  ```python
  # Homodimer has 2-fold symmetry
  %obs: 'dimers' |A(x[1]), A(x[1])| / 2
  ```
- **Rule activity**: Symmetric embeddings may represent same physical event
- PyKappa default: No automatic symmetry correction (user responsibility)

### Rate Constants and Scaling
**Stochastic vs deterministic**:
```
γ_stochastic = k_deterministic / V^(n-1)
```
where `n` is molecularity, `V` is volume.

- **Unimolecular**: Independent of volume
- **Bimolecular**: Scales as 1/V
- **Zeroth-order**: Proportional to V

**Important**: When rescaling system by σ:
```python
V' = σ * V
n_agents' = σ * n_agents
γ' = γ / σ^(n-1)  # n = molecularity
```

### Ambiguous Molecularity
Rules where pattern can match intra- or intermolecularly:
```
'ring_or_extend' A(x[.]), A(y[.]) -> A(x[1]), A(y[1]) @ γ_bi {γ_uni}
```
- Requires component tracking (expensive!)
- Provide two rates: bimolecular `γ_bi` and unimolecular `γ_uni`

### Simulation Mechanics (CTMC)
**Core loop**:
1. Calculate system activity: `λ = Σ_i (n_embeddings_i * rate_i)`
2. Sample time to next event: `t ~ Exp(λ)`
3. Choose rule i with probability `α_i / λ`
4. Select embedding uniformly
5. Apply rule, update time T ← T + t
6. Repeat

**Rule activity**: `α_i = n_embeddings * rate_i * Ω_i`
where `Ω_i` is symmetry correction factor (typically 1 in PyKappa).

## Modeling Workflow

### 1. Define the System
```python
# Declare agents with signatures
%agent: E(s)          # Enzyme with binding site
%agent: S(e, x{u p})  # Substrate with enzyme site and modifiable site

# Variables for parameters
%var: 'k_on' 0.001
%var: 'k_off' 0.1
%var: 'k_cat' 1.0

# Rules (mechanisms)
'binding' E(s[.]), S(e[.]) <-> E(s[1]), S(e[1]) @ 'k_on', 'k_off'
'catalysis' E(s[1]), S(e[1], x{u}) -> E(s[.]), S(e[.], x{p}) @ 'k_cat'

# Initial conditions
%init: 100 E()
%init: 1000 S(x{u})

# Observables
%obs: 'Product' |S(x{p})|
%obs: 'ES_complex' |E(s[1]), S(e[1])|
```

### 2. Run Simulation
```python
import random
from pykappa.system import System, Monitor

# Reproducibility
random.seed(42)
system = System.read_ka("model.ka", seed=42)
monitor = Monitor(system)

# Simulate
system.update_until(max_time=100.0, check_interval=10)

# Or by events
# system.update_until(max_updates=10000, check_interval=1000)
```

### 3. Observe and Analyze
```python
# Get data
df = monitor.dataframe  # Time series of observables

# Check equilibration
monitor.equilibrated('Product', tail_fraction=0.1, tolerance=0.01)

# Visualize
monitor.plot()  # Or monitor.plot(combined=True)

# Specific measurements
final_product = monitor.measure('Product', time=100.0)
mean_ES = monitor.tail_mean('ES_complex', tail_fraction=0.2)
```

### 4. Iterate and Refine
**Perturbations** - Modify system during simulation.

**Parameter sweeps**:
```python
results = []
for k_cat in [0.1, 1.0, 10.0]:
    system = System.from_ka(ka_template.replace('K_CAT', str(k_cat)), seed=42)
    monitor = Monitor(system)
    system.update_until(max_time=100.0)
    results.append(monitor.dataframe)
```

**Snapshot and restart**:
```python
# Save state at equilibrium
system.to_ka("equilibrated_state.ka")

# Use as initial condition for new experiments
system_new = System.read_ka("equilibrated_state.ka")
```

## Common Patterns

### Reversible Binding
```
A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ k_on, k_off
```

### Post-translational Modification
```
# Phosphorylation
K(s[1]), S(e[1], x{u}) -> K(s[.]), S(e[.], x{p}) @ k_cat

# Conditional on binding state
K(s[1]), S(e[1], x{u}, y[_]) -> ... # Only if y is bound
```

### Polymerization
```
# Head-to-tail addition
M(head[.]), M(tail[.]) -> M(head[1]), M(tail[1]) @ k_poly
```

### Prozone/Hook Effect
Excess of bridge molecule reduces complex formation:
```
L(x[.]), E(l[.], m[.]) <-> L(x[1]), E(l[1], m[.]) @ k1_on, k1_off
M(x[.]), E(l[.], m[.]) <-> M(x[1]), E(l[.], m[1]) @ k2_on, k2_off

# When E is abundant, incomplete complexes dominate
%obs: 'complete' |L(x[1]), E(l[1], m[2]), M(x[2])|
```

## Advanced Features

### Rate Functions
Non-mass-action kinetics (use cautiously - breaks mechanism transparency):
```python
# Michaelis-Menten approximation
%var: 'Km' 1000
_E(s[.]), _S(e[.], x{u}) -> _E(s[.]), _S(e[.], x{p}) @ k_cat * |_E()| / ('Km' + |_S(x{u})|)
```

### Component Tracking
For complex topology-dependent rules:
```python
mixture = Mixture()
mixture.enable_component_tracking()
mixture.track_component(component)

# Query embeddings within specific component
emb = mixture.embeddings_in_component(pattern, specific_component)
```

## Best Practices

1. **Start simple**: Build minimal models, add complexity incrementally
2. **Set random seeds**: Ensure reproducibility in stochastic simulations
3. **Check equilibration**: Use `monitor.equilibrated()` before analyzing steady-state
4. **Visualize early**: Plot trajectories to catch unexpected behaviors
5. **Mind symmetry**: Correct observable counts for automorphisms
6. **Document mechanisms**: Clear rule names and comments explaining biology
7. **Parameter units**: Be explicit about time/concentration units and volume assumptions
8. **Version control**: Commit models with git hashes in figure filenames (per project standards)
9. **Validate**: Compare to known limits (e.g., deterministic equations for large numbers)
10. **Use appropriate simulation backend**:
    - Python simulator: Full features, slower
    - `system.update_via_kasim(time)`: Compiled KaSim, faster but limited features

## Troubleshooting

**Simulation too slow**:
- Reduce system size or rescale
- Use KaSim backend: `system.update_via_kasim()`
- Avoid component tracking unless necessary
- Check for excessive rule applications (high activity)

**Unexpected dynamics**:
- Verify rate constant units and volume scaling
- Check for missing conditions in rules (unintended side effects)
- Visualize mixture composition: snapshot and inspect
- Use smaller test systems to isolate issues

**Equilibration never reached**:
- May be oscillatory or chaotic (rare in biochemical systems)
- Check for conservation laws: are you creating/destroying mass unexpectedly?
- Verify detailed balance for reversible reactions

**Symmetry issues in observables**:
- Patterns with automorphisms are counted multiple times
- Manually divide by symmetry factor: `|A(x[1]), A(x[1])| / 2`

## Resources

- **PyKappa docs**: https://pykappa.org/
- **Kappa portal**: http://kappalanguage.org
- **Tutorial**: Start with reversible binding example
- **Examples**: Study prozone, polymerization, lac operon, chemostat models
- **Bug reports**: https://github.com/Kappa-Dev/KaSim/issues
