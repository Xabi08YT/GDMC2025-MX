import Agent
from gdpc.vector_tools import ivec3
from gdpc import Block, Editor
import Job

class Building():
    def __init__(self, center_point: ivec3 | None, agent: Agent, existing: bool = False):
        self.existing = existing
        self.center_point = center_point
        self.agent = agent

    def build(self):
        print(f"Building at x={self.center_point.x}, y={self.center_point.y}, z={self.center_point.z}!")

class JobHouse():
    def __init__(self, building: Building, job: Job):
        self.building = building
        self.job = job

class House():
    def __init__(self, building: Building):
        self.building = building

    def build_small_house_centered(self, editor: Editor, center_x: int, center_y: int, center_z: int):
        # A refaire
        width, depth, height = 5, 5, 4
        half_w, half_d = width // 2, depth // 2

        floor = Block("oak_planks")
        wall = Block("cobblestone")
        log = Block("oak_log")
        roof = Block("oak_stairs[facing=south,half=top]")
        door_bottom = Block("oak_door[facing=south,half=lower]")
        door_top = Block("oak_door[facing=south,half=upper]")
        torch = Block("torch")
        bed_head = Block("red_bed[facing=south,part=head]")
        bed_foot = Block("red_bed[facing=south,part=foot]")

        start_x = center_x - half_w
        start_z = center_z - half_d

        for dx in range(width):
            for dz in range(depth):
                editor.placeBlock((start_x + dx, center_y, start_z + dz), floor)

        for dy in range(1, height):
            for dx in range(width):
                for dz in range(depth):
                    is_edge = dx == 0 or dx == width - 1 or dz == 0 or dz == depth - 1
                    is_corner = (dx in (0, width - 1)) and (dz in (0, depth - 1))
                    if is_corner:
                        editor.placeBlock((start_x + dx, center_y + dy, start_z + dz), log)
                    elif is_edge:
                        editor.placeBlock((start_x + dx, center_y + dy, start_z + dz), wall)

        for dx in range(-1, width + 1):
            for dz in range(-1, depth + 1):
                editor.placeBlock((start_x + dx, center_y + height, start_z + dz), roof)

        door_x = center_x
        door_z = start_z + depth - 1
        editor.placeBlock((door_x, center_y + 1, door_z), door_bottom)
        editor.placeBlock((door_x, center_y + 2, door_z), door_top)

        editor.placeBlock((door_x, center_y + 3, door_z - 1), torch)

        editor.placeBlock((center_x - 1, center_y + 1, center_z - 1), bed_head)
        editor.placeBlock((center_x - 1, center_y + 1, center_z), bed_foot)