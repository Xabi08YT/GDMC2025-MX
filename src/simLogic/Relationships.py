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
        initial_value = max(-1.0, min(1.0, initial_value))
        
        key = tuple(sorted([agent1.id, agent2.id]))
        
        Relationships.RELATIONSHIPS[key] = {
            'value': initial_value,
            'agent1': agent1,
            'agent2': agent2,
        }

    @staticmethod
    def get_relationship(agent1, agent2) -> float:
        key = tuple(sorted([agent1.id, agent2.id]))
        return Relationships.RELATIONSHIPS.get(key, {})

    @staticmethod
    def get_status_relationship(agent1, agent2) -> str:
        key = tuple(sorted([agent1.id, agent2.id]))
        score = Relationships.RELATIONSHIPS.get(key, None)
        if score is None:
            return "inexistent"
        elif score < -0.5:
            return "hating each other's"
        elif score < -0.8:
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
        key = tuple(sorted([agent1.id, agent2.id]))
        if key in Relationships.RELATIONSHIPS:
            current = Relationships.RELATIONSHIPS[key]['value']
            new_value = max(-1.0, min(1.0, current + increment))
            Relationships.RELATIONSHIPS[key]['value'] = new_value

    @staticmethod
    def get_all_relationships(agent) -> dict:
        agent_relationships = {}
        for key, data in Relationships.RELATIONSHIPS.items():
            if agent.id in key:
                other_agent = data['agent2'] if data['agent1'].id == agent.id else data['agent1']
                agent_relationships[other_agent.id] = {
                    'value': data['value'],
                }
        return agent_relationships

    @staticmethod
    def remove_relationship(agent1, agent2):
        key = tuple(sorted([agent1.id, agent2.id]))
        if key in Relationships.RELATIONSHIPS:
            del Relationships.RELATIONSHIPS[key]

    @staticmethod
    def get_relationship_count() -> int:
        return len(Relationships.RELATIONSHIPS)