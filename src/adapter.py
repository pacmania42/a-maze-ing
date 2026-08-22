from typing import Any

from src.cell import Cell


class AdapterError(Exception):
    pass


class Adapter:
    grid: list[list[Cell]]
    entry: Cell
    exit: Cell
    shortest_path: list[Cell]

    def __init__(self, output_file: str) -> None:
        res = self._read_output(output_file)
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
