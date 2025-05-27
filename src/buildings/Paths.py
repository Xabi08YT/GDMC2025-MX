import numpy as np
import utils.pathfinding as pathfinding
from buildings.Building import Building

class Paths(Building):
    def __init__(self, simulation, x1, z1, x2, z2):
        self.simulation = simulation
        super().__init__(None, None, "Paths", width=self.simulation.walkable.shape[0], height=1, depth=self.simulation.shape[1])
        self.pathfinding = pathfinding(simulation, x1, z1, x2, z2)
        self.path, self.path_matrix = self.pathfinding.find_path()


    def build(self):
        for x, z in self.path:
            if self.simulation.walkable[x, z]:
                super().add_block_to_matrix(x, 0, z, "minecraft:dirt_path")
        super().built()