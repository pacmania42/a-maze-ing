"""Bridge maze-generator data to the representation used by the MLX UI."""

from pathlib import Path
from typing import Protocol, runtime_checkable

from mazegen import MazeGenerator

from src.cell import Cell
from src.models import ConfigData
from src.settings import Settings


class AdapterError(Exception):
    """Raised when maze data cannot be loaded or adapted for the UI."""


@runtime_checkable
class Generator(Protocol):
    """Describe the generator API required by :class:`Adapter`."""

    maze: list[list[int]]
    maze_entry: tuple[int, int]
    maze_exit: tuple[int, int]
    shortest_path: str
    pattern: list[tuple[int, int]] | None
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
        self.pattern: list[tuple[int, int]] | None = None
        self.carving_order: list[tuple[int, int, str]] = []

        self.generate()

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
        self.entry = self.grid[self.gen.maze_entry[1]][self.gen.maze_entry[0]]
        self.exit = self.grid[self.gen.maze_exit[1]][self.gen.maze_exit[0]]
        self.pattern = self.gen.pattern
        if isinstance(self.gen.shortest_path, str):  # TODO: update the api
            self.shortest_path = self._get_shortest_path(
                self.gen.shortest_path
            )
        self.path_dirs = self._path_dirs()

    def _path_dirs(self) -> list[str]:
        """Return the shortest-path direction string as a list of moves.

        Returns:
            list[str]: Result produced by `_path_dirs`.
        """
        return list(self.gen.shortest_path)

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

    def _get_shortest_path(self, path: str) -> list[Cell]:
        """Translate an NESW solution string into the visited Cell sequence.

        Args:
            path (str): Shortest-path direction string.

        Returns:
            list[Cell]: Result produced by `_get_shortest_path`.
        """
        shortest_path: list[Cell] = []
        y, x = self.entry.row, self.entry.col
        shortest_path.append(self.grid[y][x])

        for dirr in path:
            if dirr == "N":
                y -= 1
            elif dirr == "S":
                y += 1
            elif dirr == "E":
                x += 1
            elif dirr == "W":
                x -= 1

            shortest_path.append(self.grid[y][x])
        return shortest_path

    def export(self, output_file: Path) -> None:
        """Delegate maze serialization to the active generator.

        Args:
            output_file (Path): Path or name of the maze output file.
        """
        self.gen.export(output_file)
