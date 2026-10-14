from pathlib import Path
from pykappa.system import System

def unique_agents(mixture):
    unique_agents = []
    seen_agent_strings = set()

    for agent in mixture.agents:
        agent_string = agent.kappa_str

        if agent_string not in seen_agent_strings:
            seen_agent_strings.add(agent_string)
            unique_agents.append(agent)

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


if __name__ == "__main__":
    main()
