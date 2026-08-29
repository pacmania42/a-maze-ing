from pathlib import Path
from typing import Protocol, runtime_checkable

from mazegen import MazeGenerator

from src.cell import Cell
from src.models import ConfigData
from src.settings import Settings


class AdapterError(Exception):
    pass


@runtime_checkable
class Generator(Protocol):
    maze: list[list[int]]
    maze_entry: tuple[int, int]
    maze_exit: tuple[int, int]
    shortest_path: str
    pattern: list[tuple[int, int]] | None
    carving_order: list[tuple[int, int, str]]

    def generate(self, seed: int | None = None) -> None: ...
    def export(self, output_file: Path) -> None: ...


class MazeGeneratorFile:
    def __init__(self, output_file: str):
        self._output_file = output_file
        self.maze: list[list[int]] = [[]]
        self.maze_entry: tuple[int, int] = (0, 0)
        self.maze_exit: tuple[int, int] = (0, 0)
        self.shortest_path: str = ""
        self.pattern: list[tuple[int, int]] | None = None
        self.carving_order: list[tuple[int, int, str]] = []

        self.generate()

    def generate(self, seed: int | None = None) -> None:
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
        pass


class Adapter:
    def __init__(
        self,
        output_file: str,
        cfg: ConfigData | None,
        stg: Settings,
    ) -> None:
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
        return list(self.gen.shortest_path)

    def _create_grid(self, maze: list[list[int]]) -> list[list[Cell]]:
        grid: list[list[Cell]] = []
        for row in range(len(maze)):
            row_cells: list[Cell] = []
            for col in range(len(maze[0])):
                cell = Cell(maze[row][col], row, col)
                row_cells.append(cell)
            grid.append(row_cells)
        return grid

    def _get_shortest_path(self, path: str) -> list[Cell]:
        shortest_path: list[Cell] = []
        x, y = self.entry.row, self.entry.col
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
        self.gen.export(output_file)
