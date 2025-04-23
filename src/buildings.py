import Agent
from gdpc.vector_tools import ivec3
from gdpc import Block, Editor
import utils
import Job
from chunk import set_block


class Building:
    def __init__(self, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False):
        self.built = built
        self.orientation = orientation
        self.center_point = center_point
        self.agent = agent

    def build(self):
        if self.built is not True:
            return
        print(f"Building at x={self.center_point.x}, y={self.center_point.y}, z={self.center_point.z} done!")

    def set_orientation_towards_center(self, agent: Agent = None):
        if agent is None:
            agent = self.agent

        if self.center_point is None:
            return

        dx = self.center_point.x - agent.center_village[0]
        dz = self.center_point.z - agent.center_village[1]

        if abs(dx) > abs(dz):
            if dx > 0:
                self.orientation = "west"
            else:
                self.orientation = "east"
        else:
            if dz > 0:
                self.orientation = "north"
            else:
                self.orientation = "south"

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
        center_x = self.center_point.x
        center_y = self.center_point.y
        center_z = self.center_point.z
        width, depth, height = 5, 5, 4
        half_w, half_d = width // 2, depth // 2
        orientation = self.orientation
        bed_facing = {"north": "south", "south": "north", "east": "west", "west": "east"}[orientation]
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
                set_block(start_x + dx, center_y, start_z + dz,utils.current_editor.getBuildArea(), floor)
                set_block(start_x + dx, top_y, start_z + dz,utils.current_editor.getBuildArea(), floor)

        for dy in range(1, height):
            for dx in range(width):
                for dz in range(depth):
                    is_edge = dx == 0 or dx == width - 1 or dz == 0 or dz == depth - 1
                    is_corner = (dx in (0, width - 1)) and (dz in (0, depth - 1))
                    if is_corner:
                        set_block(start_x + dx, top_y, start_z + dz, utils.current_editor.getBuildArea(), log)
                    elif is_edge:
                        set_block(start_x + dx, top_y, start_z + dz, utils.current_editor.getBuildArea(), wall)

        door_x, door_z = center_x, start_z
        torch_pos = (door_x, center_y + 3, door_z + 1)
        bed_pos = (center_x - 1, center_y + 1, center_z)

        if orientation == "south":
            door_x, door_z = center_x, start_z + depth - 1
            torch_pos = (door_x, center_y + 3, door_z - 1)
        elif orientation == "east":
            door_x, door_z = start_x + width - 1, center_z
            torch_pos = (door_x - 1, center_y + 3, door_z)
            bed_pos = (center_x, center_y + 1, center_z - 1)
        elif orientation == "west":
            door_x, door_z = start_x, center_z
            torch_pos = (door_x + 1, center_y + 3, door_z)
            bed_pos = (center_x, center_y + 1, center_z - 1)

        utils.current_editor.placeBlock((door_x, center_y + 1, door_z), door)
        set_block(door_x,center_y,door_z, utils.current_editor.getBuildArea(), door)
        set_block(torch_pos[0], torch_pos[1], torch_pos[2], utils.current_editor.getBuildArea(), torch)
        set_block(bed_pos[0], bed_pos[1], bed_pos[2], utils.current_editor.getBuildArea(), Block(f"red_bed[facing={bed_facing}]"))


        self.built = True
        super().build()

    def get_door_position(self):
        if self.center_point is None:
            return None

        center_x = self.center_point.x
        center_y = self.center_point.y
        center_z = self.center_point.z
        width, depth = 5, 5
        half_w, half_d = width // 2, depth // 2

        start_x = center_x - half_w
        start_z = center_z - half_d

        door_x, door_z = center_x, start_z

        if self.orientation == "south":
            door_x, door_z = center_x, start_z + depth - 1
        elif self.orientation == "east":
            door_x, door_z = start_x + width - 1, center_z
        elif self.orientation == "west":
            door_x, door_z = start_x, center_z

        return (door_x, center_y, door_z)