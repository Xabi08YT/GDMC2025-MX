from Building import Building
from gdpc.vector_tools import ivec3
from gdpc import Block
from AbstractionLayer import AbstractionLayer

class Firecamp(Building):
    def __init__(self, center_point: ivec3):
        super().__init__(center_point, None, "Firecamp")

    def get_coords(self) -> ivec3:
        return self.center_point

    def build(self, abl: AbstractionLayer):
        chunk = abl.get_chunk(self.center_point.x, self.center_point.z)
        chunk.set_block(self.center_point.x, self.center_point.y, self.center_point.z, Block("minecraft:campfire"))
        plaza_material = Block("dirt_path")
        for dx in range(-1, 1):
            for dz in range(-1, 1):
                    x, z = self.center_point.x + dx, self.center_point.z + dz
                    if x == self.center_point.x and z == self.center_point.z:
                        continue
                    chunk = abl.get_chunk(x, z)
                    y = chunk.getGroundHeight(x, z)
                    chunk.set_block(x, y, z, plaza_material)
        chunk.to_file(path="generated")
        super().built()