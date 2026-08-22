

class Cell:
    n: bool
    e: bool
    s: bool
    w: bool
    path: bool

    def __init__(self, maze: list[list[int]], row: int, col: int) -> None:
        self.row = row
        self.col = col
        val = maze[row][col]

        self.n = bool(val & 0b0001)
        self.e = bool(val & 0b0010)
        self.s = bool(val & 0b0100)
        self.w = bool(val & 0b1000)
        self.path = False
