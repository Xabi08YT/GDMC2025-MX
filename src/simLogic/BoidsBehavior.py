from src.utils.math_methods import distance_xz


class BoidsBehavior:
    def __init__(self, 
                 separation_weight: float = 1.5,
                 alignment_weight: float = 1.0,
                 cohesion_weight: float = 1.0,
                 separation_radius: float = 2.0,
                 alignment_radius: float = 5.0,
                 cohesion_radius: float = 5.0):
        self.separation_weight = separation_weight
        self.alignment_weight = alignment_weight
        self.cohesion_weight = cohesion_weight
        self.separation_radius = separation_radius
        self.alignment_radius = alignment_radius
        self.cohesion_radius = cohesion_radius

    @staticmethod
    def get_neighbors(agent, agents, radius: float):
        return [other for other in agents 
                if other != agent and distance_xz(agent.x, agent.z, other.x, other.z) < radius]

    @staticmethod
    def separation(agent, neighbors) -> tuple[float, float]:
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
    def alignment(agent, neighbors) -> tuple[float, float]:
        if not neighbors:
            return .0, .0
            
        avg_vx = avg_vz = 0
        for neighbor in neighbors:
            avg_vx += neighbor.velocity_x
            avg_vz += neighbor.velocity_z
            
        n = len(neighbors)
        avg_vx /= n
        avg_vz /= n
        
        return (avg_vx - agent.velocity_x,
                avg_vz - agent.velocity_z)

    @staticmethod
    def cohesion(agent, neighbors) -> tuple[float, float]:
        if not neighbors:
            return .0, .0
            
        center_x = center_y = center_z = 0
        for neighbor in neighbors:
            center_x += neighbor.x
            center_y += neighbor.y
            center_z += neighbor.z
            
        n = len(neighbors)
        center_x /= n
        center_z /= n
        
        return (center_x - agent.x,
                center_z - agent.z)
    
    def apply_boids_behavior(self, agent, agents):
        separation_neighbors = self.get_neighbors(agent, agents, self.separation_radius)
        alignment_neighbors = self.get_neighbors(agent, agents, self.alignment_radius)
        cohesion_neighbors = self.get_neighbors(agent, agents, self.cohesion_radius)
        
        separation_force = self.separation(agent, separation_neighbors)
        alignment_force = self.alignment(agent, alignment_neighbors)
        cohesion_force = self.cohesion(agent, cohesion_neighbors)
        
        return (
            separation_force[0] * self.separation_weight +
            alignment_force[0] * self.alignment_weight +
            cohesion_force[0] * self.cohesion_weight,
            
            separation_force[1] * self.separation_weight +
            alignment_force[1] * self.alignment_weight +
            cohesion_force[1] * self.cohesion_weight
        )
