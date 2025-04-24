from json import load
from time import sleep
from gdpc import interface
from Agent import Agent
import utils

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

print("GDMC 2025 MX - Prototype")
print("Fetching map from Minecraft...")
ba = interface.getBuildArea()
offset, size = ba.offset, ba.size
blocks = interface.getBlocks(offset, size, "overworld", True)

for i in range(config["nodeAgents"][0]):
    utils.agents.append(Agent())

def processAgent(agent: Agent):
    print("Starting agent " + agent.name)
    for _ in range(100):
        agent.tick()
        sleep(0.5)
    return

print("Simulation stopped, let's see the progress of the agents")

for agent in utils.agents:
    agent.tickEnable = False
    print("Agent " + agent.name + " is " + agent.current_phase)

print("Simulation done")