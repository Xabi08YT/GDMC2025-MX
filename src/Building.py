from gdpc.interface import ivec3
from Agent import Agent
from Chunk import Chunk

class Building:
    def __init__(self, center_point: ivec3 | None, agent: Agent, name:str, orientation: str = "south", built: bool = False, folder="generated"):
        self.built = built
        self.orientation = orientation
        self.center_point = center_point
        self.agent = agent
        self.name = name
        self.folder = folder
        self.chunk = Chunk({}, name, folder)

    def build(self):
        if self.built is not True:
            return
        print(f"Building at x={self.center_point[0]}, y={self.center_point[1]}, z={self.center_point[2]} done!")

    def set_orientation_towards_center(self, agent: Agent = None):
        if agent is None:
            agent = self.agent

        if self.center_point is None:
            return

        dx = self.center_point.x - agent.center_village[0]
        dz = self.center_point.z - agent.center_village[1]

        if abs(dx) > abs(dz):
            if dx > 0:
                self.orientation = "west"
            else:
                self.orientation = "east"
        else:
            if dz > 0:
                self.orientation = "north"
            else:
                self.orientation = "south"

    def __repr__(self):
        return "Building(center_point={}, agent={})".format(self.center_point, self.agent)

    def __str__(self):
        return "Building at x={}, y={}, z={} owned by {}".format(self.center_point.x, self.center_point.y, self.center_point.z, self.agent.name)
