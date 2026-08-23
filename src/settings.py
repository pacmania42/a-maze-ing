class Settings:
    def __init__(self) -> None:
        self.cell_size = 50
        self.wall_size = self.cell_size // 10

        self.footer_height = 160
        self.text_x_offset = 30
        self.text_y_offset = 30
        self.text_line_inset = 25

        self.wall_colors = [
            0x0000FF,
            0xDDDDDD,
            0xFFFFFF,
            0x00FFFF,
        ]

        self.off_color = 0x000000  # black
        self.path_color = 0x00FF00  # green
        self.entry_color = 0xEAF6AD  # light shade of green
        self.exit_color = 0xB6DB00  # dark shade of green
        self.text_color = 0xFFFFFF  # white

        self.window_title: str = "a-maze-ing"
