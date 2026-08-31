import time
from functools import partial
from random import randint
from typing import Any, Generator

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

        self.animation_gen: Generator[None, None, None] | None = None
        self.last_tick = 0.0
        self.show_path: bool = True
        self.color_idx = 0

        self.maze_width = len(self.adapter.grid[0]) * self.stg.cell_size
        self.maze_height = len(self.adapter.grid) * self.stg.cell_size
        self.window_height = self.maze_height
        self.window_width = self.maze_width + self.stg.txt_pane_width

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
        self.mlx_loop_hook(self.mlx_ptr, self._app_loop, None)
        self.put_image = partial(
            self.mlx_put_image_to_window,
            self.mlx_ptr,
            self.win_ptr,
            self.img_addr,
            self.stg.txt_pane_width,
            0,
        )
        self.write = partial(
            self.mlx_string_put,
            mlx_ptr=self.mlx_ptr,
            win_ptr=self.win_ptr,
            x=self.stg.x_offset,
            color=self.stg.text_color,
        )

    def _app_loop(self, _: Any) -> None:
        now = time.perf_counter()

        if not self.animation_gen:
            return

        if now - self.last_tick > self.stg.animation_tick:
            self.last_tick = now
            try:
                next(self.animation_gen)
            except StopIteration:
                self.animation_gen = None

    def start_animation(self, clear_maze: bool) -> None:
        self.animation_gen = self.run_animation(clear_maze)
        self.last_tick = 0.0

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
            self.start_animation(True)
        if keycode == 0x70:  # p
            self.show_path = not self.show_path
            self.start_animation(False)
        if keycode == 0x77:  # w
            self.color_idx = (self.color_idx + 1) % len(self.stg.wall_colors)
            self.start_animation(True)

    def show(self) -> None:
        """Render the initial scene and enter the MLX event loop."""
        self.start_animation(True)
        self.mlx_loop(self.mlx_ptr)

    def render_terminals(self) -> None:
        """Draw the entry and exit cells with their configured colors."""
        terminals = (
            (self.adapter.entry, self.stg.entry_color),
            (self.adapter.exit, self.stg.exit_color),
        )

        for cell, color in terminals:
            x = cell.col * self.stg.cell_size
            y = cell.row * self.stg.cell_size

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
            self._carve_walls(cell, dir, color)

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
        """Display maze details and keybindings."""

        mode = "Generate+Visualize" if self.adapter.cfg else "Visualize-only"
        size = f"{len(self.adapter.grid[0])}X{len(self.adapter.grid)}"
        entry = f"{self.adapter.gen.maze_entry}"
        exit = f"{self.adapter.gen.maze_exit}"
        perfect = f"{self.adapter.cfg.perfect if self.adapter.cfg else 'N/A'}"
        algorithm = self.adapter.cfg.algorithm if self.adapter.cfg else "N/A"

        self.write(y=self.stg.y_offset, string="DETAILS")
        self.write(y=self.stg.y_offset + 30, string=f"MODE: {mode}")
        self.write(y=self.stg.y_offset + 60, string=f"SIZE: {size}")
        self.write(y=self.stg.y_offset + 90, string=f"ENTRY: {entry}")
        self.write(y=self.stg.y_offset + 120, string=f"EXIT: {exit}")
        self.write(y=self.stg.y_offset + 150, string=f"PERFECT: {perfect}")
        self.write(y=self.stg.y_offset + 180, string=f"ALGORITHM: {algorithm}")

        self.write(y=self.stg.y_offset + 300, string="KEYBINDINGS")
        self.write(y=self.stg.y_offset + 330, string="M | Regenerate (M)aze")
        self.write(y=self.stg.y_offset + 360, string="P | Show/Hide (P)ath")
        self.write(y=self.stg.y_offset + 390, string="W | Change (W)all color")
        self.write(y=self.stg.y_offset + 420, string="ESC | Quit")

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

    def run_animation(
        self, rebuild_walls: bool
    ) -> Generator[None, None, None]:
        """Draw maze walls and animate carving when generation data exists."""

        yield
        self.render_text()

        if rebuild_walls:
            height = len(self.adapter.grid)
            width = len(self.adapter.grid[0])
            color = self.stg.wall_colors[self.color_idx]

            self._put_box(0, 0, self.maze_width, self.maze_height, color)
            for row in range(height):
                for col in range(width):
                    y = row * self.stg.cell_size
                    x = col * self.stg.cell_size
                    self._put_box(
                        y=y + self.stg.wall_size,
                        x=x + self.stg.wall_size,
                        width=self.stg.cell_size - 2 * self.stg.wall_size,
                        height=self.stg.cell_size - 2 * self.stg.wall_size,
                        color=self.stg.off_color,
                    )

            # carve walls
            for x, y, dir in self.adapter.gen.carving_order:
                cell = self.adapter.grid[y][x]
                self._carve_walls(cell, dir, self.stg.off_color)
                self.put_image()
                yield

        self.render_pattern()
        self.render_terminals()
        self.render_path()
        self.put_image()

    def _carve_walls(self, cell: Cell, dir: str, color: int) -> None:
        """Color the passage between a cell and its neighbour in ``dir``.

        Args:
            cell (Cell): Maze cell to process.
            dir (str): Movement direction.
            color (int): Color value used for drawing.
        """
        y = cell.row * self.stg.cell_size
        x = cell.col * self.stg.cell_size

        h_width = self.stg.cell_size - 2 * self.stg.wall_size
        v_height = self.stg.cell_size - 2 * self.stg.wall_size

        if dir == "N":
            self._put_box(
                x=x + self.stg.wall_size,
                y=y - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "S":
            self._put_box(
                x=x + self.stg.wall_size,
                y=y + self.stg.cell_size - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "W":
            self._put_box(
                x=x - self.stg.wall_size,
                y=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )

        elif dir == "E":
            self._put_box(
                x=x + self.stg.cell_size - self.stg.wall_size,
                y=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )
