import numpy as np
from utils.Pathfinding import Pathfinding
from buildings.Building import Building
import os
import json

class Paths():
    def __init__(self, simulation, buildings):
        self.simulation = simulation
        self.buildings = buildings
        self.matrix = np.zeros((simulation.walkable.shape[0], simulation.walkable.shape[1]), dtype=object)

    def build(self):
        for building in self.buildings:
            if not hasattr(building, "center_point") or building.center_point is None:
                continue
            if not self.simulation.walkable[building.center_point[0], building.center_point[1]]:
                continue

            entrance = building.get_entrance_coordinates()
            if entrance is None:
                continue

            path = Pathfinding.find_path(self.simulation.walkable, entrance, self.simulation.firecamp_coords)
            if path is None:
                continue

            for x, z in path:
                self.matrix[x, z] = 1

    def export(self):
        folder_path = os.path.join("generated", "path")
        os.makedirs(folder_path, exist_ok=True)
        matrix_file = os.path.join(folder_path, "pathmap")
        self.matrix.dump(matrix_file)
