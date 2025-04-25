import Agent
from gdpc.vector_tools import ivec3
from gdpc import Block
from Building import Building


class House(Building):
    def __init__(self, center_point: ivec3 | None, agent: Agent, name:str, orientation: str = "south", built: bool = False, folder="generated"):
        super().__init__(center_point, agent, name, orientation, built, folder)

    def build(self):
        if self.center_point is None:
            return
        center_x = self.center_point[0]
        center_y = self.center_point[1]
        center_z = self.center_point[2]
        width, depth, height = 5, 5, 4
        half_w, half_d = width // 2, depth // 2
        orientation = self.orientation
        bed_facing = {"north": "south", "south": "north", "east": "west", "west": "east"}[orientation]
        relatives = {"north": (0,-1), "south": (0,1), "east": (1,0), "west": (-1,0)}
        floor = Block("oak_planks")
        wall = Block("cobblestone")
        log = Block("oak_log")
        doorlower = Block(f"oak_door[facing={bed_facing}]")
        doorupper = Block(f"oak_door[facing={bed_facing},half=upper]")
        torch = Block(f"wall_torch[facing={bed_facing}]")

        start_x = center_x - half_w
        start_z = center_z - half_d

        top_y = center_y + height
        for dx in range(width):
            for dz in range(depth):
                self.chunk.set_block(start_x + dx, center_y, start_z + dz, floor)
                self.chunk.set_block(start_x + dx, top_y, start_z + dz, floor)

        for dy in range(1, height):
            for dx in range(width):
                for dz in range(depth):
                    is_edge = dx == 0 or dx == width - 1 or dz == 0 or dz == depth - 1
                    is_corner = (dx in (0, width - 1)) and (dz in (0, depth - 1))
                    if is_corner:
                        self.chunk.set_block(start_x + dx, center_y + dy, start_z + dz, log)
                    elif is_edge:
                        self.chunk.set_block(start_x + dx, center_y + dy, start_z + dz, wall)

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

        self.chunk.set_block(door_x, center_y + 1, door_z, doorlower)
        self.chunk.set_block(door_x, center_y + 2, door_z, doorupper)
        self.chunk.set_block(torch_pos[0], torch_pos[1], torch_pos[2], torch)
        self.chunk.set_block(bed_pos[0], bed_pos[1], bed_pos[2], Block(f"red_bed[facing={bed_facing}]"))
        self.chunk.set_block(bed_pos[0]-relatives[orientation][0],
                             bed_pos[1],
                             bed_pos[2]-relatives[orientation][1],
                             Block(f"red_bed[part=head,facing={bed_facing}]")
                             )

        self.built = True
        self.chunk.to_file()
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

        return door_x, center_y, door_z

if __name__ == "__main__":
    from gdpc import interface
    from AbstractionLayer import AbstractionLayer
    from Agent import Agent
    from Chunk import Chunk
    from random import randint


    abl = AbstractionLayer(interface.getBuildArea())
    abl.save_all()
    abl.push()

    print("Beginning build test...")
    h = House((-326, 79, 60), Agent(abl, Chunk.LOADED_CHUNKS, radius=5, x=randint(-5, 5), z=randint(-5, 5)), "MaisonTest", orientation="north")
    h.build()