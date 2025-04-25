import Agent
from enum import Enum
from random import choice

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
    def __init__(self, job_type: JobType):
        self.job_type = job_type

    def __str__(self):
        return f"Job: {self.job_type.value}"

    def get_new_job(self, agent: Agent):
        if agent.attributes["muscular"] > 0.5:
            self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
            return
        if agent.needs_decay["social"] < 0.05:
            self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
            return
        if agent.needs_decay["hunger"] < 0.05:
            self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
            return
        if agent.needs_decay["energy"] < 0.05:
            self.job_type = choice([JobType.MASON, JobType.SHEPHERD])
            return
        self.job_type = JobType.FLETCHER



