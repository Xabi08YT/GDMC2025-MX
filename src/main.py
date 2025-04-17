from json import load

from Agent import Agent
from Map import Map
from gdpc import Editor, interface, vector_tools

with open("config.json", mode="r") as cfg:
    config = load(cfg)
    cfg.close()

editor = Editor(buffering=True)
buildArea = editor.getBuildArea()

def getMcMap():
    size = (buildArea.end[0] - buildArea.begin[0], buildArea.end[1] - buildArea.begin[1], buildArea.end[2] - buildArea.begin[2])
    blocks = interface.getBlocks(buildArea.begin,size)
    return blocks

mcmap = Map(getMcMap())
print(mcmap.get_block(1,1,1))
print(mcmap.get_blocks(1,1,1,4,4,4))
agents = []
for i in cfg:
    for j in range(i):
        agents.append(Agent(mcmap))