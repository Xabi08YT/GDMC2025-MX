from enum import Enum
from random import choice
import os

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
    def __init__(self, job_type: JobType = JobType.UNEMPLOYED):
        self.job_type = job_type

    def __str__(self):
        return f"{self.job_type.value}"
    
    def __repr__(self):
        return f"Job: {self.job_type.value}"

    def get_new_job(self, agent, priority):
        if priority == "hunger" and not os.path.exists(".hasfarmer"):
            self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
            try:
                with open(file=".hasfarmer", mode="x") as f:
                    f.close()
            except FileExistsError:
                pass
            return
        if agent.attributes["strength"] > 0.3:
            self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
            return
        if agent.decay_rates["social"] < 0.05:
            self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
            return
        if agent.decay_rates["energy"] < 0.3:
            self.job_type = choice([JobType.MASON, JobType.SHEPHERD])
            return
        self.job_type = JobType.FLETCHER
