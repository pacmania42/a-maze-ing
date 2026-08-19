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

        self.show_path = False
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

        if keycode == 0x70:  # p
            self.show_path = not self.show_path
            self.paint_path()

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
        )

    def show(self) -> None:
        for row in self.adapter.grid:
            for cell in row:
                cell.render(self.data_addr, self.ll, self.bpp)

        self.paint_path()
        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, self.img_addr, 0, 0
        )
        self.m.mlx_loop(self.mlx_ptr)

    def paint_terminals(self) -> None:
        terminals = (self.adapter.entry, "entry"), (self.adapter.exit, "exit")

        for cell, name in terminals:
            x = cell.row * stg.cell_size
            y = cell.col * stg.cell_size

            if not self.show_path:
                color = stg.off_color
            else:
                color = stg.entry_color if name == "entry" else stg.exit_color

            Cell.put_box(
                data_addr=self.data_addr,
                line_len=self.ll,
                bpp=self.bpp,
                y=x + stg.wall_size,
                x=y + stg.wall_size,
                width=int(stg.cell_size - 2 * stg.wall_size),
                height=int(stg.cell_size - 2 * stg.wall_size),
                color=color,
            )

    def paint_path(self) -> None:
        path = self.adapter.shortest_path[1:-1]

        for cell in path:
            x = cell.row * stg.cell_size
            y = cell.col * stg.cell_size

            color = stg.path_color if self.show_path else stg.off_color

            Cell.put_box(
                data_addr=self.data_addr,
                line_len=self.ll,
                bpp=self.bpp,
                y=x + stg.wall_size,
                x=y + stg.wall_size,
                width=int(stg.cell_size - 2 * stg.wall_size),
                height=int(stg.cell_size - 2 * stg.wall_size),
                color=color,
            )
