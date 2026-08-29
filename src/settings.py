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
            0x00FFFF,
        ]

        self.off_color = 0x000000  # black
        self.pattern_color = 0x800080  # purple
        self.path_color = 0xFFFF00  # green
        self.entry_color = 0xFF0000  # red
        self.exit_color = 0x00FF00  # green
        self.text_color = 0xFFFFFF  # white

        self.animation_tick = 0.02

        self.window_title: str = "a-maze-ing"

        self.pattern = [
            (0, 0),
            (0, 1),
            (0, 2),
            (1, 2),
            (2, 2),
            (2, 3),
            (2, 4),
            (4, 0),
            (5, 0),
            (6, 0),
            (6, 1),
            (6, 2),
            (5, 2),
            (4, 2),
            (4, 3),
            (4, 4),
            (5, 4),
            (6, 4),
        ]
