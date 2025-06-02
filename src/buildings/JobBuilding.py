from buildings.Building import Building

class JobBuilding(Building):
    def __init__(self, center_point: tuple[int, int, int] | None, agent, name, orientation: str = "north", steps: int = 10,width = 5,depth = 5,height = 5,bupdates = True):
        super().__init__(center_point, agent, name, orientation, False,width=width,height=height, depth=depth, bupdates=bupdates)
        self.step = 0
        self.steps = steps

    def build(self):
        print("This building seems to have no center point..")

    def check_built(self):
        super().built()