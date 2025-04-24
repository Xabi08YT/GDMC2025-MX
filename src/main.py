from concurrent.futures import ThreadPoolExecutor
from json import load
from time import sleep
from gdpc import interface
from Agent import Agent
from utils import agents
from random import randint

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

print("GDMC 2025 MX - Prototype")
print("Fetching map from Minecraft...")
ba = interface.getBuildArea()
offset, size = ba.offset, ba.size
map = interface.getBlocks(offset, size, "overworld", True)
radius = config["radius"]

for i in range(config["nodeAgents"][0]):
    x = randint(-radius, radius)
    z = randint(-radius, radius)
    agents.append(Agent(map, radius, x, 0, z))

def processAgent(agent: Agent):
    print("Starting agent " + agent.name)
    for _ in range(100):
        agent.tick()
        sleep(0.1)
    return

with ThreadPoolExecutor() as executor:
    executor.map(processAgent, agents)

print("Simulation stopped, let's see the progress of the agents")

for agent in agents:
    agent.tickEnable = False
    print("----")
    print("Agent " + agent.name + " - " + agent.current_phase)
    print("Hunger: " + str(agent.needs["hunger"]) + "(" + str(agent.needs_decay["hunger"]) + ")")
    print("Energy: " + str(agent.needs["energy"]) + "(" + str(agent.needs_decay["energy"]) + ")")
    print("Social: " + str(agent.needs["social"]) + "(" + str(agent.needs_decay["social"]) + ")")
    print("Health: " + str(agent.needs["health"]) + "(" + str(agent.needs_decay["health"]) + ")")
    print("Relationships: " + str(agent.relationships))

print("Simulation done")