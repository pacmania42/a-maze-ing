class Settings:
    cell_size: int = 50
    wall_size: int = cell_size // 10

    off_color: int = 0x000000  # black
    wall_color: int = 0x0000FF  # blue
    path_color: int = 0x00FF00  # green
    entry_color: int = 0xEAF6AD  # light shade of green
    exit_color: int = 0xB6DB00  # dark shade of green

    window_title: str = "a-maze-ing"
