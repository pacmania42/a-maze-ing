import inspect

from mazegen import MazeGenerator


def test_mazegenerator_init_params() -> None:
    sig = inspect.signature(MazeGenerator.__init__)
    assert set(sig.parameters) == set(
        [
            "self",
            "size",
            "entry_cell",
            "exit_cell",
            "perfect",
            "seed",
            "algorithm",
            "pattern",
        ]
    )


def test_mazegenerator_generate_params() -> None:
    sig = inspect.signature(MazeGenerator.generate)
    assert list(sig.parameters) == ["self", "seed"]


def test_mazegenerator_shortest_path() -> None:
    maze = MazeGenerator()
    maze.generate()
    assert isinstance(maze.shortest_path, str)
