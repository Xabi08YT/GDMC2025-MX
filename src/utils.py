import json

import Agent
import chunk
import random
import gdpc
from gdpc import Block

from chunk import get_chunk_from_block_coordinates

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
    while currentY > 0 and not found:
        try:
            if blocks[str((x,currentY,z))].id in params["ground"]:
                found = True
                break
        except:
            pass
        currentY -= 1

    return currentY

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


def create_path(start, end):
    path_block = Block("minecraft:dirt_path")
    start_x, start_y, start_z = start
    end_x, end_y, end_z = end

    dx = abs(end_x - start_x)
    dz = abs(end_z - start_z)
    sx = 1 if start_x < end_x else -1
    sz = 1 if start_z < end_z else -1
    err = dx - dz
    x, z = start_x, start_z

    while (x != end_x or z != end_z):
        y = get_ground_height(x, 200, z) + 1

        current_editor.placeBlock((x, y-1, z), path_block)

        e2 = 2 * err
        if e2 > -dz:
            err -= dz
            x += sx
        if e2 < dx:
            err += dx
            z += sz


def connect_houses_to_center():
    village_center = (
        agents[0].center_village[0],
        get_ground_height(agents[0].center_village[0], 200, agents[0].center_village[1]) + 1,
        agents[0].center_village[1]
    )

    for agent in agents:
        if agent.attributes["house"].built:
            door_pos = agent.attributes["house"].get_door_position()
            if door_pos:
                orientation = agent.attributes["house"].orientation
                door_x, door_y, door_z = door_pos

                if orientation == "north":
                    door_z -= 1
                elif orientation == "south":
                    door_z += 1
                elif orientation == "east":
                    door_x += 1
                elif orientation == "west":
                    door_x -= 1

                path_start = (door_x, door_y, door_z)
                create_path(path_start, village_center)

if __name__ == "__main__":
    block = get_ground_height(31, 66, 142)
    print(block)