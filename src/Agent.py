from uuid import uuid4
from time import sleep
from Map import Map
from buildings import *
from utils import *
import random
import buildings
from Job import JobType, Job

class Agent:
    def __init__(self, mcmap: Map | None, x: int = 0, y: int = 100, z: int=0):
        self.id: str = str(uuid4())
        self.map: Map = mcmap
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.tickEnable = True
        self.needs = {
            "farfromothers": random.uniform(-1, 1),
            "farfromcenter": random.uniform(-1, 1),
            "flatspace": random.uniform(-1, 1)
        }
        self.attributes = {
            "house": buildings.House(Building(None, self)),
            "jobhouse": buildings.JobHouse(Building(None, self), Job(JobType.UNEMPLOYED, self))
        }
        self.actions = {
            "buildhouse": self.attributes["house"].building.build()
        }
        self.observations = {}

        with open("./txt/agent_names.txt", "r") as f:
            self.name = random.choice(f.readlines()).strip()

    def __repr__(self):
        return "Agent(id={}, x={}, y={}, z={})".format(self.id, self.x, self.y, self.z)

    def get_id(self) -> str:
        return self.id

    def get_name(self) -> str:
        return self.name

    def get_position(self) -> tuple:
        return self.x, self.y, self.z

    def tick(self):
        while self.tickEnable:
            # TODO: Make agent take decisions
            sleep(0.1)

    def min_distance_to_others(self, others):
        return min([distance_xz(self.x, self.z, otherx, otherz) for otherx, otherz in others])

    