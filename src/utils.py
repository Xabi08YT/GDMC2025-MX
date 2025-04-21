def distance_xz(ax: float, az: float, bx: float, bz: float)-> float:
    return (ax-bx)**2 + (az-bz)**2

def is_flat():
    return True