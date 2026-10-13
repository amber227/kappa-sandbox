#!/usr/bin/env python3
"""
Consolidate interactions from all protein digest files into a single interactions.json file.
Then remove the interactions field from all digest files.
"""
import json
from pathlib import Path
from datetime import datetime
import sys

def generate_interaction_id(gene_a, gene_b):
    """Generate consistent interaction ID with alphabetical ordering."""
    sorted_genes = sorted([gene_a, gene_b])
    return f"{sorted_genes[0]}_{sorted_genes[1]}"

def consolidate_interactions():
    """Extract all interactions from digest files and consolidate."""
    digest_files = list(Path('.').glob('*_digest.json'))

    # Dictionary to store interactions by ID
    all_interactions = {}
    protein_coverage = set()

    for digest_file in digest_files:
        print(f"Processing {digest_file}...", file=sys.stderr)

        with open(digest_file, 'r') as f:
            data = json.load(f)

        gene_name = data['protein_identifier']['gene_name']
        protein_coverage.add(gene_name)

        # Extract interactions if present
        if 'interactions' in data and data['interactions']:
            for interaction in data['interactions']:
                partner_gene = interaction['partner']['gene_name']

                # Generate consistent interaction ID
                interaction_id = generate_interaction_id(gene_name, partner_gene)

                # Determine ordering (alphabetical)
                genes_sorted = sorted([gene_name, partner_gene])
                is_forward = gene_name == genes_sorted[0]

                # Create standardized interaction entry
                std_interaction = {
                    "interaction_id": interaction_id,
                    "protein_a": {
                        "gene_name": genes_sorted[0],
                        "protein_name": data['protein_identifier']['protein_name'] if is_forward else interaction['partner']['protein_name'],
                        "uniprot_accession": data['protein_identifier']['uniprot_accession'] if is_forward else interaction['partner']['uniprot_accession']
                    },
                    "protein_b": {
                        "gene_name": genes_sorted[1],
                        "protein_name": interaction['partner']['protein_name'] if is_forward else data['protein_identifier']['protein_name'],
                        "uniprot_accession": interaction['partner']['uniprot_accession'] if is_forward else data['protein_identifier']['uniprot_accession']
                    },
                    "interaction_type": interaction.get('interaction_type', ''),
                    "mechanism": interaction.get('mechanism', ''),
                    "direction": interaction.get('direction', ''),
                    "sites": interaction.get('sites', {}),
                    "kinetics": interaction.get('kinetics', {}),
                    "evidence": interaction.get('evidence', []),
                    "functional_effect": interaction.get('functional_effect', ''),
                    "pathway_context": interaction.get('pathway_context', '')
                }

                # Adjust direction if we flipped the protein order
                if not is_forward and std_interaction['direction']:
                    direction = std_interaction['direction']
                    if direction == 'this_modifies_partner':
                        std_interaction['direction'] = 'b_modifies_a'
                    elif direction == 'partner_modifies_this':
                        std_interaction['direction'] = 'a_modifies_b'

                # Also adjust site naming if we flipped
                if not is_forward and std_interaction['sites']:
                    sites = std_interaction['sites']
                    if 'this_protein' in sites or 'partner_protein' in sites:
                        std_interaction['sites'] = {
                            "protein_a": sites.get('partner_protein', []),
                            "protein_b": sites.get('this_protein', []),
                            "site_specific": sites.get('site_specific', False)
                        }
                    elif 'protein_a' in sites or 'protein_b' in sites:
                        # Already in correct format
                        pass

                # Add or merge this interaction
                if interaction_id in all_interactions:
                    # Merge evidence
                    existing = all_interactions[interaction_id]
                    for ev in std_interaction['evidence']:
                        if ev not in existing['evidence']:
                            existing['evidence'].append(ev)
                else:
                    all_interactions[interaction_id] = std_interaction

    # Create consolidated interactions file
    interactions_data = {
        "interactions": list(all_interactions.values()),
        "metadata": {
            "last_updated": datetime.now().isoformat() + "Z",
            "protein_coverage": sorted(list(protein_coverage))
        }
    }

    print(f"\nFound {len(all_interactions)} unique interactions across {len(protein_coverage)} proteins", file=sys.stderr)

    # Write consolidated interactions.json
    with open('interactions.json', 'w') as f:
        json.dump(interactions_data, f, indent=2)

    print("Wrote interactions.json", file=sys.stderr)

    # Now remove interactions field from all digest files
    for digest_file in digest_files:
        with open(digest_file, 'r') as f:
            data = json.load(f)

        if 'interactions' in data:
            del data['interactions']

            with open(digest_file, 'w') as f:
                json.dump(data, f, indent=2)

            print(f"Removed interactions from {digest_file}", file=sys.stderr)

    # Remove old separate interaction files
    for old_file in Path('.').glob('*_interactions.json'):
        if old_file.name != 'interactions.json':
            old_file.unlink()
            print(f"Deleted {old_file}", file=sys.stderr)

    print("\nConsolidation complete!", file=sys.stderr)

if __name__ == '__main__':
    consolidate_interactions()
