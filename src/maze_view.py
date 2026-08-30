from random import randint
from typing import Any

from mlx import Mlx

from src.adapter import Adapter
from src.cell import Cell
from src.settings import Settings


class MazeView(Mlx):  # type: ignore[misc]
    """Render and interact with a maze using the MiniLibX Python binding."""

    def __init__(self, adapter: Adapter, stg: Settings) -> None:
        """Create the MLX window, image buffer, and input hook for a maze.

        Args:
            adapter (Adapter): Value for `adapter`.
            visualize_only (bool): Value for `visualize_only`.
            stg (Settings): Rendering settings used by the application.
        """
        super().__init__()
        self.adapter = adapter
        self.stg = stg

        self.show_path: bool = True
        self.color_idx = 0

        self.maze_width = len(self.adapter.grid[0]) * self.stg.cell_size
        self.maze_height = len(self.adapter.grid) * self.stg.cell_size
        self.window_height = self.maze_height + self.stg.footer_height
        self.window_width = self.maze_width

        self.mlx_ptr: int = self.mlx_init()
        self.win_ptr: int = self.mlx_new_window(
            self.mlx_ptr,
            self.window_width,
            self.window_height,
            self.stg.window_title,
        )
        self.img_addr = self.mlx_new_image(
            self.mlx_ptr, self.maze_width, self.maze_height
        )
        data_addr, bpp, ll, _ = self.mlx_get_data_addr(self.img_addr)
        self.data_addr: memoryview = data_addr
        self.bpp: int = bpp
        self.ll: int = ll

        self.mlx_key_hook(self.win_ptr, self.keybinding_dispatch, None)

    def paint_window(self) -> Any:
        self._clear_maze()
        self.render_text()
        self.render_maze()
        self.render_pattern()
        self.render_terminals()
        self.render_path()
        self.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
        )

    def keybinding_dispatch(self, keycode: int, _: dict[str, Any]) -> None:
        """Handle escape, regeneration, path visibility, and wall colors.

        Args:
            keycode (int): Value for `keycode`.
            _ (dict[str, Any]): Value for `_`.
        """
        if keycode == 0xFF1B:  # escape
            self.mlx_destroy_image(self.mlx_ptr, self.img_addr)
            self.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            self.mlx_loop_exit(self.mlx_ptr)
            return
        if keycode == 0x6D:  # m
            self.adapter.generate(seed=randint(-1000, 1000))
        if keycode == 0x70:  # p
            self.show_path = not self.show_path
        if keycode == 0x77:  # w
            self.color_idx = (self.color_idx + 1) % len(self.stg.wall_colors)
        self.paint_window()

    def _clear_maze(self) -> None:
        """Fill the maze image buffer with the background color."""
        self._put_box(
            0,
            0,
            self.maze_width,
            self.maze_height,
            self.stg.off_color,
        )

    def show(self) -> None:
        """Render the initial scene and enter the MLX event loop."""
        self.paint_window()
        self.mlx_loop(self.mlx_ptr)

    def render_terminals(self) -> None:
        """Draw the entry and exit cells with their configured colors."""
        terminals = (self.adapter.entry, "entry"), (self.adapter.exit, "exit")

        for cell, name in terminals:
            x = cell.col * self.stg.cell_size
            y = cell.row * self.stg.cell_size

            color = (
                self.stg.entry_color
                if name == "entry"
                else self.stg.exit_color
            )

            self._put_box(
                y=y + self.stg.wall_size,
                x=x + self.stg.wall_size,
                width=int(self.stg.cell_size - 2 * self.stg.wall_size),
                height=int(self.stg.cell_size - 2 * self.stg.wall_size),
                color=color,
            )

    def render_path(self) -> None:
        """Animate drawing or hiding the shortest path cell by cell."""
        color = self.stg.path_color if self.show_path else self.stg.off_color
        path = self.adapter.shortest_path[:-1]

        for cell, dir in zip(path, self.adapter.path_dirs, strict=True):
            x = cell.col * self.stg.cell_size
            y = cell.row * self.stg.cell_size

            if cell is not path[0]:
                self._put_box(
                    y=y + self.stg.wall_size,
                    x=x + self.stg.wall_size,
                    width=self.stg.cell_size - 2 * self.stg.wall_size,
                    height=self.stg.cell_size - 2 * self.stg.wall_size,
                    color=color,
                )
            self.carve_walls(cell, dir, color)

    def render_pattern(self) -> None:
        """Draw the generator-provided 42 pattern inside the maze."""
        pattern = self.adapter.pattern

        if not pattern:
            return

        for col, row in pattern:
            x = col * self.stg.cell_size
            y = row * self.stg.cell_size

            self._put_box(
                y=y + self.stg.wall_size,
                x=x + self.stg.wall_size,
                width=int(self.stg.cell_size - 2 * self.stg.wall_size),
                height=int(self.stg.cell_size - 2 * self.stg.wall_size),
                color=self.stg.pattern_color,
            )

    def render_text(self) -> None:
        """Display keybindings and the active generation algorithm."""
        algorithm = self.adapter.cfg.algorithm if self.adapter.cfg else "N/A"
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height + self.stg.text_y_offset - 10,
            self.stg.text_color,
            "KEYBINDINGS",
        )
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.maze_width - 8 * self.stg.text_x_offset,
            self.maze_height + self.stg.text_y_offset - 10,
            self.stg.text_color,
            f"ALGORITHM: {algorithm}",
        )
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + self.stg.text_line_inset,
            self.stg.text_color,
            "m | Regenerate maze",
        )
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + 2 * self.stg.text_line_inset,
            self.stg.text_color,
            "p | Show/Hide shortest path",
        )
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + 3 * self.stg.text_line_inset,
            self.stg.text_color,
            "w | Change wall color",
        )
        self.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + 4 * self.stg.text_line_inset,
            self.stg.text_color,
            "ESC | Quit",
        )

    def _put_pixel(self, y: int, x: int, color: int) -> None:
        """Write one RGBA pixel directly into the MLX image buffer.

        Args:
            y (int): Vertical coordinate.
            x (int): Horizontal coordinate.
            color (int): Color value used for drawing.
        """
        offset = (y * self.ll) + (x * (self.bpp // 8))
        self.data_addr[offset] = (color) & 0xFF
        self.data_addr[offset + 1] = (color >> 8) & 0xFF
        self.data_addr[offset + 2] = (color >> 16) & 0xFF
        self.data_addr[offset + 3] = 0xFF

    def _put_box(
        self, y: int, x: int, width: int, height: int, color: int
    ) -> None:
        """Fill a rectangular area of the image buffer with one color.

        Args:
            y (int): Vertical coordinate.
            x (int): Horizontal coordinate.
            width (int): Width in pixels or cells.
            height (int): Height in pixels or cells.
            color (int): Color value used for drawing.
        """
        for yy in range(height):
            for xx in range(width):
                self._put_pixel(y=y + yy, x=x + xx, color=color)

    def render_maze(self) -> None:
        """Draw maze walls and animate carving when generation data exists."""
        height = len(self.adapter.grid)
        width = len(self.adapter.grid[0])

        # render the full grid with closed walls
        color = self.stg.wall_colors[self.color_idx]
        maze = [[Cell(15, r, c) for c in range(width)] for r in range(height)]
        for row in range(height):
            for col in range(width):
                self.paint_walls(maze[row][col], color)

        # carve walls
        for x, y, dir in self.adapter.gen.carving_order:
            cell = self.adapter.grid[y][x]
            self.carve_walls(cell, dir, self.stg.off_color)
            for _ in range(80):
                self.mlx_put_image_to_window(
                    self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
                )

    def paint_walls(
        self,
        cell: Cell,
        color: int,
    ) -> None:
        """Paint every closed wall of a cell using the selected wall color.

        Args:
            cell (Cell): Maze cell to process.
            color (int): Color value used for drawing.
        """
        y = cell.row * self.stg.cell_size
        x = cell.col * self.stg.cell_size

        # north
        if cell.n:
            self._put_box(
                x=x,
                y=y,
                width=self.stg.cell_size,
                height=self.stg.wall_size,
                color=color,
            )

        # south
        if cell.s:
            self._put_box(
                x=x,
                y=y + self.stg.cell_size - self.stg.wall_size,
                width=self.stg.cell_size,
                height=self.stg.wall_size,
                color=color,
            )

        # east wall
        if cell.e:
            self._put_box(
                x=x + self.stg.cell_size - self.stg.wall_size,
                y=y,
                width=self.stg.wall_size,
                height=self.stg.cell_size,
                color=color,
            )

        # west
        if cell.w:
            self._put_box(
                x=x,
                y=y,
                width=self.stg.wall_size,
                height=self.stg.cell_size,
                color=color,
            )

    def carve_walls(self, cell: Cell, dir: str, color: int) -> None:
        """Color the passage between a cell and its neighbour in ``dir``.

        Args:
            cell (Cell): Maze cell to process.
            dir (str): Movement direction.
            color (int): Color value used for drawing.
        """
        y = cell.row * self.stg.cell_size
        x = cell.col * self.stg.cell_size

        # color = self.stg.off_color
        h_width = self.stg.cell_size - 2 * self.stg.wall_size
        v_height = self.stg.cell_size - 2 * self.stg.wall_size

        # north
        if dir == "N":
            self._put_box(
                x=x + self.stg.wall_size,
                y=y - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        # south
        elif dir == "S":
            self._put_box(
                x=x + self.stg.wall_size,
                y=y + self.stg.cell_size - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        # west
        elif dir == "W":
            self._put_box(
                x=x - self.stg.wall_size,
                y=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )

        # east wall
        elif dir == "E":
            self._put_box(
                x=x + self.stg.cell_size - self.stg.wall_size,
                y=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )
