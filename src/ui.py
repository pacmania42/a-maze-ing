import os
from typing import Any

from mlx import Mlx


class UI:
    def __init__(self) -> None:
        self.m = Mlx()
        self.mlx_ptr = self.m.mlx_init()
        self.win_ptr = self.m.mlx_new_window(
            self.mlx_ptr, 1000, 700, "a-maze-ing"
        )
        self.m.mlx_key_hook(self.win_ptr, self.keybinding_dispatch, {})

    def keybinding_dispatch(self, keycode: int, param: dict[str, Any]) -> None:
        if keycode == 65307:
            os._exit(0)

    def show(self) -> None:
        self.m.mlx_loop(self.mlx_ptr)
