# Binary Counter Tile Assembly System Analysis
## Winfree (2000) - Figure 3

**Source**: Algorithmic Self-Assembly of DNA: Theoretical Motivations and 2D Assembly Experiments
**Author**: Erik Winfree
**Journal**: Journal of Biomolecular Structure & Dynamics, 2000
**Analysis Date**: 2026-03-12
**Git Commit**: 0e639d0

---

## SYSTEM OVERVIEW

The binary counter implements a computational tiling system that counts consecutive integers (1, 2, 3, 4, 5, ...) in binary representation (1, 10, 11, 100, 101, ...), with each successive number written in a new row above the previous one.

### Computational Goal
- Count upward from 1 in binary
- Each row represents the next integer
- Rows are stacked vertically
- Demonstrates Turing-universal computation capability through local matching rules

---

## AGENTS (Tile Types)

The binary counter system uses **7 distinct tile types**:

### 1. Seed Tile (S)
- **Function**: Initiates the computation
- **Position**: Bottom-left corner of the assembly
- **Binding sites**:
  - Top: interfaces with first counter row
  - Right: interfaces with bottom boundary tiles
- **States encoded**: Serves as origin point for the tiling

### 2. Bottom Boundary Tile (Bottom)
- **Function**: Provides initial conditions for counter bits
- **Pattern**: Produces a series of rounded tops
- **Encoding**: Represents initial counter bits ...000 (all zeros)
- **Binding sites**:
  - Top: presents "bit = 0" interface
  - Left: binds to adjacent boundary tiles (or seed)
  - Right: binds to adjacent boundary tiles
  - Bottom: inert (edge of assembly)
- **Multiplicity**: Forms a horizontal row extending rightward from seed

### 3. Right Boundary Tile (Right)
- **Function**: Provides "increment" commands to each row
- **Pattern**: Produces vertical series of "rollover" signals
- **Role**: Triggers increment operation for rightmost bit in every row
- **Binding sites**:
  - Left: presents "rollover" interface to rule tiles
  - Bottom: binds to adjacent boundary tiles (or seed)
  - Top: binds to adjacent boundary tiles
  - Right: inert (edge of assembly)
- **Multiplicity**: Forms a vertical column extending upward from seed

### 4-7. Four Rule Tiles

These tiles implement the binary addition logic. Each rule tile has **four binding domains** (top, bottom, left, right) that encode:
- **Top/Bottom domains**: Encode bit values (0 or 1)
- **Left/Right domains**: Encode rollover state (rollover or no rollover)

#### Rule Tile A: "0 stays 0 with no rollover"
- **Bottom input**: bit = 0
- **Right input**: no rollover
- **Top output**: bit = 0
- **Left output**: no rollover
- **Logic**: If current bit is 0 and there's no rollover from the right, output 0 with no rollover

#### Rule Tile B: "0 becomes 1 with rollover"
- **Bottom input**: bit = 0
- **Right input**: rollover
- **Top output**: bit = 1
- **Left output**: no rollover
- **Logic**: If current bit is 0 and there's a rollover from the right, output 1 and stop the rollover

#### Rule Tile C: "1 stays 1 with no rollover"
- **Bottom input**: bit = 1
- **Right input**: no rollover
- **Top output**: bit = 1
- **Left output**: no rollover
- **Logic**: If current bit is 1 and there's no rollover from the right, output 1 with no rollover

#### Rule Tile D: "1 becomes 0 with rollover propagation"
- **Bottom input**: bit = 1
- **Right input**: rollover
- **Top output**: bit = 0
- **Left output**: rollover
- **Logic**: If current bit is 1 and there's a rollover from the right, output 0 and propagate rollover leftward

---

## BINDING SITES AND INTERACTIONS

### Binding Site Architecture

Each tile has **four binding domains** corresponding to its geometric sides:
- **Top domain**: Encodes output bit value (for vertical propagation)
- **Bottom domain**: Recognizes input bit value (from tile below)
- **Left domain**: Outputs rollover state (for horizontal propagation leftward)
- **Right domain**: Recognizes rollover input (from tile to the right)

