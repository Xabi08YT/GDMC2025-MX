from buildings.Building import Building
from gdpc.vector_tools import ivec3
from gdpc import Block, interface
from abstractionLayer.AbstractionLayer import AbstractionLayer
import random

class Firecamp(Building):
    def __init__(self, buildArea: interface.Box, abl: AbstractionLayer):
        self.abl = abl
        super().__init__(self.get_center_point(buildArea), None, "Firecamp")


    def get_coords(self) -> ivec3:
        return self.center_point

    def get_center_point(self, buildArea: interface.Box) -> ivec3:
        min_x, min_y, min_z = buildArea.begin
        max_x, max_y, max_z = buildArea.end

        best_spot = None
        best_score = float('-inf')
        num_candidates = 15

        temp_abl = self.abl

        for _ in range(num_candidates):
            x = random.randint(min_x, max_x - 1)
            z = random.randint(min_z, max_z - 1)

            chunk = temp_abl.get_chunk(x, z)
            y = chunk.getGroundHeight(x, z)

            score = 0

            block = chunk.get_block(x, y, z)
            if block and block.id in ["minecraft:water", "minecraft:flowing_water"]:
                score -= .50

            flatness = 0
            neighbors = 0
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        ny = chunk.getGroundHeight(nx, nz)
                        flatness -= abs(y - ny)
                        neighbors += 1

            if neighbors > 0:
                score += flatness / neighbors * 0.5

            for dx in range(-3, 4):
                for dz in range(-3, 4):
                    nx, nz = x + dx, z + dz
                    if min_x <= nx < max_x and min_z <= nz < max_z:
                        ny = chunk.getGroundHeight(nx, nz)
                        block = chunk.get_block(nx, ny, nz)
                        if block and block.id in ["minecraft:lava", "minecraft:flowing_lava"]:
                            score -= 100

            if score > best_score:
                best_score = score
                best_spot = (x, y, z)

        if best_spot is None:
            center_x = (min_x + max_x) // 2
            center_z = (min_z + max_z) // 2
            chunk = temp_abl.get_chunk(center_x, center_z)
            center_y = chunk.getGroundHeight(center_x, center_z)
            best_spot = (center_x, center_y, center_z)

        return ivec3(best_spot[0], best_spot[1], best_spot[2])

    def build(self, abl: AbstractionLayer):
        chunk = abl.get_chunk(self.center_point.x, self.center_point.z)
        chunk.set_block(self.center_point.x, self.center_point.y+1, self.center_point.z, Block("minecraft:campfire"))
        plaza_floor = Block("dirt_path")
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                x, z = self.center_point.x + dx, self.center_point.z + dz
                if x == self.center_point.x and z == self.center_point.z:
                    continue
                y = chunk.getGroundHeight(x, z)
                chunk.set_block(x, y, z, plaza_floor)
                if random.randint(0, 10) < 5:
                    extra_x, extra_z = random.choice([-1, 1]), random.choice([-1, 1])
                    extra_y = chunk.getGroundHeight(x + extra_x, z + extra_z)
                    chunk.set_block(x + extra_x, extra_y, z + extra_z, plaza_floor)
        chunk.to_file(path="generated", filename="Firecamp.json")
        super().built()