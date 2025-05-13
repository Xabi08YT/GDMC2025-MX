from pyglm import ivec3
from simLogic.Job import Job
from buildings.Building import Building
from simLogic.Agent import Agent

class JobHouse(Building):
    def __init__(self, job: Job, center_point: ivec3 | None, agent: Agent, orientation: str = "south", built: bool = False, folder="generated"):
        super().__init__(center_point, agent, "JobHouse", orientation, built)
        self.job = job

    def __str__(self):
        print("JobBuilding" + super().__str__())