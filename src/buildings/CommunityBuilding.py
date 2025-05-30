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

    def build(self):
        for x in range(1, self.width - 1):
            for z in range(1, self.depth - 1):
                # Floor
                self.add_block_to_matrix(x, 0, z, 'oak_planks')

                # Walls
                if 1 <= x <= self.width - 2 and z in [1, self.depth - 2] \
                        or 1 <= z <= self.depth - 2 and x in [1, self.width - 2]:
                    for y in range(1, self.height - 3):
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


        # Interior
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
            counter = ["oak_slab[type=upper]"] * 3 + ["oak_planks"]
            if random.randint(0, 100) % 2 == 0:
                counter.reverse()
                #self.matrix[counterpos[self.orientation],self.depth-3:self.depth-8,1] = counter
                self.add_block_to_matrix(tablepos[self.orientation], 1, self.depth - 3, 'cartography_table')
            else:
                self.add_block_to_matrix(tablepos[self.orientation], 1, 2, 'cartography_table')
                #self.matrix[counterpos[self.orientation],2:6,1] = counter

        elif self.orientation in ['east', 'west']:
            zpos = {
                "east": [self.depth - 4, 5],
                "west": [3, 5]
            }
            for z in zpos[self.orientation]:
                for x in range(3, self.width - 3):
                    for y in range(3):
                        self.add_block_to_matrix(x, 1+y, z, 'bookshelf')

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

    # def make_gradual_roof(self, start_x, start_y, start_z, width, depth, inclination=2, orientation='north'):
    #     """
    #     Builds a straight inclined roof of oak_slabs along the depth (z axis) or width (x axis), depending on orientation.
    #     inclination: number of horizontal blocks per vertical step (higher = shallower roof)
    #     orientation: 'north'/'south' (roof slopes along +z), 'east'/'west' (roof slopes along +x)
    #     """
    #     if orientation in ['north', 'south']:
    #         # Roof slopes along z axis (depth)
    #         for dz in range(0, depth):
    #             y = start_y + dz // inclination
    #             z = start_z + dz if orientation == 'north' else start_z + depth - 1 - dz
    #             for x in range(start_x, start_x + width):
    #                 self.add_block_to_matrix(x, y, z, 'oak_slab')
    #     elif orientation in ['east', 'west']:
    #         # Roof slopes along x axis (width)
    #         for dx in range(0, width):
    #             y = start_y + dx // inclination
    #             x = start_x + dx if orientation == 'east' else start_x + width - 1 - dx
    #             for z in range(start_z, start_z + depth):
    #                 self.add_block_to_matrix(x, y, z, 'oak_slab')
    #     else:
    #         raise ValueError(f"Unknown orientation: {orientation}")

    @staticmethod
    def get_instance(center_point: tuple[int, int, int] | None, agent, orientation: str = "north"):
        if CommunityBuilding.INSTANCE is None:
            return CommunityBuilding(center_point, agent, orientation)
        return CommunityBuilding.INSTANCE
