from buildings.Building import Building

class JobBuilding(Building):
    def __init__(self, center_point: tuple[int, int, int] | None, agent, name, orientation: str = "north", steps: int = 10):
        super().__init__(center_point, agent, name, orientation, False)
        self.step = 0
        self.steps = steps

    def build(self):
        print("This building seems to have no center point..")

    def check_built(self):
        if self.step >= self.steps:
            super().built()


class FarmBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s FarmBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0], self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]], self.center_point[2], "minecraft:hay_block")
        super().check_built()

class BlacksmithBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s BlacksmithBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0],
                                        self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]],
                                        self.center_point[2], "minecraft:obsidian")
        super().check_built()

class CommunityBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s CommunityBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0],
                                        self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]],
                                        self.center_point[2], "minecraft:bookshelf")
        super().check_built()

class WorkshopBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s WorkshopBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0],
                                        self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]],
                                        self.center_point[2], "minecraft:clay")
        super().check_built()