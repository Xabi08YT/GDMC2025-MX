from time import time

from gdpc import interface, Editor, Block
from multiprocessing import Pool, cpu_count
import os, json

from buildings.Building import Building
from utils.math_methods import same_point
from utils.ANSIColors import ANSIColors
import numpy as np
import requests

class AbstractionLayer:

    _AbstractionLayerInstance = None

    def __init__(self, buildArea: interface.Box):
        if(AbstractionLayer._AbstractionLayerInstance is not None):
            raise RuntimeError("AbstractionLayer._AbstractionLayerInstance already initialized")
        AbstractionLayer._AbstractionLayerInstance = self
        self.buildArea = buildArea
        with open("config/simParams.json") as json_file:
            self.simParams = json.load(json_file)
            json_file.close()


    @staticmethod
    def pull_chunk(args: tuple[interface.Box,int,int, int, int, np.array, dict] ) -> tuple[int,int,np.array,np.array,np.array,np.array]:
        tmp = interface.getBlocks(
            (args[0].begin[0] + args[1] * 16, args[3]-1, args[0].begin[2] + args[2] * 16),
            (16, args[4] - args[3], 16)
        )

        walkable = np.zeros((16,16), np.bool)
        wood = np.zeros((16,16), np.bool)
        water = np.zeros((16,16), np.bool)
        lava = np.zeros((16,16), np.bool)

        for coord, block in tmp:
            bid = block.id

            x = abs(coord[0] - args[0].begin[0]) - args[1] * 16
            z = abs(coord[2] - args[0].begin[2]) - args[2] * 16

            if coord[1] == args[5][x][z]:
                wood[x, z] = bid in args[6]["wood"]

            if coord[1] == args[5][x][z] - 1:
                lava[x, z] = bid in args[6]["lava"]
                water[x, z] = bid in args[6]["water"]
                walkable[x, z] = not wood[x, z] and not lava[x, z] and not water[x, z]

        return args[1],args[2],wood,water,lava,walkable


    def get_height_map_excluding(self, blocks):

        with open("config/config.json") as f:
            config = json.load(f)
            f.close()

        if config["GDMC_HTTP_URL"] is None:
            config["GDMC_HTTP_URL"] = "http://localhost:9000"
        url = f'{config["GDMC_HTTP_URL"]}/heightmap?blocks={blocks}'
        heightmap = requests.get(url).json()
        return np.array(heightmap, dtype=np.uint)

    def pull(self, forceReload:bool = False):

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
                if same_point(self.buildArea.begin, data["begin"]) and same_point(self.buildArea.end, data["end"]) and os.path.exists("data/walkableMatrix") and os.path.exists("data/waterMatrix") and os.path.exists("data/lavaMatrix") and os.path.exists("data/woodMatrix"):
                    print(f"{ANSIColors.OKCYAN}[NOTE] Same area, skipping world pulling... If you want to pull it again, remove the folder or add the -fp argument to the launch command.{ANSIColors.ENDC}")
                    return [np.load("data/walkableMatrix",allow_pickle=True), np.load("data/woodMatrix",allow_pickle=True), np.load("data/waterMatrix",allow_pickle=True), np.load("data/lavaMatrix",allow_pickle=True), self.get_height_map_excluding("air&#leaves")]
                print(f"{ANSIColors.WARNING}[WARN] Some files appears to be missing. Initiating pull... {ANSIColors.ENDC}")
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
        heightmap = self.get_height_map_excluding("air&#leaves")
        miny = heightmap.astype(int).min()
        maxy = heightmap.astype(int).max()

        # Creating arg list for multiprocessing
        chunks_grid = [(self.buildArea, x, y, miny, maxy, heightmap, self.simParams) for x in range(size[0] // 16 + 1) for y in range(size[2] // 16 + 1)]

        # Multiprocessing
        p = Pool(cpu_count())
        results = p.map_async(AbstractionLayer.pull_chunk, chunks_grid).get()
        p.close()
        p.join()

        # Merging results
        shape = (size[0] // 16 + 1) * 16,(size[2] // 16 + 1) * 16
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

        # Saving results to cache
        walkable.dump("data/walkableMatrix")
        lava.dump("data/lavaMatrix")
        water.dump("data/waterMatrix")
        wood.dump("data/woodMatrix")

        with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
            json.dump({"begin": self.buildArea.begin.to_list(), "end": self.buildArea.end.to_list()}, f)
            f.close()
        end = time()
        print("[INFO] Minecraft world pulled in {:.2f} seconds.".format(end - start))
        return [walkable, wood, water, lava, heightmap]

    def push_building(self,args):
        if not os.path.isdir(os.path.join(args[0],args[1])):
            return

        meta = json.load(open(os.path.join(args[0],args[1],"metadata.json")))
        blocks = np.load(os.path.join(args[0],args[1],"matrix"), allow_pickle=True)


        x = meta["x"] - blocks.shape[0] // 2
        mcx = x + self.buildArea.begin[0]
        z = meta["z"] - blocks.shape[1] // 2
        mcz = z + self.buildArea.begin[2]
        mcy = args[2][x:x+blocks.shape[0],z:z+blocks.shape[1]].min().item() - 1
        print(meta["name"],mcx,mcy,mcz)

        gdpcblocks = []

        for mx in range(blocks.shape[0]):
            for mz in range(blocks.shape[1]):
                for my in range(blocks.shape[2]):
                    gdpcblocks.append(((mcx+mx, mcy+my,mcz+mz), Block(blocks[mx,mz,my])))

        for block in gdpcblocks:
            if getattr(block[1], "id", None) == "minecraft:campfire":
                print(f"firecamp : {block}")
        interface.placeBlocks(gdpcblocks)


    def push(self, folder="generated"):
        for building in Building.BUILDINGS:
            building.matrix_to_files()
        p = Pool(cpu_count())
        hmap = self.get_height_map_excluding("air&#leaves")
        p.map_async(self.push_building, [(folder,target, hmap) for target in os.listdir(folder)]).get()
        p.close()
        p.join()

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
        print(x, z, dx, dz)
        url = f'{config["GDMC_HTTP_URL"]}/biomes?x={x}&z={z}&dx={dx}&dz={dz}&withinBuildArea=true'
        biome = requests.get(url).json()
        index_map = {(entry["x"], entry["z"]): entry["id"] for entry in biome}
        return index_map

if __name__ == "__main__":
    editor = Editor(buffering=True)
    abl = AbstractionLayer(editor.getBuildArea())
    abl.get_height_map_excluding("air")