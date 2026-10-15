#!/usr/bin/env python3
"""
Generate protein digests for all missing proteins identified by find_missing_digests.py

This script reads missing_digests.json and spawns protein-info-digest agents
for each missing protein.
"""
import json
import subprocess
import sys
from pathlib import Path


def generate_digests(min_interactions: int = 1, max_concurrent: int = 10):
    """
    Generate digests for missing proteins.

    Args:
        min_interactions: Only generate for proteins with at least this many interactions
        max_concurrent: Maximum number of concurrent agent processes
    """
    # Load missing proteins
    missing_file = Path("missing_digests.json")
    if not missing_file.exists():
        print("Error: missing_digests.json not found. Run find_missing_digests.py first.")
        sys.exit(1)

    with open(missing_file, 'r') as f:
        data = json.load(f)

    missing_proteins = data['missing_proteins']

    # Filter by interaction count
    proteins_to_generate = [
        p for p in missing_proteins
        if p['num_interactions'] >= min_interactions
    ]

    print(f"Generating digests for {len(proteins_to_generate)} proteins")
    print(f"(filtered to proteins with >= {min_interactions} interactions)\n")

    # Group into batches for concurrent execution
    batches = []
    for i in range(0, len(proteins_to_generate), max_concurrent):
        batch = proteins_to_generate[i:i+max_concurrent]
        batches.append(batch)

    # Print what will be generated
    print("Proteins to generate:")
    for i, protein in enumerate(proteins_to_generate, 1):
        print(f"  {i}. {protein['gene_name']:<15} "
              f"({protein['num_interactions']} interactions) - {protein['protein_name']}")
    print()

    # Confirm before proceeding
    response = input(f"Proceed with generating {len(proteins_to_generate)} digests? [y/N]: ")
    if response.lower() != 'y':
        print("Aborted.")
        sys.exit(0)

    # Generate command for spawning agents
    # Note: This outputs a command that should be run in Claude Code
    print("\n" + "="*80)
    print("INSTRUCTIONS FOR CLAUDE CODE:")
    print("="*80)
    print("\nPlease execute the following in parallel batches:\n")

    for batch_num, batch in enumerate(batches, 1):
        print(f"# Batch {batch_num} ({len(batch)} proteins)")
        print("# Run these agents in parallel by invoking all Task tools in a single message:\n")

        for protein in batch:
            gene = protein['gene_name']
            name = protein['protein_name']
            print(f'Task(subagent_type="protein-info-digest", ')
            print(f'     description="Generate {gene} digest",')
            print(f'     prompt="Generate a comprehensive protein information digest for human {gene} ({name}) '
                  f'following the standardized schema. Create both {gene}_digest.json and update '
                  f'interactions.json with all discovered interactions. Keep your final summary brief (max 500 words).")')
        print()

    print("\nNote: After all digests are generated, run compile_kappa.py again to generate")
    print("      the updated Kappa model with all available interactions.")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate missing protein digests")
    parser.add_argument('--min-interactions', type=int, default=1,
                        help='Minimum number of interactions (default: 1)')
    parser.add_argument('--max-concurrent', type=int, default=10,
                        help='Maximum concurrent agents per batch (default: 10)')

    args = parser.parse_args()

    generate_digests(
        min_interactions=args.min_interactions,
        max_concurrent=args.max_concurrent
    )
