from json import load
import random
from time import sleep
from gdpc import Editor
from Agent import Agent
import utils
import threading

from src.chunk import pull_mc_map, push_mc_map

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

utils.current_editor = Editor(buffering=True)
buildArea = utils.current_editor.getBuildArea()

pull_mc_map(buildArea)

villageCenter = (random.randint(buildArea.begin[0],buildArea.end[0]), random.randint(buildArea.begin[2],buildArea.end[2]))

for i in range(config["nodeAgents"][0]):
    utils.agents.append(Agent())


threads = []
for agent in utils.agents:
    thread = threading.Thread(target=agent.tick)
    threads.append(thread)
    print("Agent " + agent.name + " started")
    thread.start()

sleep(10)

for agent in utils.agents:
    agent.tickEnable = False
    print("Agent " + agent.name + " is " + agent.current_phase)

for thread in threads:
    thread.join()

push_mc_map()

print("Simulation stopped, let's see the modifications in Minecraft")
