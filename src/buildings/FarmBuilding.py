import random
from math import inf
from random import randint

from buildings.JobBuilding import JobBuilding


class FarmBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, "Farm Building", orientation, width=random.randint(5, 10),
                         depth=7, height=3)
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"], agent.simulation)
        self.place(center_point, agent.simulation)

        FarmBuilding.INSTANCE = self

    def build(self):
        for dx in range(self.width):
            for dz in range(self.depth):
                is_log = (dx == 0 or dx == self.width - 1 or dz == 0 or dz == self.depth - 1)
                self.add_block_to_matrix(dx, 0, dz, "minecraft:dirt")
                if is_log:
                    self.add_block_to_matrix(dx, 1, dz, "minecraft:oak_log")
                    self.add_block_to_matrix(dx, 0, dz, "minecraft:oak_log")
                else:
                    if dz == 3:
                        self.add_block_to_matrix(dx, 1, dz, "minecraft:water")
                    else:
                        self.add_block_to_matrix(dx, 1, dz, "minecraft:farmland")
                        self.add_block_to_matrix(dx, 2, dz, "minecraft:wheat")
        self.add_block_to_matrix(0, 2, 3, "minecraft:torch")
        self.add_block_to_matrix(self.width - 1, 2, 3, "minecraft:torch")
        self.check_built()

    def best_spot(self, nbtry, simulation):
        best_spot = None
        best_score = - inf
        t = 0

        while best_spot is None or t < nbtry:
            x = randint(0, simulation.heightmap.shape[0])
            z = randint(0, simulation.heightmap.shape[1])

            score = -simulation.lava[x - self.width // 2 - 1:x + self.width // 2 + 1,
                     z - self.depth // 2 - 1:z + self.depth // 2 + 1].sum()
            score += 0.5 * simulation.water[x - self.width:x + self.width, z - self.depth:z + self.depth].sum()

            if simulation.walkable[x - self.width // 2 - 1:x + self.width // 2 + 1,
               z - self.depth // 2 - 1:z + self.depth // 2 + 1].sum().item() < self.width * self.depth or simulation.buildings[
                                                                                                          x - self.width:x + self.width,
                                                                                                          z - self.depth:z + self.depth].sum().item() > 0:
                continue

            if score > best_score:
                best_score = score
                best_spot = (x, z)

            t += 1

        return best_spot

    @staticmethod
    def get_instance(center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        if FarmBuilding.INSTANCE is None:
            return FarmBuilding(center_point, agent, orientation)
        return FarmBuilding.INSTANCE
