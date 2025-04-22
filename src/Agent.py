from uuid import uuid4
from buildings import *
from utils import *
import random
import buildings
from Job import JobType, Job

class Agent:
    def __init__(self, x: int = 0, y: int = 100, z: int=0):
        self.id: str = str(uuid4())
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
            "house": buildings.House(None, self),
            "jobhouse": buildings.JobHouse(Job(JobType.UNEMPLOYED, self), None, self),
        }
        self.actions = {
            "buildhouse": self.attributes["house"].build()
        }
        self.observations = {}
        self.best_house_score = {"score": 0, "pos": (0, 0, 0)}
        self.current_phase = "exploring"
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

    def explore(self, turns: int = 5):
        potential_spots = [(0,0)] #get random pos in buildarea
        for i in range(turns):
            tmp_score = evaluate_spot(self, potential_spots[i][0], potential_spots[i][1])
            if tmp_score > self.best_house_score["score"]:
                y = get_ground_height(potential_spots[i][0], 300, potential_spots[i][1])
                self.best_house_score = {"score": tmp_score, "pos": (potential_spots[i][0], y, potential_spots[i][1])}
        self.attributes["house"].center_point = ivec3(self.best_house_score["pos"][0], 0, self.best_house_score["pos"][1])

    def min_distance_to_others(self, others):
        return min([distance_xz(self.x, self.z, otherx, otherz) for otherx, otherz in others])