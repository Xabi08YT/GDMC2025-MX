from src.simLogic.Agent import Agent

class Relationships:
    def __init__(self):
        self.relationships = {}

    def __str__(self):
        result = []
        for key, data in self.relationships.items():
            agent1 = data['agent1']
            agent2 = data['agent2']
            status = self.get_status_relationship(agent1, agent2)
            result.append(f"Relationship between {agent1.name} and {agent2.name}: {status}")
        return "\n".join(result)
        
    def add_relationship(self, agent1: Agent, agent2: Agent, initial_value: float = 0.0):
        initial_value = max(-1.0, min(1.0, initial_value))
        
        key = tuple(sorted([agent1.id, agent2.id]))
        
        self.relationships[key] = {
            'value': initial_value,
            'agent1': agent1,
            'agent2': agent2,
        }
        
    def get_relationship(self, agent1: Agent, agent2: Agent) -> float:
        key = tuple(sorted([agent1.id, agent2.id]))
        return self.relationships.get(key, {})

    def get_status_relationship(self, agent1: Agent, agent2: Agent) -> str:
        key = tuple(sorted([agent1.id, agent2.id]))
        score = self.relationships.get(key, None)
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
    
    def update_relationship(self, agent1: Agent, agent2: Agent, increment: float):
        key = tuple(sorted([agent1.id, agent2.id]))
        if key in self.relationships:
            current = self.relationships[key]['value']
            new_value = max(-1.0, min(1.0, current + increment))
            self.relationships[key]['value'] = new_value
            
    def get_all_relationships(self, agent: Agent) -> dict:
        agent_relationships = {}
        for key, data in self.relationships.items():
            if agent.id in key:
                other_agent = data['agent2'] if data['agent1'].id == agent.id else data['agent1']
                agent_relationships[other_agent.id] = {
                    'value': data['value'],
                }
        return agent_relationships
    
    def remove_relationship(self, agent1: Agent, agent2: Agent):
        key = tuple(sorted([agent1.id, agent2.id]))
        if key in self.relationships:
            del self.relationships[key]
            
    def get_relationship_count(self) -> int:
        return len(self.relationships)