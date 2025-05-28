import random
from random import randint
from math import inf

from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz


class BlacksmithBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s BlacksmithBuilding", orientation, width=random.randint(5, 10), height=6, depth=random.randint(3, 10))
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"],agent.simulation)
        self.place(center_point,agent.simulation)
        self.corners = [
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]
        self.corner_block = "minecraft:bricks"
        BlacksmithBuilding.INSTANCE = self

    def build(self):
        for dx in range(self.width):
            for dz in range(self.depth):
                self.add_block_to_matrix(dx, 4, dz, "minecraft:cobblestone")
                self.add_block_to_matrix(dx, 0, dz, "minecraft:cobblestone")
                if dx == 0 or dx == self.width - 1 or dz == 0 or dz == self.depth - 1:
                    self.add_block_to_matrix(dx, 5, dz, "minecraft:smooth_stone_slab[type=bottom]")
                if [dx, dz] in self.corners:
                    for dy in range(1, 4):
                        self.add_block_to_matrix(dx, dy, dz, "minecraft:stone_brick_wall")
        for i in range(2):
            self.add_block_to_matrix(1 + i, 1, 0, "minecraft:furnace[facing=south]")
            self.add_block_to_matrix(3, 1, 0, "minecraft:anvil[facing=south]")
            self.add_block_to_matrix(self.width - 2, 1, self.depth - 2, "minecraft:lava_cauldron")
        self.check_built()

    def best_spot(self, nbtry, simulation):
        best_spot = None
        best_score = - inf
        t = 0

        while best_spot is None or t < nbtry:
            x = randint(0,simulation.heightmap.shape[0])
            z = randint(0,simulation.heightmap.shape[1])

            score = -simulation.water[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1:z+self.depth//2+1].sum()
            score -= distance_xz(x,simulation.firecamp_coords[0],z,simulation.firecamp_coords[1])
            score += 0.5 * simulation.lava[x-self.width:x+self.width,z-self.depth:z+self.depth].sum()

            if simulation.walkable[x - self.width // 2 - 1:x + self.width // 2 + 1,
               z - self.depth // 2 - 1:z + self.depth // 2 + 1].sum().item() < self.width * self.depth or simulation.buildings[x - self.width:x + self.width,
                          z - self.depth:z + self.depth].sum().item() > 0:
                continue

            if score > best_score:
                best_score = score
                best_spot = (x,z)

            t += 1

        return best_spot

    @staticmethod
    def get_instance(center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        if BlacksmithBuilding.INSTANCE is None:
            return BlacksmithBuilding(center_point, agent, orientation)
        return BlacksmithBuilding.INSTANCE