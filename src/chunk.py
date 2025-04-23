import json
import os
from multiprocessing import Pool, cpu_count
from time import time

from gdpc import interface, Block, Editor

import utils

excluded_files = ["areaData.json", "config.json"]

files = {}

def pull_chunk(args):
    buildArea = utils.current_editor.buildArea()
    tmp = interface.getBlocks(
        (args[0].begin[0] + args[1] * 16, -64, buildArea.begin[2] + args[2] * 16),
        (16, 385, 16)
    )

    chunk = {}
    for coord, block in tmp:
        if buildArea.contains(coord):
            chunk[str((coord[0], coord[1], coord[2]))] = (block.id, block.states, block.data)

    with open(file=f"data/{args[1]}_{args[2]}.json", mode="w+") as out:
        print(f"Saving {args[1]}_{args[2]}.json")
        json.dump(chunk, out)
        out.close()

def pull_mc_map(forceReload=False):
    buildArea = utils.current_editor.getBuildArea()
    start = time()
    print("Pulling minecraft world...")
    size = (buildArea.end[0] - buildArea.begin[0], buildArea.end[1] - buildArea.begin[1],
            buildArea.end[2] - buildArea.begin[2])
    if os.path.exists(os.path.join(os.getcwd(), "data", "areaData.json")) and not forceReload:
        try:
            with open(os.path.join(os.getcwd(), "data", "areaData.json"), "r") as f:
                data = json.load(f)
                f.close()
            if utils.same_point(buildArea.begin, data["begin"]) and utils.same_point(buildArea.end, data["end"]):
                print("Same area, skipping world pulling... If you want to pull it, remove the folder.")
                return
        except json.JSONDecodeError:
            print("Invalid JSON, loading everything...")
        except KeyError:
            print("Invalid JSON, loading everything...")

    if os.path.exists(os.path.join(os.getcwd(), "data")):
        for filename in os.listdir(os.path.join(os.getcwd(), "data")):
            os.remove(os.path.join(os.getcwd(), "data", filename))
        os.rmdir(os.path.join(os.getcwd(), "data"))
    os.mkdir(os.path.join(os.getcwd(), "data"))

    chunks_grid = [(buildArea, x,y) for x in range(size[0]//16+1) for y in range(size[2]//16+1)]

    p = Pool(cpu_count())
    p.map_async(pull_chunk, chunks_grid)
    p.close()
    p.join()

    with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
        json.dump({"begin": buildArea.begin.to_list(), "end": buildArea.end.to_list()}, f)
        f.close()
    end = time()
    print("Minecraft world pulled in {:.2f} seconds.".format(end - start))

def push_chunk(file):
    print(f"Pushing {file} to minecraft world...")
    chunk = json.load(files[file])

    formatted = [
        (
            coord[1:-1].split(","),
            Block(block[0], block[1], block[2])
        ) for coord, block in chunk.items()
    ]

    interface.placeBlocks(formatted, doBlockUpdates=False)

def push_mc_map():
    if len(files.keys()) == 0:
        load_all_files()
    start = time()
    p = Pool(cpu_count())
    t = [key for key in files.keys()]
    p.map_async(push_chunk, t)

    p.close()
    p.join()
    end = time()
    print("Minecraft world pushed in {:.2f} seconds".format(end - start))

def load_all_files():
    global files
    tmp = [(file, os.path.join(os.getcwd(), "data", file))
             for file in os.listdir(os.path.join(os.getcwd(), "data"))
             if
             (not os.path.isdir(os.path.join(os.getcwd(), "data", file))
              and file.endswith(".json")
              and not file in excluded_files)
             ]
    for f,fp in tmp:
        files[f.split(".")[0]] = open(fp, mode="r")

def scan(x, y, z, radius):
    if len(files.keys()) == 0:
        load_all_files()
    buildArea = utils.current_editor.getBuildArea()
    chunk = ((x-buildArea.begin[0])//16, (z-buildArea.begin[2])//16)
    chunkdata = json.load(files[f"{chunk[0]}_{chunk[1]}"])
    relatives = [(-1,-1),(-1,0),(-1,1),
                 (0,-1), (0,1),
                 (1,-1), (1,0), (1,1)]
    for r in relatives:
        try:
            tmp = json.load(files[f"{chunk[0]+r[0]}_{chunk[1]+r[1]}"])
            chunkdata.update(tmp)
        except KeyError:
            pass
    res = {}
    for i in range(x-radius,x+radius+1):
        for j in range(y-radius,y+radius+1):
            for k in range(z-radius,z+radius+1):
                print(chunkdata)
                b = chunkdata[str((i,j,k))]
                res[str((i,j,k))] = Block(b[0], b[1], b[2])
    return res

def close_all_files():
    for f in files:
        files[f].close()


if __name__ == "__main__":
    current_editor = Editor(buffering=True)
    buildArea = current_editor.getBuildArea()

    pull_mc_map(True)
    #load_all_files()
    #print(scan(31, 66, 142,1))
    #push_mc_map()
    #close_all_files()