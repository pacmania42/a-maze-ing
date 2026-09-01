import sys
from pathlib import Path

from mazegen.generator import MazeGeneratorError

from src.adapter import Adapter, AdapterError
from src.maze_view import MazeView
from src.models import ParseError
from src.parser import Parser
from src.settings import Settings


def main() -> None:
    """Parse input, prepare the maze, and start the graphical interface."""
    parser = Parser()
    res = parser.parse_args()

    if not res.visualize_only:
        try:
            cfg = parser.parse_config_file(res.file)
            output_file = cfg.output_file.name
        except ParseError as err:
            print(err)
            sys.exit(1)
    else:
        cfg = None
        output_file = res.file

    try:
        stg = Settings()
        adapter = Adapter(output_file, cfg, stg)
        adapter.generate()
        if cfg:
            adapter.export(Path(cfg.output_file))
    except (AdapterError, MazeGeneratorError) as e:
        print(e)
        return

    ui = MazeView(adapter, stg)
    ui.mlx_loop(ui.mlx_ptr)


if __name__ == "__main__":
    main()
