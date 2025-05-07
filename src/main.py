import os
import sys
from json import load
from time import sleep
from gdpc import Editor
from gdpc.vector_tools import ivec3
from Agent import Agent
from AbstractionLayer import AbstractionLayer
from Chunk import Chunk
from random import randint
from Firecamp import Firecamp
from LogFile import LogFile

with open("config.json", mode="r") as cfg:
    config: dict = load(cfg)
    cfg.close()

logfile = LogFile()

print("GDMC 2025 - MX")
editor = Editor(buffering=True)
editor.runCommand('tellraw @a [{"text":"GDMC 2025 - MX","color":"aqua"}]')
if not os.path.exists("generated"):
    os.mkdir("generated")

print("Fetching map from Minecraft...")
editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction started. It may take several minutes.","color":"white"}]')
ba = editor.getBuildArea()
abl = AbstractionLayer(ba)
try:
    abl.pull(sys.argv[2] == "--force-reload")
except:
    pass
radius = config["radius"]

min_x, min_z = ba.begin[0], ba.begin[2]
max_x, max_z = ba.end[0] - 1, ba.end[2] - 1

firecamp_x, firecamp_z = randint(min_x, max_x), randint(min_z, max_z)
firecamp = Firecamp(ivec3(firecamp_x, abl.get_chunk(firecamp_x, firecamp_z).getGroundHeight(firecamp_x, firecamp_z)+1, firecamp_z))

agents = []
for i in range(config["nodeAgents"][0]):
    x = randint(min_x, max_x)
    z = randint(min_z, max_z)
    agent = Agent(abl, Chunk.LOADED_CHUNKS, logfile, radius=radius, x=x, z=z, center_village=(firecamp.get_coords().x, firecamp.get_coords().z), observation_range=config["observationRange"])
    agents.append(agent)

data = [(agent, config, agents) for agent in agents]

def processAgent(args: tuple[Agent, dict, list[Agent]]):
    agent, config_data, all_agents = args
    agent.all_agents = all_agents
    for i in range(0, config_data["nbTurns"]):
        logfile.turn[args[0].id] = i
        agent.tick()
        if agent.home.built == False and i > config_data["nbTurns"]/2 and randint(0, 10) > 3:
            agent.place_house()
        sleep(0.05)
    return

print("Map extraction done, starting simulation")
editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Map extraction done, starting simulation","color":"white"}]')

firecamp.build(abl)

for data_item in data:
    processAgent(data_item)

print("Simulation stopped, let's see the progress of the agents")
editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Simulation stopped","color":"white"}]')

for agent in agents:
    agent.tickEnable = False
    print("----")
    print(agent.__repr__())
    print(agent.job.__repr__())
    print("Home: " + agent.home.__str__())
    print("Hunger: " + str(agent.needs["hunger"]) + "(" + str(agent.needs_decay["hunger"]) + ")")
    print("Energy: " + str(agent.needs["energy"]) + "(" + str(agent.needs_decay["energy"]) + ")")
    print("Social: " + str(agent.needs["social"]) + "(" + str(agent.needs_decay["social"]) + ")")
    print("Health: " + str(agent.needs["health"]) + "(" + str(agent.needs_decay["health"]) + ")")
    print("Muscular: " + str(agent.attributes["muscular"]))
    print("Observations: " + str(agent.observations))
    print("Relationships:")
    for relationship, details in agent.relationships.items():
        print(f"\t-{relationship}: {details.__repr__()}")

print("Simulation done, saving results...")
abl.save_all()
logfile.close()
print("Pushing results...")
abl.push()
for file in os.listdir("generated"):
    os.remove(os.path.join("generated", file))
editor.runCommand('tellraw @a [{"text":"GDMC","color":"aqua"},{"text":" - Modifications pushed","color":"white"}]')
print("Done! Let's see the modifications in Minecraft!")
editor.runCommand(f'tellraw @a [{{"text":"GDMC","color":"aqua"}},{{"text":" - Center of the village: ","color":"white"}},{{"text":"({firecamp.center_point.x}, {firecamp.center_point.y}, {firecamp.center_point.z})","color":"yellow","clickEvent":{{"action":"run_command","value":"/tp @s {firecamp.center_point.x} {firecamp.center_point.y} {firecamp.center_point.z}"}},"hoverEvent":{{"action":"show_text","value":"Click to teleport"}}}}]')