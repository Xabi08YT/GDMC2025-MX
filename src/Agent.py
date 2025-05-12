import random
import uuid


class Agent:
    def __init__(self, sim, x, y, z):
        self.simulation = sim
        self.dead = False
        self.attributes = {
            "hunger": 1,
            "energy": 1,
            "health": 1,
            "social": .8,
            "strength": random.uniform(0.1, 0.5),
            "adventurous": random.uniform(0.1, 1),
        }
        self.decay_rates = {
            "hunger": random.uniform(0.1, 0.2),
            "energy": random.uniform(0.1, 0.5),
            "health": random.uniform(0.1, 0.3),
            "social": random.uniform(-0.4, 0.5),
            "strength": random.uniform(0.1, 0.3),
        }
        self.attributes_mod = {
            "hunger": 0,
            "energy": 0,
            "health": 0,
            "social": 0,
            "strength": 0,
            "adventurous": 0,
        }
        self.happiness = 0
        self.happiness_decay = 0
        self.relationships = {}
        self.id = str(uuid.uuid4())
        self.name = ""
        self.x = x
        self.y = y
        self.z = z
        self.job = None
        self.turn = 0
        self.action = None
        self.home = None
        self.job_place = None
        self.nb_turn_hungry = 0
        self.nb_turn_sleepy = 0
        self.logfile = None
        self.observations = {}

    def force_constraints_on_attributes(self):
        if self.attributes["social"] < 0:
            self.attributes["social"] = -1
        elif self.attributes["social"] > 1:
            self.attributes["social"] = 1

        if self.attributes["health"] < 0:
            self.attributes["health"] = 0
        elif self.attributes["health"] > 1:
            self.attributes["health"] = 1

        if self.attributes["hunger"] < 0:
            self.attributes["hunger"] = 0
        elif self.attributes["hunger"] > 1:
            self.attributes["hunger"] = 1

        if self.attributes["energy"] < 0:
            self.attributes["energy"] = 0
        elif self.attributes["energy"] > 1:
            self.attributes["energy"] = 1

        if self.attributes["strength"] < 0:
            self.attributes["strength"] = 0
        elif self.attributes["strength"] > 1:
            self.attributes["strength"] = 1

    def apply_decay(self):
        if self.attributes["hunger"] + self.attributes_mod["hunger"] > 0:
            self.attributes["hunger"] -= self.decay_rates["hunger"]
            self.nb_turn_hungry = 0
        else:
            self.nb_turn_hungry += 1
        if self.attributes["energy"] + self.attributes_mod["energy"] > 0:
            self.attributes["energy"] -= self.decay_rates["energy"]
            self.nb_turn_sleepy = 0
        else:
            self.nb_turn_sleepy += 1

        if self.nb_turn_hungry > 12 or self.nb_turn_sleepy > 20:
            self.attributes["health"] -= self.decay_rates["health"]
        elif self.attributes["health"] < 1:
            self.attributes["health"] += self.decay_rates["health"]

        self.attributes["social"] -= self.decay_rates["social"]

        self.force_constraints_on_attributes()

        self.dead = (self.attributes["health"]  + self.attributes_mod["health"] <= 0)

    def determine_priority(self):
        return min(self.attributes.items())

    def tick(self):
        if self.dead:
            self.logfile.addLine(self, "DEAD")
            return
        self.apply_decay()
        priority = self.determine_priority()
        self.logfile.addLine(self,priority)
        pass