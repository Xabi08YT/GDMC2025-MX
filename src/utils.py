import math
import Agent

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return math.sqrt((ax-bx)**2 + (az-bz)**2)

def min_distance_to_others(agent, others):
    return min([distance_xz(agent.x, agent.z, otherx, otherz) for otherx, otherz in others])

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]

def is_flat(x: int, z: int, radius: int = 2) -> float:
    heights = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            new_y = 0 # get ground height
            heights.append(new_y)
    variation = max(heights) - min(heights)
    return 1 - min(variation / 5, 1)

def evaluate_spot(agent: Agent, x: int, z: int) -> float:
    score = 0
    other_positions = [(other.x, other.z) for other in agent.all_agents if other.id != agent.id]

    min_dist = min_distance_to_others(agent, other_positions)
    score += min_dist * (1 / agent.needs_decay["social"])

    dist_from_center = distance_xz(x, z, agent.center_village[0], agent.center_village[1])
    score += dist_from_center * agent.attributes["adventurous"]

    flatness = 1 - is_flat(x, z)
    score += flatness
    return score