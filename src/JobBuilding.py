from pyglm import ivec3
from Job import Job
from Building import Building
from Agent import Agent


class JobHouse(Building):
    def __init__(self, job: Job, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False, folder="generated"):
        super().__init__(center_point, agent, orientation, built)
        self.job = job