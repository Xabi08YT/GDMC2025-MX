import numpy as np
import heapq
from typing import List, Tuple, Dict
from utils.math_methods import distance_xz

class Pathfinding:
    def __init__(self, simulation, x1, z1, x2, z2,bridges, paths):
        # np.array of boolean values indicating walkable blocks
        self.grid = simulation.walkable
        self.water = simulation.water
        self.buildings = simulation.buildings
        # np.array of height values for the terrain xz
        self.heightmap = simulation.heightmap
        self.start = (x1, z1)
        self.end = (x2, z2)
        self.cost = 0
        self.directions = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.simulation = simulation
        self.bridges = bridges
        self.paths = paths

    @staticmethod
    def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def is_valid_position(self, pos: Tuple[int, int]) -> bool:
        x, z = pos
        return 0 <= x < self.grid.shape[0] and 0 <= z < self.grid.shape[1]
    
    def is_walkable(self, pos: Tuple[int, int]) -> bool:
        if not self.is_valid_position(pos):
            return False
        
        return self.grid[pos[0], pos[1]] == 1 or self.water[pos[0], pos[1]] == 1

    def get_movement_cost(self, current: Tuple[int, int], next_pos: Tuple[int, int]) -> float:
        if not self.is_walkable(next_pos):
            return float('inf')

        height_diff = abs(self.heightmap[next_pos[0], next_pos[1]].item() - self.heightmap[current[0], current[1]].item())

        if height_diff > 1:
            return float('inf')

        return ((1 +
                height_diff * 0.1 +
                100000 * int(self.water[next_pos[0], next_pos[1]].item() and not self.bridges[next_pos[0], next_pos[1]].item()))
                * (1.1 - int(self.paths[next_pos[0], next_pos[1]] != 0))
                + 32768 * int(self.buildings[next_pos[0], next_pos[1]] != 0))

    def get_neighbors(self, pos: Tuple[int, int]) -> List[Tuple[int, int]]:
        neighbors = []
        x, z = pos

        for dx, dz in self.directions:
            next_pos = (x + dx, z + dz)
            if self.is_walkable(next_pos):
                neighbors.append(next_pos)

        return neighbors

    @staticmethod
    def compute_mst_heuristic(landmarks: List[Tuple[int, int]]) -> float:
        if len(landmarks) <= 1:
            return 0
        
        edges = []
        for i in range(len(landmarks)):
            for j in range(i+1, len(landmarks)):
                dist = distance_xz(landmarks[i][0], landmarks[i][1], landmarks[j][0], landmarks[j][1])
                edges.append((dist, i, j))
        
        edges.sort()
        parent = list(range(len(landmarks)))
        
        def find(x):
            if parent[x] != x:
                parent[x] = find(parent[x])
            return parent[x]
        
        def union(x, y):
            parent[find(x)] = find(y)
        
        mst_cost = 0
        edge_count = 0
        
        for weight, u, v in edges:
            if find(u) != find(v):
                union(u, v)
                mst_cost += weight
                edge_count += 1
                if edge_count == len(landmarks) - 1:
                    break
        
        return mst_cost
    
    def find_path(self) -> List[Tuple[int, int]]:
        start = (self.start[0], self.start[1])
        end = (self.end[0], self.end[1])

        if not self.is_walkable(start) or not self.is_walkable(end):
            return []
        
        open_list = [(0, start)]
        came_from = {}
        g_score = {start: 0}
        f_score = {start: self.heuristic(start, end)}
        closed_set = set()
        landmarks = [end]
        
        while open_list:
            _, current = heapq.heappop(open_list)
            
            if current == end:
                path = self.reconstruct_path(came_from, end)
                return path
            
            closed_set.add(current)
            
            for neighbor in self.get_neighbors(current):
                if neighbor in closed_set:
                    continue

                tentative_g_score = g_score[current] + self.get_movement_cost(current, neighbor)

                if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g_score
                    
                    if distance_xz(neighbor[0], neighbor[1], end[0], end[1]) > 10:
                        if neighbor not in landmarks and len(landmarks) < 10:
                            landmarks.append(neighbor)
                        h_score = self.compute_mst_heuristic(landmarks)
                    else:
                        h_score = self.heuristic(neighbor, end)
                    
                    f_score[neighbor] = tentative_g_score + h_score
                    heapq.heappush(open_list, (f_score[neighbor], neighbor))
        
        return []
    
    def reconstruct_path(self, came_from: Dict[Tuple[int, int], Tuple[int, int]], current: Tuple[int, int]) -> List[Tuple[int, int]]:
        path = [current]
        self.cost = 0

        while current in came_from:
            prev = current
            current = came_from[current]

            if self.water[current[0], current[1]]:
                self.bridges[current[0], current[1]] = True

            path.append(current)
            self.cost += self.get_movement_cost(current, prev)
        
        path.reverse()

        return path
    
    def create_path_matrix(self, path: List[Tuple[int, int]]) -> np.ndarray:
        path_matrix = np.zeros((self.grid.shape[0], self.grid.shape[1]), dtype=int)
        
        for x, z in path:
            path_matrix[x, z] = 1
        
        return path_matrix

