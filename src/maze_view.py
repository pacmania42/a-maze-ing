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
        self.adapter = adapter
        self.stg = stg

        self.animation_gens: list[Generator[None, None, None] | None] = [
            self.render_maze(),
            None,
        ]
        self.last_tick = 0.0
        self.animate = True
        self.show_path = True
        self.color_idx = 0
        self.text_rendered = False

        self.maze_width = len(self.adapter.grid[0]) * self.stg.cell_size
        self.maze_height = len(self.adapter.grid) * self.stg.cell_size
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
        for i, gen in enumerate(self.animation_gens):
            if not gen:
                continue
            now = time.perf_counter()
            if not self.animate or now - self.last_tick > self.stg.tick:
                self.last_tick = now
                try:
                    next(gen)
                except StopIteration:
                    self.animation_gens[i] = None
                    if i == 0:
                        self.animation_gens[1] = self.render_path()

    def _on_keypress(self, key: int, _: Any) -> None:
        """Handle keypresses.

        Args:
            key (int): keycode for the pressed key.
            _ (Any): discarded callback data.
        """
        if key == self.stg.close_win:
            self.mlx_loop_exit(self.mlx_ptr)

        elif key == self.stg.toggle_animation:
            self.animate = not self.animate

        elif key == self.stg.toggle_path:
            self.show_path = not self.show_path
            self.reset_animation(1)

        elif key == self.stg.new_maze:
            self.adapter.generate(seed=randint(-1000, 1000))
            self.reset_animation(0)

        elif key == self.stg.change_wall_color:
            self.color_idx = (self.color_idx + 1) % len(self.stg.wall_colors)
            self.reset_animation(0)

    def reset_animation(self, idx: int) -> None:
        """Reset the appropriate animation generator.

        Args:
            idx (int): index of the animation generator.
        """
        if idx == 0:
            self.animation_gens[0] = self.render_maze()
        elif idx == 1:
            self.animation_gens[1] = self.render_path()
        self.last_tick = 0.0

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
                row=y + self.stg.wall_size,
                col=x + self.stg.wall_size,
                width=int(self.stg.cell_size - 2 * self.stg.wall_size),
                height=int(self.stg.cell_size - 2 * self.stg.wall_size),
                color=color,
            )

    def render_pattern(self) -> None:
        """Draw the pattern inside the maze."""
        for col, row in self.adapter.pattern:  # ty:ignore[not-iterable]
            x = col * self.stg.cell_size
            y = row * self.stg.cell_size

            self._put_box(
                row=y + self.stg.wall_size,
                col=x + self.stg.wall_size,
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
        self.write(y=self.stg.y_offset + 330, string="M | New (M)aze")
        self.write(y=self.stg.y_offset + 360, string="P | Toggle (P)ath")
        self.write(y=self.stg.y_offset + 390, string="W | Change (W)all color")
        self.write(y=self.stg.y_offset + 420, string="A | Toggle (A)nimation")
        self.write(y=self.stg.y_offset + 450, string="ESC | Quit")

    def _put_box(
        self, row: int, col: int, width: int, height: int, color: int
    ) -> None:
        """Fill a rectangular area of the image buffer with one color.

        Args:
            row (int): Vertical coordinate.
            col (int): Horizontal coordinate.
            width (int): Width in pixels or cells.
            height (int): Height in pixels or cells.
            color (int): Color value used for drawing.
        """
        pixel = bytes(
            ((color & 0xFF), (color >> 8 & 0xFF), (color >> 16 & 0xFF), 0xFF)
        )
        row_bytes = pixel * width
        start = col * self.bpp
        end = start + width * self.bpp

        for y in range(height):
            offset = (row + y) * self.ll
            self.data_addr[slice(offset + start, offset + end)] = row_bytes

    def render_maze(self) -> Generator[None, None, None]:
        """Generate the render steps for the maze with animation."""
        if not self.text_rendered:
            for _ in range(2):
                self.render_text()
            self.text_rendered = True

        height = len(self.adapter.grid)
        width = len(self.adapter.grid[0])
        color = self.stg.wall_colors[self.color_idx]

        self._put_box(0, 0, self.maze_width, self.maze_height, color)

        for row in range(height):
            for col in range(width):
                y = row * self.stg.cell_size
                x = col * self.stg.cell_size
                self._put_box(
                    row=y + self.stg.wall_size,
                    col=x + self.stg.wall_size,
                    width=self.stg.cell_size - 2 * self.stg.wall_size,
                    height=self.stg.cell_size - 2 * self.stg.wall_size,
                    color=self.stg.off_color,
                )

        for x, y, dir in self.adapter.gen.carving_order:
            cell = self.adapter.grid[y][x]
            self._carve_walls(cell, dir, self.stg.off_color)
            self.put_image()
            if self.animate:
                yield

        self.render_pattern()
        self.render_terminals()
        self.put_image()

    def render_path(self) -> Generator[None, None, None]:
        """Generate render steps for the shortest path with animation."""
        color = self.stg.path_color if self.show_path else self.stg.off_color
        path = self.adapter.shortest_path[:-1]

        for cell, dir in zip(path, self.adapter.path_dirs, strict=True):
            x = cell.col * self.stg.cell_size
            y = cell.row * self.stg.cell_size

            if cell is not path[0]:
                self._put_box(
                    row=y + self.stg.wall_size,
                    col=x + self.stg.wall_size,
                    width=self.stg.cell_size - 2 * self.stg.wall_size,
                    height=self.stg.cell_size - 2 * self.stg.wall_size,
                    color=color,
                )
            self._carve_walls(cell, dir, color)
            self.put_image()
            if self.animate:
                yield

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
                col=x + self.stg.wall_size,
                row=y - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "S":
            self._put_box(
                col=x + self.stg.wall_size,
                row=y + self.stg.cell_size - self.stg.wall_size,
                width=h_width,
                height=self.stg.wall_size * 2,
                color=color,
            )

        elif dir == "W":
            self._put_box(
                col=x - self.stg.wall_size,
                row=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )

        elif dir == "E":
            self._put_box(
                col=x + self.stg.cell_size - self.stg.wall_size,
                row=y + self.stg.wall_size,
                width=self.stg.wall_size * 2,
                height=v_height,
                color=color,
            )
