import os
import json
import Map

current_editor = None

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def is_flat():
    pass

def get_mc_map(buildArea, interface):
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