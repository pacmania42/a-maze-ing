from typing import Any, Callable


class Mlx:
    def mlx_init(self) -> memoryview: ...
    def mlx_new_window(
        self,
        mlx_ptr: memoryview,
        width: int,
        height: int,
        title: str,
    ) -> memoryview: ...
    def mlx_new_image(
        self,
        mlx_ptr: memoryview,
        width: int,
        height: int,
    ) -> memoryview: ...
    def mlx_get_data_addr(
        self, img_ptr: memoryview
    ) -> tuple[memoryview, int, int, int]: ...
    def mlx_string_put(
        self,
        mlx_ptr: memoryview,
        win_ptr: memoryview,
        x: int,
        y: int,
        color: int,
        text: str,
    ) -> None: ...
    def mlx_put_image_to_window(
        self,
        mlx_ptr: memoryview,
        win_ptr: memoryview,
        img_ptr: memoryview,
        x: int,
        y: int,
    ) -> None: ...
    def mlx_key_hook(
        self,
        win_ptr: memoryview,
        callback: Callable[[int, Any], None],
        param: Any,
    ) -> None: ...
    def mlx_loop(self, mlx_ptr: memoryview) -> None: ...
