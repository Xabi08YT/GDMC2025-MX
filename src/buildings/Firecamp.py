from buildings.Building import Building
from gdpc.vector_tools import ivec3
import random

class Firecamp(Building):
    def __init__(self, simulation):
        self.simulation = simulation
        super().__init__(self.get_best_location(), None, "Firecamp", width=5, height=5, depth=2)

    def get_coords(self) -> ivec3:
        return self.center_point

    def get_best_location(self) -> ivec3:
        begin_x, begin_y, begin_z = self.simulation.abl.buildArea.begin
        end_x, end_y, end_z = self.simulation.abl.buildArea.end

        best_spot = None
        best_score = float('-inf')
        num_candidates = 15

        temp_abl = self.simulation.abl
        height_map = temp_abl.get_height_map_excluding("air")

        min_x = 0
        max_x = len(height_map[0])
        min_z = 0
        max_z = len(height_map[1])

        for _ in range(num_candidates):
            x = random.randint(min_x, max_x - 1)
            z = random.randint(min_z, max_z - 1)

            y = height_map[x][z]

            score = 0

            if self.simulation.water[x][z]:
                score -= .50

            flatness = 0
            neighbors = 0
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        ny = height_map[nx][nz]
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
            center_x = (min_x + max_x - 1) // 2
            center_z = (min_z + max_z - 1) // 2
            center_y = height_map[center_x][center_z]
            best_spot = (center_x, center_y, center_z)

        return best_spot[0], best_spot[1], best_spot[2]

    def build(self):
        super().add_block_to_matrix(3, 1, 3, self.simulation.params["villageCenterBlock"])
        plaza_floor = self.simulation.params["centerPlazaFloor"]
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                rel_x, rel_z = 3 + dx, 3 + dz
                if rel_x == 3 and rel_z == 3:
                    continue
                abs_x, abs_z = self.center_point[0] + dx, self.center_point[2] + dz
                y = self.simulation.abl.get_height_map_excluding("air")[abs_x][abs_z] - self.center_point[1] + 1
                super().add_block_to_matrix(rel_x, y, rel_z, plaza_floor)
                if random.randint(0, 10) < 5:
                    extra_dx, extra_dz = random.choice([-1, 1]), random.choice([-1, 1])
                    rel_extra_x, rel_extra_z = rel_x + extra_dx, rel_z + extra_dz
                    abs_extra_x, abs_extra_z = abs_x + extra_dx, abs_z + extra_dz
                    y_extra = self.simulation.abl.get_height_map_excluding("air")[abs_extra_x][abs_extra_z] - \
                              self.center_point[1] + 1
                    super().add_block_to_matrix(rel_extra_x, y_extra, rel_extra_z, plaza_floor)
        super().built()