import os
from concurrent.futures import ThreadPoolExecutor
from json import load
from time import sleep
from gdpc import Editor
from Agent import Agent
from AbstractionLayer import AbstractionLayer
from Chunk import Chunk
from random import randint
import sys

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

print("GDMC 2025 MX")
if not os.path.exists("generated"):
    os.mkdir("generated")

print("Fetching map from Minecraft...")
editor = Editor(buffering=True)
ba = editor.getBuildArea()
abl = AbstractionLayer(ba)
try:
    abl.pull(sys.argv[2] == "--force-reload")
except:
    pass
radius = config["radius"]

agents = [Agent(abl, Chunk.LOADED_CHUNKS, radius=radius, x=randint(-radius, radius), z=randint(-radius, radius)) for i in range(config["nodeAgents"][0])]
data = [(agent,config,agents) for agent in agents]

def processAgent(args: tuple[Agent, dict,list[Agent]]):
    print("Starting agent " + args[0].name)
    args[0].all_agents = agents
    for _ in range(0,args[1]["nbTurns"]):
        args[0].tick()
        sleep(0.1)
    return

with ThreadPoolExecutor() as executor:
    executor.map(processAgent, data)

print("Simulation stopped, let's see the progress of the agents")

for agent in agents:
    agent.tickEnable = False
    print("----")
    print(agent.__str__())
    print(agent.job.__str__())
    print("Hunger: " + str(agent.needs["hunger"]) + "(" + str(agent.needs_decay["hunger"]) + ")")
    print("Energy: " + str(agent.needs["energy"]) + "(" + str(agent.needs_decay["energy"]) + ")")
    print("Social: " + str(agent.needs["social"]) + "(" + str(agent.needs_decay["social"]) + ")")
    print("Health: " + str(agent.needs["health"]) + "(" + str(agent.needs_decay["health"]) + ")")
    print("Muscular: " + str(agent.attributes["muscular"]))
    print("Relationships: " + str(agent.relationships))

print("Simulation done")
print("Saving results...")
abl.save_all()
print("Pushing results...")
abl.push()