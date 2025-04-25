import os
from concurrent.futures import ThreadPoolExecutor
from json import load
from time import sleep
from gdpc import interface, Editor
from Agent import Agent
from src.AbstractionLayer import AbstractionLayer
from src.Chunk import Chunk
from utils import agents
from random import randint
import sys

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

print("GDMC 2025 MX - Prototype")
if not os.path.exists("generated"):
    os.mkdir("generated")

print("Fetching map from Minecraft...")
editor = Editor(buffering=True)
ba = editor.getBuildArea()
abl = AbstractionLayer(ba)
abl.pull(sys.argv[2] == "--force-reload")
radius = config["radius"]

data = []

for i in range(config["nodeAgents"][0]):
    x = randint(-radius, radius)
    z = randint(-radius, radius)
    data.append((Agent(world=map, radius=radius, x=x, z=z), abl, Chunk.LOADED_CHUNKS,config))

def processAgent(args: tuple[Agent, AbstractionLayer, list, dict]):
    print("Starting agent " + args[0].name)
    for _ in range(100):
        args[0].tick()
        sleep(0.1)
    return

with ThreadPoolExecutor() as executor:
    executor.map(processAgent, data)

print("Simulation stopped, let's see the progress of the agents")

for agent in agents:
    agent.tickEnable = False
    print("----")
    print("Agent " + agent.name + " - " + agent.current_phase)
    print("Position: " + str(agent.x) + ", " + str(agent.y) + ", " + str(agent.z))
    print("Hunger: " + str(agent.needs["hunger"]) + "(" + str(agent.needs_decay["hunger"]) + ")")
    print("Energy: " + str(agent.needs["energy"]) + "(" + str(agent.needs_decay["energy"]) + ")")
    print("Social: " + str(agent.needs["social"]) + "(" + str(agent.needs_decay["social"]) + ")")
    print("Health: " + str(agent.needs["health"]) + "(" + str(agent.needs_decay["health"]) + ")")
    print("Relationships: " + str(agent.relationships))

print("Simulation done")
print("Saving results...")
abl.save_all()
print("Pushing results...")
abl.push()