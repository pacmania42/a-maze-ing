WHITE = 0xFFFFFF
BLACK = 0x000000
RED = 0xFF0000
GREEN = 0x00FF00
BLUE = 0x0000FF


class Settings:
    # sizes
    cell_size: int = 100
    wall_size: int = cell_size // 10

    # default colors
    wall_color: int = BLUE
    path_color: int = GREEN

    # secondary colors
    sec_wall_color: int = RED
    sec_path_color: int = WHITE

    window_title: str = "a-maze-ing"
