import Building
from gdpc.vector_tools import ivec3
from gdpc import Block

class Firecamp(Building):
    def __init__(self, center_point: ivec3 | None):
        super().__init__(center_point, None, "Firecamp")

    def get_coords(self):
        return self.center_point

    def build(self):
        self.chunk.set_block(self.center_point[0], self.center_point[1], self.center_point[2], Block("campfire"))
