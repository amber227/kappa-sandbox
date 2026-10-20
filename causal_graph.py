from pathlib import Path
from pykappa.system import System
from pykappa.pattern import Component, Agent
from collections import defaultdict
from typing import Iterable
import re

class SourceMap:
    '''
    Maps agents and rules back to their source lines in the .ka file.
    '''
    def __init__(self, model_path: Path):
        self.model_path = model_path
        self.agent_to_line = {}  # Maps agent kappa_str to line number
        self.rule_to_line = {}   # Maps rule name to line number

        self._parse_source()

    def _parse_source(self):
        '''Parse the .ka file to extract line numbers for %init and rules.'''
        with open(self.model_path, 'r') as f:
            lines = f.readlines()

        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.strip()

            # Parse %init lines - extract agent type name
            if line_stripped.startswith('%init:'):
                # Extract agent pattern after the count
                # Format: %init: <count> <agent_pattern>
                match = re.match(r'%init:\s*\d+\s+(\w+)\(', line_stripped)
                if match:
                    agent_name = match.group(1)
                    # Store the mapping from agent name to line number
                    # Use agent name as key since PyKappa expands signatures
                    self.agent_to_line[agent_name] = line_num

    def map_rules(self, system: System):
        '''
        Map rules from the system to their line numbers.
        This requires the parsed system to match rule strings with file lines.
        '''
        with open(self.model_path, 'r') as f:
            lines = f.readlines()

        # Build a mapping from normalized rule strings to line numbers
        rule_line_map = {}
        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.strip()
            if '->' in line_stripped and '@' in line_stripped and not line_stripped.startswith('//'):
                # Normalize: remove extra whitespace
                normalized = ' '.join(line_stripped.split())
                rule_line_map[normalized] = line_num

        # Now match system rules to file lines
        # This is heuristic: we'll try to match based on kappa_str similarity
        for rule_name, rule in system.rules.items():
            rule_str = rule.kappa_str
            # Try to find a matching line
            # The rule_str might not exactly match due to formatting
            # We'll use a simple approach: look for the rule components in the file

            # For now, use a simpler approach: match by order of appearance
            # This assumes rules are loaded in the same order they appear in the file
            pass

        # Simpler approach: just scan through and assign rules by order
        rule_names = list(system.rules.keys())
        rule_lines = []
        for line_num, line in enumerate(lines, start=1):
            line_stripped = line.strip()
            if '->' in line_stripped and '@' in line_stripped and not line_stripped.startswith('//'):
                rule_lines.append(line_num)

        # Assign rules to lines in order
        for i, rule_name in enumerate(rule_names):
            if i < len(rule_lines):
                self.rule_to_line[rule_name] = rule_lines[i]

    def get_agent_source(self, agent: Agent) -> int:
        '''Get the source line number for an agent.'''
        # Extract agent name from the agent
        # agent.kappa_str format is like "Axin(...)"
        agent_name = agent.agent_name if hasattr(agent, 'agent_name') else None
        if not agent_name:
            # Parse from kappa_str
            match = re.match(r'(\w+)\(', agent.kappa_str)
            if match:
                agent_name = match.group(1)
        return self.agent_to_line.get(agent_name)

    def get_rule_source(self, rule_name: str) -> int:
        '''Get the source line number for a rule.'''
        return self.rule_to_line.get(rule_name)

