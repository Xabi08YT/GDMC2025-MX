import numpy as np
from utils.Pathfinding import Pathfinding
from buildings.Building import Building
from buildings.Bridge import Bridge
import os
import json

from utils.ANSIColors import ANSIColors


class Paths():
    def __init__(self, simulation, buildings):
        self.simulation = simulation
        self.buildings = buildings
        self.matrix = np.zeros((simulation.walkable.shape[0], simulation.walkable.shape[1]), dtype=object)
        self.bridges = np.zeros((simulation.walkable.shape[0], simulation.walkable.shape[1]), dtype=bool)
        self.paths = np.zeros((simulation.walkable.shape[0], simulation.walkable.shape[1]), dtype=bool)

    def build(self):
        i = 0
        for building in self.buildings:
            i+= 1
            if not hasattr(building, "center_point") or building.center_point is None:
                continue
            if not self.simulation.walkable[building.center_point[0], building.center_point[1]]:
                continue

            entrance = building.get_entrance_coordinates()
            if entrance is None:
                continue

            print(f"{ANSIColors.OKBLUE}[SIMULATION INFO] Building path between {ANSIColors.ENDC}{ANSIColors.OKGREEN}{building.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE} and firecamp{ANSIColors.ENDC}")

            pclass = Pathfinding(self.simulation, entrance[0],entrance[1], self.simulation.firecamp_coords[0],self.simulation.firecamp_coords[1],self.bridges,self.paths)
            path = pclass.find_path()
            self.bridges = pclass.bridges
            if path is None:
                continue

            for x, z in path:
                self.matrix[max(0,x-1):min(self.simulation.heightmap.shape[0],x+2),
                max(0,z-1):min(self.simulation.heightmap.shape[1],z+2)] = i
                self.paths[x, z] = True

    def export(self):
        folder_path = os.path.join("generated", "path")
        os.makedirs(folder_path, exist_ok=True)
        matrix_file = os.path.join(folder_path, "pathmap")
        self.matrix.dump(matrix_file)
