import random
from uuid import uuid4
from random import choice
from Job import JobType, Job
from gdpc import Block
from gdpc.vector_tools import ivec3
from utils import distance_xz, agents

class Agent:
    def __init__(self, world: list[tuple[ivec3, Block]], radius: int = 20, x: int = 0, y: int = 100, z: int=0, center_village: tuple = (0, 0), job: Job = JobType.UNEMPLOYED):
        self.id: str = str(uuid4())
        self.world: list[tuple[ivec3, Block]] = world
        self.radius = radius
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.center_village: tuple = center_village
        self.job = job
        self.tickEnable = True
        self.basics_needs = {
            "hunger": 1.0,
            "social": 0.8,
            "energy": 1.0,
            "health": 1.0,
            "chill": 0.5,
        }
        self.needs = {
            "hunger": 1.0,
            "social": 0.8,
            "energy": 1.0,
            "health": 1.0,
        }
        self.needs_decay = {
            "hunger": round(random.uniform(0.00, 0.1), 2),
            "energy": round(random.uniform(0.00, 0.1), 2),
            "social": round(random.uniform(0.00, 0.1), 2),
            "health": round(random.uniform(0.00, 0.1), 2),
        }
        self.attributes = {}
        self.relationships = []
        self.actions = {}
        self.observations = {}
        self.current_phase = "starting"
        with open("./txt/agent_names.txt", "r") as f:
            self.name = choice(f.readlines()).strip()

    def __repr__(self):
        return "Agent(id={}, x={}, y={}, z={})".format(self.id, self.x, self.y, self.z)

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_position(self) -> tuple:
        return self.x, self.y, self.z

    def set_need(self, need: str, increment: float):
        new_need = self.needs[need] + increment
        if (new_need >= 0 and new_need <= 1):
            self.needs[need] = new_need

    # -- ACTIONS --

    def eat(self):
        self.current_phase = "eating"
        self.set_need("energy", -self.needs_decay["energy"])
        self.set_need("health", -self.needs_decay["health"])
        self.set_need("hunger", round(random.uniform(0.8, 1.0), 2))
        self.set_need("social", -self.needs_decay["social"])

    def social(self):
        self.current_phase = "socializing"
        self.set_need("energy", -self.needs_decay["energy"])
        self.set_need("health", self.needs_decay["health"])
        self.set_need("hunger", -self.needs_decay["hunger"])
        self.set_need("social", self.needs_decay["social"])

        other_agent = min([agent for agent in agents if agent.id != self.id], key=lambda agent: distance_xz(self.x, self.z, agent.x, agent.z))

        dx = (other_agent.x - self.x) * 0.5
        dz = (other_agent.z - self.z) * 0.5
        self.move(dx, 0, dz)

        if distance_xz(self.x, self.z, other_agent.x, other_agent.z) > 5:
            pass

        if other_agent.name not in self.relationships:
            self.relationships.append(other_agent.name)

        print(f"{self.name} socialized with {other_agent.name}")

    def sleep(self):
        self.current_phase = "sleeping"
        self.set_need("energy", round(random.uniform(0.8, 1.0), 2))
        self.set_need("health", round(random.uniform(0.15, 0.4), 2))
        self.set_need("hunger", -self.needs_decay["hunger"])
        self.set_need("social", -self.needs_decay["social"])

    def rest(self):
        self.current_phase = "resting"
        self.set_need("energy", round(random.uniform(0.3, 0.5), 2))
        self.set_need("health", round(random.uniform(0.1, 0.3), 2))
        self.set_need("hunger", -self.needs_decay["hunger"])
        self.set_need("social", -self.needs_decay["social"])

    def move(self, increment_x: float, increment_y: float, increment_z: float):
        self.current_phase = "moving"
        new_x = self.x + increment_x
        new_z = self.z + increment_z
        if (new_x <= self.radius and new_x >= -self.radius):
            self.x = new_x
        if (new_z <= self.radius and new_z >= -self.radius):
            self.z = new_z
        self.set_need("hunger", -self.needs_decay["hunger"])
        self.set_need("energy", -self.needs_decay["energy"])
        self.set_need("health", self.needs_decay["health"])
        self.set_need("social", -self.needs_decay["social"])
        print(f"{self.name}'s pos = {self.x}, {self.z}")

    # -- TICK --

    def tick(self):
        if not self.tickEnable:
            return

        priority_need = min(self.needs, key=self.needs.get)

        if priority_need == "hunger":
            self.eat()
        elif priority_need == "social":
            self.social()
        elif priority_need == "energy":
            self.sleep()
        elif priority_need == "health":
            self.move(random.randint(-5, 5), 0, random.randint(-5, 5))
        else:
            self.move(random.randint(-5, 5), 0, random.randint(-5, 5))
        print(self.name + " is " + self.current_phase)