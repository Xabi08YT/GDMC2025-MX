import math

def distance_xz(ax: float, az: float, bx: float, bz: float) -> float:
    return math.sqrt((ax-bx)**2 + (az-bz)**2)

def same_point(p1, p2):
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]