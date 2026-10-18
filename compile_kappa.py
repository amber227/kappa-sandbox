#!/usr/bin/env python3
"""
Compile protein database (digest JSONs + interactions.json) into a Kappa model.

This program generates a .ka file with full provenance tracking, allowing
each Kappa component to be traced back to specific schema sections that
informed its generation.
"""
import json
import os
import random
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime
import re

import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = "https://openrouter.ai/api/v1/chat/completions"


@dataclass
class Citation:
    """A citation to a specific part of a schema file."""
    source_file: str
    json_path: str  # JSONPath to the cited data
    value: Any
    reasoning: str  # Natural language explanation of how this influenced the output


@dataclass
class AgentSignature:
    """Generated agent signature with provenance."""
    agent_name: str
    kappa_signature: str
    citations: List[Citation] = field(default_factory=list)

    def to_dict(self):
        return {
            "agent_name": self.agent_name,
            "kappa_signature": self.kappa_signature,
            "citations": [asdict(c) for c in self.citations]
        }


@dataclass
class KappaRule:
    """Generated Kappa rule with provenance."""
    rule_name: str
    kappa_rule: str
    unimolecular_rate: Optional[float]
    bimolecular_rate: Optional[float]
    citations: List[Citation] = field(default_factory=list)
    rate_citations: List[Citation] = field(default_factory=list)  # Specific to rate constants

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "kappa_rule": self.kappa_rule,
            "unimolecular_rate": self.unimolecular_rate,
            "bimolecular_rate": self.bimolecular_rate,
            "citations": [asdict(c) for c in self.citations],
            "rate_citations": [asdict(c) for c in self.rate_citations]
        }


@dataclass
class CompilationResult:
    """Complete compilation output with provenance."""
    agents: List[AgentSignature]
    rules: List[KappaRule]
    metadata: Dict[str, Any]

    def to_dict(self):
        return {
            "agents": [a.to_dict() for a in self.agents],
            "rules": [r.to_dict() for r in self.rules],
            "metadata": self.metadata
        }


