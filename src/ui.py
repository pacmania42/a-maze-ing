import os
from typing import Any

from mlx import Mlx

from src.adapter import Adapter
from src.cell import Cell
from src.settings import Settings


class UI:
    grid: list[list[Cell]]
    settings: Settings
    m: Mlx
    mlx_ptr: int
    win_ptr: int
    data_addr: int
    height: int
    width: int

    def __init__(self, adapter: Adapter) -> None:
        self.adapter = adapter

        self.m = Mlx()
        self.mlx_ptr: int = self.m.mlx_init()
        self.width = adapter.columns * Settings.cell_size
        self.height = adapter.rows * Settings.cell_size

        self.win_ptr: int = self.m.mlx_new_window(
            self.mlx_ptr,
            self.width,
            self.height,
            Settings.window_title,
        )

        self.m.mlx_key_hook(self.win_ptr, self.keybinding_dispatch, {})

    def keybinding_dispatch(self, keycode: int, _: dict[str, Any]) -> None:
        if keycode == 65307:
            os._exit(0)

    def show(self) -> None:
        img_addr = self.m.mlx_new_image(
            self.mlx_ptr,
            self.width,
            self.height,
        )
        data_addr, bpp, ll, _ = self.m.mlx_get_data_addr(img_addr)
        for row in self.adapter.grid:
            for cell in row:
                cell.render(
                    data_addr,
                    ll,
                    bpp,
                    Settings.wall_color,
                    Settings.path_color,
                )

        self.m.mlx_put_image_to_window(
            self.mlx_ptr, self.win_ptr, img_addr, 0, 0
        )
        self.m.mlx_loop(self.mlx_ptr)
