from buildings.JobBuilding import JobBuilding

class CommunityBuilding(JobBuilding):
    def __init__(self, center_point: tuple[int,int,int] | None, agent, orientation: str = "north"):
        super().__init__(center_point, agent, agent.name + "'s CommunityBuilding", orientation)

    def build(self):
        for i in range(self.step):
            super().add_block_to_matrix(self.center_point[0],
                                        self.agent.simulation.heightmap[self.center_point[0], self.center_point[1]],
                                        self.center_point[2], "minecraft:bookshelf")
        super().check_built()