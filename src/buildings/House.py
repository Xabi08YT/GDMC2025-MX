from gdpc import Block
from Building import Building
from gdpc.minecraft_tools import signBlock
import random

from Job import JobType
from math_methods import distance_xz

from src.utils.ANSIColors import ANSIColors


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
        for rel in agent.relationships.values():
            if rel.value >= 0.8:
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
            "foundation": 40,
            "walls": 30,
            "roof": 20,
            "furniture": 10
        }

        if self.center_point is not None:
            self.setup_positions()

    def choose_materials(self, biome: str = "plains"):
        floor_options = ["oak_planks", "spruce_planks", "birch_planks", "dark_oak_planks", "acacia_planks"]
        wall_options = {
            "stone": ["stone", "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks"],
            "cobblestone": ["cobblestone", "mossy_cobblestone"],
            "bricks": ["bricks", "cracked_bricks"],
            "wood": ["oak_planks", "spruce_planks", "birch_planks", "dark_oak_planks", "acacia_planks"]
        }
        log_options = ["oak_log", "spruce_log", "birch_log", "dark_oak_log", "acacia_log"]
        door_options = ["oak_door", "spruce_door", "birch_door", "dark_oak_door", "acacia_door"]
        bed_options = ["red_bed", "blue_bed", "green_bed", "yellow_bed", "black_bed"]

        if biome == "plains":
            floor_options = ["oak_planks", "cobblestone", "stone_bricks"]
            wall_options = {
                "stone": ["stone", "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks"],
                "cobblestone": ["cobblestone", "mossy_cobblestone"]
            }
            log_options = ["oak_log"]
        elif biome == "desert":
            floor_options = ["sandstone", "cut_sandstone", "smooth_sandstone"]
            wall_options = {
                "sandstone": ["sandstone", "cut_sandstone", "smooth_sandstone", "chiseled_sandstone"],
                "terracotta": ["terracotta", "white_terracotta", "orange_terracotta"]
            }
            log_options = ["stripped_acacia_log", "birch_log"]
        elif biome == "taiga" or biome == "snowy_taiga":
            floor_options = ["spruce_planks", "stone_bricks", "cobblestone"]
            wall_options = {
                "stone": ["stone", "stone_bricks", "cracked_stone_bricks", "mossy_stone_bricks"],
                "cobblestone": ["cobblestone", "mossy_cobblestone"],
                "wood": ["spruce_planks"]
            }
            log_options = ["spruce_log"]
            door_options = ["spruce_door"]
        elif biome == "jungle":
            floor_options = ["jungle_planks", "mossy_cobblestone", "mossy_stone_bricks"]
            wall_options = {
                "stone": ["stone", "mossy_cobblestone", "mossy_stone_bricks"],
                "wood": ["jungle_planks"]
            }
            log_options = ["jungle_log"]
            door_options = ["jungle_door"]
        elif biome == "savanna":
            floor_options = ["acacia_planks", "terracotta", "smooth_sandstone"]
            wall_options = {
                "terracotta": ["terracotta", "white_terracotta", "orange_terracotta"],
                "wood": ["acacia_planks"]
            }
            log_options = ["acacia_log"]
            door_options = ["acacia_door"]
        elif biome == "swamp":
            floor_options = ["dark_oak_planks", "mossy_cobblestone", "mossy_stone_bricks"]
            wall_options = {
                "stone": ["stone", "mossy_cobblestone", "mossy_stone_bricks"],
                "wood": ["dark_oak_planks"]
            }
            log_options = ["dark_oak_log", "oak_log"]
            door_options = ["dark_oak_door"]

        wall_type = random.choice(list(wall_options.keys()))
        wall_variants = wall_options[wall_type]

        return {
            "floor": random.choice(floor_options),
            "wall": wall_variants,
            "log": random.choice(log_options),
            "door": random.choice(door_options),
            "bed": random.choice(bed_options)
        }

    def setup_positions(self):
        if self.center_point is None:
            return

        center_x = self.center_point[0]
        center_y = self.center_point[1]
        center_z = self.center_point[2]

        half_w = self.width // 2
        half_d = self.depth // 2

        self.start_x = center_x - half_w
        self.start_z = center_z - half_d
        self.top_y = center_y + self.height

        self.set_orientation_according_to_center(self.agent)

        self.bed_facing = {
            "north": "south",
            "south": "north",
            "east": "west",
            "west": "east"
        }[self.orientation]

        self.relatives = {
            "north": (0, -1),
            "south": (0, 1),
            "east": (1, 0),
            "west": (-1, 0)
        }

        self.sign_relatives = {
            "north": (1, 0),
            "south": (-1, 0),
            "east": (0, 1),
            "west": (0, -1)
        }

        self.setup_door_position()
        self.setup_torch_position()
        self.setup_bed_position()
        self.setup_sign_position()

    def setup_door_position(self):
        center_x = self.center_point[0]
        center_z = self.center_point[2]

        if self.orientation == "north":
            self.door_x, self.door_z = center_x, self.start_z
        elif self.orientation == "south":
            self.door_x, self.door_z = center_x, self.start_z + self.depth - 1
        elif self.orientation == "east":
            self.door_x, self.door_z = self.start_x + self.width - 1, center_z
        elif self.orientation == "west":
            self.door_x, self.door_z = self.start_x, center_z

    def setup_torch_position(self):
        center_y = self.center_point[1]

        if self.orientation == "north":
            self.torch_pos = (self.door_x, center_y + 3, self.door_z + 1)
        elif self.orientation == "south":
            self.torch_pos = (self.door_x, center_y + 3, self.door_z - 1)
        elif self.orientation == "east":
            self.torch_pos = (self.door_x - 1, center_y + 3, self.door_z)
        elif self.orientation == "west":
            self.torch_pos = (self.door_x + 1, center_y + 3, self.door_z)

    def setup_bed_position(self):
        center_x = self.center_point[0]
        center_y = self.center_point[1]
        center_z = self.center_point[2]

        if self.orientation == "north":
            self.bed_pos = (center_x, center_y + 1, self.start_z + self.depth - 3)
        elif self.orientation == "south":
            self.bed_pos = (center_x, center_y + 1, self.start_z + 2)
        elif self.orientation == "east":
            self.bed_pos = (self.start_x + 2, center_y + 1, center_z)
        else:
            self.bed_pos = (self.start_x + self.width - 3, center_y + 1, center_z)

        self.bed_pos = (
            max(min(self.bed_pos[0], self.start_x + self.width - 2), self.start_x + 1),
            self.bed_pos[1],
            max(min(self.bed_pos[2], self.start_z + self.depth - 2), self.start_z + 1)
        )

        if self.orientation == "north":
            self.bed_head_pos = (self.bed_pos[0], self.bed_pos[1], self.bed_pos[2] + 1)
        elif self.orientation == "south":
            self.bed_head_pos = (self.bed_pos[0], self.bed_pos[1], self.bed_pos[2] - 1)
        elif self.orientation == "east":
            self.bed_head_pos = (self.bed_pos[0] - 1, self.bed_pos[1], self.bed_pos[2])
        else:
            self.bed_head_pos = (self.bed_pos[0] + 1, self.bed_pos[1], self.bed_pos[2])

    def setup_sign_position(self):
        self.sign_x = self.door_x + self.sign_relatives[self.orientation][0]
        self.sign_z = self.door_z + self.sign_relatives[self.orientation][1]

        sign_adjustments = {
            "north": (0, -1),
            "east": (1, 0),
            "west": (-1, 0),
            "south": (0, 1)
        }

        if self.orientation in sign_adjustments:
            self.sign_x += sign_adjustments[self.orientation][0]
            self.sign_z += sign_adjustments[self.orientation][1]

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

        if not hasattr(self, 'start_x'):
            self.setup_positions()

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
        elif current_phase == "roof":
            self.build_roof_progressive(phase_ratio)
        elif current_phase == "furniture":
            self.build_furniture_progressive(phase_ratio)

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

        self.chunk.to_file()

    def build_foundation_progressive(self, progress_ratio):
        center_y = self.center_point[1]
        floor = Block(self.materials["floor"])

        total_blocks = self.width * self.depth
        blocks_to_place = int(total_blocks * progress_ratio)

        for i in range(blocks_to_place):
            dx = i % self.width
            dz = i // self.width
            self.chunk.set_block(self.start_x + dx, center_y, self.start_z + dz, floor)

        if progress_ratio > 0.5:
            support_ratio = (progress_ratio - 0.5) * 2
            num_supports = random.randint(4, 8)
            supports_to_place = int(num_supports * support_ratio)

            for i in range(supports_to_place):
                dx = random.randint(0, self.width - 1)
                dz = random.randint(0, self.depth - 1)
                for dy in range(1, random.randint(2, 4)):
                    self.chunk.set_block(self.start_x + dx, center_y - dy, self.start_z + dz,
                                         Block(self.materials["log"]))

    def build_walls_progressive(self, progress_ratio):
        center_y = self.center_point[1]
        log = Block(self.materials["log"])

        total_wall_blocks = (2 * (self.width + self.depth - 2)) * (self.height - 1)
        blocks_to_place = int(total_wall_blocks * progress_ratio)

        block_count = 0
        for dy in range(1, self.height):
            for dx in range(self.width):
                for dz in range(self.depth):
                    if block_count >= blocks_to_place:
                        return

                    is_edge = dx == 0 or dx == self.width - 1 or dz == 0 or dz == self.depth - 1
                    is_corner = (dx in (0, self.width - 1)) and (dz in (0, self.depth - 1))

                    x, z = self.start_x + dx, self.start_z + dz

                    if (x == self.door_x and z == self.door_z and dy <= 2):
                        continue

                    if is_corner:
                        self.chunk.set_block(x, center_y + dy, z, log)
                        block_count += 1
                    elif is_edge:
                        if dy == 1:
                            wall_block = Block(random.choice(self.materials["wall"]))
                        elif dy == self.height - 1:
                            wall_block = Block(random.choice(self.materials["wall"]))
                        else:
                            if random.random() < 0.2:
                                wall_block = Block(random.choice(self.materials["wall"]))
                            else:
                                wall_block = Block(self.materials["wall"][0])

                        self.chunk.set_block(x, center_y + dy, z, wall_block)
                        block_count += 1

        if progress_ratio > 0.25:
            door = self.materials["door"]
            self.chunk.set_block(self.door_x, center_y + 1, self.door_z,
                                 Block(f"{door}[facing={self.bed_facing}]"))
            self.chunk.set_block(self.door_x, center_y + 2, self.door_z,
                                 Block(f"{door}[facing={self.bed_facing},half=upper]"))

    def build_roof_progressive(self, progress_ratio):
        center_y = self.center_point[1]
        roof_material = random.choice(["oak_planks", "spruce_planks"])
        stairs_material = roof_material.replace("planks", "stairs")

        roof_height = min(3, max(2, (self.width + self.depth) // 6))

        if progress_ratio > 0.3:
            for dy in range(roof_height):
                overhang = roof_height - dy - 1
                y = self.top_y + dy
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
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(f"{stairs_material}[facing={facing},shape={shape}]")
                            )
                        elif is_west:
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(f"{stairs_material}[facing=east]")
                            )
                        elif is_east:
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(f"{stairs_material}[facing=west]")
                            )
                        elif is_north:
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(f"{stairs_material}[facing=south]")
                            )
                        elif is_south:
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(f"{stairs_material}[facing=north]")
                            )
                        elif -overhang < dx < self.width + overhang - 1 and -overhang < dz < self.depth + overhang - 1:
                            self.chunk.set_block(
                                self.start_x + dx,
                                y,
                                self.start_z + dz,
                                Block(roof_material)
                            )

        if progress_ratio > 0.99 and random.randint(0, 1) < 0.2:
            chimney_x = self.start_x + self.width - random.randint(1, 3) - 1
            chimney_z = self.start_z + random.randint(1, 3)
            self.chunk.set_block(chimney_x, self.top_y + 1, chimney_z, Block("bricks"))
            self.chunk.set_block(chimney_x, self.top_y + 2, chimney_z, Block("brick_wall"))
            self.chunk.set_block(chimney_x, self.top_y + 3, chimney_z, Block("flower_pot"))

    def build_furniture_progressive(self, progress_ratio):
        center_y = self.center_point[1]

        if progress_ratio > 0.5:
            self.chunk.set_block(self.torch_pos[0], self.torch_pos[1], self.torch_pos[2],
                                 Block(f"wall_torch[facing={self.bed_facing}]"))

        if progress_ratio > 0.75:
            bed = self.materials["bed"]
            self.chunk.set_block(self.bed_pos[0], self.bed_pos[1], self.bed_pos[2],
                                 Block(f"{bed}[facing={self.bed_facing}]"))
            self.chunk.set_block(self.bed_head_pos[0], self.bed_head_pos[1], self.bed_head_pos[2],
                                 Block(f"{bed}[part=head,facing={self.bed_facing}]"))

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

                self.chunk.set_block(x, self.bed_head_pos[1], z, Block(f"{block_type}[facing={self.bed_facing}]"))

        if progress_ratio > 0.9:
            block = signBlock(
                wall=True,
                facing=self.orientation,
                rotation=0,
                frontLine2=self.agent.name,
                frontLine3=self.agent.job.__str__(),
            )
            self.chunk.set_block(self.sign_x, center_y + 2, self.sign_z, block)

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