from buildings.Building import Building
from gdpc.minecraft_tools import signBlock
import random
from simLogic.Job import JobType
from utils.math_methods import distance_xz
from utils.ANSIColors import ANSIColors

class House(Building):
    def __init__(self, center_point: tuple[int,int] | None, agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated"):
        super().__init__(center_point, agent, name, orientation, built, folder)
        self.construction_phase = 0
        self.construction_progress = 0
        self.construction_ticks = 0
        self.helping_agents = {}
        self.built_phases = set()
        self.utility_blocks = [
            "crafting_table"
            "furnace",
            "chest",
            "barrel",
            "loom",
            "stonecutter"
        ]

        family_size = 1
        for rel in agent.simulation.relationships.RELATIONSHIPS.keys():
            if rel['value'] >= 0.8:
                family_size += 1

        if family_size <= 2:
            self.width = 5
            self.depth = 5
        elif family_size <= 4:
            self.width = 7
            self.depth = 7
        else:
            self.width = 9
            self.depth = 9

        self.height = random.randint(4, 5)
        self.materials = self.choose_materials("plains")

        self.phase_times = {
            "foundation": 20,
            "walls": 10,
            "roof": 5,
            "furniture": 2
        }

        self.corners = [
            [0, 0],
            [0, self.depth - 1],
            [self.width - 1, 0],
            [self.width - 1, self.depth - 1]
        ]


    def choose_materials(self,biome: str = "plains"):
        door_options = ["minecraft:oak_door", "minecraft:spruce_door", "minecraft:birch_door", "minecraft:dark_oak_door", "minecraft:acacia_door"]
        bed_options = ["minecraft:red_bed", "minecraft:blue_bed", "minecraft:green_bed", "minecraft:yellow_bed", "minecraft:black_bed"]

        if biome in self.agent.simulation.params["biome"].keys():
            floor_options = self.agent.simulation.params["biome"][biome]["floor_options"]
            wall_options = self.agent.simulation.params["biome"][biome]["wall_options"]
            log_options = self.agent.simulation.params["biome"][biome]["log_options"]
        else:
            floor_options = ["minecraft:oak_planks", "minecraft:spruce_planks", "minecraft:birch_planks", "minecraft:dark_oak_planks", "minecraft:acacia_planks"]
            wall_options = {
                "stone": ["minecraft:stone", "minecraft:stone_bricks", "minecraft:cracked_stone_bricks", "minecraft:mossy_stone_bricks"],
                "cobblestone": ["minecraft:cobblestone", "minecraft:mossy_cobblestone"],
                "bricks": ["minecraft:bricks", "minecraft:cracked_bricks"],
                "wood": ["minecraft:oak_planks", "minecraft:spruce_planks", "minecraft:birch_planks", "minecraft:dark_oak_planks", "minecraft:acacia_planks"]
            }
            log_options = ["minecraft:oak_log", "minecraft:spruce_log", "minecraft:birch_log", "minecraft:dark_oak_log", "minecraft:acacia_log"]

        wall_type = random.choice(list(wall_options.keys()))
        wall_variants = wall_options[wall_type]

        return {
            "floor": random.choice(floor_options),
            "wall": wall_variants,
            "log": random.choice(log_options),
            "door": random.choice(door_options),
            "bed": random.choice(bed_options)
        }

    def get_construction_status(self) -> str:
        phases = ["foundation", "walls", "roof", "furniture"]
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

        current_phase = ["foundation", "walls", "roof", "furniture"][self.construction_phase]
        phase_time = self.phase_times[current_phase]
        construction_speed = self.calculate_construction_speed()

        self.construction_progress += (100 / phase_time) * construction_speed

        phase_progress = min(100, self.construction_progress)
        phase_ratio = phase_progress / 100.0

        if current_phase == "foundation":
            self.build_foundation_progressive(phase_ratio)
        elif current_phase == "walls":
            self.build_walls_progressive(phase_ratio)
        #elif current_phase == "roof":
        #    self.build_roof_progressive(phase_ratio)
        #elif current_phase == "furniture":
        #    self.build_furniture_progressive(phase_ratio)

        if self.construction_progress >= 100:
            self.construction_progress = 0
            self.construction_phase += 1

            if self.construction_phase >= 4:
                super().built()
                self.helping_agents.clear()
                print(f"{ANSIColors.OKBLUE}[SIMULATION INFO]{ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house is complete!{ANSIColors.ENDC}")

        if self.construction_phase < 4:
            status = self.get_construction_status()
            helpers = f" with {len(self.helping_agents)} helpers" if self.helping_agents else ""
            print(f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.agent.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE}'s house: {ANSIColors.ENDC}{ANSIColors.OKCYAN}{status}{helpers}{ANSIColors.ENDC}")

    def build_foundation_progressive(self, progress_ratio):
        y = 0
        floor = self.materials["floor"]
        total_blocks = self.width * self.depth
        blocks_to_place = int(total_blocks * progress_ratio)
        for i in range(blocks_to_place):
            dx = i % self.width
            dz = i // self.width
            super().add_block_to_matrix(dx, y, dz, floor)

            if progress_ratio > 0.8:
                log = self.materials["log"]
                for dy in range(self.height):
                    for corner in self.corners:
                        if dx == corner[0] and dz == corner[1]:
                            super().add_block_to_matrix(dx, dy, dz, log)

    def build_walls_progressive(self, progress_ratio):
        y = 1

        total_wall_blocks = (2 * (self.width + self.depth - 2)) * (self.height - 1)
        blocks_to_place = int(total_wall_blocks * progress_ratio)

        blocks = 0
        for dy in range(1, self.height):
            for dx in range(self.width):
                for dz in range(self.depth):
                    if blocks >= blocks_to_place:
                        return

                    is_corner = [dx, dz] in self.corners
                    is_wall = (dx == 0 or dx == self.width - 1 or dz == 0 or dz == self.depth - 1)

                    if not is_corner and is_wall:
                        wall_block = random.choice(self.materials["wall"])
                        super().add_block_to_matrix(dx, dy, dz, wall_block)
                        blocks += 1

        x, z = self.width // 2, self.depth // 2
        if self.orientation == "north":
            door_x, door_z = x + self.width // 2, z
        elif self.orientation == "south":
            door_x, door_z = x + self.width // 2, z + self.depth - 1
        elif self.orientation == "east":
            door_x, door_z = x + self.width - 1, z + self.depth // 2
        elif self.orientation == "west":
            door_x, door_z = x, z + self.depth // 2
        else:
            door_x, door_z = x + self.width // 2, z

        #door_block = self.materials["door"] if "door" in self.materials else "minecraft:oak_door"
        super().add_block_to_matrix(door_x - x, 1, door_z - z, "minecraft:air")
        super().add_block_to_matrix(door_x - x, 2, door_z - z, "minecraft:air")

    def build_roof_progressive(self, progress_ratio):
        roof_material = random.choice(["oak_planks", "spruce_planks"])
        stairs_material = roof_material.replace("planks", "stairs")

        roof_height = min(3, max(2, (self.width + self.depth) // 6))

        if progress_ratio > 0.3:
            for dy in range(roof_height):
                overhang = roof_height - dy - 1
                y = self.height + dy
                for dx in range(-overhang, self.width + overhang):
                    for dz in range(-overhang, self.depth + overhang):
                        is_west = dx == -overhang
                        is_east = dx == self.width + overhang - 1
                        is_north = dz == -overhang
                        is_south = dz == self.depth + overhang - 1
                        is_corner = (is_west or is_east) and (is_north or is_south)
                        if is_corner:
                            facing = ""
                            shape = ""
                            if is_west and is_north:
                                facing = "east"
                                shape = "outer_right"
                            elif is_east and is_north:
                                facing = "south"
                                shape = "outer_right"
                            elif is_east and is_south:
                                facing = "west"
                                shape = "outer_right"
                            elif is_west and is_south:
                                facing = "north"
                                shape = "outer_right"
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                f"{stairs_material};facing={facing};shape={shape}"
                            )
                        elif is_west:
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                f"{stairs_material};facing=east"
                            )
                        elif is_east:
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                f"{stairs_material};facing=west"
                            )
                        elif is_north:
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                f"{stairs_material};facing=south"
                            )
                        elif is_south:
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                f"{stairs_material};facing=north"
                            )
                        elif -overhang < dx < self.width + overhang - 1 and -overhang < dz < self.depth + overhang - 1:
                            super().add_block_to_matrix(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                roof_material
                            )

        if progress_ratio > 0.99 and random.randint(0, 1) < 0.2:
            chimney_x = self.start_x + self.width - random.randint(1, 3) - 1
            chimney_z = self.start_z + random.randint(1, 3)
            super().add_block_to_matrix(chimney_x, self.height + 1, chimney_z, "bricks")
            super().add_block_to_matrix(chimney_x, self.height + 2, chimney_z, "brick_wall")
            super().add_block_to_matrix(chimney_x, self.height + 3, chimney_z, "flower_pot")

    def build_furniture_progressive(self, progress_ratio):
        center_y = self.center_point[1]

        if progress_ratio > 0.5:
            super().add_block_to_matrix(self.torch_pos[0], self.torch_pos[1], self.torch_pos[2],
                                 f"minecraft:wall_torch;facing={self.bed_facing}")

        if progress_ratio > 0.75:
            bed = self.materials["bed"]
            super().add_block_to_matrix(self.bed_pos[0], self.bed_pos[1], self.bed_pos[2],
                                 f"{bed};facing={self.bed_facing}")
            super().add_block_to_matrix(self.bed_head_pos[0], self.bed_head_pos[1], self.bed_head_pos[2],
                                 f"{bed};part=head;facing={self.bed_facing}")

            num_blocks = random.randint(0, 1)
            for _ in range(num_blocks):
                if not self.utility_blocks:
                    break

                block_type = random.choice(self.utility_blocks)
                self.utility_blocks.remove(block_type)

                if self.orientation in ["north", "south"]:
                    side = random.choice([-1, 1])
                    x = self.bed_head_pos[0] + side
                    z = self.bed_head_pos[2]
                else:
                    side = random.choice([-1, 1])
                    x = self.bed_head_pos[0]
                    z = self.bed_head_pos[2] + side

                super().add_block_to_matrix(x, self.bed_head_pos[1], z, f"{block_type};facing={self.bed_facing}")

        if progress_ratio > 0.9:
            block = signBlock(
                wall=True,
                facing=self.orientation,
                rotation=0,
                frontLine2=self.agent.name,
                frontLine3=self.agent.job.__str__(),
            )
            super().add_block_to_matrix(self.sign_x, center_y + 2, self.sign_z, block)

    def get_door_position(self):
        if self.center_point is None:
            return None

        if not hasattr(self, 'door_x'):
            self.setup_positions()

        return self.door_x, self.center_point[1], self.door_z

    def evaluate_spot(self, x: int, z: int) -> float:
        score = 0.0

        center_distance = distance_xz(x, z, self.agent.center_village[0], self.agent.center_village[1])
        center_score = max(0, 1 - (center_distance / 50))
        score += center_score * 0.3

        water_distance = float('inf')
        for water_coord in self.agent.observations["terrain"]["water"]:
            dist = distance_xz(x, z, water_coord[0], water_coord[2])
            water_distance = min(water_distance, dist)
        if water_distance != float('inf'):
            water_score = max(0, 1 - (water_distance / 30))
            score += water_score * 0.2

        chunk = self.agent.abl.get_chunk(x, z)
        y = chunk.getGroundHeight(x, z)
        altitude_score = min(1, y / 100)
        score += altitude_score * 0.2

        relationship_score = 0
        for other_agent in self.agent.all_agents:
            if other_agent.id != self.agent.id and other_agent.does_have_house:
                rel = self.agent.get_relationship(other_agent)
                dist = distance_xz(x, z, other_agent.x, other_agent.z)
                rel_score = rel.value * (1 - min(1, dist / 30))
                relationship_score += rel_score
        relationship_score = max(-1, min(1, relationship_score / len(self.agent.all_agents)))
        score += (relationship_score + 1) * 0.15

        if Building.detect_all_trespassing(x, z):
            return -1

        for other_agent in self.agent.all_agents:
            if other_agent.id != self.agent.id and other_agent.does_have_house:
                rel = self.agent.get_relationship(other_agent)
                if rel.value < -0.5:
                    if self.blocks_path_to_center(x, z, other_agent):
                        return -1

        return score

    def blocks_path_to_center(self, x: int, z: int, other_agent) -> bool:
        if not other_agent.does_have_house:
            return False

        house_to_center = (self.agent.center_village[0] - other_agent.x,
                           self.agent.center_village[1] - other_agent.z)
        spot_to_center = (self.agent.center_village[0] - x,
                          self.agent.center_village[1] - z)

        if (abs(spot_to_center[0]) < abs(house_to_center[0]) and
                abs(spot_to_center[1]) < abs(house_to_center[1])):
            return True
        return False