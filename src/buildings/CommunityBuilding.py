from math import inf
from random import randint
import random

from buildings.JobBuilding import JobBuilding
from pyglm.glm import orientation

from utils.math_methods import distance_xz


class CommunityBuilding(JobBuilding):
    INSTANCE = None

    def __init__(self, center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        width = 11
        depth = random.choice([13, 15, 17])
        if orientation in ['east', 'west']:
            width = random.choice([13, 15, 17])
            depth = 11
        super().__init__(center_point, agent, agent.name + "'s CommunityBuilding", orientation, width=width, height=7,
                         depth=depth)

        print(self.matrix.shape)
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"], agent.simulation)
        self.place(center_point, agent.simulation)
        self.corners = [
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]

        CommunityBuilding.INSTANCE = self

    def need_log(self, x, z):
        """
        Returns True if the block at (x,z) needs to be logged, False otherwise.
        """
        return (x in [1, 5, self.width - 2] and z in [1, self.depth - 2] and self.orientation in ["north", "south"]) \
            or (z in [1, 5, self.depth - 2] and x in [1, self.width - 2] and self.orientation in ['east', 'west'])

    def need_window(self, x, z):
        """
        Returns True if the block at (x,z) needs to be a window, False otherwise.
        """
        return (((x in [3, self.width - 4] and z in [1, self.depth - 2])
                 or (x in [1, self.width - 2] and z in [3, self.depth - 4])
                 and self.orientation in ["north", "south"])
                or (z in [3, self.depth - 4]
                    and x in [1, self.width - 2]
                    or (z in [1, self.depth - 2]
                        and x in [3, self.width - 4])
                    and self.orientation in ['east', 'west']))

    def need_big_window(self, x, z):
        conditions = {
            "north": (x == 1 and 4 < z < self.depth - 5),
            "south": (x == self.depth - 2 and 4 < z < self.depth - 5),
            "east": (z == 1 and 4 < x < self.depth - 5),
            "west": (z == self.depth - 2 and 4 < x < self.depth - 5)
        }
        return conditions[self.orientation]

    def is_door(self, x, z):
        conditions = {
            "south": (x == 1 and z == self.depth//2),
            "north": (x == self.width - 2 and z == self.depth//2),
            "west": (z == 1 and x == self.depth//2),
            "east": (z == self.depth - 2 and x == self.depth//2)
        }
        return conditions[self.orientation]

    def get_door_orientation(self):
        orientations = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }
        return orientations[self.orientation]

    def define_roof_outline(self):
        rwidth = self.width // 2 if self.orientation in ["north", "south"] else self.depth // 2
        rblocks = []
        rublocks = []
        mods = []
        umods = []
        for i in range(rwidth):
            mods.append((i+1)//2)
            umods.append(i//2)
            if i % 2 == 0:
                rblocks.append("oak_slab[type=top]")
                if i != 0:
                    rublocks.append("oak_planks")
            else:
                rblocks.append("oak_slab[type=bottom]")
                rublocks.append("oak_slab[type=top]")

        # For symmetry, we reverse the lists
        tmprblocks = rblocks.copy()
        tmprblocks.reverse()
        tmprublocks = rublocks.copy()
        tmprublocks.reverse()
        tmpmods = mods.copy()
        tmpmods.reverse()
        tmpumods = umods.copy()
        tmpumods.reverse()

        # Adding center row
        if rblocks[-1] == "oak_slab[type=top]":
            rblocks.append("oak_slab[type=bottom]")
            rublocks.append("oak_slab[type=top]")
            mods.append(mods[-1]+1)
            umods.append(umods[-1])
        else:
            rblocks.append("oak_slab[type=top]")
            rublocks.append("oak_planks")
            mods.append(mods[-1])
            umods.append(umods[-1]+1)
        # Adding the reversed lists
        rublocks += tmprublocks
        rblocks += tmprblocks
        mods += tmpmods
        umods += tmpumods
        return rblocks, rublocks,mods, umods

    def build(self):
        if self.built:
            return
        for x in range(1, self.width - 1):
            for z in range(1, self.depth - 1):
                # Floor
                self.add_block_to_matrix(x, 0, z, 'oak_planks')

                # Walls
                if 1 <= x <= self.width - 2 and z in [1, self.depth - 2] \
                        or 1 <= z <= self.depth - 2 and x in [1, self.width - 2]:
                    mod =  (2 < x < self.width - 3 and self.orientation in ["north", "south"] or (2 < z < self.width - 3 and self.orientation in ['east', 'west']))
                    for y in range(1, self.height - 3 + mod):
                        self.add_block_to_matrix(x, y, z, 'oak_planks')

                # Pillars
                if self.need_log(x, z):
                    mod = 2 * (x == 5 and self.orientation in ["north", "south"] or (z == 5 and self.orientation in ['east', 'west']))
                    for y in range(1, self.height - 3 + mod):
                        self.add_block_to_matrix(x, y, z, 'oak_log')

                # Windows
                elif self.need_window(x, z):
                    for y in range(2):
                        self.add_block_to_matrix(x, 2 + y, z, 'oak_fence')

                # Big window
                elif self.need_big_window(x, z):
                    for y in range(2):
                        self.add_block_to_matrix(x, 2 + y, z, 'oak_fence')

                # Door
                elif self.is_door(x, z):
                    self.add_block_to_matrix(x, 1, z, f'oak_door[facing={self.get_door_orientation()}]')
                    self.add_block_to_matrix(x, 2, z, f'oak_door[half=upper,facing={self.get_door_orientation()}]')

        # Roof
        rblocks, rublocks, mods, umods = self.define_roof_outline()
        if self.orientation in ["north", "south"]:
            for x in range(self.width):
                for z in range(self.depth):
                    self.add_block_to_matrix(x, self.height - 4 + mods[x], z, rblocks[x])
                    if (x not in [0,self.width - 1] and not self.need_log(x, z)
                            and z in [0,1, self.depth - 2,self.depth - 1]):
                        if z in [1, self.depth - 2] and rublocks[x-1] == "oak_planks" or z in [0,self.depth - 1]:
                            self.add_block_to_matrix(x, self.height - 4 + umods[x], z, rublocks[x-1])
        else:
            for z in range(self.depth):
                for x in range(self.width):
                    self.add_block_to_matrix(z, self.height - 4 + mods[z], x, rblocks[z])
                    if (z not in [0,self.width - 1] and not self.need_log(z, x)
                            and x in [0,1, self.depth - 2,self.depth - 1]):
                        if x in [1, self.depth - 2] and rublocks[z-1] == "oak_planks" or x in [0,self.depth - 1]:
                            self.add_block_to_matrix(z, self.height - 4 + umods[z], x, rublocks[z-1])


        # Interior
        counter = ["minecraft:oak_slab[type=top]"] * 3 + ["oak_planks"]
        if self.orientation in ["north", "south"]:
            xpos = {
                "north": [self.width - 4, 5],
                "south": [3, 5]
            }
            counterpos = {
                "north": 3,
                "south": self.width - 4,
            }
            tablepos = {
                "north": 2,
                "south": self.width - 3,
            }
            for x in xpos[self.orientation]:
                for z in range(3, self.depth - 3):
                    for y in range(3):
                        self.add_block_to_matrix(x, 1+y, z, 'bookshelf')

            if random.randint(0, 100) % 2 == 0:
                self.add_block_to_matrix(tablepos[self.orientation], 1, self.depth - 3, 'cartography_table')
                for i,b in enumerate(counter):
                    self.add_block_to_matrix(counterpos[self.orientation],1, self.depth - 3 - i, b)

            else:
                self.add_block_to_matrix(tablepos[self.orientation], 1, 2, 'cartography_table')
                for i,b in enumerate(counter):
                    self.add_block_to_matrix(counterpos[self.orientation],1, 2 + i, b)

                self.add_block_to_matrix(5, 5, 3, 'lantern[hanging=true]')
                self.add_block_to_matrix(5, 5, self.depth-4, 'lantern[hanging=true]')


        elif self.orientation in ['east', 'west']:
            zpos = {
                "east": [self.depth - 4, 5],
                "west": [3, 5]
            },
            counterpos = {
                "east": 3,
                "west": self.depth - 4,
            }
            tablepos = {
                "east": 2,
                "west": self.depth - 3,
            }
            for z in zpos[self.orientation]:
                for x in range(3, self.width - 3):
                    for y in range(3):
                        self.add_block_to_matrix(x, 1+y, z, 'bookshelf')

            if random.randint(0, 100) % 2 == 0:
                self.add_block_to_matrix(self.depth - 3, 1, tablepos[self.orientation], 'cartography_table')
                for i,b in enumerate(counter):
                    self.add_block_to_matrix(self.depth - 3 - i,1, counterpos[self.orientation], b)

            else:
                self.add_block_to_matrix(2, 1, tablepos[self.orientation], 'cartography_table')
                for i,b in enumerate(counter):
                    self.add_block_to_matrix( 2 + i,1,counterpos[self.orientation], b)

            self.add_block_to_matrix(3, 5, 5, 'lantern[hanging=true]')
            self.add_block_to_matrix(self.width - 4,5,5, 'lantern[hanging=true]')

        self.built = True
        return

    def best_spot(self, nbtry, simulation):
        best_spot = None
        best_score = - inf
        t = 0

        while best_spot is None or t < nbtry:
            x = randint(0, simulation.heightmap.shape[0])
            z = randint(0, simulation.heightmap.shape[1])

            score = simulation.walkable[x - self.width // 2 - 1:x + self.width // 2 + 1,
                    z - self.depth // 2 - 1:z + self.depth // 2 + 1].sum()
            score += distance_xz(x, simulation.firecamp_coords[0], z, simulation.firecamp_coords[1])

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
        if CommunityBuilding.INSTANCE is None:
            return CommunityBuilding(center_point, agent, orientation)
        return CommunityBuilding.INSTANCE
