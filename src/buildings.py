import Agent
from gdpc.vector_tools import ivec3
from gdpc import Block, Editor
from utils import current_editor
import Job

class Building():
    def __init__(self, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False):
        self.built = built
        self.orientation = orientation
        self.center_point = center_point
        self.agent = agent

    def build(self):
        if self.center_point is None:
            return
        print(f"Building at x={self.center_point.x}, y={self.center_point.y}, z={self.center_point.z}!")

    def __repr__(self):
        return "Building(center_point={}, agent={})".format(self.center_point, self.agent)

    def __str__(self):
        return "Building at x={}, y={}, z={} owned by {}".format(self.center_point.x, self.center_point.y, self.center_point.z, self.agent.name)

class JobHouse(Building):
    def __init__(self, job: Job, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False):
        super().__init__(center_point, agent, orientation, built)
        self.job = job

class House(Building):
    def __init__(self, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False):
        super().__init__(center_point, agent, orientation, built)

    def build(self):
        if self.center_point is None:
            return
        super().build()
        center_x = self.center_point.x
        center_y = self.center_point.y
        center_z = self.center_point.z
        width, depth, height = 5, 5, 4
        half_w, half_d = width // 2, depth // 2
        bed_facing = {"north": "south", "south": "north", "east": "west", "west": "east"}[self.orientation]
        floor = Block("oak_planks")
        wall = Block("cobblestone")
        log = Block("oak_log")
        door = Block(f"oak_door[facing={bed_facing}]")
        torch = Block(f"wall_torch[facing={bed_facing}]")

        start_x = center_x - half_w
        start_z = center_z - half_d

        top_y = center_y + height
        for dx in range(width):
            for dz in range(depth):
                current_editor.placeBlock((start_x + dx, center_y, start_z + dz), floor)
                current_editor.placeBlock((start_x + dx, top_y, start_z + dz), floor)

        for dy in range(1, height):
            for dx in range(width):
                for dz in range(depth):
                    is_edge = dx == 0 or dx == width - 1 or dz == 0 or dz == depth - 1
                    is_corner = (dx in (0, width - 1)) and (dz in (0, depth - 1))
                    if is_corner:
                        current_editor.placeBlock((start_x + dx, center_y + dy, start_z + dz), log)
                    elif is_edge:
                        current_editor.placeBlock((start_x + dx, center_y + dy, start_z + dz), wall)

        door_x = center_x
        door_z = start_z + depth - 1
        door_x, door_z = center_x, start_z
        torch_pos = (door_x, center_y + 3, door_z + 1)
        bed_pos = (center_x - 1, center_y + 1, center_z)
        if self.orientation == "south":
            door_x, door_z = center_x, start_z + depth - 1
            torch_pos = (door_x, center_y + 3, door_z - 1)
        elif self.orientation == "east":
            door_x, door_z = start_x + width - 1, center_z
            torch_pos = (door_x - 1, center_y + 3, door_z)
            bed_pos = (center_x, center_y + 1, center_z - 1)
        elif self.orientation == "west":
            door_x, door_z = start_x, center_z
            torch_pos = (door_x + 1, center_y + 3, door_z)
            bed_pos = (center_x, center_y + 1, center_z - 1)

        current_editor.placeBlock((door_x, center_y + 1, door_z), door)
        current_editor.placeBlock(torch_pos, torch)
        current_editor.placeBlock(bed_pos, Block(f"red_bed[facing={bed_facing}]"))

        self.built = True