import sys
import json
import os
from gdpc import Block, interface

if __name__ == "__main__":
    print(f"Pushing {sys.argv[1]} to minecraft world...")
    with open(os.path.join(os.getcwd(),"data",sys.argv[1]), mode="r") as data:
        chunk = json.load(data)
        data.close()

    formatted = [
        (
            coord.replace("(", "").replace(")", "").split(","),
            Block(block[0], block[1], block[2])
        ) for coord, block in chunk.items()
    ]

    interface.placeBlocks(formatted, doBlockUpdates=False)