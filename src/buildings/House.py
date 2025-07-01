from buildings.Building import Building
import random
from simLogic.Job import JobType
from utils.math_methods import distance_xz
from utils.ANSIColors import ANSIColors
from simLogic.Job import JobBlock

class House(Building):
    def __init__(self, center_point: tuple[int,int] | None, agent, name: str, built: bool = False, folder="generated"):
        """
        Initializes a House object.
        :param center_point: The center point of the house in the format (x, z).
        :param agent: The agent who is building the house.
        :param name: The name of the house.
        :param built: True if the house is already built, False otherwise.
        :param folder: Folder where the house data will be stored.
        """
        orientation = random.choice(["south", "north", "east", "west"])
        super().__init__(center_point, agent, name, orientation, built, folder, height=random.randint(6, 7), width=7, depth=7)
        self.construction_phase = 0
        self.construction_progress = 0
        self.construction_ticks = 0
        self.helping_agents = {}
        self.door = None
        self.bed = None
        self.container = None
        self.roof_style = random.choice(["flat", "pyramid"])
        self.materials = self.choose_materials()

        self.phase_times = {
            "foundation": 15,
            "walls": 5,
            "roof": 2
        }

        self.corners = [
            [1, 1],
            [1, self.depth - 2],
            [self.width - 2, 1],
            [self.width - 2, self.depth - 2]
        ]
        self.clear()

    def choose_materials(self):
        """
        Chooses materials for the house based on predefined options.
        :return: Materials dictionary containing floor, wall, log, door, and bed.
        """
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
        """
        Returns the current construction status of the house.
        :return: The current construction phase and progress as a string.
        """
        phases = ["foundation", "walls", "roof"]
        if self.construction_phase >= len(phases):
            return "Completed"

        current_phase = phases[self.construction_phase]
        progress = min(100, round(self.construction_progress, 1))

        return f"{current_phase} ({progress}%)"

    def calculate_construction_speed(self) -> float:
        """
        Calculates the construction speed based on the agent's strength and the helping agents' contributions.
        :return: The construction speed as a float.
        """
        base_speed = 0.3 + self.agent.attributes["strength"]

        helper_speed = 0
        for agent, strength in self.helping_agents.items():
            speed_boost = strength
            if agent.job.job_type == JobType.MASON:
                speed_boost *= 1.5
            helper_speed += speed_boost

        return base_speed + (helper_speed * 0.5)

    def build(self):
        """
        Builds the house by constructing its foundation, walls, and roof in phases.
        """
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
            self.build_foundation(phase_ratio)
        elif current_phase == "walls":
            self.build_walls(phase_ratio)
        elif current_phase == "roof":
            self.build_roof(phase_ratio)

        if self.construction_progress >= 100:
            self.construction_progress = 0
            self.construction_phase += 1

            if self.construction_phase >= 3:
                self.build_furniture()
                super().built()
                self.helping_agents.clear()
                print(f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house is complete!{ANSIColors.ENDC}")
                return

        status = self.get_construction_status()
        helpers = f" with {len(self.helping_agents)} helpers" if self.helping_agents else ""
        print(f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house: {ANSIColors.ENDC}{ANSIColors.OKCYAN}{status}{helpers}{ANSIColors.ENDC}")

    def build_foundation(self, progress):
        """
        Builds the foundation of the house.
        :param progress: Progress ratio (0.0 to 1.0) indicating how much of the foundation has been built.
        """
        y = 0
        floor = self.materials["floor"]
        total_blocks = (self.width) * (self.depth)
        blocks_to_place = int(total_blocks * progress)
        placed = 0
        for i in range(0, self.width):
            for j in range(0, self.depth):
                if placed >= blocks_to_place:
                    return
                if i == 0 or i == self.width - 1 or j == 0 or j == self.depth - 1:
                    super().add_block_to_matrix(i, y, j, "minecraft:grass_block")
                else:
                    super().add_block_to_matrix(i, y, j, floor)
                    log = self.materials["log"]
                    for dy in range(self.height):
                        for corner in self.corners:
                            if i == corner[0] and j == corner[1]:
                                super().add_block_to_matrix(i, dy, j, log)
                placed += 1

    def build_walls(self, progress):
        """
        Builds the walls of the house.
        :param progress: Progress ratio (0.0 to 1.0) indicating how much of the foundation has been built.
        """
        wall_blocks = []
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
                        wall_blocks.append((dx, dy, dz))
        total_blocks = len(wall_blocks)
        if progress > 0.9:
            blocks_to_place = total_blocks
        else:
            blocks_to_place = int(total_blocks * progress)
        for idx, (dx, dy, dz) in enumerate(wall_blocks):
            if idx >= blocks_to_place:
                break
            wall_block = random.choice(self.materials["wall"])
            super().add_block_to_matrix(dx, dy, dz, wall_block)
        x, z = (self.width - 1) // 2, (self.depth - 1) // 2
        if self.door is None:
            door_x, door_z = x, z
            if self.orientation == "north":
                door_z = 1
            elif self.orientation == "south":
                door_z = self.depth - 2
            elif self.orientation == "east":
                door_x = self.width - 2
            elif self.orientation == "west":
                door_x = 1
            super().add_block_to_matrix(door_x, 1, door_z, f'{self.materials["door"]}[half=lower,facing={self.orientation}]')
            super().add_block_to_matrix(door_x, 2, door_z, f'{self.materials["door"]}[half=upper,facing={self.orientation}]')
            self.door = (door_x, 1, door_z)

    def build_roof(self, progress):
        """
        Builds the roof of the house.
        :param progress: Progress ratio (0.0 to 1.0) indicating how much of the foundation has been built.
        :return:
        """
        roof_material = "oak_planks"
        roof_blocks = []
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
                        roof_blocks.append((x, fill_y, z, roof_material))
                    if max_dist > 0:
                        if dist_x > dist_z:
                            facing = "east" if x < center_x else "west"
                        else:
                            facing = "south" if z < center_z else "north"
                        stair_block = f"minecraft:oak_stairs[facing={facing},half=bottom,shape=straight]"
                        roof_blocks.append((x, y, z, stair_block))
                        if y < self.height - 1:
                            roof_blocks.append((x, y + 1, z, "minecraft:air"))
                    else:
                        roof_blocks.append((center_x, y-3, center_z, "minecraft:lantern[hanging=true]"))
        elif self.roof_style == "flat":
            for dx in range(self.width):
                for dz in range(self.depth):
                    if 1 <= dx < self.width - 1 and 1 <= dz < self.depth - 1:
                        roof_blocks.append((dx, self.height - 2, dz, roof_material))
                        roof_blocks.append((dx, self.height - 1, dz, "minecraft:air"))
                    elif (dx == 0 or dx == self.width - 1) or (dz == 0 or dz == self.depth - 1):
                        roof_blocks.append((dx, self.height - 2, dz, "minecraft:oak_slab[type=bottom]"))
            roof_blocks.append((3, self.height - 3, 3, "minecraft:lantern[hanging=true]"))
        total_blocks = len(roof_blocks)
        blocks_to_place = int(total_blocks * progress)
        for idx, (x, y, z, block) in enumerate(roof_blocks):
            if idx >= blocks_to_place:
                break
            super().add_block_to_matrix(x, y, z, block)

    def build_furniture(self):
        """
        Builds furniture inside the house, including a bed and a container.
        :return:
        """
        facing = self.orientation
        if facing == "north":
            corners = [((2, 2), (2, 3)), ((4, 2), (4, 3))]
            bed_facing = "south"
        elif facing == "south":
            corners = [((2, 4), (2, 3)), ((4, 4), (4, 3))]
            bed_facing = "north"
        elif facing == "east":
            corners = [((4, 2), (3, 2)), ((4, 4), (3, 4))]
            bed_facing = "west"
        elif facing == "west":
            corners = [((2, 2), (3, 2)), ((2, 4), (3, 4))]
            bed_facing = "east"
        else:
            corners = [((2, 2), (2, 3)), ((4, 2), (4, 3))]
            bed_facing = "south"
        foot, head = random.choice(corners)
        bed_pattern = {foot: self.materials["bed"] + f"[part=foot,facing={bed_facing}]",
                       head: self.materials["bed"] + f"[part=head,facing={bed_facing}]"}
        for (x, z), block in bed_pattern.items():
            super().add_block_to_matrix(x, 1, z, block)
        bed_positions = list(bed_pattern.keys())
        forbidden_positions = [(3, 3)] + bed_positions
        if self.door is not None:
            door_x, _, door_z = self.door
            if self.orientation == "north":
                front_pos = (door_x, door_z + 1)
            elif self.orientation == "south":
                front_pos = (door_x, door_z - 1)
            elif self.orientation == "east":
                front_pos = (door_x - 1, door_z)
            elif self.orientation == "west":
                front_pos = (door_x + 1, door_z)
            else:
                front_pos = None
            if front_pos and 2 <= front_pos[0] <= 4 and 2 <= front_pos[1] <= 4:
                forbidden_positions.append(front_pos)
        possible_positions = [(x, z) for x in range(2, 5) for z in range(2, 5)
                                  if (x, z) not in forbidden_positions]
        if possible_positions:
            pos = random.choice(possible_positions)
            possible_positions.remove(pos)
            self.container = (pos[0], 1, pos[1])
        if possible_positions:
            pos = random.choice(possible_positions)
            furniture = self.agent.job.get_block_from_job(self.agent.job.job_type)
            super().add_block_to_matrix(pos[0], 1, pos[1], furniture)
        if self.door is not None:
            door_x, _, door_z = self.door
            if self.orientation == "north":
                sign_x, sign_z = door_x - 1, door_z - 1
            elif self.orientation == "south":
                sign_x, sign_z = door_x + 1, door_z + 1
            elif self.orientation == "east":
                sign_x, sign_z = door_x + 1, door_z - 1
            elif self.orientation == "west":
                sign_x, sign_z = door_x - 1, door_z + 1
            else:
                sign_x, sign_z = door_x, door_z
            super().add_block_to_matrix(sign_x, 2, sign_z, f'minecraft:oak_sign')
        else:
            super().add_block_to_matrix(3, 2, 3, 'minecraft:oak_sign')
