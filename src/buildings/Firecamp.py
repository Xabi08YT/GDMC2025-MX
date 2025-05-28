from buildings.Building import Building
from math import inf
from gdpc.vector_tools import ivec3
import random

class Firecamp(Building):
    def __init__(self, simulation):
        self.simulation = simulation
        super().__init__(None, None, "Firecamp", width=5, height=2, depth=5, bupdates=False)
        fx,fy,fz = self.get_best_location()
        self.place((fx,fz),self.simulation)

    def get_coords(self) -> ivec3:
        return self.center_point

    def get_best_location(self) -> tuple[int,int,int]:
        best_spot = None
        best_score = -inf

        min_x = self.width // 2 + 1
        max_x = self.simulation.heightmap.shape[0] - self.width//2-1
        min_z = self.depth // 2 + 1
        max_z = self.simulation.heightmap.shape[1] - self.depth//2-1
        try_number = self.simulation.config["nbBuildingTries"]

        while best_spot is None or try_number < 20:
            x = random.randint(min_x, max_x - 1)
            z = random.randint(min_z, max_z - 1)
            y = self.simulation.heightmap[x][z]
            score = 0

            tmp = self.simulation.walkable[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1:z+self.depth//2+1]
            if False in tmp:
                continue

            subhmap = self.simulation.heightmap[x-self.width//2+1:x+self.width//2+1,z-self.depth//2+1:z+self.depth//2+1]
            score -= subhmap.max().item() - subhmap.min().item()

            if score > best_score:
                best_score = score
                best_spot = (x, y, z)

            try_number += 1

        return best_spot

    def build(self):
        plaza_floor = self.simulation.params["centerPlazaFloor"]
        y = 0
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                rel_x, rel_z = 2 + dx, 2 + dz
                super().add_block_to_matrix(rel_x, 1, rel_z, "minecraft:air")
                super().add_block_to_matrix(rel_x, y, rel_z, plaza_floor)
                if random.randint(0, 10) < 5:
                    extra_dx, extra_dz = random.choice([-1, 1]), random.choice([-1, 1])
                    super().add_block_to_matrix(min(rel_x + extra_dx,4), y, min(rel_z + extra_dz,4), plaza_floor)
        super().add_block_to_matrix(2, 1, 2, self.simulation.params["villageCenterBlock"])
        super().add_block_to_matrix(2, 0, 2, "minecraft:hay_block")
        super().built()