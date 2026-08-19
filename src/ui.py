import os
from typing import Any

from mlx import Mlx

from src.adapter import Adapter
from src.cell import Cell
from src.settings import Settings as stg


class UI:
    grid: list[list[Cell]]
    m: Mlx
    mlx_ptr: int
    win_ptr: int
    data_addr: memoryview
    ll: int
    bpp: int
    height: int
    width: int

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter
        rows, columns = len(self.adapter.grid), len(self.adapter.grid[0])

        self.m = Mlx()
        self.mlx_ptr: int = self.m.mlx_init()
        self.width = columns * stg.cell_size
        self.height = rows * stg.cell_size

        self.win_ptr: int = self.m.mlx_new_window(
            self.mlx_ptr,
            self.width,
            self.height,
            stg.window_title,
        )
        self.img_addr = self.m.mlx_new_image(
            self.mlx_ptr, self.width, self.height
        )
        data_addr, bpp, ll, _ = self.m.mlx_get_data_addr(self.img_addr)
        self.data_addr = data_addr
        self.bpp = bpp
        self.ll = ll

        self.m.mlx_key_hook(self.win_ptr, self.keybinding_dispatch, {})

    def keybinding_dispatch(self, keycode: int, _: dict[str, Any]) -> None:
        if keycode == 65307:  # escape
            self.m.mlx_destroy_window(self.mlx_ptr, self.win_ptr)
            os._exit(0)

    def show(self) -> None:
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
            x = cell.row * stg.cell_size
            y = cell.col * stg.cell_size

            color = stg.entry_color if name == "entry" else stg.exit_color

            self._put_box(
                y=x + stg.wall_size,
                x=y + stg.wall_size,
                width=int(stg.cell_size - 2 * stg.wall_size),
                height=int(stg.cell_size - 2 * stg.wall_size),
                color=color,
            )

    def render_path(self) -> None:
        path = self.adapter.shortest_path[1:-1]

        for cell in path:
            x = cell.row * stg.cell_size
            y = cell.col * stg.cell_size

            self._put_box(
                y=x + stg.wall_size,
                x=y + stg.wall_size,
                width=int(stg.cell_size - 2 * stg.wall_size),
                height=int(stg.cell_size - 2 * stg.wall_size),
                color=stg.path_color,
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
                y = cell.row * stg.cell_size
                x = cell.col * stg.cell_size

                # north
                if cell.n:
                    self._put_box(
                        y=y,
                        x=x,
                        width=stg.cell_size,
                        height=stg.wall_size,
                        color=stg.wall_color,
                    )

                # south
                if cell.s:
                    self._put_box(
                        y=y + stg.cell_size - stg.wall_size,
                        x=x,
                        width=stg.cell_size,
                        height=stg.wall_size,
                        color=stg.wall_color,
                    )

                # east wall
                if cell.e:
                    self._put_box(
                        y=y,
                        x=x + stg.cell_size - stg.wall_size,
                        width=stg.wall_size,
                        height=stg.cell_size,
                        color=stg.wall_color,
                    )

                # west
                if cell.w:
                    self._put_box(
                        x=x,
                        y=y,
                        width=stg.wall_size,
                        height=stg.cell_size,
                        color=stg.wall_color,
                    )
