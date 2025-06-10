import random
from time import time

from gdpc import interface, Editor, Block
from multiprocessing import Pool, cpu_count
import os, json
from buildings.Building import Building
from gdpc.editor_tools import placeContainerBlock
from gdpc.minecraft_tools import signBlock
from utils.math_methods import same_point
from utils.ANSIColors import ANSIColors
import numpy as np
import requests
from buildings.House import House
from simLogic.Job import Job


class AbstractionLayer:
    _AbstractionLayerInstance = None
    wools = ["minecraft:red_wool", "minecraft:blue_wool", "minecraft:green_wool", "minecraft:yellow_wool", "minecraft:orange_wool", "minecraft:purple_wool", "minecraft:light_blue_wool", "minecraft:black_wool", "minecraft:white_wool", "minecraft:lime_wool", "minecraft:gray_wool", "minecraft:light_gray_wool", "minecraft:pink_wool"]

    def __init__(self, buildArea: interface.Box):
        if (AbstractionLayer._AbstractionLayerInstance is not None):
            raise RuntimeError("AbstractionLayer._AbstractionLayerInstance already initialized")
        AbstractionLayer._AbstractionLayerInstance = self
        self.buildArea = buildArea
        with open("config/simParams.json") as json_file:
            self.simParams = json.load(json_file)
            json_file.close()

    @staticmethod
    def pull_chunk(args: tuple[interface.Box, int, int, int, int, np.array, dict]) -> tuple[
        int, int, np.array, np.array, np.array, np.array]:
        tmp = interface.getBlocks(
            (args[0].begin[0] + args[1] * 16, args[3] - 1, args[0].begin[2] + args[2] * 16),
            (16, args[4] - args[3], 16)
        )

        walkable = np.zeros((16, 16), np.bool)
        wood = np.zeros((16, 16), np.bool)
        water = np.zeros((16, 16), np.bool)
        lava = np.zeros((16, 16), np.bool)

        for coord, block in tmp:
            bid = block.id
            mx = coord[0] - args[0].begin[0]
            mz = coord[2] - args[0].begin[2]
            x = coord[0] - (args[0].begin[0] + args[1] * 16)
            z = coord[2] - (args[0].begin[2] + args[2] * 16)

            if mx >= args[5].shape[0] or mz >= args[5].shape[1]:
                continue

            if coord[1] == args[5][mx][mz] - 1:
                wood[x, z] = bid in args[6]["wood"]
                lava[x, z] = bid in args[6]["lava"]
                water[x, z] = bid in args[6]["water"]
                walkable[x, z] = not wood[x, z] and not lava[x, z] and not water[x, z]

        return args[1], args[2], wood, water, lava, walkable

    def get_height_map_excluding(self, blocks):

        with open("config/config.json") as f:
            config = json.load(f)
            f.close()

        if config["GDMC_HTTP_URL"] is None:
            config["GDMC_HTTP_URL"] = "http://localhost:9000"
        url = f'{config["GDMC_HTTP_URL"]}/heightmap?blocks={blocks}'
        heightmap = requests.get(url).json()
        return np.array(heightmap, dtype=int)

    def pull(self, forceReload: bool = False):

        # General setup
        start = time()
        size = (self.buildArea.end[0] - self.buildArea.begin[0], self.buildArea.end[1] - self.buildArea.begin[1],
                self.buildArea.end[2] - self.buildArea.begin[2])

        # Checkin if we can skip pulling everything
        if os.path.exists(os.path.join(os.getcwd(), "data", "areaData.json")) and not forceReload:
            try:
                with open(os.path.join(os.getcwd(), "data", "areaData.json"), "r") as f:
                    data = json.load(f)
                    f.close()
                if same_point(self.buildArea.begin, data["begin"]) and same_point(self.buildArea.end,
                                                                                  data["end"]) and os.path.exists(
                    "data/walkableMatrix") and os.path.exists("data/waterMatrix") and os.path.exists(
                    "data/lavaMatrix") and os.path.exists("data/woodMatrix") and os.path.exists("data/biomeMatrix"):
                    print(
                        f"{ANSIColors.OKCYAN}[NOTE] Same area, skipping world pulling... If you want to pull it again, remove the folder or add the -fp argument to the launch command.{ANSIColors.ENDC}")
                    return [np.load("data/walkableMatrix", allow_pickle=True),
                            np.load("data/woodMatrix", allow_pickle=True),
                            np.load("data/waterMatrix", allow_pickle=True),
                            np.load("data/lavaMatrix", allow_pickle=True),
                            self.get_height_map_excluding("air,%23leaves"),
                            np.load("data/biomeMatrix", allow_pickle=True)]
                print(
                    f"{ANSIColors.WARNING}[WARN] Some files appears to be missing. Initiating pull... {ANSIColors.ENDC}")
            except json.JSONDecodeError:
                print(f"{ANSIColors.WARNING}[WARN] Invalid cache JSON, resuming pulling...{ANSIColors.ENDC}")
            except KeyError:
                print(f"{ANSIColors.WARNING}[WARN] Invalid cache JSON, resuming pulling...{ANSIColors.ENDC}")

        # Cleaning and setting up prerequisites
        if os.path.exists(os.path.join(os.getcwd(), "data")):
            for filename in os.listdir(os.path.join(os.getcwd(), "data")):
                os.remove(os.path.join(os.getcwd(), "data", filename))
            os.rmdir(os.path.join(os.getcwd(), "data"))
        os.mkdir(os.path.join(os.getcwd(), "data"))

        # Getting height between which we will need to pull to have the hole surface
        heightmap = self.get_height_map_excluding("air,%23leaves")
        miny = heightmap.astype(int).min().item()
        maxy = heightmap.astype(int).max().item()

        # Creating arg list for multiprocessing
        chunks_grid = [(self.buildArea, x, y, miny, maxy, heightmap, self.simParams) for x in range(size[0] // 16 + 1)
                       for y in range(size[2] // 16 + 1)]

        # Multiprocessing
        p = Pool(cpu_count())
        results = p.map_async(AbstractionLayer.pull_chunk, chunks_grid).get()
        p.close()
        p.join()

        # Merging results
        shape = (size[0] // 16 + 1) * 16, (size[2] // 16 + 1) * 16
        walkable = np.zeros(shape, np.bool)
        wood = np.zeros(shape, np.bool)
        water = np.zeros(shape, np.bool)
        lava = np.zeros(shape, np.bool)

        for res in results:
            walkable[16 * res[0]:16 * res[0] + 16, 16 * res[1]:16 * res[1] + 16] = res[5]
            lava[16 * res[0]:16 * res[0] + 16, 16 * res[1]:16 * res[1] + 16] = res[4]
            water[16 * res[0]:16 * res[0] + 16, 16 * res[1]:16 * res[1] + 16] = res[3]
            wood[16 * res[0]:16 * res[0] + 16, 16 * res[1]:16 * res[1] + 16] = res[2]

        # Adapting results size
        walkable = walkable[0:size[0], 0:size[2]]
        wood = wood[0:size[0], 0:size[2]]
        water = water[0:size[0], 0:size[2]]
        lava = lava[0:size[0], 0:size[2]]
        biomes = self.get_biome_map()

        # Saving results to cache
        walkable.dump("data/walkableMatrix")
        lava.dump("data/lavaMatrix")
        water.dump("data/waterMatrix")
        wood.dump("data/woodMatrix")
        biomes.dump("data/biomeMatrix")

        with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
            json.dump({"begin": self.buildArea.begin.to_list(), "end": self.buildArea.end.to_list()}, f)
            f.close()
        end = time()
        print("[INFO] Minecraft world pulled in {:.2f} seconds.".format(end - start))
        return walkable, wood, water, lava, heightmap, biomes

    def add_foundation_pillar_to_layer(self,mcx,mcz,mcy,gdpcblocks):
        for fx in range(-1, 1):
            for fz in range(-1, 1):
                gdpcblocks.append(((mcx + fx, mcy, mcz + fz), Block(self.simParams["foundations"]["accent_block"])))

    def push_building(self, args):
        if not os.path.isdir(os.path.join(args[0], args[1])):
            return

        meta = json.load(open(os.path.join(args[0], args[1], "metadata.json")))
        blocks = np.load(os.path.join(args[0], args[1], "matrix"), allow_pickle=True)

        x = meta["x"] - blocks.shape[0] // 2
        mcx = x + self.buildArea.begin[0]
        z = meta["z"] - blocks.shape[1] // 2
        mcz = z + self.buildArea.begin[2]
        mcy = args[2][max(x - 1, 0):min(args[2].shape[0], x + blocks.shape[0] + 1),
              max(z - 1, 0):min(args[2].shape[0], z + blocks.shape[1] + 1)].max().item() - 1
        mcminy = args[3][max(x - 1, 0):min(args[2].shape[0], x + blocks.shape[0] + 1),
                 max(z - 1, 0):min(args[2].shape[0], z + blocks.shape[1] + 1)].min().item()

        gdpcblocks = []
        foundations = mcy - mcminy

        if "firecamp" in meta["name"].lower():
            foundations = -1
            mcy = int(np.average(args[2][x:x + blocks.shape[0],z:z + blocks.shape[1]]).item() - 1)
        if "bridge" in meta["name"].lower():
            mcy = args[2][x:x + blocks.shape[0], z:z + blocks.shape[1]].min().item() - 1

        if "bridge" not in meta["name"].lower():
            for fy in range(foundations):
                for fx in range(blocks.shape[0]):
                    for fz in range(blocks.shape[1]):
                        gdpcblocks.append(((mcx + fx, mcminy + fy, mcz + fz), Block(random.choice(self.simParams["foundations"]["main_blocks"]))))

                self.add_foundation_pillar_to_layer(mcx,mcz,mcminy + fy, gdpcblocks)
                self.add_foundation_pillar_to_layer(mcx,mcz + blocks.shape[1],mcminy + fy, gdpcblocks)
                self.add_foundation_pillar_to_layer(mcx + blocks.shape[0],mcz,mcminy + fy, gdpcblocks)
                self.add_foundation_pillar_to_layer(mcx + blocks.shape[0],mcz + blocks.shape[1],mcminy + fy, gdpcblocks)

            if foundations > 0:
                for fx in range(-1, blocks.shape[0] + 1):
                    for fz in range(-1, blocks.shape[1] + 1):
                        gdpcblocks.append(
                            ((mcx + fx, mcminy + foundations, mcz + fz),
                            Block("minecraft:polished_andesite")))

        if "house" in meta["name"].lower() and meta["happiness"] >= 0.75:
            flowers = ["minecraft:poppy", "minecraft:dandelion", "minecraft:blue_orchid", "minecraft:allium", "minecraft:azure_bluet", "minecraft:red_tulip", "minecraft:orange_tulip", "minecraft:white_tulip", "minecraft:pink_tulip", "minecraft:oxeye_daisy"]
            for fx in range(blocks.shape[0]):
                for fz in range(blocks.shape[1]):
                    if fx == 0 or fx == blocks.shape[0] - 1 or fz == 0 or fz == blocks.shape[1] - 1:
                        if random.randint(0, 10) <= 8:
                            flower = random.choice(flowers)
                            blocks[fx, fz, 1] = flower
        editor = Editor(buffering=True)
        for mx in range(blocks.shape[0]):
            for mz in range(blocks.shape[1]):
                for my in range(blocks.shape[2]):
                    if "house" in meta["name"].lower() and meta["happiness"] < -0.5 and "sign" not in str(blocks[mx, mz, my]) and random.randint(0, 100) < 5:
                            gdpcblocks.append(((mcx + mx, mcy + my, mcz + mz), Block("minecraft:cobweb")))
                    else:
                        if "oak" in str(blocks[mx, mz, my]):
                            wood = None
                            for key in self.simParams["biome"]:
                                if key in meta["biome"]:
                                    wood = self.simParams["biome"][key]
                                    break
                            if wood is None:
                                wood = "oak"
                            block = blocks[mx, mz, my].replace("oak", wood)
                            if "sign" in str(blocks[mx, mz, my]):
                                block = signBlock(wood=wood, facing=meta["orientation"], wall=True, frontLine2=meta["name"].replace(" House", ""), frontLine3="Happiness: " + str(round(meta["happiness"], 2)))
                                gdpcblocks.append(((mcx + mx, mcy + my, mcz + mz), block))
                            else:
                                gdpcblocks.append(((mcx + mx, mcy + my, mcz + mz), Block(block)))
                        elif "house" in meta["name"].lower() and "container" in meta and meta["container"]:
                            if mx == meta["container"][0] and my == meta["container"][1] and mz == meta["container"][2]:
                                pos = (mcx + mx, mcy + my, mcz + mz)
                                block = Block(random.choice(["minecraft:chest", "minecraft:barrel"]))
                                placeContainerBlock(editor, pos, block)
                                items = Job(None).get_items_from_job(meta["job_type"])
                                for i in range(random.randint(3, 7)):
                                    item = random.choice(items)
                                    slot = random.randint(0, 26)
                                    editor.runCommand(
                                        f"item replace block ~ ~ ~ container.{slot} with {item}",
                                        position=pos,
                                        syncWithBuffer=True
                                    )
                                nbt = {
                                    "title": meta["book"]["title"],
                                    "author": meta["book"]["author"],
                                    "pages": meta["book"]["pages"]
                                }
                                nbt_str = json.dumps(nbt)
                                editor.runCommand(
                                    f"item replace block ~ ~ ~ container.{random.randint(0, 26)} with minecraft:written_book[written_book_content={nbt_str}]",
                                    position=pos,
                                    syncWithBuffer=True
                                )
                        else:
                            gdpcblocks.append(((mcx + mx, mcy + my, mcz + mz), Block(blocks[mx, mz, my])))
                            if "building" in meta["name"].lower() and "barrel" in str(blocks[mx, mz, my]):
                                items = Job(None).get_items_from_job(meta["job_type"])
                                for i in range(random.randint(10, 23)):
                                    item = random.choice(items)
                                    slot = random.randint(0, 26)
                                    editor.runCommand(
                                        f"item replace block ~ ~ ~ container.{slot} with {item}",
                                        position=(mcx + mx, mcy + my, mcz + mz),
                                        syncWithBuffer=True
                                    )

        print(
            f'{ANSIColors.OKCYAN}[GDPC INFO] Generated {ANSIColors.ENDC}{ANSIColors.OKGREEN}{meta["name"]}{ANSIColors.ENDC}{ANSIColors.OKCYAN} at {ANSIColors.ENDC}{ANSIColors.OKGREEN}{mcx, mcy, mcz}{ANSIColors.ENDC}')
        interface.placeBlocks(gdpcblocks, doBlockUpdates=meta["bupdates"])

    def push_paths(self, folder, hmap, hmapwater, debug):
        if not os.path.isdir(os.path.join(folder, 'path')):
            return

        blocks = self.simParams["path_blocks"]
        pathmap = np.load(os.path.join(folder, "path", 'pathmap'), allow_pickle=True)
        bridgemap = np.load(os.path.join(folder, "path", 'bridgemap'), allow_pickle=True)

        mcx = self.buildArea.begin[0]
        mcz = self.buildArea.begin[2]

        gdpcblocks = []

        for x in range(pathmap.shape[0]):
            for z in range(pathmap.shape[1]):
                if pathmap[x, z] == 0 and bridgemap[x, z] == 0:
                    continue
                if random.randint(0,101) < 11 and not bridgemap[x][z]:
                    continue
                if not bridgemap[x][z]:
                    b = random.choice(blocks)
                    mcy = hmap[x, z]
                    gdpcblocks.append(((mcx + x, mcy - 1, mcz + z), Block(b)))
                    if debug:
                        gdpcblocks.append(((mcx + x, 200, mcz + z), Block(AbstractionLayer.wools[pathmap[x, z] % len(AbstractionLayer.wools)])))
                else:
                    b = "oak_planks"
                    mcy = hmapwater[x, z]
                    gdpcblocks.append(((mcx + x, mcy - 1, mcz + z), Block(b)))
                    if debug:
                        gdpcblocks.append(((mcx + x, 200, mcz + z), Block("minecraft:oak_planks")))

        interface.placeBlocks(gdpcblocks, doBlockUpdates=False)

    def push(self, agents, debug:bool, folder="generated", ):
        global gdpcblocks
        for building in Building.BUILDINGS:
            building.matrix_to_files()

        hmap = self.get_height_map_excluding(f"air,%23leaves,%23logs,%23replaceable,%23flowers,sugar_cane")
        hmapsolid = self.get_height_map_excluding(f"air,%23leaves,%23logs,%23replaceable,%23flowers,%23dirt,sugar_cane")

        self.clear_trees_for_buildings(folder)

        self.push_paths(folder, hmap,self.get_height_map_excluding("air,%23leaves,%23logs,%23flowers,sugar_cane"), debug)
        p = Pool(cpu_count())
        p.map_async(self.push_building,
                    [(folder, target, hmap, hmapsolid) for target in os.listdir(folder) if target != "path"]).get()
        p.close()
        p.join()

        gdpcblocks = []
        heightmap = self.get_height_map_excluding("air,%23leaves")
        mcx = self.buildArea.begin[0]
        mcz = self.buildArea.begin[2]
        for agent in agents:
            x = int(agent.x)
            z = int(agent.z)
            if agent.dead is True:
                y = heightmap[x, z].item()
                print(f"{ANSIColors.WARNING}[WARN] Agent {agent.name} is dead, placing deadhead at {agent.x, y, agent.z}{ANSIColors.ENDC}")
                gdpcblocks.append(((mcx + x, y, mcz + z), Block(f"minecraft:skeleton_skull[rotation={random.randint(0, 15)}]")))
            elif not isinstance(agent.home, House):
                y = heightmap[x, z].item()
                gdpcblocks.append(((mcx + x, y, mcz + z), Block(f"minecraft:red_carpet")))
                if random.randint(0, 1) == 0:
                    gdpcblocks.append(((mcx + x + random.choice([-1, 1]), y, mcz + z), Block(f"minecraft:white_carpet")))
                else:
                    gdpcblocks.append(((mcx + x, y, mcz + z + random.choice([-1, 1])), Block(f"minecraft:white_carpet")))

        interface.placeBlocks(gdpcblocks, doBlockUpdates=False)

    def clear_trees_for_buildings(self, folder="generated"):
        print(f"{ANSIColors.OKCYAN}[INFO] Clearing trees for buildings...{ANSIColors.ENDC}")
        buildings_data = []

        for target in os.listdir(folder):
            if target == "path":
                continue

            if not os.path.isdir(os.path.join(folder, target)):
                continue

            try:
                meta = json.load(open(os.path.join(folder, target, "metadata.json")))

                if not meta["built"]:
                    continue

                blocks = np.load(os.path.join(folder, target, "matrix"), allow_pickle=True)

                x = meta["x"] - blocks.shape[0] // 2
                z = meta["z"] - blocks.shape[1] // 2
                mcx = x + self.buildArea.begin[0]
                mcz = z + self.buildArea.begin[2]

                buildings_data.append({
                    "name": meta["name"],
                    "x": mcx,
                    "z": mcz,
                    "width": blocks.shape[0],
                    "length": blocks.shape[1],
                    "height": blocks.shape[2]
                })
            except (json.JSONDecodeError, FileNotFoundError, KeyError) as e:
                print(f"{ANSIColors.WARNING}[WARN] Error processing building {target}: {e}{ANSIColors.ENDC}")

        hmap = self.get_height_map_excluding("air")

        gdpcblocks = []
        trees_cleared = 0

        for building in buildings_data:
            buffer = 1
            min_x = building["x"] - buffer
            max_x = building["x"] + building["width"] + buffer
            min_z = building["z"] - buffer
            max_z = building["z"] + building["length"] + buffer

            rel_x_start = max(0, min_x - self.buildArea.begin[0])
            rel_x_end = min(hmap.shape[0], max_x - self.buildArea.begin[0])
            rel_z_start = max(0, min_z - self.buildArea.begin[2])
            rel_z_end = min(hmap.shape[1], max_z - self.buildArea.begin[2])

            if rel_x_end <= rel_x_start or rel_z_end <= rel_z_start:
                continue

            height_section = hmap[rel_x_start:rel_x_end, rel_z_start:rel_z_end]
            if height_section.size == 0:
                continue

            for x in range(min_x, max_x):
                for z in range(min_z, max_z):
                    rel_x = x - self.buildArea.begin[0]
                    rel_z = z - self.buildArea.begin[2]

                    if 0 <= rel_x < hmap.shape[0] and 0 <= rel_z < hmap.shape[1]:
                        y_base = hmap[rel_x, rel_z]
                        for y in range(y_base, y_base + 20):
                            gdpcblocks.append(((x, y, z), Block("minecraft:air")))

            trees_cleared += 1

            if len(gdpcblocks) > 10000:
                interface.placeBlocks(gdpcblocks)
                gdpcblocks = []

        if gdpcblocks:
            interface.placeBlocks(gdpcblocks)

    @staticmethod
    def get_abstraction_layer_instance():
        return AbstractionLayer._AbstractionLayerInstance

    def getBuildArea(self) -> interface.Box:
        return self.buildArea

    def get_biome_map(self):
        with open("config/config.json") as f:
            config = json.load(f)
            f.close()

        if config["GDMC_HTTP_URL"] is None:
            config["GDMC_HTTP_URL"] = "http://localhost:9000"

        x = self.buildArea.begin.x
        z = self.buildArea.begin.z
        dx = self.buildArea.end.x - x
        dz = self.buildArea.end.z - z

        url = f'{config["GDMC_HTTP_URL"]}/biomes?x={x}&z={z}&dx={dx}&dz={dz}&withinBuildArea=true'
        biome_data = requests.get(url).json()
        biome_matrix = np.zeros((dx, dz), dtype=object)
        for entry in biome_data:
            rel_x = entry["x"] - x
            rel_z = entry["z"] - z
            if 0 <= rel_x < dx and 0 <= rel_z < dz:
                biome_matrix[rel_x, rel_z] = entry["id"]
        return biome_matrix


if __name__ == "__main__":
    editor = Editor(buffering=True)
    abl = AbstractionLayer(editor.getBuildArea())
    abl.get_height_map_excluding("air")
