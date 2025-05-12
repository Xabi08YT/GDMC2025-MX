import json, os, sys
from datetime import time

from LogFile import LogFile
from gdpc import Editor
from AbstractionLayer import AbstractionLayer
from random import randint
from Agent import Agent
from Chunk import Chunk
from multiprocessing import Pool, cpu_count

class Simulation:

    LOADED_CHUNKS = Chunk.LOADED_CHUNKS

    def __init__(self):
        self.agents = []
        self.have_farmer = False
        self.creation_time = time()

        with open("config.json", mode="r") as cfg:
            self.config = json.load(cfg)
            cfg.close()

        with open("simParams.json", mode="r") as sim:
            self.params = json.load(sim)
            sim.close()

    def prepare(self):
        print("GDMC 2025 - MX")
        editor = Editor(buffering=True)
        editor.runCommand('tellraw @a [{"text":"GDMC 2025 - MX","color":"aqua"}]')
        if not os.path.exists("generated"):
            os.mkdir("generated")
        print("Fetching map from Minecraft...")
        editor.runCommand(
            'tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction started. It may take several minutes.","color":"white"}]')
        ba = editor.getBuildArea()
        self.abl = AbstractionLayer(ba)
        try:
            self.abl.pull(sys.argv[2] == "--force-reload")
        except:
            pass

        self.min_x, self.min_z = ba.begin[0], ba.begin[2]
        self.max_x, self.max_z = ba.end[0] - 1, ba.end[2] - 1

        for i in range(self.config["nodeAgents"][0]):
            x = randint(self.min_x, self.max_x)
            z = randint(self.min_z, self.max_z)
            c = self.abl.get_chunk(x,z)
            y = c.getGroundHeight(x,z)
            agent = Agent(self, x, y, z)
            self.agents.append(agent)

    def run(self, agent):
        agent.logfile = LogFile(fpath="logs/ongoing", fname=f"{str(agent.id)}.csv")
        for i in range(self.config["nbTurns"]):
            agent.turn = i
            agent.tick()
        agent.logfile.close()

    def launch(self):
        p = Pool(cpu_count())
        p.map_async(self.run, self.agents).get()
        p.close()
        p.join()

if __name__ == "__main__":
    sim = Simulation()
    sim.prepare()
    sim.launch()