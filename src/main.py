from json import load
import random
from multiprocessing import Pool
from os import cpu_count
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
utils.current_editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Prototype","color":"white"}]')
print("Fetching map from Minecraft...")
utils.current_editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction started. It may take several minutes.","color":"white"}]')
pull_mc_map()



villageCenter = (random.randint(buildArea.begin[0],buildArea.end[0]), random.randint(buildArea.begin[2],buildArea.end[2]))
center_pos = (villageCenter[0], utils.get_ground_height(villageCenter[0], 200, villageCenter[1])+1, villageCenter[1])
utils.current_editor.placeBlock(center_pos, Block("minecraft:campfire"))
utils.current_editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction done, simulation started.","color":"white"}]')

for i in range(config["nodeAgents"][0]):
    utils.agents.append(Agent(center_pos[0], center_pos[1], center_pos[2], villageCenter))

def processAgent(agent: Agent):
    print("Starting agent " + agent.name)
    for _ in range(100):
        agent.tick()
        sleep(0.1)
    return


p = Pool(cpu_count())
print(p.map_async(processAgent, utils.agents).get())
p.close()
p.join()

print("Simulation stopped, let's see the progress of the agents")

for agent in utils.agents:
    agent.tickEnable = False
    print("Agent " + agent.name + " is " + agent.current_phase)

for thread in threads:
    thread.join()

utils.connect_houses_to_center()

utils.current_editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Pushing new map. It may tell several minutes.","color":"white"}]')
print("Simulation stopped, pusing new to map to Minecraft..")
push_mc_map()
utils.current_editor.runCommand('tellraw @a [{"text":"GDMC","color":"cyan"},{"text":" - Map pushed. The program has now ended.","color":"white"}]')
print("Simulation finished, let's see the modifications in Minecraft")