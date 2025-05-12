import random
import uuid
from LogFile import LogFile


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
            "social": random.uniform(-0.5, 0.5),
            "strength": random.uniform(0.1, 0.3),
        }
        self.attributes_malus = {
            "hunger": 0,
            "energy": 0,
            "health": 0,
            "social": 0,
        }
        self.happiness = 0
        self.relationship = {}
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

    def apply_decay(self):
        if self.decay_rates["hunger"] > 0:
            self.attributes["hunger"] -= self.decay_rates["hunger"]
            self.nb_turn_hungry = 0
        else:
            self.nb_turn_hungry += 1
        if self.decay_rates["energy"] > 0:
            self.attributes["energy"] -= self.decay_rates["energy"]
            self.nb_turn_sleepy = 0
        else:
            self.nb_turn_sleepy += 1

        if self.nb_turn_hungry > 12 or self.nb_turn_sleepy > 20:
            self.attributes["health"] -= self.decay_rates["health"]
        elif self.attributes["health"] < 1:
            self.attributes["health"] += self.decay_rates["health"]

        self.attributes["social"] -= self.decay_rates["social"]

        self.dead = (self.attributes["health"] <= 0)

    def determine_priority(self):
        return min(self.attributes.items())

    def tick(self):
        self.apply_decay()
        priority = self.determine_priority()
        print(priority)
        pass