class Settings:
    cell_size = 50
    wall_size = cell_size // 10

    footer_height = 160
    text_x_offset = 30
    text_y_offset = 30
    text_line_inset = 25

    off_color = 0x000000  # black
    wall_color = 0x0000FF  # blue
    path_color = 0x00FF00  # green
    entry_color = 0xEAF6AD  # light shade of green
    exit_color = 0xB6DB00  # dark shade of green
    text_color = 0xFFFFFF  # white

    window_title: str = "a-maze-ing"
