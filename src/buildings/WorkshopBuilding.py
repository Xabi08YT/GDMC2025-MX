from math import inf
from random import randint

from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz

import random


class WorkshopBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s WorkshopBuilding", orientation, width=random.randint(5, 10), height=6, depth=random.randint(3, 10))
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
        WorkshopBuilding.INSTANCE = self

    def build(self):
        for dx in range(self.width):
            for dz in range(self.depth):
                self.add_block_to_matrix(dx, 3, dz, "minecraft:stone_bricks")
                self.add_block_to_matrix(dx, 0, dz, "minecraft:stone_bricks")
                if [dx, dz] in self.corners:
                    for dy in range(1, 3):
                        self.add_block_to_matrix(dx, dy, dz, "minecraft:cobblestone_wall")
        self.add_block_to_matrix(3, 1, 0, "minecraft:water_cauldron")
        self.add_block_to_matrix(2, 1, 0, "minecraft:stonecutter[facing=south]")
        self.check_built()

    def best_spot(self, nbtry, simulation):
        best_spot = None
        best_score = - inf
        t = 0

        while best_spot is None or t < nbtry:
            x = randint(0,simulation.heightmap.shape[0])
            z = randint(0,simulation.heightmap.shape[1])

            score = -simulation.lava[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1:z+self.depth//2+1].sum()
            score -= distance_xz(x,simulation.firecamp_coords[0],z,simulation.firecamp_coords[1])
            score += 0.5 * simulation.wood[x-self.width:x+self.width,z-self.depth:z+self.depth].sum()
            score -= 10 * simulation.buildings[x - self.radius:x + self.radius,
                          z - self.radius:z + self.radius].sum().item()

            if simulation.walkable[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1:z+self.depth//2+1].sum().item() < self.width * self.depth or simulation.buildings[x - self.width:x + self.width,
                          z - self.depth:z + self.depth].sum().item() > 0:
                continue

            if score > best_score:
                best_score = score
                best_spot = (x,z)

            t += 1

        return best_spot

    @staticmethod
    def get_instance(center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        if WorkshopBuilding.INSTANCE is None:
            return WorkshopBuilding(center_point, agent, orientation)
        return WorkshopBuilding.INSTANCE
