#!/usr/bin/env python3
"""
Kappa Reachability Explorer - Backend Server

Flask server that serves a web UI for exploring rule reachability in Kappa models.
Allows marking lines and visualizing which rules are reachable from those marks.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Set
from flask import Flask, jsonify, request, send_from_directory

from pykappa.system import System
from pykappa.pattern import Component, Agent
from causal_graph import CausalGraph, SourceMap

app = Flask(__name__, static_folder='static', static_url_path='')


class ReachabilityExplorer:
    """Handles Kappa file parsing, marking, and reachability computation."""

    def __init__(self, ka_file: Path):
        self.ka_file = ka_file

        # Load file content
        with open(ka_file, 'r') as f:
            self.ka_lines = f.readlines()

        # Parse with PyKappa
        self.system = System.read_ka(ka_file)

        # Build source map
        self.source_map = SourceMap(ka_file)
        self.source_map.map_rules(self.system)

        # Build causal graph
        self.causal_graph = CausalGraph(self.system)

        # Track marked lines (separate sets for source and destination)
        self.source_lines: Set[int] = set()
        self.destination_lines: Set[int] = set()

        # Build line type mapping
        self.line_types = self._build_line_types()

    def _build_line_types(self) -> Dict[int, str]:
        """
        Identify what type each line is (init, rule, agent, etc.)

        Returns dict: {line_number: 'init'|'rule'|'agent'|'other'}
        """
        line_types = {}

        for line_num, line in enumerate(self.ka_lines, start=1):
            line_stripped = line.strip()

            if line_stripped.startswith('%init:'):
                line_types[line_num] = 'init'
            elif '->' in line_stripped and '@' in line_stripped and not line_stripped.startswith('//'):
                line_types[line_num] = 'rule'
            elif line_stripped.startswith('%agent:'):
                line_types[line_num] = 'agent'
            else:
                line_types[line_num] = 'other'

        return line_types

    def mark_source(self, line_num: int):
        """Mark a line as source."""
        self.source_lines.add(line_num)
        # Remove from destination if it was there
        self.destination_lines.discard(line_num)

    def unmark_source(self, line_num: int):
        """Unmark a line as source."""
        self.source_lines.discard(line_num)

    def mark_destination(self, line_num: int):
        """Mark a line as destination."""
        self.destination_lines.add(line_num)
        # Remove from source if it was there
        self.source_lines.discard(line_num)

    def unmark_destination(self, line_num: int):
        """Unmark a line as destination."""
        self.destination_lines.discard(line_num)

    def compute_reachable_rules(self) -> Dict[int, str]:
        """
        Compute which rules are reachable from source lines to destination lines.

        If no destinations are marked: returns all rules reachable from sources
        If destinations are marked: returns only rules on paths from sources to destinations

        Returns dict: {line_number: rule_name} for reachable rule lines
        """
        # Collect init agents from marked source init lines
        init_agents = []

        # Collect RHS agents from marked source rules
        rhs_agents = []

        for line_num in self.source_lines:
            line_type = self.line_types.get(line_num)

            if line_type == 'init':
                # Extract agent from init line
                line = self.ka_lines[line_num - 1].strip()
                # Parse: %init: <count> <agent_pattern>
                match = re.match(r'%init:\s*\d+\s+(\w+)\(', line)
                if match:
                    agent_name = match.group(1)
                    # Find agents in the system's initial mixture with this name
                    for agent in self.system.mixture.agents:
                        # Parse agent name from kappa_str
                        agent_str = agent.kappa_str
                        agent_match = re.match(r'(\w+)\(', agent_str)
                        if agent_match and agent_match.group(1) == agent_name:
                            init_agents.append(agent)

            elif line_type == 'rule':
                # Find the rule corresponding to this line
                for rule_name, rule in self.system.rules.items():
                    source_line = self.source_map.get_rule_source(rule_name)
                    if source_line == line_num:
                        # Add all RHS agents from this rule
                        rhs_agents.extend(rule.right.agents)
                        break

        # Combine init and RHS agents
        all_init_agents = init_agents + rhs_agents

        if not all_init_agents:
            return {}

        # Collect destination rule names
        destination_rule_names = []
        for line_num in self.destination_lines:
            line_type = self.line_types.get(line_num)
            if line_type == 'rule':
                # Find the rule corresponding to this line
                for rule_name, rule in self.system.rules.items():
                    source_line = self.source_map.get_rule_source(rule_name)
                    if source_line == line_num:
                        destination_rule_names.append(rule_name)
                        break

        # Compute reachable rules
        if destination_rule_names:
            # Use find_paths to get rules on paths from sources to destinations
            path_graph = self.causal_graph.find_paths(all_init_agents, destination_rule_names)
            reachable_rule_names = list(path_graph.edges.keys())
            # Also include destination rules themselves
            reachable_rule_names = list(set(reachable_rule_names) | set(destination_rule_names))
        else:
            # No destinations: just compute forward reachability from sources
            reachable_rule_names = self.causal_graph.reachable(all_init_agents)

        # Map back to line numbers
        reachable_lines = {}
        for rule_name in reachable_rule_names:
            source_line = self.source_map.get_rule_source(rule_name)
            if source_line:
                reachable_lines[source_line] = rule_name

        return reachable_lines


# Global state
current_explorer: Optional[ReachabilityExplorer] = None


def discover_ka_files(directory: Path = Path(".")) -> List[Dict[str, str]]:
    """
    Discover .ka files in directory.

    Returns list of {ka_file, display_name}
    """
    ka_files = []

    for ka_path in directory.glob("*.ka"):
        ka_files.append({
            'ka_file': str(ka_path.name),
            'display_name': ka_path.stem
        })

    return ka_files


@app.route('/')
def index():
    """Serve main UI."""
    return send_from_directory('static', 'reachability.html')


@app.route('/api/files', methods=['GET'])
def list_files():
    """List available .ka files."""
    files = discover_ka_files()
    return jsonify({'files': files})


@app.route('/api/load', methods=['POST'])
def load_file():
    """Load a .ka file."""
    global current_explorer

    data = request.json
    ka_file = data.get('ka_file')

    if not ka_file:
        return jsonify({'error': 'Missing ka_file parameter'}), 400

    ka_path = Path(ka_file)

    if not ka_path.exists():
        return jsonify({'error': 'File not found'}), 404

    try:
        current_explorer = ReachabilityExplorer(ka_path)

        return jsonify({
            'content': ''.join(current_explorer.ka_lines),
            'lines': len(current_explorer.ka_lines),
            'line_types': current_explorer.line_types
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/mark_source', methods=['POST'])
def mark_source():
    """Mark a line as source."""
    if current_explorer is None:
        return jsonify({'error': 'No file loaded'}), 400

    data = request.json
    line_num = data.get('line_num')

    if line_num is None:
        return jsonify({'error': 'Missing line_num parameter'}), 400

    current_explorer.mark_source(line_num)

    # Recompute reachable rules
    reachable_lines = current_explorer.compute_reachable_rules()

    return jsonify({
        'source_lines': list(current_explorer.source_lines),
        'destination_lines': list(current_explorer.destination_lines),
        'reachable_lines': reachable_lines
    })


@app.route('/api/unmark_source', methods=['POST'])
def unmark_source():
    """Unmark a line as source."""
    if current_explorer is None:
        return jsonify({'error': 'No file loaded'}), 400

    data = request.json
    line_num = data.get('line_num')

    if line_num is None:
        return jsonify({'error': 'Missing line_num parameter'}), 400

    current_explorer.unmark_source(line_num)

    # Recompute reachable rules
    reachable_lines = current_explorer.compute_reachable_rules()

    return jsonify({
        'source_lines': list(current_explorer.source_lines),
        'destination_lines': list(current_explorer.destination_lines),
        'reachable_lines': reachable_lines
    })


@app.route('/api/mark_destination', methods=['POST'])
def mark_destination():
    """Mark a line as destination."""
    if current_explorer is None:
        return jsonify({'error': 'No file loaded'}), 400

    data = request.json
    line_num = data.get('line_num')

    if line_num is None:
        return jsonify({'error': 'Missing line_num parameter'}), 400

    current_explorer.mark_destination(line_num)

    # Recompute reachable rules
    reachable_lines = current_explorer.compute_reachable_rules()

    return jsonify({
        'source_lines': list(current_explorer.source_lines),
        'destination_lines': list(current_explorer.destination_lines),
        'reachable_lines': reachable_lines
    })


@app.route('/api/unmark_destination', methods=['POST'])
def unmark_destination():
    """Unmark a line as destination."""
    if current_explorer is None:
        return jsonify({'error': 'No file loaded'}), 400

    data = request.json
    line_num = data.get('line_num')

    if line_num is None:
        return jsonify({'error': 'Missing line_num parameter'}), 400

    current_explorer.unmark_destination(line_num)

    # Recompute reachable rules
    reachable_lines = current_explorer.compute_reachable_rules()

    return jsonify({
        'source_lines': list(current_explorer.source_lines),
        'destination_lines': list(current_explorer.destination_lines),
        'reachable_lines': reachable_lines
    })


@app.route('/api/state', methods=['GET'])
def get_state():
    """Get current marking state."""
    if current_explorer is None:
        return jsonify({'error': 'No file loaded'}), 400

    reachable_lines = current_explorer.compute_reachable_rules()

    return jsonify({
        'source_lines': list(current_explorer.source_lines),
        'destination_lines': list(current_explorer.destination_lines),
        'reachable_lines': reachable_lines
    })


if __name__ == '__main__':
    print("Starting Kappa Reachability Explorer...")
    print("Navigate to http://localhost:5002")
    app.run(debug=True, port=5002)
