import math
from typing import List

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
        
    def get_neighbors(self, agent, agents, radius: float):
        return [other for other in agents 
                if other != agent and agent.distance_to(other) < radius]
    
    def separation(self, agent, neighbors) -> tuple[float, float, float]:
        if not neighbors:
            return (.0, .0, .0)
            
        force_x = force_y = force_z = 0
        for neighbor in neighbors:
            dx = agent.x - neighbor.x
            dy = agent.y - neighbor.y
            dz = agent.z - neighbor.z
            
            distance = agent.distance_to(neighbor)
            if distance > 0:
                force_x += dx / distance
                force_y += dy / distance
                force_z += dz / distance
                
        return (force_x, force_y, force_z)
    
    def alignment(self, agent, neighbors) -> tuple[float, float, float]:
        if not neighbors:
            return (.0, .0, .0)
            
        avg_vx = avg_vy = avg_vz = 0
        for neighbor in neighbors:
            avg_vx += neighbor.velocity_x
            avg_vy += neighbor.velocity_y
            avg_vz += neighbor.velocity_z
            
        n = len(neighbors)
        avg_vx /= n
        avg_vy /= n
        avg_vz /= n
        
        return (avg_vx - agent.velocity_x,
                avg_vy - agent.velocity_y,
                avg_vz - agent.velocity_z)
    
    def cohesion(self, agent, neighbors) -> tuple[float, float, float]:
        if not neighbors:
            return (.0, .0, .0)
            
        center_x = center_y = center_z = 0
        for neighbor in neighbors:
            center_x += neighbor.x
            center_y += neighbor.y
            center_z += neighbor.z
            
        n = len(neighbors)
        center_x /= n
        center_y /= n
        center_z /= n
        
        return (center_x - agent.x,
                center_y - agent.y,
                center_z - agent.z)
    
    def apply_boids_behavior(self, agent, agents):
        separation_neighbors = self.get_neighbors(agent, agents, self.separation_radius)
        alignment_neighbors = self.get_neighbors(agent, agents, self.alignment_radius)
        cohesion_neighbors = self.get_neighbors(agent, agents, self.cohesion_radius)
        
        separation_force = self.separation(agent, separation_neighbors)
        alignment_force = self.alignment(agent, alignment_neighbors)
        cohesion_force = self.cohesion(agent, cohesion_neighbors)
        
        agent.apply_force(
            separation_force[0] * self.separation_weight +
            alignment_force[0] * self.alignment_weight +
            cohesion_force[0] * self.cohesion_weight,
            
            separation_force[1] * self.separation_weight +
            alignment_force[1] * self.alignment_weight +
            cohesion_force[1] * self.cohesion_weight,
            
            separation_force[2] * self.separation_weight +
            alignment_force[2] * self.alignment_weight +
            cohesion_force[2] * self.cohesion_weight
        )
