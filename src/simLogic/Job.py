from enum import Enum
from random import choice
import os
from buildings.JobBuilding import JobBuilding, WorkshopBuilding, FarmBuilding, BlacksmithBuilding, CommunityBuilding

from simLogic.Relationships import Relationships


class JobCategory(Enum):
    FARM = "FarmCategory"
    BLACKSMITH = "BlacksmithCategory"
    COMMUNITY = "CommunityCategory"
    WORKSHOP = "WorkshopCategory"


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
    def __init__(self, agent, job_type: JobType = JobType.UNEMPLOYED, job_building: JobBuilding = None):
        self.agent: Agent = agent
        self.job_type: JobType = job_type
        self.job_building: JobBuilding = job_building
        self.job_category: JobCategory = None

    def __str__(self):
        return f"{self.job_type.value}"

    def __repr__(self):
        return f"Job: {self.job_type.value}"

    def get_new_job(self, agent, priority):
        relationships = Relationships.get_all_relationships(agent)
        if relationships:
            job_counts = {}
            for rel_agent in relationships:
                job = getattr(rel_agent.job, "job_type", None)
                if job:
                    job_counts[job] = job_counts.get(job, 0) + 1
            if job_counts:
                most_common_job = max(job_counts, key=job_counts.get)
        # use in the future most_common_job to decide which job the agent will likely obtains
        if priority == "hunger" and not os.path.exists(".hasfarmer"):
            self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
            self.job_category = JobCategory.FARM
            self.job_building = FarmBuilding(None, self.agent)
            try:
                with open(file=".hasfarmer", mode="x") as f:
                    f.close()
            except FileExistsError:
                pass
            return
        if agent.attributes["strength"] > 0.7:
            self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
            self.job_category = JobCategory.BLACKSMITH
            self.job_building = BlacksmithBuilding(None, self.agent)
            return
        if agent.decay_rates["social"] < 0.05:
            self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
            self.job_category = JobCategory.COMMUNITY
            self.job_building = CommunityBuilding(None, self.agent)
            return
        if agent.decay_rates["energy"] < 0.3:
            self.job_type = choice([JobType.MASON, JobType.SHEPHERD, JobType.FLETCHER])
            self.job_category = JobCategory.WORKSHOP
            self.job_building = WorkshopBuilding(None, self.agent)
            return
        self.job_type = JobType.UNEMPLOYED

    def build_job_building(self):
        self.job_building.build()

    def work(self):
        if self.job_building.built is not True:
            self.build_job_building()
            return

        if self.job_category == JobCategory.WORKSHOP:
            # if agent coords is not around the job building -> go to building
            # decreasing energy attributes
            pass
        elif self.job_category == JobCategory.BLACKSMITH:
            # if agent coords is not around the job building -> go to building
            # decreasing energy attributes but increasing muscular attribute
            pass
        elif self.job_category == JobCategory.COMMUNITY:
            # if agent coords is not around the job building -> go to building
            # decreasing energy attributes
            pass
        elif self.job_category == JobCategory.FARM:
            # if agent coords is not around the job building -> go to building
            # decreasing energy attributes but increasing hunger attribute
            pass