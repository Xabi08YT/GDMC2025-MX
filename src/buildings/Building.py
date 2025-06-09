from random import choice
import numpy as np
import os
from utils.math_methods import distance_xz
import json


class Building:

    BUILDINGS = []

    def __init__(self, center_point: tuple[int, int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated", width = 5, height = 5, depth = 5, bupdates = True):
        self.built = built
        self.orientation = orientation
        self.width = width
        self.height = height
        self.depth = depth
        self.radius = 10
        self.center_point = center_point
        if agent is not None and center_point is not None:
            placement_success = self.place(center_point, agent.simulation)
            if placement_success and hasattr(self, "center_point") and self.center_point is not None:
                self.lowest_y = agent.simulation.heightmap[self.center_point[0] - width:self.center_point[0] + width,
                                self.center_point[1] - depth:self.center_point[1] + depth].min().item() - 1
                self.highest_y = agent.simulation.heightmap[self.center_point[0] - width:self.center_point[0] + width,
                                self.center_point[1] - depth:self.center_point[1] + depth].max().item() - 1
        self.name = name
        self.folder = folder
        self.matrix = np.zeros((self.width, self.depth, self.height), dtype=object)
        self.BUILDINGS.append(self)
        self.bupdates = bupdates
        self.corner = "minecraft:oak_log"
        self.agent = agent

    def built(self):
        self.built = True

    def set_orientation_according_to_center(self, agent=None):
        if agent is None:
            agent = self.agent

        if self.center_point is None:
            return
        village_center = agent.simulation.firecamp_coords
        orientations = {"north": [0, -1], "south": [0, 1], "east": [1, 0], "west": [-1, 0]}
        score = {k: distance_xz(village_center[0], village_center[1], self.center_point[0] + self.radius * e[0],
                                self.center_point[1] + self.radius * e[1]) for k, e in orientations.items()}

        max_distance = max(score.values())

        orientations_to_remove = [k for k, s in score.items() if s == max_distance]
        for orientation in orientations_to_remove:
            orientations.pop(orientation)

        if orientations:
            self.orientation = choice(list(orientations.keys()))
        else:
            self.orientation = choice(["north", "south", "east", "west"])

    def get_entrance_coordinates(self):
        if self.center_point is None:
            return None

        x, z = self.center_point[0], self.center_point[1]

        entrance_offset = {"north": (0, -self.radius), "south": (0, self.radius),
                           "east": (self.radius, 0), "west": (-self.radius, 0)}

        if self.orientation not in entrance_offset:
            self.orientation = "south"

        offset = entrance_offset[self.orientation]
        lateral_offset = 0
        if self.orientation in ["north", "south"]:
            lateral_offset = (self.width // 4) - 1
            if lateral_offset < 1:
                lateral_offset = 1
            entrance_x = x + offset[0] + lateral_offset
        else:
            lateral_offset = (self.depth // 4) - 1
            if lateral_offset < 1:
                lateral_offset = 1
            entrance_z = z + offset[1] + lateral_offset

        if self.orientation in ["north", "south"]:
            entrance_z = z + offset[1]
        else:
            entrance_x = x + offset[0]

        return entrance_x, entrance_z

    def check_collision(self, center_point: tuple[int, int]) -> bool:
        # Calcule les bornes du bâtiment à placer
        x_min = center_point[0] - self.width // 2
        x_max = center_point[0] + self.width // 2
        z_min = center_point[1] - self.depth // 2
        z_max = center_point[1] + self.depth // 2
        for b in Building.BUILDINGS:
            if b.center_point is None or b is self:
                continue
            bx_min = b.center_point[0] - b.width // 2
            bx_max = b.center_point[0] + b.width // 2
            bz_min = b.center_point[1] - b.depth // 2
            bz_max = b.center_point[1] + b.depth // 2
            # Test de chevauchement
            if not (x_max < bx_min or x_min > bx_max or z_max < bz_min or z_min > bz_max):
                return True
        return False

    def place(self, center_point: tuple[int, int], sim=None):
        # Vérifie le chevauchement avec les autres bâtiments
        if self.check_collision(center_point):
            return False
        center_point = (max(center_point[0], self.width), max(center_point[1], self.depth))
        center_point = (min(center_point[0], sim.heightmap.shape[0] - self.width),
                        min(center_point[1], sim.heightmap.shape[1] - self.depth))
        x_min = center_point[0] - self.width // 2 - 1
        x_max = center_point[0] + self.width // 2 + 1
        z_min = center_point[1] - self.depth // 2 - 1
        z_max = center_point[1] + self.depth // 2 + 1
        if np.any(sim.buildings[x_min:x_max, z_min:z_max]):
            return False
        self.center_point = center_point
        sim.buildings[x_min:x_max, z_min:z_max] = True
        return True

    def clear(self):
        for x in range(self.width):
            for y in range(1, self.height):
                for z in range(self.depth):
                    self.add_block_to_matrix(x, y, z, "minecraft:air")

    def __str__(self):
        return f"{self.name}"

    def add_block_to_matrix(self, x: int, y: int, z: int, block: str):
        self.matrix[x][z][y] = block

    def matrix_to_files(self):
        if not hasattr(self, "center_point") or self.center_point is None:
            return
        if type(self.center_point[0]) is not int:
            self.center_point = self.center_point[0].item(),self.center_point[1]
        if type(self.center_point[1]) is not int:
            self.center_point = self.center_point[0],self.center_point[1].item()
        data = {
            "name": self.name,
            "x": self.center_point[0],
            "z": self.center_point[1],
            "built": self.built,
            "orientation": self.orientation,
            "bupdates": self.bupdates,
            "biome": self.agent.simulation.biomes[self.center_point[0], self.center_point[1]] if hasattr(self.agent, "simulation")  else "minecraft:plains",
            "happiness": self.agent.happiness if hasattr(self, "agent") and self.agent is not None and not getattr(self.agent, "dead", False) else 0,
            "container": self.container if hasattr(self, "container") else None,
            "job_type": self.agent.job.job_type.name if hasattr(self.agent, "job") else None,
            "book": self.agent.book if hasattr(self.agent, "book") else None,
        }
        folder_path = os.path.join(self.folder, self.name)
        os.makedirs(folder_path, exist_ok=True)
        json_file = os.path.join(folder_path, "metadata.json")
        with open(json_file, "w") as f:
            json.dump(data, f)
        matrix_file = os.path.join(folder_path, "matrix")
        self.matrix.dump(matrix_file)
