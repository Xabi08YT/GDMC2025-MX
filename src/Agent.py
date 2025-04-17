class Agent:
    def __init__(self, id, x = 0.0, y = 100, z=0.0):
        self.id: int = id
        self.x: float = x
        self.y: float = y
        self.z: float = z

    def __repr__(self):
        return "Agent(id={}, x={}, y={}, z={})".format(self.id, self.x, self.y, self.z)

    def get_id(self) -> int:
        return self.id

    def get_position(self) -> tuple:
        return self.x, self.y, self.z