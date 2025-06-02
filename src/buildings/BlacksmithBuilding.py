import random
from random import randint
from math import inf

from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz


class BlacksmithBuilding(JobBuilding):

    INSTANCE = None

    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        width = random.choice([9,11,13,15])
        depth = 9
        if orientation in ["east", "west"]:
            width, depth = depth, width

        super().__init__(center_point, agent, agent.name + "'s BlacksmithBuilding", orientation, width=width, height=7, depth=depth)
        if center_point is None:
            center_point = self.best_spot(agent.simulation.config["nbBuildingTries"],agent.simulation)
        self.place(center_point,agent.simulation)
        self.corners = [
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]
        BlacksmithBuilding.INSTANCE = self

    def build(self):
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