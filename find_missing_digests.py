#!/usr/bin/env python3
"""
Analyze interactions.json to find proteins that need digest entries.

This script:
1. Reads all existing digest files
2. Reads interactions.json
3. Identifies all unique proteins mentioned in interactions
4. Reports which ones are missing digests
"""
import json
from pathlib import Path
from typing import Set, List
from dataclasses import dataclass


@dataclass
class MissingProtein:
    """Information about a protein that needs a digest."""
    gene_name: str
    protein_name: str
    uniprot_accession: str
    num_interactions: int


def find_existing_digests(digest_dir: Path = Path(".")) -> Set[str]:
    """Find all proteins that have digest files."""
    existing = set()
    for digest_file in digest_dir.glob("*_digest.json"):
        with open(digest_file, 'r') as f:
            data = json.load(f)
            gene_name = data['protein_identifier']['gene_name']
            existing.add(gene_name)
    return existing


def find_proteins_in_interactions(interactions_file: Path = Path("interactions.json")) -> dict:
    """Find all proteins mentioned in interactions.json."""
    with open(interactions_file, 'r') as f:
        data = json.load(f)

    proteins = {}  # gene_name -> {protein_name, uniprot, interaction_count}

    for interaction in data['interactions']:
        # Process protein_a
        gene_a = interaction['protein_a']['gene_name']
        if gene_a not in proteins:
            proteins[gene_a] = {
                'protein_name': interaction['protein_a']['protein_name'],
                'uniprot_accession': interaction['protein_a']['uniprot_accession'],
                'interaction_count': 0
            }
        proteins[gene_a]['interaction_count'] += 1

        # Process protein_b
        gene_b = interaction['protein_b']['gene_name']
        if gene_b not in proteins:
            proteins[gene_b] = {
                'protein_name': interaction['protein_b']['protein_name'],
                'uniprot_accession': interaction['protein_b']['uniprot_accession'],
                'interaction_count': 0
            }
        proteins[gene_b]['interaction_count'] += 1

    return proteins


def main():
    """Main analysis function."""
    print("Analyzing protein digest coverage...\n")

    # Find existing digests
    existing = find_existing_digests()
    print(f"Found {len(existing)} existing protein digests:")
    for gene in sorted(existing):
        print(f"  ✓ {gene}")
    print()

    # Find all proteins in interactions
    all_proteins = find_proteins_in_interactions()
    print(f"Found {len(all_proteins)} unique proteins in interactions.json\n")

    # Identify missing proteins
    missing = []
    for gene_name, info in all_proteins.items():
        if gene_name not in existing:
            missing.append(MissingProtein(
                gene_name=gene_name,
                protein_name=info['protein_name'],
                uniprot_accession=info['uniprot_accession'],
                num_interactions=info['interaction_count']
            ))

    # Sort by number of interactions (most important first)
    missing.sort(key=lambda p: p.num_interactions, reverse=True)

    # Report results
    print(f"Missing {len(missing)} protein digests:\n")
    print(f"{'Gene':<15} {'UniProt':<12} {'Interactions':<15} {'Protein Name'}")
    print("-" * 80)
    for protein in missing:
        print(f"{protein.gene_name:<15} {protein.uniprot_accession:<12} "
              f"{protein.num_interactions:<15} {protein.protein_name}")

    # Save to JSON for programmatic use
    output = {
        "existing_count": len(existing),
        "existing_proteins": sorted(list(existing)),
        "missing_count": len(missing),
        "missing_proteins": [
            {
                "gene_name": p.gene_name,
                "protein_name": p.protein_name,
                "uniprot_accession": p.uniprot_accession,
                "num_interactions": p.num_interactions
            }
            for p in missing
        ]
    }

    output_file = Path("missing_digests.json")
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nResults saved to {output_file}")
    print(f"\nSummary:")
    print(f"  Existing digests: {len(existing)}")
    print(f"  Missing digests: {len(missing)}")
    print(f"  Coverage: {len(existing)}/{len(all_proteins)} "
          f"({100*len(existing)/len(all_proteins):.1f}%)")

    # Calculate interaction coverage
    total_interactions = len(json.load(open("interactions.json"))['interactions'])
    missing_interaction_count = sum(p.num_interactions for p in missing)
    print(f"\nInteraction impact:")
    print(f"  {total_interactions} total interactions")
    print(f"  {missing_interaction_count} interactions involve missing proteins")


if __name__ == "__main__":
    main()
