import random
from enum import Enum
from random import choice
import os
from buildings.JobBuilding import JobBuilding
from buildings.WorkshopBuilding import WorkshopBuilding
from buildings.FarmBuilding import FarmBuilding
from buildings.BlacksmithBuilding import BlacksmithBuilding
from buildings.CommunityBuilding import CommunityBuilding

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
        self.agent = agent
        self.job_type: JobType = job_type
        self.job_building: JobBuilding = job_building
        self.job_category: JobCategory = None

    def __str__(self):
        return f"{self.job_type.value}"

    def __repr__(self):
        return f"Job: {self.job_type.value}"

    def get_new_job(self, agent, priority):
        if priority == "hunger" and not agent.simulation.hasfarmer or agent.decay_rates["hunger"] > 0.45:
            self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
            self.job_category = JobCategory.FARM
            self.job_building = FarmBuilding.get_instance(None, agent)
            agent.simulation.hasfarmer = True
            return

        relationships = Relationships.get_all_relationships(agent)
        positive_relations = sum(1 for _, data in relationships.items() if data["value"] > 0.3)
        close_relations = sum(1 for _, data in relationships.items() if data["value"] > 0.7)
        social_influence = 0.0

        friend_job_influence = {}
        for rel_id, rel_data in relationships.items():
            if rel_data["value"] > 0.3:
                for other_agent in agent.simulation.agents:
                    if other_agent.id == rel_id and other_agent.job.job_type != JobType.UNEMPLOYED:
                        if other_agent.job.job_category not in friend_job_influence:
                            friend_job_influence[other_agent.job.job_category] = 0
                        friend_job_influence[other_agent.job.job_category] += rel_data["value"]

        if close_relations > 0:
            social_influence = 0.15

        if positive_relations > 2 or close_relations > 0:
            if random.random() < 0.3 + social_influence:
                self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
                self.job_category = JobCategory.COMMUNITY
                self.job_building = CommunityBuilding.get_instance(None, agent)
                return

        if friend_job_influence:
            most_influential_category = max(friend_job_influence.items(), key=lambda x: x[1])[0]
            if random.random() < 0.4 + (friend_job_influence[most_influential_category] * 0.1):
                if most_influential_category == JobCategory.FARM:
                    self.job_type = choice([JobType.FARMER, JobType.FISHERMAN, JobType.BUTCHER])
                    self.job_category = JobCategory.FARM
                    self.job_building = FarmBuilding.get_instance(None, agent)
                    return
                elif most_influential_category == JobCategory.BLACKSMITH:
                    self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
                    self.job_category = JobCategory.BLACKSMITH
                    self.job_building = BlacksmithBuilding.get_instance(None, agent)
                    return
                elif most_influential_category == JobCategory.COMMUNITY:
                    self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
                    self.job_category = JobCategory.COMMUNITY
                    self.job_building = CommunityBuilding.get_instance(None, agent)
                    return
                elif most_influential_category == JobCategory.WORKSHOP:
                    self.job_type = choice([JobType.MASON, JobType.SHEPHERD, JobType.FLETCHER])
                    self.job_category = JobCategory.WORKSHOP
                    self.job_building = WorkshopBuilding.get_instance(None, agent)
                    return

        if agent.attributes["strength"] > (0.4 - social_influence):
            self.job_type = choice([JobType.ARMORER, JobType.WEAPONSMITH, JobType.TOOLSMITH, JobType.LEATHERWORKER])
            self.job_category = JobCategory.BLACKSMITH
            self.job_building = BlacksmithBuilding.get_instance(None, agent)
            return

        social_threshold = 0.05 + (positive_relations * 0.01)
        if agent.decay_rates["social"] < social_threshold:
            self.job_type = choice([JobType.CARTOGRAPHER, JobType.CLERIC, JobType.LIBRARIAN])
            self.job_category = JobCategory.COMMUNITY
            self.job_building = CommunityBuilding.get_instance(None, agent)
            return

        energy_threshold = 0.3 - (positive_relations * 0.02)
        if agent.decay_rates["energy"] < energy_threshold:
            self.job_type = choice([JobType.MASON, JobType.SHEPHERD, JobType.FLETCHER])
            self.job_category = JobCategory.WORKSHOP
            self.job_building = WorkshopBuilding.get_instance(None, agent)
            return

        self.job_type = JobType.UNEMPLOYED

    def build_job_building(self):
        self.job_building.build()

    def work(self):
        if self.job_building.built is not True:
            self.build_job_building()
            return

        agent_pos = (self.agent.x, self.agent.z)
        if self.job_building.center_point is not None:
            building_pos = (self.job_building.center_point[0], self.job_building.center_point[1])
            distance = ((agent_pos[0] - building_pos[0]) ** 2 + (agent_pos[1] - building_pos[1]) ** 2) ** 0.5

            if distance > 5:
                dx = building_pos[0] - agent_pos[0]
                dz = building_pos[1] - agent_pos[1]
                magnitude = (dx**2 + dz**2)**0.5
                if magnitude > 0:
                    dx /= magnitude
                    dz /= magnitude
                self.agent.apply_force(dx * 0.05, dz * 0.05)
                return

        if self.job_category == JobCategory.WORKSHOP:
            self.agent.attributes["energy"] -= 0.05
            self.agent.attributes["strength"] += 0.01
            self.agent.happiness += 0.02

        elif self.job_category == JobCategory.BLACKSMITH:
            self.agent.attributes["energy"] -= 0.08
            self.agent.attributes["strength"] += 0.03
            self.agent.attributes["hunger"] -= 0.04
            self.agent.happiness += 0.015

        elif self.job_category == JobCategory.COMMUNITY:
            self.agent.attributes["energy"] -= 0.04
            self.agent.attributes["social"] += 0.05
            self.agent.happiness += 0.025

        elif self.job_category == JobCategory.FARM:
            self.agent.attributes["energy"] -= 0.06
            self.agent.attributes["hunger"] += 0.07
            self.agent.attributes["strength"] += 0.01
            self.agent.happiness += 0.02

