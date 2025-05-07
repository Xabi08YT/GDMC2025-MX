from Edge import Edge
from Building import Building
from Firecamp import Firecamp
from DSU import DSU

class Graph:
    def __init__(self, buildings: list[Building], campfire: Firecamp):
        self.nodes = buildings
        self.edges = []
        for b in buildings:
            for b2 in buildings:
                self.edges.append(Edge(b, b2))
            self.edges.append(Edge(b,b.center_point))

    def spanning_tree(self, V):
        self.edges = sorted(self.edges, key=lambda e: e.cost)
        dsu = DSU(V)
        cost = 0
        count = 0
        for x, y, w in self.edges:

            if dsu.find(x) != dsu.find(y):
                dsu.union(x, y)
                cost += w
                count += 1
                if count == V - 1:
                    break
        return cost