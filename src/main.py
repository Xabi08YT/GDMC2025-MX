from json import load
from time import sleep
from gdpc import Editor
from Agent import Agent
import utils
import threading

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

utils.current_editor = Editor(buffering=True)
buildArea = utils.current_editor.getBuildArea()

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

print("Simulation stopped, let's see the modifications in Minecraft")
