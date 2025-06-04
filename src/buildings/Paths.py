import numpy as np
from utils.Pathfinding import Pathfinding
from buildings.Building import Building
from buildings.Bridge import Bridge
import os
import json

class Paths():
    def __init__(self, simulation, buildings):
        self.simulation = simulation
        self.buildings = buildings
        self.matrix = np.zeros((simulation.walkable.shape[0], simulation.walkable.shape[1]), dtype=object)
        self.bridges = []

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

            pclass = Pathfinding(self.simulation, entrance[0],entrance[1], self.simulation.firecamp_coords[0],self.simulation.firecamp_coords[1])
            path = pclass.find_path()
            if path is None:
                continue

            if hasattr(pclass, "bridges_to_build") and pclass.bridges_to_build:
                for start_point, end_point in pclass.bridges_to_build:
                    dx = end_point[0] - start_point[0]
                    dz = end_point[1] - start_point[1]

                    if abs(dx) > abs(dz):
                        orientation = "east" if dx > 0 else "west"
                    else:
                        orientation = "south" if dz > 0 else "north"

                    bridge = Bridge(start_point, end_point, agent=self.simulation.agents[0], orientation=orientation)
                    bridge.build()
                    bridge.matrix_to_files()
                    self.bridges.append(bridge)

                    self.update_walkable_with_bridge(start_point, end_point)


            for x, z in path:
                self.matrix[max(0,x-1):min(self.simulation.heightmap.shape[0],x+2),
                max(0,z-1):min(self.simulation.heightmap.shape[1],z+2)] = i

    def update_walkable_with_bridge(self, start_point, end_point):
        x1, z1 = start_point
        x2, z2 = end_point

        steps = max(abs(x2 - x1), abs(z2 - z1))
        if steps == 0:
            return

        dx = (x2 - x1) / steps
        dz = (z2 - z1) / steps

        for i in range(steps + 1):
            x = int(round(x1 + dx * i))
            z = int(round(z1 + dz * i))
            if 0 <= x < self.simulation.walkable.shape[0] and 0 <= z < self.simulation.walkable.shape[1]:
                self.simulation.walkable[x, z] = 1

    def export(self):
        folder_path = os.path.join("generated", "path")
        os.makedirs(folder_path, exist_ok=True)
        matrix_file = os.path.join(folder_path, "pathmap")
        self.matrix.dump(matrix_file)
