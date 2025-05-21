import csv, sys, os
from os import getcwd, path, mkdir
from time import time


class LogFile:

    def __init__(self, fpath="logs", fname=None):
        try:
            mkdir(fpath)
        except FileExistsError:
            pass
        self.file = open(path.join(getcwd(), fpath, f'{str(time()).split(".")[0]}.csv'),
                         "w+") if fname is None else open(path.join(getcwd(), fpath, fname), "w+")
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
            "coord_x",
            "coord_z"
        ])
        self.dictWriter.writeheader()

    def addLine(self, agent, priority_need: str):

        actions = {"hunger": "eat", "social": "socializing", "energy": "sleep", "health": "moving"}
        action_made = actions.get(priority_need)
        if action_made == "None":
            action_made = "explore"

        data = {
            "id": agent.id,
            "name": agent.name,
            "action": action_made,
            "turn": agent.turn,
            "job": agent.job,
            "hunger": agent.attributes["hunger"],
            "social": agent.attributes["social"],
            "energy": agent.attributes["energy"],
            "health": agent.attributes["health"],
            "happiness": agent.happiness,
            "happiness_decay": agent.happiness_decay,
            "hunger_decay": agent.decay_rates["hunger"],
            "social_decay": agent.decay_rates["social"],
            "energy_decay": agent.decay_rates["energy"],
            "health_decay": agent.decay_rates["health"],
            "attributes": agent.attributes,
            "coord_x": agent.x,
            "coord_z": agent.z,
        }

        self.dictWriter.writerow(data)

    def close(self):
        self.file.close()

    def merge_logs(self, fpath="logs/ongoing"):
        for file in os.listdir(fpath):
            if not file.endswith(".csv"):
                continue
            with open(path.join(getcwd(), fpath, file), "r") as f:
                dict_reader = csv.DictReader(f, fieldnames=[
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
                    "coord_x",
                    "coord_z"
                ])
                for row in dict_reader:
                    if row["id"] == "id":
                        continue
                    self.dictWriter.writerow(row)
                f.close()
        return
