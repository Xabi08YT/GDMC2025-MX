from typing import Tuple
from buildings.Building import Building

class Bridge(Building):

    nb_bridge = 0
    def __init__(self, start_point: Tuple[int, int], end_point: Tuple[int, int], agent=None, orientation: str = "south", built: bool = False, folder="generated"):
        center_point = ((start_point[0] + end_point[0]) // 2, (start_point[1] + end_point[1]) // 2)
        Bridge.nb_bridge += 1
        self.nb = Bridge.nb_bridge
        self.start_point = start_point
        self.end_point = end_point
        self.agent = agent
        self.width = 3
        self.depth = max(abs(end_point[0] - start_point[0]), abs(end_point[1] - start_point[1])) + 1
        self.corner_block = "minecraft:oak_log"
        self.reverse_orientation = {"north": "south", "south": "north", "east": "west", "west": "east"}[orientation]
        super().__init__(center_point, agent, "Bridge_" + str(Bridge.nb_bridge), orientation, built, folder, width=self.width, height=1, depth=self.depth)

    def build(self):
        for dx in range(self.width):
            for dz in range(self.depth):
                if dz == 0 or dz == self.depth - 1:
                    orientation_param = self.reverse_orientation if dz == 0 else self.orientation
                    self.add_block_to_matrix(dx, 0, dz, f"minecraft:oak_stairs[half=top,facing={orientation_param}]")
                else:
                    self.add_block_to_matrix(dx, 0, dz, "minecraft:oak_slab[type=top]")
        super().built()
