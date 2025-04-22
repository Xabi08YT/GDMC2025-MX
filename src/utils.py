import os
import json
import random
from json import JSONDecodeError

from multiprocessing import Pool, cpu_count
from gdpc import interface, Editor
from time import sleep

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

            chunk = {}
            for coord,block in tmp:
                chunk[str((coord[0],coord[1],coord[2]))] = (block.id,block.states,block.data)

            with open(file=f"data/{i}_{j}.json", mode="w+") as out:
                json.dump(chunk, out)
                out.close()

    with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
        json.dump({"begin": buildArea.begin.to_list(), "end": buildArea.end.to_list()}, f)
        f.close()

def exec_push_chunk(file):
    os.system(f"python pushChunk.py {file}")

def set_mc_map():
    files = [file
             for file in os.listdir(os.path.join(os.getcwd(), "data"))
             if
                (not os.path.isdir(os.path.join(os.getcwd(), "data", file))
                and file.endswith(".json")
                and not "areaData" in file
                and not "config" in file)
             ]

    p = Pool(cpu_count())
    p.map(exec_push_chunk,files)


if __name__ == "__main__":
    current_editor = Editor(buffering=True)
    buildArea = current_editor.getBuildArea()

    get_mc_map(buildArea)
    set_mc_map()