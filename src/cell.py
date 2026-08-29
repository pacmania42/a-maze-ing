"""Cell model used by the graphical maze representation."""


class Cell:
    """Represent one maze cell and the state of its four walls."""

    def __init__(self, val: int, row: int, col: int) -> None:
        """Decode the four wall bits in ``val`` and store grid coordinates.

        Args:
            val (int): Value for `val`.
            row (int): Value for `row`.
            col (int): Value for `col`.
        """
        self.row = row
        self.col = col

        self.n = bool(val & 0b0001)
        self.e = bool(val & 0b0010)
        self.s = bool(val & 0b0100)
        self.w = bool(val & 0b1000)
