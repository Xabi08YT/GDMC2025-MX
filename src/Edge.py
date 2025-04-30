import utils
from Building import Building

class Edge:
    def __init__(self, node1:Building, node2:Building):
        self.node1 = node1
        self.node2 = node2
        self.cost = utils.distance_xz(node1.center_point[0], node1.center_point[2],node2.center_point[0], node2.center_point[2])