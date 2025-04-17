from uuid import uuid4
from time import sleep
from Map import Map

class Agent:
    def __init__(self, mcmap: Map, x: int = 0, y: int = 100, z: int=0):
        self.id: str = str(uuid4())
        self.map: Map = mcmap
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.tickEnable = True

    def __repr__(self):
        return "Agent(id={}, x={}, y={}, z={})".format(self.id, self.x, self.y, self.z)

    def get_id(self) -> str:
        return self.id

    def get_position(self) -> tuple:
        return self.x, self.y, self.z

    def tick(self):
        while self.tickEnable:
            # TODO: Make agent take decisions
            sleep(0.1)