### Binding Specificity

The "shapes" mentioned in the paper represent **binding domain compatibility**:

1. **Bit encoding domains (top/bottom)**:
   - "Rounded top" shape = bit value 0
   - "Flat/square top" shape = bit value 1
   - Complementary shapes must match: a tile presenting "0" on top can only bind to a tile recognizing "0" on bottom

2. **Rollover encoding domains (left/right)**:
   - "Rollover present" shape
   - "No rollover" shape
   - Complementary shapes must match

### Interaction Rules

**Geometric constraints**:
- Tiles arrange on a **2D rectangular lattice**
- Each tile position has at most 4 neighbors (north, south, east, west)
- Binding occurs only between adjacent tiles on matching edges

**Directionality**:
- **Horizontal direction (left-right)**: Carries rollover information
  - Information flows RIGHT to LEFT (rollover propagates leftward)
- **Vertical direction (bottom-top)**: Carries bit values
  - Information flows BOTTOM to TOP (each row builds on previous row)

---

## ASSEMBLY RULES AND KINETIC CONSTRAINTS

### Critical Assembly Conditions

The paper explicitly states **two essential requirements** for correct computational assembly:

#### 1. Temporal Ordering (Staged Assembly)
> "First, to ensure that the correct pattern results, the three input tiles are assembled before the rule tiles are used."

**Implementation**:
- **Stage 1**: Seed tile (S) and boundary tiles (bottom and right) assemble first
- **Stage 2**: Rule tiles are added only after input assembly is complete
- **Rationale**: Prevents incorrect partial tilings that don't correspond to valid computation

**Relaxation note**: Paper states "This restriction can be relaxed somewhat, but it is convenient for explanation."

#### 2. Cooperative Binding (Kinetic Proofreading)
> "Second, to avoid getting stuck with an incorrect partial tiling, one must add rule tiles only when both the tiles below and to their right are already present."

**Physical interpretation**:
> "To use a biochemist's terminology, we require that binding be a highly cooperative event, and the reaction must take place at a temperature above the melting temperature of the single binding domain and below the melting temperature of a pair of cooperative binding domains."

**Mechanism**:
- Single binding domain is **insufficient** for stable attachment
- A rule tile must match **at least two binding domains simultaneously** (bottom AND right)
- This ensures tiles only attach to correct positions in the growing assembly

**Purpose**:
- Prevents formation of incorrect tilings
- Prevents spurious assembly in absence of proper input (e.g., infinite periodic lattice of all-0 tiles)
- Provides error correction through thermodynamic discrimination

### Temperature Control

**High temperature regime** (above single-domain Tm):
- Single binding domain interactions are unstable
- Tiles cannot attach via single edge

**Optimal temperature** (between single and double-domain Tm):
- Single domain binding: thermodynamically unfavorable
- Two-domain cooperative binding: thermodynamically favorable
- Enables kinetic selection of correct tile placement

**Low temperature regime** (below single-domain Tm):
- Risk of kinetic traps and errors
- Single-domain binding becomes stable

---

## ASSEMBLY GEOMETRY AND SPATIAL CONSTRAINTS

### Growth Pattern

1. **Initialization**:
   - Seed tile S placed at origin (0,0)
   - Bottom boundary tiles extend along x-axis (row 0)
   - Right boundary tiles extend along y-axis (column 0, rightmost position)

2. **Row-by-row assembly**:
   - Row 1: First counter value (binary: 1)
   - Row 2: Second counter value (binary: 10)
   - Row 3: Third counter value (binary: 11)
   - Row 4: Fourth counter value (binary: 100)
   - And so on...

3. **Growth direction**:
   - **Vertical growth**: Upward (increasing row number = increasing count)
   - **Horizontal growth**: Each row extends leftward as needed to accommodate larger binary numbers

### Spatial Determinism

> "As in the binary counter example, tile sets are typically designed such that a unique tile can fit into each location, and thus a unique tiling is deterministically produced."

