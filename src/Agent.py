from uuid import uuid4
import random

class Agent:
    def __init__(self, x: int = 0, y: int = 100, z: int=0, center_village: tuple = (0, 0)):
        self.id: str = str(uuid4())
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.center_village: tuple = center_village
        self.tickEnable = True
        self.needs = {
            "hunger": 1.0,
            "social": 0.8,
            "energy": 1.0,
            "health": 1.0,
            #"farfromothers": random.uniform(-1, 1),
            #"farfromcenter": random.uniform(-1, 1),
            #"flatspace": random.uniform(-1, 1)
        }
        self.needs_decay = {
            "hunger": 0.03,
            "energy": 0.02,
            "social": 0.05,
            "health": 0.01,
        }
        self.attributes = {}
        self.relationships = {}
        self.actions = {}
        self.observations = {}
        self.current_phase = "starting"
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
        if not self.tickEnable:
            return

        for need in self.needs:
            self.needs[need] = max(0, self.needs[need] - self.needs_decay[need])

        priority_need = min(self.needs)

        if priority_need == "hunger":
            #eat
            pass
        elif priority_need == "social":
            #social
            pass
        elif priority_need == "energy":
            #sleep
            pass
        elif priority_need == "health":
            #rest
            pass
        else:
            #explore
            pass