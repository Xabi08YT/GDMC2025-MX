from math import inf
from random import randint

from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz

import random


class WorkshopBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        width = random.choice([9,11,13,15])
        depth = 9
        if orientation in ["east", "west"]:
            width, depth = depth, width

        super().__init__(center_point, agent, agent.name + "'s WorkshopBuilding", orientation, width=width, height=7, depth=depth)
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"],agent.simulation)
        self.place(center_point,agent.simulation)
        self.corners = [
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]

        WorkshopBuilding.INSTANCE = self

    def is_floor(self, x, z):
        if self.orientation == "north":
            return  0 < z < 5 and 0 < x < self.width - 1
        elif self.orientation == "south":
            return 5 < z < self.depth - 1 and 0 < x < self.width - 1
        elif self.orientation == "east":
            return 0 < x < 5 and 0 < z < self.depth - 1
        elif self.orientation == "west":
            return 5 < x < self.width - 1 and 0 < z < self.depth - 1
        return None

    def is_pillar(self, x, z):
        if self.orientation == "north":
            return x in [1,self.width-2] and z in [1,5]
        elif self.orientation == "south":
            return x in [1,self.width-2] and z in [self.depth-2,self.depth-6]
        elif self.orientation == "east":
            return z in [1,self.depth-2] and x in [1,5]
        elif self.orientation == "west":
            return z in [1,self.depth-2] and x in [self.width-2,self.width-6]
        return None

    def is_high_pillar(self, x, z):
        if self.orientation == "north":
            return x in [1,self.width-2] and z == 5
        elif self.orientation == "south":
            return x in [1,self.width-2] and z == self.depth-6
        elif self.orientation == "east":
            return z in [1,self.depth-2] and x == 5
        elif self.orientation == "west":
            return z in [1,self.depth-2] and x == self.width-6
        return None

    def is_entrance(self, x, z):
        if self.orientation == "north":
            return x == self.width//2 and z == 1
        elif self.orientation == "south":
            return x == self.width//2 and z == self.depth - 2
        elif self.orientation == "east":
            return x == 1 and z == self.depth//2
        elif self.orientation == "west":
            return x == self.width - 2 and z == self.depth//2
        return None

    def is_wall(self,x,z):
        if self.orientation == "north":
            return 0 < z < 6 and x in [1,self.width-2] or (z == 1 and x not in [0,self.width-1])
        elif self.orientation == "south":
            return self.depth - 6 < z < self.depth - 1 and x in [1,self.width-2] or z == self.depth - 2
        elif self.orientation == "east":
            return 0 < x < 6 and z in [1,self.depth-2] or (x == 1 and z not in [0,self.depth-1])
        elif self.orientation == "west":
            return self.width - 6 < x < self.width - 1 and z in [1,self.depth-2] or x == self.width - 2
        return None

    def is_window(self, x, z):
        if self.orientation == "north":
            return z == 3 and x in [1,self.width-2]
        elif self.orientation == "south":
            return z == self.depth-4 and x in [1,self.width-2]
        elif self.orientation == "east":
            return x == 3 and z in [1,self.depth-2]
        elif self.orientation == "west":
            return x == self.width-4 and z in [1,self.depth-2]
        return None

    def is_store_support(self, x, z):
        if self.orientation == "north":
            return z == self.depth-1 and x in [1,self.width-2]
        elif self.orientation == "south":
            return z == 0 and x in [1,self.width-2]
        elif self.orientation == "east":
            return x == 0 and z in [1,self.depth-2]
        elif self.orientation == "west":
            return x == self.width-1 and z in [1,self.depth-2]
        return None

    def is_edge_store_support(self, x, z):
        if self.orientation == "north":
            return z == 8 and 0 < x < self.width - 1
        elif self.orientation == "south":
            return z == self.depth - 9 and 0 < x < self.width - 1
        elif self.orientation == "east":
            return x == 8 and 0 < z < self.depth - 1
        elif self.orientation == "west":
            return x == self.depth - 9 and 0 < z < self.depth - 1
        return None

    def is_store_front_color(self, x, z):
        if self.orientation == "north":
            return z in [6,7] and 0 < x < self.width-1
        elif self.orientation == "south":
            return z in [self.depth-8,self.depth-7] and 0 < x < self.width-1
        elif self.orientation == "east":
            return x in [6,7] and 0 < z < self.depth-1
        elif self.orientation == "west":
            return x in [self.width-8,self.width-7] and 0 < z < self.depth-1
        return None

    def is_counter(self, x, z):
        if self.orientation == "north":
            return z == 5 and 1 < x < self.width - 2
        elif self.orientation == "south":
            return z == self.depth - 6 and 1 < x < self.width - 2
        elif self.orientation == "east":
            return x == 5 and 1 < z < self.depth - 2
        elif self.orientation == "west":
            return x == self.width - 6 and 1 < z < self.depth - 2
        return None

    def build(self):
        wools = ["minecraft:red_wool","minecraft:white_wool"]
        for x in range(self.width):
            for z in range(self.depth):
                if self.is_floor(x, z):
                    self.add_block_to_matrix(x, 0, z, "minecraft:stone_bricks")
                if self.is_wall(x, z):
                    mod = int((z == 4 and self.orientation in ["north", "south"]) or (
                                x == 4 and self.orientation in ["east", "west"]))
                    for i in range(1, 4 + mod):
                        self.add_block_to_matrix(x, i, z, "minecraft:oak_planks")
                if self.is_pillar(x, z):
                    mod = 2 * self.is_high_pillar(x, z)
                    for y in range(1, 4 + mod):
                        self.add_block_to_matrix(x, y, z, "minecraft:oak_log")
                elif self.is_entrance(x, z):
                    dor = {
                        "north": "south",
                        "south": "north",
                        "east": "west",
                        "west": "east"
                    }
                    self.add_block_to_matrix(x, 1, z, f"minecraft:oak_door[half=lower,facing={dor[self.orientation]}]")
                    self.add_block_to_matrix(x, 2, z, f"minecraft:oak_door[half=upper,facing={dor[self.orientation]}]")
                elif self.is_window(x, z):
                    self.add_block_to_matrix(x, 2, z, "minecraft:oak_fence")
                    self.add_block_to_matrix(x, 3, z, "minecraft:oak_fence")
                    self.add_block_to_matrix(x, 4, z, "minecraft:oak_planks")
                elif self.is_store_support(x, z):
                    for y in range(1, 4):
                        self.add_block_to_matrix(x, y, z, "minecraft:oak_fence")
                    self.add_block_to_matrix(x, 4, z, wools[x % 2 if self.orientation in ["north", "south"] else z % 2])
                elif self.is_store_front_color(x, z):
                    self.add_block_to_matrix(x, 5, z, wools[x % 2 if self.orientation in ["north", "south"] else z % 2])
                elif self.is_edge_store_support(x, z):
                    self.add_block_to_matrix(x, 4, z, wools[x % 2 if self.orientation in ["north", "south"] else z % 2])
                elif self.is_counter(x, z):
                    self.add_block_to_matrix(x, 1, z, f"minecraft:oak_stairs[half=top,facing={self.orientation},shape=straight]")


        self.built = True
        return

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
