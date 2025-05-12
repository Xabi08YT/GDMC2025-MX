import json, os, sys

from LogFile import LogFile
from gdpc import Editor
from AbstractionLayer import AbstractionLayer
from random import randint


class Simulation:
    def __init__(self):
        self.agents = []
        self.logfile = LogFile()
        self.have_farmer = False

        with open("config.json", mode="r") as cfg:
            self.config = json.load(cfg)
            cfg.close()

        with open("simulation.json", mode="r") as sim:
            self.params = json.load(sim)
            sim.close()

    def prepare(self):
        print("GDMC 2025 - MX")
        self.editor = Editor(buffering=True)
        self.editor.runCommand('tellraw @a [{"text":"GDMC 2025 - MX","color":"aqua"}]')
        if not os.path.exists("generated"):
            os.mkdir("generated")
        print("Fetching map from Minecraft...")
        self.editor.runCommand(
            'tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction started. It may take several minutes.","color":"white"}]')
        self.ba = self.editor.getBuildArea()
        self.abl = AbstractionLayer(self.ba)
        try:
            self.abl.pull(sys.argv[2] == "--force-reload")
        except:
            pass

        self.min_x, self.min_z = self.ba.begin[0], self.ba.begin[2]
        self.max_x, self.max_z = self.ba.end[0] - 1, self.ba.end[2] - 1

        for i in range(self.config["nodeAgents"][0]):
            x = randint(self.min_x, self.max_x)
            z = randint(self.min_z, self.max_z)
            agent = Agent(self.abl, Chunk.LOADED_CHUNKS, self.logfile, radius=radius, x=x, z=z,
                          center_village=(firecamp.get_coords().x, firecamp.get_coords().z),
                          observation_range=self.config["observationRange"])
            self.agents.append(agent)