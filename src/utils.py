import os
import json
import random
import time
from json import JSONDecodeError

from multiprocessing import Pool, cpu_count
from gdpc import interface, Editor, Block
from time import sleep, time

current_editor = None

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def get_ground_height(x: int, y_start: int, z: int) -> int:
    for y in range(y_start, 0, -1):
        block = [] # block = getBlock from JSON using x, y and z
        if block[0] != "minecraft:air" and not block[0].endswith("leaves"):
            return y
    return 100

def is_flat(x: int, y: int, z: int, radius: int = 2) -> float:
    heights = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            ny = get_ground_height(x + dx, y + 10, z + dz)
            heights.append(ny)
    variation = max(heights) - min(heights)
    return 1 - min(variation / 5, 1)

def see_around(x: int, z: int, radius: int = 6):
    blocks = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            new_x, new_z = x + dx, z + dz
            block = [] # block = getBlock from JSON using new_x and new_z
            if block[0] != "minecraft:air" and not block[0].endswith("leaves"):
                blocks.append((block, (new_x, new_z)))
    return blocks

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]