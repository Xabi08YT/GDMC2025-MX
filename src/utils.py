import os
import json
from json import JSONDecodeError

import Map
from gdpc import interface, Editor

current_editor = None

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def is_flat():
    pass

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]

def get_mc_map(buildArea, forceReload=False):
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

            chunkVertSlice = {}
            for coord,block in tmp:
                chunkVertSlice[str((coord[0],coord[1],coord[2]))] = (block.id,block.states,block.data)

            with open(file=f"data/{i}_{j}.json", mode="w+") as out:
                json.dump(chunkVertSlice, out)
                out.close()

    with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
        json.dump({"begin": buildArea.begin.to_list(), "end": buildArea.end.to_list()}, f)
        f.close()

def set_mc_map(map: Map, interface):
    for i in range(map.size[0]//16+1):
        for j in range(map.size[2]//16+1):
            with open(file=f"data/{i}_{j}.json", mode="r") as inFile:
                chunkVertSlice = json.load(inFile)
                inFile.close()

            for coord,block in chunkVertSlice.items():
                for y,blockData in block.items():
                    interface.setBlock(
                        (int(coord[0]),int(y),int(coord[2])),
                        blockData[0],
                        blockData[1],
                        blockData[2]
                    )


if __name__ == "__main__":
    current_editor = Editor(buffering=True)
    buildArea = current_editor.getBuildArea()

    get_mc_map(buildArea)