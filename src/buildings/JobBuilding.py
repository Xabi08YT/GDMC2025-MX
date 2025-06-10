from buildings.Building import Building

class JobBuilding(Building):
    def __init__(self, center_point: tuple[int, int, int] | None, agent, name, orientation: str = "north", steps: int = 10,width = 5,depth = 5,height = 5,bupdates = True):
        """
        Initialize a JobBuilding instance.
        :param center_point: The center point of the building in the format (x, y, z).
        :param agent: The agent associated with the building.
        :param name: The name of the building.
        :param orientation: The orientation of the building, default is "north".
        :param steps: Number of steps to build the building, default is 10.
        :param width: Width of the building, default is 5.
        :param depth: Depth of the building, default is 5.
        :param height: Height of the building, default is 5.
        :param bupdates: If the building should update its state, default is True.
        """
        super().__init__(center_point, agent, name, orientation, False,width=width,height=height, depth=depth, bupdates=bupdates)
        self.step = 0
        self.steps = steps

    def build(self):
        """
        Build the building by incrementing the step and checking if it is built.
        :return:
        """
        print("This building seems to have no center point..")

    def check_built(self):
        """
        Check if the building is built and update its state accordingly.
        :return:
        """
        super().built()