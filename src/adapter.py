"""Bridge maze-generator data to the representation used by the MLX UI."""

from enum import Enum
from pathlib import Path
from typing import Iterable, Protocol, runtime_checkable

from mazegen import MazeGenerator

from src.cell import Cell
from src.models import ConfigData
from src.settings import Settings


class AdapterError(Exception):
    """Raised when maze data cannot be loaded or adapted for the UI."""


class Direction(Enum):
    NORTH = "N"
    EAST = "E"
    SOUTH = "S"
    WEST = "W"


@runtime_checkable
class Generator(Protocol):
    """Describe the generator API required by :class:`Adapter`."""

    maze: list[list[int]]
    maze_entry: tuple[int, int]
    maze_exit: tuple[int, int]
    shortest_path: str
    pattern: list[tuple[int, int]]
    carving_order: list[tuple[int, int, str]]

    def generate(self, seed: int | None = None) -> None:
        """Generate or reload maze data, optionally using a new seed.

        Args:
            seed (int | None): Optional random seed used for generation.
        """
        ...

    def export(self, output_file: Path) -> None:
        """Export the current maze to ``output_file`` when supported.

        Args:
            output_file (Path): Path or name of the maze output file.
        """
        ...


class MazeGeneratorFile:
    """Provide the generator API for a maze loaded from an output file."""

    def __init__(self, output_file: str):
        """Initialize the file-backed generator and load ``output_file``.

        Args:
            output_file (str): Path or name of the maze output file.
        """
        self._output_file = output_file
        self.maze: list[list[int]] = [[]]
        self.maze_entry: tuple[int, int] = (0, 0)
        self.maze_exit: tuple[int, int] = (0, 0)
        self.shortest_path: str = ""
        self.pattern: Iterable[tuple[int, int]] = []
        self.carving_order: list[tuple[int, int, str]] = []

        self.generate()
        self._get_render_order()

    def _get_render_order(self) -> None:
        self.carving_order.clear()
        width, height = len(self.maze[0]), len(self.maze)
        movements = (
            (0b0001, "N", 0, -1, "S"),
            (0b0100, "S", 0, 1, "N"),
            (0b0010, "E", 1, 0, "W"),
            (0b1000, "W", -1, 0, "E"),
        )
        carved: list[tuple[int, int, str]] = []

        for row in range(height):
            for col in range(width):
                val = self.maze[row][col]

                for mask, dir, n_col, n_row, n_dir in movements:
                    n_col += col
                    n_row += row

                    if (col, row, dir) in carved:
                        continue
                    if (0 > n_col or n_col >= width) or (
                        0 > n_row or n_col >= height
                    ):
                        continue
                    if not val & mask:
                        self.carving_order.append((col, row, dir))
                        carved.extend([(col, row, dir), (n_col, n_row, n_dir)])

    def generate(self, seed: int | None = None) -> None:
        """Reload maze rows, terminals, and solution from the output file.

        Args:
            seed (int | None): Optional random seed used for generation.
        """
        self.maze.clear()
        try:
            with open(self._output_file) as output:
                while not (line := output.readline()).isspace():
                    self.maze.append(
                        [int(item, base=16) for item in line[:-1]]
                    )

                x, y = output.readline()[:-1].split(",")
                self.maze_entry = int(x), int(y)

                x, y = output.readline()[:-1].split(",")
                self.maze_exit = int(x), int(y)

                self.shortest_path = output.readline()[:-1]

        except OSError as e:
            raise AdapterError("Error reading outputfile.") from e
        except ValueError as e:
            raise AdapterError("Invalid entries in the output file") from e

    def export(self, output_file: Path) -> None:
        """Do nothing because visualize-only input is already exported data.

        Args:
            output_file (Path): Path or name of the maze output file.
        """
        pass


class Adapter:
    """Convert generator output into cells and paths used by ``MazeView``."""

    def __init__(
        self,
        output_file: str,
        cfg: ConfigData | None,
        stg: Settings,
    ) -> None:
        """Create either a configured generator or a file-backed generator.

        Args:
            output_file (str): Path or name of the maze output file.
            cfg (ConfigData | None): Parsed maze configuration, or None when
              loading a file.
            stg (Settings): Rendering settings used by the application.
        """
        self.cfg: ConfigData | None = None
        if cfg:
            self.cfg = cfg
            self.seed: int | None = cfg.seed
            self.output_file = cfg.output_file.name
            self.gen = MazeGenerator(
                size=(cfg.width, cfg.height),
                entry_cell=cfg.entry,
                exit_cell=cfg.exit,
                perfect=cfg.perfect,
                seed=cfg.seed,
                algorithm=cfg.algorithm,
                pattern=stg.pattern,
            )
        else:
            self.gen = MazeGeneratorFile(output_file)

    def generate(self, seed: int | None = None) -> None:
        """Generate maze data and rebuild the UI-friendly grid and solution.

        Args:
            seed (int | None): Optional random seed used for generation.
        """
        self.seed = self.cfg.seed if self.cfg and seed is None else seed
        self.gen.generate(self.seed)
        self.grid = self._create_grid(self.gen.maze)
        self.height = len(self.grid)
        self.width = len(self.grid[0])
        self.entry = self.grid[self.gen.maze_entry[1]][self.gen.maze_entry[0]]
        self.exit = self.grid[self.gen.maze_exit[1]][self.gen.maze_exit[0]]
        self.pattern = self.gen.pattern
        self.shortest_path = self._get_shortest_path(self.gen.shortest_path)
        self.render_order = self._get_render_order()

    def _get_render_order(self) -> list[tuple[int, int, Direction]]:
        try:
            return [
                (col, row, Direction(dir))
                for col, row, dir in self.gen.carving_order
            ]
        except ValueError as e:
            raise AdapterError(
                f"AdapterError: Invalid direction {dir!r}"
            ) from e

    def _create_grid(self, maze: list[list[int]]) -> list[list[Cell]]:
        """Convert hexadecimal wall values into a two-dimensional Cell grid.

        Args:
            maze (list[list[int]]): Two-dimensional maze wall representation.

        Returns:
            list[list[Cell]]: Result produced by `_create_grid`.
        """
        grid: list[list[Cell]] = []
        for row in range(len(maze)):
            row_cells: list[Cell] = []
            for col in range(len(maze[0])):
                cell = Cell(maze[row][col], row, col)
                row_cells.append(cell)
            grid.append(row_cells)
        return grid

    def _get_shortest_path(
        self, path: str
    ) -> list[tuple[int, int, Direction]]:
        """Translate the shortest path to coordinate and direction sequence

        Args:
            path (str): Shortest-path direction string.

        Returns:
            list[tuple[int, int, Direction]]: The shortest path with directions
        """
        shortest_path: list[tuple[int, int, Direction]] = []
        y, x = self.entry.row, self.entry.col

        for dirr in path:
            dir = Direction(dirr)
            shortest_path.append((x, y, dir))
            if dir == Direction.NORTH:
                y -= 1
            elif dir == Direction.SOUTH:
                y += 1
            elif dir == Direction.EAST:
                x += 1
            elif dir == Direction.WEST:
                x -= 1
        return shortest_path

    def export(self, output_file: Path) -> None:
        """Delegate maze serialization to the active generator.

        Args:
            output_file (Path): Path or name of the maze output file.
        """
        self.gen.export(output_file)
