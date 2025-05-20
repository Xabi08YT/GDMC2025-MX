from random import choice
import numpy as np
import os
from utils.math_methods import distance_xz
import json

class Building:

    BUILDINGS = []

    def __init__(self, center_point: tuple[int, int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated", width = 5, height = 5, depth = 5):
        self.built = built
        self.orientation = orientation
        self.width = width
        self.height = height
        self.depth = depth
        if center_point is not None:
            self.place(center_point)
        self.radius = 10
        if agent is not None and center_point is not None:
            self.lowest_y = agent.simulation.heightmap[center_point[0] - self.radius:center_point[0] + self.radius,
                            center_point[1] - self.radius:center_point[1] + self.radius].min().item() - 1
            self.highest_y = agent.simulation.heightmap[center_point[0] - self.radius:center_point[0] + self.radius,
                             center_point[1] - self.radius:center_point[1] + self.radius].max().item() - 1
            self.agent = agent
        self.name = name
        self.folder = folder
        self.matrix = np.zeros((self.width, self.depth, self.height), dtype=object)
        self.BUILDINGS.append(self)

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
        entrance_x = x + offset[0]
        entrance_z = z + offset[1]

        return entrance_x, entrance_z

    def place(self,center_point: tuple[int, int], sim = None):
        self.center_point = center_point
        if hasattr(self,"agent") and self.agent is not None:
            self.agent.simulation.buildings[
                center_point[0] - self.width//2 - 1:center_point[0] + self.width//2 +1,
                center_point[0] - self.width//2 - 1:center_point[0] + self.width//2 +1
            ] = True
        else:
            sim.buildings[
                center_point[0] - self.width // 2 - 1:center_point[0] + self.width // 2 + 1,
                center_point[0] - self.width // 2 - 1:center_point[0] + self.width // 2 + 1
            ] = True
        return

    def __str__(self):
        return f"{self.name}"

    def add_block_to_matrix(self, x: int, y: int, z: int, block: str):
        self.matrix[x][z][y] = block

    def matrix_to_files(self):
        if not hasattr(self, "center_point") or self.center_point is None:
            return
        data = {
            "name": self.name,
            "x": self.center_point[0],
            "z": self.center_point[1].item(),
            "built": self.built
        }
        folder_path = os.path.join(self.folder, self.name)
        os.makedirs(folder_path, exist_ok=True)
        json_file = os.path.join(folder_path, "metadata.json")
        with open(json_file, "w") as f:
            json.dump(data, f)
        matrix_file = os.path.join(folder_path, "matrix")
        self.matrix.dump(matrix_file)
