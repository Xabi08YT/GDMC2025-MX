from buildings.Building import Building
from gdpc.vector_tools import ivec3
import random

class Firecamp(Building):
    def __init__(self, simulation):
        self.simulation = simulation
        super().__init__(self.get_best_location(), None, "Firecamp")

    def get_coords(self) -> ivec3:
        return self.center_point

    def get_best_location(self) -> ivec3:
        min_x, min_y, min_z = self.simulation.abl.buildArea.begin
        max_x, max_y, max_z = self.simulation.abl.buildArea.end

        best_spot = None
        best_score = float('-inf')
        num_candidates = 15

        temp_abl = self.simulation.abl

        for _ in range(num_candidates):
            x = random.randint(min_x, max_x - 1)
            z = random.randint(min_z, max_z - 1)

            y = temp_abl.get_height_map_excluding("air")[x][z]

            score = 0

            if self.simulation.water[x][z]:
                score -= .50

            flatness = 0
            neighbors = 0
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        ny = temp_abl.get_height_map_excluding("air")[nx][nz]
                        flatness -= abs(y - ny)
                        neighbors += 1

            if neighbors > 0:
                score += flatness / neighbors * 0.5

            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        if self.simulation.lava[nx][nz]:
                            score -= 100

            if score > best_score:
                best_score = score
                best_spot = (x, y, z)

        if best_spot is None:
            center_x = (min_x + max_x) // 2
            center_z = (min_z + max_z) // 2
            center_y = self.simulation.abl.get_height_map_excluding("air")[center_x][center_z]
            best_spot = (center_x, center_y, center_z)

        return ivec3(best_spot[0], best_spot[1], best_spot[2])

    def build(self):
        super().add_block_to_matrix(self.center_point[0], self.center_point[1]+1, self.center_point[1], self.simulation.params["villageCenterBlock"])
        plaza_floor = self.simulation.params["centerPlazaFloor"]
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                x, z = self.center_point[0] + dx, self.center_point[1] + dz
                if x == self.center_point[0] and z == self.center_point[1]:
                    continue
                super().add_block_to_matrix(x, self.simulation.abl.get_height_map_excluding("air")[x][z], z, plaza_floor)
                if random.randint(0, 10) < 5:
                    extra_x, extra_z = random.choice([-1, 1]), random.choice([-1, 1])
                    super().add_block_to_matrix(x + extra_x, self.simulation.abl.get_height_map_excluding("air")[extra_x][extra_z], z + extra_z, plaza_floor)
        super().built()