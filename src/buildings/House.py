from buildings.Building import Building
from gdpc.minecraft_tools import signBlock
import random
from simLogic.Job import JobType
from utils.math_methods import distance_xz
from utils.ANSIColors import ANSIColors

class House(Building):
    def __init__(self, center_point: tuple[int,int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated"):
        super().__init__(center_point, agent, name, orientation, built, folder, height=random.randint(5, 7), width=7, depth=7)
        self.construction_phase = 0
        self.construction_progress = 0
        self.construction_ticks = 0
        self.helping_agents = {}
        self.built_phases = set()
        self.door = None
        self.bed = None
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
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]

    def choose_materials(self):
        bed_options = ["minecraft:red_bed", "minecraft:blue_bed", "minecraft:green_bed", "minecraft:yellow_bed", "minecraft:black_bed"]
        wall_options = {
            "stone": ["minecraft:stone", "minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"],
            "cobblestone": ["minecraft:cobblestone", "minecraft:mossy_cobblestone"],
            "bricks": ["minecraft:bricks", "minecraft:cracked_bricks"],
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
            self.build_foundation_progressive(phase_ratio)
        elif current_phase == "walls":
            self.build_walls_progressive(phase_ratio)
        elif current_phase == "roof":
            self.build_roof_progressive(phase_ratio)

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

    def build_foundation_progressive(self, progress_ratio):
        y = 0
        floor = self.materials["floor"]
        total_blocks = self.width * self.depth
        blocks_to_place = int(total_blocks * progress_ratio)
        for i in range(self.width-1):
            for j in range(self.depth-1):
                super().add_block_to_matrix(i, y, j, floor)
                if progress_ratio > 0.8:
                    log = self.materials["log"]
                    for dy in range(self.height):
                        for corner in self.corners:
                            if i == corner[0] and j == corner[1]:
                                super().add_block_to_matrix(i, dy, j, log)

    def build_walls_progressive(self, progress_ratio):
        y = 1

        total_wall_blocks = (2 * (self.width + self.depth - 2)) * (self.height - 1)
        blocks_to_place = int(total_wall_blocks * progress_ratio)

        for dy in range(1, self.height-1):
            for dx in range(self.width-1):
                for dz in range(self.depth-1):

                    is_corner = [dx, dz] in self.corners
                    is_wall = (dx == 0 or dx == self.width - 1 or dz == 0 or dz == self.depth - 1)
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

    def build_roof_progressive(self, progress_ratio):
        roof_material = "oak_planks"
        stairs_material = roof_material.replace("planks", "stairs")

        if self.roof_style == "pyramid":
            for turn, dy in enumerate(range(self.height - 2, self.height)):
                offset = turn
                for dx in range(offset, self.width - offset - 1):
                    for dz in range(offset, self.depth - offset - 1):
                        is_edge_x = dx == offset or dx == self.width - offset - 1
                        is_edge_z = dz == offset or dz == self.depth - offset - 1
                        if is_edge_x or is_edge_z:
                            facing = "north"
                            if dx == offset:
                                facing = "east"
                            elif dx == self.width - offset - 1:
                                facing = "west"
                            elif dz == offset:
                                facing = "south"

                            stairs_block = f"minecraft:{stairs_material}[facing={facing}]"
                            super().add_block_to_matrix(dx, dy, dz, stairs_block)
                            if dy <= self.height - 2:
                                super().add_block_to_matrix(dx, dy+1, dz, "minecraft:air")
                        else:
                            super().add_block_to_matrix(dx, dy, dz, "minecraft:air")
            super().add_block_to_matrix(2, self.height-1, 2, roof_material)
            super().add_block_to_matrix(2, self.height - 2, 2, "minecraft:lantern[hanging=true]")
        elif self.roof_style == "flat":
            for dx in range(self.width-1):
                for dz in range(self.depth-1):
                        super().add_block_to_matrix(dx, self.height - 2, dz, roof_material)
                        super().add_block_to_matrix(dx, self.height - 1, dz, "minecraft:air")
            super().add_block_to_matrix(3, self.height - 3, 3, "minecraft:lantern[hanging=true]")

    def build_furniture_progressive(self):
        furniture_placed = 0
        attempts = 0
        while furniture_placed < self.furniture_counter and attempts < 20:
            x = random.randint(3, self.width - 3)
            z = random.randint(3, self.depth - 3)
            if self.matrix[x][z][1] == "minecraft:air":
                furniture = random.choice(self.furnitures)
                super().add_block_to_matrix(x, 1, z, furniture)
                furniture_placed += 1
            attempts += 1
        #super().add_block_to_matrix(3, 1, 3, 'minecraft:oak_sign')
