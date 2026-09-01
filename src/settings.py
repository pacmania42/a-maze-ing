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

        # colors
        self.off_color = 0x000000  # black
        self.pattern_color = 0x800080  # purple
        self.entry_color = 0xFF0000  #
        self.exit_color = 0x0000FF  #
        self.text_color = 0xFFFFFF  # white
        self.colors = (
            (0x1E51A4, 0xFFFF00),
            (0xBD632F, 0xF7C7DB),
            (0x52528C, 0xA000CC),
            (0x32746D, 0xFFFFFF),
        )

        # keybindings
        self.close_win = 0xFF1B
        self.new_maze = 0x6D
        self.toggle_path = 0x70
        self.change_color = 0x63
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
