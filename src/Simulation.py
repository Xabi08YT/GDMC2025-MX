import json, os, sys
from time import time

from buildings.Firecamp import Firecamp
from utils.ANSIColors import ANSIColors
from visualization.LogFile import LogFile
from gdpc import Editor
from abstractionLayer.AbstractionLayer import AbstractionLayer
from random import randint
from simLogic.Agent import Agent
from abstractionLayer.Chunk import Chunk
from multiprocessing import Pool, cpu_count
from simLogic.BoidsBehavior import BoidsBehavior


class Simulation:
    LOADED_CHUNKS = Chunk.LOADED_CHUNKS

    def __init__(self):
        self.agents = []
        self.creation_time = time()
        self.boids = BoidsBehavior()
        # self.relationships = Relationships()

        with open("config/config.json", mode="r") as cfg:
            self.config = json.load(cfg)
            cfg.close()

        with open("config/simParams.json", mode="r") as sim:
            self.params = json.load(sim)
            sim.close()

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

        if os.path.exists(".hasfarmer"):
            os.remove(".hasfarmer")
        self.show_message("Pulling minecraft map... This may take several minutes...")
        ba = editor.getBuildArea()
        self.abl = AbstractionLayer(ba)
        try:
            self.abl.pull("--force-pull" in sys.argv or "-fp" in sys.argv)
        except:
            pass

        self.show_message("Done. Preparing simulation...")

        self.min_x, self.min_z = ba.begin[0], ba.begin[2]
        self.max_x, self.max_z = ba.end[0] - 1, ba.end[2] - 1

        for i in range(self.config["nodeAgents"][0]):
            x = randint(self.min_x, self.max_x)
            z = randint(self.min_z, self.max_z)
            c = self.abl.get_chunk(x, z)
            y = c.getGroundHeight(x, z)
            agent = Agent(self, x, y, z)
            self.agents.append(agent)

        self.show_message("Simulation ready.")

    def run(self, agent):
        agent.logfile = LogFile(fpath="logs/ongoing", fname=f"{str(agent.id)}.csv")
        for i in range(self.config["nbTurns"]):
            agent.turn = i
            agent.tick()
        agent.logfile.close()

    def launch(self):
        self.show_message("Simulation launched. This may take a while to complete.")
        with open(file=".notCleaned", mode="w") as file:
            file.write("")
            file.close()

        firecamp = Firecamp(self)
        firecamp.get_best_location()
        firecamp.build()
        coords = firecamp.get_coords()

        editor = Editor(buffering=True)
        editor.runCommand(
            f'tellraw @a [{{"text":"GDMC","color":"aqua"}},{{"text":" - Center of the village: ","color":"white"}},{{"text":"({firecamp.center_point.x}, {firecamp.center_point.y}, {firecamp.center_point.z})","color":"yellow","clickEvent":{{"action":"run_command","value":"/tp @s {firecamp.center_point.x} {firecamp.center_point.y} {firecamp.center_point.z}"}},"hoverEvent":{{"action":"show_text","value":"Click to teleport"}}}}]')

        print(
            f"{ANSIColors.OKBLUE}[SIMULATION INFO] Firecamp has been placed at {ANSIColors.ENDC}{ANSIColors.OKGREEN}{coords[0], coords[1], coords[2]}{ANSIColors.ENDC}")

        p = Pool(cpu_count())
        p.map_async(self.run, self.agents).get()
        p.close()
        p.join()

        self.show_message("Simulation ended.")

    def end(self):

        self.show_message("Pushing changes to Minecraft... This may take several minutes.")

        self.abl.save_all()
        self.abl.push()

        self.show_message("Changes pushed. Beginning cleanup...")

        logfile = LogFile(fname=f"{str(self.creation_time).split(".")[0]}.csv")

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
        for file in os.listdir("logs/ongoing"):
            os.remove(f"logs/ongoing/{file}")
        os.rmdir("logs/ongoing")

        if os.path.exists(".hasfarmer"):
            os.remove(".hasfarmer")

        for file in os.listdir("generated"):
            os.remove(f"generated/{file}")

        if os.path.exists(".notCleaned"):
            os.remove(".notCleaned")


if __name__ == "__main__":
    sim = Simulation()
    sim.prepare()
    sim.launch()
    sim.end()
