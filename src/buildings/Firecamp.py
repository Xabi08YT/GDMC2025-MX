from buildings.Building import Building
from gdpc.vector_tools import ivec3
import random

class Firecamp(Building):
    def __init__(self, simulation):
        self.simulation = simulation
        super().__init__(None, None, "Firecamp", width=5, height=2, depth=5)
        self.place(self.get_best_location(),self.simulation)

    def get_coords(self) -> ivec3:
        return self.center_point

    def get_best_location(self) -> tuple[int,int]:
        best_spot = None
        best_score = float('-inf')

        temp_abl = self.simulation.abl
        height_map = temp_abl.get_height_map_excluding("#air")

        min_x = self.width // 2 + 1
        max_x = self.simulation.heightmap.shape[0] - self.width//2-1
        min_z = self.depth // 2 + 1
        max_z = self.simulation.heightmap.shape[1] - self.depth//2-1

        while best_spot is None:
            x = random.randint(min_x, max_x - 1)
            z = random.randint(min_z, max_z - 1)
            y = self.simulation.heightmap[x][z]

            score = 0

            tmp = self.simulation.water[x-self.width//2-1:x+self.width//2+1,z-self.depth//2-1:z+self.depth//2+1]
            print(tmp)
            if True in tmp:
                continue

            """water_nearby = False
            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        if self.simulation.water[nx][nz]:
                            water_nearby = True
                            break
                if water_nearby:
                    break

            if water_nearby:
                continue"""

            print(x,z)
            subhmap = self.simulation.heightmap[x-self.width//2+1:x+self.width//2+1,z-self.depth//2+1:z+self.depth//2+1]
            score -= subhmap.max().item() - subhmap.min().item()
            print(score)

            if score > best_score:
                best_score = score
                best_spot = (x, y, z)

        return best_spot

    def build(self):
        super().add_block_to_matrix(3, 1, 3, self.simulation.params["villageCenterBlock"])
        plaza_floor = self.simulation.params["centerPlazaFloor"]
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                rel_x, rel_z = 3 + dx, 3 + dz
                if rel_x == 3 and rel_z == 3:
                    continue
                abs_x, abs_z = self.center_point[0] + dx, self.center_point[1].item() + dz
                y = 0
                super().add_block_to_matrix(rel_x, y, rel_z, plaza_floor)
                if random.randint(0, 10) < 5 and False:
                    extra_dx, extra_dz = random.choice([-1, 1]), random.choice([-1, 1])
                    rel_extra_x, rel_extra_z = rel_x + extra_dx, rel_z + extra_dz
                    abs_extra_x, abs_extra_z = abs_x + extra_dx, abs_z + extra_dz
                    y_extra = self.simulation.abl.get_height_map_excluding("air")[abs_extra_x][abs_extra_z] - \
                              self.center_point[1] + 1
                    super().add_block_to_matrix(rel_extra_x, y_extra % 2, rel_extra_z % 5, plaza_floor)
        super().built()