- At each position, the bottom and right neighbors uniquely determine which rule tile can bind
- The assembly is **deterministic**: only one valid tile type fits each location
- No branching or alternative assembly pathways

---

## INITIAL CONDITIONS

### Seed Configuration
- **Single seed tile (S)** at position (0,0)

### Boundary Conditions

1. **Bottom boundary** (y = 0, x ≥ 0):
   - Infinite row of bottom boundary tiles
   - All present "bit = 0" on their top faces
   - Represents initial state: ...000000

2. **Right boundary** (x = 0, y ≥ 0):
   - Infinite column of right boundary tiles
   - All present "rollover" signal on their left faces
   - Represents increment command for each row

### Initial Mixture Composition

**For staged assembly**:

*Stage 1 (input assembly)*:
- Seed tile (S): 1 copy (or fixed surface-bound)
- Bottom boundary tiles: excess (or continuous supply)
- Right boundary tiles: excess (or continuous supply)

*Stage 2 (computation)*:
- All four rule tiles (A, B, C, D): excess quantities, equimolar ratios

**Concentration considerations** (from experimental sections, for DNA implementation):
- Stock solutions: 0.2 to 2 μM per DNA strand
- For lattice formation: equal amounts of each tile type mixed

---

## GAPS AND UNCERTAINTIES

### Mechanistic Ambiguities

1. **Rate constants not provided**:
   - No quantitative kinetic parameters given
   - Only qualitative description: "highly cooperative binding"
   - Binding affinities (Kd values) not specified

2. **Sticky-end strength not specified**:
   - Paper describes abstract "shapes" but not molecular implementation details for counter
   - DNA sequences only provided for the simpler A-B tile system (Figure 1, not the counter)

3. **Boundary tile implementation unclear**:
   - How are boundary conditions physically implemented?
   - Are boundary tiles structurally different from rule tiles?
   - In practice: could use tiles with modified sticky ends or pre-assembled structures

4. **Tile concentrations for optimal assembly**:
   - No stoichiometry specified for rule tiles vs boundary tiles
   - Optimal ratios not discussed

5. **Assembly time scale**:
   - No information on how long assembly takes
   - Equilibration time not discussed

6. **Error rate**:
   - Paper mentions cooperative binding prevents errors
   - But no quantification of error probability
   - Computer simulations mentioned: "error-free computational crystals will form in a large region of parameter space" (Winfree preliminary, 1998) - but no data shown

### Structural Uncertainties

1. **Tile size and geometry**:
   - Abstract representation as rectangles
   - Physical dimensions not specified for counter system
   - For DNA DX implementation (different system): ~25 nm × 12-13 nm per tile

2. **Binding domain details**:
   - Number of base pairs per sticky end not specified
   - Sequence design principles not elaborated

3. **3D structure**:
   - Counter shown as 2D schematic
   - Actual physical realization would be 3D molecular assembly
   - Thickness of assembly not discussed

---

## DEPENDENCIES AND LOGIC

### Causal Chains

1. **Vertical dependency** (row N → row N+1):
   - Row N must be complete before row N+1 can begin assembly
   - Each tile in row N+1 requires corresponding tile in row N (below it)
   - Bit value propagates upward from row to row

2. **Horizontal dependency** (column M → column M-1):
   - Within a row, assembly proceeds right to left
   - Rightmost position (adjacent to boundary) assembles first
   - Each position requires tile to the right before it can be filled
   - Rollover propagates leftward

### Mutual Exclusions

1. **Tile type exclusions**:
   - At each position, only ONE of the four rule tiles can correctly bind
   - Different combinations of (bottom bit, right rollover) uniquely specify tile type
   - No competing valid tiles for the same position

2. **Rollover states are mutually exclusive**:
   - Either rollover is present OR it is absent (binary state)
   - Cannot have both simultaneously

### Cooperative Relationships

1. **Two-edge cooperativity**:
   - Bottom edge AND right edge must both match for stable binding
   - Single edge match insufficient
   - This is the key error-correction mechanism

