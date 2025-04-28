from gdpc.interface import ivec3
import Agent
from Chunk import Chunk
import utils


class Building:

    BUILDINGS = []

    def __init__(self, center_point: ivec3 | None, agent: Agent, name:str, orientation: str = "south", built: bool = False, folder="generated"):
        self.built = built
        self.orientation = orientation
        self.center_point = center_point
        self.agent = agent
        self.name = name
        self.folder = folder
        self.chunk = Chunk({}, name, folder)
        self.radius = 20
        Building.BUILDINGS.append(self)

    def built(self):
        self.built = True
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
        return " at x={}, y={}, z={} owned by {}".format(self.center_point.x, self.center_point.y, self.center_point.z, self.agent.name)

    def detect_tresspassing(self, x, z):
        return utils.distance_xz(self.center_point[0], self.center_point[2], x,z) <= self.radius

    @staticmethod
    def detect_all_tresspassing(x,z):
        tresspassing = []
        for b in Building.BUILDINGS:
            if b.detect_tresspassing(x, z):
                tresspassing.append(b)
        return tresspassing