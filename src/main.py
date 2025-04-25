import os
import sys
from json import load
from time import sleep
from gdpc import Editor
from Agent import Agent
from AbstractionLayer import AbstractionLayer
from Chunk import Chunk
from random import randint

with open("config.json", mode="r") as cfg:
    config: dict = load(cfg)
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

agents = []
for i in range(config["nodeAgents"][0]):
    x = randint(-radius//2, radius//2)
    z = randint(-radius//2, radius//2)
    agent = Agent(abl, Chunk.LOADED_CHUNKS, radius=radius, x=x, z=z, center_village=(0, 0))
    agents.append(agent)

data = [(agent, config, agents) for agent in agents]

def processAgent(args: tuple[Agent, dict, list[Agent]]):
    agent, config_data, all_agents = args
    agent.all_agents = all_agents
    for _ in range(0, config_data["nbTurns"]):
        agent.tick()
        sleep(0.05)
    return

for data_item in data:
    processAgent(data_item)

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
    print("Relationships:")
    for relationship, details in agent.relationships.items():
        print(f"\t-{relationship}: {details.__str__()}")

print("Simulation done")
print("Saving results...")
abl.save_all()
print("Pushing results...")
abl.push()
print("Cleaning up...")
for file in os.listdir("generated"):
    os.remove(os.path.join("generated", file))
print("Goodbye world !")