import json
import random
from gdpc import Block
from Relationship import Relationship, RelationShipType
from uuid import uuid4
from random import choice
from Job import JobType, Job
import AbstractionLayer
from utils import evaluate_spot
from math_methods import distance_xz
from Building import Building
import House
from gdpc.vector_tools import ivec3
import os

class Agent:

    current_dir = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(current_dir, "simParams.json"), "r") as file:
        simParams = json.load(file)
        file.close()

    def __init__(self, abl: AbstractionLayer, loaded_chunks: dict, radius: int = 20, x: int = 0, y: int = 100,
                 z: int = 0, center_village: tuple[int, int] = (0, 0), job: JobType = JobType.UNEMPLOYED,
                 observation_range: int = 5):
        self.id: str = str(uuid4())
        with open("./txt/agent_names.txt", "r") as f:
            self.name = choice(f.readlines()).strip()
        self.abl: AbstractionLayer = abl
        self.loaded_chunks: dict = loaded_chunks
        self.radius: int = radius
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.center_village: tuple[int, int] = center_village
        self.job: Job = Job(job)
        self.observation_range: int = observation_range
        self.tickEnable: bool = True
        self.needs = {
            "hunger": 1.0,
            "social": 0.8,
            "energy": 1.0,
            "health": 1.0,
        }
        self.home: Building = Building(None, self, self.name + "'s Space")
        self.needs_decay = {
            "hunger": round(random.uniform(0.00, 0.1), 2),
            "energy": round(random.uniform(0.00, 0.1), 2),
            "social": round(random.uniform(0.00, 0.1), 2),
            "health": round(random.uniform(0.00, 0.1), 2),
        }
        self.attributes = {
            "muscular": round(random.uniform(0.00, 0.7), 2),
            "adventurous": round(random.uniform(0.00, 0.8), 2),
        }
        self.relationships = {}
        self.actions = {}
        self.observations = {
            "terrain": {"wood":[], "water":[], "lava":[]},
            "structures": [],
            "points_of_interest": []
        }
        self.current_phase = "starting"
        self.all_agents = []

    def __str__(self):
        return f"{self.name}"
        
    def __repr__(self):
        return "Agent {} ({}, {}, {}) is {}".format(self.name, round(self.x, 2), round(self.y, 2), round(self.z, 2),
                                                    self.current_phase)

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_position(self) -> tuple:
        return self.x, self.y, self.z

    def increment_need(self, need: str, increment: float):
        new_need = self.needs[need] + increment
        if 0 <= new_need <= 1:
            self.needs[need] = new_need

    # -- ACTIONS --

    def eat(self):
        self.current_phase = "eating"
        self.increment_need("energy", -self.needs_decay["energy"])
        self.increment_need("health", -self.needs_decay["health"])
        self.increment_need("hunger", round(random.uniform(0.8, 1.0), 2))
        self.increment_need("social", -self.needs_decay["social"])

    def social(self):
        self.current_phase = "socializing"
        self.increment_need("energy", -self.needs_decay["energy"])
        self.increment_need("health", self.needs_decay["health"])
        self.increment_need("hunger", -self.needs_decay["hunger"])
        self.increment_need("social", self.needs_decay["social"])

        other_agent = min([agent for agent in self.all_agents if agent.id != self.id],
                          key=lambda agent: distance_xz(self.x, self.z, agent.x, agent.z))

        dx = (other_agent.x - self.x) * 0.5
        dz = (other_agent.z - self.z) * 0.5
        self.move(dx, 0, dz)

        if distance_xz(self.x, self.z, other_agent.x, other_agent.z) > 5:
            return

        if other_agent.name not in self.relationships:
            self.init_relationship(other_agent)
        else:
            self.update_relationship(other_agent)

        print(f"{self.name} talked with {other_agent.name} ({self.get_relationship_type(other_agent).value})")

    def sleep(self):
        self.current_phase = "sleeping"
        self.increment_need("energy", round(random.uniform(0.8, 1.0), 2))
        self.increment_need("health", round(random.uniform(0.15, 0.4), 2))
        self.increment_need("hunger", -self.needs_decay["hunger"])
        self.increment_need("social", -self.needs_decay["social"])

    def rest(self):
        self.current_phase = "resting"
        self.increment_need("energy", round(random.uniform(0.3, 0.5), 2))
        self.increment_need("health", round(random.uniform(0.1, 0.3), 2))
        self.increment_need("hunger", -self.needs_decay["hunger"])
        self.increment_need("social", -self.needs_decay["social"])

    def observe_environment(self):
        x, y, z = int(self.x), int(self.y), int(self.z)

        chunk = self.abl.get_chunk(x,z)

        self.analyze_observations(chunk.scan(x,y,z, 2))

    def analyze_observations(self,blocks: list[tuple[tuple[int,int,int],Block]]):

        tresspassing = Building.detect_all_tresspassing(self.x, self.z)
        self.observations["structures"] = list(dict.fromkeys(self.observations["structures"] + tresspassing))

        interesting_blocks_config = [ e for i in Agent.simParams["interestingTerrainChars"] for e in Agent.simParams[i]]
        wood = Agent.simParams["wood"]
        for coord,block in blocks:
            if block.id in interesting_blocks_config:
                if block.id in wood:
                    self.observations["terrain"]["wood"].append(coord)
                elif block.id in Agent.simParams["water"]:
                    self.observations["terrain"]["water"].append(coord)
                elif block.id in Agent.simParams["lava"]:
                    self.observations["terrain"]["lava"].append(coord)

        return

    def move(self, increment_x: float, increment_y: float, increment_z: float):
        self.current_phase = "moving"
        new_x = self.x + increment_x
        new_z = self.z + increment_z
        if self.radius >= new_x >= -self.radius:
            self.x = new_x
        if self.radius >= new_z >= -self.radius:
            self.z = new_z
        self.increment_need("hunger", -self.needs_decay["hunger"])
        self.increment_need("energy", -self.needs_decay["energy"])
        self.increment_need("health", self.needs_decay["health"])
        self.increment_need("social", -self.needs_decay["social"])

        self.observe_environment()

    def place_house(self):
        if hasattr(self, 'home') and self.home.center_point is not None and self.home.built:
            print(f"{self.name} already has a home")
            return
            
        num_spots = 10
        best_spot = None
        best_score = float('-inf')

        for _ in range(num_spots):
            ba = self.abl.getBuildArea()
            min_x, min_z = ba.begin[0], ba.begin[2]
            max_x, max_z = ba.end[0] - 1, ba.end[2] - 1
            test_x = random.randint(min_x, max_x)
            test_z = random.randint(min_z, max_z)

            score = evaluate_spot(self, int(test_x), int(test_z))

            if score > best_score:
                best_score = score
                best_spot = (test_x, test_z)

        chunk = self.abl.get_chunk(int(best_spot[0]), int(best_spot[1]))
        y = chunk.getGroundHeight(int(best_spot[0]), int(best_spot[1]))

        if hasattr(self, 'home') and self.home in Building.BUILDINGS:
            Building.BUILDINGS.remove(self.home)
            
        self.home = House.House(ivec3(int(best_spot[0]), y, int(best_spot[1])), self, self.name + "'s House")
        self.home.build()
        print(f"{self.name} built a new house!")

    # -- RELATIONSHIPS --

    def init_relationship(self, other_agent: 'Agent'):
        self.relationships[other_agent.name] = Relationship()

    def set_relationship(self, other_agent: 'Agent', rel_type: RelationShipType):
        if other_agent.name in self.relationships:
            self.relationships[other_agent.name].type = rel_type
        else:
            self.relationships[other_agent.name] = Relationship(rel_type)

    def get_relationship_type(self, other_agent: 'Agent') -> RelationShipType:
        if other_agent.name in self.relationships:
            return self.relationships[other_agent.name].type
        return RelationShipType.NEUTRAL

    def get_relationship(self, other_agent: 'Agent') -> Relationship:
        if other_agent.name in self.relationships:
            return self.relationships[other_agent.name]
        return Relationship()

    def update_relationship(self, other_agent: 'Agent'):
        if other_agent.name not in self.relationships:
            self.init_relationship(other_agent)

        relationship = self.relationships[other_agent.name]

        if random.random() < 0.6:
            relationship.improve(random.uniform(0.05, 0.15))
        else:
            relationship.deteriorate(random.uniform(0.03, 0.10))

        if self.name in other_agent.relationships:
            if random.random() < 0.8:
                if random.random() < 0.7:
                    other_agent.relationships[self.name].improve(random.uniform(0.03, 0.10))
                else:
                    other_agent.relationships[self.name].deteriorate(random.uniform(0.02, 0.08))
        else:
            other_agent.init_relationship(self)

        return relationship.type

    # -- TICK --

    def tick(self):
        if not self.tickEnable:
            return

        if self.job.job_type == JobType.UNEMPLOYED and random.uniform(0, 1) < 0.5:
            self.job.get_new_job(self)
            print(f"{self.name} got a new job: {self.job.job_type.value}")

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