class KappaCompiler:
    """Compile protein database into Kappa model with provenance tracking."""

    def __init__(self, digest_dir: Path = Path(".")):
        self.digest_dir = digest_dir
        self.digests = {}
        self.interactions = None

    def load_data(self):
        """Load all protein digests and interactions."""
        # Load protein digests
        for digest_file in self.digest_dir.glob("*_digest.json"):
            with open(digest_file, 'r') as f:
                data = json.load(f)
                gene_name = data['protein_identifier']['gene_name']
                self.digests[gene_name] = data

        # Load interactions
        interactions_file = self.digest_dir / "interactions.json"
        with open(interactions_file, 'r') as f:
            self.interactions = json.load(f)

        print(f"Loaded {len(self.digests)} protein digests")
        print(f"Loaded {len(self.interactions['interactions'])} interactions")

    def generate_agent_signature(self, gene_name: str, digest: Dict) -> AgentSignature:
        """
        Generate Kappa agent signature deterministically from protein digest.

        Agent name: From protein_identifier.gene_name
        Sites: From domains_and_motifs and post_translational_modifications
        """
        citations = []

        # Agent name from gene_name
        citations.append(Citation(
            source_file=f"{gene_name}_digest.json",
            json_path="protein_identifier.gene_name",
            value=gene_name,
            reasoning="Agent name derived from gene name"
        ))

        sites = []
        site_definitions = []

        # Add sites from domains and motifs
        for i, domain in enumerate(digest.get('domains_and_motifs', [])):
            domain_id = domain.get('identifier', f"domain_{i}")
            # Sanitize domain ID for Kappa (alphanumeric + underscore)
            site_name = re.sub(r'[^a-zA-Z0-9_]', '_', domain_id)

            # For binding domains, add binding site
            if domain.get('type') in ['Domain', 'Binding_site', 'SH2', 'SH3', 'PDZ', 'PTB', 'WW']:
                sites.append(f"{site_name}[_]")  # Wildcard binding state
                site_definitions.append({
                    "name": site_name,
                    "type": "binding",
                    "source": "domain"
                })
                citations.append(Citation(
                    source_file=f"{gene_name}_digest.json",
                    json_path=f"domains_and_motifs[{i}].identifier",
                    value=domain_id,
                    reasoning=f"Binding site '{site_name}' from {domain.get('type')} domain"
                ))

        # Add sites from post-translational modifications
        for i, ptm in enumerate(digest.get('post_translational_modifications', [])):
            ptm_type = ptm.get('type', 'mod')
            position = ptm.get('position', 'unknown')
            residue = ptm.get('residue', 'X')

            # Create site name: e.g., phos_S123
            site_name = f"{self._ptm_abbrev(ptm_type)}_{residue}{position}"

            # Add state variable (modified/unmodified)
            sites.append(f"{site_name}{{u p}}")  # u=unmodified, p=phosphorylated/modified
            site_definitions.append({
                "name": site_name,
                "type": "modification",
                "source": "ptm"
            })
            citations.append(Citation(
                source_file=f"{gene_name}_digest.json",
                json_path=f"post_translational_modifications[{i}]",
                value=f"{ptm_type} at {residue}{position}",
                reasoning=f"Modification site '{site_name}' with states {{u,p}} from {ptm_type}"
            ))

        # Construct Kappa signature
        if sites:
            signature = f"%agent: {gene_name}({', '.join(sites)})"
        else:
            # Agent with no sites
            signature = f"%agent: {gene_name}()"

        return AgentSignature(
            agent_name=gene_name,
            kappa_signature=signature,
            citations=citations
        )

    def _ptm_abbrev(self, ptm_type: str) -> str:
        """Abbreviate PTM type for site names."""
        abbrevs = {
            'Phosphorylation': 'phos',
            'Ubiquitination': 'ub',
            'Acetylation': 'ac',
            'Methylation': 'me',
            'Sumoylation': 'sumo',
            'Palmitoylation': 'palm',
            'Glycosylation': 'glyc'
        }
        return abbrevs.get(ptm_type, 'mod')

    def generate_rule_with_llm(self, interaction: Dict, gene_a_digest: Dict,
                                gene_b_digest: Dict) -> KappaRule:
        """
        Generate Kappa rule from interaction using LLM.

        Bundles interaction data with relevant protein digests and uses LLM
        to reason about the interaction and generate appropriate Kappa rule.
        """
        # Extract relevant information
        gene_a = interaction['protein_a']['gene_name']
        gene_b = interaction['protein_b']['gene_name']
        interaction_id = interaction['interaction_id']

        # Build prompt with compressed Kappa context
        prompt = self._build_rule_generation_prompt(
            interaction, gene_a_digest, gene_b_digest
        )

        # Call LLM
        response = self._call_llm(prompt)

        # Parse response to extract rule, rates, and citations
        rule_data = self._parse_llm_response(response, interaction_id)

        return KappaRule(
            rule_name=rule_data['rule_name'],
            kappa_rule=rule_data['kappa_rule'],
            unimolecular_rate=rule_data.get('unimolecular_rate'),
            bimolecular_rate=rule_data.get('bimolecular_rate'),
            citations=rule_data['citations'],
            rate_citations=rule_data['rate_citations']
        )

    def _build_rule_generation_prompt(self, interaction: Dict,
                                       gene_a_digest: Dict,
                                       gene_b_digest: Dict) -> str:
        """Build LLM prompt for rule generation."""

        gene_a = interaction['protein_a']['gene_name']
        gene_b = interaction['protein_b']['gene_name']

        # Load full Kappa context from SKILL.md
        skill_path = Path(".claude/skills/modeler/SKILL.md")
        with open(skill_path, 'r') as f:
            kappa_context = f.read()

        # Extract relevant digest information
        gene_a_info = self._extract_digest_summary(gene_a_digest, gene_a)
        gene_b_info = self._extract_digest_summary(gene_b_digest, gene_b)

        prompt = f"""{kappa_context}

# Task
Generate a Kappa rule for the following protein-protein interaction. Your response must be in JSON format with specific citations to the schema.

# Interaction Data
```json
{json.dumps(interaction, indent=2)}
```

# Protein A ({gene_a}) Information
```json
{json.dumps(gene_a_info, indent=2)}
```

# Protein B ({gene_b}) Information
```json
{json.dumps(gene_b_info, indent=2)}
```

# Required JSON Response Format
{{
  "rule_name": "descriptive_name",
  "kappa_rule": "complete Kappa rule string",
  "unimolecular_rate": null or float (if applicable),
  "bimolecular_rate": null or float (if applicable),
  "citations": [
    {{
      "source_file": "interactions.json or <GENE>_digest.json",
      "json_path": "path.to.field",
      "value": "cited value",
      "reasoning": "how this influenced the rule"
    }}
  ],
  "rate_citations": [
    {{
      "source_file": "file containing kinetic data",
      "json_path": "path to kinetic parameter",
      "value": "parameter value",
      "reasoning": "how rate constant was derived"
    }}
  ]
}}

# Instructions
1. Analyze the interaction mechanism and kinetics
2. Determine if this is binding, modification, or complex
3. Generate appropriate Kappa rule following syntax above
4. Extract rate constants from kinetics data when available
5. Provide detailed citations for every decision
6. For rate_citations, specifically cite the source of k_on, k_off, Kd, etc.

Return ONLY valid JSON, no additional text.
"""
        return prompt

    def _extract_digest_summary(self, digest: Dict, gene_name: str) -> Dict:
        """Extract relevant information from digest for LLM context."""
        return {
            "gene_name": gene_name,
            "protein_name": digest['protein_identifier']['protein_name'],
            "domains_and_motifs": digest.get('domains_and_motifs', []),
            "post_translational_modifications": digest.get('post_translational_modifications', [])
        }

    def _call_llm(self, prompt: str, model: str = "z-ai/glm-5.3") -> str:
        """Call OpenRouter API with the given prompt."""
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/amber227/kappa-sandbox",
            "X-Title": "Kappa Model Compiler"
        }

        payload = {
            "model": model,  # Using free Llama model
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)

        # Debug: print response details on error
        if response.status_code != 200:
            print(f"API Error: Status {response.status_code}")
            print(f"Response: {response.text}")

        response.raise_for_status()

        result = response.json()
        return result['choices'][0]['message']['content']

    def _parse_llm_response(self, response: str, interaction_id: str) -> Dict:
        """Parse LLM JSON response into structured data."""
        # Extract JSON from response (handle markdown code blocks)
        json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response, re.DOTALL)
        if json_match:
            json_str = json_match.group(1)
        else:
            # Try to parse entire response as JSON
            json_str = response.strip()

        try:
            data = json.loads(json_str)
        except json.JSONDecodeError as e:
            print(f"Failed to parse LLM response for {interaction_id}:")
            print(response)
            raise e

        # Convert citation dicts to Citation objects
        citations = [Citation(**c) for c in data.get('citations', [])]
        rate_citations = [Citation(**c) for c in data.get('rate_citations', [])]

        return {
            'rule_name': data['rule_name'],
            'kappa_rule': data['kappa_rule'],
            'unimolecular_rate': data.get('unimolecular_rate'),
            'bimolecular_rate': data.get('bimolecular_rate'),
            'citations': citations,
            'rate_citations': rate_citations
        }

    def compile(self) -> CompilationResult:
        """Run full compilation pipeline."""
        print("Starting compilation...")

        # Generate agent signatures
        agents = []
        for gene_name, digest in self.digests.items():
            print(f"Generating agent signature for {gene_name}...")
            agent = self.generate_agent_signature(gene_name, digest)
            agents.append(agent)

        # Generate rules from interactions
        rules = []
        for i, interaction in enumerate(self.interactions['interactions']):
            gene_a = interaction['protein_a']['gene_name']
            gene_b = interaction['protein_b']['gene_name']

            # Only process if we have both digests
            if gene_a not in self.digests or gene_b not in self.digests:
                print(f"Skipping interaction {interaction['interaction_id']}: missing digest")
                continue

            print(f"Generating rule {i+1}/{len(self.interactions['interactions'])}: {interaction['interaction_id']}...")

            try:
                rule = self.generate_rule_with_llm(
                    interaction,
                    self.digests[gene_a],
                    self.digests[gene_b]
                )
                rules.append(rule)
            except Exception as e:
                print(f"Error generating rule for {interaction['interaction_id']}: {e}")
                continue

        # Create metadata
        metadata = {
            "generated_at": datetime.now().isoformat(),
            "num_agents": len(agents),
            "num_rules": len(rules),
            "source_files": {
                "digests": list(self.digests.keys()),
                "interactions": "interactions.json"
            }
        }

        return CompilationResult(
            agents=agents,
            rules=rules,
            metadata=metadata
        )

    def write_kappa_file(self, result: CompilationResult, output_file: Path):
        """Write compiled result to .ka file."""
        with open(output_file, 'w') as f:
            f.write("# Kappa model compiled from protein database\n")
            f.write(f"# Generated: {result.metadata['generated_at']}\n")
            f.write(f"# Agents: {result.metadata['num_agents']}, Rules: {result.metadata['num_rules']}\n")
            f.write("\n")

            # Write agent signatures
            f.write("# Agent Signatures\n")
            for agent in result.agents:
                f.write(f"{agent.kappa_signature}\n")
            f.write("\n")

            # Write rules
            f.write("# Rules\n")
            for rule in result.rules:
                f.write(f"{rule.kappa_rule}\n")
            f.write("\n")

    def write_provenance_file(self, result: CompilationResult, output_file: Path):
        """Write provenance data to JSON file."""
        with open(output_file, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)


def main():
    # Set random seed for reproducibility
    random.seed(42)

    # Initialize compiler
    compiler = KappaCompiler()

    # Load data
    compiler.load_data()

    # Compile
    result = compiler.compile()

    # Write outputs
    compiler.write_kappa_file(result, Path("wnt_compiled.ka"))
    compiler.write_provenance_file(result, Path("wnt_compiled_provenance.json"))

    print(f"\nCompilation complete!")
    print(f"  Generated {len(result.agents)} agents")
    print(f"  Generated {len(result.rules)} rules")
    print(f"  Kappa file: wnt_compiled.ka")
    print(f"  Provenance: wnt_compiled_provenance.json")


if __name__ == "__main__":
    main()
