import os
import json
import time
from json import JSONDecodeError

import Map
from gdpc import interface, Editor, Block

current_editor = None

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def get_ground_height(x: int, y_start: int, z: int) -> int:
    for y in range(y_start, 0, -1):
        block = [] # block = getBlock from JSON
        if block[0] != "minecraft:air" and not block[0].endswith("leaves"):
            return y
    return 100


def is_flat(x: int, y: int, z: int, radius: int = 2) -> float:
    heights = []
    for dx in range(-radius, radius + 1):
        for dz in range(-radius, radius + 1):
            ny = get_ground_height(x + dx, y + 10, z + dz)
            heights.append(ny)
    variation = max(heights) - min(heights)
    return 1 - min(variation / 5, 1)

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]

def get_mc_map(buildArea, forceReload=False):
    start_time = time.time()
    size = (buildArea.end[0] - buildArea.begin[0], buildArea.end[1] - buildArea.begin[1],
            buildArea.end[2] - buildArea.begin[2])
    if os.path.exists(os.path.join(os.getcwd(), "data", "areaData.json")) and not forceReload:
        try:
            with open(os.path.join(os.getcwd(), "data", "areaData.json"), "r") as f:
                data = json.load(f)
                f.close()
            if same_point(buildArea.begin, data["begin"]) and same_point(buildArea.end, data["end"]):
                return
        except JSONDecodeError:
            print("Invalid JSON, loading everything...")
        except KeyError:
            print("Invalid JSON, loading everything...")

    if os.path.exists(os.path.join(os.getcwd(), "data")):
        for filename in os.listdir(os.path.join(os.getcwd(), "data")):
            os.remove(os.path.join(os.getcwd(), "data", filename))
        os.rmdir(os.path.join(os.getcwd(), "data"))
    os.mkdir(os.path.join(os.getcwd(), "data"))

    for i in range(size[0]//16+1):
        for j in range(size[2]//16+1):
            tmp = interface.getBlocks(
                (buildArea.begin[0] + i*16,-64, buildArea.begin[2] + j*16),
                (16,385,16)
            )

            chunk = {}
            for coord,block in tmp:
                chunk[str((coord[0],coord[1],coord[2]))] = (block.id,block.states,block.data)

            with open(file=f"data/{i}_{j}.json", mode="w+") as out:
                json.dump(chunk, out)
                out.close()

    with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
        json.dump({"begin": buildArea.begin.to_list(), "end": buildArea.end.to_list()}, f)
        f.close()
    end_time = time.time()
    print(f"Map loaded in {end_time - start_time:.2f} seconds")

def set_mc_map():
    for file in os.listdir(os.path.join(os.getcwd(), "data")):
        fpath = os.path.join(os.getcwd(), "data", file)
        if (not os.path.isdir(fpath)
                and file.endswith(".json")
                and not "areaData" in file):

            print(f"Pushing {file} to minecraft world...")
            with open(fpath, mode="r") as data:
                chunk = json.load(data)
                data.close()

            formatted = [
                (
                    coord.replace("(","").replace(")","").split(","),
                    Block(block[0],block[1],block[2])
                ) for coord, block in chunk.items()
            ]

            interface.placeBlocks(formatted, doBlockUpdates=False)

    print("World pushed.")


if __name__ == "__main__":
    current_editor = Editor(buffering=True)
    buildArea = current_editor.getBuildArea()

    get_mc_map(buildArea)
    #set_mc_map()