from enum import Enum
from random import choice
import os
from src.simLogic import Agent
from src.buildings import Building
from src.buildings.JobBuilding import WorkshopBuilding, FarmBuilding, BlacksmithBuilding, CommunityBuilding

class JobType(Enum):
    ARMORER = "Armorer"
    BUTCHER = "Butcher"
    CARTOGRAPHER = "Cartographer"
    CLERIC = "Cleric"
    FARMER = "Farmer"
    FISHERMAN = "Fisherman"
    FLETCHER = "Fletcher"
    LEATHERWORKER = "Leatherworker"
    LIBRARIAN = "Librarian"
    MASON = "Mason"
    SHEPHERD = "Shepherd"
    TOOLSMITH = "Toolsmith"
    WEAPONSMITH = "Weaponsmith"
    UNEMPLOYED = "Unemployed"

class Job:
    def __init__(self, agent: Agent, job_type: JobType = JobType.UNEMPLOYED, job_building: Building = None):
        self.agent = agent
        self.job_type = job_type
        self.job_building = job_building

    def __str__(self):
        return f"{self.job_type.value}"
    
    def __repr__(self):
        return f"Job: {self.job_type.value}"

    def get_new_job(self, agent, priority):
        if priority == "hunger" and not os.path.exists(".hasfarmer"):
            self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
            self.job_building = FarmBuilding(None, self.agent)
            try:
                with open(file=".hasfarmer", mode="x") as f:
                    f.close()
            except FileExistsError:
                pass
            return
        if agent.attributes["strength"] > 0.7:
            self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
            self.job_building = BlacksmithBuilding(None, self.agent)
            return
        if agent.decay_rates["social"] < 0.05:
            self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
            self.job_building = CommunityBuilding(None, self.agent)
            return
        if agent.decay_rates["energy"] < 0.3:
            self.job_type = choice([JobType.MASON, JobType.SHEPHERD, JobType.FLETCHER])
            self.job_building = WorkshopBuilding(None, self.agent)
            return
        self.job_type = JobType.UNEMPLOYED

    def build_job_building(self):
        pass