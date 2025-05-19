from buildings.Building import Building


class FarmBuilding(Building):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s FarmBuilding", orientation, False)

class BlacksmithBuilding(Building):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s BlacksmithBuilding", orientation, False)

class CommunityBuilding(Building):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s CommunityBuilding", orientation, False)

class WorkshopBuilding(Building):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s WorkshopBuilding", orientation, False)