2. **Binding energy additivity**:
   - Total binding energy = bottom edge + right edge
   - Two edges together exceed stability threshold
   - One edge alone below stability threshold

### Feedback Structures

**No explicit feedback loops in the counter system**:
- The counter is a feed-forward computation
- Information flows unidirectionally (bottom-up, right-left)
- No tiles that modify earlier rows
- No regulatory circuits

**Implicit negative feedback** (thermodynamic):
- Incorrect binding attempts are thermodynamically disfavored
- Mismatched tiles dissociate before committing to assembly
- System self-corrects through equilibrium binding

---

## RULE TILE LOGIC TABLE

| Tile | Bottom Input | Right Input | Top Output | Left Output | Description |
|------|--------------|-------------|------------|-------------|-------------|
| A    | 0            | no rollover | 0          | no rollover | 0 + 0 = 0 (no carry) |
| B    | 0            | rollover    | 1          | no rollover | 0 + 1 = 1 (carry absorbed) |
| C    | 1            | no rollover | 1          | no rollover | 1 + 0 = 1 (no carry) |
| D    | 1            | rollover    | 0          | rollover    | 1 + 1 = 0 (carry out) |

This implements binary addition: current_bit + carry_in = new_bit + carry_out

---

## MODELING CONSIDERATIONS

### Suggested Simplifications for Initial Kappa Model

1. **Finite assembly size**:
   - Instead of infinite boundaries, use finite pre-assembled input
   - e.g., 8-bit counter (seed + 8 bottom tiles + 8 right tiles)
   - Limits assembly to 2^8 = 256 rows maximum

2. **Discrete time steps**:
   - Model assembly as discrete events rather than continuous kinetics
   - Each "step" allows one tile to attach

3. **Perfect binding specificity**:
   - Assume matching domains always bind
   - Non-matching domains never bind
   - Ignore error rates initially

4. **Simplified cooperativity**:
   - Rule: tile can only bind if BOTH bottom and right neighbors present
   - Don't model partial binding or intermediate states

5. **Deterministic assembly**:
   - At each position, only correct tile type attempts binding
   - No competition between different tile types

### Advanced Model Extensions

1. **Kinetic parameters**:
   - Introduce rate constants for binding (kon) and unbinding (koff)
   - Model cooperative binding explicitly with enhanced affinity

2. **Error modeling**:
   - Allow low-probability mismatched binding
   - Introduce proofreading mechanisms

3. **Spatial stochastic simulation**:
   - Track 2D position of each tile
   - Implement spatial exclusion (one tile per position)

4. **Temperature effects**:
   - Model temperature-dependent binding energies
   - Simulate annealing protocols

### Key Parameters Needing Estimation

1. **Binding rate constants**:
   - kon for single-domain interaction
   - kon for two-domain cooperative interaction
   - koff for single-domain dissociation
   - koff for two-domain dissociation

2. **Concentrations**:
   - Initial concentration of each tile type
   - Stoichiometric ratios

3. **Thermodynamic parameters**:
   - ΔG for single sticky-end binding
   - ΔG for cooperative two-edge binding
   - Temperature range for optimal assembly

4. **Geometric parameters**:
   - Lattice spacing (if modeling spatial diffusion)
   - Tile dimensions

### Validation Experiments Mentioned

From the DNA implementation section (not the abstract counter, but the simpler A-B system):

1. **Gel electrophoresis**:
   - Non-denaturing gels show lattice formation (too large to migrate)
   - Denaturing gels after ligation show long reporter strands (>30 repeats)
   - Confirms large-scale assembly

2. **Atomic Force Microscopy (AFM)**:
   - Direct visualization of 2D lattices
   - Lattices up to 2 × 8 μm observed
   - Single domain crystals with ~500,000 tiles
   - Confirms periodicity and structure

3. **Controls**:
   - Individual tiles alone don't form lattices
   - Truncated tiles (missing binding domains) form only small structures
   - Confirms specific binding requirements

