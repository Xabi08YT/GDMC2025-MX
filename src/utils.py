from gdpc import Editor
import math

current_editor = Editor(buffering=True)
agents = []

def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return math.sqrt((ax-bx)**2 + (az-bz)**2)

def min_distance_to_others(agent, others):
    return min([distance_xz(agent.x, agent.z, otherx, otherz) for otherx, otherz in others])

def same_point(p1,p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]