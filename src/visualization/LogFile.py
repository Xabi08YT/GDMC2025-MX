import csv, sys, os
from os import getcwd, path, mkdir
from time import time

from simLogic.Relationships import Relationships


class LogFile:

    def __init__(self, fpath="logs", fname=None):
        try:
            mkdir(fpath)
        except FileExistsError:
            pass
        self.file = open(path.join(getcwd(), fpath, f'{str(time()).split(".")[0]}.csv'),
                         "w+") if fname is None else open(path.join(getcwd(), fpath, fname), "w+")
        self.fieldnames = [
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
            "coord_z",
            "relationships"
        ]
        self.dictWriter = csv.DictWriter(self.file, fieldnames=self.fieldnames)
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
            "relationships": Relationships.get_all_relationships(agent),
        }

        self.dictWriter.writerow(data)

    def close(self):
        self.file.close()

    def merge_logs(self, fpath="logs/ongoing"):
        for file in os.listdir(fpath):
            if not file.endswith(".csv"):
                continue
            with open(path.join(getcwd(), fpath, file), "r") as f:
                reader_fieldnames = self.fieldnames.copy()

                with open(path.join(getcwd(), fpath, file), "r") as check_file:
                    first_line = check_file.readline().strip()
                    has_relationships = "relationships" in first_line

                dict_reader = csv.DictReader(f)

                for row in dict_reader:
                    if row.get("id") == "id":
                        continue

                    if "relationships" not in row or row["relationships"] is None:
                        row["relationships"] = "{}"

                    for field in self.fieldnames:
                        if field not in row:
                            row[field] = ""

                    self.dictWriter.writerow(row)

                f.close()
        return
