import random
import uuid
import math

from simLogic.Job import JobType, Job
from buildings.Building import Building
from buildings.House import House
from utils.utils import evaluate_spot
from utils.ANSIColors import ANSIColors
from simLogic.Relationships import Relationships
import json

class Agent:
    def __init__(self, sim, x, z, name):
        """
        Initializes an Agent instance.
        :param sim: Simulation object that this agent belongs to.
        :param x: Coordinate X of the agent
        :param z: Coordinate Z of the agent
        :param name: Name of the agent
        """
        self.simulation = sim
        self.id = str(uuid.uuid4())
        self.name = name
        self.x = x
        self.z = z
        self.velocity_x = 0
        self.velocity_z = 0
        self.max_speed = 1.0
        self.max_force = 0.1
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
            "energy": random.uniform(0.12, 0.5),
            "health": random.uniform(0.1, 0.3),
            "social": random.uniform(0.4, 0.5),
            "strength": random.uniform(0.1, 0.3),
            "adventurous": random.uniform(0.1, 0.3),
        }
        self.attributes_mod = {
            "hunger": .0,
            "energy": .0,
            "health": .0,
            "social": .0,
            "strength": .0,
            "adventurous": .0,
        }
        self.happiness = 0
        self.happiness_decay = random.uniform(0.005, 0.03)
        self.job = Job(self, JobType.UNEMPLOYED)
        self.logfile = None
        self.action = None
        self.home = None
        self.turn = 1
        self.nb_turn_hungry = 0
        self.nb_turn_sleepy = 0
        self.nb_turn_fulfilled = 0
        self.visited = []
        self.scores = {}
        self.radius = self.simulation.config["observationRange"]
        self.last_page_book = ""
        self.book = {"title": f"The life of {self.name}", "author": self.name, "pages": [json.dumps([{"text": f"My life - {self.name}\n{__import__('datetime').datetime.now().strftime('%Y/%m/%d %H:%M')}"}])]}

    def set_velocity(self, vx, vz):
        """
        Sets the velocity of the agent, ensuring it does not exceed the maximum speed.
        :param vx: New velocity in the X direction
        :param vz: New velocity in the Z direction
        """
        speed = math.sqrt(vx * vx + vz * vz)
        if speed > self.max_speed:
            vx = (vx / speed) * self.max_speed
            vz = (vz / speed) * self.max_speed
        self.velocity_x = vx
        self.velocity_z = vz

    def apply_force(self, fx, fz):
        """
        Applies a force to the agent, adjusting its velocity accordingly.
        :param fx: Force in the X direction
        :param fz: Force in the Z direction
        """
        force_magnitude = math.sqrt(fx * fx + fz * fz)
        if force_magnitude > self.max_force:
            fx = (fx / force_magnitude) * self.max_force
            fz = (fz / force_magnitude) * self.max_force

        self.velocity_x += fx
        self.velocity_z += fz

    def update_position(self):
        """
        Updates the agent's position based on its velocity, ensuring it stays within the bounds of the simulation's walkable area.
        """
        min_x, min_z = 0, 0
        max_x = self.simulation.walkable.shape[0] - 1
        max_z = self.simulation.walkable.shape[1] - 1
        new_x = self.x + self.velocity_x
        new_z = self.z + self.velocity_z
        if min_x <= new_x <= max_x and min_z <= new_z <= max_z and self.simulation.walkable[int(new_x), int(new_z)]:
            self.x = new_x
            self.z = new_z
        else:
            self.x = max(min_x, min(new_x, max_x))
            self.z = max(min_z, min(new_z, max_z))

    def force_constraints_on_attributes(self):
        """
        Ensures that the agent's attributes remain within defined bounds.
        """
        self.attributes["social"] = max(0, min(1, self.attributes["social"]))
        self.attributes["health"] = max(0, min(1, self.attributes["health"]))
        self.attributes["hunger"] = max(0, min(1, self.attributes["hunger"]))
        self.attributes["energy"] = max(0, min(1, self.attributes["energy"]))
        self.attributes["strength"] = max(0, min(1, self.attributes["strength"]))
        self.happiness = max(-1, min(1, self.happiness))

    def apply_decay(self):
        """
        Applies decay to the agent's attributes based on their current state and decay rates.
        """
        if self.attributes["hunger"] + self.attributes_mod["hunger"] > 0:
            multiply = 1 + self.attributes["strength"] + self.attributes_mod["strength"]
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

        self.attributes["strength"] = max(self.attributes["strength"] - self.decay_rates["strength"],self.base_attributes["strength"])

        if self.attributes["health"] < 0.5:
            self.attributes_mod["strength"] = -random.uniform(0.1,0.5)

        self.attributes["social"] -= self.decay_rates["social"]
        self.happiness -= self.happiness_decay

        if self.attributes["hunger"] == 1 and self.attributes["energy"] == 1:
            self.nb_turn_fulfilled += 1

        if self.attributes["health"] + self.attributes_mod["health"] <= 0:
            self.die()

    def determine_priority(self):
        """
        Determines the priority of the agent's next action based on its current attributes.
        :return: The attribute that has the lowest value, indicating the most urgent need.
        """
        tmp = {
            "hunger": self.attributes["hunger"],
            "energy": self.attributes["energy"],
            "social": self.attributes["social"],
        }
        return min(tmp.keys(), key=lambda k: tmp[k])

    def fulfill_needs(self):
        """
        Fulfills the agent's needs based on its current state and environment.
        """
        if self.simulation.hasfarmer:
            self.attributes["hunger"] = 1
            self.happiness += 0.01
        if self.home is not None and self.home.built:
            self.attributes["energy"] = 1
            self.happiness += 0.01
        else:
            self.attributes["energy"] += self.decay_rates["energy"] - 0.1

    def move(self):
        """
        Moves the agent based on the boids behavior applied to it, which considers the positions and velocities of other agents.
        """
        (fx, fz) = self.simulation.boids.apply_boids_behavior(self, self.simulation.agents)
        self.apply_force(fx, fz)
        self.update_position()

    def observe_environment(self):
        """
        Observes the environment around the agent and updates its scores based on the presence of resources, water, lava, and buildings.
        """
        x, z = int(self.x), int(self.z)
        if (x,z) in self.visited:
            return
        self.visited.append((x,z))
        return

    def compute_scores(self):
        for x,z in self.visited:
            score = self.simulation.wood[x - self.radius:x + self.radius, z - self.radius:z + self.radius].sum().item()
            score -= 5 * self.simulation.water[x - self.radius:x + self.radius,
                         z - self.radius:z + self.radius].sum().item()
            score -= 5 * self.simulation.lava[x - self.radius:x + self.radius,
                         z - self.radius:z + self.radius].sum().item()
            score -= 100 * self.simulation.buildings[x - self.radius:x + self.radius,
                           z - self.radius:z + self.radius].sum().item()
            self.scores[str((x,z))] = score

    def place_house(self):
        """
        Places a house for the agent if it does not already have one and if it has enough scores to build.
        """
        if isinstance(self.home, House):
            print(f"{self.name} already has a home")
            return

        self.compute_scores()

        threshold = int(10 + 30 * self.attributes["adventurous"])
        if len(self.scores) < threshold:
            print(f"{self.name} has not enough scores to build a house ({len(self.scores)}/{threshold})")
            return

        best_spot = max(self.scores, key=self.scores.get)
        spot_tuple = eval(best_spot)
        temp_house = House(spot_tuple, self, self.name + " House")
        temp_house.clear()
        x0, z0 = temp_house.center_point
        width, depth = temp_house.width, temp_house.depth
        building_matrix = self.simulation.buildings
        trespass = False
        for dx in range(width):
            for dz in range(depth):
                x = x0 + dx
                z = z0 + dz
                if 0 <= x < building_matrix.shape[0] and 0 <= z < building_matrix.shape[1]:
                    if building_matrix[x, z] != 0:
                        trespass = True
                        break
            if trespass:
                break
        if trespass:
            Building.BUILDINGS.remove(temp_house)
            self.scores.pop(best_spot)
            return
        self.home = temp_house
        self.home.build()
        print(
            f"{ANSIColors.OKBLUE}[SIMULATION INFO] {ANSIColors.ENDC}{ANSIColors.OKGREEN}{self.name}{ANSIColors.ENDC}{ANSIColors.OKBLUE} built a new house!{ANSIColors.ENDC}")

    def update_book(self):
        """
        Updates the agent's book with the current state of the agent, including attributes, job, home, and relationships.
        """
        if self.dead:
            return
        attributes = self.attributes
        job = self.job
        home = self.home if isinstance(self.home, House) else None
        relations = []
        for key, data in Relationships.get_all_relationships(self).items():
            relations.append({
                "name": data["agent"],
                "status": data['status'],
                "value": data['value']
            })
        if not hasattr(self, '_house_mentioned'):
            self._house_mentioned = False
        if not hasattr(self, '_job_mentioned'):
            self._job_mentioned = False
        if not hasattr(self, '_relations_memory'):
            self._relations_memory = {}
        hunger = (
            "My stomach is growling with hunger." if attributes['hunger'] < 0.3 else
            "I feel perfectly satisfied." if attributes['hunger'] > 0.7 else
            "I could use a snack soon."
        )
        energy = (
            "I am bursting with energy!" if attributes['energy'] > 0.7 else
            "I feel a bit tired today." if attributes['energy'] < 0.3 else
            "My energy is average."
        )
        health = (
            "My health is excellent." if attributes['health'] > 0.8 else
            "I'm feeling a bit under the weather." if attributes['health'] < 0.4 else
            "My health is alright."
        )
        social = (
            "I feel surrounded by friends." if attributes['social'] > 0.7 else
            "I feel a bit lonely." if attributes['social'] < 0.3 else
            "My social life is balanced."
        )
        strength = (
            "I feel incredibly strong today!" if attributes['strength'] > 0.7 else
            "I feel weak and frail." if attributes['strength'] < 0.3 else
            "My strength is average."
        )
        adventurous = (
            "I'm ready for any adventure!" if attributes['adventurous'] > 0.7 else
            "I prefer to stay safe at home." if attributes['adventurous'] < 0.3 else
            "I'm open to some new experiences."
        )
        if home and hasattr(home, 'center_point') and home.center_point and not self._house_mentioned:
            house_str = f"I built my house at {home.center_point}."
            self._house_mentioned = True
        elif self._house_mentioned:
            house_str = ""
        else:
            house_str = "I don't have a house yet."
        if job and hasattr(job, 'job_type') and job.job_type != JobType.UNEMPLOYED and not self._job_mentioned:
            job_str = f"I started working as a {job.job_type.value.lower()}."
            self._job_mentioned = True
        elif self._job_mentioned:
            job_str = ""
        else:
            job_str = "I haven't found my calling yet."
        relations_evolution = []
        for rel in relations:
            name = rel["name"]
            value = rel["value"]
            prev = self._relations_memory.get(name)
            if prev is not None and prev != value:
                if value > prev:
                    relations_evolution.append(f"My relationship with {name} improved.")
                elif value < prev:
                    relations_evolution.append(f"My relationship with {name} worsened.")
            self._relations_memory[name] = value
        if relations_evolution:
            relations_str = " ".join(relations_evolution)
        else:
            relations_str = "No significant change in my relationships."
        mood = (
            "Today, I feel truly happy." if self.happiness > 0.5 else
            "Today, I feel neutral." if self.happiness > 0 else
            "Today, I feel a bit sad."
        )
        page_lines = [
            {"text": f"Day {self.turn}\n"},
            {"text": mood},
        ]
        if job_str:
            page_lines.append({"text": job_str})
        if house_str:
            page_lines.append({"text": house_str})
        page_lines += [
            {"text": hunger},
            {"text": energy},
            {"text": health},
            {"text": social},
            {"text": strength},
            {"text": adventurous},
            {"text": relations_str},
            {"text": "Looking forward to tomorrow!"}
        ]
        if not hasattr(self, '_book_memory'):
            self._book_memory = []
            self._book_memory_size = 15
        for line in page_lines:
            if line["text"] not in self._book_memory:
                self._book_memory.append(line["text"])
                if len(self._book_memory) > self._book_memory_size:
                    self._book_memory.pop(0)
            else:
                page_lines[page_lines.index(line)] = ""
        self.book["pages"].append(json.dumps(page_lines))

    def die(self):
        """
        Marks the agent as dead and updates the happiness of other agents based on their relationships with this agent.
        """
        self.dead = True
        for agent in self.simulation.agents:
            if agent != self:
                rel_data = Relationships.get_relationship_data(self, agent)
                if rel_data and "value" in rel_data and rel_data["value"] > 0.2:
                    multiply = 1 + abs(rel_data["value"])
                    agent.happiness -= 0.1 * multiply

    def tick(self):
        """
        Executes a single tick of the agent's behavior, applying decay, fulfilling needs, moving, observing the environment,
        """
        if self.dead:
            self.logfile.addLine(self, "DEAD")
            return
        self.apply_decay()
        self.fulfill_needs()
        self.move()
        self.observe_environment()

        priority = self.determine_priority()

        if self.job.job_type == JobType.UNEMPLOYED:
            self.job.get_new_job(self, priority)

        if self.home is None and self.attributes["energy"] < 0.5:
            self.place_house()
        elif isinstance(self.home, House) and self.home.built == False:
            self.home.build()

        if self.job.job_type != JobType.UNEMPLOYED:
            self.job.work()

        self.force_constraints_on_attributes()
        self.logfile.addLine(self, priority)

        self.update_book()