class CausalGraph:
    '''
    A labelled directed graph representing the potential causal
    prerequisites of a rule firing, in . 

    An edge from Rule A to Rule B . 
    '''
    edges: dict[str, set] # Rule names
    edge_labels: dict[(str, str), set]

    def __init__(self, system):
        self.system = system
        self.edges = defaultdict(set)
        self.edge_labels = defaultdict(set)

        for name_a, rule_a in system.rules.items():
            for name_b, rule_b in system.rules.items():
                for agent_a in rule_a.left.agents:
                    if agent_a is None:
                        continue
                    # Check if agent_a embeds into any agent in rule_b's RHS
                    embeds = False
                    for agent_b in rule_b.right.agents:
                        if agent_b is None:
                            continue
                        if any(True for _ in Component([agent_a]).embeddings(Component([agent_b]))):
                            embeds = True
                            break
                    if embeds:
                        self.edges[name_a].add(name_b)
                        self.edge_labels[(name_a, name_b)].add(agent_a)

    def unreachable(self, init: Iterable[Agent]) -> list[str]:
        '''
        Returns a list of rule names that can't be reached from the agents in `init`.

        A rule is reachable if every agent in its LHS embeds into either an agent in
        `init`, or the RHS of another reachable rule.
        '''
        init_agents = list(init)
        reachable = set()
        all_rule_names = set(self.system.rules.keys())

        changed = True
        while changed:
            changed = False
            for rule_name, rule in self.system.rules.items():
                if rule_name in reachable:
                    continue

                # Collect all agents from RHS of reachable rules and init
                available_agents = list(init_agents)
                for reachable_name in reachable:
                    reachable_rule = self.system.rules[reachable_name]
                    available_agents.extend(reachable_rule.right.agents)

                # Check if all LHS agents of this rule embed into available_agents
                all_embed = True
                for lhs_agent in rule.left.agents:
                    if lhs_agent is None:
                        continue
                    if not self._agent_embeds_into_agents(lhs_agent, available_agents):
                        all_embed = False
                        break

                if all_embed:
                    reachable.add(rule_name)
                    changed = True

        unreachable_rules = list(all_rule_names - reachable)
        return unreachable_rules

    def reachable(self, init: Iterable[Agent]) -> list[str]:
        '''
        Returns a list of rule names that can be reached from the agents in `init`.

        A rule is reachable if every agent in its LHS embeds into either an agent in
        `init`, or the RHS of another reachable rule.
        '''
        init_agents = list(init)
        reachable = set()

        changed = True
        while changed:
            changed = False
            for rule_name, rule in self.system.rules.items():
                if rule_name in reachable:
                    continue

                # Collect all agents from RHS of reachable rules and init
                available_agents = list(init_agents)
                for reachable_name in reachable:
                    reachable_rule = self.system.rules[reachable_name]
                    available_agents.extend(reachable_rule.right.agents)

                # Check if all LHS agents of this rule embed into available_agents
                all_embed = True
                for lhs_agent in rule.left.agents:
                    if lhs_agent is None:
                        continue
                    if not self._agent_embeds_into_agents(lhs_agent, available_agents):
                        all_embed = False
                        break

                if all_embed:
                    reachable.add(rule_name)
                    changed = True

        return list(reachable)

    def _agent_embeds_into_agents(self, agent: Agent, target_agents: list[Agent]) -> bool:
        '''Check if an agent embeds into any agent in target_agents.'''
        for target in target_agents:
            if target is None:
                continue
            # Check if agent embeds into target
            # Note: embeddings() returns a generator, must consume it to check if non-empty
            embeddings_gen = Component([agent]).embeddings(Component([target]))
            if any(True for _ in embeddings_gen):
                return True
        return False

    def find_paths(self, init: Iterable[Agent], target: list[str]) -> 'CausalGraph':
        '''
        Returns a CausalGraph containing all paths from anything in init to any rule in target.

        A path is any sequence of directed edges in the causal graph. This uses pure graph
        traversal (not simulation-based reachability), meaning a rule is "connected" to init
        if at least one of its LHS agents embeds into an init agent.

        Args:
            init: Iterable of Agent objects representing initial agents
            target: List of rule name strings to find paths to

        Returns:
            A new CausalGraph containing only the rules and edges on paths from init to target
        '''
        init_agents = list(init)

        # Step 1: Find starting rules - rules that have at least one LHS agent
        # that embeds into any init agent
        starting_rules = set()
        for rule_name, rule in self.system.rules.items():
            for lhs_agent in rule.left.agents:
                if lhs_agent is None:
                    continue
                # Check if this LHS agent embeds into any init agent
                if self._agent_embeds_into_agents(lhs_agent, init_agents):
                    starting_rules.add(rule_name)
                    break

        # Step 2: Forward reachable - graph traversal from starting rules
        # Edge A -> B means A depends on B, so in execution order B enables A
        # Therefore, to go forward in execution, we follow edges backward in the graph
        forward_reachable = set(starting_rules)
        changed = True
        while changed:
            changed = False
            for rule_a, successors in self.edges.items():
                # If any of rule_a's dependencies are forward-reachable,
                # then rule_a is forward-reachable (we can execute dependencies first)
                for rule_b in successors:
                    if rule_b in forward_reachable and rule_a not in forward_reachable:
                        forward_reachable.add(rule_a)
                        changed = True
                        break

        # Step 3: Backward reachable - graph traversal from target rules
        # Follow edges forward (in dependency direction)
        backward_reachable = set(target)
        changed = True
        while changed:
            changed = False
            for rule_name in list(backward_reachable):
                # If rule_name is backward-reachable, all its dependencies are too
                for dependency in self.edges.get(rule_name, []):
                    if dependency not in backward_reachable:
                        backward_reachable.add(dependency)
                        changed = True

        # Step 4: Intersection - rules on paths from init to targets
        path_rules = forward_reachable & backward_reachable

        # Step 5: Create a new CausalGraph with only these rules
        new_graph = CausalGraph.__new__(CausalGraph)
        new_graph.system = self.system
        new_graph.edges = defaultdict(set)
        new_graph.edge_labels = defaultdict(set)

        # Copy only edges where both endpoints are in path_rules
        for source in path_rules:
            for dest in self.edges[source]:
                if dest in path_rules:
                    new_graph.edges[source].add(dest)
                    if (source, dest) in self.edge_labels:
                        new_graph.edge_labels[(source, dest)] = self.edge_labels[(source, dest)]

        return new_graph

    def causal_tree(self, init: Iterable[Agent], target_rule: str):
        pass

