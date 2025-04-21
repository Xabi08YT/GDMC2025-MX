import Agent
from gdpc.vector_tools import ivec3
import Job

class Building():
    def __init__(self, center_point: ivec3 | None, agent: Agent, existing: bool = False):
        self.existing = existing
        self.center_point = center_point
        self.agent = agent

    def build(self):
        print(f"Building at x={self.center_point.x}, y={self.center_point.y}, z={self.center_point.z}!")

class JobHouse():
    def __init__(self, building: Building, job: Job):
        self.building = building
        self.job = job

class House():
    def __init__(self, building: Building):
        self.building = building