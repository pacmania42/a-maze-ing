import os
from typing import Any

from mlx import Mlx

from src.adapter import Adapter
from src.cell import Cell
from src.settings import Settings


class MazeView:
    grid: list[list[Cell]]
    m: Mlx
    mlx_ptr: int
    win_ptr: int
    data_addr: memoryview
    ll: int
    bpp: int
    maze_height: int
    maze_width: int

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter
        self.stg = Settings()

        self.show_path: bool = True
        self.wall_color_idx = 0

        self.maze_width = len(self.adapter.grid[0]) * self.stg.cell_size
        self.maze_height = len(self.adapter.grid) * self.stg.cell_size
        self.view_height = self.maze_height + self.stg.footer_height
        self.view_width = self.maze_width

        self.m = Mlx()
        self.mlx_ptr: int = self.m.mlx_init()
        self.win_ptr: int = self.m.mlx_new_window(
            self.mlx_ptr,
            self.view_width,
            self.view_height,
            self.stg.window_title,
        )
        self.img_addr = self.m.mlx_new_image(
            self.mlx_ptr, self.maze_width, self.maze_height
        )
        data_addr, bpp, ll, _ = self.m.mlx_get_data_addr(self.img_addr)
        self.data_addr = data_addr
        self.bpp = bpp
        self.ll = ll

        self.m.mlx_key_hook(self.win_ptr, self.keybinding_dispatch, {})

    def keybinding_dispatch(self, keycode: int, _: dict[str, Any]) -> None:
        if keycode == 0xFF1B:  # escape
            self.m.mlx_destroy_image(self.mlx_ptr, self.img_addr)
            self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            os._exit(0)

        if keycode == 0x6D:  # m
            self.adapter.generate()
            self.clear()
            self.render_maze()
            self.render_terminals()
            self.render_path()
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
            )

        if keycode == 0x70:  # p
            self.show_path = not self.show_path
            self.render_path()
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
            )

        if keycode == 0x77:  # w
            self.wall_color_idx = (self.wall_color_idx + 1) % len(
                self.stg.wall_colors
            )
            self.render_maze()
            self.m.mlx_put_image_to_window(
                self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
            )

    def clear(self) -> None:
        self._put_box(
            0,
            0,
            self.maze_width,
            self.maze_height,
            self.stg.off_color,
        )

    def show(self) -> None:
        self.render_text()
        self.render_maze()
        self.render_terminals()
        self.render_path()

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
        )
        self.m.mlx_loop(self.mlx_ptr)

    def render_terminals(self) -> None:
        terminals = (self.adapter.entry, "entry"), (self.adapter.exit, "exit")

        for cell, name in terminals:
            x = cell.row * self.stg.cell_size
            y = cell.col * self.stg.cell_size

            color = (
                self.stg.entry_color
                if name == "entry"
                else self.stg.exit_color
            )

            self._put_box(
                y=x + self.stg.wall_size,
                x=y + self.stg.wall_size,
                width=int(self.stg.cell_size - 2 * self.stg.wall_size),
                height=int(self.stg.cell_size - 2 * self.stg.wall_size),
                color=color,
            )

    def render_path(self) -> None:
        color = self.stg.path_color if self.show_path else self.stg.off_color
        path = self.adapter.shortest_path[1:-1]

        for cell in path:
            x = cell.row * self.stg.cell_size
            y = cell.col * self.stg.cell_size

            self._put_box(
                y=x + self.stg.wall_size,
                x=y + self.stg.wall_size,
                width=int(self.stg.cell_size - 2 * self.stg.wall_size),
                height=int(self.stg.cell_size - 2 * self.stg.wall_size),
                color=color,
            )

    def render_text(self) -> None:
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height + self.stg.text_y_offset - 10,
            self.stg.text_color,
            "KEYBINDINGS",
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + self.stg.text_line_inset,
            self.stg.text_color,
            "m | Regenerate maze",
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + 2 * self.stg.text_line_inset,
            self.stg.text_color,
            "p | Show/Hide shortest path",
        )
        self.m.mlx_string_put(
            self.mlx_ptr,
            self.win_ptr,
            self.stg.text_x_offset,
            self.maze_height
            + self.stg.text_y_offset
            + 3 * self.stg.text_line_inset,
            self.stg.text_color,
            "w | Change wall color",
        )
        self.m.mlx_string_put(
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
        offset = (y * self.ll) + (x * (self.bpp // 8))
        self.data_addr[offset] = (color) & 0xFF
        self.data_addr[offset + 1] = (color >> 8) & 0xFF
        self.data_addr[offset + 2] = (color >> 16) & 0xFF
        self.data_addr[offset + 3] = 0xFF

    def _put_box(
        self, y: int, x: int, width: int, height: int, color: int
    ) -> None:
        for yy in range(height):
            for xx in range(width):
                self._put_pixel(y=y + yy, x=x + xx, color=color)

    def render_maze(
        self,
    ) -> None:
        for row in self.adapter.grid:
            for cell in row:
                y = cell.row * self.stg.cell_size
                x = cell.col * self.stg.cell_size

                # north
                if cell.n:
                    self._put_box(
                        y=y,
                        x=x,
                        width=self.stg.cell_size,
                        height=self.stg.wall_size,
                        color=self.stg.wall_colors[self.wall_color_idx],
                    )

                # south
                if cell.s:
                    self._put_box(
                        y=y + self.stg.cell_size - self.stg.wall_size,
                        x=x,
                        width=self.stg.cell_size,
                        height=self.stg.wall_size,
                        color=self.stg.wall_colors[self.wall_color_idx],
                    )

                # east wall
                if cell.e:
                    self._put_box(
                        y=y,
                        x=x + self.stg.cell_size - self.stg.wall_size,
                        width=self.stg.wall_size,
                        height=self.stg.cell_size,
                        color=self.stg.wall_colors[self.wall_color_idx],
                    )

                # west
                if cell.w:
                    self._put_box(
                        x=x,
                        y=y,
                        width=self.stg.wall_size,
                        height=self.stg.cell_size,
                        color=self.stg.wall_colors[self.wall_color_idx],
                    )
