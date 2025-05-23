import json, os, sys
import random
from shutil import rmtree
from time import time
from buildings.Firecamp import Firecamp
from simLogic.Relationships import Relationships
from utils.ANSIColors import ANSIColors
from visualization.LogFile import LogFile
from gdpc import Editor
from abstractionLayer.AbstractionLayer import AbstractionLayer
from random import randint
from simLogic.Agent import Agent
from simLogic.BoidsBehavior import BoidsBehavior
import numpy as np
from matplotlib import pyplot as plt

class Simulation:

    def __init__(self):
        self.agents = []
        self.creation_time = time()
        self.boids = BoidsBehavior()
        self.walkable = None
        self.wood = None
        self.water = None
        self.lava = None
        self.heightmap = None
        self.buildings = None
        self.hasfarmer = False
        self.relationships = Relationships()

        with open("config/config.json", mode="r") as cfg:
            self.config = json.load(cfg)
            cfg.close()

        with open("config/simParams.json", mode="r") as sim:
            self.params = json.load(sim)
            sim.close()

        with open("txt/agent_names.txt", mode="r") as agent_names:
            self.names = agent_names.readlines()
            agent_names.close()

    def show_message(self, message):
        editor = Editor(buffering=True)
        print("[INFO] " + message)
        editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - ' + message + '","color":"white"}]')

    def post_crash_cleanup(self):
        print(
            f"{ANSIColors.WARNING}[WARN] Simulation seemed to have crashed before cleanup. Initiating cleanup now.{ANSIColors.ENDC}")
        self.clean()
        print(f"{ANSIColors.OKGREEN}[INFO] Post-crash cleanup done.{ANSIColors.ENDC}")


    def prepare(self):
        if os.path.exists(".notCleaned"):
            self.post_crash_cleanup()
        print("GDMC 2025 - MX")
        editor = Editor(buffering=True)
        editor.runCommand('tellraw @a [{"text":"GDMC 2025 - MX","color":"aqua"}]')
        if not os.path.exists("generated"):
            os.mkdir("generated")
        if not os.path.exists("logs"):
            os.mkdir("logs")

        self.show_message("Pulling minecraft map... This may take several minutes...")
        ba = editor.getBuildArea()
        self.abl = AbstractionLayer(ba)
        [self.walkable, self.wood, self.water, self.lava, self.heightmap] = self.abl.pull("--force-pull" in sys.argv or "-fp" in sys.argv)

        if "--showmatrix" in sys.argv or "-sm" in sys.argv or "-s" in sys.argv:
            plt.matshow(self.walkable)
            plt.matshow(self.wood)
            plt.matshow(self.water)
            plt.matshow(self.lava)
            plt.matshow(self.heightmap)
            plt.show()

        self.buildings = np.zeros(self.heightmap.shape,dtype=bool)
        self.show_message("Done. Preparing simulation...")

        for i in range(self.config["nodeAgents"]):
            x = randint(0,self.heightmap.shape[0])
            z = randint(0,self.heightmap.shape[1])
            agent = Agent(self, x=x, z=z, name=random.choice(self.names).strip())
            self.agents.append(agent)

        self.show_message("Simulation ready.")

    def run(self, agents):
        for agent in agents:
            agent.logfile = LogFile(fpath="logs/ongoing", fname=f"{str(agent.id)}.csv")
        for i in range(self.config["nbTurns"]):
            for agent in agents:
                agent.turn = i
                agent.tick()
        for agent in agents:
            agent.logfile.close()

    def launch(self):
        self.show_message("Simulation launched. This may take a while to complete.")
        with open(file=".notCleaned", mode="w") as file:
            file.write("")
            file.close()

        firecamp = Firecamp(self)
        firecamp.build()
        self.firecamp_coords = firecamp.center_point

        self.run(self.agents)

        self.show_message("Simulation ended.")

    def end(self):

        self.show_message("Pushing changes to Minecraft... This may take several minutes.")
        self.abl.push()
        self.show_message("Changes pushed. Beginning cleanup...")

        logfile = LogFile(fname=f'{str(self.creation_time).split(".")[0]}.csv')

        logfile.merge_logs()
        logfile.close()

        self.clean()

        if "--visualize" in sys.argv or "-vs" in sys.argv:
            self.show_message("Done. Visualization server is now running. Please check your browser.")
            from visualization.VisualizeSim import launch_visualization_server
            launch_visualization_server()
        else:
            self.show_message("Done. Goodbye World !")

    def clean(self):
        try:
            for file in os.listdir("logs/ongoing"):
                os.remove(f"logs/ongoing/{file}")
            os.rmdir("logs/ongoing")
        except FileNotFoundError:
            pass

        for folder in os.listdir("generated"):
            rmtree(f"generated/{folder}")

        if os.path.exists(".notCleaned"):
            os.remove(".notCleaned")


if __name__ == "__main__":
    sim = Simulation()
    sim.prepare()
    sim.launch()
    sim.end()
