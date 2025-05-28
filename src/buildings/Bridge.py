from typing import Tuple

from buildings.Building import Building

class Bridge(Building):
    def __init__(self, start_point: Tuple[int, int], end_point: Tuple[int, int], orientation: str = "south", built: bool = False, folder="generated"):
        # TODO Initialize center point with start_point and end_point
        # TODO Building agent?
        super().__init__(None, None, "Bridge", orientation, built, folder)

    def build(self):
        pass
