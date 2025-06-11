from random import choice
import numpy as np
import os
from utils.math_methods import distance_xz
import json


class Building:
    BUILDINGS = []

    def __init__(self, center_point: tuple[int, int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated", width=5, height=5, depth=5, bupdates=True):
        """
        Initializes a new instance of the Building class.

        Args:
        :param center_point: (tuple[int, int] | None): (x, z) coordinates for the center of the building.
        :param agent: The agent associated with the building.
        :param name: (str): Name of the building.
        :param orientation: (str): Initial orientation ("north", "south", "east", "west").
        :param built: (bool): Whether the building is already constructed.
        :param folder: (str): Output folder for storing building data.
        :param width: (int): Width of the building in blocks.
        :param height: (int): Height of the building in blocks.
        :param depth: (int): Depth of the building in blocks.
        :param bupdates: (bool): Whether building updates are enabled.
        """
        self.built = built
        self.orientation = orientation
        self.width = width
        self.height = height
        self.depth = depth
        self.radius = 10
        self.center_point = center_point if center_point is not None else None
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
        self.agent = agent

    def built(self):
        """
        Marks the building as built by setting the 'built' flag to True.
        """
        self.built = True

    def set_orientation_according_to_center(self, agent=None):
        """
        Sets the building's orientation based on its position relative to the village center (firecamp).

        Args:
        :param agent: Optional agent to override the default associated agent.
        """
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
        """
        Calculates the coordinates of the building's entrance based on orientation and center point.
        Returns:
            tuple[int, int] | None: The (x, z) entrance coordinates, or None if center_point is not set.
        """
        if self.center_point is None:
            return None

        x, z = self.center_point[0], self.center_point[1]

        entrance_offset = {"north": (0, -self.width // 2), "south": (0, self.width // 2),
                           "east": (self.depth // 2, 0), "west": (-self.depth // 2, 0)}

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

    def check_collision(self, center_point, min_distance=2):
        """
        Checks if placing a building at the given center_point would result in a collision
        with any existing buildings.

        Args:
            :param center_point: (tuple[int, int]): The (x, z) coordinates for the proposed building center.
            :param min_distance: (int, optional): Minimum allowed distance between buildings. Defaults to 2.

        Returns:
            bool: True if a collision is detected, False otherwise.
        """
        x_min = center_point[0] - self.width // 2 - min_distance
        x_max = center_point[0] + self.width // 2 + min_distance
        z_min = center_point[1] - self.depth // 2 - min_distance
        z_max = center_point[1] + self.depth // 2 + min_distance
        for b in self.BUILDINGS:
            if b.center_point is None or b is self:
                continue
            bx_min = b.center_point[0] - b.width // 2 - min_distance
            bx_max = b.center_point[0] + b.width // 2 + min_distance
            bz_min = b.center_point[1] - b.depth // 2 - min_distance
            bz_max = b.center_point[1] + b.depth // 2 + min_distance
            if not (x_max < bx_min or x_min > bx_max or z_max < bz_min or z_min > bz_max):
                return True
        return False

    def place(self, center_point: tuple[int, int], sim=None):
        """
        Attempts to place the building at the specified center_point in the simulation.
        :param center_point: The (x, z) coordinates for the building's center.
        :param sim: The current simulation instance, used to check for collisions and update the heightmap.
        """
        if self.check_collision(center_point, min_distance=2):
            return False
        center_point = (max(center_point[0], self.width), max(center_point[1], self.depth))
        center_point = (min(center_point[0], sim.heightmap.shape[0] - self.width),
                        min(center_point[1], sim.heightmap.shape[1] - self.depth))
        x_min = center_point[0] - self.width // 2 - 2
        x_max = center_point[0] + self.width // 2 + 2
        z_min = center_point[1] - self.depth // 2 - 2
        z_max = center_point[1] + self.depth // 2 + 2
        if np.any(sim.buildings[x_min:x_max, z_min:z_max]):
            return False
        self.center_point = center_point
        sim.buildings[x_min:x_max, z_min:z_max] = True
        return True

    def clear(self):
        """
        Clears the building's matrix by setting all blocks above the ground level to air.
        """
        for x in range(self.width):
            for y in range(1, self.height):
                for z in range(self.depth):
                    self.add_block_to_matrix(x, y, z, "minecraft:air")

    def __str__(self):
        return f"{self.name}"

    def add_block_to_matrix(self, x: int, y: int, z: int, block: str):
        """
        Adds a block to the building's matrix at the specified coordinates.
        :param x: The x-coordinate in the matrix.
        :param y: The y-coordinate in the matrix.
        :param z: The z-coordinate in the matrix.
        :param block: The block type to add (as a string).
        """
        self.matrix[x][z][y] = block

    def matrix_to_files(self):
        """
        Exports the building's metadata and matrix to files in the specified folder.
        """
        if not hasattr(self, "center_point") or self.center_point is None:
            return
        if type(self.center_point[0]) is not int:
            self.center_point = self.center_point[0].item(), self.center_point[1]
        if type(self.center_point[1]) is not int:
            self.center_point = self.center_point[0], self.center_point[1].item()
        data = {
            "name": self.name,
            "x": self.center_point[0],
            "z": self.center_point[1],
            "built": self.built,
            "orientation": self.orientation,
            "bupdates": self.bupdates,
            "biome": self.agent.simulation.biomes[self.center_point[0], self.center_point[1]] if hasattr(self.agent,
                                                                                                         "simulation") else "minecraft:plains",
            "happiness": self.agent.happiness if hasattr(self, "agent") and self.agent is not None and not getattr(
                self.agent, "dead", False) else 0,
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