**Note**: These validation methods are described for the simpler striped lattice (Figure 1), not specifically for the binary counter (Figure 3). The binary counter is presented as a theoretical example of computational capability, but its experimental implementation is not reported in this paper.

---

## KAPPA-SPECIFIC MODELING STRATEGY

### Agent Definitions

```
# Seed tile
%agent: Seed(top, right)

# Boundary tiles
%agent: BottomBoundary(top~bit0, left, right)
%agent: RightBoundary(left~rollover, bottom, top)

# Rule tiles (with internal state encoding their type)
%agent: RuleTile(
    type~A~B~C~D,
    bottom~bit0~bit1,
    right~rollover~no_rollover,
    top~bit0~bit1,
    left~rollover~no_rollover
)
```

### Alternative Agent Design (Separate Tile Types)

```
%agent: TileA(bottom~bit0, right~no_rollover, top~bit0, left~no_rollover)
%agent: TileB(bottom~bit0, right~rollover, top~bit1, left~no_rollover)
%agent: TileC(bottom~bit1, right~no_rollover, top~bit1, left~no_rollover)
%agent: TileD(bottom~bit1, right~rollover, top~bit0, left~rollover)
```

### Site States

Each binding site has:
- **Binding partner pointer** (free or bound to adjacent tile's complementary site)
- **Encoded information state** (bit value or rollover status)

### Binding Rules (Conceptual)

```
# Rule tile binds cooperatively when both bottom and right neighbors present
# Example for Tile A binding:

%rule: 'TileA_cooperative_binding'
    TileA(bottom[.], right[.]) +
    BottomBoundary(top~bit0[.]) +
    RightBoundary(left~no_rollover[.])
    ->
    TileA(bottom[1], right[2]) +
    BottomBoundary(top~bit0[1]) +
    RightBoundary(left~no_rollover[2])
    @ kon_cooperative
```

### Spatial Constraints in Kappa

**Challenge**: Kappa doesn't natively handle 2D spatial lattices

**Solutions**:
1. **Implicit spatial structure**:
   - Use binding graph connectivity to represent adjacency
   - Each tile's bound neighbors implicitly define its position

2. **Explicit position encoding**:
   - Add position sites to agents: `position~x0y0~x0y1~x1y0~...`
   - Rule: only bind if positions are adjacent
   - Becomes combinatorially expensive

3. **Spatial Kappa extensions**:
   - Use compartmentalized Kappa if positions are discrete
   - Not ideal for 2D grid

**Recommended approach**: Implicit spatial structure with careful rule design to enforce lattice geometry

### Observable Patterns

```
# Count number of complete rows
%obs: 'Rows_complete' |RuleTile(bottom[_], right[_], top[.], left[.])|

# Detect presence of specific bit patterns
%obs: 'Binary_100' |TileC(bottom[1]), TileA(bottom[2]), TileA(bottom[3])|

# Count total assembled tiles
%obs: 'Total_tiles' |RuleTile(bottom[_])|
```

---

## CRITICAL QUOTES FROM PAPER

### On the Binary Counter System

> "These tiles implement a binary counter. The goal is simply to count 1, 2, 3, 4, 5, …, but in base 2, where it would be 1, 10, 11, 100, 101, …, with subsequent numbers written above the previous ones."

> "Shapes on the tiles represent information used in the computation: the top and bottom sides encode the value of bits in the counter, while the left and right sides are use to carry the rollover bit (more familiar in base 10, where 9 rolls over to 0 and increments the digit to its left)."

> "The four rule tiles can then be seen to effect the following logic: 'if there is no rollover from the bit on the right, this bit stays the same; but if there is a rollover from the bit on the right, 0 becomes 1, and 1 rolls over to 0.'"

### On Assembly Requirements

> "It is important to note that there are two new ingredients in this example. First, to ensure that the correct pattern results, the three input tiles are assembled before the rule tiles are used. (This restriction can be relaxed somewhat, but it is convenient for explanation.) Second, to avoid getting stuck with an incorrect partial tiling, one must add rule tiles only when both the tiles below and to their right are already present."

> "To use a biochemist's terminology, we require that binding be a highly cooperative event, and the reaction must take place at a temperature above the melting temperature of the single binding domain and below the melting temperature of a pair of cooperative binding domains."

### On Computational Universality

> "In the general case, this kind of tiling process can perform any kind of information processing task — that is to say, it is Turing-universal. A computer program can be automatically translated into a set of tiles that perform exactly the same mathematical function."

### On Determinism

> "As in the binary counter example, tile sets are typically designed such that a unique tile can fit into each location, and thus a unique tiling is deterministically produced."

### On Error Correction

> "Computer simulations suggest that error-free computational crystals will form in a large region of parameter space (Winfree preliminary, 1998)."

---

## ADDITIONAL CONTEXT

### Relationship to DNA Implementation

The paper experimentally demonstrates a **simpler system** (Figure 1: A-B striped lattice) using DNA double-crossover (DX) molecules:
- Two tile types (A and B) that form periodic stripes
- Tile dimensions: ~25 nm × 12.6 nm (from AFM measurements)
- Successful 2D lattice formation confirmed by AFM
- Crystals up to 2 × 8 μm observed (~500,000 tiles)

**Important**: The binary counter (Figure 3) is presented as a **theoretical example** to demonstrate computational capability. Its experimental implementation is **not reported** in this paper.

### Implications for Kappa Modeling

1. **Proof of concept exists**: DNA tiles CAN self-assemble into designed 2D lattices
2. **Scale is achievable**: Hundreds of thousands of tiles successfully assemble
3. **Cooperative binding works**: Temperature control enables kinetic proofreading
4. **Error rates are manageable**: Large, ordered structures form despite molecular stochasticity

### Future Experimental Directions Mentioned

> "Experimental work on these ideas is already in progress (LaBean et al. to appear)."

This suggests that DNA implementation of computational tile systems (like the binary counter) was planned/underway as of 2000.

---

## RECOMMENDATIONS FOR KAPPA MODEL

### Phase 1: Minimal Model
- 4-bit counter (seed + 4 boundary tiles each direction)
- 4 rule tile types
- Deterministic binding (no errors)
- Cooperative binding rule: require both neighbors
- Observables: count rows completed, track bit patterns

### Phase 2: Kinetic Model
- Introduce kon/koff rates
- Model single-domain vs. two-domain binding energetics
- Simulate annealing (temperature-dependent rates)
- Add error probabilities

### Phase 3: Stochastic Validation
- Run multiple simulations with different random seeds
- Compare assembly success rates vs. error rates
- Validate against qualitative expectations from paper
- Explore parameter space (temperature, concentrations)

### Key Questions to Answer with Model

1. What is the minimum cooperative binding advantage needed for error-free assembly?
2. How does assembly time scale with counter size?
3. What is the optimal tile concentration ratio?
4. How sensitive is assembly to kinetic parameters?
5. Can the model reproduce qualitative behavior described in paper?

---

## SUMMARY

The binary counter demonstrates that tile self-assembly can perform computation through local matching rules. The system uses 7 tile types (1 seed, 2 boundary types, 4 rule types) that assemble on a 2D lattice following strict geometric and temporal constraints. Correct assembly requires:

1. **Staged assembly**: Input tiles before rule tiles
2. **Cooperative binding**: Two-edge matching for stable attachment
3. **Temperature control**: Between single and double-domain Tm
4. **Deterministic rules**: Unique tile type per position

The system is theoretically Turing-universal, though the specific binary counter example is not experimentally validated in this paper. The simpler A-B lattice system provides experimental proof-of-concept for DNA tile self-assembly.

For Kappa modeling, the key challenge is representing 2D spatial constraints. Recommended approach: use binding graph connectivity to implicitly encode lattice geometry, enforce cooperative binding rules explicitly, and start with simplified deterministic model before adding stochastic kinetics.
