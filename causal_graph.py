from pathlib import Path
from pykappa.system import System
from pykappa.pattern import Component, Agent
from collections import defaultdict
from typing import Iterable

class CausalGraph:
    '''
    A labelled directed graph representing the potential causal
    prerequisites of a rule firing, in . 

    An edge from Rule A to Rule B . 
    '''
    edges: dict[str, set] # Rule names
    edge_labels: dict[(str, str), set]

    def __init__(self, system):
        self.edges = defaultdict(set)
        self.edge_labels = defaultdict(set)

        for name_a, rule_a in system.rules.items():
            for name_b, rule_b in system.rules.items():
                for agent_a in rule_a.left.agents:
                    if agent_a is None:
                        continue
                    if Component([agent_a]).embeddings(rule_b.right):
                        self.edges[name_a].add(name_b)
                        self.edge_labels[(name_a, name_b)].add(agent_a)

    def unreachable(self, init: Iterable[Agent]) -> list[str]:
        '''
        Returns a list of rule names that can't be reached from the agents in `init`
        '''
        # TODO: unreachability analysis
        pass 

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

    print("Model path loaded")
    system = System.read_ka(model_path)

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
        print(f"{index}: {agent.kappa_str}")

    print("\n=== Rules ===")
    for rule_name, rule in system.rules.items():
        print(f"{rule_name}: {rule.kappa_str}")

    causal_graph = CausalGraph(system)
    init_agents = unique_agents

    unreachable = causal_graph.unreachable(init_agents)
    
if __name__ == "__main__":
    main()
