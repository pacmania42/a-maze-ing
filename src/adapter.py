from random import randint
from typing import Any

from mazegenerator import MazeGenerator

from src.cell import Cell
from src.models import ConfigData


class AdapterError(Exception):
    pass


class Adapter:
    grid: list[list[Cell]]
    entry: Cell
    exit: Cell
    shortest_path: list[Cell]
    gen: MazeGenerator | None
    output_file: str

    def __init__(self, output_file: str, cfg: ConfigData | None) -> None:
        self.gen = None
        self.output_file = output_file
        if cfg:
            self.cfg = cfg
            self.output_file = cfg.output_file.name
            self.gen = MazeGenerator(
                size=(cfg.width, cfg.height),
                entry_cell=cfg.entry,
                exit_cell=cfg.exit,
                perfect=cfg.perfect,
                seed=cfg.seed,
            )

    def generate(self) -> None:
        if self.gen:
            self.gen.generate(randint(-1000, 1000))
            self.grid = self._create_grid(self.gen.maze)
            self.entry = self.grid[self.cfg.entry[1]][self.cfg.entry[0]]
            self.exit = self.grid[self.cfg.exit[1]][self.cfg.exit[0]]
            if isinstance(self.gen.shortest_path, str):  # TODO: update the api
                self.shortest_path = self._get_shortest_path(
                    self.gen.shortest_path
                )
        else:
            res = self._read_output(self.output_file)
            self.grid = self._create_grid(res["grid"])
            self.entry = self.grid[res["entry"][1]][res["entry"][0]]
            self.exit = self.grid[res["exit"][1]][res["exit"][0]]
            self.shortest_path = self._get_shortest_path(res["path"])

    def _read_output(self, output_file: str) -> dict[str, Any]:
        res: dict[str, Any] = {
            "grid": [],
            "entry": (),
            "exit": (),
            "path": [],
        }

        try:
            with open(output_file) as output:
                while not (line := output.readline()).isspace():
                    res["grid"].append(
                        [int(item, base=16) for item in line[:-1]]
                    )

                x, y = output.readline()[:-1].split(",")
                res["entry"] = int(x), int(y)

                x, y = output.readline()[:-1].split(",")
                res["exit"] = int(x), int(y)

                res["path"] = output.readline()[:-1]

        except OSError as e:
            raise AdapterError("Error reading outputfile.") from e
        except ValueError as e:
            raise AdapterError("Invalid entries in the output file") from e

        return res

    def _create_grid(self, maze: list[list[int]]) -> list[list[Cell]]:
        grid: list[list[Cell]] = []
        for row in range(len(maze)):
            row_cells: list[Cell] = []
            for col in range(len(maze[0])):
                cell = Cell(maze, row, col)
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
