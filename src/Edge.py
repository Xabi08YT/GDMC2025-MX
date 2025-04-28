import utils


class Edge:
    def __init__(self, node1, node2):
        self.node1 = node1
        self.node2 = node2
        try:
            self.cost = utils.disance_xz(node1.center[0], node1.center[2],node2.center[0], node2.center[2])
        except AttributeError:
            try:
                self.cost = utils.distance_xz(node1.center[0], node1.center[2], node2[0], node2[2])
            except AttributeError:
                self.cost = utils.distance_xz(node1[0], node1[2], node2.center[0], node2.center[2])
