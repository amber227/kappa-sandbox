"""
Parameter sweep experiment to quantify relationship between reaction rates
and time to equilibrium.

Runs n=100 replicates for each of 25 parameter combinations (5x5 grid of
binding/unbinding rates) and measures time to equilibrium.
"""

import random
import subprocess
import numpy as np
import pandas as pd
from pykappa.system import System
import matplotlib.pyplot as plt
import seaborn as sns
from tqdm import tqdm

# Get git commit hash for figure filename
try:
    git_hash = subprocess.check_output(['git', 'rev-parse', '--short', 'HEAD']).decode('ascii').strip()
except:
    git_hash = 'no-git'

# Experimental parameters
N_REPLICATES = 100
BINDING_RATES = np.logspace(-2, 0, 5)  # 0.01, 0.032, 0.1, 0.316, 1.0
UNBINDING_RATES = np.logspace(-2, 0, 5)  # 0.01, 0.032, 0.1, 0.316, 1.0
MAX_TIME = 50  # Maximum simulation time
EQUILIBRIUM_THRESHOLD = 0.02  # 2% change threshold
WINDOW_SIZE = 0.5  # Time window for equilibrium check

def measure_equilibrium_time(k_on, k_off, seed, max_time=MAX_TIME):
    """
    Run a single simulation and measure time to equilibrium.

    Equilibrium is defined as when the AB observable changes by less than
    EQUILIBRIUM_THRESHOLD (2%) over a time window of WINDOW_SIZE.

    Returns:
        float: Time to reach equilibrium, or max_time if not reached
    """
    random.seed(seed)
    np.random.seed(seed)

    system = System.from_ka(
        f"""
        %init: 100 A(x[.])
        %init: 100 B(x[.])

        %obs: 'AB' |A(x[1]), B(x[1])|

        A(x[.]), B(x[.]) <-> A(x[1]), B(x[1]) @ {k_on}, {k_off}
        """
    )

    # Track observables over time
    times = []
    ab_values = []

    while system.time < max_time:
        system.update()
        current_time = system.time

        # Count AB complexes by querying the mixture
        ab_count = system.mixture.count("A(x[1]), B(x[1])")

        times.append(current_time)
        ab_values.append(ab_count)

        # Check for equilibrium once we have enough data
        if current_time > WINDOW_SIZE:
            # Find values within the last WINDOW_SIZE time units
            recent_mask = np.array(times) > (current_time - WINDOW_SIZE)
            recent_ab = np.array(ab_values)[recent_mask]

            if len(recent_ab) > 1:
                # Calculate relative change in the window
                mean_ab = np.mean(recent_ab)
                if mean_ab > 0:
                    relative_change = (np.max(recent_ab) - np.min(recent_ab)) / mean_ab

                    if relative_change < EQUILIBRIUM_THRESHOLD:
                        return current_time

    return max_time

def run_parameter_sweep():
    """
    Run parameter sweep across binding and unbinding rates.

    Returns:
        pd.DataFrame: Results with columns [k_on, k_off, replicate, eq_time]
    """
    results = []

    total_sims = len(BINDING_RATES) * len(UNBINDING_RATES) * N_REPLICATES

    with tqdm(total=total_sims, desc="Running simulations") as pbar:
        for k_on in BINDING_RATES:
            for k_off in UNBINDING_RATES:
                for replicate in range(N_REPLICATES):
                    seed = hash((k_on, k_off, replicate)) % (2**32)
                    eq_time = measure_equilibrium_time(k_on, k_off, seed)

                    results.append({
                        'k_on': k_on,
                        'k_off': k_off,
                        'replicate': replicate,
                        'eq_time': eq_time
                    })

                    pbar.update(1)

    return pd.DataFrame(results)

def create_heatmap(df):
    """
    Create heatmap of mean equilibrium time vs binding/unbinding rates.
    """
    # Calculate mean equilibrium time for each parameter combination
    pivot_data = df.groupby(['k_on', 'k_off'])['eq_time'].mean().reset_index()
    heatmap_data = pivot_data.pivot(index='k_off', columns='k_on', values='eq_time')

    # Create figure
    fig, ax = plt.subplots(figsize=(10, 8))

    # Plot heatmap
    sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='viridis_r',
                cbar_kws={'label': 'Mean Time to Equilibrium'}, ax=ax)

    ax.set_xlabel('Binding Rate (k_on)', fontsize=12)
    ax.set_ylabel('Unbinding Rate (k_off)', fontsize=12)
    ax.set_title(f'Time to Equilibrium vs Reaction Rates\n(n={N_REPLICATES} replicates per combination)',
                 fontsize=14, pad=20)

    # Format tick labels to show actual rate values
    k_on_labels = [f'{k:.3f}' for k in BINDING_RATES]
    k_off_labels = [f'{k:.3f}' for k in UNBINDING_RATES[::-1]]  # Reversed for heatmap
    ax.set_xticklabels(k_on_labels, rotation=45, ha='right')
    ax.set_yticklabels(k_off_labels, rotation=0)

    plt.tight_layout()

    return fig

if __name__ == "__main__":
    print(f"Starting parameter sweep experiment...")
    print(f"Binding rates: {BINDING_RATES}")
    print(f"Unbinding rates: {UNBINDING_RATES}")
    print(f"Replicates per combination: {N_REPLICATES}")
    print(f"Total simulations: {len(BINDING_RATES) * len(UNBINDING_RATES) * N_REPLICATES}")
    print()

    # Run parameter sweep
    results_df = run_parameter_sweep()

    # Save results to CSV
    results_csv = f"parameter_sweep_results_{git_hash}.csv"
    results_df.to_csv(results_csv, index=False)
    print(f"\nResults saved to {results_csv}")

    # Print summary statistics
    print("\nSummary statistics by parameter combination:")
    summary = results_df.groupby(['k_on', 'k_off'])['eq_time'].agg(['mean', 'std', 'min', 'max'])
    print(summary)

    # Create and save heatmap
    fig = create_heatmap(results_df)
    heatmap_filename = f"equilibrium_time_heatmap_{git_hash}.png"
    fig.savefig(heatmap_filename, dpi=150, bbox_inches='tight')
    print(f"\nHeatmap saved to {heatmap_filename}")

    plt.show()
