import json
import os
from json import load

from Agent import Agent
from Map import Map
from gdpc import Editor, interface, vector_tools

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

editor = Editor(buffering=True)
buildArea = editor.getBuildArea()

#def getMcMap():
#    size = (buildArea.end[0] - buildArea.begin[0], buildArea.end[1] - buildArea.begin[1], buildArea.end[2] - buildArea.begin[2])
#    blocks = interface.getBlocks(buildArea.begin,size)
#    return blocks

def getMcMap():
    size = (buildArea.end[0] - buildArea.begin[0], buildArea.end[1] - buildArea.begin[1],
            buildArea.end[2] - buildArea.begin[2])
    for i in range(size[0]//16+1):
        for j in range(size[2]//16+1):
            tmp = interface.getBlocks(
                (buildArea.begin[0] + i*16,-64, buildArea.begin[2] + j*16),
                (16,385,16)
            )

            chunkVertSlice = {}
            for coord,block in tmp:
                if str((coord[0],coord[2])) not in chunkVertSlice:
                    chunkVertSlice[str((coord[0],coord[2]))] = {}
                chunkVertSlice[str((coord[0],coord[2]))][coord[1]] = (block.id,block.states,block.data)

            if not os.path.exists(os.path.join(os.getcwd(), "data")):
                os.mkdir(os.path.join(os.getcwd(), "data"))
            with open(file=f"data/{i}_{j}.json", mode="w+") as out:
                json.dump(chunkVertSlice, out)
                out.close()

getMcMap()