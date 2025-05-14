from random import random, choice
from gdpc.interface import ivec3
from abstractionLayer.Chunk import Chunk
import utils.utils as utils
from utils.utils import distance_xz


class Building:
    BUILDINGS = []

    def __init__(self, center_point: ivec3 | None, agent, name: str, orientation: str = "south",
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

    def set_orientation_according_to_center(self, agent = None):
        if agent is None:
            agent = self.agent

        if self.center_point is None:
            return
        village_center = agent.simulation.firecamp_coords
        orientations = {"north": [0, -1], "south": [0, 1], "east": [1, 0], "west": [-1, 0]}
        score = {k: distance_xz(village_center[0], village_center[1], self.center_point.x + self.radius * e[0], self.center_point.z + self.radius * e[1]) for k,e in orientations.items()}

        max_distance = max(score.values())
        
        orientations_to_remove = [k for k, s in score.items() if s == max_distance]
        for orientation in orientations_to_remove:
            orientations.pop(orientation)
        
        if orientations:
            self.orientation = choice(list(orientations.keys()))
        else:
            self.orientation = choice(["north", "south", "east", "west"])

    def get_entrance_coordinates(self):
        if self.center_point is None:
            return None

        try:
            if isinstance(self.center_point, ivec3):
                x, y, z = self.center_point.x, self.center_point.y, self.center_point.z
            else:
                x, y, z = self.center_point[0], self.center_point[1], self.center_point[2]
        except (TypeError, IndexError, AttributeError) as e:
            return None
        
        entrance_offset = {"north": (0, -self.radius), "south": (0, self.radius), 
                          "east": (self.radius, 0), "west": (-self.radius, 0)}

        if self.orientation not in entrance_offset:
            self.orientation = "south"
            
        offset = entrance_offset[self.orientation]
        entrance_x = x + offset[0]
        entrance_z = z + offset[1]

        return (entrance_x, entrance_z)

    def __str__(self):
         return f"{self.name}"

    def detect_trespassing(self, x, z):
        if self.center_point is None:
            return False
        return utils.distance_xz(self.center_point[0], self.center_point[2], x, z) <= self.radius

    @staticmethod
    def detect_all_trespassing(x, z):
        trespassing = []
        for b in Building.BUILDINGS:
            if b.detect_trespassing(x, z):
                trespassing.append(b)
        return trespassing