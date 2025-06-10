import random
from utils.ANSIColors import ANSIColors

class Relationships:
    RELATIONSHIPS = {}

    def __str__(self):
        result = []
        for key, data in Relationships.RELATIONSHIPS.items():
            agent1 = data['agent1']
            agent2 = data['agent2']
            status = self.get_status_relationship(agent1, agent2)
            result.append(f"Relationship between {agent1.name} and {agent2.name}: {status}")
        return "\n".join(result)

    @staticmethod
    def add_relationship(agent1, agent2, initial_value: float = 0.0):
        """
        Adds a relationship between two agents with an initial value.
        :param agent1: Agent object representing the first agent.
        :param agent2: Agent object representing the second agent.
        :param initial_value: Initial value of the relationship, should be between -1.0 and 1.0.
        """
        if agent1.dead or agent2.dead:
            return

        initial_value = max(-1.0, min(1.0, initial_value))
        
        key = tuple(sorted([agent1.id, agent2.id]))
        
        Relationships.RELATIONSHIPS[key] = {
            'value': initial_value,
            'agent1': agent1,
            'agent2': agent2,
        }

    @staticmethod
    def get_relationship(agent1, agent2) -> float:
        """
        Get the relationship value between two agents.
        :param agent1: Agent object representing the first agent.
        :param agent2: Agent object representing the second agent.
        :return: Relationship value between -1.0 and 1.0, or 0.0 if no relationship exists.
        """
        key = tuple(sorted([agent1.id, agent2.id]))
        rel = Relationships.RELATIONSHIPS.get(key, None)
        return rel['value'] if rel else 0.0

    @staticmethod
    def get_relationship_data(agent1, agent2) -> dict:
        """
        Get the relationship data between two agents.
        :param agent1: Agent object representing the first agent.
        :param agent2: Agent object representing the second agent.
        :return: Dictionary containing relationship data or None if no relationship exists.
        """
        key = tuple(sorted([agent1.id, agent2.id]))
        return Relationships.RELATIONSHIPS.get(key, None)

    @staticmethod
    def get_status_relationship(agent1, agent2) -> str:
        """
        Get the status of the relationship between two agents.
        :param agent1: Agent object representing the first agent.
        :param agent2: Agent object representing the second agent.
        :return: String representing the status of the relationship.
        """
        key = tuple(sorted([agent1.id, agent2.id]))
        rel = Relationships.RELATIONSHIPS.get(key, None)
        if rel is None:
            return "inexistent"

        score = rel['value']
        if score < -0.8:
            return "hating each other"
        elif score < -0.5:
            return "disliked"
        elif score < 0.3:
            return "neutral"
        elif score < 0.5:
            return "friends"
        elif score < 0.8:
            return "close friends"
        elif score <= 1:
            return "lovers"
        else:
            return "family"

    @staticmethod
    def update_relationship(agent1, agent2, increment: float):
        """
        Update the relationship value between two agents by a given increment.
        :param agent1: Agent object representing the first agent.
        :param agent2: Agent object representing the second agent.
        :param increment: Increment value to adjust the relationship, should be between -1.0 and 1.0.
        """
        if agent1.dead or agent2.dead:
            return None

        key = tuple(sorted([agent1.id, agent2.id]))
        if key in Relationships.RELATIONSHIPS:
            current = Relationships.RELATIONSHIPS[key]['value']
            new_value = max(-1.0, min(1.0, current + increment))
            Relationships.RELATIONSHIPS[key]['value'] = new_value
            return new_value
        return None

    @staticmethod
    def get_all_relationships(agent) -> dict:
        """
        Get all relationships for a given agent.
        :param agent: Agent object for which to retrieve relationships.
        :return: Dictionary containing relationships with other agents.
        """
        agent_relationships = {}
        for key, data in Relationships.RELATIONSHIPS.items():
            if agent.id in key:
                other_agent = data['agent2'] if data['agent1'].id == agent.id else data['agent1']
                agent_relationships[other_agent.id] = {
                    'value': data['value'],
                    'agent': other_agent.name,
                    'status': Relationships.get_status_relationship(agent, other_agent)
                }
        return agent_relationships

    @staticmethod
    def get_relationship_count() -> int:
        """
        Get the total number of relationships.
        :return: The total number of relationships.
        """
        return len(Relationships.RELATIONSHIPS)

    @staticmethod
    def initialize_relationships(simulation):
        """
        Initialize relationships between agents in the simulation.
        :param simulation: The current simulation object containing agents.
        """
        print(f"[INFO] Initializing relationships between {len(simulation.agents)} agents...")

        for i, agent1 in enumerate(simulation.agents):
            for agent2 in simulation.agents[i+1:]:
                compatibility = random.uniform(-0.3, 0.5)
                Relationships.add_relationship(agent1, agent2, compatibility)

        print(f"[INFO] Initialized {Relationships.get_relationship_count()} relationships")

    @staticmethod
    def generate_social_events(simulation):
        """
        Generate social events between agents in the simulation.
        :param simulation: The current simulation object containing agents.
        """
        events = [
            {"name": "helped_in_need", "effect": (0.05, 0.15), "probability": 0.15},
            {"name": "shared_resources", "effect": (0.03, 0.08), "probability": 0.2},
            {"name": "had_argument", "effect": (-0.1, -0.02), "probability": 0.2},
            {"name": "worked_together", "effect": (0.02, 0.07), "probability": 0.15},
            {"name": "betrayed_trust", "effect": (-0.5, -0.1), "probability": 0.10},
            {"name": "gave_gift", "effect": (0.1, 0.2), "probability": 0.15}
        ]

        for i, agent1 in enumerate(simulation.agents):
            if agent1.dead:
                continue

            for agent2 in simulation.agents[i+1:]:
                if agent2.dead:
                    continue

                for event in events:
                    if random.random() < event["probability"]:
                        effect_range = event["effect"]
                        effect = random.uniform(effect_range[0], effect_range[1])
                        value = Relationships.get_relationship(agent1, agent2)
                        new_value = Relationships.update_relationship(agent1, agent2, effect)
                        if abs(effect) > 0.1:
                            print(f"{ANSIColors.OKCYAN}[RELATIONSHIP] {agent1.name} and {agent2.name} {event['name']}: {value:.2f} → {new_value:.2f} ({effect:.2f}){ANSIColors.ENDC}")
                        break

    @staticmethod
    def update_social_attributes(simulation):
        """
        Update social attributes of agents based on their relationships.
        :param simulation: The current simulation object containing agents.
        """
        for agent in simulation.agents:
            if agent.dead:
                continue

            relationships = Relationships.get_all_relationships(agent)
            positive_connections = sum(1 for _, data in relationships.items() if data["value"] > 0.3)
            close_connections = sum(1 for _, data in relationships.items() if data["value"] > 0.7)

            social_boost = (positive_connections * 0.03) + (close_connections * 0.07)
            agent.attributes_mod["social"] += min(social_boost, 0.2)

            if positive_connections > 0:
                agent.happiness += min(social_boost * 0.5, 0.15)
