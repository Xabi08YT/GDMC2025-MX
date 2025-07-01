import math

def distance_xz(ax: float, az: float, bx: float, bz: float) -> float:
    """
Calculate the distance between two points in the XZ plane.
    :param ax: The X coordinate of the first point.
    :param az: The Z coordinate of the first point.
    :param bx: The X coordinate of the second point.
    :param bz: The Z coordinate of the second point.
    :return: The distance between the two points in the XZ plane.
    """
    return math.sqrt((ax-bx)**2 + (az-bz)**2)

def same_point(p1, p2):
    """
    Check if two points in 3D space are the same.
    :param p1: The first point as a tuple (x, y, z).
    :param p2: The second point as a tuple (x, y, z).
    :return: True if the points are the same, False otherwise.
    """
    return p1[0] == p2[0] and p1[1] == p2[1] and p1[2] == p2[2]