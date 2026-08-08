import inspect

from mazegenerator.mazegenerator import MazeGenerator


def test_mazegenerator_init_params() -> None:
    sig = inspect.signature(MazeGenerator.__init__)
    assert list(sig.parameters) == [
        "self",
        "size",
        "perfect",
        "entry_cell",
        "exit_cell",
        "seed",
    ]


def test_mazegenerator_generate_params() -> None:
    sig = inspect.signature(MazeGenerator.generate)
    assert list(sig.parameters) == ["self", "seed"]


def test_mazegenerator_shortest_path() -> None:
    maze = MazeGenerator()
    maze.generate()
    assert isinstance(maze.shortest_path, str)
