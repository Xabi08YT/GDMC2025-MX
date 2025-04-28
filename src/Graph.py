from Edge import Edge
from Building import Building


class Graph:
    def __init__(self, buildings: list[Building]):
        self.nodes = buildings
        self.edges = []
        for b in buildings:
            for b2 in buildings:
                self.edges.append(Edge(b, b2))
            self.edges.append(Edge(b,b.center_point))

    def spanning_tree(self):
        self.edges = sorted(self.edges, key=lambda e: e.cost)
