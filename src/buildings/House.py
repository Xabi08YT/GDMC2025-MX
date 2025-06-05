from buildings.Building import Building
from gdpc.minecraft_tools import signBlock
import random
from simLogic.Job import JobType
from utils.math_methods import distance_xz
from utils.ANSIColors import ANSIColors

class House(Building):
    def __init__(self, center_point: tuple[int,int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated"):
        super().__init__(center_point, agent, name, orientation, built, folder, height=random.randint(6, 7), width=7, depth=7)
        self.construction_phase = 0
        self.construction_progress = 0
        self.construction_ticks = 0
        self.helping_agents = {}
        self.built_phases = set()
        self.door = None
        self.bed = None
        self.container = None
        self.roof_style = random.choice(["flat", "pyramid"])
        self.furniture_counter = random.randint(1, 2)
        self.furnitures = ["minecraft:crafting_table", "minecraft:chest", "minecraft:barrel", "minecraft:smithing_table", "minecraft:grindstone"]
        self.corner_block = "minecraft:oak_log"
        self.materials = self.choose_materials()

        self.phase_times = {
            "foundation": 20,
            "walls": 10,
            "roof": 5
        }

        self.corners = [
            [1, 1],
            [1, self.depth - 2],
            [self.width - 2, 1],
            [self.width - 2, self.depth - 2]
        ]

    def choose_materials(self):
        bed_options = ["minecraft:red_bed", "minecraft:blue_bed", "minecraft:green_bed", "minecraft:yellow_bed", "minecraft:black_bed"]
        wall_options = {
            "stone": ["minecraft:stone", "minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"],
            "cobblestone": ["minecraft:cobblestone", "minecraft:mossy_cobblestone"],
            "wood": ["minecraft:oak_planks"]
        }
        wall_type = random.choice(list(wall_options.keys()))
        wall_variants = wall_options[wall_type]

        return {
            "floor": "minecraft:oak_planks",
            "wall": wall_variants,
            "log": "minecraft:oak_log",
            "door": "minecraft:oak_door",
            "bed": random.choice(bed_options)
        }

    def get_construction_status(self) -> str:
        phases = ["foundation", "walls", "roof"]
        if self.construction_phase >= len(phases):
            return "Completed"

        current_phase = phases[self.construction_phase]
        progress = min(100, round(self.construction_progress, 1))

        return f"{current_phase} ({progress}%)"

    def add_helping_agent(self, agent, strength: float):
        if agent not in self.helping_agents:
            self.helping_agents[agent] = strength
            if agent.id in self.agent.relationships:
                self.agent.relationships[agent.id].improve(0.1)
            print(f"{agent.name} started helping {self.agent.name} build their house")

    def remove_helping_agent(self, agent):
        if agent in self.helping_agents:
            del self.helping_agents[agent]
            print(f"{agent.name} stopped helping {self.agent.name} build their house")

    def calculate_construction_speed(self) -> float:
        base_speed = 0.3 + self.agent.attributes["strength"]

        helper_speed = 0
        for agent, strength in self.helping_agents.items():
            speed_boost = strength
            if agent.job.job_type == JobType.MASON:
                speed_boost *= 1.5
            helper_speed += speed_boost

        return base_speed + (helper_speed * 0.5)

    def build(self):
        if self.center_point is None or self.built:
            return

        self.construction_ticks += 1

        current_phase = ["foundation", "walls", "roof"][self.construction_phase]
        phase_time = self.phase_times[current_phase]
        construction_speed = self.calculate_construction_speed()

        self.construction_progress += (100 / phase_time) * construction_speed

        phase_progress = min(100, self.construction_progress)
        phase_ratio = phase_progress / 100.0

        if current_phase == "foundation":
            self.build_foundation_progressive()
        elif current_phase == "walls":
            self.build_walls_progressive()
        elif current_phase == "roof":
            self.build_roof_progressive()

        if self.construction_progress >= 100:
            self.construction_progress = 0
            self.construction_phase += 1

            if self.construction_phase >= 3:
                self.build_furniture_progressive()
                super().built()
                self.helping_agents.clear()
                print(f"{ANSIColors.OKBLUE}[SIMULATION INFO]{ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house is complete!{ANSIColors.ENDC}")

        if self.construction_phase < 3:
            status = self.get_construction_status()
            helpers = f" with {len(self.helping_agents)} helpers" if self.helping_agents else ""
            print(f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house: {ANSIColors.ENDC}{ANSIColors.OKCYAN}{status}{helpers}{ANSIColors.ENDC}")

    def build_foundation_progressive(self):
        y = 0
        floor = self.materials["floor"]
        for i in range(0, self.width):
            for j in range(0, self.depth):
                if i == 0 or i == self.width - 1 or j == 0 or j == self.depth - 1:
                    super().add_block_to_matrix(i, y, j, "minecraft:grass_block")
                else:
                    super().add_block_to_matrix(i, y, j, floor)
                    log = self.materials["log"]
                    for dy in range(self.height):
                        for corner in self.corners:
                            if i == corner[0] and j == corner[1]:
                                super().add_block_to_matrix(i, dy, j, log)

    def build_walls_progressive(self):
        for dy in range(1, self.height-1):
            for dx in range(1, self.width-1):
                for dz in range(1, self.depth-1):

                    is_corner = [dx, dz] in self.corners
                    is_wall = (dx == 1 or dx == self.width - 2 or dz == 1 or dz == self.depth - 2)
                    is_door = False
                    if self.door is not None:
                        door_x, door_y, door_z = self.door
                        is_door = (dx == door_x and dz == door_z and dy in [1, 2])

                    if not is_corner and is_wall and not is_door:
                        wall_block = random.choice(self.materials["wall"])
                        super().add_block_to_matrix(dx, dy, dz, wall_block)

        x, z = (self.width - 1) // 2, (self.depth - 1) // 2

        if self.door is None:
            door_x, door_z = x, z

            if self.orientation == "north":
                door_z = 0
            elif self.orientation == "south":
                door_z = self.depth - 2
            elif self.orientation == "east":
                door_x = self.width - 2
            elif self.orientation == "west":
                door_x = 0

            super().add_block_to_matrix(door_x, 1, door_z, f'{self.materials["door"]}[half=lower]')
            super().add_block_to_matrix(door_x, 2, door_z, f'{self.materials["door"]}[half=upper]')
            self.door = (door_x, 1, door_z)

    def build_roof_progressive(self):
        roof_material = "oak_planks"

        if self.roof_style == "pyramid":
            center_x = (self.width - 1) // 2
            center_z = (self.depth - 1) // 2
            roof_base_y = self.height - 2
            max_distance = min(center_x, center_z)
            for x in range(self.width):
                for z in range(self.depth):
                    dist_x = abs(x - center_x)
                    dist_z = abs(z - center_z)
                    max_dist = max(dist_x, dist_z)
                    height_offset = max_distance - max_dist - 1
                    y = roof_base_y + height_offset
                    for fill_y in range(roof_base_y, y):
                        super().add_block_to_matrix(x, fill_y, z, roof_material)
                    if max_dist > 0:
                        if dist_x > dist_z:
                            if x < center_x:
                                facing = "east"
                            else:
                                facing = "west"
                        else:
                            if z < center_z:
                                facing = "south"
                            else:
                                facing = "north"

                        stair_block = f"minecraft:oak_stairs[facing={facing},half=bottom,shape=straight]"
                        super().add_block_to_matrix(x, y, z, stair_block)
                        if y < self.height - 1:
                            super().add_block_to_matrix(x, y + 1, z, "minecraft:air")
                    else:
                        super().add_block_to_matrix(center_x, y-3, center_z,"minecraft:lantern[hanging=true]")

        elif self.roof_style == "flat":
            for dx in range(self.width):
                for dz in range(self.depth):
                    if 1 <= dx < self.width - 1 and 1 <= dz < self.depth - 1:
                        super().add_block_to_matrix(dx, self.height - 2, dz, roof_material)
                        super().add_block_to_matrix(dx, self.height - 1, dz, "minecraft:air")
                    elif (dx == 0 or dx == self.width - 1) or (dz == 0 or dz == self.depth - 1):
                        super().add_block_to_matrix(dx, self.height - 2, dz, "minecraft:oak_slab[type=bottom]")
            super().add_block_to_matrix(3, self.height - 3, 3, "minecraft:lantern[hanging=true]")

    def build_furniture_progressive(self):
        patterns = [
            {
                (2, 2): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (2, 3): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (2, 3): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (2, 2): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (2, 3): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (2, 4): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (2, 4): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (2, 3): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (4, 2): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (4, 3): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (4, 3): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (4, 2): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (4, 3): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (4, 4): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (4, 4): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (4, 3): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (2, 2): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (3, 2): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (3, 2): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (4, 2): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
            {
                (4, 2): self.materials["bed"] + "[part=foot,facing=" + self.orientation + "]",
                (3, 2): self.materials["bed"] + "[part=head,facing=" + self.orientation + "]",
            },
        ]
        selected_pattern = random.choice(patterns)
        for (x, z), block in selected_pattern.items():
            super().add_block_to_matrix(x, 1, z, block)
        bed_positions = list(selected_pattern.keys())
        forbidden_positions = [(3, 3), (3, 4)] + bed_positions
        possible_positions = [(x, z) for x in range(2, 5) for z in range(2, 5)
                                  if (x, z) not in forbidden_positions]
        if possible_positions:
            pos = random.choice(possible_positions)
            possible_positions.remove(pos)
            self.container = (pos[0], 1, pos[1])
        if possible_positions:
            pos = random.choice(possible_positions)
            furniture = "minecraft:crafting_table"
            super().add_block_to_matrix(pos[0], 1, pos[1], furniture)
        if self.door is not None:
            door_x, _, door_z = self.door
            if self.orientation == "north":
                sign_x, sign_z = door_x - 1, door_z + 1
            elif self.orientation == "south":
                sign_x, sign_z = door_x + 1, door_z + 1
            elif self.orientation == "east":
                sign_x, sign_z = door_x + 1, door_z - 1
            elif self.orientation == "west":
                sign_x, sign_z = door_x + 1, door_z + 1
            else:
                sign_x, sign_z = door_x, door_z
            super().add_block_to_matrix(sign_x, 2, sign_z, f'minecraft:oak_sign')
        else:
            super().add_block_to_matrix(3, 2, 3, 'minecraft:oak_sign')
