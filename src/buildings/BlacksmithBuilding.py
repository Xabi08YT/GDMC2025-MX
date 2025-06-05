import random
from random import randint
from math import inf

import numpy as np
from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz


class BlacksmithBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        width = random.choice([9,11,13,15])
        depth = 9
        if orientation in ["east", "west"]:
            width, depth = depth, width

        super().__init__(center_point, agent, "Blacksmith Building", orientation, width=width, height=8, depth=depth)
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
        super().clear()

    def is_floor(self, x, z):
        if self.orientation == "north":
            return 0 < z < 5 and 0 < x < self.width - 1
        elif self.orientation == "south":
            return 5 < z < self.depth - 1 and 0 < x < self.width - 1
        elif self.orientation == "east":
            return 0 < x < 5 and 0 < z < self.depth - 1
        elif self.orientation == "west":
            return 5 < x < self.width - 1 and 0 < z < self.depth - 1
        return None

    def is_pillar(self, x, z):
        if self.orientation == "north":
            return x in [1, self.width - 2] and z in [1, 5]
        elif self.orientation == "south":
            return x in [1, self.width - 2] and z in [self.depth - 2, self.depth - 6]
        elif self.orientation == "east":
            return z in [1, self.depth - 2] and x in [1, 5]
        elif self.orientation == "west":
            return z in [1, self.depth - 2] and x in [self.width - 2, self.width - 6]
        return None

    def is_high_pillar(self, x, z):
        if self.orientation == "north":
            return x in [1, self.width - 2] and z == 5
        elif self.orientation == "south":
            return x in [1, self.width - 2] and z == self.depth - 6
        elif self.orientation == "east":
            return z in [1, self.depth - 2] and x == 5
        elif self.orientation == "west":
            return z in [1, self.depth - 2] and x == self.width - 6
        return None

    def is_entrance(self, x, z):
        if self.orientation == "north":
            return x == self.width // 2 and z == 1
        elif self.orientation == "south":
            return x == self.width // 2 and z == self.depth - 2
        elif self.orientation == "east":
            return x == 1 and z == self.depth // 2
        elif self.orientation == "west":
            return x == self.width - 2 and z == self.depth // 2
        return None

    def is_wall(self, x, z):
        if self.orientation == "north":
            return 0 < z < 6 and x == 1 or (z == 1 and x not in [0, self.width - 1])
        elif self.orientation == "south":
            return self.depth - 6 < z < self.depth - 1 and x == self.width - 2 or z == self.depth - 2
        elif self.orientation == "east":
            return 0 < x < 6 and z == 1 or (x == 1 and z not in [0, self.depth - 1])
        elif self.orientation == "west":
            return self.width - 6 < x < self.width - 1 and z == self.depth - 2 or x == self.width - 2
        return None

    def is_window(self, x, z):
        if self.orientation == "north":
            return z == 3 and x == 1
        elif self.orientation == "south":
            return z == self.depth - 4 and x == self.width - 2
        elif self.orientation == "east":
            return x == 3 and z == 1
        elif self.orientation == "west":
            return x == self.width - 4 and z == self.depth - 2
        return None

    def is_store_support(self, x, z):
        if self.orientation == "north":
            return z == self.depth - 1 and x in [1, self.width - 2]
        elif self.orientation == "south":
            return z == 0 and x in [1, self.width - 2]
        elif self.orientation == "east":
            return x == 0 and z in [1, self.depth - 2]
        elif self.orientation == "west":
            return x == self.width - 1 and z in [1, self.depth - 2]
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
            return z in [6, 7] and 0 < x < self.width - 1
        elif self.orientation == "south":
            return z in [self.depth - 8, self.depth - 7] and 0 < x < self.width - 1
        elif self.orientation == "east":
            return x in [6, 7] and 0 < z < self.depth - 1
        elif self.orientation == "west":
            return x in [self.width - 8, self.width - 7] and 0 < z < self.depth - 1
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

    def is_anvil(self, x, z):
        if self.orientation == "north":
            return z == 3 and x == self.width - 4
        elif self.orientation == "south":
            return z == self.depth - 4 and x == self.width - 4
        elif self.orientation == "east":
            return x == 3 and z == self.depth - 4
        elif self.orientation == "west":
            return x == self.width - 4 and z == 3
        return None

    def is_other_utility(self, x, z):
        if self.orientation == "north":
            return x == 2 and 1 < z < 5
        elif self.orientation == "south":
            return x == 2 and self.depth - 6 < z < self.depth - 2
        elif self.orientation == "east":
            return z == 2 and 1 < x < 5
        elif self.orientation == "west":
            return z == 2 and self.width - 6 < x < self.width - 2
        return None

    def is_water_cauldron(self, x, z):
        if self.orientation == "north":
            return x == self.width-2 and z == 4
        elif self.orientation == "south":
            return x == 1 and z == self.depth - 5
        elif self.orientation == "east":
            return x == 4 and z == self.depth - 2
        elif self.orientation == "west":
            return x == self.width - 5 and z == 1
        return None

    def define_roof_outline(self):
        rwidth = self.width // 2 + 2 if self.orientation in ["north", "south"] else self.depth // 2 + 2
        rblocks = []
        rublocks = []
        mods = []
        umods = []
        for i in range(rwidth):
            mods.append((i + 1) // 2)
            umods.append(i // 2)
            if i % 2 == 0:
                rblocks.append("oak_slab[type=top]")
                if i != 0:
                    rublocks.append("oak_planks")
            else:
                rblocks.append("oak_slab[type=bottom]")
                rublocks.append("oak_slab[type=top]")

        return rblocks, rublocks, mods, umods

    def is_furnace_front(self,x,z):
        if self.orientation == "north":
            return x == self.width - 1 and 1 < z < 5
        elif self.orientation == "south":
            return x == 0 and self.depth - 6 < z < self.depth - 2
        elif self.orientation == "east":
            return z == self.depth - 1 and 1 < x < 5
        elif self.orientation == "west":
            return z == 0 and self.width - 6 < x < self.width - 2
        return None

    def generate_furnace(self):
        sf = {
            "north":"west",
            "south":"east",
            "east":"north",
            "west":"south"
        }
        if self.orientation in ["north","south"]:
            matrix = np.zeros(shape=[2,self.depth,self.height], dtype=object)
            mod = int(self.orientation == "south")
            matrix[mod][3][1:] = ["minecraft:lava_cauldron","air","minecraft:cobbled_deepslate", "minecraft:cobbled_deepslate", "minecraft:cobbled_deepslate_wall","minecraft:cobbled_deepslate_wall","minecraft:flower_pot"]
            matrix[(mod + 1) % 2][3][1:4] = [f"cobbled_deepslate_stairs[facing={sf[self.orientation]},half=top]", "minecraft:cobbled_deepslate", f"cobbled_deepslate_stairs[facing={sf[self.orientation]},half=bottom]"]
            matrix[(mod + 1) % 2][2][2] = "minecraft:cobbled_deepslate"
            matrix[(mod + 1) % 2][4][2] = "minecraft:cobbled_deepslate"
            matrix[mod][4][1:4] = [f"cobbled_deepslate_stairs[facing=north,half=top]", "minecraft:cobbled_deepslate", f"cobbled_deepslate_stairs[facing=north,half=bottom]"]
            matrix[mod][2][1:4] = [f"cobbled_deepslate_stairs[facing=south,half=top]", "minecraft:cobbled_deepslate", f"cobbled_deepslate_stairs[facing=south,half=bottom]"]
        elif self.orientation in ["east","west"]:
            matrix = np.zeros(shape=[self.width,2,self.height], dtype=object)
        else: return None
        return matrix

    def build(self):
        if self.built: return
        wools = ["minecraft:light_blue_wool", "minecraft:white_wool"]
        sff = ["north","south"]
        if self.orientation in ["east", "west"]:
            sff = ["east","west"]
        furnace_front =  [["minecraft:cobbled_deepslate", "minecraft:cobbled_deepslate", "minecraft:cobbled_deepslate"],
             ["minecraft:cobbled_deepslate", "minecraft:air", "minecraft:cobbled_deepslate"],
                [f"minecraft:cobbled_deepslate_stairs[facing={sff[1]}]", "minecraft:cobbled_deepslate", f"minecraft:cobbled_deepslate_stairs[facing={sff[0]}]"]]
        c = 0
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
                        "north": "west",
                        "south": "east",
                        "east": "north",
                        "west": "south"
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
                    self.add_block_to_matrix(x, 1, z,
                                             f"minecraft:oak_stairs[half=top,facing={self.orientation},shape=straight]")
                    if self.orientation in ["north", "south"] and x == self.width // 2:
                        self.add_block_to_matrix(x, 5, z, "minecraft:lantern[hanging=true]")
                    elif self.orientation in ["east", "west"] and z == self.depth // 2:
                        self.add_block_to_matrix(x, 5, z, "minecraft:lantern[hanging=true]")
                elif self.is_anvil(x, z):
                    scf = {
                        "north": "west",
                        "south": "east",
                        "east": "north",
                        "west": "south"
                    }
                    self.add_block_to_matrix(x, 1, z, f"minecraft:anvil[facing={scf[self.orientation]}]")
                elif self.is_other_utility(x, z):
                    self.add_block_to_matrix(x, 1, z, "minecraft:barrel[facing=up]")
                if self.is_water_cauldron(x, z):
                    self.add_block_to_matrix(x, 1, z, f"minecraft:water_cauldron[level={random.randint(1, 3)}]")
                if self.is_furnace_front(x, z):
                    for y in range(3):
                        self.add_block_to_matrix(x, y + 1, z, furnace_front[y][c])
                    c+=1


        rblocks, rublocks, mods, umods = self.define_roof_outline()

        for x in range(self.width):
            for z in range(self.depth):
                if self.orientation == "north" and 0 <= z < 6:
                    self.add_block_to_matrix(x, 3 + mods[z], z, rblocks[z])
                    if (x in [0, self.width - 1] or (
                            x == 1 and rublocks[z - 1] == "oak_planks")) and 0 < z < 6:
                        self.add_block_to_matrix(x, 3 + umods[z], z, rublocks[z - 1])
                elif self.orientation == "south" and self.depth - 6 <= z < self.depth:
                    self.add_block_to_matrix(x, 3 + mods[self.depth - z - 1], z, rblocks[self.depth - z - 1])
                    if (x in [0, self.width - 1] or (x == 1 and rublocks[
                        self.depth - z - 2] == "oak_planks")) and self.depth - 6 < z < self.depth:
                        self.add_block_to_matrix(x, 3 + umods[self.depth - z - 1], z, rublocks[self.depth - z - 2])
                elif self.orientation == "east" and 0 <= x < 6:
                    self.add_block_to_matrix(x, 3 + mods[x], z, rblocks[x])
                    if (z in [0, self.depth - 1] or (z == 1 and rublocks[x - 1] == "oak_planks")) and 0 < x < 6:
                        self.add_block_to_matrix(x, 3 + umods[x], z, rublocks[x - 1])
                elif self.orientation == "west" and self.width - 6 <= x < self.width:
                    self.add_block_to_matrix(x, 3 + mods[self.width - x - 1], z, rblocks[self.width - x - 1])
                    if (z in [0, self.depth - 1] or (z == 1 and rublocks[self.width - x - 2] == "oak_planks")) and self.width - 6 < x < self.width:
                        self.add_block_to_matrix(x, 3 + umods[self.width - x - 1], z, rublocks[self.width - x - 2])

        matrix = self.generate_furnace()
        if self.orientation == "north":
            self.matrix = np.concat((self.matrix,matrix),axis=0)
        elif self.orientation == "south":
            self.matrix = np.concat((matrix,self.matrix),axis=0)
        elif self.orientation == "east":
            self.matrix = np.concat((self.matrix,matrix),axis=1)
        elif self.orientation == "west":
            self.matrix = np.concat((matrix,self.matrix),axis=1)
        self.built = True
        return

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
            score -= 10 * simulation.buildings[x - self.radius:x + self.radius,
                          z - self.radius:z + self.radius].sum().item()

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