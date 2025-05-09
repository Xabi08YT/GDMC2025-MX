import csv
from os import getcwd, path, mkdir
from time import time

class LogFile:

    def __init__(self, fpath =  "logs"):
        if not path.exists(fpath):
            mkdir(fpath)
        self.file = open(path.join(getcwd(), fpath, f"{str(time()).split(".")[0]}.csv"), "w+")
        self.dictWriter = csv.DictWriter(self.file, fieldnames=[
            "id",
            "name",
            "action",
            "turn",
            "job",
            "hunger",
            "social",
            "energy",
            "health",
            "happiness",
            "happiness_decay",
            "hunger_decay",
            "social_decay",
            "energy_decay",
            "health_decay",
            "attributes",
            "relationships",
            "observations",
            "coord_x",
            "coord_y",
            "coord_z"
        ])
        self.dictWriter.writeheader()
        self.turn = {}

    def addLine(self, agent, priority_need: str):

        actions = {"hunger":"eat","social":"socializing","energy":"sleep","health":"moving"}
        action_made = actions.get(priority_need)
        if action_made == "None":
            action_made = "explore"

        data = {
            "id": agent.id,
            "name": agent.name,
            "action": action_made,
            "turn": self.turn[agent.id],
            "job": agent.job,
            "hunger": agent.needs["hunger"],
            "social": agent.needs["social"],
            "energy": agent.needs["energy"],
            "health": agent.needs["health"],
            "happiness": agent.happiness,
            "happiness_decay": agent.happiness_decay,
            "hunger_decay": agent.needs_decay["hunger"],
            "social_decay": agent.needs_decay["social"],
            "energy_decay": agent.needs_decay["energy"],
            "health_decay": agent.needs_decay["health"],
            "attributes": agent.attributes,
            "relationships": agent.relationships,
            "observations": agent.observations,
            "coord_x": agent.x,
            "coord_y": agent.y,
            "coord_z": agent.z,
        }

        self.dictWriter.writerow(data)

    def close(self):
        self.file.close()