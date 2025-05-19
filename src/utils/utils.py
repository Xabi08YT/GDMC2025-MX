from src.utils.math_methods import distance_xz

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
    from src.buildings.Building import Building
    if Building.detect_all_trespassing(x, z):
        return float('-inf')

    score = 0
    other_positions = [(other.x, other.z) for other in agent.simulation.agents if other.id != agent.id]

    min_dist = min_distance_to_others(agent, other_positions)
    social_factor = 1
    if agent.decay_rates["social"] != 0:
        social_factor = 1 / (agent.decay_rates["social"])
    score += min_dist * social_factor

    dist_from_center = distance_xz(x, z, agent.simulation.firecamp_coords[0], agent.simulation.firecamp_coords[1])
    score += dist_from_center * agent.attributes["adventurous"]

    flatness = 1 - is_flat(x, z, agent.simulation.abl)
    score += flatness
    return score