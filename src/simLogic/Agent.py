import random
import uuid
import math
import BoidsBehavior

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
        self.velocity_x = 0
        self.velocity_y = 0
        self.velocity_z = 0
        self.max_speed = 1.0
        self.max_force = 0.1
        self.job = None
        self.turn = 0
        self.action = None
        self.home = None
        self.job_place = None
        self.nb_turn_hungry = 0
        self.nb_turn_sleepy = 0
        self.logfile = None
        self.observations = {}
        
    def get_position(self):
        return (self.x, self.y, self.z)
        
    def get_velocity(self):
        return (self.velocity_x, self.velocity_y, self.velocity_z)
        
    def set_velocity(self, vx, vy, vz):
        speed = math.sqrt(vx*vx + vy*vy + vz*vz)
        if speed > self.max_speed:
            vx = (vx/speed) * self.max_speed
            vy = (vy/speed) * self.max_speed
            vz = (vz/speed) * self.max_speed
        self.velocity_x = vx
        self.velocity_y = vy
        self.velocity_z = vz
        
    def apply_force(self, fx, fy, fz):
        force_magnitude = math.sqrt(fx*fx + fy*fy + fz*fz)
        if force_magnitude > self.max_force:
            fx = (fx/force_magnitude) * self.max_force
            fy = (fy/force_magnitude) * self.max_force
            fz = (fz/force_magnitude) * self.max_force
            
        self.velocity_x += fx
        self.velocity_y += fy
        self.velocity_z += fz
        
    def update_position(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.z += self.velocity_z

    def force_constraints_on_attributes(self):
        self.attributes["social"] = max(0, min(1, self.attributes["social"]))
        self.attributes["health"] = max(0, min(1, self.attributes["health"]))
        self.attributes["hunger"] = max(0, min(1, self.attributes["hunger"]))
        self.attributes["energy"] = max(0, min(1, self.attributes["energy"]))
        self.attributes["strength"] = max(0, min(1, self.attributes["strength"]))

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
        return min(self.attributes.items(), key=lambda x: x[1])

    def fulfill_needs(self):
        if self.simulation.has_farmer:
            self.attributes["hunger"] = 1
        if self.home is not None and self.home.built:
            self.attributes["energy"] = 1

    def apply_priority(self, priority):
        pass

    def move(self):
        BoidsBehavior.apply_boids_behavior(self, [])
        self.update_position()

    def tick(self):
        if self.dead:
            self.logfile.addLine(self, "DEAD")
            return
        self.apply_decay()
        self.fulfill_needs()
        self.move()
        priority = self.determine_priority()
        self.logfile.addLine(self,priority)
        pass