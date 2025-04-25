import json
import os

from gdpc import Block, interface
from pyglm.glm import ivec3
from uuid import uuid4


class Chunk:

    CHUNK_SIZE = 16
    LOADED_CHUNKS = {}

    def __init__(self,chunk: dict[str,Block], name: str = str(uuid4()), folder:str = "data"):
        if chunk is None:
            chunk = {}
        self.chunk = chunk
        self.name = name
        self.folder = folder

    def get_block(self,x,y,z) -> Block:
        return self.chunk[Chunk.coord_to_key(x,y,z)]

    def set_block(self,x:int ,y: int,z: int,block: Block) -> None:
        self.chunk[Chunk.coord_to_key(x,y,z)] = block

    def is_in_chunk(self, x:int, y:int, z:int) -> bool:
        return Chunk.coord_to_key(x,y,z) in self.chunk.keys()

    @staticmethod
    def serialize(data: dict[str, tuple[str,dict,any]]):
        res = {}
        for coord, block in data.items():
            res[coord] = Block(block[0], block[1], block[2])
        return Chunk(res)

    @staticmethod
    def deserialize(chunk) -> dict[str, tuple[str,dict,any]]:
        res = {}
        for coord, block in chunk.chunk.items():
            res[coord] = (block.id,block.states,block.data)
        return res

    @staticmethod
    def from_gdmc(data: list[tuple[ivec3, Block]], name: str):
        if name.replace(".json","") in Chunk.LOADED_CHUNKS.keys():
            return Chunk.LOADED_CHUNKS[name.replace(".json","")]
        cdata = {}
        for coord, block in data:
            if not "void_air" in block.id:
                cdata[Chunk.ivec3_to_key(coord)] = block
        c = Chunk(cdata, name)
        Chunk.LOADED_CHUNKS[c.name] = c
        return c

    def to_gdmc(self):
        return [(Chunk.key_to_coord(coord),block) for coord,block in self.chunk.items()]

    @staticmethod
    def from_file(filename: str, path: str = "data"):
        if filename.replace(".json","") in Chunk.LOADED_CHUNKS.keys():
            return Chunk.LOADED_CHUNKS[filename.replace(".json","")]

        with open(os.path.join(os.getcwd(), path, filename),"r") as f:
            data = json.load(f)
            f.close()
        c = Chunk.serialize(data)
        c.name = filename.replace(".json","")
        Chunk.LOADED_CHUNKS[c.name] = c
        return c

    def to_file(self, filename: str = None, path: str = None):
        if filename is None:
            filename = self.name + ".json"
        if path is None:
            path = self.folder
        print(f"Saving Chunk {self.name} to: {filename}")
        with open(os.path.join(os.getcwd(), path, filename),"w+") as f:
            json.dump(self.deserialize(self), f)
            f.close()
        try:
            Chunk.LOADED_CHUNKS.pop(self.name)
        except KeyError:
            pass
        return

    @staticmethod
    def ivec3_to_key(coord: ivec3) -> str:
        return str((coord[0], coord[1], coord[2]))

    @staticmethod
    def coord_to_key(x,y,z) -> str:
        return str((x, y, z))

    @staticmethod
    def key_to_coord(key):
        return key[1:-1].split(",")

    @staticmethod
    def get_chunk_id_from_coord(buildArea: interface.Box, x:int,z:int) -> tuple[int,int]:
        return x - buildArea.begin[0], z - buildArea.begin[2]