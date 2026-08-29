class Cell:
    def __init__(self, val: int, row: int, col: int) -> None:
        self.row = row
        self.col = col

        self.n = bool(val & 0b0001)
        self.e = bool(val & 0b0010)
        self.s = bool(val & 0b0100)
        self.w = bool(val & 0b1000)
