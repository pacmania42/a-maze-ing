"""Central visual and animation settings for the MLX interface."""


class Settings:
    """Store dimensions, colors, timing, title, and the required 42 pattern."""

    def __init__(self) -> None:
        """Initialize the default rendering and animation configuration."""

        #
        self.tick = 1 / 60
        self.window_title: str = "a-maze-ing"

        # spacings
        self.cell_size = 72
        self.wall_size = self.cell_size // 10
        self.txt_pane_width = 400
        self.x_offset = 30
        self.y_offset = 30
        self.inset = 25

        # colors
        self.off_color = 0x000000  # black
        self.pattern_color = 0x800080  # purple
        self.path_color = 0xFFFF00  #
        self.entry_color = 0xFF00FF  #
        self.exit_color = 0x00FFFF  #
        self.text_color = 0xFFFFFF  # white
        self.wall_colors = (
            0x0000FF,
            0xFF0000,
            0x00FF00,
        )

        # keybindings
        self.close_win = 0xFF1B
        self.new_maze = 0x6D
        self.toggle_path = 0x70
        self.change_wall_color = 0x77
        self.toggle_animation = 0x61

        self.pattern = (
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
        )
