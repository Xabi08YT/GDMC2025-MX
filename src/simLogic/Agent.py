import random
import uuid
import math
from gdpc.vector_tools import ivec3
from simLogic.Job import JobType, Job
import os
from buildings.Building import Building
from buildings.House import House
from utils.utils import evaluate_spot
from utils.ANSIColors import ANSIColors

class Agent:
    def __init__(self, sim, x, z, name):
        self.simulation = sim
        self.dead = False
        self.base_attributes = {
            "hunger": 1,
            "energy": 1,
            "health": 1,
            "social": 1,
            "strength": random.uniform(0.1, 0.5),
            "adventurous": random.uniform(0.1, 1),
        }
        self.attributes = {
            "hunger": self.base_attributes["hunger"],
            "energy": self.base_attributes["energy"],
            "health": self.base_attributes["health"],
            "social": self.base_attributes["social"],
            "strength": self.base_attributes["strength"],
            "adventurous": self.base_attributes["adventurous"],
        }
        self.decay_rates = {
            "hunger": random.uniform(0.1, 0.5),
            "energy": random.uniform(0.1, 0.5),
            "health": random.uniform(0.1, 0.3),
            "social": random.uniform(-0.4, 0.5),
            "strength": random.uniform(0.1, 0.3),
            "adventurous": random.uniform(0.1, 0.3),
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
        self.happiness_decay = random.uniform(0.005, 0.03)
        self.id = str(uuid.uuid4())
        self.name = name
        self.x = x
        self.z = z
        self.velocity_x = 0
        self.velocity_z = 0
        self.max_speed = 1.0
        self.max_force = 0.1
        self.job = Job(JobType.UNEMPLOYED)
        self.turn = 0
        self.action = None
        self.home = Building(None, self, self.name + "'s Space")
        self.nb_turn_hungry = 0
        self.nb_turn_sleepy = 0
        self.nb_turn_fulfilled = 0
        self.logfile = None
        self.scores = {}
        self.radius = self.simulation.config["observationRange"]

    def get_position(self):
        return self.x, self.z

    def get_velocity(self):
        return self.velocity_x, self.velocity_z

    def set_velocity(self, vx, vz):
        speed = math.sqrt(vx * vx + vz * vz)
        if speed > self.max_speed:
            vx = (vx / speed) * self.max_speed
            vz = (vz / speed) * self.max_speed
        self.velocity_x = vx
        self.velocity_z = vz

    def apply_force(self, fx, fz):
        force_magnitude = math.sqrt(fx * fx + fz * fz)
        if force_magnitude > self.max_force:
            fx = (fx / force_magnitude) * self.max_force
            fz = (fz / force_magnitude) * self.max_force

        self.velocity_x += fx
        self.velocity_z += fz

    def update_position(self):
        self.x += self.velocity_x
        self.z += self.velocity_z

    def force_constraints_on_attributes(self):
        self.attributes["social"] = max(0, min(1, self.attributes["social"]))
        self.attributes["health"] = max(0, min(1, self.attributes["health"]))
        self.attributes["hunger"] = max(0, min(1, self.attributes["hunger"]))
        self.attributes["energy"] = max(0, min(1, self.attributes["energy"]))
        self.attributes["strength"] = max(0, min(1, self.attributes["strength"]))

    def apply_decay(self):
        if self.attributes["hunger"] + self.attributes_mod["hunger"] > 0:
            multiply = 1 + self.attributes["strength"]
            self.attributes["hunger"] -= self.decay_rates["hunger"] * multiply
            self.nb_turn_hungry = 0
        else:
            self.nb_turn_hungry += 1
        if self.attributes["energy"] + self.attributes_mod["energy"] > 0:
            self.attributes["energy"] -= self.decay_rates["energy"]
            self.nb_turn_sleepy = 0
        else:
            self.nb_turn_sleepy += 1

        if self.attributes["strength"] + self.attributes_mod["strength"] > 0:
            if self.attributes["strength"] - self.decay_rates["strength"] >= self.base_attributes["strength"]:
                self.attributes["strength"] -= self.decay_rates["strength"]

        if self.nb_turn_hungry >= 3 or self.nb_turn_sleepy >= 5:
            self.attributes["health"] -= self.decay_rates["health"]
        elif self.attributes["health"] < 1 and self.nb_turn_fulfilled >= 3:
            self.attributes["health"] += self.decay_rates["health"]

        self.attributes["social"] -= self.decay_rates["social"]
        self.happiness -= self.happiness_decay

        if self.attributes["hunger"] == 1 and self.attributes["energy"] == 1:
            self.nb_turn_fulfilled += 1

        self.force_constraints_on_attributes()

        self.dead = (self.attributes["health"] + self.attributes_mod["health"] <= 0)

    def determine_priority(self):
        tmp = {
            "hunger": self.attributes["hunger"],
            "energy": self.attributes["energy"],
            "social": self.attributes["social"],
        }
        return min(tmp.keys(), key=lambda k: tmp[k])

    def fulfill_needs(self):
        if os.path.exists(".hasfarmer"):
            self.attributes["hunger"] = 1
            self.happiness += 0.01
        if self.home is not None and self.home.built:
            self.attributes["energy"] = 1
            self.happiness += 0.01

    def move(self):
        (fx, fz) = self.simulation.boids.apply_boids_behavior(self, []) # [] à remplacer par la liste de tous les agents
        self.apply_force(fx, fz)
        self.update_position()

    def observe_environment(self):
        x, z = int(self.x), int(self.z)

        if str((x, z)) in self.scores:
            return

        score = self.simulation.wood[x-self.radius:x+self.radius,z-self.radius:z+self.radius].sum().item()
        score -= self.simulation.water[x - self.radius:x + self.radius, z - self.radius:z + self.radius].sum().item()
        score -= self.simulation.lava[x - self.radius:x + self.radius, z - self.radius:z + self.radius].sum().item()
        score -= self.simulation.buildings[x - self.radius:x + self.radius, z - self.radius:z + self.radius].sum().item()

        self.scores[str((x, z))] = score

        return

    def place_house(self):
        if hasattr(self, 'home') and self.home.center_point is not None and self.home.built:
            print(f"{self.name} already has a home")
            return

        best_spot = max(self.scores, key=self.scores.get)

        if hasattr(self, 'home') and self.home in Building.BUILDINGS:
            Building.BUILDINGS.remove(self.home)

        # Transform best_stop into tuple
        # self.home = House(lll, self, self.name + "'s House")
        #self.home.build()
        print(
            f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE} built a new house!{ANSIColors.ENDC}")

    def tick(self):
        if self.dead:
            self.logfile.addLine(self, "DEAD")
            return
        self.apply_decay()
        self.fulfill_needs()
        self.move()
        priority = self.determine_priority()
        self.logfile.addLine(self, priority)
        if self.job.job_type == JobType.UNEMPLOYED:
            self.job.get_new_job(self, priority)
        self.observe_environment()
        if self.turn > 10 and hasattr(self.home,"center_point") and self.home.center_point is None:
            self.place_house()