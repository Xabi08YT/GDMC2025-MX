from utils.math_methods import distance_xz

class BoidsBehavior:
    def __init__(self, 
                 separation_weight: float = 1.5,
                 cohesion_weight: float = 1.0,
                 separation_radius: float = 250,
                 cohesion_radius: float = 250):
        """
        Initialize the BoidsBehavior with weights and radii for separation and cohesion.
        :param separation_weight: Weight for the separation force.
        :param cohesion_weight: Weight for the cohesion force.
        :param separation_radius: Radius within which separation force is applied.
        :param cohesion_radius: Radius within which cohesion force is applied.
        """
        self.separation_weight = separation_weight
        self.cohesion_weight = cohesion_weight
        self.separation_radius = separation_radius
        self.cohesion_radius = cohesion_radius

    @staticmethod
    def get_neighbors(agent, agents, radius: float):
        """
        Get neighbors of an agent within a specified radius.
        :param agent: Agent for which neighbors are being found.
        :param agents: List of all agents.
        :param radius: Radius to consider for neighbors.
        :return: List of neighboring agents within the specified radius.
        """
        return [other for other in agents 
                if other != agent and distance_xz(agent.x, agent.z, other.x, other.z) < radius]

    @staticmethod
    def separation(agent, neighbors) -> tuple[float, float]:
        """
        Calculate the separation force for an agent based on its neighbors.
        :param agent: Agent for which separation force is calculated.
        :param neighbors: List of neighboring agents.
        :return: Forces in the x and z directions to apply for separation.
        """
        if not neighbors:
            return .0, .0
            
        force_x = force_z = 0
        for neighbor in neighbors:
            dx = agent.x - neighbor.x
            dz = agent.z - neighbor.z
            
            distance = distance_xz(agent.x, agent.z, neighbor.x, neighbor.z)
            if distance > 0:
                force_x += dx / distance
                force_z += dz / distance
                
        return force_x, force_z

    @staticmethod
    def cohesion(agent, neighbors) -> tuple[float, float]:
        """
        Calculate the cohesion force for an agent based on its neighbors.
        :param agent: Agent for which cohesion force is calculated.
        :param neighbors: List of neighboring agents.
        :return: Centering forces in the x and z directions to apply for cohesion.
        """
        if not neighbors:
            return .0, .0
            
        center_x = center_y = center_z = 0
        for neighbor in neighbors:
            center_x += neighbor.x
            center_z += neighbor.z
            
        n = len(neighbors)
        center_x /= n
        center_z /= n
        
        return (center_x - agent.x,
                center_z - agent.z)
    
    def apply_boids_behavior(self, agent, agents):
        """
        Apply boids behavior to an agent based on its neighbors.
        :param agent: Agent to which boids behavior is applied.
        :param agents: List of all agents.
        :return: Separation and cohesion forces to apply to the agent.
        """
        separation_neighbors = self.get_neighbors(agent, agents, self.separation_radius)
        cohesion_neighbors = self.get_neighbors(agent, agents, self.cohesion_radius)
        
        separation_force = self.separation(agent, separation_neighbors)
        cohesion_force = self.cohesion(agent, cohesion_neighbors)
        
        return (
            separation_force[0] * self.separation_weight +
            cohesion_force[0] * self.cohesion_weight,
            
            separation_force[1] * self.separation_weight +
            cohesion_force[1] * self.cohesion_weight
        )
