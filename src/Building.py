from random import random, choice

from gdpc.interface import ivec3
import Agent
from Chunk import Chunk
import utils
from src.utils import distance_xz


class Building:
    BUILDINGS = []

    def __init__(self, center_point: ivec3 | None, agent: Agent, name: str, orientation: str = "south",
                 built: bool = False, folder="generated"):
        self.built = built
        self.orientation = orientation
        self.center_point = center_point
        self.agent = agent
        self.name = name
        self.folder = folder
        self.chunk = Chunk({}, name, folder)
        self.radius = 10
        Building.BUILDINGS.append(self)

    def built(self):
        self.built = True
        print(f"Building at x={self.center_point[0]}, y={self.center_point[1]}, z={self.center_point[2]} done!")

    def set_orientation_according_to_center(self, village_center: tuple[int, int], agent: Agent = None):
        if agent is None:
            agent = self.agent

        if self.center_point is None:
            return

        orientations = {"north": [0, -1], "south": [0, 1], "east": [0, 1], "west": [0, -1]}
        score = {k: distance_xz(village_center[0], village_center[1], self.center_point.x + self.radius * e[0], self.center_point.z + self.radius * e[1]) for k,e in orientations.items()}

        max = -32768
        K = None
        for k,s in score.items():
            if s > max:
                max = s
                K = k
            elif s == max and random() < 0.5:
                K = k

        orientations.pop(K)
        keys = list(orientations.keys())
        self.orientation = orientations[choice(keys)]

    def __repr__(self):
        return "Building(center_point={}, agent={})".format(self.center_point, self.agent)

    def __str__(self):
        return " at x={}, y={}, z={} owned by {}".format(self.center_point.x, self.center_point.y, self.center_point.z,
                                                         self.agent.name)

    def detect_tresspassing(self, x, z):
        return utils.distance_xz(self.center_point[0], self.center_point[2], x, z) <= self.radius

    @staticmethod
    def detect_all_tresspassing(x, z):
        tresspassing = []
        for b in Building.BUILDINGS:
            if b.detect_tresspassing(x, z):
                tresspassing.append(b)
        return tresspassing
