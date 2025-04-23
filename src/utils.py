import json

import Agent
import chunk
import gdpc

from src.chunk import get_chunk_from_block_coordinates

current_editor = gdpc.Editor(buffering=True)
agents = []

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def get_ground_height(x: int, y_start: int, z: int) -> int:
    blocks = get_chunk_from_block_coordinates(x,z,current_editor.getBuildArea())
    currentY = y_start
    found = False
    with open("simParams.json", "r") as file:
        params = json.load(file)
    while currentY > -64 and not found:
        if blocks[str((x,currentY,z))].id in params["ground"]:
            found = True
        currentY -= 1
    return currentY - 1

def is_flat(x: int, z: int, radius: int = 2) -> float:
    heights = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            ny = get_ground_height(x + dx, 300, z + dz)
            heights.append(ny)
    variation = max(heights) - min(heights)
    return 1 - min(variation / 5, 1)

def evaluate_spot(agent: Agent, x: int, z: int) -> float:
    score = 0
    other_positions = [(other.x, other.z) for other in agents if other.id != agent.id]

    min_dist = agent.min_distance_to_others(other_positions)
    if agent.needs["farfromothers"] > 0:
        score += min_dist * agent.needs["farfromothers"]
    else:
        score += (1 / max(1, min_dist)) * abs(agent.needs["farfromothers"])

    dist_from_center = distance_xz(x, z, agent.center_village[0], agent.center_village[1])
    if agent.needs["farfromcenter"] > 0:
        score += dist_from_center * agent.needs["farfromcenter"]
    else:
        score += (1 / max(1, int(dist_from_center))) * abs(agent.needs["farfromcenter"])

    flatness = 1 - is_flat(x, z)
    score += flatness * agent.needs["flatspace"]
    return score

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]

if __name__ == "__main__":
    block = get_ground_height(31, 66, 142)
    print(block)