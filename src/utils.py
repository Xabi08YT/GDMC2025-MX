from math_methods import distance_xz

def min_distance_to_others(agent, others):
    return min([distance_xz(agent.x, agent.z, otherx, otherz) for otherx, otherz in others])

def is_flat(x: int, z: int, abl, radius: int = 2) -> float:
    heights = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            nx, nz = x + dx, z + dz
            chunk = abl.get_chunk(nx, nz)
            new_y = chunk.getGroundHeight(nx, nz)
            heights.append(new_y)
    variation = max(heights) - min(heights)
    return 1 - min(variation / 5, 1)


def evaluate_spot(agent, x: int, z: int) -> float:
    from Agent import Agent as AgentClass
    from Building import Building

    if Building.detect_all_tresspassing(x, z):
        return float('-inf')

    score = 0
    other_positions = [(other.x, other.z) for other in agent.all_agents if other.id != agent.id]

    min_dist = min_distance_to_others(agent, other_positions)
    social_factor = 1
    if agent.needs_decay["social"] != 0:
        social_factor = 1 / (agent.needs_decay["social"])
    score += min_dist * social_factor

    dist_from_center = distance_xz(x, z, agent.center_village[0], agent.center_village[1])
    score += dist_from_center * agent.attributes["adventurous"]

    flatness = 1 - is_flat(x, z, agent.abl)
    score += flatness
    return score