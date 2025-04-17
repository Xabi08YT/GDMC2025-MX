from numpy import array as nparray

class Map:

    def __init__(self, data):
        self.mcmap = nparray(data)

    def get_block(self, x: int, y: int, z: int):
        return self.mcmap[x, y, z]

    def get_blocks(self, x1: int, y1: int, z1: int, x2: int, y2: int, z2: int):
        return self.mcmap[(x1, y1, z1), (x2, y2, z2)]

    def format_MinecraftMap(self):
        pass