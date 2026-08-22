from src.settings import Settings as stg


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

    @staticmethod
    def put_pixel(
        data_addr: memoryview,
        line_len: int,
        bpp: int,
        y: int,
        x: int,
        color: int,
    ) -> None:
        offset = (y * line_len) + (x * (bpp // 8))
        data_addr[offset] = (color) & 0xFF
        data_addr[offset + 1] = (color >> 8) & 0xFF
        data_addr[offset + 2] = (color >> 16) & 0xFF
        data_addr[offset + 3] = 0xFF

    @staticmethod
    def put_box(
        data_addr: memoryview,
        line_len: int,
        bpp: int,
        y: int,
        x: int,
        width: int,
        height: int,
        color: int,
    ) -> None:
        for yy in range(height):
            for xx in range(width):
                Cell.put_pixel(
                    data_addr=data_addr,
                    line_len=line_len,
                    bpp=bpp,
                    y=y + yy,
                    x=x + xx,
                    color=color,
                )

    def render(
        self,
        data_addr: memoryview,
        ll: int,
        bpp: int,
    ) -> None:
        y = self.row * stg.cell_size
        x = self.col * stg.cell_size

        # north wall
        Cell.put_box(
            data_addr=data_addr,
            line_len=ll,
            bpp=bpp,
            y=y,
            x=x,
            width=stg.cell_size,
            height=stg.wall_size,
            color=stg.wall_color,
        )

        # south wall
        Cell.put_box(
            data_addr=data_addr,
            line_len=ll,
            bpp=bpp,
            y=y + stg.cell_size - stg.wall_size,
            x=x,
            width=stg.cell_size,
            height=stg.wall_size,
            color=stg.wall_color,
        )

        # east wall
        Cell.put_box(
            data_addr=data_addr,
            line_len=ll,
            bpp=bpp,
            y=y,
            x=x + stg.cell_size - stg.wall_size,
            width=stg.wall_size,
            height=stg.cell_size,
            color=stg.wall_color,
        )

        # west wall
        Cell.put_box(
            data_addr=data_addr,
            line_len=ll,
            bpp=bpp,
            x=x,
            y=y,
            width=stg.wall_size,
            height=stg.cell_size,
            color=stg.wall_color,
        )
