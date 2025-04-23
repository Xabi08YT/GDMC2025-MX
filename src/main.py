from json import load
import random
from time import sleep
from gdpc import Editor, Block
from Agent import Agent
import utils
import threading

from chunk import pull_mc_map, push_mc_map

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

utils.current_editor = Editor(buffering=True)
buildArea = utils.current_editor.getBuildArea()
print("GDMC 2025 MX - Prototype")
utils.current_editor.runCommand('tellraw @a "GDMC - Prototype"')
print("Fetching map from Minecraft...")
utils.current_editor.runCommand('tellraw @a "GDMC - Map extraction started..."')
pull_mc_map()



villageCenter = (random.randint(buildArea.begin[0],buildArea.end[0]), random.randint(buildArea.begin[2],buildArea.end[2]))
center_pos = (villageCenter[0], utils.get_ground_height(villageCenter[0], 200, villageCenter[1])+1, villageCenter[1])
utils.current_editor.placeBlock(center_pos, Block("minecraft:campfire"))
utils.current_editor.runCommand('tellraw @a "GDMC - Map extraction done, simulation started..."')

for i in range(config["nodeAgents"][0]):
    utils.agents.append(Agent(center_pos[0], center_pos[1], center_pos[2], villageCenter))

threads = []
for agent in utils.agents:
    thread = threading.Thread(target=agent.tick)
    threads.append(thread)
    print("Agent " + agent.name + " started")
    thread.start()

sleep(10)

print("Simulation stopped, let's see the progress of the agents")

for agent in utils.agents:
    agent.tickEnable = False
    print("Agent " + agent.name + " is " + agent.current_phase)

for thread in threads:
    thread.join()

utils.current_editor.runCommand('tellraw @a "GDMC - Simulation stopped, pushing new map to Minecraft.."')
print("Simulation stopped, pusing new to map to Minecraft..")
push_mc_map()
utils.current_editor.runCommand('tellraw @a "GDMC - Map pushed, simulation finished"')
print("Simulation finished, let's see the modifications in Minecraft")