from gdpc.interface import Block

class MatrixMCBlock:
    def __init__(self, block:Block, matrixCoordinates:tuple[int,int,int]) -> None:
        self.block = block
        self.coord = matrixCoordinates