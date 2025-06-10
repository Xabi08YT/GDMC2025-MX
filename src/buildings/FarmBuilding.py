import random
from math import inf
from random import randint

from buildings.JobBuilding import JobBuilding


class FarmBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        """
        Initializes a FarmBuilding instance.
        :param center_point: The center point of the building, or None to find the best spot.
        :param agent: The agent responsible for the building.
        :param orientation: The orientation of the building, default is "north".
        """
        width = random.randint(13, 22)
        depth = 11
        if orientation == "north" or orientation == "south":
            width = 11
            depth = random.randint(13, 22)

        super().__init__(center_point, agent, "Farm Building", orientation, width=width,
                         depth=depth, height=6)
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"], agent.simulation)
        self.place(center_point, agent.simulation)
        FarmBuilding.INSTANCE = self
        self.corner_block = "minecraft:oak_log"
        super().clear()

    def is_field(self,x,z):
        """
        Determines if the given coordinates (x, z) are part of the field area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of the field area, False otherwise.
        """
        if self.orientation == "north":
            return 0 < x < 5 and 1 < z < self.depth - 2
        elif self.orientation == "south":
            return 5 < x < self.width - 1 and 1 < z < self.depth - 2
        elif self.orientation == "east":
            return 0 < z < 5 and 1 < x < self.width - 2
        elif self.orientation == "west":
            return 5 < z < self.depth - 1 and 1 < x < self.width - 1
        return None

    def is_log(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of the log area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of the log area, False otherwise.
        """
        if self.orientation == "north":
            return x in [0,5,self.width - 2] and 0 < z < self.depth-1  or (z in [1,self.depth - 2] and 0 <= x < self.width-1)
        elif self.orientation == "south":
            return x in [1,5,self.width - 1] and 0 < z < self.depth-1 or (z in [1,self.depth - 2] and 0 <= x < self.width-1)
        elif self.orientation == "east":
            return z in [0,5,self.depth - 2] and 0 < x < self.width-1 or (x in [1,self.width - 2] and 0 <= x < self.width-1)
        elif self.orientation == "west":
            return z in [1,5,self.depth - 1] and 0 < x < self.width-1 or (x in [1,self.width - 1] and 0 <= x < self.width-1)
        return None

    def is_watterlogged_slab(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a waterlogged slab area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a waterlogged slab area, False otherwise.
        """
        if self.orientation in ["north", "south"]:
            return x == 5 and z in [6, self.depth - 7]
        return z == 5 and x in [6, self.depth - 7]

    def is_fence_gate(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a fence gate area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a fence gate area, False otherwise.
        """
        if self.orientation in ["north", "south"]:
            return x == 5 and z == self.depth // 2
        return z == 5 and x == self.width // 2

    def is_pillar(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a pillar area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a pillar area, False otherwise.
        """
        if self.orientation == "north":
            return x in [5, self.width - 2] and z in [1, self.depth - 2]
        elif self.orientation == "south":
            return x in [1, 5] and z in [1, self.depth - 2]
        elif self.orientation == "east":
            return z in [5, self.depth - 2] and x in [1, self.width - 2]
        elif self.orientation == "west":
            return z in [1, 5] and x in [1, self.width - 2]
        return None

    def is_wall(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a wall area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a wall area, False otherwise.
        """
        if self.orientation == "north":
            return x == self.width - 2 and 1 < z < self.depth - 2 or (z in [1, self.depth - 2] and 5 < x < self.width - 2)
        elif self.orientation == "south":
            return x == 2 and 1 < z < self.depth - 2 or (z in [1, self.depth - 2] and 5 < x < self.width - 2)
        elif self.orientation == "east":
            return z == self.depth - 2 and 1 < x < self.width - 2 or (x in [1, self.width - 2] and 5 < z < self.depth - 2)
        elif self.orientation == "west":
            return z == 2 and 1 < x < self.width - 2 or (x in [1, self.width - 2] and 5 < z < self.depth - 2)
        return None

    def is_window(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a window area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a window area, False otherwise.
        """
        if self.orientation == "north":
            return x == self.width - 4 and z == self.depth - 2
        elif self.orientation == "south":
            return x == 3 and z == 1
        elif self.orientation == "east":
            return z == self.depth - 4 and x == self.width - 2
        elif self.orientation == "west":
            return z == 3 and x == 1
        return None

    def is_door(self, x, z):
        """
        Determines if the given coordinates (x, z) are part of a door area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of a door area, False otherwise.
        """
        if self.orientation == "north":
            return x == self.width - 4 and z == 1
        elif self.orientation == "south":
            return x == 3 and z == self.depth - 2
        elif self.orientation == "east":
            return z == self.depth - 4 and x == 1
        elif self.orientation == "west":
            return z == 3 and x == self.width - 2
        return None

    def define_roof_outline(self):
        """
        Defines the roof outline based on the building's orientation and dimensions.
        :return: Blocks for the roof, upper roof blocks, mods, and upper mods.
        """
        rwidth = self.width // 2 + 1 if self.orientation in ["north", "south"] else self.depth // 2 + 1
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

    def is_storage_area(self,x,z):
        """
        Determines if the given coordinates (x, z) are part of the storage area.
        :param x: The x-coordinate.
        :param z: The z-coordinate.
        :return: True if the coordinates are part of the storage area, False otherwise.
        """
        if self.orientation == "south":
            return 2 <= x <= 3 and 2 <= z <= self.depth - 4
        elif self.orientation == "north":
            return self.width - 4 <= x <= self.width - 3 and 4 <= z <= self.depth - 3
        elif self.orientation == "west":
            return 2 <= z <= 3 and 2 <= x <= self.width - 4
        elif self.orientation == "east":
            return self.depth - 4 <= z <= self.depth - 3 and 2 <= x <= self.width - 4
        return None

    def build(self):
        """
        Builds the farm building by placing blocks in the matrix according to the defined structure.
        """
        if self.built:
            return
        crops = ["minecraft:wheat", "minecraft:carrots", "minecraft:potatoes", "minecraft:beetroots"]
        choice = random.choice(crops)
        for x in range(self.width):
            for z in range(self.depth):
                # Ground layer
                if self.is_field(x,z):
                    self.add_block_to_matrix(x, 0, z, f"minecraft:farmland[moisture={randint(1, 7)}]")
                    self.add_block_to_matrix(x, 1, z, f"{choice}[age={randint(1, 7)}]")
                elif self.is_log(x,z):
                    self.add_block_to_matrix(x, 0, z, "minecraft:oak_log")
                    self.add_block_to_matrix(x, 1, z, "minecraft:oak_fence")
                else:
                    self.add_block_to_matrix(x, 0, z, "minecraft:stone_bricks")

                # Walls, pillars, slabs, gates, windows and doors

                if self.is_watterlogged_slab(x, z):
                    self.add_block_to_matrix(x, 0, z, "minecraft:oak_slab[waterlogged=true,type=top]")
                elif self.is_fence_gate(x, z):
                    fgf = {"north":"east", "south":"west", "east":"north", "west":"south"}
                    self.add_block_to_matrix(x, 1, z, f"minecraft:oak_fence_gate[facing={fgf[self.orientation]}]")
                elif self.is_wall(x, z):
                    mod = 0
                    if self.orientation in ["north", "south"]:
                        mod = (2 < x < self.width - 3)
                    elif self.orientation in ["east", "west"]:
                        mod = (2 < z < self.depth - 3)
                    for y in range(1,3+mod):
                        self.add_block_to_matrix(x, y, z, "minecraft:oak_planks")
                elif self.is_pillar(x, z):
                    mod = 2 * (x==5) if self.orientation in ["north", "south"] else 2 * (z==5)
                    for y in range(3+mod):
                        self.add_block_to_matrix(x, y, z, "minecraft:oak_log")

                if self.is_window(x, z):
                    for y in range(2,4):
                        self.add_block_to_matrix(x, y, z, "minecraft:oak_fence")
                elif self.is_door(x, z):
                    pf = {"north":"south", "south":"north", "east":"west", "west":"east"}
                    self.add_block_to_matrix(x, 1, z, f"minecraft:oak_door[facing={pf[self.orientation]},half=lower]")
                    self.add_block_to_matrix(x, 2, z, f"minecraft:oak_door[facing={pf[self.orientation]},half=upper]")

                # Storage area
                if randint(1,32768)//3%2 == 0 and self.is_storage_area(x, z):
                    self.add_block_to_matrix(x, 1, z, 'barrel[facing=up]')

        # Roof
        rblocks, rublocks, mods, umods = self.define_roof_outline()
        if self.orientation in ["north", "east"]:
            mods.reverse()
            rblocks.reverse()
            rublocks.reverse()
            umods.reverse()
        for x in range(self.width):
            for z in range(self.depth):
                if self.orientation == "north" and self.width // 2 - 1 < x:
                    self.add_block_to_matrix(x, 2 + mods[x - self.width//2], z, rblocks[x - self.width//2])
                    if (x not in [0, self.width - 1] and not self.is_pillar(x, z)
                            and z in [0, 1, self.depth - 2, self.depth - 1]):
                        if z in [1, self.depth - 2] and rublocks[x - self.width//2] == "oak_planks" or z in [0, self.depth - 1]:
                            self.add_block_to_matrix(x, 2 + umods[x - self.width//2], z, rublocks[x - self.width//2])
                elif self.orientation == "east" and self.depth // 2 - 1 < z:
                    self.add_block_to_matrix(z, 2 + mods[z - self.width//2], x, rblocks[z - self.width//2])
                    if (z not in [0, self.width - 1] and not self.is_pillar(x, z)
                            and x in [0, 1, self.depth - 2, self.depth - 1]):
                        if x in [1, self.depth - 2] and rublocks[z - self.width//2] == "oak_planks" or x in [0, self.depth - 1]:
                            self.add_block_to_matrix(z, 2 + umods[z - self.width//2], x, rublocks[z - self.width//2])
                elif self.orientation == "south" and x < self.width // 2 + 1:
                    self.add_block_to_matrix(x, 2 + mods[x], z, rblocks[x])
                    if (x not in [0, self.width - 1] and not self.is_pillar(x, z)
                            and z in [0, 1, self.depth - 2, self.depth - 1]):
                        if z in [1, self.depth - 2] and rublocks[x] == "oak_planks" or z in [0, self.depth - 1]:
                            self.add_block_to_matrix(x, 2 + umods[x], z, rublocks[x])
                elif self.orientation == "west" and z < self.depth // 2 + 1:
                    self.add_block_to_matrix(z, 2 + mods[z], x, rblocks[z])
                    if (z not in [0, self.width - 1] and not self.is_pillar(x, z)
                            and x in [0, 1, self.depth - 2, self.depth - 1]):
                        if x in [1, self.depth - 2] and rublocks[z] == "oak_planks" or x in [0, self.depth - 1]:
                            self.add_block_to_matrix(z, 2 + umods[z], x, rublocks[z])

        # Add lighting
        coords = {
            "north": [(0,2,1,False),(0,2,self.depth-2,False),(7,3,3,True),(7,3,self.depth-4,True)],
            "south": [(self.width-1,2,1,False),(self.width-1,2,self.depth-2,False),(3,3,self.depth-4,True),(3,3,3,True)],
            "east": [(1,2,0,False)],
            "west": [(1,2,self.depth-1,False)],
        }

        for e in coords[self.orientation]:
            self.add_block_to_matrix(e[0], e[1], e[2], f"minecraft:lantern[hanging={str(e[3]).lower()}]")

        self.built = True
        return

    def best_spot(self, nbtry, simulation):
        """
        Finds the best spot for the farm building based on various criteria.
        :param nbtry: Number of attempts to find a suitable spot.
        :param simulation: The current simulation context.
        :return: The best spot as a tuple (x, z).
        """
        best_spot = None
        best_score = - inf
        t = 0

        while best_spot is None or t < nbtry:
            x = randint(0, simulation.heightmap.shape[0])
            z = randint(0, simulation.heightmap.shape[1])

            score = -simulation.lava[x - self.width // 2 - 1:x + self.width // 2 + 1,
                     z - self.depth // 2 - 1:z + self.depth // 2 + 1].sum()
            score += 0.5 * simulation.water[x - self.width:x + self.width, z - self.depth:z + self.depth].sum()
            score -= 10 * simulation.buildings[x - self.radius:x + self.radius,
                          z - self.radius:z + self.radius].sum().item()

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
        """
        Returns an instance of FarmBuilding, creating it if it does not already exist.
        :param center_point: The center point of the building, or None to find the best spot.
        :param agent: The agent responsible for the building.
        :param orientation: The orientation of the building, default is "north".
        :return: The instance of FarmBuilding.
        """
        if FarmBuilding.INSTANCE is None:
            return FarmBuilding(center_point, agent, orientation)
        return FarmBuilding.INSTANCE