def unique_agents(mixture):
    unique_agents = []
    seen_agent_strings = set()

    for agent in mixture.agents:
        agent_string = agent.kappa_str

        if agent_string not in seen_agent_strings:
            seen_agent_strings.add(agent_string)
            unique_agents.append(agent)

def generate_causal_graph(system):
    causal_graph = defaultdict(set)

    for name_a, rule_a in system.rules.items():
        for name_b, rule_b in system.rules.items():
            for agent_a in rule_a.left.agents:
                if agent_a is None:
                    continue
                if Component([agent_a]).embeddings(rule_b.right):
                    causal_graph[name_a].add(name_b)

    return causal_graph

def unreachable(init: Iterable[Agent], causal_graph, system):
    system.unique_agents

def main():
    model_path = Path(__file__).with_name("wnt_v8.ka")
    # model_path = Path(__file__).with_name("simple.ka")

    print("Model path loaded")
    system = System.read_ka(model_path)

    # Build source map
    source_map = SourceMap(model_path)
    source_map.map_rules(system)

    # List the agents present in the initial mixture.
    #
    # system.mixture.kappa_str preserves the %init-style representation,
    # including copy counts and complexes.
    print("=== Initial mixture ===")
    print(system.mixture.kappa_str or "(no initialized agents)")

    # Keep one copy of each exactly identical agent representation.
    unique_agents = []
    seen_agent_strings = set()

    for agent in system.mixture.agents:
        agent_string = agent.kappa_str

        if agent_string not in seen_agent_strings:
            seen_agent_strings.add(agent_string)
            unique_agents.append(agent)

    for index, agent in enumerate(unique_agents, start=1):
        source_line = source_map.get_agent_source(agent)
        source_info = f" (line {source_line})" if source_line else ""
        print(f"{index}: {agent.kappa_str}{source_info}")

    print("\n=== Rules ===")
    for rule_name, rule in system.rules.items():
        source_line = source_map.get_rule_source(rule_name)
        source_info = f" (line {source_line})" if source_line else ""
        print(f"{rule_name}: {rule.kappa_str}{source_info}")

    causal_graph = CausalGraph(system)
    init_agents = unique_agents

    unreachable_rules = causal_graph.unreachable(init_agents)

    print("\n=== Unreachable Rules ===")
    if unreachable_rules:
        for rule_name in unreachable_rules:
            source_line = source_map.get_rule_source(rule_name)
            source_info = f" (line {source_line})" if source_line else ""
            print(f"{rule_name}{source_info}")
    
if __name__ == "__main__":
    main()
