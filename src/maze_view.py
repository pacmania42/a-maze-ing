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
            stg (Settings): Rendering settings used by the application.
        """
        super().__init__()
        self.adp = adapter
        self.stg = stg

        self.text_animation = self.render_text()
        self.maze_animation = self.render_maze()
        self.esp_animation = self.render_esp_cells()
        self.path_animation = self.render_path()
        self.animator: Generator[None, None, None] | None = self.animate()
        self.last_tick = 0.0
        self.animation_enabled = True
        self.show_path = True
        self.color_idx = 0

        self.maze_width = len(self.adp.grid[0]) * self.stg.cell_size
        self.maze_height = len(self.adp.grid) * self.stg.cell_size
        self.win_height = self.maze_height
        self.win_width = self.maze_width + self.stg.txt_pane_width

        self.mlx_ptr = self.mlx_init()
        self.win_ptr = self.mlx_new_window(
            self.mlx_ptr,
            self.win_width,
            self.win_height,
            self.stg.window_title,
        )
        self.img_ptr = self.mlx_new_image(
            self.mlx_ptr, self.maze_width, self.maze_height
        )
        data_addr, bpp, ll, _ = self.mlx_get_data_addr(self.img_ptr)
        self.data_addr: memoryview = data_addr
        self.bpp: int = bpp // 8
        self.ll: int = ll

        self.mlx_key_hook(self.win_ptr, self._on_keypress, None)
        self.mlx_hook(self.win_ptr, 0x21, 0, self._on_event, None)
        self.mlx_loop_hook(self.mlx_ptr, self.app_loop, None)
        self.put_image = partial(
            self.mlx_put_image_to_window,
            self.mlx_ptr,
            self.win_ptr,
            self.img_ptr,
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

    def app_loop(self, _: Any) -> None:
        """Run the render steps with optional animation.

        Args:
            _ (Any): discarded callback data.
        """
        if self.animator is None:
            return
        now = time.perf_counter()
        if not self.animation_enabled or now - self.last_tick > self.stg.tick:
            self.last_tick = now
            try:
                next(self.animator)
            except StopIteration:
                self.animator = None

    def animate(self) -> Generator[None, None, None]:
        """Runs the animation in a pipeline-manner.

        Returns:
            Generator[None, None, None]: generator that runs the animations in
                the pipeline sequentially.
        """
        yield from self.text_animation
        yield from self.maze_animation
        yield from self.esp_animation
        yield from self.path_animation

    def reset_animation(self, idx: int) -> None:
        """Reset the appropriate animation generator.

        Args:
            idx (int): index of the animation generator.
        """
        if idx == 1:
            self.path_animation = self.render_path()
        elif idx == 0:
            self.maze_animation = self.render_maze()
            self.esp_animation = self.render_esp_cells()
            self.path_animation = self.render_path()
        self.animator = self.animate()
        self.last_tick = 0.0

    def _on_event(self, _: Any) -> None:
        self.mlx_destroy_image(self.mlx_ptr, self.img_ptr)
        self.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
        self.mlx_loop_exit(self.mlx_ptr)

    def _on_keypress(self, key: int, _: Any) -> None:
        """Handle keypresses.

        Args:
            key (int): keycode for the pressed key.
            _ (Any): discarded callback data.
        """
        if key == self.stg.close_win:
            self._on_event(None)

        elif key == self.stg.toggle_animation:
            self.animation_enabled = not self.animation_enabled

        elif key == self.stg.toggle_path:
            self.show_path = not self.show_path
            self.reset_animation(1)

        elif key == self.stg.new_maze:
            self.adp.generate(seed=randint(-1000, 1000))
            self.reset_animation(0)

        elif key == self.stg.change_color:
            self.color_idx = (self.color_idx + 1) % len(self.stg.colors)
            self.reset_animation(0)

    def render_text(self) -> Generator[None, None, None]:
        """Display maze details and keybindings."""
        for _ in range(2):
            mode = "Generate+Visualize" if self.adp.cfg else "Visualize-only"
            size = f"{len(self.adp.grid[0])}X{len(self.adp.grid)}"
            entry = f"{self.adp.gen.maze_entry}"
            exit = f"{self.adp.gen.maze_exit}"
            perfect = f"{self.adp.cfg.perfect if self.adp.cfg else 'N/A'}"
            algorithm = self.adp.cfg.algorithm if self.adp.cfg else "N/A"

            self.write(y=self.stg.y_offset, string="DETAILS")
            self.write(y=self.stg.y_offset + 30, string=f"MODE: {mode}")
            self.write(y=self.stg.y_offset + 60, string=f"SIZE: {size}")
            self.write(y=self.stg.y_offset + 90, string=f"ENTRY: {entry}")
            self.write(y=self.stg.y_offset + 120, string=f"EXIT: {exit}")
            self.write(y=self.stg.y_offset + 150, string=f"PERFECT: {perfect}")
            self.write(y=self.stg.y_offset + 180, string=f"ALGO: {algorithm}")

            self.write(y=self.stg.y_offset + 300, string="KEYBINDINGS")
            self.write(y=self.stg.y_offset + 330, string="M | New (M)aze")
            self.write(y=self.stg.y_offset + 360, string="P | Toggle (P)ath")
            self.write(y=self.stg.y_offset + 390, string="C | Change (C)olors")
            self.write(
                y=self.stg.y_offset + 420, string="A | Toggle (A)nimation"
            )
            self.write(y=self.stg.y_offset + 450, string="ESC | Quit")
            yield

    def render_maze(self) -> Generator[None, None, None]:
        """Generate the render steps for the maze with animation.

        Returns:
            Generator[None, None, None]: generator that runs _carve_walls per
                cell in the maze.
        """
        color = self.stg.colors[self.color_idx][0]

        self._put_box(0, 0, self.maze_width, self.maze_height, color)
        for row in range(self.adp.height):
            for col in range(self.adp.width):
                self._put_box(
                    xx=(col * self.stg.cell_size) + self.stg.wall_size,
                    yy=(row * self.stg.cell_size) + self.stg.wall_size,
                    width=self.stg.cell_size - 2 * self.stg.wall_size,
                    height=self.stg.cell_size - 2 * self.stg.wall_size,
                    color=self.stg.off_color,
                )

        for col, row, dir in self.adp.gen.carving_order:
            self._carve_walls(self.adp.grid[row][col], dir, self.stg.off_color)
            if self.animation_enabled:
                self.put_image()
                yield
        if not self.animation_enabled:
            self.put_image()

    def render_esp_cells(self) -> Generator[None, None, None]:
        """Draw the pattern inside the maze.

        Returns:
            Generator[None, None, None]: generator that runs cell-wise render
        """
        esp_cells = [
            (
                self.adp.entry.col,
                self.adp.entry.row,
                self.stg.entry_color,
            ),
            (
                self.adp.exit.col,
                self.adp.exit.row,
                self.stg.exit_color,
            ),
            *[
                (col, row, self.stg.pattern_color)
                for col, row in self.adp.pattern
            ],
        ]

        for col, row, color in esp_cells:
            self._put_box(
                xx=(col * self.stg.cell_size) + self.stg.wall_size,
                yy=(row * self.stg.cell_size) + self.stg.wall_size,
                width=self.stg.cell_size - 2 * self.stg.wall_size,
                height=self.stg.cell_size - 2 * self.stg.wall_size,
                color=color,
            )
            if self.animation_enabled:
                self.put_image()
                yield
        if not self.animation_enabled:
            self.put_image()

    def render_path(self) -> Generator[None, None, None]:
        """Generate render steps for the shortest path with animation.

        Returns:
            Generator[None, None, None]: generator that runs per cell in path
        """
        color = (
            self.stg.colors[self.color_idx][1]
            if self.show_path
            else self.stg.off_color
        )
        path = self.adp.shortest_path[:-1]

        for cell, dir in zip(path, self.adp.path_dirs, strict=True):
            if cell is not path[0]:
                self._put_box(
                    yy=(cell.row * self.stg.cell_size) + self.stg.wall_size,
                    xx=(cell.col * self.stg.cell_size) + self.stg.wall_size,
                    width=self.stg.cell_size - 2 * self.stg.wall_size,
                    height=self.stg.cell_size - 2 * self.stg.wall_size,
                    color=color,
                )
            self._carve_walls(cell, dir, color)
            if self.animation_enabled:
                self.put_image()
                yield
        if not self.animation_enabled:
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
                xx=x + self.stg.wall_size,
                yy=y - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "S":
            self._put_box(
                xx=x + self.stg.wall_size,
                yy=y + self.stg.cell_size - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "W":
            self._put_box(
                xx=x - self.stg.wall_size,
                yy=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )

        elif dir == "E":
            self._put_box(
                xx=x + self.stg.cell_size - self.stg.wall_size,
                yy=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )

    def _put_box(
        self, xx: int, yy: int, width: int, height: int, color: int
    ) -> None:
        """Fill a rectangular area of the image buffer with one color.

        Args:
            col (int): Horizontal coordinate.
            row (int): Vertical coordinate.
            width (int): Width in pixels or cells.
            height (int): Height in pixels or cells.
            color (int): Color value used for drawing.
        """
        pixel = bytes(
            ((color & 0xFF), (color >> 8 & 0xFF), (color >> 16 & 0xFF), 0xFF)
        )
        row_bytes = pixel * width
        start = xx * self.bpp
        end = start + width * self.bpp

        for y in range(height):
            offset = (yy + y) * self.ll
            self.data_addr[slice(offset + start, offset + end)] = row_bytes
