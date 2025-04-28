from Chunk import Chunk
from time import time
from gdpc import interface, Editor
from multiprocessing import Pool, cpu_count
import os, json, utils


class AbstractionLayer:

    _AbstractionLayerInstance = None

    def __init__(self, buildArea: interface.Box):
        if(AbstractionLayer._AbstractionLayerInstance is not None):
            raise RuntimeError("AbstractionLayer._AbstractionLayerInstance already initialized")
        AbstractionLayer._AbstractionLayerInstance = self
        self.buildArea = buildArea

    @staticmethod
    def pull_chunk(args: tuple[interface.Box,int,int]) -> None:
        tmp = interface.getBlocks(
            (args[0].begin[0] + args[1] * 16, -64, args[0].begin[2] + args[2] * 16),
            (16, 385, 16)
        )

        chunk = Chunk.from_gdmc(tmp, f"{args[1]}_{args[2]}")
        chunk.to_file()

    def pull(self, forceReload:bool =False):
        start = time()
        print("Pulling minecraft world...")
        size = (self.buildArea.end[0] - self.buildArea.begin[0], self.buildArea.end[1] - self.buildArea.begin[1],
                self.buildArea.end[2] - self.buildArea.begin[2])
        if os.path.exists(os.path.join(os.getcwd(), "data", "areaData.json")) and not forceReload:
            try:
                with open(os.path.join(os.getcwd(), "data", "areaData.json"), "r") as f:
                    data = json.load(f)
                    f.close()
                if utils.same_point(self.buildArea.begin, data["begin"]) and utils.same_point(self.buildArea.end, data["end"]):
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

        chunks_grid = [(self.buildArea, x, y) for x in range(size[0] // 16 + 1) for y in range(size[2] // 16 + 1)]

        p = Pool(cpu_count())
        p.map_async(AbstractionLayer.pull_chunk, chunks_grid)
        p.close()
        p.join()

        with open(os.path.join(os.getcwd(), "data", "areaData.json"), "w+") as f:
            json.dump({"begin": self.buildArea.begin.to_list(), "end": self.buildArea.end.to_list()}, f)
            f.close()
        end = time()
        print("Minecraft world pulled in {:.2f} seconds.".format(end - start))

    def get_chunk(self,x,z) -> Chunk:
        cid = Chunk.get_chunk_id_from_coord(self.buildArea, x, z)
        return Chunk.from_file(f"{cid[0]}_{cid[1]}.json")

    def save_all(self):
        for chunk in Chunk.LOADED_CHUNKS.keys():
            Chunk.LOADED_CHUNKS[chunk].to_file(filename=f"{chunk.name}.json", path=chunk.path)
        Chunk.LOADED_CHUNKS.clear()

    def push(self, folder="generated"):
        self.save_all()
        for file in os.listdir(folder):
            if file.endswith(".json"):
                c = Chunk.from_file(file,folder)
                interface.placeBlocks(c.to_gdmc(), doBlockUpdates=False)

    @staticmethod
    def get_abstraction_layer_instance():
        return AbstractionLayer._AbstractionLayerInstance

if __name__ == "__main__":
    editor = Editor(buffering=True)
    abl = AbstractionLayer(editor.getBuildArea())
    abl.pull()
    abl.save_all()
    abl.push()