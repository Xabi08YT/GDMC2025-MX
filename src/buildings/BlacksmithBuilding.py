from random import randint
from math import inf

from buildings.JobBuilding import JobBuilding

from utils.math_methods import distance_xz


class BlacksmithBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s BlacksmithBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0],
                                        self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]],
                                        self.center_point[2], "minecraft:obsidian")
        super().check_built()

    def place(self, nbtry, simulation):
        best_spot = None
        best_score = - inf
        t = 0

        while not best_spot is None or t < nbtry:
            x = randint(0,self.heightmap.shape[0])
            z = randint(0,self.heightmap.shape[1])

            score = -simulation.water[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1,z+self.depth//2+1].sum()
            score -= distance_xz(x,simulation.firecamp_coords[0],z,simulation.firecamp_coords[1])
            score += 0.5 * simulation.lava[x-self.width:x+self.width,z-self.depth,z+self.depth]

            if simulation.walkable[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1,z+self.depth//2+1].count().item() < self.width * self.depth:
                continue

            if score > best_score:
                best_score = score
                best_spot = (x,z)

        return best_spot